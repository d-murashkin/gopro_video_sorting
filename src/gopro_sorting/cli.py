from __future__ import annotations

import argparse
from pathlib import Path

from .classify import GoProClassifier
from .config import AnalyzerConfig
from .exporters import write_outputs
from .timeline import build_unified_timeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sort GoPro videos into movement/stationary/night timelines.")
    parser.add_argument("input_dir", type=Path, help="Input folder containing videos")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Output folder for timeline files")
    parser.add_argument("--brightness-night-threshold", type=float, default=40.0)
    parser.add_argument("--motion-threshold", type=float, default=2.2)
    parser.add_argument("--sample-every-n-frames", type=int, default=30)
    parser.add_argument("--min-segment-seconds", type=float, default=3.0)
    parser.add_argument("--confidence-floor", type=float, default=0.55)
    parser.add_argument(
        "--max-analysis-seconds",
        type=float,
        default=None,
        help="Only analyze the first N seconds of each video (useful for quick tuning).",
    )
    return parser.parse_args()


def run(config: AnalyzerConfig) -> tuple[Path, Path, Path, Path]:
    classifier = GoProClassifier(config)
    videos, segments = classifier.classify_folder()
    timeline = build_unified_timeline(segments)
    return write_outputs(config.output_dir, videos, timeline)


def main() -> None:
    args = parse_args()
    config = AnalyzerConfig(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        brightness_night_threshold=args.brightness_night_threshold,
        motion_threshold=args.motion_threshold,
        sample_every_n_frames=args.sample_every_n_frames,
        min_segment_seconds=args.min_segment_seconds,
        confidence_floor=args.confidence_floor,
        max_analysis_seconds=args.max_analysis_seconds,
    )
    csv_path, json_path, summary_path, ffmpeg_script_path = run(config)
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {ffmpeg_script_path}")


if __name__ == "__main__":
    main()
