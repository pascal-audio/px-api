/**
 * Base TypeScript WebSocket Client for Thorium Firmware JSON-RPC API
 * 
 * Auto-generated from Rust handlers - DO NOT EDIT MANUALLY
 * 
 * Features:
 * - Type-safe method calls with Typebox validation
 * - WebSocket connection management with auto-reconnect
 * - Batch request support
 * - Promise-based async API
 * - Domain-organized client classes
 * - Path-aware setup methods with type safety
 */

import * as Types from './schemas.typebox';
import type { ValidPath, PathTypeMap, PathPatchMap } from './path-types';

// ============================================================================
// Core Types
// ============================================================================

export interface JrpcRequest {
  jsonrpc: '2.0';
  method: string;
  params: unknown;
  id: number;
}

export interface JrpcResponse<T = unknown> {
  jsonrpc: '2.0';
  id: number;
  result?: T;
  error?: JrpcError;
}

export interface JrpcError {
  code: number;
  message: string;
  data?: unknown;
}

export interface JrpcNotification {
  jsonrpc: '2.0';
  method: string;
  params: unknown;
}

export type WebSocketState = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface ClientOptions {
  url: string;
  reconnect?: boolean;
  reconnectDelay?: number;
  timeout?: number;
}

// ============================================================================
// WebSocket Client Base
// ============================================================================

export class JrpcWebSocketClient {
  private ws: WebSocket | null = null;
  private requestId = 0;
  private pendingRequests = new Map<number, { resolve: (value: unknown) => void; reject: (error: Error) => void }>();
  private state: WebSocketState = 'disconnected';
  private options: Required<ClientOptions>;
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor(options: ClientOptions) {
    this.options = {
      reconnect: true,
      reconnectDelay: 3000,
      timeout: 30000,
      ...options,
    };
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    return new Promise((resolve, reject) => {
      this.state = 'connecting';
      this.ws = new WebSocket(this.options.url);

      this.ws.onopen = () => {
        this.state = 'connected';
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
        resolve();
      };

      this.ws.onerror = (error) => {
        this.state = 'error';
        reject(new Error(`WebSocket error: ${error}`));
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onclose = () => {
        this.state = 'disconnected';
        this.handleDisconnect();
      };
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.state = 'disconnected';
    
    // Reject all pending requests
    for (const { reject } of Array.from(this.pendingRequests.values())) {
      reject(new Error('Connection closed'));
    }
    this.pendingRequests.clear();
  }

  /**
   * Get current connection state
   */
  getState(): WebSocketState {
    return this.state;
  }

  /**
   * Send JSON-RPC request
   */
  public async request<T = unknown>(method: string, params: unknown): Promise<T> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect();
    }

    const id = ++this.requestId;
    const request: JrpcRequest = {
      jsonrpc: '2.0',
      method,
      params,
      id,
    };

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, this.options.timeout);

      this.pendingRequests.set(id, {
        resolve: (value) => {
          clearTimeout(timeoutId);
          resolve(value as T);
        },
        reject: (error) => {
          clearTimeout(timeoutId);
          reject(error);
        },
      });

      this.ws!.send(JSON.stringify(request));
    });
  }

  /**
   * Send batch request (multiple methods in one call)
   */
  async batch(requests: Array<{ method: string; params: unknown }>): Promise<unknown[]> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect();
    }

    const batchRequests = requests.map((req) => ({
      jsonrpc: '2.0' as const,
      method: req.method,
      params: req.params,
      id: ++this.requestId,
    }));

    const promises = batchRequests.map((req) => {
      return new Promise((resolve, reject) => {
        this.pendingRequests.set(req.id, { resolve, reject });
      });
    });

    this.ws.send(JSON.stringify(batchRequests));

    return Promise.all(promises);
  }

  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);

      // Handle batch response
      if (Array.isArray(message)) {
        for (const item of message) {
          this.handleSingleMessage(item);
        }
        return;
      }

      this.handleSingleMessage(message);
    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }

  private handleSingleMessage(message: JrpcResponse | JrpcNotification): void {
    // Check if it's a notification (no id)
    if (!('id' in message)) {
      // Handle notification (e.g., setup_update, metrics_update)
      // Subclasses can override this
      return;
    }

    const pending = this.pendingRequests.get(message.id);
    if (!pending) {
      console.warn('Received response for unknown request:', message.id);
      return;
    }

    this.pendingRequests.delete(message.id);

    if (message.error) {
      pending.reject(new Error(`${message.error.message} (code: ${message.error.code})`));
    } else {
      pending.resolve(message.result);
    }
  }

  private handleDisconnect(): void {
    if (this.options.reconnect && this.state !== 'error') {
      this.reconnectTimer = setTimeout(() => {
        console.log('Attempting to reconnect...');
        this.connect().catch((error) => {
          console.error('Reconnection failed:', error);
        });
      }, this.options.reconnectDelay);
    }
  }
}


