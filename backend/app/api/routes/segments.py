"""片段相关 API：确认等审核操作。"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import provide_review_service
from app.core import constants
from app.domain.schemas import SegmentSchema
from app.services.review import ReviewService, SegmentNotFoundError

router = APIRouter(tags=["segments"])


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
    except SegmentNotFoundError as error:
        raise HTTPException(
            status_code=constants.HTTP_STATUS_NOT_FOUND,
            detail=str(segment_id),
        ) from error
    return SegmentSchema.model_validate(segment)
