from app.domain.models import Segment


def test_reviewed_segment_preserves_raw_text() -> None:
    segment = Segment.create(raw_text="原始识别")

    segment.apply_text_edit("人工修订")

    assert segment.raw_text == "原始识别"
    assert segment.edited_text == "人工修订"
    assert segment.final_text == "人工修订"