// ============================================================================
// Domain-Specific Clients
// ============================================================================

/**
 * ApiClient - API domain methods
 * 
 * Generated from Rust handlers
 */
export class ApiClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * checkVersion - Check client version compatibility.

Validates whether the client version is compatible with the server API.
Supports N-1 major version compatibility (current and previous major version).

# Parameters
* `params.client_version` - Client version string (e.g., "1.0.0")

# Returns
`ApiCheckVersionResponse` with compatibility status and warnings

# Errors
This method does not return errors under normal operation.
   * @param client_version - required, type: string
   */
  async checkVersion(client_version: string): Promise<Types.ApiCheckVersionResponse> {
    return this.client.request<Types.ApiCheckVersionResponse>('api_check_version', { client_version });
  }
  
  /**
   * ping - Ping the API.

Simple connectivity test that returns "pong".

# Parameters
None

# Returns
String "pong"

# Errors
This method does not return errors under normal operation.
   */
  async ping(): Promise<Types.ApiPingResponse> {
    return this.client.request<Types.ApiPingResponse>('api_ping', {});
  }
  
  /**
   * version - Get API version information.

Returns current JAPI version, API level, and firmware version.

# Parameters
None

# Returns
`ApiVersionResponse` with version details

# Errors
This method does not return errors under normal operation.
   */
  async version(): Promise<Types.ApiVersionResponse> {
    return this.client.request<Types.ApiVersionResponse>('api_version', {});
  }
  
}

/**
 * BackupClient - BACKUP domain methods
 * 
 * Generated from Rust handlers
 */
export class BackupClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * create - Create device backup
   */
  async create(): Promise<Types.DeviceBackupResponse> {
    return this.client.request<Types.DeviceBackupResponse>('backup_create', {});
  }
  
  /**
   * restore - Restore device from backup
   * @param config - required, type: string
   * @param preserve_network_settings - optional, type: boolean
   */
  async restore(config: string, preserve_network_settings?: boolean): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('backup_restore', { config, preserve_network_settings });
  }
  
}

/**
 * DeviceClient - DEVICE domain methods
 * 
 * Generated from Rust handlers
 */
export class DeviceClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * findMe - Make device identify itself (find me)
   * @param timeout - optional, type: Types.FindMeTimeout
   */
  async findMe(timeout?: Types.FindMeTimeout): Promise<Types.DeviceFindMeResponse> {
    return this.client.request<Types.DeviceFindMeResponse>('device_find_me', { timeout });
  }
  
  /**
   * getTime - Get system time in UTC RFC 3339 format
   */
  async getTime(): Promise<Types.SystemTimeResponse> {
    return this.client.request<Types.SystemTimeResponse>('device_get_time', {});
  }
  
  /**
   * powerOff - Power off the device
   */
  async powerOff(): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('device_power_off', {});
  }
  
  /**
   * powerOn - Power on the device
   */
  async powerOn(): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('device_power_on', {});
  }
  
  /**
   * reboot - Reboot the device
   */
  async reboot(): Promise<Types.JapiSuccessResponse> {
    return this.client.request<Types.JapiSuccessResponse>('device_reboot', {});
  }
  
  /**
   * reset - Factory reset the device
   * @param preserve_network - optional, type: boolean
   */
  async reset(preserve_network?: boolean): Promise<Types.DeviceResetResponse> {
    return this.client.request<Types.DeviceResetResponse>('device_reset', { preserve_network });
  }
  
  /**
   * setTime - Set system time from UTC RFC 3339 format
   * @param time - required, type: Types.Rfc3339Timestamp
   */
  async setTime(time: Types.Rfc3339Timestamp): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('device_set_time', { time });
  }
  
}

