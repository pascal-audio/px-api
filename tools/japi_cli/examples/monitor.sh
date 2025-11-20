#!/bin/bash
# Monitor Device Script
# Continuously monitor device metrics and setup changes

DEVICE_IP="${1:-192.168.64.100}"
echo "Monitoring device at $DEVICE_IP..."
echo "Press Ctrl+C to stop"

# Start monitoring in background
echo "Starting setup subscription..."
python ../japi_cli.py -t $DEVICE_IP setup_subscribe &
SETUP_PID=$!

echo "Starting metrics subscription..."
python ../japi_cli.py -t $DEVICE_IP metrics_subscribe &
METRICS_PID=$!

# Wait for user interrupt
trap "echo 'Stopping monitoring...'; kill $SETUP_PID $METRICS_PID 2>/dev/null; exit 0" INT

wait