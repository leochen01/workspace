# 跨境电商多 Agent 协作系统配置指南

**配置日期**: 2026 年 3 月 2 日  
**参考文章**: [OpenClaw 多 Agent 协作](https://mp.weixin.qq.com/s/YmqaoLZlu6_faB_pWwoRWw)

---

## 📋 系统架构

### 5 个核心 Agent

| Agent | 职责 | 推荐模型 | 工作区 |
|-------|------|----------|--------|
| **大总管 (lead)** | 需求拆解、任务分发 | Qwen3.5-Plus | `workspace-lead` |
| **VOC 市场分析师** | 竞品评价抓取、痛点提炼 | GLM-5 (性价比) | `workspace-voc` |
| **GEO 内容优化师** | 产品内容撰写、SEO 优化 | GLM-5 | `workspace-geo` |
| **Reddit 营销专家** | 社区养号、长尾流量 | GLM-5 | `workspace-reddit` |
| **TikTok 编导** | 视频脚本、生图生视频 | Qwen3.5-Plus | `workspace-tiktok` |

---

## ✅ 已完成配置

### 1. 工作区目录创建

```bash
~/.openclaw/workspace-lead/        # 大总管工作区
~/.openclaw/workspace-voc/         # VOC 分析师工作区
~/.openclaw/workspace-geo/         # GEO 优化师工作区
~/.openclaw/workspace-reddit/      # Reddit 专家工作区
~/.openclaw/workspace-tiktok/      # TikTok 编导工作区
```

### 2. Agent 人设文件

| 文件 | 路径 | 说明 |
|------|------|------|
| `AGENTS.md` | `workspace-lead/AGENTS.md` | 大总管的团队通讯录和协作手册 |
| `SOUL.md` | `workspace-lead/SOUL.md` | 大总管的人设和职责 |
| `SOUL.md` | `workspace-voc/SOUL.md` | VOC 分析师的工作规范 |
| `SOUL.md` | `workspace-geo/SOUL.md` | GEO 优化师的撰写原则 |
| `SOUL.md` | `workspace-reddit/SOUL.md` | Reddit 专家的 5 周养号 SOP |
| `SOUL.md` | `workspace-tiktok/SOUL.md` | TikTok 编导的 25 宫格分镜规范 |

### 3. 配置片段

`~/.openclaw/workspace/多 Agent 配置片段.json` - 包含完整的 agents/binding/tools 配置

---

## 🔧 待完成配置

### 步骤 1：在飞书开放平台创建 5 个独立应用

访问：https://open.feishu.cn/app

为每个 Agent 创建一个飞书应用：

| Agent | 应用名称 | 记录 App ID | 记录 App Secret |
|-------|----------|-------------|-----------------|
| lead | 跨境电商 - 大总管 | `cli_xxx_lead` | `xxx_lead` |
| voc | 跨境电商-VOC | `cli_xxx_voc` | `xxx_voc` |
| geo | 跨境电商-GEO | `cli_xxx_geo` | `xxx_geo` |
| reddit | 跨境电商-Reddit | `cli_xxx_reddit` | `xxx_reddit` |
| tiktok | 跨境电商-TikTok | `cli_xxx_tiktok` | `xxx_tiktok` |

**重要权限配置**（每个应用都需要）：
- 机器人权限
- 消息发送/接收权限
- 群组权限
- WebSocket 长连接

---

### 步骤 2：更新 openclaw.json

**⚠️ 重要**：先备份当前配置

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d)
```

**合并配置**：

1. 打开 `~/.openclaw/openclaw.json`
2. 找到 `agents.list` 数组
3. 将 `多 Agent 配置片段.json` 中的 `agents.list` 内容添加进去
4. 替换 `tools.agentToAgent.allow` 为新的 Agent 列表
5. 替换 `bindings` 数组为新的绑定配置
6. 替换 `channels.feishu.accounts` 为新的账号配置

**或者使用以下命令自动合并**（推荐）：

```bash
# 使用 jq 工具合并（需要先安装 jq）
brew install jq

# 备份原配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 合并 agents.list
jq '.agents.list += input.agents.list' \
  ~/.openclaw/openclaw.json \
  ~/.openclaw/workspace/多 Agent 配置片段.json > /tmp/openclaw_merged.json

# 替换 tools.agentToAgent
jq --slurpfile config ~/.openclaw/workspace/多 Agent 配置片段.json \
  '.tools.agentToAgent = $config[0].tools.agentToAgent' \
  /tmp/openclaw_merged.json > /tmp/openclaw_merged2.json

# 替换 bindings
jq --slurpfile config ~/.openclaw/workspace/多 Agent 配置片段.json \
  '.bindings = $config[0].bindings' \
  /tmp/openclaw_merged2.json > /tmp/openclaw_merged3.json

# 合并 channels.feishu.accounts
jq --slurpfile config ~/.openclaw/workspace/多 Agent 配置片段.json \
  '.channels.feishu.accounts = $config[0].channels.feishu.accounts' \
  /tmp/openclaw_merged3.json > ~/.openclaw/openclaw.json.new

