#!/usr/bin/env python3
"""
OpenClaw Agent Management API Server - Multi-Tenant Version
支持多租户的用户隔离，每个用户有独立的 Agent、workspace 和会话
"""

import os
import json
import subprocess
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse

# ========== 配置 ==========
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
APP = FastAPI(
    title="OpenClaw Multi-Tenant API", 
    version="2.0.0",
    description="多租户 Agent 管理 API"
)

# API 密钥验证
API_TOKEN = os.environ.get("OPENCLAW_API_TOKEN", "your-secret-token")


# ========== Pydantic 模型 ==========

class TenantCreate(BaseModel):
    """创建租户"""
    tenant_id: str  # 租户标识
    name: Optional[str] = None  # 租户名称
    workspace: Optional[str] = None  # 自定义工作空间
    model: Optional[str] = None  # 使用的模型
    channel: Optional[str] = None  # 绑定渠道 (telegram/discord/whatsapp)
    user_id: Optional[str] = None  # 渠道用户ID


class TenantUpdate(BaseModel):
    """更新租户"""
    name: Optional[str] = None
    model: Optional[str] = None


class TenantChat(BaseModel):
    """租户聊天"""
    tenant_id: str
    message: str
    stream: bool = False


class TenantConfig(BaseModel):
    """租户配置"""
    tenant_id: str
    key: str
    value: Any


class ApiKeySet(BaseModel):
    """设置 API 密钥"""
    provider: str
    api_key: str


# ========== 依赖 ==========

async def verify_token(authorization: str = Header(None)):
    """验证 API Token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    
    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return True


# ========== 工具函数 ==========

def run_cli(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    """执行 OpenClaw CLI 命令"""
    cmd = ["openclaw"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Command timeout", "code": -1}
    except FileNotFoundError:
        return {"ok": False, "error": "OpenClaw CLI not found", "code": -1}
    except Exception as e:
        return {"ok": False, "error": str(e), "code": -1}


def get_config() -> Dict:
    """读取配置文件"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config read error: {e}")


def save_config(config: Dict) -> None:
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config write error: {e}")


def get_tenant_workspace(tenant_id: str) -> str:
    """获取租户的工作空间路径"""
    return os.path.expanduser(f"~/.openclaw/workspace-{tenant_id}")


def get_tenant_agent_dir(tenant_id: str) -> str:
    """获取租户的 agent 目录"""
    return os.path.expanduser(f"~/.openclaw/agents/{tenant_id}")


# ========== 租户管理端点 ==========

@APP.post("/api/tenants", dependencies=[Depends(verify_token)])
async def create_tenant(tenant: TenantCreate):
    """
    创建新租户
    
    每个租户拥有：
    - 独立的 Agent (agentId = tenant_id)
    - 独立的工作空间 (workspace-tenant_id)
    - 独立的会话存储
    - 可选的渠道绑定
    """
    tenant_id = tenant.tenant_id
    
    # 验证 tenant_id 格式
    if not tenant_id or not tenant_id.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid tenant_id format")
    
    # 检查是否已存在
    config = get_config()
    agents_list = config.get("agents", {}).get("list", [])
    for agent in agents_list:
        if agent.get("id") == tenant_id:
            raise HTTPException(status_code=400, detail=f"Tenant {tenant_id} already exists")
    
    # 创建工作空间
    workspace = tenant.workspace or get_tenant_workspace(tenant_id)
    workspace = os.path.expanduser(workspace)
    os.makedirs(workspace, exist_ok=True)
    
    # 创建基础配置文件
    workspace_files = {
        "SOUL.md": """# SOUL.md - 我是谁

## 核心原则
- 真诚帮助用户解决问题
- 保持专业但友好的语气
- 尊重用户隐私

## 风格
有用就说话，无需则安静。
""",
        "USER.md": f"""# USER.md - 关于用户

- **租户ID**: {tenant_id}
- **名称**: {tenant.name or '未命名'}
- **创建时间**: 自动记录
""",
        "AGENTS.md": """# AGENTS.md - 工作区指南

## 每轮会话
1. 读 `SOUL.md` — 我是谁
2. 读 `USER.md` — 用户是谁

## 注意事项
- 保护用户隐私
- 不泄露配置信息
""",
        "MEMORY.md": f"""# MEMORY.md - {tenant.name or tenant_id} 的记忆

## 重要记录
- 租户ID: {tenant_id}
- 创建时间: 自动记录
"""
    }
    
    for filename, content in workspace_files.items():
        filepath = os.path.join(workspace, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)
    
    # 添加 Agent 到配置
    agent_config = {
        "id": tenant_id,
        "workspace": workspace
    }
    
    if "agents" not in config:
        config["agents"] = {}
    if "list" not in config["agents"]:
        config["agents"]["list"] = []
    
    config["agents"]["list"].append(agent_config)
    
    # 如果指定了渠道，添加 Binding
    if tenant.channel and tenant.user_id:
        if "bindings" not in config:
            config["bindings"] = []
        
        binding = {
            "agentId": tenant_id,
            "match": {
                "channel": tenant.channel,
                "peer": {"id": tenant.user_id}
            }
        }
        config["bindings"].append(binding)
    
    save_config(config)
    
    # 设置默认模型（如果指定）
    if tenant.model:
        run_cli(["config", "set", f"agents.list.{tenant_id}.model.primary", tenant.model])
    
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "workspace": workspace,
        "message": f"Tenant '{tenant_id}' created successfully"
    }


