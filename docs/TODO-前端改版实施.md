# TODO: 前端改版实施

> 本任务基于技术路线文档执行前端改版工作，将现有基础 dashboard 改造成管理台应用。

## 任务概述

**目标**：将现有基础 dashboard 改造成管理台应用，支持快速添加新功能，并提前规划 BFF 数据接入层。

**参考项目**：https://github.com/dianprata/nuxt-shadcn-dashboard

**技术方案**：采用激进方案，直接复用参考项目的 `app/` 目录结构，最大化复用代码。

**相关文档**：
- `docs/技术方案设计-前端改版.md` - 完整的技术方案
- `docs/技术路线-前端改版.md` - 详细的任务拆解
- `docs/前端改版开发指南.md` - 开发指南和操作说明

## Phase 1：基础架构搭建

### 任务 1.2：重构项目结构并安装依赖

**状态**：⏳ 待开始

**任务描述**：
重构项目为 `app/` 目录结构（Nuxt 3.8+），安装所有参考项目的依赖，从参考项目复制配置文件。

**完成标准**：
- [ ] 创建 `app/` 目录结构
- [ ] 迁移现有文件到 `app/` 目录（pages、components、composables、api 等）
- [ ] 安装所有参考项目的依赖：
  - `shadcn-nuxt@2.3.1+`
  - `reka-ui@^2.5.1`
  - `tailwindcss@^4.1.14` + `@tailwindcss/vite@^4.1.14`
  - `lucide-vue-next@^0.482.0` + `@nuxt/icon@^1.15.0`
  - `tailwind-merge@^2.6.0` + `clsx@^2.1.1` + `class-variance-authority@^0.7.1`
  - `@nuxtjs/color-mode@^3.5.2` + `@vueuse/nuxt@^12.8.2`
  - `tw-animate-css@^1.4.0`
- [ ] 从参考项目复制 `components.json` 到 `app/components.json`
- [ ] 从参考项目复制 `app.config.ts` 到 `app/app.config.ts`
- [ ] 更新 `nuxt.config.ts`：
  - 移除 `@nuxtjs/tailwindcss` 模块
  - 添加 `@tailwindcss/vite` 插件
  - 添加 `shadcn-nuxt` 模块和配置
  - 添加其他必要的模块

**操作步骤**：
1. 克隆参考项目到临时目录：`git clone https://github.com/dianprata/nuxt-shadcn-dashboard.git /tmp/nuxt-shadcn-dashboard-ref`
2. 创建 `app/` 目录并迁移现有文件
3. 安装依赖：`cd frontend && pnpm install`
4. 复制配置文件
5. 更新 `nuxt.config.ts`

**注意事项**：
- 使用激进方案，直接采用参考项目的结构
- 确保所有依赖版本与参考项目一致
- 迁移时保持现有 API 调用逻辑不变

---

### 任务 1.3：复用布局系统和组件

**状态**：⏳ 待开始

**任务描述**：
从参考项目复制布局系统和组件，直接复用参考项目的代码，减少开发工作量。

**完成标准**：
- [ ] 从参考项目复制 `app/layouts/default.vue`
- [ ] 从参考项目复制 `app/components/layout/` 目录（包含 AppSidebar、Header、SidebarNavGroup、SidebarNavLink 等）
- [ ] 从参考项目复制 `app/composables/useAppSettings.ts`
- [ ] 从参考项目复制 `app/lib/utils.ts`（cn 工具函数）
- [ ] 从参考项目复制 `app/assets/css/tailwind.css`（TailwindCSS 4 样式）
- [ ] 从参考项目复制 `app/types/nav.ts`（导航类型定义）

**操作步骤**：
1. 从 `/tmp/nuxt-shadcn-dashboard-ref/app/` 复制上述文件到 `frontend/app/`
2. 检查文件路径和导入是否正确
3. 确保所有依赖已安装

**注意事项**：
- 直接复用参考项目的代码，后续根据需求进行适配
- 检查文件中的路径引用（`@/` 别名等）

---

### 任务 1.4：安装 shadcn 组件并配置导航菜单

**状态**：⏳ 待开始

**任务描述**：
使用 `shadcn-nuxt` CLI 安装基础组件，从参考项目复制导航菜单配置并适配我们的菜单结构。

**完成标准**：
- [ ] 使用 `shadcn-nuxt` CLI 安装基础组件：
  - `npx shadcn-nuxt@latest add button`
  - `npx shadcn-nuxt@latest add card`
  - `npx shadcn-nuxt@latest add sidebar`
  - 其他需要的组件
- [ ] 从参考项目复制 `app/constants/menus.ts` 到 `app/constants/menus.ts`
- [ ] 适配导航菜单配置，添加 Playground 相关菜单项：
  - 首页（概览）
  - Playground 模块（包含 Node.js、Python、Rust 服务测试页面）
- [ ] 确保侧边栏导航正常工作（展开/折叠、路由高亮等）

