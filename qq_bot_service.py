import os
import requests
from dotenv import load_dotenv
from utils.log_utils import write_log

load_dotenv()

QQ_APPID = os.getenv("QQ_BOT_APPID")
QQ_SECRET = os.getenv("QQ_BOT_SECRET")
QQ_API = "https://api.sgroup.qq.com"
TARGET_CHANNEL = os.getenv("QQ_TARGET_CHANNEL_ID")

def get_qq_token():
    url = f"{QQ_API}/app/getAppAccessToken"
    data = {"app_id": QQ_APPID, "client_secret": QQ_SECRET}
    r = requests.post(url, json=data)
    return r.json()["access_token"]

def send_to_qq_channel(content: str):
    try:
        token = get_qq_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{QQ_API}/channels/{TARGET_CHANNEL}/messages"
        body = {"content": content}
        requests.post(url, headers=headers, json=body)
        write_log(f"成功推送文案到QQ频道，内容：{content[:50]}...")
        return True
    except Exception as e:
        write_log(f"QQ推送失败：{str(e)}")
        return False
