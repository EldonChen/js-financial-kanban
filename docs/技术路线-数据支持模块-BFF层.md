# 技术路线 - 数据支持模块（BFF层）

> **任务状态**：待开始  
> **创建时间**：2025-01-12  
> **最后更新**：2025-01-20  
> **文档位置**：docs/  
> **说明**：本文档仅用于当前任务，任务完成后可归档或删除  
> **优先级**：P0 - 最高优先级

## 任务概述

实现数据支持模块的 BFF（Backend For Frontend）层，为前端提供定制化、高聚合度的接口。

**实施范围调整**（2025-01-20）：
- 📋 **当前实施**：历史数据视图、技术指标视图
- ⏸️ **暂缓实施**：数据质量视图、数据同步视图

## 任务拆解

### 阶段 1：HTTP 客户端实现（基础依赖）

#### 任务 1.1：实现历史数据服务 HTTP 客户端
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级，必须先完成）
- **描述**：创建历史数据服务的 HTTP 客户端，用于调用后台服务
- **内容**：
  - 创建 `bff/bff-main/src/clients/historical-data.client.ts`
  - 实现 `getKlineData` 方法（获取历史K线数据）
  - 实现 `updateKlineData` 方法（更新历史K线数据）
  - 实现 `getKlineDataStatistics` 方法（获取统计数据）
  - 实现错误处理和超时配置
  - 实现请求重试机制
- **验收标准**：
  - [ ] HTTP 客户端可以正常调用后台服务
  - [ ] 错误处理完善
  - [ ] 超时和重试机制正常工作
- **输出**：`bff/bff-main/src/clients/historical-data.client.ts`

#### 任务 1.2：实现技术指标服务 HTTP 客户端
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级）
- **描述**：创建技术指标服务的 HTTP 客户端
- **内容**：
  - 创建 `bff/bff-main/src/clients/indicators.client.ts`
  - 实现 `calculateIndicator` 方法（计算技术指标）
  - 实现 `queryIndicatorData` 方法（查询技术指标数据）
  - 实现 `getSupportedIndicators` 方法（获取支持的指标列表）
  - 实现错误处理和超时配置
- **验收标准**：
  - [ ] HTTP 客户端可以正常调用后台服务
  - [ ] 错误处理完善
- **输出**：`bff/bff-main/src/clients/indicators.client.ts`

#### 任务 1.3：实现数据质量和同步服务 HTTP 客户端 ⏸️ 暂缓
- **状态**：暂缓
- **优先级**：⭐⭐⭐（后续）
- **描述**：创建数据质量和同步服务的 HTTP 客户端
- **说明**：数据质量检查和数据同步功能暂缓实施，优先完成核心的历史数据和技术指标功能。

### 阶段 2：历史数据视图实现（核心功能）

#### 任务 2.1：实现历史数据视图服务
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级）
- **描述**：创建历史数据视图服务，聚合后台服务数据
- **内容**：
  - 创建 `bff/bff-main/src/views/historical-data/historical-data.service.ts`
  - 实现 `getKlineData` 方法（获取历史K线数据）
  - 实现 `updateKlineData` 方法（更新历史K线数据）
  - 实现 `getKlineDataStatistics` 方法（获取统计数据）
  - 实现数据格式转换（统一响应格式）
  - 实现错误处理（允许部分失败，返回空数据）
- **验收标准**：
  - [ ] 服务可以正常调用 HTTP 客户端
  - [ ] 数据格式转换正确
  - [ ] 错误处理完善
- **依赖**：任务 1.1
- **输出**：`bff/bff-main/src/views/historical-data/historical-data.service.ts`

#### 任务 2.2：实现历史数据视图控制器
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级）
- **描述**：创建历史数据视图控制器，提供 RESTful API
- **内容**：
  - 创建 `bff/bff-main/src/views/historical-data/historical-data.controller.ts`
  - 实现 `GET /api/bff/v1/views/historical-data/:ticker` 接口（支持分页）
  - 实现 `GET /api/bff/v1/views/historical-data/:ticker/statistics` 接口
  - 实现 `POST /api/bff/v1/views/historical-data/:ticker/update` 接口
  - 实现 `GET /api/bff/v1/views/historical-data/batch` 接口（SSE，⚠️ 使用 GET）
  - 实现 `GET /api/bff/v1/views/historical-data/full-update` 接口（SSE，⚠️ 使用 GET）
  - 实现 `DELETE /api/bff/v1/views/historical-data/:ticker` 接口
  - 实现请求参数验证
  - 实现错误处理和统一响应格式
  - 实现分页逻辑（根据是否有 page/page_size 参数判断）
