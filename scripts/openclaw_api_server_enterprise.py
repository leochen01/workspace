#!/usr/bin/env python3
"""
OpenClaw Multi-Tenant API Server - Enterprise Version
业务模型：
- 租户 (Tenant) → 有多个 Agent
- 租户 (Tenant) → 有多个用户 (User)
- 用户 (User) → 根据权限可以看到不同的 Agent
- 用户 → 选择 Agent 进行会话
- 会话上下文完全隔离
"""

import os
import json
import subprocess
import uuid
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.responses import JSONResponse
import shutil

# ========== 配置 ==========
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
APP = FastAPI(
    title="OpenClaw Enterprise API", 
    version="3.0.0",
    description="企业级多租户 API - 租户→用户→Agent 三层架构"
)

API_TOKEN = os.environ.get("OPENCLAW_API_TOKEN", "your-secret-token")

# 数据存储路径
DATA_DIR = os.path.expanduser("~/.openclaw/multi-tenant")
TENANTS_FILE = os.path.join(DATA_DIR, "tenants.json")

# ========== 数据模型 ==========

class Tenant(BaseModel):
    """租户"""
    tenant_id: str
    name: str
    created_at: str = None
    
class Agent(BaseModel):
    """Agent"""
    agent_id: str
    tenant_id: str
    name: str
    model: str = "minimax-cn/MiniMax-M2.5"
    workspace: str = None
    description: str = ""
    
class User(BaseModel):
    """用户"""
    user_id: str
    tenant_id: str
    name: str
    email: str = ""
    allowed_agents: List[str] = []  # 有权限访问的 Agent 列表
    created_at: str = None

class UserCreate(BaseModel):
    """创建用户"""
    user_id: str
    tenant_id: str
    name: str
    email: str = ""
    allowed_agents: List[str] = []

class ChatRequest(BaseModel):
    """聊天请求"""
    tenant_id: str
    user_id: str
    agent_id: str
    message: str
    session_id: str = None  # 可选指定会话 ID

class UserPermissionUpdate(BaseModel):
    """更新用户权限"""
    allowed_agents: List[str]

# ========== 依赖 ==========

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid format")
    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

# ========== 工具函数 ==========

