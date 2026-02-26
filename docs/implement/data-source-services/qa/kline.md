# 历史 K 线 - 验收方案

对应 SPEC： [PRD 03 - 历史 K 线](../../../spec/data-source-service/prd/03-kline.md)、[model/schemas.yaml - Kline, KlineResponseData](../../../spec/data-source-service/model/schemas.yaml)。

## 验收方法

1. **自动化**：API 测试对 `GET /api/v1/kline/{ticker}` 发起多种参数组合（period、start_date、end_date、market、data_source），断言状态码、body 结构、data 中 K 线数组与单条 K 线结构。
2. **手工**：curl/Postman 调用，检查日期格式、period 枚举、排序与字段。
3. **契约**：成功响应中 `data` 符合 KlineResponseData，单条 K 线符合 Kline schema。

## 验收标准

### 查询入口与参数

- [ ] **AC-1** 路径为 `GET /api/v1/kline/{ticker}`（或契约约定），支持 query：`period`（可选，默认 `1d`）、`start_date`、`end_date`、`market`、`data_source`。
- [ ] **AC-2** `period` 支持枚举：1m、5m、15m、30m、60m、1d、1w、1M；若支持别名（如 daily），则规范化为上述枚举后再转发。
- [ ] **AC-3** `period` 不在支持范围或格式非法时，返回 400 及参数错误说明。
- [ ] **AC-4** 日期参数使用 YYYY-MM-DD 解析；格式错误时返回 400。

### 路由与能力

- [ ] **AC-5** 仅将请求派发至已实现 K 线能力且支持该市场（若指定）及周期的 Provider；指定 `data_source` 时仅派发至该 Provider。
- [ ] **AC-6** 无任何 Provider 支持当前请求的市场/周期组合，或所有候选均失败时，返回 503 或 404，`data` 为 null 或空结构，符合 error 规范。

### 响应格式

- [ ] **AC-7** 成功响应中 `data` 包含：ticker、period、data（K 线数组）、data_source；单条 K 线包含 date、open、high、low、close、volume 及可选的 amount、adj_close、timestamp、data_source。
- [ ] **AC-8** 单条 K 线符合 [Kline schema](../../../spec/data-source-service/model/schemas.yaml)；可选字段缺失时为 null 或省略。
- [ ] **AC-9** `data` 数组按时间升序排列（由实现约定）。

### 边界与限流

- [ ] **AC-10** 日期区间过大导致下游超时或拒绝时，返回 400 或 503，message 或 detail 可说明原因。
- [ ] **AC-11** 下游限流时按 error 规范返回 429 或 503，并在 Provider/配置中注明限流与退避策略。
