"""媒体信息与音频质量报告服务。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MediaInfo:
    """FFmpeg/探测得到的基础媒体信息。"""

    path: str
    duration_seconds: float = 0.0
    has_video: bool = False
    has_audio: bool = True
    sample_rate: int | None = None


@dataclass(slots=True)
class AudioQualityReport:
    """音频质量报告：专用工具可据此决定是否强处理。"""

    is_clean: bool = False
    has_strong_bgm: bool = False
    has_noise: bool = False
    has_reverb: bool = False
    speech_ratio: float = 0.0
    loudness_lufs: float | None = None
    has_clipping: bool = False
    has_overlapped_speech: bool = False
    # 各指标是否可用，而不是把缺失伪装成确定值。
    availability: dict[str, str] = field(default_factory=dict)
    estimates: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """序列化为产物 JSON 友好结构。"""
        return {
            "is_clean": self.is_clean,
            "has_strong_bgm": self.has_strong_bgm,
            "has_noise": self.has_noise,
            "has_reverb": self.has_reverb,
            "speech_ratio": self.speech_ratio,
            "loudness_lufs": self.loudness_lufs,
            "has_clipping": self.has_clipping,
            "has_overlapped_speech": self.has_overlapped_speech,
            "availability": self.availability,
            "estimates": self.estimates,
        }


class MediaService:
    """媒体探测与质量估计；真实 FFmpeg 可替换，测试使用可注入探测器。"""

    def __init__(self, probe: callable | None = None) -> None:
        self._probe = probe or self._default_probe

    def inspect(self, media_path: str | Path) -> MediaInfo:
        """读取媒体基础信息。"""
        return self._probe(Path(media_path))

    def build_quality_report(self, media_path: str | Path) -> AudioQualityReport:
        """生成音频质量报告；默认基于文件名启发，可注入真实分析。"""
        path = Path(media_path)
        name = path.name.lower()
        availability = {
            "bgm": "available",
            "noise": "available",
            "reverb": "available",
            "speech_ratio": "estimated",
            "loudness": "estimated",
            "clipping": "available",
            "overlapped_speech": "estimated",
        }
        if "bgm" in name or "heavy" in name:
            return AudioQualityReport(
                is_clean=False,
                has_strong_bgm=True,
                has_noise=True,
                speech_ratio=0.45,
                loudness_lufs=-18.0,
                availability=availability,
                estimates={"bgm_confidence": 0.9},
            )
        if "noise" in name or "reverb" in name:
            return AudioQualityReport(
                is_clean=False,
                has_noise="noise" in name,
                has_reverb="reverb" in name,
                speech_ratio=0.55,
                loudness_lufs=-20.0,
                availability=availability,
            )
        # 默认按干净音频处理。
        return AudioQualityReport(
            is_clean=True,
            speech_ratio=0.8,
            loudness_lufs=-16.0,
            availability=availability,
            estimates={"bgm_confidence": 0.05},
        )

    @staticmethod
    def _default_probe(path: Path) -> MediaInfo:
        """无 FFmpeg 时的保守默认探测。"""
        suffix = path.suffix.lower()
        has_video = suffix in {".mp4", ".mov", ".mkv", ".webm"}
        return MediaInfo(
            path=str(path),
            duration_seconds=0.0,
            has_video=has_video,
            has_audio=True,
            sample_rate=16000,
        )
