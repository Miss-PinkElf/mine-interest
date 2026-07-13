from pathlib import Path

from app.services.media import MediaService


def test_quality_report_covers_core_dimensions(tmp_path: Path) -> None:
    media = tmp_path / "clean.wav"
    media.write_bytes(b"RIFF")
    report = MediaService().build_quality_report(media)
    assert "bgm" in report.availability
    assert "noise" in report.availability
    assert "reverb" in report.availability
    assert "speech_ratio" in report.availability
    assert "loudness" in report.availability
    assert "clipping" in report.availability
    assert "overlapped_speech" in report.availability
    assert report.is_clean is True

    bgm = tmp_path / "bgm_heavy.wav"
    bgm.write_bytes(b"RIFF")
    bgm_report = MediaService().build_quality_report(bgm)
    assert bgm_report.has_strong_bgm is True
