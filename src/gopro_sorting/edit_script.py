from __future__ import annotations

from pathlib import Path


def _safe_stem(path: str) -> str:
    return Path(path).stem.replace(" ", "_")


def build_cut_commands(rows: list[dict[str, str | float]], output_dir: Path) -> str:
    """Build shell script that cuts timeline segments into label subfolders with ffmpeg."""
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f'OUT_ROOT="{output_dir}"',
        'mkdir -p "$OUT_ROOT/movement" "$OUT_ROOT/stationary" "$OUT_ROOT/night"',
        "",
    ]

    for idx, row in enumerate(rows):
        video_path = str(row["video_path"])
        label = str(row["label"])
        start_s = float(row["local_start_seconds"])
        end_s = float(row["local_end_seconds"])
        stem = _safe_stem(video_path)
        clip_name = f"{stem}_{idx:04d}_{label}.mp4"

        lines.append(
            "ffmpeg -y "
            f"-ss {start_s:.3f} -to {end_s:.3f} "
            f"-i \"{video_path}\" -c copy "
            f"\"$OUT_ROOT/{label}/{clip_name}\""
        )

    lines.append("")
    return "\n".join(lines)
