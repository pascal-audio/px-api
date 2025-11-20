# PX API JSON Schemas

JSON Schema definitions for all PX API types - request parameters, responses, and configuration structures.

## Overview

- **Total Schemas:** 225+ JSON Schema files  
- **Standard:** JSON Schema Draft-07  
- **Generated From:** Rust type definitions using `schemars`

## Directory Structure

```
schemas/
├── catalog.json              # Index of all schemas with metadata
├── japi_path_registry.json   # Setup path tree structure (32 paths)
├── types/                    # Request/response types and enums (79 schemas)
├── definitions/              # Core configuration types (124 schemas)
├── status/                   # Device status and state types (12 schemas)
├── changes/                  # Setup change notification types (2 schemas)
└── views/                    # Response wrapper types (8 schemas)
```

## Schema Categories

### types/
Request parameters, response types, and enums:
- `DeviceSetup.json`, `AudioSetup.json` - Configuration structures
- `EqualizerBand.json`, `Crossover.json` - DSP component types
- `DeviceInfoResponse.json` - RPC response formats
- `EqualizerType.json`, `CrossoverType.json` - Enum definitions

### definitions/
Core type definitions referenced by other schemas:
- Configuration base types
- Nested component structures
- Shared data models

### status/
Device status and monitoring:
- `DeviceStatus.json` - Overall device state
- `NetworkStatus.json` - Network interface status
- `AudioStatus.json` - Audio sync status
- `FirmwareVersions.json` - Firmware component versions

### changes/
Setup change notification payloads:
- `SetupChange.json` - Individual change events
- `SetupChanged.json` - Batch change notifications

### views/
Response wrapper types for flattened API responses:
- `DeviceSetupView.json` - Simplified setup views
- `PresetProcessingView.json` - Preset read-only views

## Quick Start

### Validation (Python)

```python
import json
from jsonschema import validate

# Load schema
with open('schemas/types/ApiPingResponse.json') as f:
    schema = json.load(f)

# Validate response
response = {"pong": "hello", "timestamp": 1234567890}
validate(instance=response, schema=schema)
```

### Validation (JavaScript/Node.js)

```javascript
import Ajv from 'ajv';
import fs from 'fs';

const ajv = new Ajv();

// Load and compile schema
const schema = JSON.parse(fs.readFileSync('schemas/types/ApiPingResponse.json'));
const validate = ajv.compile(schema);

// Validate response
const valid = validate({pong: "hello", timestamp: 1234567890});
if (!valid) console.log(validate.errors);
```

### TypeScript Type Generation

```bash
# Using json-schema-to-typescript
npx json-schema-to-typescript schemas/types/DeviceSetup.json > DeviceSetup.d.ts

# Or generate all types
find schemas/types -name "*.json" -exec npx json-schema-to-typescript {} \;
```

## Schema References

Schemas use `$ref` for composition:

```json
{
  "type": "object",
  "properties": {
    "audio": {
      "$ref": "../definitions/AudioSetup.json"
    }
  }
}
```

When resolving references:
- Paths are relative to the schema file location
- Use a schema resolver library (Ajv handles this automatically)
- See `catalog.json` for the full schema dependency graph

## Catalog and Registry

### catalog.json
Complete index of all schemas with metadata:
- Schema paths and categories
- Description and version info
- Dependency relationships

### japi_path_registry.json
Maps JSON-RPC API paths to schema types:
```json
{
  "/audio/output/speaker/{channel}/gain": {
    "type": "number",
    "format": "f32",
    "description": "Output gain in dB",
    "range": {"min": -60.0, "max": 12.0}
  }
}
```

Use this for:
- Path validation in client libraries
- Auto-generating path constants
- Understanding parameter constraints

## AsyncAPI Integration

These schemas are referenced in the AsyncAPI specification (`asyncapi/px-api.yaml`):
- Request/response payloads for each JSON-RPC method
- Notification payloads for subscriptions
- Error response structures

The AsyncAPI spec uses a filtered subset of schemas (55 schemas) relevant to the API surface.

## Notes

- **Recursive Types:** Some schemas have recursive references (e.g., `SetupChangedType`) that may need special handling in validation libraries
- **Vendor Types:** Encrypted preset formats and hardware-specific types are not included
- **Updates:** Regenerate schemas after Rust type changes using the build system

## See Also

- [AsyncAPI Specification](../asyncapi/px-api.yaml) - Complete API documentation
- [API Reference](../docs/01-api-reference.md) - Method documentation with examples
- [Configuration Guide](../docs/02-configuration-guide.md) - Setup path structure
