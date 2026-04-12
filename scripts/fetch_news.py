#!/usr/bin/env python3
"""
技术快讯采集脚本
每天自动采集: OpenAlex AI论文 · GitHub Trending · StackOverflow 热点
输出: Markdown 格式文档
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ─── 配置 ───────────────────────────────────────────────
GITHUB_TOKEN = ""  # 可选，未填写用匿名请求
OUTPUT_DIR = Path(__file__).parent.parent / "daily"
TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "daily_template.md"

# ─── 工具函数 ────────────────────────────────────────────
def _hdrs():
    h = {"Accept": "application/json", "User-Agent": "tech-news-digest/1.0"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"token {GITHUB_TOKEN}"
    return h


def format_date(fmt="%Y年%m月%d日"):
    return datetime.now().strftime(fmt)


def slug_date():
    return datetime.now().strftime("%Y-%m-%d")


# ─── 1. OpenAlex AI 论文 ─────────────────────────────────
def fetch_openalex_news(limit=5):
    """
    通过 OpenAlex API 搜索 AI/ML 高影响力论文
    """
    # 用 filter + sort（避免 search 与 cited_by_count 冲突）
    # filter 格式: OR 用 | 分隔
    url = (
        "https://api.openalex.org/works"
        "?search=artificial intelligence,machine learning,large language model"
        "&filter=publication_year:2025|2026"
        "&sort=relevance_score:desc"
        f"&per_page={limit}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"title": f"⚠️ 获取失败: {e}", "url": "#", "published": "-", "abstract": "暂无"}]

    news = []
    for item in data.get("results", []):
        title = item.get("title", "无标题")
        abs_short = item.get("abstract_inverted_index")
        if abs_short:
            # 重建摘要文本
            words = []
            idx_map = abs_short
            max_pos = max(max(positions) for positions in idx_map.values())
            recon = ["" for _ in range(max_pos + 1)]
            for word, positions in idx_map.items():
                for pos in positions:
                    recon[pos] = word
            abstract = " ".join(recon)[:300] + "..."
        else:
            abstract = "无摘要"

        # 取第一作者
        authors = item.get("authorships", [])
        author_str = ", ".join(a.get("author", {}).get("display_name", "Unknown")
                               for a in authors[:2])

        pub_date = item.get("publication_date", "Unknown")
        url2 = item.get("doi", "#")

        news.append({
            "title": title,
            "url": url2,
            "published": f"{pub_date} · {author_str}" if author_str else pub_date,
            "abstract": abstract,
        })
    return news


# ─── 2. GitHub Trending ───────────────────────────────────
def fetch_github_trending(language="", limit=10):
    """
    获取 GitHub 高星活跃项目（模拟 Trending 效果）
    使用 stars:>500 + pushed:>7days ago 过滤
    """
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = f"stars:>500 pushed:>{week_ago}"
    if language:
        query += f" language:{language}"

    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }
    try:
        resp = requests.get(url, params=params, headers=_hdrs(), timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"rank": 1, "name": f"⚠️ 获取失败: {e}", "url": "#",
                 "description": "", "language": "-", "stars": "-",
                 "forks": "-", "today_stars": "-"}]

    repos = []
    for i, repo in enumerate(data.get("items", []), 1):
        repos.append({
            "rank": i,
            "name": repo.get("full_name", "unknown"),
            "url": repo.get("html_url", "#"),
            "description": repo.get("description") or "暂无描述",
            "language": repo.get("language") or "—",
            "stars": f"{repo.get('stargazers_count', 0):,}",
            "forks": f"{repo.get('forks_count', 0):,}",
            "today_stars": "⭐+?",
        })
    return repos


# ─── 3. StackOverflow 热点 ───────────────────────────────
def fetch_stackoverflow(tags=None, limit=5):
    """
    获取 StackOverflow 热点问题
    tags: list, 如 ["python","machine-learning"]
    """
    tag_str = " OR ".join(f"{{{t}}}" for t in (tags or [])) or "unknown"
    url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "pagesize": limit,
        "tagged": ";".join(tags) if tags else "",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"title": f"⚠️ 获取失败: {e}", "link": "#",
                 "tags": [], "votes": 0, "answers": 0, "views": 0}]

    questions = []
    for q in data.get("items", []):
        questions.append({
            "title": q.get("title", "无标题"),
            "link": q.get("link", "#"),
            "tags": q.get("tags", []),
            "votes": f"{q.get('score', 0):,}",
            "answers": q.get("answer_count", 0),
            "views": f"{q.get('view_count', 0):,}",
        })
    return questions


# ─── 渲染 Markdown ───────────────────────────────────────
def render_template(context):
    lines = []
    lines.append(f"# 技术快讯 | {context['date']}")
    lines.append("")
    lines.append("> 每天自动生成 | 更新周期: 每日 08:00 (UTC+8)")
    lines.append("> 数据来源: OpenAlex · GitHub Trending · StackOverflow")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── AI 资讯 ──
    lines.append("## 🤖 AI 资讯")
    lines.append("")
    if context["ai_news"]:
        for n in context["ai_news"]:
            lines.append(f"### {n['title']}")
            lines.append(f"- **来源**: OpenAlex")
            lines.append(f"- **论文**: [{n['title']}]({n['url']})")
            lines.append(f"- **发表**: {n['published']}")
            lines.append(f"- **摘要**: {n['abstract']}")
            lines.append("")
    else:
        lines.append("*今日暂无 AI 相关论文*")
        lines.append("")
    lines.append("---")
    lines.append("")

    # ── GitHub Trending ──
    lines.append("## 🔥 GitHub Trending")
    lines.append("")
    if context["github_trending"]:
        for r in context["github_trending"]:
            lines.append(f"### {r['rank']}. {r['name']}")
            if r["description"] and r["description"] != "暂无描述":
                lines.append(f">{r['description']}")
            lines.append(f"- **语言**: {r['language']} | **⭐**: {r['stars']} | **🔱**: {r['forks']}")
            lines.append(f"- **链接**: [GitHub]({r['url']})")
            lines.append("")
    else:
        lines.append("*今日暂无热门项目*")
        lines.append("")
    lines.append("---")
    lines.append("")

    # ── StackOverflow ──
    lines.append("## 💬 StackOverflow 技术热点")
    lines.append("")
    if context["stackoverflow"]:
        for q in context["stackoverflow"]:
            lines.append(f"### {q['title']}")
            tag_html = " ".join(f"`{t}`" for t in q["tags"])
            lines.append(f"- **标签**: {tag_html}")
            lines.append(f"- **投票**: {q['votes']} | **回答**: {q['answers']} | **浏览**: {q['views']}")
            lines.append(f"- **链接**: [查看问题]({q['link']})")
            lines.append("")
    else:
        lines.append("*今日暂无热点问题*")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 📬 订阅此仓库: Watch → Releases only | 如需定制化需求 Open Issue")

    return "\n".join(lines)


# ─── 主流程 ───────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📡 正在采集数据...")
    print("  🤖 OpenAlex AI 论文...")
    ai_news = fetch_openalex_news(limit=5)

    print("  🔥 GitHub Trending...")
    github_trending = fetch_github_trending(limit=8)

    print("  💬 StackOverflow 热点...")
    stackoverflow = fetch_stackoverflow(tags=["python", "javascript", "machine-learning"], limit=5)

    context = {
        "date": format_date(),
        "ai_news": ai_news,
        "github_trending": github_trending,
        "stackoverflow": stackoverflow,
    }

    print("  📝 渲染 Markdown...")
    md_content = render_template(context)

    out_file = OUTPUT_DIR / f"{slug_date()}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ 生成完成: {out_file}")
    print(f"   - AI 资讯: {len(ai_news)} 条")
    print(f"   - GitHub Trending: {len(github_trending)} 条")
    print(f"   - StackOverflow: {len(stackoverflow)} 条")
    return str(out_file)


if __name__ == "__main__":
    main()
