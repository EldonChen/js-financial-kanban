/**
 * API 适配器接口定义
 * 支持不同的数据源（直接调用后端、BFF 等）
 */

import type { ApiResponse, RequestConfig } from '../types'

/**
 * API 适配器接口
 * 所有适配器必须实现此接口
 */
export interface ApiAdapter {
  /**
   * GET 请求
   */
  get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>>

  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>

  /**
   * PUT 请求
   */
  put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>

  /**
   * DELETE 请求
   */
  delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>>
}
