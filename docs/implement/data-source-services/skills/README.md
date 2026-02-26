# 编程规范与最佳实践

本目录描述数据源服务实现中的**编程规范**与**最佳实践**，与项目根目录 `.cursorrules` 及 SPEC 对齐；部分内容可直接复用业界或 GitHub 上已有的实践（见各文件引用）。

## 文件索引

| 文件 | 内容 |
|------|------|
| [python-conventions.md](python-conventions.md) | Python 风格、类型注解、异步、项目结构约定 |
| [api-error-handling.md](api-error-handling.md) | API 层统一响应、错误码映射、异常分类与安全 |
| [testing.md](testing.md) | 单元测试、API 测试、mock 与集成测试约定 |

## 使用方式

- 开发时以本目录为编码规范；Code Review 时可据此检查。
- 与 [spec/error](../../../spec/data-source-service/error/)、[spec/observability](../../../spec/data-source-service/observability/) 冲突时以 SPEC 为准。
