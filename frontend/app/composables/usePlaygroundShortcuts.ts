/**
 * Playground 页面键盘快捷键
 */

import { useShortcuts } from './useShortcuts'
import { whenever } from '@vueuse/core'

export function usePlaygroundShortcuts(options: {
  onCreate?: () => void
  onRefresh?: () => void
  onSearch?: () => void
}) {
  const { metaSymbol, usingInput } = useShortcuts()

  // Ctrl/Cmd + N: 创建新项目
  whenever(
    () => !usingInput.value,
    () => {
      const handler = (e: KeyboardEvent) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
          e.preventDefault()
          options.onCreate?.()
        }
      }
      window.addEventListener('keydown', handler)
      return () => window.removeEventListener('keydown', handler)
    },
  )

  // Ctrl/Cmd + R: 刷新数据
  whenever(
    () => !usingInput.value,
    () => {
      const handler = (e: KeyboardEvent) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
          e.preventDefault()
          options.onRefresh?.()
        }
      }
      window.addEventListener('keydown', handler)
      return () => window.removeEventListener('keydown', handler)
    },
  )

  // Ctrl/Cmd + K: 聚焦搜索框
  whenever(
    () => !usingInput.value,
    () => {
      const handler = (e: KeyboardEvent) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
          e.preventDefault()
          options.onSearch?.()
        }
      }
      window.addEventListener('keydown', handler)
      return () => window.removeEventListener('keydown', handler)
    },
  )

  // Escape: 关闭对话框
  const handleEscape = (callback?: () => void) => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        callback?.()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }

  return {
    metaSymbol,
    handleEscape,
  }
}
