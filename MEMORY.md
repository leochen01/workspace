# MEMORY.md

## Agents
- **coder agent** 已配置启用，使用 Qwen Coder 模型
- **main agent** 使用 MiniMax M2.1 模型

## Skills
- 常用已安装：Feishu 系列、coding-agent、tmux、nano-pdf、smart-illustrator
- **smart-illustrator**：使用 MiniMax API 生成文章配图
  - 默认 provider: minimax
  - 默认模型: image-01
  - 默认尺寸: 2K (2048px)
  - 默认比例: 16:9
  - 配置文件: `~/.openclaw/workspace/.smart-illustrator/config.json`

## API Keys
- **MiniMax API Key**: (见 ~/.openclaw/workspace/.smart-illustrator/config.json)
- **GitHub Token**: (已配置在 git remote 中)

## Workflows
- 飞书用户文章需求：先写作 → 用 MiniMax 生成图片
- 图片生成默认使用 MiniMax API (minimax-portal/MiniMax-M2.1 或 image-01)
- coder agent 测试命令：`openclaw agent --agent coder --message "任务描述"`

## Notes
- 工作目录：~/.openclaw/workspace
- 代理配置：~/.openclaw/openclaw.json
