# OpenClaw Enterprise API Server

企业级多租户 API，支持租户→用户→Agent 三层架构。

## 业务模型

```
┌─────────────────────────────────────────────────────────────┐
│                        租户 (Tenant)                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    Agent 列表                         │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │ │
│  │  │ Agent 1 │  │ Agent 2 │  │ Agent N │          │ │
│  │  │ (客服)   │  │ (销售)   │  │ (技术)   │          │ │
│  │  └─────────┘  └─────────┘  └─────────┘          │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    用户 列表                         │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │ │
│  │  │ User A  │  │ User B  │  │ User C  │          │ │
│  │  │ [Agent1]│  │[Agent1,2]│ │ [AgentN]│          │ │
│  │  └─────────┘  └─────────┘  └─────────┘          │ │
│  │    ↑              ↑              ↑                 │ │
│  │    └──────────────┴──────────────┘               │ │
│  │            权限配置: 用户可访问的Agent            │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 核心特性

| 特性 | 说明 |
|------|------|
| 三层隔离 | Tenant → User → Agent 完全隔离 |
| 权限控制 | 用户只能访问被授权的 Agent |
| 会话隔离 | 每个用户×Agent 有独立会话 |
| 独立配置 | 每个 Agent 有独立 workspace |

---

## 快速开始

```bash
# 启动服务
python scripts/openclaw_api_server_enterprise.py

# 或
uvicorn scripts/openclaw_api_server_enterprise:APP --host 0.0.0.0 --port 18888
```

---

## API 接口

### 1. 租户管理

#### 创建租户

```bash
curl -X POST http://localhost:18888/api/tenants \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "company_a",
    "name": "A公司"
  }'
```

#### 列出租户

```bash
curl http://localhost:18888/api/tenants \
  -H "Authorization: Bearer TOKEN"
```

---

### 2. Agent 管理

#### 创建 Agent

```bash
curl -X POST http://localhost:18888/api/tenants/company_a/agents \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "support",
    "name": "客服助手",
    "description": "提供客户服务支持",
    "model": "minimax-cn/MiniMax-M2.5"
  }'
```

#### 列出 Agent

```bash
curl http://localhost:18888/api/tenants/company_a/agents \
  -H "Authorization: Bearer TOKEN"
```

---

### 3. 用户管理

#### 创建用户

```bash
curl -X POST http://localhost:18888/api/tenants/company_a/users \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "zhangsan",
    "name": "张三",
    "email": "zhangsan@company.com",
    "allowed_agents": ["support", "sales"]
  }'
```

#### 更新用户权限

```bash
curl -X PUT http://localhost:18888/api/tenants/company_a/users/zhangsan/permissions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "allowed_agents": ["support", "sales", "tech"]
  }'
```

---

### 4. 聊天接口

#### 用户与 Agent 聊天

```bash
curl -X POST http://localhost:18888/api/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "company_a",
    "user_id": "zhangsan",
    "agent_id": "support",
    "message": "你好，我想咨询一下产品问题"
  }'
```

**响应：**
```json
{
  "ok": true,
  "tenant_id": "company_a",
  "user_id": "zhangsan",
  "agent_id": "support",
  "session_id": "sess_1234567890_abc123",
  "response": {
    "choices": [{
      "message": {"role": "assistant", "content": "您好！有什么可以帮助您的？"}
    }]
  }
}
```

#### 继续会话

```bash
curl -X POST http://localhost:18888/api/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "company_a",
    "user_id": "zhangsan",
    "agent_id": "support",
    "session_id": "sess_1234567890_abc123",
    "message": "我想了解企业版的功能"
  }'
```

---

### 5. 会话管理

#### 列出用户所有会话

```bash
curl http://localhost:18888/api/tenants/company_a/users/zhangsan/sessions \
  -H "Authorization: Bearer TOKEN"
```

**响应：**
```json
{
  "ok": true,
  "tenant_id": "company_a",
  "user_id": "zhangsan",
  "sessions_by_agent": {
    "support": [
      {"session_id": "sess_xxx", "size": 12345, "modified": "2026-02-28 14:30"},
      {"session_id": "sess_yyy", "size": 6789, "modified": "2026-02-27 10:00"}
    ],
    "sales": []
  }
}
```

#### 删除会话

```bash
curl -X DELETE http://localhost:18888/api/tenants/company_a/users/zhangsan/sessions/support/sess_xxx \
  -H "Authorization: Bearer TOKEN"
