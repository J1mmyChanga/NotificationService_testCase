from prometheus_client import Counter, Histogram, Gauge, start_http_server

NOTIFICATION_LAG = Histogram(
    "notification_lag_seconds",
    "Отклонение фактического времени отправки от запланированного (в миллисекундах)",
)

NOTIFICATIONS_PENDING = Gauge(
    "notifications_pending_count",
    "Текущее количество просроченных уведомлений в очереди PENDING"
)

WORKER_PROCESSING_TIME = Histogram(
    "worker_processing_seconds",
    "Время выполнения циклов воркера"
)

NOTIFICATIONS_TOTAL = Counter(
    "notifications_total",
    "Количество обработанных уведомлений в секунду (пропускная способность)",
    ["status", "channel"]
)

EXTERNAL_API_REQUESTS = Counter(
    "external_api_requests_total",
    "Соотношение ответов внешних API (Telegram)",
    ["target", "status_code"]
)

# EXTERNAL_API_RETRIES = Counter( ###
#     "external_api_retries_total",
#     "Количество повторных попыток запросов к внешним API",
#     ["target"]
# )


def start_metrics_server(port: int = 8002):
    try:
        start_http_server(port)
        print(f"📊 Prometheus metrics server started on port {port}")
    except Exception as e:
        print(f"⚠️ Metrics server already running or failed: {e}")