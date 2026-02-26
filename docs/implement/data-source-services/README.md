# 数据源服务 - 实现文档

> 本文档为「数据源服务」独立可部署实现的细化说明，在通过审查前**不得进入实际开发**。实现须严格遵循 [SPEC（docs/spec/data-source-service）](../../spec/data-source-service/README.md) 与设计契约。

## 文档结构

```
docs/implement/data-source-services/
├── README.md                 # 本文件
├── architecture/             # 技术栈与架构设计
│   ├── README.md
│   ├── tech-stack.md         # 技术选型与版本
│   ├── service-layout.md     # 服务目录与分层
│   └── deployment.md         # 独立部署与 Docker
├── roadmap/                  # 技术路线与任务拆解（每模块一文件）
│   ├── README.md
│   ├── 01-service-skeleton.md
│   ├── 02-config-registry.md
│   ├── 03-providers-adapters.md
│   ├── 04-router-normalization.md
│   ├── 05-api-layer.md
│   └── 06-tests-observability.md
├── qa/                       # 验证方案（编码前声明验收方法与标准）
│   ├── README.md
│   ├── capability-query.md
│   ├── stock-meta-list.md
│   ├── kline.md
│   ├── provider-registry-routing.md
│   ├── config-auth.md
│   └── e2e-service.md
└── skills/                   # 编程规范与最佳实践
    ├── README.md
    ├── python-conventions.md
    ├── api-error-handling.md
    └── testing.md
```

## 使用方式

1. **审查阶段**：按 `architecture/` → `roadmap/` → `qa/` → `skills/` 顺序阅读，确认与 SPEC 及现有 py-stock-info-service 行为对齐。
2. **开发阶段**：以 `roadmap/` 为任务顺序，以 `qa/` 为验收依据，以 `skills/` 为编码规范。
3. **验收阶段**：按 `qa/` 中声明的验收方法与标准逐项执行，并更新任务状态。

## 与 SPEC 的对应关系

| 实现文档 | SPEC 来源 |
|----------|-----------|
| architecture/ | spec/architecture/*, spec/prd/00-overview.md |
| roadmap/* | spec/architecture/interfaces.md, routing.md, registry.md, extension-guide.md |
| qa/* | spec/prd/01~05, spec/error/*, spec/model/schemas.yaml |
| skills/* | 项目 .cursorrules + 通用最佳实践 |

## 与现有 py-stock-info-service 的对齐

- **Provider 抽象**：与 `app/services/providers/base.StockDataProvider` 对齐，并扩展为 SPEC 的 IStockMetaProvider / IKlineProvider 及 IProviderMetadata。
- **路由与容错**：与 `app/services/providers/router.StockDataRouter` 的优先级、首选数据源、按市场筛选、失败回退行为一致。
- **字段与模型**：与 `app/schemas/stock`、历史 K 线结构及 `field_mapper` 映射结果对齐到 spec/model/schemas.yaml。
- **配置**：与 `app/config.Settings` 的 ENABLE_*、凭证、超时等环境变量约定一致，并满足 PRD 05 的校验规则。
