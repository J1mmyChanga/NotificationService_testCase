from abc import ABC, abstractmethod
from typing import Dict


class BaseNotificationChannel(ABC):
    @property
    @abstractmethod
    def channel_name(self) -> str:
        pass

    @abstractmethod
    async def send(self, channel_address: int, message_text: str) -> None:
        pass


class NotificationChannelRegistry:
    def __init__(self):
        self._channels: Dict[str, BaseNotificationChannel] = {}

    def register(self, channel: BaseNotificationChannel) -> None:
        self._channels[channel.channel_name] = channel

    def get(self, channel_name: str) -> BaseNotificationChannel:
        channel = self._channels.get(channel_name)
        if not channel:
            raise ValueError(f"Channel '{channel_name}' is not registered")
        return channel