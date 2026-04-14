#!/bin/bash
# blog-batch.sh — 未ブログ化コメントを一括処理する
#
# Usage:
#   ./scripts/blog-batch.sh <issue_number> [options]
#
# Options:
#   --dry-run         ツイート内容を一覧表示するのみ（ブログ作成しない）
#   --limit N         処理件数の上限（デフォルト: 全件）
#   --skip-review     ファクトチェック・エージェントレビューを省略（高速化）
#   --model MODEL     使用モデル（デフォルト: sonnet）
#   --interval SECS   処理間のインターバル秒数（デフォルト: 5）
#   --overnight       夜間バッチモード（nohup 相当 + インターバル60秒 + PRサマリー出力）
#
# Examples:
#   ./scripts/blog-batch.sh 1 --dry-run                     # 未ブログ化一覧を確認
#   ./scripts/blog-batch.sh 1 --limit 3                     # 3件だけ処理
#   ./scripts/blog-batch.sh 1 --skip-review --limit 5       # レビュー省略で5件処理
#   ./scripts/blog-batch.sh 1 --overnight                   # 全件を夜間バッチで処理
#   ./scripts/blog-batch.sh 1 --overnight --interval 120    # 2分間隔で夜間バッチ

set -euo pipefail

REPO="hdknr/blogs"
ISSUE_NUMBER="${1:?Usage: blog-batch.sh <issue_number> [--dry-run] [--limit N] [--skip-review] [--model MODEL] [--interval SECS] [--overnight]}"
shift

# --- オプション解析 ---
DRY_RUN=false
LIMIT=0
SKIP_REVIEW=false
MODEL="sonnet"
INTERVAL=5
OVERNIGHT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)      DRY_RUN=true; shift ;;
    --limit)        LIMIT="$2"; shift 2 ;;
    --skip-review)  SKIP_REVIEW=true; shift ;;
    --model)        MODEL="$2"; shift 2 ;;
    --interval)     INTERVAL="$2"; shift 2 ;;
    --overnight)    OVERNIGHT=true; shift ;;
    *)              echo "Unknown option: $1"; exit 1 ;;
  esac
done

# overnight モードのデフォルト設定
if [[ "$OVERNIGHT" == "true" ]]; then
  if [[ "$INTERVAL" -eq 5 ]]; then
    INTERVAL=60  # デフォルトを60秒に
  fi
  SKIP_REVIEW=true  # 夜間は自動でレビュー省略
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE=".claude/temp/blog-batch-${TIMESTAMP}.log"
REPORT_FILE=".claude/temp/blog-batch-report-${TIMESTAMP}.md"

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
  echo ""
  echo "夜間バッチ例:"
  echo "  nohup ./scripts/blog-batch.sh ${ISSUE_NUMBER} --overnight > .claude/temp/blog-batch-stdout.log 2>&1 &"
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
declare -a PR_URLS=()
declare -a FAILED_URLS=()

# レポートヘッダー
cat > "$REPORT_FILE" <<HEADER
# Blog Batch Report

- **実行日時**: $(date '+%Y-%m-%d %H:%M:%S')
- **Issue**: #${ISSUE_NUMBER}
- **対象件数**: ${PROCESS_COUNT} / ${TOTAL}
- **モデル**: ${MODEL}
- **インターバル**: ${INTERVAL}秒
- **レビュー省略**: ${SKIP_REVIEW}

## 処理結果

| # | コメント | ステータス | PR |
|---|---------|-----------|-----|
HEADER

echo ""
echo "=== ブログ化開始 (インターバル: ${INTERVAL}秒) ==="
echo "ログ: ${LOG_FILE}"
echo "レポート: ${REPORT_FILE}"
echo ""

for i in $(seq 0 $((PROCESS_COUNT - 1))); do
  if [[ "$i" -ge "$TOTAL" ]]; then
    break
  fi

  COMMENT=$(echo "$COMMENTS" | jq -r ".[$i]")
  COMMENT_ID=$(echo "$COMMENT" | jq -r '.id')
  COMMENT_URL=$(echo "$COMMENT" | jq -r '.url')
  BODY_PREVIEW=$(echo "$COMMENT" | jq -r '.body' | head -1 | cut -c1-80)
  NUM=$((i + 1))

  echo "[${NUM}/${PROCESS_COUNT}] $(date '+%H:%M:%S') ${COMMENT_URL}"
  echo "    ${BODY_PREVIEW}"

  # claude -p でブログ作成
  PROMPT="/blog ${COMMENT_URL}"
  if [[ -n "$SKIP_REVIEW_PROMPT" ]]; then
    PROMPT="${PROMPT}
