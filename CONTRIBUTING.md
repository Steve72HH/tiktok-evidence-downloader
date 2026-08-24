# Contributing

Danke fuer dein Interesse an diesem Projekt.

## Entwicklung

```powershell
py -m pip install -r requirements.txt
py -m py_compile tt_evidence_downloader.py
py .\tt_evidence_downloader.py
```

Optionale Transkription:

```powershell
py -m pip install -r requirements-transcription.txt
winget install Gyan.FFmpeg
```

## Pull Requests

- Keine heruntergeladenen Videos, Transkripte, Logs oder privaten URLs committen.
- Aenderungen klein und nachvollziehbar halten.
- Vor dem Commit mindestens `py -m py_compile tt_evidence_downloader.py` ausfuehren.
