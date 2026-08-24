# TikTok Evidence Downloader

Kleine Desktop-App zum lokalen Sichern von TikTok-Videos, einzeln oder als Batchliste.

## Funktionen

- Desktop-Oberflaeche mit Tkinter
- Einzel- und Batchdownload von TikTok-URLs
- Zielordner frei waehlbar
- optional Metadaten-JSON und Thumbnails
- optional lokale Transkription mit Whisper
- Download-Archiv gegen doppelte Downloads
- CSV-Protokoll fuer Nachvollziehbarkeit

## Zweck

Die App ist fuer rechtssichere Eigen-Dokumentation gedacht: Videos werden lokal in einem Zielordner gespeichert, dazu wird ein Download-Protokoll geschrieben. Bitte nutze sie nur fuer Inhalte, die du rechtlich sichern darfst, und veraendere Originaldateien fuer Beweiszwecke nicht.

## Voraussetzungen

- Python 3.10 oder neuer
- `yt-dlp`
- Optional fuer Transkription: `openai-whisper`
- Optional fuer Transkription: `ffmpeg`

Installation unter Windows PowerShell:

```powershell
py -m pip install -r requirements.txt
```

Optional mit Whisper-Transkription:

```powershell
py -m pip install -U openai-whisper
winget install Gyan.FFmpeg
```

Installation unter Debian:

```bash
python3 -m pip install -r requirements.txt
```

Optional mit Whisper-Transkription:

```bash
python3 -m pip install -U openai-whisper
sudo apt install ffmpeg
```

## Start

Windows:

```powershell
.\start-windows.bat
```

Debian:

```bash
python3 ./tt_evidence_downloader.py
```

## Nutzung

1. TikTok-URLs in das Textfeld einfuegen, eine URL pro Zeile.
2. Zielordner auswaehlen.
3. Optional `Metadaten-JSON speichern` aktiviert lassen.
4. Optional `Transkription mit Whisper` aktivieren und Modell waehlen.
5. `Download starten` klicken.

Die App speichert Videos mit Zeitstempel und TikTok-ID im Dateinamen. Im Zielordner entsteht ausserdem `download-log.csv`.
Transkripte werden im Unterordner `transcripts` als `.txt` gespeichert.

## Whisper-Modellwahl

- `tiny` und `base`: schnell, aber weniger genau.
- `small`: guter Standard fuer viele deutsche TikTok-Videos.
- `medium`: genauer, braucht mehr Zeit und Leistung.
- `large`: beste Genauigkeit, aber langsam und ressourcenhungrig.

## Hinweise fuer Beweissicherung

- Sichere zusaetzlich Screenshots der Profilseite, Videoseite, Kommentare und des Upload-Datums.
- Notiere Fundzeitpunkt, TikTok-URL, Benutzername und kurzen Kontext.
- Arbeite mit Kopien und bewahre die Originaldateien unveraendert auf.
- Bei strafrechtlich relevanten Inhalten: nicht weiterverbreiten, sondern nur dokumentieren und melden.

## Rechtlicher Hinweis

Dieses Tool laedt nur Inhalte ueber die von `yt-dlp` unterstuetzten Quellen herunter. Es umgeht keine Zugangsbeschraenkungen und ersetzt keine rechtliche Beratung. Beachte Urheberrecht, Plattformbedingungen, Datenschutz und Strafrecht.
