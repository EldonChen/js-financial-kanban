# Stock Info Service

股票基本信息服务，基于 Python + FastAPI，支持多数据源（akshare、yfinance、easyquotation 等），用于从多个数据源抓取股票信息，经过数据转换后存入 MongoDB，并提供 RESTful API 接口。

## ✨ 核心特性

- ✅ **多数据源支持**：支持 akshare、yfinance、easyquotation 等多个数据源
- ✅ **自动容错**：主数据源失败时自动切换到备用数据源
- ✅ **多市场覆盖**：支持 A 股、港股、美股等多个市场
- ✅ **全量股票列表**：支持获取某市场的全量股票列表
- ✅ **数据源优先级**：免费优先、无需认证的数据源为第一优先级
- ✅ **灵活配置**：支持通过环境变量配置数据源启用/禁用

## 技术栈

- **框架**: FastAPI 0.104+
- **ASGI 服务器**: Uvicorn
- **数据库**: MongoDB
- **数据库驱动**: Motor (异步 MongoDB 驱动)
- **数据抓取**:
  - **akshare** (A 股主数据源，免费，无需认证)
  - **yfinance** (美股/港股主数据源，免费，无需认证)
  - **easyquotation** (A 股实时行情补充，可选)
  - **Tushare** (A 股备用数据源，需要 token，可选)
  - **IEX Cloud** (美股备用数据源，需要 API Key，可选)
  - **Alpha Vantage** (美股备用数据源，需要 API Key，可选)
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

#### 数据源配置

**第一优先级数据源（免费优先、无需认证，默认启用）**：
```bash
ENABLE_AKSHARE=true      # 默认启用，A 股主数据源
ENABLE_YFINANCE=true     # 默认启用，美股/港股主数据源
ENABLE_EASYQUOTATION=false  # 可选，A 股实时行情补充
```

**第二优先级数据源（需要注册 API Key，可选）**：
```bash
# Tushare（A 股备用数据源）
ENABLE_TUSHARE=false
TUSHARE_TOKEN=          # 如果启用 Tushare，需要配置 token

# IEX Cloud（美股备用数据源）
ENABLE_IEX_CLOUD=false
IEX_CLOUD_API_KEY=      # 如果启用 IEX Cloud，需要配置 API Key

# Alpha Vantage（美股备用数据源）
ENABLE_ALPHA_VANTAGE=false
ALPHA_VANTAGE_API_KEY=  # 如果启用 Alpha Vantage，需要配置 API Key
```

**注意**：
- 第一优先级数据源无需配置即可使用（默认启用）
- 第二优先级数据源需要配置相应的 API Key 才能启用
- 如果未配置第二优先级数据源，系统会自动跳过，不影响使用

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
│   ├── config.py            # 配置管理（包含数据源配置）
│   ├── database.py          # 数据库连接
│   ├── routers/             # 路由模块
│   │   ├── __init__.py
│   │   ├── stocks.py        # 股票查询接口
│   │   ├── schedules.py     # 更新计划管理接口
│   │   └── providers.py     # 数据源管理接口（新增）
│   ├── schemas/             # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── stock.py         # 股票数据模式（已扩展支持多市场字段）
│   │   ├── schedule.py      # 更新计划模式
│   │   └── response.py     # 统一响应格式
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── yfinance_service.py  # yfinance 数据抓取服务（保留向后兼容）
│   │   ├── stock_service.py    # 股票数据业务逻辑（已支持多数据源）
│   │   ├── scheduler_service.py # 定时任务服务
│   │   └── providers/          # 数据源提供者模块（新增）
│   │       ├── __init__.py
│   │       ├── base.py          # 数据源抽象基类
│   │       ├── router.py        # 数据源路由器
│   │       ├── field_mapper.py   # 字段映射器
│   │       ├── initializer.py    # 数据源初始化模块
│   │       ├── config_validator.py  # 配置验证器
│   │       ├── akshare_provider.py  # akshare 数据源适配器
│   │       ├── yfinance_provider.py # yfinance 数据源适配器
│   │       └── easyquotation_provider.py  # easyquotation 数据源适配器
│   └── models/              # 数据模型（MongoDB 集合定义）
│       ├── __init__.py
│       ├── stock.py         # 股票数据模型（已扩展支持多市场字段）
│       └── schedule.py       # 更新计划模型
├── tests/                   # 测试代码
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_providers.py    # 数据源提供者测试（新增）
│   ├── test_router.py       # 数据源路由器测试（新增）
│   ├── test_field_mapper.py # 字段映射器测试（新增）
│   ├── test_provider_integration.py  # 数据源集成测试（新增）
│   └── test_stock_service.py # 股票服务测试（已更新）
├── .env.example
├── pyproject.toml
├── pytest.ini
└── README.md
```

## API 端点

### 股票查询接口

- `GET /api/v1/stocks` - 股票列表查询（支持筛选和分页）
  - 查询参数：
    - `ticker` - 股票代码（精确匹配）
    - `name` - 股票名称（模糊查询）
    - `market` - 市场（精确匹配）
    - `market_type` - 市场类型（精确匹配：A股、港股、美股）
    - `sector` - 行业板块（精确匹配）
    - `page` - 页码（默认 1）
    - `page_size` - 每页数量（默认 20，最大 100）
- `GET /api/v1/stocks/{ticker}` - 获取单个股票信息
- `POST /api/v1/stocks/{ticker}/update` - 手动更新单个股票（支持多数据源）
  - 查询参数：
    - `market` - 市场类型（可选，用于选择合适的数据源：A股、港股、美股）
    - `preferred_provider` - 首选数据源（可选：akshare、yfinance、easyquotation等）
- `POST /api/v1/stocks/update-all` - 手动触发所有股票的更新
- `POST /api/v1/stocks/batch-update` - 批量手动更新股票
- `POST /api/v1/stocks/fetch-all` - 从数据源拉取全部股票列表并保存（SSE 实时推送进度，支持多数据源）
  - 查询参数：
    - `market` - 市场类型（可选，用于选择合适的数据源：A股、港股、美股）
    - `delay` - 每次抓取之间的延迟（秒，默认 1.0 秒）

### 数据源管理接口（新增）

- `GET /api/v1/providers/status` - 获取数据源状态信息
  - 返回已注册的数据源列表、支持的市场、市场覆盖情况

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
uv run pytest tests/test_providers.py -v
uv run pytest tests/test_router.py -v
uv run pytest tests/test_field_mapper.py -v
uv run pytest tests/test_provider_integration.py -v

# 运行测试并显示覆盖率
uv run pytest tests/ --cov=app --cov-report=html
```

