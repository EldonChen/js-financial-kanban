# 金融看板系统 (Financial Kanban System)

一个基于前后端分离架构的金融看板系统，采用 Monorepo 结构管理代码。

## 📋 项目概述

本项目是一个金融看板系统，采用现代化的技术栈构建，支持多语言后端服务（Python、Node.js、Rust）和统一的前端界面。

## 🏗️ 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **元框架**: Nuxt.js 3
- **UI 组件库**: Shadcn UI + Tailwind CSS
- **状态管理**: Pinia
- **HTTP 客户端**: Fetch API
- **包管理**: pnpm

### 后端服务
- **Python 服务**: FastAPI
  - 包管理: uv
  - 数据库驱动: Motor (异步 MongoDB 驱动)
- **Node.js 服务**: Bun + Nest.js
  - 数据库驱动: Mongoose
- **Rust 服务**: Axum
  - 包管理: Cargo
  - 数据库驱动: mongodb crate
- **Python 股票信息服务**: FastAPI
  - 提供股票信息管理功能

### BFF 层
- **BFF 服务**: NestJS + Bun
  - 为前端提供定制化、高聚合度的接口
  - 聚合多个后台服务的数据
  - 面向前端视图设计接口

### 数据库
- **MongoDB**: 文档数据库，适合金融数据灵活存储

## 📁 项目结构

```
js-financial-kanban/
├── frontend/                 # 前端应用（Nuxt.js）
│   ├── pages/               # Nuxt 页面路由
│   ├── components/          # 组件
│   ├── composables/         # 组合式函数
│   ├── stores/              # Pinia 状态管理
│   ├── api/                 # API 调用封装
│   └── nuxt.config.ts
├── services/                # 后端服务
│   ├── python-service/      # Python FastAPI 服务
│   ├── py-stock-info-service/  # Python 股票信息服务（多数据源支持）
│   ├── node-service/        # Node.js (Bun + Nest.js) 服务
│   ├── rust-service/        # Rust (Axum) 服务
│   └── py-stock-info-service/ # Python 股票信息服务
├── bff/                     # BFF (Backend For Frontend) 层
│   ├── bff-main/           # 主 BFF 服务（NestJS）
│   └── shared/             # BFF 层共享代码（可选）
├── shared/                  # 共享代码（类型定义、工具函数等）
├── docs/                    # 项目文档
├── .gitignore
├── .cursorrules             # AI 协作规则
└── README.md
```

## 🚀 快速开始

### 前置要求

- **Node.js**: >= 18.x (或使用 Bun)
- **Python**: >= 3.10
- **Rust**: >= 1.70
- **MongoDB**: >= 5.0
- **pnpm**: >= 8.x
- **uv**: Python 包管理工具
- **Bun**: Node.js 运行时（可选，用于 Node.js 服务）

### 安装依赖

#### 前端
```bash
cd frontend
pnpm install
```

#### Python 服务
```bash
cd services/python-service
uv sync
```

#### Node.js 服务
```bash
cd services/node-service
bun install
```

#### Rust 服务
```bash
cd services/rust-service
cargo build
```

#### BFF 服务
```bash
cd bff/bff-main
bun install
```

### 环境配置

各服务需要配置 MongoDB 连接字符串，创建对应的 `.env` 文件：

#### Python 服务
```bash
cd services/python-service
# 创建 .env 文件
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=financial_kanban
PORT=8000
```

#### Node.js 服务
```bash
cd services/node-service
# 创建 .env 文件
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=financial_kanban
PORT=3000
```

#### Rust 服务
```bash
cd services/rust-service
# 创建 .env 文件
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=financial_kanban
PORT=8080
```

#### 前端
```bash
cd frontend
# 创建 .env 文件
NUXT_PUBLIC_BFF_API_URL=http://localhost:4000
# 保留原有配置以兼容（可选）
NUXT_PUBLIC_PYTHON_API_URL=http://localhost:8000
NUXT_PUBLIC_NODE_API_URL=http://localhost:3000
NUXT_PUBLIC_RUST_API_URL=http://localhost:8080
```

#### BFF 服务
```bash
cd bff/bff-main
# 创建 .env 文件
PORT=4000
PYTHON_SERVICE_URL=http://localhost:8000
NODE_SERVICE_URL=http://localhost:3000
RUST_SERVICE_URL=http://localhost:8080
STOCK_INFO_SERVICE_URL=http://localhost:8001
```

