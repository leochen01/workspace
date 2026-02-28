# OpenClaw 与大模型交互流程详解

本文档详细分析 OpenClaw 与后端大语言模型（LLM）的交互流程，详解如何管理 SOUL、TOOLS、USER、IDENTITY、AGENTS 等配置文件。

## 交互流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenClaw Agent Runtime                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │  Workspace   │    │  System      │    │   Session    │    │
│  │  Files       │    │  Prompt      │    │   History    │    │
│  │              │    │  Builder     │    │              │    │
│  │ - SOUL.md   │───▶│              │───▶│              │    │
│  │ - TOOLS.md  │    │ - Tooling    │    │ - Messages   │    │
│  │ - USER.md   │    │ - Skills     │    │ - Tool Calls │    │
│  │ - IDENTITY  │    │ - Safety     │    │ - Results    │    │
│  │ - AGENTS.md │    │ - Runtime    │    │              │    │
│  │ - HEARTBEAT │    │ - Time       │    │              │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│         │                   │                   │             │
│         └───────────────────┼───────────────────┘             │
│                             ▼                                   │
│                   ┌─────────────────┐                          │
│                   │   Context       │                          │
│                   │   (Full Prompt) │                          │
│                   └────────┬────────┘                          │
│                            ▼                                    │
│                   ┌─────────────────┐                          │
│                   │   LLM Provider  │                          │
│                   │   (API Call)    │                          │
│                   └────────┬────────┘                          │
│                            ▼                                    │
│                   ┌─────────────────┐                          │
│                   │   Response      │                          │
│                   │   + Tool Calls  │                          │
│                   └─────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Workspace 文件注入机制

### 注入的文件列表

每次对话开始时，OpenClaw 会自动将以下文件内容注入到模型上下文（称为 "Project Context"）：

| 文件 | 说明 | 用途 |
|------|------|------|
| `SOUL.md` | Agent 人格/边界 | 定义 Agent 的性格、行为准则 |
| `TOOLS.md` | 工具使用笔记 | 用户维护的工具使用规范 |
| `USER.md` | 用户信息 | 用户是谁、如何称呼 |
| `IDENTITY.md` | Agent 身份 | 名称、头像、风格 |
| `AGENTS.md` | 操作说明 | Agent 的"记忆"和指令 |
| `HEARTBEAT.md` | 定时任务 | 心跳任务清单 |
| `BOOTSTRAP.md` | 首次运行引导 | 首次运行时的一次性脚本 |
| `MEMORY.md` | 长期记忆 | 精选要点（手动管理） |

### 注入规则

```python
# 伪代码：注入逻辑
if session.is_new:
    inject_workspace_files()  # 首次对话注入所有 bootstrap 文件

# 文件大小限制
bootstrapMaxChars = 20000      # 单个文件最大字符数
bootstrapTotalMaxChars = 150000 # 所有文件总最大字符数
```

### Sub-agent 特殊处理

子代理会话只注入部分文件：
- ✅ `AGENTS.md`
- ✅ `TOOLS.md`
- ❌ `SOUL.md` (不注入)
- ❌ `USER.md` (不注入)

---

## 2. System Prompt 构建流程

### Prompt 组成结构

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM PROMPT                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Tooling                                                 │
│     - 当前可用工具列表 + 简短描述                            │
│                                                              │
│  2. Safety                                                  │
│     - 安全护栏提示（不绕过监督等）                           │
│                                                              │
│  3. Skills (可选)                                           │
│     - 可用技能列表                                           │
│     - 告诉模型如何按需加载技能                               │
│                                                              │
│  4. OpenClaw Self-Update                                    │
│     - 如何运行 config.apply 和 update.run                   │
│                                                              │
│  5. Workspace                                               │
│     - 工作目录路径                                           │
│                                                              │
│  6. Documentation                                           │
│     - 本地文档路径                                           │
│                                                              │
│  7. Project Context (Workspace Files)                        │
│     ┌─────────────────────────────────────────────────┐     │
│     │ # AGENTS.md 内容                                │     │
│     │ # SOUL.md 内容                                  │     │
│     │ # TOOLS.md 内容                                 │     │
│     │ # IDENTITY.md 内容                              │     │
│     │ # USER.md 内容                                  │     │
│     │ # HEARTBEAT.md 内容                             │     │
│     └─────────────────────────────────────────────────┘     │
│                                                              │
│  8. Sandbox (可选)                                          │
│     - 沙箱模式说明                                           │
│                                                              │
│  9. Current Date & Time                                     │
│     - 当前时间 + 时区                                         │
│                                                              │
│  10. Runtime                                                │
│      - 主机、OS、节点、模型、思考模式                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Prompt Mode

