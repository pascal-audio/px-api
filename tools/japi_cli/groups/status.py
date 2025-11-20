"""Status commands group - device runtime status queries."""

from japi_cli_base import CommandGroup, SubCommand


class StatusGroup(CommandGroup):
    """Status command group for runtime status operations."""

    name = "status"
    description = "Device runtime status queries"

    @staticmethod
    def register_commands(subparsers):
        """Register status commands."""
        status_parser = subparsers.add_parser(
            StatusGroup.name,
            help=StatusGroup.description,
            description=StatusGroup.description,
        )
        status_subparsers = status_parser.add_subparsers(dest="status_action", required=True)

        # status get
        _register_status_get(status_subparsers)

        # status subscribe
        subscribe_parser = status_subparsers.add_parser(
            "subscribe", help="Subscribe to status updates (JSON-RPC: status_subscribe)"
        )
        subscribe_parser.add_argument("paths", nargs="*", help="Specific paths to subscribe to (empty for all)")
        subscribe_parser.add_argument("-t", "--timeout", type=int, help="Timeout in seconds (default: no timeout)")
        subscribe_parser.set_defaults(command_cls=StatusSubscribe)


def _register_status_get(subparsers):
    """Register status get commands."""
    get_parser = subparsers.add_parser("get", help="Show device status (JSON-RPC: status_get with path parameter)")
    get_subparsers = get_parser.add_subparsers(dest="status_target", required=True)

    # status get all
    all_parser = get_subparsers.add_parser("all", help="Show all device status (JSON-RPC: status_get_all)")
    all_parser.set_defaults(command_cls=StatusShowAll)

    # status get info
    info_parser = get_subparsers.add_parser("info", help="Show device info (serial, model, vendor) (path: /info)")
    info_parser.set_defaults(command_cls=StatusShowInfo)

    # status get state
    state_parser = get_subparsers.add_parser("state", help="Show device state (power, find-me) (path: /state)")
    state_parser.set_defaults(command_cls=StatusShowState)

    # status get network
    network_parser = get_subparsers.add_parser("network", help="Show network status (path: /network)")
    network_parser.set_defaults(command_cls=StatusShowNetwork)

    # status get audio
    audio_parser = get_subparsers.add_parser("audio", help="Show audio status (path: /audio)")
    audio_parser.set_defaults(command_cls=StatusShowAudio)

    # status get firmware
    firmware_parser = get_subparsers.add_parser("firmware", help="Show firmware status (path: /firmware)")
    firmware_parser.set_defaults(command_cls=StatusShowFirmware)


class StatusShowAll(SubCommand):
    """Show all device status."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(args.target, args.port, "status_get_all", {}, args.verbose, args.quiet)


class StatusShowInfo(SubCommand):
    """Show device info (serial, model, vendor)."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target, args.port, "status_get", {"path": "/info"}, args.verbose, args.quiet
        )


class StatusShowState(SubCommand):
    """Show device state (power, find-me)."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target, args.port, "status_get", {"path": "/state"}, args.verbose, args.quiet
        )


class StatusShowNetwork(SubCommand):
    """Show network status."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target, args.port, "status_get", {"path": "/network"}, args.verbose, args.quiet
        )


class StatusShowAudio(SubCommand):
    """Show audio status."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target, args.port, "status_get", {"path": "/audio"}, args.verbose, args.quiet
        )


class StatusShowFirmware(SubCommand):
    """Show firmware status."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target, args.port, "status_get", {"path": "/firmware"}, args.verbose, args.quiet
        )


class StatusSubscribe(SubCommand):
    """Subscribe to status updates."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.paths:
            params["paths"] = args.paths

        await cls.send_subscribe_jrpc_message(
            "status_subscribe",
            args.target,
            args.port,
            params,
            args.verbose,
            timeout=args.timeout if hasattr(args, "timeout") else None,
        )
