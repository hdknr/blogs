---
name: ship
description: Take a draft PR through ready → CI → merge → cleanup in one pass
arguments:
  - name: pr
    description: PR number to ship (e.g. 599). Required.
---

Ship a pull request: flip it out of draft, wait for the Link check to finish, merge it
only if the check passed, then do the post-merge cleanup.

This exists because `linkcheck.yml` triggers on `pull_request: [ready_for_review, reopened]`
rather than on every push. The check is meant to run **once per PR, at the moment the PR
becomes mergeable** — which makes "ready", "CI", and "merge" a single sequence rather than
three things the user has to drive by hand.

## Preconditions

- `$PR` is the PR number passed as the argument. Abort with a Japanese error if absent:
  「エラー: PR 番号を指定してください（例: /ship 599）。」
- Only operate on `hdknr/blogs`. Always pass `--repo hdknr/blogs` explicitly.
- **Never merge a PR whose Link check failed.** Report and stop instead.

## Mandatory Bash rules

Same as the rest of this repo (see `CLAUDE.md`): no `&&` / `|` chaining, no `/tmp`,
no HEREDOC with `gh`. Run each command as a separate Bash call.

Foreground `sleep` is blocked by the harness, so the CI wait **must** run as a
background Bash call (`run_in_background: true`). You get one notification when it exits.

## Procedure

### 1. Inspect the PR

```bash
gh pr view $PR --repo hdknr/blogs --json number,title,state,isDraft,headRefName,mergeable
```

- `state` is not `OPEN` → report that it is already closed/merged and jump to step 5
  (cleanup may still be pending).
- Record `headRefName` — needed to locate the worktree in step 5.

### 2. Make the PR ready (this is what triggers CI)

**If `isDraft` is `true`** — the normal `/blog` case:

```bash
gh pr ready $PR --repo hdknr/blogs
```

**If `isDraft` is `false`** — the PR was opened as ready, or commits were pushed after it
became ready. In both cases `ready_for_review` has not fired for the current head, so no
run exists for this commit. Re-toggle to fire it:

```bash
gh pr ready $PR --repo hdknr/blogs --undo
```

```bash
gh pr ready $PR --repo hdknr/blogs
```

> Do not skip the re-toggle on the assumption that "a green check is already there".
> A check from an earlier commit does not cover the current head.

### 3. Wait for the Link check

Run as a **background** Bash call. Two properties of this loop are load-bearing:

- The `length > 0` guard: immediately after `gh pr ready`, GitHub has not registered the run
  yet, and an unguarded "nothing is pending" test would pass instantly.
- The comparison is **positive** (`= "done"`), never negative (`!= "OPEN"`-style). A
  transient `gh` failure produces an empty string, which must mean *keep waiting*. A
  negated test treats that empty string as "condition met" and exits with a false positive
  — silently skipping the CI gate. Always write poll conditions so that "no answer" loops.

```bash
until [ "$(gh pr checks $PR --repo hdknr/blogs --json bucket --jq 'if length > 0 and (all(.[]; .bucket != "pending")) then "done" else "wait" end' 2>/dev/null)" = "done" ]; do sleep 20; done
```

When the notification arrives, read the result:

```bash
gh pr checks $PR --repo hdknr/blogs --json name,bucket,link
```

- every `bucket` is `pass` → continue to step 4
- any `bucket` is `fail` → **stop.** Report the failing check and its `link` to the user in
  Japanese, and do not merge. Fixing the failure means pushing a commit and re-running
  `/ship` (which re-toggles ready and re-fires CI).

### 4. Merge

This repo uses merge commits (see `git log --merges`), not squash:

```bash
gh pr merge $PR --repo hdknr/blogs --merge --delete-branch
```

### 5. Remove the worktree

`--force` is required because of untracked files like `pr_body.md` and `pr-url.txt`.
Resolve the absolute path from `git worktree list` — **do not** construct it from the
branch name by hand.

```bash
git worktree list
```

```bash
git worktree remove --force "<absolute path matching headRefName>"
```

If `--delete-branch` in step 4 left a stale local branch, prune it:

```bash
git worktree prune
```

### 6. Wiki auto-ingest check

Skip this step entirely if the caller asked to skip Wiki auto-ingest (e.g. `/blog` invoked
from `scripts/blog-batch.sh`). Bundling wiki commits into blog branches causes conflicts
when several blog PRs run in parallel.

```bash
cat .claude/wiki-last-ingest.txt
```

Count posts in `content/posts/` whose frontmatter `date` is on or after that date
(default `1970-01-01` if the file is missing).

- **≥ 20 posts** → run `/wiki-ingest all`, then use the Write tool to set
  `.claude/wiki-last-ingest.txt` to today's date.
- **< 20 posts** → just report 「あと N 本で Wiki 更新」. Do not run ingest.

## Report to the user

In Japanese, concisely:

- the check result (pass/fail, and which check)
- the merge commit / PR URL
- whether the worktree was removed
- the Wiki ingest decision and the remaining count

If the run stopped at step 3 because CI failed, say so plainly and state that nothing was
merged.
