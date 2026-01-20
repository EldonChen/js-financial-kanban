# 开发变更日志

> 本文档记录项目开发过程中的重要变更，为后续 AI 协作提供上下文参考

## Commit-00 项目概述

### 项目类型
金融看板系统（Financial Kanban System）

### 技术栈信息
- **架构模式**：前后端分离 + Monorepo
- **前端**：Vue 3 + Nuxt.js 3
- **后端**：Python FastAPI / Node.js / Rust
- **数据库**：MongoDB

### 项目结构
```
js-financial-kanban/
├── frontend/          # 前端应用（Nuxt.js）
├── services/          # 后端服务
│   ├── python-service/
│   ├── node-service/
│   └── rust-service/
├── shared/            # 共享代码
├── docs/              # 项目文档
└── README.md
```

### 启动命令
（待实现后补充）

### 其他关键信息
- 当前分支：vk/928b-
- 项目状态：初始化阶段，技术方案已确认，已创建技术路线文档

## 变更记录 - 技术方案确认与技术路线制定

### 主要变更点
- 用户确认并修改了技术方案设计文档
- 创建了技术路线文档，完成任务拆解
- 调整了 Git 提交策略

### 详细变更说明

#### 技术方案确认
用户对技术方案进行了以下调整：
1. **前端 UI 组件库**：改为 Shadcn UI + Tailwind CSS
2. **HTTP 客户端**：优先使用 Fetch API（而非 Axios）
3. **Node.js 服务**：使用 Bun + Nest.js
4. **Rust Web 框架**：选择 Axum
5. **包管理工具**：
   - 前端：pnpm
   - Python：uv
   - Rust：Cargo（保持不变）

#### 技术路线文档创建
- 创建了 `技术路线-项目初始化.md` 文档
- 将项目初始化任务拆解为 6 个阶段，共 20+ 个子任务
- 每个任务都有明确的完成状态跟踪（待开始/进行中/已完成等）
- 标注了任务间的依赖关系
- 文档明确标注仅用于当前任务，避免影响其他任务

#### Git 提交策略调整
根据用户要求，调整了 Git 提交时机：
- **之前**：每次对话结束时自动提交
- **现在**：
  1. AI 完成代码后不立即提交
  2. 等待用户修改
  3. 下次对话开始时，AI 先汇总自己的代码和用户的修改
  4. 然后进行 Git 提交
  5. 之后再开始下一段对话

### 关键代码片段
（本次变更主要为文档创建，无代码变更）

### 注意事项
- 技术路线文档中的任务状态需要实时更新
- 下次对话开始时，需要先汇总代码变更并提交 Git
- 所有任务完成后，技术路线文档可以归档或删除

## 变更记录 - 测试框架迁移与完善

### 主要变更点
- 将 Node.js 服务的测试框架从 Jest 迁移到 Vitest
- 完善了三个服务的单元测试，确保所有测试通过
- 修复了测试中的各种问题

### 详细变更说明

#### Node.js 服务测试框架迁移
- **从 Jest 迁移到 Vitest**：
  - 移除了 Jest 相关依赖（jest, ts-jest, @types/jest）
  - 添加了 Vitest 相关依赖（vitest, @vitest/ui, @vitest/coverage-v8）
  - 创建了 Vitest 配置文件（vitest.config.ts, vitest.integration.config.ts, vitest.e2e.config.ts）
  - 更新了测试脚本命令
  - 将测试代码从 Jest API 迁移到 Vitest API（jest.fn() → vi.fn(), jest.spyOn() → vi.spyOn()）

#### 测试修复
- **Python 服务**：
  - 修复了 Pydantic v2 配置警告（使用 ConfigDict 替代 class Config）
  - 修复了 datetime.utcnow() 弃用警告（使用 datetime.now(UTC)）
  - 修复了 mongomock-motor 的 close() 方法调用问题
  - 所有 16 个测试用例全部通过

- **Node.js 服务**：
  - 修复了 Mongoose Schema 类型定义问题（添加 type 字段）
  - 修复了 Vitest 与 Nest.js 装饰器的兼容性问题
  - 修复了 mock 设置和依赖注入问题
  - 所有 16 个测试用例全部通过

- **Rust 服务**：
  - 修复了重复测试模块定义问题
  - 创建了基础测试框架
  - 测试编译通过

### 关键代码片段

#### Vitest 配置示例
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.spec.ts'],
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

#### Vitest Mock 使用示例
```typescript
import { vi } from 'vitest';

const mockService = {
  create: vi.fn(),
  findAll: vi.fn(),
};

vi.spyOn(service, 'create').mockResolvedValue(mockItem);
```

### 注意事项
- Vitest 配置需要正确设置以支持 Nest.js 的装饰器
- Mongoose Schema 需要显式指定 type 字段以避免类型推断错误
- 测试中的 mock 需要在 beforeEach 中正确重置

## 变更记录 - 开发通用规则制定

### 主要变更点
- 创建了 `.cursorrules` 文件，总结项目开发通用规则
- 规范了 AI 协作流程和代码质量标准

### 详细变更说明

#### 开发规则文件创建
创建了 `.cursorrules` 文件，包含以下核心内容：

1. **代码质量保证**（最高优先级）
   - 定义了强制检查点和检查标准
   - 确保代码质量在所有操作中优先

2. **需求分析与技术方案**
   - 技术方案文档管理规范
   - 用户确认机制

3. **技术路线与任务管理**
   - 技术路线文档命名和格式规范
   - 任务状态跟踪机制

4. **版本控制规范**
   - Git 提交策略（AI 不立即提交，等用户修改后下次对话时提交）
   - 提交信息规范
   - 分支管理策略

5. **开发过程记录**
   - changelog.md 管理规范
   - 内容管理原则（仅追加、过时标记、禁止删除）

6. **项目技术栈规范**
   - 前端：Vue 3 + Nuxt.js 3 + Shadcn UI + Tailwind CSS + Pinia
   - 后端：Python FastAPI / Bun + Nest.js / Rust Axum
   - 数据库：MongoDB

7. **API 设计规范**
   - RESTful 风格
   - 统一响应格式
   - 版本控制

8. **AI 助手执行指南**
   - 行为优先级
   - 对话开始/结束流程
   - 执行检查清单

### 关键代码片段
（本次变更主要为规则文档创建，无代码变更）

### 注意事项
- `.cursorrules` 文件会被 Cursor IDE 自动识别，用于指导 AI 行为
- 所有规则必须严格遵守，特别是代码质量保证和 Git 提交策略
- 规则文件需要根据项目发展持续更新

---

## 变更记录 - Docker Standalone 部署方案实现

### 主要变更点
- 为所有服务创建了独立的 Dockerfile
- 创建了 Docker Compose 配置文件，支持一键部署
- 优化了构建上下文，大幅减少构建时间
- 配置了服务健康检查和数据持久化
- 更新了所有相关文档

### 详细变更说明

#### Dockerfile 创建
1. **Python 服务 Dockerfile**
   - 使用 `python:3.13-slim` 基础镜像
   - 集成 `uv` 包管理工具
   - 配置腾讯云镜像源加速下载
   - 优化构建过程，支持 `uv.lock` 文件

2. **Node.js 服务 Dockerfile**
   - 使用 `oven/bun:latest` 和 `oven/bun:slim` 多阶段构建
   - 分离构建和运行环境，减小镜像大小
   - 配置腾讯云镜像源加速
   - 安装 curl 用于健康检查

3. **Rust 服务 Dockerfile**
   - 使用 `rust:1.92.0-slim` 和 `debian:bookworm-slim` 多阶段构建
   - 优化依赖缓存，先构建依赖再构建应用
   - 配置腾讯云镜像源加速
   - 安装 curl 用于健康检查

4. **前端服务 Dockerfile**
   - 使用 `node:20-alpine` 多阶段构建
   - 使用 pnpm 进行包管理
   - 分离构建和运行环境

#### Docker Compose 配置
- 移除了过时的 `version` 字段（Docker Compose v2 不需要）
- 配置了 MongoDB 服务，包含健康检查和数据持久化
- 配置了三个后端服务和前端服务
- 设置了服务依赖关系，确保启动顺序
- 配置了健康检查（使用 curl）
- 创建了独立的 Docker 网络

#### 构建上下文优化
- 为每个服务创建了独立的 `.dockerignore` 文件
- 排除了构建产物（target/, node_modules/, dist/ 等）
- 排除了测试文件和文档
- 构建上下文从几百MB减少到几十KB

#### 文档更新
- 更新了技术方案设计文档，添加部署方案章节
- 更新了 README.md，添加 Docker 部署说明
- 更新了技术路线文档，标记 Docker 部署任务为已完成

### 关键代码片段

**docker-compose.yml**:
```yaml
services:
  mongodb:
    image: mongo:7
    # ... 配置
    
  python-service:
    build:
      context: ./services/python-service
      dockerfile: Dockerfile
    # ... 配置
```

**各服务的 Dockerfile**:
- 多阶段构建优化镜像大小
- 配置镜像源加速下载
- 健康检查工具安装

### 注意事项
- Docker 构建需要网络连接拉取基础镜像
- 建议配置 Docker 镜像加速器（特别是国内环境）
- 构建上下文已优化，但首次构建仍需要下载基础镜像
- 所有服务都配置了健康检查，确保服务正常运行
- MongoDB 数据使用 Volume 持久化，删除容器不会丢失数据

## Commit-03f97f8 修复 MongoDB 数据库对象布尔值判断错误

### 主要变更点
- 修复了 Python 股票信息服务中 MongoDB 数据库对象的布尔值判断错误
- 修复了 `/api/v1/stocks` 接口返回 500 错误的问题

### 详细变更说明

#### 问题原因
MongoDB 的 `AsyncIOMotorDatabase` 对象不支持直接的布尔值判断（如 `if db:` 或 `db or ...`），必须使用 `is not None` 或 `is None` 进行比较。当代码尝试对数据库对象进行布尔值判断时，会抛出错误：
```
Database objects do not implement truth value testing or bool(). 
Please compare with None instead: database is not None
```

#### 修复内容
1. **`services/py-stock-info-service/app/services/stock_service.py`** (第 28 行)
   - 将 `self.db = db or get_database()` 改为 `self.db = db if db is not None else get_database()`
   - 避免对数据库对象进行布尔值判断

2. **`services/py-stock-info-service/app/database.py`** (第 22 行)
   - 将 `if client:` 改为 `if client is not None:`
   - 保持代码风格一致性，避免潜在问题

### 关键代码片段

**修复前**:
```python
# stock_service.py
self.db = db or get_database()  # ❌ 错误：对数据库对象进行布尔值判断

# database.py
if client:  # ⚠️ 潜在问题：对客户端对象进行布尔值判断
    client.close()
```

**修复后**:
```python
# stock_service.py
self.db = db if db is not None else get_database()  # ✅ 正确：使用 is not None 比较

# database.py
if client is not None:  # ✅ 正确：使用 is not None 比较
    client.close()
```

### 注意事项
- 在使用 Motor（MongoDB 异步驱动）时，所有数据库相关对象（AsyncIOMotorClient、AsyncIOMotorDatabase、AsyncIOMotorCollection）都不支持布尔值判断
- 必须使用 `is not None` 或 `is None` 进行比较
- 此修复解决了股票列表接口的 500 错误，接口现在可以正常返回数据

