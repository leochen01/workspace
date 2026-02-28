# OpenClaw Multi-Tenant API Server

多租户版本的 Agent 管理 API，支持用户隔离。

## 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/scripts
pip install fastapi uvicorn httpx pydantic
```

### 2. 启动服务

```bash
python openclaw_api_server_multitenant.py
# 或
uvicorn openclaw_api_server_multitenant:APP --host 0.0.0.0 --port 18888
```

### 3. 设置环境变量

```bash
export OPENCLAW_API_TOKEN="your-secret-token"
export OPENCLAW_GATEWAY_URL="http://127.0.0.1:18789"
export OPENCLAW_GATEWAY_TOKEN="your-gateway-token"
```

---

## API 接口

### 租户管理

#### 创建租户

```bash
curl -X POST http://localhost:18888/api/tenants \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "user_001",
    "name": "张三",
    "model": "minimax-cn/MiniMax-M2.5"
  }'
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `tenant_id` | string | 租户唯一标识 |
| `name` | string | 租户名称 |
| `workspace` | string | 自定义工作空间 |
| `model` | string | 使用的模型 |
| `channel` | string | 绑定渠道 |
| `user_id` | string | 渠道用户ID |

**响应：**
```json
{
  "ok": true,
  "tenant_id": "user_001",
  "workspace": "/Users/xxx/.openclaw/workspace-user_001",
  "message": "Tenant 'user_001' created successfully"
}
```

---

#### 列出所有租户

```bash
curl http://localhost:18888/api/tenants \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "ok": true,
  "tenants": [
    {
      "tenant_id": "user_001",
      "workspace": "/Users/xxx/.openclaw/workspace-user_001",
      "model": "minimax-cn/MiniMax-M2.5",
      "bindings": [],
      "session_count": 5
    }
  ]
}
```

---

#### 获取租户详情

```bash
curl http://localhost:18888/api/tenants/user_001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

#### 删除租户

```bash
curl -X DELETE http://localhost:18888/api/tenants/user_001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 聊天接口

#### 与租户聊天

```bash
curl -X POST http://localhost:18888/api/tenants/user_001/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "user_001",
    "message": "你好"
  }'
```

**特点：**
- 自动使用租户专属的 Agent
- 每次对话生成唯一的 session_key
- 会话完全隔离

---

### 会话管理

#### 列出会话

```bash
curl http://localhost:18888/api/tenants/user_001/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "ok": true,
  "tenant_id": "user_001",
  "sessions": [
    {
      "session_id": "tenant:user_001:a1b2c3d4",
      "size_bytes": 15234,
      "updated_at": "2026-02-28 14:30:00"
    }
  ]
}
```

#### 删除会话

```bash
curl -X DELETE http://localhost:18888/api/tenants/user_001/sessions/tenant:user_001:a1b2c3d4 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 配置管理

#### 获取配置

```bash
curl http://localhost:18888/api/tenants/user_001/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 设置配置

```bash
curl -X POST http://localhost:18888/api/tenants/user_001/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "user_001",
    "key": "SOUL",
    "value": "# SOUL.md - 我是谁\n\n## 核心原则\n- 保持专业..."
  }'
```

支持的 key：
- `SOUL` - Agent 人格
- `USER` - 用户信息
- `AGENTS` - 操作指令
- `custom` - 自定义配置

---

### 渠道绑定

#### 添加绑定

```bash
curl -X POST "http://localhost:18888/api/tenants/user_001/binding?channel=telegram&user_id=123456789" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 架构说明

### 隔离机制

```
┌─────────────────────────────────────────────────────────┐
│                   OpenClaw Gateway                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Tenant 1   │  │  Tenant 2   │  │  Tenant N   │   │
│  │ agent:user1 │  │ agent:user2 │  │ agent:userN │   │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤   │
│  │ workspace   │  │ workspace   │  │ workspace   │   │
│  │ -user1     │  │ -user2     │  │ -userN     │   │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤   │
│  │ sessions   │  │ sessions   │  │ sessions   │   │
│  │ /user1/    │  │ /user2/    │  │ /userN/    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
~/.openclaw/
├── agents/
│   ├── main/              # 默认 Agent
│   ├── user1/             # 租户 1
│   │   ├── agent/         # Agent 配置
│   │   └── sessions/       # 会话历史
│   └── user2/             # 租户 2
│       ├── agent/
│       └── sessions/
├── workspace/             # 默认工作空间
├── workspace-user1/        # 租户 1 工作空间
│   ├── SOUL.md
│   ├── USER.md
│   ├── AGENTS.md
│   └── MEMORY.md
└── workspace-user2/       # 租户 2 工作空间
    └── ...
```

---

## Python SDK 示例

```python
import requests

TOKEN = "your-secret-token"
BASE_URL = "http://localhost:18888"

headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. 创建租户
resp = requests.post(
    f"{BASE_URL}/api/tenants",
    headers=headers,
    json={
        "tenant_id": "user_001",
        "name": "张三",
        "model": "minimax-cn/MiniMax-M2.5"
    }
)
print(resp.json())

# 2. 与租户聊天
resp = requests.post(
    f"{BASE_URL}/api/tenants/user_001/chat",
    headers=headers,
    json={
        "tenant_id": "user_001",
        "message": "你好"
    }
)
print(resp.json())

# 3. 设置 Agent 人格
resp = requests.post(
    f"{BASE_URL}/api/tenants/user_001/config",
    headers=headers,
    json={
        "tenant_id": "user_001",
        "key": "SOUL",
        "value": "# SOUL.md\n\n我是专业的技术顾问..."
    }
)
print(resp.json())

# 4. 查看会话
resp = requests.get(
    f"{BASE_URL}/api/tenants/user_001/sessions",
    headers=headers
)
print(resp.json())
```

---

## 完整 API 列表

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/tenants` | 创建租户 |
| GET | `/api/tenants` | 列出所有租户 |
| GET | `/api/tenants/{id}` | 获取租户详情 |
| DELETE | `/api/tenants/{id}` | 删除租户 |
| POST | `/api/tenants/{id}/chat` | 租户聊天 |
| POST | `/api/tenants/{id}/binding` | 添加渠道绑定 |
| GET | `/api/tenants/{id}/sessions` | 列出所有会话 |
| DELETE | `/api/tenants/{id}/sessions/{sid}` | 删除会话 |
| GET | `/api/tenants/{id}/config` | 获取配置 |
| POST | `/api/tenants/{id}/config` | 设置配置 |
| GET | `/health` | 健康检查 |
