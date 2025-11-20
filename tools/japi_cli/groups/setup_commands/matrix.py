"""Setup commands - Auto-generated module split."""

from japi_cli_base import SubCommand

__all__ = [
    "GetSummingMatrix",
    "GetSummingMatrixRow",
    "GetSummingMatrixCell",
    "SetSummingMatrixCell",
]

# SUMMING MATRIX COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetSummingMatrix(SubCommand):
    """Get entire summing matrix."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, "/audio/output/summing_matrix", args.verbose, args.quiet
        )


class GetSummingMatrixRow(SubCommand):
    """Get summing matrix row (legacy - for detailed access)."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/summing_matrix", args.verbose, args.quiet
        )


class GetSummingMatrixCell(SubCommand):
    """Get summing matrix cell (legacy - for detailed access)."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.output_channel}/summing_matrix/{args.input_channel}",
            args.verbose,
            args.quiet,
        )


class SetSummingMatrixCell(SubCommand):
    """Set summing matrix cell."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.output_channel}/summing_matrix/{args.input_channel}",
            {"gain": args.value},
            args.verbose,
            args.quiet,
        )


# ==============================================================================
