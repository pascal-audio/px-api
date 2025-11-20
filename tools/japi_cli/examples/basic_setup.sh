#!/bin/bash
# Basic Device Setup Script
# Configure a device with standard 4-channel analog I/O setup

DEVICE_IP="${1:-192.168.64.100}"
echo "Configuring device at $DEVICE_IP..."

# Set input configuration to analog
echo "Setting input configuration to analog..."
python ../japi_cli.py -t $DEVICE_IP set_input_config analog

# Configure inputs with proper names and gains
echo "Configuring input channels..."
python ../japi_cli.py -t $DEVICE_IP set_input analog/1 -n "Input 1" -g 0.0
python ../japi_cli.py -t $DEVICE_IP set_input analog/2 -n "Input 2" -g 0.0
python ../japi_cli.py -t $DEVICE_IP set_input analog/3 -n "Input 3" -g 0.0
python ../japi_cli.py -t $DEVICE_IP set_input analog/4 -n "Input 4" -g 0.0

# Configure outputs with 1:1 routing
echo "Configuring output channels..."
python ../japi_cli.py -t $DEVICE_IP set_output 1 -n "Output 1" -ps analog/1 -g -3.0
python ../japi_cli.py -t $DEVICE_IP set_output 2 -n "Output 2" -ps analog/2 -g -3.0
python ../japi_cli.py -t $DEVICE_IP set_output 3 -n "Output 3" -ps analog/3 -g -3.0
python ../japi_cli.py -t $DEVICE_IP set_output 4 -n "Output 4" -ps analog/4 -g -3.0

# Reset summing matrix to identity
echo "Resetting summing matrix to identity..."
python ../japi_cli.py -t $DEVICE_IP set_summing_matrix --reset

# Enable basic high-pass filtering on all outputs
echo "Configuring basic EQ (high-pass at 80Hz)..."
for ch in 1 2 3 4; do
    python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $ch 1 -t high_pass12 -f 80 -b false
done

echo "Basic setup complete!"
echo "Verify configuration with: python ../japi_cli.py -t $DEVICE_IP setup_get_all"