import datetime
from datetime import datetime as dt

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Counter(Base):
    __tablename__ = "counters"

    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)


class URLMapping(Base):
    __tablename__ = "url_mappings"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    original_url = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: dt.now(datetime.UTC), nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    is_custom = Column(Integer, default=0, nullable=False)

    access_logs = relationship("AccessLog", back_populates="url_mapping", cascade="all, delete-orphan")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(20), ForeignKey("url_mappings.short_code", ondelete="CASCADE"), nullable=False, index=True)
    accessed_at = Column(DateTime, default=lambda: dt.now(datetime.UTC), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    url_mapping = relationship("URLMapping", back_populates="access_logs")

    __table_args__ = (
        Index("ix_access_logs_short_code_accessed", "short_code", "accessed_at"),
    )
