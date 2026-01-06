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
