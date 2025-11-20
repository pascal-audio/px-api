import argparse
import asyncio
import itertools
import json
import sys
import time
from typing import Any, NamedTuple

import websockets
from colorama import Fore, Style


class CommandError(Exception):
    """Exception raised when a command fails (error already printed to user)."""

    pass


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


INPUT_CHANNELS = [
    "analog/1",
    "analog/2",
    "analog/3",
    "analog/4",
    "digital/1",
    "digital/2",
    "digital/3",
    "digital/4",
    "network/1",
    "network/2",
    "network/3",
    "network/4",
]


OUTPUT_SRC_CHANNELS = [
    "analog/1",
    "analog/2",
    "analog/3",
    "analog/4",
    "digital/1",
    "digital/2",
    "digital/3",
    "digital/4",
    "network/1",
    "network/2",
    "network/3",
    "network/4",
    "off",
]


NETWORK_SRC_CHANNELS = [
    "off",
    "analog/1",
    "analog/2",
    "analog/3",
    "analog/4",
    "digital/1",
    "digital/2",
    "digital/3",
    "digital/4",
    "speaker/1",
    "speaker/2",
    "speaker/3",
    "speaker/4",
]


EQ_FILTER_TYPES = [
    "parametric",
    "low_pass6",
    "low_pass12",
    "high_pass6",
    "high_pass12",
    "low_shelf",
    "low_shelf_q",
    "low_shelf6",
    "low_shelf12",
    "high_shelf",
    "high_shelf6",
    "high_shelf_q",
    "high_shelf12",
    "allpass1",
    "allpass2",
    "bandpass",
    "notch",
    "tilt",
]


OUTPUT_DRIVE_MODES = [
    "output_off",
    "output_low_z",
    "output70_v",
    "output100_v",
    "output_btl",
]


XR_TYPES = [
    "off",
    "but6",
    "but12",
    "but24",
    "but18",
    "but36",
    "but48",
    "bes12",
    "bes24",
    "bes48",
    "lr12",
    "lr24",
    "lr36",
    "lr48",
]


CLIP_LIMITER_MODES = ["fast", "normal"]


GENERATOR_TYPES = ["white_noise", "pink_noise", "sine"]

GENERATOR_MIX_MODES = ["off", "mix", "solo"]


HPF_FILTER_TYPES = [
    "off",
    "but12",
    "but24",
    "lr12",
    "lr24",
]


POWER_ON_MODES = [
    "audio",
    "audio_eco",
    "trigger",
    "trigger_eco",
    "network_only",
    "audio_dsp",
]

FUSE_PROTECTION_MODES = [
    "off",
    "auto",
]

SPEAKER_WAYS = [
    "LF",  # Low Frequency
    "LM",  # Low-Mid Frequency
    "MF",  # Mid Frequency
    "HM",  # High-Mid Frequency
    "HF",  # High Frequency
    "FR",  # Full Range (default)
    "SUB",  # Subwoofer
]

GPIO_PIN_TYPES = [
    "off",
    "vcc3_v3",
    "volume_control",
    "trigger12_v_out",
    "trigger12_v_in",
    "standby_no",
    "standby_nc",
    "mute_no",
    "mute_nc",
]


id_generator = (i for i in itertools.count(1))


def jrpc_request(
    method: str,
    params: dict[str, Any] | tuple[Any, ...] | None,
    id: Any = None,
) -> str:
    """Create a JSON-RPC 2.0 request string."""
    req = {
        "jsonrpc": "2.0",
        "method": method,
        "id": id if id else next(id_generator),
    }
    if params is not None:
        req["params"] = list(params) if isinstance(params, tuple) else params
    return json.dumps(req)


class JrpcResponseOK(NamedTuple):
    id: Any
    result: Any


class JrpcResponseErr(NamedTuple):
    id: Any
    error: dict[str, Any]


class JrpcNotification(NamedTuple):
    method: str
    params: Any


