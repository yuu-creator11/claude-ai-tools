"""
毎朝7時にニュース配信を実行するスケジューラー（常駐プロセス版）
"""

import logging
import signal
import sys
import time
from pathlib import Path

import schedule

from news_delivery import main as deliver_news

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def run_news_job():
    logger.info("ニュース配信ジョブ開始")
    try:
        deliver_news()
        logger.info("ニュース配信ジョブ完了")
    except Exception as e:
        logger.error(f"ニュース配信ジョブ失敗: {e}")


def handle_signal(signum, frame):
    logger.info("シグナル受信、スケジューラーを停止します")
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    schedule.every().day.at("07:00").do(run_news_job)

    logger.info("スケジューラー起動 — 毎朝07:00にニュース配信を実行します")
    next_run = schedule.next_run()
    logger.info(f"次回実行予定: {next_run}")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
