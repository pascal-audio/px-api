"""Preset commands group - create, apply, show, and clear channel presets."""

import base64
import json
from datetime import UTC, datetime

from colorama import Fore, Style

from japi_cli_base import CommandGroup, SubCommand


class PresetGroup(CommandGroup):
    """Preset command group for managing channel presets."""

    name = "preset"
    description = "Manage channel presets"

    @staticmethod
    def register_commands(subparsers):
        """Register preset commands."""
        preset_parser = subparsers.add_parser(
            PresetGroup.name,
            help=PresetGroup.description,
            description=PresetGroup.description,
        )
        preset_subparsers = preset_parser.add_subparsers(dest="preset_action", required=True)

        # preset create <CH> -n NAME -v VERSION [-f FILE] [-l]
        create_parser = preset_subparsers.add_parser(
            "create",
            help="Create a new preset (JSON-RPC: preset_create)",
            description="Create preset from current channel configuration. Maps to JSON-RPC: preset_create",
        )
        create_parser.add_argument("channel", type=int, help="Channel number")
        create_parser.add_argument("-n", "--name", required=True, help="Preset name")
        create_parser.add_argument("-v", "--version", required=True, help="Preset version")
        create_parser.add_argument("-f", "--file", help="Output file path (default: <name>_<version>.json)")
        create_parser.add_argument("-l", "--lock", action="store_true", help="Lock preset settings")
        create_parser.set_defaults(command_cls=PresetCreate)

        # preset apply <CH> -f FILE
        apply_parser = preset_subparsers.add_parser(
            "apply",
            help="Apply a preset (JSON-RPC: preset_apply)",
            description="Apply preset to channel. Loads file locally, sends via JSON-RPC: preset_apply",
        )
        apply_parser.add_argument("channel", type=int, help="Channel number")
        apply_parser.add_argument("-f", "--file", required=True, help="Preset file path")
        apply_parser.set_defaults(command_cls=PresetApply)

        # preset show <CH>
        show_parser = preset_subparsers.add_parser(
            "show",
            help="Show current preset (JSON-RPC: preset_show)",
            description="Show current preset for channel. Maps to JSON-RPC: preset_show",
        )
        show_parser.add_argument("channel", type=int, help="Channel number")
        show_parser.set_defaults(command_cls=PresetShow)

        # preset clear <CH>
        clear_parser = preset_subparsers.add_parser(
            "clear",
            help="Clear preset (JSON-RPC: preset_clear)",
            description="Clear preset from channel. Maps to JSON-RPC: preset_clear",
        )
        clear_parser.add_argument("channel", type=int, help="Channel number")
        clear_parser.set_defaults(command_cls=PresetClear)


class PresetCreate(SubCommand):
    """Create a new preset from current channel configuration."""

    @classmethod
    async def run(cls, args):
        # Default to current UTC date if not specified

        creation_date = datetime.now(UTC).isoformat()

        params = {
            "channel": args.channel,
            "name": args.name,
            "version": args.version,
            "created_date": creation_date,
            "vendor_lock": args.lock,
        }

        # When saving to file, force quiet mode to suppress automatic printing
        quiet_mode = args.quiet or bool(args.file)

        result = await cls.send_command_jrpc_message(
            args.target, args.port, "preset_create", params, args.verbose, quiet_mode
        )

        # If -f is specified, save the preset to a file
        if args.file and result and result.result:
            preset_type = result.result.get("preset_type")
            preset_data = result.result.get("preset")
            metadata = result.result.get("metadata")

            if preset_type == "binary":
                # Decode base64 and write binary file
                binary_data = base64.b64decode(preset_data)
                with open(args.file, "wb") as f:
                    f.write(binary_data)
                if not args.quiet:
                    print(f"{Fore.GREEN}✓{Style.RESET_ALL} Binary preset saved to {args.file}")
            elif preset_type == "json":
                # Write JSON file
                with open(args.file, "w") as f:
                    json.dump(preset_data, f, indent=2)
                if not args.quiet:
                    print(f"{Fore.GREEN}✓{Style.RESET_ALL} JSON preset saved to {args.file}")

            if metadata and not args.quiet:
                print(f"{Fore.CYAN}Preset:{Style.RESET_ALL} {metadata['name']}")
                print(f"{Fore.CYAN}Version:{Style.RESET_ALL} {metadata['version']}")
                print(f"{Fore.CYAN}Sample Rate:{Style.RESET_ALL} {metadata['sample_rate']}")
                if metadata.get("vendor_lock"):
                    print(f"{Fore.CYAN}Vendor Lock:{Style.RESET_ALL} {metadata['vendor_lock']}")
                if metadata.get("created_date"):
                    print(f"{Fore.CYAN}Created:{Style.RESET_ALL} {metadata['created_date']}")


class PresetApply(SubCommand):
    """Apply a preset to a channel."""

    @classmethod
    async def run(cls, args):
        # Read the preset file
        try:
            # Try to read as JSON first
            with open(args.file) as f:
                preset_data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If not JSON, read as binary and convert to base64
            with open(args.file, "rb") as f:
                binary_data = f.read()
            preset_data = base64.b64encode(binary_data).decode("ascii")

        params = {"channel": args.channel, "preset": preset_data}

        await cls.send_command_jrpc_message(args.target, args.port, "preset_apply", params, args.verbose, args.quiet)

        if not args.quiet:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} Preset applied to channel {args.channel}")


class PresetShow(SubCommand):
    """Show current preset for a channel."""

    @classmethod
    async def run(cls, args):
        """Show preset information for a speaker channel"""
        params = {"channel": args.channel}
        await cls.send_command_jrpc_message(args.target, args.port, "preset_show", params, args.verbose, args.quiet)


class PresetClear(SubCommand):
    """Clear preset from a channel."""

    @classmethod
    async def run(cls, args):
        params = {"channel": args.channel}
        await cls.send_command_jrpc_message(args.target, args.port, "preset_clear", params, args.verbose, args.quiet)
        if not args.quiet:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} Preset cleared from channel {args.channel}")