@APP.get("/api/tenants", dependencies=[Depends(verify_token)])
async def list_tenants():
    """列出所有租户"""
    config = get_config()
    agents_list = config.get("agents", {}).get("list", [])
    bindings = config.get("bindings", [])
    
    tenants = []
    for agent in agents_list:
        tenant_id = agent.get("id")
        
        # 查找对应的 binding
        tenant_bindings = [
            b for b in bindings 
            if b.get("agentId") == tenant_id
        ]
        
        # 统计会话数
        agent_dir = get_tenant_agent_dir(tenant_id)
        sessions_dir = os.path.join(agent_dir, "sessions")
        session_count = 0
        if os.path.exists(sessions_dir):
            session_count = len([f for f in os.listdir(sessions_dir) if f.endswith('.jsonl')])
        
        tenants.append({
            "tenant_id": tenant_id,
            "workspace": agent.get("workspace"),
            "model": agent.get("model", {}).get("primary") if isinstance(agent.get("model"), dict) else None,
            "bindings": tenant_bindings,
            "session_count": session_count
        })
    
    return {"ok": True, "tenants": tenants}


@APP.get("/api/tenants/{tenant_id}", dependencies=[Depends(verify_token)])
async def get_tenant(tenant_id: str):
    """获取租户详情"""
    config = get_config()
    agents_list = config.get("agents", {}).get("list", [])
    
    agent = None
    for a in agents_list:
        if a.get("id") == tenant_id:
            agent = a
            break
    
    if not agent:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    bindings = config.get("bindings", [])
    tenant_bindings = [b for b in bindings if b.get("agentId") == tenant_id]
    
    # 获取会话列表
    agent_dir = get_tenant_agent_dir(tenant_id)
    sessions_dir = os.path.join(agent_dir, "sessions")
    sessions = []
    if os.path.exists(sessions_dir):
        for f in os.listdir(sessions_dir):
            if f.endswith('.jsonl'):
                session_id = f.replace('.jsonl', '')
                sessions.append({
                    "session_id": session_id,
                    "path": os.path.join(sessions_dir, f)
                })
    
    return {
        "ok": True,
        "tenant": {
            "tenant_id": tenant_id,
            "workspace": agent.get("workspace"),
            "model": agent.get("model"),
            "bindings": tenant_bindings,
            "sessions": sessions
        }
    }


