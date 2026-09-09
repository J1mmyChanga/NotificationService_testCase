# app/common/core/logger.py (v1.1)
import logging
import json
from datetime import datetime, timezone
import contextvars
from contextlib import contextmanager

# Контекстная переменная для хранения дополнительных полей логов
log_context_var = contextvars.ContextVar("log_context", default={})


@contextmanager
def log_context(**kwargs):
    """
    Контекстный менеджер для добавления полей в логгер.
    Все логи внутри блока with log_context(...) получат переданные поля.
    """
    current_context = log_context_var.get().copy()
    current_context.update(kwargs)
    token = log_context_var.set(current_context)
    try:
        yield
    finally:
        log_context_var.reset(token)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Автоматически подмешиваем контекст
        current_context = log_context_var.get()
        if current_context:
            log_data.update(current_context)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())

        logger.addHandler(handler)

    return logger


logger = setup_logger()