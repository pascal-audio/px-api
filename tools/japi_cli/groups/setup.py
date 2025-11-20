"""Setup commands group - Get and set device configuration."""

from japi_cli_base import (
    CLIP_LIMITER_MODES,
    EQ_FILTER_TYPES,
    FUSE_PROTECTION_MODES,
    GENERATOR_MIX_MODES,
    GENERATOR_TYPES,
    GPIO_PIN_TYPES,
    HPF_FILTER_TYPES,
    NETWORK_SRC_CHANNELS,
    OUTPUT_DRIVE_MODES,
    OUTPUT_SRC_CHANNELS,
    POWER_ON_MODES,
    CommandGroup,
    SubCommand,
    str2bool,
)

# Import command implementations from split modules
from .setup_commands.batch import (
    BatchApply,
    BatchCreate,
)
from .setup_commands.input import (
    GetInputAnalog,
    GetInputConfig,
    GetInputDigital,
    GetInputNetwork,
)
from .setup_commands.matrix import (
    GetSummingMatrix,
)
from .setup_commands.setters import (
    SetArray,
    SetArrayEq,
    SetArrayFir,
    SetDigitalOutput,
    SetGenerator,
    SetGpio,
    SetInputAnalog,
    SetInputConfig,
    SetInputDigital,
    SetInputNetwork,
    SetInstall,
    SetNetworkOutput,
    SetPreset,
    SetPresetCrossover,
    SetPresetEq,
    SetPresetFir,
    SetPresetLimiterClip,
    SetPresetLimiterPeak,
    SetPresetLimiterRms,
    SetSpeakerOutput,
    SetSummingMatrix,
    SetUser,
    SetUserEq,
)
from .setup_commands.speaker import (
    GetSpeakerArrayEqAll,
    GetSpeakerArrayEqBand,
    GetSpeakerArrayFir,
    GetSpeakerChannel,
    GetSpeakerDelay,
    GetSpeakerGain,
    GetSpeakerMute,
    GetSpeakerPresetCrossover,
    GetSpeakerPresetEqAll,
    GetSpeakerPresetEqBand,
    GetSpeakerPresetFir,
    GetSpeakerPresetLimiterClip,
    GetSpeakerPresetLimiterPeak,
    GetSpeakerPresetLimiterRms,
    GetSpeakerUserEqAll,
    GetSpeakerUserEqBand,
    GetSpeakerUserFir,
    SetSpeakerArrayCrossover,
    SetSpeakerArrayEqBand,
    SetSpeakerArrayFir,
    SetSpeakerDelay,
    SetSpeakerGain,
    SetSpeakerMute,
    SetSpeakerUserEqBand,
    SetSpeakerUserFir,
)
from .setup_commands.system import (
    GetDigitalOutput,
    GetGenerator,
    GetGpio,
    GetInstall,
    GetNetworkConfig,
    GetNetworkLan,
    GetNetworkOutput,
    GetNetworkOutputChannel,
    GetPower,
    GetWays,
    SetNetworkConfig,
    SetNetworkLan,
    SetNetworkOutputChannel,
    SetPower,
    SetSpeakerArrayDelay,
    SetSpeakerArrayEqBypass,
    SetSpeakerArrayGain,
    SetSpeakerArrayPolarity,
    SetSpeakerFallbackSrc,
    SetSpeakerName,
    SetSpeakerPrimarySrc,
    SetSpeakerUserDelay,
    SetSpeakerUserEqBypass,
    SetSpeakerUserGain,
    SetSpeakerUserGeneratorMix,
    SetSpeakerUserHpf,
    SetSpeakerUserMute,
    SetSpeakerUserPolarity,
    SetWays,
)


class SetupGroup(CommandGroup):
    """Setup command group for device configuration."""

    name = "setup"
    description = "Get and set device configuration"

    @staticmethod
    def register_commands(subparsers):
        """Register setup commands with get/set structure."""
        setup_parser = subparsers.add_parser(
            SetupGroup.name,
            help=SetupGroup.description,
            description=SetupGroup.description,
        )
        setup_subparsers = setup_parser.add_subparsers(dest="setup_action", required=True)

        # Register get, set, batch, and subscribe commands
        _register_get_commands(setup_subparsers)
        _register_set_commands(setup_subparsers)
        _register_batch_commands(setup_subparsers)

        # setup subscribe
        subscribe_parser = setup_subparsers.add_parser("subscribe", help="Subscribe to setup configuration changes")
        subscribe_parser.add_argument("paths", nargs="*", help="Specific paths to subscribe to (empty for all)")
        subscribe_parser.add_argument("-t", "--timeout", type=int, help="Timeout in seconds (default: no timeout)")
        subscribe_parser.set_defaults(command_cls=SetupSubscribe)


def _register_get_commands(subparsers):
    """Register all 'setup get' commands."""
    get_parser = subparsers.add_parser(
        "get",
        help="Get device configuration (JSON-RPC: setup_get)",
        description="Get device configuration. Maps to JSON-RPC: setup_get with path parameter (e.g., /audio/output/speaker/1/gain)",
    )
    get_subparsers = get_parser.add_subparsers(dest="setup_resource", required=True)

    # All setup configuration
    all_parser = get_subparsers.add_parser(
        "all",
        help="Get all setup configuration (JSON-RPC: setup_get_all)",
        description="Get entire device configuration. Maps to JSON-RPC: setup_get_all",
    )
    all_parser.add_argument("-f", "--flatten", action="store_true", help="Flatten json output")
    all_parser.set_defaults(command_cls=GetAll)

    # Input commands
    _register_get_input(get_subparsers)

    # Generator command
    _register_get_generator(get_subparsers)

    # Output commands (speaker, digital, network)
    _register_get_outputs(get_subparsers)

    # User processing commands (flattened)
    _register_get_user(get_subparsers)

    # Array processing commands (flattened)
    _register_get_array(get_subparsers)

    # Preset processing commands (flattened)
    _register_get_preset(get_subparsers)

    # Summing-matrix commands
    _register_get_summing_matrix(get_subparsers)

    # Ways commands
    _register_get_ways(get_subparsers)

    # GPIO commands
    _register_get_gpio(get_subparsers)

    # Network/LAN commands
    _register_get_network(get_subparsers)

    # Power management commands
    _register_get_power(get_subparsers)

    # install info commands
    _register_get_install(get_subparsers)


def _register_set_commands(subparsers):
    """Register all 'setup set' commands using FLATTENED structure matching get commands."""
    set_parser = subparsers.add_parser(
        "set",
        help="Set device configuration (JSON-RPC: setup_set)",
        description="Set device configuration. Maps to JSON-RPC: setup_set with path and value parameters (e.g., path: /audio/output/speaker/1/gain, value: -6.0)",
    )
    set_subparsers = set_parser.add_subparsers(dest="setup_resource", required=True)

    # Input commands (flattened)
    _register_set_input(set_subparsers)

    # Generator command
    _register_set_generator(set_subparsers)

    # Output commands (flattened: output-speaker, output-digital, output-network)
    _register_set_outputs(set_subparsers)

    # User processing commands (flattened)
    _register_set_user(set_subparsers)

    # Array processing commands (flattened)
    _register_set_array(set_subparsers)

    # Preset processing commands (flattened)
    _register_set_preset(set_subparsers)

    # Summing-matrix commands
    _register_set_summing_matrix(set_subparsers)

    # Ways commands
    _register_set_ways(set_subparsers)

    # Install-info commands
    _register_set_install(set_subparsers)

    # GPIO commands
    _register_set_gpio(set_subparsers)

    # Network commands (config, lan)
    _register_set_network(set_subparsers)

    # Power management commands
    _register_set_power(set_subparsers)


