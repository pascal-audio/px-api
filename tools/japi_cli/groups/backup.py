"""Backup commands group - device configuration backup and restore."""

from japi_cli_base import CommandGroup, SubCommand


class BackupGroup(CommandGroup):
    """Backup command group for configuration backup/restore."""

    name = "backup"
    description = "Device configuration backup and restore"

    @staticmethod
    def register_commands(subparsers):
        """Register backup commands."""
        backup_parser = subparsers.add_parser(
            BackupGroup.name,
            help=BackupGroup.description,
            description=BackupGroup.description,
        )
        backup_subparsers = backup_parser.add_subparsers(dest="backup_action", required=True)

        # backup create
        create_parser = backup_subparsers.add_parser("create", help="Create device configuration backup")
        create_parser.add_argument("-f", "--file", help="Save backup to file")
        create_parser.set_defaults(command_cls=BackupCreate)

        # backup restore
        restore_parser = backup_subparsers.add_parser("restore", help="Restore device configuration from backup")
        restore_parser.add_argument("-f", "--file", required=True, help="Backup file to restore from")
        restore_parser.add_argument(
            "--preserve-network", action="store_true", help="Preserve network settings during restore"
        )
        restore_parser.set_defaults(command_cls=BackupRestore)


class BackupCreate(SubCommand):
    """Create device configuration backup."""

    @classmethod
    async def run(cls, args):
        import json

        response = await cls.send_command_jrpc_message(
            args.target, args.port, "backup_create", {}, args.verbose, args.quiet
        )

        if args.file and response:
            # Save backup to file
            with open(args.file, "w") as f:
                json.dump(response.result, f, indent=2)
            if not args.quiet:
                print(f"Backup saved to: {args.file}")


class BackupRestore(SubCommand):
    """Restore device configuration from backup."""

    @classmethod
    async def run(cls, args):
        import json

        from colorama import Fore, Style

        # Read backup data from file
        try:
            with open(args.file) as f:
                backup_data = json.load(f)
        except FileNotFoundError:
            if not args.quiet:
                print(f"{Fore.RED}Error: Backup file not found: {args.file}{Style.RESET_ALL}")
            return
        except json.JSONDecodeError:
            if not args.quiet:
                print(f"{Fore.RED}Error: Invalid JSON in backup file: {args.file}{Style.RESET_ALL}")
            return

        # Extract config from backup response format
        # backup_create returns: {"timestamp": "...", "config": "base64data"}
        # backup_restore expects: {"config": "base64data", "preserve_network_settings": bool}
        if isinstance(backup_data, dict) and "config" in backup_data:
            restore_params = {"config": backup_data["config"]}
            if args.preserve_network:
                restore_params["preserve_network_settings"] = True
        else:
            if not args.quiet:
                print(f"{Fore.RED}Error: Invalid backup data format (missing 'config' field){Style.RESET_ALL}")
            return

        if not args.quiet:
            print("Restoring device configuration...")
        await cls.send_command_jrpc_message(
            args.target, args.port, "backup_restore", restore_params, args.verbose, args.quiet
        )
