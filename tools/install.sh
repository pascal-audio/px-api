#!/bin/bash
# Quick install script for japi_cli
# Supports both uv and pip installation methods

set -e

echo "========================================="
echo "  JAPI CLI Installation Script"
echo "========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

echo "Detected Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "Error: Python 3.9 or higher is required"
    echo "Please upgrade Python and try again"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Navigate to japi_cli directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/japi_cli"

# Check for uv
if command -v uv &> /dev/null; then
    echo "Installing with uv (fast Python package installer)..."
    echo "Running: uv pip install -e ."
    echo ""
    uv pip install -e .
    INSTALL_METHOD="uv"
elif command -v pip3 &> /dev/null; then
    echo "Installing with pip..."
    echo "Running: pip3 install -e ."
    echo ""
    pip3 install -e .
    INSTALL_METHOD="pip3"
elif command -v pip &> /dev/null; then
    echo "Installing with pip..."
    echo "Running: pip install -e ."
    echo ""
    pip install -e .
    INSTALL_METHOD="pip"
else
    echo "Error: Neither uv nor pip found"
    echo ""
    echo "Please install pip or uv first:"
    echo "  - Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  - Or install pip: python3 -m ensurepip --upgrade"
    exit 1
fi

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "Test the installation:"
echo "  japi_cli --help"
echo ""
echo "Connect to an emulator:"
echo "  japi_cli -t localhost -p 8080 api ping"
echo ""
echo "Interactive mode:"
echo "  japi_cli -t localhost -p 8080 -i"
echo ""
echo "Optional: Enable tab completion"
echo "  source setup_completion.sh"
echo ""
echo "Installed with: $INSTALL_METHOD"
echo "========================================="
