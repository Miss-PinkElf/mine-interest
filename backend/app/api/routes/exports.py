"""导出相关 API：JSON / Markdown 产物生成。"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import provide_export_service
from app.core import constants
from app.domain.schemas import ExportArtifactSchema, ExportRequestSchema
from app.services.exports import ExportNotReadyError, ExportService
from app.services.jobs import JobNotFoundError

router = APIRouter(tags=["exports"])


@router.post(
    f"{constants.API_JOBS_PATH}/{{job_id}}/{constants.API_JOB_EXPORTS_SUFFIX}",
    response_model=ExportArtifactSchema,
    status_code=constants.HTTP_STATUS_CREATED,
)
def export_job(
    job_id: str,
    body: ExportRequestSchema,
    export_service: ExportService = Depends(provide_export_service),
) -> ExportArtifactSchema:
    """为任务生成导出文件。"""
    try:
        artifact = export_service.export_job(job_id, body.format)
    except JobNotFoundError as error:
        raise HTTPException(
            status_code=constants.HTTP_STATUS_NOT_FOUND,
            detail=str(job_id),
        ) from error
    except ExportNotReadyError as error:
        raise HTTPException(
            status_code=constants.HTTP_STATUS_BAD_REQUEST,
            detail=str(error),
        ) from error
    return ExportArtifactSchema.model_validate(artifact)
