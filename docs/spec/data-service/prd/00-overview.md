# 数据源服务 PRD - 总览

## 文档说明

- **规范**：EARS（Easy Approach to Requirements Syntax）
- **范围**：数据源服务（Data Source Service）作为统一 Proxy 的完整需求
- **模块划分**：本目录下按功能模块拆分为独立 PRD 文件，本文件为总览与术语表

## 产品定位

数据源服务是上游业务服务（股票信息服务、历史数据服务、指标服务等）的**统一数据入口**。其职责为：接收标准化请求 → 按市场/优先级/数据源选择外部 Provider → 转发请求 → 将各 Provider 原始响应转换为统一数据模型 → 返回给调用方。**不负责**持久化、调度、指标计算等业务逻辑。

## 利益相关方

| 角色 | 说明 |
|------|------|
| 调用方 | 股票信息服务、历史数据服务、指标服务等，通过 HTTP/RPC 调用数据源服务 |
| 数据源服务 | 本系统，统一 Proxy 层 |
| 外部数据源 | yfinance、akshare、easyquotation、Tushare 等，由 Provider 适配 |

## 功能模块索引

| 文件 | 模块 | 概要 |
|------|------|------|
| 01-capability-query.md | 能力查询 | 按 provider / feature 维度查询已注册数据源及支持能力 |
| 02-stock-meta.md | 股票元信息与列表 | 单只/批量元信息、按市场股票列表 |
| 03-kline.md | 历史 K 线 | 按标的、周期、日期区间获取 K 线 |
| 04-provider-registry.md | Provider 注册与路由 | 动态注册、优先级、按市场/能力路由与容错 |
| 05-config-auth.md | 配置与凭证 | 启用/禁用、优先级、凭证、超时、限流、环境变量 |

## EARS 句型约定

- **When** [触发/场景]，**the system shall** [行为]。
- **Where** [位置/上下文]，**the system shall** [行为]。
- **If** [条件]，**then** [结果/行为]。
- **The system shall** [行为] **while** [约束]。
- **The system shall** [行为] **until** [条件]。

## 术语表

| 术语 | 定义 |
|------|------|
| Provider | 外部数据源的适配实现，实现统一接口，负责请求转发与字段映射 |
| 统一模型 | 对外交付的标准数据类型（Stock、Kline 等），与具体数据源解耦 |
| 路由/转发层 | 根据 market、data_source、优先级、能力（feature）选择 Provider 并转发请求 |
| Feature | 能力维度，如 stock_info、stock_list、kline |
| Market | 市场维度，如 A股、港股、美股 |
