from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.append('/opt/airflow/scripts')

import parse_gubkin
import load_to_postgres
import send_alert

default_args = {
    'owner': 'otus',
    'depends_on_past': False,
    'start_date': datetime(2026, 8, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'check_pipeline',
    default_args=default_args,
    description='ETL для мониторинга рейтинга абитуриентов',
    schedule_interval='@hourly',
    catchup=False,
    tags=['otus', 'diplom'],
)

def run_parse():
    """Обёртка для вызова parse_gubkin.main()"""
    parse_gubkin.main()

def run_load():
    """Обёртка для вызова load_to_postgres.main()"""
    load_to_postgres.main()

def run_alert():
    """Обёртка для вызова monitor_and_alert_email.main()"""
    send_alert.main()

# Задачи
task_parse = PythonOperator(
    task_id='parse_gubkin',
    python_callable=run_parse,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_to_postgres',
    python_callable=run_load,
    dag=dag,
)

task_alert = PythonOperator(
    task_id='send_alert',
    python_callable=run_alert,
    dag=dag,
)

# Порядок выполнения
task_parse >> task_load >> task_alert