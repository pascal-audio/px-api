# PX API - JSON-RPC Interface

Official API documentation and tooling for Pascal Audio PX series professional audio amplifiers.

## Version 1.0.0

**Release Date:** November 2025  
**API Level:** 1  
**Status:** Stable

## Quick Start

### 1. Install CLI Tool

**Linux/macOS:**
```bash
cd tools/
./install.sh
```

**Windows:**
```cmd
cd tools
install.bat
```

**Manual installation:**
```bash
cd tools/japi_cli
pip install -e .
```

### 2. Run Emulator

**Linux:**
```bash
cd emulators/
chmod +x thrust-linux-x86_64
./thrust-linux-x86_64 --port 8080
```

**Windows:**
```cmd
cd emulators
thrust-windows-x86_64.exe --port 8080
```

**macOS:**
```bash
cd emulators/
chmod +x thrust-macos-arm64
./thrust-macos-arm64 --port 8080
```

### 3. Test Connection

```bash
# Ping the emulator
japi_cli -t localhost -p 8080 api ping

# Get device status info
japi_cli -t localhost -p 8080 status get info

# Set speaker gain
japi_cli -t localhost -p 8080 setup set user-gain 1 -3.0
```

## What's Included

### 📖 Documentation (`docs/`)
- **01-api-reference.md** - Complete JSON-RPC method reference (28 methods)
- **02-configuration-guide.md** - Setup paths and parameter reference
- **03-device-management.md** - Device operations and power management
- **04-preset-guide.md** - Channel preset system
- **05-best-practices.md** - Connection handling, error recovery, security
- **README.md** - Overview and getting started

### 📋 JSON Schemas (`schemas/`)
- 224 JSON Schema files for validation
- `catalog.json` - Schema index with metadata
- TypeScript type generation support
- Python/JavaScript validation examples

### 🖥️ Emulators (`emulators/`)
- Virtual device simulators (no hardware required)
- **Linux x86_64** - Primary platform for CI/CD
- **Windows x86_64** - Cross-compiled
- **macOS ARM64** - Native Apple Silicon build
- Full API compatibility with real devices

### 🛠️ CLI Tool (`tools/`)
- **japi_cli** - Python CLI for device control
- Interactive mode with tab completion
- Batch operations (backup/restore configs)
- Real-time subscriptions (setup/metrics updates)
- Cross-platform (Linux, macOS, Windows)

### 💻 Code Examples (`examples/`)
- **TypeScript** - WebSocket JSON-RPC client (`PXClient`)
  - basic-control.ts - Connection, get/set parameters
  - eq-adjustment.ts - DSP EQ configuration
  - real-time-monitor.ts - Subscriptions and live updates

### 📚 Client Libraries (`clients/`)
- **TypeScript Client** - Auto-generated from schemas
  - Type-safe WebSocket client
  - Full TypeScript definitions
  - JSON-RPC 2.0 support
- **Python Client** - Simple WebSocket client
  - Async/await support
  - Example implementations

### 🔌 AsyncAPI (`asyncapi/`)
- AsyncAPI 3.0 specification (px-api.yaml)
- Message schemas and examples
- WebSocket protocol documentation

## API Overview

### Connection
- **Protocol:** JSON-RPC 2.0 over WebSocket
- **Endpoint:** `ws://{host}:{port}/ws`
- **Default Ports:**
  - Emulator: 8080
  - Hardware: 80

### Key Features
- 28 documented API methods
- Real-time notifications (setup_update, metrics_update)
- 3-layer audio processing (User → Array → Preset)
- 10-band parametric EQ per channel
- FIR filters, crossovers, limiters
- Channel preset save/recall
- Batch configuration operations

### Method Categories
- **API** - Version, ping
- **Device** - Info, reboot, logs, power management
- **Setup** - Get/set configuration (hierarchical paths)
- **Preset** - Channel preset operations
- **Subscription** - Real-time notifications

## Hardware Connection

For physical PX devices:

```bash
# Discover devices on network (mDNS)
japi_cli device discover

# Connect to device
japi_cli -t 192.168.1.100 -p 80 device info

# Interactive mode
japi_cli -t 192.168.1.100 -p 80 -i 
```

## Support

- **Documentation:** See `docs/` directory
- **Issues:** Report bugs or request features
- **API Version:** Check with `japi_cli api version`

## License

**Dual License:**

- **MIT License** - Documentation, schemas, CLI, examples, client libraries  
  Free to use, modify, and distribute

- **Proprietary** - Emulator binaries only  
  Free for development/testing, no redistribution or reverse engineering

See [LICENSE.txt](LICENSE.txt) for complete terms.

© 2025 Pascal Audio. All rights reserved.

## Version Compatibility

| API Version | Firmware Version | Status |
|-------------|------------------|--------|
| 1.0.0 | TBD | Stable |

**Note:** For detailed API status, roadmap, and changelog, see docs/README.md
