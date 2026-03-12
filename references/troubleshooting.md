# 故障排除

## "GEMINI_API_KEY not set"

未设置 AI API Key。提供至少一个：

- `GEMINI_API_KEY`: 在 https://aistudio.google.com/apikey 免费获取
- `OPENAI_API_KEY`: OpenAI 或兼容接口

## "Gemini 配额超限或请求失败"

脚本自动降级到 OpenAI 兼容接口。确保已设置 `OPENAI_API_KEY`，可选设置 `OPENAI_API_BASE` 指定兼容接口地址。

## "Failed to fetch N feeds"

部分 RSS 源可能暂时不可用。脚本会跳过失败源继续处理，不影响最终结果（只要有足够的源成功返回）。

## "No articles found in time range"

指定时间范围内无文章。扩大 `--hours` 参数：

- `--hours 48` → `--hours 72` 或 `--hours 168`（一周）

## 网络问题

- 确认可访问 RSS 源域名（部分源可能需要代理）
- 确认可访问 AI API（Gemini: `generativelanguage.googleapis.com`，OpenAI: `api.openai.com`）
- 脚本超时设置为 15 秒/源，网络较慢时可能产生较多失败

## 输出为空或摘要缺失

- AI API 返回空响应时，脚本会使用默认值填充（标题不翻译、无摘要）
- 检查 stderr 输出中的具体错误信息
- Gemini 免费配额有请求频率限制，文章数量较多时可能触发
