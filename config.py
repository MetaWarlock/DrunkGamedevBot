import os
from dotenv import load_dotenv

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

missing = [k for k, v in {'API_ID': API_ID, 'API_HASH': API_HASH, 'BOT_TOKEN': BOT_TOKEN}.items() if not v]
if missing:
    raise ValueError(f"Отсутствуют переменные: {', '.join(missing)}")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("Не все переменные окружения (API_ID, API_HASH, BOT_TOKEN) указаны в .env")