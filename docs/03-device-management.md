# Device Management

**PX Control API v1.0.0**

Complete guide to device operations, power management, firmware updates, and system monitoring.

---

## Table of Contents

- [Device Discovery](#device-discovery)
- [Device Information](#device-information)
- [Power Management](#power-management)
- [System Control](#system-control)
- [Time Synchronization](#time-synchronization)
- [Logging](#logging)
- [Firmware Updates](#firmware-updates)
- [Status Monitoring](#status-monitoring)
- [Backup & Restore](#backup--restore)

---

## Device Discovery

PX devices advertise themselves on the local network using **mDNS** (multicast DNS), enabling automatic discovery without manual IP configuration.

### Service Details

- **Service Type:** `_px._sub._pasconnect._tcp.local.`
- **Default Port:** 80 (JSON-RPC WebSocket at `/ws`)
- **Protocol:** WebSocket JSON-RPC 2.0

### Discovery Methods

**Python (Zeroconf):**

```python
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import socket
import time

class PxListener(ServiceListener):
    def add_service(self, zc, type_name, name):
        info = zc.get_service_info(type_name, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            print(f"Found: {name} at {address}:{info.port}")
            print(f"Properties: {info.properties}")

zeroconf = Zeroconf()
listener = PxListener()
browser = ServiceBrowser(zeroconf, "_px._sub._pasconnect._tcp.local.", listener)

time.sleep(3)  # Wait for discovery
browser.cancel()
zeroconf.close()
```

**CLI:**

```bash
# Discover devices with 5 second timeout
japi_cli device discover -t 5.0

# JSON output for scripting
japi_cli device discover -q
```

### Service Properties

Devices may advertise additional properties via mDNS TXT records:
- Model identifier
- Firmware version
- Device name
- Serial number

**Note:** Property availability depends on firmware version and configuration.

---

## Device Information

### Get Device Info

Query device identity and hardware information:

```python
info = await client.request('status_get', {'path': '/info'})

print('Model:', info['model_name'])               # 'PX2004D'
print('Serial:', info['serial'])                  # '11002233345X12345'
print('Vendor:', info['vendor_name'])             # 'Pascal Audio'
print('Model ID:', info['model_id'])              # 2002
```

**Use Cases:**
- Initial device discovery
- Multi-device management
- Support diagnostics
- UI display

---

## Power Management

### Power On

Power on amplifier outputs (from standby):

```python
await client.request('device_power_on', {})
print('Amplifier powered on')
```

**Timeline:**
1. Method returns immediately (~10ms)
2. Power rails sequence on (~2-5 seconds)
3. DSP initializes
4. Amplifier outputs active

**Use Cases:**
- Remote power control
- Scheduled power on
- Automation integration
- Room control systems

---

### Power Off

Power off amplifier outputs (standby mode):

```python
await client.request('device_power_off', {})
print('Amplifier in standby')
```

**Note:** Device remains network-connected and API-accessible. Only amplifier outputs disabled.

**Timeline:**
1. Outputs muted
2. Power rails sequence off (~1-2 seconds)
3. Device remains on network

**Use Cases:**
- Energy saving mode
- Scheduled off hours
- Emergency mute
- Automated shutdown

---

### Reboot Device

Perform warm restart:

```python
# Immediate reboot
await client.request('device_reboot', {})

# Delayed reboot (30 seconds)
await client.request('device_reboot', {'delay': 30})
```

**Timeline:**
1. Method returns success
2. Wait `delay` seconds (default: 5)
3. Device reboots
4. WebSocket disconnects
5. Device comes back online (~30-60 seconds)

**Use Cases:**
- Apply firmware updates
- Recover from error state
- Clear transient issues
- Scheduled maintenance

---

### Factory Reset

Reset device to factory defaults:

```python
# Full factory reset
await client.request('device_reset', {})

# Reset but preserve network settings
await client.request('device_reset', {
  'preserve_network': True
})
```

**Warning:** This operation:
- Erases all user configuration
- Clears all presets
- Resets audio processing
- Optionally preserves network config
- Device auto-reboots

**Use Cases:**
- Return to factory state
- Clear problematic config
- Prepare for new installation
- Testing clean slate

---

### Find Me

Visual/audible device identification:

```python
# Identify for 60 seconds (default)
await client.request('device_find_me', {})

# Identify for 2 minutes
await client.request('device_find_me', {'timeout': 120})
```

**Device Behavior:**
- LEDs flash in pattern
- Optional audible tone
- Auto-timeout

**Use Cases:**
- Locate device in rack
- Physical verification
- Multi-device identification
- Network-to-physical mapping

---

## System Control

### Get System Time

```python
from datetime import datetime

result = await client.request('device_get_time', {})
print('Device time:', result['time'])
# Output: '2025-11-17T14:30:00Z'

# Check clock drift
from datetime import timezone
device_time = datetime.fromisoformat(result['time'].replace('Z', '+00:00'))
local_time = datetime.now(timezone.utc)
drift = abs((device_time - local_time).total_seconds())
print(f'Clock drift: {drift} seconds')
```

---

### Set System Time

```python
from datetime import datetime

# Set to current time
now = datetime.utcnow().isoformat() + 'Z'
await client.request('device_set_time', {'time': now})

# Set specific time (UTC)
await client.request('device_set_time', {
  'time': '2025-11-17T14:30:00Z'
})
```

**Note:**
- Time is UTC
- Persists to RTC (survives reboot)
- Prefer NTP for production

**Use Cases:**
- Initial time setup
- Manual time correction
- Testing with specific times
- Offline installations

---

## Logging

### Get Device Logs

Retrieve logs with pagination:

```python
# Get latest 100 logs (default)
response = await client.request('logs_get', {})
for log in response['logs']:
    print(f"[{log['timestamp']}] {log['level']}: {log['message']}")

# Pagination: get next 100
more_response = await client.request('logs_get', {
  'limit': 100,
  'offset': 100
})

# Get only recent 20 logs
recent_response = await client.request('logs_get', {'limit': 20})

# Filter errors
errors = [log for log in recent_response['logs'] if log['level'] == 'error']
```

**Log Entry Format:**
```ts
{
  'timestamp': str  # ISO 8601 UTC
  'level': str      # 'error' | 'warn' | 'info' | 'debug' | 'trace'
  'target': str     # Module (e.g., 'thrust::device')
  'message': str    # Log message
}
```

**Use Cases:**
- Debugging issues
- Remote diagnostics
- Error monitoring
- Support investigations

---

### Set Log Level

Dynamically adjust logging verbosity:

```python
# Set global log level
await client.request('logs_set_level', {'filter': 'DEBUG'})

# Available levels: 'TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR'
await client.request('logs_set_level', {'filter': 'INFO'})

# Most verbose
await client.request('logs_set_level', {'filter': 'TRACE'})
```

**Log Levels:**
- `error`: Errors only
- `warn`: Warnings + errors
- `info`: Normal operation (default)
- `debug`: Debug output
- `trace`: Verbose tracing

**Use Cases:**
- Enable verbose logging for debugging
- Reduce log noise in production
- Focus on specific subsystems

---

## Firmware Updates

PX devices use **RAUC** (Robust Auto-Update Controller) for safe, atomic firmware updates with automatic rollback.

### Update Features

- **Atomic updates:** All-or-nothing (no partial updates)
- **Dual partition:** A/B system (current + backup)
- **Automatic rollback:** Falls back to previous version on failure
- **Signature verification:** Only signed bundles accepted
- **Safe mode:** Recovery mode if both partitions fail

### Update Process

```python
# 1. Initiate update
await client.request('firmware_update', {
  'bundle_url': 'http://192.168.1.10/firmware/px-v1.2.0.raucb'
})

# 2. Monitor progress via system_notification
def on_notification(params):
    event = params.get('event')
    
    if event == 'update_started':
        print('Update started')
    elif event == 'update_downloading':
        print('Progress:', params.get('progress'), '%')
    elif event == 'update_installing':
        print('Installing...')
    elif event == 'update_complete':
        print('Update complete - device will reboot')
    elif event == 'update_failed':
        print('Update failed:', params.get('error'))

# Subscribe to system notifications
await client.subscribe('system_subscribe', {}, on_notification)
```

### Update Timeline

```
┌──────────────────────────────────────────────────────────┐
│ TIMELINE: Firmware Update Process                        │
└──────────────────────────────────────────────────────────┘

T+0s    : Client calls firmware_update()
T+1s    : Device responds { success: true }
T+1s    : Download starts (bundle_url)
          → Notification: update_downloading (0%)
T+30s   : Download 50%
          → Notification: update_downloading (50%)
T+60s   : Download complete
          → Notification: update_downloading (100%)
T+61s   : Installing to inactive partition
          → Notification: update_installing
T+120s  : Installation complete
          → Notification: update_complete
T+125s  : Device reboots
          ─────────────────────
T+155s  : Device boots from new partition
T+160s  : Device online (new firmware)
T+180s  : Boot watchdog confirms success
          (If boot fails, auto-rollback to old partition)
```

### Bundle URL Requirements

- Must be HTTP/HTTPS URL
- Device must have network access
- Signed RAUC bundle (`.raucb` file)
- Firmware compatibility checked

**Example URLs:**
```python
# HTTP server
'http://192.168.1.10/firmware/px-v1.2.0.raucb'

# HTTPS
'https://firmware.pascal-audio.com/px/v1.2.0/px-v1.2.0.raucb'

# Local network file server
'http://update-server.local/px-v1.2.0.raucb'
```

### Safe Mode

If firmware update fails catastrophically:

1. Device attempts boot from partition A
2. Fails → attempts boot from partition B
3. Both fail → boots into safe mode

**Safe Mode Features:**
- Minimal firmware (safe_mode binary)
- Network accessible
- Firmware update API available
- Limited functionality (no audio processing)

**Recovery from Safe Mode:**
```python
from py_client import PxClient

# Connect to device in safe mode
async with PxClient(host='192.168.1.100', port=80) as client:
    # Push recovery firmware
    await client.request('firmware_update', {
        'bundle_url': 'http://192.168.1.10/firmware/px-v1.1.0.raucb'
    })

# Device reboots to working firmware
```

### Best Practices

**1. Backup before update:**
```python
import base64

backup = await client.request('backup_create', {})
config_binary = base64.b64decode(backup['config'])
with open('pre-update-backup.bin', 'wb') as f:
    f.write(config_binary)

await client.request('firmware_update', {'bundle_url': '...'})
```

**2. Fleet updates with retry logic:**
```python
import asyncio
from py_client import PxClient

async def update_fleet(devices: list[str], bundle_url: str):
    for address in devices:
        retries = 3
        while retries > 0:
            try:
                async with PxClient(host=address, port=80) as client:
                    await client.request('firmware_update', {'bundle_url': bundle_url})
                    print(f'✓ {address} update initiated')
                    break
            except Exception as error:
                retries -= 1
                print(f'✗ {address} failed, retries left: {retries}')
                await asyncio.sleep(5)
```

---

## Status Monitoring

⚠️ **Warning:** Status API structure may change in v1.x releases. Use with caution in production.

### Get All Status

```python
try:
    status = await client.request('status_get_all', {})
except Exception as e:
    print(f'Status request failed: {e}')
    status = None

# Check if status was returned
if status and isinstance(status, dict):
    # Device status
    print('Power:', status['state']['power_state'])       # 'on' | 'standby' | 'off'
    print('Uptime:', status['state']['uptime_seconds'])   # 3600
    print('Boot time:', status['state']['boot_time'])     # '2025-11-17T10:00:00Z'

    # Network status
    if status.get('network'):
        print('LAN1 IP:', status['network']['lan1']['address'])   # '192.168.1.100'
        print('LAN1 connected:', status['network']['lan1']['connected'])  # True
        if status['network'].get('dante'):
            print('Dante:', status['network']['dante'].get('connected'))  # True

    # Audio status
    print('Sample rate:', status['audio']['sample_rate'])  # 48000
    print('Sync source:', status['audio']['sync_source'])  # 'internal' | 'dante'

    # Firmware versions (if available)
    if status.get('firmware'):
        print('Main:', status['firmware']['main'])             # '1.2.3'
        print('DSP:', status['firmware']['dsp'])               # '2.0.1'
```

### Get Specific Status

```python
# Get device state only
device_state = await client.request('status_get', {
  'path': '/state'
})

# Get device info
info = await client.request('status_get', {
  'path': '/info'
})

# Get network status
network = await client.request('status_get', {
  'path': '/network'
})
```

### Subscribe to Status Changes

```python
def on_status_change(params):
    print('Status changed:', params['path'])
    print('New value:', params['value'])

sub_id = await client.subscribe('status_subscribe',
                                {'paths': ['/state', '/info', '/network']},
                                on_status_change)
```

**Recommendation:** For production, prefer setup subscriptions and metrics subscriptions over status subscriptions.

**Note:** For backup/restore operations, see **[02-configuration-guide.md](02-configuration-guide.md)** Workflows section.

---

## Device Workflows

### Workflow 1: System Health Check

```python
async def health_check(client):
    # 1. Ping device
    ping = await client.request('api_ping', {})
    if ping != 'pong':
        raise Exception('Device not responding')

    # 2. Get device info
    info = await client.request('status_get', {'path': '/info'})
    print(f"Device: {info['model_name']} ({info['serial']})")

    # 3. Get status
    status = await client.request('status_get_all', {})
    print(f"Power: {status['state']['power_state']}")
    print(f"Uptime: {status['state']['uptime_seconds']}s")

    # 4. Check for pending reboot
    if status['state']['reboot_pending']['pending']:
        print(f"Reboot pending: {status['state']['reboot_pending']['reason']}")

    # 5. Get recent errors
    logs_result = await client.request('logs_get', {'limit': 20})
    errors = [log for log in logs_result['logs'] if log['level'] == 'error']
    if len(errors) > 0:
        print(f'{len(errors)} errors in recent logs')

    return {'healthy': len(errors) == 0, 'info': info, 'status': status}
```

### Workflow 2: Emergency Troubleshooting

```python
import json
import time
from datetime import datetime

async def emergency_diagnostics(client):
    print('Running emergency diagnostics...')

    # 1. Collect device info
    info = await client.request('status_get', {'path': '/info'})

    # 2. Enable verbose logging
    await client.request('logs_set_level', {
        'filter': 'trace'
    })
    print('✓ Verbose logging enabled')

    # 3. Collect diagnostics (for troubleshooting only - format unstable)
    diag = await client.request('diagnostics_get', {})

    # 4. Collect recent logs
    logs_result = await client.request('logs_get', {'limit': 500})

    # 5. Get full status
    status = await client.request('status_get_all', {})

    # 6. Get full config
    config = await client.request('setup_get_all', {})

    # 7. Save diagnostic bundle
    bundle = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'info': info,
        'status': status,
        'config': config,
        'logs': logs_result['logs'],
        'diagnostics': diag
    }

    filename = f"diagnostic-{info['serial']}-{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(bundle, f, indent=2)

    print('✓ Diagnostic bundle saved')

    # 8. Restore normal logging
    await client.request('logs_set_level', {'filter': 'info'})
```

---

*PX Control API v1.0.0 - © 2025 Pascal Audio*
