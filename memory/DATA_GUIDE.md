# QQ说说数据获取指南

由于QQ官方没有提供直接导出说说功能，以下是几种常用方案：

---

## 方法一：使用现成工具（推荐）

### 1. QzoneExporter (GitHub开源)
```
https://github.com/OwnGitee/QzoneExporter
```
- 免费开源
- 支持导出说说、相册、日志
- 需要Cookie登录

### 2. QQ邮箱导出
1. 登录QQ邮箱 → 设置 → 体验室
2. 开通「QQ邮箱记事本」（自动同步说说）
3. 导出为文本/HTML

### 3. 第三方付费工具
- 「说说导出助手」
- 「Qzone历史记录导出」
- 淘宝/闲鱼搜索 "QQ说说导出"

---

## 方法二：手动整理（最简单）

### 步骤：
1. 登录QQ空间 → 我的说说
2. 按时间顺序浏览
3. 复制内容到Excel/表格
4. 使用项目中的 `export_tool.py` 转换为JSON

### Excel格式模板：

| content | created_at | like_count | comment_count | location | comments |
|---------|------------|------------|---------------|----------|----------|
| 说说内容 | 2012-03-15 14:30:00 | 25 | 8 | 地点 | 小华:真羡慕 |
| ... | ... | ... | ... | ... | ... |

---

## 方法三：浏览器开发者工具

1. 登录QQ空间
2. 打开F12 → Network
3. 翻页说说，观察网络请求
4. 分析JSON响应，复制保存

---

## 数据字段说明

| 字段 | 必填 | 说明 | 示例 |
|:-----|:----:|:-----|:-----|
| id | ✅ | 唯一标识 | "1" |
| content | ✅ | 说说文字内容 | "今天很开心" |
| images | ❌ | 图片列表 | ["img1.jpg"] |
| created_at | ✅ | 发布时间 | "2012-03-15 14:30:00" |
| like_count | ❌ | 点赞数 | 25 |
| comment_count | ❌ | 评论数 | 8 |
| comments | ❌ | 评论列表 | [{"author":"小明","content":"好"}] |
| location | ❌ | 位置 | "北京" |

---

## 快速开始

### 1. 整理你的说说

创建 `data/moments.json`，格式如下：

```json
{
    "user": {
        "qq": "123456789",
        "nickname": "你的昵称"
    },
    "moments": [
        {
            "id": "1",
            "content": "你的第一条说说内容",
            "images": [],
            "created_at": "2012-03-15 14:30:00",
            "like_count": 10,
            "comment_count": 2,
            "comments": [
                {"content": "写的真好", "author": "朋友A"}
            ],
            "location": ""
        }
    ]
}
```

### 2. 添加图片

将图片放入 `images/` 文件夹，JSON中引用：

```json
"images": ["images/photo1.jpg", "images/photo2.jpg"]
```

### 3. 运行

双击 `index.html` 打开

---

## 常见问题

### Q: 图片太多怎么管理？
A: 在 `images/` 文件夹按年份创建子文件夹，如 `2012/`、`2013/`

### Q: 有图片但显示不出来？
A: 检查路径是否正确，确保 `index.html` 和 `images/` 在同一目录

### Q: 中文字符乱码？
A: 确保JSON文件保存为 UTF-8 编码

### Q: 想导出别人的说说？
A: 需要对方QQ空间开放访问权限，或使用Cookie