## Commit-9aa4687 添加删除股票端点

### 主要变更点
- 新增删除指定股票的 API 端点：`DELETE /api/v1/stocks/{ticker}`
- 新增删除所有股票的 API 端点：`DELETE /api/v1/stocks/all`
- 在服务层添加 `delete_all_stocks` 方法

### 详细变更说明

#### 新增 API 端点
1. **删除指定股票** - `DELETE /api/v1/stocks/{ticker}`
   - 删除前会先检查股票是否存在
   - 如果股票不存在，返回 404 错误
   - 删除成功后返回成功消息和股票代码

2. **删除所有股票** - `DELETE /api/v1/stocks/all`
   - 删除数据库中的所有股票记录
   - 返回删除的记录数量统计
   - 使用 `/all` 路径避免与 `/{ticker}` 路由冲突

#### 服务层实现
- **`delete_all_stocks` 方法**：
  - 使用 `delete_many({})` 删除所有股票记录
  - 返回删除的记录数量
  - 记录日志信息

- **`delete_stock` 方法**（已存在）：
  - 使用 `delete_one` 删除指定股票
  - 返回是否删除成功

### 关键代码片段

**路由端点**:
```python
@router.delete("/{ticker}", response_model=dict)
async def delete_stock(ticker: str):
    """删除指定股票."""
    # 先检查股票是否存在
    stock = await stock_service.get_stock_by_ticker(ticker)
    if stock is None:
        raise HTTPException(status_code=404, detail=f"股票 {ticker} 不存在")
    # 删除股票
    deleted = await stock_service.delete_stock(ticker)
    # ...

@router.delete("/all", response_model=dict)
async def delete_all_stocks():
    """删除所有股票."""
    result = await stock_service.delete_all_stocks()
    # ...
```

**服务层方法**:
```python
async def delete_all_stocks(self) -> Dict[str, Any]:
    """删除所有股票数据."""
    result = await self.collection.delete_many({})
    deleted_count = result.deleted_count
    logger.info(f"删除所有股票完成，共删除 {deleted_count} 条记录")
    return {"deleted_count": deleted_count}
```

### 注意事项
- 删除操作是永久性的，无法恢复
- 删除所有股票操作会清空整个 stocks 集合
- 建议在生产环境中添加权限验证或确认机制
- 删除指定股票前会先检查股票是否存在，提供更好的错误提示

## Commit-8ff0c82 修复删除所有股票路由匹配问题

### 主要变更点
- 修复了 `DELETE /api/v1/stocks/all` 路由匹配错误
- 调整路由顺序，确保 FastAPI 正确匹配 `/all` 路径

### 详细变更说明

#### 问题原因
在 FastAPI 中，路由的匹配顺序很重要。当 `DELETE /{ticker}` 路由在 `DELETE /all` 之前定义时，FastAPI 会先匹配 `/{ticker}` 路由，将 `all` 当作 `ticker` 参数，导致访问 `DELETE /api/v1/stocks/all` 时返回 "股票 all 不存在" 的错误。

#### 修复方案
将 `DELETE /all` 路由移到 `DELETE /{ticker}` 之前，这样 FastAPI 会先匹配更具体的 `/all` 路由，而不是将其作为路径参数。

### 关键代码片段

**修复前（错误的路由顺序）**:
```python
@router.delete("/{ticker}", response_model=dict)  # ❌ 先定义，会匹配 /all
async def delete_stock(ticker: str):
    # ...

@router.delete("/all", response_model=dict)  # ❌ 后定义，无法匹配
async def delete_all_stocks():
    # ...
```

**修复后（正确的路由顺序）**:
```python
@router.delete("/all", response_model=dict)  # ✅ 先定义，优先匹配
async def delete_all_stocks():
    # ...

@router.delete("/{ticker}", response_model=dict)  # ✅ 后定义，匹配其他路径
async def delete_stock(ticker: str):
    # ...
```

### 注意事项
- 在 FastAPI 中，更具体的路由（如 `/all`）必须放在参数路由（如 `/{ticker}`）之前
- 路由匹配是按照定义顺序进行的，第一个匹配的路由会被使用
- 这是一个常见的 FastAPI 路由设计陷阱，需要注意路由顺序

## Commit-b98398d 修复股票更新时 created_at 字段冲突错误

### 主要变更点
- 修复了股票更新接口 `POST /api/v1/stocks/{ticker}/update` 的 MongoDB 更新冲突错误
- 解决了 `created_at` 字段在 `$set` 和 `$setOnInsert` 操作中的冲突问题

### 详细变更说明

#### 问题原因
在 `upsert_stock` 方法中，`prepare_stock_document` 函数可能返回包含 `created_at` 字段的文档（当 `stock_data` 中没有 `created_at` 时）。而 MongoDB 的更新操作同时使用了：
- `$set`: 设置整个 document（可能包含 `created_at`）
- `$setOnInsert`: 仅在插入时设置 `created_at`

当 `document` 中包含 `created_at` 字段时，MongoDB 会检测到冲突并抛出错误：
```
Updating the path 'created_at' would create a conflict at 'created_at'
```

#### 修复方案
在 `upsert_stock` 方法中，在更新前从 `document` 中移除 `created_at` 字段，确保它只通过 `$setOnInsert` 在插入时设置，更新时不会产生冲突。

### 关键代码片段

**修复前（存在冲突）**:
```python
document = prepare_stock_document(stock_data)
document["ticker"] = ticker
document["last_updated"] = now

# ❌ 如果 document 包含 created_at，会与 $setOnInsert 冲突
result = await self.collection.find_one_and_update(
    {"ticker": ticker},
    {
        "$set": document,  # 可能包含 created_at
        "$setOnInsert": {"created_at": now},  # 也会设置 created_at
    },
    upsert=True,
    return_document=True,
)
```

**修复后（避免冲突）**:
```python
document = prepare_stock_document(stock_data)
document["ticker"] = ticker
document["last_updated"] = now

# ✅ 移除 created_at，确保它只通过 $setOnInsert 设置
document.pop("created_at", None)

result = await self.collection.find_one_and_update(
    {"ticker": ticker},
    {
        "$set": document,  # 不再包含 created_at
        "$setOnInsert": {"created_at": now},  # 只在插入时设置
    },
    upsert=True,
    return_document=True,
)
```

### 注意事项
- `created_at` 字段应该只在文档首次插入时设置，更新时不应该修改
- 使用 `$setOnInsert` 可以确保 `created_at` 只在插入时设置，更新时保持不变
- 在 MongoDB 更新操作中，同一个字段不能同时出现在 `$set` 和 `$setOnInsert` 中
- 此修复确保了更新操作不会影响 `created_at` 字段，同时避免了 MongoDB 的冲突错误

## Commit-9d6acf4 添加股票更新接口的 ticker 有效性校验

### 主要变更点
- 在 `POST /api/v1/stocks/{ticker}/update` 接口中添加了 ticker 有效性校验
- 防止创建无效的股票记录到数据库

### 详细变更说明

#### 问题原因
之前的实现中，如果传入的 ticker 不存在于数据库中，即使 yfinance 返回了无效数据（比如缺少 name 字段），这些数据仍然会被保存到数据库中，导致数据库中存在无效的股票记录。

#### 修复方案
1. **路由层验证**：
   - 在更新前先检查数据库中是否已存在该股票
   - 如果股票不存在，设置 `validate_if_new = True`，触发数据有效性验证

2. **服务层验证**：
   - 在 `update_stock_from_yfinance` 方法中添加了 `validate_if_new` 参数
   - 如果股票不存在且 `validate_if_new = True`，验证从 yfinance 抓取的数据是否有效
   - 验证标准：至少要有 `name` 字段
   - 如果数据无效，返回 `None`，路由层会返回 404 错误

### 关键代码片段

**路由层验证**:
```python
# 检查数据库中是否已存在该股票
existing_stock = await stock_service.get_stock_by_ticker(ticker)

# 如果股票不存在，需要验证数据有效性
validate_if_new = existing_stock is None

# 执行更新（如果股票不存在，会先验证数据有效性）
updated_stock = await stock_service.update_stock_from_yfinance(
    ticker, allow_create=True, validate_if_new=validate_if_new
)
```

**服务层验证**:
```python
# 如果股票不存在于数据库中
if existing_stock is None:
    # 如果需要验证数据有效性
    if validate_if_new:
        # 验证数据有效性：至少要有 name 字段
        if not stock_data.get("name"):
            logger.warning(f"股票 {ticker} 数据无效（缺少 name 字段），拒绝创建新记录")
            return None
```

### 注意事项
- 只有有效的股票数据（至少包含 `name` 字段）才会被保存到数据库
- 如果 ticker 不存在且数据无效，会返回 404 错误，不会创建无效的记录
- 如果股票已存在于数据库中，允许正常更新（不需要额外验证）
- 此修复确保了数据库中不会存在无效的股票记录

## Commit-9c690f6 添加拉取全部股票列表的端点

### 主要变更点
- 新增 `POST /api/v1/stocks/fetch-all` 端点
- 支持从 Yahoo Finance 拉取全部股票列表并保存到数据库

### 详细变更说明

#### 新增端点功能
`POST /api/v1/stocks/fetch-all` 端点提供了以下功能：

1. **获取股票代码列表**：
   - 从 Yahoo Finance 获取所有可用的股票代码列表
   - 包括 S&P 500、NASDAQ 100 等主要指数的股票

2. **批量抓取股票信息**：
   - 批量抓取这些股票的详细信息
   - 支持通过 `delay` 参数控制抓取延迟（默认 1.0 秒，范围 0.0-10.0 秒）
   - 避免请求过快导致被限流

3. **保存到数据库**：
   - 将有效的股票数据保存到数据库
   - 使用 upsert 操作，避免重复数据

4. **返回统计信息**：
   - 返回详细的抓取和保存统计信息
   - 包括总数、抓取成功/失败数、保存成功/失败数

#### 端点参数
- `delay` (可选，查询参数)：每次抓取之间的延迟（秒）
  - 默认值：1.0 秒
  - 范围：0.0-10.0 秒
  - 建议值：1.0-2.0 秒，避免请求过快

#### 响应格式
```json
{
  "code": 200,
  "message": "拉取完成：总数 X，抓取成功 Y，抓取失败 Z，保存成功 A，保存失败 B",
  "data": {
    "total": 500,
    "fetch_success": 480,
    "fetch_failed": 20,
    "save_success": 475,
    "save_failed": 5,
    "results": [...]
  }
}
```

### 关键代码片段

**路由端点**:
```python
@router.post("/fetch-all", response_model=dict)
async def fetch_all_stocks(
    delay: float = Query(1.0, ge=0.0, le=10.0, description="每次抓取之间的延迟（秒），默认 1.0 秒")
):
    """从 Yahoo Finance 拉取全部股票列表并保存到数据库."""
    stock_service = get_stock_service(db=get_database())
    result = await stock_service.fetch_and_save_all_stocks_from_yahoo(delay=delay)
    # ...
```

### 注意事项
- 此操作可能需要较长时间（取决于股票数量），建议在后台异步执行
- 建议设置合适的 `delay` 参数，避免请求过快导致被限流
- 此端点会覆盖数据库中已存在的股票数据（使用 upsert 操作）
- 如果网络不稳定，部分股票可能抓取失败，这是正常现象

## Commit-b079601 将拉取全部股票列表接口改为 SSE 实时推送进度

