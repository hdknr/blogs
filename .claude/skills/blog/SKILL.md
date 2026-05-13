---
name: blog
description: Create a new Hugo blog post and open a pull request
arguments:
  - name: topic
    description: "Post topic, title, or a GitHub issue/comment URL"
    required: true
  - name: date
    description: "Post date (YYYY-MM-DD). Defaults to today."
    required: false
---

Create a Hugo blog post from the given topic and open a PR.

## URL allowlist (security)

**Important: when the topic is a GitHub URL, only URLs under `https://github.com/hdknr/blogs/` are accepted.**

- Allowed: `https://github.com/hdknr/blogs/issues/...`, `https://github.com/hdknr/blogs/pull/...`, etc.
- Rejected: any other GitHub URL (different repo, different owner)
- On rejection, abort and show this error message **in Japanese**:
  「エラー: このスキルで受け付ける URL は https://github.com/hdknr/blogs/ 配下のみです。」

## Procedure

### 1. Classify the topic

Decide which of the following the argument is:

- **GitHub issue-comment URL**: `https://github.com/hdknr/blogs/issues/{number}#issuecomment-{id}`
- **GitHub issue URL**: `https://github.com/hdknr/blogs/issues/{number}`
- **Text topic**: anything that is not a URL
- **Disallowed URL**: anything else → abort with the error above

### 2. GitHub issue-comment URL

Fetch the comment body and use it as the post source:

1. Parse the URL into `owner`, `repo`, `issue_number`, `comment_id`.
2. Fetch the comment:
   ```bash
   gh api /repos/{owner}/{repo}/issues/comments/{comment_id} --jq '{body, created_at, html_url}'
   ```
3. Fetch the issue title too:
   ```bash
   gh api /repos/{owner}/{repo}/issues/{issue_number} --jq '{title, body}'
   ```
4. Use the comment body as the post content.
5. Take the post title from the first heading (`#` or `##`) in the comment body. If absent, fall back to the issue title.
6. Take the date from the comment's `created_at` (overridable by the `date` argument).
7. Record the comment's `html_url` in the frontmatter as `source_url`.

### 3. GitHub issue URL

Fetch the issue body and use it as the post source:

1. Parse the URL into `owner`, `repo`, `issue_number`.
2. Fetch the issue:
   ```bash
   gh api /repos/{owner}/{repo}/issues/{issue_number} --jq '{title, body, created_at, html_url}'
   ```
3. Use the issue body as the post content.
4. Use the issue title as the post title.
5. Record the issue's `html_url` in the frontmatter as `source_url`.

### 4. Text topic

- Compose a technical blog post that fits the topic.
- If the user only provided a topic, use WebSearch to research the latest information first.
- If the user also supplied content, use that as the base and reshape it into a post.

### 5. Decide the target date

- If the `date` argument is given (YYYY-MM-DD), use it.
- For a GitHub URL, use the comment/issue `created_at`.
- Otherwise, use today (`date +%Y-%m-%d`).

### 6. Create the post file

- Path: `content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md`
- `<slug>`: derived from the topic (lowercase, alphanumerics and hyphens only)
- If the file already exists, add a suffix (e.g. `-2`).

### 7. Auto-assign categories and tags

- Follow the rules in `scripts/categorize.py` to derive the category and tags from the post body.
- Pick exactly **one** category from:
  - AI/LLM, セキュリティ, クラウド/インフラ, Web開発, プログラミング言語,
    モバイル, データベース, ツール/開発環境, ビジネス/キャリア, 地域/グルメ, その他
  - (Category names stay in Japanese — they are literal frontmatter values consumed by `scripts/categorize.py`.)
- Pick up to 5 tags relevant to the content.

## Frontmatter templates

**`slug:` is mandatory.** It must match the filename with the `YYYY-MM-DD-` date prefix removed.
Without an explicit slug, Hugo derives the URL from the Japanese title, which breaks wiki and cross-post links.

GitHub-URL-sourced post:

```yaml
---
title: "記事タイトル"
date: YYYY-MM-DD
lastmod: YYYY-MM-DD
slug: "<slug>"
draft: false
source_url: "https://github.com/..."
categories: ["カテゴリ"]
tags: ["tag1", "tag2"]
---
```

