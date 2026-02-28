# QQ说说回忆馆

一个震撼的本地Web应用，展示QQ说说回忆。

![Preview](preview.png)

## 效果预览

- 🌟 动态星空背景
- 🎬 炫酷启动动画
- 📜 时间隧道浏览
- 📊 回忆数据统计
- 🌙 暗色护眼主题

---

## 快速开始

### 1. 双击打开

```bash
# 或使用本地服务器
python -m http.server 8080
# 访问 http://localhost:8080
```

### 2. 准备数据

编辑 `data/moments.json`，填入你的说说数据。

---

## 数据导出工具

本项目提供3种数据获取方式：

### 方式一：QzoneExporter（推荐）

1. **下载工具**
   ```bash
   # 方式A：访问 GitHub 下载
   https://github.com/OwnGitee/QzoneExporter
   
   # 方式B：使用本项目的脚本尝试自动下载
   python qzone_exporter.py
   ```

2. **导出说说**
   - 运行 QzoneExporter
   - 登录QQ空间
   - 选择导出说说为JSON格式

3. **转换格式**
   ```bash
   # 将导出的JSON转换为回忆馆格式
   python auto_export.py convert 你的说说文件.json
   ```

### 方式二：手动整理

1. 下载CSV模板：`data/template.csv`
2. 用Excel/Numbers打开填写
3. 运行：
   ```bash
   python export_tool.py
   # 选择 2 导入CSV
   ```

### 方式三：浏览器自动化

```bash
# 需要先安装 playwright
pip install playwright
playwright install chromium

# 登录获取Cookie（会弹出浏览器窗口）
python auto_export.py login

# 转换数据
python auto_export.py convert
```

---

## 目录结构

```
qq-memory/
├── index.html              # 主页面（双击打开）
├── auto_export.py          # 自动导出工具
├── qzone_exporter.py        # QzoneExporter对接工具
├── export_tool.py          # CSV转换工具
├── README.md               # 说明文档
├── DATA_GUIDE.md           # 数据获取指南
├── data/
│   ├── moments.json        # 说说数据（替换此文件）
│   └── template.csv         # CSV模板
├── images/                 # 图片文件夹
└── QzoneExporter/          # 导出工具（需下载）
```

---

## 数据格式

```json
{
    "user": {
        "qq": "123456789",
        "nickname": "你的昵称"
    },
    "moments": [
        {
            "id": "1",
            "content": "说说内容",
            "images": ["images/photo1.jpg"],
            "created_at": "2012-03-15 14:30:00",
            "like_count": 25,
            "comment_count": 8,
            "comments": [
                {"content": "评论内容", "author": "评论者"}
            ],
            "location": "地点"
        }
    ]
}
```

---

## 字段说明

| 字段 | 必填 | 说明 |
|:-----|:----:|:-----|
| id | ✅ | 唯一标识 |
| content | ✅ | 说说文字 |
| images | ❌ | 图片列表 |
| created_at | ✅ | 发布时间 |
| like_count | ❌ | 点赞数 |
| comment_count | ❌ | 评论数 |
| comments | ❌ | 评论列表 |
| location | ❌ | 位置 |

---

## 常见问题

### Q: 导出工具下载失败？
A: 手动访问 https://github.com/OwnGitee/QzoneExporter 下载

### Q: 图片显示不出来？
A: 确保图片放在 `images/` 目录，JSON中路径正确

### Q: 想导出别人的说说？
A: 需要对方QQ空间开放权限，或使用Cookie

---

*让每一段回忆都值得被温柔以待*