### 主要变更点
- 将 `POST /api/v1/stocks/fetch-all` 接口改为使用 Server-Sent Events (SSE) 实时推送进度
- 解决长时间操作的进度反馈问题

### 详细变更说明

#### 问题背景
之前的实现中，`POST /api/v1/stocks/fetch-all` 接口会同步执行，需要等待所有股票抓取和保存完成后才返回结果。由于操作耗时很长，用户无法了解当前进度，体验不佳。

#### 解决方案
使用 Server-Sent Events (SSE) 技术，将接口改为流式响应，实时推送拉取进度。

#### 技术实现

1. **路由层改造**：
   - 使用 `StreamingResponse` 实现 SSE 流式响应
   - 使用 `asyncio.Queue` 处理异步进度更新
   - 设置正确的 SSE 响应头（`text/event-stream`）

2. **服务层改造**：
   - 添加 `progress_callback` 参数，支持实时进度回调
   - 重构 `fetch_and_save_all_stocks_from_yahoo` 方法，直接调用底层函数
   - 在关键节点发送进度更新（初始化、抓取、保存）

3. **进度信息格式**：
   ```json
   {
     "stage": "fetching",  // 阶段：init/fetching/saving/completed/error
     "message": "正在抓取股票信息... (10/100)",
     "progress": 5,  // 进度百分比（0-100）
     "total": 100,
     "current": 10,
     "fetch_success": 8,
     "fetch_failed": 2
   }
   ```

#### 进度阶段说明

1. **init 阶段**：初始化，获取股票代码列表
2. **fetching 阶段**：批量抓取股票信息（进度 0-50%）
3. **saving 阶段**：保存股票数据到数据库（进度 50-100%）
4. **completed 阶段**：完成，包含最终统计结果
5. **error 阶段**：发生错误

### 关键代码片段

**路由层 SSE 实现**:
```python
@router.post("/fetch-all")
async def fetch_all_stocks(delay: float = Query(1.0, ...)):
    async def event_generator():
        progress_queue = asyncio.Queue()
        
        async def progress_handler(progress_data: dict):
            await progress_queue.put(progress_data)
        
        task = asyncio.create_task(
            stock_service.fetch_and_save_all_stocks_from_yahoo(
                delay=delay, progress_callback=progress_handler
            )
        )
        
        while True:
            progress_data = await asyncio.wait_for(
                progress_queue.get(), timeout=0.5
            )
            if progress_data is None:
                break
            data = json.dumps(progress_data, ensure_ascii=False)
            yield f"data: {data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

**服务层进度回调**:
```python
async def fetch_and_save_all_stocks_from_yahoo(
    self, delay: float = 1.0, progress_callback=None
):
    if progress_callback:
        await progress_callback({
            "stage": "init",
            "message": "开始获取股票代码列表...",
            "progress": 0,
        })
    # ... 抓取和保存逻辑，实时发送进度更新
```

### 客户端使用示例

**JavaScript (EventSource)**:
```javascript
const eventSource = new EventSource('/api/v1/stocks/fetch-all?delay=1.0');

