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

/**
 * Stock 数据模型
 */
export interface Stock {
  ticker: string
  name?: string
  sector?: string
  industry?: string
  market?: string // 市场（NASDAQ, NYSE, SSE, SZSE 等）
  market_type?: string // 市场类型（A股、港股、美股）
  country?: string // 国家
  exchange?: string // 交易所代码
  currency?: string // 货币
  market_cap?: number
  price?: number
  volume?: number
  data_source?: string // 数据来源（yfinance、akshare、easyquotation 等）
  created_at?: string
  last_updated?: string
}
