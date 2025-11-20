# API Reference

**PX Control API v1.0.0 (API Level 1)**

Complete reference for all JSON-RPC methods organized by domain. All examples use Python with the `py_client` library.

For protocol details (connection, JSON-RPC format, error codes), see [README.md](README.md).

---

## Quick Method Index

| Domain | Method | Description |
|--------|--------|-------------|
| **API** | `api_ping` | Health check |
| | `api_version` | Get API/firmware version |
| | `api_check_version` | Check client version compatibility |
| **Device** | `device_reboot` | Reboot device |
| | `device_reset` | Factory reset |
| | `device_power_on` | Power amplifier on |
| | `device_power_off` | Power amplifier off |
| | `device_find_me` | Visual/audio identification |
| | `device_get_time` | Get system time |
| | `device_set_time` | Set system time |
| | `logs_get` | Retrieve device logs |
| | `logs_set_level` | Set log filter level |
| | `diagnostics_get` | Get diagnostic information |
| **Setup** | `setup_get` | Get object at path |
| | `setup_get_value` | Get single value at path |
| | `setup_get_all` | Get entire configuration |
| | `setup_set` | Set object at path |
| | `setup_set_value` | Set single value at path |
| | `setup_subscribe` | Subscribe to config changes |
| | `setup_unsubscribe` | Unsubscribe from changes |
| | `backup_create` | Create configuration backup |
| | `backup_restore` | Restore configuration |
| **Preset** | `preset_apply` | Apply preset to channel |
| | `preset_clear` | Clear channel preset |
| | `preset_create` | Create preset from channel |
| | `preset_show` | Show current preset |
| **Status** | `status_get_all` | Get all device status ⚠️ WIP |
| | `status_get` | Get status at path ⚠️ WIP |
| | `status_subscribe` | Subscribe to status ⚠️ WIP |
| | `status_unsubscribe` | Unsubscribe from status ⚠️ WIP |
| **Metrics** | `metrics_subscribe` | Subscribe to real-time metrics |
| | `metrics_unsubscribe` | Unsubscribe from metrics |

---

## API Domain

### `api_ping`

Health check endpoint - verify device is responsive.

**Parameters:** None

**Returns:** `"pong"` (string)

**Example:**

```python
response = await client.request('api_ping')
print(response)  # "pong"
```

**Use Cases:**
- Initial connection verification
- Periodic health checks
- Connection monitoring

---

### `api_version`

Get API and firmware version information.

**Parameters:** None

**Returns:**

```typescript
{
  api_version: string,       // API semantic version (e.g., "1.0.0")
  api_level: number,         // API level (increments with breaking changes)
  firmware_version: string   // Firmware version (e.g., "1.2.3")
}
```

**Example:**

```python
version = await client.request('api_version')
print(f"API: {version['api_version']} Level: {version['api_level']}")
print(f"Firmware: {version['firmware_version']}")

# Check compatibility
if version['api_level'] >= 1:
    # Use v1.x features
    pass
```

**Version Fields:**
- `api_version`: Semantic version of JSON-RPC API (MAJOR.MINOR.PATCH)
- `api_level`: Integer for quick compatibility checks (same level = compatible)
- `firmware_version`: Main firmware version

**Use Cases:**
- Feature detection
- Compatibility checks
- Display version to users
- Support diagnostics

---

### `api_check_version`

Check client version compatibility with server API.

**Parameters:**

```typescript
{
  client_version: string       # Client version string (e.g., "1.0.0")
}
```

**Returns:**

```typescript
{
  compatible: boolean        // Is client compatible with server?
  server_version: string     // Server API version
  client_version: string     // Echo of client version
  warnings: list[string]     // Optional compatibility warnings
}
```

**Example:**

```python
compat = await client.request('api_check_version', {
    'client_version': '1.0.0'
})

if not compat['compatible']:
    print('Incompatible API version!')
    print(f"Client: {compat['client_version']}")
    print(f"Server: {compat['server_version']}")
else:
    print('API compatible')
    if compat.get('warnings'):
        for w in compat['warnings']:
            print(f'Warning: {w}')
```

**Compatibility Rules:**
- Same MAJOR version: fully compatible
- N-1 MAJOR version: compatible with warnings (supports previous major version)
- Older/newer MAJOR versions: incompatible

**Use Cases:**
- Client initialization checks
- Version negotiation
- Graceful degradation
- User warnings about outdated clients

---

## Device Domain

### `device_reboot`

Reboot the device (warm restart).

**Parameters:**

```typescript
{
  delay?: number  // Optional delay in seconds (default: 5)
}
```

**Returns:**

```typescript
{
  success: boolean
  message: string
  reboot_time: number  // Seconds until reboot
}
```

**Example:**

```python
# Reboot immediately
await client.request('device_reboot')

# Reboot with 30 second delay
await client.request('device_reboot', {'delay': 30})
```