def run_cli(args: List[str], timeout: int = 30) -> Dict:
    cmd = ["openclaw"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_data() -> Dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(TENANTS_FILE):
        with open(TENANTS_FILE, 'r') as f:
            return json.load(f)
    return {"tenants": {}, "agents": {}, "users": {}}

def save_data(data: Dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TENANTS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_tenant_workspace(tenant_id: str) -> str:
    return os.path.expanduser(f"~/.openclaw/workspaces/{tenant_id}")

def get_agent_workspace(tenant_id: str, agent_id: str) -> str:
    return os.path.expanduser(f"~/.openclaw/workspaces/{tenant_id}/agents/{agent_id}")

def get_user_session_dir(tenant_id: str, user_id: str, agent_id: str) -> str:
    return os.path.expanduser(f"~/.openclaw/sessions/{tenant_id}/{user_id}/{agent_id}")

def generate_session_id() -> str:
    return f"sess_{int(time.time())}_{uuid.uuid4().hex[:8]}"

# ========== 租户管理 ==========

@APP.post("/api/tenants", dependencies=[Depends(verify_token)])
async def create_tenant(tenant: Tenant):
    """创建租户"""
    data = load_data()
    
    if tenant.tenant_id in data["tenants"]:
        raise HTTPException(status_code=400, detail="Tenant exists")
    
    # 创建租户工作空间
    workspace = get_tenant_workspace(tenant.tenant_id)
    os.makedirs(workspace, exist_ok=True)
    
    # 初始化租户配置
    tenant.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    data["tenants"][tenant.tenant_id] = tenant.dict()
    
    save_data(data)
    
    return {"ok": True, "tenant_id": tenant.tenant_id, "workspace": workspace}

@APP.get("/api/tenants", dependencies=[Depends(verify_token)])
async def list_tenants():
    """列出租户"""
    data = load_data()
    return {"ok": True, "tenants": list(data["tenants"].values())}

@APP.get("/api/tenants/{tenant_id}", dependencies=[Depends(verify_token)])
async def get_tenant(tenant_id: str):
    """获取租户详情"""
    data = load_data()
    if tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant = data["tenants"][tenant_id]
    agents = [a for a in data["agents"].values() if a["tenant_id"] == tenant_id]
    users = [u for u in data["users"].values() if u["tenant_id"] == tenant_id]
    
    return {
        "ok": True,
        "tenant": tenant,
        "agents_count": len(agents),
        "users_count": len(users)
    }

@APP.delete("/api/tenants/{tenant_id}", dependencies=[Depends(verify_token)])
async def delete_tenant(tenant_id: str):
    """删除租户"""
    data = load_data()
    if tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # 删除工作空间
    workspace = get_tenant_workspace(tenant_id)
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    
    # 删除会话数据
    sessions_dir = os.path.expanduser(f"~/.openclaw/sessions/{tenant_id}")
    if os.path.exists(sessions_dir):
        shutil.rmtree(sessions_dir)
    
    # 从数据中移除
    del data["tenants"][tenant_id]
    data["agents"] = {k: v for k, v in data["agents"].items() if v["tenant_id"] != tenant_id}
    data["users"] = {k: v for k, v in data["users"].items() if v["tenant_id"] != tenant_id}
    
    save_data(data)
    
    return {"ok": True, "message": f"Tenant {tenant_id} deleted"}

# ========== Agent 管理 ==========

@APP.post("/api/tenants/{tenant_id}/agents", dependencies=[Depends(verify_token)])
async def create_agent(tenant_id: str, agent: Agent):
    """在租户下创建 Agent"""
    data = load_data()
    
    if tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    agent_key = f"{tenant_id}_{agent.agent_id}"
    if agent_key in data["agents"]:
        raise HTTPException(status_code=400, detail="Agent exists")
    
    # 创建 Agent 工作空间
    workspace = get_agent_workspace(tenant_id, agent.agent_id)
    os.makedirs(workspace, exist_ok=True)
    
    # 创建基础文件
    files = {
        "SOUL.md": f"""# SOUL.md - {agent.name}

## 核心原则
- 专业的 {agent.name}
- 帮助用户解决问题

## 风格
专业、友好、有帮助。
""",
        "USER.md": f"""# USER.md

Agent: {agent.name}
描述: {agent.description}
""",
        "AGENTS.md": f"""# AGENTS.md

## 关于
这是 {agent.name} Agent
"""
    }
    
    for fname, content in files.items():
        with open(os.path.join(workspace, fname), 'w') as f:
            f.write(content)
    
    # 保存 Agent 配置
    agent.tenant_id = tenant_id
    agent.workspace = workspace
    data["agents"][agent_key] = agent.dict()
    
    save_data(data)
    
    return {"ok": True, "agent_id": agent.agent_id, "workspace": workspace}

@APP.get("/api/tenants/{tenant_id}/agents", dependencies=[Depends(verify_token)])
async def list_agents(tenant_id: str):
    """列出租户下的所有 Agent"""
    data = load_data()
    
    if tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    agents = [a for a in data["agents"].values() if a["tenant_id"] == tenant_id]
    
    return {"ok": True, "agents": agents}

@APP.get("/api/tenants/{tenant_id}/agents/{agent_id}", dependencies=[Depends(verify_token)])
async def get_agent(tenant_id: str, agent_id: str):
    """获取 Agent 详情"""
    data = load_data()
    
    agent_key = f"{tenant_id}_{agent_id}"
    if agent_key not in data["agents"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"ok": True, "agent": data["agents"][agent_key]}

@APP.delete("/api/tenants/{tenant_id}/agents/{agent_id}", dependencies=[Depends(verify_token)])
async def delete_agent(tenant_id: str, agent_id: str):
    """删除 Agent"""
    data = load_data()
    
    agent_key = f"{tenant_id}_{agent_id}"
    if agent_key not in data["agents"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 删除工作空间
    workspace = get_agent_workspace(tenant_id, agent_id)
    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    
    del data["agents"][agent_key]
    
    # 移除用户对该 Agent 的权限
    for user in data["users"].values():
        if agent_id in user.get("allowed_agents", []):
            user["allowed_agents"].remove(agent_id)
    
    save_data(data)
    
    return {"ok": True, "message": f"Agent {agent_id} deleted"}

# ========== 用户管理 ==========

@APP.post("/api/tenants/{tenant_id}/users", dependencies=[Depends(verify_token)])
async def create_user(tenant_id: str, user: UserCreate):
    """在租户下创建用户"""
    data = load_data()
    
    if tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    user_key = f"{tenant_id}_{user.user_id}"
    if user_key in data["users"]:
        raise HTTPException(status_code=400, detail="User exists")
    
    # 验证权限配置中的 Agent 是否存在
    for agent_id in user.allowed_agents:
        agent_key = f"{tenant_id}_{agent_id}"
        if agent_key not in data["agents"]:
            raise HTTPException(status_code=400, detail=f"Agent {agent_id} not found")
    
    # 保存用户
    user.tenant_id = tenant_id
    user.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    data["users"][user_key] = user.dict()
    
    save_data(data)
    
    return {"ok": True, "user_id": user.user_id}

@APP.get("/api/tenants/{tenant_id}/users", dependencies=[Depends(verify_token)])
async def list_users(tenant_id: str):
    """列出租户下的所有用户"""
    data = load_data()
    
    if tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    users = [u for u in data["users"].values() if u["tenant_id"] == tenant_id]
    
    return {"ok": True, "users": users}

@APP.get("/api/tenants/{tenant_id}/users/{user_id}", dependencies=[Depends(verify_token)])
async def get_user(tenant_id: str, user_id: str):
    """获取用户详情"""
    data = load_data()
    
    user_key = f"{tenant_id}_{user_id}"
    if user_key not in data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = data["users"][user_key]
    
    # 获取用户可访问的 Agent 详情
    accessible_agents = []
    for agent_id in user.get("allowed_agents", []):
        agent_key = f"{tenant_id}_{agent_id}"
        if agent_key in data["agents"]:
            accessible_agents.append(data["agents"][agent_key])
    
    return {
        "ok": True,
        "user": user,
        "accessible_agents": accessible_agents
    }

@APP.put("/api/tenants/{tenant_id}/users/{user_id}/permissions", dependencies=[Depends(verify_token)])
async def update_user_permissions(tenant_id: str, user_id: str, perm: UserPermissionUpdate):
    """更新用户的 Agent 访问权限"""
    data = load_data()
    
    user_key = f"{tenant_id}_{user_id}"
    if user_key not in data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 验证所有 Agent 存在
    for agent_id in perm.allowed_agents:
        agent_key = f"{tenant_id}_{agent_id}"
        if agent_key not in data["agents"]:
            raise HTTPException(status_code=400, detail=f"Agent {agent_id} not found")
    
    data["users"][user_key]["allowed_agents"] = perm.allowed_agents
    save_data(data)
    
    return {"ok": True, "allowed_agents": perm.allowed_agents}

@APP.delete("/api/tenants/{tenant_id}/users/{user_id}", dependencies=[Depends(verify_token)])
async def delete_user(tenant_id: str, user_id: str):
    """删除用户"""
    data = load_data()
    
    user_key = f"{tenant_id}_{user_id}"
    if user_key not in data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 删除用户会话
    session_dir = os.path.expanduser(f"~/.openclaw/sessions/{tenant_id}/{user_id}")
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
    
    del data["users"][user_key]
    save_data(data)
    
    return {"ok": True, "message": f"User {user_id} deleted"}

# ========== 聊天接口 ==========

@APP.post("/api/chat", dependencies=[Depends(verify_token)])
async def chat(chat_req: ChatRequest):
    """聊天接口
    
    关键：会话隔离
    - 每个用户有独立的会话目录
    - 用户只能访问有权限的 Agent
    - 会话 ID 格式: {tenant_id}_{user_id}_{agent_id}_{session_id}
    """
    data = load_data()
    
    # 1. 验证租户
    if chat_req.tenant_id not in data["tenants"]:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # 2. 验证用户
    user_key = f"{chat_req.tenant_id}_{chat_req.user_id}"
    if user_key not in data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = data["users"][user_key]
    
    # 3. 验证用户有权限访问该 Agent
    if chat_req.agent_id not in user.get("allowed_agents", []):
        raise HTTPException(status_code=403, detail="No permission to access this agent")
    
    # 4. 验证 Agent 存在
    agent_key = f"{chat_req.tenant_id}_{chat_req.agent_id}"
    if agent_key not in data["agents"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = data["agents"][agent_key]
    
    # 5. 生成或使用指定的会话 ID
    # 会话隔离: tenant_id/user_id/agent_id/session_id
    if chat_req.session_id:
        session_id = chat_req.session_id
    else:
        session_id = generate_session_id()
    
    # 完整会话 Key
    full_session_key = f"tenant:{chat_req.tenant_id}:user:{chat_req.user_id}:agent:{chat_req.agent_id}:{session_id}"
    
    # 6. 调用 Gateway
    gateway_url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789")
    gateway_token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", API_TOKEN)
    
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{gateway_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {gateway_token}",
                    "Content-Type": "application/json",
                    "x-openclaw-session-key": full_session_key
                },
                json={
                    "model": agent.get("model", "openclaw"),
                    "messages": [{"role": "user", "content": chat_req.message}]
                },
                timeout=120.0
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    result = response.json()
    
    return {
        "ok": True,
        "tenant_id": chat_req.tenant_id,
        "user_id": chat_req.user_id,
        "agent_id": chat_req.agent_id,
        "session_id": session_id,
        "response": result
    }

# ========== 会话管理 ==========

@APP.get("/api/tenants/{tenant_id}/users/{user_id}/sessions", dependencies=[Depends(verify_token)])
async def list_user_sessions(tenant_id: str, user_id: str):
    """列出用户的所有会话（按 Agent 分组）"""
    data = load_data()
    
    # 验证用户
    user_key = f"{tenant_id}_{user_id}"
    if user_key not in data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = data["users"][user_key]
    
    # 列出用户可访问的 Agent 的会话
    sessions_by_agent = {}
    
    for agent_id in user.get("allowed_agents", []):
        session_dir = os.path.expanduser(f"~/.openclaw/sessions/{tenant_id}/{user_id}/{agent_id}")
        
        if os.path.exists(session_dir):
            sessions = []
            for f in os.listdir(session_dir):
                if f.endswith('.jsonl'):
                    fpath = os.path.join(session_dir, f)
                    sessions.append({
                        "session_id": f.replace('.jsonl', ''),
                        "size": os.path.getsize(fpath),
                        "modified": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(fpath)))
                    })
            sessions_by_agent[agent_id] = sessions
        else:
            sessions_by_agent[agent_id] = []
    
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "sessions_by_agent": sessions_by_agent
    }

@APP.delete("/api/tenants/{tenant_id}/users/{user_id}/sessions/{agent_id}/{session_id}", dependencies=[Depends(verify_token)])
async def delete_session(tenant_id: str, user_id: str, agent_id: str, session_id: str):
    """删除用户的特定会话"""
    data = load_data()
    
    # 验证用户有权限
    user_key = f"{tenant_id}_{user_id}"
    if user_key not in data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = data["users"][user_key]
    if agent_id not in user.get("allowed_agents", []):
        raise HTTPException(status_code=403, detail="No permission")
    
    # 删除会话文件
    session_file = os.path.expanduser(f"~/.openclaw/sessions/{tenant_id}/{user_id}/{agent_id}/{session_id}.jsonl")
    
    if os.path.exists(session_file):
        os.remove(session_file)
        return {"ok": True, "message": "Session deleted"}
    
    raise HTTPException(status_code=404, detail="Session not found")

# ========== 权限验证 ==========

@APP.get("/api/tenants/{tenant_id}/users/{user_id}/can_use/{agent_id}", dependencies=[Depends(verify_token)])
async def check_permission(tenant_id: str, user_id: str, agent_id: str):
    """检查用户是否有权限使用某个 Agent"""
    data = load_data()
    
    user_key = f"{tenant_id}_{user_id}"
    if user_key not in data["users"]:
        return {"ok": True, "allowed": False, "reason": "User not found"}
    
    user = data["users"][user_key]
    allowed = agent_id in user.get("allowed_agents", [])
    
    return {
        "ok": True,
        "allowed": allowed,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "agent_id": agent_id
    }

# ========== 健康检查 ==========

@APP.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "mode": "enterprise-multi-tenant"
    }

