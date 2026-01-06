# Python FastAPI Service

Python 后端服务，使用 FastAPI 框架和 MongoDB 数据库。

## 技术栈

- **框架**: FastAPI 0.128+
- **ASGI 服务器**: Uvicorn
- **数据库**: MongoDB
- **数据库驱动**: Motor (异步 MongoDB 驱动)
- **数据验证**: Pydantic 2.x
- **包管理**: uv
- **测试框架**: pytest + pytest-asyncio + mongomock-motor

## 快速开始

### 安装依赖

```bash
# 使用 uv 安装依赖
uv sync
```

### 环境配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试文件
uv run pytest tests/test_items.py -v

# 运行测试并显示覆盖率
uv run pytest tests/ --cov=app --cov-report=html
```

### 启动服务

```bash
# 开发模式（自动重载）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
uv run python -m app.main
```

### API 文档

启动服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
python-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # 应用入口
│   ├── config.py        # 配置管理（Pydantic Settings）
│   ├── database.py      # 数据库连接（Motor）
│   ├── routers/         # 路由模块
│   │   ├── __init__.py
│   │   └── items.py     # Items 路由
│   └── schemas/         # Pydantic 模式
│       ├── __init__.py
│       ├── item.py      # Item 数据模式
│       └── response.py  # 统一响应格式
├── tests/               # 测试代码
│   ├── __init__.py
│   ├── conftest.py      # Pytest 配置和 fixtures
│   └── test_items.py    # Items API 测试
├── .env.example         # 环境变量示例
├── pyproject.toml       # 项目配置（uv）
├── pytest.ini          # Pytest 配置
└── README.md
```

## API 端点

### Items API

- `GET /api/v1/items` - 获取所有 items
- `GET /api/v1/items/{id}` - 获取单个 item
- `POST /api/v1/items` - 创建 item
- `PUT /api/v1/items/{id}` - 更新 item
- `DELETE /api/v1/items/{id}` - 删除 item

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

### 测试框架
- **pytest**: Python 测试框架
- **pytest-asyncio**: 异步测试支持
- **mongomock-motor**: MongoDB Mock 驱动（用于单元测试）

### 测试覆盖
- ✅ CRUD 操作测试
- ✅ 数据验证测试
- ✅ 错误处理测试
- ✅ 边界条件测试

### 运行测试
```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_items.py::TestItemsAPI::test_create_item_success -v

# 生成覆盖率报告
uv run pytest tests/ --cov=app --cov-report=html
```
