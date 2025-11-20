# PX Control API Documentation

**Version:** 1.0.0  
**API Level:** 1  
**Emulator Version:** 2025.40.0-beta.1  
**Protocol:** JSON-RPC 2.0 over WebSocket  
**Last Updated:** November 17, 2025

---

## What is PX Control API?

The PX Control API provides comprehensive control over Pascal Audio professional amplifiers with integrated DSP processing. The API uses **JSON-RPC 2.0** over WebSocket for bidirectional communication, enabling third-party applications to:

- **Configure audio processing** - EQ, crossovers, delays, limiters across 3 processing layers
- **Monitor device status** - Real-time metrics, temperatures, power states
- **Manage presets** - Create, apply, and distribute channel configurations
- **Control device operations** - Power, reboot, firmware updates, time synchronization
- **Subscribe to events** - Real-time notifications for configuration changes and metrics

**Products supported:**
- PX Series - Professional amplifiers (PX2004, PX2004D, PX4004, PX4004D)

---

## API Status & Roadmap

### ✅ Stable (v1.0.0 - Production Ready)

- **Setup API** - All paths finalized, backward compatible in v1.x
- **Device API** - All methods stable
- **Preset API** - Locking mechanism finalized
- **Metrics API** - Real-time metrics stable

### ⚠️ Work in Progress

- **Status API** - Structure may change in v1.x
  - Use with caution in production
  - Existing fields may change
  - New fields may be added
  - **Recommendation:** Use setup subscriptions for critical workflows

### 🔮 Future (Roadmap)

**v1.1.0** 
- Status API stabilization

**v1.2.0** 
- Authentication


See **[05-best-practices.md](05-best-practices.md)** revision history section for detailed changelog.

---

## Quick Start (5 minutes)

### 1. Discover Devices on Network

PX devices advertise themselves via **mDNS** (Multicast DNS / Bonjour):

```bash
# Using avahi-browse (Linux)
avahi-browse -r _px._sub._pasconnect._tcp

# Using dns-sd (macOS)
dns-sd -B _px._sub._pasconnect._tcp

# Using japi_cli (cross-platform)
japi_cli device discover
```

**mDNS Service Details:**
- Service type: `_px._sub._pasconnect._tcp.local.`
- Default port: 80 (production), 8080 (emulator)

**Example output:**
```
Found 1 device(s):

Device: PX4000.4 0000-00000._pasconnect._tcp.local.
  Address: 192.168.176.128:8080
  Properties:
    firmware_version: 0.0.0
    serial: 0000001234X00000
    api_level: 1
    model_id: 50001
    api_version: 1.0.0
    device_name: PX4000.4 0000-00000
    vendor_id: 2
    vendor_name: Pascal Audio
    software_id: 50002
    model_name: PX4000.4
```

### 2. Run Emulator (Development)

