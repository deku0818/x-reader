# B站（Bilibili）

## 字幕提取

先尝试通过 yt-dlp 提取字幕：

```bash
yt-dlp --skip-download --write-auto-sub --sub-lang "zh-Hans,zh" -o "/tmp/media_sub" "URL"
ls /tmp/media_sub*.vtt 2>/dev/null
```

- **有字幕** → 读取 VTT 内容，返回主流程第 4 步
- **无字幕** → 继续下方音频下载

## 音频下载（API 方式）

yt-dlp 访问 B站即使带 cookies 也会返回 412，改用 B站 API：

```bash
# 1. 从 URL 中提取 BV 号
BV="BV1xxxxx"

# 2. 获取视频信息（标题、时长、CID）
curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BV" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.bilibili.com/" \
  | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(f\"标题: {d['title']}\n时长: {d['duration']}秒\nCID: {d['cid']}\")"

# 3. 获取音频流链接
CID=<上一步获取的 CID>
AUDIO_URL=$(curl -s "https://api.bilibili.com/x/player/playurl?bvid=$BV&cid=$CID&fnval=16&qn=64" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.bilibili.com/" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['dash']['audio'][0]['baseUrl'])")

# 4. 下载音频（必须带 Referer，否则 403）
curl -L -o /tmp/media_audio.m4s \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.bilibili.com/" "$AUDIO_URL"

# 5. 转换为 mp3
ffmpeg -y -i /tmp/media_audio.m4s -acodec libmp3lame -q:a 5 /tmp/media_audio.mp3
```

→ 返回主流程第 2 步（检查大小并分段）

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| yt-dlp 返回 412 | B站反爬 | 使用上方 API 方式 |
| curl 下载 403 | 缺少 Referer 头 | 确保 `-H "Referer: https://www.bilibili.com/"` |
| API 返回空数据 | BV 号提取错误 | 检查 URL 格式，确认 BV 号正确 |