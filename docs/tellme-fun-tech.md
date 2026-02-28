# tellme.fun - 技术架构设计

> 版本：v1.0 | 基于确认的配置

---

## 一、技术栈确认

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| 框架 | Next.js 14 (App Router) | 全栈能力，静态/动态兼顾 |
| 语言 | TypeScript | 类型安全 |
| UI | Tailwind CSS + shadcn/ui | 极简风格，快速开发 |
| 数据库 | SQLite | 免费、零配置、文件存储 |
| ORM | Prisma | 类型安全的数据库操作 |
| 认证 | NextAuth.js | 开源、支持多种provider |
| 编辑器 | @uiw/react-md-editor | Markdown富文本 |
| 部署 | 私有服务器 (Node.js) | pm2 + Nginx |

---

## 二、项目结构

```
tellme.fun/
├── prisma/
│   └── schema.prisma          # 数据库模型
├── src/
│   ├── app/
│   │   ├── (site)/           # 前端页面
│   │   │   ├── page.tsx      # 首页
│   │   │   ├── work/
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx  # 作品详情
│   │   │   └── layout.tsx   # 前端布局
│   │   │
│   │   ├── (admin)/          # 管理后台
│   │   │   ├── admin/
│   │   │   │   ├── page.tsx      # 仪表盘
│   │   │   │   ├── profile/
│   │   │   │   │   └── page.tsx  # 个人资料
│   │   │   │   ├── links/
│   │   │   │   │   └── page.tsx  # 社交链接
│   │   │   │   └── works/
│   │   │   │       ├── page.tsx  # 作品列表
│   │   │   │       └── [id]/
│   │   │   │           └── page.tsx  # 作品编辑
│   │   │   ├── layout.tsx   # 后台布局(含侧边栏)
│   │   │   └── login/
│   │   │       └── page.tsx  # 登录页
│   │   │
│   │   ├── api/              # API
│   │   │   ├── auth/
│   │   │   │   └── [...nextauth]/
│   │   │   │       └── route.ts
│   │   │   ├── profile/
│   │   │   │   └── route.ts
│   │   │   ├── links/
│   │   │   │   └── route.ts
│   │   │   └── works/
│   │   │       └── route.ts
│   │   │
│   │   ├── layout.tsx       # 根布局
│   │   └── globals.css      # 全局样式
│   │
│   ├── components/
│   │   ├── ui/              # shadcn组件
│   │   ├── site/            # 前端组件
│   │   │   ├── ProfileCard.tsx
│   │   │   ├── SocialLinks.tsx
│   │   │   ├── WorkCard.tsx
│   │   │   └── WorkGrid.tsx
│   │   └── admin/           # 后台组件
│   │       ├── Sidebar.tsx
│   │       ├── ProfileForm.tsx
│   │       ├── LinksManager.tsx
│   │       └── WorkEditor.tsx
│   │
│   ├── lib/
│   │   ├── db.ts            # Prisma客户端
│   │   ├── auth.ts          # NextAuth配置
│   │   └── utils.ts         # 工具函数
│   │
│   └── types/
│       └── index.ts         # 类型定义
│
├── public/                   # 静态资源
│   ├── images/              # 上传的图片
│   └── favicon.ico
│
├── .env                     # 环境变量
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 三、数据库模型 (Prisma Schema)

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

// 个人资料（单条记录）
model Profile {
  id          String   @id @default(cuid())
  name        String
  avatar      String?  // 头像URL
  title       String?
  bio         String?  // 个人简介
  location    String?
  
  // 主题
  primaryColor    String @default("#000000")
  backgroundColor String @default("#ffffff")
  fontFamily      String @default("default")
  
  // SEO
  seoTitle       String?
  seoDescription String?
  
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

// 社交链接
model SocialLink {
  id          String   @id @default(cuid())
  platform    String   // github, bilibili, xiaohongshu 等
  label       String
  url         String
  icon        String?  // 自定义图标
  visible     Boolean  @default(true)
  sortOrder   Int      @default(0)
  
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

// 作品
model Work {
  id          String   @id @default(cuid())
  type        String   // article, video, software, tool
  title       String
  slug        String   @unique
  description String?  // 简介
  coverImage  String?  // 封面图
  content     String?  // Markdown内容
  
  tags        String?  // 逗号分隔
  category    String?
  
  // 链接
  demoUrl     String?
  sourceUrl   String?
  downloadUrl String?
  articleUrl  String?
  
  publishDate DateTime?
  visible     Boolean  @default(false)
  featured    Boolean  @default(false)
  
  views       Int      @default(0)
  
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

// 用户（后台登录）
model User {
  id       String @id @default(cuid())
  email    String @unique
  password String // 加密后的密码
  name     String?
  
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

---

## 四、环境变量 (.env)

```bash
# 数据库
DATABASE_URL="file:./dev.db"

# NextAuth
NEXTAUTH_URL="https://tellme.fun"
NEXTAUTH_SECRET="your-secret-key-generate-with-openssl"

# 管理员账号
ADMIN_EMAIL="admin@tellme.fun"
ADMIN_PASSWORD="your-password"  # 会加密存储
```

---

## 五、部署配置

### PM2 配置 (ecosystem.config.js)

```javascript
module.exports = {
  apps: [{
    name: 'tellme-fun',
    script: 'npm',
    args: 'start',
    cwd: '/var/www/tellme.fun',
    instances: 1,
    exec_mode: 'cluster',
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
```

### Nginx 配置

```nginx
server {
    server_name tellme.fun;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 静态文件缓存
    location /images {
        alias /var/www/tellme.fun/public/images;
        expires 30d;
    }
}
```

---

## 六、密码保护实现

### 认证流程

```
用户访问 /admin
       ↓
检查 Session
       ↓
有Session → 进入后台
无Session → 重定向到 /admin/login
       ↓
登录表单（邮箱+密码）
       ↓
验证成功 → 创建Session → 跳转后台
验证失败 → 显示错误
```

### 安全措施

| 措施 | 说明 |
|------|------|
| 密码加密 | bcrypt 哈希存储 |
| Session | NextAuth JWT |
| 登录限制 | 5次错误后锁定5分钟 |
| HTTPS | 私有服务器需配置SSL |

---

## 七、开发启动命令

```bash
# 1. 安装依赖
npm install

# 2. 初始化数据库
npx prisma generate
npx prisma db push

# 3. 创建管理员账号
# 首次运行会自动创建默认管理员

# 4. 开发模式
npm run dev

# 5. 生产构建
npm run build
npm start
```

---

## 八、接下来

1. **确认启动** → 我开始创建项目脚手架
2. **调整** → 有需求改动PRD

要现在启动项目搭建吗？