```

---

### 6. 权限验证

#### 检查权限

```bash
curl http://localhost:18888/api/tenants/company_a/users/zhangsan/can_use/support \
  -H "Authorization: Bearer TOKEN"
```

---

## 完整 API 列表

| 方法 | 端点 | 说明 |
|------|------|------|
| **租户管理** |||
| POST | `/api/tenants` | 创建租户 |
| GET | `/api/tenants` | 列出租户 |
| GET | `/api/tenants/{id}` | 获取租户详情 |
| DELETE | `/api/tenants/{id}` | 删除租户 |
| **Agent 管理** |||
| POST | `/api/tenants/{tid}/agents` | 创建 Agent |
| GET | `/api/tenants/{tid}/agents` | 列出 Agent |
| GET | `/api/tenants/{tid}/agents/{id}` | 获取 Agent |
| DELETE | `/api/tenants/{tid}/agents/{id}` | 删除 Agent |
| **用户管理** |||
| POST | `/api/tenants/{tid}/users` | 创建用户 |
| GET | `/api/tenants/{tid}/users` | 列出用户 |
| GET | `/api/tenants/{tid}/users/{id}` | 获取用户详情 |
| PUT | `/api/tenants/{tid}/users/{id}/permissions` | 更新权限 |
| DELETE | `/api/tenants/{tid}/users/{id}` | 删除用户 |
| **聊天** |||
| POST | `/api/chat` | 聊天 |
| **会话** |||
| GET | `/api/tenants/{tid}/users/{uid}/sessions` | 会话列表 |
| DELETE | `/api/tenants/{tid}/users/{uid}/sessions/{aid}/{sid}` | 删除会话 |

---

## 会话隔离机制

### 目录结构

```
~/.openclaw/
├── sessions/
│   └── {tenant_id}/
│       └── {user_id}/
│           └── {agent_id}/
│               ├── sess_1234567890_abc.jsonl
│               └── sess_9876543210_def.jsonl
```

### 会话 Key 格式

```
tenant:{tenant_id}:user:{user_id}:agent:{agent_id}:{session_id}
```

**示例：**
```
tenant:company_a:user:zhangsan:agent:support:sess_1234567890_abc123
```

### 隔离保证

1. **用户间隔离**：用户只能看到自己的会话
2. **Agent 间隔离**：用户访问不同 Agent 会话完全独立
3. **数据存储隔离**：每个 user × agent 组合有独立目录

---

## Python SDK

```python
import requests

TOKEN = "your-token"
BASE = "http://localhost:18888"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 1. 创建租户
requests.post(f"{BASE}/api/tenants", json={
    "tenant_id": "company_a", "name": "A公司"
}, headers=HEADERS)

# 2. 创建 Agent
requests.post(f"{BASE}/api/tenants/company_a/agents", json={
    "agent_id": "support", "name": "客服助手", "model": "minimax-cn/MiniMax-M2.5"
}, headers=HEADERS)

# 3. 创建用户（配置权限）
requests.post(f"{BASE}/api/tenants/company_a/users", json={
    "user_id": "zhangsan", "name": "张三",
    "allowed_agents": ["support"]
}, headers=HEADERS)

# 4. 聊天
resp = requests.post(f"{BASE}/api/chat", json={
    "tenant_id": "company_a",
    "user_id": "zhangsan",
    "agent_id": "support",
    "message": "你好"
}, headers=HEADERS)
print(resp.json())

# 5. 查看会话
resp = requests.get(f"{BASE}/api/tenants/company_a/users/zhangsan/sessions", 
                   headers=HEADERS)
print(resp.json())
```

---

## 权限流程

```
用户发起聊天
    │
    ▼
验证租户存在
    │
    ▼
验证用户存在
    │
    ▼
验证用户有权限访问该 Agent ←── 配置 allowed_agents
    │
    ▼
验证 Agent 存在
    │
    ▼
生成/使用会话 ID
    │
    ▼
调用 Gateway（带隔离的 session_key）
```

---

## 配置文件

数据存储在：`~/.openclaw/multi-tenant/tenants.json`

```json
{
  "tenants": {
    "company_a": {
      "tenant_id": "company_a",
      "name": "A公司",
      "created_at": "2026-02-28 14:00:00"
    }
  },
  "agents": {
    "company_a_support": {
      "agent_id": "support",
      "tenant_id": "company_a",
      "name": "客服助手",
      "workspace": "/path/to/workspace"
    }
  },
  "users": {
    "company_a_zhangsan": {
      "user_id": "zhangsan",
      "tenant_id": "company_a",
      "allowed_agents": ["support"]
    }
  }
}
```
