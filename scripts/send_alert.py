import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# --- Конфигурация из .env ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

APPLICANT_ID = os.getenv("APPLICANT_ID")
CONTEST_GROUP_ID = int(os.getenv("CONTEST_GROUP_ID") or 2457)
BUDGET_PLACES = int(os.getenv("BUDGET_PLACES") or 25)

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Настройки SMTP Яндекса
SMTP_SERVER = "smtp.yandex.ru"
SMTP_PORT = 465  # SSL (или 587 для TLS)
USE_SSL = True    # для порта 465

# --- Функции ---
def connect_db():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        sys.exit(1)

def get_current_position(conn):
    cursor = conn.cursor()
    # Получаем дату последней загрузки для данной специальности
    sql_latest_date = """
        SELECT MAX(load_date)
        FROM applicants
        WHERE contest_group_id = %s
    """
    cursor.execute(sql_latest_date, (CONTEST_GROUP_ID,))
    latest_date = cursor.fetchone()[0]
    if not latest_date:
        return None

    # Вычисляем позицию только среди тех, у кого agreement = true
    sql = """
        WITH ranked AS (
            SELECT 
                applicant_id,
                total_balls,
                load_date,
                ROW_NUMBER() OVER (ORDER BY total_balls DESC) AS calculated_position
            FROM applicants
            WHERE contest_group_id = %s
              AND enrollment_agreement = true
              AND load_date = %s
        )
        SELECT calculated_position, total_balls, load_date
        FROM ranked
        WHERE applicant_id = %s
    """
    cursor.execute(sql, (CONTEST_GROUP_ID, latest_date, APPLICANT_ID))
    result = cursor.fetchone()
    cursor.close()
    return result

def send_email_alert(position, total_balls, load_date):
    subject = f"⚠️  Рейтинг опустился ниже бюджетной планки! Позиция: {position}"
    body = f"""
Здравствуйте!

Ваш рейтинг на специальности (contest_group_id={CONTEST_GROUP_ID}) ухудшился.

Текущая позиция: {position}
Бюджетных мест: {BUDGET_PLACES}
Общий балл: {total_balls if total_balls else 'не указан'}
Дата загрузки данных: {load_date.strftime('%d.%m.%Y %H:%M')}

Рекомендуется проверить конкурсную ситуацию на сайте вуза.
"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        if USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Письмо отправлено на {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"❌ Ошибка отправки письма: {e}")

# --- Основной блок ---
def main():
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("❌ Не настроены EMAIL_SENDER или EMAIL_PASSWORD в .env")
        sys.exit(1)

    print(f"🔍 Проверка позиции для applicant_id={APPLICANT_ID}...")
    conn = connect_db()
    result = get_current_position(conn)
    conn.close()

    if result is None:
        print("❌ Абитуриент не найден в базе. Проверьте APPLICANT_ID.")
        sys.exit(1)

    position, total_balls, load_date = result
    print(f"📍  Текущая позиция: {position}, бюджетных мест: {BUDGET_PLACES}")

    if position > BUDGET_PLACES:
        print("⚠️  Позиция хуже бюджетной планки — отправляем алерт!")
        send_email_alert(position, total_balls, load_date)
    else:
        print("✅ Всё хорошо, позиция в пределах бюджета")

if __name__ == "__main__":
    main()