from __future__ import annotations

import re
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .config import SUPPORTED_EXTENSIONS
from .models import VideoFile

_GOPRO_NAME_RE = re.compile(r"^(\d{8})T(\d{6})S\d+_GH\d+", re.IGNORECASE)


def discover_video_files(input_dir: Path) -> list[Path]:
    """Return sorted list of candidate video files in a folder tree."""
    candidates: list[Path] = []
    for path in input_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            candidates.append(path)
    return sorted(candidates)


def parse_start_time_from_filename(path: Path) -> float | None:
    """Parse GoPro timestamp from filename if present and return UNIX epoch."""
    match = _GOPRO_NAME_RE.match(path.name)
    if not match:
        return None

    date_part, time_part = match.groups()
    dt = datetime.strptime(f"{date_part}{time_part}", "%Y%m%d%H%M%S")
    return dt.replace(tzinfo=timezone.utc).timestamp()


def build_video_record(path: Path) -> VideoFile:
    """Create a video record with best-effort start timestamp."""
    start_epoch = parse_start_time_from_filename(path)
    if start_epoch is None:
        start_epoch = path.stat().st_mtime
    return VideoFile(path=path, start_epoch=start_epoch)


def build_video_records(input_dir: Path) -> list[VideoFile]:
    """Build normalized records sorted by their inferred start time."""
    records = [build_video_record(path) for path in discover_video_files(input_dir)]
    return sorted(records, key=lambda r: r.start_epoch)


def with_media_props(record: VideoFile, duration_seconds: float, fps: float) -> VideoFile:
    """Return a copy of the record with runtime media properties attached."""
    return replace(record, duration_seconds=duration_seconds, fps=fps)
