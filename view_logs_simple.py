import sqlite3
from datetime import datetime

def main():
    # Подключаемся к базе данных
    conn = sqlite3.connect('prompt_logs.db')
    cursor = conn.cursor()
    
    # Получаем все записи
    cursor.execute("SELECT timestamp, original_prompt, enhanced_prompt, prompt_metadata FROM prompt_logs")
    logs = cursor.fetchall()
    
    if not logs:
        print("База данных пуста")
        return
    
    print(f"\nНайдено записей: {len(logs)}\n")
    
    # Выводим каждую запись
    for log in logs:
        timestamp, original, enhanced, metadata = log
        print(f"=== Запись от {timestamp} ===")
        print(f"Оригинальный промпт:\n{original}\n")
        print(f"Улучшенный промпт:\n{enhanced}\n")
        if metadata:
            print(f"Метаданные: {metadata}\n")
        print("="*50 + "\n")
    
    conn.close()

if __name__ == "__main__":
    main() 