# ==============================================================================
# INPUT COMMANDS
# ==============================================================================


def _register_get_input(subparsers):
    """Register 'setup get input' commands."""
    input_parser = subparsers.add_parser("input", help="get input configuration")
    input_subparsers = input_parser.add_subparsers(dest="input_type", required=True)

    # setup get input config
    config_parser = input_subparsers.add_parser("config", help="Get input configuration (path: /audio/input/config)")
    config_parser.set_defaults(command_cls=GetInputConfig)

    # setup get input analog <CH>
    analog_parser = input_subparsers.add_parser(
        "analog", help="Get analog input channel (path: /audio/input/analog/{CH})"
    )
    analog_parser.add_argument("channel", type=int, choices=range(1, 5), help="Channel number (1-4)")
    analog_parser.set_defaults(command_cls=GetInputAnalog)

    # setup get input digital <CH>
    digital_parser = input_subparsers.add_parser(
        "digital", help="Get digital input channel (path: /audio/input/digital/{CH})"
    )
    digital_parser.add_argument("channel", type=int, choices=range(1, 5), help="Channel number (1-4)")
    digital_parser.set_defaults(command_cls=GetInputDigital)

    # setup get input network <CH>
    network_parser = input_subparsers.add_parser(
        "network", help="Get network (AoIP) input channel (path: /audio/input/network/{CH})"
    )
    network_parser.add_argument("channel", type=int, choices=range(1, 5), help="Channel number (1-4)")
    network_parser.set_defaults(command_cls=GetInputNetwork)


# ==============================================================================
# OUTPUT COMMANDS (speaker, digital, network outputs)
# ==============================================================================


def _register_get_outputs(subparsers):
    """Register output get commands."""
    # setup get output-speaker <CH>
    speaker_parser = subparsers.add_parser(
        "output-speaker", help="Get speaker output channel (path: /audio/output/speaker/{CH})"
    )
    speaker_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    speaker_parser.set_defaults(command_cls=GetSpeakerChannel)

    # setup get output-digital <CH>
    digital_parser = subparsers.add_parser(
        "output-digital", help="Get digital output channel (path: /audio/output/digital/{CH})"
    )
    digital_parser.add_argument("channel", type=int, choices=range(1, 5), help="Digital output channel (1-4)")
    digital_parser.set_defaults(command_cls=GetDigitalOutput)

    # setup get output-network <CH>
    network_parser = subparsers.add_parser(
        "output-network", help="Get network output channel (path: /audio/output/network/{CH})"
    )
    network_parser.add_argument("channel", type=int, choices=range(1, 5), help="Network output channel (1-4)")
    network_parser.set_defaults(command_cls=GetNetworkOutput)


def _register_get_user(subparsers):
    """Register flattened user processing commands."""
    # setup get user <CH> - get all user processing
    user_parser = subparsers.add_parser("user", help="Get user processing (path: /audio/output/speaker/{CH}/user)")
    user_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    user_parser.set_defaults(command_cls=GetUser)

    # setup get user-eq <CH> [BAND]
    eq_parser = subparsers.add_parser("user-eq", help="Get user EQ (path: /audio/output/speaker/{CH}/user/eq)")
    eq_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    eq_parser.add_argument("band", type=int, choices=range(1, 11), nargs="?", help="EQ band (1-10, optional)")
    eq_parser.set_defaults(command_cls=GetUserEq)


def _register_get_array(subparsers):
    """Register flattened array processing commands."""
    # setup get array <CH> - get all array processing
    array_parser = subparsers.add_parser("array", help="Get array processing (path: /audio/output/speaker/{CH}/array)")
    array_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    array_parser.set_defaults(command_cls=GetArray)

    # setup get array-fir <CH>
    fir_parser = subparsers.add_parser(
        "array-fir", help="Get array FIR filter (path: /audio/output/speaker/{CH}/array/fir)"
    )
    fir_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    fir_parser.set_defaults(command_cls=GetSpeakerArrayFir)

    # setup get array-eq <CH> [BAND]
    eq_parser = subparsers.add_parser("array-eq", help="Get array EQ (path: /audio/output/speaker/{CH}/array/eq)")
    eq_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    eq_parser.add_argument("band", type=int, choices=range(1, 6), nargs="?", help="EQ band (1-5, optional)")
    eq_parser.set_defaults(command_cls=GetArrayEq)


def _register_get_preset(subparsers):
    """Register flattened preset processing commands."""
    # setup get preset <CH> - get all preset processing
    preset_parser = subparsers.add_parser(
        "preset", help="Get preset processing (path: /audio/output/speaker/{CH}/preset)"
    )
    preset_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    preset_parser.set_defaults(command_cls=GetPreset)

    # setup get preset-fir <CH>
    fir_parser = subparsers.add_parser(
        "preset-fir", help="Get preset FIR filter (path: /audio/output/speaker/{CH}/preset/fir)"
    )
    fir_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    fir_parser.set_defaults(command_cls=GetSpeakerPresetFir)

    # setup get preset-crossover <CH>
    xr_parser = subparsers.add_parser(
        "preset-crossover", help="Get preset crossover (path: /audio/output/speaker/{CH}/preset/crossover)"
    )
    xr_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    xr_parser.set_defaults(command_cls=GetSpeakerPresetCrossover)

    # setup get preset-eq <CH> [BAND]
    eq_parser = subparsers.add_parser("preset-eq", help="Get preset EQ (path: /audio/output/speaker/{CH}/preset/eq)")
    eq_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    eq_parser.add_argument("band", type=int, choices=range(1, 16), nargs="?", help="EQ band (1-15, optional)")
    eq_parser.set_defaults(command_cls=GetPresetEq)

    # setup get preset-limiter-peak <CH>
    peak_parser = subparsers.add_parser(
        "preset-limiter-peak",
        help="Get preset peak limiter (path: /audio/output/speaker/{CH}/preset/limiters/peak)",
    )
    peak_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    peak_parser.set_defaults(command_cls=GetSpeakerPresetLimiterPeak)

    # setup get preset-limiter-rms <CH>
    rms_parser = subparsers.add_parser(
        "preset-limiter-rms",
        help="Get preset RMS limiter (path: /audio/output/speaker/{CH}/preset/limiters/rms)",
    )
    rms_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    rms_parser.set_defaults(command_cls=GetSpeakerPresetLimiterRms)

    # setup get preset-limiter-clip <CH>
    clip_parser = subparsers.add_parser(
        "preset-limiter-clip",
        help="Get preset clip limiter (path: /audio/output/speaker/{CH}/preset/limiters/clip)",
    )
    clip_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    clip_parser.set_defaults(command_cls=GetSpeakerPresetLimiterClip)


# ==============================================================================
# SPEAKER COMMANDS (with user/array/preset hierarchy) - OLD STRUCTURE - KEEPING FOR SET COMMANDS
# ==============================================================================
# ==============================================================================