**操作步骤**：
1. 运行 `shadcn-nuxt` CLI 安装组件
2. 复制并适配 `menus.ts` 文件
3. 测试侧边栏导航功能

**注意事项**：
- 导航菜单配置已包含在复用的组件中
- 只需适配菜单内容，不需要重新实现导航逻辑
- 菜单项路径要与实际页面路径一致

---

### 任务 1.5：迁移现有页面到新结构

**状态**：⏳ 待开始

**任务描述**：
将现有页面迁移到 `app/pages/playground/` 目录，更新页面使用新布局，迁移 API 调用到 `app/api/` 目录。

**完成标准**：
- [ ] 创建 `app/pages/playground/` 目录
- [ ] 迁移 `pages/node-items.vue` 到 `app/pages/playground/node-items.vue`
- [ ] 迁移 `pages/python-items.vue` 到 `app/pages/playground/python-items.vue`
- [ ] 迁移 `pages/rust-items.vue` 到 `app/pages/playground/rust-items.vue`
- [ ] 更新页面使用新布局：`definePageMeta({ layout: 'default' })`
- [ ] 更新页面内的路由链接（如果需要）
- [ ] 迁移 API 调用到 `app/api/` 目录（保持结构不变）：
  - `api/node.ts` → `app/api/node.ts`
  - `api/python.ts` → `app/api/python.ts`
  - `api/rust.ts` → `app/api/rust.ts`
- [ ] 迁移 `composables/useApi.ts` 到 `app/composables/useApi.ts`
- [ ] 确保所有页面功能正常

**操作步骤**：
1. 创建 `app/pages/playground/` 目录
2. 移动页面文件
3. 更新页面中的布局配置和路由引用
4. 移动 API 文件
5. 测试所有页面功能

**注意事项**：
- 保持现有 API 调用逻辑不变
- 页面会自动使用新布局
- 确保所有功能正常工作

---

### 任务 1.6：更新首页和测试验证

**状态**：⏳ 待开始

**任务描述**：
更新首页为管理台概览，进行全面的测试验证和代码质量检查。

**完成标准**：
- [ ] 更新 `app/pages/index.vue` 为管理台概览（可选，可后续完善）
- [ ] 测试所有页面功能正常：
  - Playground 页面可以正常访问
  - API 调用正常工作
  - 数据可以正常显示和操作
- [ ] 测试侧边栏导航功能：
  - 侧边栏可以展开/折叠
  - 路由跳转正常
  - 路由高亮显示正确
- [ ] 代码质量检查：
  - 代码编译通过：`pnpm build`
  - 无 TypeScript 错误
  - 无 ESLint 错误
  - 开发服务器可以正常启动：`pnpm dev`

**操作步骤**：
1. 更新首页（可选）
2. 运行开发服务器测试所有功能
3. 运行构建命令检查编译错误
4. 运行 lint 检查代码规范

**注意事项**：
- 这是强制检查点，必须通过才能继续
- 确保所有功能正常工作
- 可以后续再完善首页内容

---

## Phase 2：API 层重构

### 任务 2.1：设计 API 适配器接口

**状态**：⏳ 待开始

**任务描述**：
设计统一的 API 适配器接口，为后续 BFF 切换做准备。

**完成标准**：
- [ ] 创建 `app/api/types.ts` 类型定义文件
- [ ] 定义 `ApiAdapter` 接口（包含 get、post、put、delete 方法）
- [ ] 定义 `ApiClient` 类结构
- [ ] 定义统一的响应格式 `ApiResponse<T>`
- [ ] 保持与现有 `useApi.ts` 的兼容性

**注意事项**：
- 接口设计要考虑后续 BFF 切换
- 使用 TypeScript 严格类型
- 参考技术方案设计文档中的 API 客户端设计

---

### 任务 2.2：实现 DirectAdapter

**状态**：⏳ 待开始

**任务描述**：
实现直接调用后端服务的适配器，复用现有的 `useApi.ts` 逻辑。

**完成标准**：
- [ ] 创建 `app/api/adapters/direct.ts`
- [ ] 实现 `DirectAdapter` 类，实现 `ApiAdapter` 接口
- [ ] 实现所有 HTTP 方法（GET、POST、PUT、DELETE）
- [ ] 复用现有的 `useApi.ts` 逻辑
- [ ] 确保错误处理正确

**注意事项**：
- 保持与现有 API 调用方式一致
- 支持请求拦截和响应拦截（可选）

---

### 任务 2.3：预留 BffAdapter 接口

**状态**：⏳ 待开始

**任务描述**：
预留 BFF 适配器接口，不实现具体逻辑，只定义结构。

**完成标准**：
- [ ] 创建 `app/api/adapters/bff.ts`
- [ ] 定义 `BffAdapter` 类结构，实现 `ApiAdapter` 接口
- [ ] 实现接口方法（返回占位实现）
- [ ] 添加 TODO 注释说明后续实现

