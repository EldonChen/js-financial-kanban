/**
 * BffAdapter - BFF 适配器（预留）
 * 后续切换到 BFF 架构时使用
 */

import type { ApiAdapter } from './index'
import type { ApiResponse, RequestConfig } from '../types'
import { ApiError } from '../types'

export class BffAdapter implements ApiAdapter {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '') // 移除末尾斜杠
  }

  /**
   * 构建完整 URL
   */
  private buildUrl(url: string): string {
    // 如果 url 已经是完整 URL，直接返回
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    // 确保 url 以 / 开头
    const path = url.startsWith('/') ? url : `/${url}`
    // BFF API 路径前缀
    return `${this.baseUrl}/api/bff${path}`
  }

  /**
   * 构建请求配置
   */
  private buildRequestConfig(config?: RequestConfig): RequestInit {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config?.headers,
    }

    const requestInit: RequestInit = {
      headers,
      signal: config?.signal,
    }

    return requestInit
  }

  /**
   * 处理响应
   */
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    // 检查响应状态
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`
      let errorData: any = null

      try {
        const errorBody = await response.json()
        errorMessage = errorBody.message || errorMessage
        errorData = errorBody
      }
      catch {
        // 如果响应不是 JSON，使用默认错误信息
      }

      throw new ApiError(response.status, errorMessage, errorData)
    }

    // 解析响应
    const data = await response.json()

    // 验证响应格式（应该包含 code, message, data）
    if (typeof data === 'object' && data !== null && 'code' in data && 'message' in data) {
      return data as ApiResponse<T>
    }

    // 如果响应格式不符合预期，包装为标准格式
    return {
      code: response.status,
      message: 'success',
      data: data as T,
    }
  }

  async get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    const fullUrl = this.buildUrl(url)
    const requestConfig = this.buildRequestConfig(config)

    try {
      const response = await fetch(fullUrl, {
        method: 'GET',
        ...requestConfig,
      })

      return await this.handleResponse<T>(response)
    }
    catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      // 网络错误或其他错误
      throw new ApiError(0, error instanceof Error ? error.message : 'Network error', error)
    }
  }

  async post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    const fullUrl = this.buildUrl(url)
    const requestConfig = this.buildRequestConfig(config)

    try {
      const response = await fetch(fullUrl, {
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined,
        ...requestConfig,
      })

      return await this.handleResponse<T>(response)
    }
    catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(0, error instanceof Error ? error.message : 'Network error', error)
    }
  }

  async put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    const fullUrl = this.buildUrl(url)
    const requestConfig = this.buildRequestConfig(config)

    try {
      const response = await fetch(fullUrl, {
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined,
        ...requestConfig,
      })

      return await this.handleResponse<T>(response)
    }
    catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(0, error instanceof Error ? error.message : 'Network error', error)
    }
  }

  async delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    const fullUrl = this.buildUrl(url)
    const requestConfig = this.buildRequestConfig(config)

    try {
      const response = await fetch(fullUrl, {
        method: 'DELETE',
        ...requestConfig,
      })

      return await this.handleResponse<T>(response)
    }
    catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(0, error instanceof Error ? error.message : 'Network error', error)
    }
  }
}

/**
 * TODO: 后续实现 BFF 服务后，更新此适配器
 * - 添加认证 token 处理
 * - 添加请求日志
 * - 优化错误处理
 * - 添加请求重试机制
 */
