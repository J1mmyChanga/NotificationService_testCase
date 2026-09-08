import uuid
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.models.base import Base
from app.common.channel.models.channel import ChannelStatus
if TYPE_CHECKING:
    from app.common.user.models.user import User


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"  # ожидает времени отправки
    PROCESSING = "PROCESSING"  # взято воркером в обработку
    SENT = "SENT"
    FAILED = "FAILED"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.PENDING,
        index=True,
        nullable=False
    )
    channel: Mapped[ChannelStatus] = mapped_column(
        SQLEnum(ChannelStatus),
        index=True,
        nullable=True
    )

    user = relationship("User", back_populates="notifications")