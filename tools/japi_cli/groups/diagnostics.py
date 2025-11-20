"""Diagnostics commands group - device diagnostics retrieval."""

from japi_cli_base import CommandGroup, SubCommand


class DiagnosticsGroup(CommandGroup):
    """Diagnostics command group for diagnostic operations."""

    name = "diagnostics"
    description = "Device diagnostics operations"

    @staticmethod
    def register_commands(subparsers):
        """Register diagnostics commands."""
        diagnostics_parser = subparsers.add_parser(
            DiagnosticsGroup.name,
            help=DiagnosticsGroup.description,
            description=DiagnosticsGroup.description,
        )
        diagnostics_subparsers = diagnostics_parser.add_subparsers(dest="diagnostics_action", required=True)

        # diagnostics show
        show_parser = diagnostics_subparsers.add_parser("show", help="Show device diagnostics")
        show_parser.add_argument("-n", "--namespace", help="Filter by namespace")
        show_parser.set_defaults(command_cls=DiagnosticsShow)


class DiagnosticsShow(SubCommand):
    """Show device diagnostics."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.namespace:
            params["namespace"] = args.namespace
        await cls.send_command_jrpc_message(args.target, args.port, "diagnostics_get", params, args.verbose, args.quiet)
