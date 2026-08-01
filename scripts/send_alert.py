import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sys

# Конфигурация БД
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "mysecretpassword"
}

# НАСТРОЙТЕ ПОД СЕБЯ:
APPLICANT_ID = "1345505"          # ваш идентификатор из поля fio
CONTEST_GROUP_ID = 2457           # ваша специальность
BUDGET_PLACES = 25                # количество бюджетных мест на специальности

# Настройки почты (для отправки алертов)
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # пароль приложения, не обычный
EMAIL_RECEIVER = "your_email@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def connect_db():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        sys.exit(1)

def get_current_position(conn):
    """Получить последнюю позицию абитуриента"""
    cursor = conn.cursor()
    sql = """
    SELECT position, total_balls, load_date
    FROM applicants
    WHERE applicant_id = %s AND contest_group_id = %s
    ORDER BY load_date DESC
    LIMIT 1
    """
    cursor.execute(sql, (APPLICANT_ID, CONTEST_GROUP_ID))
    result = cursor.fetchone()
    cursor.close()
    return result  # (position, total_balls, load_date)

def send_alert(position, total_balls, load_date):
    """Отправить email с предупреждением"""
    subject = f"⚠️  Рейтинг опустился ниже бюджетной планки! Позиция: {position}"
    body = f"""
    Здравствуйте!
    
    Ваш рейтинг на специальности (contest_group_id={CONTEST_GROUP_ID}) ухудшился.
    
    Текущая позиция: {position}
    Бюджетных мест: {BUDGET_PLACES}
    Общий балл: {total_balls if total_balls else 'не указан'}
    Дата загрузки данных: {load_date}
    
    Рекомендуется проверить конкурсную ситуацию на сайте вуза.
    """
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Алерт отправлен на {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")

if __name__ == "__main__":
    print(f"Проверка позиции для applicant_id={APPLICANT_ID}, contest_group_id={CONTEST_GROUP_ID}...")
    conn = connect_db()
    
    result = get_current_position(conn)
    conn.close()
    
    if result is None:
        print("❌ Абитуриент не найден в базе. Проверьте APPLICANT_ID.")
        sys.exit(1)
    
    position, total_balls, load_date = result
    print(f"Текущая позиция: {position}, бюджетных мест: {BUDGET_PLACES}")
    
    if position > BUDGET_PLACES:
        print(f"⚠️  Позиция {position} хуже бюджетной планки {BUDGET_PLACES}")
        send_alert(position, total_balls, load_date)
    else:
        print(f"✅ Всё хорошо. Позиция {position} в пределах бюджета")