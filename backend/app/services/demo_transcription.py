"""显式演示模式使用的假转写引擎，不分析上传媒体。"""

from app.core import constants
from app.services.transcription import TranscriptionResult, TranscriptionWord


class DemoTranscriptionEngine:
    """返回固定演示片段，供自动审核链路验收。"""

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """忽略媒体内容；来源声明由任务与导出层共同保留。"""
        return TranscriptionResult(
            words=[
                TranscriptionWord(
                    text=constants.DEMO_TRANSCRIPT_TEXT,
                    start=constants.DEMO_SEGMENT_START_SECONDS,
                    end=constants.DEMO_SEGMENT_END_SECONDS,
                )
            ],
            raw_engine_payload={"engine": constants.DEMO_ENGINE_NAME},
        )