**Download emulator** (v${EMULATOR_VERSION}) from [GitHub Releases](https://github.com/pascal-audio/px-api/releases):
- macOS: `px-emulator-release-${EMULATOR_VERSION}-aarch64-apple-darwin.tar.gz`
- Windows: `px-emulator-release-${EMULATOR_VERSION}-x86_64-pc-windows-gnu.tar.gz`  
- Linux: `px-emulator-release-${EMULATOR_VERSION}-x86_64-unknown-linux-gnu.tar.gz`

Extract and run:

```bash
# macOS (Apple Silicon)
tar -xzf px-emulator-release-${EMULATOR_VERSION}-aarch64-apple-darwin.tar.gz
cd px-emulator-release-${EMULATOR_VERSION}-aarch64-apple-darwin/
./px-emulator --port 8080

# Windows (PowerShell)
# Extract ZIP, then:
cd px-emulator-release-${EMULATOR_VERSION}-x86_64-pc-windows-gnu\
.\px-emulator.exe --port 8080

# Linux
tar -xzf px-emulator-release-${EMULATOR_VERSION}-x86_64-unknown-linux-gnu.tar.gz
cd px-emulator-release-${EMULATOR_VERSION}-x86_64-unknown-linux-gnu/
./px-emulator --port 8080
```

**Note:** Emulators bind to `0.0.0.0:8080` and advertise via mDNS as `PX-EMU-{random}.local`

### 3. Test Connection

We use [uv](https://docs.astral.sh/uv/) - a fast Python package manager (10-100x faster than pip) that handles dependencies automatically.

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run CLI tool (from tools/japi_cli directory)
cd tools/japi_cli

# Ping device
uv run japi_cli -t 192.168.1.100 api ping

# Show speaker 1 configuration
uv run japi_cli -t 192.168.1.100 setup get output-speaker 1
```

**Note:** `uv run` automatically manages dependencies - no need to install packages manually.

### 4. First API Call (Python)

```python
import asyncio
from py_client import PxClient

async def ping_device():
    async with PxClient(host='192.168.1.100', port=80) as client:
        # Ping device
        result = await client.request('api_ping', {})
        print('Ping response:', result)  # "pong"

asyncio.run(ping_device())
```

---

## JSON-RPC 2.0 Protocol

The PX Control API uses **JSON-RPC 2.0** for all communication. The protocol defines three message types:

1. **Request** (Client → Server) - Call a method
2. **Response** (Server → Client) - Return result or error
3. **Notification** (Server → Client) - Unsolicited update

**Full specification:** https://www.jsonrpc.org/specification

### Request Format

```typescript
{
  jsonrpc: "2.0",           // Always "2.0"
  method: "setup_get_value", // API method name
  params: {                  // Method parameters (object)
    path: "/audio/output/speaker/1/gain"
  },
  id: 1                      // Unique request ID (number or string)
}
```

### Response Format (Success)

```typescript
{
  jsonrpc: "2.0",
  result: {                  // Method result
    value: -3.0,
    type: "number",
    range: { min: -60.0, max: 12.0 }
  },
  id: 1                      // Matches request ID
}
```

### Response Format (Error)

```typescript
{
  jsonrpc: "2.0",
  error: {
    code: -32602,            // Standard JSON-RPC error code
    message: "Invalid params",
    data: {                  // PX-specific error details
      code: "INVALID_PATH",
      message: "Path does not exist: /audio/output/speaker/5",
      path: "/audio/output/speaker/5"
    }
  },
  id: 1
}
```

### Notification Format (Server → Client)

Server sends notifications to subscribed clients:

```typescript
{
  jsonrpc: "2.0",
  method: "setup_update",   // Notification method
  params: {                  // Notification data
    path: "/audio/output/speaker/1",
    value: -3.0,
  }
  // NO 'id' field (notifications don't have IDs)
}
```

**Notification Methods:**

| Method | Type | Payload | Description |
|--------|------|---------|-------------|
| `setup_update` | Subscription | `{path: string, value: any}` | Configuration changed at path |
| `metrics_update` | Subscription | `{path: string, value: object}` | Real-time audio metrics |
| `status_update` | Subscription | `{path: string, value: any}` | Device status changed at path ⚠️ WIP |
| `system_notification` | Broadcast | `{event: string, message: string, ...}` | Critical system events (ALL clients) |

**Subscription vs Broadcast:**
- **Subscription-based**: Only sent to clients who explicitly subscribed via `setup_subscribe`, `metrics_subscribe`, or `status_subscribe`
- **Broadcast**: Sent to ALL connected clients regardless of subscription (e.g., firmware updates, reboots)

**See:** [Notification Reference](#notification-reference) below for detailed schemas.

---

## WebSocket Connection

### Connection Lifecycle

```python
import asyncio
from py_client import PxClient

class PXDevice:
    """Wrapper around PxClient for application use."""
    
    def __init__(self, host: str, port: int = 80):
        self.client = PxClient(host=host, port=port)
    
    async def connect(self):
        """Connect to device."""
        await self.client.connect()
        print('Connected to PX device')
        # Send ping to verify connection
        await self.request('api_ping', {})
    
    async def request(self, method: str, params: dict):
        """Send request to device."""
        return await self.client.request(method, params)
    
    def handle_notification(self, method: str, params: dict):
        """Handle server notifications."""
        if method == 'setup_update':
            print('Config changed:', params['path'], '=', params['value'])
        elif method == 'metrics_update':
            print('Metrics:', params)
        elif method == 'system_notification':
            print('System event:', params['event'], params['message'])
    
    async def disconnect(self):
        """Disconnect from device."""
        await self.client.disconnect()
        print('Disconnected from PX device')

# Usage
async def main():
    device = PXDevice(host='192.168.1.100', port=80)
    await device.connect()
    
    # Get speaker 1 config
    result = await device.request('setup_get', {
        'path': '/audio/output/speaker/1'
    })
    print('Config:', result)
    
    # Set gain
    await device.request('setup_set', {
        'path': '/audio/output/speaker/1/gain',
        'value': {'gain': -3.0}
    })
    
    await device.disconnect()

asyncio.run(main())
```

---

## API Versioning

The PX Control API uses **semantic versioning** with two components:

### 1. API Version (Semantic)

**Format:** `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)

- **MAJOR** - Breaking changes (incompatible API changes)
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

**Query version:**
```python
version = await client.request('api_version', {})
# Returns: {'version': '1.0.0', 'level': 1}
```

### 2. API Level (Integer)

**Format:** Integer (e.g., `1`, `2`, `3`)

- Increments with each MAJOR version
- Used for rapid compatibility checks
- Client can check: `if (level >= 2) { use_new_features(); }`

**Version History:**
- **1.0.0** (Level 1) - November 2025 - Initial release
- **1.1.0** (Level 1) - Planned - Status API stabilization
- **2.0.0** (Level 2) - Future - Breaking changes TBD

---

## Documentation Structure

### **[01-api-reference.md](01-api-reference.md)** - Complete API Reference
All methods organized by domain with parameters, responses, error codes, and examples:
- **API Domain** (2): `api_ping`, `api_version`
- **Device Domain** (7): `device_reboot`, `device_reset`, `device_power_on`, `device_power_off`, `device_find_me`, `device_get_time`, `device_set_time`
- **Setup Domain** (8): `setup_get`, `setup_get_value`, `setup_set`, `setup_set_value`, `setup_get_all`, `setup_subscribe`, `backup_create`, `backup_restore`
- **Preset Domain** (4): `preset_apply`, `preset_clear`, `preset_create`, `preset_show`
- **Status Domain** (3): `status_get_all`, `status_get`, `status_subscribe` ⚠️ WIP (paths: `/state`, `/info`, `/network`, `/audio`, `/firmware`)
- **Metrics Domain** (2): `metrics_subscribe`, `metrics_unsubscribe` (paths: `/metrics/vu`, `/metrics/gain_reduction`, `/metrics/clip`)
- **Diagnostics** (1): `diagnostics_get`

### **[02-configuration-guide.md](02-configuration-guide.md)** - Setup Operations
Understanding the configuration system:
- **3-layer audio processing** (User → Array → Preset)
- **Setup tree architecture** (hierarchical JSON structure)
- **JSON path addressing** (`/audio/output/speaker/1/gain`)
- **GET operations** (single value, bulk read, flattened mode)
- **SET operations** (single value, batch updates, validation)
- **SUBSCRIBE operations** (real-time change notifications)
- **Common paths reference** (quick lookup table)

### **[03-device-management.md](03-device-management.md)** - Device Operations
Device-level control and monitoring:
- **Device information** (model, serial, firmware version)
- **Power management** (power on/off, reboot, reset)
- **Time synchronization** (get/set time, NTP)
- **Backup/restore** (configuration backup, restore from file)
- **Firmware updates** (RAUC update procedure, progress monitoring, safe mode)
- **Status monitoring** ⚠️ WIP (device/network/audio status)
- **Log access** (get logs, set log level, filtering)

### **[04-preset-guide.md](04-preset-guide.md)** - Preset Management
Working with channel presets:
- **Preset concept** (snapshot of preset processing layer)
- **Creating presets** (from current config, encrypted or plain JSON)
- **Applying presets** (to channels, with locking)
- **Preset locking** (vendor-locked fields return `null`)
- **Binary format** (`.px-preset` encrypted format)
- **Workflows** (factory distribution, installer tuning, A/B testing)

### **[05-best-practices.md](05-best-practices.md)** - Production Patterns
Building robust applications:
- **Error handling** (8 structured error codes with recovery patterns)
- **Connection management** (persistent connections, reconnection logic)
- **Request optimization** (batching, caching, debouncing)
- **Subscription management** (selective subscriptions, unsubscribe cleanup)
- **Performance tips** (rate limiting, throttling, bulk operations)
- **Security considerations** (network access, firmware signing)
- **Testing strategies** (unit tests, integration tests, emulator testing)
- **Monitoring** (health checks, error tracking, metrics)

---

## Notification Reference

Server-initiated notifications for real-time updates. Notifications are JSON-RPC messages without an `id` field.

### 1. setup_update

**Method:** `setup_update`  
**Type:** Subscription-based (requires `setup_subscribe`)  
**Purpose:** Notify when configuration value changes

**Payload:**
```typescript
{
  jsonrpc: "2.0",
  method: "setup_update",
  params: {
    path: string,    // JSON path of changed config (e.g., "/audio/output/speaker/1/user/gain")
    value: any       // New value at that path
  }
}
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "setup_update",
  "params": {
    "path": "/audio/output/speaker/1/user/gain",
    "value": -3.0
  }
}
```

**Triggers:**
- `setup_set` or `setup_set_value` operations
- `preset_apply` (multiple notifications for affected fields)
- `preset_clear` (multiple notifications)
- `backup_restore` (multiple notifications)

**See:** [02-configuration-guide.md - Subscriptions](02-configuration-guide.md#subscriptions)

---

### 2. metrics_update

**Method:** `metrics_update`  
**Type:** Subscription-based (requires `metrics_subscribe`)  
**Purpose:** Real-time audio metrics (VU meters, clipping, gain reduction)

**Payload:**
```typescript
{
  jsonrpc: "2.0",
  method: "metrics_update",
  params: {
    path: string,    // Metrics channel path (e.g., "/vu/speaker/1", "/clip/speaker/2")
    value: {         // Metrics object (structure depends on metric type)
      // VU metrics
      peak_db?: number,       // Peak level in dB
      rms_db?: number,        // RMS level in dB
      
      // Clip metrics
      clip_count?: number,    // Clip event count
      last_clip_ms?: number,  // Time since last clip
      
      // Gain reduction metrics
      reduction_db?: number   // Current gain reduction in dB
    }
  }
}
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "metrics_update",
  "params": {
    "path": "/vu/speaker/1",
    "value": {
      "peak_db": -12.5,
      "rms_db": -18.2
    }
  }
}
```

**Frequency:** Configurable per subscription (10Hz - 60Hz typical)

**See:** [01-api-reference.md - metrics_subscribe](01-api-reference.md#metrics_subscribe)

---

### 3. status_update

**Method:** `status_update`  
**Type:** Subscription-based (requires `status_subscribe`)  
**Purpose:** Device status changes (power state, network, errors) ⚠️ **WIP**

**Payload:**
```typescript
{
  jsonrpc: "2.0",
  "method": "status_update",
  "params": {
    path: string,    // Status path (e.g., "/state/power", "/network/lan1")
    value: any       // New status value
  }
}
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "status_update",
  "params": {
    "path": "/state/power",
    "value": "on"
  }
}
```

**Note:** Status API is work-in-progress. Structure may change in future versions.

**See:** [01-api-reference.md - status_subscribe](01-api-reference.md#status_subscribe)

---

### 4. system_notification

**Method:** `system_notification`  
**Type:** Broadcast (sent to ALL clients, no subscription required)  
**Purpose:** Critical system events requiring immediate attention

**Payload:**
```typescript
{
  jsonrpc: "2.0",
  "method": "system_notification",
  params: {
    event: string,      // Event type identifier
    message: string,    // Human-readable message
    severity: string,   // "info" | "warning" | "error" | "critical"
    timestamp?: string, // ISO 8601 timestamp
    ...                 // Additional event-specific fields
  }
}
```

**Event Types:**

| Event | Description | Additional Fields |
|-------|-------------|-------------------|
| `webserver_restart` | Server restarting (network config change) | `delay_seconds: number` |
| `firmware_update_started` | Firmware update beginning | `version: string` |
| `firmware_update_progress` | Update download/install progress | `progress: number, stage: string` |
| `firmware_update_complete` | Update successful, will reboot | `version: string` |
| `firmware_update_failed` | Update failed | `error: string` |
| `device_rebooting` | Device rebooting | `reason: string, delay_seconds: number` |
| `hardware_error` | Critical hardware failure | `component: string, error: string` |

**Examples:**

**Firmware Update:**
```json
{
  "jsonrpc": "2.0",
  "method": "system_notification",
  "params": {
    "event": "firmware_update_progress",
    "message": "Downloading firmware update",
    "severity": "info",
    "progress": 45,
    "stage": "downloading"
  }
}
```

**Network Config Change:**
```json
{
  "jsonrpc": "2.0",
  "method": "system_notification",
  "params": {
    "event": "webserver_restart",
    "message": "Server will restart in 3 seconds to apply network configuration",
    "severity": "warning",
    "delay_seconds": 3
  }
}
```

**Why Broadcast?**
- Cannot guarantee clients are subscribed before critical events
- Ensures all clients receive warnings about imminent disconnections
- Critical for firmware updates, reboots, hardware failures

**Client Requirements:**
- MUST handle unsolicited notifications at any time
- MUST NOT block waiting for response without processing notifications
- SHOULD implement reconnection logic for expected disconnections

**See:** [03-device-management.md - Firmware Updates](03-device-management.md#firmware-updates)

---

## Configuration System Overview

### 3-Layer Audio Processing

PX devices use a **3-layer signal processing chain** for speaker outputs:

```
Audio Input → User Layer → Array Layer → Preset Layer → Audio Output
```

1. **User Layer** - End-user adjustments
   - 10-band parametric EQ
   - Gain, polarity, delay, mute
   - High-pass filter
   - Generator mix
   - **Path:** `/audio/output/speaker/{channel}/user/`

2. **Array Layer** - Installer/integrator tuning
   - 5-band parametric EQ
   - Gain, polarity, delay
   - FIR filter
   - **Path:** `/audio/output/speaker/{channel}/array/`

3. **Preset Layer** - Factory presets
   - Drive mode (voltage/current)
   - 15-band parametric EQ
   - Crossover (up to 5-way: LF, LM, MF, HM, HF)
   - FIR filter
   - Peak/RMS/thermal limiters
   - Read-only if preset set (vendor-locked)
   - **Path:** `/audio/output/speaker/{channel}/preset/`

### Setup Tree Structure

Configuration stored as hierarchical JSON object:

```typescript
{
  audio: {
    input: {
      analog: [{'name': ..., 'gain': ..., 'delay': ..., 'mute': ...}, ...],
      digital: [],
      network: [{'name': ..., 'gain': ..., 'delay': ..., 'mute': ...}, ...],
      generator: {'kind': ..., 'frequency': ..., 'gain': ..., ...},
      config: {'input_switch': ...}
    },
    output: {
      speaker: [
        {'name': ..., 'primary_src': ..., 'fallback_src': ..., 'user': ..., 'array': ..., 'preset': ...},
        ...
      ],
      digital: [...],
      network: [...],
      speaker_ways: [{ id, way }, ...],
      summing_matrix: [[...]]
    }
  },
  install: {
    device_name, venue_name, customer_name, installer_name, ...
  },
  network: {
    lan1: { network_mode, ip_address, gateway, ... },
    lan2: { network_mode, ip_address, gateway, ... },
    mode: "split" | "bridge"
  },
  power: {
    power_on, standby_time, mute_time, fuse_protection, ...
  },
  gpio: {
    gpio1, gpio2, gpio3, gpio4
  }
}
```

### JSON Path Addressing

Every parameter accessible via path:

```
/audio/output/speaker/1/gain               # Speaker 1 output gain
/audio/output/speaker/1/user/eq/bands/3    # User EQ band 3
/audio/output/speaker/1/array/delay        # Array layer delay
/audio/output/speaker/1/preset/crossover   # Preset crossover
/network/lan/hostname                      # Device hostname
```

---

## Common Operations

### Get Single Value

```python
# Get speaker 1 configuration
result = await client.request('setup_get', {
  'path': '/audio/output/speaker/1'
})
print('Config:', result)
# Returns: {'fallback_src': 'off', 'name': 'Speaker 1', 'primary_src': 'analog/1'}
```

### Set Single Value

```python
# Set user EQ band 3 gain to 3.0 dB
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user/eq/bands/3',
  'value': {'gain': 3.0}
})
# Returns: {'success': True, 'path': '/audio/output/speaker/1/gain'}
```

### Get Node Object (Multiple Values)

```python
# Get entire user processing for speaker 1
result = await client.request('setup_get', {
  'path': '/audio/output/speaker/1/user'
})
print('User gain:', result['gain'])
print('User polarity:', result['polarity'])
# Returns: {'gain': -3.0, 'polarity': 1, 'mute': False, 'delay': 0.0, ...}

# Get EQ separately
eq = await client.request('setup_get', {'path': '/audio/output/speaker/1/user/eq'})
print('EQ bypass:', eq['bypass'])

# Get specific EQ band
band = await client.request('setup_get', {'path': '/audio/output/speaker/1/user/eq/bands/1'})
print('Band 1:', band)
```

### Set Node Object (Multiple Values)

```python
# Set EQ band parameters
await client.request('setup_set', {
  'path': '/audio/output/speaker/1/user/eq/bands/3',
  'value': {
    'frequency': 1000,
    'gain': 3.0,
    'q': 1.4,
    'kind': 'parametric'
  }
})
```

### Subscribe to Changes

```python
# Subscribe to all speaker 1 changes
def on_change(params):
    print('Changed:', params['path'], '=', params['value'])
    # Update UI here

sub_id = await client.subscribe('setup_subscribe', 
                                {'path': '/audio/output/speaker/1'},
                                on_change)
```

### Backup Configuration

```python
import json

# Backup entire device config
backup = await client.request('backup_create', {})
# Returns: {'config': {...}, 'timestamp': '...', 'version': 1}

# Save to file
with open('px-12345-backup.json', 'w') as f:
    json.dump(backup, f, indent=2)
```

### Restore Configuration

```python
import json

# Load from file
with open('px-12345-backup.json', 'r') as f:
    backup = json.load(f)

# Restore to device (pass the config object from backup)
await client.request('backup_restore', {'config': backup['config']})
# Returns: {'success': True, 'restored_paths': [...], 'message': '...'}
```

---

## Error Handling

The PX Control API uses **8 structured error codes** for machine-readable error handling:

| Code | Meaning | Recovery |
|------|---------|----------|
| `INVALID_PATH` | Configuration path doesn't exist | Check path syntax |
| `INVALID_CHANNEL` | Channel out of range (1-4) | Use valid channel |
| `INVALID_VALUE` | Value outside valid range | Check value constraints |
| `PRESET_LOCKED` | Preset field is vendor-locked | Field is read-only |
| `PRESET_INVALID` | Corrupted preset data | Re-create preset |
| `DEVICE_BUSY` | Operation in progress | Retry after delay |
| `HARDWARE_ERROR` | Hardware communication failed | Check device health |
| `PERMISSION_DENIED` | Operation not allowed | Check permissions |

**Example error response:**

```typescript
{
  jsonrpc: "2.0",
  error: {
    code: -32602,
    message: "Invalid params",
    data: {
      code: "INVALID_CHANNEL",
      message: "Channel 5 does not exist (valid range: 1-4)",
      channel: 5
    }
  },
  id: 1
}
```

**Error handling pattern:**

```python
import asyncio

try:
    await client.request('setup_set', {
        'path': '/audio/output/speaker/5/user',
        'value': {'gain': -3.0}
    })
except ValueError as error:
    error_msg = str(error)
    
    if 'INVALID_CHANNEL' in error_msg or 'Path not handled' in error_msg:
        print('Invalid channel - check message:', error_msg)
    elif 'INVALID_VALUE' in error_msg:
        print('Value out of range:', error_msg)
    elif 'DEVICE_BUSY' in error_msg:
        # Retry after 1 second
        await asyncio.sleep(1)
        # retry logic here
    else:
        print('Unexpected error:', error)
```

See **[05-best-practices.md](05-best-practices.md)** for complete error handling strategies.

---

## Preset Locking

Vendor-locked presets protect intellectual property by encrypting sensitive DSP parameters (crossover, limiters, EQ). When a locked preset is applied:

- **Locked fields** return `null` when queried
- **Unlocked fields** return actual values
- **SET operations** on locked fields are rejected with `PRESET_LOCKED` error

**Example locked preset:**

```python
# Get preset layer scalar values
preset = await client.request('setup_get', {
  'path': '/audio/output/speaker/1/preset'
})
print('Gain:', preset.get('gain'))  # May be None if locked or value if unlocked
print('Polarity:', preset.get('polarity'))  # Scalar field

# Get preset complex objects (must query their own paths)
try:
    crossover = await client.request('setup_get', {
        'path': '/audio/output/speaker/1/preset/crossover'
    })
    print('Crossover accessible:', crossover)
except ValueError as error:
    if 'PRESET_LOCKED' in str(error):
        print('Crossover is locked')

# Try to modify locked field
try:
    await client.request('setup_set', {
        'path': '/audio/output/speaker/1/preset/crossover',
        'value': {'ways': []}
    })
except ValueError as error:
    error_msg = str(error)
    if 'PRESET_LOCKED' in error_msg:
        print('Cannot modify locked preset field')
```

See **[04-preset-guide.md](04-preset-guide.md)** for complete preset workflows.

---

## Tools & Resources

### Python CLI Tool (`japi_cli`)

Command-line interface for all API operations. Uses [uv](https://docs.astral.sh/uv/) for fast, automatic dependency management.

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to CLI directory
cd tools/japi_cli

# Interactive mode with tab completion
uv run japi_cli -i -t 192.168.1.100

# Command examples
uv run japi_cli -t 192.168.1.100 setup get output-speaker 1
uv run japi_cli -t 192.168.1.100 setup set user-eq 1 3 --gain 3.0
uv run japi_cli -t 192.168.1.100 status get all
```

**Full documentation:** See `tools/japi_cli/README.md` for complete command reference and installation options.

### Virtual Emulators

Cross-platform device emulators for development without hardware access.

**Download:** [GitHub Releases](https://github.com/pascal-audio/px-api/releases) (v${EMULATOR_VERSION})
- `px-emulator-release-${EMULATOR_VERSION}-aarch64-apple-darwin.tar.gz` (macOS ARM64)
- `px-emulator-release-${EMULATOR_VERSION}-x86_64-pc-windows-gnu.tar.gz` (Windows)
- `px-emulator-release-${EMULATOR_VERSION}-x86_64-unknown-linux-gnu.tar.gz` (Linux)

**Usage:**
```bash
# Extract archive, navigate to directory, then run:
./px-emulator --port 8080               # macOS/Linux
.\px-emulator.exe --port 8080            # Windows
```

Emulators provide full API support with simulated DSP processing. See `README.md` in emulator package for details.

### JSON Schemas

Complete schemas for all types available in `schemas/` directory (available in release):

```
schemas/
├── catalog.json                    # Schema catalog with all type references
├── japi_path_registry.json        # Path-to-type mappings for setup operations
├── types/                          # Request/response types
│   ├── ApiVersionResponse.json
│   ├── DeviceRebootParams.json
│   ├── SetupGetParams.json
│   ├── SetupSetParams.json
│   └── ...
├── definitions/                    # DeviceSetup component types
│   ├── ArrayProcessing.json
│   ├── UserProcessing.json
│   ├── PresetProcessing.json
│   └── ...
├── views/                          # Read-optimized view types
│   ├── Device.Setup.View.json
│   ├── Audio.Setup.View.json
│   └── ...
├── status/                         # Runtime status types
│   ├── DeviceState.json
│   ├── AudioStatus.json
│   └── ...
└── changes/                        # Setup change notification types
    ├── Setup.Change.json
    └── Setup.Changed.json
```

**Key files:**
- `catalog.json` - Complete schema index with all type definitions and references
- `japi_path_registry.json` - Maps configuration paths to their data types

Use for code generation, validation, and contract testing.

---

## Support & Resources

**Version:** 1.0.0 (API Level 1)  
**Release Date:** November 2025  
**Support Status:** Fully supported

**Documentation:**
- [01-api-reference.md](01-api-reference.md) - Complete method reference
- [02-configuration-guide.md](02-configuration-guide.md) - Setup operations
- [03-device-management.md](03-device-management.md) - Device control
- [04-preset-guide.md](04-preset-guide.md) - Preset workflows
- [05-best-practices.md](05-best-practices.md) - Production patterns

**Contact:**
- Technical Support: support@pascal-audio.com
- GitHub Issues: https://github.com/pascal-audio/px-api/issues
- Documentation: https://github.com/pascal-audio/px-api

---

## License

**MIT License** - Documentation, schemas, CLI tool, examples, and client libraries are freely available under the MIT License.

**Emulator Binaries** - Proprietary license. Free for development and testing, but no redistribution or reverse engineering permitted.

See LICENSE file in repository root for complete terms.

---

*PX Control API v1.0.0 - © 2025 Pascal Audio*
