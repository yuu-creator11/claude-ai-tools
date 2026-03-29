#!/usr/bin/env python3
"""毎朝7時にAIニュースときゅうり栽培ニュースをGmailへ送るためのスクリプト。"""

from __future__ import annotations

import os
import smtplib
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.message import EmailMessage
from html import unescape
from urllib.parse import quote_plus
from urllib.request import urlopen

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
TOPIC_QUERIES = {
    "最新AIニュース": "AI OR 生成AI OR LLM",
    "きゅうり栽培ニュース": "きゅうり 栽培 OR cucumber cultivation",
}
MAX_ITEMS_PER_TOPIC = 5


def fetch_rss_items(query: str, max_items: int = MAX_ITEMS_PER_TOPIC) -> list[dict[str, str]]:
    """Google News RSSから記事を取得する。"""
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    with urlopen(url, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item")[:max_items]:
        items.append(
            {
                "title": unescape(item.findtext("title", default="(タイトルなし)")),
                "link": item.findtext("link", default=""),
                "pub_date": item.findtext("pubDate", default=""),
            }
        )
    return items


def build_email_body(all_news: dict[str, list[dict[str, str]]]) -> str:
    now_jst = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        "おはようございます！",
        f"{now_jst} 時点のニュースをお届けします。",
        "",
    ]

    for topic, items in all_news.items():
        lines.append(f"■ {topic}")
        if not items:
            lines.append("  - 記事が見つかりませんでした。")
        for idx, article in enumerate(items, start=1):
            lines.append(f"  {idx}. {article['title']}")
            lines.append(f"     {article['link']}")
            if article["pub_date"]:
                lines.append(f"     公開: {article['pub_date']}")
        lines.append("")

    lines.append("このメールは自動送信です。")
    return "\n".join(lines)


def send_gmail(subject: str, body: str) -> None:
    sender = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL", sender)

    if not sender or not app_password:
        raise RuntimeError(
            "GMAIL_ADDRESS と GMAIL_APP_PASSWORD を環境変数に設定してください。"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)


def main() -> None:
    news_by_topic = {
        topic: fetch_rss_items(query)
        for topic, query in TOPIC_QUERIES.items()
    }
    subject = f"【デイリーニュース】AI & きゅうり栽培 ({datetime.now():%Y-%m-%d})"
    body = build_email_body(news_by_topic)
    send_gmail(subject, body)
    print("メールを送信しました。")


if __name__ == "__main__":
    main()
