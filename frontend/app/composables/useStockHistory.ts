/**
 * Stock History Composable
 * 提供股票历史数据和技术指标的管理逻辑
 */

import type { HistoricalData, HistoricalDataQueryParams, HistoricalDataStatistics, IndicatorData, SSEProgress as SSEProgressType, SupportedIndicator } from '~/api/types'
import { toast } from 'vue-sonner'
import { handleApiError } from '~/composables/useApiError'
import { useHistoricalDataService } from '~/composables/useHistoricalData'
import { useIndicatorsService } from '~/composables/useIndicators'

export function useStockHistory(ticker: Ref<string>) {
  const historicalDataService = useHistoricalDataService()
  const indicatorsService = useIndicatorsService()

  // ==================== 历史数据相关 ====================
  const historicalData = ref<HistoricalData[]>([])
  const historicalStatistics = ref<HistoricalDataStatistics | null>(null)
  const historicalLoading = ref(false)
  const historicalPagination = ref({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 0,
  })
  const historicalQueryParams = ref<HistoricalDataQueryParams>({
    ticker: '',
    period: '1d',
    start_date: '',
    end_date: '',
    page: 1,
    page_size: 20,
  })
  const historicalSSEProgress = ref<SSEProgressType | null>(null)
  const isUpdatingHistorical = ref(false)

  // 时间周期选项
  const periodOptions = [
    { label: '分时', value: 'tick' },
    { label: '日K', value: '1d' },
    { label: '1min', value: '1m' },
    { label: '5min', value: '5m' },
    { label: '15min', value: '15m' },
    { label: '30min', value: '30m' },
    { label: '1h', value: '60m' },
    { label: '周K', value: '1w' },
    { label: '月K', value: '1M' },
  ]

  // 加载历史数据
  async function loadHistoricalData() {
    if (!ticker.value)
      return

    historicalLoading.value = true
    try {
      historicalQueryParams.value.ticker = ticker.value
      const response = await historicalDataService.getKlineDataPaginated(
        ticker.value,
        historicalQueryParams.value,
      )
      historicalData.value = response.items
      historicalPagination.value = {
        total: response.total,
        page: response.page,
        page_size: response.page_size,
        total_pages: response.total_pages,
      }

      const stats = await historicalDataService.getKlineDataStatistics(
        ticker.value,
        historicalQueryParams.value.period,
      )
      historicalStatistics.value = stats
    }
    catch (err) {
      handleApiError(err, { defaultMessage: '无法加载历史数据' })
    }
    finally {
      historicalLoading.value = false
    }
  }

  // 更新历史数据
  async function updateHistoricalData() {
    if (!ticker.value)
      return

    isUpdatingHistorical.value = true
    historicalSSEProgress.value = null

    try {
      await historicalDataService.batchUpdateKlineData(
        [ticker.value],
        {
          period: historicalQueryParams.value.period,
          start_date: historicalQueryParams.value.start_date,
          end_date: historicalQueryParams.value.end_date,
        },
        (progress) => {
          historicalSSEProgress.value = progress
        },
      )
      toast.success('历史数据更新完成')
      await loadHistoricalData()
    }
    catch (err) {
      handleApiError(err, { defaultMessage: '历史数据更新失败' })
    }
    finally {
      isUpdatingHistorical.value = false
      historicalSSEProgress.value = null
    }
  }

  // 处理周期变化
  function handlePeriodChange(period: string) {
    historicalQueryParams.value.period = period
    loadHistoricalData()
  }

  // ==================== 技术指标相关 ====================
  const selectedIndicators = ref<string[]>([]) // 多选指标
  const indicatorDataMap = ref<Record<string, IndicatorData[]>>({}) // 每个指标的数据
  const indicatorLoading = ref(false)
  const supportedIndicators = ref<SupportedIndicator[]>([])
  const isCalculating = ref(false)
  const indicatorSSEProgress = ref<SSEProgressType | null>(null)

  // 加载支持的指标列表
  async function loadSupportedIndicators() {
    try {
      const indicators = await indicatorsService.getSupportedIndicators()
      supportedIndicators.value = indicators
    }
    catch (err) {
      console.error('Failed to load supported indicators:', err)
    }
  }

  // 加载指标数据（支持多选）
  async function loadIndicatorData() {
    if (!ticker.value || selectedIndicators.value.length === 0) {
      indicatorDataMap.value = {}
      return
    }

    indicatorLoading.value = true
    try {
      // 并行加载所有选中的指标数据
      const promises = selectedIndicators.value.map(async (indicatorName) => {
        try {
          const response = await indicatorsService.getIndicatorDataPaginated(
            ticker.value,
            indicatorName,
            {
              ticker: ticker.value,
              indicator_name: indicatorName,
              period: historicalQueryParams.value.period,
              start_date: historicalQueryParams.value.start_date,
              end_date: historicalQueryParams.value.end_date,
              page: 1,
              page_size: 1000,
            },
          )
          return { indicatorName, data: response.items }
        }
        catch (err) {
          console.error(`Failed to load indicator ${indicatorName}:`, err)
          return { indicatorName, data: [] }
        }
      })

      const results = await Promise.all(promises)
      const newMap: Record<string, IndicatorData[]> = {}
      results.forEach(({ indicatorName, data }) => {
        newMap[indicatorName] = data || []
      })
      indicatorDataMap.value = newMap
    }
    catch (err) {
      handleApiError(err, { defaultMessage: '无法加载指标数据' })
    }
    finally {
      indicatorLoading.value = false
    }
  }

  // 切换指标选择
  async function toggleIndicator(indicatorName: string) {
    console.warn('[useStockHistory] toggleIndicator called:', {
      indicatorName,
      currentSelected: [...selectedIndicators.value],
      ticker: ticker.value,
    })

    const index = selectedIndicators.value.indexOf(indicatorName)
    if (index > -1) {
      console.warn('[useStockHistory] Removing indicator:', indicatorName)
      selectedIndicators.value.splice(index, 1)
      // 删除该指标的数据
      delete indicatorDataMap.value[indicatorName]
      console.warn('[useStockHistory] After remove:', {
        selectedIndicators: [...selectedIndicators.value],
        indicatorDataMapKeys: Object.keys(indicatorDataMap.value),
      })
    }
    else {
      console.warn('[useStockHistory] Adding indicator:', indicatorName)
      selectedIndicators.value.push(indicatorName)
      console.warn('[useStockHistory] After push:', {
        selectedIndicators: [...selectedIndicators.value],
      })

      // 先尝试加载数据
      await loadIndicatorData()
      console.warn('[useStockHistory] After loadIndicatorData:', {
        indicatorDataMapKeys: Object.keys(indicatorDataMap.value),
        hasDataForIndicator: !!indicatorDataMap.value[indicatorName],
        dataLength: indicatorDataMap.value[indicatorName]?.length || 0,
      })

      // 检查数据是否加载成功，如果为空则自动计算
      const hasData = indicatorDataMap.value[indicatorName] && indicatorDataMap.value[indicatorName].length > 0

      if (!hasData) {
        console.warn('[useStockHistory] No data found, calculating indicator:', indicatorName)
        // 数据不存在，自动计算该指标
        try {
          isCalculating.value = true
          await indicatorsService.calculateIndicator(
            ticker.value,
            indicatorName,
            {
              period: historicalQueryParams.value.period,
              start_date: historicalQueryParams.value.start_date,
              end_date: historicalQueryParams.value.end_date,
            },
          )
          console.warn('[useStockHistory] Indicator calculated, reloading data')
          // 计算完成后重新加载数据
          await loadIndicatorData()
          console.warn('[useStockHistory] After reload:', {
            indicatorDataMapKeys: Object.keys(indicatorDataMap.value),
            hasDataForIndicator: !!indicatorDataMap.value[indicatorName],
            dataLength: indicatorDataMap.value[indicatorName]?.length || 0,
          })
        }
        catch (err) {
          console.error(`Failed to calculate indicator ${indicatorName}:`, err)
          // 如果计算失败，从选中列表中移除
          const removeIndex = selectedIndicators.value.indexOf(indicatorName)
          if (removeIndex > -1) {
            selectedIndicators.value.splice(removeIndex, 1)
          }
          handleApiError(err, { defaultMessage: `无法计算指标 ${indicatorName}` })
        }
        finally {
          isCalculating.value = false
        }
      }
    }
  }

  // 监听时间周期变化，重新加载指标数据
  watch(
    () => historicalQueryParams.value.period,
    () => {
      if (selectedIndicators.value.length > 0) {
        loadIndicatorData()
      }
    },
  )

  return {
    // 历史数据
    historicalData,
    historicalStatistics,
    historicalLoading,
    historicalPagination,
    historicalQueryParams,
    historicalSSEProgress,
    isUpdatingHistorical,
    periodOptions,
    loadHistoricalData,
    updateHistoricalData,
    handlePeriodChange,
    // 技术指标
    selectedIndicators,
    indicatorDataMap,
    indicatorLoading,
    supportedIndicators,
    isCalculating,
    indicatorSSEProgress,
    loadSupportedIndicators,
    loadIndicatorData,
    toggleIndicator,
  }
}
