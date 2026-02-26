# 技术栈设计

## 语言与运行时

| 项目 | 选型 | 版本约束 | 说明 |
|------|------|----------|------|
| 语言 | Python | 3.11+ | 与现有 py-stock-info-service 一致，便于复用与迁移 |
| 包管理 | uv | 最新稳定版 | 项目规范（.cursorrules）约定 Python 使用 uv |
| 异步运行时 | asyncio | 标准库 | 与 Motor/FastAPI 异步模型一致 |

##  Web 框架与 API

| 项目 | 选型 | 版本约束 | 说明 |
|------|------|----------|------|
| Web 框架 | FastAPI | 0.109+ | 与现有 Python 服务一致；OpenAPI 自动生成 |
| 校验与配置 | Pydantic | v2 | FastAPI 默认；用于请求/响应模型与配置校验 |
| 配置加载 | pydantic-settings | 2.0+ | 环境变量与 .env，与 PRD 05 环境变量约定对齐 |

## 数据源依赖（Provider 实现）

| 数据源 | 库/方式 | 说明 |
|--------|----------|------|
| A 股 / 通用 | akshare | 现有 py-stock-info-service 已用，迁移或封装 |
| 美股/港股 | yfinance | 同上 |
| 实时行情（A 股） | easyquotation | 可选，按配置启用 |
| Tushare | tushare / 官方 API | 需 token，第二优先级 |
| IEX Cloud / Alpha Vantage | 按需 | 可选扩展，需 API Key |

- 以上库的**版本**在实现时于 `pyproject.toml` 或 `requirements.txt` 中固定，并在 README 中注明。
- 新增数据源时仅增加新依赖与新 Provider 实现，不改变框架选型。

## 可观测性与错误处理

| 项目 | 选型 | 说明 |
|------|------|------|
| 结构化日志 | 标准 logging + JSON 格式（可选） | 至少包含 trace_id、level、message、provider、ticker 等 |
| 链路追踪 | OpenTelemetry（可选首版） | 遵循 [spec/observability/opentelemetry.md](../../../spec/data-source-service/observability/opentelemetry.md)；首版可实现为「预留 Span 点」，后续补全 |
| 错误码 | 与 [spec/error/error-codes.md](../../../spec/data-source-service/error/error-codes.md) 一致 | HTTP 状态码 + body.code + message，不含凭证明文 |

## 测试

| 项目 | 选型 | 说明 |
|------|------|------|
| 测试框架 | pytest | 与项目规范一致 |
| 异步测试 | pytest-asyncio | 用于 async Provider / Router 测试 |
| HTTP 客户端测试 | httpx | FastAPI TestClient 或 httpx.AsyncClient 调用 ASGI 应用 |
|  mock 外部数据源 | pytest fixture + unittest.mock 或 respx | 单元测试不请求真实 akshare/yfinance API；集成测试可标记为可选 |

## 不包含（与本服务边界）

- **数据库**：本服务不持久化业务数据，仅做代理与规整；无需 MongoDB/Redis。
- **消息队列**：不做调度与异步任务，无需 Celery/RQ。
- **前端**：纯 API 服务，无前端技术栈。

## 选型依据小结

- **Python + FastAPI**：与现有 monorepo 内 py-stock-info-service 一致，降低认知与运维成本；FastAPI 满足 REST、OpenAPI、异步与校验需求。
- **uv**：项目统一包管理工具。
- **pydantic-settings**：直接对应 PRD 05 的环境变量表，便于校验「至少一个第一优先级启用」等规则。
- **pytest + pytest-asyncio**：项目规范明确，且适合 Provider/Router 的单元与集成测试。
