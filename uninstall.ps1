# l2w uninstaller
#
# Run with:
#   iwr -useb https://raw.githubusercontent.com/Andrew-most-likely/l2w/master/uninstall.ps1 | iex

param(
    [string]$InstallDir = "$env:USERPROFILE\.l2w"
)

Write-Host ""
Write-Host "l2w uninstaller" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan
Write-Host ""

# Remove install directory
if (Test-Path $InstallDir) {
    Remove-Item -Recurse -Force $InstallDir
    Write-Host "Removed $InstallDir" -ForegroundColor Green
} else {
    Write-Host "$InstallDir not found, nothing to remove." -ForegroundColor Gray
}

# Remove from PATH
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$Clean    = ($UserPath -split ";") | Where-Object { $_ -notlike "*\.l2w*" } | Where-Object { $_ -ne "" }
[Environment]::SetEnvironmentVariable("PATH", ($Clean -join ";"), "User")
Write-Host "Removed l2w entries from PATH" -ForegroundColor Green

Write-Host ""
Write-Host "Uninstall complete. Open a new terminal to apply PATH changes." -ForegroundColor Cyan
Write-Host ""
