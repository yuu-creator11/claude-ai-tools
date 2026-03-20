#!/usr/bin/env python3
"""
ショート動画バズ要因分析ツール

YouTube Shorts, TikTok, Instagram Reelsなどのショート動画URLを入力すると、
Claude AIがバズ要因を詳細に分析します。
"""

import sys
import json
import argparse
import yt_dlp
import anthropic


def fetch_video_metadata(url: str) -> dict:
    """yt-dlpを使って動画のメタデータを取得する"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    # 分析に必要なフィールドを抽出
    metadata = {
        "title": info.get("title", ""),
        "description": info.get("description", "")[:1000] if info.get("description") else "",
        "uploader": info.get("uploader", "") or info.get("channel", ""),
        "upload_date": info.get("upload_date", ""),
        "duration": info.get("duration", 0),
        "view_count": info.get("view_count", 0),
        "like_count": info.get("like_count", 0),
        "comment_count": info.get("comment_count", 0),
        "tags": info.get("tags", [])[:20],
        "categories": info.get("categories", []),
        "webpage_url": info.get("webpage_url", url),
        "extractor": info.get("extractor", ""),
        "thumbnail": info.get("thumbnail", ""),
        "subtitles": list(info.get("subtitles", {}).keys()),
        "automatic_captions": list((info.get("automatic_captions") or {}).keys()),
    }

    # エンゲージメント率を計算（視聴数がある場合）
    if metadata["view_count"] and metadata["view_count"] > 0:
        likes = metadata["like_count"] or 0
        comments = metadata["comment_count"] or 0
        metadata["engagement_rate"] = round((likes + comments) / metadata["view_count"] * 100, 2)
    else:
        metadata["engagement_rate"] = None

    return metadata


def format_number(n) -> str:
    """数値を読みやすい形式にフォーマット"""
    if n is None:
        return "不明"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_duration(seconds) -> str:
    """秒数を mm:ss 形式に変換"""
    if not seconds:
        return "不明"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def analyze_viral_factors(metadata: dict, url: str) -> str:
    """Claude APIを使ってバズ要因を分析する"""
    client = anthropic.Anthropic()

    # メタデータのサマリーを作成
    meta_summary = f"""
動画URL: {url}
プラットフォーム: {metadata.get('extractor', '不明')}
タイトル: {metadata.get('title', '不明')}
投稿者: {metadata.get('uploader', '不明')}
投稿日: {metadata.get('upload_date', '不明')}
動画時間: {format_duration(metadata.get('duration'))}

--- エンゲージメント指標 ---
再生数: {format_number(metadata.get('view_count'))}
いいね数: {format_number(metadata.get('like_count'))}
コメント数: {format_number(metadata.get('comment_count'))}
エンゲージメント率: {metadata.get('engagement_rate', '不明')}%

--- コンテンツ情報 ---
説明文: {metadata.get('description', '（なし）')}
タグ: {', '.join(metadata.get('tags', [])) if metadata.get('tags') else '（なし）'}
カテゴリ: {', '.join(metadata.get('categories', [])) if metadata.get('categories') else '（なし）'}
字幕: {', '.join(metadata.get('subtitles', [])) if metadata.get('subtitles') else '（なし）'}
"""

    prompt = f"""以下のショート動画のメタデータを分析し、この動画がバズ（拡散・人気）した要因を詳細に分析してください。

{meta_summary}

以下の観点から分析してください：

1. **エンゲージメント指標の評価**
   - 再生数・いいね・コメントの水準と業界平均との比較
   - エンゲージメント率の評価

2. **タイトル・フック戦略**
   - タイトルの心理的訴求点
   - クリックを誘発する要素
   - キーワードの使い方

3. **コンテンツ戦略**
   - ターゲット層の推定
   - 感情的トリガー（好奇心・感動・笑い・驚き など）
   - 視聴者が最後まで見たくなる要素

4. **アルゴリズム最適化**
   - タグ・カテゴリの戦略
   - 動画時間の最適性
   - SEO観点での評価

5. **トレンド・タイミング要因**
   - 投稿タイミングの評価
   - 時事・トレンドとの関連性

6. **総合評価と改善提案**
   - バズの主要因トップ3
   - さらに伸ばすための具体的アドバイス

日本語で、箇条書きや見出しを使って分かりやすく回答してください。"""

    print("\n🤖 Claude AIが分析中...\n")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        result = []
        thinking_shown = False

        for event in stream:
            if event.type == "content_block_start":
                if event.content_block.type == "thinking" and not thinking_shown:
                    print("💭 [分析思考中...]\n")
                    thinking_shown = True
                elif event.content_block.type == "text":
                    if thinking_shown:
                        print("=" * 60)
                        print("📊 バズ要因分析レポート")
                        print("=" * 60 + "\n")
                        thinking_shown = False

            elif event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)
                    result.append(event.delta.text)

        print("\n")
        return "".join(result)


def print_metadata_summary(metadata: dict, url: str):
    """メタデータのサマリーを表示"""
    print("\n" + "=" * 60)
    print("📹 動画情報")
    print("=" * 60)
    print(f"URL        : {url}")
    print(f"プラットフォーム: {metadata.get('extractor', '不明')}")
    print(f"タイトル    : {metadata.get('title', '不明')}")
    print(f"投稿者      : {metadata.get('uploader', '不明')}")
    print(f"投稿日      : {metadata.get('upload_date', '不明')}")
    print(f"動画時間    : {format_duration(metadata.get('duration'))}")
    print()
    print("📈 エンゲージメント指標")
    print("-" * 40)
    print(f"再生数      : {format_number(metadata.get('view_count'))}")
    print(f"いいね数    : {format_number(metadata.get('like_count'))}")
    print(f"コメント数  : {format_number(metadata.get('comment_count'))}")
    if metadata.get('engagement_rate') is not None:
        print(f"エンゲージメント率: {metadata['engagement_rate']}%")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="ショート動画のバズ要因をAIで分析するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python viral_video_analyzer.py https://www.youtube.com/shorts/xxxxx
  python viral_video_analyzer.py https://www.tiktok.com/@user/video/xxxxx
  python viral_video_analyzer.py --json https://www.youtube.com/shorts/xxxxx
        """,
    )
    parser.add_argument("url", help="分析する動画のURL")
    parser.add_argument(
        "--json",
        action="store_true",
        help="メタデータをJSON形式で出力（分析はスキップ）",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="メタデータのみ表示（AI分析なし）",
    )

    args = parser.parse_args()

    print(f"\n🔍 動画情報を取得中: {args.url}")

    try:
        metadata = fetch_video_metadata(args.url)
    except Exception as e:
        print(f"\n❌ 動画情報の取得に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return

    print_metadata_summary(metadata, args.url)

    if args.metadata_only:
        return

    try:
        analyze_viral_factors(metadata, args.url)
    except anthropic.AuthenticationError:
        print("\n❌ ANTHROPIC_API_KEY が設定されていないか無効です。", file=sys.stderr)
        print("環境変数 ANTHROPIC_API_KEY を設定してください。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ AI分析中にエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
