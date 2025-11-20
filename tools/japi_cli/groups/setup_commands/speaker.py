"""Setup commands - Auto-generated module split."""

from japi_cli_base import SubCommand

__all__ = [
    "GetSpeakerChannel",
    "GetSpeakerGain",
    "GetSpeakerMute",
    "GetSpeakerDelay",
    "SetSpeakerGain",
    "SetSpeakerMute",
    "SetSpeakerDelay",
    "GetSpeakerUserFir",
    "SetSpeakerUserFir",
    "GetSpeakerUserEqAll",
    "GetSpeakerUserEqBand",
    "SetSpeakerUserEqBand",
    "GetSpeakerArrayFir",
    "SetSpeakerArrayFir",
    "SetSpeakerArrayCrossover",
    "GetSpeakerArrayEqAll",
    "GetSpeakerArrayEqBand",
    "SetSpeakerArrayEqBand",
    "GetSpeakerPresetFir",
    "GetSpeakerPresetCrossover",
    "GetSpeakerPresetEqAll",
    "GetSpeakerPresetEqBand",
    "GetSpeakerPresetLimiterPeak",
    "GetSpeakerPresetLimiterRms",
    "GetSpeakerPresetLimiterClip",
]

# SPEAKER MAIN LAYER COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetSpeakerChannel(SubCommand):
    """Get speaker channel configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}", args.verbose, args.quiet
        )


class GetSpeakerGain(SubCommand):
    """Get speaker gain."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}", args.verbose, args.quiet
        )


class GetSpeakerMute(SubCommand):
    """Get speaker mute state."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}", args.verbose, args.quiet
        )


class GetSpeakerDelay(SubCommand):
    """Get speaker delay."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}", args.verbose, args.quiet
        )


class SetSpeakerGain(SubCommand):
    """Set speaker gain."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}",
            {"gain": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerMute(SubCommand):
    """Set speaker mute state."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}",
            {"mute": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerDelay(SubCommand):
    """Set speaker delay."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}",
            {"delay": args.value},
            args.verbose,
            args.quiet,
        )


# ==============================================================================
# SPEAKER USER LAYER COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetSpeakerUserFir(SubCommand):
    """Get user FIR filter."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/user/fir", args.verbose, args.quiet
        )


class SetSpeakerUserFir(SubCommand):
    """Set user FIR filter."""

    @classmethod
    async def run(cls, args):
        params = {}

        if args.file:
            try:
                with open(args.file) as f:
                    coeffs = [float(line.strip()) for line in f if line.strip()]
                params["coefficients"] = coeffs
            except Exception as e:
                print(f"Error reading FIR coefficients file: {e}")
                return

        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass

        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/user/fir", params, args.verbose, args.quiet
        )


class GetSpeakerUserEqAll(SubCommand):
    """Get all user EQ bands."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/user/eq", args.verbose, args.quiet
        )


class GetSpeakerUserEqBand(SubCommand):
    """Get specific user EQ band."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user/eq/bands/{args.band}",
            args.verbose,
            args.quiet,
        )


class SetSpeakerUserEqBand(SubCommand):
    """Set specific user EQ band."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass
        if args.frequency is not None:
            params["frequency"] = args.frequency
        if args.gain is not None:
            params["gain"] = args.gain
        if args.q is not None:
            params["q"] = args.q
        if args.type is not None:
            params["kind"] = args.type  # Note: API uses "kind" not "filter_type"

        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user/eq/bands/{args.band}",
            params,
            args.verbose,
            args.quiet,
        )


# ==============================================================================
# SPEAKER ARRAY LAYER COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetSpeakerArrayFir(SubCommand):
    """Get array FIR filter."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/array/fir", args.verbose, args.quiet
        )


class SetSpeakerArrayFir(SubCommand):
    """Set array FIR filter."""

    @classmethod
    async def run(cls, args):
        params = {}

        if args.file:
            try:
                with open(args.file) as f:
                    coeffs = [float(line.strip()) for line in f if line.strip()]
                params["coefficients"] = coeffs
            except Exception as e:
                print(f"Error reading FIR coefficients file: {e}")
                return

        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass

        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/array/fir", params, args.verbose, args.quiet
        )


class SetSpeakerArrayCrossover(SubCommand):
    """Set array crossover."""

    @classmethod
    async def run(cls, args):
        params = {"frequency": args.frequency, "filter_type": args.type}
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array/crossover",
            params,
            args.verbose,
            args.quiet,
        )


class GetSpeakerArrayEqAll(SubCommand):
    """Get all array EQ bands."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/array/eq", args.verbose, args.quiet
        )


class GetSpeakerArrayEqBand(SubCommand):
    """Get specific array EQ band."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array/eq/bands/{args.band}",
            args.verbose,
            args.quiet,
        )


class SetSpeakerArrayEqBand(SubCommand):
    """Set specific array EQ band."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass
        if args.frequency is not None:
            params["frequency"] = args.frequency
        if args.gain is not None:
            params["gain"] = args.gain
        if args.q is not None:
            params["q"] = args.q
        if args.type is not None:
            params["kind"] = args.type  # Note: API uses "kind" not "filter_type"

        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array/eq/bands/{args.band}",
            params,
            args.verbose,
            args.quiet,
        )


# ==============================================================================
# SPEAKER PRESET LAYER COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetSpeakerPresetFir(SubCommand):
    """Get preset FIR filter."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset/fir", args.verbose, args.quiet
        )


class GetSpeakerPresetCrossover(SubCommand):
    """Get preset crossover."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset/crossover", args.verbose, args.quiet
        )


class GetSpeakerPresetEqAll(SubCommand):
    """Get all preset EQ bands."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset/eq", args.verbose, args.quiet
        )


class GetSpeakerPresetEqBand(SubCommand):
    """Get specific preset EQ band."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/eq/bands/{args.band}",
            args.verbose,
            args.quiet,
        )


class GetSpeakerPresetLimiterPeak(SubCommand):
    """Get peak limiter."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/peak_limiter",
            args.verbose,
            args.quiet,
        )


class GetSpeakerPresetLimiterRms(SubCommand):
    """Get RMS limiter."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset/rms_limiter", args.verbose, args.quiet
        )


class GetSpeakerPresetLimiterClip(SubCommand):
    """Get clip limiter."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/clip_limiter",
            args.verbose,
            args.quiet,
        )


# ==============================================================================
