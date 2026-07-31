# hdknr blog

Tech blog built with Hugo + PaperMod, hosted on GitHub Pages.

## Permission-prompt language rule

- When asking the user to approve a tool call (Bash, file ops, etc.), the prompt explanation MUST be written in **Japanese**.
- Always include a security risk estimate (%) for each of:
  - Risk of leaking passwords or private keys
  - Risk of sending data to an external server
  - Risk of executing malicious code
  - Risk of overwriting PC configuration

> Rationale: keep the cacheable instruction set in English, but switch to Japanese at the user-facing boundary. The rest of this file stays English for prompt-cache stability.

## Project layout

- `content/posts/YYYY/MM/` — blog posts (`YYYY-MM-DD-<slug>.md`, year/month subfolders)
- `content/wiki/` — wiki knowledge base (`concepts/`, `tools/`, `guides/`)
- `.claude/skills/wiki-ingest/` — `/wiki-ingest` skill
- `scripts/categorize.py` — automatic category/tag assignment
- `hugo.toml` — Hugo config
- `.claude/skills/blog/` — `/blog` skill
- `.claude/skills/ship/` — `/ship` skill (draft PR → ready → CI → merge → cleanup)
- `.claude/agents/` — custom specialist agents
- `.claude/temp/` — scratch dir (gitignored, use instead of `/tmp`)
- `.worktrees/` — git worktree dir (gitignored, lives outside `.claude/` so it is not flagged as a sensitive file)

## Custom agents (under `.claude/agents/`)

- **fact-checker** — fact-checks posts (tool names, commands, URLs, versions)
- **seo-advisor** — SEO optimisation (titles, tags, internal links)
- **tech-writer** — review of post quality (structure, readability, Japanese style)
- **trend-researcher** — tech trend research and post-idea suggestions

## Writing posts

- Use `/blog <topic-or-GitHub-issue-URL>` to drive the full pipeline from drafting through PR creation.
- **URL allowlist:** `/blog` only accepts URLs under `https://github.com/hdknr/blogs/`. Reject URLs from other repos.
- **Post body language: Japanese.** (English may appear in code, quoted snippets, or external proper nouns.)
- Post path: `content/posts/YYYY/MM/YYYY-MM-DD-<slug>.md`
- Frontmatter: `title`, `date`, `lastmod`, `draft`, `categories`, `tags` (+ `source_url`).
- Categories follow the rules in `scripts/categorize.py`.
- Build check: `hugo --gc`.
- **Diagrams must be rendered as images.** Do NOT use ASCII art in fenced code blocks. Use drawio and embed PNG.
  - drawio source: `static/images/<name>.drawio`
  - export: `/Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --scale 2 --output <out>.png <in>.drawio`
  - reference in post: `![alt text in Japanese](/blogs/images/<name>.png)` (absolute path)
  - the alt text should describe the diagram in natural Japanese (SEO + accessibility)

## External URL fetching

- For both post drafting and fact-checking, prefer the `aegis_fetch` MCP tool for external URLs.
- Fall back to `WebFetch` when aegis is unavailable (e.g. MCP not connected).
- For SPA sites (X/Twitter, etc.) use alternative APIs such as `api.fxtwitter.com`.
- aegis environment: `~/Projects/hdknr/aegis` (`docker compose up -d`).
- See the "外部 URL のフェッチ方針" section in `.claude/skills/blog/SKILL.md` for details.

## Wiki management (LLM Wiki pattern)

- `/wiki-ingest <target>` auto-generates and updates wiki pages from posts.
- Structure: `content/wiki/concepts/` (concepts), `content/wiki/tools/` (tools), `content/wiki/guides/` (how-to).
- Wiki frontmatter: `title`, `description`, `date`, `lastmod`, `aliases`, `related_posts`, `tags`.
- Wiki pages are NOT raw copies of posts — synthesise, summarise, and merge into reusable knowledge.
- `/wiki-lint` runs health checks (orphans, missing links, stale entries).
- Wiki section uses a dedicated layout under `layouts/wiki/` (`single.html`, `list.html`).
- See `.claude/skills/wiki-ingest/SKILL.md` and `.claude/skills/wiki-lint/SKILL.md`.

## Category list

AI/LLM, セキュリティ, クラウド/インフラ, Web開発, プログラミング言語, モバイル, データベース, ツール/開発環境, ビジネス/キャリア, 地域/グルメ, その他

> Category names stay in Japanese — they are the literal frontmatter values consumed by `scripts/categorize.py`.

## Mandatory Bash rules (auto-mode compatible)

Violations break auto-mode because commands fail to match the allowlist patterns. **No exceptions.**

- **No `&&` or `|` chaining** — run each command via a separate Bash call.
- **Do not use `/tmp`** — put scratch files under `.claude/temp/`.
- **Do not use a HEREDOC with `gh pr create`** — write `pr_body.md` inside the worktree via the Write tool and pass it with `--body-file`.
- **Avoid arguments containing `$(...)` command substitution** — use a temp file + `--input` instead.
- **Do not chain variable assignment and a command on the same line** — run `BRANCH_NAME=...` and `git worktree add ...` as separate calls.

See "コミット・ブランチ・PR 作成" in `.claude/skills/blog/SKILL.md` for concrete examples.

## Branch / PR conventions

- Branch name: `blog/YYYY-MM-DD-<slug>`
- Commit message: `Add blog post: <post-title-in-Japanese>`
- PR title: `Add blog: <post-title-in-Japanese>`
- When the source is a GitHub URL, append a link back to the source after the PR is created.
- **Open PRs as drafts** (`gh pr create --draft`). Merges use merge commits (`gh pr merge --merge`), not squash.

## Draft → ready → CI → merge (`/ship`)

`linkcheck.yml` triggers on `pull_request: [ready_for_review, reopened]` — **not** on every
push. So the internal link check runs once per PR, when the PR becomes mergeable.

- `/blog` creates a **draft** PR and stops there. Follow-up edits are pushed to the same
  draft branch and fire no CI.
- `/ship <PR-number>` does ready → wait for Link check → merge (only if green) → remove the
  worktree → Wiki ingest check.
- A PR that is already ready needs `gh pr ready --undo` then `gh pr ready` to fire CI for
  the current head; `/ship` handles this. A green check from an earlier commit does not
  cover the current head.
- See `.claude/skills/ship/SKILL.md`.

## Blog-post status tracking (🚀 reaction convention)

The "is this issue comment already turned into a post?" state is tracked via **GitHub reactions**:

- 🚀 (rocket) reaction → **already blogged**
- no reaction → **not yet blogged**
- The `/blog` skill auto-adds 🚀 to the source comment when it ships a post.
- For comments deliberately skipped (duplicate topic, etc.), add 🚀 manually.
- List unblogged comments:
  `gh api repos/hdknr/blogs/issues/{N}/comments --paginate --jq '.[] | select(.reactions.rocket == 0) | .html_url'`
