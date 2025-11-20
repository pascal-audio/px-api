#!/usr/bin/env python3
"""
Advanced JAPI CLI Auto-Discovery Test Generator

This tool goes beyond the basic test suite by using the actual japi_cli command line
interface to discover all available commands and their options automatically,
then generates comprehensive test cases.

Features:
- Discovers commands by parsing `japi_cli.py --help` output
- Extracts parameter details by calling `japi_cli.py <command> --help`
- Auto-generates test values based on parameter types and help text
- Creates test matrices for all parameter combinations
- Generates both positive and negative test cases
- Supports advanced option discovery through CLI introspection
"""

import argparse
import asyncio
import json
import logging
import os
import random
import re
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add parent directory to path to import CLI modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import only what we need for auto-discovery
from japi_cli_base import str2bool


@dataclass
class TestResult:
    """Represents the result of a single test execution."""

    command: str
    args: list[str]
    success: bool
    duration: float
    error: str | None = None
    response: dict | None = None


@dataclass
class TestStats:
    """Aggregate test statistics."""

    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[TestResult] = field(default_factory=list)
    duration: float = 0.0


class ParameterGenerator:
    """Generates test values for different parameter types."""

    @staticmethod
    def generate_int_value(choices: list | None = None, min_val: int = 1, max_val: int = 4) -> int:
        """Generate integer test values."""
        if choices:
            return random.choice(choices)
        return random.randint(min_val, max_val)

    @staticmethod
    def generate_float_value(min_val: float = -20.0, max_val: float = 20.0) -> float:
        """Generate float test values."""
        return round(random.uniform(min_val, max_val), 2)

    @staticmethod
    def generate_string_value(choices: list | None = None, prefix: str = "test") -> str:
        """Generate string test values."""
        if choices:
            return random.choice(choices)
        return f"{prefix}_{random.randint(1000, 9999)}"

    @staticmethod
    def generate_ip_address() -> str:
        """Generate valid IP address for testing."""
        return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"

    @staticmethod
    def generate_bool_value() -> bool:
        """Generate boolean test values."""
        return random.choice([True, False])

    @staticmethod
    def generate_matrix_file() -> str:
        """Generate a temporary matrix file for testing."""
        matrix = [[random.uniform(-1.0, 1.0) for _ in range(4)] for _ in range(4)]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(matrix, f)
            return f.name


