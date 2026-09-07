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

## Verification and review (mandatory, parallel fan-out)

Before committing the post, run **three independent reviewers over the same draft, in
parallel**: `fact-checker`, `tech-writer`, `seo-advisor`. **This step is mandatory.**

**Do not fact-check the post yourself.** You wrote it, so self-checking grades the answer
from the same place the error came from and misses most of it (maker-checker / four-eyes).
Facts go to `fact-checker`, which owns the full verification checklist — tool/service
existence via `gh api`, command syntax against official docs, feature and version claims,
and the ✅/⚠️/❌/ℹ️ result format. See `.claude/agents/fact-checker.md`; **do not restate
that checklist here**, or the two copies drift.

The split between the three is deliberate and already encoded in the agents: `tech-writer`
is told *not* to judge technical correctness ("それはファクトチェッカーの役割"), and
`seo-advisor` only looks at titles, tags and metadata. Three lenses on one draft — correct,
readable, findable.

### How to run

Trigger all three via the Agent tool **in a single message** so they run concurrently:

```
Agent(subagent_type="fact-checker", model="<別ティア>", prompt="以下の記事をファクトチェックしてください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
Agent(subagent_type="tech-writer",  prompt="以下の記事をレビューしてください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
Agent(subagent_type="seo-advisor",  prompt="以下の記事を分析してください: $WORKTREE_DIR/content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md")
```

**`model` on `fact-checker` is mandatory — never omit it.** Without it the agent inherits
your model, and a checker with the writer's weights shares the writer's factual priors: the
claim you were confidently wrong about looks obviously fine to it too. Separating the agent
buys context decorrelation; the tier is what buys weight decorrelation. Pick the tier
against the model **you** are running on:

| You are drafting on | `fact-checker` runs on |
|---|---|
| `sonnet` (the `blog-batch.sh` default) | `opus` |
| `opus` | `sonnet` |

- **Never `haiku`** for this agent — judging whether the evidence actually supports the
  claim is the whole job, and that is the first thing to degrade.
- The opus → sonnet direction trades some reasoning depth for decorrelation. That is the
  right trade here: with the evidence rule in `fact-checker.md`, most verdicts are decided
  by what `gh api` / WebSearch returned, not by how deeply the checker reasons.
- `tech-writer` and `seo-advisor` inherit your model on purpose. Prose quality and tags are
  taste calls, not factual priors — there is no shared-blind-spot problem to break.

- By this point the post already lives inside the worktree — `$WORKTREE_DIR` is the absolute
  path obtained in "Commit / branch / PR creation" step 3. Pass it in full: the agents run
  with their own working directory and **cannot find the file from a relative path**.
- **Do not edit the post while they are running.** All three must read the same snapshot, so
  their line numbers agree and their suggestions can be reconciled in one pass.
- None of the three writes files; they only return notes. All edits are applied by you,
  after every agent has reported.
- If the post cites external URLs, say so in the `fact-checker` prompt — it fetches them
  per "External URL fetching" above.

### Acting on the results

Collect all three outputs first, then apply edits in this order:

0. **Check that `fact-checker` actually checked.** It must return a per-claim table with an
   evidence column (a command, a query, or a URL) and a final tally. If the tally covers
   noticeably fewer claims than the post makes, or verdicts arrive with an empty evidence
   column, **send it back rather than accepting it** — an unchecked ✅ is worse than no
   check, because it launders a guess into a confirmation.
1. **`fact-checker` first, and it wins.** Every ⚠️ **要修正** and ❌ **誤り** must be fixed
   or the claim removed before the post is committed — this is a gate, not a suggestion.
   Where a factual correction and a style suggestion touch the same line, the correction
   takes precedence and the style note is re-judged against the corrected text.
2. **Apply immediately** from the other two: typos, inconsistent spelling, obvious
   structural problems, missing or extraneous tags.
3. **Ask the user**: title changes, category changes, large structural rewrites.
4. **Skip**: stylistic taste calls (minor wording), adding internal links to existing posts
   (handle in a separate PR).

Then report to the user, in Japanese and in one place:

- the ✅/⚠️/❌/ℹ️ tally from `fact-checker`, with what was fixed for each ⚠️/❌
- any ℹ️ **未確認** items left standing, so the user can judge the residual risk
- the review changes applied, listed concisely

**Ask for the user's confirmation before moving on to the commit.**

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
7. Create the PR **as a draft** (explicitly pin the branch with `--head` and avoid `cd`):
   Write the PR body to a file inside the worktree, then pass it via `--body-file`. The worktree is outside `.claude/`, so the Write tool can write to it directly.
   ```bash
   # Use the Write tool to write the PR body to $WORKTREE_DIR/pr_body.md
   gh pr create --repo hdknr/blogs --draft --head "$BRANCH_NAME" --title "Add blog: <post-title-in-Japanese>" --body-file "$WORKTREE_DIR/pr_body.md"
   ```
   **`--draft` is mandatory.** `linkcheck.yml` triggers on `pull_request: [ready_for_review, reopened]`, not on every push. Creating the PR as a draft means the Link check runs **once**, when `/ship` marks it ready — instead of once per intermediate push during review and follow-up edits.
   **Note: do not use `cd "$WORKTREE_DIR" && gh pr create`.** Commands that start with `cd` do not match the `Bash(gh:*)` allowlist pattern and trigger a prompt every time. As long as you pass `--head`, you do not need to be inside the worktree.
   **Note: do not use the `--body "$(cat <<'EOF'...)"` style.** Lines starting with `#` inside the HEREDOC trip a security check ("quoted newline followed by #-prefixed line") and trigger a prompt every time.
8. Note the PR URL (used when linking back to the source).
9. **Hand off to `/ship` — do not merge or clean up here.** Tell the user the PR is a draft and that `/ship <PR-number>` will take it through ready → CI → merge → worktree removal → Wiki ingest check. Follow-up edits requested by the user are pushed to the same draft branch; because the PR is still a draft, those pushes do not fire CI.

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

## Handing off to `/ship`

`/blog` ends at "draft PR created, source marked with 🚀". It does **not** mark the PR
ready, wait for CI, merge, remove the worktree, or run the Wiki ingest check — all of that
lives in `/ship` (`.claude/skills/ship/SKILL.md`).

1. Send the PR URL to the user and state that it is a **draft**.
2. Tell them `/ship <PR-number>` runs ready → Link check → merge → worktree removal →
   Wiki ingest check as one sequence.
3. If the user asks for follow-up edits, push them to the same branch. The PR is still a
   draft, so those pushes do not fire CI — which is the entire point of the split.

> Why the split: `linkcheck.yml` triggers on `pull_request: [ready_for_review, reopened]`.
> Keeping the PR in draft during drafting and review means the Link check runs once, at
> ship time, instead of once per push.

   ```bash
   # Read the last ingest date
   cat .claude/wiki-last-ingest.txt
   # → 2026-04-06

   # After running ingest, use the Write tool to set
   # .claude/wiki-last-ingest.txt to today's date.
   ```

   > **Why the skip-condition matters**: a single `/blog` run that triggers `/wiki-ingest all` will add commits to the current blog branch that modify shared wiki files like `content/wiki/concepts/harness-engineering.md` and `content/wiki/tools/claude-code.md`. When `blog-batch.sh` produces many blog branches in parallel, each carrying its own wiki commit, those branches conflict with each other and with `main`. Always let the batch driver decide when to run wiki ingest (via `--final-wiki-ingest`).
