"""Device commands group - device-level actions and control."""

from datetime import UTC

from japi_cli_base import CommandGroup, SubCommand


class DeviceGroup(CommandGroup):
    """Device command group for device-level operations."""

    name = "device"
    description = "Device-level actions and control"

    @staticmethod
    def register_commands(subparsers):
        """Register device commands."""
        device_parser = subparsers.add_parser(
            DeviceGroup.name,
            help=DeviceGroup.description,
            description=DeviceGroup.description,
        )
        device_subparsers = device_parser.add_subparsers(dest="device_action", required=True)

        # device reboot
        reboot_parser = device_subparsers.add_parser("reboot", help="Reboot the device (JSON-RPC: device_reboot)")
        reboot_parser.set_defaults(command_cls=DeviceReboot)

        # device reset (factory reset)
        reset_parser = device_subparsers.add_parser("reset", help="Factory reset the device (JSON-RPC: device_reset)")
        reset_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
        reset_parser.add_argument(
            "--preserve-network", action="store_true", help="Preserve network settings during reset"
        )
        reset_parser.set_defaults(command_cls=DeviceReset)

        # device power-on
        power_on_parser = device_subparsers.add_parser(
            "power-on", help="Power on the device (JSON-RPC: device_power_on)"
        )
        power_on_parser.set_defaults(command_cls=DevicePowerOn)

        # device power-off
        power_off_parser = device_subparsers.add_parser(
            "power-off", help="Power off the device (JSON-RPC: device_power_off)"
        )
        power_off_parser.set_defaults(command_cls=DevicePowerOff)

        # device find-me
        find_me_parser = device_subparsers.add_parser(
            "find-me", help="Make device identify itself (LED flash) (JSON-RPC: device_find_me)"
        )
        find_me_parser.add_argument("-t", "--timeout", type=float, help="Timeout in seconds (0 to stop)")
        find_me_parser.set_defaults(command_cls=DeviceFindMe)

        # device fwupd
        fwupd_parser = device_subparsers.add_parser(
            "fwupd", help="Upload firmware file to device (HTTP POST to /api/firmware)"
        )
        fwupd_parser.add_argument("-f", "--file", required=True, help="Firmware file to upload")
        fwupd_parser.set_defaults(command_cls=DeviceFirmwareUpdate)

        # device discover (mDNS discovery)
        discover_parser = device_subparsers.add_parser(
            "discover",
            help="Discover PX devices on network (mDNS - not JSON-RPC)",
            description="Discover devices via mDNS/Zeroconf. Local-only operation, does not use JSON-RPC.",
        )
        discover_parser.add_argument(
            "-t", "--timeout", type=float, default=3.0, help="Discovery timeout in seconds (default: 3.0)"
        )
        discover_parser.set_defaults(command_cls=DeviceDiscover)

        # device time subgroup
        _register_device_time(device_subparsers)


def _register_device_time(subparsers):
    """Register device time commands."""
    time_parser = subparsers.add_parser(
        "time", help="Device time operations (JSON-RPC: device_get_time, device_set_time)"
    )
    time_subparsers = time_parser.add_subparsers(dest="time_action", required=True)

    # device time show
    show_parser = time_subparsers.add_parser("show", help="Show device time (JSON-RPC: device_get_time)")
    show_parser.set_defaults(command_cls=DeviceTimeShow)

    # device time set
    set_parser = time_subparsers.add_parser("set", help="Set device time (JSON-RPC: device_set_time)")
    set_parser.add_argument("-t", "--time", help="Time in ISO 8601 format (default: current host time in UTC)")
    set_parser.set_defaults(command_cls=DeviceTimeSet)


# Command implementations


class DeviceReboot(SubCommand):
    """Reboot the device."""

    @classmethod
    async def run(cls, args):
        if not args.quiet:
            print("Rebooting device...")
        await cls.send_command_jrpc_message(args.target, args.port, "device_reboot", {}, args.verbose, args.quiet)


class DeviceReset(SubCommand):
    """Factory reset the device."""

    @classmethod
    async def run(cls, args):
        if not args.yes and not args.quiet:
            response = input("Are you sure you want to factory reset the device? (yes/no): ")
            if response.lower() != "yes":
                print("Factory reset cancelled.")
                return

        params = {}
        if args.preserve_network:
            params["preserve_network_settings"] = True

        if not args.quiet:
            print("Performing factory reset...")
        await cls.send_command_jrpc_message(args.target, args.port, "device_reset", params, args.verbose, args.quiet)


class DevicePowerOn(SubCommand):
    """Power on the device."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(args.target, args.port, "device_power_on", {}, args.verbose, args.quiet)


class DevicePowerOff(SubCommand):
    """Power off the device."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(args.target, args.port, "device_power_off", {}, args.verbose, args.quiet)


class DeviceFindMe(SubCommand):
    """Make device identify itself."""

    @classmethod
    async def run(cls, args):
        params = {}
        if args.timeout is not None:
            params["timeout_sec"] = args.timeout
        await cls.send_command_jrpc_message(args.target, args.port, "device_find_me", params, args.verbose, args.quiet)


class DeviceTimeShow(SubCommand):
    """Show device time."""

    @classmethod
    async def run(cls, args):
        await cls.send_command_jrpc_message(args.target, args.port, "device_get_time", {}, args.verbose, args.quiet)


class DeviceTimeSet(SubCommand):
    """Set device time."""

    @classmethod
    async def run(cls, args):
        from datetime import datetime

        # If no time provided, use current host time in UTC
        time_str = args.time if args.time else datetime.now(UTC).isoformat()

        await cls.send_command_jrpc_message(
            args.target,
            args.port,
            "device_set_time",
            {"time": time_str},
            args.verbose,
            args.quiet,
        )


