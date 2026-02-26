# 设计模式与软件架构

## 采用的模式

### 1. 策略模式 (Strategy)

- **场景**：不同数据源对「获取股票信息」「获取 K 线」的实现策略不同。
- **实现**：`IStockMetaProvider` / `IKlineProvider` 为策略接口；AkshareProvider、YFinanceProvider 等为具体策略。Router 在运行时根据 market、data_source、优先级选择并调用对应策略，调用方（API 层）不关心具体是哪个数据源。
- **收益**：新增数据源 = 新增策略类，符合开闭原则。

### 2. 注册表模式 (Registry)

- **场景**：Provider 集合动态变化，需按名称、市场、能力查询。
- **实现**：`IRegistry` 维护 name → Provider 的映射，以及 market/feature 的索引（如 market → List<Provider> 按 priority 排序）。注册/注销在启动或热更新时完成；Router 仅依赖 IRegistry 查询，不依赖具体 Provider 列表。
- **收益**：集中管理插件生命周期，便于扩展与测试（可注入 Mock Registry）。

### 3. 适配器模式 (Adapter)

- **场景**：外部 API（yfinance、akshare、Tushare 等）的请求/响应格式各异，需统一为内部模型。
- **实现**：每个 Provider 实现类即一个适配器：将「统一请求参数」转为外部 API 的调用方式，将「外部 API 响应」经 `IFieldMapper`（或内聚的 map 逻辑）转为 [Stock](../model/schemas.yaml) / [Kline](../model/schemas.yaml)。
- **收益**：外部数据源变更仅影响对应适配器，不影响路由与 API 契约。

### 4. 模板方法（可选）

- **场景**：多个 Provider 的「调用 → 映射 → 返回」流程一致，仅「调用外部 API」与「映射函数」不同。
- **实现**：可定义抽象基类，模板方法为 `fetchStockInfo`，子类实现 `callExternalApi` 与 `mapToStock`；或保持显式组合（Provider 内聚调用 + Mapper），不强制继承。
- **收益**：减少重复代码，统一超时与错误处理。

### 5. 外观模式 (Facade)

- **场景**：API 层不需要感知 Router、Registry、Provider 的细节。
- **实现**：应用服务层（Application Service）对外暴露「按 ticker/market 获取股票」「按 ticker/period 获取 K 线」等粗粒度接口，内部编排 Router 调用、统一响应格式与错误码映射。
- **收益**：API 层与底层插件架构解耦，便于替换或扩展底层实现。

## 架构风格

- **插件式架构**：Provider 为可插拔组件，通过接口与 Registry 集成；核心（Router、Registry、API）稳定，扩展点（新 Provider）开放。
- **分层架构**：API → 应用服务 → Router → Provider → 外部数据源；依赖单向向下，避免循环依赖。
- **可观测性**：在 Router 与 Provider 边界注入 Trace/Span（见 [observability](../observability/opentelemetry.md)），便于全链路追踪与未来扩展为多实例/分布式。
