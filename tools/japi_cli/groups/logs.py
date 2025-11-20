"""Logs commands group - device log retrieval and configuration."""

from japi_cli_base import CommandGroup, SubCommand


class LogsGroup(CommandGroup):
    """Logs command group for log operations."""

    name = "logs"
    description = "Device log operations"

    @staticmethod
    def register_commands(subparsers):
        """Register logs commands."""
        logs_parser = subparsers.add_parser(
            LogsGroup.name,
            help=LogsGroup.description,
            description=LogsGroup.description,
        )
        logs_subparsers = logs_parser.add_subparsers(dest="logs_action", required=True)

        # logs show
        show_parser = logs_subparsers.add_parser("show", help="Show device logs")
        show_parser.add_argument("-l", "--limit", type=int, help="Maximum number of log entries to return")
        show_parser.add_argument("-o", "--offset", type=int, help="Offset for pagination")
        show_parser.set_defaults(command_cls=LogsShow)

        # logs set-level
        set_level_parser = logs_subparsers.add_parser("set-level", help="Set log level filter")
        set_level_parser.add_argument("filter", help="Log level filter (error, warn, info, debug, trace)")
        set_level_parser.set_defaults(command_cls=LogsSetLevel)


class LogsShow(SubCommand):
    """Show device logs."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.limit is not None:
            params["limit"] = args.limit
        if args.offset is not None:
            params["offset"] = args.offset
        await cls.send_command_jrpc_message(args.target, args.port, "logs_get", params, args.verbose, args.quiet)


class LogsSetLevel(SubCommand):
    """Set log level filter."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target, args.port, "logs_set_level", {"filter": args.filter}, args.verbose, args.quiet
        )
