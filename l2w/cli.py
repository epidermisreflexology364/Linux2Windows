"""
CLI entry point for l2w (Linux-to-Windows command translator).

Usage examples
--------------
  l2w ls -la /tmp
  l2w cp -r src/ dest/
  l2w rm -rf build/
  l2w grep -i "error" logfile.txt
  l2w --dry-run mv old.txt new.txt
  l2w --list
  l2w --info grep
  l2w --config ~/my_commands.json ls
"""

import argparse
import sys
from typing import List, Optional

from .config_loader import load_config
from .executor import Executor
from .translator import TranslationError, Translator
from .wrappers import _DEFAULT_DIR, install_wrappers, print_path_instructions


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="l2w",
        description="Translate and execute Linux commands on Windows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  l2w ls -la\n"
            "  l2w cp -r src/ dest/\n"
            "  l2w grep -i 'error' app.log\n"
            "  l2w --dry-run rm -rf build/\n"
            "  l2w --list\n"
            "  l2w --info grep\n"
        ),
    )

    # Meta-commands (mutually exclusive with running a Linux command)
    meta = parser.add_argument_group("informational flags")
    meta.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all supported Linux commands and exit.",
    )
    meta.add_argument(
        "--info", "-i",
        metavar="CMD",
        help="Show translation details for a specific Linux command.",
    )
    meta.add_argument(
        "--install-wrappers",
        metavar="DIR",
        nargs="?",
        const="",
        help=(
            "Generate .bat wrapper files so you can type 'ls' instead of 'l2w ls'. "
            "Optionally specify a target directory (default: ~/.l2w/bin)."
        ),
    )
    meta.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing wrapper files when used with --install-wrappers.",
    )

    # Execution modifiers
    run_group = parser.add_argument_group("execution options")
    run_group.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Print the translated Windows command without executing it.",
    )
    run_group.add_argument(
        "--show-cmd", "-s",
        action="store_true",
        help="Print the translated Windows command before executing it.",
    )
    run_group.add_argument(
        "--config", "-c",
        metavar="FILE",
        help="Path to a JSON file with custom command mappings.",
    )

    # The Linux command + its arguments - captured with REMAINDER so flags
    # intended for the Linux command are not consumed by argparse.
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Linux command and its arguments (e.g. ls -la /tmp).",
    )

    return parser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_list(translator: Translator) -> None:
    cmds = translator.supported_commands()
    col_width = max(len(c) for c in cmds) + 2
    print(f"\n{'Linux command':<{col_width}}  Windows equivalent")
    print("-" * 60)
    for cmd in cmds:
        defn = translator.get_definition(cmd)
        print(f"  {cmd:<{col_width - 2}}  {defn.windows}")
    print(f"\nTotal: {len(cmds)} commands supported.\n")


def _print_info(translator: Translator, cmd: str) -> None:
    defn = translator.get_definition(cmd)
    if defn is None:
        print(f"l2w: '{cmd}' is not in the translation table.")
        sys.exit(1)

    print(f"\nLinux command : {cmd}")
    print(f"Windows cmd   : {defn.windows}")
    print(f"Description   : {defn.description}")
    if defn.flag_map:
        print("Flag mappings :")
        for lf, wf in defn.flag_map.items():
            wf_display = wf if wf else "(dropped)"
            print(f"  {lf:<10}  ->  {wf_display}")
    if defn.notes:
        print(f"Notes         : {defn.notes}")
    print()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Load extra mappings from config (if any).
    extra_map = load_config(args.config)
    translator = Translator(extra_map=extra_map or None)

    # --- Informational sub-commands ---
    if args.list:
        _print_list(translator)
        return 0

    if args.info:
        _print_info(translator, args.info)
        return 0

    if args.install_wrappers is not None:
        target = args.install_wrappers.strip() or _DEFAULT_DIR
        commands = translator.supported_commands()
        created, skipped = install_wrappers(target, commands, force=args.force)
        print(f"Installed {created} wrapper(s) to: {target}")
        if skipped:
            print(f"Skipped {skipped} (already exist or are built-in Windows commands).")
        print_path_instructions(target)
        return 0

    # --- Translate & run ---
    tokens = args.command
    if not tokens:
        parser.print_help()
        return 0

    try:
        windows_cmd = translator.translate(tokens)
    except TranslationError as exc:
        print(f"l2w: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"l2w: {exc}", file=sys.stderr)
        return 1

    if args.show_cmd or args.dry_run:
        print(f"[cmd] {windows_cmd}")

    if args.dry_run:
        return 0

    executor = Executor()
    result = executor.run(windows_cmd)
    return result.returncode if result is not None else 0


def entry_point() -> None:
    """Setuptools / PyInstaller entry point."""
    sys.exit(main())


if __name__ == "__main__":
    entry_point()
