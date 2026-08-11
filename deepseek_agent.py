import os
import requests
from dotenv import load_dotenv

load_dotenv()

PROVIDER_CONFIGS = {
    "dashscope": {
        "key_env": "DASHSCOPE_API_KEY",
        "base_url_env": "DASHSCOPE_BASE_URL",
        "model_env": "DASHSCOPE_MODEL",
        "default_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
    },
    "deepseek": {
        "key_env": "DEEPSEEK_API_KEY",
        "base_url_env": "DEEPSEEK_BASE_URL",
        "model_env": "DEEPSEEK_MODEL",
        "default_base": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
}


class CopyAgent:
    def __init__(self):
        provider = os.getenv("AI_PROVIDER", "dashscope").lower()
        cfg = PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS["dashscope"])
        self.provider = provider
        self.api_key = os.getenv(cfg["key_env"], "")
        self.base_url = os.getenv(cfg["base_url_env"], cfg["default_base"]).rstrip("/")
        self.model = os.getenv(cfg["model_env"], cfg["default_model"])
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, scene: str, style: str, user_require: str):
        system_prompt = """你是专业文案生成Agent，严格按要求输出：
1. 根据使用场景、风格、用户需求生成纯文案；
2. 场景支持：朋友圈、小红书、短视频文案、通知公告、祝福语、商务话术；
3. 风格：简约、文艺、搞笑、正式、可爱、高冷；
4. 小红书自动加话题标签，朋友圈加合适emoji；
5. 只返回最终文案，不要解释、不要开场白。"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"使用场景：{scene}，文案风格：{style}，具体需求：{user_require}"},
        ]
        payload = {
            "model": self.model,
            "temperature": 0.7,
            "messages": messages,
        }
        url = f"{self.base_url}/chat/completions"
        resp = requests.post(url, headers=self.headers, json=payload, timeout=60)
        res_data = resp.json()
        return res_data["choices"][0]["message"]["content"].strip()


agent = CopyAgent()
