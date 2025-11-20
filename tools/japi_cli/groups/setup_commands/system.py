"""Setup commands - Auto-generated module split."""

from japi_cli_base import SubCommand

__all__ = [
    "GetInstall",
    "GetGenerator",
    "GetGpio",
    "SetSpeakerName",
    "SetSpeakerPrimarySrc",
    "SetSpeakerFallbackSrc",
    "SetSpeakerUserMute",
    "SetSpeakerUserGain",
    "SetSpeakerUserPolarity",
    "SetSpeakerUserDelay",
    "SetSpeakerUserHpf",
    "SetSpeakerUserGeneratorMix",
    "SetSpeakerUserEqBypass",
    "SetSpeakerArrayGain",
    "SetSpeakerArrayPolarity",
    "SetSpeakerArrayDelay",
    "SetSpeakerArrayEqBypass",
    "GetWays",
    "SetWays",
    "GetDigitalOutput",
    "GetNetworkOutput",
    "GetNetworkOutputChannel",
    "SetNetworkOutputChannel",
    "GetNetworkLan",
    "SetNetworkLan",
    "GetNetworkConfig",
    "SetNetworkConfig",
    "GetPower",
    "SetPower",
]

# INSTALL INFO COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetInstall(SubCommand):
    """Get system information."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(args.target, args.port, "/install", args.verbose, args.quiet)


# ==============================================================================
# GENERATOR COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetGenerator(SubCommand):
    """Get generator configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, "/audio/input/generator", args.verbose, args.quiet
        )


# ==============================================================================
# GPIO COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetGpio(SubCommand):
    """Get all GPIO configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(args.target, args.port, "/gpio", args.verbose, args.quiet)


# ==============================================================================
# ADDITIONAL SPEAKER MAIN COMMAND IMPLEMENTATIONS
# ==============================================================================


class SetSpeakerName(SubCommand):
    """Set speaker channel name."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}",
            {"name": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerPrimarySrc(SubCommand):
    """Set primary audio source."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}",
            {"primary_src": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerFallbackSrc(SubCommand):
    """Set fallback audio source."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}",
            {"fallback_src": args.value},
            args.verbose,
            args.quiet,
        )


# ==============================================================================
# ADDITIONAL SPEAKER USER LAYER IMPLEMENTATIONS
# ==============================================================================


class SetSpeakerUserMute(SubCommand):
    """Set user layer mute."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user",
            {"mute": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerUserGain(SubCommand):
    """Set user layer gain."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user",
            {"gain": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerUserPolarity(SubCommand):
    """Set user layer polarity."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user",
            {"polarity": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerUserDelay(SubCommand):
    """Set user layer delay."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user",
            {"delay": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerUserHpf(SubCommand):
    """Set high-pass filter."""

    @classmethod
    async def run(cls, args):
        params = {"hpf": args.type}
        if args.frequency:
            params["hpf_freq"] = args.frequency
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/user", params, args.verbose, args.quiet
        )


class SetSpeakerUserGeneratorMix(SubCommand):
    """Set generator mix mode."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user",
            {"generator_mix": args.mode},
            args.verbose,
            args.quiet,
        )


class SetSpeakerUserEqBypass(SubCommand):
    """Set user EQ bypass."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/user/eq",
            {"bypass": args.value},
            args.verbose,
            args.quiet,
        )


# ==============================================================================
# ADDITIONAL SPEAKER ARRAY LAYER IMPLEMENTATIONS
# ==============================================================================


class SetSpeakerArrayGain(SubCommand):
    """Set array layer gain."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array",
            {"gain": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerArrayPolarity(SubCommand):
    """Set array layer polarity."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array",
            {"polarity": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerArrayDelay(SubCommand):
    """Set array layer delay."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array",
            {"delay": args.value},
            args.verbose,
            args.quiet,
        )


class SetSpeakerArrayEqBypass(SubCommand):
    """Set array EQ bypass."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_set_jrpc_message(
            args.target,
            args.port,
            f"/audio/output/speaker/{args.channel}/array/eq",
            {"bypass": args.value},
            args.verbose,
            args.quiet,
        )