**Timeline:**
1. Client sends reboot request
2. Device responds with success
3. Device waits `delay` seconds
4. Device reboots (WebSocket connection drops)
5. Device comes back online (~30-60 seconds)

**Use Cases:**
- Apply critical firmware updates
- Recover from error states
- Scheduled maintenance
- Remote recovery

**Error Codes:**
- `PERMISSION_DENIED`: System command failed

---

### `device_reset`

Factory reset device to default configuration.

**Parameters:**

```typescript
{
  preserve_network?: boolean  // Keep network settings (default: false)
}
```

**Returns:**

```typescript
{
  success: boolean
  message: string
}
```

**Example:**

```python
# Full factory reset
await client.request('device_reset')

# Reset but keep network config
await client.request('device_reset', {'preserve_network': True})
```

**Warning:** This operation:
- Erases all user configuration
- Resets all audio processing to defaults
- Clears all channel presets
- Optionally preserves network settings
- Device reboots automatically

**Use Cases:**
- Return device to factory state
- Clear problematic configuration
- Prepare device for new installation
- Testing with clean slate

**Error Codes:**
- `PERMISSION_DENIED`: System command failed
- `DEVICE_BUSY`: Reset operation in progress

---

### `device_power_on`

Power on the amplifier outputs.

**Parameters:** None

**Returns:**

```typescript
{
  success: boolean
  message: string
}
```

**Example:**

```typescript
await device.request('device_power_on', {});
console.log('Amplifier powered on');
```

**Timeline:**
1. Client sends power_on
2. Device responds immediately
3. Power rails sequence on (~2-5 seconds)
4. DSP initializes
5. Amplifier outputs active

**Use Cases:**
- Remote power control
- Scheduled power on/off
- Automation systems
- Integration with room control

**Error Codes:**
- `HARDWARE_ERROR`: Power sequencing failed
- `DEVICE_BUSY`: Power operation in progress

---

### `device_power_off`

Power off the amplifier outputs (standby mode).

**Parameters:** None

**Returns:**

```typescript
{
  success: boolean
  message: string
}
```

**Example:**

```python
await client.request('device_power_off')
print('Amplifier in standby')
```

**Note:** This is a standby mode - device remains network-connected and API-accessible. Only amplifier outputs are disabled.

**Timeline:**
1. Client sends power_off
2. Device mutes outputs
3. Power rails sequence off (~1-2 seconds)
4. Device remains network-active

**Use Cases:**
- Energy saving
- Scheduled off hours
- Automation systems
- Emergency mute

**Error Codes:**
- `HARDWARE_ERROR`: Power sequencing failed
- `DEVICE_BUSY`: Power operation in progress

---

### `device_find_me`

Make device identify itself visually or audibly.

**Parameters:**

```typescript
{
  timeout?: number  // Identification duration in seconds (default: 60)
}
```

**Returns:**

```typescript
{
  status: "identifying"
  timeout: number
}
```

**Example:**

```python
# Identify for 60 seconds (default)
await client.request('device_find_me')

# Identify for 2 minutes
await client.request('device_find_me', {'timeout': 120})
```

**Device Behavior:**
- LEDs flash in pattern
- Optional audible tone (configurable)
- Automatic timeout

**Use Cases:**
- Locate device in rack
- Verify physical device during installation
- Multi-device identification
- Network device mapping

---

### `device_get_time`

Get current system time in UTC (RFC 3339 format).

**Parameters:** None

**Returns:**

```typescript
{
  time: string  // RFC 3339 UTC timestamp
}
```

**Example:**

```python
from datetime import datetime, timezone

result = await client.request('device_get_time')
print(f"Device time: {result['time']}")
# Output: "2025-11-17T14:30:00+00:00"

device_time = datetime.fromisoformat(result['time'])
local_time = datetime.now(timezone.utc)
drift = abs((device_time - local_time).total_seconds())
print(f"Clock drift: {drift} seconds")
```

**Use Cases:**
- Time synchronization checks
- Event timestamp correlation
- Clock drift monitoring
- Logging diagnostics

---

### `device_set_time`

Set system time (UTC RFC 3339 format).

**Parameters:**

```typescript
{
  time: string  // ISO 8601 UTC timestamp
}
```

**Returns:**

```typescript
{
  success: boolean
  message: string
}
```

**Example:**

```python
from datetime import datetime, timezone

# Set to current time (RFC 3339 format)
now = datetime.now(timezone.utc).isoformat().replace('+00:00', '+00:00')
await client.request('device_set_time', {'time': now})

# Set specific time
await client.request('device_set_time', {
    'time': '2025-11-17T14:30:00+00:00'
})
```

**Note:** 
- Time must be in RFC 3339 format (e.g., "2025-11-17T14:30:00+00:00")
- System time persists across reboots (written to RTC)
- Prefer NTP synchronization for production use

**Use Cases:**
- Initial time setup
- Manual time correction
- Testing with specific times
- Offline installations

