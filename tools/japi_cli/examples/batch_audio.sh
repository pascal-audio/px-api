#!/bin/bash
# Example: Send all audio values using batch request
# This demonstrates using the batch_set_all_audio command to send
# all current audio endpoint values in a single JSON-RPC batch request

DEVICE_IP="${1:-192.168.1.100}"

echo "Sending all audio values to device at $DEVICE_IP using batch request..."
echo "This includes:"
echo "  - Audio inputs (analog, digital, network)"
echo "  - Input configuration and generator"
echo "  - Audio outputs (speaker, digital, network)"
echo "  - Summing matrix"
echo "  - User processing (gain, delay, mute, HPF, EQ)"
echo "  - Array processing (gain, delay, polarity, EQ, FIR)"
echo "  - Preset processing (crossover, EQ, FIR, limiters)"
echo ""
echo "Note: Excludes only device settings (network, power, GPIO, etc.)"
echo ""

python japi_cli.py -t "$DEVICE_IP" batch_set_all_audio -v

echo ""
echo "Batch operation complete!"
