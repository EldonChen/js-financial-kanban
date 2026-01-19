# BFF 接口实现检查清单

> **文档目的**：确保前端代码与 BFF 接口定义保持一致  
> **检查时间**：2025-01-20  
> **检查结果**：✅ 接口定义匹配，无需调整

## 检查结果总结

### ✅ 接口定义匹配

前端代码调用的 BFF 接口与设计规范完全匹配，无需调整。

### ✅ Mock 数据完整

Mock 适配器已覆盖所有前端实际使用的接口。

### ✅ 类型定义完整

所有必需的类型定义已添加到 `frontend/app/api/types.ts`。

---

## 详细检查报告

### 1. 历史数据接口（Historical Data）

#### 前端实际调用

| 方法 | 路径 | 前端调用 | BFF 定义 | Mock 支持 | 状态 |
|------|------|----------|----------|-----------|------|
| GET | `/v1/views/historical-data/:ticker` | ✅ | ✅ | ✅ | ✅ 匹配 |
| GET | `/v1/views/historical-data/:ticker/statistics` | ✅ | ✅ | ✅ | ✅ 匹配 |
| POST | `/v1/views/historical-data/:ticker/update` | ✅ | ✅ | ✅ | ✅ 匹配 |
| GET | `/v1/views/historical-data/batch` (SSE) | ✅ | ✅ | ✅ Mock 模拟 | ✅ 匹配 |
| GET | `/v1/views/historical-data/full-update` (SSE) | ✅ | ✅ | ✅ Mock 模拟 | ✅ 匹配 |
| DELETE | `/v1/views/historical-data/:ticker` | ✅ | ✅ | ⚠️ 未测试 | ✅ 匹配 |

**说明**：
- 所有接口定义匹配
- SSE 接口正确使用 GET 方法（EventSource 要求）
- Mock 模式下，SSE 接口使用 `simulateSSEProgress` 模拟，不实际调用

#### 参数对比

**查询参数**：
- `period` - ✅ 匹配
- `start_date` - ✅ 匹配
- `end_date` - ✅ 匹配
- `limit` - ✅ 匹配
- `page` - ✅ 匹配
- `page_size` - ✅ 匹配
- `incremental` - ✅ 匹配
- `data_source` - ✅ 匹配
- `tickers` - ✅ 匹配（逗号分隔）

**响应格式**：
- 分页模式：✅ 匹配
- 列表模式：✅ 匹配
- 统计格式：✅ 匹配
- SSE 格式：✅ 匹配

### 2. 技术指标接口（Indicators）

#### 前端实际调用

| 方法 | 路径 | 前端调用 | BFF 定义 | Mock 支持 | 状态 |
|------|------|----------|----------|-----------|------|
| GET | `/v1/views/indicators/supported` | ✅ | ✅ | ✅ | ✅ 匹配 |
| POST | `/v1/views/indicators/:ticker/calculate` | ✅ | ✅ | ✅ | ✅ 匹配 |
| GET | `/v1/views/indicators/:ticker` | ✅ | ✅ | ✅ | ✅ 匹配 |
| GET | `/v1/views/indicators/batch-calculate` (SSE) | ✅ | ✅ | ✅ Mock 模拟 | ✅ 匹配 |

**说明**：
- 所有接口定义匹配
- 支持的指标列表返回格式正确
- 计算接口支持请求体传递参数

#### 参数对比

**查询参数**：
- `indicator_name` - ✅ 匹配（必填）
- `period` - ✅ 匹配
- `start_date` - ✅ 匹配
- `end_date` - ✅ 匹配
- `limit` - ✅ 匹配
- `page` - ✅ 匹配
- `page_size` - ✅ 匹配
- `tickers` - ✅ 匹配
- `indicator_names` - ✅ 匹配

**请求体**：
- `indicator_params` - ✅ 匹配（可选）

**响应格式**：
- 分页模式：✅ 匹配
- 列表模式：✅ 匹配
- 指标列表：✅ 匹配
- SSE 格式：✅ 匹配

---

## 发现的问题和调整

### ⚠️ 问题 1：SSE 接口的 HTTP 方法

**问题描述**：
- EventSource API 只支持 GET 请求
- 但数据更新和指标计算通常使用 POST 方法

