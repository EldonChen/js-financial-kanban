# 数据源服务 - SPEC 规格说明

本目录为**数据源服务（Data Source Service）**的完整 SPEC，按「SPEC 编程」思维组织，供开发前评审与开发中执行使用。

## 目录结构

```
docs/spec/data-service/
├── README.md           # 本文件
├── prd/                # 需求（EARS 语法，按功能模块）
├── model/              # 统一领域模型（OpenAPI 规范）
├── architecture/       # 插件式架构、UML、接口与设计模式
├── error/              # 错误码与异常处理规范
└── observability/     # OpenTelemetry 全链路追踪规范
```

## 使用方式

1. **开发前**：阅读 `prd/00-overview.md` 与各模块 PRD，理解 EARS 需求；阅读 `architecture/overview.md` 与 `interfaces.md` 理解抽象与扩展点。
2. **开发中**：按 `model/schemas.yaml` 实现对外数据类型；按 `architecture/interfaces.md` 实现 Provider、Registry、Router；按 `error/` 与 `observability/` 处理错误与追踪。
3. **联调与验收**：以 PRD 为验收依据；以 `error/error-codes.md` 与 `model/schemas.yaml` 为契约校验依据。

## 与上游设计文档的关系

- 本 SPEC 与项目根目录下 `docs/数据源服务-设计与契约.md` 对齐：职责边界、API 能力、数据模型、Provider 抽象、配置等在本 SPEC 中细化为可执行的 PRD、模型、架构与规范。
- 实现时以本 SPEC 为准，设计文档作为背景与迁移对照参考。
