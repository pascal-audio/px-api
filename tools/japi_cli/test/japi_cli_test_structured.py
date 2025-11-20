#!/usr/bin/env python3
"""
Structured JAPI CLI Test Suite

This test suite focuses on complex workflows that require specific sequencing
and state management, particularly backup/restore operations that need to be
tested as an integrated workflow rather than individual commands.

Features:
- Backup/Restore workflow testing
- File-based operations with proper cleanup
- Sequential test dependencies
- State validation between operations
"""

import argparse
import asyncio
import logging
import os
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field
from typing import Any

# Add parent directory to path to import CLI modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import base functionality


@dataclass
class WorkflowTestResult:
    """Represents the result of a workflow test execution."""

    workflow_name: str
    steps: list[str]
    success: bool
    duration: float
    step_results: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    cleanup_success: bool = True


@dataclass
class WorkflowTestStats:
    """Aggregate workflow test statistics."""

    total_workflows: int = 0
    passed: int = 0
    failed: int = 0
    duration: float = 0.0
    errors: list[WorkflowTestResult] = field(default_factory=list)


class StructuredTestRunner:
    """Test runner for structured workflows requiring specific sequencing."""

    def __init__(self, target: str, port: int = 80, verbose: bool = False, dry_run: bool = False):
        self.target = target
        self.port = port
        self.verbose = verbose
        self.dry_run = dry_run

        self.results: list[WorkflowTestResult] = []
        self.stats = WorkflowTestStats()

        # Setup logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Temporary files for testing
        self.temp_files: list[str] = []

    async def run_all_workflows(self) -> WorkflowTestStats:
        """Run all structured workflow tests."""
        start_time = time.time()

        self.logger.info("Starting structured workflow test suite")
        self.logger.info(f"Target: {self.target}:{self.port}")

        # Test device connectivity
        if not await self._test_connectivity():
            self.logger.error("Failed to connect to device. Aborting tests.")
            return self.stats

        # Run backup/restore workflow
        await self._test_backup_restore_workflow()

        # Calculate final stats
        self.stats.duration = time.time() - start_time
        self.stats.total_workflows = len(self.results)
        self.stats.passed = sum(1 for r in self.results if r.success)
        self.stats.failed = self.stats.total_workflows - self.stats.passed
        self.stats.errors = [r for r in self.results if not r.success]

        self._cleanup_temp_files()
        self._print_summary()

        return self.stats

    async def _test_connectivity(self) -> bool:
        """Test basic connectivity to the device."""
        try:
            self.logger.info("Testing device connectivity...")

            if self.dry_run:
                self.logger.info("Dry run mode - assuming connectivity")
                return True

            # Test with a simple api_ping command

            cli_script = os.path.join(os.path.dirname(__file__), "..", "japi_cli.py")
            result = await asyncio.create_subprocess_exec(
                "python3",
                cli_script,
                "api_ping",
                "--target",
                self.target,
                "--port",
                str(self.port),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                self.logger.info("Device connectivity confirmed")
                return True
            else:
                self.logger.error(f"Connectivity test failed: {stderr.decode()}")
                return False

        except Exception as e:
            self.logger.error(f"Connectivity test failed: {e}")
            return False

    async def _test_backup_restore_workflow(self):
        """Test the complete backup and restore workflow."""
        workflow_name = "backup_restore_workflow"
        steps = [
            "create_backup_file_path",
            "execute_device_backup",
            "validate_backup_file",
            "execute_device_restore",
            "cleanup_backup_file",
        ]

        start_time = time.time()
        step_results = []
        success = True
        error = None
        cleanup_success = True

        self.logger.info(f"Starting workflow: {workflow_name}")

        # Create temporary backup file path
        backup_file = None
        try:
            # Step 1: Create backup file path
            step_start = time.time()
            backup_file = os.path.join(tempfile.gettempdir(), f"japi_test_backup_{int(time.time())}.bin")
            self.temp_files.append(backup_file)

            step_results.append(
                {
                    "step": "create_backup_file_path",
                    "duration": time.time() - step_start,
                    "success": True,
                    "details": {"backup_file": backup_file},
                }
            )
            self.logger.info(f"✅ Created backup file path: {backup_file}")

            # Step 2: Execute device backup
            if not self.dry_run:
                step_start = time.time()
                backup_success, backup_error = await self._execute_device_backup(backup_file)
                step_duration = time.time() - step_start

                step_results.append(
                    {
                        "step": "execute_device_backup",
                        "duration": step_duration,
                        "success": backup_success,
                        "details": {"error": backup_error} if backup_error else {},
                    }
                )

                if backup_success:
                    self.logger.info(f"✅ Device backup completed in {step_duration:.2f}s")
                else:
                    self.logger.error(f"❌ Device backup failed: {backup_error}")
                    success = False
                    error = f"Backup failed: {backup_error}"
            else:
                step_results.append(
                    {"step": "execute_device_backup", "duration": 0.1, "success": True, "details": {"dry_run": True}}
                )
                self.logger.info("✅ Device backup (dry run)")

            # Step 3: Validate backup file
            if success and not self.dry_run:
                step_start = time.time()
                file_valid, file_error = self._validate_backup_file(backup_file)
                step_duration = time.time() - step_start

                step_results.append(
                    {
                        "step": "validate_backup_file",
                        "duration": step_duration,
                        "success": file_valid,
                        "details": {"error": file_error}
                        if file_error
                        else {"file_size": os.path.getsize(backup_file) if file_valid else 0},
                    }
                )

                if file_valid:
                    self.logger.info(f"✅ Backup file validation passed in {step_duration:.2f}s")
                else:
                    self.logger.error(f"❌ Backup file validation failed: {file_error}")
                    success = False
                    error = f"File validation failed: {file_error}"
            else:
                step_results.append(
                    {"step": "validate_backup_file", "duration": 0.1, "success": True, "details": {"dry_run": True}}
                )
                self.logger.info("✅ Backup file validation (dry run)")

            # Step 4: Execute device restore
            if success and not self.dry_run:
                step_start = time.time()
                restore_success, restore_error = await self._execute_device_restore(backup_file)
                step_duration = time.time() - step_start

                step_results.append(
                    {
                        "step": "execute_device_restore",
                        "duration": step_duration,
                        "success": restore_success,
                        "details": {"error": restore_error} if restore_error else {},
                    }
                )

                if restore_success:
                    self.logger.info(f"✅ Device restore completed in {step_duration:.2f}s")
                else:
                    self.logger.error(f"❌ Device restore failed: {restore_error}")
                    success = False
                    error = f"Restore failed: {restore_error}"
            else:
                step_results.append(
                    {"step": "execute_device_restore", "duration": 0.1, "success": True, "details": {"dry_run": True}}
                )
                self.logger.info("✅ Device restore (dry run)")

        except Exception as e:
            success = False
            error = f"Workflow exception: {str(e)}"
            self.logger.error(f"❌ Workflow failed with exception: {e}")
            if self.verbose:
                traceback.print_exc()

        # Step 5: Cleanup
        try:
            if backup_file and os.path.exists(backup_file):
                os.unlink(backup_file)
                if backup_file in self.temp_files:
                    self.temp_files.remove(backup_file)
                self.logger.info("✅ Backup file cleaned up")
        except Exception as e:
            cleanup_success = False
            self.logger.warning(f"⚠️  Cleanup failed: {e}")

        step_results.append({"step": "cleanup_backup_file", "duration": 0.1, "success": cleanup_success, "details": {}})

        # Record workflow result
        result = WorkflowTestResult(
            workflow_name=workflow_name,
            steps=steps,
            success=success,
            duration=time.time() - start_time,
            step_results=step_results,
            error=error,
            cleanup_success=cleanup_success,
        )

        self.results.append(result)

        if success:
            self.logger.info(f"✅ Workflow '{workflow_name}' completed successfully in {result.duration:.2f}s")
        else:
            self.logger.error(f"❌ Workflow '{workflow_name}' failed in {result.duration:.2f}s: {error}")

    async def _execute_device_backup(self, backup_file: str) -> tuple[bool, str | None]:
        """Execute device backup command and save to file."""
        try:
            self.logger.info(f"Executing device backup to: {backup_file}")

            cli_script = os.path.join(os.path.dirname(__file__), "..", "japi_cli.py")
            result = await asyncio.create_subprocess_exec(
                "python3",
                cli_script,
                "device_backup",
                "--target",
                self.target,
                "--port",
                str(self.port),
                "--file",
                backup_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                return True, None
            else:
                return False, stderr.decode().strip()

        except Exception as e:
            return False, str(e)

    def _validate_backup_file(self, backup_file: str) -> tuple[bool, str | None]:
        """Validate that the backup file was created and has reasonable content."""
        try:
            if not os.path.exists(backup_file):
                return False, "Backup file does not exist"

            file_size = os.path.getsize(backup_file)
            if file_size == 0:
                return False, "Backup file is empty"

            if file_size < 100:  # Expect at least 100 bytes for a valid backup
                return False, f"Backup file too small: {file_size} bytes"

            # Try to read first few bytes to ensure it's not corrupted
            with open(backup_file, "rb") as f:
                first_bytes = f.read(10)
                if len(first_bytes) == 0:
                    return False, "Could not read backup file content"

            self.logger.debug(f"Backup file validation passed: {file_size} bytes")
            return True, None

        except Exception as e:
            return False, str(e)

    async def _execute_device_restore(self, backup_file: str) -> tuple[bool, str | None]:
        """Execute device restore command from backup file."""
        try:
            self.logger.info(f"Executing device restore from: {backup_file}")

            cli_script = os.path.join(os.path.dirname(__file__), "..", "japi_cli.py")
            result = await asyncio.create_subprocess_exec(
                "python3",
                cli_script,
                "device_restore",
                "--target",
                self.target,
                "--port",
                str(self.port),
                "--file",
                backup_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                return True, None
            else:
                return False, stderr.decode().strip()

        except Exception as e:
            return False, str(e)

    def _cleanup_temp_files(self):
        """Clean up any remaining temporary files."""
        for temp_file in self.temp_files[:]:  # Copy list to avoid modification during iteration
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    self.logger.debug(f"Cleaned up temp file: {temp_file}")
                self.temp_files.remove(temp_file)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {temp_file}: {e}")

    def _print_summary(self):
        """Print test execution summary."""
        print("\n" + "=" * 80)
        print("STRUCTURED WORKFLOW TEST SUMMARY")
        print("=" * 80)
        print(f"Total Workflows: {self.stats.total_workflows}")
        print(f"Passed: {self.stats.passed}")
        print(f"Failed: {self.stats.failed}")
        print(f"Duration: {self.stats.duration:.2f}s")

        if self.stats.errors:
            print(f"\nFAILED WORKFLOWS ({len(self.stats.errors)}):")
            for error in self.stats.errors:
                print(f"  ❌ {error.workflow_name}: {error.error}")
                if self.verbose:
                    for step in error.step_results:
                        status = "✅" if step["success"] else "❌"
                        print(f"    {status} {step['step']}: {step['duration']:.2f}s")

        if self.stats.passed > 0:
            print(f"\nPASSED WORKFLOWS ({self.stats.passed}):")
            for result in self.results:
                if result.success:
                    print(f"  ✅ {result.workflow_name}: {result.duration:.2f}s")


async def main():
    """Main entry point for structured workflow tests."""
    parser = argparse.ArgumentParser(
        description="Structured JAPI CLI Workflow Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 japi_cli_test_structured.py --target 192.168.1.100
  python3 japi_cli_test_structured.py --target 192.168.1.100 --port 8080 --verbose
  python3 japi_cli_test_structured.py --target 192.168.1.100 --dry-run
        """,
    )

    parser.add_argument("--target", "-t", type=str, required=True, help="Target device IP address")
    parser.add_argument("--port", "-p", type=int, default=80, help="Target device port (default: 80)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Show planned workflows without executing commands")

    args = parser.parse_args()

    # Create structured test runner
    runner = StructuredTestRunner(target=args.target, port=args.port, verbose=args.verbose, dry_run=args.dry_run)

    try:
        stats = await runner.run_all_workflows()
        sys.exit(0 if stats.failed == 0 else 1)

    except KeyboardInterrupt:
        print("\nStructured workflow test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Structured workflow test suite failed: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