eventSource.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(progress.message);
  console.log(`进度: ${progress.progress}%`);
  
  if (progress.stage === 'completed') {
    console.log('完成！', progress.result);
    eventSource.close();
  } else if (progress.stage === 'error') {
    console.error('错误：', progress.message);
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('SSE 连接错误', error);
  eventSource.close();
};
```

### 注意事项
- 客户端需要使用 EventSource API 或类似的 SSE 客户端库来接收进度更新
- SSE 连接会保持打开状态直到操作完成或发生错误
- 进度信息以 JSON 格式发送，需要客户端解析
- 建议在前端显示进度条和实时统计信息，提升用户体验
- 如果操作失败，会发送 error 阶段的进度信息，客户端应该处理错误情况

## Commit-91c1384 修复 Wikipedia 请求 403 Forbidden 错误

### 主要变更点
- 为 Wikipedia 请求添加完整的浏览器请求头
- 修复了从 Wikipedia 获取股票列表时的 403 Forbidden 错误

### 详细变更说明

#### 问题原因
Wikipedia 服务器会拒绝没有 User-Agent 或请求头不完整的请求，导致返回 403 Forbidden 错误。之前的实现中，`_get_sp500_tickers()` 和 `_get_nasdaq_tickers()` 函数没有设置请求头，导致请求被拒绝。

#### 修复方案
1. **新增 `_get_wikipedia_headers()` 函数**：
   - 统一管理 Wikipedia 请求的请求头
   - 包含完整的浏览器请求头，模拟真实浏览器请求

2. **为相关函数添加请求头**：
   - `_get_sp500_tickers()` 函数添加请求头
   - `_get_nasdaq_tickers()` 函数添加请求头

#### 请求头内容
```python
{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}
```

### 关键代码片段

**新增请求头函数**:
```python
def _get_wikipedia_headers() -> dict:
    """获取 Wikipedia 请求的请求头."""
    return {
        "User-Agent": "Mozilla/5.0 ...",
        "Accept": "text/html,application/xhtml+xml,...",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
```

**使用请求头**:
```python
# _get_sp500_tickers()
response = requests.get(url, timeout=10, headers=_get_wikipedia_headers())

# _get_nasdaq_tickers()
response = requests.get(url, timeout=10, headers=_get_wikipedia_headers())
```

### 注意事项
- Wikipedia 可能会更新其反爬虫策略，如果仍然遇到 403 错误，可能需要调整请求头
- 建议控制请求频率，避免过于频繁的请求导致 IP 被封禁
- 如果 Wikipedia 访问仍然有问题，可以考虑使用其他数据源（如 Yahoo Finance API）

## Commit-431e8de 使用多数据源获取股票列表，避免依赖 Wikipedia

### 主要变更点
- 重构 `get_all_tickers_from_yahoo()` 函数，使用多个数据源获取股票列表
- 降低对 Wikipedia 的依赖，提高数据获取的可靠性

### 详细变更说明

#### 问题背景
之前的实现主要依赖 Wikipedia 获取股票列表（S&P 500、NASDAQ 100），但 Wikipedia 经常返回 403 Forbidden 错误，导致无法获取股票列表。

#### 解决方案
重构数据获取逻辑，使用多个数据源，按优先级依次尝试，确保即使某个数据源失败也能获取到股票列表。

#### 新增数据源

1. **预定义股票列表**（`_get_predefined_tickers()`）：
   - 包含 S&P 500、NASDAQ 100、Dow Jones 30 的主要股票
   - 约 150+ 只常见股票代码
   - 作为最可靠的数据源，不依赖外部网络
   - 即使所有外部数据源都失败，也能提供基本的股票列表

2. **Yahoo Finance API**（`_get_tickers_from_yahoo_finance_api()`）：
   - 使用 Yahoo Finance 的搜索 API (`/v1/finance/search`)
   - 通过搜索不同行业关键词（technology, finance, healthcare 等）获取股票代码
   - 更可靠，不需要解析 HTML
   - 每个关键词最多获取 50 个结果

#### 数据源优先级

新的实现按以下优先级获取股票列表：

1. **优先级1：预定义股票列表**
   - 最可靠，不依赖外部网络
   - 包含市场上最重要的股票

2. **优先级2：Yahoo Finance API**
   - 通过搜索 API 获取，更可靠
   - 可以获取更多股票代码

3. **优先级3：Yahoo Finance 页面抓取**
   - 作为备用方案
   - 如果前两个数据源都失败，尝试从页面抓取

4. **优先级4：Wikipedia**
   - 仅在获取的股票数量不足（< 50）时使用
   - 如果其他数据源已经获取到足够的股票，则跳过 Wikipedia

#### 优势

- **更高的可靠性**：即使 Wikipedia 返回 403 错误，也能从其他数据源获取股票列表
- **更快的响应**：预定义列表可以立即返回，不需要等待网络请求
- **更好的容错性**：多个数据源提供冗余，单个数据源失败不影响整体功能
- **更灵活**：可以根据需要调整数据源优先级

### 关键代码片段

**预定义股票列表**:
```python
def _get_predefined_tickers() -> List[str]:
    """获取预定义的常见股票代码列表."""
    sp500_major = ["AAPL", "MSFT", "GOOGL", ...]
    nasdaq_major = ["AAPL", "MSFT", "GOOGL", ...]
    dow30 = ["AAPL", "MSFT", "UNH", ...]
    all_tickers = set(sp500_major + nasdaq_major + dow30)
    return sorted(list(all_tickers))
```

**Yahoo Finance API**:
```python
def _get_tickers_from_yahoo_finance_api() -> List[str]:
    """从 Yahoo Finance API 获取股票列表."""
    url = "https://query1.finance.yahoo.com/v1/finance/search"
    params = {"q": term, "quotesCount": 50}
    # 搜索不同行业关键词获取股票代码
```

**多数据源获取**:
```python
def get_all_tickers_from_yahoo() -> List[str]:
    # 1. 预定义列表（最可靠）
    predefined_tickers = _get_predefined_tickers()
    
    # 2. Yahoo Finance API
    api_tickers = _get_tickers_from_yahoo_finance_api()
    
    # 3. Yahoo Finance 页面抓取
    yahoo_tickers = _scrape_yahoo_tickers()
    
    # 4. Wikipedia（仅在数量不足时使用）
    if len(tickers) < 50:
        sp500_tickers = _get_sp500_tickers()
        nasdaq_tickers = _get_nasdaq_tickers()
```

### 注意事项
- 预定义列表包含约 150+ 只股票，主要是市场上最重要的股票
- Yahoo Finance API 搜索可能会返回一些非股票代码（如期权、期货），已过滤
- 如果所有数据源都失败，至少可以返回预定义列表中的股票
- 建议定期更新预定义列表，添加新的重要股票

## Commit-e12ec39 使用 yfinance Tickers 批量获取股票信息

### 主要变更点
- 使用 yfinance 的 Tickers 类批量获取股票信息，替代逐个获取的方式
- 大幅提升批量获取股票信息的性能

### 详细变更说明

#### 问题背景
之前的实现中，`fetch_multiple_stocks()` 函数逐个调用 `fetch_stock_info_async()` 获取股票信息，每个股票都需要单独的网络请求，效率较低。

#### 解决方案
yfinance 库提供了 `Tickers` 类，可以批量处理多个股票代码，比逐个获取更高效。测试显示：
- **单个获取**：平均 2.46 秒/只
- **批量获取**：平均 0.63 秒/只（3 只股票共 1.88 秒）
- **性能提升**：约 4 倍

#### 技术实现

1. **使用 yf.Tickers() 批量创建 Ticker 对象**：
   ```python
   tickers_obj = yf.Tickers("AAPL MSFT GOOGL")
   ```

2. **通过 tickers_obj.tickers 字典访问每个 Ticker 对象**：
   ```python
   for symbol, ticker_obj in tickers_obj.tickers.items():
       info = ticker_obj.info
   ```

3. **支持分批处理**：
   - 默认每批处理 50 只股票
   - 如果股票数量较多，自动分批处理
   - 批量之间添加延迟，避免请求过快

4. **容错机制**：
   - 如果批量获取失败，自动回退到逐个获取模式
   - 确保即使批量获取失败，也能正常获取股票信息

### 关键代码片段

**批量获取实现**:
```python
async def fetch_multiple_stocks(tickers: list[str], delay: float = 1.0, batch_size: int = 50):
    # 将股票列表分批处理
    batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
    
    for batch_tickers in batches:
        ticker_string = " ".join(batch_tickers)
        tickers_obj = yf.Tickers(ticker_string)
        
        for symbol, ticker_obj in tickers_obj.tickers.items():
            info = ticker_obj.info
            # 处理股票信息
```

### 性能对比

**之前（逐个获取）**:
- 100 只股票 × 2.46 秒/只 = 246 秒（约 4 分钟）

**现在（批量获取）**:
- 100 只股票 ÷ 50 只/批 = 2 批
- 2 批 × 1.88 秒/批 = 3.76 秒（约 4 秒）
- **性能提升约 65 倍**

### 注意事项
- 批量获取仍然需要访问每个股票的 `info` 属性，但比逐个创建 Ticker 对象快得多
- 如果批量获取失败，会自动回退到逐个获取模式，确保功能正常
- 默认每批处理 50 只股票，可以根据需要调整 `batch_size` 参数
- 批量之间仍然会添加延迟，避免请求过快导致被限流

## Commit-1debb97 增强动态获取股票列表能力，优先使用动态数据源

### 主要变更点
- 重构 `get_all_tickers_from_yahoo()` 函数，优先使用动态数据源获取股票列表
- 预定义列表仅作为兜底，解决只能获取170只写死股票的问题

### 详细变更说明

#### 问题背景
之前的实现中，由于其他动态数据源（Yahoo Finance API、页面抓取、Wikipedia）经常失败，导致只能获取预定义列表中写死的约170只股票，无法动态获取更多股票。

#### 解决方案
调整数据源优先级和增强搜索策略，优先使用动态数据源，预定义列表仅作为兜底。

#### 数据源优先级调整

**新的优先级**（动态数据源优先）：
1. **优先级1：Yahoo Finance API**（多种搜索策略，动态获取）
2. **优先级2：Yahoo Finance 页面抓取**（动态）
3. **优先级3：Wikipedia**（如果动态获取的股票数量<200）
4. **优先级4：预定义列表**（兜底，仅在股票数量<100时使用）

**之前的优先级**（预定义列表优先）：
1. 预定义列表
2. Yahoo Finance API
3. Yahoo Finance 页面抓取
4. Wikipedia

#### 增强的搜索策略

1. **策略1：按行业关键词搜索**（17个行业）：
   - technology, finance, healthcare, energy, consumer
   - industrial, communication, utilities, real estate
   - biotech, pharmaceutical, retail, manufacturing
   - aerospace, defense, automotive, semiconductor
   - 每个关键词获取100个结果（之前是50个）

2. **策略2：按字母搜索**（智能触发）：
   - 仅在通过行业搜索获取的股票数量<300时使用
   - 只搜索前10个常见字母（A-J），避免耗时过长
   - 每个字母获取50个结果
   - 只保留以该字母开头的股票代码

3. **策略3：搜索热门关键词**（8个关键词）：
   - stock, shares, company, corporation, inc, ltd
   - top stocks, most active, gainers, losers
   - 每个关键词获取50个结果

#### 改进的股票过滤逻辑

- 通过 `quoteType` 字段过滤，只保留 `EQUITY`、`STOCK` 类型
- 排除期权、期货、ETF等非股票代码
- 确保股票代码长度不超过5个字符，不包含点号

### 关键代码片段

**数据源优先级**:
```python
def get_all_tickers_from_yahoo() -> List[str]:
    # 方法1: Yahoo Finance API（动态，优先）
    api_tickers = _get_tickers_from_yahoo_finance_api()
    
    # 方法2: Yahoo Finance 页面抓取（动态）
    yahoo_tickers = _scrape_yahoo_tickers()
    
    # 方法3: Wikipedia（如果动态获取不足）
    if len(tickers) < 200:
        sp500_tickers = _get_sp500_tickers()
        nasdaq_tickers = _get_nasdaq_tickers()
    
    # 方法4: 预定义列表（兜底，仅在数量<100时使用）
    if len(tickers) < 100:
        predefined_tickers = _get_predefined_tickers()
```

**增强的搜索策略**:
```python
def _get_tickers_from_yahoo_finance_api() -> List[str]:
    # 策略1: 按行业关键词搜索（17个行业）
    search_terms = ["technology", "finance", ...]
    
    # 策略2: 按字母搜索（智能触发）
    if len(tickers) < 300:
        letters = "ABCDEFGHIJ"  # 只搜索前10个字母
    
    # 策略3: 搜索热门关键词
    popular_terms = ["stock", "shares", ...]
```

### 预期效果

- **动态获取的股票数量**：从约170只增加到500+只
- **数据源可靠性**：多个动态数据源提供冗余，单个失败不影响整体
- **预定义列表作用**：仅作为兜底，确保至少有一些股票
- **股票多样性**：通过多种搜索策略获取更多样化的股票列表

### 注意事项
- 按字母搜索可能会获取一些不相关的股票，但通过 `quoteType` 过滤可以排除大部分
- 如果所有动态数据源都失败，仍然会使用预定义列表作为兜底
- 搜索策略的延迟设置（0.2-0.3秒）可以避免请求过快导致被限流
- 建议监控日志，了解各个数据源的获取情况

## Commit-53ada61 为 fetch-all 接口添加详细日志

### 主要变更点
- 为 `fetch_and_save_all_stocks_from_yahoo` 和 `get_all_tickers_from_yahoo` 函数添加详细的日志记录
- 方便调试和监控 fetch-all 操作的执行情况

### 详细变更说明

#### 问题背景
之前的实现中，fetch-all 操作的日志信息较少，难以了解操作的详细进度、各个数据源的获取情况、失败原因等，不利于调试和监控。

#### 解决方案
为关键函数添加详细的日志记录，包括操作步骤、耗时统计、进度信息、失败详情等。

#### 日志增强内容

1. **fetch_and_save_all_stocks_from_yahoo 函数**：
   - **操作开始/结束标记**：使用分隔线（`=` * 80）标记操作开始和结束
   - **总耗时统计**：记录整个操作的开始时间和总耗时
   - **步骤1：获取股票代码列表**：
     - 记录开始时间和耗时
     - 记录获取到的股票总数和示例（前10只）
   - **步骤2：批量抓取股票信息**：
     - 记录批量抓取参数（delay、总数）
     - 每10只股票记录一次进度（包含成功/失败数、已耗时、预计剩余时间）
     - 记录每只股票的抓取耗时（DEBUG级别）
     - 记录失败的股票代码列表（前20只）
     - 记录抓取阶段的统计信息（成功/失败数、总耗时）
   - **步骤3：保存股票数据**：
     - 记录待保存的股票数量
     - 每10只股票记录一次进度
     - 记录每只股票的保存耗时（DEBUG级别）
     - 记录保存失败的股票代码列表（前20只）
     - 记录保存阶段的统计信息
   - **操作完成总结**：汇总所有统计信息

2. **get_all_tickers_from_yahoo 函数**：
   - **数据源统计**：记录每个数据源的执行情况
     - Yahoo Finance API：成功/失败、获取数量、新增数量、耗时
     - Yahoo Finance 页面：成功/失败、获取数量、新增数量、耗时
     - Wikipedia（S&P 500、NASDAQ）：获取数量、新增数量
     - 预定义列表：获取数量、新增数量、耗时
   - **数据源汇总**：输出所有数据源的统计信息表格
   - **最终统计**：记录总股票数、总耗时、是否动态获取
   - **股票代码示例**：记录前20只股票代码

### 日志级别说明

- **INFO**：主要步骤、进度、统计信息（默认显示）
- **DEBUG**：每只股票的详细操作（需要设置日志级别为DEBUG）
- **WARNING**：失败和警告信息
- **ERROR**：错误信息

### 日志示例

**操作开始**:
```
================================================================================
开始执行 fetch_and_save_all_stocks_from_yahoo 操作
参数: delay=1.0, progress_callback=已设置
步骤1: 开始获取股票代码列表...
```

**数据源统计**:
```
================================================================================
数据源统计信息:
  Yahoo Finance API: 成功 | 获取 450 只 | 新增 450 只 | 耗时 12.34秒
  Yahoo Finance 页面: 失败 | 错误: 403 Forbidden | 耗时 2.50秒
  预定义列表: 成功 | 获取 150 只 | 新增 50 只 | 耗时 0.01秒
================================================================================
```

**进度信息**:
```
抓取进度: 50/500 (10%) | 成功: 48 | 失败: 2 | 已耗时: 45.2秒 | 预计剩余: 407.1秒
```

**操作完成**:
```
================================================================================
操作完成总结: 总耗时 452.34 秒 | 股票总数 500 | 抓取成功 485 | 抓取失败 15 | 保存成功 480 | 保存失败 20
================================================================================
```

### 关键代码片段

**步骤标记和耗时统计**:
```python
logger.info("=" * 80)
logger.info("开始执行 fetch_and_save_all_stocks_from_yahoo 操作")
start_time = time.time()

# ... 操作 ...

total_elapsed = time.time() - start_time
logger.info(f"操作完成总结: 总耗时 {total_elapsed:.2f} 秒")
logger.info("=" * 80)
```

**进度记录**:
```python
if (idx + 1) % 10 == 0 or idx == total - 1:
    elapsed = time.time() - fetch_start_time
    avg_time = elapsed / (idx + 1)
    remaining = avg_time * (total - idx - 1)
    logger.info(
        f"抓取进度: {idx + 1}/{total} ({int((idx + 1) / total * 100)}%) | "
        f"成功: {fetch_success} | 失败: {fetch_failed} | "
        f"已耗时: {elapsed:.1f}秒 | 预计剩余: {remaining:.1f}秒"
    )
```

**数据源统计**:
```python
data_source_stats["Yahoo Finance API"] = {
    "success": True,
    "count": len(api_tickers),
    "added": added_count,
    "elapsed": api_elapsed,
}
```

### 注意事项
- DEBUG 级别的日志需要设置日志级别为 DEBUG 才能看到
- 日志输出可能会比较多，建议使用日志轮转或过滤
- 预计剩余时间的计算基于当前平均速度，可能不够准确
- 失败的股票代码列表只显示前20只，避免日志过长

## 变更记录 - 废弃旧技术方案，创建新的技术方案和路线文档

### 主要变更点
- 废弃之前的前端改版技术方案和技术路线文档
- 创建新的技术方案文档，聚焦 Playground 页面和 BFF 架构设计
- 创建新的技术路线文档，详细拆解任务

### 详细变更说明

#### 文档管理
1. **废弃旧文档**：
   - 将 `技术方案设计-前端改版.md` 移动到 `archived/` 目录
   - 将 `技术路线-前端改版.md` 移动到 `archived/` 目录
   - 旧文档已归档，不再使用

2. **创建新文档**：
   - 创建 `技术方案设计.md`：新的技术方案文档
   - 创建 `技术路线-Playground与BFF架构设计.md`：新的技术路线文档

#### 新阶段任务

**主要任务**：
1. **Playground 页面开发**：
   - 在新的前端项目中，增加一个 playground 页面
   - 用于访问和测试三个后端服务（Node.js、Python、Rust）
   - 提供统一的 CRUD 操作界面

2. **BFF 架构 API 层设计**：
   - 设计新的 API 层，支持当前直接调用后端服务
   - 使用适配器模式，支持后续平滑过渡到 BFF 架构
   - 预留 BFF 适配器接口

#### 技术方案要点

**API 层架构设计**：
- **适配器模式**：
  - `ApiAdapter` 接口：统一的适配器接口
  - `DirectAdapter`：直接调用后端服务（当前使用）
  - `BffAdapter`：BFF 适配器（预留）
- **统一 API 客户端**：
  - `ApiClient` 类：统一的 API 客户端
  - 支持依赖注入，切换适配器
  - 支持请求/响应拦截器（预留）
- **服务层封装**：
  - `api/services/node.ts`：Node.js 服务 API
  - `api/services/python.ts`：Python 服务 API
  - `api/services/rust.ts`：Rust 服务 API

**Playground 页面设计**：
- **页面结构**：
  - `/playground`：主页面（服务选择）
  - `/playground/node`：Node.js 服务测试页面
  - `/playground/python`：Python 服务测试页面
  - `/playground/rust`：Rust 服务测试页面
- **功能**：
  - 统一的 CRUD 操作界面
  - 数据列表展示
  - 创建/更新/删除操作
  - 加载状态和错误处理

#### 技术路线拆解

**Phase 1：API 层基础架构**（核心）
- 设计适配器接口和类型定义
- 实现 DirectAdapter
- 创建统一 ApiClient
- 实现三个服务的 API 封装
- 配置环境变量和 Runtime Config

**Phase 2：Playground 页面开发**（核心）
- 创建 Playground 主页面
- 创建三个服务的测试页面
- 实现 CRUD 操作界面
- 更新导航菜单配置

**Phase 3：功能完善**（重要）
- 添加请求/响应拦截器（预留）
- 完善错误处理
- 优化用户体验

**Phase 4：BFF 准备**（后续）
- 预留 BffAdapter 接口
- 设计 BFF API 规范文档

**Phase 5：测试和验证**（重要）
- 功能测试
- 代码质量检查

### 关键代码片段

**适配器接口设计**:
```typescript
interface ApiAdapter {
  get<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>>
  post<T>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>
  put<T>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>
  delete<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>>
}
```

**ApiClient 使用示例**:
```typescript
// 当前使用 DirectAdapter
const apiClient = new ApiClient(new DirectAdapter())

// 后续切换到 BFF
const apiClient = new ApiClient(new BffAdapter())
```

### 注意事项
- 新文档聚焦当前阶段的具体任务（Playground 页面 + BFF 架构设计）
- 技术方案和技术路线文档已更新，反映新的开发方向
- 旧文档已归档，保留历史记录
- 后续开发将按照新的技术路线进行

#### 文档命名优化
- 将 `技术方案设计.md` 重命名为 `技术方案设计-前端开发.md`，便于 AI-Agent 识别
- 将 `技术路线-Playground与BFF架构设计.md` 重命名为 `技术路线-前端开发.md`，统一命名规范
- 删除 archived 目录下的废弃文档（`技术方案设计-前端改版.md`、`技术路线-前端改版.md`）

## 变更记录 - 前端项目重构：废弃旧实现，使用模版项目重新初始化

### 主要变更点
- 删除现有的 frontend 文件夹（旧的前端实现）
- 使用 `npx nuxi@latest init` 初始化新的 Nuxt 项目
- 使用模版项目：`github:dianprata/nuxt-shadcn-dashboard`
- 创建对比分析文档，总结新旧项目差异

### 详细变更说明

#### 问题背景
现有的简单前端实现不具备可扩展性，尝试对项目进行迭代但不成功。因此决定废弃现有实现，使用社区已有的成熟模版项目重新实现。

#### 执行步骤

1. **删除旧项目**：
   - 完全删除 `frontend/` 文件夹及其所有内容
   - 包括旧的 API 封装、组件、页面等

2. **初始化新项目**：
   - 使用命令：`npx nuxi@latest init -t github:dianprata/nuxt-shadcn-dashboard frontend`
   - 选择包管理器：pnpm（符合项目规范）
   - 成功创建基于 Nuxt 4 + Shadcn Vue + TailwindCSS 4 的新项目

3. **创建对比文档**：
   - 创建 `docs/前端项目重构对比分析.md` 文档
   - 详细对比新旧项目的技术栈、项目结构、配置文件等
   - 列出需要迁移的内容和下一步行动

#### 新项目特点

**技术栈升级**：
- Nuxt 3.13.0 → Nuxt 4.1.3
- Tailwind CSS 3 → TailwindCSS 4
- 新增 Shadcn Vue 组件库（300+ 组件）
- 新增完整的 TypeScript 支持
- 新增 ESLint 代码检查

**项目结构**：
- 使用 Nuxt 4 的 `app/` 目录结构
- 完整的布局系统（default, blank）
- 丰富的示例页面（认证、错误页、设置、Kanban、任务管理等）
- 完整的主题系统（深色/浅色模式、多种主题颜色）

**开发体验**：
- 完整的 ESLint 配置（@antfu/eslint-config）
- TypeScript 类型检查（vue-tsc）
- 代码格式化工具
- 完整的组件库和示例

#### 需要迁移的内容

1. **API 封装**（必须迁移）：
   - `api/node.ts` - Node.js 服务 API 封装
   - `api/python.ts` - Python 服务 API 封装
   - `api/rust.ts` - Rust 服务 API 封装
   - `composables/useApi.ts` - 统一 API 调用封装

2. **配置文件**（必须添加）：
   - `.env.example` - 环境变量配置
   - `Dockerfile` 和 `.dockerignore` - Docker 支持
   - `nuxt.config.ts` 中的 Runtime Config - API 地址配置

3. **应用信息**（需要更新）：
   - `app.vue` 中的 title 和 meta 信息
   - 应用名称和描述

### 关键代码片段

**新项目 nuxt.config.ts**:
```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css'],
  vite: {
    plugins: [tailwindcss()],
  },
  modules: [
    'shadcn-nuxt',
    '@vueuse/nuxt',
    '@nuxt/eslint',
    '@nuxt/icon',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    '@nuxt/fonts',
  ],
  shadcn: {
    prefix: '',
    componentDir: '~/components/ui',
  },
  compatibilityDate: '2024-12-14',
});
```

**需要添加的 Runtime Config**:
```typescript
runtimeConfig: {
  public: {
    pythonApiUrl: process.env.NUXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000',
    nodeApiUrl: process.env.NUXT_PUBLIC_NODE_API_URL || 'http://localhost:3000',
    rustApiUrl: process.env.NUXT_PUBLIC_RUST_API_URL || 'http://localhost:8080',
  },
},
```

### 注意事项
- 新项目使用 Nuxt 4，需要 Node.js 22.x
- 新项目使用 pnpm 作为包管理器（packageManager: "pnpm@10.10.0"）
- 需要迁移现有的 API 封装到新项目
- 需要添加环境变量配置和 Docker 支持
- 新项目提供了丰富的示例代码，可以作为开发参考
- 建议先熟悉新项目的结构和组件库，再进行业务功能开发
- 对比文档已创建在 `docs/前端项目重构对比分析.md`，包含详细的迁移清单

## 变更记录 - BFF 层设计与实现

### 主要变更点
- 创建了 BFF（Backend For Frontend）层，为前端提供定制化、高聚合度的接口
- 实现了三个视图模块：Dashboard、Items、Stocks
- 实现了四个后台服务客户端：Python、Node、Rust、股票信息服务
- 集成了 Docker 部署方案
- 配置了 Monorepo 管理（pnpm workspace）

### 详细变更说明

#### BFF 层架构设计
- **技术选型**：使用 NestJS 框架，与现有 Node.js 服务技术栈一致
- **项目结构**：按视图拆分模块（dashboard、items、stocks），面向前端页面设计
- **目录组织**：
  - `bff/bff-main/`：主 BFF 服务
  - `src/views/`：视图模块（按前端页面组织）
  - `src/clients/`：后台服务客户端
  - `src/common/`：公共模块（拦截器、过滤器、工具函数）

#### HTTP 客户端模块
实现了四个后台服务的 HTTP 客户端：
- **PythonClient**：调用 Python FastAPI 服务
- **NodeClient**：调用 Node.js Nest.js 服务
- **RustClient**：调用 Rust Axum 服务
- **StockInfoClient**：调用 Python 股票信息服务

所有客户端都配置了超时和重试策略，使用 `@nestjs/axios` 进行 HTTP 请求。

#### 视图模块实现

1. **Dashboard 视图**（`/api/bff/v1/views/dashboard`）：
   - 聚合所有服务的统计信息
   - 获取最近的 Items 和 Stocks 数据
   - 支持部分服务失败，使用 `Promise.allSettled` 处理

2. **Items 视图**（`/api/bff/v1/views/items`）：
   - 聚合 Python、Node、Rust 三个服务的 Items 数据
   - 实现数据格式统一转换
   - 实现数据去重（按 name）和排序（按更新时间）

3. **Stocks 视图**（`/api/bff/v1/views/stocks`）：
   - 聚合股票信息服务的数据
   - 支持获取所有股票和单个股票信息

#### 公共模块

1. **统一响应格式**：
   - 使用 `TransformInterceptor` 统一响应格式：`{ code, message, data, timestamp }`
   - 全局配置，所有接口自动应用

2. **错误处理**：
   - 使用 `HttpExceptionFilter` 统一错误响应格式
   - 支持部分服务失败，返回空数组或默认值

3. **工具函数**：
   - `promise.util.ts`：提供 `allSettledWithNull`、`withTimeout`、`retry` 等工具函数
   - `transform.util.ts`：提供数据转换、去重、排序等工具函数

#### Monorepo 配置
- 创建了 `pnpm-workspace.yaml`，配置了 workspace
- BFF 项目作为独立的 workspace 包管理
- 支持在根目录统一管理依赖

#### Docker 集成
- 创建了 `bff/bff-main/Dockerfile`，使用多阶段构建
- 使用 Bun 作为运行时
- 集成到根目录 `docker-compose.yml`：
  - BFF 服务依赖所有后台服务
  - 前端服务依赖 BFF 服务（而非直接依赖后台服务）
  - 配置了健康检查和环境变量

### 关键代码片段

**HTTP 客户端示例**:
```typescript
@Injectable()
export class PythonClient {
  private readonly baseUrl: string;

