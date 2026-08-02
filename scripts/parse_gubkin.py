import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_data(group_id):
    base_url = "https://transfer.priem.gubkin.ru/abiturients_list/api/api.php"
    params = {
        "act": "search",
        "method": "get",
        "educationTypeId": 1,
        "contestGroupId": group_id
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    print("Запрашиваю данные...")
    resp = requests.get(base_url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])

def main():
    """Основная функция для вызова из Airflow"""
    group_id = int(os.getenv("CONTEST_GROUP_ID") or 2457)
    records = fetch_data(group_id)
    print(f"Загружено записей: {len(records)}")
    
    if records:
        filename = f"raw_data_{group_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"Данные сохранены в {filename}")
    else:
        print("Данные не получены")

if __name__ == "__main__":
    main()