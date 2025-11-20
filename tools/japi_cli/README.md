# JAPI CLI - Hierarchical Command-Line Interface

A modern, hierarchical command-line interface for controlling devices via JSON-RPC over WebSocket.

## Features

- **Hierarchical Command Structure** - Intuitive nested commands (e.g., `setup get speaker preset limiter peak <CH>`)
- **Deep Speaker Processing Layers** - User, Array, and Preset layers for advanced speaker configuration
- **Interactive Mode** - REPL-style interactive session for rapid testing
- **Tab Completion** - Full argcomplete support for all command paths
- **Verbose & Quiet Modes** - Control output verbosity
- **Real-time Subscriptions** - Subscribe to setup changes, metrics, and events

## Installation

We recommend using [uv](https://docs.astral.sh/uv/) - a fast Python package manager that handles dependencies automatically. If you prefer traditional tools, pip works too.

### Install uv (recommended)

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install japi_cli in development mode
cd tools/japi_cli
uv pip install -e .
```

**Why uv?**
- Fast: 10-100x faster than pip
- Automatic virtual environment management
- Reproducible installs across machines
- Single command for setup

### Alternative: Using pip

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Setup Completion (Optional)

```bash
# Enable tab completion in your shell
source setup_completion.sh
```

## Quick Start

```bash
# Get device information
japi_cli -t 192.168.1.100 status get info

# Show speaker channel configuration
japi_cli -t 192.168.1.100 setup get speaker channel 1

# Set speaker gain
japi_cli -t 192.168.1.100 setup set speaker gain 1 -6.0

# Show preset limiter
japi_cli -t 192.168.1.100 setup get speaker preset limiter peak 1

# Create a preset
japi_cli -t 192.168.1.100 preset create 1 -n "MyPreset" -v "1.0"

# Interactive mode
japi_cli -i -t 192.168.1.100
```

**Note:** If you installed with `uv pip install -e .`, the `japi_cli` command is available directly. Alternatively, use `uv run japi_cli` without installing.

## Command Groups

The CLI is organized into 6 main groups:

1. **api** - API version and ping
2. **device** - Device operations (reboot, logs, time, power)
3. **preset** - Channel preset management
4. **setup** - Device configuration (get/set)
5. **status** - Device runtime status (read-only)
6. **subscribe** - Real-time updates

## CLI to JSON-RPC Mapping

The CLI commands translate directly to JSON-RPC API calls. This comprehensive table shows how CLI commands map to the underlying protocol:

### API Commands
| CLI Command | JSON-RPC Method | Parameters | Notes |
|-------------|-----------------|------------|-------|
| `api ping` | `api_ping` | `{}` | Connectivity test |
| `api version` | `api_version` | `{}` | Returns version + API level |

### Device Commands
| CLI Command | JSON-RPC Method | Parameters | Notes |
|-------------|-----------------|------------|-------|
| `device reboot` | `device_reboot` | `{}` | Reboot device |
| `device reset` | `device_reset` | `{}` | Factory reset |
| `device power-on` | `device_power_on` | `{}` | Power on |
| `device power-off` | `device_power_off` | `{}` | Power off |
| `device find-me` | `device_find_me` | `{}` | LED identification |
| `device time show` | `device_get_time` | `{}` | Get device time |
| `device time set <TS>` | `device_set_time` | `timestamp: <TS>` | Set device time |
| `device discover` | - | - | **Local mDNS only** |

### Setup Get Commands (Read Configuration)
| CLI Command | JSON-RPC Method | Path | Notes |
|-------------|-----------------|------|-------|
| `setup get all` | `setup_get_all` | - | Full config tree |
| `setup get input analog 1` | `setup_get` | `/audio/input/analog/1` | Analog input |
| `setup get input digital 1` | `setup_get` | `/audio/input/digital/1` | Digital input |
| `setup get input network 1` | `setup_get` | `/audio/input/network/1` | Network input |
| `setup get generator` | `setup_get` | `/audio/generator` | Signal generator |
| `setup get output-speaker 1` | `setup_get` | `/audio/output/speaker/1` | Speaker config |
| `setup get output-digital 1` | `setup_get` | `/audio/output/digital/1` | Digital output |
| `setup get output-network 1` | `setup_get` | `/audio/output/network/1` | Network output |
| `setup get user 1` | `setup_get` | `/audio/output/speaker/1/user` | User processing |
| `setup get user-eq 1 [3]` | `setup_get` | `/audio/output/speaker/1/user/eq[/bands/3]` | User EQ [band] |
| `setup get array 1` | `setup_get` | `/audio/output/speaker/1/array` | Array processing |
| `setup get array-eq 1 [2]` | `setup_get` | `/audio/output/speaker/1/array/eq[/bands/2]` | Array EQ [band] |
| `setup get array-fir 1` | `setup_get` | `/audio/output/speaker/1/array/fir` | Array FIR |
| `setup get preset 1` | `setup_get` | `/audio/output/speaker/1/prese` | Preset processing |
| `setup get preset-eq 1 [5]` | `setup_get` | `/audio/output/speaker/1/preset/eq[/bands/5]` | Preset EQ [band] |
| `setup get preset-fir 1` | `setup_get` | `/audio/output/speaker/1/preset/fir` | Preset FIR |
| `setup get preset-crossover 1` | `setup_get` | `/audio/output/speaker/1/preset/crossover` | Preset crossover |
| `setup get preset-limiter-peak 1` | `setup_get` | `/audio/output/speaker/1/preset/limiters/peak` | Peak limiter |
| `setup get preset-limiter-rms 1` | `setup_get` | `/audio/output/speaker/1/preset/limiters/rms` | RMS limiter |
| `setup get preset-limiter-clip 1` | `setup_get` | `/audio/output/speaker/1/preset/limiters/clip` | Clip limiter |
| `setup get summing-matrix` | `setup_get` | `/audio/summing_matrix` | Summing matrix |
| `setup get speaker-ways` | `setup_get` | `/audio/output/speaker_ways` | Speaker way mapping |
| `setup get gpio` | `setup_get` | `/gpio` | GPIO config |
| `setup get network config` | `setup_get` | `/network/config` | Network config |
| `setup get network lan 1` | `setup_get` | `/network/lan/1` | LAN1 config |
| `setup get network lan 2` | `setup_get` | `/network/lan/2` | LAN2 config |
| `setup get power` | `setup_get` | `/power` | Power settings |
| `setup get install` | `setup_get` | `/install` | Installation info |

### Setup Set Commands (Write Configuration)
| CLI Command | JSON-RPC Method | Path | Notes |
|-------------|-----------------|------|-------|
| `setup set input analog 1 -g -3.0` | `setup_set` | `/audio/input/analog/1` | Set analog input |
| `setup set input digital 1 -n "Main"` | `setup_set` | `/audio/input/digital/1` | Set digital input |
| `setup set input network 1 -g -6.0` | `setup_set` | `/audio/input/network/1` | Set network input |
| `setup set generator -k sine -f 1000` | `setup_set` | `/audio/generator` | Set generator |
| `setup set output-speaker 1 -n "Main"` | `setup_set` | `/audio/output/speaker/1` | Set speaker output |
| `setup set output-digital 1 -s analog/1` | `setup_set` | `/audio/output/digital/1` | Set digital output |
| `setup set output-network 1 -s speaker/1` | `setup_set` | `/audio/output/network/1` | Set network output |
| `setup set user 1 -g -3.0 -d 0.5` | `setup_set` | `/audio/output/speaker/1/user` | Set user processing |
| `setup set user-eq 1 [3] -f 1k -g 3` | `setup_set` | `/audio/output/speaker/1/user/eq[/bands/3]` | Set user EQ [band] |
| `setup set array 1 -g -3.0 -p -1` | `setup_set` | `/audio/output/speaker/1/array` | Set array processing |
| `setup set array-eq 1 [2] -f 500 -g 2` | `setup_set` | `/audio/output/speaker/1/array/eq[/bands/2]` | Set array EQ [band] |
| `setup set array-fir 1 -f fir.txt` | `setup_set` | `/audio/output/speaker/1/array/fir` | Set array FIR |
| `setup set preset 1 -m normal -g -1.0` | `setup_set` | `/audio/output/speaker/1/preset` | Set preset |
| `setup set preset-eq 1 [5] -f 2k -g 1.5` | `setup_set` | `/audio/output/speaker/1/preset/eq[/bands/5]` | Set preset EQ [band] |
| `setup set preset-fir 1 -f fir.txt` | `setup_set` | `/audio/output/speaker/1/preset/fir` | Set preset FIR |
| `setup set preset-crossover 1 --lpf-freq 1k` | `setup_set` | `/audio/output/speaker/1/preset/crossover` | Set crossover |
| `setup set preset-limiter-peak 1 -t -3` | `setup_set` | `/audio/output/speaker/1/preset/limiters/peak` | Set peak limiter |
| `setup set preset-limiter-rms 1 -t -6` | `setup_set` | `/audio/output/speaker/1/preset/limiters/rms` | Set RMS limiter |
| `setup set preset-limiter-clip 1 -m soft` | `setup_set` | `/audio/output/speaker/1/preset/limiters/clip` | Set clip limiter |
| `setup set summing-matrix -m "[[1,0,0,0],...]"` | `setup_set` | `/audio/summing_matrix` | Set summing matrix |
| `setup set speaker-ways "HF:1 LF:2"` | `setup_set` | `/audio/output/speaker_ways` | Set speaker ways |
| `setup set gpio 1 -m output` | `setup_set` | `/gpio/pins/1` | Set GPIO pin |
| `setup set network config -m split` | `setup_set` | `/network/config` | Set network config |
| `setup set network lan 1 --ip 192.168.1.50` | `setup_set` | `/network/lan/1` | Set LAN1 |
| `setup set network lan 2 --dhcp` | `setup_set` | `/network/lan/2` | Set LAN2 |
| `setup set power -m always_on` | `setup_set` | `/power` | Set power mode |
| `setup set install --venue "Hall"` | `setup_set` | `/install` | Set install info |

### Setup Batch Commands
| CLI Command | JSON-RPC Method | Parameters | Notes |
|-------------|-----------------|------------|-------|
| `setup batch create -f backup.json` | `backup_create` | `{}` | Create backup file locally |
| `setup batch apply -f config.json` | `backup_restore` | `config: {...}` | Restore from backup file |

### Preset Commands
| CLI Command | JSON-RPC Method | Parameters | Notes |
|-------------|-----------------|------------|-------|
| `preset create 1 -n "Name" -v "1.0"` | `preset_create` | `channel: 1, name: "Name", version: "1.0"` | Create preset |
| `preset apply 1 -f file.json` | `preset_apply` | `channel: 1, preset: {...}` | **File loaded locally** |
| `preset show 1` | `preset_show` | `channel: 1` | Show preset |
| `preset clear 1` | `preset_clear` | `channel: 1` | Clear preset |

### Status Commands (Read-only)
| CLI Command | JSON-RPC Method | Path | Notes |
|-------------|-----------------|------|-------|
| `status get all` | `status_get_all` | - | All status |
| `status get info` | `status_get` | `/info` | Device info |
| `status get state` | `status_get` | `/state` | Device state |
| `status get network` | `status_get` | `/network` | Network status |
| `status get audio` | `status_get` | `/audio` | Audio status |
| `status get firmware` | `status_get` | `/firmware` | Firmware versions |

### Subscribe Commands
| CLI Command | JSON-RPC Method | Parameters | Notes |
|-------------|-----------------|------------|-------|
| `subscribe setup` | `setup_subscribe` | `path: "/"` | All setup changes |
| `subscribe setup speaker/1` | `setup_subscribe` | `path: "/audio/output/speaker/1"` | Speaker 1 only |
| `subscribe metrics -i 1000` | `metrics_subscribe` | `interval: 1000` | Metrics every 1s |

### Path Translation Examples
```
CLI: setup get user-eq 1 3
  → setup_get(path="/audio/output/speaker/1/user/eq/bands/3")

CLI: setup set array-fir 1 -f correction.wav
  → Reads file locally
  → setup_set(path="/audio/output/speaker/1/array/fir", value={fir_data})

CLI: preset apply 1 -f studio.json
  → Reads studio.json locally
  → preset_apply(channel=1, preset={...json_content...})
```

**Key Patterns:**
- **setup get/set**: Maps to `setup_get`/`setup_set` with JSON path addressing
- **Channel numbers**: Embedded in paths (e.g., `/audio/output/speaker/1`)
- **File operations** (`-f`): CLI loads files locally, then sends data via JSON-RPC
- **Batch operations**: Use `backup_create`/`backup_restore` methods
- **mDNS discovery**: Local-only, doesn't use JSON-RPC
- **Flattened commands**: CLI shortcuts map to full paths (e.g., `user-gain` → `/audio/output/speaker/1/user/gain`)

See [API Documentation](../../docs/japi/) for complete JSON-RPC protocol reference.

## Global Options

```bash
-t, --target <IP>       # Device IP (default: 192.168.64.100)
-p, --port <PORT>       # WebSocket port (default: 80)
-v, --verbose           # Verbose output
-q, --quiet             # Quiet mode (JSON only)
-i, --interactive       # Interactive REPL mode
```

For complete documentation, see sections below.

---

## Complete Command Reference

### 1. API Commands

```bash
japi_cli api version              # Get API version
japi_cli api ping                 # Ping device
```

### 2. Device Commands

#### Basic Device Operations
```bash
japi_cli device reboot            # Reboot device
japi_cli device factory-reset     # Factory reset (with confirmation)
japi_cli device factory-reset -y  # Factory reset (skip confirmation)
```

#### Time Operations
```bash
japi_cli device time show         # Show device time
japi_cli device time set <TIMESTAMP>  # Set device time
```

#### Logs Operations
```bash
japi_cli device logs show -n 100  # Show last 100 log lines
japi_cli device logs show -l error  # Show only error logs
japi_cli device logs clear        # Clear logs
japi_cli device logs download -f logs.txt  # Download to file
```

#### Power Operations
```bash
japi_cli device power status      # Show power status
japi_cli device power mode normal # Set power mode
japi_cli device power mode eco    # Set eco mode
japi_cli device power mode standby  # Set standby mode
```

### 3. Preset Commands

**Note**: Channel number comes first in preset commands!

```bash
# Create preset from current configuration
japi_cli preset create <CH> -n <NAME> -v <VERSION> [-f FILE] [-l]
japi_cli preset create 1 -n "Studio_A" -v "1.0"
japi_cli preset create 1 -n "Studio_A" -v "1.0" -f studio_a.json -l

# Apply preset to channel
japi_cli preset apply <CH> -f <FILE>
japi_cli preset apply 1 -f studio_a.json

# Show current preset
japi_cli preset show <CH>
japi_cli preset show 1

# Clear preset
japi_cli preset clear <CH>
japi_cli preset clear 1
```

### 4. Setup Commands

Setup commands follow a hierarchical structure: `setup {get|set} {resource} {item} <CH>`

#### Input Commands

```bash
# Show input configuration
japi_cli setup get input channel <CH>     # Full channel config
japi_cli setup get input gain <CH>        # Gain
japi_cli setup get input delay <CH>       # Delay
japi_cli setup get input polarity <CH>    # Polarity
japi_cli setup get input phantom <CH>     # Phantom power

# Set input configuration
japi_cli setup set input gain <CH> <VALUE>          # Set gain (dB)
japi_cli setup set input delay <CH> <VALUE>         # Set delay (ms)
japi_cli setup set input polarity <CH> {normal|inverted}
japi_cli setup set input phantom <CH> {on|off}

# Examples
japi_cli setup get input gain 1
japi_cli setup set input gain 1 12.5
japi_cli setup set input polarity 1 inverted
japi_cli setup set input phantom 1 on
```

#### Speaker Commands - Three Processing Layers

Speaker processing is organized into hierarchical layers:

**Main Layer** - Direct speaker properties:
```bash
# Show
japi_cli setup get speaker channel <CH>    # Full channel config
japi_cli setup get speaker gain <CH>       # Gain
japi_cli setup get speaker mute <CH>       # Mute state
japi_cli setup get speaker delay <CH>      # Delay

# Set
japi_cli setup set speaker gain <CH> <VALUE>      # Set gain (dB)
japi_cli setup set speaker mute <CH> {on|off}     # Set mute
japi_cli setup set speaker delay <CH> <VALUE>     # Set delay (ms)

# Examples
japi_cli setup get speaker gain 1
japi_cli setup set speaker gain 1 -6.0
japi_cli setup set speaker mute 1 on
japi_cli setup set speaker delay 1 10.5
```

**User Layer** - User-adjustable processing:
```bash
# User EQ
japi_cli setup get speaker user eq all <CH>      # All EQ bands
japi_cli setup get speaker user eq band <CH> <BAND>  # Specific band

japi_cli setup set speaker user eq band <CH> <BAND> \
  -f <FREQ> -g <GAIN> -q <Q> -t {peq|lowshelf|highshelf}

# User FIR
japi_cli setup get speaker user fir <CH>         # Show user FIR
japi_cli setup set speaker user fir <CH> -f <FILE>  # Load user FIR

# Examples
japi_cli setup get speaker user eq all 1
japi_cli setup get speaker user eq band 1 3
japi_cli setup set speaker user eq band 1 3 -f 1000 -g 3.5 -q 2.0 -t peq
japi_cli setup set speaker user fir 1 -f user_correction.wav
```

**Array Layer** - Array-level processing:
```bash
# Array EQ
japi_cli setup get speaker array eq all <CH>     # All EQ bands
japi_cli setup get speaker array eq band <CH> <BAND>

japi_cli setup set speaker array eq band <CH> <BAND> \
  -f <FREQ> -g <GAIN> -q <Q> -t {peq|lowshelf|highshelf}

# Array FIR
japi_cli setup get speaker array fir <CH>
japi_cli setup set speaker array fir <CH> -f <FILE>

# Array Crossover
japi_cli setup get speaker array crossover <CH>
japi_cli setup set speaker array crossover <CH> -f <FREQ> -t {lr2|lr4|lr8}

# Examples
japi_cli setup get speaker array eq all 1
japi_cli setup set speaker array eq band 1 2 -f 500 -g -2.0 -q 1.5 -t lowshelf
japi_cli setup set speaker array fir 1 -f array_tuning.wav
japi_cli setup set speaker array crossover 1 -f 2500 -t lr4
```

**Preset Layer** - Preset-based processing (mostly read-only):
```bash
# Preset EQ
japi_cli setup get speaker preset eq all <CH>
japi_cli setup get speaker preset eq band <CH> <BAND>

# Preset FIR
japi_cli setup get speaker preset fir <CH>

# Preset Crossover
japi_cli setup get speaker preset crossover <CH>

# Preset Limiters
japi_cli setup get speaker preset limiter peak <CH>
japi_cli setup get speaker preset limiter rms <CH>
japi_cli setup get speaker preset limiter clip <CH>

# Examples
japi_cli setup get speaker preset eq all 1
japi_cli setup get speaker preset eq band 1 1
japi_cli setup get speaker preset limiter peak 1
japi_cli setup get speaker preset limiter rms 1
```

#### Summing Matrix Commands

```bash
# Show
japi_cli setup get summing-matrix row <OUT_CH>        # Show all inputs for output
japi_cli setup get summing-matrix cell <OUT_CH> <IN_CH>  # Show specific cell

# Set
japi_cli setup set summing-matrix cell <OUT_CH> <IN_CH> <VALUE>  # Set cell gain (dB)

# Examples
japi_cli setup get summing-matrix row 1
japi_cli setup get summing-matrix cell 1 2
japi_cli setup set summing-matrix cell 1 2 -3.0
```

#### install info Commands

```bash
# Show install info (device name, venue, installer, etc.)
japi_cli setup get install

# Set install info fields
japi_cli setup set install --device-name "Studio_Main"
japi_cli setup set install --venue "Main_Hall"
japi_cli setup set install --venue "Main_Hall" --device-name "Studio_Main"
japi_cli setup set install --installer "John Doe" --contact "john@example.com"

# Examples
japi_cli setup get install
japi_cli setup set install --venue "Main_Hall" --device-name "Main-Hall"
```

#### Amp Commands

```bash
# Show
japi_cli setup get amp mode <CH>           # Show amp mode
japi_cli setup get amp impedance <CH>      # Show amp impedance

# Set
japi_cli setup set amp mode <CH> {standby|active}  # Set amp mode

# Examples
japi_cli setup get amp mode 1
japi_cli setup set amp mode 1 active
```

#### Generator Commands

```bash
# Show
japi_cli setup get generator config        # Generator config
japi_cli setup get generator sine          # Sine generator
japi_cli setup get generator pink          # Pink noise generator

# Set
japi_cli setup set generator enable {on|off}  # Enable/disable
japi_cli setup set generator sine -f <FREQ> -g <GAIN>  # Configure sine

# Examples
japi_cli setup get generator config
japi_cli setup set generator enable on
japi_cli setup set generator sine -f 1000 -g -20
```

#### GPIO Commands

```bash
# Show
japi_cli setup get gpio pin <PIN>          # Show specific pin
japi_cli setup get gpio all                # Show all pins

# Set
japi_cli setup set gpio pin <PIN> {high|low}  # Set pin value

# Examples
japi_cli setup get gpio pin 1
japi_cli setup set gpio pin 1 high
```

### 5. Status Commands

Query device runtime status (read-only, volatile state):

```bash
# Get complete device status
japi_cli status get all                    # All status info

# Get specific status categories
japi_cli status get info                   # Static device info (serial, model, hardware/software IDs)
japi_cli status get state                  # Device state (power, uptime, find-me)
japi_cli status get network                # Network interfaces (LAN1, LAN2, Dante)
japi_cli status get audio                  # Audio status (sample rate, sync)
japi_cli status get firmware               # Firmware versions
```

**Status vs Setup:**
- **Status** - Runtime state (read-only, volatile) - device info, power, uptime, network state
- **Setup** - Configuration (read/write, persistent) - EQ, gain, network settings, user metadata

### 6. Subscribe Commands

Subscribe to real-time device updates:

```bash
# Setup changes
japi_cli subscribe setup                    # All setup changes
japi_cli subscribe setup speaker/1 speaker/2  # Specific paths
japi_cli subscribe setup -t 60              # With 60s timeout

# Device metrics
japi_cli subscribe metrics -i 1000          # Metrics every 1s
japi_cli subscribe metrics -i 500 -t 300    # Every 500ms, 5min timeout

# Device events
japi_cli subscribe events                   # All events
japi_cli subscribe events -l warning        # Warnings and errors only
japi_cli subscribe events -l error -t 600   # Errors only, 10min timeout
```

---

## Interactive Mode

Start an interactive REPL session:

```bash
japi_cli -i

# Or specify target
japi_cli -i -t 192.168.1.50 -p 8080 -v
```

In interactive mode, omit the `japi_cli` prefix:

```
japi> setup get speaker gain 1
Response: {"gain": -6.0}

japi> setup set speaker gain 1 -3.0
Response: {"status": "ok"}

japi> preset create 1 -n "Test" -v "1.0"
Preset created: Test_1.0.json

japi> status get info
Response: {...}

japi> exit

---

## Design Principles

### 1. Channel Number Placement

**Consistency Rule**: Channel numbers always come at the **end** of command paths.

✅ **Correct**:
```bash
setup get speaker preset limiter peak <CH>
setup get input gain <CH>
preset create <CH> -n "Name" -v "1.0"
```

❌ **Incorrect**:
```bash
setup get speaker <CH> preset limiter peak
setup get input <CH> gain
preset <CH> create -n "Name" -v "1.0"
```

**Rationale**:
- Better tab completion (group by type, not by channel)
- Cleaner conceptual hierarchy (navigate to feature → specify channel)
- Consistent with CLI best practices
- Easier to remember and use

### 2. Speaker Processing Hierarchy

Three distinct layers in order of signal flow:

1. **User Layer** - User-adjustable EQ and FIR (end-user control)
2. **Array Layer** - Array-level tuning: EQ, FIR, crossover (system integrator)
3. **Preset Layer** - Preset-defined processing: EQ, FIR, crossover, limiters (manufacturer)

Each layer serves a different purpose and audience.

### 3. Get vs Set Pattern

All setup commands follow the `setup {get|set}` pattern:
- `get` - Read configuration
- `set` - Write configuration

This provides clear intent and prevents accidental modifications.

Status commands only support `get` (read-only):
- `status get` - Read runtime state
- No `status set` - Status is derived from device operation

---

## Examples

### Complete Workflow Examples

**Setting up a speaker channel:**
```bash
# 1. Load a preset
japi_cli preset apply 1 -f jbl_srx835p.json

# 2. View preset limiter settings
japi_cli setup get speaker preset limiter peak 1

# 3. Set user EQ adjustment
japi_cli setup set speaker user eq band 1 1 -f 100 -g -2.0 -q 1.0 -t lowshelf

# 4. Set array crossover
japi_cli setup set speaker array crossover 1 -f 1800 -t lr4

# 5. Set final gain
japi_cli setup set speaker gain 1 -6.0

# 6. Save current configuration as new preset
japi_cli preset create 1 -n "JBL_SRX835P_Custom" -v "1.0"
```

**Monitoring device in real-time:**
```bash
# Terminal 1: Subscribe to setup changes
japi_cli subscribe setup speaker/1 speaker/2

# Terminal 2: Make changes
japi_cli setup set speaker gain 1 -3.0
# Changes appear immediately in Terminal 1

# Terminal 3: Subscribe to metrics
japi_cli subscribe metrics -i 500
# See temperature, voltage, etc. every 500ms
```

**Using with scripts:**
```bash
# Get current gain value
GAIN=$(japi_cli -q setup get speaker gain 1 | jq -r '.gain')
echo "Current gain: $GAIN dB"

# Set multiple channels in loop
for ch in 1 2 3 4; do
  japi_cli setup set speaker gain $ch -6.0
  echo "Set channel $ch gain to -6.0 dB"
done

# Batch operations with quiet mode
japi_cli -q preset create 1 -n "Channel1" -v "1.0" > /dev/null && echo "✓ Preset created"
```

---

## Development

### Project Structure

```
japi_cli/
├── japi_cli.py              # Main entry point
├── japi_cli_base.py         # Base classes
├── japi_cli_interactive.py  # Interactive REPL
└── groups/                  # Command groups
    ├── __init__.py
    ├── api.py              # API commands
    ├── device.py           # Device commands
    ├── preset.py           # Preset commands
    ├── setup.py            # Setup commands (largest)
    ├── status.py           # Status commands
    └── subscribe.py        # Subscribe commands
```

### Adding New Commands

1. Choose appropriate group file in `groups/`
2. Register command in `register_commands()` method
3. Create SubCommand class with async `run()` method
4. Use base class helpers for JSON-RPC

Example:

```python
def _register_my_commands(subparsers):
    """Register my commands."""
    my_parser = subparsers.add_parser("mycommand", help="My command")
    my_parser.add_argument("value", type=int, help="Value")
    my_parser.set_defaults(command_cls=MyCommand)


class MyCommand(SubCommand):
    """My command description."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(
            args.target,
            args.port,
            "my_rpc_method",
            {"value": args.value},
            args.verbose,
            args.quiet,
        )
```

---

## Troubleshooting

### Tab Completion Not Working

```bash
# Re-source the completion script
source setup_completion.sh

# Or add to shell config
echo "source $(pwd)/setup_completion.sh" >> ~/.bashrc  # or ~/.zshrc
```

### Connection Errors

```bash
# Test connectivity
ping 192.168.64.100

# Test with verbose mode
japi_cli -v api ping

# Try different port
japi_cli -t 192.168.64.100 -p 8080 api ping
```

### Interactive Mode Issues

```bash
# Make sure -i flag is present
japi_cli -i -t 192.168.1.50

# Check Python version
python --version  # Should be 3.7+
```

### Command Not Found

```bash
# Install in development mode
pip install -e .

# Or run directly
python japi_cli.py status get info
```

---

## License

See LICENSE file for details.
