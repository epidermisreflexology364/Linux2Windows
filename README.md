# l2w - Linux to Windows

![CI](https://github.com/Andrew-most-likely/l2w/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

Translate and run Linux commands on Windows. Type `l2w ls -la` and it runs `dir /a`. That's it.

---

## Why

I work in Linux a lot. When I am at my home PC I constantly find myself typing Linux commands out of habit and blanking on the Windows equivalent. At some point I figured it would be easier to just make the most common Linux commands work on Windows rather than keep googling "windows equivalent of ls".

Is this silly? Yes. Am I aware? Also yes. Am I lazy enough to build a whole translation table instead of just learning the commands? Apparently.

---

## Install

**One-liner (recommended) - open PowerShell and run:**
```powershell
iwr -useb https://raw.githubusercontent.com/Andrew-most-likely/l2w/master/install.ps1 | iex
```

This downloads the exe, installs it, generates all the command wrappers, and adds everything to your PATH. Open a new terminal when it finishes and type `ls` directly.

**To uninstall:**
```powershell
iwr -useb https://raw.githubusercontent.com/Andrew-most-likely/l2w/master/uninstall.ps1 | iex
```

---

**Manual install (no Python required):**

Download `l2w.exe` from [Releases](https://github.com/Andrew-most-likely/l2w/releases), copy it to a folder in your PATH, then run:
```
l2w --install-wrappers
```
And add `%USERPROFILE%\.l2w\bin` to your PATH.

**From source:**
```
git clone https://github.com/Andrew-most-likely/l2w.git
cd l2w
pip install -e .
```

---

## Usage

```
l2w <linux-command> [arguments]
```

```
l2w ls -la
l2w ls -a C:\Users

l2w cp file1.txt file2.txt
l2w cp -r src/ dest/

l2w mv old.txt new.txt

l2w rm file.txt
l2w rm -rf build/

l2w grep -i "error" app.log
l2w grep -r "TODO" .

l2w cat README.md
l2w head -n 20 file.txt
l2w tail -f app.log

l2w touch newfile.txt
l2w mkdir myfolder

l2w ps
l2w kill -9 1234

l2w --dry-run rm -rf dist/     # show translated command, do not execute
l2w --show-cmd cp -r src/ dst/ # show translated command then execute
l2w --list                     # list all supported commands
l2w --info grep                # show translation details for a command
```

---

## Supported commands

| Linux | Windows | Notes |
|---|---|---|
| `ls` | `dir` | `-a` maps to `/a` |
| `cp` | `copy` / `xcopy` | auto-switches to `xcopy /e /i` when `-r` is used |
| `mv` | `move` | |
| `rm` | `del` / `rmdir` | auto-switches to `rmdir /s /q` when `-r` is used |
| `mkdir` | `mkdir` | |
| `rmdir` | `rmdir /s /q` | |
| `touch` | `type nul >` | |
| `cat` | `type` | |
| `less` / `more` | `more` | |
| `head` | `Get-Content -TotalCount N` | |
| `tail` | `Get-Content -Tail N` | `-f` maps to `-Wait` |
| `grep` | `findstr` | |
| `find` | `dir /s /b` | |
| `pwd` | `cd` | |
| `echo` | `echo` | |
| `clear` | `cls` | |
| `ps` | `tasklist` | |
| `kill` | `taskkill /pid` | `-9` maps to `/f` |
| `killall` | `taskkill /im` | |
| `ping` | `ping` | `-c` maps to `-n` |
| `ifconfig` | `ipconfig` | |
| `netstat` | `netstat` | |
| `wget` | `curl -O` | |
| `curl` | `curl` | |
| `ssh` / `scp` | `ssh` / `scp` | Windows 10+ OpenSSH |
| `df` | `wmic logicaldisk ...` | |
| `chmod` | `icacls` | |
| `chown` | `icacls` | |
| `sort` | `sort` | |
| `diff` | `fc` | |
| `wc` | `Measure-Object` | |
| `sleep` | `timeout /t` | |
| `tar` | `tar` | Windows 10 build 17063+ |
| `zip` / `unzip` | `Compress-Archive` / `Expand-Archive` | |
| `which` | `where` | |
| `whoami` | `whoami` | |
| `man` | `help` | |
| `env` | `set` | |
| `history` | `doskey /history` | |
| `uname` | `ver` | |
| `ln` | `mklink` | |

Run `l2w --list` for the full list.

---

## Flags

| Flag | Description |
|---|---|
| `--dry-run`, `-n` | Print translated command without executing |
| `--show-cmd`, `-s` | Print translated command then execute |
| `--list`, `-l` | List all supported Linux commands |
| `--info CMD`, `-i CMD` | Show translation details for a command |
| `--config FILE`, `-c FILE` | Load custom command mappings from a JSON file |

---

## Custom commands

Add or override mappings without touching the source. Create `config/commands.json` (already included) or `~/.l2w/commands.json`:

```json
{
  "commands": {
    "ll": {
      "windows": "dir /a",
      "description": "Long listing alias",
      "flag_map": {}
    }
  }
}
```

Then run:
```
l2w --config ~/.l2w/commands.json ll
```

Or place the file at `~/.l2w/commands.json` and it will be picked up automatically.

---

## Project structure

```
l2w/
├── l2w/
│   ├── commands.py       # translation table (add new commands here)
│   ├── translator.py     # translation logic
│   ├── executor.py       # subprocess runner
│   ├── cli.py            # argparse CLI
│   └── config_loader.py  # JSON config support
├── config/
│   └── commands.json     # user-editable overrides
├── tests/
│   └── test_translator.py
├── main.py               # entry point
├── setup.py
├── build.bat             # builds dist\l2w.exe via PyInstaller
└── requirements.txt
```

---

## Adding a new command

Open `l2w/commands.py` and add an entry to `COMMAND_MAP`:

```python
"mycommand": CommandDef(
    windows="MyWindowsCmd.exe",
    description="What it does",
    flag_map={
        "-v": "/verbose",
        "-f": "/force",
    },
    notes="Optional caveats.",
),
```

For commands with complex argument handling, add a `_handle_mycommand` method to the `Translator` class in `translator.py`.

---

## Running tests

```
pip install pytest
pytest tests/ -v
```

---

## License

MIT - see [LICENSE](LICENSE).
