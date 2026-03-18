from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .edit_script import build_cut_commands
from .models import Segment, VideoFile
from .timeline import timeline_rows


def write_outputs(output_dir: Path, videos: list[VideoFile], timeline: list[Segment]) -> tuple[Path, Path, Path, Path]:
    """Write timeline CSV/JSON and summary JSON to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = timeline_rows(timeline)
    csv_path = output_dir / "timeline.csv"
    json_path = output_dir / "timeline.json"
    summary_path = output_dir / "summary.json"
    ffmpeg_script_path = output_dir / "cut_by_label.sh"

    pd.DataFrame(rows).to_csv(csv_path, index=False)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    duration_by_label: dict[str, float] = {}
    for row in rows:
        label = str(row["label"])
        duration_by_label[label] = duration_by_label.get(label, 0.0) + float(row["duration_seconds"])

    summary = {
        "input_videos": [str(v.path) for v in videos],
        "video_count": len(videos),
        "segment_count": len(timeline),
        "duration_by_label_seconds": duration_by_label,
        "low_confidence_segments": [
            row for row in rows if float(row["confidence"]) < 0.7
        ],
    }
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    ffmpeg_script = build_cut_commands(rows, output_dir / "clips")
    with ffmpeg_script_path.open("w", encoding="utf-8") as f:
        f.write(ffmpeg_script)

    ffmpeg_script_path.chmod(0o755)
    return csv_path, json_path, summary_path, ffmpeg_script_path
