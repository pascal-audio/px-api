"""API commands group - version and ping."""

from japi_cli_base import CommandGroup, SubCommand


class ApiGroup(CommandGroup):
    """API command group for basic API operations."""

    name = "api"
    description = "API version and ping commands"

    @staticmethod
    def register_commands(subparsers):
        """Register API commands."""
        api_parser = subparsers.add_parser(
            ApiGroup.name,
            help=ApiGroup.description,
            description=ApiGroup.description,
        )
        api_subparsers = api_parser.add_subparsers(dest="api_action", required=True)

        # api ping
        ping_parser = api_subparsers.add_parser(
            "ping",
            help="Ping the device (JSON-RPC: api_ping)",
            description="Ping the device. Maps to JSON-RPC method: api_ping",
        )
        ping_parser.set_defaults(command_cls=ApiPing)

        # api version
        version_parser = api_subparsers.add_parser(
            "version",
            help="Get API version (JSON-RPC: api_version)",
            description="Get API version and level. Maps to JSON-RPC method: api_version",
        )
        version_parser.set_defaults(command_cls=ApiVersion)


class ApiPing(SubCommand):
    """Ping the device."""

    @classmethod
    async def run(cls, args):
        """Ping the device."""
        await cls.send_command_jrpc_message(args.target, args.port, "api_ping", {}, args.verbose, args.quiet)


class ApiVersion(SubCommand):
    """Get API version."""

    @classmethod
    async def run(cls, args):
        """Get API version from device."""
        await cls.send_command_jrpc_message(args.target, args.port, "api_version", {}, args.verbose, args.quiet)
