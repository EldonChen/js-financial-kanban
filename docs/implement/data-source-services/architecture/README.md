# 架构设计

本目录描述数据源服务的**技术栈**、**服务布局**与**部署方式**，确保实现与 SPEC 一致且可独立部署。

## 文件索引

| 文件 | 内容 |
|------|------|
| [tech-stack.md](tech-stack.md) | 语言、框架、依赖、版本与选型依据 |
| [service-layout.md](service-layout.md) | 代码目录、分层、与 SPEC 分层的映射 |
| [deployment.md](deployment.md) | 独立启动、配置、Docker 镜像与 docker-compose 集成 |

## 设计原则

- **契约优先**：API 与数据模型以 [spec/model/schemas.yaml](../../../spec/data-source-service/model/schemas.yaml) 及 PRD 为准。
- **插件式扩展**：新增数据源仅新增适配器与配置，不修改 Router/Registry 核心逻辑（见 [spec/architecture/extension-guide.md](../../../spec/data-source-service/architecture/extension-guide.md)）。
- **与现有服务对齐**：与 py-stock-info-service 中 providers、router、historical_data_fetcher、field_mapper 行为对齐，便于后续迁移调用方。
