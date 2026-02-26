# 数据源服务 - 统一领域模型（OpenAPI）

本目录定义数据源服务对外交付的**标准结果**数据类型，符合 OpenAPI 3.0 规范。所有 API 响应中的 `data` 或子结构均须符合此处定义的 schema，保证调用方与具体数据源解耦。

## 文件说明

| 文件 | 说明 |
|------|------|
| schemas.yaml | 核心领域模型：ApiResponse、Stock、Kline、能力查询响应等 |
| openapi.yaml | 完整 OpenAPI 文档（可选），引用 schemas 并描述 API 路径 |

## 使用约定

- 对外 HTTP API 的请求/响应体必须与本文档 schema 一致；实现时可由代码生成或手工保证。
- 新增对外数据类型时，在此扩展 schema 并更新版本说明。
