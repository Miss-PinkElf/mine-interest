from pathlib import Path

from app.domain.enums import AnalysisStatus
from app.domain.models import Segment
from app.services.artifacts import ArtifactStore
from app.services.jobs import JobService
from app.services.review import ReviewService


def test_split_only_marks_affected_segments_stale(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path)
    jobs = JobService(store)
    review = ReviewService(jobs._session_factory)
    job = jobs.create(source_media_path="sample.mp4")

    stable = Segment.create(raw_text="稳定", start_seconds=0.0, end_seconds=1.0)
    stable.analysis_status = AnalysisStatus.CURRENT
    target = Segment.create(raw_text="待切", start_seconds=1.0, end_seconds=3.0)
    target.analysis_status = AnalysisStatus.CURRENT
    review.add_segment(job.id, stable)
    review.add_segment(job.id, target)

    parts = review.split_segment(target.id, at_seconds=2.0)
    assert len(parts) == 2
    assert all(part.analysis_status == AnalysisStatus.STALE for part in parts)

    remaining = {item.id: item for item in review.list_segments(job.id)}
    assert remaining[stable.id].analysis_status == AnalysisStatus.CURRENT
