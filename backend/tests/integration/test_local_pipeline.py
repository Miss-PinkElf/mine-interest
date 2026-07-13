from pathlib import Path

from app.services.artifacts import ArtifactStore
from app.services.evidence import EvidenceService
from app.services.exports import ExportService
from app.services.jobs import JobService
from app.services.media import MediaService
from app.services.orchestrator import FrameManifest, run_pipeline
from app.services.preprocess import PreprocessService
from app.services.review import ReviewService
from app.services.transcription import TranscriptionService
from tests.fakes.transcription import FakeTranscriptionEngine


def test_local_pipeline_upload_preprocess_transcribe_export(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path)
    jobs = JobService(store)
    review = ReviewService(jobs._session_factory)
    exports = ExportService(store, jobs, review)

    source = tmp_path / "clean.wav"
    source.write_bytes(b"RIFF-clean")
    job = jobs.create_from_upload("clean.wav", source.read_bytes())

    report = MediaService().build_quality_report(source)
    plan = PreprocessService(store).run(job.id, str(source), report)
    assert plan.steps

    segments = TranscriptionService(FakeTranscriptionEngine()).run(str(source))
    for segment in segments:
        review.add_segment(job.id, segment)

    pipeline = run_pipeline(frame_manifest=FrameManifest(has_face=False))
    evidence = EvidenceService().from_pipeline(segments[0].id, pipeline)
    assert evidence

    review.confirm_segment(segments[0].id)
    artifact = exports.export_job(job.id, __import__("app.domain.enums", fromlist=["ExportFormat"]).ExportFormat.MARKDOWN)
    assert Path(artifact.artifact_path).exists()
