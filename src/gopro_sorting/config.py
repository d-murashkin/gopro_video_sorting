from dataclasses import dataclass
from pathlib import Path



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