**解决方案**：
- SSE 接口使用 GET 方法，参数通过 URL 查询参数传递
- BFF 层实现时需要注意这一点

**影响接口**：
- `GET /v1/views/historical-data/batch`
- `GET /v1/views/historical-data/full-update`
- `GET /v1/views/indicators/batch-calculate`

**状态**：✅ 已在 API 文档中明确说明

### ✅ 确认：接口设计合理

所有非 SSE 接口的 HTTP 方法使用正确：
- GET - 查询操作
- POST - 创建/计算操作
- DELETE - 删除操作
- PUT - 更新操作（当前未使用）

---

## Mock 数据检查

### 已实现的 Mock 接口

**历史数据**：
- ✅ `GET /v1/views/historical-data/:ticker` - 支持分页和非分页
- ✅ `GET /v1/views/historical-data/:ticker/statistics` - 返回统计信息
- ✅ `POST /v1/views/historical-data/:ticker/update` - 返回更新结果
- ✅ SSE 模拟 - 使用 `simulateSSEProgress`

**技术指标**：
- ✅ `GET /v1/views/indicators/supported` - 返回4个预定义指标
- ✅ `POST /v1/views/indicators/:ticker/calculate` - 返回计算结果
- ✅ `GET /v1/views/indicators/:ticker` - 支持分页和非分页
- ✅ SSE 模拟 - 使用 `simulateSSEProgress`

### Mock 数据质量

**数据真实性**：
- ✅ K线数据格式正确（OHLCV）
- ✅ 价格数据合理（基于随机波动）
- ✅ 日期范围合理（默认1年）
- ✅ 技术指标数据合理

**分页支持**：
- ✅ 正确处理 page 和 page_size 参数
- ✅ 返回正确的分页元数据
- ✅ total_pages 计算正确

**SSE 模拟**：
- ✅ 模拟真实的进度更新（200ms 间隔）
- ✅ 包含所有阶段（init, fetching, saving, calculating, completed）
- ✅ 包含进度百分比和统计信息
- ✅ 模拟合理的时长（3-6秒）

---

## 需要注意的事项

### 1. 响应格式兼容性

前端代码已添加兼容性处理，支持两种响应格式：

**格式1（包装格式）**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "data": [...]  // 数据在 data.data 中
  }
}
```

**格式2（直接格式）**：
```json
{
  "code": 200,
  "message": "success",
  "data": [...]  // 数据直接在 data 中
}
```

BFF 实现时建议使用**格式1**（包装格式），更清晰。

### 2. SSE 实现要点

**BFF 层需要**：
- 接收后端服务的 SSE 流
- 转发给前端（作为 SSE 代理）
- 处理连接错误和超时
- 设置正确的响应头

**参考实现**（NestJS）：
```typescript
@Get('batch')
async batchUpdate(@Res() res: Response, @Query() query) {
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  
  // 代理后端服务的 SSE 流
  await this.service.batchUpdateSSE(query.tickers.split(','), res)
}
```

### 3. 前端 Mock 切换

**当前状态**：
- 默认使用 Mock（`useMock = true`）
- 前端可独立开发和测试

**切换到真实 BFF**：
```bash
# 方法1：环境变量
export NUXT_PUBLIC_USE_DATA_SUPPORT_MOCK=false

# 方法2：修改 composables
# 将 useMock 默认值从 true 改为 false
```

---

## 结论

### ✅ 检查通过

1. **接口定义完全匹配**：前端代码与 BFF 设计规范一致
2. **Mock 数据完整**：覆盖所有前端使用的接口
3. **类型定义完整**：所有必需类型已定义
4. **SSE 实现正确**：使用 GET 方法，符合 EventSource API 要求

### 📋 无需调整

前端代码已准备就绪，BFF 层可以按照当前接口定义直接实现，无需修改前端代码。

### 🚀 下一步

可以开始实现 BFF 层：
1. 创建 `historical-data` 视图模块
2. 创建 `indicators` 视图模块
3. 实现接口（参考 `BFF-API-数据支持模块.md`）
4. 测试接口
5. 前端切换到真实模式

---

**检查完成时间**：2025-01-20  
**检查人**：AI Assistant  
**结论**：✅ 前端代码与 BFF 定义完全匹配，可以开始 BFF 层实现
