import enum


class ChannelStatus(str, enum.Enum):
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"