| Mode | 说明 | 注入内容 |
|------|------|----------|
| `full` | 默认完整模式 | 所有章节 |
| `minimal` | 子代理模式 | Tooling, Safety, Workspace, Runtime |
| `none` | 极简模式 | 仅基础身份行 |

---

## 3. 各配置文件详解

### SOUL.md - Agent 人格

```markdown
# SOUL.md - 我是谁

## 核心原则
- **真帮忙，不客气话** — 直接做，少说"好问题"
- **可以有观点** — 可以不同意、喜欢/不喜欢
- **先自己试试** — 查文件、搜资料，再问
- **获取信任靠能力** — 外部操作谨慎，内部操作大胆

## 边界
- 私事保密
- 不确定时先问
- 不代用户发言

## 风格
有用就说话，无需则安静。不是搜索引擎，是助手。
```

**作用**：定义 Agent 的性格、价值观、行为边界

---

### TOOLS.md - 工具笔记

```markdown
# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here
- Camera names and locations
- SSH hosts and aliases
- 任何环境特定的内容
```

**作用**：用户维护的工具使用规范和本地配置说明

---

### USER.md - 用户信息

```markdown
# USER.md - About Your Human

- **Name:** 陈佳成
- **What to call them:** 
- **Pronouns:** 
- **Timezone:** Asia/Shanghai

## Context
用户是一个...
```

**作用**：记录用户信息，让 Agent 知道在和谁对话

---

### IDENTITY.md - Agent 身份

```markdown
# IDENTITY.md - Who Am I?

- **Name:** 小 Claw
- **Creature:** AI 助手
- **Vibe:** 友好、高效
- **Emoji:** 🦞
- **Avatar:** avatars/openclaw.png
```

**作用**：定义 Agent 的公开身份展示

---

### AGENTS.md - 操作指令

```markdown
# AGENTS.md - 工作区指南

## 每轮会话
1. 读 `SOUL.md` — 我是谁
2. 读 `USER.md` — 用户是谁
3. 读 `memory/YYYY-MM-DD.md` (今天+昨天)
4. 主会话时加读 `MEMORY.md`

## 记忆
- **每日笔记**: `memory/YYYY-MM-DD.md`
- **长期记忆**: `MEMORY.md`
```

**作用**：Agent 的"记忆"和操作指南，每轮自动读取

---

### HEARTBEAT.md - 定时任务

```markdown
# HEARTBEAT.md
# Keep this file empty to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.
```

**作用**：定义需要定期检查的任务

---

## 4. 运行时上下文（Context）

### Context 组成部分

```
Context = System Prompt + Conversation History + Tool Calls/Results
```

| 组成部分 | 说明 |
|----------|------|
| System Prompt | OpenClaw 构建的规则和工具说明 |
| Conversation History | 对话历史（消息 + 助手回复） |
| Tool Calls | 工具调用 + 返回结果 |
| Attachments | 图片/音频/文件 |

### 查看 Context 使用

```bash
# 快速查看上下文占用
/status

# 查看注入的文件列表
/context list

# 查看详细分析
/context detail
```

---

## 5. 与 LLM Provider 的交互

### API 请求结构