### 启动服务

#### 启动 MongoDB
```bash
# 使用 Docker（推荐）
docker run -d -p 27017:27017 --name mongodb mongo:latest

# 或使用本地安装的 MongoDB
mongod
```

#### 启动后端服务

**Python 服务** (端口 8000):
```bash
cd services/python-service
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Node.js 服务** (端口 3000):
```bash
cd services/node-service
bun run start:dev
```

**Rust 服务** (端口 8080):
```bash
cd services/rust-service
cargo run
```

**BFF 服务** (端口 4000):
```bash
cd bff/bff-main
bun run start:dev
```

#### 启动前端（待实现）
```bash
cd frontend
pnpm dev
```

前端将在 `http://localhost:3001` 启动。

## 🐳 Docker 部署（Standalone）

项目提供完整的 Docker 容器化部署方案，支持一键启动所有服务。

### 前置要求

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0

### 快速开始

1. **克隆项目**（如果还没有）：
   ```bash
   git clone <repository-url>
   cd js-financial-kanban
   ```

2. **构建镜像**：
   ```bash
   docker-compose build
   ```

3. **启动所有服务**：
   ```bash
   docker-compose up -d
   ```

4. **查看服务状态**：
   ```bash
   docker-compose ps
   ```

5. **查看日志**：
   ```bash
   # 查看所有服务日志
   docker-compose logs -f
   
   # 查看特定服务日志
   docker-compose logs -f python-service
   docker-compose logs -f node-service
   docker-compose logs -f rust-service
   docker-compose logs -f frontend
   ```

6. **停止服务**：
   ```bash
   docker-compose down
   ```

7. **清理数据**（谨慎使用，会删除 MongoDB 数据）：
   ```bash
   docker-compose down -v
   ```

### 服务访问地址

启动后，可以通过以下地址访问各服务：

- **前端**: http://localhost:3001
- **BFF 服务**: http://localhost:4000
  - Dashboard: http://localhost:4000/api/bff/v1/views/dashboard
  - Items: http://localhost:4000/api/bff/v1/views/items
  - Stocks: http://localhost:4000/api/bff/v1/views/stocks
- **Python 服务**: http://localhost:8000
  - Swagger 文档: http://localhost:8000/docs
- **Node.js 服务**: http://localhost:3000
- **Rust 服务**: http://localhost:8080
- **Python 股票信息服务**: http://localhost:8001
- **MongoDB**: localhost:27017

### 环境变量配置

各服务的环境变量可以通过以下方式配置：

1. **修改 `docker-compose.yml`**：直接在文件中修改 `environment` 部分
2. **使用 `.env` 文件**：在根目录创建 `.env` 文件（注意：`.env` 文件不应提交到 Git）

### 单独构建和运行服务

如果需要单独构建或运行某个服务：

```bash
# 构建特定服务
docker-compose build python-service

# 运行特定服务（包括依赖）
docker-compose up python-service

# 只运行特定服务（不启动依赖）
docker-compose run --rm python-service
```

### 开发模式

对于开发环境，建议使用本地开发方式（见上方"快速开始"部分），因为：

- 代码变更可以实时生效（热重载）
- 调试更方便
- 构建速度更快

Docker 部署主要用于：
- 生产环境部署
- CI/CD 流程
- 快速验证环境一致性
- 演示和测试

### 故障排查

1. **服务无法启动**：
   ```bash
   # 查看服务日志
   docker-compose logs <service-name>
   
   # 检查服务健康状态
   docker-compose ps
   ```

2. **MongoDB 连接失败**：
   - 确认 MongoDB 容器已启动：`docker-compose ps mongodb`
   - 检查 MongoDB 健康状态：`docker-compose logs mongodb`
   - 确认网络配置正确

3. **端口冲突**：
   - 检查端口占用：`lsof -i :8000`（或其他端口）
   - 修改 `docker-compose.yml` 中的端口映射

4. **构建失败**：
   - 清理构建缓存：`docker-compose build --no-cache`
   - 检查 Dockerfile 语法
   - 查看构建日志：`docker-compose build --progress=plain`

## 📚 API 文档

### Python 服务 (FastAPI)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API 基础路径**: http://localhost:8000/api/v1

