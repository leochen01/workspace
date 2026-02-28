#!/usr/bin/env python3
"""
OpenClaw Agent Management API Server (FastAPI Version)
更完整的 API 实现，支持异步、参数验证、错误处理
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse

# ========== 配置 ==========
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
APP = FastAPI(title="OpenClaw Agent API", version="1.0.0")

# API 密钥验证
API_TOKEN = os.environ.get("OPENCLAW_API_TOKEN", "your-secret-token")


# ========== Pydantic 模型 ==========

class AgentCreate(BaseModel):
    name: str
    workspace: Optional[str] = None
    model: Optional[str] = None


class AgentDelete(BaseModel):
    name: str


class ModelSet(BaseModel):
    model: str
    agent: str = "defaults"


class ApiKeySet(BaseModel):
    provider: str
    api_key: str


class SkillInstall(BaseModel):
    name: str


class ConfigSet(BaseModel):
    path: str
    value: Any


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


# ========== CLI 封装 ==========

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


# ========== Agent 端点 ==========

@APP.get("/api/agents", dependencies=[Depends(verify_token)])
async def list_agents():
    """列出所有 Agent"""
    result = run_cli(["agents", "list", "--json"])
    
    if result["ok"]:
        try:
            agents = json.loads(result["stdout"])
            return {"ok": True, "agents": agents}
        except json.JSONDecodeError:
            return {"ok": True, "agents": [], "raw": result["stdout"]}
    
    # 回退到读取配置
    config = get_config()
    return {"ok": True, "agents": config.get("agents", {})}


@APP.post("/api/agents", dependencies=[Depends(verify_token)])
async def create_agent(agent: AgentCreate):
    """创建新 Agent"""
    if not agent.name:
        raise HTTPException(status_code=400, detail="name is required")
    
    workspace = agent.workspace or f"~/.openclaw/workspace-{agent.name}"
    workspace = os.path.expanduser(workspace)
    
    # 创建工作目录
    os.makedirs(workspace, exist_ok=True)
    
    # 执行 CLI
    args = ["agents", "add", agent.name, "--workspace", workspace, "--non-interactive"]
    if agent.model:
        args.extend(["--model", agent.model])
    
    result = run_cli(args)
    
    if result["ok"]:
        return {
            "ok": True,
            "agent": agent.name,
            "workspace": workspace,
            "model": agent.model,
            "message": f"Agent '{agent.name}' created successfully"
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("stderr", "Unknown error"))


@APP.delete("/api/agents", dependencies=[Depends(verify_token)])
async def delete_agent(agent: AgentDelete):
    """删除 Agent"""
    if not agent.name:
        raise HTTPException(status_code=400, detail="name is required")
    
    # 检查是否是默认 agent
    if agent.name == "main":
        raise HTTPException(status_code=400, detail="Cannot delete default agent")
    
    result = run_cli(["agents", "delete", agent.name])
    
    if result["ok"]:
        return {"ok": True, "message": f"Agent '{agent.name}' deleted"}
    else:
        raise HTTPException(status_code=500, detail=result.get("stderr", "Unknown error"))


# ========== 模型端点 ==========

@APP.get("/api/models", dependencies=[Depends(verify_token)])
async def list_models():
    """列出可用模型"""
    result = run_cli(["models"])
    
    if result["ok"]:
        return {"ok": True, "models": result["stdout"]}
    
    # 回退到配置
    config = get_config()
    providers = config.get("models", {}).get("providers", {})
    return {"ok": True, "providers": providers}


@APP.post("/api/model", dependencies=[Depends(verify_token)])
async def set_model(data: ModelSet):
    """设置 Agent 模型"""
    if not data.model:
        raise HTTPException(status_code=400, detail="model is required")
    
    if data.agent == "defaults":
        result = run_cli(["config", "set", "agents.defaults.model.primary", data.model])
    else:
        result = run_cli(["config", "set", f"agents.list.{data.agent}.model.primary", data.model])
    
    if result["ok"]:
        return {"ok": True, "model": data.model, "agent": data.agent}
    else:
        raise HTTPException(status_code=500, detail=result.get("stderr", "Unknown error"))


# ========== API 密钥端点 ==========

@APP.get("/api/providers", dependencies=[Depends(verify_token)])
async def list_providers():
    """列出已配置的模型提供商"""
    config = get_config()
    providers = config.get("models", {}).get("providers", {})
    
    # 隐藏密钥
    for name, data in providers.items():
        if "apiKey" in data and data["apiKey"]:
            key = data["apiKey"]
            data["apiKey"] = "***" + key[-4:] if len(key) > 4 else "***"
    
    return {"ok": True, "providers": providers}


@APP.post("/api/api-key", dependencies=[Depends(verify_token)])
async def set_api_key(data: ApiKeySet):
    """设置 API 密钥"""
    if not data.provider or not data.api_key:
        raise HTTPException(status_code=400, detail="provider and api_key are required")
    
    # 尝试保存到 secrets
    result = run_cli(["secrets", "add", f"{data.provider}-api-key", data.api_key])
    
    if result["ok"]:
        return {"ok": True, "message": f"API key for {data.provider} saved to secrets"}
    
    # 回退到直接修改配置
    config = get_config()
    
    if "models" not in config:
        config["models"] = {}
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}
    if data.provider not in config["models"]["providers"]:
        config["models"]["providers"][data.provider] = {}
    
    config["models"]["providers"][data.provider]["apiKey"] = data.api_key
    save_config(config)
    
    return {"ok": True, "message": f"API key for {data.provider} saved to config"}


# ========== 技能端点 ==========

@APP.get("/api/skills", dependencies=[Depends(verify_token)])
async def list_skills():
    """列出已安装技能"""
    result = run_cli(["skills", "list"])
    
    if result["ok"]:
        return {"ok": True, "skills": result["stdout"]}
    return {"ok": True, "skills": [], "error": result.get("stderr")}


@APP.post("/api/skills/install", dependencies=[Depends(verify_token)])
async def install_skill(skill: SkillInstall):
    """安装技能"""
    if not skill.name:
        raise HTTPException(status_code=400, detail="name is required")
    
    result = run_cli(["skills", "install", skill.name])
    
    if result["ok"]:
        return {"ok": True, "message": f"Skill '{skill.name}' installed"}
    else:
        raise HTTPException(status_code=500, detail=result.get("stderr", "Unknown error"))


# ========== 配置端点 ==========

@APP.get("/api/config", dependencies=[Depends(verify_token)])
async def get_config_api():
    """获取完整配置"""
    config = get_config()
    
    # 隐藏敏感信息
    if "models" in config and "providers" in config["models"]:
        for name, data in config["models"]["providers"].items():
            if "apiKey" in data and data["apiKey"]:
                data["apiKey"] = "***"
    
    return {"ok": True, "config": config}


@APP.post("/api/config", dependencies=[Depends(verify_token)])
async def set_config_api(data: ConfigSet):
    """设置配置项"""
    if not data.path or data.value is None:
        raise HTTPException(status_code=400, detail="path and value are required")
    
    value_str = json.dumps(data.value) if isinstance(data.value, (dict, list)) else str(data.value)
    
    result = run_cli(["config", "set", data.path, value_str])
    
    if result["ok"]:
        return {"ok": True, "message": f"Config '{data.path}' updated"}
    else:
        raise HTTPException(status_code=500, detail=result.get("stderr", "Unknown error"))


# ========== 状态端点 ==========

@APP.get("/api/status", dependencies=[Depends(verify_token)])
async def get_status():
    """获取 OpenClaw 状态"""
    result = run_cli(["status"])
    
    return {
        "ok": result["ok"],
        "status": result["stdout"] if result["ok"] else result.get("stderr", "Unknown")
    }


# ========== 健康检查 ==========

@APP.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


# ========== 主程序 ==========

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
╔════════════════════════════════════════════════════╗
║     OpenClaw Agent Management API (FastAPI)       ║
╠════════════════════════════════════════════════════╣
║  Token: {API_TOKEN[:30]:<34} ║
║  Config: {CONFIG_FILE:<39} ║
╚════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(APP, host="0.0.0.0", port=18888)