  constructor(private readonly httpService: HttpService) {
    this.baseUrl = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';
  }

  async getItems(): Promise<PythonItem[]> {
    const response = await firstValueFrom(
      this.httpService.get(`${this.baseUrl}/api/v1/items`),
    );
    return response.data.data || [];
  }
}
```

**视图服务示例（数据聚合）**:
```typescript
async getAllItems(): Promise<UnifiedItem[]> {
  // 并行获取所有服务的 items，允许部分失败
  const [pythonItems, nodeItems, rustItems] = await allSettledWithNull([
    this.pythonClient.getItems(),
    this.nodeClient.getItems(),
    this.rustClient.getItems(),
  ]);

  // 转换数据格式并合并去重
  const unifiedItems = [
    ...(pythonItems || []).map(transformPythonItem),
    ...(nodeItems || []).map(transformNodeItem),
    ...(rustItems || []).map(transformRustItem),
  ];

  return sortItemsByUpdatedAt(mergeAndDeduplicateItems(unifiedItems));
}
```

**Docker Compose 配置**:
```yaml
bff-main:
  build:
    context: ./bff/bff-main
    dockerfile: Dockerfile
  ports:
    - "4000:4000"
  environment:
    PYTHON_SERVICE_URL: http://python-service:8000
    NODE_SERVICE_URL: http://node-service:3000
    RUST_SERVICE_URL: http://rust-service:8080
    STOCK_INFO_SERVICE_URL: http://py-stock-info-service:8001
  depends_on:
    python-service:
      condition: service_healthy
    # ... 其他服务依赖