def _register_get_speaker(subparsers):
    """Register 'setup get speaker' commands with hierarchical structure."""
    speaker_parser = subparsers.add_parser("speaker", help="Get speaker configuration")
    speaker_subparsers = speaker_parser.add_subparsers(dest="speaker_layer", required=True)

    # Main layer (direct speaker channel properties)
    _register_get_speaker_main(speaker_subparsers)

    # User layer (user-adjustable processing)
    _register_get_speaker_user(speaker_subparsers)

    # Array layer (array-level processing)
    _register_get_speaker_array(speaker_subparsers)

    # Preset layer (preset-based processing)
    _register_get_speaker_preset(speaker_subparsers)


def _register_set_speaker(subparsers):
    """Register 'setup set speaker' commands with hierarchical structure."""
    speaker_parser = subparsers.add_parser("speaker", help="Set speaker configuration")
    speaker_subparsers = speaker_parser.add_subparsers(dest="speaker_layer", required=True)

    # Main layer (direct speaker channel properties)
    _register_set_speaker_main(speaker_subparsers)

    # User layer (user-adjustable processing)
    _register_set_speaker_user(speaker_subparsers)

    # Array layer (array-level processing)
    _register_set_speaker_array(speaker_subparsers)

    # Preset layer (preset-based processing)
    _register_set_speaker_preset(speaker_subparsers)


def _register_get_speaker_main(subparsers):
    """Register 'setup get speaker <main_items>' commands."""
    # setup get speaker channel <CH>
    channel_parser = subparsers.add_parser("channel", help="Get speaker channel configuration")
    channel_parser.add_argument("channel", type=int, help="Channel number")
    channel_parser.set_defaults(command_cls=GetSpeakerChannel)

    # setup get speaker gain <CH>
    gain_parser = subparsers.add_parser("gain", help="Get speaker gain")
    gain_parser.add_argument("channel", type=int, help="Channel number")
    gain_parser.set_defaults(command_cls=GetSpeakerGain)

    # setup get speaker mute <CH>
    mute_parser = subparsers.add_parser("mute", help="Get speaker mute state")
    mute_parser.add_argument("channel", type=int, help="Channel number")
    mute_parser.set_defaults(command_cls=GetSpeakerMute)

    # setup get speaker delay <CH>
    delay_parser = subparsers.add_parser("delay", help="Get speaker delay")
    delay_parser.add_argument("channel", type=int, help="Channel number")
    delay_parser.set_defaults(command_cls=GetSpeakerDelay)


def _register_set_speaker_main(subparsers):
    """Register 'setup set speaker <main_items>' commands."""
    # setup set speaker name <CH> <VALUE>
    name_parser = subparsers.add_parser("name", help="Set speaker channel name")
    name_parser.add_argument("channel", type=int, help="Channel number")
    name_parser.add_argument("value", type=str, help="Channel name")
    name_parser.set_defaults(command_cls=SetSpeakerName)

    # setup set speaker source primary <CH> <VALUE>
    primary_parser = subparsers.add_parser("primary", help="Set primary audio source")
    primary_parser.add_argument("channel", type=int, help="Channel number")
    primary_parser.add_argument("value", type=str, help="Primary source channel")
    primary_parser.set_defaults(command_cls=SetSpeakerPrimarySrc)

    # setup set speaker source fallback <CH> <VALUE>
    fallback_parser = subparsers.add_parser("fallback", help="Set fallback audio source")
    fallback_parser.add_argument("channel", type=int, help="Channel number")
    fallback_parser.add_argument("value", type=str, help="Fallback source channel")
    fallback_parser.set_defaults(command_cls=SetSpeakerFallbackSrc)

    # setup set speaker gain <CH> <VALUE>
    gain_parser = subparsers.add_parser("gain", help="Set speaker gain")
    gain_parser.add_argument("channel", type=int, help="Channel number")
    gain_parser.add_argument("value", type=float, help="Gain value in dB")
    gain_parser.set_defaults(command_cls=SetSpeakerGain)

    # setup set speaker mute <CH> <VALUE>
    mute_parser = subparsers.add_parser("mute", help="Set speaker mute state")
    mute_parser.add_argument("channel", type=int, help="Channel number")
    mute_parser.add_argument("value", type=int, choices=[0, 1], help="Mute state (0=off, 1=on)")
    mute_parser.set_defaults(command_cls=SetSpeakerMute)

    # setup set speaker delay <CH> <VALUE>
    delay_parser = subparsers.add_parser("delay", help="Set speaker delay")
    delay_parser.add_argument("channel", type=int, help="Channel number")
    delay_parser.add_argument("value", type=float, help="Delay value in ms")
    delay_parser.set_defaults(command_cls=SetSpeakerDelay)


def _register_get_speaker_user(subparsers):
    """Register 'setup get speaker user' commands."""
    user_parser = subparsers.add_parser("user", help="Get user-adjustable processing")
    user_subparsers = user_parser.add_subparsers(dest="user_resource", required=True)

    # setup get speaker user eq <CH>
    _register_get_speaker_user_eq(user_subparsers)

    # setup get speaker user fir <CH>
    fir_parser = user_subparsers.add_parser("fir", help="Get user FIR filter")
    fir_parser.add_argument("channel", type=int, help="Channel number")
    fir_parser.set_defaults(command_cls=GetSpeakerUserFir)


def _register_set_speaker_user(subparsers):
    """Register 'setup set speaker user' commands."""
    user_parser = subparsers.add_parser("user", help="Set user-adjustable processing")
    user_subparsers = user_parser.add_subparsers(dest="user_resource", required=True)

    # setup set speaker user mute <CH> <VALUE>
    mute_parser = user_subparsers.add_parser("mute", help="Set user layer mute")
    mute_parser.add_argument("channel", type=int, help="Channel number")
    mute_parser.add_argument("value", type=str2bool, help="Mute state")
    mute_parser.set_defaults(command_cls=SetSpeakerUserMute)

    # setup set speaker user gain <CH> <VALUE>
    gain_parser = user_subparsers.add_parser("gain", help="Set user layer gain")
    gain_parser.add_argument("channel", type=int, help="Channel number")
    gain_parser.add_argument("value", type=float, help="Gain value in dB")
    gain_parser.set_defaults(command_cls=SetSpeakerUserGain)

    # setup set speaker user polarity <CH> <VALUE>
    polarity_parser = user_subparsers.add_parser("polarity", help="Set user layer polarity")
    polarity_parser.add_argument("channel", type=int, help="Channel number")
    polarity_parser.add_argument("value", type=int, choices=[-1, 1], help="Polarity (1 or -1)")
    polarity_parser.set_defaults(command_cls=SetSpeakerUserPolarity)

    # setup set speaker user delay <CH> <VALUE>
    delay_parser = user_subparsers.add_parser("delay", help="Set user layer delay")
    delay_parser.add_argument("channel", type=int, help="Channel number")
    delay_parser.add_argument("value", type=float, help="Delay value in seconds")
    delay_parser.set_defaults(command_cls=SetSpeakerUserDelay)

    # setup set speaker user hpf <CH> <TYPE>
    hpf_parser = user_subparsers.add_parser("hpf", help="Set high-pass filter")
    hpf_parser.add_argument("channel", type=int, help="Channel number")
    hpf_parser.add_argument("type", type=str, help="HPF filter type")
    hpf_parser.add_argument("-f", "--frequency", type=float, help="HPF frequency in Hz")
    hpf_parser.set_defaults(command_cls=SetSpeakerUserHpf)

    # setup set speaker user generator-mix <CH> <MODE>
    genmix_parser = user_subparsers.add_parser("generator-mix", help="Set generator mix mode")
    genmix_parser.add_argument("channel", type=int, help="Channel number")
    genmix_parser.add_argument("mode", type=str, help="Generator mix mode")
    genmix_parser.set_defaults(command_cls=SetSpeakerUserGeneratorMix)

    # setup set speaker user eq <CH>
    _register_set_speaker_user_eq(user_subparsers)

    # setup set speaker user fir <CH>
    fir_parser = user_subparsers.add_parser("fir", help="Set user FIR filter")
    fir_parser.add_argument("channel", type=int, help="Channel number")
    fir_parser.add_argument(
        "-f", "--file", required=True, help="FIR coefficients file (text file, one coefficient per line)"
    )
    fir_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass FIR filter")
    fir_parser.set_defaults(command_cls=SetSpeakerUserFir)


