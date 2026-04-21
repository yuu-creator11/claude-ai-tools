"""
毎朝7時に最新のAIニュースときゅうり栽培ニュースを配信するスクリプト
"""

import anthropic
import datetime
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def fetch_news() -> str:
    client = anthropic.Anthropic()

    today = datetime.date.today().strftime("%Y年%m月%d日")

    prompt = f"""今日は{today}です。以下の2つのカテゴリについて、最新ニュースをウェブ検索で収集し、日本語で分かりやすくまとめてください。

## 1. 最新AIニュース
- 大手AI企業（OpenAI, Google, Anthropic, Meta, Mistral等）の最新動向
- 新しいAIモデルや機能のリリース
- AI政策・規制に関するニュース
- 注目のAI研究・論文

## 2. きゅうり栽培ニュース
- きゅうりの栽培技術・スマート農業の最新情報
- 病害虫・天候に関する農業情報
- 市場価格や流通の動向
- 品種改良や新技術

各カテゴリについて、重要なニュースを3〜5件ピックアップし、以下の形式でまとめてください：

---
📰 **[ニュースのタイトル]**
概要：（2〜3文で要約）
出典：（メディア名）

---

最後に、本日のまとめと農業・AIに関する注目ポイントを1段落で締めくくってください。"""

    print(f"🔍 ニュースを収集中... ({today})", flush=True)

    response_text = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=32000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[
            {"type": "web_search_20260209", "name": "web_search"},
        ],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response_text += text

    print(flush=True)
    return response_text


def save_log(content: str) -> Path:
    today = datetime.date.today().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"news_{today}.txt"

    header = f"{'='*60}\n📅 {today} 朝のニュース配信\n{'='*60}\n\n"
    log_file.write_text(header + content, encoding="utf-8")

    return log_file


def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"🌅 おはようございます！朝のニュース配信 - {now}")
    print(f"{'='*60}\n")

    try:
        news_content = fetch_news()

        log_file = save_log(news_content)
        print(f"\n\n{'='*60}")
        print(f"✅ 配信完了。ログ保存先: {log_file}")
        print(f"{'='*60}\n")

    except anthropic.AuthenticationError:
        print("❌ エラー: ANTHROPIC_API_KEY が無効です。", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("❌ エラー: APIへの接続に失敗しました。ネットワークを確認してください。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