**Error Codes:**
- `INVALID_VALUE`: Invalid RFC 3339 timestamp format
- `PERMISSION_DENIED`: Failed to execute system commands
- `HARDWARE_ERROR`: Failed to persist time to RTC

---

### `logs_get`

Retrieve device logs with pagination.

**Parameters:**

```typescript
{
  limit?: number   // Max entries to return (default: 100)
  offset?: number  // Skip first N entries (default: 0)
}
```

**Returns:** Object containing array of log entries (newest first)

```typescript
{
  logs: Array<{
    timestamp: string  // RFC 3339 timestamp
    level: string      // "error", "warn", "info", "debug", "trace"
    target: string     // Module path (e.g., "thrust::device")
    message: string    // Log message
  }>
}
```

**Example:**

```python
# Get latest 100 logs
result = await client.request('logs_get')
for log in result['logs']:
    print(f"[{log['timestamp']}] {log['level']}: {log['message']}")

# Pagination: get next 100 logs
more_result = await client.request('logs_get', {
    'limit': 100,
    'offset': 100
})
for log in more_result['logs']:
    print(log['message'])

# Get only recent errors
recent_result = await client.request('logs_get', {'limit': 20})
errors = [log for log in recent_result['logs'] if log['level'] == 'error']
```

**Use Cases:**
- Debugging issues
- Remote diagnostics
- Error monitoring
- Support investigations

**Error Codes:**
- `DEVICE_BUSY`: Log controller unavailable

---

### `logs_set_level`

Set logging filter level dynamically.

**Parameters:**

```typescript
{
  filter: string  // Log filter string (e.g., "TRACE", "DEBUG", "INFO", "WARN", "ERROR")
}
```

**Returns:**

```typescript
{
  success: boolean
  message: string
}
```

**Example:**

```python
# Set global level to debug
result = await client.request('logs_set_level', {'filter': 'INFO'})
print(f"Success with 'levels': {result}")
```

**Filter Syntax:**
- Global level: `"info"`, `"debug"`, `"trace"`
- Module-specific: `"module::path=level"`
- Combined: `"global,module1=level1,module2=level2"`

**Log Levels:**
- `error`: Errors only
- `warn`: Warnings and errors
- `info`: Informational messages (default)
- `debug`: Debug output
- `trace`: Verbose tracing

**Use Cases:**
- Enable verbose logging for debugging
- Reduce log noise in production
- Focus on specific subsystems
- Remote diagnostics

**Error Codes:**
- `INVALID_VALUE`: Invalid filter syntax
- `DEVICE_BUSY`: Log controller unavailable

---

## Setup Domain

The Setup domain provides access to the persistent device configuration tree. All setup changes:
- Persist automatically to storage (5-second debounced write)
- Trigger `setup_update` notifications to subscribers
- Are validated before application according to JSON schemas (see `build/schemas/` directory)

**Path Reference:** See **[02-configuration-guide.md](02-configuration-guide.md)** for complete setup path documentation and examples.

### `setup_get`

Get configuration node (object or array) at JSON path.

**Parameters:**

```typescript
{
  path: string  // JSON path (e.g., "/audio/output/speaker/1")
}
```

**Returns:** Configuration node directly (object or array, no wrapper)

**Example:**

```python
 # Get speaker 1 config
speaker = await client.request('setup_get', {
    'path': '/audio/output/speaker/1'
})
print(f"Speaker 1 name: {speaker['name']}")
print(f"Primary source: {speaker['primary_src']}")
print(f"Fallback source: {speaker['fallback_src']}")

# Get EQ object
eq = await client.request('setup_get', {
    'path': '/audio/output/speaker/1/user/eq'
})
print(f"EQ bypass: {eq['bypass']}")

# Get EQ band
band = await client.request('setup_get', {
    'path': '/audio/output/speaker/1/user/eq/bands/1'
})
print(f"Band 1: {band}")
```

**Use Cases:**
- Read complex nested objects
- Get multiple related parameters
- Bulk parameter retrieval

**Error Codes:**
- `INVALID_PATH`: Path does not exist in configuration tree

---

### `setup_get_value`

Get single property value from a configuration path.

**Parameters:**

```typescript
{
  path: string  // JSON path to specific value - comprises a known path to an node + a property name
}
```

**Returns:** Property value directly (no metadata)

**Example:**

```python
    # Get speaker name
    name = await client.request('setup_get_value', {
        'path': '/audio/output/speaker/1/name'
    })
    print(f'Speaker name: {name}')

    # Get speaker use-gain
    gain = await client.request('setup_get_value', {
        'path': '/audio/output/speaker/1/user/gain',
    })
    print(f'Speaker gain: {gain}')
```

**Difference from `setup_get`:**
- `setup_get`: Returns entire node (object/array)
- `setup_get_value`: Returns single property value from within a node

