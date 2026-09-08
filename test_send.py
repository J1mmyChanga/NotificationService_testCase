from datetime import datetime, timedelta, timezone
import uuid
import requests

BASE_URL = "http://localhost:8000"
TELEGRAM_ID = 1150841196
scheduled_time = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()

payload = {
    "channel_address": TELEGRAM_ID,
    "scheduled_time": scheduled_time,
    "message_text": "За любым столом всегда была лишь только черемша",
    "channel": "TELEGRAM"
}

headers = {
    "Content-Type": "application/json"
}

print(f"📡 Отправка запроса на {BASE_URL}/api/v1/schedule/ ...")
print(f"⏰ Запланированное время (UTC): {scheduled_time}")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/schedule/",
        json=payload,
    )

    print(f"\nСтатус ответа: {response.status_code}")
    print("Тело ответа API:")
    print(response.json())

except requests.exceptions.ConnectionError:
    print("❌ Ошибка: Не удалось подключиться к FastAPI на http://127.0.0.1:8000. Проверь, запущен ли Терминал №1.")
except Exception as e:
    print(f"❌ Ошибка при выполнении запроса: {e}")