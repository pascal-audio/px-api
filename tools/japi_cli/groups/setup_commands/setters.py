"""Setup commands - Auto-generated module split."""

from japi_cli_base import SubCommand

__all__ = [
    "SetInputAnalog",
    "SetInputDigital",
    "SetInputNetwork",
    "SetInputConfig",
    "SetGenerator",
    "SetSpeakerOutput",
    "SetDigitalOutput",
    "SetNetworkOutput",
    "SetUser",
    "SetUserEq",
    "SetArray",
    "SetArrayFir",
    "SetArrayEq",
    "SetPreset",
    "SetPresetFir",
    "SetPresetCrossover",
    "SetPresetEq",
    "SetPresetLimiterPeak",
    "SetPresetLimiterRms",
    "SetPresetLimiterClip",
    "SetSummingMatrix",
    "SetInstall",
    "SetGpio",
]

# FLATTENED SET COMMAND IMPLEMENTATIONS (matching japi_cli_set.py parameters)
# ==============================================================================


class SetInputAnalog(SubCommand):
    """Set analog input channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["name"] = args.name
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "delay") and args.delay is not None:
            params["delay"] = args.delay
        if hasattr(args, "mute") and args.mute:
            params["mute"] = args.mute
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/input/analog/{args.channel}", params, args.verbose, args.quiet
        )


class SetInputDigital(SubCommand):
    """Set digital input channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["name"] = args.name
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "delay") and args.delay is not None:
            params["delay"] = args.delay
        if hasattr(args, "mute") and args.mute:
            params["mute"] = args.mute
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/input/digital/{args.channel}", params, args.verbose, args.quiet
        )


class SetInputNetwork(SubCommand):
    """Set network (AoIP) input channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["name"] = args.name
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "delay") and args.delay is not None:
            params["delay"] = args.delay
        if hasattr(args, "mute") and args.mute:
            params["mute"] = args.mute
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/input/network/{args.channel}", params, args.verbose, args.quiet
        )


class SetInputConfig(SubCommand):
    """Set input configuration."""

    @classmethod
    async def run(cls, args):
        params = {"input_switch": args.value}
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, "/audio/input/config", params, args.verbose, args.quiet
        )


class SetGenerator(SubCommand):
    """Set generator configuration."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "kind") and args.kind:
            params["kind"] = args.kind
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "frequency") and args.frequency is not None:
            params["frequency"] = args.frequency
        if hasattr(args, "lpf_freq") and args.lpf_freq is not None:
            params["lpf_freq"] = args.lpf_freq
        if hasattr(args, "hpf_freq") and args.hpf_freq is not None:
            params["hpf_freq"] = args.hpf_freq
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, "/audio/input/generator", params, args.verbose, args.quiet
        )


class SetSpeakerOutput(SubCommand):
    """Set speaker output channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["name"] = args.name
        if hasattr(args, "primary_src") and args.primary_src:
            params["primary_src"] = args.primary_src
        if hasattr(args, "fallback_src") and args.fallback_src:
            params["fallback_src"] = args.fallback_src
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}", params, args.verbose, args.quiet
        )


class SetDigitalOutput(SubCommand):
    """Set digital output channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["name"] = args.name
        if hasattr(args, "source") and args.source:
            params["source"] = args.source
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/digital/{args.channel}", params, args.verbose, args.quiet
        )


class SetNetworkOutput(SubCommand):
    """Set network output channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["name"] = args.name
        if hasattr(args, "source") and args.source:
            params["source"] = args.source
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/network/{args.channel}", params, args.verbose, args.quiet
        )


class SetUser(SubCommand):
    """Set user processing."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "mute") and args.mute:
            params["mute"] = args.mute
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "polarity") and args.polarity is not None:
            params["polarity"] = args.polarity
        if hasattr(args, "delay") and args.delay is not None:
            params["delay"] = args.delay
        if hasattr(args, "hpf_kind") and args.hpf_kind:
            params["hpf"] = args.hpf_kind
        if hasattr(args, "hpf_freq") and args.hpf_freq is not None:
            params["hpf_freq"] = args.hpf_freq
        if hasattr(args, "generator_mix") and args.generator_mix:
            params["generator_mix"] = args.generator_mix
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/user", params, args.verbose, args.quiet
        )


class SetUserEq(SubCommand):
    """Set user EQ (whole EQ or specific band)."""

    @classmethod
    async def run(cls, args):
        if hasattr(args, "band") and args.band:
            # Set specific band
            params = {}
            if hasattr(args, "bypass") and args.bypass is not None:
                params["bypass"] = args.bypass
            if hasattr(args, "kind") and args.kind:
                params["kind"] = args.kind
            if hasattr(args, "gain") and args.gain is not None:
                params["gain"] = args.gain
            if hasattr(args, "frequency") and args.frequency is not None:
                params["frequency"] = args.frequency
            if hasattr(args, "q") and args.q is not None:
                params["q"] = args.q
            await cls.send_setup_set_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/user/eq/bands/{args.band}",
                params,
                args.verbose,
                args.quiet,
            )
        else:
            # Set EQ bypass
            params = {}
            if hasattr(args, "bypass") and args.bypass is not None:
                params["bypass"] = args.bypass
            await cls.send_setup_set_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/user/eq",
                params,
                args.verbose,
                args.quiet,
            )


