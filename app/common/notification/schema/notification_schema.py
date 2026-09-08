from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ScheduleNotificationRequest(BaseModel):
    user_id: int = Field(..., description="Telegram ID пользователя")
    scheduled_time: datetime = Field(..., description="время отправки (yyyy:mm:dd, hh:mm:ss)")
    message_text: str = Field(..., min_length=1, max_length=4096)
    channel: str = Field(..., min_length=1, max_length=100)

    @field_validator("scheduled_time")
    @classmethod
    def validate_scheduled_time(cls, v: datetime) -> datetime:
        if v.tzinfo is not None:
            now = datetime.now(v.tzinfo)
        else:
            now = datetime.now()

        if v <= now:
            raise ValueError("Время напоминания должно быть в будущем!")
        return v


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    message_text: str
    scheduled_time: datetime
    status: str
    channel: str
    created_at: datetime

    class Config:
        from_attributes = True