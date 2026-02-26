# PRD - 历史 K 线模块

## 模块概述

调用方需要从数据源服务获取**历史 K 线**数据，按标的（ticker）、周期（period）、日期区间（start_date、end_date）及可选的市场与数据源进行查询。所有返回的 K 线条目必须符合 [统一领域模型 - Kline](../model/schemas.yaml#Kline)。本模块规定请求参数、周期枚举、路由与响应格式。

## EARS 需求

### 查询入口与参数

- **When** 调用方发起 `GET /api/v1/kline/{ticker}` 且路径参数 `ticker` 合法时，**the system shall** 接受查询参数：`period`（可选，默认 `1d`）、`start_date`（可选）、`end_date`（可选）、`market`（可选）、`data_source`（可选），并根据 [架构-路由规则](../architecture/routing.md) 选择支持 K 线能力的 Provider，转发请求并返回符合 [Kline](../model/schemas.yaml) 的数组。
- **The system shall** 支持以下 `period` 枚举值：`1m`、`5m`、`15m`、`30m`、`60m`、`1d`、`1w`、`1M`；若传入别名（如 `daily`），**then** the system shall 规范化为上述枚举之一（如 `daily` → `1d`）再转发。
- **If** `period` 不在支持范围内或格式非法，**then** the system shall 返回 400 及参数错误说明。
- **Where** 日期参数存在，**the system shall** 使用 `YYYY-MM-DD` 格式解析；若格式错误则返回 400。

### 路由与 Provider 能力

- **When** 选择 Provider 处理 K 线请求时，**the system shall** 仅将请求派发至已实现 K 线能力且支持该市场（若指定）及周期的 Provider；若指定 `data_source`，则仅派发至该 Provider（且需支持 K 线）。
- **If** 无任何 Provider 支持当前请求的市场/周期组合，或所有候选 Provider 均失败，**then** the system shall 返回 503 或 404，`data` 为 null 或空结构，并符合 [错误码规范](../error/error-codes.md)。

### 响应格式

- **The system shall** 在成功响应中返回 `data` 包含至少：`ticker`、`period`、`data`（K 线数组）、`data_source`；单条 K 线符合 [Kline](../model/schemas.yaml) 定义，包含 date、open、high、low、close、volume 及可选的 amount、adj_close、timestamp、data_source。
- **Where** 某条 K 线在原始数据源中缺少可选字段，**the system shall** 在统一模型中置为 null 或省略，不得破坏 schema 约束。
- **The system shall** 保证 `data` 数组按时间升序排列（由实现约定），**while** 不改变原始数据语义。

### 边界与限流

- **If** 请求的日期区间过大导致下游 Provider 超时或拒绝，**then** the system shall 返回 400 或 503，并可在 `message` 或 `detail` 中说明原因；实现可约定最大区间或分页策略。
- **Where** 外部数据源存在限流，**the system shall** 在 Provider 层遵守该限流与退避策略，并在 [配置规范](../prd/05-config-auth.md) 中注明；触发限流时按 [错误码规范](../error/error-codes.md) 返回 429 或 503。
