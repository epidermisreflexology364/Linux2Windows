"""
Executor module: runs a translated Windows command string in a subprocess.
"""

import subprocess
import sys
from typing import Optional


class ExecutionResult:
    """Holds the outcome of a command execution."""

    def __init__(self, returncode: int, stdout: str, stderr: str, command: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command

    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __repr__(self) -> str:
        return (
            f"ExecutionResult(returncode={self.returncode!r}, "
            f"command={self.command!r})"
        )


class Executor:
    """Execute translated Windows commands.

    Parameters
    ----------
    dry_run:
        When True, print the command but do not execute it.
    capture:
        When True, capture stdout/stderr instead of streaming them to the
        terminal. Useful for programmatic use; default is False (streaming).
    shell:
        Pass the command to cmd.exe /c. Required for built-in shell commands
        like 'dir', 'cls', 'type', etc. Defaults to True.
    """

    def __init__(
        self,
        dry_run: bool = False,
        capture: bool = False,
        shell: bool = True,
    ):
        self.dry_run = dry_run
        self.capture = capture
        self.shell = shell

    def run(self, windows_cmd: str) -> Optional[ExecutionResult]:
        """Execute *windows_cmd*.

        In dry-run mode, prints the command and returns None.
        Otherwise returns an :class:`ExecutionResult`.
        """
        if self.dry_run:
            print(f"[dry-run] {windows_cmd}")
            return None

        try:
            if self.capture:
                proc = subprocess.run(
                    windows_cmd,
                    shell=self.shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                return ExecutionResult(
                    returncode=proc.returncode,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                    command=windows_cmd,
                )
            else:
                # Stream output directly to the terminal.
                proc = subprocess.run(
                    windows_cmd,
                    shell=self.shell,
                )
                return ExecutionResult(
                    returncode=proc.returncode,
                    stdout="",
                    stderr="",
                    command=windows_cmd,
                )
        except FileNotFoundError:
            print(
                f"l2w: command not found: '{windows_cmd.split()[0]}'\n"
                "Make sure the Windows command is available in your PATH.",
                file=sys.stderr,
            )
            return ExecutionResult(returncode=127, stdout="", stderr="", command=windows_cmd)
        except Exception as exc:
            print(f"l2w: unexpected error while running '{windows_cmd}': {exc}",
                  file=sys.stderr)
            return ExecutionResult(returncode=1, stdout="", stderr="", command=windows_cmd)
