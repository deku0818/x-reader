# 通用视频（YouTube、X/Twitter 等）

## 字幕提取（优先）

```bash
# YouTube：优先英文，回退中文
yt-dlp --skip-download --write-auto-sub --sub-lang "en,zh-Hans" -o "/tmp/media_sub" "URL"

ls /tmp/media_sub*.vtt 2>/dev/null
```

- **有字幕** → 读取 VTT 内容，返回主流程第 4 步
- **无字幕** → 继续下方音频下载

## 音频下载

```bash
# --cookies-from-browser chrome 可绕过 YouTube 机器人检测
yt-dlp --cookies-from-browser chrome -f "ba[ext=m4a]/ba/b" \
  --extract-audio --audio-format mp3 --audio-quality 5 \
  -o "/tmp/media_audio.%(ext)s" "URL"
```

→ 返回主流程第 2 步（检查大小并分段）

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| YouTube 提示 "Sign in to confirm" | 机器人检测 | 添加 `--cookies-from-browser chrome` |
| X/Twitter 无字幕 | 平台不提供字幕 | 正常现象，走 Whisper 转录 |
| 下载速度极慢 | 地区或网络限制 | 尝试使用代理 |