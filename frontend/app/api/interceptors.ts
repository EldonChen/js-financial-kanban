/**
 * API 拦截器示例
 * 提供常用的请求/响应拦截器
 */

import type { ErrorInterceptor, RequestInterceptor, ResponseInterceptor } from './client'
import type { ApiResponse, RequestConfig } from './types'

/**
 * 日志拦截器 - 记录请求和响应
 */
export function createLogInterceptor(enabled = true): {
  request: RequestInterceptor
  response: ResponseInterceptor
} {
  return {
    request: (config: RequestConfig) => {
      if (enabled && import.meta.dev) {
        console.log('[API Request]', {
          url: config.url || 'unknown',
          method: config.method || 'GET',
          headers: config.headers,
          timestamp: new Date().toISOString(),
        })
      }
      return config
    },
    response: <T>(response: ApiResponse<T>) => {
      if (enabled && import.meta.dev) {
        console.log('[API Response]', {
          code: response.code,
          message: response.message,
          data: response.data,
          timestamp: new Date().toISOString(),
        })
      }
      return response
    },
  }
}

/**
 * 认证拦截器 - 添加认证 token（预留）
 */
export function createAuthInterceptor(getToken: () => string | null): RequestInterceptor {
  return (config: RequestConfig) => {
    const token = getToken()
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      }
    }
    return config
  }
}

/**
 * 错误重试拦截器 - 自动重试失败的请求（预留）
 */
export function createRetryInterceptor(maxRetries = 3, delay = 1000): ErrorInterceptor {
  return async (error: Error) => {
    // TODO: 实现重试逻辑
    // 这里只是示例，实际实现需要更复杂的逻辑
    return error
  }
}

/**
 * 请求时间统计拦截器
 */
export function createTimingInterceptor(): {
  request: RequestInterceptor
  response: ResponseInterceptor
} {
  const timings = new Map<string, number>()

  return {
    request: (config: RequestConfig) => {
      const requestId = `${Date.now()}-${Math.random()}`
      timings.set(requestId, Date.now())
      // 将 requestId 存储到 config 中，供响应拦截器使用
      ;(config as any).__requestId = requestId
      return config
    },
    response: <T>(response: ApiResponse<T>) => {
      const requestId = (response as any).__requestId
      if (requestId) {
        const startTime = timings.get(requestId)
        if (startTime) {
          const duration = Date.now() - startTime
          if (import.meta.dev) {
            console.log(`[API Timing] Request took ${duration}ms`)
          }
          timings.delete(requestId)
        }
      }
      return response
    },
  }
}
