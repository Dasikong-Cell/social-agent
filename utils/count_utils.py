import os
import threading

COUNT_FILE = "count_record.txt"
_COUNT_LOCK = threading.Lock()

def get_today_date():
    from datetime import date
    return str(date.today())

def _read_all():
    data = {}
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                try:
                    k, v = line.split("=", 1)
                    data[k] = int(v)
                except ValueError:
                    continue
    return data

def _write_all(data):
    with open(COUNT_FILE, "w", encoding="utf-8") as f:
        for k, v in data.items():
            f.write(f"{k}={v}\n")

def add_count():
    today = get_today_date()
    with _COUNT_LOCK:
        data = _read_all()
        data[today] = data.get(today, 0) + 1
        _write_all(data)

def get_today_count():
    today = get_today_date()
    return _read_all().get(today, 0)
