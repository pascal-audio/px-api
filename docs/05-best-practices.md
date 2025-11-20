# Best Practices & Error Handling

**PX Control API v1.0.0**

Production-ready patterns for robust, efficient integration.

---

## Table of Contents

- [Error Handling](#error-handling)
- [Connection Management](#connection-management)
- [Request Optimization](#request-optimization)
- [Subscription Management](#subscription-management)
- [Performance Tips](#performance-tips)
- [Security Considerations](#security-considerations)
- [Testing Strategies](#testing-strategies)
- [Monitoring & Observability](#monitoring--observability)

---

## Error Handling

### Error Code Reference

All errors return structured JSON-RPC responses with:
- **Numeric code**: JSON-RPC error code (standard -326xx or application-specific -320xx)
- **String code**: Specific error identifier in `error.data.code` field

**Error Code Ranges:**
- `-32700` to `-32603`: Standard JSON-RPC errors (reserved by spec)
- `-32099` to `-32000`: Application-specific errors (PX domain errors)
- `-32602`: Parameter validation errors (standard)

**Standard JSON-RPC Errors:**

| Code | Name | Meaning | Recovery |
|------|------|---------|----------|
| -32600 | INVALID_REQUEST | Malformed JSON-RPC | Fix request format |
| -32601 | METHOD_NOT_FOUND | Unknown method | Check method name |
| -32602 | INVALID_PARAMS | Missing/invalid params | Validate parameters |
| -32603 | INTERNAL_ERROR | Server error | Retry, check logs |

**Application-Specific Errors** (in `error.data.code`):

| Code String | JSON-RPC Code | Meaning | Recovery |
|-------------|---------------|---------|----------|
| INVALID_PATH | -32602 | Config path doesn't exist | Check path spelling |
| INVALID_CHANNEL | -32602 | Channel out of range (1-4) | Use valid channel |
| INVALID_VALUE | -32602 | Value outside valid range | Check value constraints |
| PRESET_INVALID | -32602 | Preset corrupted/incompatible | Use valid preset |
| PRESET_LOCKED | -32001 | Preset is vendor-locked | Fields return null |
| PERMISSION_DENIED | -32002 | Operation not allowed | Check user permissions |
| DEVICE_BUSY | -32003 | Device performing operation | Wait and retry |
| HARDWARE_ERROR | -32004 | Hardware communication failed | Check device, retry |

### Error Handling Pattern

```python
import asyncio
from typing import TypeVar, Any

T = TypeVar('T')

async def robust_request(
    client,
    method: str,
    params: dict,
    retries: int = 3
) -> Any:
    for attempt in range(retries):
        try:
            return await client.request(method, params)
        except ValueError as error:
            # Parse error message - contains error code string
            error_msg = str(error)
            
            # Unrecoverable errors - don't retry
            if any(code in error_msg for code in [
                'INVALID_REQUEST',
                'METHOD_NOT_FOUND', 
                'INVALID_PARAMS',
                'INVALID_PATH',
                'INVALID_CHANNEL',
                'INVALID_VALUE',
                'PRESET_INVALID',
                'PRESET_LOCKED',
                'PERMISSION_DENIED'
            ]):
                raise  # Don't retry

            # Recoverable errors - retry with backoff
            if any(code in error_msg for code in [
                'INTERNAL_ERROR',
                'DEVICE_BUSY',
                'HARDWARE_ERROR'
            ]):
                print(f'Attempt {attempt + 1}/{retries} failed: {error_msg}')
                if attempt < retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    continue

            # Unknown error - throw
            raise

    raise Exception('Max retries exceeded')

# Usage
try:
    user = await robust_request(client, 'setup_get', {
        'path': '/audio/output/speaker/1/user'
    })
    print('Gain:', user['gain'])
except ValueError as error:
    print(f'Failed: {str(error)}')
```

### Error-Specific Recovery

```python
import asyncio

async def set_gain_with_recovery(
    client,
    channel: int,
    gain: float
):
    try:
        await client.request('setup_set', {
            'path': f'/audio/output/speaker/{channel}/user',
            'value': {'gain': gain}
        })
    except ValueError as error:
        error_msg = str(error)
        
        if 'INVALID_PATH' in error_msg or 'Path not handled' in error_msg:  # INVALID_PATH'Path not handled' in error_msg:  # INVALID_PATH
            raise Exception(f'Channel {channel} does not exist')
        elif 'INVALID_CHANNEL' in error_msg:  # INVALID_CHANNEL
            raise Exception(f'Channel must be 1-4, got {channel}')
        elif 'INVALID_VALUE' in error_msg:  # INVALID_VALUE
            raise Exception(f'Gain {gain} outside valid range (-30 to +10 dB)')
        elif 'DEVICE_BUSY' in error_msg:  # DEVICE_BUSY DEVICE_BUSY
            print('Device busy, retrying...')
            await asyncio.sleep(0.5)
            return await set_gain_with_recovery(client, channel, gain)  # Retry
        elif 'HARDWARE_ERROR' in error_msg:  # HARDWARE_ERROR
            print('Hardware communication failed')
            raise
        else:
            raise
```

---

## Connection Management

### Robust WebSocket Client

Note: The `PxClient` library already handles connection management and reconnection. For custom implementations:

```python
class RobustPXDevice:
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private requestId = 0;
  private pendingRequests = new Map<number, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }>();

  constructor(
    private address: string,
    private port: number = 80
  ) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(`ws://${this.address}:${this.port}/ws`);

      this.ws.onopen = () => {
        console.log('✓ Connected');
        this.clearReconnectTimer();
        resolve();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.warn('Connection closed, reconnecting...');
        this.scheduleReconnect();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };
    });
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setTimeout(() => {
      console.log('Reconnecting...');
      this.connect().catch(() => {
        // Retry again
        this.reconnectTimer = null;
        this.scheduleReconnect();
      });
    }, 5000);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private handleMessage(data: string): void {
    try {
      const msg = JSON.parse(data);

      // Handle response
      if ('id' in msg && msg.id !== undefined) {
        const pending = this.pendingRequests.get(msg.id);
        if (pending) {
          this.pendingRequests.delete(msg.id);
          if (msg.error) {
            pending.reject(msg.error);
          } else {
            pending.resolve(msg.result);
          }
        }
      }

      // Handle notification
      if ('method' in msg && !('id' in msg)) {
        this.emit('notification', msg);
      }
    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }

  async request(method: string, params: any, timeout = 5000): Promise<any> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    return new Promise((resolve, reject) => {
      const id = ++this.requestId;

      // Store promise
      this.pendingRequests.set(id, { resolve, reject });

      // Send request
      this.ws!.send(JSON.stringify({
        jsonrpc: '2.0',
        id,
        method,
        params
      }));

      // Timeout
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, timeout);
    });
  }

  disconnect(): void {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage
const device = new RobustPXDevice('192.168.1.100', 80);
await device.connect();

// Survives disconnections
const gain = await device.request('setup_get_value', {
  path: '/audio/output/speaker/1/user/gain'
});
```

### Connection Health Check

```python
import asyncio
import time

class HealthMonitor:
    def __init__(self, client, interval_ms: int = 30000):
        self.client = client
        self.interval_ms = interval_ms
        self.task = None
        self.running = False
    
    async def _monitor_loop(self):
        while self.running:
            try:
                start = time.time()
                await self.client.request('api_ping', {})
                latency = (time.time() - start) * 1000  # ms

                print(f'✓ Ping: {latency:.0f}ms')

                if latency > 1000:
                    print('High latency detected')
            except Exception as error:
                print('Ping failed:', error)
                # Connection will auto-reconnect
            
            await asyncio.sleep(self.interval_ms / 1000)
    
    def start(self):
        self.running = True
        self.task = asyncio.create_task(self._monitor_loop())
    
    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            self.task = None

# Usage
monitor = HealthMonitor(client)
monitor.start()
```

---

## Request Optimization

### Batch Operations

```python
# BAD: 10 sequential requests (bands are 1-indexed)
for band in range(1, 11):
    await client.request('setup_set', {
        'path': f'/audio/output/speaker/1/user/eq/bands/{band}',
        'value': {
            'kind': 'parametric',
            'gain': 0.0,
            'frequency': 1000.0,
            'q': 0.7,
            'bypass': False
        }
    })

# BETTER: Batch requests using asyncio.gather
import asyncio

band_updates = []
for band in range(1, 11):
    band_updates.append(
        client.request('setup_set', {
            'path': f'/audio/output/speaker/1/user/eq/bands/{band}',
            'value': {
                'kind': 'parametric',
                'gain': 0.0,
                'frequency': 100.0 * band,
                'q': 0.7,
                'bypass': False
            }
        })
    )

# Execute all updates concurrently
await asyncio.gather(*band_updates)
```

### Caching Strategy

```python
import time

class CachedPXDevice:
    def __init__(self, client, cache_ttl_ms: int = 5000):
        self.client = client
        self.cache = {}  # path -> {'value': ..., 'timestamp': ...}
        self.cache_ttl_ms = cache_ttl_ms
        
        # Subscribe to changes
        async def on_notification(msg):
            if msg.get('method') == 'setup_update':
                # Invalidate cache for changed path
                self.invalidate_cache(msg['params']['path'])
        
        # Note: You'd call client.subscribe('setup_update', ..., on_notification)
    
    async def get(self, path: str, use_cache: bool = True):
        # Check cache
        if use_cache:
            cached = self.cache.get(path)
            if cached and (time.time() * 1000 - cached['timestamp']) < self.cache_ttl_ms:
                return cached['value']
        
        # Fetch fresh (get parent object)
        value = await self.client.request('setup_get', {'path': path})
        
        # Update cache
        self.cache[path] = {
            'value': value,
            'timestamp': time.time() * 1000
        }
        
        return value
    
    def invalidate_cache(self, path: str):
        # Invalidate exact match
        self.cache.pop(path, None)
        
        # Invalidate children (e.g., /audio/output/speaker/1)
        keys_to_delete = [key for key in self.cache.keys() if key.startswith(path)]
        for key in keys_to_delete:
            del self.cache[key]

# Usage
cached = CachedPXDevice(client)

# First call: fetches from device
user = await cached.get('/audio/output/speaker/1/user')
gain1 = user['gain']

# Second call: returns cached (if within TTL)
user2 = await cached.get('/audio/output/speaker/1/user')
gain2 = user2['gain']

# Force refresh
user3 = await cached.get('/audio/output/speaker/1/user', False)
gain3 = user3['gain']
```

### Debounced Updates

```python
import asyncio

class DebouncedUpdater:
    def __init__(self, client, delay_ms: int = 300):
        self.client = client
        self.delay_ms = delay_ms
        self.timers = {}  # path -> (task, value)
    
    def set(self, path: str, value):
        # Clear existing timer
        if path in self.timers:
            task, _ = self.timers[path]
            task.cancel()
        
        # Schedule update
        async def delayed_update():
            try:
                await asyncio.sleep(self.delay_ms / 1000)
                await self.client.request('setup_set', {'path': path, 'value': value})
                print(f'✓ Updated {path}')
            except asyncio.CancelledError:
                pass
            except Exception as error:
                print(f'Failed to update {path}:', error)
            finally:
                self.timers.pop(path, None)
        
        task = asyncio.create_task(delayed_update())
        self.timers[path] = (task, value)
    
    async def flush(self):
        # Trigger all pending updates immediately
        tasks = []
        
        for path, (task, value) in list(self.timers.items()):
            task.cancel()
            tasks.append(
                self.client.request('setup_set', {'path': path, 'value': value})
            )
        
        self.timers.clear()
        await asyncio.gather(*tasks, return_exceptions=True)

# Usage (e.g., slider UI)
updater = DebouncedUpdater(client)

# User drags slider - many rapid updates
def on_slider_input(value):
    updater.set('/audio/output/speaker/1/user', {'gain': value})

# Only sends last value after 300ms of no changes
```

---

## Subscription Management

### Subscription Manager

```python
class SubscriptionManager:
    def __init__(self, client):
        self.client = client
        self.subscriptions = set()
        
        # Note: Resubscribe on reconnect would be handled by
        # a reconnection callback if implementing custom WebSocket client
    
    async def subscribe(self, path: str):
        if path not in self.subscriptions:
            await self.client.request('setup_subscribe', {'path': path})
            self.subscriptions.add(path)
            print(f'✓ Subscribed to {path}')
    
    async def unsubscribe(self, path: str):
        if path in self.subscriptions:
            await self.client.request('setup_unsubscribe', {'path': path})
            self.subscriptions.discard(path)
            print(f'✓ Unsubscribed from {path}')
    
    async def resubscribe_all(self):
        print(f'Resubscribing to {len(self.subscriptions)} paths...')
        for path in self.subscriptions:
            try:
                await self.client.request('setup_subscribe', {'path': path})
            except Exception as error:
                print(f'Failed to resubscribe to {path}:', error)
    
    def get_subscriptions(self) -> list:
        return list(self.subscriptions)

# Usage
subs = SubscriptionManager(client)

await subs.subscribe('/audio/output/speaker/1/user/gain')
await subs.subscribe('/audio/output/speaker/2/user/gain')

# Automatic resubscription on reconnect
```

---

## Performance Tips

### 1. Use `setup_get_all` for Bulk Reads

```python
# BAD: 40 individual requests
gains = []
for ch in range(1, 5):
    for band in range(1, 11):  # Bands are 1-indexed
        result = await client.request('setup_get', {
            'path': f'/audio/output/speaker/{ch}/user/eq/bands/{band}'
        })
        gain = result['gain']
        gains.append(gain)

# GOOD: Single request
config = await client.request('setup_get_all', {'flatten': False})
for ch in ['1', '2', '3', '4']:
    speaker = config['audio']['output']['speaker'][ch]
    for band in speaker['user']['eq']['bands']:
        gains.append(band['gain'])
```

### 2. Minimize Subscription Scope

```python
# BAD: Subscribe to entire tree
await client.request('setup_subscribe', {'path': '/'})

# GOOD: Subscribe to specific paths
await client.request('setup_subscribe', {
    'path': '/audio/output/speaker/1/user'
})
```

### 3. Batch Related Updates

```python
# BAD: Multiple requests
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {'gain': -3.0}
})
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {'mute': False}
})

# GOOD: Single request
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {
        'gain': -3.0,
        'mute': False
    }
})
```

---

## Security Considerations

### 1. Network Isolation

Devices should be on isolated control network:
- **Management VLAN:** API access
- **Audio VLAN:** Dante/audio traffic
- **Public network:** Blocked

### 2. Secure Firmware Updates

Use official firmware update tools and signed RAUC bundles. Contact Pascal Audio support for firmware update procedures.

### 3. Configuration Validation

```python
# Validate before applying
def validate_gain(gain: float):
    if gain < -30 or gain > 10:
        raise ValueError(f'Gain {gain} outside valid range [-30, 10]')