Text-topic post:

```yaml
---
title: "記事タイトル"
date: YYYY-MM-DD
lastmod: YYYY-MM-DD
slug: "<slug>"
draft: false
categories: ["カテゴリ"]
tags: ["tag1", "tag2"]
---
```

> The title field is written in Japanese — the post body is Japanese, and so is the user-facing title.

## External URL fetching

When fetching external URLs (for either drafting or fact-checking), follow this priority order:

1. **Prefer `aegis_fetch`**
   - Returns content together with a security verdict (`allow`/`warn`/`block`).
   - verdict `warn` → show the warning to the user and ask for confirmation.
   - verdict `block` → do not use the content; report to the user.
   - Claude parses the returned HTML/JSON directly.

2. **Fall back to `WebFetch` if `aegis_fetch` is unavailable**
   - MCP not connected, aegis not running, etc.

3. **Handling large `aegis_fetch` results**
   - If the result exceeds the token limit, Claude Code auto-saves it under `~/.claude/projects/.../tool-results/`.
   - That path is treated as a sensitive file, so `cp` or `Grep` against it triggers a consent prompt.
   - **Workaround: copy it into `.claude/temp/` first, then Read/Grep there.**
     ```bash
     cp /Users/hdknr/.claude/projects/.../tool-results/mcp-aegis-aegis_fetch-XXXX.txt .claude/temp/aegis-result.txt
     ```
   - Delete the copy from `.claude/temp/` when done.
   - **Permanent fix for the consent prompt**: on the first prompt, choose "Yes, and always allow access to tool-results/ from this project". After that, accesses to `tool-results/` are auto-approved.

4. **SPA (JavaScript-rendered) sites**
   - Sometimes neither `aegis_fetch` nor `WebFetch` can extract content from the raw HTML.
   - X (Twitter): rewrite the URL to `api.fxtwitter.com` and fetch via its JSON API.
   - Other SPAs: use `WebSearch` to retrieve information about the page.

## Post-structure guidelines

- Structure the post with `##` headings.
- Use syntax-highlighted code blocks for code examples.
- **Write the post body in Japanese.**
- Open with an overview / introduction.
- Include practical material (commands, configuration snippets, code samples).
- When the source is a GitHub comment/issue, preserve its content but reshape it into readable blog prose.

### Diagram rules

When an architecture or flow diagram is needed, **do not use ASCII art** — render it with drawio.

1. Create a drawio source file: `static/images/<slug>-<diagram-name>.drawio`
2. Export to PNG (`--scale 2` for high resolution):
   ```bash
   /Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --scale 2 --output static/images/<name>.png static/images/<name>.drawio
   ```
3. Reference it from the post using an absolute path:
   ```markdown
   ![図の内容を自然文で記述した alt テキスト](/blogs/images/<name>.png)
   ```
4. **alt text**: describe the diagram in natural Japanese prose (improves image-search SEO + accessibility).
5. **Do not use relative paths (`../../images/`)** — Hugo's permalink layout turns them into 404s. Always use the absolute `/blogs/images/` form.
6. Match the visual style of existing drawio files (e.g. `static/images/openclaw-gateway-architecture.drawio`).

## Fact-checking

Before committing the post, verify the facts it contains.
**This step is mandatory.**

### What to verify

Extract and verify every item in the following categories:

1. **Existence of tools / services / libraries**
   - Verify that any tool, plugin, library, or service mentioned actually exists.
   - For GitHub repo URLs, confirm with `gh api`:
     ```bash
     gh api /repos/{owner}/{repo} --jq '.full_name' 2>&1
     ```
   - For official-site URLs, fetch and verify according to "External URL fetching".

2. **Command / API correctness**
   - Confirm that install commands and CLI commands in the post use the correct syntax.
   - Cross-check against official documentation via WebSearch.

3. **Feature / spec correctness**
   - Confirm that the features and specs described actually exist.
   - Check official docs and release notes via WebSearch.

4. **Version / date accuracy**
   - Confirm version numbers and release dates are correct.

### Verification procedure

1. List every claim that needs verification.
2. Back each one up via WebSearch or `gh api`.
3. Tag the results:
   - ✅ **Confirmed** — verified
   - ⚠️ **Needs fix** — partially correct, needs adjustment
   - ❌ **Wrong** — could not be verified (possible hallucination)
   - ℹ️ **Unverified** — could not verify but low risk
