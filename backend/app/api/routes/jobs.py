"""任务相关 API：上传、查询与片段列表。"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import provide_job_service, provide_review_service
from app.core import constants
from app.domain.schemas import JobSchema, SegmentSchema
from app.services.jobs import JobNotFoundError, JobService
from app.services.review import ReviewService

router = APIRouter(tags=["jobs"])


@router.post(
    constants.API_JOBS_PATH,
    response_model=JobSchema,
    status_code=constants.HTTP_STATUS_CREATED,
)
async def create_job_from_upload(
    file: UploadFile = File(...),
    job_service: JobService = Depends(provide_job_service),
) -> JobSchema:
    """接收本地媒体上传并创建任务。"""
    content = await file.read()
    try:
        job = job_service.create_from_upload(
            filename=file.filename or constants.DEFAULT_UPLOAD_FILENAME,
            content=content,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=constants.HTTP_STATUS_BAD_REQUEST,
            detail=str(error),
        ) from error
    return JobSchema.model_validate(job)


@router.get(
    f"{constants.API_JOBS_PATH}/{{job_id}}",
    response_model=JobSchema,
)
def get_job(
    job_id: str,
    job_service: JobService = Depends(provide_job_service),
) -> JobSchema:
    """查询任务状态与失败信息。"""
    try:
        job = job_service.get(job_id)
    except JobNotFoundError as error:
        raise HTTPException(
            status_code=constants.HTTP_STATUS_NOT_FOUND,
            detail=str(job_id),
        ) from error
    return JobSchema.model_validate(job)


@router.get(
    f"{constants.API_JOBS_PATH}/{{job_id}}/{constants.API_JOB_SEGMENTS_SUFFIX}",
    response_model=list[SegmentSchema],
)
def list_job_segments(
    job_id: str,
    job_service: JobService = Depends(provide_job_service),
    review_service: ReviewService = Depends(provide_review_service),
) -> list[SegmentSchema]:
    """查询任务下全部片段。"""
    try:
        job_service.get(job_id)
    except JobNotFoundError as error:
        raise HTTPException(
            status_code=constants.HTTP_STATUS_NOT_FOUND,
            detail=str(job_id),
        ) from error
    segments = review_service.list_segments(job_id)
    return [SegmentSchema.model_validate(segment) for segment in segments]
