#!/bin/bash
# ニュース配信スケジューラーの起動・停止・状態確認

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/scheduler.pid"
LOG_FILE="$SCRIPT_DIR/logs/scheduler.log"

mkdir -p "$SCRIPT_DIR/logs"

check_api_key() {
    if [ -z "$ANTHROPIC_API_KEY" ] && [ -f "$SCRIPT_DIR/.env" ]; then
        # shellcheck source=/dev/null
        . "$SCRIPT_DIR/.env"
    fi
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "❌ ANTHROPIC_API_KEY が設定されていません。"
        echo "   export ANTHROPIC_API_KEY='your-api-key' を実行してください。"
        exit 1
    fi
}

start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "⚠️  スケジューラーは既に実行中です (PID: $(cat "$PID_FILE"))"
        exit 0
    fi

    check_api_key

    # APIキーを .env に保存
    echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" > "$SCRIPT_DIR/.env"
    chmod 600 "$SCRIPT_DIR/.env"

    cd "$SCRIPT_DIR" || exit 1
    nohup python3 scheduler.py >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ スケジューラー起動 (PID: $!)"
    echo "   ログ: $LOG_FILE"
    echo "   毎朝07:00にAIニュース・きゅうり栽培ニュースを配信します"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "⚠️  PIDファイルが見つかりません。スケジューラーは起動していません。"
        exit 0
    fi
    PID=$(cat "$PID_FILE")
    if kill -TERM "$PID" 2>/dev/null; then
        rm -f "$PID_FILE"
        echo "✅ スケジューラー停止 (PID: $PID)"
    else
        echo "⚠️  プロセス $PID が見つかりません。PIDファイルを削除します。"
        rm -f "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "✅ スケジューラー実行中 (PID: $(cat "$PID_FILE"))"
    else
        echo "⛔ スケジューラーは停止しています"
    fi
}

test_run() {
    check_api_key
    cd "$SCRIPT_DIR" || exit 1
    echo "🧪 テスト実行中..."
    python3 news_delivery.py
}

case "${1:-}" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; sleep 1; start ;;
    status)  status ;;
    test)    test_run ;;
    *)
        echo "使い方: $0 {start|stop|restart|status|test}"
        echo ""
        echo "  start    — スケジューラーをバックグラウンドで起動"
        echo "  stop     — スケジューラーを停止"
        echo "  restart  — スケジューラーを再起動"
        echo "  status   — 実行状態を確認"
        echo "  test     — 今すぐニュース配信をテスト実行"
        exit 1
        ;;
esac