def jrpc_parse(s: str | bytes) -> JrpcResponseOK | JrpcResponseErr | JrpcNotification:
    """
    Parse a JSON-RPC 2.0 message string into either ResponseOK, ResponseErr, or Notification.

    Args:
        s: JSON string or bytes containing the JSON-RPC message

    Returns:
        ResponseOK: For successful responses (has 'result' field)
        ResponseErr: For error responses (has 'error' field)
        Notification: For notifications (has 'method' field, no 'id')

    Raises:
        ValueError: If the string is not valid JSON or not a valid JSON-RPC message
    """
    try:
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Check if it's a valid JSON-RPC 2.0 message
    if not isinstance(data, dict):
        raise ValueError("JSON-RPC message must be an object")

    jsonrpc_version = data.get("jsonrpc")
    if jsonrpc_version != "2.0":
        raise ValueError(f"Invalid or missing JSON-RPC version: {jsonrpc_version}")

    # Check if it's a notification (has method, no id)
    if "method" in data and "id" not in data:
        return JrpcNotification(method=data["method"], params=data.get("params"))

    # Check if it's a response (has id)
    if "id" in data:
        msg_id = data["id"]

        # Success response (has result)
        if "result" in data:
            return JrpcResponseOK(id=msg_id, result=data["result"])

        # Error response (has error)
        elif "error" in data:
            return JrpcResponseErr(id=msg_id, error=data["error"])

        else:
            raise ValueError("Response must have either 'result' or 'error' field")

    # If we get here, it's neither a valid response nor notification
    raise ValueError("Invalid JSON-RPC message: missing required fields")


