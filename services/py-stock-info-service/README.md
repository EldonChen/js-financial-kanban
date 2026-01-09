# Stock Info Service

股票基本信息服务，基于 Python + FastAPI + yfinance，用于从 Yahoo Finance 抓取股票信息，经过数据转换后存入 MongoDB，并提供 RESTful API 接口。

## 技术栈

- **框架**: FastAPI 0.104+
- **ASGI 服务器**: Uvicorn
- **数据库**: MongoDB
- **数据库驱动**: Motor (异步 MongoDB 驱动)
- **数据抓取**: yfinance (Yahoo Finance Python 库)
- **定时任务**: APScheduler (异步任务调度)
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

### 启动服务

```bash
# 开发模式（自动重载）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 或使用 Python 直接运行
uv run python -m app.main
```

### API 文档

启动服务后，访问：
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 项目结构

```
py-stock-info-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── routers/             # 路由模块
│   │   ├── __init__.py
│   │   ├── stocks.py        # 股票查询接口
│   │   └── schedules.py     # 更新计划管理接口
│   ├── schemas/             # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── stock.py         # 股票数据模式
│   │   ├── schedule.py      # 更新计划模式
│   │   └── response.py     # 统一响应格式
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── yfinance_service.py  # yfinance 数据抓取服务
│   │   ├── stock_service.py    # 股票数据业务逻辑
│   │   └── scheduler_service.py # 定时任务服务
│   └── models/              # 数据模型（MongoDB 集合定义）
│       ├── __init__.py
│       ├── stock.py         # 股票数据模型
│       └── schedule.py       # 更新计划模型
├── tests/                   # 测试代码
│   ├── __init__.py
│   └── conftest.py
├── .env.example
├── pyproject.toml
├── pytest.ini
└── README.md
```

## API 端点

### 股票查询接口

- `GET /api/v1/stocks` - 股票列表查询（支持筛选和分页）
- `GET /api/v1/stocks/{ticker}` - 获取单个股票信息
- `POST /api/v1/stocks/{ticker}/update` - 手动更新单个股票
- `POST /api/v1/stocks/update-all` - 手动触发所有股票的更新
- `POST /api/v1/stocks/batch-update` - 批量手动更新股票

### 更新计划管理接口

- `GET /api/v1/schedules` - 查询更新计划列表
- `GET /api/v1/schedules/{schedule_id}` - 获取单个更新计划
- `GET /api/v1/schedules/status` - 查询更新状态统计
- `POST /api/v1/schedules` - 新增更新计划
- `PUT /api/v1/schedules/{schedule_id}` - 更新更新计划
- `DELETE /api/v1/schedules/{schedule_id}` - 删除更新计划
- `POST /api/v1/schedules/{schedule_id}/toggle` - 切换激活状态

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

## 定时任务

服务支持通过 APScheduler 实现定时自动更新股票数据。更新计划是全局的，执行时会更新所有股票。

### 创建更新计划示例

```bash
# 创建 Cron 调度（每个工作日 9:00 执行）
curl -X POST http://localhost:8001/api/v1/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_type": "cron",
    "schedule_config": {
      "cron": "0 9 * * 1-5"
    },
    "is_active": true
  }'

# 创建间隔调度（每 3600 秒执行一次）
curl -X POST http://localhost:8001/api/v1/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_type": "interval",
    "schedule_config": {
      "interval": 3600
    },
    "is_active": true
  }'
```

## 测试

### 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试文件
uv run pytest tests/test_stocks.py -v

# 运行测试并显示覆盖率
uv run pytest tests/ --cov=app --cov-report=html
```

## 注意事项

1. **yfinance API 限制**：Yahoo Finance 可能有请求频率限制，服务在批量更新时会自动添加延迟（默认 1 秒）
2. **数据字段**：当前只抓取股票基本信息（ticker, name, market, sector, industry, currency, exchange, country），不包含价格和市值数据
3. **更新计划**：更新计划是全局的，不绑定特定股票，执行时会更新所有股票
4. **服务端口**：默认端口为 8001，避免与 python-service (8000) 冲突
