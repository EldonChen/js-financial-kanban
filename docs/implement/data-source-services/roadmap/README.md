# 技术路线与任务拆解

每个**独立可验证的功能模块**对应一个文件，便于按模块推进与验收。任务状态在各自文件内维护（待开始/进行中/已完成/已取消/阻塞中）。

## 模块与文件

| 文件 | 模块 | 概要 | 依赖 |
|------|------|------|------|
| [01-service-skeleton.md](01-service-skeleton.md) | 服务骨架 | 目录、FastAPI 应用、配置骨架、健康检查、Docker | 无 |
| [02-config-registry.md](02-config-registry.md) | 配置与注册 | 配置模型、校验、Registry 实现、启动时注册 | 01 |
| [03-providers-adapters.md](03-providers-adapters.md) | Provider 适配器 | 接口与基类、akshare/yfinance/easyquotation 适配器、字段映射 | 02 |
| [04-router-normalization.md](04-router-normalization.md) | 路由与规整 | Router 实现、按 market/feature/data_source 选择与容错、数据规整出口 | 02, 03 |
| [05-api-layer.md](05-api-layer.md) | API 层 | 契约 API 实现、统一响应与错误码、OpenAPI 文档 | 04 |
| [06-tests-observability.md](06-tests-observability.md) | 测试与可观测 | 单元/API/集成测试、日志与可选 OpenTelemetry | 01~05 |

## 执行顺序

1. **01** 完成后即可独立启动空服务并打 Docker 镜像。
2. **02** 完成后具备「配置加载 + 注册表」，尚无真实 Provider。
3. **03** 完成后具备可被注册的 Provider 与字段映射。
4. **04** 完成后具备完整路由与规整，可被应用服务层调用。
5. **05** 完成后对外暴露完整 REST API，满足契约。
6. **06** 贯穿各模块，建议每完成一模块即补充对应测试；最后做 E2E 与可观测性收尾。

## 任务状态约定

- **待开始**：未动手
- **进行中**：正在实现
- **已完成**：实现完成且通过该模块 qa/ 验收
- **已取消**：不再做，并说明原因
- **阻塞中**：依赖未满足或外部阻塞，说明原因

每个 roadmap 文件末尾保留「任务状态」小节，便于更新。
