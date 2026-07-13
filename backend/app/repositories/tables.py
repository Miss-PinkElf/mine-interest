"""SQLite 表映射，仅服务仓储层持久化。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class JobRow(Base):
    """任务状态表：保存来源媒体、生命周期与失败信息。"""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_media_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    failed_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    retryable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SegmentRow(Base):
    """片段表：为后续审核 API 预留最小持久化字段。"""

    __tablename__ = "segments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    end_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    speaker_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    analysis_status: Mapped[str] = mapped_column(String(32), nullable=False)



class ProviderSettingsRow(Base):
    """本地云端 Provider 配置表；密钥只存本机。"""

    __tablename__ = "provider_settings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    base_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    api_key: Mapped[str] = mapped_column(Text, nullable=False, default="")
