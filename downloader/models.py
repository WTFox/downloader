"""SQLAlchemy models for database schema."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, Float, Uuid
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class DownloadLog(Base):
    """Model for tracking download jobs."""

    __tablename__ = "downloads"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, nullable=False)
    url = Column(String(2048), nullable=False, index=True)
    download_type = Column(String(50), nullable=False)  # 'video', 'audio', 'both'
    status = Column(String(50), nullable=False, default="queued")  # 'queued', 'processing', 'completed', 'failed'
    success = Column(Boolean, nullable=True)  # NULL until completion
    requested_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    error_message = Column(String(4096), nullable=True)
    output_path = Column(String(2048), nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<DownloadLog(id={self.id}, url={self.url[:50]}..., "
            f"type={self.download_type}, status={self.status}, success={self.success})>"
        )