**Use Cases:**
- Read single scalar values
- Get parameter constraints (range)
- Simple parameter queries

**Error Codes:**
- `INVALID_PATH`: Path does not exist

---

### `setup_get_all`

Get entire device configuration tree.

**Parameters:**

```typescript
{
  flatten?: boolean  // Return flattened path map (default: false)
}
```

**Returns:** 
- **Hierarchical mode** (`flatten: false`): Full nested DeviceSetup object
- **Flattened mode** (`flatten: true`): Map of paths → leaf objects containing primitives

**Example (hierarchical):**

```python
# Get full config tree
config = await client.request('setup_get_all')
print(f"Speaker 1 gain: {config['audio']['output']['speaker']['1']['user']['gain']} dB")
print(f"Network mode: {config['network']['mode']}")
```

**Example (flattened):**

```python
# Get as flat path map (each path → object with primitive values)
flat = await client.request('setup_get_all', {'flatten': True})

# Access leaf objects at each path
user = flat['/audio/output/speaker/1/user']
print(f"Speaker 1 gain: {user['gain']} dB")
print(f"Speaker 1 polarity: {user['polarity']}")

network = flat['/network']
print(f"Network mode: {network['mode']}")

# Iterate all paths
for path, leaf_obj in flat.items():
    if isinstance(leaf_obj, dict):
        print(f"{path}: {list(leaf_obj.keys())}")
```

**Use Cases:**
- Configuration backup
- Initial cache population
- Bulk parameter reading
- Configuration comparison

**Flattened Structure Explained:**

Flattened mode creates a single-level map where:
- **Keys** are JSON paths (e.g., `/audio/output/speaker/1/user`)
- **Values** are leaf objects containing only primitive fields at that path

Example structure:
```json
{
  "/audio/output/speaker/1/user": { "gain": -3.0, "polarity": 1, "mute": false, ... },
  "/network": { "mode": "static", "hostname": "px-device", ... }
}
```

This allows O(1) path lookups while keeping related primitives grouped together.

**Error Codes:**
- `HARDWARE_ERROR`: Failed to serialize configuration

**Performance Note:** Flattened mode is faster for path lookups but loses hierarchical structure.

---

### `setup_set`

Set configuration node (object or array) at JSON path.

**Parameters:**

```typescript
{
  path: string  // JSON path
  value: any    // Object to set (preserves structure)
}
```

**Returns:** The updated node value (echoes back what was set)

**Example:**

```python
# Set EQ band parameters (object)
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user/eq/bands/3',
    'value': {
        'kind': 'parametric',
        'frequency': 1000,
        'gain': 3.0,
        'q': 1.4
    }
})

# Set multiple speaker parameters
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {
        'gain': -3.0,
        'mute': False,
        'polarity': 1
    }
})
```

**Notes:**
- Triggers `setup_update` notification for the set path
- Auto-saves to storage (5-second debounce)
- Validates entire object before applying
- Partial objects merge with existing config

**Use Cases:**
- Set multiple related parameters atomically
- Apply complex nested objects
- Structured parameter updates

**Error Codes:**
- `INVALID_PATH`: Path does not exist
- `INVALID_CHANNEL`: Channel out of range (1-4)
- `INVALID_VALUE`: Validation failed (range, type, enum)
- `DEVICE_BUSY`: Service unavailable
- `HARDWARE_ERROR`: Failed to apply to hardware

---

### `setup_set_value`

Set single property value within a configuration node.

**Parameters:**

```typescript
{
  path: string  // JSON path to specific parameter
  value: any    // New value (string, number, boolean)
}
```

**Returns:** Success confirmation

**Example:**

```python
# Set gain property
await client.request('setup_set_value', {
    'path': '/audio/output/speaker/1/user/gain',
    'value': -3.0
})

# Set mute property
await client.request('setup_set_value', {
    'path': '/audio/output/speaker/1/user/mute',
    'value': True
})

# Set device name property
await client.request('setup_set_value', {
    'path': '/install/venue_name',
    'value': 'Studio Main L'
})
```

**Difference from `setup_set`:**
- `setup_set`: Sets entire node (object/array with all fields)
- `setup_set_value`: Sets single property within a node

**Use Cases:**
- Simple parameter updates
- UI sliders/toggles
- Single value changes

**Error Codes:**
- `INVALID_PATH`: Path does not exist
- `INVALID_VALUE`: Value validation failed
- `DEVICE_BUSY`: Service unavailable
- `HARDWARE_ERROR`: Failed to apply to hardware

---

### `setup_subscribe`

Subscribe to configuration change notifications.

**Parameters:**

```typescript
{
  path?: string  // JSON path to watch (omit for all changes)
}
```

**Returns:**

```typescript
{
  subscription_id: string  // UUID for unsubscribing
}
```

**Server Notifications:**

When subscribed config changes, server sends:

