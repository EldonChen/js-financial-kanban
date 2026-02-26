# 数据源服务 - 架构规范

本目录定义数据源服务的**插件式架构**、UML 建模、抽象接口与设计模式，以实现**动态调度、动态扩展、动态注册**，并保证未来可扩展性。

## 文件索引

| 文件 | 说明 |
|------|------|
| overview.md | 架构总览、分层与设计原则 |
| interfaces.md | 抽象类/接口定义（Provider、Registry、Mapper 等） |
| uml-class.puml | 类图（PlantUML），展示核心抽象与实现关系 |
| uml-sequence.puml | 序列图（请求转发与容错流程） |
| routing.md | 路由与转发规则（按 market、data_source、feature、优先级） |
| registry.md | 注册与发现机制（动态注册、配置驱动） |
| design-patterns.md | 采用的设计模式（策略、注册表、适配器等） |

## 设计原则

- **面向接口编程**：路由层依赖 Provider 抽象接口，不依赖具体数据源实现。
- **开闭原则**：新增数据源通过新增 Provider 实现 + 配置注册完成，无需修改路由核心。
- **单一职责**：Provider 只负责「请求外部 API + 映射为统一模型」；路由层只负责「选择 Provider + 转发 + 容错」。
