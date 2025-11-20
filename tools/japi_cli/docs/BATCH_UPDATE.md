# Batch Set All Audio Command - Update Summary

## Changes Made

The `batch_set_all_audio` command has been updated to **include preset processing endpoints** as requested.

### What's Included Now

The command sends ALL audio endpoints in a single JSON-RPC batch request:

#### Audio Inputs
- Analog, digital, and network input channels (gain, delay, mute, name)
- Input configuration (analog/digital selection)
- Signal generator settings

#### Audio Outputs
- Summing matrix
- Speaker, digital, and network output routing
- User processing (mute, gain, polarity, delay, HPF, EQ with 10 bands, generator mix)
- Array processing (gain, polarity, delay, EQ with 5 bands, FIR filter)
- **Preset processing (NOW INCLUDED)**:
  - Main preset settings (mode, gain, delay, polarity, HPF)
  - Crossover settings
  - Preset EQ with bands
  - Preset FIR filter
  - Peak limiter
  - RMS limiter
  - Clip limiter

### What's Excluded

Only **device settings** are excluded:
- `/install` - Install information  
- `/power` - Power
- `/gpio` - GPIO settings
- `/network/lan1`, `/network/lan2` - Network configuration

## Files Modified

1. **japi_cli_set.py**
   - Updated help text to remove "preset" from exclusions
   - Added code to include all preset processing endpoints in batch
   - Added handling for: preset main, crossover, EQ, EQ bands, FIR, peak_limiter, rms_limiter, clip_limiter

2. **README.md**
   - Updated batch command description
   - Clarified what's included/excluded

3. **docs/batch_set_all_audio.md**
   - Moved preset processing from "Excluded" to "Included" section
   - Added detailed list of all preset endpoints
   - Updated use cases

4. **examples/batch_audio.sh**
   - Updated script to reflect preset processing inclusion

## Usage

```bash
# Send all audio values including preset processing
python japi_cli.py batch_set_all_audio

# With verbose output
python japi_cli.py batch_set_all_audio -v

# To specific device
python japi_cli.py -t 192.168.1.100 batch_set_all_audio
```

## Implementation Details

The preset processing data is extracted from the setup response and sent as separate batch requests for:
- Main preset settings (excluding nested objects)
- Crossover (if present)
- EQ settings and all bands (if present)
- FIR filter (if present)
- Each limiter type (if present)

This ensures complete audio configuration replication including factory preset settings.