@APP.delete("/api/tenants/{tenant_id}", dependencies=[Depends(verify_token)])
async def delete_tenant(tenant_id: str):
    """删除租户"""
    if tenant_id == "main":
        raise HTTPException(status_code=400, detail="Cannot delete default tenant")
    
    config = get_config()
    
    # 移除 Agent
    agents_list = config.get("agents", {}).get("list", [])
    config["agents"]["list"] = [a for a in agents_list if a.get("id") != tenant_id]
    
    # 移除 Binding
    if "bindings" in config:
        config["bindings"] = [
            b for b in config["bindings"] 
            if b.get("agentId") != tenant_id
        ]
    
    save_config(config)
    
    return {
        "ok": True,
        "message": f"Tenant '{tenant_id}' deleted (workspace not removed)"
    }


@APP.post("/api/tenants/{tenant_id}/chat", dependencies=[Depends(verify_token)])
async def chat_with_tenant(chat: TenantChat, request: Request):
    """
    与指定租户聊天
    
    使用租户专属的 Agent 和会话隔离
    """
    tenant_id = chat.tenant_id
    
    # 验证租户存在
    config = get_config()
    agents_list = config.get("agents", {}).get("list", [])
    tenant_exists = any(a.get("id") == tenant_id for a in agents_list)
    
    if not tenant_exists:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # 生成唯一的会话 Key
    session_key = f"tenant:{tenant_id}:{uuid.uuid4().hex[:8]}"
    
    # 调用 Gateway API
    gateway_url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789")
    gateway_token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", API_TOKEN)
    
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{gateway_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {gateway_token}",
                "Content-Type": "application/json",
                "x-openclaw-agent-id": tenant_id,
                "x-openclaw-session-key": session_key
            },
            json={
                "model": "openclaw",
                "messages": [{"role": "user", "content": chat.message}],
                "stream": chat.stream
            },
            timeout=120.0
        )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Gateway error: {response.text}"
        )
    
    result = response.json()
    
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "session_key": session_key,
        "response": result
    }


@APP.post("/api/tenants/{tenant_id}/binding", dependencies=[Depends(verify_token)])
async def add_tenant_binding(
    tenant_id: str, 
    channel: str, 
    user_id: str
):
    """为租户添加渠道绑定"""
    config = get_config()
    
    # 验证租户存在
    agents_list = config.get("agents", {}).get("list", [])
    tenant_exists = any(a.get("id") == tenant_id for a in agents_list)
    
    if not tenant_exists:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # 添加 Binding
    if "bindings" not in config:
        config["bindings"] = []
    
    # 检查是否已存在
    for b in config["bindings"]:
        if b.get("agentId") == tenant_id and b.get("match", {}).get("channel") == channel:
            b["match"]["peer"] = {"id": user_id}
            break
    else:
        binding = {
            "agentId": tenant_id,
            "match": {
                "channel": channel,
                "peer": {"id": user_id}
            }
        }
        config["bindings"].append(binding)
    
    save_config(config)
    
    return {
        "ok": True,
        "message": f"Binding added for tenant {tenant_id}"
    }


@APP.get("/api/tenants/{tenant_id}/sessions", dependencies=[Depends(verify_token)])
async def list_tenant_sessions(tenant_id: str):
    """列出租户的所有会话"""
    config = get_config()
    agents_list = config.get("agents", {}).get("list", [])
    
    tenant_exists = any(a.get("id") == tenant_id for a in agents_list)
    if not tenant_exists:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    agent_dir = get_tenant_agent_dir(tenant_id)
    sessions_dir = os.path.join(agent_dir, "sessions")
    
    sessions = []
    if os.path.exists(sessions_dir):
        for f in sorted(os.listdir(sessions_dir), reverse=True):
            if f.endswith('.jsonl'):
                filepath = os.path.join(sessions_dir, f)
                # 读取会话大小
                size = os.path.getsize(filepath)
                # 读取最后一行获取更新时间
                import time
                mtime = os.path.getmtime(filepath)
                
                sessions.append({
                    "session_id": f.replace('.jsonl', ''),
                    "size_bytes": size,
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                })
    
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "sessions": sessions
    }


