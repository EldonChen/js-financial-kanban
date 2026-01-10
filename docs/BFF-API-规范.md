# BFF API 规范

> 本文档定义了 Backend for Frontend (BFF) 架构的 API 规范，用于统一前端与后端服务的交互。

## 目录

- [概述](#概述)
- [API 路径规范](#api-路径规范)
- [请求/响应格式](#请求响应格式)
- [适配器切换](#适配器切换)
- [BFF 服务实现建议](#bff-服务实现建议)
- [迁移步骤](#迁移步骤)
- [示例代码](#示例代码)

## 概述

### 什么是 BFF？

Backend for Frontend (BFF) 是一种架构模式，为前端应用提供定制化的 API 层。BFF 层位于前端和后端服务之间，负责：

- **统一接口**：为前端提供统一的 API 接口，屏蔽后端服务的差异
- **数据聚合**：聚合多个后端服务的数据，减少前端请求次数
- **数据转换**：统一数据格式，处理不同服务的字段差异
- **业务逻辑**：处理前端特定的业务逻辑
- **性能优化**：缓存、批处理等优化策略

### 当前架构

```
前端 (Nuxt.js)
  ↓
DirectAdapter (直接调用)
  ↓
后端服务 (Node.js / Python / Rust)
```

### 目标架构

```
前端 (Nuxt.js)
  ↓
BffAdapter (通过 BFF)
  ↓
BFF 服务
  ↓
后端服务 (Node.js / Python / Rust)
```

## API 路径规范

### 路径前缀

所有 BFF API 使用统一的前缀：`/api/bff`

### 资源路径规范

BFF API 遵循 RESTful 风格，路径结构如下：

```
/api/bff/{service}/{resource}
```

- `{service}`: 服务标识（node、python、rust）
- `{resource}`: 资源名称（items、users 等）

### 完整路径示例

#### Items 资源

```
GET    /api/bff/node/items          # 获取所有 items（Node.js 服务）
GET    /api/bff/node/items/:id      # 获取单个 item
POST   /api/bff/node/items          # 创建 item
PUT    /api/bff/node/items/:id     # 更新 item
DELETE /api/bff/node/items/:id     # 删除 item

GET    /api/bff/python/items        # 获取所有 items（Python 服务）
GET    /api/bff/python/items/:id   # 获取单个 item
POST   /api/bff/python/items       # 创建 item
PUT    /api/bff/python/items/:id   # 更新 item
DELETE /api/bff/python/items/:id   # 删除 item

GET    /api/bff/rust/items         # 获取所有 items（Rust 服务）
GET    /api/bff/rust/items/:id     # 获取单个 item
POST   /api/bff/rust/items         # 创建 item
PUT    /api/bff/rust/items/:id     # 更新 item
DELETE /api/bff/rust/items/:id     # 删除 item
```

#### 批量操作（可选）

```
POST   /api/bff/node/items/batch    # 批量创建
PUT    /api/bff/node/items/batch    # 批量更新
DELETE /api/bff/node/items/batch    # 批量删除
```

#### 聚合接口（可选）

```
GET    /api/bff/items/all           # 聚合所有服务的 items
GET    /api/bff/items/stats         # 获取统计信息
```

## 请求/响应格式

### 统一响应格式

所有 BFF API 响应遵循统一的格式：

```typescript
interface ApiResponse<T> {
  code: number      // HTTP 状态码或业务状态码
  message: string   // 响应消息
  data: T          // 响应数据
}
```

### 成功响应示例

#### 获取所有 items

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Item 1",
      "description": "Description 1",
      "price": 99.99,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 获取单个 item

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "name": "Item 1",
    "description": "Description 1",
    "price": 99.99,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

#### 创建 item

```json
{
  "code": 201,
  "message": "Item created successfully",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "name": "New Item",
    "description": "New Description",
    "price": 99.99,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

### 错误响应格式

```json
{
  "code": 400,
  "message": "Validation failed",
  "data": {
    "errors": [
      {
        "field": "name",
        "message": "Name is required"
      }
    ]
  }
}
```

#### 常见错误码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `500`: 服务器错误

### 请求格式

#### 创建 Item

```http
POST /api/bff/node/items
Content-Type: application/json

{
  "name": "New Item",
  "description": "Description",
  "price": 99.99
}
```

#### 更新 Item

```http
PUT /api/bff/node/items/:id
Content-Type: application/json

{
  "name": "Updated Item",
  "description": "Updated Description",
  "price": 199.99
}
```

## 适配器切换

### 当前实现（DirectAdapter）

前端直接调用后端服务：

```typescript
// app/api/services/node.ts
export class NodeService {
  private basePath = '/api/v1/items'
  
  constructor(apiUrl: string) {
    // 使用 DirectAdapter
    this.client = createApiClient(apiUrl) // http://localhost:3000
  }
  
  async getItems(): Promise<Item[]> {
    // 请求: http://localhost:3000/api/v1/items
    const response = await this.client.get<NodeItem[]>(this.basePath)
    return response.data.map(transformNodeItem)
  }
}
```

### 切换到 BFF（BffAdapter）

前端通过 BFF 调用后端服务：

```typescript
// app/api/services/node.ts
import { ApiClient } from '../client'
import { BffAdapter } from '../adapters/bff'

export class NodeService {
  private basePath = '/node/items'  // 注意：路径已改变
  
  constructor(bffApiUrl: string) {
    // 使用 BffAdapter
    const adapter = new BffAdapter(bffApiUrl) // http://localhost:4000
    this.client = new ApiClient(adapter)
  }
  
  async getItems(): Promise<Item[]> {
    // 请求: http://localhost:4000/api/bff/node/items
    const response = await this.client.get<Item[]>(this.basePath)
    return response.data  // BFF 已统一数据格式，无需转换
  }
}
```

### 配置切换

#### 方式 1：环境变量控制

```typescript
// app/composables/useApi.ts
export function useNodeService(): NodeService {
  const config = useRuntimeConfig()
  const useBff = config.public.useBff || false
  
  if (useBff) {
    return createNodeServiceWithBff(config.public.bffApiUrl)
  } else {
    return createNodeService(config.public.nodeApiUrl)
  }
}
```

#### 方式 2：服务工厂函数

```typescript
// app/api/services/node.ts
export function createNodeService(apiUrl: string, useBff = false): NodeService {
  if (useBff) {
    const adapter = new BffAdapter(apiUrl)
    const client = new ApiClient(adapter)
    return new NodeService(client, '/node/items')
  } else {
    const client = createApiClient(apiUrl)
    return new NodeService(client, '/api/v1/items')
  }
}
```

## BFF 服务实现建议

### 技术选型

推荐使用 **Node.js + Express/Fastify** 或 **Python + FastAPI** 实现 BFF 服务。

#### Node.js + Express 示例

```typescript
// bff-service/src/routes/items.ts
import express from 'express'
import { nodeService, pythonService, rustService } from '../services'

const router = express.Router()

// GET /api/bff/node/items
router.get('/node/items', async (req, res) => {
  try {
    const items = await nodeService.getItems()
    res.json({
      code: 200,
      message: 'success',
      data: items,
    })
  } catch (error) {
    res.status(500).json({
      code: 500,
      message: error.message,
      data: null,
    })
  }
})

// POST /api/bff/node/items
router.post('/node/items', async (req, res) => {
  try {
    const item = await nodeService.createItem(req.body)
    res.status(201).json({
      code: 201,
      message: 'Item created successfully',
      data: item,
    })
  } catch (error) {
    res.status(400).json({
      code: 400,
      message: error.message,
      data: null,
    })
  }
})

export default router
```

#### Python + FastAPI 示例

```python
# bff-service/app/routers/items.py
from fastapi import APIRouter, HTTPException
from app.services import node_service, python_service, rust_service

router = APIRouter(prefix="/api/bff", tags=["items"])

@router.get("/node/items")
async def get_node_items():
    try:
        items = await node_service.get_items()
        return {
            "code": 200,
            "message": "success",
            "data": items,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/node/items")
async def create_node_item(item: CreateItemDto):
    try:
        new_item = await node_service.create_item(item)
        return {
            "code": 201,
            "message": "Item created successfully",
            "data": new_item,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 数据转换

BFF 层负责统一数据格式，处理不同服务的字段差异：

```typescript
// bff-service/src/services/node.ts
export async function getItems(): Promise<Item[]> {
  const response = await fetch('http://localhost:3000/api/v1/items')
  const data = await response.json()
  
  // 转换 Node.js 服务的数据格式（_id → id）
  return data.data.map((item: NodeItem) => ({
    id: item._id,
    name: item.name,
    description: item.description,
    price: item.price,
    createdAt: item.createdAt,
    updatedAt: item.updatedAt,
  }))
}
```

### 错误处理

BFF 层统一处理错误：

```typescript
// bff-service/src/middleware/errorHandler.ts
export function errorHandler(err: Error, req: Request, res: Response) {
  if (err instanceof ValidationError) {
    return res.status(400).json({
      code: 400,
      message: 'Validation failed',
      data: { errors: err.errors },
    })
  }
  
  if (err instanceof NotFoundError) {
    return res.status(404).json({
      code: 404,
      message: 'Resource not found',
      data: null,
    })
  }
  
  return res.status(500).json({
    code: 500,
    message: 'Internal server error',
    data: null,
  })
}
```

### 性能优化

#### 1. 数据聚合

```typescript
// GET /api/bff/items/all - 聚合所有服务的 items
router.get('/items/all', async (req, res) => {
  const [nodeItems, pythonItems, rustItems] = await Promise.all([
    nodeService.getItems(),
    pythonService.getItems(),
    rustService.getItems(),
  ])
  
  res.json({
    code: 200,
    message: 'success',
    data: {
      node: nodeItems,
      python: pythonItems,
      rust: rustItems,
      total: nodeItems.length + pythonItems.length + rustItems.length,
    },
  })
})
```

#### 2. 缓存

```typescript
import NodeCache from 'node-cache'

const cache = new NodeCache({ stdTTL: 60 }) // 缓存 60 秒

router.get('/node/items', async (req, res) => {
  const cacheKey = 'node:items'
  const cached = cache.get(cacheKey)
  
  if (cached) {
    return res.json(cached)
  }
  
  const items = await nodeService.getItems()
  const response = {
    code: 200,
    message: 'success',
    data: items,
  }
  
  cache.set(cacheKey, response)
  res.json(response)
})
```

#### 3. 批处理

```typescript
// POST /api/bff/node/items/batch
router.post('/node/items/batch', async (req, res) => {
  const items = req.body.items
  const results = await Promise.allSettled(
    items.map(item => nodeService.createItem(item))
  )
  
  const success = results.filter(r => r.status === 'fulfilled')
  const failed = results.filter(r => r.status === 'rejected')
  
  res.json({
    code: 200,
    message: `Created ${success.length} items, ${failed.length} failed`,
    data: {
      success: success.map(r => r.value),
      failed: failed.map(r => r.reason),
    },
  })
})
```

## 迁移步骤

### 步骤 1：实现 BFF 服务

1. 创建 BFF 服务项目
2. 实现基础路由和中间件
3. 实现数据转换逻辑
4. 实现错误处理
5. 添加测试

### 步骤 2：更新前端适配器

1. 更新 `BffAdapter` 实现
2. 更新服务层路径（从 `/api/v1/items` 改为 `/node/items`）
3. 移除数据转换逻辑（BFF 已统一格式）

### 步骤 3：配置切换

1. 添加环境变量 `NUXT_PUBLIC_USE_BFF=true`
2. 更新 `useApi.ts` composable 支持切换
3. 更新服务工厂函数

### 步骤 4：测试验证

1. 测试所有 CRUD 操作
2. 测试错误处理
3. 测试性能（缓存、批处理等）
4. 对比 DirectAdapter 和 BffAdapter 的行为

### 步骤 5：逐步迁移

1. 先在开发环境启用 BFF
2. 验证功能正常
3. 在测试环境启用
4. 最后在生产环境启用

## 示例代码

### 完整示例：Node.js + Express BFF 服务

```typescript
// bff-service/src/app.ts
import express from 'express'
import cors from 'cors'
import itemsRouter from './routes/items'
import { errorHandler } from './middleware/errorHandler'

const app = express()

app.use(cors())
app.use(express.json())
app.use('/api/bff', itemsRouter)
app.use(errorHandler)

app.listen(4000, () => {
  console.log('BFF service running on http://localhost:4000')
})
```

```typescript
// bff-service/src/routes/items.ts
import express from 'express'
import { nodeService } from '../services/node'

const router = express.Router()

router.get('/node/items', async (req, res, next) => {
  try {
    const items = await nodeService.getItems()
    res.json({
      code: 200,
      message: 'success',
      data: items,
    })
  } catch (error) {
    next(error)
  }
})

router.get('/node/items/:id', async (req, res, next) => {
  try {
    const item = await nodeService.getItem(req.params.id)
    if (!item) {
      return res.status(404).json({
        code: 404,
        message: 'Item not found',
        data: null,
      })
    }
    res.json({
      code: 200,
      message: 'success',
      data: item,
    })
  } catch (error) {
    next(error)
  }
})

router.post('/node/items', async (req, res, next) => {
  try {
    const item = await nodeService.createItem(req.body)
    res.status(201).json({
      code: 201,
      message: 'Item created successfully',
      data: item,
    })
  } catch (error) {
    next(error)
  }
})

router.put('/node/items/:id', async (req, res, next) => {
  try {
    const item = await nodeService.updateItem(req.params.id, req.body)
    res.json({
      code: 200,
      message: 'Item updated successfully',
      data: item,
    })
  } catch (error) {
    next(error)
  }
})

router.delete('/node/items/:id', async (req, res, next) => {
  try {
    await nodeService.deleteItem(req.params.id)
    res.json({
      code: 200,
      message: 'Item deleted successfully',
      data: null,
    })
  } catch (error) {
    next(error)
  }
})

export default router
```

```typescript
// bff-service/src/services/node.ts
interface NodeItem {
  _id: string
  name: string
  description?: string
  price?: number
  createdAt?: string
  updatedAt?: string
}

interface Item {
  id: string
  name: string
  description?: string
  price?: number
  createdAt?: string
  updatedAt?: string
}

function transformNodeItem(item: NodeItem): Item {
  return {
    id: item._id,
    name: item.name,
    description: item.description,
    price: item.price,
    createdAt: item.createdAt,
    updatedAt: item.updatedAt,
  }
}

export const nodeService = {
  async getItems(): Promise<Item[]> {
    const response = await fetch('http://localhost:3000/api/v1/items')
    const data = await response.json()
    return data.data.map(transformNodeItem)
  },
  
  async getItem(id: string): Promise<Item | null> {
    const response = await fetch(`http://localhost:3000/api/v1/items/${id}`)
    if (!response.ok) {
      return null
    }
    const data = await response.json()
    return transformNodeItem(data.data)
  },
  
  async createItem(dto: CreateItemDto): Promise<Item> {
    const response = await fetch('http://localhost:3000/api/v1/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dto),
    })
    const data = await response.json()
    return transformNodeItem(data.data)
  },
  
  async updateItem(id: string, dto: UpdateItemDto): Promise<Item> {
    const response = await fetch(`http://localhost:3000/api/v1/items/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dto),
    })
    const data = await response.json()
    return transformNodeItem(data.data)
  },
  
  async deleteItem(id: string): Promise<void> {
    await fetch(`http://localhost:3000/api/v1/items/${id}`, {
      method: 'DELETE',
    })
  },
}
```

### 前端切换示例

```typescript
// app/api/services/node.ts
import { ApiClient } from '../client'
import { DirectAdapter } from '../adapters/direct'
import { BffAdapter } from '../adapters/bff'

export function createNodeService(apiUrl: string, useBff = false): NodeService {
  let client: ApiClient
  
  if (useBff) {
    // 使用 BFF 适配器
    const adapter = new BffAdapter(apiUrl)
    client = new ApiClient(adapter)
    return new NodeService(client, '/node/items') // BFF 路径
  } else {
    // 使用直接适配器
    client = createApiClient(apiUrl)
    return new NodeService(client, '/api/v1/items') // 直接路径
  }
}

// app/composables/useApi.ts
export function useNodeService(): NodeService {
  const config = useRuntimeConfig()
  const useBff = config.public.useBff || false
  
  if (useBff) {
    return createNodeService(config.public.bffApiUrl, true)
  } else {
    return createNodeService(config.public.nodeApiUrl, false)
  }
}
```

## 注意事项

1. **向后兼容**：确保 BFF API 与现有 DirectAdapter 行为一致
2. **错误处理**：统一错误格式，便于前端处理
3. **性能考虑**：BFF 层可能成为瓶颈，需要合理使用缓存和批处理
4. **安全性**：BFF 层需要处理认证、授权、输入验证等
5. **监控**：添加日志和监控，便于排查问题

## 总结

BFF 架构为前端提供了统一的 API 接口，简化了前端代码，提高了可维护性。通过适配器模式，可以平滑地从直接调用后端切换到 BFF 架构，无需修改业务代码。

---

**文档版本**：v1.0  
**创建时间**：2024年  
**适用项目**：js-financial-kanban
