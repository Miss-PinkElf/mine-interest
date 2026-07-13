"""条件预处理路由与双/三音轨产物策略。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from app.core import constants
from app.services.artifacts import ArtifactStore
from app.services.media import AudioQualityReport


class PreprocessStep(str, Enum):
    """可组合的预处理步骤。"""

    NORMALIZE_LOUDNESS = "normalize_loudness"
    SEPARATE_VOCALS = "separate_vocals"
    DEREVERB = "dereverb"
    DENOISE = "denoise"


@dataclass(slots=True)
class PreprocessOutputs:
    """预处理产物路径约定。"""

    raw_track: str = constants.AUDIO_RAW_FILENAME
    light_track: str = constants.AUDIO_LIGHT_FILENAME
    stt_ready_track: str = constants.AUDIO_STT_READY_FILENAME


@dataclass(slots=True)
class PreprocessPlan:
    """根据质量报告生成的处理计划。"""

    steps: list[PreprocessStep]
    outputs: PreprocessOutputs = field(default_factory=PreprocessOutputs)
    reason: str = ""


class PreprocessRouter:
    """确定性预处理路由：干净音频跳过强处理。"""

    def build(self, report: AudioQualityReport) -> PreprocessPlan:
        """根据质量报告构建步骤清单。"""
        if report.is_clean and not report.has_strong_bgm:
            return PreprocessPlan(
                steps=[PreprocessStep.NORMALIZE_LOUDNESS],
                reason=constants.PREPROCESS_REASON_CLEAN_NORMALIZE,
            )
        steps: list[PreprocessStep] = [PreprocessStep.NORMALIZE_LOUDNESS]
        if report.has_strong_bgm:
            steps.insert(0, PreprocessStep.SEPARATE_VOCALS)
        if report.has_reverb:
            steps.append(PreprocessStep.DEREVERB)
        if report.has_noise and not report.is_clean:
            steps.append(PreprocessStep.DENOISE)
        reason = (
            constants.PREPROCESS_REASON_STRONG_BGM
            if report.has_strong_bgm
            else "CONDITIONAL_PREPROCESS"
        )
        return PreprocessPlan(steps=steps, reason=reason)


class PreprocessService:
    """执行计划并写入 audio_raw / audio_light / audio_stt_ready 占位产物。"""

    def __init__(self, artifact_store: ArtifactStore, router: PreprocessRouter | None = None) -> None:
        self._artifact_store = artifact_store
        self._router = router or PreprocessRouter()

    def run(self, job_id: str, source_media_path: str, report: AudioQualityReport) -> PreprocessPlan:
        """按计划写产物；原始轨写入后不再覆盖。"""
        plan = self._router.build(report)
        media_dir = constants.MEDIA_ARTIFACT_DIR
        raw_rel = f"{media_dir}/{plan.outputs.raw_track}"
        if not self._artifact_store.exists(job_id, raw_rel):
            # 原始轨只写一次。
            source_bytes = Path(source_media_path).read_bytes() if Path(source_media_path).exists() else b"RAW"
            self._artifact_store.write_bytes(job_id, raw_rel, source_bytes)

        light_rel = f"{media_dir}/{plan.outputs.light_track}"
        self._artifact_store.write_bytes(job_id, light_rel, b"LIGHT")

        if PreprocessStep.SEPARATE_VOCALS in plan.steps or not report.is_clean:
            stt_rel = f"{media_dir}/{plan.outputs.stt_ready_track}"
            self._artifact_store.write_bytes(job_id, stt_rel, b"STT_READY")
        return plan
