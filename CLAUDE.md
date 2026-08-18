# hdknr blog

Tech blog built with **Astro + AstroPaper**, hosted on GitHub Pages.

> The Hugo site it migrated from is still checked in (`hugo.toml`, `layouts/`,
> `themes/PaperMod`). It is not built by CI any more — reverting the cutover
> commit puts it straight back. Delete it once Astro has proved itself.

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
- `scripts/validate_frontmatter.py` — frontmatter/placement validation, enforced in CI
- `scripts/normalize_tags.py` — collapse tag spelling variants (dry run by default)
- `scripts/check_assets.py` — every referenced image/CSS/JS exists in the build
- `astro/` — the Astro site. `content/` and `static/` stay at the repo root and are
  read in place (`publicDir: "../static"`, collections point at `../content`)
- `astro/src/plugins/rehypePicture.mjs` — markdown images → WebP `<picture>`
- `astro/scripts/generate-images.mjs` — produces those WebP/PNG renditions
- `.pagefindversion` — pinned Pagefind version, read by both CI workflows
- `hugo.toml`, `layouts/`, `themes/`, `.hugoversion` — the old Hugo site, kept for revert
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
- Build check: `npm ci && npx astro build` in `astro/`, then
  `node scripts/generate-images.mjs` and `python3 ../scripts/check_assets.py dist --base /blogs`.
  **The build alone is not enough** — it happily produces a site whose images all 404,
  because nothing in it verifies that referenced assets exist.
- **Diagrams must be rendered as images.** Do NOT use ASCII art in fenced code blocks. Use drawio and embed PNG.
  - drawio source: `static/images/<name>.drawio`
  - export: `/Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --scale 2 --output <out>.png <in>.drawio`
  - reference in post: `![alt text in Japanese](/blogs/images/<name>.png)` (absolute path)
  - the alt text should describe the diagram in natural Japanese (SEO + accessibility)
  - **Nothing else to do for optimisation.** `astro/src/plugins/rehypePicture.mjs`
    turns that markdown into a `<picture>` with WebP at 640/1024/1600 plus a resized PNG
    fallback, and links the original so a dense diagram stays zoomable. Keep writing plain
    markdown image syntax — raw `<img>` in a post bypasses the plugin and ships the
    full-size PNG.

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

**This list is enforced**, not advisory. `scripts/validate_frontmatter.py` fails CI on any
other value, on a missing `title`/`date`/`slug`/`categories`/`tags`, and on a post outside
`content/posts/YYYY/MM/`. Run it locally with `python3 scripts/validate_frontmatter.py`.
Adding a category means editing `VALID_CATEGORIES` there **and** this list.

## No Hugo shortcodes

**Never write `{{< ref >}}`, `{{< x >}}` or any other Hugo shortcode.** Astro renders them
as literal text, and 19 posts shipped that way after the migration — `{{< ref >}}` sits in
a link target, so 47 cross-links were showing readers raw syntax instead of linking.

Nothing else catches it: the page builds, no asset is missing, and **a link that never
becomes an `<a>` has no href for the link checker to fetch**. `validate_frontmatter.py`
fails CI on any `{{<` in content for exactly that reason.

- Link another post with a plain Markdown link to its permalink:
  `[title](/blogs/posts/YYYY/MM/<slug>/)` — the slug from frontmatter, not the filename.
- `scripts/convert_hugo_shortcodes.py` converts any that slip back in.

## Tag vocabulary

**One spelling per tag, across posts AND the wiki.** They share a single `tags` taxonomy,
so `MCP` and `mcp` both build `/tags/mcp/` and only the display name differs — and which
one wins is decided by map iteration order, so it changed between builds of identical
content. `validate_frontmatter.py` fails CI on any two spellings that urlize alike.

- `astro/src/utils/slugify.ts` ports Hugo's urlize. AstroPaper's own slugify disagreed on
  106 of the 1161 tags — `AI/LLM` became `ai-llm` instead of the two-level `ai/llm`.
- Adding a tag to `TAG_RULES` in `categorize.py` means matching the spelling already used
  in content, or CI fails on the collision.
- To re-normalise after a bulk import: `python3 scripts/normalize_tags.py` (dry run),
  then `--apply`. The canonical spelling is the most-used variant.

## Search (Pagefind)

Search runs on **Pagefind**, indexed after Astro builds — `npx pagefind --site dist
--glob "{posts,wiki}/**/*.html"` in both workflows.

- **Only posts and the wiki are indexed.** Including the tag/category pages doubled the
  index (13MB → 29MB) and pushed taxonomy pages above real articles in the results.
- Indexing is actually driven by **`data-pagefind-body`**: once any page carries it,
  Pagefind indexes only pages that do. AstroPaper puts it on post articles, so the wiki
  route has to set it too or all 152 wiki pages drop out of search silently.
- The index does not exist under `astro dev`; run the pagefind command by hand to try
  search locally.
- **Known limit:** Pagefind segments Japanese via `Intl.Segmenter`, which mishandles some
  long katakana compounds. `プロンプトインジェクション` returns nothing while
  `プロンプト インジェクション` returns 175 results. The search page tells readers to
  space-separate; don't treat a 0-result compound as a broken index.

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