### Node.js 服务 (Nest.js)
- **API 基础路径**: http://localhost:3000/api/v1
- **健康检查**: http://localhost:3000/api/v1/ (根路径)

### Rust 服务 (Axum)
- **API 基础路径**: http://localhost:8080/api/v1
- **健康检查**: http://localhost:8080/health

### BFF 服务 (NestJS)
- **API 基础路径**: http://localhost:4000/api/bff/v1
- **Dashboard 视图**: http://localhost:4000/api/bff/v1/views/dashboard
- **Items 视图**: http://localhost:4000/api/bff/v1/views/items
- **Stocks 视图**: http://localhost:4000/api/bff/v1/views/stocks

> 提示：可以使用 Postman、Insomnia 或 curl 测试 API

## 🛠️ 开发指南

### 代码规范

- **前端**: Prettier + ESLint
- **Python**: Black + pylint
- **Rust**: rustfmt + clippy

### Git 工作流

1. 从 main 分支创建功能分支: `feature/xxx`
2. 在功能分支开发
3. 提交前进行代码质量检查
4. 合并前整理提交历史

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<类型>(<范围>): <简短描述>

<详细说明（可选，空行分隔）>

<脚注（可选）>
```

**类型**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**范围**: 可选，指定变更影响的范围（如 `python-service`, `frontend`）

详细规范请参考 [.cursorrules](./.cursorrules) 文件。

## 📖 文档

- [技术方案设计](./技术方案设计.md) - 项目技术架构和选型说明
- [开发变更日志](./changelog.md) - 开发过程中的重要变更记录
- [技术路线文档](./技术路线-项目初始化.md) - 项目初始化任务拆解和进度跟踪
- [AI 协作规则](./.cursorrules) - 开发规范和 AI 协作流程

### 子项目文档

- [Python 服务 README](./services/python-service/README.md)
- [股票信息服务 README](./services/py-stock-info-service/README.md) - 支持多数据源的股票信息服务
- [Node.js 服务 README](./services/node-service/README.md)
- [Rust 服务 README](./services/rust-service/README.md)
- [BFF 服务 README](./bff/bff-main/README.md)

### 功能文档

- [API 文档 - 股票信息服务](./docs/API文档-股票信息服务.md) - 股票信息服务 API 详细文档
- [数据源调研报告](./docs/数据源调研报告.md) - 股票数据源调研和对比
- [技术方案设计 - 多数据源支持](./docs/技术方案设计-多数据源支持.md) - 多数据源支持技术方案

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

（待补充）

## 🧪 测试

### 运行测试

**Python 服务**:
```bash
cd services/python-service
uv run pytest tests/ -v
```

**Node.js 服务**:
```bash
cd services/node-service
bun run test
```

**Rust 服务**:
```bash
cd services/rust-service
cargo test
```

### 测试状态

- ✅ Python 服务：16 个测试用例全部通过
- ✅ Node.js 服务：16 个测试用例全部通过
- ✅ Rust 服务：基础测试框架已就绪

### 集成测试

运行集成测试脚本验证所有服务的集成情况：

```bash
# 确保所有服务已启动（MongoDB、三个后端服务、前端）
./scripts/integration-test.sh
```

详细集成验证指南请参考 [集成验证指南](./docs/集成验证指南.md)。

## 📊 项目状态

### ✅ 已完成
- 项目结构初始化
- Python FastAPI 服务（完整 CRUD API + 测试）
- 股票信息服务（多数据源支持）
  - ✅ 多数据源架构设计（Provider/Adapter 模式）
  - ✅ 数据源适配器实现（akshare、yfinance、easyquotation）
  - ✅ 数据源路由和容错机制
  - ✅ 多市场支持（A 股、港股、美股）
  - ✅ 全量股票列表获取
  - ✅ 单元测试和集成测试
- Node.js Nest.js 服务（完整 CRUD API + 测试）
- Rust Axum 服务（完整 CRUD API + 基础测试）
- Python 股票信息服务（股票信息管理 + 测试）
- BFF 层（数据聚合、视图接口、Docker 集成）

### 🚧 进行中
- 集成测试和验证

### 📋 待完成
- 完整的集成测试执行（需要 MongoDB 运行）
- 部署配置
- 第二优先级数据源适配器实现（Tushare、IEX Cloud、Alpha Vantage）

---

**最后更新**: 2024年
**当前版本**: 0.1.0