def _register_get_speaker_user_eq(subparsers):
    """Register 'setup get speaker user eq' commands."""
    eq_parser = subparsers.add_parser("eq", help="Get user EQ")
    eq_subparsers = eq_parser.add_subparsers(dest="eq_item", required=True)

    # setup get speaker user eq all <CH>
    all_parser = eq_subparsers.add_parser("all", help="Get all EQ bands")
    all_parser.add_argument("channel", type=int, help="Channel number")
    all_parser.set_defaults(command_cls=GetSpeakerUserEqAll)

    # setup get speaker user eq band <CH> <BAND>
    band_parser = eq_subparsers.add_parser("band", help="Get specific EQ band")
    band_parser.add_argument("channel", type=int, help="Channel number")
    band_parser.add_argument("band", type=int, help="Band number")
    band_parser.set_defaults(command_cls=GetSpeakerUserEqBand)


def _register_set_speaker_user_eq(subparsers):
    """Register 'setup set speaker user eq' commands."""
    eq_parser = subparsers.add_parser("eq", help="Set user EQ")
    eq_subparsers = eq_parser.add_subparsers(dest="eq_item", required=True)

    # setup set speaker user eq bypass <CH> <VALUE>
    bypass_parser = eq_subparsers.add_parser("bypass", help="Set EQ bypass")
    bypass_parser.add_argument("channel", type=int, help="Channel number")
    bypass_parser.add_argument("value", type=str2bool, help="Bypass state")
    bypass_parser.set_defaults(command_cls=SetSpeakerUserEqBypass)

    # setup set speaker user eq band <CH> <BAND> -f <FREQ> -g <GAIN> -q <Q> -t <TYPE>
    band_parser = eq_subparsers.add_parser("band", help="Set specific EQ band")
    band_parser.add_argument("channel", type=int, help="Channel number")
    band_parser.add_argument("band", type=int, help="Band number")
    band_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass this band")
    band_parser.add_argument("-f", "--frequency", type=float, help="Frequency in Hz")
    band_parser.add_argument("-g", "--gain", type=float, help="Gain in dB")
    band_parser.add_argument("-q", "--q", type=float, help="Q factor")
    band_parser.add_argument("-t", "--type", choices=EQ_FILTER_TYPES, help="Filter type")
    band_parser.set_defaults(command_cls=SetSpeakerUserEqBand)


def _register_get_speaker_array(subparsers):
    """Register 'setup get speaker array' commands."""
    array_parser = subparsers.add_parser("array", help="Get array-level processing")
    array_subparsers = array_parser.add_subparsers(dest="array_resource", required=True)

    # setup get speaker array eq <CH>
    _register_get_speaker_array_eq(array_subparsers)

    # setup get speaker array fir <CH>
    fir_parser = array_subparsers.add_parser("fir", help="Get array FIR filter")
    fir_parser.add_argument("channel", type=int, help="Channel number")
    fir_parser.set_defaults(command_cls=GetSpeakerArrayFir)


def _register_set_speaker_array(subparsers):
    """Register 'setup set speaker array' commands."""
    array_parser = subparsers.add_parser("array", help="Set array-level processing")
    array_subparsers = array_parser.add_subparsers(dest="array_resource", required=True)

    # setup set speaker array gain <CH> <VALUE>
    gain_parser = array_subparsers.add_parser("gain", help="Set array layer gain")
    gain_parser.add_argument("channel", type=int, help="Channel number")
    gain_parser.add_argument("value", type=float, help="Gain value in dB")
    gain_parser.set_defaults(command_cls=SetSpeakerArrayGain)

    # setup set speaker array polarity <CH> <VALUE>
    polarity_parser = array_subparsers.add_parser("polarity", help="Set array layer polarity")
    polarity_parser.add_argument("channel", type=int, help="Channel number")
    polarity_parser.add_argument("value", type=int, choices=[-1, 1], help="Polarity (1 or -1)")
    polarity_parser.set_defaults(command_cls=SetSpeakerArrayPolarity)

    # setup set speaker array delay <CH> <VALUE>
    delay_parser = array_subparsers.add_parser("delay", help="Set array layer delay")
    delay_parser.add_argument("channel", type=int, help="Channel number")
    delay_parser.add_argument("value", type=float, help="Delay value in seconds")
    delay_parser.set_defaults(command_cls=SetSpeakerArrayDelay)

    # setup set speaker array eq <CH>
    _register_set_speaker_array_eq(array_subparsers)

    # setup set speaker array fir <CH>
    fir_parser = array_subparsers.add_parser("fir", help="Set array FIR filter")
    fir_parser.add_argument("channel", type=int, help="Channel number")
    fir_parser.add_argument(
        "-f", "--file", required=True, help="FIR coefficients file (text file, one coefficient per line)"
    )
    fir_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass FIR filter")
    fir_parser.set_defaults(command_cls=SetSpeakerArrayFir)

    # setup set speaker array crossover <CH>
    crossover_parser = array_subparsers.add_parser("crossover", help="Set array crossover")
    crossover_parser.add_argument("channel", type=int, help="Channel number")
    crossover_parser.add_argument("-f", "--frequency", type=float, required=True, help="Crossover frequency in Hz")
    crossover_parser.add_argument("-t", "--type", required=True, choices=["lr2", "lr4", "lr8"], help="Crossover type")
    crossover_parser.set_defaults(command_cls=SetSpeakerArrayCrossover)


def _register_get_speaker_array_eq(subparsers):
    """Register 'setup get speaker array eq' commands."""
    eq_parser = subparsers.add_parser("eq", help="Get array EQ")
    eq_subparsers = eq_parser.add_subparsers(dest="eq_item", required=True)

    # setup get speaker array eq all <CH>
    all_parser = eq_subparsers.add_parser("all", help="Get all EQ bands")
    all_parser.add_argument("channel", type=int, help="Channel number")
    all_parser.set_defaults(command_cls=GetSpeakerArrayEqAll)

    # setup get speaker array eq band <CH> <BAND>
    band_parser = eq_subparsers.add_parser("band", help="Get specific EQ band")
    band_parser.add_argument("channel", type=int, help="Channel number")
    band_parser.add_argument("band", type=int, help="Band number")
    band_parser.set_defaults(command_cls=GetSpeakerArrayEqBand)