4. If any ⚠️ or ❌ remains, fix the post before moving on.
5. Report the verification result to the user and ask for confirmation.

### Verification focus areas

- **GitHub repo existence**: every GitHub URL in the post must be checked via `gh api`.
- **Command syntax**: cross-check install/configuration commands against official docs.
- **"Official" plugins/extensions**: when the post claims something is "official", verify it.
- **Original claims without a source**: be especially strict on any claim added during drafting that is not in the source material.

## Agent review (quality)

After fact-checking and before committing, **run two custom agents in parallel** to raise post quality.
**This step is mandatory.**

### How to run

Trigger `tech-writer` and `seo-advisor` simultaneously via the Agent tool:

```
Agent(subagent_type="tech-writer", prompt="以下の記事をレビューしてください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
Agent(subagent_type="seo-advisor", prompt="以下の記事を分析してください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
```

- The two agents are independent, so launch them **in a single message** in parallel.
- The agents only read the post and return review notes; they do not edit files.

### Acting on review results

1. Collect both agents' outputs.
2. Filter the suggestions by priority:
   - **Apply immediately**: typos, inconsistent spelling, obvious structural issues, missing/extraneous tags
   - **Ask the user**: title changes, category changes, large structural rewrites
   - **Skip**: stylistic taste calls (minor wording), adding internal links to existing posts (handle in a separate PR)
3. Report the applied changes concisely to the user.

## Commit / branch / PR creation (worktree pattern)

After drafting the post, open a PR following this procedure.
**Important: use a git worktree so the main working tree stays clean.**
**Important: do not chain commands with `&&`.** Chained commands break the allowlist patterns and trigger a confirmation prompt every time. Issue each command as a separate Bash call.

1. Decide the branch name: `blog/YYYY-MM-DD-<slug>`
2. Create the worktree:
   ```bash
   # Run from the main repo root (stay on main)
   BRANCH_NAME="blog/YYYY-MM-DD-<slug>"
   git worktree add -b "$BRANCH_NAME" ".worktrees/<slug>" main
   ```
3. **Get the absolute path of the worktree (important):**
   ```bash
   git worktree list
   ```
   Read the absolute path from the output and use it as `$WORKTREE_DIR` for everything that follows.
   **Do not guess the absolute path from a relative one.** The Write tool happily creates files at non-existent paths, so a wrong path will silently fail with no error and force a redo.
4. Create the post file inside the worktree:
   - Path: `$WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md`
5. Check the Hugo build inside the worktree (use `--source` instead of `cd`):
   ```bash
   hugo --source "$WORKTREE_DIR" --gc 2>&1 | tail -5
   ```
6. Commit and push inside the worktree (use `git -C` instead of `cd`):
   ```bash
   git -C "$WORKTREE_DIR" add content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md
   git -C "$WORKTREE_DIR" commit -m "Add blog post: <post-title-in-Japanese>"
   git -C "$WORKTREE_DIR" push -u origin "$BRANCH_NAME"
   ```
7. Create the PR (explicitly pin the branch with `--head` and avoid `cd`):
   Write the PR body to a file inside the worktree, then pass it via `--body-file`. The worktree is outside `.claude/`, so the Write tool can write to it directly.
   ```bash
   # Use the Write tool to write the PR body to $WORKTREE_DIR/pr_body.md
   gh pr create --repo hdknr/blogs --head "$BRANCH_NAME" --title "Add blog: <post-title-in-Japanese>" --body-file "$WORKTREE_DIR/pr_body.md"
   ```
   **Note: do not use `cd "$WORKTREE_DIR" && gh pr create`.** Commands that start with `cd` do not match the `Bash(gh:*)` allowlist pattern and trigger a prompt every time. As long as you pass `--head`, you do not need to be inside the worktree.
   **Note: do not use the `--body "$(cat <<'EOF'...)"` style.** Lines starting with `#` inside the HEREDOC trip a security check ("quoted newline followed by #-prefixed line") and trigger a prompt every time.
8. Note the PR URL (used when linking back to the source).
9. **Remove the worktree once the PR is merged.** When the user confirms the merge, run `git worktree remove --force "$WORKTREE_DIR"` (the `--force` is needed because of untracked files like `pr_body.md`).

