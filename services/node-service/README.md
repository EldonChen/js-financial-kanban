# Node.js Nest.js Service

Node.js 后端服务，使用 Bun + Nest.js 框架和 MongoDB 数据库。

## 技术栈

- **运行时**: Bun 1.3+
- **框架**: Nest.js 10.x
- **数据库**: MongoDB
- **数据库驱动**: Mongoose 8.x
- **数据验证**: class-validator + class-transformer
- **包管理**: Bun
- **测试框架**: Vitest 4.x + @nestjs/testing

## 快速开始

### 安装依赖

```bash
# 使用 Bun 安装依赖
bun install
```

### 环境配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 运行测试

```bash
# 运行所有测试
bun run test

# 监视模式运行测试
bun run test:watch

# 运行测试并生成覆盖率报告
bun run test:cov

# 运行集成测试
bun run test:integration
```

### 启动服务

```bash
# 开发模式（自动重载）
bun run start:dev

# 生产模式
bun run build
bun run start:prod
```

### API 文档

启动服务后，访问：
- API 基础路径: http://localhost:3000/api/v1

## 项目结构

```
node-service/
├── src/
│   ├── main.ts              # 应用入口
│   ├── app.module.ts        # 根模块
│   ├── config/              # 配置模块
│   │   └── app-config.module.ts
│   ├── common/              # 通用模块
│   │   ├── filters/         # 异常过滤器
│   │   │   └── http-exception.filter.ts
│   │   └── interceptors/    # 拦截器
│   │       └── transform.interceptor.ts
│   └── items/               # Items 模块
│       ├── items.controller.ts  # 控制器
│       ├── items.service.ts     # 服务层
│       ├── items.module.ts      # 模块定义
│       ├── items.controller.spec.ts  # Controller 测试
│       ├── items.service.spec.ts     # Service 测试
│       ├── items.integration.spec.ts  # 集成测试
│       ├── schemas/         # Mongoose Schema
│       │   └── item.schema.ts
│       └── dto/             # 数据传输对象
│           ├── create-item.dto.ts
│           └── update-item.dto.ts
├── .env.example            # 环境变量示例
├── vitest.config.ts        # Vitest 主配置
├── vitest.integration.config.ts  # 集成测试配置
├── vitest.e2e.config.ts    # E2E 测试配置
├── package.json
├── tsconfig.json
└── README.md
```

## API 端点

### Items API

- `GET /api/v1/items` - 获取所有 items
- `GET /api/v1/items/:id` - 获取单个 item
- `POST /api/v1/items` - 创建 item
- `PATCH /api/v1/items/:id` - 更新 item（部分更新）
- `PUT /api/v1/items/:id` - 更新 item（完整更新）
- `DELETE /api/v1/items/:id` - 删除 item

### 其他端点

- `GET /api/v1/` - 根路径（通过全局前缀）
- `GET /api/v1/health` - 健康检查（如果实现）

## 统一响应格式

所有 API 响应遵循以下格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 测试

### 测试框架
- **Vitest**: 快速、现代的测试框架
- **@nestjs/testing**: Nest.js 官方测试工具

### 测试类型
- **单元测试**: Service 和 Controller 层的单元测试
- **集成测试**: 需要真实 MongoDB 连接的集成测试

### 运行测试
```bash
# 运行所有单元测试
bun run test

# 监视模式
bun run test:watch

# 生成覆盖率报告
bun run test:cov
```