class BaseCommand:
    command = None
    help = None

    @classmethod
    def add_parser(cls, subparsers):
        parser = subparsers.add_parser(cls.command, help=cls.help)
        cls.add_arguments(parser)
        parser.set_defaults(command_cls=cls)

    @classmethod
    def add_arguments(cls, parser):
        pass

    @classmethod
    async def run(cls, args):
        # Override in subclass
        pass

    @classmethod
    async def _connect_ws(cls, target, port):
        uri = f"ws://{target}:{port}/ws"
        # Configure WebSocket limits to handle batch operations
        # max_size: maximum message size in bytes (None = unlimited)
        # max_queue: maximum number of messages in receive queue
        # write_limit: controls frame size - use 4KB frames for better compatibility
        # read_limit: buffer size for reading frames
        return websockets.connect(
            uri,
            ping_interval=20,
            ping_timeout=10,
            max_queue=128,  # Increase queue size for large responses
        )

    @classmethod
    async def send_command_jrpc_message(
        cls, target: str, port: int, command: str, params: dict, verbose: bool, quiet: bool = False
    ) -> JrpcResponseOK:
        try:
            async with await cls._connect_ws(target, port) as websocket:
                return await cls.send_command_jrpc_message_on_socket(websocket, command, params, verbose, quiet)
        except websockets.exceptions.WebSocketException as err:
            if quiet:
                error_output = {"error": {"message": "Connection failed", "details": str(err)}}
                print(json.dumps(error_output))
                raise CommandError(f"Connection failed: {str(err)}") from err
            else:
                print(f"{Fore.RED}Connection error: {str(err)}{Style.RESET_ALL}", file=sys.stderr)
                if verbose:
                    import traceback

                    traceback.print_exc()
                # Raise CommandError since we already printed the error
                raise CommandError() from err
        except TimeoutError as err:
            if quiet:
                error_output = {"error": {"message": "Connection timeout", "details": "Connection timed out"}}
                print(json.dumps(error_output))
                raise CommandError("Connection timeout") from err
            else:
                print(f"{Fore.RED}Connection error: Connection timed out{Style.RESET_ALL}", file=sys.stderr)
                if verbose:
                    import traceback

                    traceback.print_exc()
                # Raise CommandError since we already printed the error
                raise CommandError() from err
        except CommandError:
            # Re-raise CommandError without catching it
            raise
        except Exception as err:
            if quiet:
                error_output = {"error": {"message": "Unexpected error", "details": str(err)}}
                print(json.dumps(error_output))
                # Re-raise with message for quiet mode
                raise
            else:
                error_msg = str(err) if str(err) else type(err).__name__
                print(f"{Fore.RED}Error: {error_msg}{Style.RESET_ALL}", file=sys.stderr)
                if verbose:
                    import traceback

                    traceback.print_exc()
                # Raise CommandError since we already printed the error
                raise CommandError() from err

    @classmethod
    async def send_command_jrpc_message_on_socket(
        cls, websocket, command: str, params: dict, verbose: bool, quiet: bool = False
    ) -> JrpcResponseOK:
        req = jrpc_request(command, params)
        req_data = json.loads(req)
        request_id = req_data.get("id")

        if not quiet and verbose:
            print(f"{Fore.CYAN}Command:{Style.RESET_ALL} {command}")
            if params:
                params_formatted = json.dumps(params, indent=2)
                print(f"{Fore.CYAN}Parameters:{Style.RESET_ALL}\n{params_formatted}")
            print(f"{Fore.CYAN}Raw JSON-RPC:{Style.RESET_ALL} {req}")

        start_time = time.time()
        await websocket.send(req)

        # Loop to receive messages, skipping notifications until we get the actual response
        while True:
            response_str = await websocket.recv()
            response = jrpc_parse(response_str)

            # If it's a notification, log it and continue waiting for the response
            if isinstance(response, JrpcNotification):
                if verbose and not quiet:
                    print(f"Received notification: {response.method}")
                continue

            # If it's a response (OK or Error), verify it matches our request ID
            if isinstance(response, (JrpcResponseOK, JrpcResponseErr)):
                if response.id == request_id:
                    break
                else:
                    # Response for different request, shouldn't happen but handle it
                    if verbose and not quiet:
                        print(
                            f"Warning: Received response for different request ID: {response.id} (expected {request_id})"
                        )
                    continue

        end_time = time.time()
        if verbose and not quiet:
            print(f"Round trip time: {((end_time - start_time) * 1000):.1f} ms")

        if isinstance(response, JrpcResponseErr):
            error_msg = response.error.get("message", "Unknown error")
            error_code = response.error.get("code", "N/A")

            if quiet:
                # Quiet mode: output only JSON error
                error_output = {"error": response.error, "id": response.id}
                print(json.dumps(error_output))
                # Raise with message for quiet mode
                raise CommandError(f"JSON-RPC error [{error_code}]: {error_msg}")
            else:
                # Normal mode: print error and raise
                print(
                    f"{Fore.RED}Error [{error_code}]: {error_msg}{Style.RESET_ALL}",
                    file=sys.stderr,
                )
                if verbose:
                    # Verbose mode: full error details
                    print(f"{Fore.RED}Full error details:{Style.RESET_ALL}", file=sys.stderr)
                    print(json.dumps(response.error, indent=2), file=sys.stderr)
                # Raise CommandError since we already printed the error
                raise CommandError()
        elif isinstance(response, JrpcResponseOK):
            if quiet:
                # Quiet mode: output only JSON result
                print(json.dumps(response.result))
            else:
                # Normal mode: formatted output with color
                response_formatted = json.dumps(response.result, indent=4)
                print(f"{Fore.GREEN}Response:{Style.RESET_ALL} {response_formatted}")

            return response
        elif isinstance(response, JrpcNotification):
            if quiet:
                notification_output = {"notification": {"method": response.method, "params": response.params}}
                print(json.dumps(notification_output))
            else:
                print(f"{Fore.YELLOW}Notification received: {response}{Style.RESET_ALL}")
            # Raise CommandError
            raise CommandError("Unexpected notification received")
        else:
            if quiet:
                error_output = {"error": {"message": "Unknown response type", "data": str(response)}}
                print(json.dumps(error_output))
            else:
                print(
                    f"{Fore.RED}Unknown response type: {response}{Style.RESET_ALL}",
                    file=sys.stderr,
                )
            # Raise CommandError
            raise CommandError(f"Unknown response type: {response}")

    @classmethod
    async def send_setup_get_jrpc_message(cls, target: str, port: int, path: str, verbose: bool, quiet: bool = False):
        await cls.send_command_jrpc_message(target, port, "setup_get", {"path": path}, verbose, quiet)

    @classmethod
    async def send_setup_set_jrpc_message(
        cls, target: str, port: int, path: str, param_dict: dict | list, verbose: bool, quiet: bool = False
    ):
        await cls.send_command_jrpc_message(
            target, port, "setup_set", {"path": path, "value": param_dict}, verbose, quiet
        )

    @classmethod
    async def send_setup_get_all_jrpc_message(
        cls, target: str, port: int, params: dict, verbose: bool, quiet: bool = False
    ):
        await cls.send_command_jrpc_message(target, port, "setup_get_all", params, verbose, quiet)

    @classmethod
    async def send_subscribe_jrpc_message(
        cls,
        rpc_method: str,
        target: str,
        port: int,
        params: dict,
        verbose: bool,
        timeout: int | None = None,
    ):
        async with await cls._connect_ws(target, port) as websocket:
            await cls.send_command_jrpc_message_on_socket(websocket, rpc_method, params, verbose)

            # Listen for subsequent messages
            try:
                if timeout:
                    print(f"{Fore.CYAN}Connection will timeout after {timeout} seconds{Style.RESET_ALL}")

                start_listen_time = time.time()
                while True:
                    # Handle timeout if specified
                    if timeout:
                        elapsed = time.time() - start_listen_time
                        if elapsed >= timeout:
                            print(f"{Fore.CYAN}Timeout reached ({timeout}s), closing connection{Style.RESET_ALL}")
                            break

                        remaining_timeout = timeout - elapsed
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=remaining_timeout)
                        except TimeoutError:
                            print(f"{Fore.CYAN}Timeout reached ({timeout}s), closing connection{Style.RESET_ALL}")
                            break
                    else:
                        message = await websocket.recv()

                    try:
                        parsed_update = jrpc_parse(message)
                        if isinstance(parsed_update, JrpcResponseErr):
                            print(
                                f"{Fore.RED}Update Error: {parsed_update.error}{Style.RESET_ALL}",
                                file=sys.stderr,
                            )
                        elif isinstance(parsed_update, JrpcResponseOK):
                            update_formatted = json.dumps(parsed_update.result, indent=4)
                            print(f"{Fore.YELLOW}Update:{Style.RESET_ALL} {update_formatted}")
                        elif isinstance(parsed_update, JrpcNotification):
                            notif_formatted = json.dumps(parsed_update.params, indent=4)
                            print(f"{Fore.YELLOW}Notification:{Style.RESET_ALL} {notif_formatted}")
                        else:
                            print(f"{Fore.YELLOW}Raw message:{Style.RESET_ALL} {message}")
                    except Exception as e:
                        try:
                            raw_json = json.loads(message)
                            update_formatted = json.dumps(raw_json, indent=4)
                            print(f"{Fore.YELLOW}Message:{Style.RESET_ALL} {update_formatted}")
                        except json.JSONDecodeError:
                            print(f"{Fore.YELLOW}Raw message:{Style.RESET_ALL} {message}")
                            print(
                                f"{Fore.RED}Parse error: {e}{Style.RESET_ALL}",
                                file=sys.stderr,
                            )

            except websockets.exceptions.ConnectionClosed:
                print(f"{Fore.RED}WebSocket connection closed{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}Subscription terminated by user{Style.RESET_ALL}")


# New hierarchical command support classes
class CommandGroup:
    """Base class for command groups with nested subcommands."""

    name = None
    description = None

    @staticmethod
    def register_commands(subparsers):
        """Override this to register group commands."""
        pass


class SubCommand(BaseCommand):
    """Alias for BaseCommand to make the hierarchy clearer."""

    pass


# Registry
class CommandRegistry:
    commands = []
    groups = []

    @classmethod
    def register(cls, command_cls):
        cls.commands.append(command_cls)

    @classmethod
    def register_group(cls, group_cls):
        """Register a command group."""
        cls.groups.append(group_cls)

    @classmethod
    def build_parser(cls):
        parser = argparse.ArgumentParser(description="Set input parameters via WebSocket")
        parser.add_argument("-t", "--target", type=str, default="192.168.64.100")
        parser.add_argument("-p", "--port", type=int, default=80)
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable verbose output with timing and full error details"
        )
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="Quiet mode: output only JSON (no colors or extra messages)"
        )
        subparsers = parser.add_subparsers(dest="command")

        # Register individual commands
        for cmd in cls.commands:
            cmd.add_parser(subparsers)

        # Register command groups
        for group in cls.groups:
            group.register_commands(subparsers)

        return parser
