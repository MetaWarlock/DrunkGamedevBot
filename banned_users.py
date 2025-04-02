import logging
import datetime
import os
from telethon import TelegramClient
from telethon.tl.types import ChatBannedRights

async def get_banned_users(client: TelegramClient, chat_id: int):
    """
    Получает список ID пользователей с АКТИВНЫМИ ограничениями на отправку сообщений.
    """
    banned_users_ids = []
    current_time = datetime.datetime.now(datetime.timezone.utc)
    logging.info(f"Проверка ограничений для чата {chat_id}")

    try:
        async for user in client.iter_participants(chat_id, aggressive=True):
            rights = None
            if hasattr(user, 'banned_rights'):
                rights = user.banned_rights
            elif hasattr(user, 'participant') and hasattr(user.participant, 'banned_rights'):
                rights = user.participant.banned_rights

            if rights and rights.send_messages:  # Только ограничение на отправку сообщений
                is_active = rights.until_date is None or rights.until_date > current_time
                
                if is_active:
                    logging.debug(f"Найден пользователь с активным ограничением чата: ID {user.id}")
                    banned_users_ids.append(user.id)

        logging.info(f"Найдено {len(banned_users_ids)} пользователей с ограничениями на чат.")
        return banned_users_ids

    except Exception as e:
        logging.error(f"Ошибка при получении пользователей: {e}", exc_info=True)
        return []

async def remove_banned_users(client: TelegramClient, chat_id: int):
    """Удаляет пользователей с активными ограничениями на чат."""
    logging.info(f"Запуск удаления для чата {chat_id}")
    banned_ids = await get_banned_users(client, chat_id)
    
    if not banned_ids:
        logging.info("Не найдено пользователей для удаления.")
        return 0

    count = 0
    for user_id in banned_ids:
        try:
            await client.kick_participant(chat_id, user_id)
            logging.info(f"Успешно удалён пользователь {user_id}")
            count += 1
            await asyncio.sleep(1)  # Защита от FloodWait
        except Exception as e:
            logging.error(f"Ошибка удаления {user_id}: {e}")
    logging.info(f"Итог удаления: {count} пользователей")
    return count

async def show_banned_users(client: TelegramClient, chat_id: int):
    """Генерирует список пользователей в формате: Имя @username #id"""
    logging.info(f"Формирование списка для чата {chat_id}")
    banned_ids = await get_banned_users(client, chat_id)
    
    filepath = os.path.join(os.path.dirname(__file__), "logs/banned_list.txt")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            if not banned_ids:
                f.write("Список пуст")
                return True, 0
                
            for user_id in banned_ids:
                try:
                    user = await client.get_entity(user_id)
                    # Форматирование имени
                    first = user.first_name or ""
                    last = user.last_name or ""
                    name = f"{first} {last}".strip() or "[Без имени]"
                    # Форматирование юзернейма
                    username = f"@{user.username}" if user.username else "[нет @]"
                    f.write(f"{name} {username} #{user_id}\n")
                except Exception as e:
                    logging.error(f"Ошибка получения данных {user_id}: {e}")
                    f.write(f"Неизвестный пользователь #{user_id}\n")
            
            logging.info(f"Записано {len(banned_ids)} записей")
            return True, len(banned_ids)
            
    except Exception as e:
        logging.error(f"Файловая ошибка: {e}", exc_info=True)
        return False, 0