# ========== 主程序 ==========

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║     OpenClaw Enterprise Multi-Tenant API             ║
╠══════════════════════════════════════════════════════════╣
║  Version: 3.0.0                                      ║
║  Token: {API_TOKEN[:40]:<40}║
╠══════════════════════════════════════════════════════════╣
║  业务模型:                                            ║
║    租户 (Tenant)                                       ║
║      └── 用户 (User) ← 多用户                          ║
║      └── Agent (代理) ← 多 Agent                       ║
║                                                         ║
║    用户 → 权限配置 → 可访问的不同 Agent                ║
║    用户 × Agent → 独立会话隔离                         ║
╠══════════════════════════════════════════════════════════╣
║  Endpoints:                                           ║
║    POST   /api/tenants                    创建租户    ║
║    GET    /api/tenants                    列出租户    ║
║    DELETE /api/tenants/{id}               删除租户    ║
║    POST   /api/tenants/{id}/agents        创建 Agent ║
║    GET    /api/tenants/{id}/agents        列出 Agent ║
║    DELETE /api/tenants/{id}/agents/{id}    删除 Agent ║
║    POST   /api/tenants/{id}/users         创建用户   ║
║    GET    /api/tenants/{id}/users         列出用户   ║
║    PUT    /api/tenants/{id}/users/{id}/permissions 更新权限║
║    DELETE /api/tenants/{id}/users/{id}     删除用户   ║
║    POST   /api/chat                       聊天接口   ║
║    GET    /api/tenants/{id}/users/{id}/sessions 会话列表║
║    DELETE .../sessions/{agent_id}/{sid}    删除会话  ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(APP, host="0.0.0.0", port=18888)
