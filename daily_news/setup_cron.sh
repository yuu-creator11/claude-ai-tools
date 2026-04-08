#!/bin/bash
# 毎朝7時のニュース配信をcronに登録するスクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(which python3)
SCRIPT="$SCRIPT_DIR/news_delivery.py"
ENV_FILE="$SCRIPT_DIR/.env"
LOG="$SCRIPT_DIR/logs/cron.log"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY が設定されていません。"
    echo "   export ANTHROPIC_API_KEY='your-api-key' を実行してから再試行してください。"
    exit 1
fi

# APIキーを .env ファイルに保存（cronから安全に読み込むため）
echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" > "$ENV_FILE"
chmod 600 "$ENV_FILE"
echo "🔑 APIキーを $ENV_FILE に保存しました（パーミッション: 600）"

# pip install
pip install -r "$SCRIPT_DIR/requirements.txt" -q

# cron エントリ（毎朝7時、.envからAPIキーを読み込む）
CRON_ENTRY="0 7 * * * . $ENV_FILE && $PYTHON $SCRIPT >> $LOG 2>&1"

# 既存のエントリを確認して重複登録を防ぐ
(crontab -l 2>/dev/null | grep -v "news_delivery.py"; echo "$CRON_ENTRY") | crontab -

echo "✅ cronに登録しました："
echo "   $CRON_ENTRY"
echo ""
echo "📋 現在のcron設定："
crontab -l | grep news_delivery
echo ""
echo "🧪 今すぐテスト実行する場合："
echo "   python3 $SCRIPT"
