#!/usr/bin/env python3
"""Auto-categorize Hugo blog posts based on title and content keywords."""

import os
import re
import glob

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')

# Category rules: (category, [keywords])
# Order matters - first match wins for primary category
CATEGORY_RULES = [
    # AI/LLM
    ("AI/LLM", [
        "claude", "gpt", "chatgpt", "llm", "ai ", "ai-", "aiエージェント",
        "anthropic", "openai", "gemini", "copilot", "qwen", "ollama",
        "プロンプト", "prompt", "rag", "langchain", "agent", "エージェント",
        "機械学習", "深層学習", "大規模言語", "生成ai", "notebooklm",
        "mcp", "agentic", "openhands", "openclaw", "openfang",
        "vibe coding", "cursor", "ハルシネーション", "sycophancy",
        "シコファンシー", "fingpt", "animaworks", "goose",
    ]),
    # セキュリティ
    ("セキュリティ", [
        "セキュリティ", "security", "脆弱性", "vulnerability", "攻撃",
        "inject", "インジェクション", "xss", "csrf", ".env", "dotenv",
        "認証", "暗号", "encrypt", "credential", "trivy", "shannon",
        "ペネトレーション", "dmarc", "spf", "hijack", "マルウェア",
        "1password", "keychain", "vault", "lkr",
    ]),
    # クラウド/インフラ
    ("クラウド/インフラ", [
        "aws", "gcp", "azure", "docker", "kubernetes", "k8s",
        "terraform", "cloudfront", "bigquery", "bedrock",
        "nginx", "apache", "linux", "centos", "ubuntu",
        "sre", "devops", "ci/cd", "github actions",
    ]),
    # Web開発
    ("Web開発", [
        "django", "flask", "fastapi", "rails", "laravel",
        "react", "vue", "next", "nuxt", "angular",
        "javascript", "typescript", "node", "deno", "bun",
        "html", "css", "bootstrap", "jquery", "webpack",
        "rest", "api", "graphql", "websocket",
        "wagtail", "wordpress", "cakephp", "php",
    ]),
    # プログラミング言語
    ("プログラミング言語", [
        "python", "rust", "go ", "golang", "swift",
        "java ", "kotlin", "ruby", "perl", "c++",
        "haskell", "elixir", "scala",
    ]),
    # モバイル
    ("モバイル", [
        "ios", "android", "swift", "kotlin",
        "react native", "flutter", "mobile",
    ]),
    # データベース
    ("データベース", [
        "mysql", "postgresql", "postgres", "sqlite",
        "redis", "mongodb", "database", "sql",
        "doctrine", "orm",
    ]),
    # ツール/開発環境
    ("ツール/開発環境", [
        "git ", "github", "vscode", "vim", "emacs",
        "homebrew", "brew", "packer", "vagrant",
        "editor", "terminal", "tmux", "shell",
        "obsidian", "figma", "theatre.js",
    ]),
    # ビジネス/キャリア
    ("ビジネス/キャリア", [
        "ビジネス", "経営", "採用", "キャリア", "仕事",
        "マネジメント", "組織", "市場", "売上", "vc",
        "スタートアップ", "起業", "ceo", "cto",
        "言語化", "勉強法", "学習", "ロードマップ",
        "デザイナー", "エンジニア",
    ]),
    # 地域/グルメ
    ("地域/グルメ", [
        "town:", "横浜", "中華街", "恵比寿", "渋谷",
        "新宿", "目黒", "世田谷", "品川", "港区",
        "レストラン", "カフェ", "ラーメン", "グルメ",
        "running", "散歩",
    ]),
]

