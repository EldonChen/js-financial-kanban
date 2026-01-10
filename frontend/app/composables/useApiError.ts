/**
 * API 错误处理 Composable
 * 提供统一的错误处理逻辑
 */

import { ApiError } from '~/api/types'
import { toast } from 'vue-sonner'

/**
 * 判断错误类型
 */
export function getErrorType(error: unknown): 'network' | 'api' | 'unknown' {
  if (error instanceof ApiError) {
    return 'api'
  }
  if (error instanceof Error && (error.message.includes('fetch') || error.message.includes('network'))) {
    return 'network'
  }
  return 'unknown'
}

/**
 * 获取错误消息
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message || '请求失败'
  }
  if (error instanceof Error) {
    return error.message
  }
  return '未知错误'
}

/**
 * 获取错误详情
 */
export function getErrorDetails(error: unknown): any {
  if (error instanceof ApiError) {
    return error.data
  }
  return null
}

/**
 * 处理 API 错误
 */
export function handleApiError(error: unknown, options?: {
  showToast?: boolean
  defaultMessage?: string
}): {
  type: 'network' | 'api' | 'unknown'
  message: string
  details: any
} {
  const { showToast = true, defaultMessage } = options || {}
  const type = getErrorType(error)
  const message = getErrorMessage(error) || defaultMessage || '操作失败'
  const details = getErrorDetails(error)

  if (showToast) {
    // 根据错误类型显示不同的提示
    if (type === 'network') {
      toast.error('网络错误', {
        description: '请检查网络连接或稍后重试',
      })
    }
    else if (type === 'api') {
      toast.error('请求失败', {
        description: message,
      })
    }
    else {
      toast.error('操作失败', {
        description: message,
      })
    }
  }

  return { type, message, details }
}

/**
 * 使用 API 错误处理
 */
export function useApiError() {
  return {
    getErrorType,
    getErrorMessage,
    getErrorDetails,
    handleApiError,
  }
}
