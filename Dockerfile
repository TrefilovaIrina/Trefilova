FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем директорию для файла сессии
RUN mkdir -p /app/telegram_excursion_bot

# Устанавливаем права на запись
RUN chmod -R 777 /app/telegram_excursion_bot

CMD ["python", "telegram_excursion_bot/bot.py"] 