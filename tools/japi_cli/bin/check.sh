#!/usr/bin/env bash
# Code quality check script for japi_cli
# Runs formatting, linting, and type checking

set -e

echo "Running Ruff formatter..."
uv run ruff format .

echo "Running Ruff linter with auto-fix..."
uv run ruff check . --fix

echo "Running Pyright type checker..."
uv run pyright

echo "All checks passed! ✓"
