# claude-ai-tools
Claude Codeで作るAIツール集

## 毎朝7時にAIニュース＋きゅうり栽培ニュースをGmailに送る

`send_daily_digest.py` は Google News RSS を使って、
- 最新AIニュース
- きゅうり栽培ニュース

を収集し、Gmailで指定の宛先に送信します。

### 1) Gmailアプリパスワードを作成
1. Googleアカウントで2段階認証を有効化
2. 「アプリパスワード」を発行
3. 16桁パスワードを控える

### 2) 環境変数を設定
```bash
export GMAIL_ADDRESS="your_address@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
export RECIPIENT_EMAIL="your_address@gmail.com"
```

- `RECIPIENT_EMAIL` を省略すると `GMAIL_ADDRESS` 宛に送信します。

### 3) 動作確認
```bash
python3 send_daily_digest.py
```

### 4) 毎朝7時に自動実行 (cron)
```bash
crontab -e
```
以下を追加:
```cron
0 7 * * * /usr/bin/env bash -lc 'cd /workspace/claude-ai-tools && GMAIL_ADDRESS="your_address@gmail.com" GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx" RECIPIENT_EMAIL="your_address@gmail.com" python3 send_daily_digest.py >> /tmp/daily_digest.log 2>&1'
```

## 注意
- ニュースソースは Google News RSS です。
- 検索クエリは `send_daily_digest.py` の `TOPIC_QUERIES` で調整できます。
