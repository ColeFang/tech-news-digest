# 技术快讯 | Tech News Digest

每日自动更新的技术快讯，聚合以下三个数据源：

Daily auto-updated tech newsletter, aggregating three data sources:

- 🤖 **OpenAlex** — AI / ML 学术论文 (Academic Papers)
- 🔥 **GitHub Trending** — 当日热门开源项目 (Trending Repositories)
- 💬 **StackOverflow** — 技术热点问答 (Hot Q&A)

## ✨ AI 增强功能 | AI-Enhanced Features

| 编号 | 功能 | 说明 | Feature | Description |
|------|------|------|---------|-------------|
| A1 | 每日摘要 | LLM 生成今日技术形势导语 | Daily Summary | LLM-generated overview |
| A2 | 趋势分析 | 扫描过去 7 天识别热门/上升/新兴话题 | Trend Analysis | 7-day topic detection |
| B1/B2 | 个性化排序 | 基于 `preferences.yaml` 匹配用户兴趣 | Personalized Ranking | Interest-based sorting |
| B3 | 多渠道分发 | Telegram / Email / WeChat / 飞书 Lark | Multi-Channel Delivery | 4 channels supported |

**双语内容 | Bilingual Content:**

每日快讯中，AI 论文标题、摘要、GitHub 项目描述均提供中英双语翻译，并附带深度分析和落地场景推荐。

All daily digests include bilingual (Chinese + English) translations for paper titles, abstracts, and project descriptions, along with deep analysis and application scenario recommendations.

## 📂 目录结构 | Directory Structure

```
tech-news-digest/
├── daily/                    # 每日快讯文档 (Daily digests)
│   └── trends-YYYY-MM-DD.md # 周趋势报告 (Weekly trend reports)
├── templates/                # MD 模板 (Markdown templates)
├── scripts/
│   ├── fetch_news.py         # 主采集脚本 (Main pipeline)
│   ├── summarize.py          # A1 每日摘要 (Daily summary)
│   ├── analyze_trends.py     # A2 趋势分析 (Trend analysis)
│   ├── rank.py               # B1/B2 个性化排序 (Personalized ranking)
│   ├── deliver.py            # B3 多渠道分发 (Multi-channel delivery)
│   └── llm_utils.py          # 统一 LLM 适配层 (Unified LLM adapter)
├── preferences.yaml.example  # 用户偏好配置模板 (Config template)
├── EVOLUTION.md              # 进化方案文档 (Evolution plan)
└── README.md
```

## ⚙️ 本地运行 | Getting Started

```bash
# 克隆 (Clone)
git clone git@github.com:ColeFang/tech-news-digest.git
cd tech-news-digest

# 安装依赖 (Install dependencies)
pip install requests pyyaml

# 运行采集 (Run digest)
python scripts/fetch_news.py                    # 纯文本版 (Plain text)
python scripts/fetch_news.py --trends           # 含 A2 趋势分析 (With trend analysis)
python scripts/fetch_news.py --trends=14        # 含 14 天趋势分析 (14-day trends)
python scripts/fetch_news.py --deliver=telegram # 采集 + 分发 (Fetch + deliver)
```

## 🔑 LLM 配置 | LLM Configuration

所有脚本统一使用 **OpenAI 兼容协议**（`/chat/completions` 端点），支持以下任意提供商：

All scripts use the **OpenAI-compatible protocol** (`/chat/completions` endpoint), supporting any provider:

| 提供商 Provider | `LLM_BASE_URL` | `LLM_MODEL` 示例 |
|-----------------|-----------------|-------------------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o-mini` |
| **MiniMax** | `https://minimax.a7m.com.cn/v1` | `MiniMax-M2.7-highspeed` |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` |
| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `anthropic/claude-sonnet-4` |
| **Ollama** | `http://localhost:11434/v1` | `llama3` |

```bash
# 统一配置方式 (Unified configuration)
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o-mini"

# 向后兼容旧变量名 (Backward compatible)
# OPENAI_API_KEY, OPENAI_BASE_URL, MINIMAX_API_KEY, MINIMAX_BASE_URL 仍可使用
```

**环境变量优先级 (Priority):** `LLM_API_KEY` > `MINIMAX_API_KEY` > `OPENAI_API_KEY`

## 📅 文档命名规范 | File Naming

```
daily/YYYY-MM-DD.md         # 每日快讯 (Daily digest)
daily/trends-YYYY-MM-DD.md  # 周趋势报告 (Trend report)
```

## 🔧 个性化配置 | Personalization

复制配置模板并填写个人兴趣：

Copy the config template and fill in your interests:

```bash
cp preferences.yaml.example preferences.yaml
# 编辑 preferences.yaml (Edit preferences.yaml)
```

## 📬 分发渠道配置 | Delivery Channels

| 渠道 Channel | 配置项 Config | 说明 Description |
|------|--------|------|
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | 向 @BotFather 创建 Bot (Create via @BotFather) |
| Email | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_TO` | 支持 Gmail / 任意 SMTP (Gmail / any SMTP) |
| WeChat | `WEIXIN_ILINK_HOOK` | 微信 ilink 协议 (WeChat ilink) |
| 飞书 Lark | `LARK_WEBHOOK_URL` | 群机器人 Webhook (Group Bot Webhook) |

所有配置项均可通过环境变量或 `preferences.yaml` 设置（环境变量优先）。

All settings can be configured via environment variables or `preferences.yaml` (env vars take priority).

## 🔄 与 Obsidian 同步 | Obsidian Sync

```bash
# 在 Obsidian vault 目录 (In your Obsidian vault directory)
git clone git@github.com:ColeFang/tech-news-digest.git ~/Documents/tech-news-digest
```

安装 **Obsidian Git** 插件，设置自动 push 时间，即可在 Obsidian 中阅读每日快讯。

Install the **Obsidian Git** plugin, set auto-push intervals, and read daily digests directly in Obsidian.

---

> 由 [Hermes Agent](https://github.com/ColeFang/hermes-agent) 自动维护
