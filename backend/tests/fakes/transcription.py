from app.services.transcription import TranscriptionResult, TranscriptionWord


def fake_transcription_result() -> TranscriptionResult:
    return TranscriptionResult(
        words=[
            TranscriptionWord(text="你好", start=0.0, end=1.2, speaker_id="speaker_0"),
            TranscriptionWord(text="世界", start=1.2, end=2.4, speaker_id="speaker_0"),
            TranscriptionWord(text="下一段", start=2.4, end=5.1, speaker_id="speaker_1"),
        ],
        raw_engine_payload={"engine": "fake"},
    )


class FakeTranscriptionEngine:
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        return fake_transcription_result()
