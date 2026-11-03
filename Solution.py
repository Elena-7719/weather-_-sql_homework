import csv
import os
import sqlite3

DB_NAME = "weather.db"
CSV_NAME = "weather.csv"


# ==========================================
# ЧАСТЬ 1: Создание базы данных и импорт
# ==========================================
def create_database():
    """Создание базы данных SQLite и таблицы measurements."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # id задается автоматически через AUTOINCREMENT
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            temperature INTEGER NOT NULL,
            precipitation TEXT,
            wind_speed INTEGER NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()
    print("[БД] База данных и таблица measurements успешно созданы.")


def import_csv_data():
    """Импорт данных из CSV-файла с приведением типов."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        with open(CSV_NAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data_to_insert = []

            for row in reader:
                # Обработка пустых значений и строки 'null' для SQL
                precipitation = row["precipitation"]
                if precipitation == "" or precipitation.lower() == "null":
                    precipitation = None

                # Приводим числа к типу int, id не передаем — он сгенерируется сам
                data_to_insert.append(
                    (
                        row["date"],
                        row["time"],
                        int(row["temperature"]),
                        precipitation,
                        int(row["wind_speed"]),
                    )
                )

            # Массовая вставка данных
            cursor.executemany(
                """
                INSERT INTO measurements (date, time, temperature, precipitation, wind_speed)
                VALUES (?, ?, ?, ?, ?)
            """,
                data_to_insert,
            )

            conn.commit()
            print(f"[БД] Данные из {CSV_NAME} успешно импортированы.")
    except FileNotFoundError:
        print(f"[Ошибка] Файл {CSV_NAME} не найден в папке со скриптом.")
    finally:
        conn.close()


# ==========================================
# ЧАСТЬ 2: Запросы к базе данных
# ==========================================
def run_sql_queries():
    """Выполнение всех 8 обязательных SQL-запросов."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    def print_result(title, rows):
        print(f"\n--- {title} ---")
        if not rows:
            print("Нет данных.")
            return
        for row in rows:
            print(row)

    # 1. Вывести все данные
    cursor.execute("SELECT * FROM measurements")
    print_result("1. Все данные из таблицы", cursor.fetchall())

    # 2. Вывести только дату, время и температуру
    cursor.execute("SELECT date, time, temperature FROM measurements")
    print_result("2. Дата, время и температура", cursor.fetchall())

    # 3. Найти все измерения, где температура ниже 0
    cursor.execute("SELECT * FROM measurements WHERE temperature < 0")
    print_result("3. Измерения с температурой ниже 0", cursor.fetchall())

    # 4. Найти все записи с дождём (rain)
    cursor.execute("SELECT * FROM measurements WHERE precipitation = 'rain'")
    print_result("4. Записи с дождем", cursor.fetchall())

    # 5. Найти измерения, где скорость ветра больше 20 км/ч
    cursor.execute("SELECT * FROM measurements WHERE wind_speed > 20")
    print_result("5. Скорость ветра > 20 км/ч", cursor.fetchall())

    # 6. Отсортировать все измерения на заданную дату по температуре по возрастанию (ввод пользователя)
    user_date = input(
        "\nВведите дату для запроса №6 (например, 2026-05-01): "
    )
    cursor.execute(
        """
        SELECT * FROM measurements 
        WHERE date = ? 
        ORDER BY temperature ASC
    """,
        (user_date,),
    )
    print_result(
        f"6. Измерения на дату {user_date}, отсортированные по температуре",
        cursor.fetchall(),
    )

    # 7. Показать все снежные (snow) измерения, отсортированные по температуре
    cursor.execute(
        """
        SELECT * FROM measurements 
        WHERE precipitation = 'snow' 
        ORDER BY temperature ASC
    """
    )
    print_result("7. Снежные измерения по температуре", cursor.fetchall())

    # 8. Найти измерения без осадков (null) и отсортировать по скорости ветра от большей к меньшей
    cursor.execute(
        """
        SELECT * FROM measurements 
        WHERE precipitation IS NULL 
        ORDER BY wind_speed DESC
    """
    )
    print_result(
        "8. Измерения без осадков по убыванию скорости ветра", cursor.fetchall()
    )

    conn.close()


# ==========================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ (СОЗДАНИЕ ТЕСТОВОГО CSV)
# ==========================================
def create_mock_csv():
    """Автоматически создает файл weather.csv, чтобы скрипт сразу работал."""
    csv_data = """id,date,time,temperature,precipitation,wind_speed
1,2026-05-01,06:00,12,null,8
2,2026-05-01,09:00,15,null,10
3,2026-05-01,12:00,18,rain,14
4,2026-05-01,15:00,17,rain,12
5,2026-05-01,18:00,14,null,9
6,2026-05-02,06:00,8,fog,6
7,2026-05-02,09:00,10,null,7
8,2026-05-02,12:00,13,rain,11
9,2026-05-02,15:00,11,rain,15
10,2026-05-02,18:00,9,null,8
11,2026-05-03,06:00,-2,snow,18
12,2026-05-03,09:00,0,snow,20
13,2026-05-03,12:00,2,fog,17
14,2026-05-03,15:00,3,null,14
15,2026-05-03,18:00,1,null,10
16,2026-05-04,06:00,5,null,9
17,2026-05-04,09:00,7,rain,13
18,2026-05-04,12:00,11,rain,16
19,2026-05-04,15:00,10,null,12
20,2026-05-04,18:00,6,fog,8"""

    with open(CSV_NAME, "w", encoding="utf-8") as f:
        f.write(csv_data.strip())


# ==========================================
# ТОЧКА ВХОДА
# ==========================================
if __name__ == "__main__":
    # 1. Если файла weather.csv еще нет, скрипт создаст его сам
    if not os.path.exists(CSV_NAME):
        create_mock_csv()

    # 2. Запуск логики
    create_database()
    import_csv_data()
    run_sql_queries()