### 测试覆盖

- ✅ 数据源提供者单元测试（akshare、yfinance、easyquotation）
- ✅ 数据源路由器单元测试（注册、选择、容错）
- ✅ 字段映射器单元测试（所有数据源的字段映射）
- ✅ 数据源集成测试（多数据源切换场景）
- ✅ StockService 多数据源功能测试

## 多数据源支持

### 数据源优先级

系统采用**"免费优先、无需认证"**的优先级策略：

#### 第一优先级（免费优先、无需认证）

1. **akshare** - A 股主数据源
   - 支持市场：A 股、港股、美股
   - 支持全量股票列表
   - 完全免费，无需注册
   - 社区活跃，持续更新

2. **yfinance** - 美股/港股主数据源
   - 支持市场：美股、港股
   - 支持全量股票列表
   - 完全免费，无需注册
   - 已使用，稳定可靠

3. **easyquotation** - A 股实时行情补充（可选）
   - 支持市场：A 股
   - 仅用于实时行情补充
   - 不支持全量股票列表
   - 完全免费，无需注册

#### 第二优先级（需要注册 API Key，存在限制）

1. **Tushare** - A 股备用数据源（可选）
   - 需要配置 `TUSHARE_TOKEN`
   - 数据质量高，支持全量股票列表

2. **IEX Cloud** - 美股备用数据源（可选）
   - 需要配置 `IEX_CLOUD_API_KEY`
   - 免费版 50,000 次/月

3. **Alpha Vantage** - 美股备用数据源（可选）
   - 需要配置 `ALPHA_VANTAGE_API_KEY`
   - 免费版 5 次/分钟

### 数据源选择逻辑

1. **按市场自动选择**：
   - A 股：优先使用 akshare，失败时自动切换到 easyquotation 或 Tushare
   - 美股/港股：优先使用 yfinance，失败时自动切换到 IEX Cloud 或 Alpha Vantage

2. **手动指定数据源**：
   - 通过 API 参数 `preferred_provider` 指定首选数据源

3. **自动容错**：
   - 主数据源失败时自动切换到备用数据源
   - 所有数据源都失败时返回错误

### 数据字段扩展

股票数据模型已扩展，支持以下新字段：

- `market_type` - 市场类型（A股、港股、美股）
- `market_cap` - 市值（可选）
- `pe_ratio` - 市盈率（可选）
- `pb_ratio` - 市净率（可选）
- `dividend_yield` - 股息率（可选）
- `listing_date` - 上市日期（可选）

## 使用示例

### 更新 A 股股票

```bash
# 使用默认数据源（自动选择 akshare）
curl -X POST "http://localhost:8001/api/v1/stocks/000001/update"

# 指定市场类型（自动选择合适的数据源）
curl -X POST "http://localhost:8001/api/v1/stocks/000001/update?market=A股"

# 指定首选数据源
curl -X POST "http://localhost:8001/api/v1/stocks/000001/update?preferred_provider=akshare"
```

### 更新美股股票

```bash
# 使用默认数据源（自动选择 yfinance）
curl -X POST "http://localhost:8001/api/v1/stocks/AAPL/update"

# 指定市场类型
curl -X POST "http://localhost:8001/api/v1/stocks/AAPL/update?market=美股"
```

### 拉取 A 股全量股票列表

```bash
# 使用 SSE 接收实时进度
curl -X POST "http://localhost:8001/api/v1/stocks/fetch-all?market=A股&delay=1.0"
```

### 查询数据源状态

```bash
curl "http://localhost:8001/api/v1/providers/status"
```

## 注意事项

1. **数据源可用性**：
   - 第一优先级数据源（akshare、yfinance）默认启用，无需配置
   - 第二优先级数据源需要配置 API Key 才能启用
   - 系统启动时会自动验证配置并注册可用的数据源

2. **数据源限制**：
   - akshare：依赖第三方网站，可能被反爬虫机制影响
   - yfinance：在中国大陆可能访问受限（需要代理）
   - 建议配置多个数据源以提高可用性

3. **数据字段**：
   - 不同数据源返回的字段可能不同
   - 系统会自动映射和清洗字段，统一格式
   - 支持扩展字段（财务指标、上市日期等）

4. **更新计划**：更新计划是全局的，不绑定特定股票，执行时会更新所有股票

5. **服务端口**：默认端口为 8001，避免与 python-service (8000) 冲突