# Tag extraction rules
TAG_RULES = [
    ("claude-code", ["claude code", "claude-code"]),
    ("claude", ["claude"]),
    ("chatgpt", ["chatgpt", "gpt-4", "gpt-3"]),
    ("llm", ["llm", "大規模言語"]),
    ("openai", ["openai"]),
    ("anthropic", ["anthropic"]),
    ("gemini", ["gemini"]),
    ("qwen", ["qwen"]),
    ("ollama", ["ollama"]),
    ("mcp", [" mcp ", "mcp ", " mcp"]),
    ("agent", ["agent", "エージェント"]),
    ("rag", [" rag ", "rag "]),
    ("prompt", ["プロンプト", "prompt"]),
    ("python", ["python"]),
    ("django", ["django"]),
    ("rust", [" rust ", "rust "]),
    ("go", [" go ", "golang"]),
    ("swift", ["swift"]),
    ("javascript", ["javascript", " js "]),
    ("typescript", ["typescript"]),
    ("react", ["react"]),
    ("docker", ["docker"]),
    ("kubernetes", ["kubernetes", " k8s"]),
    ("aws", [" aws ", "aws-", "aws "]),
    ("github", ["github"]),
    ("github-actions", ["github actions"]),
    ("security", ["セキュリティ", "security", "脆弱性"]),
    ("hugo", ["hugo"]),
    ("github-pages", ["github pages"]),
    ("figma", ["figma"]),
    ("obsidian", ["obsidian"]),
    ("vscode", ["vscode", "vs code"]),
    ("tdd", ["tdd", "テスト駆動"]),
    ("bigquery", ["bigquery"]),
    ("nginx", ["nginx"]),
    ("mysql", ["mysql"]),
    ("redis", ["redis"]),
    ("wordpress", ["wordpress"]),
    ("laravel", ["laravel"]),
    ("homebrew", ["homebrew"]),
]


def parse_frontmatter(filepath):
    """Parse Hugo frontmatter and content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None, None, content

    fm_text = match.group(1)
    body = match.group(2)

    # Simple YAML-like parse
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            fm[key] = value

    return fm, fm_text, body


def categorize(title, body_preview):
    """Assign category based on title and first 500 chars of body."""
    text = (title + " " + body_preview[:500]).lower()

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return category

    return "その他"


def extract_tags(title, body_preview):
    """Extract tags based on title and content."""
    text = (title + " " + body_preview[:1000]).lower()
    tags = []

    for tag, keywords in TAG_RULES:
        for kw in keywords:
            if kw.lower() in text:
                tags.append(tag)
                break

    return tags[:5]  # Max 5 tags


def update_post(filepath):
    """Update a post's frontmatter with category and tags."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return False

    fm_text = match.group(1)
    body = match.group(2)

    # Skip if already categorized
    if 'categories: [' in fm_text:
        cat_match = re.search(r'categories: \[(.*?)\]', fm_text)
        if cat_match and cat_match.group(1).strip():
            return False  # Already has categories

    # Get title
    title_match = re.search(r'title:\s*"(.*?)"', fm_text)
    if not title_match:
        title_match = re.search(r'title:\s*(.*)', fm_text)
    title = title_match.group(1) if title_match else ""

    category = categorize(title, body)
    tags = extract_tags(title, body)

    # Update frontmatter
    cat_str = f'["{category}"]'
    tag_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]" if tags else "[]"

    new_fm = re.sub(r'categories: \[\]', f'categories: {cat_str}', fm_text)
    new_fm = re.sub(r'tags: \[\]', f'tags: {tag_str}', new_fm)

    new_content = f"---\n{new_fm}\n---\n{body}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def main():
    posts = sorted(glob.glob(os.path.join(POSTS_DIR, '**', '*.md'), recursive=True))
    updated = 0
    category_counts = {}

    for filepath in posts:
        if os.path.basename(filepath) == '_index.md':
            continue
        if update_post(filepath):
            updated += 1

            # Count categories for summary
            with open(filepath, 'r') as f:
                content = f.read()
            cat_match = re.search(r'categories: \["(.*?)"\]', content)
            if cat_match:
                cat = cat_match.group(1)
                category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"Updated {updated} posts")
    print("\nCategory distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


if __name__ == '__main__':
    main()
