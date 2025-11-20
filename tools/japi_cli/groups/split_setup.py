#!/usr/bin/env python3
"""Split setup.py into manageable modules."""

# Read the original file
with open("setup.py") as f:
    content = f.read()
    lines = content.split("\n")

# Define section markers and their target files
sections = {
    "input": {
        "start_marker": "# INPUT COMMAND IMPLEMENTATIONS",
        "end_marker": "# SPEAKER MAIN LAYER COMMAND IMPLEMENTATIONS",
        "file": "setup_commands/input.py",
    },
    "speaker": {
        "start_marker": "# SPEAKER MAIN LAYER COMMAND IMPLEMENTATIONS",
        "end_marker": "# SUMMING MATRIX COMMAND IMPLEMENTATIONS",
        "file": "setup_commands/speaker.py",
    },
    "matrix": {
        "start_marker": "# SUMMING MATRIX COMMAND IMPLEMENTATIONS",
        "end_marker": "# INSTALL INFO COMMAND IMPLEMENTATIONS",
        "file": "setup_commands/matrix.py",
    },
    "system": {
        "start_marker": "# INSTALL INFO COMMAND IMPLEMENTATIONS",
        "end_marker": "# FLATTENED SET COMMAND IMPLEMENTATIONS",
        "file": "setup_commands/system.py",
    },
}

# Find section boundaries
section_lines = {}
for name, info in sections.items():
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if info["start_marker"] in line:
            start_idx = i
        if info["end_marker"] in line and start_idx is not None:
            end_idx = i
            break

    if start_idx and end_idx:
        section_lines[name] = (start_idx, end_idx)
        print(f"{name}: lines {start_idx}-{end_idx} ({end_idx - start_idx} lines)")

print(f"\nTotal lines in file: {len(lines)}")
print("Run this script with 'execute' argument to create the split files")
