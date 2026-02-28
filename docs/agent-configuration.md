# OpenClaw Agent 与模型配置指南

本文档详细介绍如何通过 CLI 创建 Agent、配置模型和 API 密钥。

## 目录

1. [Agent 管理](#agent-管理)
2. [模型配置](#模型配置)
3. [API 密钥配置](#api-密钥配置)
4. [技能配置](#技能配置)
5. [配置示例](#配置示例)

---

## Agent 管理

### 列出所有 Agent

```bash
openclaw agents list
```

### 创建新 Agent

```bash
# 基本创建
openclaw agents add my-agent --workspace ~/my-agent-workspace

# 指定模型
openclaw agents add coder --workspace ~/coder-workspace --model qwen-portal/coder-model

# 绑定渠道
openclaw agents add telegram-agent --bind telegram:myaccount
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `--workspace` | Agent 的工作目录 |
| `--model` | 使用的模型 ID |
| `--bind` | 绑定渠道 (可多次使用) |
| `--agent-dir` | Agent 状态目录 |

### 删除 Agent

```bash
openclaw agents delete my-agent
```

### 设置 Agent 身份

```bash
# 从 IDENTITY.md 文件读取
openclaw agents set-identity --agent main --from-identity

# 手动设置
openclaw agents set-identity --agent main --name "My Agent" --emoji "🤖" --avatar "avatar.png"
```

---

## 模型配置

### 查看当前模型配置

```bash
# 查看默认模型
openclaw config get agents.defaults.model

# 查看所有模型
openclaw config get models.providers
```

### 设置主模型

```bash
# 设置主模型
openclaw config set agents.defaults.model.primary "minimax-cn/MiniMax-M2.5"

# 添加备用模型
openclaw config set agents.defaults.model.fallbacks '["minimax-portal/MiniMax-M2.1", "qwen-portal/coder-model"]'
```

### 模型 ID 格式

模型 ID 格式为 `<provider>/<model-id>`，例如：
- `minimax-cn/MiniMax-M2.5`
- `qwen-portal/coder-model`
- `minimax-portal/MiniMax-M2.1`

---

## API 密钥配置

### 方式 1：通过交互式配置

```bash
# 启动交互式配置向导
openclaw configure

# 只配置模型
openclaw configure --section model

# 只配置 web 工具
openclaw configure --section web
```

### 方式 2：手动编辑配置

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "models": {
    "providers": {
      "minimax-cn": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "apiKey": "your-api-key-here",
        "api": "anthropic-messages"
      },
      "openai": {
        "baseUrl": "https://api.openai.com/v1",
        "apiKey": "sk-xxx",
        "api": "openai-completions"
      }
    }
  }
}
```

### 方式 3：通过环境变量

```bash
# 设置 API 密钥
export MINIMAX_API_KEY="your-key"
export OPENAI_API_KEY="sk-xxx"

# 设置提供商
export OPENCLAW_PROVIDER="minimax-cn"
```

### 方式 4：通过 secrets

```bash
# 添加 secrets
openclaw secrets add minimax-api-key "your-key"
openclaw secrets add openai-api-key "sk-xxx"

# 在配置中引用
openclaw config set models.providers.minimax-cn.apiKey "{{secrets.minimax-api-key}}"
```

### 认证模式

OpenClaw 支持多种认证模式：

```json
{
  "auth": {
    "profiles": {
      "minimax-cn:default": {
        "provider": "minimax-cn",
        "mode": "api_key"
      },
      "minimax-portal:default": {
        "provider": "minimax-portal",
        "mode": "oauth"
      }
    }
  }
}
```

**认证模式：**
- `api_key` - 直接使用 API 密钥
- `oauth` - 使用 OAuth 认证

---

## 技能配置

### 安装技能

```bash
# 列出可用技能
openclaw skills list

# 安装技能
openclaw skills install github
openclaw skills install feishu-doc
```

### 配置技能

技能在 agent 的 `skills` 目录中配置：

```bash
# 查看已安装技能
ls ~/.openclaw/skills/

# 查看特定技能
openclaw skills info github
```

---

## 配置示例

### 完整 Agent 配置示例

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax-cn/MiniMax-M2.5",
        "fallbacks": [
          "minimax-portal/MiniMax-M2.1",
          "qwen-portal/coder-model"
        ]
      },
      "models": {
        "minimax-cn/MiniMax-M2.5": {
          "alias": "minimax"
        },
        "qwen-portal/coder-model": {
          "alias": "qwen"
        }
      },
      "workspace": "/path/to/workspace",
      "tools": {
        "profile": "coding"
      },
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      }
    }
  },
  "models": {
    "providers": {
      "minimax-cn": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "apiKey": "{{secrets.minimax-api-key}}",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "MiniMax-M2.5",
            "name": "MiniMax M2.5",
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      },
      "qwen-portal": {
        "baseUrl": "https://portal.qwen.ai/v1",
        "apiKey": "{{secrets.qwen-api-key}}",
        "api": "openai-completions",
        "models": [
          {
            "id": "coder-model",
            "name": "Qwen Coder",
            "contextWindow": 128000
          }
        ]
      }
    }
  },
  "auth": {
    "profiles": {
      "minimax-cn:default": {
        "provider": "minimax-cn",
        "mode": "api_key"
      }
    }
  }
}
```

### 创建专属 Coding Agent

```bash
# 1. 创建工作目录
mkdir -p ~/coder-workspace

# 2. 创建 Agent
openclaw agents add coder \
  --workspace ~/coder-workspace \
  --model qwen-portal/coder-model \
  --bind telegram:coder

# 3. 配置工具权限
openclaw config set agents.defaults.tools.profile "coding"
```

### 创建专属写作 Agent

```bash
# 1. 创建 Agent
openclaw agents add writer \
  --workspace ~/writer-workspace \
  --model minimax-cn/MiniMax-M2.5

# 2. 设置身份
openclaw agents set-identity --agent writer \
  --name "写作助手" \
  --emoji "✍️"
```

---

## 常用命令速查

```bash
# Agent 管理
openclaw agents list                          # 列出所有 Agent
openclaw agents add <name> --workspace <path> # 创建 Agent
openclaw agents delete <name>                  # 删除 Agent
openclaw agents bind --agent <name> --bind <channel>  # 绑定渠道
openclaw agents set-identity --agent <name>   # 设置身份

# 模型配置
openclaw config get agents.defaults.model      # 查看模型配置
openclaw config set agents.defaults.model.primary "<model>"  # 设置主模型

# 密钥配置
openclaw configure                            # 交互式配置
openclaw configure --section model            # 只配置模型
openclaw secrets add <key> <value>            # 添加密钥

# 技能
openclaw skills list                          # 列出技能
openclaw skills install <name>                # 安装技能

# 状态查看
openclaw status                               # 查看状态
openclaw models                               # 列出可用模型
```

---

## 故障排除

### 模型无法使用

1. 检查 API 密钥是否正确配置
2. 验证密钥是否有效：`openclaw models`
3. 查看日志：`openclaw logs`

### 配置不生效

1. 重启 Gateway：`openclaw gateway restart`
2. 检查配置语法：`openclaw doctor`
3. 手动验证 JSON 格式

### 密钥安全问题

- 不要在配置文件中明文存储密钥
- 使用 `secrets` 功能或环境变量
- 定期轮换 API 密钥
