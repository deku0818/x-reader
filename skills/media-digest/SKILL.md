---
name: media-digest
description: >
  自动提取视频和播客的转录文本并生成结构化摘要。
  支持 YouTube、Bilibili（B站）、X/Twitter、小宇宙、Apple Podcasts 以及直链媒体文件
  （mp3/mp4/m3u8/m4a/webm）。当用户发送以上任意平台的媒体链接，或要求总结/转录某个视频或播客时触发此技能。
  当用户粘贴包含 youtube.com、youtu.be、bilibili.com、b23.tv、x.com、twitter.com、
  xiaoyuzhoufm.com、podcasts.apple.com 的链接，或直接音视频文件链接时也应触发。
  即使是随意的请求如"这个视频讲了什么？"附带链接，也应触发此技能。
---

# 媒体摘要

发送视频或播客链接 → 获取完整转录文本 + 结构化摘要。

## 前置条件

- `yt-dlp`：视频下载与字幕提取
- `ffmpeg`：音频转换与分段
- `curl`：小宇宙和 B站 API 的 HTTP 请求
- `GROQ_API_KEY` 环境变量：Whisper 转录所需，如果没有应该提醒用户获取再继续之后的行动（免费获取：https://console.groq.com/keys）

开始前检查：
```bash
command -v yt-dlp && command -v ffmpeg && command -v curl && echo "OK" || echo "缺少依赖"
[ -n "$GROQ_API_KEY" ] && echo "API 密钥已设置" || echo "⚠️ GROQ_API_KEY 未设置"
```

如果 `GROQ_API_KEY` 缺失且无可用字幕，告知用户并提供注册链接。

---

## 第 0 步：清理临时文件

每次任务开始前先清理上次可能残留的文件，避免使用到缓存数据：

```bash
rm -f /tmp/media_sub*.vtt /tmp/media_audio.* /tmp/media_segment_*.mp3 /tmp/media_transcript*.json 2>/dev/null
```

---

## 第 1 步：识别平台并路由

根据 URL 识别平台，然后**只读取对应的平台文档**获取下载方法：

| URL 模式 | 平台 | 读取 |
|----------|------|------|
| `bilibili.com`、`b23.tv` | B站 | → `platforms/bilibili.md` |
| `xiaoyuzhoufm.com/episode/` | 小宇宙 | → `platforms/xiaoyuzhou.md` |
| `podcasts.apple.com` | Apple Podcasts | → `platforms/apple-podcasts.md` |
| `.mp3`、`.m4a` 直链 | 直链音频 | → `curl -L -o /tmp/media_audio.mp3 "URL"`，跳到第 3 步 |
| 其他（YouTube、X 等） | 通用视频 | → `platforms/generic.md` |

完成平台文档中的操作后，音频文件应已保存为 `/tmp/media_audio.mp3`（或有字幕时已获取 VTT）。

- **已获取字幕** → 跳到第 4 步
- **已下载音频** → 继续第 2 步

---

## 第 2 步：检查大小并分段

```bash
FILE_SIZE=$(stat -c%s /tmp/media_audio.* 2>/dev/null || stat -f%z /tmp/media_audio.* 2>/dev/null)
echo "文件大小: $FILE_SIZE 字节"
```

- **≤ 25MB（25000000）** → 直接进入第 3 步
- **> 25MB** → 先分段，再对每段执行第 3 步

### 大音频分段

```bash
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/media_audio.* | head -1)
SEGMENT_SEC=600
SEGMENTS=$(python3 -c "import math; print(math.ceil(float('$DURATION')/$SEGMENT_SEC))")

for i in $(seq 0 $((SEGMENTS-1))); do
  START=$((i * SEGMENT_SEC))
  ffmpeg -y -i /tmp/media_audio.* -ss $START -t $SEGMENT_SEC \
    -acodec libmp3lame -q:a 5 "/tmp/media_segment_${i}.mp3" 2>/dev/null
done
```

**依次**转录每个分段——并行请求会触发 Groq 524 超时。每段之间间隔 5–8 秒，按顺序拼接结果。

---

## 第 3 步：Whisper 转录

### 单个文件

```bash
curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@音频文件路径" \
  -F "model=whisper-large-v3-turbo" \
  -F "response_format=verbose_json" \
  -F "language=zh" \
  > /tmp/media_transcript.json

python3 -c "import json; print(json.load(open('/tmp/media_transcript.json'))['text'])"
```

### 多个分段

```bash
FULL_TEXT=""
for seg in /tmp/media_segment_*.mp3; do
  RESULT=$(curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
    -H "Authorization: Bearer $GROQ_API_KEY" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$seg" \
    -F "model=whisper-large-v3-turbo" \
    -F "response_format=verbose_json" \
    -F "language=zh")
  SEGMENT_TEXT=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['text'])")
  FULL_TEXT="$FULL_TEXT $SEGMENT_TEXT"
  sleep 6
done
```

### 模型与语言选项

| 模型 | 速度 | 适用场景 |
|------|------|---------|
| `whisper-large-v3-turbo` | 10 倍实时 | 默认选择 |
| `whisper-large-v3` | 5 倍实时 | 嘈杂音频或专业内容 |

语言参数：中文用 `zh`，英文用 `en`，省略则自动检测。

### Groq 限制

- 每次请求最大 25MB
- 免费额度：每小时 7200 秒音频（滚动窗口）
- 支持格式：mp3、mp4、mpeg、mpga、m4a、wav、webm

---

## 第 4 步：结构化摘要

### 短内容（≤ 20 分钟）

```
## 📺 视频摘要

**标题**：[标题]  |  **时长**：[x 分钟]  |  **语言**：[语言]

### 概述
[1–2 句话]

### 要点
1. ...

### 精彩引用
> "..." — [时间戳]

### 行动项
- [如适用]
```

### 长内容（> 20 分钟）

```
## 🎙️ 播客摘要

**节目**：[名称]  |  **单集**：[标题]  |  **时长**：[x 分钟]  |  **嘉宾**：[如有]

### 概述
[2–3 句话：谁讨论了什么，核心结论]

### 分章摘要
#### 1. [话题]（~xx:xx–xx:xx）
[2–3 句话]

### 要点
1. ...

### 精彩引用
> "..."

### 行动项
- [如适用]
```

---

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| 无字幕 + 未设置 `GROQ_API_KEY` | 提示用户设置 API 密钥 |
| 音频 > 25MB | ffmpeg 分段（每段 10 分钟），依次转录 |
| 播客超过 2 小时 | 提醒用户时长较长，确认后再继续 |
| Groq 524 超时 | 不要并行；依次转录 + 每段间隔 5–8 秒 |
| Groq 429 限流 | 等待 `retry-after` 头指定的时间后重试 |
| Spotify 链接 | 不支持（DRM 保护），告知用户 |
| 网络超时 | 重试一次 |
| 平台特定错误 | 参见对应平台文档中的说明 |