- **验收标准**：
  - [ ] 所有 API 接口正常工作
  - [ ] 分页和非分页模式都正常
  - [ ] 请求参数验证正确
  - [ ] 错误处理完善
  - [ ] SSE 代理正常工作
- **依赖**：任务 2.1
- **输出**：`bff/bff-main/src/views/historical-data/historical-data.controller.ts`

#### 任务 2.3：实现历史数据视图模块注册
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级）
- **描述**：创建历史数据视图模块，注册到主应用
- **内容**：
  - 创建 `bff/bff-main/src/views/historical-data/historical-data.module.ts`
  - 配置模块依赖（HttpModule）
  - 注册 Controller 和 Service
  - 在 `views.module.ts` 中注册新模块
- **验收标准**：
  - [ ] 模块可以正常启动
  - [ ] 路由可以正常访问
- **依赖**：任务 2.2
- **输出**：
  - `bff/bff-main/src/views/historical-data/historical-data.module.ts`
  - 更新后的 `bff/bff-main/src/views/views.module.ts`

### 阶段 3：技术指标视图实现（核心功能）

#### 任务 3.1：实现技术指标视图服务
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级）
- **描述**：创建技术指标视图服务，聚合后台服务数据
- **内容**：
  - 创建 `bff/bff-main/src/views/indicators/indicators.service.ts`
  - 实现 `calculateIndicator` 方法（计算技术指标）
  - 实现 `queryIndicatorData` 方法（查询技术指标数据）
  - 实现 `getSupportedIndicators` 方法（获取支持的指标列表）
  - 实现数据格式转换
  - 实现错误处理
- **验收标准**：
  - [ ] 服务可以正常调用 HTTP 客户端
  - [ ] 数据格式转换正确
  - [ ] 错误处理完善
- **依赖**：任务 1.2
- **输出**：`bff/bff-main/src/views/indicators/indicators.service.ts`

#### 任务 3.2：实现技术指标视图控制器和模块
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐⭐（最高优先级）
- **描述**：创建技术指标视图控制器和模块
- **内容**：
  - 创建 `bff/bff-main/src/views/indicators/indicators.controller.ts`
  - 实现 `GET /api/bff/v1/views/indicators/supported` 接口
  - 实现 `POST /api/bff/v1/views/indicators/:ticker/calculate` 接口
  - 实现 `GET /api/bff/v1/views/indicators/:ticker` 接口（支持分页）
  - 实现 `GET /api/bff/v1/views/indicators/batch-calculate` 接口（SSE，⚠️ 使用 GET）
  - 创建 `indicators.module.ts` 并注册模块
  - 实现分页逻辑
- **验收标准**：
  - [ ] 所有 API 接口正常工作
  - [ ] 分页和非分页模式都正常
  - [ ] 请求参数验证正确
  - [ ] SSE 代理正常工作
  - [ ] 模块可以正常启动
- **依赖**：任务 3.1
- **输出**：
  - `bff/bff-main/src/views/indicators/indicators.controller.ts`
  - `bff/bff-main/src/views/indicators/indicators.module.ts`
  - 更新后的 `views.module.ts`

### 阶段 4：数据质量和同步视图实现 ⏸️ 暂缓

> **说明**：数据质量和同步功能暂缓实施，不在当前实现范围内。

### 阶段 5：SSE 代理实现（重要功能）

#### 任务 5.1：实现 SSE 代理功能
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐（重要）
- **描述**：实现 SSE 代理功能，将后台服务的 SSE 流转发给前端
- **内容**：
  - 在 `HistoricalDataService` 中实现 `batchUpdateKlineDataSSE` 方法
  - 在 `IndicatorsService` 中实现 `batchCalculateIndicatorsSSE` 方法
  - 在 `DataSyncService` 中实现 `syncDataSSE` 方法
  - 使用 axios 接收后台服务的 SSE 流
  - 将流转发给前端（使用 Response 对象）
  - 实现错误处理和超时处理
- **验收标准**：
  - [ ] SSE 代理正常工作
  - [ ] 可以正确转发后台服务的 SSE 流
  - [ ] 错误处理和超时处理完善
- **依赖**：任务 2.2, 3.2, 4.2
- **输出**：更新后的服务文件

### 阶段 6：测试和验证（质量保证）

