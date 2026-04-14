#!/bin/bash
# blog-batch.sh — 未ブログ化コメントを一括処理する
#
# Usage:
#   ./scripts/blog-batch.sh <issue_number> [options]
#
# Options:
#   --dry-run       ツイート内容を一覧表示するのみ（ブログ作成しない）
#   --limit N       処理件数の上限（デフォルト: 全件）
#   --skip-review   ファクトチェック・エージェントレビューを省略（高速化）
#   --model MODEL   使用モデル（デフォルト: sonnet）
#
# Examples:
#   ./scripts/blog-batch.sh 1 --dry-run              # 未ブログ化一覧を確認
#   ./scripts/blog-batch.sh 1 --limit 3              # 3件だけ処理
#   ./scripts/blog-batch.sh 1 --skip-review --limit 5 # レビュー省略で5件処理

set -euo pipefail

REPO="hdknr/blogs"
ISSUE_NUMBER="${1:?Usage: blog-batch.sh <issue_number> [--dry-run] [--limit N] [--skip-review] [--model MODEL]}"
shift

# --- オプション解析 ---
DRY_RUN=false
LIMIT=0
SKIP_REVIEW=false
MODEL="sonnet"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    DRY_RUN=true; shift ;;
    --limit)      LIMIT="$2"; shift 2 ;;
    --skip-review) SKIP_REVIEW=true; shift ;;
    --model)      MODEL="$2"; shift 2 ;;
    *)            echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- 未ブログ化コメント取得 ---
echo "=== Issue #${ISSUE_NUMBER} の未ブログ化コメントを取得中... ==="
COMMENTS_JSON=$(gh api "repos/${REPO}/issues/${ISSUE_NUMBER}/comments" \
  --paginate \
  --jq '[.[] | select(.reactions.rocket == 0) | {id: .id, url: .html_url, body: .body}]')

# jq で配列を結合（--paginate は複数の配列を出力する）
COMMENTS=$(echo "$COMMENTS_JSON" | jq -s 'add')
TOTAL=$(echo "$COMMENTS" | jq 'length')

if [[ "$TOTAL" -eq 0 ]]; then
  echo "✅ 未ブログ化コメントはありません"
  exit 0
fi

echo "📋 未ブログ化コメント: ${TOTAL} 件"

if [[ "$LIMIT" -gt 0 ]]; then
  PROCESS_COUNT="$LIMIT"
  echo "📌 処理上限: ${LIMIT} 件"
else
  PROCESS_COUNT="$TOTAL"
fi

# --- dry-run: 一覧表示 ---
if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "=== 未ブログ化コメント一覧 ==="
  echo ""
  for i in $(seq 0 $((TOTAL - 1))); do
    COMMENT=$(echo "$COMMENTS" | jq -r ".[$i]")
    URL=$(echo "$COMMENT" | jq -r '.url')
    BODY=$(echo "$COMMENT" | jq -r '.body' | head -3)
    echo "[$((i + 1))/${TOTAL}] ${URL}"
    echo "    ${BODY}"
    echo ""
  done
  echo "=== ブログ化するには --dry-run を外して実行してください ==="
  exit 0
fi

# --- ブログ化処理 ---
SKIP_REVIEW_PROMPT=""
if [[ "$SKIP_REVIEW" == "true" ]]; then
  SKIP_REVIEW_PROMPT="ファクトチェックとエージェントレビュー（tech-writer, seo-advisor）は省略してください。"
fi

SUCCESS=0
FAILED=0
SKIPPED=0
LOG_FILE=".claude/temp/blog-batch-$(date +%Y%m%d-%H%M%S).log"

echo ""
echo "=== ブログ化開始 ==="
echo "ログ: ${LOG_FILE}"
echo ""

for i in $(seq 0 $((PROCESS_COUNT - 1))); do
  if [[ "$i" -ge "$TOTAL" ]]; then
    break
  fi

  COMMENT=$(echo "$COMMENTS" | jq -r ".[$i]")
  COMMENT_ID=$(echo "$COMMENT" | jq -r '.id')
  COMMENT_URL=$(echo "$COMMENT" | jq -r '.url')
  BODY_PREVIEW=$(echo "$COMMENT" | jq -r '.body' | head -1 | cut -c1-80)

  echo "[$((i + 1))/${PROCESS_COUNT}] ${COMMENT_URL}"
  echo "    ${BODY_PREVIEW}"

  # claude -p でブログ作成
  PROMPT="/blog ${COMMENT_URL}"
  if [[ -n "$SKIP_REVIEW_PROMPT" ]]; then
    PROMPT="${PROMPT}
${SKIP_REVIEW_PROMPT}"
  fi

  RESULT_FILE=".claude/temp/blog-batch-result-${COMMENT_ID}.txt"

  if claude -p \
    --model "$MODEL" \
    --dangerously-skip-permissions \
    --max-budget-usd 2.00 \
    "$PROMPT" \
    > "$RESULT_FILE" 2>&1; then
    echo "    ✅ 成功"
    SUCCESS=$((SUCCESS + 1))
  else
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 2 ]]; then
      echo "    ⏭️  スキップ（ブログ化不適と判断）"
      SKIPPED=$((SKIPPED + 1))
    else
      echo "    ❌ 失敗 (exit code: ${EXIT_CODE})"
      FAILED=$((FAILED + 1))
    fi
  fi

  # 結果をログに追記
  echo "=== ${COMMENT_URL} ===" >> "$LOG_FILE"
  cat "$RESULT_FILE" >> "$LOG_FILE" 2>/dev/null
  echo "" >> "$LOG_FILE"
  rm -f "$RESULT_FILE"

  # レート制限対策: 短い待機
  if [[ $((i + 1)) -lt "$PROCESS_COUNT" ]]; then
    sleep 5
  fi
done

echo ""
echo "=== 完了 ==="
echo "✅ 成功: ${SUCCESS} 件"
echo "⏭️  スキップ: ${SKIPPED} 件"
echo "❌ 失敗: ${FAILED} 件"
echo "📄 ログ: ${LOG_FILE}"
