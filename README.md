# x-reader

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Universal content reader — fetch, transcribe, and digest content from any platform.

Give it a URL (article, video, podcast, tweet), get back structured content. Works as CLI, Python library, or MCP server.

> ## 🔗 源项目 / Original Project
>
> **本项目 Fork 自 [runesleo/x-reader](https://github.com/runesleo/x-reader)**
>
> Original author: [@runes_leo](https://x.com/runes_leo) — more AI tools at [leolabs.me](https://leolabs.me)
>
> 本仓库地址: [deku0818/x-reader](https://github.com/deku0818/x-reader)

---

## What It Does

```
Any URL → Platform Detection → Fetch Content → Unified Output
              ↓                      ↓
         auto-detect           text: Jina Reader
         7+ platforms          video: yt-dlp subtitles
                               audio: Whisper transcription
                               API: Bilibili / RSS / Telegram
```

## Quick Start — MCP Server

推荐通过 `x-reader mcp` 命令启动 MCP server：

### 1. 安装

```bash
git clone https://github.com/deku0818/x-reader.git
cd x-reader
pip install -e ".[mcp]"
```

### 2. 启动 MCP Server

```bash
# stdio 模式（默认，适用于 Claude Desktop / Cursor 等）
x-reader mcp

# SSE 模式（适用于远程调用）
x-reader mcp --transport sse --host 127.0.0.1 --port 8000
```

### 3. 配置 MCP Client

在你的 MCP 客户端（如 Claude Desktop、Cursor、Kiro 等）中添加配置：

```json
{
  "mcpServers": {
    "x-reader": {
      "command": "x-reader",
      "args": ["mcp"]
    }
  }
}
```

或者直接指定 Python 模块路径：

```json
{
  "mcpServers": {
    "x-reader": {
      "command": "python",
      "args": ["-m", "x_reader.cli", "mcp"]
    }
  }
}
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `read_url(url)` | 读取任意 URL，返回结构化内容 |
| `read_batch(urls)` | 批量读取多个 URL |
| `list_inbox()` | 查看已读取的内容列表 |
| `detect_platform(url)` | 识别 URL 所属平台 |

---

## CLI Usage

```bash
# 读取任意 URL
x-reader https://mp.weixin.qq.com/s/abc123

# 读取推文
x-reader https://x.com/elonmusk/status/123456

# 批量读取
x-reader https://url1.com https://url2.com

# 平台登录（一次性，用于浏览器回退）
x-reader login xhs

# 查看 inbox
x-reader list
```

## Use as Library

```python
import asyncio
from x_reader.reader import UniversalReader

async def main():
    reader = UniversalReader()
    content = await reader.read("https://mp.weixin.qq.com/s/abc123")
    print(content.title)
    print(content.content[:200])

asyncio.run(main())
```

## Supported Platforms

| Platform | Text Fetch | Video/Audio Transcript |
|----------|-----------|----------------------|
| YouTube | ✅ Jina | ✅ yt-dlp subtitles → Groq Whisper fallback |
| Bilibili (B站) | ✅ API | ✅ via skill |
| X / Twitter | ✅ Jina → Playwright | — |
| WeChat (微信公众号) | ✅ Jina → Playwright | — |
| Xiaohongshu (小红书) | ✅ Jina → Playwright* | — |
| Telegram | ✅ Telethon | — |
| RSS | ✅ feedparser | — |
| 小宇宙 (Xiaoyuzhou) | — | ✅ via skill |
| Apple Podcasts | — | ✅ via skill |
| Any web page | ✅ Jina fallback | — |

> \*XHS requires a one-time login: `x-reader login xhs`
>
> YouTube Whisper transcription requires `GROQ_API_KEY` — get a free key from [Groq](https://console.groq.com/keys)

## Install

```bash
# 从本仓库安装
pip install git+https://github.com/deku0818/x-reader.git

# 带 Telegram 支持
pip install "x-reader[telegram] @ git+https://github.com/deku0818/x-reader.git"

# 带浏览器回退（Playwright）
pip install "x-reader[browser] @ git+https://github.com/deku0818/x-reader.git"
playwright install chromium

# 全部依赖
pip install "x-reader[all] @ git+https://github.com/deku0818/x-reader.git"
playwright install chromium
```

本地开发：
```bash
git clone https://github.com/deku0818/x-reader.git
cd x-reader
pip install -e ".[all]"
playwright install chromium
```

### 可选依赖（视频/音频）

```bash
# macOS
brew install yt-dlp ffmpeg

# Linux
pip install yt-dlp
apt install ffmpeg
```

## Configuration

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `TG_API_ID` | Telegram only | From https://my.telegram.org |
| `TG_API_HASH` | Telegram only | From https://my.telegram.org |
| `GROQ_API_KEY` | Whisper only | From https://console.groq.com/keys (free) |
| `INBOX_FILE` | No | Path to inbox JSON (default: `./unified_inbox.json`) |
| `OUTPUT_DIR` | No | Directory for Markdown output (default: disabled) |

## Architecture

```
x_reader/
├── cli.py             # CLI entry point (including `x-reader mcp`)
├── reader.py          # URL dispatcher (UniversalReader)
├── schema.py          # Unified data model
├── mcp_server.py      # MCP server (FastMCP)
├── login.py           # Browser login manager
├── fetchers/
│   ├── jina.py        # Jina Reader (universal fallback)
│   ├── browser.py     # Playwright headless
│   ├── bilibili.py    # Bilibili API
│   ├── youtube.py     # yt-dlp subtitle extraction
│   ├── rss.py         # feedparser
│   ├── telegram.py    # Telethon
│   ├── twitter.py     # Jina-based
│   ├── wechat.py      # Jina → Playwright fallback
│   └── xhs.py         # Jina → Playwright + session fallback
└── utils/
    └── storage.py     # JSON + Markdown dual output
```

## License

MIT — see [LICENSE](LICENSE)

---

> 🔗 **源项目: [runesleo/x-reader](https://github.com/runesleo/x-reader)** | Author: [@runes_leo](https://x.com/runes_leo)
