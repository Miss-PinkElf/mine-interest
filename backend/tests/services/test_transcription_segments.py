from app.services.transcription import TranscriptionService
from tests.fakes.transcription import FakeTranscriptionEngine, fake_transcription_result


def test_transcription_result_becomes_reviewable_segments() -> None:
    service = TranscriptionService(FakeTranscriptionEngine())
    segments = service.to_segments(fake_transcription_result())
    assert [(item.start_seconds, item.end_seconds, item.speaker_id) for item in segments] == [
        (0.0, 2.4, "speaker_0"),
        (2.4, 5.1, "speaker_1"),
    ]
    assert segments[0].raw_text == "你好世界"