```typescript
{
  jsonrpc: "2.0",
  method: "setup_update",  // Notification method
  params: {
    path: string,           // Path that changed
    value: any,             // New value
  }
  // NO 'id' field (notifications don't have request IDs)
}
```

**Example:**

```python
# Subscribe to all speaker 1 changes
def on_setup_change(params):
    print(f"Config changed: {params['path']}")
    print(f"New value: {params['value']}")
    # Update UI here

sub_id = await client.subscribe(
    'setup_subscribe',
    {'path': '/audio/output/speaker/1'},
    on_setup_change
)

# Subscribe to specific EQ band
eq_sub_id = await client.subscribe(
    'setup_subscribe',
    {'path': '/audio/output/speaker/1/user/eq/bands/3'},
    on_setup_change
)

# Subscribe to ALL changes (no path filter)
all_sub_id = await client.subscribe('setup_subscribe', {}, on_setup_change)
```

**Path Matching:**
- Subscribes to exact path and all children
- `/audio` matches all audio changes
- `/audio/output/speaker/1` matches all speaker 1 changes
- `/audio/output/speaker/1/gain` matches only gain changes

**Use Cases:**
- Real-time UI updates
- Multi-client synchronization
- Change logging
- Undo/redo implementation

---

### `setup_unsubscribe`

Unsubscribe from configuration change notifications.

**Parameters:**

```typescript
{
  subscription_id: string  // UUID from setup_subscribe
}
```

**Returns:** `null`

**Example:**

```python
# Subscribe
sub_id = await client.subscribe(
    'setup_subscribe',
    {'path': '/audio/output/speaker/1'},
    lambda p: print(f"Changed: {p['path']}")
)

# Later: unsubscribe
await client.unsubscribe('setup_unsubscribe', sub_id)
```

**Best Practice:** Always unsubscribe when closing UI panels or disconnecting to avoid memory leaks.

---

### `backup_create`

Create full configuration backup.

**Parameters:** None

**Returns:**

```typescript
{
  config: object    // Full DeviceSetup object
  timestamp: string // RFC 3339 backup creation time
  version: number   // Setup version number
}
```

**Example:**

```python
import json
from datetime import datetime

# Create backup
backup = await client.request('backup_create')

# Save to file
with open(f"backup-{int(datetime.now().timestamp())}.json", 'w') as f:
    json.dump(backup, f, indent=2)
```

**Use Cases:**
- Configuration backup before changes
- Device migration
- Configuration versioning
- Disaster recovery

---

### `backup_restore`

Restore configuration from backup.

**Parameters:**

```typescript
{
  config: object                   // DeviceSetup object from backup_create
  preserve_network_settings?: boolean  // Keep current network config (default: false)
}
```

**Returns:**

```typescript
{
  success: boolean
  restored_paths: string[]  // List of paths that were restored
  message: string
}
```

**Example:**

```python
import json

# Load backup from file
with open('backup.json', 'r') as f:
    backup = json.load(f)

# Restore (will change network settings)
await client.request('backup_restore', {
    'config': backup['config']
})

# Restore but keep current network settings
await client.request('backup_restore', {
    'config': backup['config'],
    'preserve_network_settings': True
})
```

**Notes:**
- Triggers multiple `setup_update` notifications
- Validates entire config before applying
- Can preserve network settings to avoid losing connection

**Use Cases:**
- Restore from backup
- Clone configuration to multiple devices
- Revert to known-good state
- Factory reset with custom defaults

**Error Codes:**
- `INVALID_VALUE`: Invalid config structure
- `DEVICE_BUSY`: Restore in progress
- `HARDWARE_ERROR`: Failed to apply config

---

## Preset Domain

### `preset_apply`

Apply a channel preset to a speaker.

**Parameters:**

```typescript
{
  channel: number              // Speaker channel (1-4)
  preset: object | string      // ChannelPreset object or base64-encoded binary
}
```

**Returns:**

```typescript
{
  success: boolean
  message: string
  preset_name: string          // Name of applied preset
}
```

**Example (JSON preset):**

```python
import json

# Load preset from file
with open('studio-monitor.json', 'r') as f:
    preset = json.load(f)

# Apply to channel 1
await client.request('preset_apply', {
    'channel': 1,
    'preset': preset
})
```

**Example (binary encrypted preset):**

```python
import base64

# Load binary preset (base64-encoded)
with open('vendor-preset.px-preset', 'rb') as f:
    preset_binary = base64.b64encode(f.read()).decode('utf-8')

# Apply encrypted preset
await client.request('preset_apply', {
    'channel': 1,
    'preset': preset_binary
})
```

**Notes:**
- Applies to preset processing layer only (not user/array layers)
- Triggers multiple `setup_update` notifications
- Locked presets encrypt sensitive parameters (crossover, limiters)
- User and array layers remain unchanged

**Use Cases:**
- Apply factory presets
- Load installer tunings
- A/B comparison testing
- Preset distribution