def _register_set_speaker_array_eq(subparsers):
    """Register 'setup set speaker array eq' commands."""
    eq_parser = subparsers.add_parser("eq", help="Set array EQ")
    eq_subparsers = eq_parser.add_subparsers(dest="eq_item", required=True)

    # setup set speaker array eq bypass <CH> <VALUE>
    bypass_parser = eq_subparsers.add_parser("bypass", help="Set EQ bypass")
    bypass_parser.add_argument("channel", type=int, help="Channel number")
    bypass_parser.add_argument("value", type=str2bool, help="Bypass state")
    bypass_parser.set_defaults(command_cls=SetSpeakerArrayEqBypass)

    # setup set speaker array eq band <CH> <BAND> -f <FREQ> -g <GAIN> -q <Q> -t <TYPE>
    band_parser = eq_subparsers.add_parser("band", help="Set specific EQ band")
    band_parser.add_argument("channel", type=int, help="Channel number")
    band_parser.add_argument("band", type=int, help="Band number")
    band_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass this band")
    band_parser.add_argument("-f", "--frequency", type=float, help="Frequency in Hz")
    band_parser.add_argument("-g", "--gain", type=float, help="Gain in dB")
    band_parser.add_argument("-q", "--q", type=float, help="Q factor")
    band_parser.add_argument("-t", "--type", choices=EQ_FILTER_TYPES, help="Filter type")
    band_parser.set_defaults(command_cls=SetSpeakerArrayEqBand)


def _register_get_speaker_preset(subparsers):
    """Register 'setup get speaker preset' commands."""
    preset_parser = subparsers.add_parser("preset", help="Get preset-based processing")
    preset_subparsers = preset_parser.add_subparsers(dest="preset_resource", required=True)

    # setup get speaker preset eq <CH>
    _register_get_speaker_preset_eq(preset_subparsers)

    # setup get speaker preset fir <CH>
    fir_parser = preset_subparsers.add_parser("fir", help="Get preset FIR filter")
    fir_parser.add_argument("channel", type=int, help="Channel number")
    fir_parser.set_defaults(command_cls=GetSpeakerPresetFir)

    # setup get speaker preset crossover <CH>
    crossover_parser = preset_subparsers.add_parser("crossover", help="Get preset crossover")
    crossover_parser.add_argument("channel", type=int, help="Channel number")
    crossover_parser.set_defaults(command_cls=GetSpeakerPresetCrossover)

    # setup get speaker preset limiter <CH>
    _register_get_speaker_preset_limiter(preset_subparsers)


def _register_set_speaker_preset(subparsers):
    """Register 'setup set speaker preset' commands."""
    preset_parser = subparsers.add_parser("preset", help="Set preset-based processing (read-only in most cases)")
    _preset_subparsers = preset_parser.add_subparsers(dest="preset_resource", required=True)

    # Most preset values are read-only, but we can add setters if needed
    # For now, just get the structure


def _register_get_speaker_preset_eq(subparsers):
    """Register 'setup get speaker preset eq' commands."""
    eq_parser = subparsers.add_parser("eq", help="Get preset EQ")
    eq_subparsers = eq_parser.add_subparsers(dest="eq_item", required=True)

    # setup get speaker preset eq all <CH>
    all_parser = eq_subparsers.add_parser("all", help="Get all EQ bands")
    all_parser.add_argument("channel", type=int, help="Channel number")
    all_parser.set_defaults(command_cls=GetSpeakerPresetEqAll)

    # setup get speaker preset eq band <CH> <BAND>
    band_parser = eq_subparsers.add_parser("band", help="Get specific EQ band")
    band_parser.add_argument("channel", type=int, help="Channel number")
    band_parser.add_argument("band", type=int, help="Band number")
    band_parser.set_defaults(command_cls=GetSpeakerPresetEqBand)


def _register_get_speaker_preset_limiter(subparsers):
    """Register 'setup get speaker preset limiter' commands."""
    limiter_parser = subparsers.add_parser("limiter", help="Get preset limiter")
    limiter_subparsers = limiter_parser.add_subparsers(dest="limiter_type", required=True)

    # setup get speaker preset limiter peak <CH>
    peak_parser = limiter_subparsers.add_parser("peak", help="Get peak limiter")
    peak_parser.add_argument("channel", type=int, help="Channel number")
    peak_parser.set_defaults(command_cls=GetSpeakerPresetLimiterPeak)

    # setup get speaker preset limiter rms <CH>
    rms_parser = limiter_subparsers.add_parser("rms", help="Get RMS limiter")
    rms_parser.add_argument("channel", type=int, help="Channel number")
    rms_parser.set_defaults(command_cls=GetSpeakerPresetLimiterRms)

    # setup get speaker preset limiter clip <CH>
    clip_parser = limiter_subparsers.add_parser("clip", help="Get clip limiter")
    clip_parser.add_argument("channel", type=int, help="Channel number")
    clip_parser.set_defaults(command_cls=GetSpeakerPresetLimiterClip)


# ==============================================================================
# SUMMING-MATRIX COMMANDS
# ==============================================================================


def _register_get_summing_matrix(subparsers):
    """Register 'setup get summing-matrix' command."""
    # setup get summing-matrix - get entire summing matrix
    sm_parser = subparsers.add_parser(
        "summing-matrix", help="Get summing matrix configuration (path: /audio/summing_matrix)"
    )
    sm_parser.set_defaults(command_cls=GetSummingMatrix)


# ==============================================================================
# GENERATOR COMMANDS
# ==============================================================================


def _register_get_generator(subparsers):
    """Register 'setup get generator' command."""
    # setup get generator - get all generator configuration
    gen_parser = subparsers.add_parser("generator", help="Get signal generator configuration (path: /audio/generator)")
    gen_parser.set_defaults(command_cls=GetGenerator)


# ==============================================================================
# GPIO COMMANDS
# ==============================================================================


def _register_get_gpio(subparsers):
    """Register 'setup get gpio' command."""
    # setup get gpio - get all GPIO configuration
    gpio_parser = subparsers.add_parser("gpio", help="Get GPIO configuration (path: /gpio)")
    gpio_parser.set_defaults(command_cls=GetGpio)


# ==============================================================================
# WAYS COMMANDS
# ==============================================================================


def _register_get_ways(subparsers):
    """Register 'setup get speaker-ways' command."""
    ways_parser = subparsers.add_parser(
        "speaker-ways", help="Get speaker way mapping (path: /audio/output/speaker_ways)"
    )
    ways_parser.set_defaults(command_cls=GetWays)


# ==============================================================================
# NETWORK OUTPUT COMMANDS
# ==============================================================================


def _register_get_network_output(subparsers):
    """Register 'setup get network-output' commands."""
    net_parser = subparsers.add_parser("network-output", help="Get network output configuration")
    net_subparsers = net_parser.add_subparsers(dest="net_item", required=True)

    # setup get network-output channel <CH>
    channel_parser = net_subparsers.add_parser("channel", help="Get network output channel")
    channel_parser.add_argument("channel", type=int, help="Channel number")
    channel_parser.set_defaults(command_cls=GetNetworkOutputChannel)


def _register_set_network_output(subparsers):
    """Register 'setup set network-output' commands."""
    net_parser = subparsers.add_parser("network-output", help="Set network output configuration")
    net_subparsers = net_parser.add_subparsers(dest="net_item", required=True)

    # setup set network-output channel <CH>
    channel_parser = net_subparsers.add_parser("channel", help="Set network output channel")
    channel_parser.add_argument("channel", type=int, help="Channel number")
    channel_parser.add_argument("-s", "--source", type=str, help="Source channel")
    channel_parser.add_argument("-n", "--name", type=str, help="Channel name")
    channel_parser.set_defaults(command_cls=SetNetworkOutputChannel)


# ==============================================================================
# NETWORK/LAN COMMANDS
# ==============================================================================


