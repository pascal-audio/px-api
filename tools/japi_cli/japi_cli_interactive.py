"""
Interactive REPL mode for japi_cli using prompt-toolkit.
"""

import argparse
import asyncio
import shlex
import sys
from typing import TYPE_CHECKING

from colorama import Fore
from colorama import Style as ColoramaStyle

# Import CommandError from base
from japi_cli_base import CommandError

# Try to import prompt_toolkit, but make it optional
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.styles import Style

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    # Define stub types for type checking when prompt_toolkit is not available
    if TYPE_CHECKING:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import Completer, Completion
        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.styles import Style
    else:
        # Create dummy classes to avoid runtime errors
        Completer = object  # type: ignore
        Completion = object  # type: ignore

        def HTML(x):  # type: ignore
            return x

        InMemoryHistory = object  # type: ignore
        Style = object  # type: ignore
        PromptSession = object  # type: ignore

    print("Warning: prompt_toolkit not installed. Interactive mode will use basic input.", file=sys.stderr)
    print("Install with: pip install prompt-toolkit", file=sys.stderr)


# Only define completer if prompt_toolkit is available
if PROMPT_TOOLKIT_AVAILABLE:

    class JapiCliCompleter(Completer):
        """Custom completer for japi_cli hierarchical commands."""

        def __init__(self, parser: argparse.ArgumentParser):
            self.parser = parser
            self.command_tree = self._build_command_tree()

        def _build_command_tree(self) -> dict:
            """Build a tree of all available commands from argparse."""
            tree = {}

            # Get top-level subparsers
            for action in self.parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for choice_name, choice_parser in action.choices.items():
                        tree[choice_name] = self._extract_subcommands(choice_parser)

            return tree

        def _extract_subcommands(self, parser: argparse.ArgumentParser) -> dict:
            """Recursively extract subcommands from a parser."""
            subcommands = {}

            for action in parser._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for choice_name, choice_parser in action.choices.items():
                        subcommands[choice_name] = self._extract_subcommands(choice_parser)

            return subcommands

        def get_completions(self, document, complete_event):
            """Generate completions based on current input."""
            text = document.text_before_cursor
            words = shlex.split(text) if text else []

            # Handle empty or trailing space
            if not text or text.endswith(" "):
                current_word = ""
            else:
                current_word = words[-1] if words else ""
                words = words[:-1]

            # Navigate the command tree
            current_level = self.command_tree
            for word in words:
                if word.startswith("-"):
                    # Skip options
                    continue
                if word in current_level:
                    if isinstance(current_level[word], dict):
                        current_level = current_level[word]
                    else:
                        # Reached a leaf, no more completions
                        return
                else:
                    # Invalid path, no completions
                    return

            # Suggest completions at current level
            for cmd_name in current_level.keys():
                if cmd_name.startswith(current_word):
                    yield Completion(
                        cmd_name,
                        start_position=-len(current_word),
                        display=cmd_name,
                    )