**注意事项**：
- 接口要与 `DirectAdapter` 保持一致
- 添加清晰的注释说明
- 不实现具体逻辑，只预留接口

---

### 任务 2.4：创建统一 API 客户端

**状态**：⏳ 待开始

**任务描述**：
创建统一的 API 客户端，支持切换适配器。

**完成标准**：
- [ ] 创建 `app/api/client.ts`
- [ ] 实现 `ApiClient` 类
- [ ] 支持切换适配器（使用依赖注入模式）
- [ ] 默认使用 `DirectAdapter`
- [ ] 提供统一的 API 调用方法

**注意事项**：
- 使用依赖注入模式
- 提供切换适配器的方法

---

### 任务 2.5：重构现有 API 调用

**状态**：⏳ 待开始

**任务描述**：
重构现有 API 调用，使用适配器模式，确保所有 API 调用正常工作。

**完成标准**：
- [ ] 更新 `app/api/node.ts` 使用 `ApiClient`
- [ ] 更新 `app/api/python.ts` 使用 `ApiClient`
- [ ] 更新 `app/api/rust.ts` 使用 `ApiClient`
- [ ] 确保所有 API 调用正常工作
- [ ] 测试所有页面的 API 调用

**注意事项**：
- 保持 API 接口不变（对外接口保持一致）
- 确保所有页面功能正常
- 测试所有 API 调用

---

## Phase 3：功能完善（可选）

### 任务 3.1：完善 Playground 页面

**状态**：⏳ 待开始（可选）

**任务描述**：
完善 Playground 页面样式和功能，优化用户体验。

**完成标准**：
- [ ] 统一 Playground 页面样式
- [ ] 添加页面标题和描述
- [ ] 优化用户体验

**注意事项**：
- 保持简洁，避免过度设计
- 可以后续再完善

---

### 任务 3.2：添加更多 UI 组件

**状态**：⏳ 待开始（可选）

**任务描述**：
根据需求添加更多 shadcn/ui 组件。

**完成标准**：
- [ ] 添加需要的 UI 组件（Table、Dialog、Form 等）
- [ ] 确保组件正常工作

**注意事项**：
- 按需添加，不要一次性添加所有组件
- 确保组件类型定义正确

---

### 任务 3.3：优化用户体验

**状态**：⏳ 待开始（可选）

**任务描述**：
优化整体用户体验，添加加载状态、错误提示等。

**完成标准**：
- [ ] 添加加载状态
- [ ] 添加错误提示
- [ ] 优化页面过渡动画
- [ ] 响应式优化

**注意事项**：
- 保持简洁，避免过度动画
- 确保性能不受影响

---

## Phase 4：文档和测试

### 任务 4.1：更新项目文档

**状态**：⏳ 待开始

**任务描述**：
更新项目文档，说明新的架构和使用方式。

**完成标准**：
- [ ] 更新 `frontend/README.md`
- [ ] 添加架构说明
- [ ] 添加使用指南
- [ ] 添加开发指南
- [ ] 说明如何添加新功能

**注意事项**：
- 文档要清晰易懂
- 包含代码示例

---

### 任务 4.2：代码质量检查

**状态**：⏳ 待开始

**任务描述**：
进行最终的代码质量检查，确保所有功能正常。

**完成标准**：
- [ ] 代码编译通过：`pnpm build`
- [ ] 无 TypeScript 错误
- [ ] 无 ESLint 错误
- [ ] 所有功能正常工作
- [ ] 开发服务器可以正常启动：`pnpm dev`

**注意事项**：
- 这是强制检查点
- 必须通过才能继续

---

## 任务依赖关系

```
Phase 1: 基础架构
1.2 → 1.3 → 1.4 → 1.5 → 1.6

Phase 2: API 层重构
2.1 → 2.2 ─┐
2.1 → 2.3 ─┼→ 2.4 → 2.5
            └─────────┘

Phase 3: 功能完善（可选）
1.6 → 3.1
1.2 → 3.2
1.6, 2.5 → 3.3

Phase 4: 文档和测试
2.5 → 4.1
2.5, 3.3 → 4.2
```

## 关键资源

- **参考项目**：https://github.com/dianprata/nuxt-shadcn-dashboard
- **参考项目在线演示**：https://nuxt-shadcn-dashboard.vercel.app
- **技术方案文档**：`docs/技术方案设计-前端改版.md`
- **技术路线文档**：`docs/技术路线-前端改版.md`
- **开发指南**：`docs/前端改版开发指南.md`

## 注意事项

1. **Keep it Simple**：优先实现核心功能，避免过度设计
2. **向后兼容**：确保现有功能在改版后仍能正常工作
3. **代码质量**：每个阶段完成后进行代码质量检查
4. **文档更新**：及时更新文档，保持与代码同步
5. **测试验证**：每个功能完成后进行测试验证