/**
 * DiagnosticsClient - DIAGNOSTICS domain methods
 * 
 * Generated from Rust handlers
 */
export class DiagnosticsClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * get - diagnostics_get
   * @param namespace - optional, type: string
   */
  async get(namespace?: string): Promise<unknown> {
    return this.client.request<unknown>('diagnostics_get', { namespace });
  }
  
}

/**
 * LogsClient - LOGS domain methods
 * 
 * Generated from Rust handlers
 */
export class LogsClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * get - Get device logs with optional limit and offset (default: 100 most recent entries, offset 0)
Logs are returned newest first. Use offset for paging.
   * @param limit - optional, type: number
   * @param offset - optional, type: number
   */
  async get(limit?: number, offset?: number): Promise<Types.DeviceGetLogsResponse> {
    return this.client.request<Types.DeviceGetLogsResponse>('logs_get', { limit, offset });
  }
  
  /**
   * setLevel - Set log level filter
   * @param filter - required, type: Types.LogLevel
   */
  async setLevel(filter: Types.LogLevel): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('logs_set_level', { filter });
  }
  
}

/**
 * MetricsClient - METRICS domain methods
 * 
 * Generated from Rust handlers
 */
export class MetricsClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * subscribe - Subscribe to metrics updates.

Creates a subscription for real-time metrics data (audio levels, temperatures, etc.).

# Parameters
* `params.path` - Optional path filter (None = all metrics)
* `params.freq` - Optional update frequency in Hz (default: system default)

# Returns
Subscription response with subscription_id

# Errors
* `INVALID_VALUE` - Invalid frequency value (out of supported range)
   * @param freq - optional, type: number
   * @param path - optional, type: string
   */
  async subscribe(freq?: number, path?: string): Promise<Types.JapiSubscribeResponse> {
    return this.client.request<Types.JapiSubscribeResponse>('metrics_subscribe', { freq, path });
  }
  
  /**
   * unsubscribe - Unsubscribe from metrics updates.

Cancels an active metrics subscription.

# Parameters
* `params.subscription_id` - Subscription identifier to cancel

# Returns
Null value confirming cancellation

# Errors
This method does not return errors under normal operation.
   * @param subscription_id - optional, type: string
   */
  async unsubscribe(subscription_id?: string): Promise<Types.JapiSuccessResponse> {
    return this.client.request<Types.JapiSuccessResponse>('metrics_unsubscribe', { subscription_id });
  }
  
}

/**
 * PresetClient - PRESET domain methods
 * 
 * Generated from Rust handlers
 */
export class PresetClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * apply - Apply a speaker preset to a channel

Accepts presets in two formats:
1. **JSON object** - Plain `ChannelPreset` structure with all processing parameters
2. **Base64 string** - Encoded binary preset (encrypted vendor-locked or plain CBOR)

The method automatically detects the format, deserializes the preset, and applies
all processing parameters to the specified channel. Encrypted presets are decrypted
transparently if the device has the vendor key.

# Parameters
* `params.channel` - Speaker channel (1-4)
* `params.preset` - Preset data (JSON object or base64 string)

# Returns
Success response with applied preset name:
```json
{
"success": true,
"message": "Preset applied to channel 1",
"preset_name": "Stadium Mode"
}
```

