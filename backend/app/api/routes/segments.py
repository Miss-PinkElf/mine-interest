"""片段相关 API：确认、切分、合并、删除与文本修改。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import provide_review_service
from app.core import constants
from app.domain.schemas import SegmentSchema
from app.services.review import ReviewOperationError, ReviewService, SegmentNotFoundError

router = APIRouter(tags=["segments"])


class SplitRequest(BaseModel):
    at_seconds: float = Field(..., description="切分时间点（秒）")


class MergeRequest(BaseModel):
    left_segment_id: str
    right_segment_id: str


class TextEditRequest(BaseModel):
    edited_text: str


class SpeakerEditRequest(BaseModel):
    speaker_id: str


def _map_errors(error: Exception) -> HTTPException:
    if isinstance(error, SegmentNotFoundError):
        return HTTPException(status_code=constants.HTTP_STATUS_NOT_FOUND, detail=str(error))
    if isinstance(error, ReviewOperationError):
        return HTTPException(status_code=constants.HTTP_STATUS_BAD_REQUEST, detail=str(error))
    return HTTPException(status_code=500, detail=str(error))


@router.post(
    f"{constants.API_SEGMENTS_PATH}/{{segment_id}}/{constants.API_SEGMENT_CONFIRM_SUFFIX}",
    response_model=SegmentSchema,
)
def confirm_segment(
    segment_id: str,
    review_service: ReviewService = Depends(provide_review_service),
) -> SegmentSchema:
    """确认单个片段的最终文本。"""
    try:
        segment = review_service.confirm_segment(segment_id)
    except Exception as error:  # noqa: BLE001
        raise _map_errors(error) from error
    return SegmentSchema.model_validate(segment)


@router.post(
    f"{constants.API_SEGMENTS_PATH}/{{segment_id}}/split",
    response_model=list[SegmentSchema],
)
def split_segment(
    segment_id: str,
    body: SplitRequest,
    review_service: ReviewService = Depends(provide_review_service),
) -> list[SegmentSchema]:
    try:
        segments = review_service.split_segment(segment_id, body.at_seconds)
    except Exception as error:  # noqa: BLE001
        raise _map_errors(error) from error
    return [SegmentSchema.model_validate(item) for item in segments]


@router.post(
    f"{constants.API_SEGMENTS_PATH}/merge",
    response_model=SegmentSchema,
)
def merge_segments(
    body: MergeRequest,
    review_service: ReviewService = Depends(provide_review_service),
) -> SegmentSchema:
    try:
        segment = review_service.merge_adjacent(body.left_segment_id, body.right_segment_id)
    except Exception as error:  # noqa: BLE001
        raise _map_errors(error) from error
    return SegmentSchema.model_validate(segment)


@router.post(
    f"{constants.API_SEGMENTS_PATH}/{{segment_id}}/delete",
    status_code=204,
)
def delete_segment(
    segment_id: str,
    review_service: ReviewService = Depends(provide_review_service),
) -> None:
    try:
        review_service.delete_segment(segment_id)
    except Exception as error:  # noqa: BLE001
        raise _map_errors(error) from error


@router.post(
    f"{constants.API_SEGMENTS_PATH}/{{segment_id}}/text",
    response_model=SegmentSchema,
)
def edit_segment_text(
    segment_id: str,
    body: TextEditRequest,
    review_service: ReviewService = Depends(provide_review_service),
) -> SegmentSchema:
    try:
        segment = review_service.apply_text_edit(segment_id, body.edited_text)
    except Exception as error:  # noqa: BLE001
        raise _map_errors(error) from error
    return SegmentSchema.model_validate(segment)


@router.post(
    f"{constants.API_SEGMENTS_PATH}/{{segment_id}}/speaker",
    response_model=SegmentSchema,
)
def edit_segment_speaker(
    segment_id: str,
    body: SpeakerEditRequest,
    review_service: ReviewService = Depends(provide_review_service),
) -> SegmentSchema:
    try:
        segment = review_service.apply_speaker_edit(segment_id, body.speaker_id)
    except Exception as error:  # noqa: BLE001
        raise _map_errors(error) from error
    return SegmentSchema.model_validate(segment)