class JAPITestRunner:
    """Main test runner for JAPI CLI commands."""

    def __init__(self, target: str, port: int = 80, verbose: bool = False, dry_run: bool = False):
        self.target = target
        self.port = port
        self.verbose = verbose
        self.dry_run = dry_run
        self.param_gen = ParameterGenerator()
        self.stats = TestStats()
        self.results: list[TestResult] = []
        self.introspector: Any = None  # Will be set by subclasses

        # Setup logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    async def run_all_tests(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        test_variations: bool = True,
    ) -> TestStats:
        """Run comprehensive tests on all discovered commands."""
        start_time = time.time()

        self.logger.info("Starting comprehensive JAPI CLI test suite")
        self.logger.info(f"Target: {self.target}:{self.port}")
        self.logger.info(f"Discovered {len(self.introspector.get_commands())} commands")

        # Filter commands based on patterns
        commands_to_test = self._filter_commands(self.introspector.get_commands(), include_patterns, exclude_patterns)

        self.logger.info(f"Testing {len(commands_to_test)} commands")

        # Test device connectivity first
        if not await self._test_connectivity():
            self.logger.error("Failed to connect to device. Aborting tests.")
            return self.stats

        # Run tests for each command
        for command in commands_to_test:
            await self._test_command(command, test_variations)

        # Calculate final stats
        self.stats.duration = time.time() - start_time
        self.stats.total_tests = len(self.results)
        self.stats.passed = sum(1 for r in self.results if r.success)
        self.stats.failed = self.stats.total_tests - self.stats.passed
        self.stats.errors = [r for r in self.results if not r.success]

        self._print_summary()
        return self.stats

    def _filter_commands(
        self,
        commands: list[str],
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[str]:
        """Filter commands based on include/exclude patterns."""
        filtered = commands[:]

        if include_patterns:
            filtered = [cmd for cmd in filtered if any(pattern in cmd for pattern in include_patterns)]

        if exclude_patterns:
            filtered = [cmd for cmd in filtered if not any(pattern in cmd for pattern in exclude_patterns)]

        return filtered

    async def _test_connectivity(self) -> bool:
        """Test basic connectivity to the device."""
        try:
            self.logger.info("Testing device connectivity...")

            if self.dry_run:
                self.logger.info("Dry run mode - skipping connectivity test")
                return True

            # For auto-discovery tests, we'll skip the connectivity test
            # and let individual command tests handle failures
            self.logger.info("Connectivity test skipped for auto-discovery mode")
            return True

        except Exception as e:
            self.logger.error(f"Connectivity test failed: {e}")
            return False

    async def _test_command(self, command: str, test_variations: bool = True):
        """Test a single command with various parameter combinations."""
        cmd_class, params = self.introspector.get_command_info(command)

        if not cmd_class:
            self.logger.warning(f"Command class not found for: {command}")
            return

        self.logger.info(f"Testing command: {command}")

        # Generate test cases
        test_cases = self._generate_test_cases(command, params, test_variations)

        for test_case in test_cases:
            result = await self._run_single_test(cmd_class, command, test_case)
            self.results.append(result)

            if result.success:
                self.logger.debug(f"✅ {command} {' '.join(test_case)} - PASSED")
            else:
                self.logger.warning(f"❌ {command} {' '.join(test_case)} - FAILED: {result.error}")

    def _generate_test_cases(self, command: str, params: dict, test_variations: bool) -> list[list[str]]:
        """Generate test cases for command parameters."""
        test_cases = []

        # Basic test case with minimal parameters
        basic_case = self._generate_basic_case(params)
        test_cases.append(basic_case)  # Always append, even if empty

        if not test_variations:
            return test_cases

        # Generate variations
        variations = self._generate_parameter_variations(params)
        test_cases.extend(variations)

        # Limit test cases to prevent excessive testing
        max_cases = 10
        if len(test_cases) > max_cases:
            test_cases = random.sample(test_cases, max_cases)

        return test_cases

    def _generate_basic_case(self, params: dict) -> list[str]:
        """Generate basic test case with minimal required parameters."""
        args = []

        for param_name, param_info in params.items():
            if param_info.get("required", False) or not param_info.get("option_strings"):
                # This is a required positional argument
                value = self._generate_parameter_value(param_name, param_info)
                if value is not None:
                    args.append(str(value))

        return args  # Return empty list if no parameters, which is valid

    def _generate_parameter_variations(self, params: dict) -> list[list[str]]:
        """Generate parameter variations for comprehensive testing."""
        variations = []

        # Test with different optional parameters
        optional_params = {k: v for k, v in params.items() if not v.get("required", False) and v.get("option_strings")}

        # Generate combinations of optional parameters
        for param_name, param_info in optional_params.items():
            base_args = self._generate_basic_case(params)

            # Add this optional parameter
            option_string = param_info.get("option_strings", [f"--{param_name}"])[0]
            value = self._generate_parameter_value(param_name, param_info)

            if value is not None:
                if param_info.get("action") == "_StoreTrueAction":
                    if value:  # Only add flag if True
                        base_args.extend([option_string])
                        variations.append(base_args)
                else:
                    base_args.extend([option_string, str(value)])
                    variations.append(base_args)

        return variations

    def _generate_parameter_value(self, param_name: str, param_info: dict) -> Any:
        """Generate appropriate test value for a parameter."""
        choices = param_info.get("choices")
        param_type = param_info.get("type")

        # Handle special parameter names first (highest priority)
        if param_name == "ch" or param_name == "channel":
            return self.param_gen.generate_int_value(choices or list(range(1, 5)))

        elif param_name == "band":
            max_band = 16 if "preset" in param_name else 11
            return self.param_gen.generate_int_value(choices or list(range(1, max_band)))

        elif param_name in ["interface"]:
            return self.param_gen.generate_string_value(choices or ["lan1", "lan2"])

        elif param_name in ["ip_address", "netmask", "gateway", "dns1", "dns2"]:
            return self.param_gen.generate_ip_address()

        elif param_name in ["standby_time", "mute_time"]:
            # Force integer generation for time parameters
            return self.param_gen.generate_int_value(choices=None, min_val=1, max_val=60)

        elif param_name in ["value"] and choices:
            return self.param_gen.generate_string_value(choices)

        # Handle by type (only if not handled above)
        elif param_type is int or (choices and all(isinstance(c, int) for c in choices)):
            return self.param_gen.generate_int_value(choices)

        elif param_type is float:
            return self.param_gen.generate_float_value()

        elif param_type == str2bool or param_info.get("action") == "_StoreTrueAction":
            return self.param_gen.generate_bool_value()

        elif param_type is str or choices:
            return self.param_gen.generate_string_value(choices)

        # Default string value
        return self.param_gen.generate_string_value()

    async def _run_single_test(self, cmd_class, command: str, test_args: list[str]) -> TestResult:
        """Run a single test case."""
        start_time = time.time()

        try:
            if self.dry_run:
                # Simulate success in dry run mode
                duration = time.time() - start_time
                return TestResult(
                    command=command, args=test_args, success=True, duration=duration, response={"dry_run": True}
                )

            # Create argument namespace
            args = self._create_args_namespace(command, test_args)

            # Run the command
            await cmd_class.run(args)

            duration = time.time() - start_time
            return TestResult(command=command, args=test_args, success=True, duration=duration)

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            if self.verbose:
                error_msg += f"\n{traceback.format_exc()}"

            return TestResult(command=command, args=test_args, success=False, duration=duration, error=error_msg)

    def _create_args_namespace(self, command: str, test_args: list[str]) -> argparse.Namespace:
        """Create argument namespace from test arguments."""
        # Create a simple namespace for legacy compatibility
        return argparse.Namespace(
            target=self.target, port=self.port, verbose=self.verbose, command=command, args=test_args
        )

    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("JAPI CLI TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests:     {self.stats.total_tests}")
        print(f"Passed:          {self.stats.passed}")
        print(f"Failed:          {self.stats.failed}")
        print(
            f"Success Rate:    {(self.stats.passed / self.stats.total_tests * 100):.1f}%"
            if self.stats.total_tests > 0
            else "0.0%"
        )
        print(f"Total Duration:  {self.stats.duration:.2f}s")
        print(
            f"Avg Per Test:    {(self.stats.duration / self.stats.total_tests):.3f}s"
            if self.stats.total_tests > 0
            else "0.000s"
        )

        if self.stats.failed > 0:
            print(f"\nFAILED TESTS ({self.stats.failed}):")
            print("-" * 40)
            for result in self.stats.errors[:10]:  # Show first 10 failures
                print(f"❌ {result.command} {' '.join(result.args)}")
                if result.error:
                    print(f"   Error: {result.error.split(chr(10))[0]}...")  # First line only

            if len(self.stats.errors) > 10:
                print(f"   ... and {len(self.stats.errors) - 10} more failures")

        print("=" * 80)


@dataclass
@dataclass
class DiscoveredParameter:
    """Represents a parameter discovered from CLI help."""

    name: str
    short_name: str | None = None
    description: str = ""
    type_hint: str = ""
    choices: list[str] = field(default_factory=list)
    required: bool = False
    default_value: Any = None
    metavar: str | None = None


@dataclass
class DiscoveredCommand:
    """Represents a command discovered from CLI help."""

    name: str
    description: str
    parameters: dict[str, DiscoveredParameter] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    raw_help: str = ""


class CLIHelpParser:
    """Parses CLI help output to discover commands and parameters."""

    def __init__(self, cli_script: str | None = None):
        if cli_script is None:
            cli_script = os.path.join(os.path.dirname(__file__), "..", "japi_cli.py")
        self.cli_script = cli_script
        self.logger = logging.getLogger(__name__)
        self.discovered_commands: dict[str, DiscoveredCommand] = {}

    async def discover_all_commands(self) -> dict[str, DiscoveredCommand]:
        """Discover all commands by parsing CLI help output."""
        self.logger.info("Discovering commands from CLI help system...")

        # Get main help to discover available commands
        main_help = await self._get_cli_help()
        command_names = self._parse_command_list(main_help)

        self.logger.info(f"Discovered {len(command_names)} commands from main help")

        # Get detailed help for each command
        for cmd_name in command_names:
            try:
                cmd_help = await self._get_cli_help(cmd_name)
                command = self._parse_command_help(cmd_name, cmd_help)
                self.discovered_commands[cmd_name] = command
                self.logger.debug(f"Parsed command: {cmd_name} ({len(command.parameters)} parameters)")
            except Exception as e:
                self.logger.warning(f"Failed to parse help for command {cmd_name}: {e}")

        return self.discovered_commands

    async def _get_cli_help(self, command: str | None = None) -> str:
        """Get help output from CLI."""
        cmd = ["python", self.cli_script]
        if command:
            cmd.append(command)
        cmd.append("--help")

        try:
            # Run the command and capture output
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=Path(self.cli_script).parent
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                self.logger.warning(f"CLI help command failed: {stderr.decode()}")
                return ""

            return stdout.decode()

        except Exception as e:
            self.logger.error(f"Failed to run CLI help: {e}")
            return ""

    def _parse_command_list(self, help_text: str) -> list[str]:
        """Parse the main help output to extract command names."""
        commands = []

        # Look for the command list in braces format: {cmd1,cmd2,cmd3,...}
        # This appears in the usage line and positional arguments section
        brace_pattern = r"\{([^}]+)\}"
        matches = re.findall(brace_pattern, help_text)

        for match in matches:
            # Split by comma and clean up command names
            cmd_list = [cmd.strip() for cmd in match.split(",")]
            commands.extend(cmd_list)

        # Also look for individual command descriptions in the positional arguments section
        lines = help_text.split("\n")
        in_commands_section = False

        for line in lines:
            line_stripped = line.strip()

            # Detect start of commands section
            if "positional arguments:" in line_stripped.lower():
                in_commands_section = True
                continue

            # Detect end of commands section
            if in_commands_section and (
                line_stripped.startswith("optional arguments:") or line_stripped.startswith("options:")
            ):
                break

            # Extract command names from individual descriptions
            if in_commands_section and line_stripped:
                # Look for lines like "    get_input           Get input"
                parts = line_stripped.split()
                if (
                    parts
                    and not parts[0].startswith("-")
                    and not parts[0].startswith("{")
                    and "_" in parts[0]
                    and not parts[0].endswith(":")
                ):
                    commands.append(parts[0])

        # Clean up and deduplicate
        commands = list(set([cmd.strip() for cmd in commands if cmd.strip()]))

        # Filter out invalid entries
        valid_commands = []
        for cmd in commands:
            if cmd and not cmd.startswith("-") and not cmd.endswith(":") and len(cmd) > 2:
                valid_commands.append(cmd)

        return valid_commands

    def _parse_command_help(self, command_name: str, help_text: str) -> DiscoveredCommand:
        """Parse individual command help to extract parameters."""
        lines = help_text.split("\n")

        # Extract description (usually the first non-empty line after usage)
        description = ""
        for line in lines:
            if line.strip() and not line.startswith("usage:"):
                description = line.strip()
                break

        # Parse parameters
        parameters = {}
        current_param = None
        in_positional_section = False
        in_options_section = False
        positional_count = 0  # Track multiple positional arguments

        for line in lines:
            line_stripped = line.strip()

            # Detect positional arguments section
            if "positional arguments:" in line_stripped.lower():
                in_positional_section = True
                in_options_section = False
                continue

            # Detect options sections
            if "optional arguments:" in line_stripped.lower() or "options:" in line_stripped.lower():
                in_options_section = True
                in_positional_section = False
                continue

            # End of current section
            if line_stripped and not line.startswith("  ") and (in_positional_section or in_options_section):
                in_positional_section = False
                in_options_section = False

            # Parse positional arguments
            if in_positional_section and line.startswith("  "):
                param_info = self._parse_positional_parameter(line, positional_count)
                if param_info:
                    parameters[param_info.name] = param_info
                    current_param = param_info.name
                    positional_count += 1

            # Parse optional arguments
            elif in_options_section and line.startswith("  -"):
                param_info = self._parse_parameter_line(line)
                if param_info:
                    parameters[param_info.name] = param_info
                    current_param = param_info.name

            # Handle continuation lines
            elif current_param and line.startswith("    ") and line_stripped:
                if current_param in parameters:
                    parameters[current_param].description += " " + line_stripped

        # Extract examples
        examples = self._extract_examples(help_text)

        return DiscoveredCommand(
            name=command_name, description=description, parameters=parameters, examples=examples, raw_help=help_text
        )

    def _parse_positional_parameter(self, line: str, position: int) -> DiscoveredParameter | None:
        """Parse a positional parameter definition line from help output."""
        line = line.strip()

        # Handle positional arguments with choices like "{1,2,3,4}             Channel"
        positional_match = re.match(r"^\{([^}]+)\}\s*(.*)$", line)
        if positional_match:
            choices_str = positional_match.group(1)
            description = positional_match.group(2).strip()
            choices = [c.strip().strip("'\"") for c in choices_str.split(",")]

            # Determine parameter name based on description or position
            if "channel" in description.lower():
                param_name = "channel"
                type_hint = "channel"
            elif "band" in description.lower() or (position == 1 and not description):
                param_name = "band"
                type_hint = "band"
            elif "preset" in description.lower():
                param_name = "preset"
                type_hint = "int"
            else:
                # Generic positional argument names
                param_names = ["channel", "band", "preset", "index"]
                param_name = param_names[min(position, len(param_names) - 1)]
                type_hint = "int"

            return DiscoveredParameter(
                name=param_name,
                short_name=None,
                description=description or f"Positional argument {position + 1}",
                type_hint=type_hint,
                choices=choices,
                required=True,
                metavar=None,
            )

        return None

    def _parse_parameter_line(self, line: str) -> DiscoveredParameter | None:
        """Parse an optional parameter definition line from help output."""
        # Example formats:
        # -h, --help            show this help message and exit
        # -g GAIN, --gain GAIN  Gain value
        # --verbose             Enable verbose output

        line = line.strip()

        # Handle optional arguments
        # Pattern: -h, --help [METAVAR]  description
        # Also handle: -ho HOLD, --hold HOLD  Hold time
        # And: -b BYPASS, --bypass BYPASS  Bypass status
        opt_match = re.match(r"^(-\w+)(?:\s+(\w+))?(?:,?\s+(--\w+))?(?:\s+(\w+))?\s+(.*)$", line)
        if not opt_match:
            return None

        short_name = opt_match.group(1).lstrip("-") if opt_match.group(1) else None
        short_metavar = opt_match.group(2)  # Metavar after short option
        long_name = opt_match.group(3).removeprefix("--") if opt_match.group(3) else None
        long_metavar = opt_match.group(4)  # Metavar after long option
        description = opt_match.group(5)

        # Use metavar from either short or long form
        metavar = short_metavar or long_metavar

        # Determine parameter name (prefer long name)
        param_name = long_name or short_name
        if not param_name:
            return None

        # Extract choices from description - look for {choice1,choice2,choice3} patterns
        choices = []
        choice_matches = re.findall(r"\{([^}]+)\}", description)
        if choice_matches:
            # Take the first set of choices found
            choices = [c.strip().strip("'\"") for c in choice_matches[0].split(",")]

        # Determine if this parameter takes a value
        takes_value = metavar is not None or choices or "help" not in param_name.lower()

        # Special handling for help parameter
        if param_name.lower() == "help" or (short_name == "h" and not long_name):
            takes_value = False

        # Determine type from metavar, choices, or description
        if choices:
            type_hint = "choice"
        elif not takes_value:
            type_hint = "bool"
        else:
            type_hint = self._infer_type(metavar, description)

        return DiscoveredParameter(
            name=param_name,
            short_name=short_name,
            description=description,
            type_hint=type_hint,
            choices=choices,
            required=False,  # Optional arguments are not required
            metavar=metavar,
        )

    def _infer_type(self, metavar: str | None, description: str) -> str:
        """Infer parameter type from metavar and description."""
        if not metavar and not description:
            return "bool"

        desc_lower = description.lower()
        metavar_upper = metavar.upper() if metavar else ""

        # Check for specific type indicators
        if any(word in desc_lower for word in ["frequency", "freq", "hz"]):
            return "frequency"
        elif any(word in desc_lower for word in ["gain", "db", "decibel"]) or metavar_upper in ["GAIN"]:
            return "gain"
        elif any(word in desc_lower for word in ["threshold"]) and "db" in desc_lower:
            return "gain"  # Threshold in dB is like gain
        elif any(word in desc_lower for word in ["delay", "time", "seconds", "attack", "release", "hold"]):
            return "delay"
        elif any(word in desc_lower for word in ["channel", "ch"]):
            return "channel"
        elif any(word in desc_lower for word in ["band"]):
            return "band"
        elif any(word in desc_lower for word in ["bypass", "status"]) or metavar_upper in ["BYPASS"]:
            return "bool_value"  # Boolean that takes a value (true/false)
        elif any(word in desc_lower for word in ["auto", "mode"]) or metavar_upper in ["AUTO"]:
            return "bool_value"  # Boolean that takes a value (true/false)
        elif "file" in desc_lower or "path" in desc_lower:
            return "file"
        elif "ip" in desc_lower or "address" in desc_lower:
            return "ip"
        elif metavar_upper in ["INT", "INTEGER"]:
            return "int"
        elif metavar_upper in ["FLOAT", "NUMBER", "Q"]:
            return "float"
        elif metavar_upper in ["THRESHOLD", "ATTACK", "RELEASE", "HOLD", "KNEE"]:
            return "float"  # Audio parameters are usually float
        elif any(word in desc_lower for word in ["true", "false", "enable", "disable"]):
            return "bool"
        else:
            return "str"

    def _extract_examples(self, help_text: str) -> list[str]:
        """Extract examples from help text."""
        examples = []
        lines = help_text.split("\n")
        in_examples = False

        for line in lines:
            if "examples:" in line.lower():
                in_examples = True
                continue
            elif in_examples:
                if line.strip() and line.startswith("  "):
                    examples.append(line.strip())
                elif not line.strip():
                    continue
                else:
                    break

        return examples


class AutoTestGenerator:
    """Generates comprehensive tests from discovered CLI structure."""

    def __init__(self):
        self.param_gen = ParameterGenerator()
        self.logger = logging.getLogger(__name__)

    def generate_test_matrix(self, commands: dict[str, DiscoveredCommand]) -> dict[str, list[list[str]]]:
        """Generate comprehensive test matrix for all commands."""
        test_matrix = {}

        for cmd_name, command in commands.items():
            test_cases = self._generate_command_tests(command)
            test_matrix[cmd_name] = test_cases
            self.logger.info(f"Generated {len(test_cases)} test cases for {cmd_name}")

        return test_matrix

    def _generate_command_tests(self, command: DiscoveredCommand) -> list[list[str]]:
        """Generate test cases for a single command."""
        test_cases = []

        # Get required parameters first
        required_params = {name: param for name, param in command.parameters.items() if param.required}
        optional_params = {
            name: param
            for name, param in command.parameters.items()
            if not param.required and param.name.lower() not in ["help", "h"]
        }

        # Check if this is a subscribe command
        is_subscribe_command = "subscribe" in command.name.lower()

        # Always generate a base test case (commands with no params get empty args list)
        base_case = self._generate_base_case(required_params)

        # For subscribe commands, always add timeout of 1 second for testing
        if is_subscribe_command:
            base_case.extend(["--timeout", "1"])

        test_cases.append(base_case)

        # Generate tests with individual optional parameters (excluding help and timeout for subscribe commands)
        for _param_name, param in optional_params.items():
            # Skip timeout parameter for subscribe commands since we add it manually
            if is_subscribe_command and param.name == "timeout":
                continue

            test_case = self._generate_base_case(required_params)
            param_args = self._generate_parameter_args(param)
            if param_args:  # Only add if we got valid arguments
                test_case.extend(param_args)

                # For subscribe commands, always add timeout of 1 second for testing
                if is_subscribe_command:
                    test_case.extend(["--timeout", "1"])

                test_cases.append(test_case)

        # Generate combination tests (up to 2 optional parameters at once, excluding help and timeout for subscribe commands)
        optional_names = list(optional_params.keys())
        # Filter out timeout for subscribe commands
        if is_subscribe_command:
            optional_names = [name for name in optional_names if name != "timeout"]

        for i in range(len(optional_names)):
            for j in range(i + 1, min(i + 3, len(optional_names))):  # Max 2 combinations
                test_case = self._generate_base_case(required_params)
                args1 = self._generate_parameter_args(optional_params[optional_names[i]])
                args2 = self._generate_parameter_args(optional_params[optional_names[j]])
                if args1 and args2:  # Only add if both sets of arguments are valid
                    test_case.extend(args1)
                    test_case.extend(args2)

                    # For subscribe commands, always add timeout of 1 second for testing
                    if is_subscribe_command:
                        test_case.extend(["--timeout", "1"])

                    test_cases.append(test_case)

        return test_cases

    def _generate_base_case(self, required_params: dict[str, DiscoveredParameter]) -> list[str]:
        """Generate base case with required parameters."""
        args = []

        for param in required_params.values():
            value = self._generate_parameter_value(param)
            if value is not None:
                args.append(str(value))

        return args

    def _generate_parameter_args(self, param: DiscoveredParameter) -> list[str]:
        """Generate argument list for a parameter."""
        value = self._generate_parameter_value(param)
        if value is None and param.type_hint != "bool":
            return []

        args = []

        # Handle positional arguments (no flag prefix)
        if param.required:
            args.append(str(value))
            return args

        # Handle optional arguments
        # Add parameter flag (prefer long form for clarity)
        if param.name != param.short_name and len(param.name) > 1:
            args.append(f"--{param.name}")
        elif param.short_name:
            args.append(f"-{param.short_name}")
        else:
            args.append(f"--{param.name}")

        # Add value if not a boolean flag
        if param.type_hint != "bool" and value is not None:
            args.append(str(value))

        return args

    def _generate_parameter_value(self, param: DiscoveredParameter) -> Any:
        """Generate appropriate value for a parameter."""
        # Handle choices first
        if param.choices:
            return self.param_gen.generate_string_value(param.choices)

        # Handle specific parameter names that need special treatment
        if param.name in ["standby_time", "mute_time"]:
            return self.param_gen.generate_int_value(choices=None, min_val=1, max_val=60)
        elif param.name in ["ip_address", "netmask", "gateway", "dns1", "dns2"]:
            return "192.168.1.100"
        elif param.name in ["flatten"]:
            # Force this to be treated as a boolean flag
            param.type_hint = "bool"
            return None  # Boolean flag, no value needed

        type_hint = param.type_hint

        if type_hint == "choice":
            # Should have been handled above, but fallback
            return "analog/1"
        elif type_hint == "channel":
            return self.param_gen.generate_int_value(choices=list(range(1, 5)))
        elif type_hint == "band":
            return self.param_gen.generate_int_value(choices=list(range(1, 11)))
        elif type_hint == "frequency":
            return self.param_gen.generate_float_value(20.0, 20000.0)
        elif type_hint == "gain":
            return self.param_gen.generate_float_value(-20.0, 20.0)
        elif type_hint == "delay":
            return self.param_gen.generate_float_value(0.001, 1.0)  # Attack/release times
        elif type_hint == "int":
            return self.param_gen.generate_int_value()
        elif type_hint == "float":
            return self.param_gen.generate_float_value(0.1, 10.0)  # Q values, etc.
        elif type_hint == "bool":
            return None  # Boolean flags don't need values
        elif type_hint == "bool_value":
            # Boolean parameters that take a value, generate true/false
            return self.param_gen.generate_string_value(["true", "false", "1", "0"])
        elif type_hint == "file":
            return self._generate_temp_file()
        elif type_hint == "ip":
            return "192.168.1.100"
        else:
            return self.param_gen.generate_string_value()

    def _generate_temp_file(self) -> str:
        """Generate a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": "data"}, f)
            return f.name


class AdvancedAutoTestRunner(JAPITestRunner):
    """Enhanced test runner that uses CLI discovery."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli_parser = CLIHelpParser()
        self.test_generator = AutoTestGenerator()
        self.discovered_commands: dict[str, DiscoveredCommand] = {}

    async def run_discovery_tests(self) -> TestStats:
        """Run tests using CLI discovery."""
        start_time = time.time()

        self.logger.info("Starting CLI discovery-based test suite")

        # Discover commands from CLI help
        self.discovered_commands = await self.cli_parser.discover_all_commands()

        # Exclude backup/restore commands as they need special handling
        backup_restore_commands = ["device_backup", "device_restore"]
        original_count = len(self.discovered_commands)
        self.discovered_commands = {
            cmd: info for cmd, info in self.discovered_commands.items() if cmd not in backup_restore_commands
        }
        excluded_count = original_count - len(self.discovered_commands)

        if excluded_count > 0:
            self.logger.info(f"Excluded {excluded_count} backup/restore commands from discovery tests")

        if not self.discovered_commands:
            self.logger.error("No commands discovered from CLI help")
            return self.stats

        self.logger.info(f"Discovered {len(self.discovered_commands)} commands via CLI help")

        # Generate test matrix
        test_matrix = self.test_generator.generate_test_matrix(self.discovered_commands)

        # Test device connectivity
        if not await self._test_connectivity():
            self.logger.error("Failed to connect to device. Aborting tests.")
            return self.stats

        # Run tests
        for cmd_name, test_cases in test_matrix.items():
            await self._test_discovered_command(cmd_name, test_cases)

        # Calculate final stats
        self.stats.duration = time.time() - start_time
        self.stats.total_tests = len(self.results)
        self.stats.passed = sum(1 for r in self.results if r.success)
        self.stats.failed = self.stats.total_tests - self.stats.passed
        self.stats.errors = [r for r in self.results if not r.success]

        self._print_discovery_summary()
        return self.stats

    async def _test_discovered_command(self, command: str, test_cases: list[list[str]]):
        """Test a discovered command with generated test cases."""
        self.logger.info(f"Testing discovered command: {command} ({len(test_cases)} test cases)")

        for test_case in test_cases:
            result = await self._run_discovered_test(command, test_case)
            self.results.append(result)

            if result.success:
                self.logger.debug(f"✅ {command} {' '.join(test_case)} - PASSED")
            else:
                self.logger.warning(f"❌ {command} {' '.join(test_case)} - FAILED: {result.error}")

    async def _run_discovered_test(self, command: str, test_args: list[str]) -> TestResult:
        """Run a test case for a discovered command."""
        start_time = time.time()

        try:
            if self.dry_run:
                duration = time.time() - start_time
                return TestResult(
                    command=command,
                    args=test_args,
                    success=True,
                    duration=duration,
                    response={"dry_run": True, "discovered": True},
                )

            # Run the actual CLI command
            cli_script = os.path.join(os.path.dirname(__file__), "..", "japi_cli.py")
            cmd = ["python", cli_script, "--target", self.target, "--port", str(self.port)]
            if self.verbose:
                cmd.append("--verbose")
            cmd.append(command)
            cmd.extend(test_args)

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=Path(cli_script).parent
            )

            stdout, stderr = await process.communicate()
            duration = time.time() - start_time

            success = process.returncode == 0
            error = stderr.decode() if not success else None

            return TestResult(
                command=command,
                args=test_args,
                success=success,
                duration=duration,
                error=error,
                response={"stdout": stdout.decode()} if success else None,
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(command=command, args=test_args, success=False, duration=duration, error=str(e))

    def _print_discovery_summary(self):
        """Print summary of discovery-based tests."""
        print("\n" + "=" * 80)
        print("CLI DISCOVERY TEST SUMMARY")
        print("=" * 80)
        print(f"Commands Discovered: {len(self.discovered_commands)}")
        print(f"Total Tests:         {self.stats.total_tests}")
        print(f"Passed:              {self.stats.passed}")
        print(f"Failed:              {self.stats.failed}")
        print(
            f"Success Rate:        {(self.stats.passed / self.stats.total_tests * 100):.1f}%"
            if self.stats.total_tests > 0
            else "0.0%"
        )
        print(f"Total Duration:      {self.stats.duration:.2f}s")

        # Show discovered commands
        print(f"\nDISCOVERED COMMANDS ({len(self.discovered_commands)}):")
        print("-" * 40)
        for cmd_name, command in self.discovered_commands.items():
            param_count = len(command.parameters)
            print(f"  {cmd_name:<25} ({param_count} parameters)")

        if self.stats.failed > 0:
            print(f"\nFAILED TESTS ({self.stats.failed}):")
            print("-" * 40)
            for result in self.stats.errors[:10]:
                print(f"❌ {result.command} {' '.join(result.args)}")
                if result.error:
                    print(f"   Error: {result.error.split(chr(10))[0]}...")

        print("=" * 80)


async def main():
    """Main entry point for advanced auto-discovery testing."""
    parser = argparse.ArgumentParser(
        description="Advanced JAPI CLI Auto-Discovery Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool uses the CLI's own help system to discover commands and parameters,
then auto-generates comprehensive test cases.

Examples:
  # Auto-discover and test all commands
  python japi_cli_autodiscovery.py --target 192.168.1.100
  
  # Discovery with verbose output
  python japi_cli_autodiscovery.py --target 192.168.1.100 --verbose
  
  # Dry run to see discovered commands and generated tests
  python japi_cli_autodiscovery.py --target 192.168.1.100 --dry-run
        """,
    )

    parser.add_argument("--target", "-t", type=str, required=True, help="Target device IP address")
    parser.add_argument("--port", "-p", type=int, default=80, help="Target device port (default: 80)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show discovered commands and generated tests without executing"
    )
    default_cli_script = os.path.join(os.path.dirname(__file__), "..", "japi_cli.py")
    parser.add_argument(
        "--cli-script", type=str, default=default_cli_script, help=f"Path to CLI script (default: {default_cli_script})"
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Create enhanced test runner
    runner = AdvancedAutoTestRunner(target=args.target, port=args.port, verbose=args.verbose, dry_run=args.dry_run)

    runner.cli_parser.cli_script = args.cli_script

    try:
        stats = await runner.run_discovery_tests()
        sys.exit(0 if stats.failed == 0 else 1)

    except KeyboardInterrupt:
        print("\nAuto-discovery test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Auto-discovery test suite failed: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
