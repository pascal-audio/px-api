# PX Control API - Python Client

Minimal Python client library for PX Control API (JSON-RPC over WebSocket).

## Installation

```bash
cd tools/py_client
pip install websockets
```

## Quick Start

```python
import asyncio
from py_client import PxClient

async def main():
    client = PxClient(host="192.168.64.100", port=80)
    await client.connect()
    
    # Make a request
    result = await client.request("api_ping")
    print(result)  # "pong"
    
    # Get configuration
    speaker = await client.request("setup_get", {"path": "/audio/output/speaker/1"})
    print(f"Gain: {speaker['gain']} dB")
    
    # Set configuration
    await client.request("setup_set_value", {
        "path": "/audio/output/speaker/1",
        "property": "gain",
        "value": -3.0
    })
    
    await client.disconnect()

asyncio.run(main())
```

## API Reference

### `PxClient(host, port)`

Create a new client instance.

**Parameters:**
- `host` (str): Device IP address (default: "192.168.64.100")
- `port` (int): WebSocket port (default: 80)

### `await client.connect()`

Connect to device WebSocket endpoint.

### `await client.disconnect()`

Disconnect from device.

### `await client.request(method, params)`

Send JSON-RPC request and wait for response.

**Parameters:**
- `method` (str): JSON-RPC method name (e.g., "setup_get" ...)
- `params` (dict, optional): Method parameters

**Returns:** Result value from JSON-RPC response

**Raises:**
- `RuntimeError`: If not connected
- `ValueError`: If server returns error response

**Example:**
```python
version = await client.request("api_version")
print(version['api_version'])
```

### `await client.subscribe(method, params, callback)`

Subscribe to notifications.

**Parameters:**
- `method` (str): Subscription method (e.g., "setup_subscribe", "metrics_subscribe")
- `params` (dict, optional): Subscription parameters
- `callback` (callable, optional): Handler for notification messages (receives params dict)

**Returns:** Subscription ID (str)

**Example:**
```python
def on_change(params):
    print(f"Changed: {params['path']} = {params['value']}")

sub_id = await client.subscribe(
    "setup_subscribe",
    {"path": "/audio/output/speaker/1"},
    on_change
)
```

### `await client.unsubscribe(method, subscription_id)`

Unsubscribe from notifications.

**Parameters:**
- `method` (str): Unsubscribe method (e.g., "setup_unsubscribe")
- `subscription_id` (str): Subscription ID from `subscribe()`

## Context Manager

Use `async with` for automatic connection/disconnection:

```python
async with PxClient(host="192.168.64.100") as client:
    result = await client.request("api_ping")
    print(result)
```

## Common Methods

### Device Control

```python
# Ping device
await client.request("api_ping")

# Get version
version = await client.request("api_version")

# Reboot device
await client.request("device_reboot", {"delay": 5})

# Power control
await client.request("device_power_on")
await client.request("device_power_off")
```

### Configuration

```python
# Get value
speaker = await client.request("setup_get", {"path": "/audio/output/speaker/1"})

# Set value
await client.request("setup_set_value", {
    "path": "/audio/output/speaker/1",
    "property": "gain",
    "value": -3.0
})

# Get entire config
config = await client.request("setup_get_all")

# Subscribe to changes
sub_id = await client.subscribe(
    "setup_subscribe",
    {"path": "/audio/output/speaker/1"},
    lambda p: print(f"Changed: {p['path']}")
)
```

### Presets

```python
# Apply preset
await client.request("preset_apply", {
    "channel": 1,
    "preset": preset_data
})

# Clear preset
await client.request("preset_clear", {"channel": 1})

# Show current preset
preset = await client.request("preset_show", {"channel": 1})
```

### Metrics

```python
# Subscribe to real-time metrics
def on_metrics(params):
    metrics = params.get("metrics", {})
    for path, value in metrics.items():
        print(f"{path}: {value}")

sub_id = await client.subscribe(
    "metrics_subscribe",
    {"freq": 10},
    on_metrics
)

# Unsubscribe
await client.unsubscribe("metrics_unsubscribe", sub_id)
```

## Error Handling

```python
try:
    result = await client.request("setup_get", {"path": "/invalid/path"})
except ValueError as e:
    print(f"Error: {e}")
except RuntimeError as e:
    print(f"Connection error: {e}")
```

## Examples

See `example.py` for complete working examples:

```bash
cd tools/py_client
python example.py
```

## Development

Install dev dependencies:

```bash
uv sync --extra dev
```

Format and lint code:

```bash
uv run ruff format .
uv run ruff check --fix .
```

## API Documentation

Full API reference: [docs/japi/01-api-reference.md](../../docs/japi/01-api-reference.md)