validate_gain(-3.0)
await client.request('setup_set', {
    'path': '/audio/output/speaker/1/user',
    'value': {'gain': -3.0}
})
```

---

## Testing Strategies

### Unit Testing with Mocks

```python
import pytest

# Mock device
class MockPXDevice:
    def __init__(self):
        self.state = {}
    
    async def request(self, method: str, params: dict):
        if method == 'setup_get':
            return self.state.get(params['path'])
        
        if method == 'setup_set':
            self.state[params['path']] = params['value']
            return {'success': True}
        
        raise NotImplementedError(f'Method not mocked: {method}')

# Test
@pytest.mark.asyncio
async def test_gain_controller():
    mock = MockPXDevice()
    controller = GainController(mock)
    
    await controller.set_gain(1, -3.0)
    
    user = await mock.request('setup_get', {
        'path': '/audio/output/speaker/1/user'
    })
    gain = user['gain']
    
    assert gain == -3.0
```

### Integration Testing

```python
import pytest
import re
from py_client import PxClient

@pytest.fixture
async def device():
    async with PxClient(host='192.168.1.100', port=80) as client:
        yield client

@pytest.mark.asyncio
async def test_device_info(device):
    info = await device.request('status_get', {'path': '/info'})
    assert re.match(r'^PX\d{4}$', info['model_name'])

