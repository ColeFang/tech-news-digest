# tech-news-digest 进化方案 | Evolution Plan

## 目标 | Goal

将 tech-news-digest 从「数据采集 + LLM 判断」升级为「AI 理解 + 趋势分析 + 个性化分发」的技术情报平台。

Evolve tech-news-digest from "data collection + LLM judgment" to an "AI understanding + trend analysis + personalized delivery" tech intelligence platform.

---

## 统一 LLM 协议 | Unified LLM Protocol

所有脚本统一使用 **OpenAI 兼容协议**（`/chat/completions` 端点），通过以下环境变量配置：

All scripts use the **OpenAI-compatible protocol** (`/chat/completions` endpoint), configured via:

| 变量 Variable | 用途 Purpose | 回退 Fallback |
|------|------|------|
| `LLM_API_KEY` | API 密钥 | `MINIMAX_API_KEY` → `OPENAI_API_KEY` |
| `LLM_BASE_URL` | API 端点 | `MINIMAX_BASE_URL` → `OPENAI_BASE_URL` |
| `LLM_MODEL` | 模型名称 | 默认 `gpt-4o-mini` |

支持的提供商 (Supported Providers)：OpenAI、MiniMax、DeepSeek、Groq、OpenRouter、Ollama、vLLM 等任何兼容 `/chat/completions` 的服务。

**`scripts/llm_utils.py`** 提供统一的响应解析层，自动处理：
- 标准模型的 `content` 字段
- 推理模型的 `reasoning_content` + `content` 字段
- 截断 JSON、markdown 代码块等异常格式

---

## 方案 A：自动摘要 + 趋势分析 | Plan A: Summary + Trends

### A1. 每日总摘要 (Daily Digest Summary)
在每份 daily MD 顶部，由 LLM 生成一段 3-5 句话的今日技术形势综述，作为快讯的「前言」。

**实现方式：**
- 采集完三类数据后，将今日所有 item 的 title + abstract/description 打包发给 LLM
- LLM 输出格式：`{"summary": "今日要点：..."}`
- 插入到 `## 🤖 AI 资讯` 之前

**Prompt 示例：**
```
你是一位技术主笔，为今日技术快讯撰写一段30字左右的导语，帮助读者快速了解今日最重要的技术趋势。
要求：简洁、有观点、不重复具体内容。
```

### A2. 趋势分析 (Trend Analysis)
识别近 7 天内重复出现的话题，标注为「热门持续」；发现单日异常集中的话题，标注为「今日焦点」。

**数据结构：**
```
TRENDS = {
  "rising": [...],      # 本周出现频率上升的话题
  "stable": [...],      # 持续热门话题
  "emerging": [...]     # 单日新焦点
}
```

**实现方式：**
- 在 `daily/` 目录下扫描过去 7 天的 `.md` 文件
- 提取每篇的 AI news topics + GitHub repo names + SO tags
- 用关键词匹配做话题聚合
- 输出 `daily/trends-YYYY-MM-DD.md` 汇总

---

## 方案 B：个性化推荐 + 多渠道分发 | Plan B: Personalization + Delivery

### B1. 兴趣配置 (User Preferences)
用户可在 `preferences.yaml` 中配置关注领域：

```yaml
interests:
  - AI / LLM
  - Python
  - WebAssembly
  - CloudInfra

exclude:
  - JavaScript

max_per_category: 5

delivery:
  channels: ["wechat", "telegram"]
```

### B2. 精选推荐 (Personalized Ranking)
基于用户兴趣，对三类数据源做综合 ranking：

1. **关键词匹配** — interests 中的话题词命中文献/项目
2. **过滤排除** — exclude 中的关键词被排除
3. **得分排序** — 按匹配分数降序排列

### B3. 多渠道分发 (Multi-Channel Distribution)

| 渠道 Channel | 配置 Config | 说明 Description |
|------|--------|------|
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Bot API Markdown 消息 |
| Email | `SMTP_HOST/PORT/USER/PASS`, `EMAIL_TO` | HTML + 纯文本双格式 |
| WeChat | `WEIXIN_ILINK_HOOK` | 微信 ilink 协议精简摘要 |
| 飞书 Lark | `LARK_WEBHOOK_URL` | 群机器人 Webhook 消息 |

