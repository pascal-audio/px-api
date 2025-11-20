# Preset Management

**PX Control API v1.0.0**

Complete guide to channel presets: creating, applying, locking, and workflows.

---

## Table of Contents

- [Preset Concepts](#preset-concepts)
- [Creating Presets](#creating-presets)
- [Applying Presets](#applying-presets)
- [Preset Locking](#preset-locking)
- [Binary Presets](#binary-presets)
- [Workflows](#workflows)

---

## Preset Concepts

### What is a Preset?

A **preset** is a snapshot of a channel's **preset layer** processing configuration. This includes:

- Drive mode
- Gain
- Polarity
- Delay
- Crossover settings
- EQ (15 bands)
- FIR filter
- Clip limiter
- Peak limiter
- RMS limiter

**Key Points:**
- Presets capture **only** the preset layer (not user or array layers)
- User/array processing remains independent
- Multiple presets can be created for A/B testing
- Presets can be locked (vendor-controlled)

### 3-Layer Architecture Recap

```
┌──────────────────────────────────────────────────────┐
│ Signal Flow: Input → User → Array → Preset → Output │
└──────────────────────────────────────────────────────┘

USER LAYER (user-controlled)
  - Gain, polarity, delay
  - EQ (10 bands)
  - FIR filter
  - HPF, mute
  - Generator mix

ARRAY LAYER (installer-controlled)
  - Gain, polarity, delay
  - EQ (5 bands)
  - FIR filter

PRESET LAYER (factory/vendor-controlled)
  - Drive mode
  - Crossover
  - EQ (15 bands)
  - FIR filter
  - Limiters (peak, RMS)
  ← Presets capture THIS layer
```

**Use Cases:**
- **User Layer:** End-user adjustments (room EQ, gain trim)
- **Array Layer:** Installer tuning (array processing, splay EQ)
- **Preset Layer:** Factory voicing (speaker model, drive mode, protection)

---

## Creating Presets

### Create from Current Configuration

```python
import json

# Create preset from channel 1's current preset layer
from datetime import datetime, timezone
result = await client.request('preset_create', {
  'channel': 1,
  'name': 'Studio Monitor - Flat',
  'version': '1.0',
  'created_date': datetime.now(timezone.utc).isoformat(),
  'vendor_lock': False
})

print('Preset ID:', result['metadata']['id'])          # 'preset-uuid-12345'
print('Preset JSON:', json.dumps(result['preset'], indent=2))
```

**Created Preset Structure:**
```typescript
{
  id: 'preset-uuid-12345';
  metadata: {
    name: 'Studio Monitor - Flat';
    description: 'Flat response for studio monitoring';
    author: 'Pascal Audio';
    version: '1.0';
    created: '2025-11-17T14:30:00Z';
    device_model: 'PX4004';
    firmware_version: '1.2.3';
  };
  config: {
    drive_mode: 'linear';
    gain: 0.0;
    polarity: false;
    delay: { enabled: false; value: 0.0 };
    crossover: { /* ... */ };
    eq: { bands: [ /* ... */ ] };
    fir: { /* ... */ };
    limiter_peak: { /* ... */ };
    limiter_rms: { /* ... */ };
  };
}
```

### Create Multiple Presets

```python
import json

# Create presets for all 4 channels
from datetime import datetime, timezone
presets = []

for ch in range(1, 5):
    try:
        result = await client.request('preset_create', {
            'channel': ch,
            'name': f'Channel {ch} - Reference',
            'version': '1.0',
            'created_date': datetime.now(timezone.utc).isoformat(),
            'vendor_lock': False
        })
        
        preset_data = result['preset']
        presets.append(preset_data)
        
        # Save to file
        with open(f'preset-ch{ch}.json', 'w') as f:
            json.dump(preset_data, f, indent=2)
    except ValueError as e:
        if 'Invalid channel' in str(e):
            break  # Device has fewer channels

print(f'✓ Created {len(presets)} presets')
```

---

## Applying Presets

### Apply Preset from JSON

```python
import json

# Load preset from file
with open('studio-flat.json', 'r') as f:
    preset = json.load(f)

# Apply to channel 1
await client.request('preset_apply', {
  'channel': 1,
  'preset': preset
})

print('Preset applied to channel 1')
```

### Apply with Validation

```python
# Assuming preset was obtained from preset_create or loaded from file
from datetime import datetime, timezone
result = await client.request('preset_create', {
    'channel': 1,
    'name': 'My Preset',
    'version': '1.0',
    'created_date': datetime.now(timezone.utc).isoformat(),
    'vendor_lock': False
})
preset_data = result['preset']  # From previous preset_create call

try:
    await client.request('preset_apply', {
        'channel': 1,
        'preset': preset_data
    })
    print('✓ Preset applied successfully')
except Exception as error:
    # Check JSON-RPC error response
    error_msg = str(error)
    if 'PRESET_INVALID' in error_msg:
        print('Preset corrupted or incompatible')
    elif 'PRESET_LOCKED' in error_msg:
        print('Preset is vendor-locked')
    else:
        raise
```

### Apply Across Channels

```python
import json

# Clone preset to all channels
with open('reference.json', 'r') as f:
    preset = json.load(f)

for ch in range(1, 5):
    await client.request('preset_apply', {
        'channel': ch,
        'preset': preset
    })
    print(f'Applied to channel {ch}')
```

---

## Preset Locking

### Vendor-Locked Presets

Presets can be **locked** to prevent modification. Locked fields return `None` when read.

```python
# Read preset layer gain (unlocked preset)
gain = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/preset/gain'
})
print('Gain:', gain)  # 0.0

# Read locked preset's gain
locked_gain = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/preset/gain'
})
print('Gain:', locked_gain)  # None (locked)
```

### Check Locked Fields

```python
# Check scalar fields in preset object
preset = await client.request('setup_get', {
    'path': '/audio/output/speaker/1/preset'
})

scalar_fields = ['gain', 'polarity', 'delay']
for field in scalar_fields:
    if preset.get(field) is None:
        print(f'✗ {field} is locked')
    else:
        print(f'✓ {field} is accessible')

# Check complex objects (must query at their own paths)
complex_paths = [
    'eq',
    'crossover', 
    'peak_limiter',
    'rms_limiter'
]

for path in complex_paths:
    try:
        obj = await client.request('setup_get', {
            'path': f'/audio/output/speaker/1/preset/{path}'
        })
        print(f'✓ {path} is accessible')
    except ValueError as error:
        if 'PRESET_LOCKED' in str(error):
            print(f'✗ {path} is locked')
```

### Create Locked Preset

Locked presets use **binary encryption** (`.px-preset` format). See [Binary Presets](#binary-presets).

---

## Binary Presets

### What are Binary Presets?

Binary presets (`.px-preset` files) are:
- Encrypted
- Vendor-locked (**ALL** fields in preset layer return `null` when read)
- Tamper-proof
- Signed

**Use Cases:
- Factory presets
- Proprietary tunings
- Commercial speaker models
- Protected intellectual property

### Apply Binary Preset

```python
import base64

# Load binary preset
with open('factory-model-xyz.px-preset', 'rb') as f:
    binary_data = f.read()
    b64_data = base64.b64encode(binary_data).decode('utf-8')

# Apply to channel
await client.request('preset_apply', {
  'channel': 1,
  'preset_binary': b64_data
})

print('✓ Binary preset applied')
```

### Locked Preset Behavior

When a locked preset is applied:

```python
# Preset scalar fields are locked (None/unavailable)
preset = await client.request('setup_get', {
  'path': '/audio/output/speaker/1/preset'
})
print(f"Gain: {preset.get('gain')}")  # None (locked)

# Preset complex objects return PRESET_LOCKED error
try:
    crossover = await client.request('setup_get', {
        'path': '/audio/output/speaker/1/preset/crossover'
    })
except ValueError as error:
    print('Crossover locked')  # PRESET_LOCKED error

# User/array layers remain accessible
user = await client.request('setup_get', {
    'path': '/audio/output/speaker/1/user'
})
print(f"User gain: {user['gain']}")  # 0.0 (accessible)

# Can still adjust user layer
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {'gain': -3.0}
})
```

**Key Insight:** Locked presets protect factory tuning while allowing user/installer adjustments in their layers.

---

## Clear Preset

### Restore Default Preset

```python
# Clear channel 1 preset (restore factory default)
await client.request('preset_clear', {
  'channel': 1
})

print('Preset cleared, factory defaults restored')
```

**Use Cases:**
- Remove custom preset
- Troubleshooting
- Return to known state

---

## Workflows

### Workflow 1: Factory Preset Distribution

```python
import asyncio

async def ab_test_presets(client, channel: int):
    # Create preset A (current state)
    from datetime import datetime, timezone
    preset_a = await client.request('preset_create', {
        'channel': channel,
        'name': 'Preset A - Original',
        'version': '1.0',
        'created_date': datetime.now(timezone.utc).isoformat(),
        'vendor_lock': False
    })
    print('✓ Preset A created')

    # User makes adjustments to preset layer...
    # (via setup_set on preset paths)

    # Create preset B (modified state)
    preset_b = await client.request('preset_create', {
        'channel': channel,
        'name': 'Preset B - Modified',
        'version': '1.0',
        'created_date': datetime.now(timezone.utc).isoformat(),
        'vendor_lock': False
    })
    print('✓ Preset B created')

    # Toggle between presets
    print('Applying Preset A...')
    await client.request('preset_apply', {
        'channel': channel,
        'preset': preset_a['preset']
    })
    await asyncio.sleep(5)

    print('Applying Preset B...')
    await client.request('preset_apply', {
        'channel': channel,
### Workflow 2: Installer Custom Tuning

```python
import json
import base64

async def installer_workflow(client):
    # 1. Apply factory preset (locked)
    with open('factory-locked.px-preset', 'rb') as f:
        factory_preset = f.read()
        b64_preset = base64.b64encode(factory_preset).decode('utf-8')
    
    await client.request('preset_apply', {
        'channel': 1,
        'preset_binary': b64_preset
    })
    print('✓ Factory preset applied (locked)')

    # 2. Installer tunes array layer (accessible)
    await client.request('setup_set', {
        'path': '/audio/output/speaker/1/array',
        'value': {'gain': -2.0}
    })

    await client.request('setup_set', {
        'path': '/audio/output/speaker/1/array',
        'value': {'delay': 12.5}
    })

    print('✓ Array layer tuned')

    # 3. User adjusts user layer (accessible)
    await client.request('setup_set', {
        'path': '/audio/output/speaker/1/user',
        'value': {'gain': -1.5}
    })

    print('✓ User layer adjusted')

    # 4. Backup full config
    backup = await client.request('backup_create', {})
    
    # Decode base64 and save binary
    config_binary = base64.b64decode(backup['config'])
    with open('site-config.bin', 'wb') as f:
        f.write(config_binary)

    print('✓ Configuration backed up')
```

### Workflow 3: Multi-Channel Preset Clone

```python
async def clone_preset(
    client,
    source_channel: int,
    target_channels: list[int]
):
    # Create preset from source
    from datetime import datetime, timezone
    preset = await client.request('preset_create', {
        'channel': source_channel,
        'name': f'Cloned from CH{source_channel}',
        'version': '1.0',
        'created_date': datetime.now(timezone.utc).isoformat(),
        'vendor_lock': False
    })

    print(f'✓ Created preset from channel {source_channel}')

    # Apply to targets
    for target in target_channels:
        await client.request('preset_apply', {
            'channel': target,
            'preset': preset['preset']
        })

        print(f'✓ Applied to channel {target}')

# Clone channel 1 to channels 2, 3, 4
await clone_preset(client, 1, [2, 3, 4])
```

---

## Best Practices

### 1. Version Presets

Always include version metadata:
```python
from datetime import datetime, timezone
preset = await client.request('preset_create', {
    'channel': 1,
    'name': 'Studio Monitor',
    'version': '1.2.0',  # Semantic versioning
    'created_date': datetime.now(timezone.utc).isoformat(),
    'vendor_lock': False
})
```

### 2. Backup Before Applying

```python
# Backup current preset
from datetime import datetime, timezone
backup = await client.request('preset_create', {
    'channel': 1,
    'name': 'Backup',
    'version': '1.0',
    'created_date': datetime.now(timezone.utc).isoformat(),
    'vendor_lock': False
})

# Load and apply new preset
with open('new_preset.json', 'r') as f:
    new_preset_data = json.load(f)

await client.request('preset_apply', {
    'channel': 1,
    'preset': new_preset_data
})

# On error, restore backup
try:
    await client.request('preset_apply', {'channel': 1, 'preset': new_preset_data})
except Exception as error:
    # Restore backup on failure
    await client.request('preset_apply', {'channel': 1, 'preset': backup['preset']})
    raise
```

### 3. Validate Preset Compatibility

```python
import json

with open('preset.json', 'r') as f:
    preset = json.load(f)

# Check firmware version
version = await client.request('api_version', {})
if preset['metadata']['firmware_version'] != version['firmware_version']:
    print('⚠️ Preset created on different firmware version')

# Check device model
info = await client.request('status_get', {'path': '/info'})
if preset['metadata']['device_model'] != info['model_name']:
    print('⚠️ Preset created for different device model')
```

### 4. Store Unlocked JSON with Locked Presets

**CRITICAL:** When creating locked binary presets, always save an unlocked JSON version for your records:

```python
import json
import base64

# 1. Create unlocked JSON preset first
from datetime import datetime, timezone
preset = await client.request('preset_create', {
    'channel': 1,
    'name': 'Factory Model XYZ',
    'version': '2.1.0',
    'created_date': datetime.now(timezone.utc).isoformat(),
    'vendor_lock': False
})

# 2. Save unlocked JSON for internal use
with open('model-xyz-unlocked.json', 'w') as f:
    json.dump(preset['preset'], f, indent=2)

print('✓ Unlocked JSON saved')

# 3. Create locked binary version (offline process)
# Use proprietary tooling to encrypt preset_json → .px-preset file
# This locks ALL fields in the preset layer

# 4. Distribute locked binary to customers
with open('model-xyz-locked.px-preset', 'rb') as f:
    locked_binary = f.read()
    locked_b64 = base64.b64encode(locked_binary).decode('utf-8')

await client.request('preset_apply', {
    'channel': 1,
    'preset_binary': locked_b64
})

print('✓ Locked preset applied to customer device')
```

**Why this matters:**
- Locked presets make **ALL preset layer fields** unreadable (`null`)
- You cannot extract settings from a locked preset
- Keep unlocked JSON for version control, modifications, and troubleshooting
- Only distribute locked `.px-preset` files to protect IP

### 5. Test Before Distribution

```python
async def test_preset(client, preset: dict):
    # Apply to test channel
    await client.request('preset_apply', {
        'channel': 1,
        'preset': preset
    })

    # Verify applied correctly
    applied_gain = await client.request('setup_get_value', {
        'path': '/audio/output/speaker/1/preset/gain'
    })

    print('Applied gain:', applied_gain)

    # Check for errors
    logs_result = await client.request('logs_get', {'limit': 10})
    errors = [log for log in logs_result['logs'] if log['level'] == 'error']

    if len(errors) > 0:
        raise Exception('Preset caused errors')

    print('✓ Preset validated')
```

---

*PX Control API v1.0.0 - © 2025 Pascal Audio*
