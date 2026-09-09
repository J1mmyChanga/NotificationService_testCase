import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.channel.models.deliverychannel import DeliveryChannel
from app.common.channel.models.channel import ChannelStatus


class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_address(self, address: str, channel: ChannelStatus) -> DeliveryChannel | None:
        stmt = select(DeliveryChannel).where(DeliveryChannel.address == address, DeliveryChannel.channel == channel)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID, channel: ChannelStatus) -> DeliveryChannel | None:
        stmt = select(DeliveryChannel).where(DeliveryChannel.user_id == user_id, DeliveryChannel.channel == channel)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_delivery_address(self, user_id: uuid.UUID, channel: ChannelStatus, address: str) -> DeliveryChannel:
        delivery_channel = DeliveryChannel(
            user_id=user_id,
            channel=channel,
            address=address,
        )
        self.session.add(delivery_channel)
        await self.session.commit()
        await self.session.refresh(delivery_channel)
        return delivery_channel