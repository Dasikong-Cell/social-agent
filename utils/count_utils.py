import os

COUNT_FILE = "count_record.txt"

def get_today_date():
    from datetime import date
    return str(date.today())

def add_count():
    today = get_today_date()
    data = {}
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                k, v = line.strip().split("=")
                data[k] = int(v)
    data[today] = data.get(today, 0) + 1
    with open(COUNT_FILE, "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")

def get_today_count():
    today = get_today_date()
    if not os.path.exists(COUNT_FILE):
        return 0
    with open(COUNT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            k, v = line.strip().split("=")
            if k == today:
                return int(v)
    return 0
