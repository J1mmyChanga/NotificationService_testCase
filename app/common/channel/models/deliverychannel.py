# app/common/channel/models/delivery_channel.py (v1.1)
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.models.base import Base

if TYPE_CHECKING:
    from app.common.channel.models.channel import Channel
    from app.common.user.models.user import User


class DeliveryChannel(Base):
    __tablename__ = "delivery_channels"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Адрес доставки (Telegram ID, e-mail или номер телефона)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="delivery_channels")
    channel: Mapped["Channel"] = relationship(back_populates="delivery_channels")

    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="uq_user_channel"),
    )