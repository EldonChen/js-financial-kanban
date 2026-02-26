# PRD - Provider 注册与路由模块

## 模块概述

数据源服务采用**插件式架构**：外部数据源通过 **Provider** 适配并**动态注册**到运行时；**路由/转发层**根据请求的 market、data_source、能力（feature）与优先级**动态调度**到合适 Provider，并在失败时**容错切换**。本模块规定注册方式、路由规则、能力维度与可扩展性要求。

## EARS 需求

### 动态注册

- **When** 系统启动或配置重载时，**the system shall** 根据 [配置与凭证规范](05-config-auth.md) 读取已启用的 Provider 列表，逐个实例化并执行**注册**（如调用 `Registry.register(provider)`）；每个 Provider 具有唯一 `name`，重复名称由实现约定为覆盖或报错。
- **The system shall** 支持在**不重启进程**的前提下通过配置热更新或管理接口增加/移除 Provider（可选，由实现决定）；若支持，**then** 需在 [架构-注册与发现](../architecture/registry.md) 中说明。
- **If** 某 Provider 依赖的凭证未配置或无效，**then** the system shall 不注册该 Provider 或将其标记为不可用，并记录警告日志。

### 能力维度与接口

- **When** 注册 Provider 时，**the system shall** 要求每个 Provider 声明其支持的能力（feature），至少包括：`stock_info`、`stock_list`、`kline` 中的若干项；不支持的能力不得被路由层派发到该 Provider。
- **The system shall** 保证路由层仅将「股票元信息/列表」请求派发至声明了 `stock_info` 或 `stock_list` 的 Provider，将「历史 K 线」请求派发至声明了 `kline` 的 Provider，**while** 遵守 [架构-接口定义](../architecture/interfaces.md) 中的能力契约。
- **Where** 某 Provider 仅实现部分能力（如 easyquotation 仅行情），**the system shall** 在能力查询接口中正确暴露其 feature 集合，并在路由时跳过不具备该能力的 Provider。

### 按市场与优先级路由

- **When** 请求未指定 `data_source` 时，**the system shall** 根据请求中的 `market`（若有）筛选出 `supported_markets` 包含该市场的 Provider，再按 `priority` 升序排序，依次尝试直至某 Provider 返回有效结果或全部失败。
- **When** 请求指定了 `data_source` 时，**the system shall** 仅将请求派发至该名称的 Provider；若该 Provider 未注册、不可用或不支持当前 market/feature，返回 404 或 503。
- **The system shall** 在同等优先级下约定排序规则（如按注册顺序），保证行为可复现；文档见 [架构-路由规则](../architecture/routing.md)。

### 容错与重试

- **If** 当前选中的 Provider 调用失败（异常、超时、返回空），**then** the system shall 按优先级尝试下一个候选 Provider，**until** 某次成功或候选耗尽；耗尽时返回 503 或 404，并符合 [错误码规范](../error/error-codes.md)。
- **The system shall** 支持可配置的请求超时与重试次数（见 [05-config-auth](05-config-auth.md)）；单次 Provider 调用超时后视为失败并进入容错流程。
- **Where** 实现重试，**the system shall** 在重试前区分「可重试错误」与「不可重试错误」（如 4xx 参数错误），仅对可重试错误进行重试，避免无效请求重复下发。

### 可扩展性

- **The system shall** 允许在不修改路由核心逻辑的前提下，通过**新增 Provider 实现类 + 配置启用**扩展新数据源；新 Provider 只需实现 [架构-接口定义](../architecture/interfaces.md) 并满足能力与市场声明。
- **The system shall** 保证新增能力类型（feature）时，仅需扩展接口与路由的 feature 枚举及能力查询响应结构，现有 Provider 可声明不支持新能力，保持向后兼容。
