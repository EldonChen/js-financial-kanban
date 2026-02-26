# Provider 注册与路由 - 验收方案

对应 SPEC： [PRD 04 - Provider 注册与路由](../../../spec/data-source-service/prd/04-provider-registry.md)、[architecture/routing.md](../../../spec/data-source-service/architecture/routing.md)、[architecture/registry.md](../../../spec/data-source-service/architecture/registry.md)。

## 验收方法

1. **单元测试**：Registry 的 register、getByName、getByMarket（含 feature）、getAll；Router 在「指定 data_source」「未指定 data_source」「多 Provider 优先级与回退」下的行为。
2. **集成/API 测试**：通过 API 间接验证路由结果（如指定 data_source 时响应中的 data_source 与请求一致；未指定时可选验证优先级顺序）。
3. **手工**：修改配置启用/禁用某 Provider，重启后能力查询接口与业务接口行为符合预期。

## 验收标准

### 动态注册

- [ ] **AC-1** 系统启动或配置重载时，根据配置读取已启用 Provider 列表，逐个实例化并调用 Registry.register(provider)；每个 Provider 的 name 在 Registry 内唯一。
- [ ] **AC-2** 某 Provider 依赖的凭证未配置或无效时，不注册该 Provider 或标记为不可用，并记录警告日志。
- [ ] **AC-3** 可选：支持不重启进程的配置热更新或管理接口增删 Provider；若支持，文档说明并发与快照语义。

### 能力与接口

- [ ] **AC-4** 每个 Provider 声明 features（至少含 stock_info、stock_list、kline 的部分）；路由层仅将股票元信息/列表请求派发至声明了对应能力的 Provider，将 K 线请求派发至声明了 kline 的 Provider。
- [ ] **AC-5** 能力查询接口中暴露的 feature 集合与各 Provider 实际能力一致。

### 按市场与优先级路由

- [ ] **AC-6** 未指定 data_source 时，按 market（若有）筛选 supported_markets 包含该市场的 Provider，再按 priority 升序排序，依次尝试直至某 Provider 返回有效结果或全部失败。
- [ ] **AC-7** 指定 data_source 时，仅派发至该名称的 Provider；若未注册、不可用或不支持当前 market/feature，返回 404 或 503。
- [ ] **AC-8** 同等优先级下排序规则稳定、可复现（如注册顺序）。

### 容错与重试

- [ ] **AC-9** 当前 Provider 调用失败（异常、超时、空）时，按优先级尝试下一候选，直至某次成功或候选耗尽；耗尽时返回 503 或 404，符合 error 规范。
- [ ] **AC-10** 单次 Provider 调用应用配置的超时与最大重试次数；可重试错误重试后仍失败则下一 Provider；不可重试错误（如 4xx）不重试当前 Provider。

### 可扩展性

- [ ] **AC-11** 新增数据源仅需新增 Provider 实现类与配置启用，不修改 Router/Registry 核心逻辑。
- [ ] **AC-12** 新增能力类型（feature）时，仅需扩展接口与路由的 feature 枚举及能力查询响应，现有 Provider 可声明不支持新能力，保持向后兼容。
