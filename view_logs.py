from src.utils.db_utils import init_db, get_logs
from datetime import datetime

def format_timestamp(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def main():
    # Инициализируем подключение к базе
    session = init_db()
    
    # Получаем все логи
    logs = get_logs(session)
    
    if not logs:
        print("База данных пуста")
        return
    
    print(f"\nНайдено записей: {len(logs)}\n")
    
    # Выводим каждую запись
    for log in logs:
        print(f"=== Запись от {format_timestamp(log.timestamp)} ===")
        print(f"Оригинальный промпт:\n{log.original_prompt}\n")
        print(f"Улучшенный промпт:\n{log.enhanced_prompt}\n")
        if log.prompt_metadata:
            print(f"Метаданные: {log.prompt_metadata}\n")
        print("="*50 + "\n")

if __name__ == "__main__":
    main() 