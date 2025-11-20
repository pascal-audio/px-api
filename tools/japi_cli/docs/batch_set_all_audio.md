# Batch Set All Audio Command

## Overview
The `batch_set_all_audio` command sends all current audio endpoint values to the device using a single JSON-RPC batch request. This is useful for reapplying audio configuration or testing batch request performance.

## Usage
```bash
python japi_cli.py batch_set_all_audio [-t TARGET] [-p PORT] [-v]
```

### Options
- `-t, --target`: Target device IP address (default: 127.0.0.1)
- `-p, --port`: Target device port (default: 80)
- `-v, --verbose`: Enable verbose output including round-trip time

## What It Does

1. **Retrieves current setup**: Calls `setup_get_all` to get all current configuration
2. **Builds batch request**: Constructs a JSON-RPC batch array with all audio endpoints
3. **Sends batch**: Transmits the batch request in a single WebSocket message
4. **Reports results**: Shows success/failure count for batch operations

## Included Endpoints

### Audio Inputs
- `/audio/input/analog/{1-4}` - Analog input channels (gain, delay, mute, name)
- `/audio/input/digital/{1-4}` - Digital input channels (gain, delay, mute, name)
- `/audio/input/network/{1-4}` - Network input channels (gain, delay, mute, name)
- `/audio/input/config` - Input configuration (analog/digital selection)
- `/audio/input/generator` - Signal generator settings

### Audio Outputs
- `/audio/output/summing_matrix` - Input to output summing matrix
- `/audio/output/speaker/{1-4}` - Speaker output routing (primary_src, fallback_src, name)
- `/audio/output/digital/{1-4}` - Digital output channels
- `/audio/output/network/{1-4}` - Network output channels

### User Processing (per speaker channel)
- `/audio/output/speaker/{ch}/user` - User processing (mute, gain, polarity, delay, hpf, generator_mix)
- `/audio/output/speaker/{ch}/user/eq` - User EQ settings
- `/audio/output/speaker/{ch}/user/eq/bands/{1-10}` - Individual user EQ bands

### Array Processing (per speaker channel)
- `/audio/output/speaker/{ch}/array` - Array processing (gain, polarity, delay)
- `/audio/output/speaker/{ch}/array/eq` - Array EQ settings
- `/audio/output/speaker/{ch}/array/eq/bands/{1-5}` - Individual array EQ bands
- `/audio/output/speaker/{ch}/array/fir` - Array FIR filter coefficients

### Preset Processing (per speaker channel)
- `/audio/output/speaker/{ch}/preset` - Preset processing settings (mode, gain, delay, polarity, hpf)
- `/audio/output/speaker/{ch}/preset/crossover` - Crossover settings
- `/audio/output/speaker/{ch}/preset/eq` - Preset EQ settings
- `/audio/output/speaker/{ch}/preset/eq/bands/{1-10}` - Individual preset EQ bands
- `/audio/output/speaker/{ch}/preset/fir` - Preset FIR filter coefficients
- `/audio/output/speaker/{ch}/preset/peak_limiter` - Peak limiter settings
- `/audio/output/speaker/{ch}/preset/rms_limiter` - RMS limiter settings
- `/audio/output/speaker/{ch}/preset/clip_limiter` - Clip limiter settings

## Excluded Endpoints

### Device Settings (intentionally excluded)
- `/install` - Installation information
- `/power` - Power settings
- `/gpio` - GPIO settings
- `/network/lan1` - LAN 1 network setup
- `/network/lan2` - LAN 2 network setup

## Example Output

```bash
$ python japi_cli.py batch_set_all_audio -v

Sending message: {"jsonrpc":"2.0","method":"setup_get_all","id":1}
Response: {...}
Sending batch request with 87 audio endpoints...
Round trip time: 142.3 ms
Batch complete: 87 succeeded, 0 failed
```

## Use Cases

1. **Configuration Replication**: Reapply all audio settings after a device reset
2. **Performance Testing**: Test batch request handling and response times
3. **Sync Multiple Devices**: Copy complete audio configuration between similar devices
4. **Full Audio Refresh**: Reapply all user, array, and preset processing settings

## Technical Details

- Uses JSON-RPC 2.0 batch request format (array of request objects)
- Each request in the batch has a unique ID for tracking
- Responses are correlated by ID to determine success/failure
- All requests in a batch are processed by the server
- Batch processing is more efficient than individual requests

## Related Commands

- `setup_get_all`: Get all device configuration
- Individual `set_*` commands: Set specific endpoints one at a time
- `device_backup`/`device_restore`: Full device configuration backup/restore
