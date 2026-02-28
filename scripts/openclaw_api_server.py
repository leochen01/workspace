#!/usr/bin/env python3
"""
OpenClaw Agent Management API Server
包装 OpenClaw CLI，提供 HTTP API 进行 Agent 创建和配置
"""

import os
import sys
import json
import subprocess
import argparse
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 配置
PORT = 18888
TOKEN = os.environ.get("OPENCLAW_API_TOKEN", "your-secret-token")
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")
CONFIG_FILE = os.path.join(OPENCLAW_DIR, "openclaw.json")

# 全局变量存储服务
server = None


def run_cli(args, cwd=None):
    """执行 OpenClaw CLI 命令"""
    cmd = ["openclaw"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Command timeout", "code": -1}
    except Exception as e:
        return {"ok": False, "error": str(e), "code": -1}


def get_config():
    """读取配置文件"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {}


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


class APIHandler(BaseHTTPRequestHandler):
    """API 请求处理"""
    
    def log_message(self, format, *args):
        """日志"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def check_auth(self):
        """检查认证"""
        auth = self.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return False
        token = auth[7:]
        return token == TOKEN
    
    def require_auth(self):
        """需要认证"""
        if not self.check_auth():
            self.send_json({"error": "Unauthorized"}, 401)
            return False
        return True
    
    def parse_body(self):
        """解析请求体"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode())
        return {}
    
    # ========== Agent 管理 ==========
    
    def do_get_agents(self):
        """获取所有 Agent"""
        if not self.require_auth():
            return
        
        result = run_cli(["agents", "list", "--json"])
        if result["ok"]:
            try:
                data = json.loads(result["stdout"])
                self.send_json({"ok": True, "agents": data})
            except:
                self.send_json({"ok": True, "agents": [], "raw": result["stdout"]})
        else:
            # 尝试直接读取配置
            config = get_config()
            agents = config.get("agents", {})
            self.send_json({"ok": True, "agents": agents})
    
    def do_create_agent(self):
        """创建 Agent"""
        if not self.require_auth():
            return
        
        body = self.parse_body()
        name = body.get("name")
        workspace = body.get("workspace", f"~/.openclaw/workspace-{name}")
        
        if not name:
            self.send_json({"error": "name is required"}, 400)
            return
        
        # 展开路径
        workspace = os.path.expanduser(workspace)
        
        # 创建工作目录
        os.makedirs(workspace, exist_ok=True)
        
        # 执行 CLI
        result = run_cli(["agents", "add", name, "--workspace", workspace, "--non-interactive"])
        
        if result["ok"]:
            self.send_json({
                "ok": True, 
                "agent": name,
                "workspace": workspace,
                "message": f"Agent '{name}' created successfully"
            })
        else:
            self.send_json({
                "ok": False,
                "error": result.get("stderr", result.get("error", "Unknown error"))
            }, 500)
    
    def do_delete_agent(self):
        """删除 Agent"""
        if not self.require_auth():
            return
        
        body = self.parse_body()
        name = body.get("name")
        
        if not name:
            self.send_json({"error": "name is required"}, 400)
            return
        
        result = run_cli(["agents", "delete", name])
        
        if result["ok"]:
            self.send_json({"ok": True, "message": f"Agent '{name}' deleted"})
        else:
            self.send_json({"ok": False, "error": result.get("stderr", "Unknown error")}, 500)
    
    # ========== 模型配置 ==========
    
    def do_get_models(self):
        """获取可用模型"""
        if not self.require_auth():
            return
        
        result = run_cli(["models"])
        
        if result["ok"]:
            self.send_json({"ok": True, "models": result["stdout"]})
        else:
            # 从配置读取
            config = get_config()
            providers = config.get("models", {}).get("providers", {})
            self.send_json({"ok": True, "providers": providers})
    
    def do_set_model(self):
        """设置 Agent 模型"""
        if not self.require_auth():
            return
        
        body = self.parse_body()
        model = body.get("model")
        agent = body.get("agent", "defaults")
        
        if not model:
            self.send_json({"error": "model is required"}, 400)
            return
        
        # 设置模型
        if agent == "defaults":
            result = run_cli(["config", "set", "agents.defaults.model.primary", model])
        else:
            result = run_cli(["config", "set", f"agents.list.{agent}.model.primary", model])
        
        if result["ok"]:
            self.send_json({"ok": True, "model": model, "message": "Model updated"})
        else:
            self.send_json({"ok": False, "error": result.get("stderr", "Unknown error")}, 500)
    
    # ========== API 密钥配置 ==========
    
    def do_set_api_key(self):
        """设置 API 密钥"""
        if not self.require_auth():
            return
        
        body = self.parse_body()
        provider = body.get("provider")
        api_key = body.get("api_key")
        
        if not provider or not api_key:
            self.send_json({"error": "provider and api_key are required"}, 400)
            return
        
        # 保存到 secrets
        result = run_cli(["secrets", "add", f"{provider}-api-key", api_key])
        
        if result["ok"]:
            self.send_json({"ok": True, "message": f"API key for {provider} saved"})
        else:
            # 直接修改配置
            config = get_config()
            if "models" not in config:
                config["models"] = {}
            if "providers" not in config["models"]:
                config["models"]["providers"] = {}
            if provider not in config["models"]["providers"]:
                config["models"]["providers"][provider] = {}
            config["models"]["providers"][provider]["apiKey"] = api_key
            save_config(config)
            self.send_json({"ok": True, "message": f"API key for {provider} saved to config"})
    
    def do_get_providers(self):
        """获取已配置的模型提供商"""
        if not self.require_auth():
            return
        
        config = get_config()
        providers = config.get("models", {}).get("providers", {})
        
        # 隐藏密钥
        for name, data in providers.items():
            if "apiKey" in data and data["apiKey"]:
                data["apiKey"] = "***" + data["apiKey"][-4:] if len(data.get("apiKey", "")) > 4 else "***"
        
        self.send_json({"ok": True, "providers": providers})
    
    # ========== 技能配置 ==========
    
    def do_list_skills(self):
        """列出已安装技能"""
        if not self.require_auth():
            return
        
        result = run_cli(["skills", "list"])
        
        if result["ok"]:
            self.send_json({"ok": True, "skills": result["stdout"]})
        else:
            self.send_json({"ok": True, "skills": [], "error": result.get("stderr")})
    
    def do_install_skill(self):
        """安装技能"""
        if not self.require_auth():
            return
        
        body = self.parse_body()
        skill_name = body.get("name")
        
        if not skill_name:
            self.send_json({"error": "name is required"}, 400)
            return
        
        result = run_cli(["skills", "install", skill_name])
        
        if result["ok"]:
            self.send_json({"ok": True, "message": f"Skill '{skill_name}' installed"})
        else:
            self.send_json({"ok": False, "error": result.get("stderr", "Unknown error")}, 500)
    
    # ========== 配置管理 ==========
    
    def do_get_config(self):
        """获取配置"""
        if not self.require_auth():
            return
        
        config = get_config()
        
        # 隐藏敏感信息
        if "models" in config and "providers" in config["models"]:
            for name, data in config["models"]["providers"].items():
                if "apiKey" in data and data["apiKey"]:
                    data["apiKey"] = "***"
        
        self.send_json({"ok": True, "config": config})
    
    def do_set_config(self):
        """设置配置项"""
        if not self.require_auth():
            return
        
        body = self.parse_body()
        path = body.get("path")
        value = body.get("value")
        
        if not path or value is None:
            self.send_json({"error": "path and value are required"}, 400)
            return
        
        # 转换为 CLI 参数
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        result = run_cli(["config", "set", path, str(value)])
        
        if result["ok"]:
            self.send_json({"ok": True, "message": f"Config '{path}' updated"})
        else:
            self.send_json({"ok": False, "error": result.get("stderr", "Unknown error")}, 500)
    
    # ========== 状态 ==========
    
    def do_status(self):
        """获取状态"""
        if not self.require_auth():
            return
        
        result = run_cli(["status"])
        
        self.send_json({
            "ok": True,
            "status": result["stdout"] if result["ok"] else result.get("stderr", "Unknown")
        })
    
    # ========== 路由 ==========
    
    def do_GET(self):
        """处理 GET 请求"""
        path = urlparse(self.path).path
        
        if path == "/api/agents":
            self.do_get_agents()
        elif path == "/api/models":
            self.do_get_models()
        elif path == "/api/providers":
            self.do_get_providers()
        elif path == "/api/skills":
            self.do_list_skills()
        elif path == "/api/config":
            self.do_get_config()
        elif path == "/api/status":
            self.do_status()
        elif path == "/health":
            self.send_json({"status": "ok"})
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        """处理 POST 请求"""
        path = urlparse(self.path).path
        
        if path == "/api/agents":
            self.do_create_agent()
        elif path == "/api/agents/delete":
            self.do_delete_agent()
        elif path == "/api/model":
            self.do_set_model()
        elif path == "/api/api-key":
            self.do_set_api_key()
        elif path == "/api/skills/install":
            self.do_install_skill()
        elif path == "/api/config":
            self.do_set_config()
        else:
            self.send_json({"error": "Not found"}, 404)


def main():
    global server
    
    parser = argparse.ArgumentParser(description="OpenClaw API Server")
    parser.add_argument("--port", type=int, default=PORT, help="Server port")
    parser.add_argument("--token", default=TOKEN, help="API token")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    args = parser.parse_args()
    
    # 更新全局配置
    globals()["PORT"] = args.port
    globals()["TOKEN"] = args.token
    
    server = HTTPServer((args.host, args.port), APIHandler)
    
    print(f"""
╔════════════════════════════════════════════════════╗
║     OpenClaw Agent Management API Server          ║
╠════════════════════════════════════════════════════╣
║  Port:     {args.port:<38} ║
║  Token:    {args.token[:20]:<38} ║
║  Config:   {CONFIG_FILE:<38} ║
╠════════════════════════════════════════════════════╣
║  Endpoints:                                      ║
║    GET  /api/agents     - List agents            ║
║    POST /api/agents     - Create agent           ║
║    GET  /api/models     - List models            ║
║    POST /api/model      - Set agent model        ║
║    POST /api/api-key    - Set API key            ║
║    GET  /api/skills     - List skills            ║
║    POST /api/skills/install - Install skill      ║
║    GET  /api/config     - Get config             ║
║    POST /api/config     - Set config             ║
║    GET  /api/status     - Get status             ║
║  Health:     /health                              ║
╚════════════════════════════════════════════════════╝
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
