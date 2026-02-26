# 模块 06：测试与可观测性

## 目标

完成**单元测试**、**API 层测试**与**必要的集成测试**，并落实日志与可选的 OpenTelemetry 约定。

## 任务拆解

| 序号 | 任务 | 可验收产出 | 状态 |
|------|------|------------|------|
| 6.1 | 单元测试：Registry（注册、getByName、getByMarket 排序、getAll）；Router（指定 data_source、未指定时优先级与回退、超时/失败切换）；Config（校验至少一个第一优先级） | pytest 通过，覆盖率可选用 | 待开始 |
| 6.2 | 单元测试：各 FieldMapper（akshare/yfinance 原始 → Stock/Kline），断言字段与 schema 一致、缺失为 null | pytest 通过 | 待开始 |
| 6.3 | API 测试：使用 TestClient 或 httpx，对 GET/POST stocks、GET stocks/list、GET kline、GET providers/status 做正常与异常用例（400、404、503）；mock Router 或使用真实 Router+Mock Provider | 所有契约 API 有至少一条成功与一条失败用例 | 待开始 |
| 6.4 | 集成测试（可选）：使用真实 akshare/yfinance（可标记 @pytest.mark.integration 或环境变量控制），验证端到端返回结构符合契约 | 可选跳过或 CI 可选执行 | 待开始 |
| 6.5 | 日志：关键路径（Router 选 Provider、Provider 调用、失败回退）打日志，含 provider name、market、ticker 等；不记录凭证明文；级别符合 spec/error/exception-handling.md | 人工或脚本可验证日志内容 | 待开始 |
| 6.6 | 可选 OpenTelemetry：在 Router 与 Provider 调用处预留 Span（或简单实现），trace_id 可写入响应或日志；完整实现可后续迭代 | 文档说明当前范围 | 待开始 |

## 依赖关系

- 依赖 **01~05**；测试随各模块推进可提前编写，本模块做收尾与补充。

## 注意事项

- 与现有 py-stock-info-service 的 test_providers、test_router、test_field_mapper 等行为对齐或复用思路。
- 验收标准以 qa/ 下各文件为准。

## 任务状态

- 整体状态：**待开始**
- 最后更新：-