```json
{
  "model": "minimax-cn/MiniMax-M2.5",
  "messages": [
    {
      "role": "system",
      "content": "【完整的 System Prompt，包含所有注入的文件】"
    },
    {
      "role": "user", 
      "content": "用户消息..."
    },
    {
      "role": "assistant",
      "content": "之前的回复...",
      "tool_calls": [...]
    },
    {
      "role": "tool",
      "tool_call_id": "xxx",
      "content": "工具返回结果..."
    }
  ],
  "tools": [
    // 工具 Schema 定义
  ],
  "stream": false
}
```

### 响应处理流程

```
LLM Response
     │
     ▼
┌─────────────┐
│ 纯文本回复   │ ──▶ 直接返回给用户
└─────────────┘
     │
     ▼
┌─────────────┐
│ 包含 Tool   │ ──▶ 1. 提取工具调用
│   Calls?    │     2. 执行工具
└─────────────┘     3. 将结果作为 tool 消息
                      4. 再次调用 LLM
```

---

## 6. 配置管理命令

### 查看当前 Context

```bash
# 查看上下文占用
/status

# 列出注入的文件
/context list

# 详细分析
/context detail

# 查看 token 使用
/usage tokens
```

### 管理 Bootstrap 文件

```bash
# 重新初始化 workspace
openclaw setup

# 跳过 bootstrap（预配置的 workspace）
# 在配置中设置：
{
  "agent": {
    "skipBootstrap": true
  }
}
```

### 配置注入参数

```json
{
  "agents": {
    "defaults": {
      "bootstrapMaxChars": 20000,
      "bootstrapTotalMaxChars": 150000,
      "userTimezone": "Asia/Shanghai",
      "timeFormat": "auto"
    }
  }
}
```

---

## 7. 完整交互示例

### 首次对话流程

```
1. 用户发送: "你好"

2. OpenClaw 构建 System Prompt:
   - 加载工具列表
   - 加载技能列表
   - 注入 SOUL.md
   - 注入 TOOLS.md  
   - 注入 USER.md
   - 注入 IDENTITY.md
   - 注入 AGENTS.md
   - 注入 HEARTBEAT.md (如存在)

3. 发送请求到 LLM:
   messages = [
     {role: "system", content: "【完整 System Prompt】"},
     {role: "user", content: "你好"}
   ]

4. LLM 返回:
   {role: "assistant", content: "你好！我是..."}

5. 返回给用户
```

### 工具调用流程

```
1. 用户: "列出当前目录文件"

2. OpenClaw 构建 Context:
   - System Prompt
   - 历史消息

3. LLM 返回 Tool Call:
   {
     "tool_calls": [{
       "type": "function",
       "function": {
         "name": "exec",
         "arguments": {"command": "ls -la"}
       }
     }]
   }

4. OpenClaw 执行工具:
   exec(command="ls -la")
   返回: "total 100..."

5. 再次调用 LLM:
   messages = [
     ..., 
     {role: "assistant", tool_calls: [...]},
     {role: "tool", content: "total 100..."}
   ]

6. LLM 生成最终回复

7. 返回给用户
```

---

## 8. 文件优先级和覆盖

### 加载优先级

```
1. 内置 Skills → 打包安装的技能
2. Managed Skills → ~/.openclaw/skills
3. Workspace Skills → <workspace>/skills
   (workspace 优先于同名 skill)
```

### 配置文件查找

```
Agent 配置查找顺序:
1. agents.list[<id>]    # 指定 Agent 配置
2. agents.defaults      # 默认配置
3. 内置默认值
```

---

## 9. 常见问题

### Q: 如何让 Agent 使用新的人格？

A: 修改 `SOUL.md` 文件内容，对话会自动使用新内容。

### Q: 如何禁用某些工具？

A: 在 `openclaw.json` 中配置：
```json
{
  "tools": {
    "deny": ["browser", "exec"]
  }
}
```

### Q: 上下文窗口满了怎么办？

A: 使用 compaction 压缩历史：
```bash
/compact
```

### Q: 如何让子代理有不同的行为？

A: 设置 `promptMode: "minimal"` 或通过 `agent:bootstrap` hook 替换注入内容。
