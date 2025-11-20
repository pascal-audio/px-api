#!/bin/bash
# Example: Boot diagnostics and performance monitoring
# Shows boot timing metrics and TPM verification status

TARGET="${1:-192.168.64.100}"

echo "=== Boot Diagnostics Example ==="
echo "Target: $TARGET"
echo

# Get boot metrics and verification state
echo "1. Boot timing and verification state:"
python japi_cli.py diagnostics show -n boot -t "$TARGET"
echo

# Check if restart is needed (config mismatch)
echo "2. Check restart requirement:"
python japi_cli.py diagnostics show -n boot -t "$TARGET" | grep -E "(needs_restart|needs_restart_reason)"
echo

# Monitor boot performance
echo "3. Boot performance summary:"
python japi_cli.py diagnostics show -n boot -t "$TARGET" | grep -E "(webserver_ready_ms|config_loaded_ms|hal_initialized_ms|boot_complete_ms)"
echo

echo "=== Boot Diagnostics Complete ==="
