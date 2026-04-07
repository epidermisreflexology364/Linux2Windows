# l2w installer
# Installs l2w.exe and creates Linux command wrappers on Windows.
#
# Run with:
#   iwr -useb https://raw.githubusercontent.com/Andrew-most-likely/l2w/master/install.ps1 | iex

param(
    [string]$InstallDir = "$env:USERPROFILE\.l2w",
    [string]$WrapperDir = "$env:USERPROFILE\.l2w\bin"
)

$ErrorActionPreference = "Stop"
$Repo    = "Andrew-most-likely/l2w"
$ExeName = "l2w.exe"

Write-Host ""
Write-Host "l2w installer" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------
# 1. Create install directory
# -----------------------------------------------------------------------
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}
if (-not (Test-Path $WrapperDir)) {
    New-Item -ItemType Directory -Path $WrapperDir | Out-Null
}

# -----------------------------------------------------------------------
# 2. Download latest release
# -----------------------------------------------------------------------
Write-Host "Fetching latest release from GitHub..." -ForegroundColor Yellow

$ReleaseUrl = "https://api.github.com/repos/$Repo/releases/latest"
$Release    = Invoke-RestMethod -Uri $ReleaseUrl -UseBasicParsing
$Asset      = $Release.assets | Where-Object { $_.name -eq $ExeName } | Select-Object -First 1

if (-not $Asset) {
    Write-Host "ERROR: Could not find $ExeName in the latest release." -ForegroundColor Red
    exit 1
}

$ExeDest = Join-Path $InstallDir $ExeName
Write-Host "Downloading $ExeName $($Release.tag_name)..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $Asset.browser_download_url -OutFile $ExeDest -UseBasicParsing
Write-Host "Saved to $ExeDest" -ForegroundColor Green

# -----------------------------------------------------------------------
# 3. Add InstallDir to PATH (so 'l2w' itself is found)
# -----------------------------------------------------------------------
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")

if ($UserPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
    Write-Host "Added $InstallDir to PATH" -ForegroundColor Green
} else {
    Write-Host "$InstallDir already in PATH" -ForegroundColor Gray
}

# -----------------------------------------------------------------------
# 4. Generate command wrappers
# -----------------------------------------------------------------------
Write-Host "Installing command wrappers to $WrapperDir..." -ForegroundColor Yellow
& $ExeDest --install-wrappers $WrapperDir

# -----------------------------------------------------------------------
# 5. Add WrapperDir to PATH (so 'ls', 'grep' etc. are found)
# -----------------------------------------------------------------------
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")

if ($UserPath -notlike "*$WrapperDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$WrapperDir", "User")
    Write-Host "Added $WrapperDir to PATH" -ForegroundColor Green
} else {
    Write-Host "$WrapperDir already in PATH" -ForegroundColor Gray
}

# -----------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------
Write-Host ""
Write-Host "Done! Open a new terminal and try:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ls -la" -ForegroundColor White
Write-Host "  grep -i error app.log" -ForegroundColor White
Write-Host "  rm -rf build/" -ForegroundColor White
Write-Host ""
Write-Host "To uninstall, run:" -ForegroundColor Gray
Write-Host "  iwr -useb https://raw.githubusercontent.com/Andrew-most-likely/l2w/master/uninstall.ps1 | iex" -ForegroundColor Gray
Write-Host ""