# Errors
* `INVALID_CHANNEL` - Channel index out of range (not 1-4)
* `INVALID_VALUE` - Preset format invalid (not JSON object or base64 string)
* `PRESET_INVALID` - Preset data corrupted or malformed
* `PRESET_LOCKED` - Encrypted preset decryption failed (wrong vendor key)
* `DEVICE_BUSY` - Device service unavailable or factory config verification in progress
* `PERMISSION_DENIED` - Write operations blocked (verification failed or restart needed)
* `HARDWARE_ERROR` - Failed to apply preset to hardware

# Notes
Applying a preset emits granular `setup_update` notifications for all affected
fields (crossover, EQ, limiters, etc.) so clients can track individual changes.
   * @param channel - required, type: number
   * @param preset - required, type: unknown
   */
  async apply(channel: number, preset: unknown): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('preset_apply', { channel, preset });
  }
  
  /**
   * clear - Clear the applied preset for a channel

Removes the current preset and restores factory default processing configuration.
This resets all preset layer parameters (crossover, EQ, limiters, etc.) to their
default values while preserving user and array layer settings.

# Parameters
* `params.channel` - Speaker channel (1-4)

# Returns
Success confirmation:
```json
{
"success": true,
"message": "Preset cleared on channel 1"
}
```

# Errors
* `INVALID_CHANNEL` - Channel index out of range (not 1-4)
* `DEVICE_BUSY` - Device service unavailable
* `HARDWARE_ERROR` - Failed to apply default configuration to hardware

# Notes
Clearing emits `setup_update` notifications for all affected preset layer fields.
   * @param channel - required, type: number
   */
  async clear(channel: number): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('preset_clear', { channel });
  }
  
  /**
   * create - Create a preset from the current channel configuration

Captures the current processing configuration from a speaker channel and creates
a portable preset that can be applied to other channels or devices. The preset
includes all preset layer parameters: drive mode, polarity, delay, crossover,
EQ (15 bands), FIR filter, and all limiters.

# Parameters
* `params.channel` - Speaker channel (1-4) to capture configuration from
* `params.name` - Human-readable preset name (e.g., "Stadium Mode")
* `params.version` - Version string (e.g., "1.0", "2.3.1")
* `params.created_date` - Creation timestamp in RFC3339 format
* `params.vendor_lock` - If true, encrypts preset with device vendor key

# Returns
**Plain JSON preset** (vendor_lock=false):
```json
{
"success": true,
"preset_type": "json",
"preset": { /* ChannelPreset structure */ },
"metadata": { /* ChannelPresetMetadata */ }
}
```

**Encrypted binary preset** (vendor_lock=true):
```json
{
"success": true,
"preset_type": "binary",
"preset": "base64EncodedCBOR...",
"metadata": { /* ChannelPresetMetadata with vendor_lock */ }
}
```

# Errors
* `INVALID_CHANNEL` - Channel index out of range
* `HARDWARE_ERROR` - Failed to serialize preset to CBOR or encrypt

# Notes
- FIR filter taps are captured for the current sample rate only
- Vendor-locked presets cannot be modified after creation
- Each preset gets a unique UUID identifier
   * @param channel - required, type: number
   * @param created_date - required, type: Types.Rfc3339Date
   * @param name - required, type: string
   * @param vendor_lock - optional, type: boolean
   * @param version - required, type: string
   */
  async create(channel: number, created_date: Types.Rfc3339Date, name: string, version: string, vendor_lock?: boolean): Promise<Types.PresetCreateResponse> {
    return this.client.request<Types.PresetCreateResponse>('preset_create', { channel, created_date, name, vendor_lock, version });
  }
  
  /**
   * show - Show preset information for a channel

Returns metadata about the currently applied preset, including whether it has
been customized (modified after application). If no preset is applied, returns null.

# Parameters
* `params.channel` - Speaker channel (1-4)

# Returns
**When preset is applied:**
```json
{
"id": "550e8400-e29b-41d4-a716-446655440000",
"name": "Stadium Mode",
"version": "1.0",
"created_date": "2024-01-15T10:30:00Z",
"is_locked": false,
"is_customized": true
}
```

**When no preset is applied:**
```json
null
```

# Errors
* `INVALID_CHANNEL` - Channel index out of range (not 1-4)
* `HARDWARE_ERROR` - Internal error reading preset information

# Notes
- `is_locked`: true if preset is vendor-locked (encrypted)
- `is_customized`: true if user modified any preset parameters after application
   * @param channel - required, type: number
   */
  async show(channel: number): Promise<Types.Option < ChannelPresetMetadataView >> {
    return this.client.request<Types.Option < ChannelPresetMetadataView >>('preset_show', { channel });
  }
  
}

/**
 * SetupClient - Path-aware setup configuration methods
 * 
 * This class provides type-safe setup_get and setup_set methods
 * that understand the path structure and return proper types.
 */
export class SetupClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * get - Type-safe setup path getter
   * 
   * @param path - Valid configuration path
   * @returns Typed value for the given path
   * 
   * @example
   * const gain = await setup.get('/audio/output/speaker/1/gain');
   * const eq = await setup.get('/audio/output/speaker/1/user/eq');
   */
  async get<P extends ValidPath>(path: P): Promise<PathTypeMap[P]> {
    return this.client.request<PathTypeMap[P]>('setup_get', { path });
  }
  
  /**
   * set - Type-safe setup path setter
   * 
   * @param path - Valid configuration path
   * @param value - Patch object for the path
   * @returns Updated value
   * 
   * @example
   * await setup.set('/audio/output/speaker/1/gain', { gain: -6.0 });
   * await setup.set('/audio/output/speaker/1/user/eq', { enabled: true });
   */
  async set<P extends keyof PathPatchMap>(
    path: P,
    value: PathPatchMap[P]
  ): Promise<PathTypeMap[P]> {
    return this.client.request<PathTypeMap[P]>('setup_set', { path, value });
  }
  
  /**
   * getAll - Get all setup configuration
   * 
   * @param flatten - Return flattened key-value pairs instead of nested structure
   * @returns Complete device setup
   */
  async getAll(flatten?: boolean): Promise<unknown> {
    return this.client.request<unknown>('setup_get_all', { flatten });
  }
  
  /**
   * getValue - Get setup value by JSON path (legacy)
   * 
   * @param json_path - JSON path to value
   * @returns Value at path
   */
  async getValue(json_path: string): Promise<unknown> {
    return this.client.request<unknown>('setup_get_value', { json_path });
  }
  
  /**
   * setValue - Set setup value by JSON path (legacy)
   * 
   * @param json_path - JSON path to value
   * @param value - New value
   * @returns Updated value
   */
  async setValue(json_path: string, value: unknown): Promise<unknown> {
    return this.client.request<unknown>('setup_set_value', { json_path, value });
  }
  
  /**
   * subscribe - Subscribe to setup change notifications
   * 
   * @param topic - Notification topic (default: "setup_update")
   * @returns Subscription confirmation
   */
  async subscribe(topic?: string): Promise<Types.JapiSubscribeResponse> {
    return this.client.request<Types.JapiSubscribeResponse>('setup_subscribe', { topic });
  }
  
  /**
   * unsubscribe - Unsubscribe from setup notifications
   * 
   * @param topic - Notification topic (default: "setup_update")
   * @returns Success response
   */
  async unsubscribe(topic?: string): Promise<Types.JapiSuccessResponse> {
    return this.client.request<Types.JapiSuccessResponse>('setup_unsubscribe', { topic });
  }
  
  /**
   * batchSet - Set multiple setup paths in a single batch request
   * 
   * @param operations - Array of {path, value} operations
   * @returns Array of typed results for each operation
   * 
   * @example
   * const results = await setup.batchSet([
   *   { path: '/audio/output/speaker/1/gain', value: { gain: -6.0 } },
   *   { path: '/audio/output/speaker/2/gain', value: { gain: -3.0 } },
   *   { path: '/audio/output/speaker/1/user/eq', value: { enabled: true } }
   * ]);
   */
  async batchSet<P extends keyof PathPatchMap>(
    operations: Array<{ path: P; value: PathPatchMap[P] }>
  ): Promise<Array<PathTypeMap[P]>> {
    const requests = operations.map(op => ({
      method: 'setup_set',
      params: { path: op.path, value: op.value }
    }));
    return this.client.batch(requests) as Promise<Array<PathTypeMap[P]>>;
  }
  
  /**
   * batchGet - Get multiple setup paths in a single batch request
   * 
   * @param paths - Array of paths to retrieve
   * @returns Array of typed values for each path
   * 
   * @example
   * const [gain1, gain2, eq] = await setup.batchGet([
   *   '/audio/output/speaker/1/gain',
   *   '/audio/output/speaker/2/gain',
   *   '/audio/output/speaker/1/user/eq'
   * ]);
   */
  async batchGet<P extends ValidPath>(paths: P[]): Promise<Array<PathTypeMap[P]>> {
    const requests = paths.map(path => ({
      method: 'setup_get',
      params: { path }
    }));
    return this.client.batch(requests) as Promise<Array<PathTypeMap[P]>>;
  }
  
}

/**
 * StatusClient - Path-aware status query methods
 * 
 * This class provides type-safe status_get method that understands
 * the path structure (similar to SetupClient but read-only).
 */
export class StatusClient {
  constructor(private client: JrpcWebSocketClient) {}
  
  /**
   * get - Type-safe status path getter (read-only)
   * 
   * @param path - Valid configuration path (optional, returns subtree if provided)
   * @returns Current runtime status for the given path
   * 
   * @example
   * const speakerStatus = await status.get('/audio/output/speaker/1');
   * const allStatus = await status.get();
   */
  async get<P extends ValidPath>(path?: P): Promise<P extends ValidPath ? PathTypeMap[P] : unknown> {
    return this.client.request('status_get', { path });
  }
  
  /**
   * getAll - Get complete device status
   * 
   * @returns Complete runtime status of all subsystems
   */
  async getAll(): Promise<Types.DeviceState> {
    return this.client.request<Types.DeviceState>('status_get_all', {});
  }
  
  /**
   * subscribe - Subscribe to status change notifications
   * 
   * @param topic - Notification topic (default: "status_update")
   * @returns Subscription confirmation
   */
  async subscribe(topic?: string): Promise<Types.JapiSubscribeResponse> {
    return this.client.request<Types.JapiSubscribeResponse>('status_subscribe', { topic });
  }
  
  /**
   * unsubscribe - Unsubscribe from status notifications
   * 
   * @param topic - Notification topic (default: "status_update")
   * @returns Success response
   */
  async unsubscribe(topic?: string): Promise<Types.StatusResponse> {
    return this.client.request<Types.StatusResponse>('status_unsubscribe', { topic });
  }
  
}

// ============================================================================
// Main Client
// ============================================================================

/**
 * PxClient - Main client with all domain methods
 */
export class PxClient extends JrpcWebSocketClient {
  public readonly api: ApiClient;
  public readonly device: DeviceClient;
  public readonly setup: SetupClient;
  public readonly preset: PresetClient;
  public readonly metrics: MetricsClient;
  public readonly status: StatusClient;
  public readonly backup: BackupClient;
  public readonly logs: LogsClient;
  public readonly diagnostics: DiagnosticsClient;
  
  constructor(options: ClientOptions) {
    super(options);
    this.api = new ApiClient(this);
    this.device = new DeviceClient(this);
    this.setup = new SetupClient(this);
    this.preset = new PresetClient(this);
    this.metrics = new MetricsClient(this);
    this.status = new StatusClient(this);
    this.backup = new BackupClient(this);
    this.logs = new LogsClient(this);
    this.diagnostics = new DiagnosticsClient(this);
  }
}
