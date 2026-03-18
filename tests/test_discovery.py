from pathlib import Path

from gopro_sorting.discovery import parse_start_time_from_filename


def test_parse_start_time_from_gopro_filename() -> None:
    path = Path("20220304T000819S000000_GH580049.MP4")
    epoch = parse_start_time_from_filename(path)
    assert epoch is not None


def test_parse_start_time_returns_none_for_unknown_name() -> None:
    path = Path("random_clip.mp4")
    assert parse_start_time_from_filename(path) is None
