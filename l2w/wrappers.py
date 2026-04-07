"""
Wrapper generator: creates .bat files for every supported command so the user
can type 'ls' instead of 'l2w ls'.

Each wrapper is a one-liner that forwards all arguments to l2w:

    ls.bat  ->  @l2w ls %*

Usage (from the CLI):
    l2w --install-wrappers              installs to default dir (~/.l2w/bin)
    l2w --install-wrappers C:\bin       installs to a custom directory

The target directory must be in PATH for the wrappers to work everywhere.
"""

import os
import sys
from typing import List, Tuple


# Commands that clash with real Windows built-ins that should NOT be shadowed.
# Users can override this by editing the list below.
_SKIP = {
    "cd",       # built-in - shadowing it breaks navigation
    "echo",     # built-in
    "exit",     # built-in
    "date",     # built-in
    "time",     # built-in
    "sort",     # real Windows command, identical name
    "more",     # real Windows command, identical name
    "curl",     # available natively on Win10+ with the same name
    "ssh",      # available natively on Win10+ with the same name
    "scp",      # available natively on Win10+ with the same name
    "tar",      # available natively on Win10+ with the same name
    "ping",     # real Windows command, identical name
    "netstat",  # real Windows command, identical name
    "hostname", # real Windows command, identical name
    "whoami",   # real Windows command, identical name
}

_DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".l2w", "bin")


def install_wrappers(
    target_dir: str,
    commands: List[str],
    force: bool = False,
) -> Tuple[int, int]:
    """Write .bat wrapper files into *target_dir*.

    Returns (created, skipped) counts.
    """
    os.makedirs(target_dir, exist_ok=True)

    created = 0
    skipped_list = []

    for cmd in commands:
        if cmd in _SKIP:
            skipped_list.append(cmd)
            continue

        bat_path = os.path.join(target_dir, f"{cmd}.bat")

        if os.path.exists(bat_path) and not force:
            skipped_list.append(cmd)
            continue

        with open(bat_path, "w") as fh:
            fh.write(f"@l2w {cmd} %*\n")

        created += 1

    return created, len(skipped_list)


def print_path_instructions(target_dir: str) -> None:
    """Print instructions for adding target_dir to PATH."""
    print()
    print("To use the wrappers, add the following directory to your PATH:")
    print()
    print(f"  {target_dir}")
    print()
    print("Option 1 - permanent (run once in an elevated PowerShell):")
    print()
    print(f'  [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";{target_dir}", "User")')
    print()
    print("Option 2 - current session only (cmd.exe):")
    print()
    print(f"  set PATH=%PATH%;{target_dir}")
    print()
    print("After adding to PATH, open a new terminal and type 'ls' to test.")
    print()
