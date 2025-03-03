from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UUID
from sqlalchemy.orm import relationship

import uuid

from .base import Base, TimestampMixin


class Scheduled(Base, TimestampMixin):
    __tablename__ = 'scheduled'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    message = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    is_done = Column(Boolean, default=False, server_default='FALSE')

    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    chat = relationship('Chat')
