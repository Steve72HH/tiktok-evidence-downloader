$ErrorActionPreference = "Stop"
py -m pip install -U yt-dlp
Write-Host ""
Write-Host "yt-dlp ist installiert oder aktualisiert."
Write-Host ""
Write-Host "Optional fuer Transkription:"
Write-Host "  py -m pip install -U openai-whisper"
Write-Host "  winget install Gyan.FFmpeg"
Write-Host "Starte die App danach mit: .\start-windows.bat"
