#!/bin/bash
# Update a GitHub issue comment by appending a blog PR link.
# Usage: update-issue-comment.sh <owner> <repo> <comment_id> <pr_url>
#
# Example:
#   bash .claude/scripts/update-issue-comment.sh hdknr blogs 4129378712 https://github.com/hdknr/blogs/pull/138

set -euo pipefail

OWNER="$1"
REPO="$2"
COMMENT_ID="$3"
PR_URL="$4"
TEMP_DIR=".claude/temp"

# Fetch current comment body
gh api "/repos/${OWNER}/${REPO}/issues/comments/${COMMENT_ID}" --jq '.body' > "${TEMP_DIR}/blog_comment_body.txt"

# Append PR link
printf '\n\n---\n📝 Blog: %s' "${PR_URL}" >> "${TEMP_DIR}/blog_comment_body.txt"

# Build JSON payload
jq -n --rawfile body "${TEMP_DIR}/blog_comment_body.txt" '{body: $body}' > "${TEMP_DIR}/patch_body.json"

# PATCH the comment
gh api "/repos/${OWNER}/${REPO}/issues/comments/${COMMENT_ID}" --method PATCH --input "${TEMP_DIR}/patch_body.json" --jq '.html_url'

# Cleanup
rm -f "${TEMP_DIR}/blog_comment_body.txt" "${TEMP_DIR}/patch_body.json"
