import requests
import json
import sys

sys.stdout.reconfigure(line_buffering=True)

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

if __name__ == "__main__":
    group_id = 2457
    records = fetch_data(group_id)
    print(f"Загружено записей: {len(records)}")
    
    if records:
        print("\nПример записи:")
        print(json.dumps(records[0], indent=2, ensure_ascii=False))
        with open(f"raw_data_{group_id}.json", "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"\nДанные сохранены в raw_data_{group_id}.json")
    else:
        print("Данные не получены")