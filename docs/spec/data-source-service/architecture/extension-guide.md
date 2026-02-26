# 扩展指南：新 Provider 适配 与 新能力定义

本文说明在现有架构下：**如何接入一个新 Provider**，以及 **如何定义一种新能力（feature）并让已有/新数据结构适配该能力**。

---

## 一、如何适配一个新的 Provider

「新 Provider」指一个新的外部数据源（例如 Tushare、Finnhub、Wind 等），需要被数据源服务统一接入，参与路由与容错。

### 1.1 前提与约束

- 新 Provider 提供的能力必须是**已有 feature 之一**（如 `stock_info`、`stock_list`、`kline`），或你先完成「二、定义新能力」再按本节的 1.2～1.5 接入。
- 路由、注册表、API 层**不修改**，只做「新实现类 + 配置」。

### 1.2 步骤总览

| 步骤 | 做什么 | 涉及文件/位置 |
|------|--------|----------------|
| 1 | 实现接口并做字段映射 | 新建 `XxxProvider` 类 + 可选 `XxxFieldMapper` |
| 2 | 将原始响应映射为统一模型 | 输出符合 `model/schemas.yaml` 的 Stock / Kline |
| 3 | 在启动/注册逻辑里根据配置实例化并注册 | 配置 + Registry.register(provider) |
| 4 | 配置启用与凭证 | 环境变量或配置文件 |
| 5 | 可选：补充单元测试与文档 | tests + docs |

以下按步骤展开。

### 1.3 步骤 1：实现接口

新 Provider 必须实现架构里定义的**能力接口**（见 [interfaces.md](interfaces.md)）：

- 若只提供**股票元信息/列表**：实现 `IStockMetaProvider`（并满足 `IProviderMetadata`）。
- 若只提供**历史 K 线**：实现 `IKlineProvider`。
- 若两者都提供：同一个类实现两个接口即可。

**必须提供的元数据**（IProviderMetadata）：

- `name`：唯一标识，如 `"tushare"`，用于路由中的 `data_source` 与能力查询。
- `supported_markets`：如 `["A股"]`。
- `priority`：数字，越小越优先；可与现有 akshare/yfinance 对齐（如 1=免费优先，2=需凭证）。
- `features`：如 `["stock_info", "stock_list", "kline"]`，声明自己支持哪些能力。

**必须实现的方法**（以 IStockMetaProvider 为例）：

- `fetchStockInfo(ticker, market?)` → 返回 `Stock | null`，且 `Stock.data_source === this.name`。
- `fetchStockList(market?)` → 返回 `string[]`；若不支持列表可返回 `[]` 或抛「不支持」由路由层处理。
- `fetchStockBatch(tickers, market?)` → 可选；未实现则路由层可回退到循环调用 `fetchStockInfo`。
- `isAvailable()` → 健康检查，如发一次探测请求。

实现时内部会：

- 调用**外部 API**（HTTP/ SDK/ 库）。
- 把**原始响应**通过字段映射转成 [model/schemas.yaml](../model/schemas.yaml) 里的 **Stock**（或 **Kline**）；缺失字段填 `null`，不新增 schema 未定义字段。

### 1.4 步骤 2：字段映射到统一模型

- **已有类型（Stock / Kline）**：新 Provider 的返回必须符合现有 schema；在 Provider 内部或独立 Mapper 里实现「原始响应 → Stock / Kline」。
- 若该数据源有**特有字段**且你暂时不想扩展 schema：只映射到现有字段，特有信息可丢弃或仅在日志中使用；后续若需要对外暴露，再走「二、定义新能力」扩展模型与 API。

这样「适配新 Provider」不会改变对外契约，只是多了一个实现类。

### 1.5 步骤 3：注册到 Registry

- 在**启动/初始化**流程中（与现有 akshare、yfinance 一样）：
  - 从配置读取「是否启用该 Provider、优先级、凭证」；
  - 若启用且凭证有效，则 `new TushareProvider(...)` 并 `registry.register(provider)`。
- **不修改** Router、不修改「按 market/feature 查候选」的逻辑；Registry 的 `getByMarket(market, feature)` 会自动把新 Provider 纳入候选（因为新类已声明 `supported_markets` 与 `features`）。

### 1.6 步骤 4：配置

- **环境变量**（或等价配置）：例如 `ENABLE_TUSHARE=true`、`TUSHARE_TOKEN=xxx`。
- 若该 Provider 需要**凭证**：校验规则与现有一致——启用则必须配置凭证，否则不注册并打 warning。
- 若需**覆盖默认优先级**：在配置里增加 `TUSHARE_PRIORITY=2` 等，由启动逻辑在构造 Provider 时传入。

