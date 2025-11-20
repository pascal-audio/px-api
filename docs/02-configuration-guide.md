# Configuration Guide

**PX Control API v1.0.0**

Complete guide to the PX device configuration system - setup tree architecture, 3-layer processing model, and configuration operations.

---

## Table of Contents

- [Setup Tree Architecture](#setup-tree-architecture)
- [3-Layer Audio Processing](#3-layer-audio-processing)
- [JSON Path Addressing](#json-path-addressing)
- [Reading Configuration](#reading-configuration)
- [Writing Configuration](#writing-configuration)
- [Subscriptions](#subscriptions)
- [Common Paths Reference](#common-paths-reference)
- [Configuration Workflows](#configuration-workflows)

---

## Setup Tree Architecture

The PX device configuration is organized as a hierarchical **Setup Tree** - a structured JSON object defining all device parameters:

- **Hierarchical** - Organized by domain (audio, network, device)
- **Addressable** - Each value accessible via JSON path
- **Persistent** - Auto-saved to storage (5-second debounced write)
- **Validated** - All changes validated before application
- **Versioned** - Migration support for firmware updates

### Root Structure

```python
{
  'audio': {
    'input': {
      'analog': {'1': {...}, '2': {...}, '3': {...}, '4': {...}},
      'digital': {'1': {...}, '2': {...}, '3': {...}, '4': {...}},
      'network': {'1': {...}, '2': {...}, ...}
    },
    'output': {
      'speaker': {
        '1': {'gain': ..., 'mute': ..., 'user': ..., 'array': ..., 'preset': ...},
        '2': {'gain': ..., 'mute': ..., 'user': ..., 'array': ..., 'preset': ...},
        '3': {'gain': ..., 'mute': ..., 'user': ..., 'array': ..., 'preset': ...},
        '4': {'gain': ..., 'mute': ..., 'user': ..., 'array': ..., 'preset': ...}
      }
    }
  },
  'network': {
    'lan': {'mode': ..., 'ip_address': ..., 'netmask': ..., 'gateway': ...},
    'dante': {'name': ..., 'sample_rate': ...}
  },
  'device': {
    'name': str,
    'location': str
  }
}
```

### Audio Domain

```
audio/
├── input/
│   ├── analog/
│   │   ├── 1/
│   │   │   ├── name: string
│   │   │   ├── gain: number (-60 to 12 dB)
│   │   │   └── mute: boolean
│   │   └── 2..4/ (same structure)
│   ├── digital/
│   │   ├── 1/
│   │   │   ├── name: string
│   │   │   ├── gain: number (-60 to 12 dB)
│   │   │   └── mute: boolean
│   │   └── 2..4/ (same structure)
│   └── network/
│       ├── 1/
│       │   ├── name: string
│       │   ├── gain: number (-60 to 12 dB)
│       │   └── mute: boolean
│       └── 2..N/ (same structure)
│
└── output/
    └── speaker/
        ├── 1/
        │   ├── name: string
        │   ├── source: string (input routing)
        │   ├── gain: number (-60 to 12 dB)
        │   ├── mute: boolean
        │   ├── user/     # User Layer
        │   ├── array/    # Array Layer
        │   └── preset/   # Preset Layer
        └── 2..4/ (same structure)
```

---

## 3-Layer Audio Processing

PX devices use a **3-layer signal processing chain** for speaker outputs. This provides separation between user controls, installer tuning, and factory presets.

### Signal Flow

```
Audio Input
    ↓
┌──────────────────────┐
│   USER LAYER         │  End-user adjustments
│   - Mute             │  Full control
│   - Gain             │  Real-time changes
│   - Polarity         │
│   - Delay            │
│   - HPF              │
│   - Generator mix    │
│   - EQ (10 bands)    │  
└──────────────────────┘
    ↓
┌──────────────────────┐
│   ARRAY LAYER        │  Installer tuning
│   - Gain             │  Array-specific setup
│   - Polarity         │
│   - Delay            │
│   - EQ (5 bands)     │  
│   - FIR filter       │
└──────────────────────┘
    ↓
┌──────────────────────┐
│   PRESET LAYER       │  Factory presets
│   - Drive mode       │  read-only if
│   - Gain             │  Vendor-locked
│   - Polarity         │
│   - Delay            │
│   - Crossover        │  
│   - EQ (15 bands)    │
│   - FIR filter       │
│   - Limiters         │
└──────────────────────┘
    ↓
Amplifier Output
```

### Layer Details

#### 1. User Layer
**Path:** `/audio/output/speaker/{1-4}/user/`

**Who:** End users, operators  
**Purpose:** Day-to-day adjustments, room tuning, show-specific changes  
**Access:** Full read/write

**Parameters:**
- `mute`: boolean
- `gain`: -144 to +12 dB
- `polarity`: `-1` | `1` |
- `delay`: 0 to 2.0 sec
- `hpf`: filter type (off, BUT12, BUT24, LR12, LR24)
- `hpf_freq`: filter freq (10-22kHz)
- `generator_mix`: Test signal mix (Off, Replace, Mix)
- `eq`: 10-band parametric EQ

**Example:**
```python
# User adjusts gain for venue
await client.request('setup_set_value', {
  'path': '/audio/output/speaker/1/user/gain',
  'value': -3.0
})

# User tweaks EQ
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user/eq/bands/3',
    'value': {
        'kind': 'parametric',
        'frequency': 1000,
        'gain': 2.0,
        'q': 1.4,
  }
})
```

#### 2. Array Layer
**Path:** `/audio/output/speaker/{1-4}/array/`

**Who:** System installers, integrators  
**Purpose:** Array configuration, permanent venue tuning  
**Access:** Full read/write (typically locked from users via control system)

**Parameters:**
- `gain`: -60 to +12 dB
- `polarity`: `-1` | `1` |
- `delay`: 0 to 500 ms
- `eq`: 5-band parametric EQ
- `fir`: FIR filter (up to 64 taps)

**Example:**
```python
# Installer delays rear speaker for array alignment
await client.request('setup_set_value', {
  'path': '/audio/output/speaker/3/array/delay',
  'value': 0.015  # sec
})

# Installer applies array EQ compensation
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/array/eq/bands/1',
    'value': {
    'kind': 'parametric',
    'frequency': 125,
    'gain': -3.0,
    'q': 2.0
  }
})
```

#### 3. Preset Layer
**Path:** `/audio/output/speaker/{1-4}/preset/`

**Who:** Factory (Pascal Audio)  
**Purpose:** Speaker voicing, protection, crossover design  
**Access:** Read-only for most parameters (vendor-locked presets)

**Parameters:**
- `drive_mode`: `"Off"` | `"lo_z"` | `"70v"` | `"100v"`
- `gain`: -15 to +15 dB
- `polarity`: `-1` | `1` |
- `delay`: 0 to 0.01 sec 
- `crossover`: Multi-way crossover (locked)
- `eq`: 15-band parametric EQ (may be locked per-band)
- `fir`: FIR filter (locked)
- `limiters`: Peak/RMS/thermal limiters (locked)

**Example:**
```python
# Apply factory preset (contains locked crossover)
# (Assumes preset JSON loaded from file)
import json
with open('factory-preset.json', 'r') as f:
    factory_preset_data = json.load(f)

await client.request('preset_apply', {
    'channel': 1,
    'preset': factory_preset_data
})

# Read unlocked preset gain
gain = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/preset/gain'
})
print('Preset gain:', gain)  # -3.0

# Try to read locked crossover (returns None)
xr = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/preset/crossover'
})
print('Crossover:', xr)  # None (locked)
```

### Why 3 Layers?

**Separation of concerns:**
- **User** doesn't accidentally break installer tuning
- **Installer** doesn't overwrite factory voicing
- **Factory** protects driver safety (limiters, crossover)

**Example scenario:**
```
User boosts bass (+6dB @ 100Hz in user layer)
  → Doesn't affect array layer delay alignment
  → Doesn't disable factory limiters in preset layer
```

---

## JSON Path Addressing

Every parameter is accessible via a JSON path string:

**Format:** `/{domain}/{category}/{index}/{parameter}[/{sub-parameter}]`

**Examples:**

```python
# Top-level parameters
'/audio/output/speaker/1/name'           # Speaker 1 name
'/audio/output/speaker/1/primary_src'    # Speaker 1 primary source
'/network/lan1/ip_address'               # LAN1 IP address
'/install/device_name'               # Device name

# User layer
'/audio/output/speaker/1/user/gain'
'/audio/output/speaker/1/user/eq/bypass'
'/audio/output/speaker/1/user/eq/bands/3/frequency'

# Array layer
'/audio/output/speaker/1/array/delay'
'/audio/output/speaker/1/array/eq/bands/2/gain'

# Preset layer
'/audio/output/speaker/1/preset/crossover'
'/audio/output/speaker/1/preset/limiters/peak/threshold'

# Inputs
'/audio/input/analog/1/gain'
'/audio/input/network/name'
```

### Path Conventions

- **Lowercase:** All path components lowercase
- **Hyphens:** Use hyphens for multi-word names (`high_pass_filter`)
- **Numeric indices:** Channels use numbers as strings (`"1"`, `"2"`, `"3"`, `"4"`)
- **EQ bands:** One-indexed (`bands/1`, `bands/2`, ...) - User: 1-10, Array: 1-5, Preset: 1-15

---

## Reading Configuration

### Method 1: Get All Configuration

**Use Case:** Initial load, backup, configuration export

```python
# Get hierarchical structure
config = await client.request('setup_get_all', {})

print('Speaker 1 user gain:', config['audio']['output']['speaker']['1']['user']['gain'])
print('Device name:', config['install']['device_name'])
print('LAN1 IP:', config['network']['lan1']['ip_address'])
```

**Flattened mode** (returns leaf objects at each path):

```python
flat = await client.request('setup_get_all', {'flatten': True})

# Flattened mode returns leaf objects containing primitive values
# Each path maps to an object with the primitive fields at that level
user = flat['/audio/output/speaker/1/user']
print(user['gain'])  # -3.0
print(user['polarity'])  # 1 or -1
print(user['mute'])  # true or false

install = flat['/install']
print(install['device_name'])  # 'PX4000.4 0000-00000'

network = flat['/network']
print(network['mode'])  # 'static' or 'dhcp'

# Iterate all paths in flattened structure
for path, leaf_obj in flat.items():
    if isinstance(leaf_obj, dict):
        print(f'{path}: {list(leaf_obj.keys())}')
```

### Method 2: Get Object at Path

**Use Case:** Read section of config tree

```python
# Get entire user processing for speaker 1
user = await client.request('setup_get', {
    'path': '/audio/output/speaker/1/user'
})
print('Gain:', user['gain'])
print('Polarity:', user['polarity'])
print('Mute:', user['mute'])

# Get entire user EQ (separate path)
user_eq = await client.request('setup_get', {
  'path': '/audio/output/speaker/1/user/eq'
})
print('Bypass:', user_eq['bypass'])

# Get specific band
band_3 = await client.request('setup_get', {
  'path': '/audio/output/speaker/1/user/eq/bands/3'
})
print('Band 3 gain:', band_3['gain'])
```

### Method 3: Get Single Value

**Use Case:** Read individual parameter

```python
# Get gain (returns value directly)
gain = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/user/gain'
})
print('Gain:', gain, 'dB')  # -3.0

# Get mute (boolean)
mute = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/user/mute'
})
print('Muted:', mute)  # True/False

# Get speaker name (string)
name = await client.request('setup_get_value', {
  'path': '/audio/output/speaker/1/name'
})
print('Name:', name)  # 'Studio Main L'
```

---

## Writing Configuration

### Method 1: Set Single Value

**Use Case:** Update individual parameter (slider, toggle, text input)

```python
# Set user layer parameters using setup_set with full path
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user',
  'value': {'gain': -3.0}
})

# Set mute
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user',
  'value': {'mute': True}
})

# Set device name
await client.request('setup_set', {
  'path': '/install',
  'value': {'device_name': 'Studio Main L'}
})
```

### Method 2: Set Object

**Use Case:** Update multiple related parameters atomically

```python
# Set entire EQ band
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user/eq/bands/3',
  'value': {
    'frequency': 1000,
    'gain': 3.0,
    'q': 1.4,
    'kind': 'parametric'
  }
})

# Set speaker metadata
await client.request('setup_set', {
    'path': '/audio/output/speaker/1',
    'value': {
        'name': 'Front Left',
        'primary_src': 'analog/1',
        'fallback_src': 'off'
    }
})

# Set network config
await client.request('setup_set', {
    'path': '/network/lan1',
    'value': {
        'network_mode': 'static',
        'ip_address': '192.168.1.100',
        'netmask': '255.255.255.0',
        'gateway': '192.168.1.1'
    }
})
```

### Validation

All `setup_set` and `setup_set_value` calls are validated before application:

- **Range checks:** Numbers within min/max bounds
- **Type validation:** Correct type (string, number, boolean, enum)
- **Enum validation:** Value in allowed set
- **Path validation:** Path exists in setup tree
- **Channel validation:** Channel 1-4 for speaker parameters

**Example validation errors:**

```python
# Out of range
try:
    await client.request('setup_set', {
        'path': '/audio/output/speaker/1/user',
        'value': {'gain': 999.0}  # Max is +15 dB
    })
except ValueError as error:
    error_msg = str(error)
    if 'must be between' in error_msg or 'validation' in error_msg.lower():
        print('Validation failed as expected')

# Invalid channel
try:
    await client.request('setup_set', {
        'path': '/audio/output/speaker/5/user',  # Only 1-4
        'value': {'gain': -3.0}
    })
except ValueError as error:
    error_msg = str(error)
    print('Error:', error_msg)  # Path not handled or invalid channel
    if 'Path not handled' in error_msg:
        print('Channel 5 does not exist (valid range: 1-4)')

# Invalid path
try:
    await client.request('setup_set_value', {
        'path': '/audio/output/speaker/1/invalid_param',
        'value': 123
    })
except ValueError as error:
    error_msg = str(error)
    if 'INVALID_PATH' in error_msg or 'Path not handled' in error_msg:
        print('Invalid path error as expected')
```

### Auto-Save

All configuration changes auto-save to persistent storage:

1. Client calls `setup_set` or `setup_set_value`
2. Device validates and applies immediately
3. Device queues save operation (5-second debounce)
4. After 5 seconds of no changes, writes to storage
5. Survives power loss and reboots

**No explicit save needed** - just set values and they persist automatically.

---

## Subscriptions

### Subscribe to Configuration Changes

Real-time notifications when configuration changes (from any client):

```python
# Subscribe to all speaker 1 changes
def on_change(params):
    print('Changed:', params['path'], '=', params['value'])

sub_id = await client.subscribe('setup_subscribe',
                                {'path': '/audio/output/speaker/1'},
                                on_change)
print('Subscription ID:', sub_id)

# Subscribe to specific parameter
gain_sub_id = await client.subscribe('setup_subscribe',
                                     {'path': '/audio/output/speaker/1/gain'},
                                     on_change)

# Subscribe to ALL config changes (omit path)
all_sub_id = await client.subscribe('setup_subscribe', {}, on_change)
```

### Handle Notifications

Server sends `setup_update` notifications when subscribed config changes:

```python
def on_setup_update(params):
    # Check if it's a config change notification
    print('Config changed:')
    print('  Path:', params['path'])
    print('  Value:', params['value'])
    print('  Timestamp:', params['timestamp'])
    
    # Update UI
    update_ui(params['path'], params['value'])

# Subscribe with callback
await client.subscribe('setup_subscribe', 
                       {'path': '/audio/output/speaker/1'},
                       on_setup_update)
```

**Notification format:**

```ts
{
  jsonrpc: 2.0
  method: 'setup_update'  // Notification method
  params: {
    path: str             // Path that changed
    value: any            // New value
  }
  // NO 'id' field (notifications don't have request IDs)
}
```

### Path Matching

Subscriptions match the exact path and all children:

```python
# Example 1: Subscribe to '/audio'
# This matches:
#   - /audio/output/speaker/1
#   - /audio/input/analog/1
#   - /audio/output/speaker/2
await client.request('setup_subscribe', {'path': '/audio'})

# Example 2: Subscribe to '/audio/output/speaker/1'
# This matches:
#   - /audio/output/speaker/1
#   - /audio/output/speaker/1/user/eq/bands/3
# This does NOT match:
#   - /audio/output/speaker/2
await client.request('setup_subscribe', {'path': '/audio/output/speaker/1'})
```

### Unsubscribe

Always unsubscribe when done to avoid memory leaks:

```python
# Unsubscribe
await client.unsubscribe('setup_unsubscribe', sub_id)
```

### Multi-Client Synchronization

Subscriptions enable multi-client sync:

```
[Client A] → setup_set_value("/audio/output/speaker/1/gain", -3.0)
              ↓
           [Device] validates, applies, saves
              ↓
           [Device] sends setup_update to subscribers
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
[Client B]          [Client C]
Updates UI          Updates UI
```

---

## Common Paths Reference

### Speaker Output Paths

```python
# Top-level speaker parameters
'/audio/output/speaker/{1-4}/name'              # str
'/audio/output/speaker/{1-4}/primary_src'       # Primary input routing
'/audio/output/speaker/{1-4}/fallback_src'      # Fallback input routing

# User layer
"/audio/output/speaker/{1-4}/user/gain"
"/audio/output/speaker/{1-4}/user/polarity"
"/audio/output/speaker/{1-4}/user/delay"
"/audio/output/speaker/{1-4}/user/mute"
"/audio/output/speaker/{1-4}/user/eq/enabled"
"/audio/output/speaker/{1-4}/user/eq/bands/{1-10}/frequency"
"/audio/output/speaker/{1-4}/user/eq/bands/{1-10}/gain"
"/audio/output/speaker/{1-4}/user/eq/bands/{1-10}/q"
"/audio/output/speaker/{1-4}/user/eq/bands/{1-10}/filter_type"
"/audio/output/speaker/{1-4}/user/high_pass_filter/enabled"
"/audio/output/speaker/{1-4}/user/high_pass_filter/frequency"

# Array layer
"/audio/output/speaker/{1-4}/array/gain"
"/audio/output/speaker/{1-4}/array/polarity"
"/audio/output/speaker/{1-4}/array/delay"
"/audio/output/speaker/{1-4}/array/eq/enabled"
"/audio/output/speaker/{1-4}/array/eq/bands/{1-5}/frequency"
"/audio/output/speaker/{1-4}/array/eq/bands/{1-5}/gain"

# Preset layer (may be locked)
"/audio/output/speaker/{1-4}/preset/gain"
"/audio/output/speaker/{1-4}/preset/polarity"
"/audio/output/speaker/{1-4}/preset/delay"
"/audio/output/speaker/{1-4}/preset/drive_mode"
"/audio/output/speaker/{1-4}/preset/crossover"  
"/audio/output/speaker/{1-4}/preset/limiters"   
```

### Input Paths

```python
# Analog inputs
'/audio/input/analog/{1-4}/name'
'/audio/input/analog/{1-4}/gain'
'/audio/input/analog/{1-4}/mute'

# Digital inputs
'/audio/input/digital/{1-4}/name'
'/audio/input/digital/{1-4}/gain'
'/audio/input/digital/{1-4}/mute'

# Network inputs (Dante/AES67)
'/audio/input/network/{1-N}/name'
'/audio/input/network/{1-N}/gain'
'/audio/input/network/{1-N}/mute'
```

### Network Paths

```python
'/network/lan1/mode'                  # 'dhcp' | 'static'
'/network/lan2/ip_address'
'/network/lan2/netmask'
```

---

## Configuration Workflows

### Workflow 1: User Adjusts Gain from UI

```python
# 1. User moves slider
new_gain = -3.0  # dB

# 2. Send to device
await client.request('setup_set_value', {
  'path': '/audio/output/speaker/1/gain',
  'value': new_gain
})

# 3. Confirmation (success)
print('Gain updated to', new_gain, 'dB')

# 4. Other clients receive notification
# (if subscribed to /audio/output/speaker/1)
def on_change(params):
    if params['path'] == '/audio/output/speaker/1/gain':
        update_slider(params['value'])

await client.subscribe('setup_subscribe',
                       {'path': '/audio/output/speaker/1'},
                       on_change)
```

### Workflow 2: Backup Configuration

```python
import base64
import json

# 1. Create backup
backup = await client.request('backup_create', {})
# Returns: {'config': '<base64-string>', 'timestamp': '...'}

# 2. Decode base64 to binary and save to file
config_binary = base64.b64decode(backup['config'])
with open(f"px-{backup['timestamp']}.bin", 'wb') as f:
    f.write(config_binary)

print('Backup saved:', backup['timestamp'])
```

### Workflow 3: Restore Configuration

```python
import base64

# 1. Load backup file
with open('px-backup.bin', 'rb') as f:
    config_binary = f.read()

# 2. Encode binary to base64
config_base64 = base64.b64encode(config_binary).decode('ascii')

# 3. Restore to device
result = await client.request('backup_restore', {
  'config': config_base64,
  'preserve_network_settings': True  # Don't overwrite network config
})

print('Restored', len(result['restored_paths']), 'paths')
```

### Workflow 4: Clone Configuration to Multiple Devices

```python
from py_client import PxClient

# 1. Backup from source device
async with PxClient(host='192.168.1.100', port=80) as source:
    backup = await source.request('backup_create', {})

# 2. Restore to target devices
device_ips = ['192.168.1.101', '192.168.1.102', '192.168.1.103']

for ip in device_ips:
    async with PxClient(host=ip, port=80) as target:
        await target.request('backup_restore', {
            'config': backup['config'],
            'preserve_network_settings': True  # Keep unique IPs
        })
        print(f'Cloned to {ip}')
```

### Workflow 5: Bulk Parameter Update

```python
# Update multiple related parameters atomically
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {
        'gain': -3.0,
        'polarity': 1,  # 1 = normal, -1 = inverted
        'delay': 0.0,
        'mute': False,
        'hpf': 'off',
        'hpf_freq': 20.0,
        'generator_mix': 'off'
    }
})

# Alternative: Multiple individual updates (less efficient)
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user',
  'value': {'gain': -3.0}
})
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user',
  'value': {'polarity': 1}  # 1 = normal, -1 = inverted
})
# ... etc
```

### Workflow 6: Real-Time UI Sync

```python
from py_client import PxClient

class DeviceConfigUI:
    def __init__(self):
        self.client = None
        self.subscriptions = {}
    
    async def connect(self, host: str, port: int = 80):
        self.client = PxClient(host=host, port=port)
        await self.client.connect()
        
        # Subscribe to all config changes
        def on_change(params):
            self.handle_config_change(params)
        
        sub_id = await self.client.subscribe('setup_subscribe', {}, on_change)
        self.subscriptions['all'] = sub_id
    
    def handle_config_change(self, params: dict):
        # Update UI based on path
        path = params['path']
        value = params['value']
        
        if '/gain' in path:
            self.update_gain_slider(path, value)
        elif '/mute' in path:
            self.update_mute_button(path, value)
        elif '/eq/bands' in path:
            self.update_eq_display(path, value)
    
    async def disconnect(self):
        # Unsubscribe all
        for sub_id in self.subscriptions.values():
            await self.client.unsubscribe('setup_unsubscribe', sub_id)
        
        await self.client.disconnect()
```

---

*PX Control API v1.0.0 - © 2025 Pascal Audio*