def _register_get_network(subparsers):
    """Register 'setup get network' commands."""
    network_parser = subparsers.add_parser("network", help="Get network configuration")
    network_subparsers = network_parser.add_subparsers(dest="network_item", required=True)

    # setup get network config
    config_parser = network_subparsers.add_parser("config", help="Get network configuration (path: /network/config)")
    config_parser.set_defaults(command_cls=GetNetworkConfig)

    # setup get network lan <INTERFACE>
    lan_parser = network_subparsers.add_parser(
        "lan", help="Get LAN interface configuration (path: /network/lan/{INTERFACE})"
    )
    lan_parser.add_argument("interface", type=int, choices=[1, 2], help="LAN interface (1 or 2)")
    lan_parser.set_defaults(command_cls=GetNetworkLan)


# ==============================================================================
# POWER MANAGEMENT COMMANDS
# ==============================================================================


def _register_get_power(subparsers):
    """Register 'setup get power' commands."""
    power_parser = subparsers.add_parser("power", help="Get power management configuration (path: /power)")
    power_parser.set_defaults(command_cls=GetPower)


def _register_set_power(subparsers):
    """Register 'setup set power' commands."""
    power_parser = subparsers.add_parser("power", help="Set power management configuration")
    power_parser.add_argument("-m", "--mode", type=str, choices=POWER_ON_MODES, help="Power on mode")
    power_parser.add_argument("-s", "--standby-time", type=int, help="Standby time in minutes")
    power_parser.add_argument("-u", "--mute-time", type=int, help="Mute time in seconds")
    power_parser.add_argument(
        "-f", "--fuse-protection", type=str, choices=FUSE_PROTECTION_MODES, help="Fuse protection mode"
    )
    power_parser.set_defaults(command_cls=SetPower)


# ==============================================================================
# FLATTENED SET COMMAND REGISTRATIONS (matching Get structure)
# ==============================================================================


def _register_set_input(subparsers):
    """Register 'setup set input' commands with flattened structure."""
    input_parser = subparsers.add_parser("input", help="Set input configuration")
    input_subparsers = input_parser.add_subparsers(dest="input_type", required=True)

    # setup set input config <VALUE>
    config_parser = input_subparsers.add_parser("config", help="Set input configuration (analog/digital)")
    config_parser.add_argument("value", choices=["analog", "digital"], type=str, help="Input type (analog or digital)")
    config_parser.set_defaults(command_cls=SetInputConfig)

    # setup set input analog <CH> [OPTIONS]
    analog_parser = input_subparsers.add_parser("analog", help="Set analog input channel")
    analog_parser.add_argument("channel", type=int, choices=range(1, 5), help="Channel number (1-4)")
    analog_parser.add_argument("-n", "--name", type=str, help="Channel name")
    analog_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    analog_parser.add_argument("-d", "--delay", type=float, help="Delay value in ms")
    analog_parser.add_argument("-m", "--mute", type=int, choices=[0, 1], help="Mute state (0=off, 1=on)")
    analog_parser.set_defaults(command_cls=SetInputAnalog)

    # setup set input digital <CH> [OPTIONS]
    digital_parser = input_subparsers.add_parser("digital", help="Set digital input channel")
    digital_parser.add_argument("channel", type=int, choices=range(1, 5), help="Channel number (1-4)")
    digital_parser.add_argument("-n", "--name", type=str, help="Channel name")
    digital_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    digital_parser.add_argument("-d", "--delay", type=float, help="Delay value in ms")
    digital_parser.add_argument("-m", "--mute", type=int, choices=[0, 1], help="Mute state (0=off, 1=on)")
    digital_parser.set_defaults(command_cls=SetInputDigital)

    # setup set input network <CH> [OPTIONS]
    network_parser = input_subparsers.add_parser("network", help="Set network (AoIP) input channel")
    network_parser.add_argument("channel", type=int, choices=range(1, 5), help="Channel number (1-4)")
    network_parser.add_argument("-n", "--name", type=str, help="Channel name")
    network_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    network_parser.add_argument("-d", "--delay", type=float, help="Delay value in ms")
    network_parser.add_argument("-m", "--mute", type=int, choices=[0, 1], help="Mute state (0=off, 1=on)")
    network_parser.set_defaults(command_cls=SetInputNetwork)


def _register_set_generator(subparsers):
    """Register 'setup set generator' command."""
    gen_parser = subparsers.add_parser("generator", help="Set signal generator configuration")
    gen_parser.add_argument("-k", "--kind", type=str, choices=GENERATOR_TYPES, help="Generator type")
    gen_parser.add_argument("-g", "--gain", type=float, help="Generator gain in dB")
    gen_parser.add_argument("-f", "--frequency", type=float, help="Sine wave frequency (for sine generator)")
    gen_parser.add_argument("--lpf-freq", type=float, help="Low-pass filter frequency (for noise generators)")
    gen_parser.add_argument("--hpf-freq", type=float, help="High-pass filter frequency (for noise generators)")
    gen_parser.set_defaults(command_cls=SetGenerator)


def _register_set_outputs(subparsers):
    """Register flattened output set commands."""
    # setup set output-speaker <CH> [OPTIONS]
    speaker_parser = subparsers.add_parser("output-speaker", help="Set speaker output channel")
    speaker_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    speaker_parser.add_argument("-n", "--name", type=str, help="Channel name")
    speaker_parser.add_argument(
        "-p", "--primary-src", type=str, choices=OUTPUT_SRC_CHANNELS, help="Primary source channel"
    )
    speaker_parser.add_argument(
        "-f", "--fallback-src", type=str, choices=OUTPUT_SRC_CHANNELS, help="Fallback source channel"
    )
    speaker_parser.set_defaults(command_cls=SetSpeakerOutput)

    # setup set output-digital <CH> [OPTIONS]
    digital_parser = subparsers.add_parser("output-digital", help="Set digital output channel")
    digital_parser.add_argument("channel", type=int, choices=range(1, 5), help="Digital output channel (1-4)")
    digital_parser.add_argument("-n", "--name", type=str, help="Channel name")
    digital_parser.add_argument("-s", "--source", type=str, choices=NETWORK_SRC_CHANNELS, help="Source channel")
    digital_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    digital_parser.set_defaults(command_cls=SetDigitalOutput)

    # setup set output-network <CH> [OPTIONS]
    network_parser = subparsers.add_parser("output-network", help="Set network output channel")
    network_parser.add_argument("channel", type=int, choices=range(1, 5), help="Network output channel (1-4)")
    network_parser.add_argument("-n", "--name", type=str, help="Channel name")
    network_parser.add_argument("-s", "--source", type=str, choices=NETWORK_SRC_CHANNELS, help="Source channel")
    network_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    network_parser.set_defaults(command_cls=SetNetworkOutput)


