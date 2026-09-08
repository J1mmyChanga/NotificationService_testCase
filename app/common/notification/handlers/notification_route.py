from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.notification.schema.notification_schema import NotificationResponse, ScheduleNotificationRequest
from app.common.core.logger import logger
from app.common.core.database import get_db
from app.common.notification.service.create_notification import create_notification

router = APIRouter(prefix="/api/v1")


@router.post(
    "/schedule",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Запланировать напоминание"
)
async def schedule_notification(
    payload: ScheduleNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    log_context = {
        "user_id": str(payload.user_id),
        "channel": payload.channel,
        "scheduled_time": payload.scheduled_time.isoformat(),
        "service": "api"
    }

    logger.info("Received request to create notification", extra=log_context)
    try:
        notification = await create_notification(
            session=db,
            telegram_id=payload.user_id,
            scheduled_time=payload.scheduled_time,
            message_text=payload.message_text,
            channel=payload.channel
        )
        return notification
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )