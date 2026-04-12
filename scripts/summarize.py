#!/usr/bin/env python3
"""
A1: 每日摘要生成器
在每份快讯开头，由 LLM 生成一段今日技术形势综述（3-5 句话）
"""

import requests
import os
from typing import List, Dict


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def build_summary_prompt(ai_news: List[dict], github_trending: List[dict], stackoverflow: List[dict]) -> str:
    """构建摘要 prompt，将所有内容浓缩为参考上下文"""

    # 提取 AI 论文标题
    ai_titles = "；".join(n.get("title", "") for n in ai_news[:5]) or "无"

    # 提取 GitHub 项目名 + 描述
    gh_items = []
    for r in github_trending[:8]:
        name = r.get("name", "")
        desc = r.get("description", "")[:60]
        gh_items.append(f"{name}: {desc}")
    gh_text = "；".join(gh_items) or "无"

    # 提取 SO 问题标题
    so_titles = "；".join(q.get("title", "") for q in stackoverflow[:5]) or "无"

    prompt = f"""你是一位技术主笔，为今日技术快讯撰写一段50-80字的导语，帮助读者快速把握今日最重要的技术趋势。

今日内容概览：

【AI 论文】{ai_titles}

【GitHub 热门】{gh_text}

【StackOverflow 热点】{so_titles}

要求：
1. 50-80 字，简洁有力
2. 点出今日最值得关注的 1-2 个技术趋势
3. 不要罗列具体条目，要提炼趋势
4. 使用中文，行文自然
5. 不要以"今日"开头
"""
    return prompt


def gen_daily_summary(ai_news: List[dict], github_trending: List[dict], stackoverflow: List[dict]) -> str:
    """调用 LLM 生成每日摘要"""
    if not OPENAI_API_KEY:
        return "（未配置 OPENAI_API_KEY，跳过摘要）"

    prompt = build_summary_prompt(ai_news, github_trending, stackoverflow)

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是一位资深技术主笔，擅长用简洁有力的语言捕捉技术趋势。输出只包含导语正文，不要额外解释。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 200,
        "temperature": 0.7,
    }

    # 兼容不同 API 端点
    if "openrouter" in OPENAI_BASE_URL:
        payload["model"] = LLM_MODEL
    elif "groq" in OPENAI_BASE_URL:
        payload["model"] = "llama-3.1-8b-instant"

    try:
        resp = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        summary = data["choices"][0]["message"]["content"].strip()
        # 去掉可能的引号
        summary = summary.strip('"').strip("'").strip()
        return summary
    except Exception as e:
        return f"（摘要生成失败: {e}）"


def format_summary_markdown(summary: str) -> str:
    """将摘要格式化为 Markdown 片段"""
    if not summary or summary.startswith("（"):
        return ""
    return f"""> **今日要点** {summary}

---"""
