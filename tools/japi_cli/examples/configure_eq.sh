#!/bin/bash
# EQ Configuration Script
# Configure output EQ with common room correction curve

DEVICE_IP="${1:-192.168.64.100}"
CHANNEL="${2:-1}"

echo "Configuring EQ for output channel $CHANNEL on device $DEVICE_IP..."

# Enable output EQ
python ../japi_cli.py -t $DEVICE_IP set_output_eq $CHANNEL -b false

# Configure EQ bands for typical room correction
echo "Setting up room correction EQ curve..."

# Band 1: High-pass at 80Hz
python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $CHANNEL 1 -t high_pass12 -f 80 -b false

# Band 2: Low-mid cut at 200Hz
python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $CHANNEL 2 -t parametric -f 200 -g -2.0 -q 1.0 -b false

# Band 3: Mid boost at 1kHz
python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $CHANNEL 3 -t parametric -f 1000 -g 1.5 -q 0.7 -b false

# Band 4: Presence boost at 3kHz
python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $CHANNEL 4 -t parametric -f 3000 -g 2.0 -q 1.4 -b false

# Band 5: High-frequency notch at 8kHz
python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $CHANNEL 5 -t parametric -f 8000 -g -3.0 -q 2.0 -b false

# Band 6: High-shelf at 10kHz
python ../japi_cli.py -t $DEVICE_IP set_output_eq_band $CHANNEL 6 -t high_shelf -f 10000 -g -1.0 -q 0.7 -b false

echo "EQ configuration complete for channel $CHANNEL"
echo "Current EQ settings:"
python ../japi_cli.py -t $DEVICE_IP get_output_eq $CHANNEL