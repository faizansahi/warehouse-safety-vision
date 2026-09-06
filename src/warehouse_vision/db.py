import os
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class SafetyEvent(Base):
    __tablename__ = "safety_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(10), index=True)
    source: Mapped[str] = mapped_column(String(500))
    details: Mapped[dict] = mapped_column(JSON)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///./safety.db"),
    connect_args={"check_same_thread": False} if not os.getenv("DATABASE_URL") else {},
)
Session = sessionmaker(engine, expire_on_commit=False)