class SetArray(SubCommand):
    """Set array processing."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "polarity") and args.polarity is not None:
            params["polarity"] = args.polarity
        if hasattr(args, "delay") and args.delay is not None:
            params["delay"] = args.delay
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/array", params, args.verbose, args.quiet
        )


class SetArrayFir(SubCommand):
    """Set array FIR filter."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "file") and args.file:
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


class SetArrayEq(SubCommand):
    """Set array EQ (whole EQ or specific band)."""

    @classmethod
    async def run(cls, args):
        if hasattr(args, "band") and args.band:
            # Set specific band
            params = {}
            if hasattr(args, "bypass") and args.bypass is not None:
                params["bypass"] = args.bypass
            if hasattr(args, "kind") and args.kind:
                params["kind"] = args.kind
            if hasattr(args, "gain") and args.gain is not None:
                params["gain"] = args.gain
            if hasattr(args, "frequency") and args.frequency is not None:
                params["frequency"] = args.frequency
            if hasattr(args, "q") and args.q is not None:
                params["q"] = args.q
            await cls.send_setup_set_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/array/eq/bands/{args.band}",
                params,
                args.verbose,
                args.quiet,
            )
        else:
            # Set EQ bypass
            params = {}
            if hasattr(args, "bypass") and args.bypass is not None:
                params["bypass"] = args.bypass
            await cls.send_setup_set_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/array/eq",
                params,
                args.verbose,
                args.quiet,
            )


class SetPreset(SubCommand):
    """Set preset processing."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "drive_mode") and args.drive_mode:
            params["drive"] = args.drive_mode
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "polarity") and args.polarity is not None:
            params["polarity"] = args.polarity
        if hasattr(args, "delay") and args.delay is not None:
            params["delay"] = args.delay
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset", params, args.verbose, args.quiet
        )


class SetPresetFir(SubCommand):
    """Set preset FIR filter."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "file") and args.file:
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
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset/fir", params, args.verbose, args.quiet
        )


class SetPresetCrossover(SubCommand):
    """Set preset crossover."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "gain") and args.gain is not None:
            params["gain"] = args.gain
        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass
        if hasattr(args, "lpf_kind") and args.lpf_kind:
            params["lpf"] = args.lpf_kind
        if hasattr(args, "lpf_freq") and args.lpf_freq is not None:
            params["lpf_freq"] = args.lpf_freq
        if hasattr(args, "hpf_kind") and args.hpf_kind:
            params["hpf"] = args.hpf_kind
        if hasattr(args, "hpf_freq") and args.hpf_freq is not None:
            params["hpf_freq"] = args.hpf_freq
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/crossover",
            params,
            args.verbose,
            args.quiet,
        )


class SetPresetEq(SubCommand):
    """Set preset EQ (whole EQ or specific band)."""

    @classmethod
    async def run(cls, args):
        if hasattr(args, "band") and args.band:
            # Set specific band
            params = {}
            if hasattr(args, "bypass") and args.bypass is not None:
                params["bypass"] = args.bypass
            if hasattr(args, "kind") and args.kind:
                params["kind"] = args.kind
            if hasattr(args, "gain") and args.gain is not None:
                params["gain"] = args.gain
            if hasattr(args, "frequency") and args.frequency is not None:
                params["frequency"] = args.frequency
            if hasattr(args, "q") and args.q is not None:
                params["q"] = args.q
            await cls.send_setup_set_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/preset/eq/bands/{args.band}",
                params,
                args.verbose,
                args.quiet,
            )
        else:
            # Set EQ bypass
            params = {}
            if hasattr(args, "bypass") and args.bypass is not None:
                params["bypass"] = args.bypass
            await cls.send_setup_set_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/preset/eq",
                params,
                args.verbose,
                args.quiet,
            )


class SetPresetLimiterPeak(SubCommand):
    """Set preset peak limiter."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass
        if hasattr(args, "auto") and args.auto is not None:
            params["auto"] = args.auto
        if hasattr(args, "threshold") and args.threshold is not None:
            params["threshold"] = args.threshold
        if hasattr(args, "attack") and args.attack is not None:
            params["attack"] = args.attack
        if hasattr(args, "release") and args.release is not None:
            params["release"] = min(args.release, 11.8)
        if hasattr(args, "hold") and args.hold is not None:
            params["hold"] = args.hold
        if hasattr(args, "knee") and args.knee is not None:
            params["knee"] = args.knee
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/peak_limiter",
            params,
            args.verbose,
            args.quiet,
        )


