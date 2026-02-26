# 抽象类与接口定义

以下为数据源服务核心抽象，实现方须满足接口契约；语言中立描述，实现时映射为具体语言（如 Python 的 ABC、TypeScript 的 interface）。

---

## 1. IProviderMetadata（元数据，所有 Provider 共有）

用于注册与路由的只读元信息，不包含具体请求能力。

| 成员 | 类型 | 说明 |
|------|------|------|
| `name` | string | 唯一标识，如 "akshare"、"yfinance" |
| `supported_markets` | string[] | 支持的市场，如 ["A股","港股"] |
| `priority` | int | 优先级，数字越小越高 |
| `features` | string[] | 支持的能力：stock_info、stock_list、kline 等 |

约束：同一 Registry 内 `name` 唯一；`features` 决定路由层是否将对应类型请求派发给该 Provider。

---

## 2. IStockMetaProvider（股票元信息与列表）

具备「单只元信息、批量元信息、股票列表」能力的 Provider 必须实现本接口（或等价能力的方法集合）。

| 方法 | 签名（语义） | 说明 |
|------|--------------|------|
| `fetchStockInfo` | (ticker: string, market?: string) => Promise\<Stock \| null\> | 返回统一模型 Stock，失败或不存在返回 null |
| `fetchStockList` | (market?: string) => Promise\<string[]\> | 返回 ticker 列表；不支持则返回 [] 或抛「不支持」 |
| `fetchStockBatch` | (tickers: string[], market?: string) => Promise\<Record\<string, Stock \| null\>\> | 批量查询；可选实现，未实现则由路由层循环调用 fetchStockInfo |
| `isAvailable` | () => Promise\<boolean\> | 健康检查，如探测一次请求是否成功 |

- 实现类必须实现 **IProviderMetadata**（或通过组合提供相同字段）。
- 返回的 `Stock` 必须符合 [model/schemas.yaml - Stock](../model/schemas.yaml)；`data_source` 字段设为该 Provider 的 `name`。

---

## 3. IKlineProvider（历史 K 线）

具备「历史 K 线」能力的 Provider 必须实现本接口。

| 方法 | 签名（语义） | 说明 |
|------|--------------|------|
| `fetchKline` | (ticker: string, period: string, options?: { startDate?, endDate?, market? }) => Promise\<Kline[]\> | 返回统一模型 Kline 数组，按时间升序 |
| `isAvailable` | () => Promise\<boolean\> | 健康检查 |

- 实现类必须实现 **IProviderMetadata**，且 `features` 包含 `kline`。
- `period` 为规范后的枚举：1m、5m、15m、30m、60m、1d、1w、1M。
- 返回的每条 K 线符合 [model/schemas.yaml - Kline](../model/schemas.yaml)。

---

## 4. IRegistry（Provider 注册表）

负责 Provider 的**动态注册**与**按条件查询**，供 Router 使用。

| 方法 | 签名（语义） | 说明 |
|------|--------------|------|
| `register` | (provider: IStockMetaProvider | IKlineProvider) => void | 注册 Provider；同一 name 覆盖或报错由实现约定 |
| `unregister` | (name: string) => boolean | 按名称移除（可选，用于热更新） |
| `getByName` | (name: string) => T \| null | 按名称获取 |
| `getByMarket` | (market: string, feature?: string) => T[] | 返回支持该市场（及可选 feature）的 Provider 列表，按 priority 排序 |
| `getAll` | () => T[] | 返回所有已注册 Provider（用于能力查询接口） |

泛型 T 为同时满足 IProviderMetadata 与至少一种能力接口的类型；实现时可拆为 `getMetaProvidersByMarket` / `getKlineProvidersByMarket` 等。

---

## 5. IRouter（路由/转发）

根据请求参数选择 Provider 并执行调用，带容错（失败则尝试下一个）。

| 方法 | 签名（语义） | 说明 |
|------|--------------|------|
| `fetchStockInfo` | (ticker, market?, dataSource?) => Promise\<Stock \| null\> | 按 [routing.md](routing.md) 选 Provider，转发并返回 |
| `fetchStockBatch` | (tickers, market?, dataSource?) => Promise\<Record\<string, Stock \| null\>\> | 同上，批量 |
| `fetchStockList` | (market, dataSource?) => Promise\<string[]\> | 同上，列表 |
| `fetchKline` | (ticker, period, options?, dataSource?) => Promise\<Kline[]\> | 同上，K 线 |

- 实现依赖 **IRegistry** 与各 Provider 接口；内部逻辑：解析 dataSource/market/feature → 从 Registry 取候选列表 → 按优先级依次调用直至成功或耗尽。
- 超时、重试、错误分类（可重试/不可重试）见 [error](../error/exception-handling.md) 与 PRD 04。

---

## 6. IFieldMapper（字段映射，可选抽象）

将某数据源「原始响应」转为统一模型。可每 Provider 内聚实现，或抽成独立 Mapper 接口供多 Provider 复用。

| 方法（示例） | 签名（语义） | 说明 |
|--------------|--------------|------|
| `mapToStock` | (raw: unknown) => Stock | 原始响应 → Stock |
| `mapToKlineList` | (raw: unknown) => Kline[] | 原始响应 → Kline[] |

- 若某字段在原始数据中不存在，输出中对应属性为 null 或省略；不得返回未在 [model](../model/schemas.yaml) 中定义的字段。

---

## 实现约定

- **同一进程内**：Registry 与 Router 通常为单例；Provider 实例在启动时创建并注册。
- **多语言**：Python 使用 `abc.ABC` 与 `@abstractmethod`；TypeScript/Java 使用 `interface` 与 `implements`；命名可调整为符合语言习惯（如 snake_case）。
- **能力组合**：一个类可同时实现 `IStockMetaProvider` 与 `IKlineProvider`（如 AkshareProvider），并在 `features` 中声明两者。
