# 股票元信息与列表 - 验收方案

对应 SPEC： [PRD 02 - 股票元信息与列表](../../../spec/data-source-service/prd/02-stock-meta.md)、[model/schemas.yaml - Stock, StockBatchData, StockListData](../../../spec/data-source-service/model/schemas.yaml)。

## 验收方法

1. **自动化**：API 测试对 GET /api/v1/stocks/{ticker}、POST /api/v1/stocks/batch、GET /api/v1/stocks/list 发起正常与异常请求，断言状态码、body 结构、data 内容。
2. **手工**：使用 curl/Postman 调用上述接口，检查响应与契约一致。
3. **契约**：成功响应中 `data` 符合 schemas.yaml 中 Stock / StockBatchData / StockListData。

## 验收标准

### 单只股票元信息 GET /api/v1/stocks/{ticker}

- [ ] **AC-1** 合法 ticker 且至少一个 Provider 返回有效数据时，返回 200，`data` 为单个 Stock 对象，且包含必填字段 ticker、name、data_source。
- [ ] **AC-2** 未指定 `data_source` 时，按 market 与优先级选择 Provider；未指定 market 时，按实现约定尝试直至成功或耗尽。
- [ ] **AC-3** 指定 `data_source` 时，仅向该 Provider 转发；若该 Provider 未注册或不支持当前 market/feature，返回 404 或 503 及明确错误信息。
- [ ] **AC-4** 所有候选 Provider 均未返回有效数据时，返回 404 或 503，`data` 为 null。
- [ ] **AC-5** 返回的 Stock 符合 schemas.yaml（必填与可选字段），且 `data_source` 为实际提供数据的 Provider 名称；缺失字段为 null 或省略。

### 批量股票元信息 POST /api/v1/stocks/batch

- [ ] **AC-6** 请求体含合法 `tickers`（非空数组）时，按与单只相同的路由与转发规则执行；响应 `data` 为 `Record<ticker, Stock | null>`，key 集合与请求 `tickers` 一致。
- [ ] **AC-7** 缺少 `tickers` 或格式非法时，返回 400 及参数错误说明。
- [ ] **AC-8** 每个非 null 的 value 符合 Stock 模型，且 `data_source` 正确。

### 股票列表 GET /api/v1/stocks/list

- [ ] **AC-9** 提供 query `market` 时，返回 200，`data` 至少包含 `tickers`（字符串数组）、`market`、`data_source`。
- [ ] **AC-10** 未提供 `market` 时，返回 400，要求必填参数。
- [ ] **AC-11** 所选 Provider 不支持列表能力时，尝试其他支持该市场的 Provider，或全部不可用时返回 503。

### 通用

- [ ] **AC-12** 所有成功返回的股票元信息符合 [Stock schema](../../../spec/data-source-service/model/schemas.yaml)；不返回 schema 未定义字段；原始数据缺失的字段在统一模型中为 null 或省略。
