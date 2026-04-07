@echo off
REM ============================================================
REM  build.bat - Build the l2w standalone Windows executable
REM  using PyInstaller.
REM
REM  Prerequisites:
REM    pip install pyinstaller
REM
REM  Output:
REM    dist\l2w.exe   (single self-contained executable)
REM ============================================================

setlocal

REM -- Ensure PyInstaller is available --
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not found.  Run:  pip install pyinstaller
    exit /b 1
)

echo [l2w] Cleaning previous build artefacts...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist l2w.spec del /f l2w.spec

echo [l2w] Building standalone executable...
pyinstaller ^
    --onefile ^
    --console ^
    --name l2w ^
    --add-data "config/commands.json;config" ^
    main.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

echo.
echo [l2w] Build successful!
echo       Executable: dist\l2w.exe
echo.
echo  To install system-wide, copy dist\l2w.exe to a directory in your PATH.
echo  Example:
echo    copy dist\l2w.exe C:\Windows\System32\l2w.exe
echo.

endlocal
