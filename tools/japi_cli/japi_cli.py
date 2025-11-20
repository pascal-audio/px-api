import asyncio
import sys

import argcomplete
from colorama import init

# Import command groups
from groups.api import ApiGroup
from groups.backup import BackupGroup
from groups.device import DeviceGroup
from groups.diagnostics import DiagnosticsGroup
from groups.logs import LogsGroup
from groups.metrics import MetricsGroup
from groups.preset import PresetGroup
from groups.setup import SetupGroup
from groups.status import StatusGroup
from japi_cli_base import CommandRegistry


def main():
    init()

    # Check if we're entering interactive mode early (before building parser)
    # This allows interactive mode to work properly
    if "-i" in sys.argv or "--interactive" in sys.argv:
        # Get target and port from args if provided
        target = "192.168.64.100"
        port = 80
        verbose = False

        if "-t" in sys.argv:
            idx = sys.argv.index("-t")
            if idx + 1 < len(sys.argv):
                target = sys.argv[idx + 1]
        elif "--target" in sys.argv:
            idx = sys.argv.index("--target")
            if idx + 1 < len(sys.argv):
                target = sys.argv[idx + 1]

        if "-p" in sys.argv:
            idx = sys.argv.index("-p")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])
        elif "--port" in sys.argv:
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])

        if "-v" in sys.argv or "--verbose" in sys.argv:
            verbose = True

        # Build parser for interactive mode
        CommandRegistry.register_group(ApiGroup)
        CommandRegistry.register_group(BackupGroup)
        CommandRegistry.register_group(DeviceGroup)
        CommandRegistry.register_group(DiagnosticsGroup)
        CommandRegistry.register_group(LogsGroup)
        CommandRegistry.register_group(MetricsGroup)
        CommandRegistry.register_group(PresetGroup)
        CommandRegistry.register_group(SetupGroup)
        CommandRegistry.register_group(StatusGroup)
        parser = CommandRegistry.build_parser()

        from japi_cli_interactive import run_interactive_mode

        run_interactive_mode(parser, target, port, verbose)
        return

    # Register command groups
    CommandRegistry.register_group(ApiGroup)
    CommandRegistry.register_group(BackupGroup)
    CommandRegistry.register_group(DeviceGroup)
    CommandRegistry.register_group(DiagnosticsGroup)
    CommandRegistry.register_group(LogsGroup)
    CommandRegistry.register_group(MetricsGroup)
    CommandRegistry.register_group(PresetGroup)
    CommandRegistry.register_group(SetupGroup)
    CommandRegistry.register_group(StatusGroup)

    # Build parser
    parser = CommandRegistry.build_parser()

    # Add interactive mode flag
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive REPL mode")

    # Enable shell completion
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # Execute command if provided
    if hasattr(args, "command_cls"):
        try:
            asyncio.run(args.command_cls.run(args))
        except Exception:
            # Command failed - exit with code 1 in CLI mode
            # Error message already printed by command
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
