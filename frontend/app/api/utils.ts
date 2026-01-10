/**
 * API 工具函数
 */

import type { ApiError } from './types'

/**
 * 判断是否为 API 错误
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

/**
 * 判断是否为网络错误
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code === 0
  }
  if (error instanceof Error) {
    return error.message.includes('fetch') || error.message.includes('network')
  }
  return false
}

/**
 * 判断是否为业务错误（4xx）
 */
export function isClientError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code >= 400 && error.code < 500
  }
  return false
}

/**
 * 判断是否为服务器错误（5xx）
 */
export function isServerError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.code >= 500 && error.code < 600
  }
  return false
}

/**
 * 获取错误状态码
 */
export function getErrorCode(error: unknown): number | null {
  if (error instanceof ApiError) {
    return error.code
  }
  return null
}

/**
 * 格式化错误消息
 */
export function formatErrorMessage(error: unknown, defaultMessage = '操作失败'): string {
  if (error instanceof ApiError) {
    return error.message || defaultMessage
  }
  if (error instanceof Error) {
    return error.message || defaultMessage
  }
  return defaultMessage
}
