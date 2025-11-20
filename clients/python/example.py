"""Example usage of PX Control API client."""

import asyncio

from py_client import PxClient


async def main():
    """Demonstrate basic client usage."""

    # Create client
    client = PxClient(host="192.168.64.100", port=80)

    try:
        # Connect to device
        print("Connecting to device...")
        await client.connect()
        print("Connected!")

        # Simple request: ping
        print("\n--- API Ping ---")
        result = await client.request("api_ping")
        print(f"Ping result: {result}")

        # Get version info
        print("\n--- API Version ---")
        version = await client.request("api_version")
        print(f"API: {version['api_version']} (level {version['api_level']})")
        print(f"Firmware: {version['firmware_version']}")

        # Get configuration value
        print("\n--- Setup Get ---")
        speaker1 = await client.request("setup_get", {"path": "/audio/output/speaker/1"})
        print(f"Speaker 1 gain: {speaker1['gain']} dB")
        print(f"Speaker 1 mute: {speaker1['mute']}")

        # Set a value
        print("\n--- Setup Set ---")
        await client.request("setup_set_value", {"path": "/audio/output/speaker/1", "property": "gain", "value": -3.0})
        print("Set speaker 1 gain to -3.0 dB")

        # Subscribe to configuration changes
        print("\n--- Subscribe to Changes ---")

        def on_setup_change(params):
            print(f"[NOTIFICATION] {params['path']} = {params['value']}")

        sub_id = await client.subscribe("setup_subscribe", {"path": "/audio/output/speaker/1"}, on_setup_change)
        print(f"Subscribed with ID: {sub_id}")

        # Make a change to trigger notification
        print("\n--- Trigger Notification ---")
        await client.request("setup_set_value", {"path": "/audio/output/speaker/1", "property": "mute", "value": True})

        # Wait to receive notification
        await asyncio.sleep(1)

        # Unsubscribe
        print("\n--- Unsubscribe ---")
        await client.unsubscribe("setup_unsubscribe", sub_id)
        print("Unsubscribed")

        # Get device logs
        print("\n--- Device Logs ---")
        logs = await client.request("logs_get", {"limit": 5})
        print(f"Retrieved {len(logs)} log entries:")
        for log in logs[:3]:
            print(f"  [{log['level']}] {log['message']}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Disconnect
        print("\n--- Disconnect ---")
        await client.disconnect()
        print("Disconnected")


async def subscription_example():
    """Example: Monitor real-time metrics."""

    async with PxClient(host="192.168.64.100", port=80) as client:
        print("Connected via context manager")

        # Subscribe to metrics
        def on_metrics(params):
            metrics = params.get("metrics", {})
            for path, value in metrics.items():
                if "level" in path:
                    print(f"Level: {value:.1f} dBFS")

        sub_id = await client.subscribe("metrics_subscribe", {"freq": 10}, on_metrics)

        print("Monitoring metrics for 5 seconds...")
        await asyncio.sleep(5)

        await client.unsubscribe("metrics_unsubscribe", sub_id)
        print("Stopped monitoring")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())

    # Uncomment to run subscription example
    # asyncio.run(subscription_example())
