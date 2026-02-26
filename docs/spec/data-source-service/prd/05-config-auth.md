# PRD - 配置与凭证模块

## 模块概述

数据源服务的**启用/禁用**、**优先级**、**凭证**（API Key/Token）、**超时与重试**、**限流**等均由配置驱动；配置来源包括环境变量与可选配置文件。本模块规定配置项语义、校验规则与环境变量约定，以及凭证的安全存储与使用要求。

## EARS 需求

### 按数据源启用/禁用

- **When** 系统启动或配置加载时，**the system shall** 读取每个已知数据源对应的「启用」开关（如 `ENABLE_AKSHARE`、`ENABLE_YFINANCE`）；若为 true 且该数据源依赖的凭证已配置（若需要），则注册该 Provider，否则不注册或标记不可用。
- **The system shall** 保证**至少一个第一优先级数据源**（如 akshare、yfinance、easyquotation 之一）被启用；**If** 校验失败，**then** 启动失败或拒绝服务并记录明确错误，符合 [错误码规范](../error/error-codes.md) 中的启动/配置错误约定。
- **If** 某第二优先级数据源（如 Tushare、IEX Cloud）已启用但对应凭证为空或无效，**then** the system shall 不注册该 Provider 并记录 warning，不阻塞其他 Provider 注册。

### 优先级与凭证

- **The system shall** 支持为每个 Provider 配置优先级（数字，越小越高）；若配置未提供，则使用该数据源类型的默认优先级（见设计文档 §4.4）。
- **The system shall** 对需要凭证的 Provider 从环境变量或安全存储中读取凭证（如 `TUSHARE_TOKEN`、`IEX_CLOUD_API_KEY`）；**Where** 凭证被使用，**the system shall** 不在日志、错误信息或响应体中输出凭证明文。
- **Where** 实现支持配置文件（如 YAML），**the system shall** 支持占位符引用环境变量（如 `token: ${TUSHARE_TOKEN}`），避免凭证写死在配置文件中。

### 超时与重试

- **The system shall** 支持全局或按 Provider 的**请求超时**（如 `DATA_SOURCE_REQUEST_TIMEOUT`，单位秒）与**最大重试次数**（如 `DATA_SOURCE_MAX_RETRIES`）；未配置时使用实现定义的默认值（建议超时 30s，重试 1 次）。
- **When** 向外部数据源发起请求时，**the system shall** 在超时后中止请求并视为失败，进入 [04-provider-registry](04-provider-registry.md) 规定的容错流程；重试仅针对可重试错误且不超过配置次数。

### 限流

- **The system shall** 支持可配置的限流策略（如每 IP / 每 API Key 的 QPS 或并发上限）；若未实现应用层限流，**then** 需在文档中明确说明「由网关或上游负责限流」，并与 [错误码-429](../error/error-codes.md) 约定一致。
- **Where** 外部数据源自身存在限流（如 Tushare、Alpha Vantage），**the system shall** 在 Provider 实现或配置中注明各数据源的限流与退避策略，并在触发下游限流时返回 429 或 503 及适当信息。

### 环境变量约定

- **The system shall** 遵循下表约定的环境变量名与类型；布尔类型接受 `true`/`false`、`1`/`0` 等常见形式，由实现统一解析。

| 环境变量 | 类型 | 默认 | 说明 |
|----------|------|------|------|
| ENABLE_AKSHARE | bool | true | 是否启用 akshare |
| ENABLE_YFINANCE | bool | true | 是否启用 yfinance |
| ENABLE_EASYQUOTATION | bool | false | 是否启用 easyquotation |
| ENABLE_TUSHARE | bool | false | 是否启用 Tushare |
| TUSHARE_TOKEN | string | "" | Tushare token |
| ENABLE_IEX_CLOUD | bool | false | 是否启用 IEX Cloud |
| IEX_CLOUD_API_KEY | string | "" | IEX Cloud API Key |
| ENABLE_ALPHA_VANTAGE | bool | false | 是否启用 Alpha Vantage |
| ALPHA_VANTAGE_API_KEY | string | "" | Alpha Vantage API Key |
| DATA_SOURCE_REQUEST_TIMEOUT | int | 30 | 单次请求超时（秒） |
| DATA_SOURCE_MAX_RETRIES | int | 1 | 失败重试次数 |

- **The system shall** 在启动时执行配置校验（至少一个第一优先级启用、凭证与启用一致），校验失败时按上文「按数据源启用/禁用」要求处理。