**Error Codes:**
- `INVALID_CHANNEL`: Channel out of range (1-4)
- `PRESET_INVALID`: Malformed preset data
- `PRESET_LOCKED`: Cannot decrypt encrypted preset
- `DEVICE_BUSY`: Service unavailable
- `HARDWARE_ERROR`: Failed to apply preset

---

### `preset_clear`

Clear channel preset and restore factory defaults for preset layer.

**Parameters:**

```typescript
{
  channel: number  // Speaker channel (1-4)
}
```

**Returns:**

```typescript
{
  success: boolean
  message: string
}
```

**Example:**

```python
# Clear preset from channel 1
await client.request('preset_clear', {'channel': 1})
```

**Notes:**
- Resets preset processing layer to factory defaults
- Does NOT affect user or array layers
- Removes any preset locking
- Triggers `setup_update` notifications

**Use Cases:**
- Remove applied preset
- Return to flat frequency response
- Clear vendor-locked settings
- Start fresh tuning

**Error Codes:**
- `INVALID_CHANNEL`: Channel out of range (1-4)
- `DEVICE_BUSY`: Service unavailable
- `HARDWARE_ERROR`: Failed to clear preset

---

### `preset_create`

Create a preset from current channel configuration.

**Parameters:**

```typescript
{
  channel: number          // Speaker channel (1-4)
  name: string             // Preset name
  version: string          // Preset version (e.g., "1.0")
  created_date: string     // ISO 8601 date
  vendor_lock?: boolean    // Encrypt preset (default: false)
}
```

**Returns:** ChannelPreset object (JSON) or base64-encoded binary (if vendor_lock=true)

**Example (JSON preset):**

```python
import json
from datetime import datetime

# Create unencrypted JSON preset
preset = await client.request('preset_create', {
    'channel': 1,
    'name': 'Studio Monitor',
    'version': '1.0',
    'created_date': datetime.now().isoformat(),
    'vendor_lock': False
})

# Save to file
with open('studio-monitor.json', 'w') as f:
    json.dump(preset, f, indent=2)
```

**Example (encrypted binary preset):**

```python
import base64

# Create vendor-locked encrypted preset
encrypted = await client.request('preset_create', {
    'channel': 1,
    'name': 'Vendor Tuning',
    'version': '2.1',
    'created_date': '2025-11-17T10:00:00Z',
    'vendor_lock': True
})

# Save binary preset
with open('vendor-preset.px-preset', 'wb') as f:
    f.write(base64.b64decode(encrypted))
```

**Notes:**
- Captures preset processing layer only (not user/array)
- Vendor-locked presets hide sensitive DSP parameters
- Locked fields return `null` when queried after application
- Binary format uses proprietary encryption + compression (device-specific, not intended for external parsing)

**Use Cases:**
- Save factory tunings
- Create installer presets
- Protect intellectual property
- Distribute commercial presets

**Error Codes:**
- `INVALID_CHANNEL`: Channel out of range (1-4)
- `DEVICE_BUSY`: Service unavailable

---

### `preset_show`

Show current preset configuration for channel.

**Parameters:**

```typescript
{
  channel: number  // Speaker channel (1-4)
}
```

**Returns:** Current ChannelPreset object or `null` if no preset applied

```typescript
{
  name: string
  version: string
  created_date: string
  preset: {
    drive_mode: string
    gain: number
    polarity: string
    delay: number
    crossover: object | null    // null if locked
    eq: object                  // May have locked bands
    fir: object | null          // null if locked
    limiters: object | null     // null if locked
  }
} | null
```

**Example:**

```python
# Get current preset
preset = await client.request('preset_show', {'channel': 1})

if preset is None:
    print('No preset applied')
else:
    print(f"Preset: {preset['name']} {preset['version']}")
    crossover = preset['prese']['crossover'] or 'LOCKED'
    print(f"Crossover: {crossover}")
    print(f"Gain: {preset['preset']['gain']} dB")
```

**Notes:**
- Returns `null` for locked fields in vendor-locked presets
- Unlocked fields show actual values
- Does not include user or array layer settings

**Use Cases:**
- Display current preset info
- Check preset lock status
- Preset comparison
- Debugging

**Error Codes:**
- `INVALID_CHANNEL`: Channel out of range (1-4)

---

## Status Domain ⚠️ Work in Progress

**Warning:** The Status API structure may change in v1.x releases. Existing fields may be renamed, moved, or have their types changed. Use with caution in production code.

**Note:** Status uses read-only runtime values (not configuration). Status paths mirror the structure returned by `status_get_all` (e.g., `/state`, `/info`, `/network`, `/audio`, `/firmware`).

### `status_get_all`

Get complete device status snapshot.

**Parameters:** None

**Returns:**

