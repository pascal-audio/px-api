"""Setup commands - Batch operations for configuration backup/restore."""

from japi_cli_base import SubCommand

__all__ = [
    "BatchCreate",
    "BatchApply",
]


class BatchCreate(SubCommand):
    """Save current device configuration to a file as batch commands."""

    @classmethod
    async def run(cls, args):
        import sys

        from colorama import Fore, Style

        from japi_cli_base import JrpcResponseErr, JrpcResponseOK, jrpc_parse, jrpc_request

        # Get the current setup from device
        async with await cls._connect_ws(args.target, args.port) as websocket:
            # Get all setup configuration
            get_all_req = jrpc_request("setup_get_all", {})
            await websocket.send(get_all_req)
            response_str = await websocket.recv()
            response = jrpc_parse(response_str)

            if isinstance(response, JrpcResponseErr):
                print(f"{Fore.RED}Failed to get setup: {response.error}{Style.RESET_ALL}", file=sys.stderr)
                sys.exit(1)

            if not isinstance(response, JrpcResponseOK):
                print(f"{Fore.RED}Unexpected response type{Style.RESET_ALL}", file=sys.stderr)
                sys.exit(1)

            setup = response.result

            # Write batch commands to file
            try:
                with open(args.file, "w") as f:
                    cls._write_batch_commands(f, setup)
                print(f"{Fore.GREEN}Configuration saved to {args.file}{Style.RESET_ALL}")
            except OSError as e:
                print(f"{Fore.RED}Failed to write file: {e}{Style.RESET_ALL}", file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def _write_batch_commands(f, setup):
        """Write setup as batch commands with comments grouping sections."""
        import json

        f.write("# Thorium Firmware Batch Configuration\n")
        f.write("# One JSON-RPC command per line (comments start with #)\n")
        f.write('# Format: {"method": "setup_set", "params": {"path": "...", "value": {...}}}\n\n')

        # ==============================================================================
        # Install INFORMATION
        # ==============================================================================
        if "install" in setup:
            f.write("# ==============================================================================\n")
            f.write("# INSTALL INFORMATION\n")
            f.write("# ==============================================================================\n")
            install = setup["install"]
            cmd = {"method": "setup_set", "params": {"path": "/install", "value": install}}
            f.write(json.dumps(cmd, separators=(",", ":")) + "\n\n")

        # ==============================================================================
        # GPIO CONFIGURATION
        # ==============================================================================
        if "gpio" in setup:
            f.write("# ==============================================================================\n")
            f.write("# GPIO CONFIGURATION\n")
            f.write("# ==============================================================================\n")
            gpio_data = setup["gpio"]
            cmd = {"method": "setup_set", "params": {"path": "/gpio", "value": gpio_data}}
            f.write(json.dumps(cmd, separators=(",", ":")) + "\n\n")

        # ==============================================================================
        # NETWORK CONFIGURATION
        # ==============================================================================
        if "network" in setup:
            f.write("# ==============================================================================\n")
            f.write("# NETWORK CONFIGURATION\n")
            f.write("# ==============================================================================\n")
            network_data = setup["network"]

            # Network mode (split/dante/disabled)
            if "mode" in network_data:
                mode_only = {"mode": network_data["mode"]}
                cmd = {"method": "setup_set", "params": {"path": "/network", "value": mode_only}}
                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

            # LAN1 setup
            if "lan1" in network_data:
                f.write("# --- LAN1 Setup\n")
                cmd = {
                    "method": "setup_set",
                    "params": {"path": "/network/lan1", "value": network_data["lan1"]},
                }
                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

            # LAN2 setup
            if "lan2" in network_data:
                f.write("# --- LAN2 Setup\n")
                cmd = {
                    "method": "setup_set",
                    "params": {"path": "/network/lan2", "value": network_data["lan2"]},
                }
                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

            f.write("\n")

        # ==============================================================================
        # POWER MANAGEMENT
        # ==============================================================================
        if "power" in setup:
            f.write("# ==============================================================================\n")
            f.write("# POWER MANAGEMENT\n")
            f.write("# ==============================================================================\n")
            power_data = setup["power"]
            cmd = {"method": "setup_set", "params": {"path": "/power", "value": power_data}}
            f.write(json.dumps(cmd, separators=(",", ":")) + "\n\n")

        # ==============================================================================
        # AUDIO CONFIGURATION
        # ==============================================================================
        # Audio Input - Analog channels
        if "audio" in setup and "input" in setup["audio"]:
            audio_input = setup["audio"]["input"]

            if "analog" in audio_input:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO INPUT - ANALOG CHANNELS\n")
                f.write("# ==============================================================================\n")
                for ch_id, ch_data in sorted(audio_input["analog"].items()):
                    path = f"/audio/input/analog/{ch_id}"
                    cmd = {"method": "setup_set", "params": {"path": path, "value": ch_data}}
                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")
                f.write("\n")

            # Digital inputs
            if "digital" in audio_input:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO INPUT - DIGITAL CHANNELS\n")
                f.write("# ==============================================================================\n")
                for ch_id, ch_data in sorted(audio_input["digital"].items()):
                    path = f"/audio/input/digital/{ch_id}"
                    cmd = {"method": "setup_set", "params": {"path": path, "value": ch_data}}
                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")
                f.write("\n")

            # Network inputs
            if "network" in audio_input:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO INPUT - NETWORK CHANNELS\n")
                f.write("# ==============================================================================\n")
                for ch_id, ch_data in sorted(audio_input["network"].items()):
                    path = f"/audio/input/network/{ch_id}"
                    cmd = {"method": "setup_set", "params": {"path": path, "value": ch_data}}
                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")
                f.write("\n")

            # Input config
            if "config" in audio_input:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO INPUT - CONFIGURATION\n")
                f.write("# ==============================================================================\n")
                cmd = {"method": "setup_set", "params": {"path": "/audio/input/config", "value": audio_input["config"]}}
                f.write(json.dumps(cmd, separators=(",", ":")) + "\n\n")

            # Generator
            if "generator" in audio_input:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO INPUT - GENERATOR\n")
                f.write("# ==============================================================================\n")
                cmd = {
                    "method": "setup_set",
                    "params": {"path": "/audio/input/generator", "value": audio_input["generator"]},
                }
                f.write(json.dumps(cmd, separators=(",", ":")) + "\n\n")

        # Audio Output
        if "audio" in setup and "output" in setup["audio"]:
            audio_output = setup["audio"]["output"]

            # Summing matrix
            if "summing_matrix" in audio_output:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO OUTPUT - SUMMING MATRIX\n")
                f.write("# ==============================================================================\n")
                cmd = {
                    "method": "setup_set",
                    "params": {"path": "/audio/output/summing_matrix", "value": audio_output["summing_matrix"]},
                }
                f.write(json.dumps(cmd, separators=(",", ":")) + "\n\n")

            # Speaker outputs
            if "speaker" in audio_output:
                for ch_id, ch_data in sorted(audio_output["speaker"].items()):
                    f.write("# ==============================================================================\n")
                    f.write(f"# SPEAKER CHANNEL {ch_id}\n")
                    f.write("# ==============================================================================\n")

                    # Main speaker channel settings
                    speaker_main = {k: v for k, v in ch_data.items() if k in ["primary_src", "fallback_src", "name"]}
                    if speaker_main:
                        cmd = {
                            "method": "setup_set",
                            "params": {"path": f"/audio/output/speaker/{ch_id}", "value": speaker_main},
                        }
                        f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                    # User processing
                    if "user" in ch_data:
                        f.write(f"# --- Speaker {ch_id} - User Processing\n")
                        user_data = ch_data["user"]
                        user_main = {k: v for k, v in user_data.items() if k != "eq"}
                        if user_main:
                            cmd = {
                                "method": "setup_set",
                                "params": {"path": f"/audio/output/speaker/{ch_id}/user", "value": user_main},
                            }
                            f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # User EQ
                        if "eq" in user_data:
                            eq_data = user_data["eq"]
                            eq_main = {k: v for k, v in eq_data.items() if k != "bands"}
                            if eq_main:
                                cmd = {
                                    "method": "setup_set",
                                    "params": {"path": f"/audio/output/speaker/{ch_id}/user/eq", "value": eq_main},
                                }
                                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                            # User EQ bands
                            if "bands" in eq_data:
                                for band_id, band_data in sorted(eq_data["bands"].items()):
                                    cmd = {
                                        "method": "setup_set",
                                        "params": {
                                            "path": f"/audio/output/speaker/{ch_id}/user/eq/bands/{band_id}",
                                            "value": band_data,
                                        },
                                    }
                                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                    # Array processing
                    if "array" in ch_data:
                        f.write(f"# --- Speaker {ch_id} - Array Processing\n")
                        array_data = ch_data["array"]
                        array_main = {k: v for k, v in array_data.items() if k not in ["eq", "fir"]}
                        if array_main:
                            cmd = {
                                "method": "setup_set",
                                "params": {"path": f"/audio/output/speaker/{ch_id}/array", "value": array_main},
                            }
                            f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # Array EQ
                        if "eq" in array_data:
                            eq_data = array_data["eq"]
                            eq_main = {k: v for k, v in eq_data.items() if k != "bands"}
                            if eq_main:
                                cmd = {
                                    "method": "setup_set",
                                    "params": {"path": f"/audio/output/speaker/{ch_id}/array/eq", "value": eq_main},
                                }
                                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                            # Array EQ bands
                            if "bands" in eq_data:
                                for band_id, band_data in sorted(eq_data["bands"].items()):
                                    cmd = {
                                        "method": "setup_set",
                                        "params": {
                                            "path": f"/audio/output/speaker/{ch_id}/array/eq/bands/{band_id}",
                                            "value": band_data,
                                        },
                                    }
                                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # Array FIR
                        if "fir" in array_data:
                            cmd = {
                                "method": "setup_set",
                                "params": {
                                    "path": f"/audio/output/speaker/{ch_id}/array/fir",
                                    "value": array_data["fir"],
                                },
                            }
                            f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                    # Preset processing
                    if "preset" in ch_data:
                        f.write(f"# --- Speaker {ch_id} - Preset Processing\n")
                        preset_data = ch_data["preset"]
                        preset_main = {
                            k: v
                            for k, v in preset_data.items()
                            if k
                            not in [
                                "crossover",
                                "eq",
                                "fir",
                                "peak_limiter",
                                "rms_limiter",
                                "clip_limiter",
                                "preset",
                                "preset_customized",
                            ]
                        }
                        if preset_main:
                            cmd = {
                                "method": "setup_set",
                                "params": {"path": f"/audio/output/speaker/{ch_id}/preset", "value": preset_main},
                            }
                            f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # Preset crossover
                        if "crossover" in preset_data:
                            cmd = {
                                "method": "setup_set",
                                "params": {
                                    "path": f"/audio/output/speaker/{ch_id}/preset/crossover",
                                    "value": preset_data["crossover"],
                                },
                            }
                            f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # Preset EQ
                        if "eq" in preset_data:
                            eq_data = preset_data["eq"]
                            eq_main = {k: v for k, v in eq_data.items() if k != "bands"}
                            if eq_main:
                                cmd = {
                                    "method": "setup_set",
                                    "params": {"path": f"/audio/output/speaker/{ch_id}/preset/eq", "value": eq_main},
                                }
                                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                            # Preset EQ bands
                            if "bands" in eq_data:
                                for band_id, band_data in sorted(eq_data["bands"].items()):
                                    cmd = {
                                        "method": "setup_set",
                                        "params": {
                                            "path": f"/audio/output/speaker/{ch_id}/preset/eq/bands/{band_id}",
                                            "value": band_data,
                                        },
                                    }
                                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # Preset FIR
                        if "fir" in preset_data:
                            cmd = {
                                "method": "setup_set",
                                "params": {
                                    "path": f"/audio/output/speaker/{ch_id}/preset/fir",
                                    "value": preset_data["fir"],
                                },
                            }
                            f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                        # Preset limiters
                        for limiter_type in ["peak_limiter", "rms_limiter", "clip_limiter"]:
                            if limiter_type in preset_data:
                                cmd = {
                                    "method": "setup_set",
                                    "params": {
                                        "path": f"/audio/output/speaker/{ch_id}/preset/{limiter_type}",
                                        "value": preset_data[limiter_type],
                                    },
                                }
                                f.write(json.dumps(cmd, separators=(",", ":")) + "\n")

                    f.write("\n")

            # Digital outputs
            if "digital" in audio_output:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO OUTPUT - DIGITAL CHANNELS\n")
                f.write("# ==============================================================================\n")
                for ch_id, ch_data in sorted(audio_output["digital"].items()):
                    cmd = {
                        "method": "setup_set",
                        "params": {"path": f"/audio/output/digital/{ch_id}", "value": ch_data},
                    }
                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")
                f.write("\n")

            # Network outputs
            if "network" in audio_output:
                f.write("# ==============================================================================\n")
                f.write("# AUDIO OUTPUT - NETWORK CHANNELS\n")
                f.write("# ==============================================================================\n")
                for ch_id, ch_data in sorted(audio_output["network"].items()):
                    cmd = {
                        "method": "setup_set",
                        "params": {"path": f"/audio/output/network/{ch_id}", "value": ch_data},
                    }
                    f.write(json.dumps(cmd, separators=(",", ":")) + "\n")
                f.write("\n")


class BatchApply(SubCommand):
    """Apply configuration from a file to the device."""

    @classmethod
    async def run(cls, args):
        import itertools
        import json
        import sys
        import time

        from colorama import Fore, Style

        # Read batch commands from file
        try:
            with open(args.file) as f:
                batch_requests = cls._read_batch_commands(f)
        except OSError as e:
            print(f"{Fore.RED}Failed to read file: {e}{Style.RESET_ALL}", file=sys.stderr)
            sys.exit(1)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"{Fore.RED}Invalid batch file format: {e}{Style.RESET_ALL}", file=sys.stderr)
            sys.exit(1)

        if not batch_requests:
            print(f"{Fore.YELLOW}No commands found in batch file{Style.RESET_ALL}")
            return

        # Add JSON-RPC envelope and ID to each command
        id_generator = (i for i in itertools.count(1))
        for cmd in batch_requests:
            cmd["jsonrpc"] = "2.0"
            cmd["id"] = next(id_generator)

        batch_response_str = None
        try:
            async with await cls._connect_ws(args.target, args.port) as websocket:
                # Send batch request
                batch_json = json.dumps(batch_requests)
                print(f"Sending batch request with {len(batch_requests)} commands...")
                if args.verbose:
                    print(f"Batch request size: {len(batch_json)} bytes ({len(batch_json) / 1024:.1f} KB)")
                    print(
                        f"Batch request: {batch_json[:500]}..."
                        if len(batch_json) > 500
                        else f"Batch request: {batch_json}"
                    )

                start_time = time.time()
                await websocket.send(batch_json)

                if args.verbose:
                    print("Waiting for response...")

                # Loop to receive messages, skipping notifications until we get the batch response
                batch_response_str = None
                while True:
                    msg = await websocket.recv()

                    # Try to parse as JSON to check if it's a notification or response
                    try:
                        parsed = json.loads(msg)
                        # If it's a notification (no 'id' field, has 'method'), skip it
                        if isinstance(parsed, dict) and "method" in parsed and "id" not in parsed:
                            if args.verbose:
                                print(f"Received notification: {parsed.get('method')}")
                            continue
                        # If it's a batch response (list) or single response (has 'id'), use it
                        batch_response_str = msg
                        break
                    except json.JSONDecodeError:
                        # If we can't parse it, assume it's the response
                        batch_response_str = msg
                        break

                end_time = time.time()

                if args.verbose:
                    print(f"Response size: {len(batch_response_str)} bytes ({len(batch_response_str) / 1024:.1f} KB)")
                    print(f"Round trip time: {((end_time - start_time) * 1000):.1f} ms")

                # Parse batch response
                batch_response = json.loads(batch_response_str)

                if not isinstance(batch_response, list):
                    print(f"{Fore.RED}Expected batch response to be a list{Style.RESET_ALL}", file=sys.stderr)
                    sys.exit(1)

                success_count = 0
                error_count = 0

                for resp in batch_response:
                    if "error" in resp:
                        error_count += 1
                        if args.verbose:
                            print(f"{Fore.RED}Error in batch item {resp.get('id')}: {resp['error']}{Style.RESET_ALL}")
                    elif "result" in resp:
                        success_count += 1

                print(f"{Fore.GREEN}Batch complete: {success_count} succeeded, {error_count} failed{Style.RESET_ALL}")

                if error_count > 0:
                    sys.exit(1)

        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse batch response: {e}{Style.RESET_ALL}", file=sys.stderr)
            if args.verbose and batch_response_str is not None:
                print(f"Response: {batch_response_str}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Batch operation failed: {e}{Style.RESET_ALL}", file=sys.stderr)
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    @staticmethod
    def _read_batch_commands(f):
        """Read batch commands from file, one JSON command per line, ignoring comments."""
        import json

        commands = []
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            try:
                cmd = json.loads(line)
                if not isinstance(cmd, dict) or "method" not in cmd or "params" not in cmd:
                    raise ValueError(f"Line {line_num}: Invalid command format (must have 'method' and 'params')")
                commands.append(cmd)
            except json.JSONDecodeError as e:
                raise ValueError(f"Line {line_num}: Invalid JSON - {e}") from e
        return commands
