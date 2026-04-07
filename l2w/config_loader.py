"""
Config loader: merges user-defined command mappings (JSON) into the translation table.

Expected JSON format
--------------------
{
  "commands": {
    "mycmd": {
      "windows": "MyWindowsCmd.exe",
      "description": "My custom command",
      "flag_map": {"-v": "/verbose"},
      "notes": "Optional notes string"
    }
  }
}

Any key under "commands" that matches a built-in command will *override* it.
New keys extend the table.
"""

import json
import os
import sys
from typing import Dict, Optional

from .commands import CommandDef


_DEFAULT_CONFIG_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "config", "commands.json"),
    os.path.join(os.path.expanduser("~"), ".l2w", "commands.json"),
]


def load_config(path: Optional[str] = None) -> Dict[str, CommandDef]:
    """Load user command overrides from a JSON config file.

    Parameters
    ----------
    path:
        Explicit path to a JSON config file.  If None, the function tries
        the default locations listed in ``_DEFAULT_CONFIG_PATHS``.

    Returns
    -------
    dict
        Mapping of Linux command name -> CommandDef, containing only the
        entries defined in the config file.  Returns an empty dict if no
        config file is found or if the file is empty.
    """
    config_path = _resolve_path(path)
    if config_path is None:
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"l2w: invalid JSON in config file '{config_path}': {exc}",
              file=sys.stderr)
        return {}
    except OSError as exc:
        print(f"l2w: cannot read config file '{config_path}': {exc}",
              file=sys.stderr)
        return {}

    commands_raw = raw.get("commands", {})
    if not isinstance(commands_raw, dict):
        print("l2w: 'commands' key in config must be a JSON object.", file=sys.stderr)
        return {}

    extra: Dict[str, CommandDef] = {}
    for name, entry in commands_raw.items():
        if not isinstance(entry, dict):
            print(f"l2w: config entry for '{name}' must be a JSON object - skipping.",
                  file=sys.stderr)
            continue
        windows = entry.get("windows")
        if not windows:
            print(f"l2w: config entry '{name}' missing 'windows' key - skipping.",
                  file=sys.stderr)
            continue
        extra[name] = CommandDef(
            windows=windows,
            description=entry.get("description", f"User-defined: {name}"),
            flag_map=entry.get("flag_map", {}),
            notes=entry.get("notes"),
        )

    return extra


def _resolve_path(explicit: Optional[str]) -> Optional[str]:
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        print(f"l2w: config file not found: '{explicit}'", file=sys.stderr)
        return None

    for candidate in _DEFAULT_CONFIG_PATHS:
        if os.path.isfile(candidate):
            return candidate

    return None