def _register_set_user(subparsers):
    """Register flattened user processing set commands."""
    # setup set user <CH> [OPTIONS]
    user_parser = subparsers.add_parser("user", help="Set user processing")
    user_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    user_parser.add_argument("-m", "--mute", type=int, choices=[0, 1], help="Mute status (0=off, 1=on)")
    user_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    user_parser.add_argument("-p", "--polarity", type=int, choices=[-1, 1], help="Polarity status")
    user_parser.add_argument("-d", "--delay", type=float, help="Delay value in seconds")
    user_parser.add_argument("--hpf-kind", type=str, choices=HPF_FILTER_TYPES, help="High-pass filter kind")
    user_parser.add_argument("--hpf-freq", type=float, help="High-pass filter frequency in Hz")
    user_parser.add_argument("--generator-mix", type=str, choices=GENERATOR_MIX_MODES, help="Generator mix mode")
    user_parser.set_defaults(command_cls=SetUser)

    # setup set user-eq <CH> [OPTIONS]
    eq_parser = subparsers.add_parser("user-eq", help="Set user EQ")
    eq_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    eq_parser.add_argument("band", type=int, choices=range(1, 11), nargs="?", help="EQ band (1-10, optional)")
    eq_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    eq_parser.add_argument("-k", "--kind", type=str, choices=EQ_FILTER_TYPES, help="Eq Filter kind")
    eq_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    eq_parser.add_argument("-f", "--frequency", type=float, help="Frequency value in Hz")
    eq_parser.add_argument("-q", type=float, help="Q value")
    eq_parser.set_defaults(command_cls=SetUserEq)


def _register_set_array(subparsers):
    """Register flattened array processing set commands."""
    # setup set array <CH> [OPTIONS]
    array_parser = subparsers.add_parser("array", help="Set array processing")
    array_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    array_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    array_parser.add_argument("-p", "--polarity", type=int, choices=[-1, 1], help="Polarity status")
    array_parser.add_argument("-d", "--delay", type=float, help="Delay value in seconds")
    array_parser.set_defaults(command_cls=SetArray)

    # setup set array-fir <CH> [OPTIONS]
    fir_parser = subparsers.add_parser("array-fir", help="Set array FIR filter")
    fir_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    fir_parser.add_argument("-f", "--file", type=str, help="Path to FIR coefficients file")
    fir_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    fir_parser.set_defaults(command_cls=SetArrayFir)

    # setup set array-eq <CH> [BAND] [OPTIONS]
    eq_parser = subparsers.add_parser("array-eq", help="Set array EQ")
    eq_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    eq_parser.add_argument("band", type=int, choices=range(1, 6), nargs="?", help="EQ band (1-5, optional)")
    eq_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    eq_parser.add_argument("-k", "--kind", type=str, choices=EQ_FILTER_TYPES, help="Eq Filter kind")
    eq_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    eq_parser.add_argument("-f", "--frequency", type=float, help="Frequency value in Hz")
    eq_parser.add_argument("-q", type=float, help="Q value")
    eq_parser.set_defaults(command_cls=SetArrayEq)


def _register_set_preset(subparsers):
    """Register flattened preset processing set commands."""
    # setup set preset <CH> [OPTIONS]
    preset_parser = subparsers.add_parser("preset", help="Set preset processing")
    preset_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    preset_parser.add_argument("-m", "--drive_mode", type=str, choices=OUTPUT_DRIVE_MODES, help="Output drive mode")
    preset_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    preset_parser.add_argument("-p", "--polarity", type=int, choices=[-1, 1], help="Polarity status")
    preset_parser.add_argument("-d", "--delay", type=float, help="Delay value in seconds")
    preset_parser.set_defaults(command_cls=SetPreset)

    # setup set preset-fir <CH> [OPTIONS]
    fir_parser = subparsers.add_parser("preset-fir", help="Set preset FIR filter")
    fir_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    fir_parser.add_argument("-f", "--file", type=str, help="Path to FIR coefficients file")
    fir_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    fir_parser.set_defaults(command_cls=SetPresetFir)

    # setup set preset-crossover <CH> [OPTIONS]
    xr_parser = subparsers.add_parser("preset-crossover", help="Set preset crossover")
    xr_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    xr_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    xr_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    xr_parser.add_argument("--lpf-kind", type=str, help="Lowpass filter kind")
    xr_parser.add_argument("--lpf-freq", type=float, help="Lowpass frequency value")
    xr_parser.add_argument("--hpf-kind", type=str, help="Highpass filter kind")
    xr_parser.add_argument("--hpf-freq", type=float, help="Highpass frequency value")
    xr_parser.set_defaults(command_cls=SetPresetCrossover)

    # setup set preset-eq <CH> [BAND] [OPTIONS]
    eq_parser = subparsers.add_parser("preset-eq", help="Set preset EQ")
    eq_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    eq_parser.add_argument("band", type=int, choices=range(1, 16), nargs="?", help="EQ band (1-15, optional)")
    eq_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    eq_parser.add_argument("-k", "--kind", type=str, choices=EQ_FILTER_TYPES, help="Eq Filter kind")
    eq_parser.add_argument("-g", "--gain", type=float, help="Gain value in dB")
    eq_parser.add_argument("-f", "--frequency", type=float, help="Frequency value in Hz")
    eq_parser.add_argument("-q", type=float, help="Q value")
    eq_parser.set_defaults(command_cls=SetPresetEq)

    # setup set preset-limiter-peak <CH> [OPTIONS]
    peak_parser = subparsers.add_parser("preset-limiter-peak", help="Set preset peak limiter")
    peak_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    peak_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    peak_parser.add_argument("-a", "--auto", type=str2bool, help="Auto Mode")
    peak_parser.add_argument("-t", "--threshold", type=float, help="Threshold in dB")
    peak_parser.add_argument("--attack", type=float, help="Attack time")
    peak_parser.add_argument("-r", "--release", type=float, help="Release time")
    peak_parser.add_argument("--hold", type=float, help="Hold time")
    peak_parser.add_argument("-k", "--knee", type=float, help="Knee in dB")
    peak_parser.set_defaults(command_cls=SetPresetLimiterPeak)

    # setup set preset-limiter-rms <CH> [OPTIONS]
    rms_parser = subparsers.add_parser("preset-limiter-rms", help="Set preset RMS limiter")
    rms_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    rms_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    rms_parser.add_argument("-t", "--threshold", type=float, help="Threshold in dB")
    rms_parser.add_argument("--attack", type=float, help="Attack time")
    rms_parser.add_argument("-r", "--release", type=float, help="Release time")
    rms_parser.add_argument("--hold", type=float, help="Hold time")
    rms_parser.add_argument("-k", "--knee", type=float, help="Knee in dB")
    rms_parser.set_defaults(command_cls=SetPresetLimiterRms)

    # setup set preset-limiter-clip <CH> [OPTIONS]
    clip_parser = subparsers.add_parser("preset-limiter-clip", help="Set preset clip limiter")
    clip_parser.add_argument("channel", type=int, choices=range(1, 5), help="Speaker channel (1-4)")
    clip_parser.add_argument("-b", "--bypass", type=str2bool, help="Bypass status")
    clip_parser.add_argument("-m", "--mode", type=str, choices=CLIP_LIMITER_MODES, help="Clip limiter mode")
    clip_parser.set_defaults(command_cls=SetPresetLimiterClip)


def _register_set_summing_matrix(subparsers):
    """Register 'setup set summing-matrix' command."""
    sm_parser = subparsers.add_parser(
        "summing-matrix",
        help="Set summing matrix configuration",
        description='Set summing matrix. Use quotes for inline matrix: --matrix "[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]"',
    )
    sm_parser.add_argument("-f", "--file", type=str, help="JSON file containing matrix data (4x4 array)")
    sm_parser.add_argument(
        "-m",
        "--matrix",
        type=str,
        help='Inline matrix as JSON string (4x4 array). MUST be quoted: --matrix "[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]"',
    )
    sm_parser.add_argument("-r", "--reset", action="store_true", help="Reset to identity matrix")
    sm_parser.set_defaults(command_cls=SetSummingMatrix)


