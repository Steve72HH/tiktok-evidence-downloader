#!/usr/bin/env python3
"""
Small Tkinter desktop app for saving TikTok videos via yt-dlp.

The app intentionally keeps the UI and dependencies simple so it can run on
Windows and Linux admin workstations.
"""

from __future__ import annotations

import csv
import datetime as dt
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "TikTok Evidence Downloader"


class DownloadApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x680")
        self.minsize(760, 560)

        self.output_dir = tk.StringVar(value=str(Path.home() / "Downloads" / "tiktok-evidence"))
        self.save_metadata = tk.BooleanVar(value=True)
        self.write_thumbnails = tk.BooleanVar(value=True)
        self.download_archive = tk.BooleanVar(value=True)
        self.transcribe_audio = tk.BooleanVar(value=False)
        self.whisper_model = tk.StringVar(value="small")
        self.running = False
        self.worker: threading.Thread | None = None
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()

        self._build_ui()
        self.after(100, self._poll_events)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=12)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Zielordner").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(top, textvariable=self.output_dir).grid(row=0, column=1, sticky="ew")
        ttk.Button(top, text="Auswaehlen", command=self._choose_folder).grid(row=0, column=2, padx=(8, 0))

        options = ttk.Frame(top)
        options.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Checkbutton(options, text="Metadaten-JSON speichern", variable=self.save_metadata).grid(row=0, column=0, padx=(0, 16))
        ttk.Checkbutton(options, text="Thumbnail speichern", variable=self.write_thumbnails).grid(row=0, column=1, padx=(0, 16))
        ttk.Checkbutton(options, text="Bereits geladene URLs ueberspringen", variable=self.download_archive).grid(row=0, column=2)

        transcript_options = ttk.Frame(top)
        transcript_options.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))
        ttk.Checkbutton(transcript_options, text="Transkription mit Whisper", variable=self.transcribe_audio).grid(row=0, column=0, padx=(0, 12))
        ttk.Label(transcript_options, text="Modell").grid(row=0, column=1, padx=(0, 6))
        model_select = ttk.Combobox(
            transcript_options,
            textvariable=self.whisper_model,
            values=("tiny", "base", "small", "medium", "large"),
            width=10,
            state="readonly",
        )
        model_select.grid(row=0, column=2)

        body = ttk.PanedWindow(self, orient=tk.VERTICAL)
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        urls_frame = ttk.LabelFrame(body, text="TikTok-URLs, eine pro Zeile", padding=8)
        urls_frame.rowconfigure(0, weight=1)
        urls_frame.columnconfigure(0, weight=1)
        self.urls = tk.Text(urls_frame, height=12, wrap="word", undo=True)
        self.urls.grid(row=0, column=0, sticky="nsew")
        urls_scroll = ttk.Scrollbar(urls_frame, command=self.urls.yview)
        urls_scroll.grid(row=0, column=1, sticky="ns")
        self.urls.configure(yscrollcommand=urls_scroll.set)
        body.add(urls_frame, weight=2)

        log_frame = ttk.LabelFrame(body, text="Protokoll", padding=8)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log = tk.Text(log_frame, height=14, wrap="word", state="disabled")
        self.log.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=log_scroll.set)
        body.add(log_frame, weight=3)

        bottom = ttk.Frame(self, padding=(12, 0, 12, 12))
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.start_button = ttk.Button(bottom, text="Download starten", command=self._start_downloads)
        self.start_button.grid(row=0, column=1)

    def _choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir.get() or str(Path.home()))
        if selected:
            self.output_dir.set(selected)

    def _start_downloads(self) -> None:
        if self.running:
            return

        yt_dlp = shutil.which("yt-dlp")
        if yt_dlp is None:
            messagebox.showerror(
                APP_TITLE,
                "yt-dlp wurde nicht gefunden.\n\nInstalliere es mit:\npy -m pip install -U yt-dlp",
            )
            return

        whisper = shutil.which("whisper")
        if self.transcribe_audio.get() and whisper is None:
            messagebox.showerror(
                APP_TITLE,
                "Whisper wurde nicht gefunden.\n\nInstalliere es mit:\npy -m pip install -U openai-whisper\n\nZusaetzlich wird ffmpeg benoetigt.",
            )
            return

        urls = self._get_urls()
        if not urls:
            messagebox.showwarning(APP_TITLE, "Bitte mindestens eine TikTok-URL einfuegen.")
            return

        target = Path(self.output_dir.get()).expanduser()
        target.mkdir(parents=True, exist_ok=True)

        self.running = True
        self.start_button.configure(state="disabled")
        self.progress.start(12)
        self._append_log(f"Starte Download von {len(urls)} URL(s) nach: {target}")

        self.worker = threading.Thread(
            target=self._download_worker,
            args=(yt_dlp, whisper, urls, target),
            daemon=True,
        )
        self.worker.start()

    def _get_urls(self) -> list[str]:
        raw = self.urls.get("1.0", "end").splitlines()
        urls: list[str] = []
        seen: set[str] = set()
        for line in raw:
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            if value not in seen:
                urls.append(value)
                seen.add(value)
        return urls

    def _download_worker(self, yt_dlp: str, whisper: str | None, urls: list[str], target: Path) -> None:
        log_path = target / "download-log.csv"
        archive_path = target / "download-archive.txt"
        transcribe = self.transcribe_audio.get()

        with log_path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            if log_path.stat().st_size == 0:
                writer.writerow(["timestamp_utc", "status", "url", "return_code", "transcript_status"])

            for index, url in enumerate(urls, start=1):
                self.events.put(("log", f"[{index}/{len(urls)}] Lade: {url}"))
                command = self._build_ytdlp_command(yt_dlp, target, archive_path, url)
                started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
                started_local = dt.datetime.now()
                try:
                    completed = subprocess.run(
                        command,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    output = completed.stdout.strip()
                    if output:
                        self.events.put(("log", output))
                    status = "ok" if completed.returncode == 0 else "error"
                    transcript_status = "not_requested"
                    if status == "ok" and transcribe and whisper is not None:
                        transcript_status = self._transcribe_new_videos(whisper, target, started_local)
                    writer.writerow([started, status, url, completed.returncode, transcript_status])
                    fh.flush()
                    self.events.put(("log", f"Status: {status}"))
                except Exception as exc:  # pragma: no cover - UI safety net
                    writer.writerow([started, "exception", url, "", "not_started"])
                    fh.flush()
                    self.events.put(("log", f"FEHLER: {exc}"))

        self.events.put(("done", f"Fertig. Protokoll: {log_path}"))

    def _build_ytdlp_command(self, yt_dlp: str, target: Path, archive_path: Path, url: str) -> list[str]:
        timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_template = str(target / f"{timestamp}-%(uploader|unknown)s-%(id)s.%(ext)s")
        command = [
            yt_dlp,
            "--no-playlist",
            "--restrict-filenames",
            "--windows-filenames",
            "--output",
            output_template,
        ]

        if self.save_metadata.get():
            command.append("--write-info-json")
        if self.write_thumbnails.get():
            command.append("--write-thumbnail")
        if self.download_archive.get():
            command.extend(["--download-archive", str(archive_path)])

        command.append(url)
        return command

    def _transcribe_new_videos(self, whisper: str, target: Path, started_local: dt.datetime) -> str:
        video_files = self._find_new_video_files(target, started_local)
        if not video_files:
            self.events.put(("log", "Transkription: keine neue Videodatei gefunden."))
            return "no_video_found"

        transcript_dir = target / "transcripts"
        transcript_dir.mkdir(parents=True, exist_ok=True)
        model = self.whisper_model.get()
        overall_status = "ok"

        for video in video_files:
            self.events.put(("log", f"Transkribiere mit Whisper/{model}: {video.name}"))
            command = [
                whisper,
                str(video),
                "--model",
                model,
                "--language",
                "de",
                "--task",
                "transcribe",
                "--output_dir",
                str(transcript_dir),
                "--output_format",
                "txt",
            ]
            completed = subprocess.run(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            output = completed.stdout.strip()
            if output:
                self.events.put(("log", output))
            if completed.returncode != 0:
                overall_status = "error"
                self.events.put(("log", f"Transkription fehlgeschlagen: {video.name}"))

        return overall_status

    def _find_new_video_files(self, target: Path, started_local: dt.datetime) -> list[Path]:
        suffixes = {".mp4", ".webm", ".mkv", ".mov", ".m4v"}
        started_ts = started_local.timestamp() - 2
        results: list[Path] = []
        for path in target.iterdir():
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if path.stat().st_mtime >= started_ts:
                results.append(path)
        return sorted(results, key=lambda item: item.stat().st_mtime)

    def _poll_events(self) -> None:
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if event == "log":
                self._append_log(payload)
            elif event == "done":
                self._append_log(payload)
                self.running = False
                self.progress.stop()
                self.start_button.configure(state="normal")

        self.after(100, self._poll_events)

    def _append_log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


def main() -> None:
    app = DownloadApp()
    app.mainloop()


if __name__ == "__main__":
    main()
