import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TARGET_CHATS = os.getenv('TARGET_CHATS').split(',')  # Список чатов для мониторинга
YOUR_CHAT_ID = int(os.getenv('YOUR_CHAT_ID'))

logger.info("Starting bot with configuration:")
logger.info(f"API_ID: {API_ID}")
logger.info(f"API_HASH: {API_HASH[:4]}...{API_HASH[-4:]}")
logger.info(f"TARGET_CHATS: {TARGET_CHATS}")
logger.info(f"YOUR_CHAT_ID: {YOUR_CHAT_ID}")

# Создаем клиент
client = TelegramClient('excursion_monitor', API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_CHATS))
async def monitor_messages(event):
    """Обработчик новых сообщений"""
    try:
        # Проверяем наличие слова "экскурсия"
        if "экскурсия" in event.text.lower():
            # Получаем информацию о чате
            chat = await event.get_chat()
            chat_title = chat.title if hasattr(chat, 'title') else chat.username
            
            # Получаем информацию о нашем аккаунте
            me = await client.get_me()
            monitor_name = f"{me.first_name} {me.last_name if me.last_name else ''}"
            
            # Формируем уведомление
            sender = event.sender
            sender_name = f"{sender.first_name} {sender.last_name if sender.last_name else ''}"
            
            notification = (
                f"🔔 Найдено слово 'экскурсия'!\n\n"
                f"Мониторинг: {monitor_name}\n"
                f"Чат: {chat_title}\n"
                f"От: {sender_name}\n"
                f"Сообщение: {event.text}\n\n"
                f"Ссылка на сообщение: https://t.me/{chat.username}/{event.id}"
            )
            
            # Отправляем уведомление
            await client.send_message(YOUR_CHAT_ID, notification)
            logger.info(f"Отправлено уведомление о сообщении от {sender_name} в чате {chat_title}")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}")

async def main():
    """Основная функция"""
    logger.info("Скрипт запущен и мониторит сообщения...")
    logger.info(f"Мониторинг чатов: {', '.join(TARGET_CHATS)}")
    
    try:
        await client.start()
        me = await client.get_me()
        logger.info(f"Авторизация успешна! Мониторинг через аккаунт: {me.first_name} {me.last_name if me.last_name else ''}")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        raise

if __name__ == '__main__':
    # Запускаем скрипт
    client.loop.run_until_complete(main()) 