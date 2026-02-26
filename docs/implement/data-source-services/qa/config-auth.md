# 配置与凭证 - 验收方案

对应 SPEC： [PRD 05 - 配置与凭证](../../../spec/data-source-service/prd/05-config-auth.md)、[error/error-codes.md](../../../spec/data-source-service/error/error-codes.md)。

## 验收方法

1. **单元测试**：加载不同环境变量组合，断言配置对象字段与校验结果（至少一个第一优先级启用、凭证与启用一致）。
2. **手工**：设置/取消 ENABLE_*、凭证、超时等，重启服务，观察注册结果与请求行为。
3. **安全**：确认日志与错误信息中不包含凭证明文。

## 验收标准

### 按数据源启用/禁用

- [ ] **AC-1** 每个已知数据源有对应「启用」开关（如 ENABLE_AKSHARE、ENABLE_YFINANCE）；若为 true 且该数据源需要凭证，则凭证已配置时才注册，否则不注册或标记不可用。
- [ ] **AC-2** 至少一个第一优先级数据源（akshare、yfinance、easyquotation 之一）被启用；校验失败时启动失败或拒绝服务，并记录明确错误，符合 error 规范。
- [ ] **AC-3** 第二优先级数据源（如 Tushare、IEX Cloud）已启用但凭证为空或无效时，不注册该 Provider 并记录 warning，不阻塞其他 Provider 注册。

### 优先级与凭证

- [ ] **AC-4** 每个 Provider 可配置优先级（数字，越小越高）；未配置时使用该数据源类型的默认优先级。
- [ ] **AC-5** 凭证从环境变量或安全存储读取；不在日志、错误信息或响应体中输出凭证明文。
- [ ] **AC-6** 若支持配置文件，支持占位符引用环境变量（如 `token: ${TUSHARE_TOKEN}`）。

### 超时与重试

- [ ] **AC-7** 支持全局或按 Provider 的请求超时（如 DATA_SOURCE_REQUEST_TIMEOUT，单位秒）与最大重试次数（如 DATA_SOURCE_MAX_RETRIES）；未配置时使用实现定义的默认值（建议超时 30s，重试 1 次）。
- [ ] **AC-8** 向外部数据源发起请求时，超时后中止并视为失败，进入容错流程；重试仅针对可重试错误且不超过配置次数。

### 环境变量约定

- [ ] **AC-9** 环境变量名与类型与 PRD 05 表格一致：ENABLE_AKSHARE、ENABLE_YFINANCE、ENABLE_EASYQUOTATION、ENABLE_TUSHARE、TUSHARE_TOKEN、ENABLE_IEX_CLOUD、IEX_CLOUD_API_KEY、ENABLE_ALPHA_VANTAGE、ALPHA_VANTAGE_API_KEY、DATA_SOURCE_REQUEST_TIMEOUT、DATA_SOURCE_MAX_RETRIES；布尔类型接受 true/false、1/0 等常见形式。
- [ ] **AC-10** 启动时执行配置校验（至少一个第一优先级启用、凭证与启用一致），校验失败时按「按数据源启用/禁用」要求处理。
