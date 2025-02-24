from sqlalchemy import BigInteger, Column, String

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Represents a Telegram user in the database.
    """

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
