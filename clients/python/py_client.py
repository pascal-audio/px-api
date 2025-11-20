"""Minimal Python client for PX Control API (JSON-RPC over WebSocket)."""

import asyncio
import json
from typing import Any, Callable, Optional

import websockets
from websockets.client import WebSocketClientProtocol


class PxClient:
    """WebSocket client for PX Control API with JSON-RPC support."""

    def __init__(self, host: str = "192.168.64.100", port: int = 80):
        """Initialize client with target host and port.

        Args:
            host: Device IP address
            port: WebSocket port (default: 80)
        """
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}/ws"
        self.ws: Optional[WebSocketClientProtocol] = None
        self._request_id = 0
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._subscriptions: dict[str, Callable[[dict], None]] = {}
        self._receive_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Connect to device WebSocket endpoint."""
        self.ws = await websockets.connect(self.url)
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def disconnect(self) -> None:
        """Disconnect from device."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self.ws:
            await self.ws.close()
            self.ws = None

    async def request(self, method: str, params: Optional[dict] = None) -> Any:
        """Send JSON-RPC request and wait for response.

        Args:
            method: JSON-RPC method name (e.g., "setup_get" ...)
            params: Method parameters (default: empty dict)

        Returns:
            Result value from JSON-RPC response

        Raises:
            RuntimeError: If not connected or request fails
            ValueError: If server returns error response
        """
        if not self.ws:
            raise RuntimeError("Not connected - call connect() first")

        self._request_id += 1
        request_id = self._request_id

        request = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": request_id}

        # Create future for response
        future: asyncio.Future = asyncio.Future()
        self._pending_requests[request_id] = future

        # Send request
        await self.ws.send(json.dumps(request))

        # Wait for response
        try:
            return await future
        finally:
            self._pending_requests.pop(request_id, None)

    async def subscribe(
        self, method: str, params: Optional[dict] = None, callback: Optional[Callable[[dict], None]] = None
    ) -> str:
        """Subscribe to notifications.

        Args:
            method: Subscription method (e.g., "setup_subscribe", "metrics_subscribe")
            params: Subscription parameters (e.g., path, freq)
            callback: Handler for notification messages (receives params dict)

        Returns:
            Subscription ID from server

        Example:
            sub_id = await client.subscribe(
                "setup_subscribe",
                {"path": "/audio/output/speaker/1"},
                lambda params: print(f"Changed: {params['path']} = {params['value']}")
            )
        """
        result = await self.request(method, params)

        # Store callback for this subscription
        if callback:
            subscription_id = result.get("subscription_id")
            if subscription_id:
                self._subscriptions[subscription_id] = callback

        return result.get("subscription_id")

    async def unsubscribe(self, method: str, subscription_id: str) -> None:
        """Unsubscribe from notifications.

        Args:
            method: Unsubscribe method (e.g., "setup_unsubscribe", "metrics_unsubscribe")
            subscription_id: Subscription ID from subscribe()
        """
        await self.request(method, {"subscription_id": subscription_id})
        self._subscriptions.pop(subscription_id, None)

    async def _receive_loop(self) -> None:
        """Background task to receive and route WebSocket messages."""
        if not self.ws:
            return

        try:
            async for message in self.ws:
                data = json.loads(message)

                # Response to request
                if "id" in data:
                    request_id = data["id"]
                    future = self._pending_requests.get(request_id)

                    if future and not future.done():
                        if "error" in data:
                            error = data["error"]
                            error_msg = error.get("message", "Unknown error")
                            if "data" in error:
                                error_msg = f"{error_msg}: {error['data'].get('message', '')}"
                            future.set_exception(ValueError(error_msg))
                        else:
                            future.set_result(data.get("result"))

                # Notification (no id field)
                elif "method" in data:
                    params = data.get("params", {})

                    # Route to subscription callbacks
                    for callback in self._subscriptions.values():
                        try:
                            callback(params)
                        except Exception as e:
                            print(f"Error in subscription callback: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Receive loop error: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
