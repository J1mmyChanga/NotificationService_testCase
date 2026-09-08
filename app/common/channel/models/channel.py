import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.models.base import Base


class ChannelStatus(str, enum.Enum):
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


# class Channel(Base):
#     __tablename__ = "channels"
#
#     id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
#     channel: Mapped[ChannelStatus] = mapped_column(
#         SQLEnum(ChannelStatus),
#         index=True,
#         nullable=False
#     )
#
#     delivery_channels = relationship("DeliveryChannel", back_populates="channel", cascade="all, delete-orphan")