def _register_set_ways(subparsers):
    """Register 'setup set speaker-ways' command."""
    ways_parser = subparsers.add_parser("speaker-ways", help="Set speaker way mapping")
    ways_parser.add_argument("ways", type=str, help='Speaker way mapping (e.g., "HF:1 LF:1 FR:2 FR:3")')
    ways_parser.set_defaults(command_cls=SetWays)


def _register_get_install(subparsers):
    """Register 'setup get install' command."""
    sys_parser = subparsers.add_parser("install", help="Get install information (path: /install)")
    sys_parser.set_defaults(command_cls=GetInstall)


def _register_set_install(subparsers):
    """Register 'setup set install' command."""
    sys_parser = subparsers.add_parser("install", help="Set install information")
    sys_parser.add_argument("-n", "--name", type=str, help="Device name")
    sys_parser.add_argument("-v", "--venue-name", type=str, help="Venue name")
    sys_parser.add_argument("-c", "--customer-name", type=str, help="Customer name")
    sys_parser.add_argument("-a", "--asset-tag", type=str, help="Asset tag")
    sys_parser.add_argument("-i", "--installer-name", type=str, help="Installer name")
    sys_parser.add_argument("--contact-info", type=str, help="Contact information")
    sys_parser.add_argument("--install-date", type=str, help="Installation date")
    sys_parser.add_argument("--install-notes", type=str, help="Installation notes")
    sys_parser.add_argument("--custom1", type=str, help="Custom field 1")
    sys_parser.add_argument("--custom2", type=str, help="Custom field 2")
    sys_parser.add_argument("--custom3", type=str, help="Custom field 3")
    sys_parser.set_defaults(command_cls=SetInstall)


def _register_set_gpio(subparsers):
    """Register 'setup set gpio' command."""
    gpio_parser = subparsers.add_parser("gpio", help="Set GPIO pin configuration")
    gpio_parser.add_argument("pin", type=int, choices=range(1, 5), help="GPIO pin number (1-4)")
    gpio_parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=GPIO_PIN_TYPES,
        help="Pin mode",
    )
    gpio_parser.set_defaults(command_cls=SetGpio)


def _register_set_network(subparsers):
    """Register 'setup set network' commands."""
    network_parser = subparsers.add_parser("network", help="Set network configuration")
    network_subparsers = network_parser.add_subparsers(dest="network_item", required=True)

    # setup set network config [OPTIONS]
    config_parser = network_subparsers.add_parser("config", help="Set network configuration")
    config_parser.add_argument("-m", "--mode", type=str, choices=["split", "redundant"], help="Network mode")
    config_parser.set_defaults(command_cls=SetNetworkConfig)

    # setup set network lan <INTERFACE> [OPTIONS]
    lan_parser = network_subparsers.add_parser("lan", help="Set LAN interface configuration")
    lan_parser.add_argument("interface", type=int, choices=[1, 2], help="LAN interface (1 or 2)")
    lan_parser.add_argument("-m", "--mode", type=str, choices=["dhcp", "static"], help="Network mode")
    lan_parser.add_argument("-i", "--ip", type=str, help="IP address (for static mode)")
    lan_parser.add_argument("-n", "--netmask", type=str, help="Subnet mask (for static mode)")
    lan_parser.add_argument("-g", "--gateway", type=str, help="Gateway address (for static mode)")
    lan_parser.add_argument("--dns1", type=str, help="Primary DNS server (for static mode)")
    lan_parser.add_argument("--dns2", type=str, help="Secondary DNS server (for static mode)")
    lan_parser.set_defaults(command_cls=SetNetworkLan)


def _register_batch_commands(subparsers):
    """Register 'setup batch' commands."""
    batch_parser = subparsers.add_parser("batch", help="Batch operations for device configuration")
    batch_subparsers = batch_parser.add_subparsers(dest="batch_action", required=True)

    # setup batch create -f FILE
    create_parser = batch_subparsers.add_parser("create", help="Save current device configuration to a file")
    create_parser.add_argument("-f", "--file", type=str, required=True, help="Output JSON file path")
    create_parser.set_defaults(command_cls=BatchCreate)

    # setup batch apply -f FILE
    apply_parser = batch_subparsers.add_parser("apply", help="Apply configuration from a file to the device")
    apply_parser.add_argument("-f", "--file", type=str, required=True, help="Input JSON file path")
    apply_parser.set_defaults(command_cls=BatchApply)


# ==============================================================================
# SPEAKER COMMANDS (with user/array/preset hierarchy) - OLD STRUCTURE - KEEPING FOR BACKWARDS COMPAT
# ==============================================================================
# ==============================================================================


# ==============================================================================
# Get ALL COMMAND
# ==============================================================================


class GetAll(SubCommand):
    """Get all setup configuration."""

    @classmethod
    async def run(cls, args):
        params = {}
        if hasattr(args, "flatten") and args.flatten:
            params["flatten"] = args.flatten

        await cls.send_setup_get_all_jrpc_message(args.target, args.port, params, args.verbose)


# ==============================================================================
# SIMPLIFIED FLATTENED COMMAND IMPLEMENTATIONS
# ==============================================================================


class GetUserEq(SubCommand):
    """Get user EQ (all bands or specific band)."""

    @classmethod
    async def run(cls, args):
        if hasattr(args, "band") and args.band:
            await cls.send_setup_get_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/user/eq/bands/{args.band}",
                args.verbose,
                args.quiet,
            )
        else:
            await cls.send_setup_get_jrpc_message(
                args.target, args.port, f"/audio/output/speaker/{args.channel}/user/eq", args.verbose, args.quiet
            )


class GetArrayEq(SubCommand):
    """Get array EQ (all bands or specific band)."""

    @classmethod
    async def run(cls, args):
        if hasattr(args, "band") and args.band:
            await cls.send_setup_get_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/array/eq/bands/{args.band}",
                args.verbose,
                args.quiet,
            )
        else:
            await cls.send_setup_get_jrpc_message(
                args.target, args.port, f"/audio/output/speaker/{args.channel}/array/eq", args.verbose, args.quiet
            )


class GetPresetEq(SubCommand):
    """Get preset EQ (all bands or specific band)."""

    @classmethod
    async def run(cls, args):
        if hasattr(args, "band") and args.band:
            await cls.send_setup_get_jrpc_message(
                args.target,
                args.port,
                f"/audio/output/speaker/{args.channel}/preset/eq/bands/{args.band}",
                args.verbose,
                args.quiet,
            )
        else:
            await cls.send_setup_get_jrpc_message(
                args.target, args.port, f"/audio/output/speaker/{args.channel}/preset/eq", args.verbose, args.quiet
            )


class GetUser(SubCommand):
    """Get user processing (all user settings for a channel)."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/user", args.verbose, args.quiet
        )


class GetArray(SubCommand):
    """Get array processing (all array settings for a channel)."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/array", args.verbose, args.quiet
        )


class GetPreset(SubCommand):
    """Get preset processing (all preset settings for a channel)."""

    @classmethod
    async def run(cls, args):
        await cls.send_setup_get_jrpc_message(
            args.target, args.port, f"/audio/output/speaker/{args.channel}/preset", args.verbose, args.quiet
        )


class SetupSubscribe(SubCommand):
    """Subscribe to setup configuration changes."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.paths:
            params["paths"] = args.paths

        await cls.send_subscribe_jrpc_message(
            "setup_subscribe",
            args.target,
            args.port,
            params,
            args.verbose,
            timeout=args.timeout if hasattr(args, "timeout") else None,
        )
