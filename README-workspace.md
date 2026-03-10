# Workspace 目录结构说明

**最后整理**: 2026-03-11

---

## 📁 核心配置文件

```
~/workspace/
├── AGENTS.md          # Agent 行为准则
├── SOUL.md            # Agent 人格定义
├── USER.md            # 用户信息
├── IDENTITY.md        # Agent 身份标识
├── MEMORY.md          # 长期记忆（仅主会话加载）
├── TOOLS.md           # 工具配置笔记
├── HEARTBEAT.md       # 心跳任务配置
└── openclaw.json      # OpenClaw 配置（在 config/ 目录）
```

---

## 📁 目录结构

### articles/ 文章管理
```
articles/
├── published/         # 已发布文章
│   ├── civilization-cost-analysis.html
│   ├── civilization-cost-analysis.docx
│   └── civilization-cost-analysis-wechat.html
├── drafts/            # 草稿文章
│   ├── 为什么有些需求会爆发 - 润色版.md
│   ├── 为什么有些需求会爆发 - 封面图.png
│   └── why-delivery-must-exist-wechat.html
└── assets/            # 文章素材
```

### wechat/ 微信公众号
```
wechat/
├── html/              # HTML 格式文章
│   └── demand-analysis-wechat.html
├── docx/              # DOCX 格式文章
│   └── demand-analysis-wechat.docx
└── 历史文章/          # 旧版文章存档
```

### config/ 配置文件
```
config/
├── openclaw.json      # OpenClaw 主配置
├── 多 Agent 配置指南.md
├── 多 Agent 配置片段.json
└── 跨境电商多 Agent 配置指南.md
```

### patents/ 专利文档
```
patents/
├── 2026-03-大模型数学规划/
├── 2026-03-电力知识库/
└── archive/           # 历史专利归档
```

### 专利 -*/ 专利工作区（临时）
```
专利 - 大模型数学规划事故预案 -20260302/
├── 专利交底书.md
├── 专利交底书.docx
└── 专利交底书 -AST 安全纠错.docx

专利 - 电力知识库专利挖掘 -20260302/
├── 专利挖掘报告.md
└── 查重分析报告.md

专利 - 电力知识库查重分析 -20260302/
└── 查重分析报告.md
```

### scripts/ 脚本工具
```
scripts/
├── utils/             # 通用工具脚本
│   ├── html2docx.py
│   ├── md2docx.py
│   ├── add-toc-to-html.js
│   └── convert_doc.py
└── 其他业务脚本/
```

### memory/ 记忆文件
```
memory/
├── 2026-02-25.md
├── 2026-02-26.md
├── 2026-03-08.md
└── 其他每日记录/
```

### 其他目录
```
docs/                  # OpenClaw 文档
downloads/             # 下载文件
games/                 # 游戏项目
projects/              # 项目文件
skills/                # 技能扩展
prompt_examples/       # Prompt 示例
prompts/               # Prompt 模板
temp/                  # 临时文件
openclaw-tech-share/   # 技术分享资料
```

---

## 📝 整理规则

### 文件归类原则
1. **公众号文章** → `articles/` 或 `wechat/`
2. **专利文档** → `patents/` 或对应专利工作区
3. **脚本工具** → `scripts/utils/`
4. **配置文件** → `config/`
5. **临时文件** → `temp/日期/`

### 命名规范
- 文章：`主题 - 版本。格式`（如：`demand-analysis-wechat.html`）
- 日期：`YYYY-MM-DD`（如：`2026-03-11`）
- 专利：`专利 - 主题 - 日期`（如：`专利 - 大模型数学规划 -20260302`）

### 清理策略
- `temp/` 目录定期清理（>7 天）
- 根目录不存放业务文件
- 已发布文章归档到 `articles/published/`

---

## 🔄 工作流程

### 公众号文章发布流程
```
1. 草稿 → articles/drafts/
2. 润色 → 生成 HTML/DOCX
3. 发布 → 移动到 articles/published/
4. 同步 → wechat/html/ 和 wechat/docx/
```

### 专利文档管理流程
```
1. 创建专利工作区 → 专利 - 主题 - 日期/
2. 撰写交底书 → 工作区内
3. 完成后 → 归档到 patents/
4. 清理临时工作区
```

---

## 📊 当前统计

| 目录 | 文件数 | 说明 |
|------|--------|------|
| articles/published/ | 3 | 已发布文章 |
| articles/drafts/ | 3 | 草稿文章 |
| wechat/ | ~15 | 公众号相关 |
| patents/ | 6 | 专利文档 |
| memory/ | ~10 | 记忆文件 |
| scripts/utils/ | 4 | 工具脚本 |

---

**备注**: 定期整理根目录，保持 workspace 整洁。
