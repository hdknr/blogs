/**
 * Hugo's urlize, ported so taxonomy URLs survive the migration unchanged.
 *
 * AstroPaper ships a slugify built on `slugify` + `lodash.kebabcase`, which
 * disagrees with Hugo on 106 of this site's 1161 tags:
 *
 *   Hugo              AstroPaper (kebabcase)
 *   tags/ai/llm       tags/ai-llm
 *   tags/ci/cd        tags/ci-cd
 *   tags/4d-サイクル   tags/4-d-サイクル
 *   tags/claude--p    tags/claude-p
 *   tags/apache2.0    tags/apache2-0
 *
 * The rules below were not guessed. They were derived in hdknr/blogs#647 by
 * urlizing all 1161 tags and comparing against the directories Hugo actually
 * produced under public/tags/ -- nothing missing, nothing extra:
 *
 *   - whitespace collapses to `-`   `Claude Code` -> claude-code
 *   - case is folded                `MCP`         -> mcp
 *   - `/` stays a PATH SEPARATOR    `AI/LLM`      -> ai/llm  (two directories)
 *   - `_` is preserved              `$GITHUB_ENV` -> github_env
 *   - `.` is preserved              `Claude.md`   -> claude.md
 *   - repeated `-` is NOT collapsed `claude -p`   -> claude--p
 */
export const slugifyStr = (str: string): string => {
  const s = str.trim().toLowerCase().replace(/\s+/g, "-");
  // Keep word chars (Unicode, so kana and kanji pass through), plus - / .
  return s.replace(/[^\p{L}\p{N}_\-/.]/gu, "");
};

export const slugifyAll = (arr: string[]) => arr.map(str => slugifyStr(str));