完成后，新 Provider 会：

- 出现在 `GET /api/v1/providers/status` 的 `providers` 与 `market_coverage` / `feature_coverage` 中。
- 在未指定 `data_source` 时，按 market + priority 参与路由；在指定 `data_source=tushare` 时被直接选用。

### 1.7 小结：适配新 Provider 的清单

- [ ] 新建实现类，实现 `IStockMetaProvider` 和/或 `IKlineProvider`，并满足 `IProviderMetadata`。
- [ ] 在类内部（或独立 Mapper）将原始响应映射为 **Stock** / **Kline**，不破坏现有 schema。
- [ ] 在启动/注册处根据配置实例化并 `registry.register(provider)`。
- [ ] 增加配置项（开关、凭证、可选优先级）。
- [ ] 不修改 Router、不修改 API 路径、不修改统一模型 schema。

---

## 二、如何定义一个新能力，并使已有数据结构适配该能力

「新能力」指一种新的**业务能力维度**（在架构里对应新的 **feature**），例如：实时行情、财务指标、板块成分等。需要：**在路由与注册表中识别该 feature**，并决定**用已有模型还是新模型**来承载返回数据。

### 2.1 两种常见情况

| 情况 | 说明 | 数据适配方式 |
|------|------|----------------|
| A. 新能力复用已有模型 | 新能力返回的数据形状与现有某类型一致（如「实时行情」用类似 Stock 的字段） | 复用 **Stock**（或现有 DTO），在 schema 中可扩展可选字段；API 返回 `data` 仍为该类型。 |
| B. 新能力需要新形状 | 新能力返回的结构与现有 Stock/Kline 差异大（如「财务指标列表」「板块成分」） | 在 **model/schemas.yaml** 中**新增 schema**（如 `FinancialReport`、`SectorConstituents`），并新增对应 API 与路由能力。 |

下面分「定义 feature → 扩展接口与路由 → 数据模型适配」三步说明。

### 2.2 步骤 1：在领域里定义新 feature

1. **给 feature 起名**  
   例如：`realtime_quote`（实时行情）、`financials`（财务指标）、`sector_constituents`（板块成分）。与现有 `stock_info`、`stock_list`、`kline` 同级，都是「能力维度」。

2. **确定该 feature 的「一次请求」的语义**  
   - 输入：例如 ticker + market、或 sector_id、或 report_type。  
   - 输出：是「单个对象」「列表」还是「分页列表」。  
   这决定了后面 API 的路径与响应 body 结构（见 2.4）。

3. **决定用已有类型还是新类型**  
   - **能用已有类型**：例如实时行情可以「用 Stock 加若干可选字段」或「用 Kline 表示最新一根」——则只需在现有 **Stock** / **Kline** 上增加**可选字段**（OpenAPI 里仍兼容），Provider 按新字段填充即可。  
   - **必须用新类型**：例如财务指标是「报表类型 + 多条指标」，和 Stock/Kline 结构不同——则在 **model/schemas.yaml** 里**新增一个 schema**（如 `FinancialReport`），并让该 feature 的 API 返回 `data: FinancialReport` 或 `data: FinancialReport[]`。

### 2.3 步骤 2：扩展接口与路由（使「已有数据结构」或「新结构」都能被该能力使用）

1. **在 Provider 层增加对新 feature 的声明与实现**  
   - 在 **IProviderMetadata** 的 `features` 中允许新值，如 `realtime_quote`。  
   - 若新能力**复用已有模型**（如用 Stock 表示实时行情）：  
     - 可以**扩展现有接口**，例如在 `IStockMetaProvider` 中增加 `fetchRealtimeQuote(ticker, market?) => Promise<Stock | null>`；  
     - 或者**新接口**，例如 `IRealtimeQuoteProvider { fetchRealtimeQuote(...) }`，返回类型仍是 **Stock**（或你在 Stock 上扩展的可选字段）。  
   - 若新能力**需要新形状**：  
     - 定义**新接口**，如 `IFinancialsProvider { fetchFinancials(ticker, reportType?) => Promise<FinancialReport[] | null> }`，返回类型为 **FinancialReport**（在 model 里新增的 schema）。

