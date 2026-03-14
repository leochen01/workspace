# MEMORY.md - 长期记忆

**最后更新**: 2026 年 3 月 2 日

---

## 🎨 图片生成方法（优先使用）

**首选方案**: DashScope 通义万相 (`z-image-turbo`)

### 命令格式

```bash
cd ~/.openclaw/skills/baoyu-image-gen
npx -y bun scripts/main.ts \
  --prompt "图片描述" \
  --image /输出路径.png \
  --provider dashscope
```

### 示例

```bash
npx -y bun scripts/main.ts \
  --prompt "一只可爱的橘猫，毛茸茸的，坐在阳光下，高清摄影风格，4K 画质" \
  --image /tmp/cat.png \
  --provider dashscope
```

### 优势

- ✅ 速度快（~30 秒生成）
- ✅ 质量高（1440x1440 默认分辨率）
- ✅ API 密钥已配置 (`DASHSCOPE_API_KEY`)
- ✅ 中文提示词支持好
- ✅ 无需额外登录/授权

### 备选方案

如果 DashScope 失败，可尝试：
1. `--provider google` (需要 GOOGLE_API_KEY)
2. `--provider openai` (需要 OPENAI_API_KEY)

### 可用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--prompt` | 图片描述（支持中文） | "一只可爱的猫咪" |
| `--image` | 输出文件路径 | `/tmp/cat.png` |
| `--provider` | 指定提供商 | `dashscope` |
| `--ar` | 宽高比 | `16:9`, `1:1`, `4:3` |
| `--size` | 尺寸 | `1024x1024` |
| `--quality` | 质量 | `normal`, `2k` |
| `--n` | 生成数量 | `1`, `2`, `4` |

---

## 📋 正在进行的项目

### 1. 专利撰写（2026-03-02）

**已完成**:
- ✅ 8 个专利创新点挖掘（大模型 + 电力调度）
- ✅ 专利查重分析报告
- ✅ 专利点 2 交底书撰写完成（角色 - 场景双维度权限控制）

**待完成**:
- [ ] 专利点 8 交底书（异常访问检测）
- [ ] 正式查新检索（委托代理机构）

### 2. 跨境电商多 Agent 系统（2026-03-02）

**已完成**:
- ✅ 5 个工作区目录创建
- ✅ 5 个 Agent 的 SOUL.md/AGENTS.md 编写
- ✅ openclaw.json 配置片段
- ✅ 完整配置指南文档

**待完成**:
- [ ] 飞书开放平台创建 5 个应用
- [ ] 合并配置到 openclaw.json
- [ ] 填写真实 App ID/Secret
- [ ] 重启 Gateway 并测试

---

## 🔧 工具偏好

| 工具 | 偏好设置 | 说明 |
|------|----------|------|
| 图片生成 | DashScope z-image-turbo | 优先使用，速度快质量好 |
| 专利撰写 | patent-disclosure-writer | 已安装并修复 |
| 多 Agent | OpenClaw sessions_send | 飞书路由 + 异步通信 |

---

## 📝 重要配置

### DashScope API

```bash
DASHSCOPE_API_KEY=sk-89cec37a4f2b4a2d9d907ee5d46c0636
DASHSCOPE_IMAGE_MODEL=z-image-turbo
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
```

### 专利工作区

```
~/.openclaw/workspace/专利 - 大模型数学规划事故预案 -20260302/
├── 专利交底书.md (44KB)
```

### 多 Agent 工作区

```
~/.openclaw/workspace-lead/         # 大总管
~/.openclaw/workspace-voc/          # VOC 分析师
~/.openclaw/workspace-geo/          # GEO 优化师
~/.openclaw/workspace-reddit/       # Reddit 专家
~/.openclaw/workspace-tiktok/       # TikTok 编导
```

---

**备注**: 本文档记录重要决策、配置和偏好，跨会话持久化。
