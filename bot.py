import logging
import sys
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN
from banned_users import remove_banned_users, show_banned_users

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot_errors.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    """Отправляет приветственное сообщение."""
    logging.info("Команда /start получена")
    await event.reply("Привет! Я бот для управления группой. Используйте команды:\n"
                      "/remove_banned - удалить пользователей с ограничениями\n"
                      "/show_banned - показать список пользователей с ограничениями")

@client.on(events.NewMessage(pattern='/remove_banned'))
async def handle_remove_banned(event):
    try:
        count = await remove_banned_users(client, event.chat_id)
        await event.reply(f"Удалено пользователей: {count}")
    except Exception as e:
        logging.error(f"Ошибка в /remove_banned: {e}", exc_info=True)
        await event.reply("⚠️ Ошибка при удалении пользователей!")

@client.on(events.NewMessage(pattern='/show_banned'))
async def handle_show_banned(event):
    success, count = await show_banned_users(client, event.chat_id)
    if success:
        await event.reply(f"Список обновлен! Записей: {count}")
    else:
        await event.reply("⚠️ Ошибка при записи файла!")

if __name__ == "__main__":
    logging.info("Бот запущен!")
    client.run_until_disconnected()