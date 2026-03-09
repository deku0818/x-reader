# 小宇宙（Xiaoyuzhou）

## 音频下载

小宇宙是 Next.js 单页应用，初始 HTML 的 `__NEXT_DATA__` 中包含音频 CDN 直链：

```bash
AUDIO_URL=$(curl -sL \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "播客链接" \
  | grep -oE 'https://media\.xyzcdn\.net/[^"]+\.(m4a|mp3)' \
  | head -1)

echo "音频链接: $AUDIO_URL"
curl -L -o /tmp/media_audio.mp3 "$AUDIO_URL"
```

→ 返回主流程第 2 步（检查大小并分段）

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `AUDIO_URL` 为空 | 页面结构变更或反爬 | 使用无头浏览器渲染页面后提取音频链接 |
| 下载的文件为 0 字节 | CDN 链接过期 | 重新提取链接后立即下载 |
