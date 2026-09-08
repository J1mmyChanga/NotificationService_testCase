from fastapi import FastAPI
from app.common.notification.handlers.notification_route import router as api_router
from app.common.user.models.user import User
from app.common.channel.models.deliverychannel import DeliveryChannel
from app.common.notification.models.notification import Notification

app = FastAPI(
    title="Notification Service API",
    version="1.0.0"
)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.services.api.main:app", host="0.0.0.0", port=8000, reload=True)