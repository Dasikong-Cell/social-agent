from apscheduler.schedulers.background import BackgroundScheduler
from qq_bot_service import send_to_qq_channel
from utils.log_utils import write_log

scheduler = BackgroundScheduler()

def add_timed_task(run_time_str: str, content: str):
    try:
        hh, mm = run_time_str.split(":")
        scheduler.add_job(
            send_to_qq_channel,
            trigger="cron",
            hour=int(hh),
            minute=int(mm),
            args=[content],
            replace_existing=True
        )
        if not scheduler.running:
            scheduler.start()
        write_log(f"添加定时任务：{run_time_str} 发布文案")
        return True
    except Exception as e:
        write_log(f"定时任务添加失败：{str(e)}")
        return False
