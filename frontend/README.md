# Frontend - Nuxt.js Application

前端应用，使用 Nuxt.js 3 框架构建。

## 技术栈

- **框架**: Nuxt.js 3
- **UI 框架**: Vue 3 (Composition API)
- **状态管理**: Pinia
- **样式**: Tailwind CSS
- **HTTP 客户端**: Fetch API
- **包管理**: pnpm

## 快速开始

### 安装依赖

```bash
pnpm install
```

### 环境配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

环境变量说明：
- `NUXT_PUBLIC_PYTHON_API_URL`: Python 服务地址（默认: http://localhost:8000）
- `NUXT_PUBLIC_NODE_API_URL`: Node.js 服务地址（默认: http://localhost:3000）
- `NUXT_PUBLIC_RUST_API_URL`: Rust 服务地址（默认: http://localhost:8080）

### 启动开发服务器

```bash
pnpm dev
```

前端将在 `http://localhost:3000` 启动（Nuxt 默认端口）。

### 构建生产版本

```bash
pnpm build
pnpm preview
```

## 项目结构

```
frontend/
├── pages/              # 页面路由
│   ├── index.vue       # 首页
│   ├── python-items.vue  # Python 服务示例页面
│   ├── node-items.vue    # Node.js 服务示例页面
│   └── rust-items.vue    # Rust 服务示例页面
├── components/         # 组件
│   └── ServiceCard.vue  # 服务卡片组件
├── composables/        # 组合式函数
│   └── useApi.ts       # API 调用封装
├── api/                # API 封装
│   ├── python.ts       # Python 服务 API
│   ├── node.ts         # Node.js 服务 API
│   └── rust.ts         # Rust 服务 API
├── stores/             # Pinia 状态管理（待使用）
├── assets/             # 静态资源
│   └── css/
│       └── main.css    # 全局样式
├── .env.example        # 环境变量示例
├── nuxt.config.ts      # Nuxt 配置
├── tailwind.config.js  # Tailwind CSS 配置
├── postcss.config.js   # PostCSS 配置
└── package.json
```

## 页面说明

### 首页 (`/`)
- 展示三个后端服务的导航卡片
- 点击卡片跳转到对应的示例页面

### Python Items 页面 (`/python-items`)
- 调用 Python FastAPI 服务的 Items API
- 实现完整的 CRUD 功能

### Node Items 页面 (`/node-items`)
- 调用 Node.js Nest.js 服务的 Items API
- 实现完整的 CRUD 功能

### Rust Items 页面 (`/rust-items`)
- 调用 Rust Axum 服务的 Items API
- 实现完整的 CRUD 功能

## API 调用

所有 API 调用都通过 `composables/useApi.ts` 进行统一封装，使用 Fetch API。

### 使用示例

```typescript
import { getItems, createItem } from '~/api/python';

// 获取所有 items
const response = await getItems();
const items = response.data;

// 创建 item
const newItem = await createItem({
  name: 'Test Item',
  description: 'Description',
  price: 99.99,
});
```

## 开发指南

### 代码规范

- 使用 TypeScript
- 遵循 Vue 3 Composition API 最佳实践
- 使用 Tailwind CSS 进行样式设计
- 组件使用 `<script setup>` 语法

### 路由

Nuxt.js 使用文件系统路由，`pages/` 目录下的文件自动生成路由。

### 环境变量

使用 `useRuntimeConfig()` 访问环境变量：

```typescript
const config = useRuntimeConfig();
const apiUrl = config.public.pythonApiUrl;
```

## 注意事项

1. 确保三个后端服务已启动
2. 确保 MongoDB 已运行
3. 如果后端服务运行在不同端口，需要更新 `.env` 文件
