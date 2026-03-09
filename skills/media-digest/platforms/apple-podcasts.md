# Apple Podcasts

## 音频下载

通过 yt-dlp 直接下载：

```bash
yt-dlp -f "ba[ext=m4a]/ba/b" --extract-audio --audio-format mp3 --audio-quality 5 \
  -o "/tmp/media_audio.%(ext)s" "APPLE_PODCAST_链接"
```

→ 返回主流程第 2 步（检查大小并分段）

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| yt-dlp 无法解析链接 | URL 格式不正确 | 确认链接格式为 `podcasts.apple.com/...` |
| 下载失败 | 地区限制 | 尝试使用代理 |
