"""局部重分析队列：只重处理关联片段。"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core import constants
from app.domain.enums import AnalysisStatus
from app.domain.models import Segment


@dataclass
class ReanalysisItem:
    segment_id: str
    status: str = constants.REANALYSIS_STATUS_QUEUED


@dataclass
class ReanalysisQueue:
    """内存队列；后续可替换为持久化。"""

    items: list[ReanalysisItem] = field(default_factory=list)

    def enqueue_stale(self, segments: list[Segment]) -> list[ReanalysisItem]:
        """仅把 analysis_status=stale 的片段入队。"""
        queued: list[ReanalysisItem] = []
        for segment in segments:
            if segment.analysis_status == AnalysisStatus.STALE:
                item = ReanalysisItem(segment_id=segment.id)
                self.items.append(item)
                queued.append(item)
        return queued

    def mark_done(self, segment_id: str) -> None:
        """标记片段重分析完成。"""
        for item in self.items:
            if item.segment_id == segment_id:
                item.status = constants.REANALYSIS_STATUS_DONE
