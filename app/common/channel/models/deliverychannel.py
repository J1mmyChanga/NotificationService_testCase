import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.models.base import Base
from app.common.channel.models.channel import ChannelStatus
from app.common.user.models.user import User


class DeliveryChannel(Base):
    __tablename__ = "delivery_channels"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    channel: Mapped[ChannelStatus] = mapped_column(
        SQLEnum(ChannelStatus),
        index=True,
        nullable=True
    )
    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Адрес доставки (Telegram ID, e-mail или номер телефона)"
    )

    user = relationship("User", back_populates="delivery_channels")

    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="uq_user_channel"),
    )