import json

from gopro_sorting.exporters import write_outputs
from gopro_sorting.models import Segment, VideoFile


def test_write_outputs_creates_csv_json_summary_and_script(tmp_path) -> None:
    video = VideoFile(path=tmp_path / "clip.mp4", start_epoch=100.0)
    segments = [
        Segment(
            video_path=str(video.path),
            global_start_epoch=100.0,
            global_end_epoch=104.0,
            local_start_seconds=0.0,
            local_end_seconds=4.0,
            label="night",
            confidence=0.8,
        )
    ]

    csv_path, json_path, summary_path, script_path = write_outputs(tmp_path, [video], segments)

    assert csv_path.exists()
    assert json_path.exists()
    assert summary_path.exists()
    assert script_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data[0]["label"] == "night"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["video_count"] == 1
    assert "duration_by_label_seconds" in summary

    script_text = script_path.read_text(encoding="utf-8")
    assert "ffmpeg -y" in script_text
