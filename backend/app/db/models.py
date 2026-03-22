import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Model(Base):
    __tablename__ = "models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    openrouter_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    context_length: Mapped[int | None] = mapped_column(Integer)
    pricing_input: Mapped[Decimal | None] = mapped_column(Numeric(20, 10))
    pricing_output: Mapped[Decimal | None] = mapped_column(Numeric(20, 10))
    pricing_image: Mapped[Decimal | None] = mapped_column(Numeric(20, 10))
    pricing_request: Mapped[Decimal | None] = mapped_column(Numeric(20, 10))
    modalities: Mapped[dict | None] = mapped_column(JSONB)
    supported_parameters: Mapped[dict | None] = mapped_column(JSONB)
    max_completion_tokens: Mapped[int | None] = mapped_column(Integer)
    architecture: Mapped[dict | None] = mapped_column(JSONB)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    benchmarks: Mapped[list["ModelBenchmark"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    tags: Mapped[list["ModelTag"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_models_provider", "provider"),
        Index("idx_models_pricing_input", "pricing_input"),
        Index("idx_models_context_length", "context_length"),
        Index("idx_models_is_active", "is_active"),
    )


class ModelBenchmark(Base):
    __tablename__ = "model_benchmarks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.id"), nullable=False
    )
    benchmark_name: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    max_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    source_url: Mapped[str | None] = mapped_column(String(500))
    measured_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    model: Mapped["Model"] = relationship(back_populates="benchmarks")

    __table_args__ = (
        UniqueConstraint("model_id", "benchmark_name"),
        Index("idx_benchmarks_model_id", "model_id"),
        Index("idx_benchmarks_name", "benchmark_name"),
    )


class ModelTag(Base):
    __tablename__ = "model_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    strength_level: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    model: Mapped["Model"] = relationship(back_populates="tags")

    __table_args__ = (
        UniqueConstraint("model_id", "category"),
        CheckConstraint(
            "strength_level BETWEEN 1 AND 5",
            name="ck_model_tags_strength_level",
        ),
        Index("idx_tags_model_id", "model_id"),
        Index("idx_tags_category", "category"),
    )
