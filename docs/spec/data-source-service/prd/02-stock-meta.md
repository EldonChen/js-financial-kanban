# PRD - 股票元信息与列表模块

## 模块概述

调用方需要从数据源服务获取**股票元信息**（单只或批量）以及**按市场维度的股票代码列表**。所有返回数据必须符合 [统一领域模型 - Stock](../model/schemas.yaml#Stock)。本模块规定请求参数、路由与转发逻辑、响应格式及边界行为。

## EARS 需求

### 单只股票元信息

- **When** 调用方发起 `GET /api/v1/stocks/{ticker}` 且路径参数 `ticker` 合法时，**the system shall** 根据查询参数 `market`（可选）与 `data_source`（可选）选择目标 Provider，向该 Provider 转发请求，并将返回结果转换为 [Stock](../model/schemas.yaml) 模型后放入响应 `data` 中返回。
- **If** 调用方未指定 `data_source`，**then** the system shall 按 [架构-路由规则](../architecture/routing.md) 根据 `market` 与优先级选择 Provider；若未指定 `market`，则按实现约定尝试所有支持该请求的 Provider 直至成功或耗尽。
- **If** 调用方指定了 `data_source`，**then** the system shall 仅向该名称的 Provider 转发请求；若该 Provider 未注册或不支持当前请求（如市场不匹配），返回 404 或 503 及明确错误信息。
- **If** 所有候选 Provider 均未返回有效数据（失败、超时或空），**then** the system shall 返回 404 或 503，`data` 为 null，并符合 [错误码规范](../error/error-codes.md)。

### 批量股票元信息

- **When** 调用方发起 `POST /api/v1/stocks/batch` 且请求体包含合法字段 `tickers`（非空数组）时，**the system shall** 按与单只相同的路由与转发规则选择 Provider，执行批量查询（若 Provider 支持批量接口则优先使用），并将结果以 `{ "<ticker>": Stock | null }` 的形式放入响应 `data` 中；未找到或失败的标的对应值为 null。
- **The system shall** 保证响应 `data` 的 key 集合与请求中 `tickers` 一致，**while** 每个 key 的 value 为 Stock 对象或 null。
- **If** 请求体缺少 `tickers` 或格式非法，**then** the system shall 返回 400 及参数错误说明。

### 股票列表（按市场）

- **When** 调用方发起 `GET /api/v1/stocks/list` 且查询参数 `market` 已提供时，**the system shall** 根据 `data_source`（可选）与 market 选择 Provider，向该 Provider 请求该市场的股票代码列表，并将结果放入响应 `data` 中，至少包含 `tickers`（字符串数组）、`market`、`data_source`。
- **If** 调用方未提供 `market`，**then** the system shall 返回 400，要求必填参数。
- **If** 所选 Provider 不支持列表能力（如 easyquotation），**then** the system shall 尝试其他支持该市场的 Provider，或返回 503 若无一可用。

### 数据模型一致性

- **The system shall** 保证所有成功返回的股票元信息（单只或批量中的非 null 项）均符合 [Stock](../model/schemas.yaml) 的必填与可选字段定义，且 `data_source` 字段为实际提供数据的 Provider 名称。
- **Where** 某字段在原始数据源中不存在，**the system shall** 在统一模型中将其置为 null 或省略（按 OpenAPI schema 约定），不得返回非法类型或未定义字段名。
