import sqlite3
from datetime import datetime

def show_all_logs():
    """Показать все записи в базе"""
    print("\n=== ВСЕ ЗАПИСИ В БАЗЕ ===")
    conn = sqlite3.connect('prompt_logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompt_logs")
    logs = cursor.fetchall()
    
    for log in logs:
        print(f"\nЗапись от {log[1]}")  # timestamp
        print(f"Оригинальный промпт: {log[2][:100]}...")  # первые 100 символов
    conn.close()

def count_logs():
    """Подсчитать количество записей"""
    conn = sqlite3.connect('prompt_logs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM prompt_logs")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"\nВсего записей в базе: {count}")

def add_test_log():
    """Добавить тестовую запись"""
    conn = sqlite3.connect('prompt_logs.db')
    cursor = conn.cursor()
    
    # Добавляем новую запись
    cursor.execute("""
        INSERT INTO prompt_logs (timestamp, original_prompt, enhanced_prompt, prompt_metadata)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now(),
        "Тестовый промпт",
        "Улучшенный тестовый промпт",
        '{"test": "value"}'
    ))
    
    conn.commit()
    conn.close()
    print("\nДобавлена тестовая запись")

def main():
    while True:
        print("\nВыберите действие:")
        print("1. Показать все записи")
        print("2. Подсчитать количество записей")
        print("3. Добавить тестовую запись")
        print("4. Выход")
        
        choice = input("\nВаш выбор (1-4): ")
        
        if choice == "1":
            show_all_logs()
        elif choice == "2":
            count_logs()
        elif choice == "3":
            add_test_log()
        elif choice == "4":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main() 