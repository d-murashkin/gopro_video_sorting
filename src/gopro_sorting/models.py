from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoFile:
    path: Path
    start_epoch: float
    duration_seconds: float | None = None
    fps: float | None = None


@dataclass
class Segment:
    video_path: str
    global_start_epoch: float
    global_end_epoch: float
    local_start_seconds: float
    local_end_seconds: float
    label: str
    confidence: float
