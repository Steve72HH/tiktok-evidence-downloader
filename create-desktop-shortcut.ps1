$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Launcher = Join-Path $ProjectDir "start-windows.bat"
$AppFile = Join-Path $ProjectDir "tt_evidence_downloader.py"

if (-not (Test-Path $Launcher)) {
    throw "start-windows.bat wurde nicht gefunden: $Launcher"
}

if (-not (Test-Path $AppFile)) {
    throw "tt_evidence_downloader.py wurde nicht gefunden: $AppFile"
}

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "TikTok Evidence Downloader.lnk"

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Launcher
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "TikTok Evidence Downloader starten"
$Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,220"
$Shortcut.Save()

Write-Host "Desktop-Verknuepfung erstellt: $ShortcutPath"
