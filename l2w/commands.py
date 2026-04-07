"""
Command translation table: Linux commands -> Windows equivalents.

Each CommandDef entry contains:
  - windows:     base Windows command string
  - flag_map:    dict mapping Linux flags to Windows flags (empty string = drop the flag)
  - description: human-readable description
  - notes:       optional caveats about the translation

To add a new command, append a new key to COMMAND_MAP.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CommandDef:
    windows: str
    description: str
    flag_map: Dict[str, str] = field(default_factory=dict)
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Core translation table
# ---------------------------------------------------------------------------
COMMAND_MAP: Dict[str, CommandDef] = {
    # --- File / directory listing ---
    "ls": CommandDef(
        windows="dir",
        description="List directory contents",
        flag_map={
            "-l":  "",       # dir already shows details
            "-a":  "/a",     # show hidden files
            "-la": "/a",
            "-al": "/a",
            "-lh": "",       # no direct human-readable size flag
            "-R":  "/s",     # recursive
            "-r":  "/o-n",   # reverse-sort by name
        },
        notes="Windows 'dir' output differs from 'ls' but covers the same use-case.",
    ),

    # --- File operations ---
    "cp": CommandDef(
        windows="copy",
        description="Copy files or directories",
        flag_map={
            "-r":  "",          # handled by xcopy /e /i - see translator special case
            "-R":  "",
            "-f":  "/y",        # force overwrite
            "-i":  "/-y",       # prompt before overwrite
            "-v":  "",          # no direct verbose flag
        },
        notes="Use 'xcopy /e /i' for recursive directory copies.",
    ),
    "mv": CommandDef(
        windows="move",
        description="Move / rename files",
        flag_map={
            "-f": "/y",
            "-i": "/-y",
        },
    ),
    "rm": CommandDef(
        windows="del",
        description="Remove files",
        flag_map={
            "-f":  "/f",        # force
            "-r":  "/s",        # recursive (del /s) - dirs need rmdir
            "-R":  "/s",
            "-rf": "/f /s",
            "-fr": "/f /s",
            "-v":  "",
        },
        notes="For directories use 'rmdir /s /q'. This tool auto-detects dirs.",
    ),
    "mkdir": CommandDef(
        windows="mkdir",
        description="Create directory",
        flag_map={
            "-p": "",           # mkdir on Windows creates intermediate dirs by default
        },
    ),
    "rmdir": CommandDef(
        windows="rmdir /s /q",
        description="Remove directory recursively",
        flag_map={},
    ),
    "touch": CommandDef(
        windows="type nul >",
        description="Create an empty file (or update timestamp)",
        flag_map={},
        notes="Windows 'type nul >' creates the file; updating timestamps requires PowerShell.",
    ),
    "cat": CommandDef(
        windows="type",
        description="Display file contents",
        flag_map={
            "-n": "",           # no direct line-numbering flag in 'type'
        },
    ),
    "more": CommandDef(
        windows="more",
        description="Page through file contents",
        flag_map={},
    ),
    "less": CommandDef(
        windows="more",
        description="Page through file contents (less -> more)",
        flag_map={},
    ),
    "head": CommandDef(
        windows="powershell -Command Get-Content",
        description="Display first N lines of a file",
        flag_map={},
        notes="Append '-TotalCount N' after the filename for first-N-lines behaviour.",
    ),
    "tail": CommandDef(
        windows="powershell -Command Get-Content",
        description="Display last N lines of a file",
        flag_map={
            "-f": "-Wait",      # follow (tail -f)
        },
        notes="Append '-Tail N' after the filename for last-N-lines behaviour.",
    ),

    # --- Search ---
    "grep": CommandDef(
        windows="findstr",
        description="Search text with a pattern",
        flag_map={
            "-i":  "/i",        # case-insensitive
            "-r":  "/s",        # recursive
            "-R":  "/s",
            "-n":  "/n",        # line numbers
            "-v":  "/v",        # invert match
            "-l":  "/m",        # only filenames
            "-E":  "/r",        # extended regex (findstr uses basic regex with /r)
        },
        notes="findstr regex syntax differs from grep. For full regex use PowerShell Select-String.",
    ),
    "find": CommandDef(
        windows="dir /s /b",
        description="Find files recursively",
        flag_map={},
        notes="Linux 'find' has many options not supported by 'dir /s /b'.",
    ),

    # --- Directory navigation ---
    "pwd": CommandDef(
        windows="cd",
        description="Print working directory",
        flag_map={},
    ),
    "cd": CommandDef(
        windows="cd",
        description="Change directory",
        flag_map={},
    ),

    # --- Process management ---
    "ps": CommandDef(
        windows="tasklist",
        description="List running processes",
        flag_map={
            "-e":  "",
            "-ef": "",
            "-aux":"",
        },
    ),
    "kill": CommandDef(
        windows="taskkill /pid",
        description="Kill a process by PID",
        flag_map={
            "-9":  "/f",        # force-kill
            "-15": "",
        },
    ),
    "killall": CommandDef(
        windows="taskkill /im",
        description="Kill processes by name",
        flag_map={
            "-9": "/f",
        },
    ),

    # --- Networking ---
    "ping": CommandDef(
        windows="ping",
        description="Send ICMP echo requests",
        flag_map={
            "-c": "-n",         # count
            "-i": "-i",         # TTL
            "-s": "-l",         # packet size
        },
    ),
    "ifconfig": CommandDef(
        windows="ipconfig",
        description="Display network interfaces",
        flag_map={
            "-a": "/all",
        },
    ),
    "netstat": CommandDef(
        windows="netstat",
        description="Network statistics",
        flag_map={
            "-a": "-a",
            "-n": "-n",
            "-t": "",
            "-p": "-b",
        },
    ),
    "wget": CommandDef(
        windows="curl -O",
        description="Download a file from a URL",
        flag_map={
            "-O": "-o",         # output filename
            "-q": "-s",         # quiet
        },
        notes="curl is available on Windows 10+ natively.",
    ),
    "curl": CommandDef(
        windows="curl",
        description="Transfer data with URLs",
        flag_map={},
    ),
    "ssh": CommandDef(
        windows="ssh",
        description="Secure shell remote login",
        flag_map={},
        notes="OpenSSH is available on Windows 10+.",
    ),
    "scp": CommandDef(
        windows="scp",
        description="Secure copy over SSH",
        flag_map={},
    ),

    # --- System info ---
    "df": CommandDef(
        windows="wmic logicaldisk get size,freespace,caption",
        description="Disk free space",
        flag_map={},
    ),
    "du": CommandDef(
        windows="dir /s",
        description="Disk usage",
        flag_map={},
    ),
    "uname": CommandDef(
        windows="ver",
        description="System/OS version",
        flag_map={
            "-a": "",
            "-r": "",
        },
    ),
    "whoami": CommandDef(
        windows="whoami",
        description="Current user name",
        flag_map={},
    ),
    "hostname": CommandDef(
        windows="hostname",
        description="System hostname",
        flag_map={},
    ),
    "uptime": CommandDef(
        windows='powershell -Command "(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime"',
        description="System uptime",
        flag_map={},
    ),
    "env": CommandDef(
        windows="set",
        description="Display environment variables",
        flag_map={},
    ),
    "printenv": CommandDef(
        windows="set",
        description="Print environment variable",
        flag_map={},
    ),

    # --- Permissions ---
    "chmod": CommandDef(
        windows="icacls",
        description="Change file permissions",
        flag_map={
            "-R": "/t",         # recursive
            "-r": "/t",
        },
        notes="Windows ACL model differs significantly from Unix permissions.",
    ),
    "chown": CommandDef(
        windows="icacls",
        description="Change file owner",
        flag_map={
            "-R": "/t",
        },
        notes="Use 'icacls <file> /setowner <user>'.",
    ),

    # --- Text / output ---
    "echo": CommandDef(
        windows="echo",
        description="Display a line of text",
        flag_map={
            "-n": "",           # suppress newline - not supported natively
            "-e": "",
        },
    ),
    "printf": CommandDef(
        windows="echo",
        description="Formatted output (basic)",
        flag_map={},
        notes="printf formatting is not directly supported by Windows echo.",
    ),
    "sort": CommandDef(
        windows="sort",
        description="Sort lines of text",
        flag_map={
            "-r": "/r",         # reverse
        },
    ),
    "uniq": CommandDef(
        windows='powershell -Command "Get-Unique"',
        description="Filter adjacent duplicate lines",
        flag_map={},
    ),
    "wc": CommandDef(
        windows='powershell -Command "Measure-Object -Line -Word -Character"',
        description="Word / line / character count",
        flag_map={
            "-l": "-Line",
            "-w": "-Word",
            "-c": "-Character",
        },
    ),
    "diff": CommandDef(
        windows="fc",
        description="Compare files line by line",
        flag_map={
            "-u": "",
            "-r": "",
        },
        notes="'fc' output format differs from unified diff.",
    ),

    # --- Misc ---
    "clear": CommandDef(
        windows="cls",
        description="Clear the terminal screen",
        flag_map={},
    ),
    "history": CommandDef(
        windows="doskey /history",
        description="Command history",
        flag_map={},
    ),
    "man": CommandDef(
        windows="help",
        description="Command manual / help",
        flag_map={},
        notes="Windows 'help' covers built-in commands only.",
    ),
    "which": CommandDef(
        windows="where",
        description="Locate a command in PATH",
        flag_map={},
    ),
    "alias": CommandDef(
        windows="doskey",
        description="Create command alias",
        flag_map={},
        notes="doskey macros are session-scoped.",
    ),
    "exit": CommandDef(
        windows="exit",
        description="Exit the shell",
        flag_map={},
    ),
    "date": CommandDef(
        windows="date /t",
        description="Display current date",
        flag_map={},
    ),
    "time": CommandDef(
        windows="time /t",
        description="Display current time",
        flag_map={},
    ),
    "sleep": CommandDef(
        windows="timeout /t",
        description="Sleep for N seconds",
        flag_map={},
        notes="Use 'timeout /t N /nobreak' to suppress key-press interruption.",
    ),
    "tar": CommandDef(
        windows="tar",
        description="Archive files",
        flag_map={
            "-c":  "-c",
            "-x":  "-x",
            "-z":  "-z",
            "-j":  "-j",
            "-v":  "-v",
            "-f":  "-f",
            "-czf": "-czf",
            "-xzf": "-xzf",
        },
        notes="Windows 10 build 17063+ ships with bsdtar.",
    ),
    "zip": CommandDef(
        windows='powershell -Command "Compress-Archive"',
        description="Compress files into a zip archive",
        flag_map={},
    ),
    "unzip": CommandDef(
        windows='powershell -Command "Expand-Archive"',
        description="Extract a zip archive",
        flag_map={},
    ),
    "ln": CommandDef(
        windows="mklink",
        description="Create symbolic / hard links",
        flag_map={
            "-s": "",           # mklink default is symlink for files
        },
        notes="'mklink /d' for directory symlinks; requires elevated privileges.",
    ),
    "mount": CommandDef(
        windows="net use",
        description="Mount a network drive",
        flag_map={},
    ),
    "crontab": CommandDef(
        windows="schtasks",
        description="Scheduled tasks",
        flag_map={
            "-l": "/query",
            "-e": "/create",
            "-r": "/delete",
        },
        notes="Windows Task Scheduler (schtasks) has a different parameter model.",
    ),
}
