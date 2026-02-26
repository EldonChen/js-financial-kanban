# 服务布局与目录结构

## 放置位置

- **推荐**：monorepo 内新服务目录 `services/data-source-service/`，与 `services/py-stock-info-service/` 同级。
- **备选**：若产品决定独立仓库，则本布局可直接平移为仓库根目录下的应用结构。

## 目录结构

```
services/data-source-service/
├── README.md
├── pyproject.toml              # 或 requirements.txt，依赖与脚本
├── .env.example                # 环境变量示例，不含敏感值
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用、生命周期（注册 Provider）
│   ├── config.py               # 配置模型与校验（Pydantic Settings）
│   ├── api/                    # API 层（Controller）
│   │   ├── __init__.py
│   │   ├── deps.py             # 依赖注入：Router、Registry 等
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── providers.py    # GET /api/v1/providers/status
│   │   │   ├── stocks.py       # GET/POST stocks, GET stocks/list
│   │   │   └── kline.py        # GET kline/{ticker}
│   │   └── schemas/            # 请求/响应 Pydantic 模型，与 spec/model 对齐
│   │       ├── __init__.py
│   │       ├── response.py     # ApiResponse 通用外壳
│   │       ├── stock.py        # Stock
│   │       ├── kline.py        # Kline, KlineResponseData
│   │       └── capability.py   # ProviderInfo, CapabilityResponseData
│   ├── services/               # 应用服务层（编排）
│   │   ├── __init__.py
│   │   └── data_source_app_service.py  # 编排 Router，封装为业务接口
│   ├── domain/                 # 路由与注册（核心领域）
│   │   ├── __init__.py
│   │   ├── registry.py         # IRegistry 实现
│   │   ├── router.py           # IRouter 实现
│   │   └── interfaces.py       # IProviderMetadata, IStockMetaProvider, IKlineProvider
│   ├── providers/              # Provider 插件实现
│   │   ├── __init__.py
│   │   ├── base.py             # 抽象基类 / 协议
│   │   ├── akshare_provider.py
│   │   ├── yfinance_provider.py
│   │   ├── easyquotation_provider.py
│   │   └── field_mappers/      # 各数据源原始 -> 统一模型
│   │       ├── __init__.py
│   │       ├── akshare_mapper.py
│   │       ├── yfinance_mapper.py
│   │       └── kline_mapper.py  # 通用或按数据源拆分
│   └── bootstrap.py            # 启动时：加载配置 -> 实例化 Provider -> 注册
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # 公共 fixture：Registry、Router、mock Provider
│   ├── unit/
│   │   ├── test_registry.py
│   │   ├── test_router.py
│   │   ├── test_config.py
│   │   └── test_field_mappers.py
│   ├── api/
│   │   ├── test_providers_api.py
│   │   ├── test_stocks_api.py
│   │   └── test_kline_api.py
│   └── integration/            # 可选：真实数据源（可标记 skip 或环境变量控制）
│       └── test_providers_live.py
├── Dockerfile
└── docker-compose.yml          # 可选，用于与其它服务一起编排
```

## 与 SPEC 分层的映射

| SPEC 层 | 实现位置 |
|---------|----------|
| API 层 (Controller / HTTP) | `app/api/routes/*`：参数校验、调用应用服务、统一响应与错误码映射 |
| 应用服务层 | `app/services/data_source_app_service.py`：编排 Router，不直接依赖具体 Provider |
| 路由/转发层 (Router) | `app/domain/router.py`：按 market/feature/data_source 选 Provider，容错与回退 |
| Provider 层 | `app/providers/*`：实现 IStockMetaProvider / IKlineProvider，内部使用 field_mappers |
| 注册表 | `app/domain/registry.py`：IRegistry，按 name / market / feature 查询 |
| 配置与启动 | `app/config.py` + `app/bootstrap.py`：配置校验、Provider 实例化与注册 |

## 与 py-stock-info-service 的对应

| 现有（py-stock-info-service） | 本服务 |
|------------------------------|--------|
| `app/services/providers/base.StockDataProvider` | `app/providers/base` + `app/domain/interfaces.py`（拆成 IProviderMetadata + IStockMetaProvider/IKlineProvider） |
| `app/services/providers/router.StockDataRouter` | `app/domain/router.py`（行为对齐：优先级、首选、按市场、失败回退） |
| `app/services/providers/field_mapper` | `app/providers/field_mappers/*`（映射到 spec/model 的 Stock、Kline） |
| `app/services/historical_data/historical_data_fetcher` | 由 KlineProvider 实现 + Router 转发替代，逻辑迁入 `app/providers/*` 与 `app/domain/router.py` |
| `app/config.Settings` | `app/config.py`：保留 ENABLE_*、凭证、超时等，并增加 PRD 05 的校验（至少一个第一优先级启用） |

## 接口与抽象所在文件

- **interfaces**：`app/domain/interfaces.py` 中定义 IProviderMetadata、IStockMetaProvider、IKlineProvider、IRegistry、IRouter（可用 Protocol 或 ABC）。
- **统一模型**：`app/api/schemas/` 中的 Pydantic 模型与 [spec/model/schemas.yaml](../../../spec/data-source-service/model/schemas.yaml) 一一对应，保证 API 响应可序列化且符合契约。
