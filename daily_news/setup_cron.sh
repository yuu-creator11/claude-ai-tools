#!/bin/bash
# 毎朝7時のニュース配信をcronに登録するスクリプト

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(which python3)
SCRIPT="$SCRIPT_DIR/news_delivery.py"
LOG="$SCRIPT_DIR/logs/cron.log"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY が設定されていません。"
    echo "   export ANTHROPIC_API_KEY='your-api-key' を実行してから再試行してください。"
    exit 1
fi

# pip install
pip install -r "$SCRIPT_DIR/requirements.txt" -q

# cron エントリ（毎朝7時、APIキーを環境変数として渡す）
CRON_ENTRY="0 7 * * * ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY $PYTHON $SCRIPT >> $LOG 2>&1"

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