所有配置项均可通过环境变量或 `preferences.yaml` 设置（环境变量优先）。

---

## 文件结构（进化后）| File Structure

```
tech-news-digest/
├── scripts/
│   ├── fetch_news.py          # 主采集 + 双语翻译 + 深度分析
│   ├── summarize.py           # A1: 每日摘要生成
│   ├── analyze_trends.py      # A2: 趋势分析
│   ├── rank.py                # B1/B2: 个性化排序
│   ├── deliver.py             # B3: 多渠道分发
│   └── llm_utils.py           # 统一 LLM 响应解析
├── daily/
│   ├── YYYY-MM-DD.md          # 每日快讯（含双语翻译 + 深度分析）
│   └── trends-YYYY-MM-DD.md   # 周趋势分析
├── templates/
│   ├── daily_template.md      # 原始模板（保留）
│   └── daily_ai_template.md   # AI 增强模板
├── .github/workflows/
│   └── daily-digest.yml       # GitHub Actions 自动化
├── preferences.yaml.example   # 配置示例
├── README.md                  # 中英双语文档
└── EVOLUTION.md               # 本文档
```

---

## 环境变量 | Environment Variables

| 变量 Variable | 用途 Purpose | 示例 Example |
|------|------|------|
| `LLM_API_KEY` | 统一 LLM 密钥 | `sk-...` |
| `LLM_BASE_URL` | 统一 LLM 端点 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI 密钥（回退） | `sk-...` |
| `OPENAI_BASE_URL` | OpenAI 端点（回退） | `https://api.openai.com/v1` |
| `MINIMAX_API_KEY` | MiniMax 密钥（回退） | `eyJ...` |
| `MINIMAX_BASE_URL` | MiniMax 端点（回退） | `https://minimax.a7m.com.cn/v1` |
| `GITHUB_TOKEN` | GitHub API | `ghp_...` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot | `123:abc...` |
| `TELEGRAM_CHAT_ID` | Telegram Chat | `-100123456` |
| `SMTP_HOST` / `SMTP_PORT` | Email SMTP | `smtp.gmail.com` / `587` |
| `SMTP_USER` / `SMTP_PASS` | Email 认证 | |
| `WEIXIN_ILINK_HOOK` | 微信 ilink | |
| `LARK_WEBHOOK_URL` | 飞书 Webhook | |

---

## 开发约定 | Development Conventions

- **不修改 `master` 分支** — Obsidian vault 直接克隆 master，任何 master 变更会影响笔记阅读
- **所有开发在 `feat-ai-evolution` 分支** — 通过 worktree 或独立 clone 进行
- **最终合并后**再更新 master，或通过 PR 审阅后合并
- **偏好 YAML 配置**而非硬编码，业务逻辑与配置分离
- **LLM 调用统一**使用 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`，向后兼容旧变量名

---

## 实施进度 | Implementation Status

1. ✅ **A1 每日摘要** — `scripts/summarize.py`，JSON-mode + max_tokens=800 + 截断重试
2. ✅ **B1 兴趣配置** — `preferences.yaml` + `scripts/rank.py`
3. ✅ **B2 精选推荐** — `rank.py` 的 `match_score()` + `rank_content()`
4. ✅ **A2 趋势分析** — `scripts/analyze_trends.py` + `--trends` 标志
5. ✅ **B3 多渠道分发** — `scripts/deliver.py` 支持 Telegram / Email / WeChat / 飞书
6. ✅ **GitHub Actions** — `.github/workflows/daily-digest.yml` 全参数支持
7. ✅ **双语翻译 + 深度分析** — MiniMax / OpenAI 兼容 API 批量生成中文翻译
8. ✅ **统一 LLM 协议** — 所有脚本统一使用 OpenAI 兼容协议，支持任意提供商
9. ✅ **响应解析层** — `llm_utils.py` 兼容标准模型和推理模型
