import os
from dotenv import load_dotenv

load_dotenv()

def _strip_quotes(value: str | None) -> str | None:
    """Убирает кавычки из значения переменной окружения, если они есть."""
    if value is None:
        return None
    value = value.strip()
    # Убираем одинарные или двойные кавычки с начала и конца
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    return value

# Telegram Bot
BOT_TOKEN = _strip_quotes(os.getenv("BOT_TOKEN"))
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# DeepSeek API
DEEPSEEK_API_KEY = _strip_quotes(os.getenv("DEEPSEEK_API_KEY"))
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY не установлен в переменных окружения")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
