import logging
import datetime
from telethon import TelegramClient
from telethon.tl.types import ChatBannedRights # Optional, but good for reference

# Ensure logging is configured somewhere (e.g., in bot.py) if running this standalone
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_banned_users(client: TelegramClient, chat_id: int):
    """
    Получает список ID пользователей с АКТИВНЫМИ ограничениями в группе.
    Проверяет флаги ограничений и дату их окончания.
    """
    banned_users_ids = []
    current_time = datetime.datetime.now(datetime.timezone.utc)
    logging.info(f"Проверка ограничений для чата {chat_id}")

    try:
        # aggressive=True helps fetch more complete participant data, including rights
        async for user in client.iter_participants(chat_id, aggressive=True):
            # participant.banned_rights exists on the main user object in recent Telethon versions
            # For older versions or different participant types, it might be under user.participant
            rights = None
            if hasattr(user, 'banned_rights'):
                rights = user.banned_rights
            elif hasattr(user, 'participant') and hasattr(user.participant, 'banned_rights'):
                 rights = user.participant.banned_rights

            if rights:
                # Check if *any* restriction flag is True.
                # This signifies the user has *some* form of restriction.
                has_restrictions = any([
                    rights.view_messages, rights.send_messages, rights.send_media,
                    rights.send_stickers, rights.send_gifs, rights.send_games,
                    rights.send_inline, rights.embed_links, rights.send_polls,
                    rights.change_info, rights.invite_users, rights.pin_messages
                    # rights.manage_topics # Uncomment if relevant for your Telegram usage/version
                ])

                if has_restrictions:
                    # Now check if the restriction is currently active (not expired)
                    # If until_date is None, the restriction is permanent (or until manually removed)
                    # If until_date exists, check if it's in the future
                    is_active = rights.until_date is None or rights.until_date > current_time
                    
                    if is_active:
                        logging.debug(f"Найден пользователь с активными ограничениями: ID {user.id}, Restrictions: {rights}")
                        banned_users_ids.append(user.id)
                    else:
                         logging.debug(f"Найден пользователь с истекшими ограничениями: ID {user.id}, Restrictions expired at: {rights.until_date}")
                # else: # Optional: Log users with a rights object but no active flags
                #    logging.debug(f"Пользователь ID {user.id} имеет объект прав, но нет активных ограничений: {rights}")

        logging.info(f"Найдено {len(banned_users_ids)} пользователей с активными ограничениями.")
        return banned_users_ids

    except Exception as e:
        # Log the full error traceback for better debugging
        logging.error(f"Ошибка при получении пользователей с ограничениями в чате {chat_id}: {e}", exc_info=True)
        return [] # Return empty list on error

async def remove_banned_users(client: TelegramClient, chat_id: int):
    """Удаляет всех пользователей с активными ограничениями из группы."""
    logging.info(f"Запуск удаления пользователей с ограничениями для чата {chat_id}")
    banned_ids = await get_banned_users(client, chat_id)
    if not banned_ids:
        logging.info("Пользователи с активными ограничениями не найдены.")
        return 0 # Indicate no users were removed

    count = 0
    for user_id in banned_ids:
        try:
            # Using kick_participant is correct for removing them
            await client.kick_participant(chat_id, user_id)
            logging.info(f"Пользователь {user_id} успешно удалён из группы {chat_id}")
            count += 1
        except Exception as e:
            # Log specific errors during kicking (e.g., permissions error, user not found)
            logging.error(f"Ошибка при удалении пользователя {user_id} из чата {chat_id}: {e}", exc_info=True)
    logging.info(f"Завершено удаление пользователей. Удалено: {count}")
    return count

async def show_banned_users(client: TelegramClient, chat_id: int):
    """Записывает список ID пользователей с активными ограничениями в файл logs/banned_list.txt."""
    logging.info(f"Запрос на получение списка пользователей с ограничениями для чата {chat_id}")
    banned_ids = await get_banned_users(client, chat_id)
    
    filepath = "logs/banned_list.txt"
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            if banned_ids:
                for user_id in banned_ids:
                    file.write(f"{user_id}\n")
                logging.info(f"Список ID пользователей ({len(banned_ids)}) с ограничениями записан в {filepath}")
            else:
                # Write an empty file or a placeholder message
                file.write("") # Creates/empties the file
                logging.info(f"Активных ограничений не найдено. Файл {filepath} очищен/создан пустым.")
        return True, len(banned_ids) # Indicate success and count
    except IOError as e:
        logging.error(f"Ошибка записи в файл {filepath}: {e}", exc_info=True)
        return False, 0 # Indicate failure