class SetPresetLimiterRms(SubCommand):
    """Set preset RMS limiter."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass
        if hasattr(args, "threshold") and args.threshold is not None:
            params["threshold"] = args.threshold
        if hasattr(args, "attack") and args.attack is not None:
            params["attack"] = args.attack
        if hasattr(args, "release") and args.release is not None:
            params["release"] = min(args.release, 11.8)
        if hasattr(args, "hold") and args.hold is not None:
            params["hold"] = args.hold
        if hasattr(args, "knee") and args.knee is not None:
            params["knee"] = args.knee
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/rms_limiter",
            params,
            args.verbose,
            args.quiet,
        )


class SetPresetLimiterClip(SubCommand):
    """Set preset clip limiter."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "bypass") and args.bypass is not None:
            params["bypass"] = args.bypass
        if hasattr(args, "mode") and args.mode:
            params["mode"] = args.mode
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/preset/clip_limiter",
            params,
            args.verbose,
            args.quiet,
        )


class SetSummingMatrix(SubCommand):
    """Set summing matrix configuration."""

    @classmethod
    async def run(cls, args):
        import json
        import sys

        from colorama import Fore, Style

        matrix_data = None

        if hasattr(args, "reset") and args.reset:
            # Create identity matrix (4x4)
            matrix_data = []
            for i in range(4):
                row = []
                for j in range(4):
                    row.append(1.0 if i == j else 0.0)
                matrix_data.append(row)
        elif hasattr(args, "file") and args.file:
            try:
                with open(args.file) as f:
                    matrix_data = json.load(f)
                    if not isinstance(matrix_data, list) or len(matrix_data) != 4:
                        print(f"{Fore.RED}Error: Matrix must be a 4x4 array{Style.RESET_ALL}", file=sys.stderr)
                        return
                    for row in matrix_data:
                        if not isinstance(row, list) or len(row) != 4:
                            print(
                                f"{Fore.RED}Error: Each matrix row must contain exactly 4 values{Style.RESET_ALL}",
                                file=sys.stderr,
                            )
                            return
            except FileNotFoundError:
                print(f"{Fore.RED}Error: Matrix file '{args.file}' not found{Style.RESET_ALL}", file=sys.stderr)
                return
            except json.JSONDecodeError as e:
                print(f"{Fore.RED}Error: Invalid JSON in matrix file: {e}{Style.RESET_ALL}", file=sys.stderr)
                return
        elif hasattr(args, "matrix") and args.matrix:
            try:
                matrix_data = json.loads(args.matrix)
                if not isinstance(matrix_data, list) or len(matrix_data) != 4:
                    print(f"{Fore.RED}Error: Matrix must be a 4x4 array{Style.RESET_ALL}", file=sys.stderr)
                    return
                for row in matrix_data:
                    if not isinstance(row, list) or len(row) != 4:
                        print(
                            f"{Fore.RED}Error: Each matrix row must contain exactly 4 values{Style.RESET_ALL}",
                            file=sys.stderr,
                        )
                        return
            except json.JSONDecodeError as e:
                print(f"{Fore.RED}Error: Invalid JSON in matrix string: {e}{Style.RESET_ALL}", file=sys.stderr)
                return
        else:
            print(f"{Fore.RED}Error: Must specify --file, --matrix, or --reset{Style.RESET_ALL}", file=sys.stderr)
            return

        # Send the matrix directly as the value (not wrapped in a params dict)
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, "/audio/output/summing_matrix", matrix_data, args.verbose, args.quiet
        )


class SetInstall(SubCommand):
    """Set system information."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "name") and args.name:
            params["device_name"] = args.name
        if hasattr(args, "venue_name") and args.venue_name:
            params["venue_name"] = args.venue_name
        if hasattr(args, "customer_name") and args.customer_name:
            params["customer_name"] = args.customer_name
        if hasattr(args, "asset_tag") and args.asset_tag:
            params["asset_tag"] = args.asset_tag
        if hasattr(args, "installer_name") and args.installer_name:
            params["installer_name"] = args.installer_name
        if hasattr(args, "contact_info") and args.contact_info:
            params["contact_info"] = args.contact_info
        if hasattr(args, "install_date") and args.install_date:
            params["install_date"] = args.install_date
        if hasattr(args, "install_notes") and args.install_notes:
            params["install_notes"] = args.install_notes
        if hasattr(args, "custom1") and args.custom1:
            params["custom1"] = args.custom1
        if hasattr(args, "custom2") and args.custom2:
            params["custom2"] = args.custom2
        if hasattr(args, "custom3") and args.custom3:
            params["custom3"] = args.custom3
        await cls.send_setup_set_jrpc_message(args.target, args.port, "/install", params, args.verbose, args.quiet)


class SetGpio(SubCommand):
    """Set GPIO pin configuration."""

    @classmethod
    async def run(cls, args):
        # GPIO path is /gpio with properties gpio1, gpio2, gpio3, gpio4
        # Build the property name: gpio1, gpio2, etc.
        property_name = f"gpio{args.pin}"

        # Mode is required - send as a dict with the property
        if hasattr(args, "mode") and args.mode:
            params = {property_name: args.mode}
            await cls.send_setup_set_jrpc_message(args.target, args.port, "/gpio", params, args.verbose, args.quiet)
