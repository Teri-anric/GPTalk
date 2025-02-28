"""
Module for the base model.
"""

from sqlalchemy import Column, DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base model for all database models.
    """

    __allow_unmapped__ = True

    metadata = MetaData()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')])})"


class TimestampMixin:
    """
    Mixin for adding timestamps to a model.
    """

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        server_default=func.now(),
    )
