"""Download YouTube videos for offline processing."""

from __future__ import annotations

import subprocess
from pathlib import Path


def download_youtube_video(url: str, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(cache_dir / "%(id)s.%(ext)s")

    command = [
        "yt-dlp",
        "--no-playlist",
        "-f",
        "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]",
        "--merge-output-format",
        "mp4",
        "-o",
        output_template,
        url,
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)

    candidates = sorted(cache_dir.glob("*.mp4"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise RuntimeError("yt-dlp finished but no mp4 file was found in cache")

    return candidates[0]
