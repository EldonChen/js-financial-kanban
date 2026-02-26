# 错误码规范

## 约定

- **HTTP 状态码**：与业务语义对齐，便于网关与客户端统一处理。
- **body.code**：与 HTTP 保持一致或扩展业务子码；成功为 200，失败为下表定义值。
- **body.message**：简短、可读、不暴露内部实现；可附带 `detail` 或 `trace_id`（见 [observability](../observability/opentelemetry.md)）。

## 错误码表

| code | HTTP Status | 含义 | 典型场景 |
|------|-------------|------|----------|
| 200 | 200 OK | 成功 | 正常返回 data |
| 400 | 400 Bad Request | 请求参数错误 | 缺少必填参数、格式错误、period 非法、日期格式错误 |
| 404 | 404 Not Found | 资源不存在 | 单只股票未找到、指定 data_source 的 Provider 未注册或不支持当前请求 |
| 429 | 429 Too Many Requests | 请求过于频繁 | 触发应用层或下游数据源限流 |
| 503 | 503 Service Unavailable | 服务不可用 | 所有候选 Provider 均失败、超时、或无可用数据源 |

## 扩展字段（可选）

错误响应 body 可包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 同上 |
| message | string | 简短描述 |
| data | null | 失败时固定为 null |
| detail | string \| object | 可选，参数错误时可列出 missing_fields、invalid_values 等 |
| trace_id | string | 可选，与 OpenTelemetry TraceId 一致，便于全链路排查 |

## 使用场景细则

### 400 Bad Request

- 缺少必填：如 GET /stocks/list 未传 `market`。
- 参数格式错误：如 `period` 非枚举值、`start_date` 非 YYYY-MM-DD。
- 业务规则不满足：如日期区间超过允许范围（若实现有上限）。

### 404 Not Found

- 单只股票元信息：所有候选 Provider 均未返回有效数据（或明确返回「不存在」）。
- 指定 data_source 时：该 Provider 未注册、不可用、或不支持当前 market/feature。
- 能力查询接口通常不返回 404；仅当服务不可用时返回 503。

### 429 Too Many Requests

- 应用层限流：如每 IP/每 Key 的 QPS 超限。
- 下游限流透传：Provider 调用外部 API 触发限流时，可返回 429 并在 message 中说明（如「数据源限流，请稍后重试」）。

### 503 Service Unavailable

- 无可用 Provider：启动时校验「至少一个第一优先级」未通过，或运行中所有 Provider 均不可用。
- 请求级失败：某次请求在所有候选 Provider 上均超时、异常或返回空，且无 fallback 成功。
- 配置/依赖故障：如无法连接下游、凭证失效等，由实现决定返回 503 或 500。

## 与 PRD 的对应

- [01-capability-query](../prd/01-capability-query.md)：查询失败时 503。
- [02-stock-meta](../prd/02-stock-meta.md)：参数错误 400；未找到/全部失败 404 或 503。
- [03-kline](../prd/03-kline.md)：同上；限流 429。
- [04-provider-registry](../prd/04-provider-registry.md)：容错耗尽返回 503/404。
- [05-config-auth](../prd/05-config-auth.md)：启动校验失败可记录错误并退出进程，或健康检查返回 503。
