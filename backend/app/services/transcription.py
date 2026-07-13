"""转写与说话人分离适配：统一为可审核 Segment。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.models import Segment


@dataclass(slots=True)
class TranscriptionWord:
    text: str
    start: float
    end: float
    speaker_id: str | None = None


@dataclass(slots=True)
class TranscriptionResult:
    """引擎无关的转写标准化结果。"""

    words: list[TranscriptionWord]
    raw_engine_payload: dict


class TranscriptionEngine(Protocol):
    """可替换转写引擎协议。"""

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """对 STT 就绪音轨执行转写。"""


class TranscriptionService:
    """把引擎输出标准化为 Segment 列表。"""

    def __init__(self, engine: TranscriptionEngine) -> None:
        self._engine = engine

    def to_segments(self, result: TranscriptionResult) -> list[Segment]:
        """将词级/段级结果折叠为审核片段。"""
        if not result.words:
            return []
        # 按说话人连续区间折叠。
        segments: list[Segment] = []
        current_speaker = result.words[0].speaker_id
        start = result.words[0].start
        end = result.words[0].end
        texts = [result.words[0].text]
        for word in result.words[1:]:
            if word.speaker_id != current_speaker:
                segments.append(
                    Segment.create(
                        raw_text="".join(texts),
                        start_seconds=start,
                        end_seconds=end,
                        speaker_id=current_speaker,
                    )
                )
                current_speaker = word.speaker_id
                start = word.start
                texts = [word.text]
            else:
                texts.append(word.text)
            end = word.end
        segments.append(
            Segment.create(
                raw_text="".join(texts),
                start_seconds=start,
                end_seconds=end,
                speaker_id=current_speaker,
            )
        )
        return segments

    def run(self, audio_path: str) -> list[Segment]:
        """执行引擎并返回片段。"""
        return self.to_segments(self._engine.transcribe(audio_path))
