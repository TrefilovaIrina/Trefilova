# Telegram Excursion Monitor

Бот для мониторинга сообщений об экскурсиях в Telegram-чатах.

## Функциональность

- Мониторинг указанных Telegram-чатов
- Поиск сообщений, содержащих слово "экскурсия"
- Отправка уведомлений в личные сообщения
- Подробная информация о найденных сообщениях

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ВАШ_ЛОГИН/telegram-excursion-monitor.git
cd telegram-excursion-monitor
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` со следующими переменными:
```
API_ID=ваш_api_id
API_HASH=ваш_api_hash
TARGET_CHATS=список_чатов_через_запятую
YOUR_CHAT_ID=ваш_chat_id
```

## Запуск

```bash
python bot.py
```

## Развертывание на Render

1. Создайте аккаунт на [Render](https://render.com)
2. Подключите GitHub репозиторий
3. Создайте новый Web Service
4. Настройте переменные окружения
5. Запустите сервис

## Лицензия

MIT 