```typescript
{
  state: {
    power_state: "on" | "standby" | "off"
    find_me: {
      active: boolean
      timeout_remaining: number | null
    }
    uptime_seconds: number
    boot_time: string
    reboot_pending: {
      pending: boolean
      reason: string | null
      delay_seconds: number | null
    }
  }
  info: {
    device_name: string
    serial_number: string
    model_name: string
    // Additional device info fields
  }
  network: {
    lan1: NetworkInterfaceStatus
    lan2: NetworkInterfaceStatus
    dante: DanteStatus | null
  }
  audio: {
    sample_rate: number
    sync_source: "internal" | "dante" | "wordclock"
  }
  firmware: {
    main: string
    dsp: string
    front_mcu: string
    system_mcu: string
    bootloader: string
  }
}
```

**Example:**

```python
status = await client.request('status_get_all', {})
print(f"Power: {status['state']['power_state']}")
print(f"Uptime: {status['state']['uptime_seconds']} seconds")
print(f"Model: {status['info']['model_name']}")
print(f"Serial: {status['info']['serial']}")
print(f"Sample rate: {status['audio']['sample_rate']} Hz")
```

**Use Cases:**
- Initial status load
- Dashboard displays
- Health monitoring
- Diagnostics

---

### `status_get`

Get status at specific path.

**Parameters:**

```typescript
{
  path: string  // Status path: "/state", "/info", "/network", "/audio", "/firmware"
}
```

**Returns:** Status object for requested path

**Example:**

```python
# Get device state
device_state = await client.request('status_get', {
    'path': '/state'
})
print(f"Power: {device_state['power_state']}")

# Get device info
info = await client.request('status_get', {
    'path': '/info'
})
print(f"Serial: {info['serial']}")

# Get network status
network = await client.request('status_get', {
    'path': '/network'
})
print(f"LAN1 IP: {network['lan1']['address']}")
```

---

### `status_subscribe`

Subscribe to status change notifications.

**Parameters:**

```typescript
{
  path: string  // Array of status paths to watch
}
```

**Returns:**

```typescript
{
  subscription_id: string
}
```

**Server Notifications:**

```typescript
{
  jsonrpc: "2.0",
  method: "status_update",
  params: {
    path: string
    value: any
  }
}
```

**Example:**

```python
# Subscribe to device status
def on_status_change(params):
    print(f"Status changed: {params['path']}")

sub_id = await client.subscribe(
    'status_subscribe',
    {'paths': ['/state', '/network']},
    on_status_change
)
```

---

## Metrics Domain

### `metrics_subscribe`

Subscribe to real-time audio metrics (VU meters, gain reduction, clip detection).

**Parameters:**

```typescript
{
  path?: string  // Metrics path filter (omit for all metrics)
  freq?: number  // Update frequency in Hz (default: 10)
}
```

**Returns:**

```typescript
{
  subscription_id: string
}
```

**Server Notifications:**

The server sends three types of metric notifications:

**1. VU Meters** (`/metrics/vu`):

```typescript
{
  jsonrpc: "2.0",
  method: "metrics_update",
  params: {
    path: "/metrics/vu",
    value: {
      analog_input_vu: Array<{live: number, peak: number}>,      // 4 channels, dBFS
      digital_input_vu: Array<{live: number, peak: number}>,     // 4 channels, dBFS
      digital_output_vu: Array<{live: number, peak: number}>,    // Variable length
      network_input_vu: Array<{live: number, peak: number}>,     // Variable length
      network_output_vu: Array<{live: number, peak: number}>,    // Variable length
      speaker_output_vu: Array<{live: number, peak: number}>     // 4 channels, dBFS
    }
  }
}
```

**2. Gain Reduction** (`/metrics/gain_reduction`):

```typescript
{
  jsonrpc: "2.0",
  method: "metrics_update",
  params: {
    path: "/metrics/gain_reduction",
    value: {
      current: Array<{live: number, peak: number}>,      // Current limiter (0.0-1.0)
      peak_gain: Array<{live: number, peak: number}>,    // Peak limiter (0.0-1.0)
      rms_gain: Array<{live: number, peak: number}>,     // RMS limiter (0.0-1.0)
      total: Array<{live: number, peak: number}>         // Combined (0.0-1.0)
    }
  }
}
```

**3. Clip Detection** (`/metrics/clip`):

```typescript
{
  jsonrpc: "2.0",
  method: "metrics_update",
  params: {
    path: "/metrics/clip",
    value: {
      analog_input_clip: Array<boolean>,      // 4 channels
      digital_output_clip: Array<boolean>,    // Variable length
      network_output_clip: Array<boolean>,    // Variable length
      speaker_output_clip: Array<boolean>     // 4 channels
    }
  }
}
```

**Example:**

