/**
 * 统一 API 客户端
 * 支持依赖注入适配器，便于切换数据源（直接调用、BFF 等）
 */

import type { ApiAdapter } from './adapters'
import type { ApiResponse, RequestConfig } from './types'
import { DirectAdapter } from './adapters/direct'

/**
 * 请求拦截器类型
 */
export type RequestInterceptor = (config: RequestConfig) => RequestConfig | Promise<RequestConfig>

/**
 * 响应拦截器类型
 */
export type ResponseInterceptor = <T>(response: ApiResponse<T>) => ApiResponse<T> | Promise<ApiResponse<T>>

/**
 * 错误拦截器类型
 */
export type ErrorInterceptor = (error: Error) => Error | Promise<Error>

export class ApiClient {
  private adapter: ApiAdapter
  private requestInterceptors: RequestInterceptor[] = []
  private responseInterceptors: ResponseInterceptor[] = []
  private errorInterceptors: ErrorInterceptor[] = []

  constructor(adapter?: ApiAdapter) {
    // 如果没有提供适配器，默认使用 DirectAdapter（需要 baseUrl，这里先不初始化）
    // 实际使用时应该通过工厂函数创建
    this.adapter = adapter || ({} as ApiAdapter)
  }

  /**
   * 设置适配器
   */
  setAdapter(adapter: ApiAdapter): void {
    this.adapter = adapter
  }

  /**
   * 添加请求拦截器
   */
  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor)
  }

  /**
   * 添加响应拦截器
   */
  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor)
  }

  /**
   * 添加错误拦截器
   */
  addErrorInterceptor(interceptor: ErrorInterceptor): void {
    this.errorInterceptors.push(interceptor)
  }

  /**
   * 执行请求拦截器
   */
  private async executeRequestInterceptors(config?: RequestConfig): Promise<RequestConfig> {
    let finalConfig = config || {}
    for (const interceptor of this.requestInterceptors) {
      finalConfig = await interceptor(finalConfig)
    }
    return finalConfig
  }

  /**
   * 执行响应拦截器
   */
  private async executeResponseInterceptors<T>(response: ApiResponse<T>): Promise<ApiResponse<T>> {
    let finalResponse = response
    for (const interceptor of this.responseInterceptors) {
      finalResponse = await interceptor(finalResponse)
    }
    return finalResponse
  }

  /**
   * 执行错误拦截器
   */
  private async executeErrorInterceptors(error: Error): Promise<Error> {
    let finalError = error
    for (const interceptor of this.errorInterceptors) {
      finalError = await interceptor(finalError)
    }
    return finalError
  }

  async get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      const finalConfig = await this.executeRequestInterceptors(config)
      const response = await this.adapter.get<T>(url, finalConfig)
      return await this.executeResponseInterceptors(response)
    }
    catch (error) {
      const finalError = await this.executeErrorInterceptors(
        error instanceof Error ? error : new Error(String(error)),
      )
      throw finalError
    }
  }

  async post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      const finalConfig = await this.executeRequestInterceptors(config)
      const response = await this.adapter.post<T>(url, data, finalConfig)
      return await this.executeResponseInterceptors(response)
    }
    catch (error) {
      const finalError = await this.executeErrorInterceptors(
        error instanceof Error ? error : new Error(String(error)),
      )
      throw finalError
    }
  }

  async put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      const finalConfig = await this.executeRequestInterceptors(config)
      const response = await this.adapter.put<T>(url, data, finalConfig)
      return await this.executeResponseInterceptors(response)
    }
    catch (error) {
      const finalError = await this.executeErrorInterceptors(
        error instanceof Error ? error : new Error(String(error)),
      )
      throw finalError
    }
  }

  async delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      const finalConfig = await this.executeRequestInterceptors(config)
      const response = await this.adapter.delete<T>(url, finalConfig)
      return await this.executeResponseInterceptors(response)
    }
    catch (error) {
      const finalError = await this.executeErrorInterceptors(
        error instanceof Error ? error : new Error(String(error)),
      )
      throw finalError
    }
  }
}

/**
 * 创建 API 客户端的工厂函数
 */
export function createApiClient(baseUrl: string): ApiClient {
  const adapter = new DirectAdapter(baseUrl)
  return new ApiClient(adapter)
}