# 替换原文件
mv ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.old
mv ~/.openclaw/openclaw.json.new ~/.openclaw/openclaw.json
```

---

### 步骤 3：填写真实的飞书 App ID 和 Secret

编辑 `~/.openclaw/openclaw.json`，找到 `channels.feishu.accounts` 部分：

```json
"accounts": {
  "lead": {
    "appId": "cli_你的真实 lead_app_id",
    "appSecret": "你的真实 lead_app_secret"
  },
  "voc": {
    "appId": "cli_你的真实 voc_app_id",
    "appSecret": "你的真实 voc_app_secret"
  },
  "geo": {
    "appId": "cli_你的真实 geo_app_id",
    "appSecret": "你的真实 geo_app_secret"
  },
  "reddit": {
    "appId": "cli_你的真实 reddit_app_id",
    "appSecret": "你的真实 reddit_app_secret"
  },
  "tiktok": {
    "appId": "cli_你的真实 tiktok_app_id",
    "appSecret": "你的真实 tiktok_app_secret"
  }
}
```

---

### 步骤 4：安装全局技能

确保以下技能已安装到全局 `~/.openclaw/skills/` 目录：

```bash
# 检查技能
clawhub list | grep -E "nano-banana-pro|seedance|tavily"

# 如未安装，执行：
clawhub install nano-banana-pro
clawhub install seedance2.0
clawhub install tavily
```

---

### 步骤 5：重启 Gateway

```bash
openclaw gateway restart
```

查看日志确认无错误：

```bash
tail -f /tmp/openclaw/openclaw-2026-03-02.log
```

---

### 步骤 6：测试多 Agent 协作

1. **创建飞书群**，将 5 个飞书机器人都拉进群

2. **在群里@大总管**，发送测试指令：

```
@大总管 分析一下露营折叠床的市场，并全渠道铺内容
```

3. **预期流程**：

```
1. 大总管收到指令
2. → sessions_send 发给 voc-analyst: "分析露营折叠床市场痛点"
3. → sessions_send 发给 geo-optimizer: "基于 VOC 数据撰写产品博客"
4. → sessions_send 发给 reddit-spec: "寻找露营装备相关老帖子"
5. → sessions_send 发给 tiktok-director: "生成露营折叠床短视频脚本"
6. 各 Agent 并行执行
7. 汇总结果，在飞书群汇报
```

---

## 🔍 故障排查

### 问题 1：Agent 收不到消息

**原因**：飞书 Bot-to-Bot 防循环机制

**解决**：
- 使用 `sessions_send` 走底层"暗线"进行数据交换
- 在群里用文本走"明线"汇报进度
- 检查 `tools.agentToAgent.enabled` 是否为 `true`

---

### 问题 2：技能加载失败

**原因**：技能放置位置错误

**解决**：
- 公共技能（生图、搜图）放 `~/.openclaw/skills/`
- 私有技能放 Agent 专属 `workspace-xxx/skills/`

---

### 问题 3：飞书配置变更不生效

**原因**：飞书应用需要发布新版本

**解决**：
1. 登录飞书开放平台
2. 进入对应应用
3. 点击"创建新版本"
4. 提交审核（通常自动通过）
5. 点击"发布"

---

### 问题 4：sessions_send 调用失败

**检查项**：
```bash
# 检查 agentToAgent 是否启用
cat ~/.openclaw/openclaw.json | jq '.tools.agentToAgent'

# 检查目标 Agent 是否在 allow 列表中
cat ~/.openclaw/openclaw.json | jq '.tools.agentToAgent.allow'

# 检查 Gateway 日志
tail -f /tmp/openclaw/openclaw-*.log | grep sessions_send
```

---

## 📊 配置验证清单

- [ ] 5 个飞书应用已创建，App ID/Secret 已记录
- [ ] `~/.openclaw/openclaw.json` 已更新并验证 JSON 格式
- [ ] 5 个工作区目录已创建，SOUL.md/AGENTS.md 已写入
- [ ] 全局技能已安装（nano-banana-pro, seedance2.0, tavily）
- [ ] Gateway 已重启，日志无错误
- [ ] 5 个飞书机器人已拉入测试群
- [ ] 在群里@大总管，收到预期响应

---

## 🎯 下一步优化

1. **模型分级配置**：
   - 决策层（lead）：使用顶级模型（Claude 4.6）
   - 执行层（voc/reddit/geo）：使用高性价比模型（GLM-5/Gemini Flash）

2. **Skill 隔离**：
   - 公共技能放全局 `~/.openclaw/skills/`
   - 私有技能（如发布工具）放各 Agent 专属目录

3. **监控与审计**：
   - 添加操作日志记录
   - 配置异常访问检测（参考专利点 8）

---

**文档版本**: v1.0  
**创建日期**: 2026 年 3 月 2 日  
**文档路径**: `/Users/chenxiangli/.openclaw/workspace/跨境电商多 Agent 配置指南.md`