```python
# Subscribe to all metrics at 20 Hz
def on_metrics(params):
    path = params['path']
    value = params['value']
    
    if path == '/metrics/vu':
        # Update VU meters
        for i, vu in enumerate(value['speaker_output_vu']):
            update_vu_meter(i + 1, vu['live'], vu['peak'])
    
    elif path == '/metrics/gain_reduction':
        # Update gain reduction meters
        for i, gr in enumerate(value['total']):
            update_gr_meter(i + 1, gr['live'])
    
    elif path == '/metrics/clip':
        # Update clip indicators
        for i, clipped in enumerate(value['speaker_output_clip']):
            if clipped:
                show_clip_indicator(i + 1)

sub_id = await client.subscribe(
    'metrics_subscribe',
    {'freq': 20},
    on_metrics
)

# Subscribe to specific metric path only
vu_sub_id = await client.subscribe(
    'metrics_subscribe',
    {'path': '/metrics/vu', 'freq': 30},
    on_metrics
)
```

**Notes:**
- All VU values are in dBFS (negative values, -144.0 = silence)
- Gain reduction values are normalized 0.0-1.0 (1.0 = full limiting)
- Peak values hold for decay time before resetting
- Empty arrays indicate unavailable channels (e.g., no Dante network)

**Use Cases:**
- VU meter displays
- Clip indicators
- Limiter gain reduction meters
- Level monitoring
- Audio presence detection

---

### `metrics_unsubscribe`

Unsubscribe from metrics updates.

**Parameters:**

```typescript
{
  subscription_id: string
}
```

**Returns:** `null`

**Example:**

```python
# Subscribe
sub_id = await client.subscribe(
    'metrics_subscribe',
    {'freq': 10},
    lambda p: print(p['metrics'])
)

# Later: unsubscribe
await client.unsubscribe('metrics_unsubscribe', sub_id)
```

---

## Diagnostics Domain

### `diagnostics_get`

Get diagnostic information for troubleshooting.

**Parameters:**

```typescript
{
  namespace?: string  // Diagnostic namespace filter (default: all)
}
```

**Returns:** Object with diagnostic data (structure varies by implementation)

**Example:**

```python
# Get all diagnostics
diag = await client.request('diagnostics_get')
print('Diagnostics:', diag)

# Get specific namespace
dsp = await client.request('diagnostics_get', {
    'namespace': 'dsp'
})
```

**Notes:**
- Available namespaces are dynamically generated and device-specific
- Diagnostic structure and content may vary between firmware versions
- Intended for support and debugging, not production monitoring

> ⚠️ **UNSTABLE API**
> 
> The namespaces, keys, and values returned by `diagnostics_get` are **NOT STABLE**
> and may change at any time without notice. This method is intended for **troubleshooting
> and support purposes only**, not for programmatic access or production monitoring.
> 
> Do not build application logic that depends on specific diagnostic fields.
> Use the Status API (`status_get_all`) for production monitoring instead.

**Use Cases:**
- Support diagnostics
- Hardware troubleshooting
- Performance analysis
- Error investigation

---

## Error Reference

All error responses follow this structure:

```typescript
{
  jsonrpc: "2.0",
  error: {
    code: number,        // JSON-RPC error code (-32xxx)
    message: string,     // Generic error message
    data: {
      code: string,      // PX error code (see table below)
      message: string,   // Detailed error description
      [key: string]: any // Additional context fields
    }
  },
  id: number | string
}
```

### Error Code Table

**Application-Specific Errors** (Domain errors use -32000 to -32099 range per JSON-RPC spec):

| PX Error Code | JSON-RPC Code | Description | Recovery Action |
|---------------|---------------|-------------|-----------------|
| `INVALID_PATH` | -32602 | Path doesn't exist in config tree | Check path syntax, verify parameter exists |
| `INVALID_CHANNEL` | -32602 | Channel out of range (1-4) | Use channel 1-4 |
| `INVALID_VALUE` | -32602 | Value outside valid range or wrong type | Check value constraints, verify type |
| `PRESET_INVALID` | -32602 | Corrupted or invalid preset data | Re-create preset, check file integrity |
| `PRESET_LOCKED` | -32001 | Preset field is vendor-locked | Field is read-only, cannot modify |
| `PERMISSION_DENIED` | -32002 | Operation not allowed | Check permissions, verify system state |
| `DEVICE_BUSY` | -32003 | Operation already in progress | Wait and retry |
| `HARDWARE_ERROR` | -32004 | Hardware communication failed | Check device health, reboot if persistent |

**Error Code Ranges:**
- `-32700` to `-32603`: Reserved by JSON-RPC 2.0 specification
- `-32099` to `-32000`: Application-specific errors (used for PX domain errors)
- Parameter validation errors use standard `-32602` (INVALID_PARAMS)

### Standard JSON-RPC Errors

| Code | Meaning |
|------|---------|
| -32700 | Parse error (invalid JSON) |
| -32600 | Invalid request (malformed JSON-RPC) |
| -32601 | Method not found |
| -32602 | Invalid params (see PX error code in data) |
| -32603 | Internal error (see PX error code in data) |

---

*PX Control API v1.0.0 - © 2025 Pascal Audio*
