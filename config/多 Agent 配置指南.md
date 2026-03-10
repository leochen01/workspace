# 多 Agent 协作系统配置指南

## 📋 概述

本配置实现了一个**5 Agent 跨境电商协作系统**，基于 OpenClaw 架构，通过飞书进行任务触发和进度汇报。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        飞书群聊                                 │
│  老板 @大总管："分析一下露营折叠床市场，全渠道铺内容"              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    大总管 (lead)                                │
│  - 需求拆解                                                     │
│  - 使用 sessions_send 并发分发任务                               │
└──────────────┬──────────────────────────────────────────────────┘
               ↓
    ┌──────────┼──────────┬──────────┬──────────┐
    ↓          ↓          ↓          ↓          ↓
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│  VOC  │ │  GEO  │ │Reddit │ │TikTok │ │  ...  │
│分析师 │ │优化师 │ │营销   │ │编导   │ │       │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘
    ↓          ↓          ↓          ↓
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│市场研报│ │产品文 │ │评论链 │ │短视频 │
│       │ │章内容 │ │接列表 │ │文件   │
└───────┘ └───────┘ └───────┘ └───────┘
               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    大总管汇总汇报                                │
│  飞书群发送完整报告                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构

```
~/.openclaw/
├── openclaw-multi-agent.json    # 多 Agent 配置文件
├── skills/                      # 全局技能库
│   ├── nano-banana-pro/        # 生图技能
│   ├── seedance2.0/            # 视频生成技能
│   └── ...
├── workspace-lead/              # 大总管工作区
│   ├── SOUL.md                 # 人设
│   └── AGENTS.md               # 团队通讯录
├── workspace-voc/               # VOC 分析师工作区
│   ├── SOUL.md
│   └── AGENTS.md
├── workspace-geo/               # GEO 优化师工作区
│   ├── SOUL.md
│   └── AGENTS.md
├── workspace-reddit/            # Reddit 专家工作区
│   ├── SOUL.md
│   └── AGENTS.md
└── workspace-tiktok/            # TikTok 编导工作区
    ├── SOUL.md
    └── AGENTS.md
```

---

## 🔧 配置步骤

### 步骤 1：飞书应用创建

需要在**飞书开放平台**创建 5 个独立应用：

| 应用名称 | accountId | 用途 |
|----------|-----------|------|
| 跨境电商 - 大总管 | lead | 任务接收与分发 |
| 跨境电商-VOC | voc | 市场分析 |
| 跨境电商-GEO | geo | 内容优化 |
| 跨境电商-Reddit | reddit | 社区营销 |
| 跨境电商-TikTok | tiktok | 视频生成 |

#### 每个应用配置：

1. **创建应用**
   - 登录 https://open.feishu.cn/
   - 进入「应用开发」→「创建企业自建应用」
   - 应用名称：如上表

2. **获取凭证**
   - App ID (cli_xxxxx)
   - App Secret

3. **配置权限**
   - 消息读写权限
   - 群组读写权限
   - 机器人权限

4. **配置事件订阅**
   - 订阅消息事件
   - WebSocket 长连接

5. **发布应用**
   - 创建新版本
   - 提交审核（如需）
   - 发布生效

---

### 步骤 2：配置文件编辑

编辑 `~/.openclaw/openclaw-multi-agent.json`：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "connectionMode": "websocket",
      "dmPolicy": "open",
      "accounts": {
        "lead": {
          "appId": "cli_xxxxx_lead",      // 替换为你的 App ID
          "appSecret": "xxxxxxxxxxxx_lead" // 替换为你的 App Secret
        },
        "voc": { ... },
        "geo": { ... },
        "reddit": { ... },
        "tiktok": { ... }
      }
    }
  },
  "bindings": [
    {
      "agentId": "lead",
      "match": {
        "channel": "feishu",
        "accountId": "lead"
      }
    },
    // ... 其他 Agent 绑定
  ],
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["lead", "voc-analyst", "geo-optimizer", "reddit-spec", "tiktok-director"]
    }
  }
}
```

**⚠️ 重要**：
- 替换所有 `cli_xxxxx_xxx` 为你的实际 App ID
- 替换所有 `xxxxxxxxxxxx_xxx` 为你的实际 App Secret

---

### 步骤 3：激活配置

有两种方式激活多 Agent 配置：

#### 方式 A：替换主配置（推荐）

```bash
# 备份当前配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# 替换为多 Agent 配置
cp ~/.openclaw/openclaw-multi-agent.json ~/.openclaw/openclaw.json

# 重启 Gateway
openclaw gateway restart
```

#### 方式 B：使用配置参数

```bash
openclaw gateway --config ~/.openclaw/openclaw-multi-agent.json
```

---

### 步骤 4：验证配置

```bash
# 检查 Gateway 状态
openclaw gateway status