## Link back to source + 🚀-reaction mark

After the PR is created, if the topic came from a GitHub URL, post the PR link back to the source and mark it as blogged with a 🚀 reaction.

### Source is an issue-comment URL

Edit the source comment and append the blog PR link at the end.
**Use the helper script `.claude/scripts/update-issue-comment.sh`.**

Write the PR URL to a temp file first, then pass that file to the script (passing the URL as a literal argument trips a security check).
**Place the temp file inside the worktree (`$WORKTREE_DIR/pr-url.txt`).** Putting it under `.claude/temp/` may cause an overwrite-confirmation prompt; placing it inside the worktree matches the `Write(//.worktrees/**)` allowlist and gets cleaned up automatically when the worktree is removed.

```bash
# 1. Use the Write tool to write the PR URL to $WORKTREE_DIR/pr-url.txt
# 2. Pass the file path to the script
bash .claude/scripts/update-issue-comment.sh {owner} {repo} {comment_id} $WORKTREE_DIR/pr-url.txt
```

Example:
```bash
# Use Write to put "https://github.com/hdknr/blogs/pull/141" into $WORKTREE_DIR/pr-url.txt
bash .claude/scripts/update-issue-comment.sh hdknr blogs 4126127772 $WORKTREE_DIR/pr-url.txt
```

The script:
1. fetches the comment body via `gh api`
2. appends the PR link
3. builds the JSON with `jq`
4. updates the comment via `gh api --method PATCH`
5. cleans up the temp file

### Mark as blogged with 🚀

After appending the PR link, add a 🚀 reaction on the source comment to mark it as blogged:

```bash
gh api repos/{owner}/{repo}/issues/comments/{comment_id}/reactions -f content=rocket
```

**Important:** when a comment is intentionally skipped (e.g. duplicate topic), still add 🚀 manually to mark it as "handled".

### Source is an issue URL

Add a new comment on the issue announcing the PR link:

```bash
gh api /repos/{owner}/{repo}/issues/{issue_number}/comments \
  --method POST \
  --field body="📝 この Issue からブログ記事を作成しました: <PR_URL>"
```

> The announcement comment body is written in Japanese — it is user-facing.

## Post-merge follow-up

1. Send the PR URL to the user.
2. After merge, auto-remove the worktree (force-remove because of untracked files like `pr_body.md`):
   ```bash
   git worktree remove --force "$WORKTREE_DIR"
   ```
3. **Wiki auto-ingest check**: after merge, decide whether to run `/wiki-ingest`:
   1. **Skip-condition check first**: if the caller (e.g. the prompt itself) has explicitly told you to skip Wiki auto-ingest — for example by including text like "Wiki auto-ingest check は実行しないでください" or "/wiki-ingest はスキップ" — do not execute this step at all. This applies whenever `/blog` is invoked from `scripts/blog-batch.sh` or any other automation, because running `/wiki-ingest` inside the same blog branch causes wiki commits to be bundled into every blog PR and creates merge conflicts when multiple blog PRs run in parallel.
   2. Read the last ingest date from `.claude/wiki-last-ingest.txt` (default `1970-01-01` if missing).
   3. Count posts in `content/posts/` whose frontmatter `date` is on or after that date.
   4. **≥ 20 posts**: auto-run `/wiki-ingest all`, then update `.claude/wiki-last-ingest.txt` to today.
   5. **< 20 posts**: just report "Wiki update in N more posts" (do not run ingest).

   ```bash
   # Read the last ingest date
   cat .claude/wiki-last-ingest.txt
   # → 2026-04-06

   # After running ingest, use the Write tool to set
   # .claude/wiki-last-ingest.txt to today's date.
   ```

   > **Why the skip-condition matters**: a single `/blog` run that triggers `/wiki-ingest all` will add commits to the current blog branch that modify shared wiki files like `content/wiki/concepts/harness-engineering.md` and `content/wiki/tools/claude-code.md`. When `blog-batch.sh` produces many blog branches in parallel, each carrying its own wiki commit, those branches conflict with each other and with `main`. Always let the batch driver decide when to run wiki ingest (via `--final-wiki-ingest`).