class InteractiveShell:
    """Interactive shell for japi_cli."""

    def __init__(self, parser: argparse.ArgumentParser, target: str, port: int, verbose: bool = False):
        self.parser = parser
        self.target = target
        self.port = port
        self.verbose = verbose
        self.use_prompt_toolkit = PROMPT_TOOLKIT_AVAILABLE
        self.session = None
        self.history = None
        self.completer = None
        self.prompt_style = None

        if self.use_prompt_toolkit:
            self.history = InMemoryHistory()
            self.completer = JapiCliCompleter(parser)

            # Custom style
            self.prompt_style = Style.from_dict(
                {
                    "prompt": "#00aa00 bold",
                    "target": "#00aaaa",
                }
            )

    def get_prompt_message(self):
        """Generate the prompt message."""
        if self.use_prompt_toolkit:
            return HTML(f"<prompt>japi</prompt> <target>[{self.target}:{self.port}]</target> > ")
        else:
            return f"{Fore.GREEN}japi{ColoramaStyle.RESET_ALL} [{Fore.CYAN}{self.target}:{self.port}{ColoramaStyle.RESET_ALL}] > "

    async def run(self):
        """Run the interactive shell."""
        if self.use_prompt_toolkit:
            self.session = PromptSession(
                history=self.history,
                completer=self.completer,
                style=self.prompt_style,
                complete_while_typing=True,
                enable_history_search=True,
            )

        print(f"{Fore.GREEN}=== JAPI CLI Interactive Mode ==={ColoramaStyle.RESET_ALL}")
        print(f"{Fore.CYAN}Target: {self.target}:{self.port}{ColoramaStyle.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'help' for usage, 'exit' or Ctrl+D to quit{ColoramaStyle.RESET_ALL}")
        print()

        while True:
            try:
                # Get input from user
                if self.use_prompt_toolkit and self.session:
                    user_input = await self.session.prompt_async(self.get_prompt_message())
                else:
                    user_input = input(self.get_prompt_message())

                # Skip empty input
                if not user_input.strip():
                    continue

                # Handle built-in commands
                if user_input.strip().lower() in ("exit", "quit", "q"):
                    print(f"{Fore.CYAN}Goodbye!{ColoramaStyle.RESET_ALL}")
                    break

                if user_input.strip().lower() == "help":
                    self.print_help()
                    continue

                if user_input.strip().lower().startswith("target "):
                    self.handle_target_command(user_input)
                    continue

                if user_input.strip().lower() == "clear":
                    print("\033[2J\033[H", end="")  # Clear screen
                    continue

                # Parse and execute command
                await self.execute_command(user_input)

            except KeyboardInterrupt:
                # Ctrl+C pressed
                print()
                continue
            except EOFError:
                # Ctrl+D pressed
                print(f"\n{Fore.CYAN}Goodbye!{ColoramaStyle.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{ColoramaStyle.RESET_ALL}", file=sys.stderr)
                if self.verbose:
                    import traceback

                    traceback.print_exc()

    def print_help(self):
        """Print help message with available commands."""
        print(f"\n{Fore.GREEN}Interactive Mode Help:{ColoramaStyle.RESET_ALL}")
        print(f"{Fore.YELLOW}Built-in Commands:{ColoramaStyle.RESET_ALL}")
        print("  help                - Show this help message")
        print("  target <ip[:port]>  - Change target device")
        print("  clear               - Clear screen")
        print("  exit, quit, q       - Exit interactive mode")
        print()
        print(f"{Fore.YELLOW}Device Commands:{ColoramaStyle.RESET_ALL}")
        print("  Use the same syntax as command-line mode, but without 'japi_cli.py'")
        print("  Examples:")
        print(f"    {Fore.CYAN}api version{ColoramaStyle.RESET_ALL}")
        print(f"    {Fore.CYAN}setup get speaker channel 1{ColoramaStyle.RESET_ALL}")
        print(f"    {Fore.CYAN}setup set speaker gain 1 -3.5{ColoramaStyle.RESET_ALL}")
        print(f"    {Fore.CYAN}device time{ColoramaStyle.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}Command Groups:{ColoramaStyle.RESET_ALL}")
        print("  api        - API version and ping")
        print("  device     - Install info and control")
        print("  preset     - Manage channel presets")
        print("  setup      - Show/set device configuration")
        print("  subscribe  - Subscribe to updates")
        print()
        print(f"{Fore.YELLOW}Tips:{ColoramaStyle.RESET_ALL}")
        if self.use_prompt_toolkit:
            print("  - Use TAB for command completion")
            print("  - Use arrow keys for command history")
        print("  - Add -v flag for verbose output: setup get speaker gain 1 -v")
        print("  - Add -q flag for JSON-only output: api version -q")
        print()

    def handle_target_command(self, user_input: str):
        """Handle the 'target' built-in command to change target device."""
        parts = user_input.strip().split(maxsplit=1)
        if len(parts) < 2:
            print(f"{Fore.RED}Usage: target <ip[:port]>{ColoramaStyle.RESET_ALL}")
            return

        target_str = parts[1]
        if ":" in target_str:
            ip, port_str = target_str.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                print(f"{Fore.RED}Invalid port number: {port_str}{ColoramaStyle.RESET_ALL}")
                return
            self.target = ip
            self.port = port
        else:
            self.target = target_str

        print(f"{Fore.GREEN}Target changed to: {self.target}:{self.port}{ColoramaStyle.RESET_ALL}")

    async def execute_command(self, user_input: str):
        """Parse and execute a japi_cli command."""
        try:
            # Parse the input into command and arguments
            args_list = shlex.split(user_input)
            if not args_list:
                return

            # Inject target and port as default arguments
            # Insert them at the beginning so they can be overridden
            full_args = ["-t", self.target, "-p", str(self.port)]
            if self.verbose:
                full_args.append("-v")
            full_args.extend(args_list)

            # Parse with the main parser
            try:
                args = self.parser.parse_args(full_args)
            except SystemExit as e:
                # argparse calls sys.exit on error, catch it
                if e.code != 0:
                    # Error occurred, message already printed
                    return
                # Help was shown successfully
                return

            # Execute the command through the command_cls
            try:
                if hasattr(args, "command_cls"):
                    await args.command_cls.run(args)
                elif hasattr(args, "func"):
                    # Some commands might use func instead
                    await args.func(args)
                else:
                    print(f"{Fore.RED}Command incomplete. Type 'help' for usage.{ColoramaStyle.RESET_ALL}")
            except Exception as cmd_error:
                # Catch errors from command execution
                # CommandError means error was already printed
                if not isinstance(cmd_error, CommandError):
                    print(f"{Fore.RED}Error: {cmd_error}{ColoramaStyle.RESET_ALL}")

                if self.verbose:
                    import traceback

                    traceback.print_exc()

        except Exception as e:
            print(f"{Fore.RED}Error parsing command: {e}{ColoramaStyle.RESET_ALL}")
            if self.verbose:
                import traceback

                traceback.print_exc()


def run_interactive_mode(parser: argparse.ArgumentParser, target: str, port: int, verbose: bool = False):
    """Entry point for interactive mode."""
    shell = InteractiveShell(parser, target, port, verbose)
    asyncio.run(shell.run())