@pytest.mark.asyncio
async def test_set_and_get_gain(device):
    await device.request('setup_set', {
        'path': '/audio/output/speaker/1/user',
        'value': {'gain': -3.0}
    })
    
    user = await device.request('setup_get', {
        'path': '/audio/output/speaker/1/user'
    })
    
    assert abs(user['gain'] - (-3.0)) < 0.01
```

---

## Monitoring & Observability

### Metrics Collection

```python
import time
import asyncio

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'error_count': 0,
            'latencies': []
        }
    
    async def instrumented_request(self, client, method: str, params: dict):
        start = time.time()
        self.metrics['request_count'] += 1
        
        try:
            result = await client.request(method, params)
            latency = (time.time() - start) * 1000  # ms
            self.metrics['latencies'].append(latency)
            return result
        except Exception as error:
            self.metrics['error_count'] += 1
            raise error
    
    def get_stats(self):
        latencies = self.metrics['latencies']
        if not latencies:
            return None
        
        return {
            'total_requests': self.metrics['request_count'],
            'error_count': self.metrics['error_count'],
            'error_rate': self.metrics['error_count'] / self.metrics['request_count'],
            'avg_latency': sum(latencies) / len(latencies),
            'p50': self.percentile(latencies, 0.5),
            'p95': self.percentile(latencies, 0.95),
            'p99': self.percentile(latencies, 0.99)
        }
    
    def percentile(self, arr: list, p: float) -> float:
        sorted_arr = sorted(arr)
        index = int(len(sorted_arr) * p)
        return sorted_arr[index]

