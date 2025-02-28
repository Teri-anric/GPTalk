"""
Module for the base model.
"""

from sqlalchemy import Column, MetaData, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase


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
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP,
        onupdate=func.now(),
        nullable=False,
        server_default=func.now(),
    )
