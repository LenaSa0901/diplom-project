import json
import psycopg2
from datetime import datetime
import sys

# Настройки подключения к БД
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "123456"
}

def connect_db():
    """Подключение к Postgres"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        sys.exit(1)

def load_applicants(conn, records, group_id, load_date):
    """Вставка данных в таблицу applicants"""
    cursor = conn.cursor()
    inserted = 0
    for item in records:
        # Пропускаем записи без totalBalls (незаполненные)
        # if item.get("totalBalls") is None:
        #     continue
            
        sql = """
        INSERT INTO applicants (
            applicant_id, position, total_balls, individual_achievements_balls,
            enrollment_agreement, priority, need_hostel, benefit,
            main_highest_priority, contest_group_id, load_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (applicant_id, contest_group_id, load_date) DO NOTHING
        """
        values = (
            item.get("fio"),  # applicant_id
            item.get("position"),
            item.get("totalBalls"),
            item.get("individualAchievementsBalls"),
            item.get("enrollmentAgreement"),
            item.get("priority"),
            item.get("needHostel"),
            item.get("benefit"),
            item.get("mainHighestPriority"),
            group_id,
            load_date
        )
        cursor.execute(sql, values)
        inserted += 1
    conn.commit()
    print(f"  Вставлено {inserted} записей в applicants")
    cursor.close()

def load_subject_scores(conn, records, group_id, load_date):
    """Вставка данных в таблицу subject_scores"""
    cursor = conn.cursor()
    inserted = 0
    for item in records:
        applicant_id = item.get("fio")
        for subject in item.get("ballsBySubjects", []):
            sql = """
            INSERT INTO subject_scores (
                applicant_id, contest_group_id, subject_name, subject_id,
                ball, priority, load_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                applicant_id,
                group_id,
                subject.get("name"),
                subject.get("id"),
                subject.get("ball"),
                subject.get("priority"),
                load_date
            )
            cursor.execute(sql, values)
            inserted += 1
    conn.commit()
    print(f"  Вставлено {inserted} записей в subject_scores")
    cursor.close()

if __name__ == "__main__":
    group_id = 2457
    load_date = datetime.now()
    
    print("Читаем данные из raw_data_2457.json...")
    with open("raw_data_2457.json", "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"Найдено {len(records)} записей")
    
    print("Подключаемся к Postgres...")
    conn = connect_db()
    
    print("Загружаем данные...")
    load_applicants(conn, records, group_id, load_date)
    load_subject_scores(conn, records, group_id, load_date)
    
    conn.close()
    print("Готово!")