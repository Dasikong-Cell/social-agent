import os

SENSITIVE_FILE = "sensitive_words.txt"

def load_sensitive_words():
    words = set()
    if os.path.exists(SENSITIVE_FILE):
        with open(SENSITIVE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip()
                if w:
                    words.add(w)
    return words

# 模块加载时缓存敏感词，避免每次请求读盘
_SENSITIVE_WORDS = load_sensitive_words()

def filter_text(text: str) -> tuple[bool, str]:
    for word in _SENSITIVE_WORDS:
        if word in text:
            return True, f"内容包含敏感词汇：{word}，已拦截"
    return False, text
