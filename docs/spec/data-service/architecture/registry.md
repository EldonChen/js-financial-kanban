# 注册与发现机制

## 动态注册

- **注册时机**：系统启动时，从 [配置与凭证](../prd/05-config-auth.md) 读取「已启用」的 Provider 列表及凭证；逐个实例化 Provider（注入凭证、超时等），并调用 `Registry.register(provider)`。
- **唯一性**：每个 Provider 的 `name` 在 Registry 内唯一；同一 name 再次注册时，实现可选择**覆盖**（新实例替换旧实例）或**拒绝**（抛错/日志并忽略）。
- **热更新**（可选）：若产品要求在不重启进程的前提下增删 Provider，需提供 `unregister(name)` 与再次 `register(provider)` 的语义；此时需保证并发安全（如写锁）与路由层使用到的列表为最新快照。

## 发现接口

- **按名称**：`getByName(name)`，用于「指定 data_source」的请求与能力查询接口展示。
- **按市场与能力**：`getByMarket(market, feature)`，返回支持该市场且具备该能力的 Provider 列表，**已按 priority 排序**，供 Router 顺序尝试。
- **全量**：`getAll()`，用于能力查询接口（如 GET /providers/status）返回所有已注册 Provider 及元数据。

## 配置驱动

- 哪些 Provider 被启用、优先级、凭证等均来自配置（环境变量或配置文件）；**不**在代码中硬编码 Provider 列表。
- 新增数据源时：实现新 Provider 类 → 在配置中增加对应开关与凭证 → 启动或重载后自动注册，无需改 Registry/Router 核心代码（**开闭原则**）。

## 与 Router 的协作

- Router 不直接持有 Provider 实例列表；每次请求通过 Registry 的 `getByMarket` / `getByName` 获取候选，保证使用的是当前已注册的 Provider 集合（含热更新后的结果）。
