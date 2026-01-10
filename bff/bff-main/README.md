# BFF (Backend For Frontend) 服务

BFF 层为前端提供定制化、高聚合度的接口，降低前端直接访问细粒度后台服务的复杂度。

## 📋 功能特性

- **数据聚合**：将多个后台服务的细粒度接口聚合成前端需要的视图数据
- **请求编排**：协调多个后台服务的调用顺序和依赖关系
- **数据转换**：将后台服务的数据格式转换为前端视图所需格式
- **性能优化**：通过并发调用、超时控制等方式优化性能
- **错误处理**：统一处理后台服务错误，支持部分失败降级

## 🏗️ 架构设计

### 技术栈

- **框架**：NestJS
- **运行时**：Bun
- **HTTP 客户端**：@nestjs/axios
- **语言**：TypeScript

### 项目结构

```
bff-main/
├── src/
│   ├── views/              # 视图模块（按前端页面组织）
│   │   ├── dashboard/      # 首页看板视图
│   │   ├── items/         # Items 管理视图
│   │   └── stocks/        # 股票信息视图
│   ├── clients/           # 后台服务客户端
│   │   ├── python.client.ts
│   │   ├── node.client.ts
│   │   ├── rust.client.ts
│   │   └── stock-info.client.ts
│   ├── common/            # 公共模块
│   │   ├── interceptors/  # 拦截器
│   │   ├── filters/       # 异常过滤器
│   │   └── utils/         # 工具函数
│   ├── app.module.ts
│   └── main.ts
├── package.json
├── tsconfig.json
└── Dockerfile
```

## 🚀 快速开始

### 前置要求

- **Bun**: >= 1.0
- **Node.js**: >= 18.x (如果使用 Node.js 运行时)

### 安装依赖

```bash
cd bff/bff-main
bun install
```

### 环境配置

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
PORT=4000
HOST=0.0.0.0
NODE_ENV=development

# 后台服务 URL
PYTHON_SERVICE_URL=http://localhost:8000
NODE_SERVICE_URL=http://localhost:3000
RUST_SERVICE_URL=http://localhost:8080
STOCK_INFO_SERVICE_URL=http://localhost:8001

# 超时配置（毫秒）
HTTP_TIMEOUT=5000
HTTP_MAX_REDIRECTS=5
```

### 启动服务

**开发模式**（热重载）：

```bash
bun run start:dev
```

**生产模式**：

```bash
bun run build
bun run start:prod
```

服务将在 `http://localhost:4000` 启动。

## 📡 API 接口

### 基础路径

所有接口的基础路径为：`/api/bff/v1`

### 视图接口

#### 1. Dashboard 视图

**GET** `/api/bff/v1/views/dashboard`

获取首页看板数据，包括统计信息和最近的数据。

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "stats": {
      "totalItems": 15,
      "pythonItems": 5,
      "nodeItems": 5,
      "rustItems": 5,
      "totalStocks": 10
    },
    "recentItems": [...],
    "recentStocks": [...]
  },
  "timestamp": 1234567890
}
```

#### 2. Items 视图

**GET** `/api/bff/v1/views/items`

获取所有 Items（聚合 Python、Node、Rust 三个服务的数据）。

**响应示例**：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "1",
      "name": "Item 1",
      "description": "Description",
      "price": 100,
      "source": "python",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "timestamp": 1234567890
}
```

#### 3. Stocks 视图

**GET** `/api/bff/v1/views/stocks`

获取所有股票信息。

**GET** `/api/bff/v1/views/stocks/:ticker`

获取指定股票信息。

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
bun run test

# 监听模式
bun run test:watch

# 生成覆盖率报告
bun run test:cov
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t bff-main .
```

### 运行容器

```bash
docker run -d \
  -p 4000:4000 \
  -e PYTHON_SERVICE_URL=http://python-service:8000 \
  -e NODE_SERVICE_URL=http://node-service:3000 \
  -e RUST_SERVICE_URL=http://rust-service:8080 \
  -e STOCK_INFO_SERVICE_URL=http://py-stock-info-service:8001 \
  bff-main
```

### 使用 Docker Compose

BFF 服务已集成到根目录的 `docker-compose.yml` 中：

```bash
# 启动所有服务（包括 BFF）
docker-compose up -d

# 查看 BFF 服务日志
docker-compose logs -f bff-main
```

## 🔧 开发指南

### 添加新的视图模块

1. 在 `src/views/` 目录下创建新的模块目录
2. 创建 `*.module.ts`、`*.controller.ts`、`*.service.ts`
3. 在 `src/views/views.module.ts` 中导入新模块

### 添加新的后台服务客户端

1. 在 `src/clients/` 目录下创建新的客户端文件
2. 在 `src/clients/clients.module.ts` 中注册客户端

### 数据转换

使用 `src/common/utils/transform.util.ts` 中的工具函数进行数据转换。

### 错误处理

- 使用 `allSettledWithNull` 允许部分服务失败
- 在 Service 层处理错误，返回默认值或空数组
- 使用全局异常过滤器统一错误响应格式

## 📝 注意事项

1. **超时控制**：所有 HTTP 请求都有超时设置（默认 5 秒）
2. **部分失败处理**：使用 `Promise.allSettled` 允许部分服务失败
3. **数据去重**：Items 视图会自动去重（按 name），保留最新的数据
4. **并发调用**：多个服务的调用是并行的，提高性能

## 🔗 相关文档

- [技术方案设计-BFF层](../../docs/技术方案设计-BFF层.md)
- [技术路线-BFF层](../../docs/技术路线-BFF层.md)

---

**最后更新**：2024年
