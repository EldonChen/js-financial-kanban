# OpenTelemetry 全链路追踪规范

## 目标

- **全链路追踪**：从 HTTP 请求进入数据源服务，到 Router 选 Provider、Provider 调用外部 API、返回响应的完整调用链，具备唯一 TraceId，便于跨服务与跨层排查。
- **统一标准**：采用 OpenTelemetry 语义约定（Trace、Span、Attributes、Events），与业界实践一致，便于接入 Jaeger、Zipkin、OTLP 等后端。

## 集成要求

### 1. SDK 与导出

- **TracerProvider**：在应用启动时初始化 OpenTelemetry TracerProvider，并配置导出器（如 OTLP exporter 到采集端，或 Console 用于开发）。
- **传播**：支持 **W3C Trace Context**（traceparent、tracestate）的注入与提取；若请求中已携带 traceparent，则延续该 Trace，否则创建新 Trace。
- **采样**：可配置采样策略（如父级已采样则跟随，否则按比例采样）；生产环境建议对错误与慢请求全量采样。

### 2. 服务与资源属性

- **Service name**：统一设置服务名，如 `data-source-service`，便于在追踪后端区分。
- **Resource attributes**：建议包含 `service.name`、`service.version`（可选）、`deployment.environment`（如 development/staging/production）。

## Trace 与 Span 约定

### 3. 顶层 Span（API 层）

- **Span name**：与操作语义一致，如 `GET /api/v1/stocks/{ticker}`、`POST /api/v1/stocks/batch`、`GET /api/v1/kline/{ticker}`、`GET /api/v1/providers/status`。
- **Attributes**（建议）：
  - `http.method`、`http.route`、`http.status_code`（响应时设置）；
  - 业务属性：`ticker`、`market`、`data_source`（若存在）、`period`（K 线请求）；
  - `data_source.request.type`：如 `stock_info`、`stock_list`、`kline`、`capability`。
- **Events**：可选记录「请求开始」「响应完成」；错误时记录 `exception`（见下）。

### 4. 路由层 Span

- **Span name**：如 `router.select_and_fetch` 或 `router.fetch_stock_info`。
- **父 Span**：以 API 层 Span 为父，形成「API → Router → Provider」层级。
- **Attributes**：
  - `data_source.candidate_providers`：尝试的 Provider 名称列表（可截断）；
  - `data_source.selected_provider`：最终成功的 Provider 名称（若成功）；
  - `data_source.attempt_count`：尝试次数（含失败）。
- **Events**：每次尝试某 Provider 时记录 `provider.attempt`，属性含 `provider.name`、`success`（bool）、若失败则含 `error.type`。

### 5. Provider 层 Span

- **Span name**：如 `provider.fetch`，或更具体 `akshare.fetch_stock_info`、`yfinance.fetch_kline`。
- **父 Span**：以路由层 Span 为父。
- **Attributes**：
  - `data_source.provider.name`：Provider 名称；
  - `ticker`、`market`、`period`（若适用）；
  - 可选：`data_source.external.api`（如 "akshare.stock_individual_info_em"）。
- **Events**：外部 API 调用开始/结束；若发生异常，记录 `exception`（类型、message，不含堆栈到生产日志可根据策略脱敏）。

### 6. 错误与异常记录

- **Span status**：当请求失败（4xx/5xx 或业务失败）时，将 Span 状态设为 `Error`，并可选设置 `status_description`。
- **Exception event**：记录 `exception` 事件，包含 exception 类型与 message；是否包含 stack trace 由策略与合规要求决定。
- **Attributes**：在发生错误的 Span 上增加 `error`：true、`http.status_code`（若已确定），便于筛选与告警。

## TraceId 与响应头

- **响应头**（可选）：在 HTTP 响应中增加 `X-Trace-Id`（或 `traceparent` 中的 trace-id 部分），便于调用方在日志或工单中引用同一 Trace。
- **日志关联**：应用日志中应包含 `trace_id`、`span_id`（或等效字段），便于与追踪系统关联查询。

## 依赖与版本

- **OpenTelemetry API**：使用官方 API 包（如 `opentelemetry-api`），保证与多种实现兼容。
- **Instrumentation**：若使用 HTTP 框架（如 FastAPI、Express），优先使用官方或社区认可的 Auto-instrumentation；对 Router 与 Provider 调用处使用手动 Span 打点，保证业务语义清晰。
- **版本**：遵循 OpenTelemetry 语义约定 1.x 与 W3C Trace Context；具体 SDK 版本由实现锁定，并在文档中注明。

## 实现检查清单

- [ ] TracerProvider 初始化，并配置 OTLP 或其它导出器；
- [ ] 入站 HTTP 请求提取 traceparent，并创建或延续 Trace；
- [ ] API 层为每个请求创建顶层 Span，并设置 http.* 与业务属性；
- [ ] 路由层在「选择并调用 Provider」处创建子 Span，并记录 provider 尝试与结果；
- [ ] Provider 层在「调用外部 API」处创建子 Span，并记录 provider 名称与关键参数；
- [ ] 异常时设置 Span 状态为 Error 并记录 exception 事件；
- [ ] 响应头或 body 中可选返回 TraceId，便于调用方关联；
- [ ] 日志中输出 trace_id/span_id，与追踪系统关联。
