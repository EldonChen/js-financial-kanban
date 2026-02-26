# 路由与转发规则

路由层根据请求参数**动态选择** Provider 并转发请求；选择顺序与容错行为必须可预测、可配置。

## 输入维度

| 参数 | 来源 | 说明 |
|------|------|------|
| `data_source` | 请求 query/body | 指定使用的 Provider 名称；若存在则优先使用，且仅尝试该 Provider |
| `market` | 请求 query/body | 市场（A股/港股/美股等），用于筛选 supported_markets |
| `feature` | 隐含 | 由 API 路径决定：stocks/* → stock_info / stock_list，kline/* → kline |

## 选择逻辑

### 1. 指定 data_source

- **When** 请求中带有有效 `data_source`（即该名称已注册）：
  - 仅将请求派发给该 Provider。
  - **If** 该 Provider 不支持当前 market（若请求带 market）或当前 feature，**then** 返回 404 或 503，不再尝试其他 Provider。
  - **If** 该 Provider 不可用（如 isAvailable() 为 false）或调用失败，**then** 返回 503 或 404，不 fallback 到其他 Provider（因调用方显式指定了数据源）。

### 2. 未指定 data_source

- **Step 1** 筛选：从 Registry 中取出「支持当前 feature 且支持当前 market（若请求带 market）」的 Provider 列表。
- **Step 2** 排序：按 `priority` 升序；同优先级按实现约定（如注册顺序）稳定排序。
- **Step 3** 依次调用：按顺序调用当前 Provider；若返回有效结果则立即返回；若失败（异常、超时、空结果）则尝试下一个。
- **Step 4** 耗尽：若所有候选均失败，返回 503 或 404，`data` 为 null 或空，并记录日志与 [错误码](../error/error-codes.md)。

### 3. 无 market 的请求

- **When** 请求未带 `market`（如仅传 ticker）：
  - 筛选时不过滤 `supported_markets`，即所有支持该 feature 的 Provider 均可作为候选。
  - 排序与容错逻辑同上；实现可约定「先尝试某默认市场」或按优先级全量尝试。

## 能力与路径映射

| API 路径/能力 | feature | 派发对象 |
|---------------|---------|----------|
| GET /stocks/{ticker}、POST /stocks/batch | stock_info | IStockMetaProvider |
| GET /stocks/list | stock_list | IStockMetaProvider（需声明 stock_list） |
| GET /kline/{ticker} | kline | IKlineProvider |

- Provider 必须在 `features` 中声明对应能力，否则不进入候选列表。

## 超时与重试

- 单次 Provider 调用应用 [配置](../prd/05-config-auth.md) 中的超时时间；超时视为失败，进入「尝试下一个」流程。
- 重试：仅对「当前 Provider 的可重试错误」进行重试，次数不超过配置；不可重试错误（如 4xx 参数错误）不重试，直接尝试下一个或返回错误。
