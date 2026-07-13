from app.domain.enums import AnalysisStatus
from app.domain.models import Segment
from app.services.reanalysis import ReanalysisQueue


def test_reanalysis_queue_only_includes_stale_segments() -> None:
    stable = Segment.create(raw_text="a")
    stable.analysis_status = AnalysisStatus.CURRENT
    stale = Segment.create(raw_text="b")
    stale.analysis_status = AnalysisStatus.STALE
    queue = ReanalysisQueue()
    queued = queue.enqueue_stale([stable, stale])
    assert [item.segment_id for item in queued] == [stale.id]