```

### 注意事项
- BFF 层使用端口 4000，避免与现有服务冲突
- 所有接口使用 `/api/bff/v1` 前缀
- 支持部分服务失败，使用 `Promise.allSettled` 处理
- 数据转换和去重逻辑在 Service 层实现
- Docker 环境变量使用服务名（如 `python-service`），而非 `localhost`
- 前端需要更新为调用 BFF 接口，而非直接调用后台服务（待实现）

### 后续工作
- [x] 前端集成：更新前端代码调用 BFF 接口 ✅
- [ ] 单元测试：为 HTTP 客户端和 Service 编写测试
- [ ] 集成测试：测试 BFF 与后台服务的集成
- [ ] 性能优化：实现缓存策略（可选）
- [ ] API 文档：添加 Swagger/OpenAPI 文档（可选）

## 变更记录 - 前端改版与 Stocks 页面开发完成

### 主要变更点
- 完成前端项目重构（Nuxt 4 + Shadcn UI + Tailwind CSS）
- 完成 Dashboard 页面开发
- 完成 Stocks 列表页开发（搜索、筛选、排序、分页、批量操作）
- 完成 Stock 详情页开发
- 完成批量更新页开发（SSE 实时进度追踪）
- 完成 API 层架构设计（适配器模式，支持 BFF 切换）

### 详细变更说明

#### 前端项目重构
- **技术栈升级**：
  - Nuxt 3.13.0 → Nuxt 4.1.3
  - Tailwind CSS 3 → TailwindCSS 4
  - 新增 Shadcn Vue 组件库（300+ 组件）
  - 完整的 TypeScript 支持
  - ESLint 代码检查

- **项目结构**：
  - 使用 Nuxt 4 的 `app/` 目录结构
  - 完整的布局系统（default, blank）
  - 丰富的示例页面和组件
  - 完整的主题系统（深色/浅色模式）

#### API 层架构设计
- **适配器模式**：
  - `ApiAdapter` 接口：统一的适配器接口
  - `DirectAdapter`：直接调用后端服务（当前使用）
  - `BffAdapter`：BFF 适配器（预留）
  - `ApiClient`：统一的 API 客户端，支持依赖注入

- **服务层封装**：
  - `app/api/services/node.ts`：Node.js 服务 API
  - `app/api/services/python.ts`：Python 服务 API
  - `app/api/services/rust.ts`：Rust 服务 API
  - `app/api/services/stocks.ts`：Stocks 服务 API（调用 BFF）

#### Dashboard 页面
- **功能实现**：
  - 统计数据展示（Total Items、Total Stocks）
  - 最近 Items 列表（来自三个后端服务）
  - 最近 Stocks 列表
  - 数据刷新功能
  - 加载状态和错误处理

- **技术实现**：
  - 使用 BFF Dashboard 视图接口：`GET /api/bff/v1/views/dashboard`
  - 使用 Shadcn UI 组件（Card、Table、Skeleton）
  - 响应式设计

#### Stocks 列表页
- **功能实现**：
  - 股票列表展示（表格形式）
  - 搜索功能（按股票代码、名称）
  - 筛选功能（按市场、行业）
  - 排序功能（按更新时间、市值）
  - 分页功能（每页 20/50/100 条）
  - 批量操作（批量更新、批量删除）

- **技术实现**：
  - 使用 BFF Stocks 视图接口：`GET /api/bff/v1/views/stocks`
  - 支持查询参数：`page`, `page_size`, `market`, `sector`, `ticker`, `name`, `sort_by`, `sort_order`
  - 使用 Shadcn UI 组件（Table、Input、Select、Button、Dialog）
  - 响应式设计

#### Stock 详情页
- **功能实现**：
  - 股票详细信息展示
  - 基本信息（代码、名称、市场、行业）
  - 财务指标（市值、P/E、P/B、股息率、52周最高/最低等）
  - 数据源信息
  - 更新/删除操作

- **技术实现**：
  - 使用 BFF Stocks 视图接口：`GET /api/bff/v1/views/stocks/{ticker}`
  - 使用 Shadcn UI 组件（Card、Badge、Button、Dialog）
  - 响应式设计

#### 批量更新页
- **功能实现**：
  - 全量更新选项
  - 延迟设置（0.0-10.0 秒）
  - 实时进度展示（SSE）
  - 进度可视化（进度条、统计信息）
  - 错误处理和重试

- **技术实现**：
  - 使用股票信息服务接口：`POST /api/v1/stocks/fetch-all?delay=1.0`
  - 使用 EventSource API 接收 SSE 进度更新
  - 使用 Shadcn UI 组件（Progress、Card、Button）
  - 实时进度统计（总数、成功数、失败数、预计剩余时间）

### 关键代码片段

**API 客户端使用示例**:
```typescript
// app/api/services/stocks.ts
import { apiClient } from '../client'

export async function getStocks(params?: StocksQueryParams) {
  const response = await apiClient.get<PaginatedResponse<Stock>>(
    '/api/bff/v1/views/stocks',
    { params }
  )
  return response.data
}
```

**SSE 进度追踪示例**:
```typescript
// app/pages/stocks/batch-update.vue
const eventSource = new EventSource(
  `${stockInfoServiceUrl}/api/v1/stocks/fetch-all?delay=${delay}`
)

