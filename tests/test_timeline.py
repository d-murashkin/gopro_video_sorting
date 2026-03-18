from gopro_sorting.models import Segment
from gopro_sorting.timeline import build_unified_timeline


def test_build_unified_timeline_orders_by_start_epoch() -> None:
    seg_a = Segment("b.mp4", 120.0, 130.0, 0.0, 10.0, "movement", 0.8)
    seg_b = Segment("a.mp4", 100.0, 105.0, 0.0, 5.0, "night", 0.9)

    timeline = build_unified_timeline([seg_a, seg_b])

    assert timeline[0].video_path == "a.mp4"
    assert timeline[1].video_path == "b.mp4"