# 检查 Agent 列表
openclaw agents list

# 应该看到 5 个 Agent:
# - lead
# - voc-analyst
# - geo-optimizer
# - reddit-spec
# - tiktok-director
```

---

### 步骤 5：飞书群配置

1. **创建飞书群**
   - 群名称：「跨境电商指挥中心」
   - 添加成员：老板、运营团队

2. **邀请机器人**
   - 在群中添加 5 个飞书机器人应用
   - 确保机器人都已启用

3. **测试通信**
   - 在群里 @大总管：「测试」
   - 确认大总管能收到并响应

---

## 🚀 使用示例

### 示例 1：市场分析任务

**老板在飞书群 @大总管**：
```
分析一下露营折叠床的市场，重点看用户痛点和竞品弱点
```

**大总管自动执行**：
1. 调用 `sessions_send` 给 `voc-analyst`
2. VOC 分析师抓取亚马逊竞品差评
3. 返回痛点分析报告
4. 大总管汇总后飞书群汇报

---

### 示例 2：全渠道内容铺设

**老板在飞书群 @大总管**：
```
推一款露营折叠床，全渠道铺内容
```

**大总管自动执行**：
```python
# 并发调用多个 Agent
sessions_send(agentId="voc-analyst", message="分析露营折叠床市场痛点")
sessions_send(agentId="geo-optimizer", message="撰写独立站博客文章")
sessions_send(agentId="reddit-spec", message="Reddit 社区引流")
sessions_send(agentId="tiktok-director", message="生成 15 秒带货视频")

# 等待所有结果
# 汇总报告
# 飞书群汇报
```

---

## ⚠️ 注意事项

### 1. 工作区隔离

- 每个 Agent 有独立工作区 (`workspace-xxx/`)
- 不要混用工作区文件
- VOC 的研报不能和 Reddit 的养号记录混在一起

### 2. 技能层级

| 技能类型 | 存放位置 | 示例 |
|----------|----------|------|
| 公共技能 | `~/.openclaw/skills/` | nano-banana-pro, seedance2.0 |
| 私有技能 | `~/.openclaw/workspace-xxx/skills/` | 特定账号发布工具 |

### 3. 飞书权限

- **发布即生效**：配置变更后必须创建新版本并发布
- **明暗双轨制**：
  - 暗线：`sessions_send` 底层数据交换
  - 明线：飞书群文本进度汇报

### 4. 模型配置策略

| Agent 层级 | 推荐模型 | 原因 |
|------------|----------|------|
| 决策层 (Lead) | Claude 4.6 / Qwen3.5-Plus | 复杂调度决策 |
| 执行层 (VOC/GEO/Reddit) | Gemini 3 Flash / Kimi K2.5 | 性价比高，成本降低 90% |
| 创意层 (TikTok) | Claude 4.6 + 专用模型 | 创意质量要求高 |

---

## 🔧 故障排查

### 问题 1：机器人收不到消息

**可能原因**：
- 飞书应用未发布新版本
- WebSocket 连接断开
- bindings 配置错误

**解决方法**：
```bash
# 检查 Gateway 日志
tail -f /tmp/openclaw/openclaw-*.log

# 验证飞书配置
openclaw doctor

# 重启 Gateway
openclaw gateway restart
```

---

### 问题 2：Agent 间通信失败

**可能原因**：
- `tools.agentToAgent` 未启用
- allow 列表缺少 Agent ID

**解决方法**：
```json
{
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["lead", "voc-analyst", "geo-optimizer", "reddit-spec", "tiktok-director"]
    }
  }
}
```

---

### 问题 3：技能加载失败

**可能原因**：
- 技能放在错误目录
- 技能依赖未安装

**解决方法**：
```bash
# 检查技能目录
ls -la ~/.openclaw/skills/

# 安装缺失技能
clawhub install <skill-name>

# 重启 Gateway
openclaw gateway restart
```

---

## 📚 参考文档

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [飞书开放平台](https://open.feishu.cn/)
- [sessions_send 使用指南](https://docs.openclaw.ai/sessions_send)
- [多 Agent 架构设计](https://docs.openclaw.ai/multi-agent)

---

## 🎯 下一步

1. ✅ 完成飞书应用创建和配置
2. ✅ 替换配置文件中的 App ID/Secret
3. ✅ 重启 Gateway
4. ✅ 飞书群测试通信
5. ✅ 运行第一个多 Agent 任务

---

**配置完成日期**: 2026 年 3 月 2 日  
**配置版本**: v1.0  
**文档路径**: `/Users/chenxiangli/.openclaw/workspace/多 Agent 配置指南.md`
