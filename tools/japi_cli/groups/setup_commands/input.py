"""Setup commands - Auto-generated module split."""

from japi_cli_base import SubCommand

__all__ = [
    "GetInputConfig",
    "GetInputAnalog",
    "GetInputDigital",
    "GetInputNetwork",
    "GetInputChannel",
    "GetInputGain",
    "GetInputDelay",
    "GetInputMute",
    "SetInputGain",
    "SetInputDelay",
    "SetInputMute",
]

# INPUT COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetInputConfig(SubCommand):
    """Get input configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(args.target, args.port, "/audio/input/config", args.verbose, args.quiet)


class GetInputAnalog(SubCommand):
    """Get analog input channel."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/analog/{args.channel}", args.verbose, args.quiet
        )


class GetInputDigital(SubCommand):
    """Get digital input channel."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/digital/{args.channel}", args.verbose, args.quiet
        )


class GetInputNetwork(SubCommand):
    """Get network (AoIP) input channel."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/network/{args.channel}", args.verbose, args.quiet
        )


class GetInputChannel(SubCommand):
    """Get input channel (legacy - used by SET commands with analog/1 format)."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/{args.channel}", args.verbose, args.quiet
        )


class GetInputGain(SubCommand):
    """Get input gain."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/{args.channel}", args.verbose, args.quiet
        )


class GetInputDelay(SubCommand):
    """Get input delay."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/{args.channel}", args.verbose, args.quiet
        )


class GetInputMute(SubCommand):
    """Get input mute."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/input/{args.channel}", args.verbose, args.quiet
        )


class SetInputGain(SubCommand):
    """Set input gain."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/input/{args.channel}", {"gain": args.value}, args.verbose, args.quiet
        )


class SetInputDelay(SubCommand):
    """Set input delay."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/input/{args.channel}", {"delay": args.value}, args.verbose, args.quiet
        )


class SetInputMute(SubCommand):
    """Set input mute."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/input/{args.channel}",
            {"mute": args.value},
            args.verbose,
            args.quiet,
        )


# ==============================================================================