eventSource.onmessage = (event) => {
  const progress = JSON.parse(event.data)
  // 更新进度状态
  progressState.value = progress
}
```

### 项目完成情况总结

#### ✅ 已完成的核心功能

1. **后端服务**：
   - ✅ Python FastAPI 服务（Items CRUD）
   - ✅ Node.js Nest.js 服务（Items CRUD）
   - ✅ Rust Axum 服务（Items CRUD）
   - ✅ Python 股票信息服务（多数据源支持、SSE 进度推送）

2. **BFF 层**：
   - ✅ Dashboard 视图（数据聚合）
   - ✅ Items 视图（数据聚合）
   - ✅ Stocks 视图（数据聚合，支持分页、筛选、排序）

3. **前端页面**：
   - ✅ Dashboard 页面
   - ✅ Stocks 列表页
   - ✅ Stock 详情页
   - ✅ 批量更新页
   - ✅ Playground 页面（三个后端服务的测试界面）

#### 🚧 进行中的工作

- 文档整理和归档
- 功能增强（数据源扩展、性能优化、错误处理完善）
- 测试和文档（单元测试、集成测试、API 文档）

#### 📋 待完成的工作

- 数据源扩展（Tushare、IEX Cloud、Alpha Vantage）
- 性能优化（缓存策略、查询优化）
- 错误处理完善（统一错误响应格式）
- 单元测试和集成测试
- 部署配置优化

### 注意事项

- 前端已完全切换到 BFF 接口，不再直接调用后端服务
- 所有前端页面都使用 Shadcn UI 组件库，保持一致的 UI 风格
- SSE 进度追踪功能已完整实现，支持实时进度更新
- API 层使用适配器模式，支持后续平滑切换到 BFF 适配器
- 所有核心页面已完成，基本的 stock 信息显示工作已完成

---

**更新时间**：2025-01-11  
**项目版本**：0.2.0  
**阶段**：Phase 2 前端页面开发已完成，进入功能完善阶段

## 变更记录 - 项目文档整理与 Phase 3 规划调整

### 主要变更点
- 全面整理项目文档，更新项目状态描述
- 归档已完成的技术方案和技术路线文档
- 调整 Phase 3 规划，将数据支持模块设为最高优先级
- 添加实时交易情况获取功能的详细设计
- 更新页面交互层映射，添加数据支持和回测框架模块设计
- 在 vibe-kanban 中创建数据支持模块的4个开发任务

### 详细变更说明

#### 项目文档整理
1. **README.md 更新**：
   - 更新项目状态，明确已完成的核心功能
   - 分类展示：后端服务、BFF 层、前端开发
   - 更新版本号：0.1.0 → 0.2.0
   - 更新最后更新时间：2025-01-11

2. **PRD 文档更新**：
   - **PRD-产品需求文档.md**：更新 Phase 2 状态，标记前端页面开发已完成
   - **PRD-Roadmap规划.md**：更新 Phase 2 前端页面开发任务状态，标记验收标准已完成

3. **changelog.md 更新**：
   - 新增章节：记录前端改版与 Stocks 页面开发完成情况
   - 详细记录已完成的核心功能
   - 总结项目完成情况边界

4. **技术路线文档归档**：
   - 将 `技术路线-前端开发.md` 移动到 `docs/archived/`
   - 将 `技术路线-Stocks列表页开发.md` 移动到 `docs/archived/`
   - 将 `技术方案设计-BFF层.md` 移动到 `docs/archived/`
   - 将 `技术路线-BFF层.md` 移动到 `docs/archived/`
   - 将 `技术方案设计-多数据源支持.md` 移动到 `docs/archived/`
   - 将 `技术路线-多数据源支持.md` 移动到 `docs/archived/`
   - 将 `技术路线-产品功能架构与Roadmap.md` 移动到 `docs/archived/`
   - 将 `技术方案设计-前端开发.md` 移动到 `docs/archived/`
   - 更新 `docs/archived/README.md`，添加新归档文档说明

5. **技术方案设计文档更新**：
   - 更新 `技术方案设计-前端开发.md`，添加项目完成情况章节
   - 标记已完成的任务和进行中的工作

#### Phase 3 规划调整
1. **优先级调整**：
   - 数据支持模块：P0（最高优先级，优先执行）
   - 回测引擎：P0（依赖数据支持）
   - 预设算法：P0（依赖数据支持和技术指标）
   - 量化交易服务：P1（重要）

2. **数据支持模块细化设计**（5个子模块）：
   - **4.2.1.1 历史K线数据获取与存储**：数据源集成、数据获取、数据存储、数据管理
   - **4.2.1.2 历史数据质量保证**：数据质量检查、数据修复机制、数据验证
   - **4.2.1.3 技术指标计算**：基础指标、高级指标、计算引擎、数据管理
   - **4.2.1.4 数据服务接口**：后端服务、BFF 层集成、前端界面
   - **4.2.1.5 数据同步与更新**：定时任务、同步策略

3. **实时交易情况获取功能设计**（P1，新增）：
   - **4.2.1.6.1 实时行情数据获取**：数据源集成、数据类型、获取方式
   - **4.2.1.6.2 实时数据订阅与管理**：订阅机制、订阅管理、推送策略
   - **4.2.1.6.3 实时数据存储与缓存**：存储设计、缓存策略、查询接口
   - **4.2.1.6.4 WebSocket 服务与连接管理**：WebSocket 服务、连接管理、消息协议
   - **4.2.1.6.5 实时数据服务接口**：后端服务、BFF 层集成、前端界面
   - **4.2.1.6.6 性能优化与容错**：性能优化、容错机制、监控告警
   - **4.2.1.6.7 实时数据应用场景**：量化交易场景、数据展示场景、数据分析场景

#### 页面交互层映射更新
1. **对比现有实现并更新**：
   - **Stocks 列表页**：补充 URL 参数同步、实时搜索等实现细节
   - **Stock 详情页**：补充 404 处理、加载状态等实现细节
   - **批量更新页**：补充 SSE 连接状态、取消操作等实现细节

2. **添加数据支持模块**（Stocks 二级模块，4个页面）：
   - **2.5.1 历史数据管理页** (`/stocks/data/history`)：历史K线数据查询、更新、删除、统计
   - **2.5.2 技术指标计算页** (`/stocks/data/indicators`)：技术指标计算、结果展示、可视化
   - **2.5.3 实时行情展示页** (`/stocks/data/realtime`)：WebSocket 实时数据推送、五档买卖盘
   - **2.5.4 数据订阅管理页** (`/stocks/data/subscriptions`)：订阅/取消订阅、推送频率配置

3. **添加回测框架模块**（一级模块，5个页面）：
   - **2.6.1 算法列表页** (`/backtesting/algorithms`)：算法浏览、搜索、筛选
   - **2.6.2 算法详情页** (`/backtesting/algorithms/{id}`)：算法信息、参数、回测历史
   - **2.6.3 回测配置页** (`/backtesting/configure`)：算法选择、股票选择、参数配置
   - **2.6.4 回测结果页** (`/backtesting/results/{id}`)：回测结果摘要、收益曲线、交易记录
   - **2.6.5 回测分析页** (`/backtesting/analysis/{id}`)：收益分析、风险分析、交易分析、持仓分析

4. **更新导航结构**：
   - 更新侧边栏导航，添加数据支持模块和回测框架模块
   - 更新页面跳转关系，包含新模块的跳转路径

#### Vibe-Kanban 任务创建
1. **Phase 2 剩余工作任务**（2个）：
   - **Phase 2 功能增强**：数据源扩展、性能优化、错误处理完善（P1）
   - **Phase 2 测试和文档**：单元测试、集成测试、文档完善（P2）

2. **数据支持模块开发任务**（4个）：
   - **技术架构详细设计**：数据模型、服务架构、接口设计（P0）
   - **基本服务层实现**：历史数据服务、技术指标服务（P0，可独立开发）
   - **BFF层实现**：历史数据视图、技术指标视图（P0，可独立开发）
   - **前端实现**：历史数据管理页、技术指标计算页（P0，可独立开发）

### 关键成果

#### 文档整理成果
- ✅ 所有项目文档已更新，反映当前项目状态
- ✅ 已完成的技术方案和技术路线文档已归档（8个文档）
- ✅ 项目完成情况边界已明确，便于后续开发规划

#### Phase 3 规划成果
- ✅ 数据支持模块已设为最高优先级（P0）
- ✅ 数据支持模块设计已细化（5个子模块，共30+个功能点）
- ✅ 实时交易情况获取功能设计已完成（7个子模块，共40+个功能点）
- ✅ 执行顺序已明确：数据支持 → 回测引擎 → 预设算法

#### 页面设计成果
- ✅ 数据支持模块页面设计已完成（4个页面）
- ✅ 回测框架模块页面设计已完成（5个页面）
- ✅ 页面交互设计已详细说明（页面结构、交互设计、API 调用）

#### 任务管理成果
- ✅ Phase 2 剩余工作任务已创建（2个任务）
- ✅ 数据支持模块开发任务已创建（4个任务，可独立开发）

### 项目当前状态总结

#### ✅ 已完成的核心功能

**后端服务层**：
- ✅ Python/Node.js/Rust 三个服务的完整 CRUD API
- ✅ 股票信息服务（多数据源支持、SSE 进度推送）

**BFF 层**：
- ✅ Dashboard、Items、Stocks 三个视图模块
- ✅ 数据聚合、格式转换、容错处理

**前端页面**：
- ✅ Dashboard 页面（统计数据、最近数据列表）
- ✅ Stocks 列表页（搜索、筛选、排序、分页、批量操作）
- ✅ Stock 详情页（详细信息、更新/删除）
- ✅ 批量更新页（SSE 实时进度追踪）

#### 🚧 进行中的工作

- ✅ 文档整理和归档（本次已完成）
- 🚧 功能增强（数据源扩展、性能优化、错误处理完善）
- 🚧 测试和文档（单元测试、集成测试、API 文档）

#### 📋 待完成的工作

**Phase 2 剩余工作**：
- 数据源扩展（Tushare、IEX Cloud、Alpha Vantage）
- 性能优化（缓存策略、查询优化）
- 错误处理完善（统一错误响应格式）
- 单元测试和集成测试

**Phase 3 核心工作**（已规划）：
- 数据支持模块（P0，最高优先级）
- 回测引擎（P0，依赖数据支持）
- 预设算法（P0，依赖数据支持和技术指标）
- 实时交易情况获取（P1，重要）

### 注意事项

- 所有文档已更新，反映当前项目状态
- 已完成的技术路线文档已归档到 `docs/archived/` 目录
- Phase 3 规划已调整，数据支持模块为最高优先级
- 数据支持模块的4个开发任务已创建，可以独立开发
- 页面交互层映射已更新，包含数据支持和回测框架模块设计

---

**更新时间**：2025-01-12  
**项目版本**：0.2.0  
**阶段**：Phase 2 前端页面开发已完成，Phase 3 规划已完成，进入数据支持模块开发阶段

## 变更记录 - 数据支持模块前端基础实现（部分）

### 主要变更点
- 实现了历史数据和技术指标功能的前端基础
- 功能集成到股票详情页，采用 Tab 切换方式
- 提供 Mock 数据支持，可独立开发和测试
- 暂不实现数据质量检查和数据同步管理功能

### 详细变更说明

#### 功能实现范围

本次仅实现了数据支持模块的部分功能，重点在于历史数据查询和技术指标计算的基础能力：

**已实现的功能**（集成到股票详情页）：
1. **历史K线数据查询**：
   - 查询历史K线数据（按时间周期、日期范围）
   - K线图可视化（使用 ECharts）
   - 时间周期切换（分时、日K、周K、月K 等）
   - 数据更新功能（SSE 进度追踪）

2. **技术指标计算与展示**：
   - 多指标选择和切换
   - 指标叠加显示（在 K线图上）
   - 支持的指标列表展示
   - 自动计算缺失的指标数据

**未实现的功能**（保留为后续任务）：
- 数据质量检查和修复
- 数据同步任务管理
- 批量历史数据管理

#### 技术实现

1. **API 服务封装**：
   - `frontend/app/api/services/historical-data.ts` - 历史数据服务
   - `frontend/app/api/services/indicators.ts` - 技术指标服务
   - 支持 Mock 模式（默认启用，直到 BFF 层实现完成）

2. **Composables 封装**：
   - `frontend/app/composables/useHistoricalData.ts` - 历史数据服务访问
   - `frontend/app/composables/useIndicators.ts` - 技术指标服务访问
   - `frontend/app/composables/useStockHistory.ts` - 统一管理历史数据和指标逻辑

3. **组件实现**：
   - `frontend/app/components/stocks/KlineChart.vue` - K线图组件
   - `frontend/app/components/stocks/IndicatorChart.vue` - 指标图表组件（支持多指标叠加）
   - `frontend/app/components/stocks/StockHistoryTab.vue` - 历史数据 Tab 组件
   - `frontend/app/components/stocks/PeriodSelector.vue` - 时间周期选择器
   - `frontend/app/components/stocks/IndicatorSelector.vue` - 技术指标选择器
   - `frontend/app/components/common/SSEProgress.vue` - SSE 进度展示组件

4. **Mock 数据支持**：
   - `frontend/app/api/mock/data-support.ts` - Mock 数据生成器
   - `frontend/app/api/adapters/mock-bff.ts` - Mock BFF 适配器
   - 支持历史数据和技术指标的 Mock 数据
   - 支持 SSE 进度模拟

5. **类型定义扩展**（`frontend/app/api/types.ts`）：
   - `HistoricalData` - 历史K线数据
   - `HistoricalDataQueryParams` - 历史数据查询参数
   - `HistoricalDataStatistics` - 历史数据统计
   - `IndicatorData` - 技术指标数据
   - `IndicatorQueryParams` - 指标查询参数
   - `SupportedIndicator` - 支持的指标类型
   - `SSEProgress` - SSE 进度信息

6. **页面集成**：
   - 股票详情页（`/stocks/[ticker]`）新增"历史数据" Tab
   - 使用 Tabs 组件组织内容（基本信息 / 历史数据）
   - 历史数据 Tab 包含：K线图、指标叠加、周期切换、数据更新

#### 架构设计

**集成方式**：
- 采用 Tab 集成而非独立页面，减少导航复杂度
- 历史数据和技术指标功能集中在股票详情页
- 使用 Composable 模式统一管理状态和逻辑
- 组件化设计，易于复用和维护

**Mock 策略**：
- 仅 Mock 数据支持模块的新接口（historical-data, indicators）
- 已上线的接口（stocks, dashboard）继续使用真实 BFF
- 通过环境变量控制 Mock 开关（`NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK`）

**数据流**：
```
前端组件 → Composable (useStockHistory) → API Service (HistoricalDataService/IndicatorsService) 
   → Mock Adapter (开发阶段) / BFF Adapter (生产阶段) → BFF 层 → 后端服务
```

### 关键代码片段

**股票详情页 Tab 集成**:

```vue
<Tabs v-model="activeTab">
  <TabsList class="grid w-full grid-cols-2">
    <TabsTrigger value="info">基本信息</TabsTrigger>
    <TabsTrigger value="history">历史数据</TabsTrigger>
  </TabsList>
  <TabsContent value="info">
    <StockInfoTab :stock="stock" />
  </TabsContent>
  <TabsContent value="history">
    <StockHistoryTab :ticker="ticker" />
  </TabsContent>
</Tabs>
```

**统一管理逻辑（useStockHistory）**:

```typescript
export function useStockHistory(ticker: Ref<string>) {
  // 历史数据管理
  const historicalData = ref<HistoricalData[]>([])
  // 技术指标管理（支持多选）
  const selectedIndicators = ref<string[]>([])
  const indicatorDataMap = ref<Record<string, IndicatorData[]>>({})
  
  // 加载历史数据
  async function loadHistoricalData() { ... }
  // 切换指标（自动加载或计算）
  async function toggleIndicator(indicatorName: string) { ... }
  
  return { historicalData, selectedIndicators, ... }
}
```

**多指标叠加图表**:

```vue
<IndicatorChart
  :kline-data="historicalData"
  :indicator-data-map="indicatorDataMap"
  :selected-indicators="selectedIndicators"
  :period="period"