2. **在 Registry 中支持按新 feature 查候选**  
   - `getByMarket(market, feature)` 的 `feature` 枚举中增加 `realtime_quote` / `financials` 等。  
   - 这样「请求实时行情」时，路由层会选出 `features` 包含 `realtime_quote` 的 Provider，并调用其 `fetchRealtimeQuote`（或你约定的方法名）。

3. **在 Router 中增加对新能力的转发**  
   - 新增方法，如 `fetchRealtimeQuote(ticker, market?, dataSource?)` 或 `fetchFinancials(ticker, reportType?, dataSource?)`。  
   - 实现与现有逻辑一致：解析 `dataSource` / market → 从 Registry 取候选（按新 feature）→ 按优先级依次调用 Provider 的新方法 → 容错与返回。  
   - 这样**已有数据结构**（如 Stock）或**新结构**（如 FinancialReport）都会通过同一套路由与容错机制返回给上层。

4. **在能力查询接口中暴露新 feature**  
   - `GET /api/v1/providers/status` 的 `feature_coverage` 中增加键 `realtime_quote` / `financials`，值为「支持该 feature 的 Provider 名称列表」。  
   - 这样调用方知道「谁支持实时行情 / 财务指标」，便于选择是否传 `data_source`。

### 2.4 步骤 3：数据模型适配（已有结构 vs 新结构）

- **已有结构适配新能力（例如用 Stock 表示实时行情）**  
  - 在 **model/schemas.yaml** 的 **Stock** 中增加**可选字段**（如 `last_price`、`change_pct`、`updated_at`），保证向后兼容。  
  - 实现新能力的 Provider 在映射时填充这些字段；旧能力（如 `stock_info`）可不填，仍符合 schema。  
  - API 响应仍为 `data: Stock`（或 `Stock[]`），无需新类型；调用方根据「是否调用的是实时行情接口」来理解字段含义。

- **新结构承载新能力（例如财务指标）**  
  - 在 **model/schemas.yaml** 中**新增** schema，例如：

    ```yaml
    FinancialReport:
      type: object
      required: [ticker, report_type, period]
      properties:
        ticker: { type: string }
        report_type: { type: string }   # e.g. "income", "balance"
        period: { type: string }         # e.g. "2024Q1"
        items: { type: array, items: { type: object } }  # 指标键值对
        data_source: { type: string }
    ```

  - 新 API 的响应约定为 `data: FinancialReport[]`（或分页结构）；Router 与 Provider 新接口的返回类型与该 schema 一致。  
  - 这样「新能力」有**专属数据结构**，同时与现有 Stock/Kline 并列，都受 OpenAPI 约束，便于生成客户端与校验。

### 2.5 小结：定义新能力并适配数据结构的清单

- [ ] 在领域内定义新 feature 名称与请求/响应语义。  
- [ ] 决定用**已有类型（扩展可选字段）**还是**新 schema**；在 model/schemas.yaml 中完成扩展或新增。  
- [ ] 在 Provider 层增加对新 feature 的接口（扩展现有接口或新接口），返回类型为已有类型或新类型。  
- [ ] 在 IProviderMetadata.features 与 Registry/Router 中支持新 feature 的查询与转发。  
- [ ] 在能力查询 API 的 feature_coverage 中暴露新 feature。  
- [ ] 新增或扩展 API 路径，响应 body 的 `data` 符合所选 schema（已有或新）。

---

## 三、对照表：新 Provider vs 新能力

| 维度 | 适配一个新 Provider | 定义一个新能力并适配数据 |
|------|----------------------|----------------------------|
| **目标** | 多一个数据源实现，参与现有能力的路由 | 多一种业务能力（新 feature），可复用或新数据结构 |
| **是否改 schema** | 一般不改；新 Provider 输出符合现有 Stock/Kline | 可选：扩展 Stock/Kline 可选字段，或新增 schema |
| **是否改接口** | 不改；新类实现现有 IStockMetaProvider/IKlineProvider | 要改：新方法或新接口 + Registry/Router 支持新 feature |
| **是否改 API 路径** | 不改；沿用现有 /stocks/*、/kline/* | 通常要加：如 GET /realtime-quote/:ticker 或 /financials/:ticker |
| **是否改配置** | 要加：新 Provider 的开关、凭证、优先级 | 一般只需在代码/SPEC 中枚举新 feature，配置可沿用现有 |

这样你可以清楚区分：**加一个数据源**只做「实现类 + 注册 + 配置」；**加一种能力**要做「feature 枚举 + 接口/路由 + 数据模型（已有扩展或新 schema）+ 新或扩展 API」。
