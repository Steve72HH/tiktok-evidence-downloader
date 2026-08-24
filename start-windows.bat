@echo off
setlocal
cd /d "%~dp0"
py tt_evidence_downloader.py
if errorlevel 1 pause
