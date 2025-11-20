#!/bin/bash
# Example: Using JAPI CLI Interactive Mode
# This shows various ways to start and use interactive mode

echo "=== JAPI CLI Interactive Mode Examples ==="
echo

# Example 1: Basic interactive mode
echo "Example 1: Basic interactive mode with default target"
echo "  python japi_cli.py -i"
echo

# Example 2: Interactive mode with custom target
echo "Example 2: With custom target"
echo "  python japi_cli.py -t 192.168.1.100 -i"
echo

# Example 3: Interactive mode with verbose output
echo "Example 3: With verbose output enabled"
echo "  python japi_cli.py -t 192.168.1.100 -v -i"
echo

echo "=== Interactive Session Example ==="
cat << 'EOF'

Once started, you can issue commands like:

    japi [192.168.64.100:80] > help
    # Shows all available commands

    japi [192.168.64.100:80] > get_speaker 1
    # Get speaker channel 1 configuration

    japi [192.168.64.100:80] > set_input analog/1 -g -3.0
    # Set input gain

    japi [192.168.64.100:80] > target 192.168.1.200
    # Switch to different device

    japi [192.168.1.200:80] > get_install_info
    # Query new device

    japi [192.168.1.200:80] > exit
    # Exit interactive mode

EOF

echo
echo "=== Tips ==="
echo "  - Press TAB for command completion"
echo "  - Use Up/Down arrows for command history"
echo "  - Press Ctrl+C to cancel input"
echo "  - Press Ctrl+D or type 'exit' to quit"
echo "  - Type 'help' to see all commands"
echo "  - Type 'clear' to clear the screen"
echo
