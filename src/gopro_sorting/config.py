import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_SLUG = "gopro_video_sorting"


def _env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else None


def default_sample_data_dir() -> Path:
    """Return the default input folder for the current project layout."""
    data_root = _env_path("WORKDATA")
    if data_root is not None:
        return data_root / "samples" / PROJECT_SLUG
    return Path.cwd()


def default_output_dir() -> Path:
    """Return the default output folder for generated project artifacts."""
    output_root = _env_path("OUTPUT")
    if output_root is not None:
        return output_root / PROJECT_SLUG
    return Path.cwd() / "output"


@dataclass
class AnalyzerConfig:
    """Runtime configuration for classification thresholds and sampling."""

    input_dir: Path
    output_dir: Path
    brightness_night_threshold: float = 40.0
    motion_threshold: float = 2.2
    sample_every_n_frames: int = 30
    min_segment_seconds: float = 3.0
    confidence_floor: float = 0.55
    max_analysis_seconds: float | None = None


SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi"}
