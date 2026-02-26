# 验证方案

本目录在**编码前**声明各功能模块的**验收方法**与**验收标准**，作为实现完成后的通过依据。实现方须逐项满足，审查方可按此清单验收。

## 文件与 SPEC 对应

| 文件 | 对应 SPEC / 模块 | 验收范围 |
|------|------------------|----------|
| [capability-query.md](capability-query.md) | PRD 01 能力查询 | GET /api/v1/providers/status 行为与响应 |
| [stock-meta-list.md](stock-meta-list.md) | PRD 02 股票元信息与列表 | GET/POST stocks、GET stocks/list |
| [kline.md](kline.md) | PRD 03 历史 K 线 | GET kline/{ticker} 参数与响应 |
| [provider-registry-routing.md](provider-registry-routing.md) | PRD 04 注册与路由 | 注册、按 market/feature/data_source 路由、容错 |
| [config-auth.md](config-auth.md) | PRD 05 配置与凭证 | 启用/禁用、优先级、凭证、超时、校验 |
| [e2e-service.md](e2e-service.md) | 整体 | 独立启动、Docker、契约一致性 |

## 验收方法类型

- **手工**：按步骤执行并检查结果（如启动、请求、查看响应与日志）。
- **自动化**：pytest/脚本断言（单元测试、API 测试、集成测试）。
- **契约**：响应 JSON 符合 spec/model/schemas.yaml 或导出的 JSON Schema。

## 使用方式

- 开发前：阅读本目录，明确「完成」的定义。
- 开发后：按各文件中的验收标准逐条执行，未通过则修复直至通过。
- 审查时：审查方可按同一标准复测或依赖自动化结果。