# Usage
metrics = MetricsCollector()

async def print_stats():
    while True:
        await asyncio.sleep(60)  # Every minute
        stats = metrics.get_stats()
        print('API Stats:', stats)

asyncio.create_task(print_stats())
```

### Health Dashboard

```python
import time
from typing import Literal

class HealthStatus:
    def __init__(self, connected: bool, latency: float, error_rate: float, 
                 device_status: Literal['online', 'degraded', 'offline']):
        self.connected = connected
        self.latency = latency
        self.error_rate = error_rate
        self.device_status = device_status

class HealthDashboard:
    async def get_health(self, client) -> HealthStatus:
        try:
            # Ping test
            start = time.time()
            await client.request('api_ping', {})
            latency = (time.time() - start) * 1000  # ms
            
            # Check device status
            status = await client.request('status_get_all', {})
            
            # Check recent errors
            logs_result = await client.request('logs_get', {'limit': 100})
            errors = [log for log in logs_result['logs'] if log.get('level') == 'ERROR']
            error_rate = len(errors) / len(logs) if logs else 0
            
            device_status = 'online'
            if error_rate > 0.1 or latency > 1000:
                device_status = 'degraded'
            
            return HealthStatus(
                connected=True,
                latency=latency,
                error_rate=error_rate,
                device_status=device_status
            )
        except Exception:
            return HealthStatus(
                connected=False,
                latency=-1,
                error_rate=1.0,
                device_status='offline'
            )
```

---

*PX Control API v1.0.0 - © 2025 Pascal Audio*
