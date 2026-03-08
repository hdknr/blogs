#!/bin/bash
# Import public gists as Hugo blog posts
# Usage: ./scripts/import-gists.sh

set -euo pipefail

BLOG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
POSTS_DIR="$BLOG_DIR/content/posts"
CACHE_DIR="$BLOG_DIR/.gist-cache"

mkdir -p "$POSTS_DIR" "$CACHE_DIR"

# Fetch all public gist metadata
echo "Fetching gist metadata..."
gh api gists --paginate --jq '.[] | select(.public==true) | {id: .id, description: .description, created_at: .created_at, updated_at: .updated_at, files: [.files | to_entries[] | {name: .key, raw_url: .value.raw_url, language: .value.language}]}' > "$CACHE_DIR/gists.jsonl"

TOTAL=$(wc -l < "$CACHE_DIR/gists.jsonl")
echo "Found $TOTAL public gists"

COUNT=0
SKIPPED=0

while IFS= read -r gist_json; do
    COUNT=$((COUNT + 1))

    GIST_ID=$(echo "$gist_json" | jq -r '.id')
    DESCRIPTION=$(echo "$gist_json" | jq -r '.description // ""')
    CREATED=$(echo "$gist_json" | jq -r '.created_at')
    UPDATED=$(echo "$gist_json" | jq -r '.updated_at')

    # Get the first markdown file, or first file
    FILENAME=$(echo "$gist_json" | jq -r '[.files[] | select(.name | test("\\.md$"))] | if length > 0 then .[0].name else empty end')
    if [ -z "$FILENAME" ]; then
        FILENAME=$(echo "$gist_json" | jq -r '.files[0].name')
    fi
    RAW_URL=$(echo "$gist_json" | jq -r --arg fn "$FILENAME" '[.files[] | select(.name == $fn)] | .[0].raw_url')
    LANGUAGE=$(echo "$gist_json" | jq -r '.files[0].language // ""')

    # Skip non-markdown/non-text gists
    if [[ "$FILENAME" != *.md ]] && [[ "$LANGUAGE" != "Markdown" ]]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    # Use date as slug prefix
    DATE=$(echo "$CREATED" | cut -c1-10)

    # Create slug from gist ID (safe, unique)
    SLUG="$GIST_ID"
    POST_FILE="$POSTS_DIR/${DATE}-${SLUG}.md"

    # Skip if already imported
    if [ -f "$POST_FILE" ]; then
        continue
    fi

    echo "[$COUNT/$TOTAL] Importing: $DESCRIPTION"

    # Download content
    CONTENT=$(curl -sL "$RAW_URL" 2>/dev/null || echo "")
    if [ -z "$CONTENT" ]; then
        echo "  WARN: Failed to download, skipping"
        continue
    fi

    # Extract title: use description, or first H1/H2, or filename
    TITLE="$DESCRIPTION"
    if [ -z "$TITLE" ] || [ "$TITLE" = "$FILENAME" ]; then
        TITLE=$(echo "$CONTENT" | grep -m1 '^#' | sed 's/^#\+\s*//' || echo "$FILENAME")
    fi

    # Escape quotes in title for YAML
    TITLE=$(echo "$TITLE" | sed 's/"/\\"/g')

    # Remove leading heading if it matches title (avoid duplication)
    BODY="$CONTENT"
    FIRST_HEADING=$(echo "$CONTENT" | grep -m1 '^#' | sed 's/^#\+\s*//' || echo "")
    # Strip description from first heading comparison
    CLEAN_DESC=$(echo "$DESCRIPTION" | sed 's/[[:space:]]*—.*$//' | sed 's/[[:space:]]*---.*$//')
    if [ -n "$FIRST_HEADING" ]; then
        BODY=$(echo "$CONTENT" | sed '0,/^#/{/^#/d;}')
    fi

    # Write Hugo post
    cat > "$POST_FILE" << FRONTMATTER
---
title: "$TITLE"
date: ${DATE}
lastmod: $(echo "$UPDATED" | cut -c1-10)
draft: false
gist_id: "$GIST_ID"
gist_url: "https://gist.github.com/hdknr/$GIST_ID"
categories: []
tags: []
---

$BODY
FRONTMATTER

done < "$CACHE_DIR/gists.jsonl"

echo ""
echo "Import complete: $((COUNT - SKIPPED)) posts imported, $SKIPPED non-markdown skipped"
echo "Posts are in: $POSTS_DIR"
echo ""
echo "Next step: Run the categorize script to auto-assign categories and tags"
