"""Metrics commands group - device metrics queries and subscriptions."""

from japi_cli_base import CommandGroup, SubCommand


class MetricsGroup(CommandGroup):
    """Metrics command group for device metrics operations."""

    name = "metrics"
    description = "Device metrics operations"

    @staticmethod
    def register_commands(subparsers):
        """Register metrics commands."""
        metrics_parser = subparsers.add_parser(
            MetricsGroup.name,
            help=MetricsGroup.description,
            description=MetricsGroup.description,
        )
        metrics_subparsers = metrics_parser.add_subparsers(dest="metrics_action", required=True)

        # metrics show
        show_parser = metrics_subparsers.add_parser("show", help="Show current device metrics")
        show_parser.set_defaults(command_cls=MetricsShow)

        # metrics subscribe
        subscribe_parser = metrics_subparsers.add_parser("subscribe", help="Subscribe to device metrics updates")
        subscribe_parser.add_argument(
            "-i", "--interval", type=int, default=1000, help="Update interval in milliseconds"
        )
        subscribe_parser.add_argument("-t", "--timeout", type=int, help="Timeout in seconds (default: no timeout)")
        subscribe_parser.set_defaults(command_cls=MetricsSubscribe)


class MetricsShow(SubCommand):
    """Show current device metrics."""

    @classmethod
    async def run(cls, args):
        # Note: metrics_get doesn't exist in current API - we use metrics_subscribe with immediate close
        # or we could add a metrics_get method. For now, inform user to use subscribe.
        import sys

        from colorama import Fore, Style

        if not args.quiet:
            print(
                f"{Fore.YELLOW}Note: One-time metrics read not yet implemented. Use 'metrics subscribe' instead.{Style.RESET_ALL}"
            )
            sys.exit(1)


class MetricsSubscribe(SubCommand):
    """Subscribe to device metrics updates."""

    @classmethod
    async def run(cls, args):
        params = {"interval": args.interval}

        await cls.send_subscribe_jrpc_message(
            "metrics_subscribe",
            args.target,
            args.port,
            params,
            args.verbose,
            timeout=args.timeout if hasattr(args, "timeout") else None,
        )
