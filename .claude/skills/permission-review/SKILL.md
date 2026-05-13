---
name: permission-review
description: Analyse commands that triggered consent prompts during the session and propose changes to allowlist rules or workflow
arguments:
  - name: log_file
    description: "Path to a consent-log file. If omitted, analyse the current session's conversation context."
    required: false
---

Analyse the commands that triggered permission prompts during the session and propose changes that reduce future prompts.

## Input

### Input-source priority

1. **`log_file` argument given**: read that file.
2. **No argument (default)**: analyse the consent prompts in the current session's conversation context.

### File-based input

A consent-log file is expected to contain entries shaped roughly like:

```
Bash command
  <command body>
  <description>

Do you want to proceed?
```

Even if the exact format differs, extract consent prompts based on signals such as `Bash command` and `Do you want to proceed?`.

### Conversation-context input (default)

When no file is supplied, analyse the current conversation. Use these signals to spot consent prompts:

- Tool calls that the user explicitly denied or approved.
- Prompts that look like `Do you want to proceed?`.
- User messages mentioning permission decisions.
- Commands executed during the session that do not match any allowlist pattern in `settings.local.json`.

**If no consent prompts are found**: report "このセッションでは同意を求められたコマンドはありませんでした" and exit.

## Analysis procedure

### 1. Extract consent prompts

From the input source (file or conversation), extract every consenting command and collect:

- **Command body**: the command that was about to run.
- **Description**: the descriptive text.
- **Warning message**: any security-check warning (e.g. "Command contains a quoted newline...").

### 2. Classify the cause

Classify each command's cause into one of the following:

| Category | Description | Example |
|---|---|---|
| **Pattern missing** | No allowlist pattern matches | `git worktree add` |
| **Security check** | Triggered a security rule | `#`-prefixed line inside a HEREDOC, `$()` substitution |
| **Path restriction** | Target path is not allowed | write to `/tmp` |
| **Compound command** | Command chained with `&&` / `\|` does not match a pattern | `rm ... && git worktree remove ...` |
| **External write** | Write operation to an external service | `gh api --method PATCH` |

### 3. Inspect the current allowlist

Read these to understand the current permissions:

- `permissions.allow` array in `.claude/settings.local.json`
- Rules in `CLAUDE.md`
- Skill definitions under `.claude/skills/`

### 4. Build improvement proposals

For each command, suggest improvements in this priority order:

#### Priority 1: Add an allowlist pattern (simplest)

If the command is safe and likely to recur, add a pattern to `settings.local.json`.

```json
"Bash(git worktree:*)"
```

**Cautions:**
- Make the pattern as narrow as possible (do not propose anything as broad as `Bash(*)`).
- Be conservative about external write operations (PATCH, POST, DELETE).

#### Priority 2: Workflow change (root cause)

If changing the command itself avoids the prompt:

- HEREDOC → `--body-file` (avoids the `#`-line trigger)
- `$()` substitution → temp file + `--input`
- `/tmp` → `.claude/temp/` (in-project scratch dir)
- `&&` chain → split into separate calls

#### Priority 3: Update skill definitions

Edit the relevant `SKILL.md` so future runs do not produce the problematic pattern.

### 5. Risk assessment

For each proposal, assess the security risk:

- **Low**: local-only operations (file read/write, git)
- **Medium**: external read operations (`gh api` GET)
- **High**: external write operations (`gh api` PATCH / POST)

For high-risk operations, prefer a workflow fix over a new allowlist entry.

## Output format

Emit a report in this shape:

```markdown
## Permission Review レポート

### 分析結果

| # | コマンド | カテゴリ | リスク | 提案 |
|---|---|---|---|---|
| 1 | `git worktree add ...` | パターン未登録 | 低 | 許可パターン追加 |
| 2 | `gh pr create --body "$(cat ...)"` | セキュリティチェック | 低 | --body-file 方式に変更 |
| ... | ... | ... | ... | ... |

### 提案1: settings.local.json への許可パターン追加

追加するパターン:
- `"Bash(git worktree:*)"`
- ...

### 提案2: ワークフローの変更

- SKILL.md の XX 行目: HEREDOC → --body-file 方式に変更
- ...

### 提案3: スキル定義の更新

- ...
```

> The report is user-facing, so the prose stays Japanese.

## Applying changes

After presenting the report, get user approval before applying any change.
When applying, update the appropriate file(s):

1. `.claude/settings.local.json` — add allowlist patterns
2. `.claude/skills/*/SKILL.md` — adjust command examples
3. `CLAUDE.md` — add rules as needed

**Important: never auto-apply.** Allowlist changes affect security, so confirm with the user first.
