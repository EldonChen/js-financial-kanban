/**
 * API 类型定义
 * 统一的 API 响应格式、错误类型、请求配置等
 */

/**
 * 统一 API 响应格式
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

/**
 * API 错误类型
 */
export class ApiError extends Error {
  constructor(
    public code: number,
    message: string,
    public data?: any,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * 请求配置
 */
export interface RequestConfig {
  headers?: Record<string, string>
  timeout?: number
  signal?: AbortSignal
  [key: string]: any
}

/**
 * 统一的 Item 数据模型（前端使用）
 */
export interface Item {
  id: string
  name: string
  description?: string
  price?: number
  createdAt?: string
  updatedAt?: string
}

/**
 * 创建 Item DTO
 */
export interface CreateItemDto {
  name: string
  description?: string
  price?: number
}

/**
 * 更新 Item DTO
 */
export interface UpdateItemDto {
  name?: string
  description?: string
  price?: number
}

/**
 * Node.js 服务返回的 Item（使用 _id）
 */
export interface NodeItem {
  _id: string
  name: string
  description?: string
  price?: number
  createdAt?: string
  updatedAt?: string
}

/**
 * Python/Rust 服务返回的 Item（使用 id）
 */
export interface PythonItem {
  id: string
  name: string
  description?: string
  price?: number
  created_at?: string
  updated_at?: string
}

export interface RustItem {
  id: string
  name: string
  description?: string
  price?: number
  created_at?: string
  updated_at?: string
}
