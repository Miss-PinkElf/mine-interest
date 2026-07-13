"""导出服务：将已审核片段写成 JSON / Markdown 产物。"""

from __future__ import annotations

import json
from pathlib import Path

from app.core import constants
from app.domain.enums import ExportFormat
from app.domain.models import ExportArtifact, Segment
from app.services.artifacts import ArtifactStore
from app.services.jobs import JobService
from app.services.review import ReviewService


class ExportNotReadyError(ValueError):
    """当任务尚不具备导出条件时抛出。"""


class ExportService:
    """根据片段最终文本生成导出文件，并更新任务状态。"""

    def __init__(
        self,
        artifact_store: ArtifactStore,
        job_service: JobService,
        review_service: ReviewService,
    ) -> None:
        self._artifact_store = artifact_store
        self._job_service = job_service
        self._review_service = review_service

    def export_job(self, job_id: str, export_format: ExportFormat) -> ExportArtifact:
        """导出指定任务；无片段时失败，且不删除既有产物。"""
        # 先确认任务存在。
        self._job_service.get(job_id)
        segments = self._review_service.list_segments(job_id)
        if not segments:
            raise ExportNotReadyError(constants.EXPORT_ERROR_NO_SEGMENTS)

        if export_format is ExportFormat.MARKDOWN:
            relative_path = (
                f"{constants.EXPORT_RELATIVE_DIR}/{constants.EXPORT_MARKDOWN_FILENAME}"
            )
            content = self._render_markdown(segments)
            self._artifact_store.write_text(job_id, relative_path, content)
        elif export_format is ExportFormat.JSON:
            relative_path = (
                f"{constants.EXPORT_RELATIVE_DIR}/{constants.EXPORT_JSON_FILENAME}"
            )
            content = self._render_json(segments)
            self._artifact_store.write_text(job_id, relative_path, content)
        else:
            raise ExportNotReadyError(f"UNSUPPORTED_FORMAT:{export_format}")

        absolute_path = str(self._artifact_store.resolve_path(job_id, relative_path))
        artifact = ExportArtifact.create(
            job_id=job_id,
            format=export_format,
            artifact_path=absolute_path,
        )
        self._job_service.mark_exported(job_id)
        return artifact

    @staticmethod
    def _render_markdown(segments: list[Segment]) -> str:
        """渲染面向人工阅读的时间轴 Markdown。"""
        lines = ["# 情感化转写导出", ""]
        for index, segment in enumerate(segments, start=1):
            speaker = segment.speaker_id or "-"
            lines.append(
                f"## 片段 {index} ({segment.start_seconds:.2f}s - {segment.end_seconds:.2f}s)"
            )
            lines.append(f"- 说话人: {speaker}")
            lines.append(f"- 状态: {segment.review_status.value}")
            lines.append("")
            lines.append(segment.final_text)
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _render_json(segments: list[Segment]) -> str:
        """渲染面向机器消费的片段 JSON。"""
        payload = [
            {
                "id": segment.id,
                "start_seconds": segment.start_seconds,
                "end_seconds": segment.end_seconds,
                "speaker_id": segment.speaker_id,
                "raw_text": segment.raw_text,
                "edited_text": segment.edited_text,
                "final_text": segment.final_text,
                "review_status": segment.review_status.value,
                "analysis_status": segment.analysis_status.value,
            }
            for segment in segments
        ]
        return json.dumps(payload, ensure_ascii=False, indent=2)
