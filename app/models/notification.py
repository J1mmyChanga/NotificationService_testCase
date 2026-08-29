import uuid
import enum
from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"  # Ожидает времени отправки
    PROCESSING = "PROCESSING"  # Взято воркером в обработку
    SENT = "SENT"  # Успешно отправлено
    FAILED = "FAILED"  # Ошибка отправки


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    # Статус отправки
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.PENDING,
        index=True,
        nullable=False
    )

    # Связь с пользователем
    user = relationship("User", back_populates="notifications")