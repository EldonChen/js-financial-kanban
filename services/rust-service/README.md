# Rust Axum Service

Rust 后端服务，使用 Axum 框架和 MongoDB 数据库。

## 技术栈

- **框架**: Axum 0.7
- **异步运行时**: Tokio 1.35+
- **数据库**: MongoDB
- **数据库驱动**: mongodb 3.4
- **序列化**: serde + serde_json
- **包管理**: Cargo
- **测试框架**: Rust 内置测试框架

## 快速开始

### 安装依赖

```bash
# 使用 Cargo 构建项目（会自动下载依赖）
cargo build
```

### 环境配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 启动服务

```bash
# 开发模式（自动重载需要 cargo-watch）
cargo run

# 或使用 release 模式（优化性能）
cargo run --release
```

### 运行测试

```bash
# 运行单元测试
cargo test

# 运行所有测试（包括集成测试，需要 MongoDB）
cargo test -- --ignored

# 运行特定测试
cargo test test_create_item
```

### API 文档

启动服务后，访问：
- API 基础路径: http://localhost:8080/api/v1

## 项目结构

```
rust-service/
├── src/
│   ├── main.rs          # 应用入口
│   ├── database.rs      # 数据库连接
│   ├── models/          # 数据模型
│   │   ├── mod.rs
│   │   └── item.rs      # Item 模型和响应结构
│   └── handlers/        # 请求处理器
│       ├── mod.rs
│       └── items.rs     # Items CRUD 处理器
├── tests/               # 集成测试
│   └── integration_test.rs
├── .env.example         # 环境变量示例
├── Cargo.toml          # 项目配置
└── README.md
```

## API 端点

### Items API

- `GET /api/v1/items` - 获取所有 items
- `GET /api/v1/items/:id` - 获取单个 item
- `POST /api/v1/items` - 创建 item
- `PUT /api/v1/items/:id` - 更新 item
- `DELETE /api/v1/items/:id` - 删除 item

### 其他端点

- `GET /` - 根路径，返回服务信息
- `GET /health` - 健康检查

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

### 单元测试

单元测试位于各个模块的 `*_test.rs` 文件中，使用 mock 数据库，无需真实 MongoDB。

```bash
cargo test
```

### 集成测试

集成测试位于 `tests/` 目录，需要真实的 MongoDB 连接。

```bash
# 运行集成测试（需要 MongoDB 运行）
cargo test -- --ignored
```