@APP.delete("/api/tenants/{tenant_id}/sessions/{session_id}", dependencies=[Depends(verify_token)])
async def delete_tenant_session(tenant_id: str, session_id: str):
    """删除租户的特定会话"""
    agent_dir = get_tenant_agent_dir(tenant_id)
    session_file = os.path.join(agent_dir, "sessions", f"{session_id}.jsonl")
    
    if not os.path.exists(session_file):
        raise HTTPException(status_code=404, detail="Session not found")
    
    os.remove(session_file)
    
    return {
        "ok": True,
        "message": f"Session {session_id} deleted"
    }


@APP.post("/api/tenants/{tenant_id}/config", dependencies=[Depends(verify_token)])
async def set_tenant_config(tenant_id: str, config_item: TenantConfig):
    """设置租户的配置"""
    # 写入租户的配置到 workspace
    workspace = get_tenant_workspace(tenant_id)
    
    # 根据 key 决定写入哪个文件
    if config_item.key == "SOUL":
        filename = "SOUL.md"
    elif config_item.key == "USER":
        filename = "USER.md"
    elif config_item.key == "AGENTS":
        filename = "AGENTS.md"
    else:
        # 通用配置写入 config.json
        config_path = os.path.join(workspace, "config.json")
        try:
            with open(config_path, 'r') as f:
                tenant_config = json.load(f)
        except:
            tenant_config = {}
        
        tenant_config[config_item.key] = config_item.value
        
        with open(config_path, 'w') as f:
            json.dump(tenant_config, f, indent=2)
        
        return {"ok": True, "message": f"Config {config_item.key} updated"}
    
    filepath = os.path.join(workspace, filename)
    with open(filepath, 'w') as f:
        f.write(str(config_item.value))
    
    return {"ok": True, "message": f"{filename} updated"}


@APP.get("/api/tenants/{tenant_id}/config", dependencies=[Depends(verify_token)])
async def get_tenant_config(tenant_id: str):
    """获取租户的配置"""
    workspace = get_tenant_workspace(tenant_id)
    
    config_files = {
        "SOUL": "SOUL.md",
        "USER": "USER.md", 
        "AGENTS": "AGENTS.md"
    }
    
    result = {}
    for key, filename in config_files.items():
        filepath = os.path.join(workspace, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                result[key] = f.read()
    
    # 通用配置
    config_path = os.path.join(workspace, "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            result["custom"] = json.load(f)
    
    return {
        "ok": True,
        "tenant_id": tenant_id,
        "config": result
    }


# ========== 原始 Agent 端点（保留兼容）==========
@APP.get("/api/agents", dependencies=[Depends(verify_token)])
async def list_agents():
    """列出所有 Agent（兼容旧版）"""
    return await list_tenants()


@APP.post("/api/agents", dependencies=[Depends(verify_token)])
async def create_agent(tenant: TenantCreate):
    """创建 Agent（兼容旧版）"""
    return await create_tenant(tenant)


# ========== 健康检查 ==========

@APP.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "mode": "multi-tenant"
    }


# ========== 主程序 ==========

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
╔════════════════════════════════════════════════════╗
║     OpenClaw Multi-Tenant API Server            ║
╠════════════════════════════════════════════════════╣
║  Token: {API_TOKEN[:30]:<34} ║
║  Config: {CONFIG_FILE:<39} ║
╠════════════════════════════════════════════════════╣
║  Multi-Tenant Endpoints:                         ║
║    POST   /api/tenants          创建租户          ║
║    GET    /api/tenants          列出租户          ║
║    GET    /api/tenants/{id}    获取租户详情       ║
║    DELETE /api/tenants/{id}    删除租户          ║
║    POST   /api/tenants/{id}/chat  租户聊天       ║
║    POST   /api/tenants/{id}/binding 添加绑定    ║
║    GET    /api/tenants/{id}/sessions 会话列表  ║
║    DELETE /api/tenants/{id}/sessions/{sid} 删除会话║
║    GET    /api/tenants/{id}/config 获取配置     ║
║    POST   /api/tenants/{id}/config 设置配置     ║
╚════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(APP, host="0.0.0.0", port=18888)
