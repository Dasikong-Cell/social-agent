import os
import time

LOG_DIR = "runtime_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def write_log(content: str):
    today = time.strftime("%Y-%m-%d", time.localtime())
    log_file = os.path.join(LOG_DIR, f"{today}.log")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_line = f"[{timestamp}] {content}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)
