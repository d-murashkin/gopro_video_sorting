from __future__ import annotations

from datetime import datetime, timezone

from .models import Segment


def build_unified_timeline(segments: list[Segment]) -> list[Segment]:
    """Sort all segments from all files into one global timeline."""
    return sorted(segments, key=lambda s: (s.global_start_epoch, s.video_path))


def timeline_rows(segments: list[Segment]) -> list[dict[str, str | float]]:
    rows: list[dict[str, str | float]] = []
    for seg in segments:
        rows.append(
            {
                "video_path": seg.video_path,
                "label": seg.label,
                "confidence": seg.confidence,
                "global_start_epoch": seg.global_start_epoch,
                "global_end_epoch": seg.global_end_epoch,
                "global_start_iso": datetime.fromtimestamp(seg.global_start_epoch, tz=timezone.utc).isoformat(),
                "global_end_iso": datetime.fromtimestamp(seg.global_end_epoch, tz=timezone.utc).isoformat(),
                "local_start_seconds": seg.local_start_seconds,
                "local_end_seconds": seg.local_end_seconds,
                "duration_seconds": max(0.0, seg.local_end_seconds - seg.local_start_seconds),
            }
        )
    return rows
