# JAPI CLI Test Suite

This directory contains comprehensive test suites for the JAPI CLI client.

## Test Files

### `japi_cli_test_discovery.py`
**Purpose**: Auto-discovery tests for all JAPI commands (except backup/restore)

**Features**:
- Automatically discovers available commands from CLI help
- Generates test variations for all parameters
- Excludes `device_backup` and `device_restore` (tested separately)
- Comprehensive parameter validation and edge case testing

**Usage**:
```bash
cd /path/to/japi_cli/test
python3 japi_cli_test_discovery.py --target 192.168.1.100
python3 japi_cli_test_discovery.py --target 192.168.1.100 --verbose
python3 japi_cli_test_discovery.py --target 192.168.1.100 --dry-run
```

### `japi_cli_test_structured.py`
**Purpose**: Structured workflow tests for backup/restore operations

**Features**:
- Tests backup → restore as complete integrated workflow
- Uses temporary files with proper cleanup
- Validates file creation, content, and restoration
- Sequential dependency testing

**Usage**:
```bash
cd /path/to/japi_cli/test
python3 japi_cli_test_structured.py --target 192.168.1.100
python3 japi_cli_test_structured.py --target 192.168.1.100 --verbose
python3 japi_cli_test_structured.py --target 192.168.1.100 --dry-run
```

## Test Organization

### Why Separate Tests?
- **Discovery Test**: Fast, comprehensive testing of individual commands
- **Structured Test**: Slower, workflow-focused testing requiring state management
- **Backup/Restore**: Special handling needed due to file operations and sequencing

### File Structure
```
tools/japi_cli/
├── japi_cli.py                    # Main CLI client
├── japi_cli_base.py              # Base classes and utilities  
├── japi_cli_commands.py          # Command implementations
├── japi_cli_get.py               # GET commands
├── japi_cli_set.py               # SET commands
├── japi_cli_subscribe.py         # SUBSCRIBE commands
└── test/                         # Test directory
    ├── README.md                 # This file
    ├── japi_cli_test_discovery.py   # Auto-discovery tests
    └── japi_cli_test_structured.py  # Workflow tests
```

## Running All Tests

To run the complete test suite:

```bash
# Run discovery tests (most commands)
python3 test/japi_cli_test_discovery.py --target YOUR_DEVICE_IP

# Run structured workflow tests (backup/restore)
python3 test/japi_cli_test_structured.py --target YOUR_DEVICE_IP
```

## Test Options

All tests support these common options:
- `--target, -t`: Target device IP address (required)
- `--port, -p`: Target device port (default: 80)
- `--verbose, -v`: Enable verbose output
- `--dry-run`: Show planned tests without executing

## Development

When adding new commands to the CLI:
1. **Regular commands**: Will be automatically discovered and tested by the discovery test
2. **Workflow commands**: Add specific test cases to the structured test if they require sequencing or special handling