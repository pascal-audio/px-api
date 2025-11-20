#!/usr/bin/env python3
"""
Quick test script for interactive mode.
Run this to test if the interactive module loads correctly.
"""

import sys

sys.path.insert(0, ".")

from groups.api import ApiGroup
from groups.backup import BackupGroup
from groups.device import DeviceGroup
from groups.diagnostics import DiagnosticsGroup
from groups.logs import LogsGroup
from groups.metrics import MetricsGroup
from groups.preset import PresetGroup
from groups.setup import SetupGroup
from groups.status import StatusGroup
from japi_cli_base import CommandRegistry

# Register command groups (all 9 groups)
CommandRegistry.register_group(ApiGroup)
CommandRegistry.register_group(BackupGroup)
CommandRegistry.register_group(DeviceGroup)
CommandRegistry.register_group(DiagnosticsGroup)
CommandRegistry.register_group(LogsGroup)
CommandRegistry.register_group(MetricsGroup)
CommandRegistry.register_group(PresetGroup)
CommandRegistry.register_group(SetupGroup)
CommandRegistry.register_group(StatusGroup)

print(f"✓ Registered {len(CommandRegistry.groups)} command groups")
print("\nCommand groups:")
for group in CommandRegistry.groups:
    print(f"  - {group.name}: {group.description}")

print("\n✓ Command registration works!")

# Test interactive module import
try:
    import japi_cli_interactive

    print("✓ Interactive module imports successfully!")

    # Check if prompt_toolkit is available
    if japi_cli_interactive.PROMPT_TOOLKIT_AVAILABLE:
        from japi_cli_interactive import JapiCliCompleter

        # Test completer - need to build parser first
        parser = CommandRegistry.build_parser()
        completer = JapiCliCompleter(parser)
        print(f"✓ Completer created with {len(completer.command_tree)} top-level commands")

        print("\n✓ All tests passed! Interactive mode with tab completion should work.")
    else:
        print("⚠ prompt_toolkit not installed - interactive mode will use basic input")
        print("  Install with: pip install prompt-toolkit")

    print("\nTo start interactive mode, run:")
    print("  python japi_cli.py -i")

except ImportError as e:
    print(f"✗ Failed to import interactive module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error testing interactive mode: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
