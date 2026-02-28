# OpenClaw 工具详细使用手册

本文档详细介绍 OpenClaw Gateway 所有可用工具的调用方法。

## 目录

1. [工具调用基础](#工具调用基础)
2. [会话管理工具](#会话管理工具)
3. [记忆工具](#记忆工具)
4. [网页工具](#网页工具)
5. [节点工具](#节点工具)
6. [浏览器工具](#浏览器工具)
7. [Canvas 工具](#canvas-工具)
8. [消息工具](#消息工具)
9. [文件操作工具](#文件操作工具)
10. [命令执行工具](#命令执行工具)
11. [定时任务工具](#定时任务工具)
12. [图片工具](#图片工具)
13. [Gateway 工具](#gateway-工具)

---

## 工具调用基础

### 通过 HTTP API 调用

所有工具通过 `/tools/invoke` 端点调用：

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "tool_name",
    "action": "action_name",
    "args": {}
  }'
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tool` | string | ✅ | 工具名称 |
| `action` | string | ❌ | 工具动作 |
| `args` | object | ❌ | 工具参数 |
| `sessionKey` | string | ❌ | 目标会话 |

### 通用 Headers

```bash
Authorization: Bearer YOUR_TOKEN
x-openclaw-agent-id: main
x-openclaw-session-key: session-key
```

---

## 会话管理工具

### session_status

获取当前会话状态。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tool": "session_status"}'
```

**响应示例：**
```json
{
  "ok": true,
  "result": {
    "content": [{
      "type": "text",
      "text": "🦞 OpenClaw 2026.2.26\n🕒 Time: Saturday, February 28th, 2026 — 10:56 AM\n🧠 Model: minimax-cn/MiniMax-M2.5\n🧮 Tokens: 504k in / 4.7k out\n📚 Context: 61k/200k (30%)"
    }]
  }
}
```

### sessions_list

列出所有会话。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "sessions_list",
    "args": {}
  }'
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `activeMinutes` | number | 仅显示最近活跃的会话（分钟） |
| `kinds` | string[] | 按类型过滤 |
| `limit` | number | 返回数量限制 |
| `messageLimit` | number | 每个会话包含的消息数 |

### sessions_history

获取会话历史。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "sessions_history",
    "args": {
      "sessionKey": "agent:main:main",
      "limit": 10
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sessionKey` | string | ✅ | 会话 key |
| `includeTools` | boolean | ❌ | 是否包含工具调用 |
| `limit` | number | ❌ | 返回消息数 |

---

## 记忆工具

### memory_search

搜索记忆。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "memory_search",
    "args": {"query": "模型配置"}
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 搜索关键词 |
| `maxResults` | number | ❌ | 最大结果数 |
| `minScore` | number | ❌ | 最低匹配分数 |

### memory_get

获取单条记忆。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "memory_get",
    "args": {
      "path": "MEMORY.md",
      "from": 1,
      "lines": 50
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 文件路径 |
| `from` | number | ❌ | 起始行 |
| `lines` | number | ❌ | 行数 |

---

## 网页工具

### web_search

网页搜索。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "web_search",
    "args": {
      "query": "OpenClaw Gateway 文档",
      "count": 5
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 搜索关键词 |
| `count` | number | ❌ | 结果数量 (1-10) |
| `freshness` | string | ❌ | 时间范围 (pd/pw/pm/py) |
| `country` | string | ❌ | 国家代码 |
| `searchLang` | string | ❌ | 搜索语言 |

### web_fetch

抓取网页内容。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "web_fetch",
    "args": {
      "url": "https://docs.openclaw.ai",
      "maxChars": 10000
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | 目标 URL |
| `extractMode` | string | ❌ | 提取模式 (markdown/text) |
| `maxChars` | number | ❌ | 最大字符数 |

---

## 节点工具

### nodes

管理配对的节点。

```bash
# 查看节点状态
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "nodes",
    "action": "status"
  }'

# 查看节点描述
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "nodes",
    "action": "describe",
    "args": {"node": "node-name"}
  }'

# 截屏
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "nodes",
    "action": "camera_snap",
    "args": {"facing": "back"}
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `status` | 查看所有节点状态 |
| `describe` | 查看节点详情 |
| `pending` | 查看待配对请求 |
| `approve` | 批准配对 |
| `reject` | 拒绝配对 |
| `notify` | 发送系统通知 |
| `run` | 在节点上运行命令 |
| `camera_list` | 列出相机 |
| `camera_snap` | 拍照 |
| `camera_clip` | 录视频 |
| `screen_record` | 屏幕录制 |
| `location_get` | 获取位置 |
| `notifications_list` | 列出通知 |

---

## 浏览器工具

### browser

控制 OpenClaw 管理的浏览器。

```bash
# 查看浏览器状态
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "status"
  }'

# 打开网页
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "open",
    "args": {"targetUrl": "https://example.com"}
  }'

# 截屏
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "screenshot"
  }'

# 获取页面快照
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "snapshot"
  }'

# 点击元素
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "act",
    "args": {
      "request": {
        "kind": "click",
        "ref": "e12"
      }
    }
  }'

# 输入文本
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "act",
    "args": {
      "request": {
        "kind": "type",
        "ref": "e12",
        "text": "Hello World"
      }
    }
  }'

# 导航
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "browser",
    "action": "navigate",
    "args": {"targetUrl": "https://example.com"}
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `status` | 浏览器状态 |
| `start` | 启动浏览器 |
| `stop` | 停止浏览器 |
| `tabs` | 列出标签页 |
| `open` | 打开 URL |
| `focus` | 聚焦标签页 |
| `close` | 关闭标签页 |
| `snapshot` | 获取页面快照 |
| `screenshot` | 截屏 |
| `act` | 执行操作 (click/type/press/hover/drag/select/fill/resize/wait/evaluate) |
| `navigate` | 导航到 URL |
| `console` | 获取控制台日志 |
| `pdf` | 导出 PDF |
| `upload` | 上传文件 |
| `dialog` | 处理对话框 |
| `profiles` | 管理浏览器配置 |

---

## Canvas 工具

### canvas

控制节点 Canvas。

```bash
# 获取 Canvas 快照
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "canvas",
    "action": "snapshot"
  }'

# 推送内容到 Canvas
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "canvas",
    "action": "a2ui_push",
    "args": {
      "javaScript": "document.body.innerHTML = '<h1>Hello</h1>'"
    }
  }'

# 执行 JavaScript
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "canvas",
    "action": "eval",
    "args": {
      "javaScript": "return document.title"
    }
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `present` | 展示内容 |
| `hide` | 隐藏内容 |
| `navigate` | 导航 |
| `eval` | 执行 JavaScript |
| `snapshot` | 获取快照 |
| `a2ui_push` | 推送 A2UI |
| `a2ui_reset` | 重置 A2UI |

---

## 消息工具

### message

发送消息到各种渠道。

```bash
# 发送文本消息
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "message",
    "action": "send",
    "args": {
      "channel": "telegram",
      "target": "user-id",
      "message": "Hello"
    }
  }'

# 发送图片
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "message",
    "action": "send",
    "args": {
      "channel": "telegram",
      "target": "user-id",
      "message": "图片",
      "media": "https://example.com/image.jpg"
    }
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `send` | 发送消息 |
| `poll` | 投票 |
| `react` | 反应 |
| `reactions` | 批量反应 |
| `read` | 已读 |
| `edit` | 编辑 |
| `delete` | 删除 |
| `pin` | 置顶 |
| `unpin` | 取消置顶 |
| `thread-create` | 创建话题 |
| `thread-list` | 列出话题 |
| `thread-reply` | 回复话题 |
| `search` | 搜索 |

**支持渠道：**

- `discord`
- `telegram`
- `slack`
- `whatsapp`
- `signal`
- `imessage`
- `googlechat`
- `msteams`

---

## 文件操作工具

### read

读取文件。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "read",
    "args": {
      "file_path": "~/.openclaw/openclaw.json"
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_path` | string | ✅ | 文件路径 |
| `limit` | number | ❌ | 最大行数 |
| `offset` | number | ❌ | 起始行号 |

### write

写入文件。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "write",
    "args": {
      "path": "~/test.txt",
      "content": "Hello World"
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 文件路径 |
| `content` | string | ✅ | 文件内容 |

### edit

编辑文件。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "edit",
    "args": {
      "path": "~/test.txt",
      "old_string": "Hello",
      "new_string": "Hi"
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 文件路径 |
| `old_string` | string | ✅ | 要替换的文本 |
| `new_string` | string | ✅ | 替换后的文本 |

---

## 命令执行工具

### exec

执行 shell 命令。

**注意：** 出于安全考虑，此工具默认不能通过 HTTP 调用。

```bash
# 通过 agent 对话调用
curl -sS --noproxy '*' http://127.0.0.1:18789/v1/chat/completions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openclaw",
    "messages": [{"role":"user","content":"执行 ls -la"}]
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 要执行的命令 |
| `timeout` | number | ❌ | 超时秒数 |
| `background` | boolean | ❌ | 后台执行 |
| `yieldMs` | number | ❌ | 自动后台超时 |
| `elevated` | boolean | ❌ | 提升权限 |
| `host` | string | ❌ | 执行主机 (sandbox/gateway/node) |
| `security` | string | ❌ | 安全模式 |
| `pty` | boolean | ❌ | 启用 TTY |

### process

管理后台进程。

**注意：** 出于安全考虑，此工具默认不能通过 HTTP 调用。

```bash
# 列出后台进程
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "process",
    "action": "list"
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `list` | 列出后台进程 |
| `poll` | 获取进程输出 |
| `log` | 获取日志 |
| `write` | 输入内容 |
| `kill` | 终止进程 |
| `clear` | 清除输出 |
| `remove` | 移除进程 |

---

## 定时任务工具

### cron

管理定时任务。

```bash
# 列出定时任务
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "cron",
    "action": "list"
  }'

# 添加定时任务
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "cron",
    "action": "add",
    "args": {
      "job": {
        "id": "my-task",
        "schedule": "*/5 * * * *",
        "command": "echo hello"
      }
    }
  }'

# 手动运行任务
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "cron",
    "action": "run",
    "args": {"jobId": "my-task"}
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `status` | 状态 |
| `list` | 列出任务 |
| `add` | 添加任务 |
| `update` | 更新任务 |
| `remove` | 删除任务 |
| `run` | 手动运行 |
| `runs` | 运行历史 |
| `wake` | 唤醒 |

---

## 图片工具

### image

分析图片。

```bash
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "image",
    "args": {
      "image": "https://example.com/image.jpg",
      "prompt": "描述这张图片"
    }
  }'
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `image` | string | ✅ | 图片路径或 URL |
| `prompt` | string | ❌ | 提示词 |
| `model` | string | ❌ | 指定模型 |
| `maxBytesMb` | number | ❌ | 最大文件大小 |

---

## Gateway 工具

### gateway

管理 Gateway。

**注意：** 出于安全考虑，此工具默认不能通过 HTTP 调用。

```bash
# 重启 Gateway
curl -sS --noproxy '*' http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "gateway",
    "action": "restart"
  }'
```

**动作 (action)：**

| 动作 | 说明 |
|------|------|
| `restart` | 重启 |
| `stop` | 停止 |
| `start` | 启动 |
| `status` | 状态 |

---

## 工具组 (Tool Groups)

工具可以通过组名批量管理：

| 组名 | 包含工具 |
|------|----------|
| `group:runtime` | `exec`, `bash`, `process` |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `cron`, `gateway` |
| `group:messaging` | `message` |
| `group:nodes` | `nodes` |

---

## HTTP 调用限制

出于安全考虑，以下工具默认禁止通过 HTTP `/tools/invoke` 调用：

- `sessions_spawn`
- `sessions_send`
- `gateway`
- `whatsapp_login`
- `exec` (默认)
- `process` (默认)

如需启用，可通过配置 `gateway.tools.allow` 自定义。

---

## 错误响应

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 工具不存在或未授权 |
| 405 | 方法不允许 |
| 429 | 请求过于频繁 |
| 500 | 服务端错误 |

**错误响应格式：**
```json
{
  "ok": false,
  "error": {
    "type": "invalid_request_error",
    "message": "错误信息"
  }
}
```
