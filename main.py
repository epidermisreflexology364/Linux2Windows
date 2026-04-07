"""
Top-level entry point - used by PyInstaller and direct invocation.

    python main.py ls -la
    python main.py --dry-run cp -r src/ dest/
"""

import os
import shutil
import sys


_INSTALL_DIR  = os.path.join(os.path.expanduser("~"), ".l2w")
_WRAPPER_DIR  = os.path.join(_INSTALL_DIR, "bin")
_EXE_DEST     = os.path.join(_INSTALL_DIR, "l2w.exe")


def _already_installed() -> bool:
    """True if this exe is already running from the install location."""
    try:
        return os.path.abspath(sys.executable) == os.path.abspath(_EXE_DEST)
    except Exception:
        return False


def _add_to_path(directory: str) -> bool:
    """Add *directory* to the user PATH in the registry. Returns True if changed."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            current, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current = ""

        parts = [p for p in current.split(";") if p]
        if directory.lower() in [p.lower() for p in parts]:
            winreg.CloseKey(key)
            return False

        parts.append(directory)
        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
        winreg.CloseKey(key)

        # Broadcast WM_SETTINGCHANGE so open terminals can pick up the change.
        try:
            import ctypes
            HWND_BROADCAST  = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 2, 5000, None
            )
        except Exception:
            pass

        return True
    except Exception:
        return False


def _self_install() -> None:
    """Copy this exe to ~/.l2w/, generate wrappers, and add both dirs to PATH."""
    frozen = getattr(sys, "frozen", False)

    print("l2w - Linux to Windows command translator")
    print("=" * 45)
    print()
    print("First run detected. Installing now...")
    print()

    # 1. Create install directory and copy exe.
    os.makedirs(_INSTALL_DIR, exist_ok=True)
    os.makedirs(_WRAPPER_DIR, exist_ok=True)

    if frozen:
        src = sys.executable
        if os.path.abspath(src) != os.path.abspath(_EXE_DEST):
            shutil.copy2(src, _EXE_DEST)
            print(f"  Installed l2w.exe  ->  {_EXE_DEST}")
        else:
            print(f"  l2w.exe already at {_EXE_DEST}")

    # 2. Generate wrapper .bat files.
    from l2w.translator import Translator
    from l2w.wrappers import install_wrappers
    t = Translator()
    created, skipped = install_wrappers(_WRAPPER_DIR, t.supported_commands(), force=True)
    print(f"  Created {created} command wrappers  ->  {_WRAPPER_DIR}")

    # 3. Add both directories to PATH.
    changed1 = _add_to_path(_INSTALL_DIR)
    changed2 = _add_to_path(_WRAPPER_DIR)

    if changed1 or changed2:
        print("  Updated PATH")
    else:
        print("  PATH already configured")

    print()
    print("Done! Open a new Command Prompt or PowerShell and type:")
    print()
    print("  ls")
    print("  grep -i error app.log")
    print("  rm -rf build/")
    print()
    print("No 'l2w' prefix needed.")
    print()
    input("Press Enter to close...")


def main():
    frozen = getattr(sys, "frozen", False)

    # No arguments = run as installer (first run or re-run without a shell).
    if frozen and len(sys.argv) == 1:
        try:
            _self_install()
        except Exception as exc:
            print(f"\nInstall failed: {exc}", file=sys.stderr)
            print("Please report this at https://github.com/Andrew-most-likely/l2w/issues",
                  file=sys.stderr)
            input("\nPress Enter to close...")
        return

    try:
        from l2w.cli import entry_point
        entry_point()
    except Exception as exc:
        print(f"\nl2w crashed: {exc}", file=sys.stderr)
        print("Please report this at https://github.com/Andrew-most-likely/l2w/issues",
              file=sys.stderr)
        if frozen:
            input("\nPress Enter to close...")
        sys.exit(1)


if __name__ == "__main__":
    main()
