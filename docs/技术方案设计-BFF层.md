# 技术方案设计 - BFF 层

## 项目技术关键点

### 1. BFF 层定位
- **Backend For Frontend**：专门为前端视图提供定制化、高聚合度的接口
- **独立逻辑层**：不是简单的代理，而是包含数据聚合、编排、转换等逻辑
- **视图驱动设计**：接口设计以「前端视图/页面」为中心，而非资源中心

### 2. 架构层级关系
```
前端 (Nuxt.js)
    ↓ HTTP 请求
BFF 层 (NestJS)
    ↓ HTTP 请求（聚合调用）
后台服务层
    ├── Python FastAPI 服务
    ├── Node.js Nest.js 服务
    ├── Rust Axum 服务
    └── Python 股票信息服务
    ↓
MongoDB 数据库
```

### 3. 核心职责
- **数据聚合**：将多个后台服务的细粒度接口聚合成前端需要的视图数据
- **请求编排**：协调多个后台服务的调用顺序和依赖关系
- **数据转换**：将后台服务的数据格式转换为前端视图所需格式
- **性能优化**：通过并发调用、缓存、批量请求等方式优化性能
- **错误处理**：统一处理后台服务错误，提供友好的错误信息

## 架构设计决策

### 1. 技术选型：NestJS

**选择理由**：
- 与现有 Node.js 服务技术栈一致，降低学习成本
- 模块化架构，便于按视图/领域拆分模块
- 依赖注入和装饰器模式，代码组织清晰
- 内置 HTTP 客户端（HttpModule），便于调用后台服务
- 支持 TypeScript，类型安全
- 丰富的中间件和拦截器，便于实现统一处理逻辑

**替代方案考虑**：
- **Express + TypeScript**：更轻量，但需要手动组织模块结构
- **Fastify**：性能更好，但生态相对较小
- **GraphQL BFF**：更灵活，但复杂度更高，当前阶段 REST 足够

### 2. 项目结构设计

#### Monorepo 组织方式
```
js-financial-kanban/
├── frontend/              # 前端应用
├── services/              # 后台服务
│   ├── python-service/
│   ├── node-service/
│   ├── rust-service/
│   └── py-stock-info-service/
├── bff/                   # BFF 层（新增）
│   ├── bff-main/         # 主 BFF 服务（默认）
│   │   ├── src/
│   │   │   ├── views/    # 视图模块（按前端页面组织）
│   │   │   │   ├── dashboard/
│   │   │   │   ├── items/
│   │   │   │   └── stocks/
│   │   │   │   ├── views.module.ts
│   │   │   │   └── views.controller.ts
│   │   │   ├── clients/  # 后台服务客户端
│   │   │   │   ├── python.client.ts
│   │   │   │   ├── node.client.ts
│   │   │   │   ├── rust.client.ts
│   │   │   │   └── stock-info.client.ts
│   │   │   ├── common/   # 公共模块
│   │   │   │   ├── interceptors/
│   │   │   │   ├── filters/
│   │   │   │   └── utils/
│   │   │   └── main.ts
│   │   ├── package.json
│   │   ├── Dockerfile
│   │   └── .env.example
│   └── shared/            # BFF 层共享代码（可选）
│       ├── types/         # 共享类型定义
│       └── utils/         # 共享工具函数
└── docker-compose.yml
```

#### 模块拆分策略

**按视图拆分**（推荐）：
- `views/dashboard/`：首页看板视图
- `views/items/`：Items 管理视图（聚合 Python/Node/Rust 服务）
- `views/stocks/`：股票信息视图（聚合股票信息服务）

**按领域拆分**（备选）：
- `domains/items/`：Items 领域
- `domains/stocks/`：股票领域

**选择按视图拆分的原因**：
- 更符合 BFF 的「面向前端视图」设计理念
- 便于前端页面与 BFF 接口一一对应
- 更容易理解和管理

### 3. 接口设计原则

