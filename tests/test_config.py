from pathlib import Path

from gopro_sorting.config import default_output_dir, default_sample_data_dir


def test_default_paths_follow_data_and_output_env(monkeypatch, tmp_path) -> None:
    data_root = tmp_path / "data"
    output_root = tmp_path / "output-root"
    monkeypatch.setenv("WORKDATA", str(data_root))
    monkeypatch.setenv("OUTPUT", str(output_root))

    assert default_sample_data_dir() == data_root / "samples" / "gopro_video_sorting"
    assert default_output_dir() == output_root / "gopro_video_sorting"


def test_default_paths_have_local_fallback(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("WORKDATA", raising=False)
    monkeypatch.delenv("OUTPUT", raising=False)
    monkeypatch.chdir(tmp_path)

    assert default_sample_data_dir() == Path.cwd()
    assert default_output_dir() == tmp_path / "output"
