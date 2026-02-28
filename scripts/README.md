# OpenClaw Agent API Server

HTTP API 服务，封装 OpenClaw CLI 实现 Agent 管理。

## 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/scripts
pip install -r requirements.txt
```

### 2. 设置 API Token

```bash
export OPENCLAW_API_TOKEN="your-secret-token"
```

### 3. 启动服务

**标准版 (无需额外依赖):**
```bash
python openclaw_api_server.py --port 18888 --token your-secret-token
```

**FastAPI 版 (推荐):**
```bash
python openclaw_api_server_fast.py
# 或
uvicorn openclaw_api_server_fast:APP --host 0.0.0.0 --port 18888
```

## API 接口

### Agent 管理

```bash
# 列出所有 Agent
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:18888/api/agents

# 创建 Agent
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "workspace": "~/my-workspace", "model": "qwen-portal/coder-model"}' \
  http://localhost:18888/api/agents

# 删除 Agent
curl -X DELETE -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent"}' \
  http://localhost:18888/api/agents
```

### 模型配置

```bash
# 列出可用模型
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:18888/api/models

# 设置 Agent 模型
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "minimax-cn/MiniMax-M2.5", "agent": "defaults"}' \
  http://localhost:18888/api/model
```

### API 密钥

```bash
# 列出已配置的模型提供商
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:18888/api/providers

# 设置 API 密钥
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider": "minimax-cn", "api_key": "your-api-key"}' \
  http://localhost:18888/api/api-key
```

### 技能管理

```bash
# 列出已安装技能
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:18888/api/skills

# 安装技能
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "github"}' \
  http://localhost:18888/api/skills/install
```

### 配置管理

```bash
# 获取完整配置
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:18888/api/config

# 设置配置项
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path": "agents.defaults.model.primary", "value": "minimax-cn/MiniMax-M2.5"}' \
  http://localhost:18888/api/config
```

### 状态

```bash
# 获取 OpenClaw 状态
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:18888/api/status
```

## Python SDK 示例

```python
import requests

TOKEN = "your-secret-token"
BASE_URL = "http://localhost:18888"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 创建 Agent
resp = requests.post(
    f"{BASE_URL}/api/agents",
    headers=headers,
    json={
        "name": "coder",
        "workspace": "~/coder-workspace",
        "model": "qwen-portal/coder-model"
    }
)
print(resp.json())

# 设置模型
resp = requests.post(
    f"{BASE_URL}/api/model",
    headers=headers,
    json={"model": "minimax-cn/MiniMax-M2.5"}
)
print(resp.json())

# 获取配置
resp = requests.get(f"{BASE_URL}/api/config", headers=headers)
print(resp.json())
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| OPENCLAW_API_TOKEN | API 认证 Token | your-secret-token |

## 端口

默认端口: `18888`