#### RESTful 风格
- 遵循 REST 设计原则
- 使用标准 HTTP 方法
- 资源命名使用复数形式

#### 视图驱动命名
- 接口路径反映前端视图/页面
- 例如：`GET /api/bff/v1/views/dashboard` 对应首页看板
- 例如：`GET /api/bff/v1/views/items` 对应 Items 列表页

#### 统一响应格式
```typescript
{
  code: number;        // 状态码（200 表示成功）
  message: string;    // 消息
  data: T;            // 数据（泛型）
  timestamp?: number; // 时间戳（可选）
}
```

#### API 版本控制
- 使用 `/api/bff/v1/` 前缀
- 后续版本使用 `/api/bff/v2/` 等

### 4. 与后台服务的集成策略

#### HTTP 客户端选择
- **NestJS HttpModule**：使用 `@nestjs/axios` 或 `@nestjs/fetch`
- **优势**：与 NestJS 集成好，支持依赖注入，便于测试

#### 聚合调用模式

**1. 并行调用**（推荐）：
```typescript
// 同时调用多个服务，等待所有结果
const [pythonItems, nodeItems, rustItems] = await Promise.all([
  this.pythonClient.getItems(),
  this.nodeClient.getItems(),
  this.rustClient.getItems(),
]);
```

**2. 串行调用**（有依赖关系时）：
```typescript
// 先获取基础数据，再获取关联数据
const stock = await this.stockClient.getStock(ticker);
const schedule = await this.scheduleClient.getSchedule(stock.id);
```

**3. 条件调用**（根据参数决定）：
```typescript
// 根据参数决定调用哪些服务
if (includePython) {
  results.python = await this.pythonClient.getItems();
}
```

#### 性能优化策略

**1. 并发控制**：
- 使用 `Promise.all()` 并行调用多个服务
- 设置超时时间，避免长时间等待
- 使用 `Promise.allSettled()` 处理部分失败的情况

**2. 请求去重**：
- 对于相同参数的请求，在短时间内只发起一次
- 使用内存缓存或 Redis 缓存

**3. 批量请求**：
- 如果后台服务支持批量接口，优先使用批量接口
- 例如：`GET /api/v1/items?ids=1,2,3` 替代多次单独请求

**4. 缓存策略**：
- 对于不经常变化的数据，使用缓存
- 使用 Redis 或内存缓存（根据数据特性选择）

#### 错误处理策略

**1. 部分失败处理**：
- 使用 `Promise.allSettled()` 允许部分服务失败
- 返回成功的数据，失败的字段标记为 `null` 或提供默认值

**2. 降级策略**：
- 如果某个服务失败，使用缓存数据或默认数据
- 记录错误日志，但不影响整体响应

**3. 超时处理**：
- 设置合理的超时时间（如 5 秒）
- 超时后返回错误或使用默认值

### 5. Monorepo 管理方案

#### 工具选型

**方案1：pnpm workspace**（推荐）
- **优势**：
  - 与前端包管理工具一致
  - 支持工作区依赖管理
  - 安装速度快，节省磁盘空间
- **配置**：在根目录创建 `pnpm-workspace.yaml`

**方案2：Nx**
- **优势**：功能强大，支持任务编排、缓存等
- **劣势**：学习成本高，配置复杂，当前阶段可能过度设计

**方案3：Turborepo**
- **优势**：性能好，配置简单
- **劣势**：需要额外学习，当前阶段 pnpm workspace 足够

**选择 pnpm workspace 的原因**：
- 简单直接，满足当前需求
- 与项目现有工具链一致
- 无需额外配置和学习

#### 依赖管理

**共享依赖**：
- 在根目录 `package.json` 定义共享依赖
- 各子项目通过 workspace 引用

**独立依赖**：
- 各 BFF 子项目可以有自己的依赖
- 例如：`bff-main` 可能需要特定的中间件

### 6. Docker 集成方案

#### Dockerfile 设计
- 使用多阶段构建，减小镜像大小
- 使用 Bun 作为运行时（与 node-service 一致）
- 配置健康检查

