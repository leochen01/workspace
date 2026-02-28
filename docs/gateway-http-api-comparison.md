# OpenClaw Gateway HTTP API 对比

本文档对比 OpenClaw Gateway 提供的两个 OpenAI 兼容 HTTP 端点：`/v1/chat/completions` 和 `/v1/responses`，以及工具调用端点 `/tools/invoke`。

## 基础信息

| 端点 | 用途 | 认证 |
|------|------|------|
| `/v1/chat/completions` | Chat 对话 | Bearer Token |
| `/v1/responses` | Responses API | Bearer Token |
| `/tools/invoke` | 直接调用工具 | Bearer Token |

## 认证

所有端点使用相同的认证方式：

```bash
# Token
Authorization: Bearer YOUR_TOKEN

# 通用 Headers
x-openclaw-agent-id: main        # 指定 agent (默认 main)
x-openclaw-session-key: xxx      # 指定会话 key
```

---

## /v1/chat/completions

OpenAI 兼容的 Chat Completions 端点。

### 基本调用

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openclaw",
    "messages": [{"role":"user","content":"你好"}],
    "stream": false
  }'
```

### 请求字段

- `model`: 模型名称，使用 `openclaw` 路由到默认 agent
- `messages`: 消息数组 `[{role: "user"|"assistant", content: "..."}]`
- `stream`: 是否流式输出 (SSE)

### 响应格式

```json
{
  "id": "chatcmpl_xxx",
  "object": "chat.completion",
  "model": "openclaw",
  "choices": [{
    "message": {"role": "assistant", "content": "回复内容"},
    "finish_reason": "stop"
  }],
  "usage": {"total_tokens": 100}
}
```

### 图片输入

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openclaw",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "描述图片"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
      ]
    }]
  }'
```

---

## /v1/responses

OpenAI Responses API（新版）。

### 基本调用

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/v1/responses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openclaw",
    "input": "你好"
  }'
```

### 请求字段

- `model`: 模型名称
- `input`: 支持字符串或消息数组
- `stream`: 是否流式输出

### 响应格式

```json
{
  "id": "resp_xxx",
  "object": "response",
  "status": "completed",
  "model": "openclaw",
  "output": [{
    "type": "message",
    "content": [{"type": "output_text", "text": "回复内容"}]
  }],
  "usage": {"total_tokens": 100}
}
```

### 流式输出

```bash
curl -N --noproxy '*' http://127.0.0.1:18789/v1/responses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openclaw",
    "input": "hi",
    "stream": true
  }'
```

输出格式 (SSE)：
```
event: response.created
data: {...}
event: response.output_text.delta
data: {"type":"response.output_text.delta","delta":"Hello"}
event: response.completed
data: {...}
data: [DONE]
```

---

## /tools/invoke

直接调用 OpenClaw 工具的端点，无需经过 agent 对话。

### 基本调用

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "tool_name",
    "args": {}
  }'
```

### 请求字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tool` | string | ✅ | 工具名称 |
| `action` | string | ❌ | 工具动作（如 `json`） |
| `args` | object | ❌ | 工具参数 |
| `sessionKey` | string | ❌ | 目标会话 key |

### 响应格式

成功 (200)：
```json
{
  "ok": true,
  "result": {
    "content": [{"type": "text", "text": "..."}],
    "details": {...}
  }
}
```

失败 (400/404/500)：
```json
{
  "ok": false,
  "error": {
    "type": "invalid_request_error",
    "message": "错误信息"
  }
}
```

### 常用工具示例

#### 1. 获取会话列表

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "sessions_list",
    "args": {}
  }'
```

#### 2. 获取当前会话状态

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "session_status"
  }'
```

响应：
```json
{
  "ok": true,
  "result": {
    "content": [{"type": "text", "text": "🦞 OpenClaw 2026.2.26\n🕒 Time: Saturday, February 28th, 2026 — 10:56 AM\n🧠 Model: minimax-cn/MiniMax-M2.5\n🧮 Tokens: 504k in / 4.7k out\n📚 Context: 61k/200k (30%)"}]
  }
}
```

#### 3. 搜索记忆

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "memory_search",
    "args": {"query": "模型配置"}
  }'
```

#### 4. 获取节点列表

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "nodes",
    "action": "status"
  }'
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 工具不存在或未授权 |
| 405 | 方法不允许 |
| 429 | 请求过于频繁 |
| 500 | 服务端错误 |

### 安全限制

默认禁止通过 HTTP 调用以下工具：
- `sessions_spawn`
- `sessions_send`
- `gateway`
- `whatsapp_login`

可通过配置 `gateway.tools` 自定义允许/禁止列表。

---

## 功能对比表

| 功能 | /v1/chat/completions | /v1/responses | /tools/invoke |
|------|---------------------|----------------|---------------|
| 文本对话 | ✅ | ✅ | ❌ |
| 流式输出 | ✅ | ✅ | ❌ |
| 图片输入 | ✅ | ❌ | ❌ |
| 文件输入 | ❌ | ❌ | ❌ |
| 工具调用 | ❌ | ❌ | ✅ |
| 直接执行 | ❌ | ❌ | ✅ |

## 使用建议

| 场景 | 推荐端点 |
|------|----------|
| 简单对话 | `/v1/responses` |
| 图片识别 | `/v1/chat/completions` |
| 流式前端展示 | `/v1/responses` |
| 直接调用工具 | `/tools/invoke` |
| 兼容 OpenAI 代码 | `/v1/chat/completions` |

## 本地配置

```bash
# Gateway 地址
GATEWAY_URL=http://127.0.0.1:18789
# Token
GATEWAY_TOKEN=95c84b0ab1cb8722d30c6748846833d96979fbf2619d6389
```

注意：如果本地有代理，需要加 `--noproxy '*'` 绕过代理。