#### 任务 6.1：编写单元测试
- **状态**：待开始
- **优先级**：⭐⭐⭐⭐（重要）
- **描述**：为所有视图服务编写单元测试
- **内容**：
  - 为历史数据视图服务编写测试
  - 为技术指标视图服务编写测试
  - 为数据质量视图服务编写测试
  - 为数据同步视图服务编写测试
  - 测试覆盖率 > 80%
- **验收标准**：
  - [ ] 所有单元测试通过
  - [ ] 测试覆盖率 > 80%
  - [ ] 测试覆盖正常流程和异常流程
- **依赖**：任务 2.3, 3.2, 4.1, 4.2
- **输出**：测试文件

#### 任务 6.2：集成测试和验证
- **状态**：待开始
- **优先级**：⭐⭐⭐（可选）
- **描述**：进行端到端集成测试
- **内容**：
  - 测试所有 API 接口
  - 测试 SSE 代理功能
  - 测试错误处理
  - 验证响应格式统一
- **验收标准**：
  - [ ] 所有集成测试通过
  - [ ] 端到端流程正常工作
- **依赖**：任务 6.1
- **输出**：集成测试报告

## 任务依赖关系图

```
阶段 1：HTTP 客户端实现
├── 任务 1.1：历史数据服务 HTTP 客户端
├── 任务 1.2：技术指标服务 HTTP 客户端
└── 任务 1.3：数据质量和同步服务 HTTP 客户端

阶段 2：历史数据视图实现
├── 任务 2.1：历史数据视图服务（依赖 1.1）
├── 任务 2.2：历史数据视图控制器（依赖 2.1）
└── 任务 2.3：历史数据视图模块注册（依赖 2.2）

阶段 3：技术指标视图实现
├── 任务 3.1：技术指标视图服务（依赖 1.2）
└── 任务 3.2：技术指标视图控制器和模块（依赖 3.1）

阶段 4：数据质量和同步视图实现 ⏸️ 暂缓

阶段 5：SSE 代理实现
└── 任务 5.1：SSE 代理功能（依赖 2.2, 3.2）

阶段 6：测试和验证
├── 任务 6.1：编写单元测试（依赖 2.3, 3.2）
└── 任务 6.2：集成测试和验证（依赖 6.1）
```

## 注意事项

1. **向后兼容**：
   - 所有新功能不影响现有视图模块
   - 使用独立的路由前缀（`/api/bff/v1/views/historical-data/*`, `/api/bff/v1/views/indicators/*`）
   - 使用独立的模块，不影响现有模块

2. **代码规范**：
   - 遵循现有代码风格（与 `stocks` 视图保持一致）
   - 使用 TypeScript 类型定义
   - 模块和函数命名清晰

3. **错误处理**：
   - 统一错误响应格式（与现有格式保持一致）
   - 允许部分服务失败（返回空数据）
   - 记录详细错误日志

4. **SSE 代理**：
   - 正确设置 SSE 响应头
   - 及时关闭流，避免资源浪费
   - 处理错误和超时

5. **性能优化**：
   - 使用连接池管理 HTTP 连接
   - 设置合理的超时时间
   - 实现请求重试机制

## 检查清单

### 代码质量检查
- [ ] 所有代码通过 lint 检查
- [ ] 所有代码通过类型检查
- [ ] 所有单元测试通过
- [ ] 测试覆盖率 > 80%

### 功能完整性检查
- [ ] 历史数据视图功能完整（6个接口）
- [ ] 技术指标视图功能完整（4个接口）
- [ ] 所有 API 接口正常工作
- [ ] SSE 代理功能正常（3个 SSE 接口）
- [ ] 分页和非分页模式都正常
- ⏸️ 数据质量视图功能（暂缓）
- ⏸️ 数据同步视图功能（暂缓）

### 兼容性检查
- [ ] 不影响现有视图模块
- [ ] 向后兼容性保证
- [ ] 响应格式统一

---

**技术路线规划已完成**

**参考文档**：
- `docs/技术方案设计-数据支持模块-BFF层实现.md`（技术方案设计）
- `docs/技术方案设计-数据支持模块-后台服务.md`（后台服务 API 设计）
- `docs/数据支持模块-前端实现总结.md`（前端实现总结）
- `docs/BFF-接口实现检查清单.md`（接口检查报告）

**前端代码参考**：
- `frontend/app/api/services/historical-data.ts` - 前端服务实现（接口调用示例）
- `frontend/app/api/services/indicators.ts` - 前端服务实现
- `frontend/app/api/adapters/mock-bff.ts` - Mock BFF 实现（可作为参考）
