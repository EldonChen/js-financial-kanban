/**
 * Stock Detail Composable
 * 提供股票详情页面的核心逻辑
 */

import type { Stock } from '~/api/types'
import { ApiError } from '~/api/types'
import { toast } from 'vue-sonner'
import { useStocksService } from '~/composables/useApi'
import { handleApiError } from '~/composables/useApiError'

export function useStockDetail(ticker: Ref<string>) {
  const router = useRouter()
  const stocksService = useStocksService()

  const stock = ref<Stock | null>(null)
  const loading = ref(false)
  const updating = ref(false)
  const deleting = ref(false)
  const showDeleteDialog = ref(false)
  const notFound = ref(false)

  // 加载股票详情
  async function loadStock() {
    loading.value = true
    notFound.value = false
    stock.value = null
    try {
      const result = await stocksService.getStock(ticker.value)
      // 如果返回 null，表示股票不存在
      if (result === null || result === undefined) {
        notFound.value = true
        stock.value = null
      }
      else {
        stock.value = result
        notFound.value = false
      }
    }
    catch (error: any) {
      console.error('loadStock error:', error)
      // 如果股票不存在（404），在页面中显示提示信息
      const isNotFound
        = (error instanceof ApiError && error.code === 404)
          || error?.code === 404
          || error?.status === 404
          || (error?.data && error.data.code === 404)
          || error?.response?.status === 404

      if (isNotFound) {
        console.log('Stock not found, showing not found card')
        notFound.value = true
        stock.value = null
      }
      else {
        // 其他错误显示错误提示
        handleApiError(error, { defaultMessage: '无法加载股票信息' })
        // 对于其他错误，也显示 notFound 提示，避免空白页面
        notFound.value = true
        stock.value = null
      }
    }
    finally {
      loading.value = false
    }
  }

  // 更新股票
  async function updateStock() {
    updating.value = true
    try {
      stock.value = await stocksService.updateStock(ticker.value)
      toast.success('股票数据更新成功')
    }
    catch (error) {
      handleApiError(error, { defaultMessage: '无法更新股票数据' })
    }
    finally {
      updating.value = false
    }
  }

  // 打开删除确认对话框
  function openDeleteDialog() {
    showDeleteDialog.value = true
  }

  // 确认删除
  async function confirmDelete() {
    deleting.value = true
    try {
      await stocksService.deleteStock(ticker.value)
      toast.success('股票删除成功')
      // 删除成功后返回上一页或首页
      if (window.history.length > 1) {
        router.back()
      }
      else {
        router.push('/')
      }
    }
    catch (error) {
      handleApiError(error, { defaultMessage: '无法删除股票' })
    }
    finally {
      deleting.value = false
      showDeleteDialog.value = false
    }
  }

  // 返回上一页
  function goBack() {
    if (window.history.length > 1) {
      router.back()
    }
    else {
      router.push('/')
    }
  }

  return {
    stock,
    loading,
    updating,
    deleting,
    showDeleteDialog,
    notFound,
    loadStock,
    updateStock,
    openDeleteDialog,
    confirmDelete,
    goBack,
  }
}

