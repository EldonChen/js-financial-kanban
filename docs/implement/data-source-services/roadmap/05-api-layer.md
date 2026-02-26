# 模块 05：API 层

## 目标

对外暴露**契约规定的 REST API**，实现统一响应格式与错误码映射，并生成 OpenAPI 文档。

## 任务拆解

| 序号 | 任务 | 可验收产出 | 状态 |
|------|------|------------|------|
| 5.1 | 定义 app/api/schemas/：ApiResponse、Stock、Kline、StockBatchData、StockListData、KlineResponseData、ProviderInfo、CapabilityResponseData，与 spec/model/schemas.yaml 一致 | 请求/响应模型与契约一致，可生成 OpenAPI | 待开始 |
| 5.2 | 实现 GET /api/v1/providers/status（或 capabilities）：调用 Registry.getAll()，组装 ProviderInfo、market_coverage、feature_coverage；可选 is_available  per Provider | 响应符合 CapabilityResponseData，code=200 | 待开始 |
| 5.3 | 实现 GET /api/v1/stocks/{ticker}：query 支持 market、data_source；调用 AppService/Router；成功返回 data: Stock；失败 404/503，data: null | 符合 PRD 02 与 error-codes | 待开始 |
| 5.4 | 实现 POST /api/v1/stocks/batch：body tickers[]，query market、data_source；返回 data: Record<ticker, Stock|null>，key 集与请求 tickers 一致 | 符合 PRD 02 | 待开始 |
| 5.5 | 实现 GET /api/v1/stocks/list：query market 必填，data_source 可选；返回 data: { tickers, market, data_source }；缺 market 返回 400 | 符合 PRD 02 | 待开始 |
| 5.6 | 实现 GET /api/v1/kline/{ticker}：query period、start_date、end_date、market、data_source；period 默认 1d，枚举校验；返回 data: KlineResponseData；非法 period/日期 400 | 符合 PRD 03 | 待开始 |
| 5.7 | 统一异常处理：捕获业务异常与未捕获异常，映射为 400/404/429/503，body 为 { code, message, data: null [, detail] }；不含凭证明文与堆栈 | 符合 spec/error/error-codes.md 与 exception-handling.md | 待开始 |
| 5.8 | 启用 FastAPI OpenAPI（/docs、/openapi.json），标签与描述与契约一致 | 文档可读且与 API 一致 | 待开始 |

## 依赖关系

- 依赖 **04-router-normalization**（AppService 与 Router 可用）。

## 注意事项

- API 路径与 PRD 一致；若 spec 中路径为单数/复数混用，以 spec 为准。
- period 别名（如 daily→1d）在 API 层或 Router 层归一化后传给 Provider。

## 任务状态

- 整体状态：**待开始**
- 最后更新：-
