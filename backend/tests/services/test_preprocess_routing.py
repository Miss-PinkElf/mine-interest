from app.services.media import AudioQualityReport
from app.services.preprocess import PreprocessRouter, PreprocessStep


def test_clean_audio_skips_separation_and_denoise() -> None:
    router = PreprocessRouter()
    plan = router.build(AudioQualityReport(is_clean=True))
    assert plan.steps == [PreprocessStep.NORMALIZE_LOUDNESS]
    assert PreprocessStep.SEPARATE_VOCALS not in plan.steps
    assert PreprocessStep.DENOISE not in plan.steps


def test_bgm_heavy_audio_creates_stt_ready_track() -> None:
    router = PreprocessRouter()
    plan = router.build(AudioQualityReport(has_strong_bgm=True, is_clean=False))
    assert PreprocessStep.SEPARATE_VOCALS in plan.steps
    assert plan.outputs.stt_ready_track == "audio_stt_ready.wav"