#### docker-compose.yml 集成
- 添加 `bff-main` 服务
- 配置服务依赖（依赖后台服务）
- 配置网络和端口映射
- 前端修改为调用 BFF 层而非直接调用后台服务

## 技术选型依据

### 1. NestJS 作为 BFF 框架

**优势**：
- ✅ 模块化架构，便于按视图拆分
- ✅ 依赖注入，便于测试和维护
- ✅ TypeScript 支持，类型安全
- ✅ 丰富的装饰器和中间件
- ✅ 与现有 Node.js 服务技术栈一致

**劣势**：
- ⚠️ 相对 Express 更重，但可接受
- ⚠️ 学习曲线，但团队已熟悉

### 2. RESTful API 而非 GraphQL

**选择 REST 的原因**：
- ✅ 简单直接，易于理解和实现
- ✅ 前端团队熟悉 REST
- ✅ 当前需求不复杂，REST 足够
- ✅ 调试和测试更方便

**GraphQL 的适用场景**（未来考虑）：
- 前端需要灵活查询字段
- 需要减少网络请求次数
- 需要实时订阅（Subscription）

### 3. pnpm workspace 作为 Monorepo 工具

**优势**：
- ✅ 与前端包管理工具一致
- ✅ 安装速度快，节省磁盘空间
- ✅ 配置简单，无需额外工具
- ✅ 支持工作区依赖管理

## 技术难点与解决方案

### 1. 数据聚合的复杂性

**难点**：
- 多个后台服务返回的数据格式可能不一致
- 需要合并、去重、排序等操作
- 错误处理复杂

**解决方案**：
- 使用 DTO/VO 统一数据格式
- 使用工具函数处理数据转换
- 使用 `Promise.allSettled()` 处理部分失败

### 2. 性能优化

**难点**：
- 多个服务调用可能较慢
- 需要控制并发数量
- 需要处理超时

**解决方案**：
- 使用 `Promise.all()` 并行调用
- 设置合理的超时时间
- 使用缓存减少重复请求
- 使用请求去重

### 3. 错误处理

**难点**：
- 部分服务失败时的处理
- 错误信息的统一格式
- 降级策略的实现

**解决方案**：
- 使用 `Promise.allSettled()` 允许部分失败
- 统一错误响应格式
- 实现降级逻辑（使用缓存或默认值）

### 4. 类型安全

**难点**：
- 多个后台服务的数据类型可能不一致
- 需要定义统一的类型

**解决方案**：
- 使用 TypeScript 定义 DTO/VO
- 使用类型转换函数
- 使用 `class-transformer` 进行数据转换

### 5. 测试复杂性

**难点**：
- 需要 Mock 多个后台服务
- 集成测试复杂

**解决方案**：
- 使用 NestJS 的测试工具
- 使用 `HttpModule` 的测试工具 Mock HTTP 请求
- 分层测试：单元测试 + 集成测试

## 参考资料来源

### NestJS 相关
- [NestJS 官方文档](https://docs.nestjs.com/)
- [NestJS HTTP 模块](https://docs.nestjs.com/techniques/http-module)
- [NestJS 测试](https://docs.nestjs.com/fundamentals/testing)

### BFF 架构模式
- [Backend For Frontend 模式](https://samnewman.io/patterns/architectural/bff/)
- [BFF 最佳实践](https://www.thoughtworks.com/insights/blog/bff-backend-frontends)

### Monorepo 工具
- [pnpm workspace](https://pnpm.io/workspaces)
- [Nx 文档](https://nx.dev/)
- [Turborepo 文档](https://turbo.build/repo/docs)

### 性能优化
- [Promise.all vs Promise.allSettled](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled)
- [HTTP 客户端性能优化](https://nodejs.org/en/docs/guides/http-request-performance/)

---

**文档版本**：v1.0  
**创建时间**：2024年  
**最后更新**：2024年