# ==============================================================================
# WAYS COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetWays(SubCommand):
    """Get speaker way mapping."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, "/audio/output/speaker_ways", args.verbose, args.quiet
        )


class SetWays(SubCommand):
    """Set speaker way mapping."""

    @classmethod
    async def run(cls, args):
        import sys

        from colorama import Fore, Style

        from japi_cli_base import SPEAKER_WAYS

        # Parse from command line format: "WAY:ID WAY:ID ..."
        # Example: "HF:1 LF:1 FR:2 FR:3" means:
        #   Channel 1 -> Speaker 1 HF
        #   Channel 2 -> Speaker 1 LF
        #   Channel 3 -> Speaker 2 FR
        #   Channel 4 -> Speaker 3 FR
        try:
            parts = args.ways.split()
            speaker_ways = []

            for part in parts:
                if ":" not in part:
                    print(
                        f"{Fore.RED}Error: Invalid format '{part}'. Expected 'WAY:ID'{Style.RESET_ALL}", file=sys.stderr
                    )
                    return

                way_str, id_str = part.split(":", 1)

                # Validate way
                if way_str not in SPEAKER_WAYS:
                    print(
                        f"{Fore.RED}Error: Invalid way '{way_str}'. Must be one of: {', '.join(SPEAKER_WAYS)}{Style.RESET_ALL}",
                        file=sys.stderr,
                    )
                    return

                # Validate ID
                try:
                    speaker_id = int(id_str)
                    if speaker_id < 1:
                        print(f"{Fore.RED}Error: Speaker ID must be >= 1{Style.RESET_ALL}", file=sys.stderr)
                        return
                except ValueError:
                    print(
                        f"{Fore.RED}Error: Invalid speaker ID '{id_str}'. Must be an integer{Style.RESET_ALL}",
                        file=sys.stderr,
                    )
                    return

                speaker_ways.append({"id": speaker_id, "way": way_str})

            if not speaker_ways:
                print(f"{Fore.RED}Error: No speaker ways specified{Style.RESET_ALL}", file=sys.stderr)
                return

        except Exception as e:
            print(f"{Fore.RED}Error parsing speaker ways: {e}{Style.RESET_ALL}", file=sys.stderr)
            return

        # Send the array directly as the value
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, "/audio/output/speaker_ways", speaker_ways, args.verbose, args.quiet
        )


# ==============================================================================
# OUTPUT COMMAND IMPLEMENTATIONS (speaker, digital, network)
# ==============================================================================


class GetDigitalOutput(SubCommand):
    """Get digital output channel."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/digital/{args.channel}", args.verbose, args.quiet
        )


class GetNetworkOutput(SubCommand):
    """Get network output channel."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/network/{args.channel}", args.verbose, args.quiet
        )


# ==============================================================================
# NETWORK OUTPUT COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetNetworkOutputChannel(SubCommand):
    """Get network output channel."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/network/{args.channel}", args.verbose, args.quiet
        )


class SetNetworkOutputChannel(SubCommand):
    """Set network output channel."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.source:
            params["source"] = args.source
        if args.name:
            params["name"] = args.name
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/audio/output/network/{args.channel}", params, args.verbose, args.quiet
        )


# ==============================================================================
# LAN COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetLan(SubCommand):
    """Get LAN configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(args.target, args.port, "/lan", args.verbose, args.quiet)


class SetLan(SubCommand):
    """Set LAN configuration."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.mode:
            params["mode"] = args.mode
        if args.ip:
            params["ip"] = args.ip
        if args.subnet:
            params["subnet"] = args.subnet
        if args.gateway:
            params["gateway"] = args.gateway
        if args.dns:
            params["dns"] = args.dns
        await cls.send_setup_set_jrpc_message(args.target, args.port, "/lan", params, args.verbose, args.quiet)


# ==============================================================================
# NETWORK CONFIG COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetNetworkConfig(SubCommand):
    """Get network configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(args.target, args.port, "/network", args.verbose, args.quiet)


class GetNetworkLan(SubCommand):
    """Get LAN interface configuration."""

    @classmethod
    async def run(cls, args):
        interface_name = f"lan{args.interface}"
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/network/{interface_name}_setup", args.verbose, args.quiet
        )


class SetNetworkConfig(SubCommand):
    """Set network configuration."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.mode:
            params["mode"] = args.mode
        await cls.send_setup_set_jrpc_message(args.target, args.port, "/network", params, args.verbose, args.quiet)


class SetNetworkLan(SubCommand):
    """Set LAN interface configuration."""

    @classmethod
    async def run(cls, args):
        interface_name = f"lan{args.interface}"
        params = {}
        if args.mode:
            params["mode"] = args.mode
        if args.ip:
            params["ip"] = args.ip
        if args.subnet:
            params["subnet"] = args.subnet
        if args.gateway:
            params["gateway"] = args.gateway
        if args.dns:
            params["dns"] = args.dns
        await cls.send_setup_set_jrpc_message(
            args.target, args.port, f"/network/{interface_name}_setup", params, args.verbose, args.quiet
        )


# ==============================================================================
# POWER MANAGEMENT COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetPower(SubCommand):
    """Get power management configuration."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(args.target, args.port, "/power", args.verbose, args.quiet)


class SetPower(SubCommand):
    """Set power management configuration."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "mode") and args.mode:
            params["power_on_mode"] = args.mode
        if hasattr(args, "standby_time") and args.standby_time is not None:
            params["standby_time"] = args.standby_time
        if hasattr(args, "mute_time") and args.mute_time is not None:
            params["mute_time"] = args.mute_time
        if hasattr(args, "fuse_protection") and args.fuse_protection:
            params["fuse_protection"] = args.fuse_protection
        await cls.send_setup_set_jrpc_message(args.target, args.port, "/power", params, args.verbose, args.quiet)


# ==============================================================================