${SKIP_REVIEW_PROMPT}"
  fi

  RESULT_FILE=".claude/temp/blog-batch-result-${COMMENT_ID}.txt"
  STATUS=""
  PR_URL="-"

  if claude -p \
    --model "$MODEL" \
    --dangerously-skip-permissions \
    --max-budget-usd 2.00 \
    "$PROMPT" \
    > "$RESULT_FILE" 2>&1; then
    echo "    ✅ 成功"
    STATUS="✅ 成功"
    SUCCESS=$((SUCCESS + 1))

    # 結果から PR URL を抽出
    EXTRACTED_PR=$(grep -oE 'https://github.com/[^/]+/[^/]+/pull/[0-9]+' "$RESULT_FILE" | tail -1 || true)
    if [[ -n "$EXTRACTED_PR" ]]; then
      PR_URL="$EXTRACTED_PR"
      PR_URLS+=("$EXTRACTED_PR")
    fi
  else
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 2 ]]; then
      echo "    ⏭️  スキップ（ブログ化不適と判断）"
      STATUS="⏭️ スキップ"
      SKIPPED=$((SKIPPED + 1))
    else
      echo "    ❌ 失敗 (exit code: ${EXIT_CODE})"
      STATUS="❌ 失敗 (exit ${EXIT_CODE})"
      FAILED=$((FAILED + 1))
      FAILED_URLS+=("$COMMENT_URL")
    fi
  fi

  # レポートに行追加
  echo "| ${NUM} | [${COMMENT_ID}](${COMMENT_URL}) | ${STATUS} | ${PR_URL} |" >> "$REPORT_FILE"

  # 結果をログに追記
  echo "=== [${NUM}/${PROCESS_COUNT}] $(date '+%Y-%m-%d %H:%M:%S') ${COMMENT_URL} ===" >> "$LOG_FILE"
  cat "$RESULT_FILE" >> "$LOG_FILE" 2>/dev/null
  echo "" >> "$LOG_FILE"
  rm -f "$RESULT_FILE"

  # インターバル（最後の1件では不要）
  if [[ $((i + 1)) -lt "$PROCESS_COUNT" ]] && [[ $((i + 1)) -lt "$TOTAL" ]]; then
    echo "    💤 ${INTERVAL}秒待機..."
    sleep "$INTERVAL"
  fi
done

# --- サマリー ---
SUMMARY="
## サマリー

- ✅ 成功: ${SUCCESS} 件
- ⏭️ スキップ: ${SKIPPED} 件
- ❌ 失敗: ${FAILED} 件
- 完了時刻: $(date '+%Y-%m-%d %H:%M:%S')
"

echo "$SUMMARY" >> "$REPORT_FILE"

# PR 一覧
if [[ ${#PR_URLS[@]} -gt 0 ]]; then
  echo "## 作成された PR（レビュー待ち）" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  for pr in "${PR_URLS[@]}"; do
    echo "- ${pr}" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
fi

# 失敗一覧
if [[ ${#FAILED_URLS[@]} -gt 0 ]]; then
  echo "## 失敗したコメント（要リトライ）" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  for url in "${FAILED_URLS[@]}"; do
    echo "- ${url}" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
fi

echo ""
echo "=== 完了 $(date '+%H:%M:%S') ==="
echo "✅ 成功: ${SUCCESS} 件"
echo "⏭️  スキップ: ${SKIPPED} 件"
echo "❌ 失敗: ${FAILED} 件"
echo "📄 ログ: ${LOG_FILE}"
echo "📊 レポート: ${REPORT_FILE}"

if [[ ${#PR_URLS[@]} -gt 0 ]]; then
  echo ""
  echo "📋 作成された PR:"
  for pr in "${PR_URLS[@]}"; do
    echo "  ${pr}"
  done
fi
