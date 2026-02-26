# API 与错误处理规范

与 [spec/error/error-codes.md](../../../spec/data-source-service/error/error-codes.md)、[spec/error/exception-handling.md](../../../spec/data-source-service/error/exception-handling.md) 一致，并给出实现层面的约定。

## 统一响应格式

- **成功**：`{ "code": 200, "message": "success", "data": <业务数据> }`。  
- **失败**：`{ "code": <错误码>, "message": "<简短描述>", "data": null }`；可选 `detail`（对象或字符串）、`trace_id`（与 OpenTelemetry 一致时便于排查）。  
- **不返回**：凭证明文、内部路径、堆栈信息给调用方。

## 错误码与 HTTP 状态映射

| code | HTTP Status | 使用场景 |
|------|-------------|----------|
| 200 | 200 OK | 正常返回 data |
| 400 | 400 Bad Request | 缺少必填参数、格式错误、period 非法、日期格式错误 |
| 404 | 404 Not Found | 单只股票未找到、指定 data_source 的 Provider 未注册或不支持当前请求 |
| 429 | 429 Too Many Requests | 应用层或下游数据源限流 |
| 503 | 503 Service Unavailable | 所有候选 Provider 均失败、超时、或无可用数据源；启动校验失败时也可 503 |

实现时在 API 层（或统一异常处理中间件）捕获业务异常与未捕获异常，映射为上述 code 与 HTTP 状态，并封装为统一 body。

## 异常分类与处理策略

| 类型 | 是否可重试 | 处理 |
|------|------------|------|
| 参数校验异常 | 否 | 400，message 描述缺失或非法参数 |
| 资源不存在 / 指定 data_source 不可用 | 否 | 404 或 503 |
| 限流 | 是（稍后重试） | 429 |
| 超时 / 下游不可用 | 是 | 路由层尝试下一 Provider 或最终 503 |
| 下游 4xx | 否 | 不重试当前 Provider，尝试下一个或返回 400/404 |
| 配置/启动错误 | 否 | 启动失败或健康检查 503 |

Router 层：不向上抛出业务异常，直至某 Provider 成功或全部耗尽；耗尽时返回 null 或抛出「无可用数据」类异常，由 API 层映射为 404/503。  
Provider 层：不泄露凭证明文；可抛出「当前数据源不可用」或返回 null/空数组。

## 日志约定

- **级别**：参数错误 400 可 INFO/WARN；404/503 用 WARN；未捕获异常用 ERROR。  
- **内容**：至少包含请求标识（如 trace_id）、错误类型、必要时 provider.name、ticker、market；不记录敏感信息。  
- **与可观测性**：异常时在 Span 上记录 exception（若已集成 OpenTelemetry），便于追踪与告警。

## 安全

- 凭证、API Key、Token 不写入日志、错误 message、响应 body。  
- 对外 message 简短、可读、不暴露内部实现细节。
