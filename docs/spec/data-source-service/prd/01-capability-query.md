# PRD - 能力查询模块

## 模块概述

调用方需要获知当前数据源服务**已注册的数据源**以及各数据源**支持的能力（feature）**与**市场（market）**，以便决定如何发起后续请求（如是否指定 `data_source`、某市场是否可用）。本模块规定能力查询接口的行为与响应结构。

## EARS 需求

### 查询入口与路径

- **When** 调用方请求查询系统支持的数据源与能力时，**the system shall** 提供唯一入口路径（如 `GET /api/v1/providers/status` 或 `GET /api/v1/providers/capabilities`），由实现统一选定并在 API 文档中公布。
- **Where** 该接口为只读、无副作用，**the system shall** 不修改任何注册状态或配置，仅返回当前运行时的能力与数据源信息。

### 按 Provider 维度

- **When** 调用方请求能力查询时，**the system shall** 在响应中返回**按 provider 维度**的以下信息：
  - 已注册数据源列表（名称唯一标识）；
  - 每个数据源支持的市场（`supported_markets`）；
  - 每个数据源的优先级（`priority`，数字越小优先级越高）。
- **If** 某数据源已注册但当前不可用（如健康检查失败），**then** 实现可选择在响应中标注该数据源状态（如 `available: false`），或仅列出已注册数据源，由实现约定。

### 按 Feature 维度

- **When** 调用方请求能力查询时，**the system shall** 在响应中返回**按 feature 维度**的信息，使调用方能判断「某能力由哪些数据源提供」：
  - 至少包含与 API 能力一致的能力标识，如：`stock_info`（元信息）、`stock_list`（列表）、`kline`（历史 K 线）；
  - 每个能力对应至少一个数据源名称列表（即哪些 Provider 支持该能力）。
- **The system shall** 保证 `feature_coverage`（或等价字段）与各 Provider 实际实现的能力一致，**until** 配置或代码变更后重新加载。

### 市场覆盖

- **When** 调用方请求能力查询时，**the system shall** 在响应中返回**市场到数据源**的映射（如 `market_coverage`）：给定市场，可用的数据源列表（按优先级排序或标注顺序），便于调用方知晓某市场应由哪些 Provider 服务。

### 响应格式

- **The system shall** 返回符合统一 API 响应格式的 JSON：`code`、`message`、`data`；成功时 `code` 为 200，`data` 包含上述 provider 维度、feature 维度与市场覆盖信息。
- **If** 服务不可用或查询过程发生未预期错误，**then** 返回相应错误码（如 503）及 `data: null`，并符合 [error 规范](../error/error-codes.md)。
