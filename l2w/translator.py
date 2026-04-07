"""
Translator module: converts a tokenised Linux command into a Windows command string.

The Translator is intentionally stateless - instantiate once and call translate()
as many times as needed.
"""

import os
import shlex
from typing import List, Optional, Tuple

from .commands import COMMAND_MAP, CommandDef


class TranslationError(Exception):
    """Raised when a command cannot be translated."""


class Translator:
    """Translate a Linux command list into a Windows command string.

    Parameters
    ----------
    extra_map:
        Optional additional CommandDef entries that override or extend COMMAND_MAP.
        Useful for injecting user-defined mappings from a JSON config.
    """

    # Commands that need special-case handling beyond simple flag substitution.
    _SPECIAL = frozenset(["cp", "rm", "touch", "head", "tail", "kill", "killall",
                           "wc", "sleep"])

    def __init__(self, extra_map: Optional[dict] = None):
        self._map = dict(COMMAND_MAP)
        if extra_map:
            self._map.update(extra_map)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate(self, tokens: List[str]) -> str:
        """Return the Windows command string for *tokens*.

        Parameters
        ----------
        tokens:
            Tokenised Linux command, e.g. ``["ls", "-la", "/tmp"]``.

        Returns
        -------
        str
            Windows command string ready to pass to subprocess.

        Raises
        ------
        TranslationError
            If the Linux command has no registered mapping.
        ValueError
            If *tokens* is empty.
        """
        if not tokens:
            raise ValueError("Empty command.")

        linux_cmd = tokens[0]
        args = tokens[1:]

        if linux_cmd not in self._map:
            raise TranslationError(
                f"'{linux_cmd}' is not in the translation table.\n"
                "Run 'l2w --list' to see supported commands."
            )

        defn = self._map[linux_cmd]

        # Route to a special handler when one exists.
        handler = getattr(self, f"_handle_{linux_cmd}", None)
        if handler is not None:
            return handler(defn, args)

        return self._generic_translate(defn, args)

    def supported_commands(self) -> List[str]:
        """Return a sorted list of all supported Linux commands."""
        return sorted(self._map.keys())

    def get_definition(self, linux_cmd: str) -> Optional[CommandDef]:
        return self._map.get(linux_cmd)

    # ------------------------------------------------------------------
    # Generic translation
    # ------------------------------------------------------------------

    def _generic_translate(self, defn: CommandDef, args: List[str]) -> str:
        """Translate flags generically and append remaining positional args."""
        flags, positional = self._split_flags(args)
        win_flags = self._map_flags(defn, flags)
        parts = [defn.windows] + win_flags + positional
        return " ".join(p for p in parts if p)

    @staticmethod
    def _split_flags(args: List[str]) -> Tuple[List[str], List[str]]:
        """Separate flag tokens (starting with '-') from positional arguments."""
        flags, positional = [], []
        for token in args:
            if token.startswith("-"):
                flags.append(token)
            else:
                positional.append(token)
        return flags, positional

    @staticmethod
    def _map_flags(defn: CommandDef, flags: List[str]) -> List[str]:
        """Map a list of Linux flags to Windows flags using defn.flag_map.

        Unknown flags are passed through unchanged so the user can still supply
        Windows-native flags directly.
        """
        win_flags = []
        for flag in flags:
            mapped = defn.flag_map.get(flag)
            if mapped is None:
                # Unknown flag - pass through as-is.
                win_flags.append(flag)
            elif mapped:
                win_flags.append(mapped)
            # mapped == "" means "drop this flag"
        return win_flags

    # ------------------------------------------------------------------
    # Special-case handlers
    # ------------------------------------------------------------------

    def _handle_cp(self, defn: CommandDef, args: List[str]) -> str:
        """Use xcopy for recursive copies, copy for plain file copies."""
        flags, positional = self._split_flags(args)
        recursive = any(f in ("-r", "-R", "-a") for f in flags)
        force = any(f in ("-f",) for f in flags)

        if recursive:
            win_flags = ["/e", "/i"]
            if force:
                win_flags.append("/y")
            return "xcopy " + " ".join(win_flags + positional)

        win_flags = self._map_flags(defn, flags)
        return "copy " + " ".join(w for w in win_flags + positional if w)

    def _handle_rm(self, defn: CommandDef, args: List[str]) -> str:
        """Use rmdir /s /q for recursive removal, del for files."""
        flags, positional = self._split_flags(args)
        recursive = any(f in ("-r", "-R", "-rf", "-fr", "-fr") for f in flags)
        force     = any(f in ("-f", "-rf", "-fr") for f in flags)

        if recursive:
            q_flag = "/q" if force else ""
            parts = ["rmdir", "/s"]
            if q_flag:
                parts.append(q_flag)
            parts.extend(positional)
            return " ".join(p for p in parts if p)

        win_flags = self._map_flags(defn, flags)
        return "del " + " ".join(w for w in win_flags + positional if w)

    def _handle_touch(self, defn: CommandDef, args: List[str]) -> str:
        """Create files with 'type nul > filename'."""
        _, positional = self._split_flags(args)
        if not positional:
            raise TranslationError("touch: missing filename operand.")
        # Create multiple files if needed.
        cmds = [f"type nul > {fname}" for fname in positional]
        return " && ".join(cmds)

    def _handle_head(self, defn: CommandDef, args: List[str]) -> str:
        """Map 'head -n N file' -> PowerShell Get-Content file -TotalCount N."""
        n, files = self._parse_n_flag(args, default=10)
        files_str = " ".join(files) if files else ""
        return f'powershell -Command "Get-Content {files_str} -TotalCount {n}"'

    def _handle_tail(self, defn: CommandDef, args: List[str]) -> str:
        """Map 'tail -n N file' -> PowerShell Get-Content file -Tail N."""
        follow = "-f" in args
        args_clean = [a for a in args if a != "-f"]
        n, files = self._parse_n_flag(args_clean, default=10)
        files_str = " ".join(files) if files else ""
        tail_part = f"-Tail {n}"
        wait_part = " -Wait" if follow else ""
        return f'powershell -Command "Get-Content {files_str} {tail_part}{wait_part}"'

    def _handle_kill(self, defn: CommandDef, args: List[str]) -> str:
        flags, positional = self._split_flags(args)
        force = any(f in ("-9", "-SIGKILL") for f in flags)
        base = "taskkill /pid"
        if force:
            base += " /f"
        return base + " " + " ".join(positional)

    def _handle_killall(self, defn: CommandDef, args: List[str]) -> str:
        flags, positional = self._split_flags(args)
        force = any(f in ("-9", "-SIGKILL") for f in flags)
        base = "taskkill /im"
        if force:
            base += " /f"
        return base + " " + " ".join(positional)

    def _handle_wc(self, defn: CommandDef, args: List[str]) -> str:
        """Map wc flags to PowerShell Measure-Object parameters."""
        flag_map = {"-l": "-Line", "-w": "-Word", "-c": "-Character"}
        flags, positional = self._split_flags(args)
        measure_flags = [flag_map[f] for f in flags if f in flag_map]
        if not measure_flags:
            measure_flags = ["-Line", "-Word", "-Character"]
        files_str = " ".join(positional)
        measure_str = " ".join(measure_flags)
        if files_str:
            return f'powershell -Command "Get-Content {files_str} | Measure-Object {measure_str}"'
        return f'powershell -Command "$input | Measure-Object {measure_str}"'

    def _handle_sleep(self, defn: CommandDef, args: List[str]) -> str:
        """Map 'sleep N' -> 'timeout /t N /nobreak'."""
        _, positional = self._split_flags(args)
        n = positional[0] if positional else "1"
        return f"timeout /t {n} /nobreak"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_n_flag(args: List[str], default: int = 10) -> Tuple[int, List[str]]:
        """Extract -n N (or -N) from args, return (count, remaining_args)."""
        n = default
        remaining = []
        i = 0
        while i < len(args):
            token = args[i]
            if token == "-n" and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                    i += 2
                    continue
                except ValueError:
                    pass
            elif token.startswith("-") and token[1:].isdigit():
                n = int(token[1:])
                i += 1
                continue
            remaining.append(token)
            i += 1
        return n, remaining
