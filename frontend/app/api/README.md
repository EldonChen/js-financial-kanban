# API 层使用指南

## 概述

本项目使用适配器模式的 API 架构，支持当前直接调用后端服务，后续可平滑过渡到 BFF 架构。

## 目录结构

```
app/api/
├── types.ts              # 类型定义
├── client.ts             # 统一 API 客户端
├── utils.ts              # 工具函数
├── interceptors.ts       # 拦截器示例
├── adapters/
│   ├── index.ts          # 适配器接口
│   ├── direct.ts         # 直接调用后端适配器
│   └── bff.ts            # BFF 适配器（预留）
└── services/
    ├── node.ts           # Node.js 服务 API
    ├── python.ts         # Python 服务 API
    └── rust.ts           # Rust 服务 API
```

## 基本使用

### 1. 使用 Composables（推荐）

```typescript
import { useNodeService } from '~/composables/useApi'

const nodeService = useNodeService()

// 获取所有 items
const items = await nodeService.getItems()

// 创建 item
const newItem = await nodeService.createItem({
  name: 'New Item',
  description: 'Description',
  price: 99.99,
})

// 更新 item
await nodeService.updateItem(itemId, {
  name: 'Updated Name',
})

// 删除 item
await nodeService.deleteItem(itemId)
```

### 2. 直接使用服务类

```typescript
import { createNodeService } from '~/api/services/node'

const nodeService = createNodeService('http://localhost:3000')
const items = await nodeService.getItems()
```

## 错误处理

### 使用错误处理 Composable

```typescript
import { handleApiError } from '~/composables/useApiError'

try {
  await nodeService.getItems()
}
catch (error) {
  handleApiError(error, { defaultMessage: '无法加载数据' })
}
```

### 错误类型判断

```typescript
import { isNetworkError, isClientError, isServerError } from '~/api/utils'

if (isNetworkError(error)) {
  // 处理网络错误
}
else if (isClientError(error)) {
  // 处理客户端错误（4xx）
}
else if (isServerError(error)) {
  // 处理服务器错误（5xx）
}
```

## 拦截器使用

### 添加日志拦截器

```typescript
import { createApiClient } from '~/api/client'
import { createLogInterceptor } from '~/api/interceptors'

const client = createApiClient('http://localhost:3000')
const logInterceptor = createLogInterceptor(true)

client.addRequestInterceptor(logInterceptor.request)
client.addResponseInterceptor(logInterceptor.response)
```

### 添加认证拦截器

```typescript
import { createAuthInterceptor } from '~/api/interceptors'

const authInterceptor = createAuthInterceptor(() => {
  // 从 localStorage 或其他地方获取 token
  return localStorage.getItem('token')
})

client.addRequestInterceptor(authInterceptor)
```

### 添加请求时间统计拦截器

```typescript
import { createTimingInterceptor } from '~/api/interceptors'

const timingInterceptor = createTimingInterceptor()

client.addRequestInterceptor(timingInterceptor.request)
client.addResponseInterceptor(timingInterceptor.response)
```

## 自定义拦截器

### 请求拦截器

```typescript
const requestInterceptor: RequestInterceptor = (config) => {
  // 修改请求配置
  config.headers = {
    ...config.headers,
    'X-Custom-Header': 'value',
  }
  return config
}

client.addRequestInterceptor(requestInterceptor)
```

### 响应拦截器

```typescript
const responseInterceptor: ResponseInterceptor = (response) => {
  // 处理响应数据
  if (response.code === 200) {
    // 成功处理
  }
  return response
}

client.addResponseInterceptor(responseInterceptor)
```

### 错误拦截器

```typescript
const errorInterceptor: ErrorInterceptor = (error) => {
  // 处理错误
  console.error('API Error:', error)
  return error
}

client.addErrorInterceptor(errorInterceptor)
```

## 适配器切换

### 当前使用 DirectAdapter

```typescript
// 在 services/node.ts 中
const client = createApiClient(apiUrl) // 默认使用 DirectAdapter
```

### 切换到 BFF（后续）

```typescript
import { ApiClient } from '~/api/client'
import { BffAdapter } from '~/api/adapters/bff'

const adapter = new BffAdapter('http://localhost:4000')
const client = new ApiClient(adapter)
```

## 类型定义

### ApiResponse

```typescript
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}
```

### Item

```typescript
interface Item {
  id: string
  name: string
  description?: string
  price?: number
  createdAt?: string
  updatedAt?: string
}
```

## 注意事项

1. **环境变量配置**：确保在 `.env` 文件中配置了正确的 API 地址
2. **错误处理**：始终使用 `handleApiError` 处理错误
3. **类型安全**：使用 TypeScript 类型定义确保类型安全
4. **拦截器顺序**：拦截器按照添加顺序执行

## 后续扩展

- [ ] 添加请求缓存
- [ ] 添加请求重试机制
- [ ] 添加请求去重
- [ ] 添加请求队列
- [ ] 添加离线支持
