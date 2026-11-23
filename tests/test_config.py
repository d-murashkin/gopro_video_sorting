from gopro_sorting.config import default_output_dir, default_sample_data_dir


def test_sample_root_is_independent_and_output_is_run_scoped(monkeypatch, tmp_path) -> None:
    sample_root = tmp_path / "sample-store"
    output_root = tmp_path / "output-store"
    monkeypatch.setenv("RESEARCHDATA", str(tmp_path / "unrelated-data"))
    monkeypatch.setenv("RESEARCHSAMPLES", str(sample_root))
    monkeypatch.setenv("RESEARCHOUTPUT", str(output_root))
    monkeypatch.setenv("RUN_NAME", "2026-09-10-migration")

    assert default_sample_data_dir() == sample_root / "gopro_video_sorting"
    assert default_output_dir() == output_root / "gopro_video_sorting" / "2026-09-10-migration"