/>
```

### 技术亮点

1. **组件化设计**：
   - 图表组件独立封装（KlineChart, IndicatorChart）
   - 选择器组件独立封装（PeriodSelector, IndicatorSelector）
   - SSE 进度组件通用化

2. **多指标支持**：
   - 支持同时选择多个指标
   - 主图指标（MA、BOLL）叠加在 K线图上
   - 附图指标（RSI、MACD）单独显示在下方

3. **智能计算**：
   - 选择指标时自动检查数据是否存在
   - 如果数据不存在，自动调用计算接口
   - 计算失败自动回滚，保证用户体验

4. **Mock 数据支持**：
   - 完整的 Mock 数据生成器
   - 模拟真实的 SSE 进度更新
   - 支持独立开发，无需等待后端

### 文档归档

所有数据支持模块的技术方案和技术路线文档已归档到 `docs/archived/` 目录：
- `archived/技术方案设计-数据支持模块-前端实现.md`
- `archived/技术方案设计-数据支持模块-BFF层实现.md`
- `archived/技术方案设计-数据支持模块-后台服务.md`
- `archived/技术路线-数据支持模块-前端实现.md`
- `archived/技术路线-数据支持模块-BFF层.md`
- `archived/技术路线-数据支持模块-服务层.md`
- `archived/技术调研-数据支持模块.md`

### 注意事项

1. **Mock 模式**：
   - 默认启用 Mock，前端可独立开发
   - 环境变量 `NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK=false` 可切换到真实 BFF

2. **后续开发**：
   - BFF 层需要实现 `historical-data` 和 `indicators` 视图模块
   - 后端服务需要实现历史数据获取和技术指标计算功能
   - 数据质量检查和数据同步功能保留为后续任务

3. **已安装依赖**：
   - `echarts` - 图表库
   - `vue-echarts` - Vue ECharts 封装

4. **设计决策**：
   - 采用集成方式而非独立页面，减少导航复杂度
   - 优先实现核心功能（历史数据、技术指标），延后质量检查和同步管理
   - 使用 Composable 模式统一管理逻辑，提高代码复用性

---

**更新时间**：2025-01-20  
**项目版本**：0.3.1  
**阶段**：Phase 3 数据支持模块 BFF 层实现完成

## 变更记录 - 数据支持模块 BFF 层实现完成

### 主要变更点
- 实现了历史数据视图和技术指标视图的 BFF 层
- 创建了 HTTP 客户端用于调用后台服务
- 实现了 SSE 代理功能，支持实时进度推送
- 所有代码通过编译和 lint 检查

### 详细变更说明

#### HTTP 客户端实现（2个）

1. **历史数据服务客户端** (`bff/bff-main/src/clients/historical-data.client.ts`)：
   - `getKlineData` - 获取历史K线数据
   - `updateKlineData` - 更新历史K线数据
   - `getKlineDataStatistics` - 获取统计数据
   - `deleteKlineData` - 删除历史数据
   - 完善的错误处理和超时配置

2. **技术指标服务客户端** (`bff/bff-main/src/clients/indicators.client.ts`)：
   - `getSupportedIndicators` - 获取支持的指标列表
   - `calculateIndicator` - 计算技术指标
   - `queryIndicatorData` - 查询技术指标数据
   - 完善的错误处理和超时配置

#### 历史数据视图实现（6个接口）

**服务层** (`historical-data.service.ts`)：
- `getKlineData` - 获取历史数据（支持分页/非分页模式）
- `updateKlineData` - 更新历史数据
- `getKlineDataStatistics` - 获取统计信息
- `deleteKlineData` - 删除历史数据
- `batchUpdateKlineDataSSE` - 批量更新（SSE 代理）
- `fullUpdateKlineDataSSE` - 全量更新（SSE 代理）

**控制器层** (`historical-data.controller.ts`)：
- `GET /api/bff/v1/views/historical-data/:ticker` - 获取历史数据
- `GET /api/bff/v1/views/historical-data/:ticker/statistics` - 获取统计
- `POST /api/bff/v1/views/historical-data/:ticker/update` - 更新数据
- `GET /api/bff/v1/views/historical-data/batch` - 批量更新（SSE）
- `GET /api/bff/v1/views/historical-data/full-update` - 全量更新（SSE）
- `DELETE /api/bff/v1/views/historical-data/:ticker` - 删除数据

#### 技术指标视图实现（4个接口）

**服务层** (`indicators.service.ts`)：
- `getSupportedIndicators` - 获取支持的指标列表
- `calculateIndicator` - 计算技术指标
- `queryIndicatorData` - 查询指标数据（支持分页/非分页模式）
- `batchCalculateIndicatorsSSE` - 批量计算（SSE 代理）

**控制器层** (`indicators.controller.ts`)：
- `GET /api/bff/v1/views/indicators/supported` - 获取支持的指标
- `POST /api/bff/v1/views/indicators/:ticker/calculate` - 计算指标
- `GET /api/bff/v1/views/indicators/:ticker` - 获取指标数据
- `GET /api/bff/v1/views/indicators/batch-calculate` - 批量计算（SSE）

#### 模块注册

- 更新 `clients.module.ts` 注册新客户端
- 更新 `views.module.ts` 注册新视图模块
- 创建 `historical-data.module.ts` 和 `indicators.module.ts`

### 技术亮点

1. **分页逻辑智能切换**：
   - 根据是否有 `page` 或 `page_size` 参数，自动切换分页/非分页模式
   - 分页模式：返回 `{ items, total, page, page_size, total_pages }`
   - 非分页模式：返回 `{ ticker, period, count, data }`

2. **SSE 代理实现**：
   - 使用 axios 接收后台服务的 SSE 流
   - 将流转发给前端，支持实时进度追踪
   - 完善的错误处理和超时处理

3. **参数验证**：
   - 使用 NestJS 的 `ParseIntPipe` 和 `ParseBoolPipe` 进行参数验证
   - 使用 `DefaultValuePipe` 提供默认值

4. **错误处理**：
   - 允许部分失败，返回空数据而不是抛出错误
   - 详细的错误日志记录

### 关键代码片段

**分页逻辑实现**:
```typescript
async getKlineData(ticker: string, params?: HistoricalDataQueryParams) {
  const hasPagination = params?.page !== undefined || params?.page_size !== undefined;
  const data = await this.historicalDataClient.getKlineData(ticker, params);
  
  if (hasPagination) {
    return { items: data, total, page, page_size, total_pages };
  } else {
    return { ticker, period, count, data };
  }
}
```

**SSE 代理实现**:
```typescript
async batchUpdateKlineDataSSE(tickers: string[], params: any, res: Response) {
  const url = `${this.baseUrl}/api/v1/historical-data/batch`;
  const response = await firstValueFrom(
    this.httpService.get(url, { responseType: 'stream', ... })
  );
  response.data.pipe(res);  // 将后端流转发给前端
}
```

### 验收标准检查

#### ✅ HTTP 客户端
- [x] 历史数据客户端可以正常调用后台服务（4个方法）
- [x] 技术指标客户端可以正常调用后台服务（3个方法）
- [x] 错误处理完善

#### ✅ 历史数据视图
- [x] 6个 API 接口实现完成
- [x] 分页和非分页模式都正常
- [x] 请求参数验证正确
- [x] SSE 代理正常工作

#### ✅ 技术指标视图
- [x] 4个 API 接口实现完成
- [x] 分页和非分页模式都正常
- [x] 请求参数验证正确
- [x] SSE 代理正常工作

#### ✅ 代码质量
- [x] 所有代码通过编译检查
- [x] 所有代码通过 lint 检查
- [x] 模块可以正常启动
- [x] 向后兼容性保证

### 注意事项

1. **SSE 接口使用 GET 方法**：
   - EventSource API 只支持 GET 请求
   - 所有 SSE 接口都使用 GET 方法而非 POST

2. **后台服务依赖**：
   - BFF 层已实现完成，等待后台服务准备好
   - 前端可以继续使用 Mock 模式，直到后台服务准备好
   - 前端只需要切换环境变量 `NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK=false` 即可切换到真实 BFF

3. **数据质量和同步功能暂缓**：
   - 根据前端实际需求，数据质量检查和数据同步功能暂缓实施
   - 优先完成核心的历史数据和技术指标功能

4. **下一步工作**：
   - 后台服务层实现（历史数据服务、技术指标服务）
   - 前端切换到真实 BFF（修改环境变量）
   - 端到端集成测试

---

**更新时间**：2025-01-20  
**项目版本**：0.3.1  
**阶段**：Phase 3 数据支持模块 BFF 层实现完成

## 变更记录 - 数据支持模块服务层任务拆分

### 主要变更点
- 将数据支持模块服务层任务拆分为4个独立可验证的功能模块
- 在 vibe-kanban 中创建了4个任务
- 更新了相关文档，反映实际的任务拆分情况

### 详细变更说明

#### 任务拆分

根据**独立可验证的功能模块**原则，将原技术路线中的7个阶段、17个子任务合并为4个独立任务：

**任务1：数据模型和历史数据服务实现**
- 任务ID: `4f980cc7-6edf-4db6-9411-c15a8b57b4fe`
- 包含：MongoDB TimeSeries Collection 数据模型 + 历史K线数据获取、存储、查询、更新、删除功能
- 依赖：无
- 状态：待开始

**任务2：技术指标服务实现**
- 任务ID: `005049e7-45cf-4159-a8ee-b4f3ed2ea4ff`
- 包含：技术指标计算引擎（TA-Lib/pandas-ta）+ 基础指标计算 + 指标存储和查询功能
- 依赖：任务1
- 状态：待开始

**任务3：数据质量和同步服务实现**
- 任务ID: `87678c0f-14a6-4332-a8fb-e1c234356571`
- 包含：数据完整性、准确性、一致性检查 + 定时任务管理 + 数据同步机制
- 依赖：任务1
- 状态：待开始

**任务4：API 路由和服务集成**
- 任务ID: `175e2dbb-28e6-471d-8a7a-6c798b13fb94`
- 包含：历史数据 API（6个接口）+ 技术指标 API（4个接口）+ 数据质量和同步 API + 服务集成 + 单元测试 + 与BFF层联调
- 依赖：任务1、2、3
- 状态：待开始

#### 任务拆分优势

- ✅ 每个任务都是独立可验证的功能模块（可以独立测试和验证）
- ✅ 任务数量合理（4个任务，符合建议范围 3-5 个）
- ✅ 依赖关系简单（主要是简单的串行依赖，便于执行）
- ✅ 功能边界清晰（每个任务对应一个完整的功能领域）
- ✅ 避免过度拆分（不会将开发步骤拆分为独立任务）

#### 推荐执行顺序

1. **先执行任务1**（数据模型和历史数据服务）- 这是核心基础
2. **并行执行任务2和任务3**（技术指标服务、数据质量和同步服务）- 它们都依赖任务1，但彼此独立
3. **最后执行任务4**（API 路由和服务集成）- 集成所有服务

#### 文档更新

更新了以下文档，反映实际的任务拆分情况：

1. **`docs/技术路线-数据支持模块-服务层.md`**：
   - 添加了 Vibe-Kanban 任务管理章节
   - 添加了任务拆分说明
   - 更新了任务依赖关系图
   - 添加了 Vibe-Kanban 任务管理说明和开发建议

2. **`docs/PRD-Roadmap规划.md`**：
   - 更新了数据支持模块的实现状态
   - 添加了 Vibe-Kanban 任务管理表格
   - 添加了推荐执行顺序说明
   - 更新了文档版本（v1.1 → v1.2）

### 关键代码片段

（本次变更主要为文档更新和任务拆分，无代码变更）

### 注意事项

- 所有任务已在 vibe-kanban 中创建，可以开始执行
- 推荐先执行任务1（数据模型和历史数据服务），这是核心基础
- 任务2和任务3可以并行开发
- 详细的技术路线和任务拆解参见 `docs/技术路线-数据支持模块-服务层.md`
- BFF 层已完成（2025-01-20），等待后台服务准备好后进行联调测试

---

**更新时间**：2025-01-20  
**项目版本**：0.3.2  
**阶段**：Phase 3 数据支持模块服务层任务拆分完成
