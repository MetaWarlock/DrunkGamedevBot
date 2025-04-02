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
    """Удаляет пользователей с ограничениями из группы."""
    chat_id = event.chat_id
    await remove_banned_users(client, chat_id)
    await event.reply("Пользователи с ограничениями удалены.")

@client.on(events.NewMessage(pattern='/show_banned'))
async def handle_show_banned(event):
    """Показывает список пользователей с ограничениями в файле logs/banned_list.txt."""
    chat_id = event.chat_id
    await show_banned_users(client, chat_id)
    await event.reply("Список пользователей с ограничениями обновлен в logs/banned_list.txt")

if __name__ == "__main__":
    logging.info("Бот запущен!")
    client.run_until_disconnected()