class DeviceFirmwareUpdate(SubCommand):
    """Upload firmware file to device."""

    @classmethod
    async def run(cls, args):
        import os
        import sys

        import aiohttp
        from colorama import Fore, Style

        from japi_cli_base import CommandError

        # Check if file exists
        if not os.path.exists(args.file):
            print(f"{Fore.RED}Error: File not found: {args.file}{Style.RESET_ALL}", file=sys.stderr)
            raise CommandError()

        file_size = os.path.getsize(args.file)

        if not args.quiet:
            print(f"{Fore.CYAN}Uploading firmware: {args.file}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}File size: {file_size:,} bytes ({file_size / (1024 * 1024):.2f} MB){Style.RESET_ALL}")

        url = f"http://{args.target}:{args.port}/api/firmware"

        try:
            async with aiohttp.ClientSession() as session:
                # Read file in chunks for progress tracking
                chunk_size = 8192  # 8KB chunks
                uploaded = 0

                # Create an async generator that yields chunks and updates progress
                async def file_sender():
                    nonlocal uploaded
                    with open(args.file, "rb") as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            uploaded += len(chunk)

                            if not args.quiet:
                                percent = (uploaded / file_size) * 100
                                bar_length = 40
                                filled = int(bar_length * uploaded / file_size)
                                bar = "█" * filled + "░" * (bar_length - filled)
                                mb_uploaded = uploaded / (1024 * 1024)
                                mb_total = file_size / (1024 * 1024)
                                print(
                                    f"\r{Fore.YELLOW}Uploading: [{bar}] {percent:.1f}% ({mb_uploaded:.2f}/{mb_total:.2f} MB){Style.RESET_ALL}",
                                    end="",
                                    flush=True,
                                )

                            yield chunk

                if not args.quiet:
                    print(f"{Fore.YELLOW}Starting upload...{Style.RESET_ALL}")

                # Send raw binary data with application/octet-stream content type
                headers = {"Content-Type": "application/octet-stream"}

                # Make the POST request with streaming data
                async with session.post(
                    url, data=file_sender(), headers=headers, timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if not args.quiet:
                        print()  # New line after progress bar

                    if response.status == 200 or response.status == 204:
                        if not args.quiet:
                            print(f"{Fore.GREEN}✓ Firmware uploaded successfully{Style.RESET_ALL}")

                        # Try to get response body if available
                        try:
                            response_text = await response.text()
                            if response_text and not args.quiet:
                                print(f"{Fore.CYAN}Response: {response_text}{Style.RESET_ALL}")
                        except Exception:
                            pass
                    else:
                        error_text = await response.text()
                        if not args.quiet:
                            print(f"{Fore.RED}✗ Upload failed with status {response.status}{Style.RESET_ALL}")
                            if error_text:
                                print(f"{Fore.RED}Error: {error_text}{Style.RESET_ALL}")
                        else:
                            print(f"Error: HTTP {response.status}")

        except aiohttp.ClientError as e:
            if not args.quiet:
                print(f"\r{' ' * 100}\r{Fore.RED}✗ Connection error: {e}{Style.RESET_ALL}")
            else:
                print(f"Error: {e}")
        except Exception as e:
            if not args.quiet:
                print(f"\r{' ' * 100}\r{Fore.RED}✗ Unexpected error: {e}{Style.RESET_ALL}")
            else:
                print(f"Error: {e}")


class DeviceDiscover(SubCommand):
    """Discover PX devices on the network using mDNS."""

    @classmethod
    async def run(cls, args):
        from colorama import Fore, Style

        try:
            import socket

            from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
        except ImportError:
            if not args.quiet:
                print(f"{Fore.RED}✗ zeroconf library not installed{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Install with: pip install zeroconf{Style.RESET_ALL}")
            else:
                print("Error: zeroconf library not installed")
            return

        class PxListener(ServiceListener):
            def __init__(self):
                self.devices = []

            def add_service(self, zc, type_, name):
                info = zc.get_service_info(type_, name)
                if info:
                    self.devices.append(
                        {
                            "name": name,
                            "address": socket.inet_ntoa(info.addresses[0]) if info.addresses else None,
                            "port": info.port,
                            "properties": {
                                k.decode(): v.decode() if isinstance(v, bytes) else v
                                for k, v in info.properties.items()
                            },
                        }
                    )

            def remove_service(self, zc, type_, name):
                pass

            def update_service(self, zc, type_, name):
                pass

        if not args.quiet:
            print(f"🔍 Discovering PX devices on network (timeout: {args.timeout}s)...")

        zeroconf = Zeroconf()
        listener = PxListener()
        browser = ServiceBrowser(zeroconf, "_px._sub._pasconnect._tcp.local.", listener)

        # Wait for discovery
        import asyncio

        await asyncio.sleep(args.timeout)

        browser.cancel()
        zeroconf.close()

        if not listener.devices:
            if not args.quiet:
                print(f"{Fore.YELLOW}No PX devices found{Style.RESET_ALL}")
            return

        if args.quiet:
            # JSON output in quiet mode
            import json

            print(json.dumps(listener.devices, indent=2))
        else:
            print(f"\n{Fore.GREEN}Found {len(listener.devices)} device(s):{Style.RESET_ALL}\n")
            for device in listener.devices:
                print(f"{Fore.CYAN}Device:{Style.RESET_ALL} {device['name']}")
                print(f"  {Fore.CYAN}Address:{Style.RESET_ALL} {device['address']}:{device['port']}")
                if device["properties"]:
                    print(f"  {Fore.CYAN}Properties:{Style.RESET_ALL}")
                    for key, value in device["properties"].items():
                        print(f"    {key}: {value}")
                print()
