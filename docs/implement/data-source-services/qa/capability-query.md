# 能力查询模块 - 验收方案

对应 SPEC： [PRD 01 - 能力查询](../../../spec/data-source-service/prd/01-capability-query.md)、[model/schemas.yaml - CapabilityResponseData, ProviderInfo](../../../spec/data-source-service/model/schemas.yaml)。

## 验收方法

1. **自动化**：API 测试请求 `GET /api/v1/providers/status`（或契约约定的路径），断言状态码 200、body 结构、必填字段存在。
2. **手工**：启动服务后 curl/浏览器访问该路径，检查 JSON 可读性与内容合理性。

## 验收标准

- [ ] **AC-1** 接口路径与契约一致（如 `GET /api/v1/providers/status` 或 `GET /api/v1/providers/capabilities`），且为只读、无副作用。
- [ ] **AC-2** 响应为统一格式：`{ code: 200, message: "success", data: {...} }`；成功时 `code` 为 200。
- [ ] **AC-3** `data` 包含按 **provider 维度** 的信息：已注册数据源列表（名称唯一）、每个的 `supported_markets`、`priority`；若实现支持，可选 `available` 表示当前是否可用。
- [ ] **AC-4** `data` 包含按 **feature 维度** 的信息：至少 `feature_coverage` 或等价结构，键为能力标识（如 `stock_info`、`stock_list`、`kline`），值为支持该能力的 Provider 名称列表。
- [ ] **AC-5** `data` 包含 **market_coverage** 或等价结构：市场 → 数据源名称列表（建议按优先级排序）。
- [ ] **AC-6** `data.total_providers` 与 `data.providers` 的键数量一致；`data.providers` 的每个元素符合 ProviderInfo（name、supported_markets、priority、可选 features、可选 available）。
- [ ] **AC-7** 当服务不可用或查询过程发生未预期错误时，返回 503 及 `data: null`，符合 error 规范。
- [ ] **AC-8** 响应 JSON 可通过 spec/model/schemas.yaml 中 CapabilityResponseData、ProviderInfo 的约束校验（手工或工具校验）。
