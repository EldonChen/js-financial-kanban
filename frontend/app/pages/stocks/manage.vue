<script setup lang="ts">
import { toast } from 'vue-sonner'
import { useStocksService } from '~/composables/useApi'

const config = useRuntimeConfig()
const stocksService = useStocksService()

// Tab 切换
const activeTab = ref('manage')

// ==================== 1. 更新股票数据 ====================
// 更新选项
const updateOption = ref<'all' | 'selected' | 'market'>('all')
const selectedMarket = ref<string>('')
const delay = ref<number[]>([1.0])

// SSE 连接状态
const isConnecting = ref(false)
const isConnected = ref(false)
const abortController = ref<AbortController | null>(null)

// 进度数据
interface ProgressData {
  stage: 'init' | 'fetching' | 'saving' | 'completed' | 'error'
  message: string
  progress: number
  total?: number
  current?: number
  fetch_success?: number
  fetch_failed?: number
  save_success?: number
  save_failed?: number
  result?: any
}

const progressData = ref<ProgressData | null>(null)
const errorMessage = ref<string | null>(null)

// 阶段显示文本
const stageText = computed(() => {
  if (!progressData.value)
    return '等待开始'
  const stageMap = {
    init: '初始化',
    fetching: '抓取中',
    saving: '保存中',
    completed: '已完成',
    error: '错误',
  }
  return stageMap[progressData.value.stage] || '未知'
})

// 开始批量更新
async function startBatchUpdate() {
  if (isConnecting.value || isConnected.value) {
    toast.warning('批量更新正在进行中，请先取消当前操作')
    return
  }

  if (updateOption.value === 'market' && !selectedMarket.value) {
    toast.error('请选择市场类型')
    return
  }

  if (delay.value[0] < 0 || delay.value[0] > 10) {
    toast.error('延迟时间必须在 0.0-10.0 秒之间')
    return
  }

  progressData.value = null
  errorMessage.value = null
  isConnecting.value = true

  try {
    const baseUrl = config.public.bffApiUrl
    const url = new URL(`${baseUrl}/api/bff/v1/views/stocks/fetch-all`)

    if (updateOption.value === 'market' && selectedMarket.value) {
      url.searchParams.append('market', selectedMarket.value)
    }
    url.searchParams.append('delay', delay.value[0].toString())

    abortController.value = new AbortController()

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
      signal: abortController.value.signal,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('Response body is null')
    }

    isConnecting.value = false
    isConnected.value = true

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as ProgressData
              progressData.value = data

              if (data.stage === 'completed' || data.stage === 'error') {
                isConnected.value = false
                if (data.stage === 'completed') {
                  toast.success('批量更新完成')
                }
                else {
                  errorMessage.value = data.message
                  toast.error(`批量更新失败: ${data.message}`)
                }
                break
              }
            }
            catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    }
    catch (error: any) {
      if (error.name === 'AbortError') {
        return
      }
      throw error
    }
    finally {
      isConnected.value = false
      abortController.value = null
    }
  }
  catch (error: any) {
    if (error.name === 'AbortError') {
      return
    }
    console.error('Batch update error:', error)
    isConnecting.value = false
    isConnected.value = false
    errorMessage.value = error.message || '批量更新失败'
    toast.error(`批量更新失败: ${errorMessage.value}`)
  }
  finally {
    abortController.value = null
  }
}

function cancelBatchUpdate() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  isConnecting.value = false
  isConnected.value = false
  progressData.value = null
  errorMessage.value = null
  toast.info('已取消批量更新')
}

// ==================== 2. 删除全部股票 ====================
const deletingAll = ref(false)
const showDeleteAllDialog = ref(false)

async function deleteAllStocks() {
  deletingAll.value = true
  try {
    const response = await fetch(`${config.public.pythonApiUrl}/api/v1/stocks/all`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    const deletedCount = data.data?.deleted_count || 0
    toast.success(`已删除所有股票，共删除 ${deletedCount} 条记录`)
    showDeleteAllDialog.value = false
  }
  catch (error: any) {
    console.error('Delete all stocks error:', error)
    toast.error(`删除失败: ${error.message || '未知错误'}`)
  }
  finally {
    deletingAll.value = false
  }
}

// ==================== 3. 手动添加股票 ====================
const addingStock = ref(false)
const newStockTicker = ref('')
const newStockMarket = ref<string>('none')
const newStockProvider = ref<string>('auto')

async function addStock() {
  if (!newStockTicker.value.trim()) {
    toast.error('请输入股票代码')
    return
  }

  addingStock.value = true
  try {
    const url = new URL(`${config.public.bffApiUrl}/api/bff/v1/views/stocks/${newStockTicker.value.trim()}/update`)
    if (newStockMarket.value && newStockMarket.value !== 'none') {
      url.searchParams.append('market', newStockMarket.value)
    }
    if (newStockProvider.value && newStockProvider.value !== 'auto') {
      url.searchParams.append('preferred_provider', newStockProvider.value)
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    toast.success(`股票 ${newStockTicker.value.trim()} 添加成功`)
    newStockTicker.value = ''
    newStockMarket.value = 'none'
    newStockProvider.value = 'auto'
  }
  catch (error: any) {
    console.error('Add stock error:', error)
    toast.error(`添加失败: ${error.message || '未知错误'}`)
  }
  finally {
    addingStock.value = false
  }
}

// ==================== 4. 查看和管理自动更新计划 ====================
const schedules = ref<any[]>([])
const scheduleStatus = ref<any>(null)
const loadingSchedules = ref(false)
const schedulePage = ref(1)
const schedulePageSize = ref(20)

async function loadSchedules() {
  loadingSchedules.value = true
  try {
    const response = await fetch(
      `${config.public.bffApiUrl}/api/bff/v1/views/stocks/schedules?page=${schedulePage.value}&page_size=${schedulePageSize.value}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )

    if (!response.ok) {
      // 404 或空数据视为正常情况，不显示错误
      if (response.status === 404) {
        schedules.value = []
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    schedules.value = data.data?.items || []
  }
  catch (error: any) {
    // 网络错误或其他错误才显示提示，404 等已在上面的 if 中处理
    if (error.message && !error.message.includes('404')) {
      console.error('Load schedules error:', error)
      toast.error(`加载更新计划失败: ${error.message || '未知错误'}`)
    }
    else {
      // 静默处理，只设置空数组
      schedules.value = []
    }
  }
  finally {
    loadingSchedules.value = false
  }
}

async function loadScheduleStatus() {
  try {
    const response = await fetch(`${config.public.bffApiUrl}/api/bff/v1/views/stocks/schedules/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      // 404 或空数据视为正常情况，设置默认值
      if (response.status === 404) {
        scheduleStatus.value = {
          total: 0,
          active: 0,
          inactive: 0,
          next_run_count: 0,
        }
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    scheduleStatus.value = data.data || {
      total: 0,
      active: 0,
      inactive: 0,
      next_run_count: 0,
    }
  }
  catch (error: any) {
    // 静默处理，设置默认值，不显示错误
    scheduleStatus.value = {
      total: 0,
      active: 0,
      inactive: 0,
      next_run_count: 0,
    }
  }
}

async function toggleSchedule(scheduleId: string) {
  try {
    const response = await fetch(`${config.public.bffApiUrl}/api/bff/v1/views/stocks/schedules/${scheduleId}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    toast.success('更新计划状态已切换')
    await loadSchedules()
    await loadScheduleStatus()
  }
  catch (error: any) {
    console.error('Toggle schedule error:', error)
    toast.error(`切换失败: ${error.message || '未知错误'}`)
  }
}

async function deleteSchedule(scheduleId: string) {
  try {
    const response = await fetch(`${config.public.bffApiUrl}/api/bff/v1/views/stocks/schedules/${scheduleId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    toast.success('更新计划已删除')
    await loadSchedules()
    await loadScheduleStatus()
  }
  catch (error: any) {
    console.error('Delete schedule error:', error)
    toast.error(`删除失败: ${error.message || '未知错误'}`)
  }
}

// 新增更新计划相关
const showCreateScheduleDialog = ref(false)
const creatingSchedule = ref(false)
const newSchedule = ref({
  schedule_type: 'cron' as 'cron' | 'interval',
  schedule_config: {
    cron: '0 9 * * 1-5', // 默认：工作日 9:00
    interval: 3600, // 默认：1小时
  },
  is_active: true,
  ticker: '',
  name: '',
})

async function createSchedule() {
  if (!newSchedule.value.name && !newSchedule.value.ticker) {
    toast.error('请填写计划名称或股票代码')
    return
  }

  if (newSchedule.value.schedule_type === 'cron' && !newSchedule.value.schedule_config.cron) {
    toast.error('请填写 Cron 表达式')
    return
  }

  if (newSchedule.value.schedule_type === 'interval' && !newSchedule.value.schedule_config.interval) {
    toast.error('请填写间隔时间（秒）')
    return
  }

  creatingSchedule.value = true
  try {
    const scheduleData: any = {
      schedule_type: newSchedule.value.schedule_type,
      schedule_config: {},
      is_active: newSchedule.value.is_active,
    }

    if (newSchedule.value.schedule_type === 'cron') {
      scheduleData.schedule_config.cron = newSchedule.value.schedule_config.cron
    }
    else {
      scheduleData.schedule_config.interval = newSchedule.value.schedule_config.interval
    }

    if (newSchedule.value.ticker) {
      scheduleData.ticker = newSchedule.value.ticker
    }
    if (newSchedule.value.name) {
      scheduleData.name = newSchedule.value.name
    }

    const response = await fetch(`${config.public.bffApiUrl}/api/bff/v1/views/stocks/schedules`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scheduleData),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }

    toast.success('更新计划创建成功')
    showCreateScheduleDialog.value = false
    // 重置表单
    newSchedule.value = {
      schedule_type: 'cron',
      schedule_config: {
        cron: '0 9 * * 1-5',
        interval: 3600,
      },
      is_active: true,
      ticker: '',
      name: '',
    }
    await loadSchedules()
    await loadScheduleStatus()
  }
  catch (error: any) {
    console.error('Create schedule error:', error)
    toast.error(`创建失败: ${error.message || '未知错误'}`)
  }
  finally {
    creatingSchedule.value = false
  }
}

// ==================== 5. 查看数据源详细信息 ====================
const providerStatus = ref<any>(null)
const loadingProviders = ref(false)

async function loadProviderStatus() {
  loadingProviders.value = true
  try {
    const response = await fetch(`${config.public.bffApiUrl}/api/bff/v1/views/stocks/providers/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    providerStatus.value = data.data
  }
  catch (error: any) {
    console.error('Load provider status error:', error)
    toast.error(`加载数据源信息失败: ${error.message || '未知错误'}`)
  }
  finally {
    loadingProviders.value = false
  }
}

// 格式化函数
function formatNumber(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN').format(value)
}

function formatPercent(value?: number): string {
  if (value === undefined || value === null)
    return '0%'
  return `${Math.round(value)}%`
}

function formatDate(dateString?: string): string {
  if (!dateString)
    return '-'
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }
  catch {
    return dateString
  }
}

// 初始化加载
onMounted(() => {
  if (activeTab.value === 'schedules') {
    loadSchedules()
    loadScheduleStatus()
  }
  else if (activeTab.value === 'providers') {
    loadProviderStatus()
  }
})

// 监听 Tab 切换
watch(activeTab, (newTab) => {
  if (newTab === 'schedules') {
    loadSchedules()
    loadScheduleStatus()
  }
  else if (newTab === 'providers') {
    loadProviderStatus()
  }
})
</script>

<template>
  <div class="w-full flex flex-col gap-6">
    <!-- 页面头部 -->
    <div>
      <h2 class="text-2xl font-bold tracking-tight">
        管理股票信息
      </h2>
      <p class="text-muted-foreground">
        管理股票数据、更新计划和数据源信息
      </p>
    </div>

    <!-- Tabs 导航 -->
    <Tabs v-model="activeTab" class="w-full">
      <TabsList class="w-full justify-center">
        <TabsTrigger value="manage">
          股票管理
        </TabsTrigger>
        <TabsTrigger value="schedules">
          自动更新计划
        </TabsTrigger>
        <TabsTrigger value="providers">
          数据源信息
        </TabsTrigger>
      </TabsList>

      <!-- 1. 股票管理（合并更新、删除、添加功能） -->
      <TabsContent value="manage" class="space-y-6">
        <!-- 1.1 更新股票数据 -->
        <Card>
          <CardHeader>
            <CardTitle>更新配置</CardTitle>
            <CardDescription>
              选择更新选项和延迟设置
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-6">
            <!-- 更新选项 -->
            <div class="space-y-2">
              <Label>更新选项</Label>
              <RadioGroup v-model="updateOption" :disabled="isConnecting || isConnected">
                <div class="flex items-center space-x-2">
                  <RadioGroupItem id="option-all" value="all" />
                  <Label for="option-all">全量更新</Label>
                </div>
                <div class="flex items-center space-x-2">
                  <RadioGroupItem id="option-selected" value="selected" />
                  <Label for="option-selected">选择更新（待实现）</Label>
                </div>
                <div class="flex items-center space-x-2">
                  <RadioGroupItem id="option-market" value="market" />
                  <Label for="option-market">按市场更新</Label>
                </div>
              </RadioGroup>
            </div>

            <!-- 市场选择 -->
            <div v-if="updateOption === 'market'" class="space-y-2">
              <Label>市场类型</Label>
              <Select v-model="selectedMarket" :disabled="isConnecting || isConnected">
                <SelectTrigger>
                  <SelectValue placeholder="请选择市场类型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="A股">
                    A股
                  </SelectItem>
                  <SelectItem value="港股">
                    港股
                  </SelectItem>
                  <SelectItem value="美股">
                    美股
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <!-- 延迟设置 -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <Label>延迟设置（秒）</Label>
                <span class="text-sm text-muted-foreground">{{ delay[0] }} 秒</span>
              </div>
              <Slider
                v-model="delay"
                :min="0"
                :max="10"
                :step="0.1"
                :disabled="isConnecting || isConnected"
              />
              <div class="flex items-center justify-between text-xs text-muted-foreground">
                <span>0.0</span>
                <span>10.0</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <Button
                :disabled="isConnecting || isConnected"
                @click="startBatchUpdate"
              >
                <Icon
                  v-if="isConnecting"
                  name="lucide:loader-2"
                  class="mr-2 h-4 w-4 animate-spin"
                />
                <Icon
                  v-else
                  name="lucide:play"
                  class="mr-2 h-4 w-4"
                />
                {{ isConnecting ? '连接中...' : '开始更新' }}
              </Button>
              <Button
                variant="outline"
                :disabled="!isConnecting && !isConnected"
                @click="cancelBatchUpdate"
              >
                <Icon name="lucide:x" class="mr-2 h-4 w-4" />
                取消
              </Button>
            </div>
          </CardContent>
        </Card>

        <!-- 进度展示 -->
        <Card v-if="progressData || errorMessage">
          <CardHeader>
            <CardTitle>更新进度</CardTitle>
            <CardDescription>
              实时显示批量更新进度
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-6">
            <!-- 阶段显示 -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <Icon
                  v-if="progressData?.stage === 'completed'"
                  name="lucide:check-circle-2"
                  class="h-5 w-5 text-green-500"
                />
                <Icon
                  v-else-if="progressData?.stage === 'error'"
                  name="lucide:x-circle"
                  class="h-5 w-5 text-red-500"
                />
                <Icon
                  v-else-if="progressData?.stage === 'fetching' || progressData?.stage === 'saving'"
                  name="lucide:loader-2"
                  class="h-5 w-5 animate-spin text-blue-500"
                />
                <Icon
                  v-else
                  name="lucide:circle"
                  class="h-5 w-5 text-muted-foreground"
                />
                <span class="font-medium">{{ stageText }}</span>
              </div>
              <span class="text-sm text-muted-foreground">
                {{ formatPercent(progressData?.progress) }}
              </span>
            </div>

            <!-- 进度条 -->
            <div class="space-y-2">
              <Progress :model-value="progressData?.progress || 0" />
              <p class="text-sm text-muted-foreground">
                {{ progressData?.message || '等待开始...' }}
              </p>
            </div>

            <!-- 统计信息 -->
            <div v-if="progressData && (progressData.total || progressData.current)" class="grid grid-cols-2 gap-4">
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  总数
                </p>
                <p class="text-2xl font-bold">
                  {{ formatNumber(progressData.total) }}
                </p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  当前进度
                </p>
                <p class="text-2xl font-bold">
                  {{ formatNumber(progressData.current) }}
                </p>
              </div>
            </div>

            <!-- 详细统计 -->
            <div v-if="progressData && (progressData.stage === 'fetching' || progressData.stage === 'saving')" class="grid grid-cols-2 gap-4">
              <div v-if="progressData.fetch_success !== undefined" class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  抓取成功
                </p>
                <p class="text-xl font-semibold text-green-600">
                  {{ formatNumber(progressData.fetch_success) }}
                </p>
              </div>
              <div v-if="progressData.fetch_failed !== undefined" class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  抓取失败
                </p>
                <p class="text-xl font-semibold text-red-600">
                  {{ formatNumber(progressData.fetch_failed) }}
                </p>
              </div>
              <div v-if="progressData.save_success !== undefined" class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  保存成功
                </p>
                <p class="text-xl font-semibold text-green-600">
                  {{ formatNumber(progressData.save_success) }}
                </p>
              </div>
              <div v-if="progressData.save_failed !== undefined" class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  保存失败
                </p>
                <p class="text-xl font-semibold text-red-600">
                  {{ formatNumber(progressData.save_failed) }}
                </p>
              </div>
            </div>

            <!-- 错误信息 -->
            <Alert v-if="errorMessage || progressData?.stage === 'error'" variant="destructive">
              <Icon name="lucide:alert-circle" mode="svg" class="h-4 w-4" />
              <AlertTitle>错误</AlertTitle>
              <AlertDescription>
                {{ errorMessage || progressData?.message || '未知错误' }}
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <!-- 1.2 手动添加股票 -->
        <Card>
          <CardHeader>
            <CardTitle>手动添加股票</CardTitle>
            <CardDescription>
              通过股票代码添加新股票到数据库
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <Label>股票代码</Label>
              <Input
                v-model="newStockTicker"
                placeholder="请输入股票代码，如：AAPL"
                :disabled="addingStock"
                @keyup.enter="addStock"
              />
            </div>
            <div class="space-y-2">
              <Label>市场类型（可选）</Label>
              <Select v-model="newStockMarket" :disabled="addingStock">
                <SelectTrigger>
                  <SelectValue placeholder="请选择市场类型（可选）" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">
                    不指定
                  </SelectItem>
                  <SelectItem value="A股">
                    A股
                  </SelectItem>
                  <SelectItem value="港股">
                    港股
                  </SelectItem>
                  <SelectItem value="美股">
                    美股
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div class="space-y-2">
              <Label>首选数据源（可选）</Label>
              <Select v-model="newStockProvider" :disabled="addingStock">
                <SelectTrigger>
                  <SelectValue placeholder="请选择数据源（可选）" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">
                    自动选择
                  </SelectItem>
                  <SelectItem value="yfinance">
                    Yahoo Finance
                  </SelectItem>
                  <SelectItem value="akshare">
                    AKShare
                  </SelectItem>
                  <SelectItem value="easyquotation">
                    EasyQuotation
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              :disabled="addingStock || !newStockTicker.trim()"
              @click="addStock"
            >
              <Icon
                v-if="addingStock"
                name="lucide:loader-2"
                class="mr-2 h-4 w-4 animate-spin"
              />
              <Icon
                v-else
                name="lucide:plus"
                class="mr-2 h-4 w-4"
              />
              {{ addingStock ? '添加中...' : '添加股票' }}
            </Button>
          </CardContent>
        </Card>

        <!-- 1.3 删除全部股票 -->
        <Card>
          <CardHeader>
            <CardTitle>删除全部股票</CardTitle>
            <CardDescription>
              此操作将删除数据库中的所有股票记录，请谨慎操作
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <Alert variant="destructive">
              <Icon name="lucide:alert-triangle" mode="svg" class="h-4 w-4" />
              <AlertTitle>危险操作</AlertTitle>
              <AlertDescription>
                删除所有股票是不可逆的操作，请确认您真的需要执行此操作。
              </AlertDescription>
            </Alert>
            <Button
              variant="destructive"
              :disabled="deletingAll"
              @click="showDeleteAllDialog = true"
            >
              <Icon
                v-if="deletingAll"
                name="lucide:loader-2"
                class="mr-2 h-4 w-4 animate-spin"
              />
              <Icon
                v-else
                name="lucide:trash-2"
                class="mr-2 h-4 w-4"
              />
              {{ deletingAll ? '删除中...' : '删除全部股票' }}
            </Button>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- 2. 查看和管理自动更新计划 -->
      <TabsContent value="schedules" class="space-y-6">
        <!-- 统计信息 -->
        <Card v-if="scheduleStatus">
          <CardHeader>
            <CardTitle>更新计划统计</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-4 gap-4">
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  总数
                </p>
                <p class="text-2xl font-bold">
                  {{ formatNumber(scheduleStatus.total) }}
                </p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  激活
                </p>
                <p class="text-2xl font-bold text-green-600">
                  {{ formatNumber(scheduleStatus.active) }}
                </p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  未激活
                </p>
                <p class="text-2xl font-bold text-gray-600">
                  {{ formatNumber(scheduleStatus.inactive) }}
                </p>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  待执行
                </p>
                <p class="text-2xl font-bold text-blue-600">
                  {{ formatNumber(scheduleStatus.next_run_count) }}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 更新计划列表 -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>更新计划列表</CardTitle>
                <CardDescription>
                  管理自动更新计划
                </CardDescription>
              </div>
              <div class="flex items-center gap-2">
                <Button variant="default" size="sm" @click="showCreateScheduleDialog = true">
                  <Icon name="lucide:plus" class="h-4 w-4 mr-2" />
                  新增更新计划
                </Button>
                <Button variant="outline" size="sm" @click="loadSchedules">
                  <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
                  刷新
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div v-if="loadingSchedules" class="flex items-center justify-center py-8">
              <Icon name="lucide:loader-2" class="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
            <div v-else-if="schedules.length === 0" class="py-8 text-center text-muted-foreground">
              <p class="mb-4">
                暂无更新计划
              </p>
              <Button variant="outline" @click="showCreateScheduleDialog = true">
                <Icon name="lucide:plus" class="h-4 w-4 mr-2" />
                创建第一个更新计划
              </Button>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="schedule in schedules"
                :key="schedule._id || schedule.id"
                class="flex items-center justify-between p-4 rounded-lg border"
              >
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <Badge :variant="schedule.is_active ? 'default' : 'secondary'">
                      {{ schedule.is_active ? '激活' : '未激活' }}
                    </Badge>
                    <span class="font-medium">{{ schedule.name || schedule.ticker || '未命名计划' }}</span>
                  </div>
                  <div class="text-sm text-muted-foreground space-y-1">
                    <p v-if="schedule.ticker">
                      股票代码: {{ schedule.ticker }}
                    </p>
                    <p v-if="schedule.cron_expression">
                      Cron 表达式: {{ schedule.cron_expression }}
                    </p>
                    <p v-if="schedule.next_run">
                      下次执行: {{ formatDate(schedule.next_run) }}
                    </p>
                    <p v-if="schedule.last_run">
                      上次执行: {{ formatDate(schedule.last_run) }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    @click="toggleSchedule(schedule._id || schedule.id)"
                  >
                    <Icon name="lucide:power" class="h-4 w-4 mr-1" />
                    {{ schedule.is_active ? '停用' : '激活' }}
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    @click="deleteSchedule(schedule._id || schedule.id)"
                  >
                    <Icon name="lucide:trash-2" class="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 历史更新记录 -->
        <Card>
          <CardHeader>
            <CardTitle>历史更新记录</CardTitle>
            <CardDescription>
              查看更新计划的执行历史
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div v-if="schedules.length === 0" class="py-8 text-center text-muted-foreground">
              暂无更新计划，无法显示历史记录
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="schedule in schedules"
                :key="schedule._id || schedule.id"
                class="p-4 rounded-lg border"
              >
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ schedule.name || schedule.ticker || '未命名计划' }}</span>
                    <Badge :variant="schedule.is_active ? 'default' : 'secondary'">
                      {{ schedule.is_active ? '激活' : '未激活' }}
                    </Badge>
                  </div>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div class="space-y-1">
                    <p class="text-muted-foreground">
                      执行次数
                    </p>
                    <p class="text-lg font-semibold">
                      {{ formatNumber(schedule.run_count || 0) }}
                    </p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-muted-foreground">
                      错误次数
                    </p>
                    <p class="text-lg font-semibold" :class="schedule.error_count > 0 ? 'text-red-600' : ''">
                      {{ formatNumber(schedule.error_count || 0) }}
                    </p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-muted-foreground">
                      上次执行
                    </p>
                    <p class="text-sm font-medium">
                      {{ schedule.last_run ? formatDate(schedule.last_run) : '从未执行' }}
                    </p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-muted-foreground">
                      下次执行
                    </p>
                    <p class="text-sm font-medium">
                      {{ schedule.next_run ? formatDate(schedule.next_run) : '未计划' }}
                    </p>
                  </div>
                </div>
                <div v-if="schedule.last_error" class="mt-3 p-2 rounded bg-destructive/10 border border-destructive/20">
                  <p class="text-xs text-destructive font-medium mb-1">
                    最后错误
                  </p>
                  <p class="text-xs text-destructive/80">
                    {{ schedule.last_error }}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- 3. 查看数据源详细信息 -->
      <TabsContent value="providers" class="space-y-6">
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>数据源信息</CardTitle>
                <CardDescription>
                  查看数据源状态和市场覆盖情况
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" @click="loadProviderStatus">
                <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
                刷新
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div v-if="loadingProviders" class="flex items-center justify-center py-8">
              <Icon name="lucide:loader-2" class="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
            <div v-else-if="!providerStatus" class="py-8 text-center text-muted-foreground">
              暂无数据源信息
            </div>
            <div v-else class="space-y-6">
              <!-- 总数 -->
              <div class="space-y-1">
                <p class="text-sm text-muted-foreground">
                  数据源总数
                </p>
                <p class="text-2xl font-bold">
                  {{ formatNumber(providerStatus.total_providers) }}
                </p>
              </div>

              <!-- 数据源列表 -->
              <div v-if="providerStatus.providers" class="space-y-4">
                <p class="font-medium">
                  数据源详情
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div
                    v-for="(provider, name) in providerStatus.providers"
                    :key="name"
                    class="p-4 rounded-lg border"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <span class="font-medium">{{ name }}</span>
                      <Badge v-if="provider.enabled" variant="default">
                        已启用
                      </Badge>
                      <Badge v-else variant="secondary">
                        已禁用
                      </Badge>
                    </div>
                    <div class="text-sm text-muted-foreground space-y-1">
                      <p v-if="provider.description">
                        描述: {{ provider.description }}
                      </p>
                      <p v-if="provider.markets">
                        支持市场: {{ Array.isArray(provider.markets) ? provider.markets.join(', ') : provider.markets }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 市场覆盖 -->
              <div v-if="providerStatus.market_coverage" class="space-y-4">
                <p class="font-medium">
                  市场覆盖情况
                </p>
                <div class="space-y-2">
                  <div
                    v-for="(providers, market) in providerStatus.market_coverage"
                    :key="market"
                    class="p-3 rounded-lg border"
                  >
                    <p class="font-medium mb-1">
                      {{ market }}
                    </p>
                    <div class="flex flex-wrap gap-2">
                      <Badge
                        v-for="provider in providers"
                        :key="provider"
                        variant="outline"
                      >
                        {{ provider }}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>

    <!-- 新增更新计划对话框 -->
    <AlertDialog v-model:open="showCreateScheduleDialog">
      <AlertDialogContent class="max-w-2xl">
        <AlertDialogHeader>
          <AlertDialogTitle>新增更新计划</AlertDialogTitle>
          <AlertDialogDescription>
            创建一个新的自动更新计划
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label>计划名称（可选）</Label>
            <Input
              v-model="newSchedule.name"
              placeholder="例如：每日更新AAPL"
              :disabled="creatingSchedule"
            />
          </div>
          <div class="space-y-2">
            <Label>股票代码（可选）</Label>
            <Input
              v-model="newSchedule.ticker"
              placeholder="例如：AAPL"
              :disabled="creatingSchedule"
            />
          </div>
          <div class="space-y-2">
            <Label>调度类型</Label>
            <Select v-model="newSchedule.schedule_type" :disabled="creatingSchedule">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cron">
                  Cron 表达式
                </SelectItem>
                <SelectItem value="interval">
                  固定间隔
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div v-if="newSchedule.schedule_type === 'cron'" class="space-y-2">
            <Label>Cron 表达式</Label>
            <Input
              v-model="newSchedule.schedule_config.cron"
              placeholder="例如：0 9 * * 1-5 (工作日 9:00)"
              :disabled="creatingSchedule"
            />
            <p class="text-xs text-muted-foreground">
              格式：分 时 日 月 周。示例：0 9 * * 1-5 表示工作日 9:00 执行
            </p>
          </div>
          <div v-else class="space-y-2">
            <Label>间隔时间（秒）</Label>
            <Input
              v-model.number="newSchedule.schedule_config.interval"
              type="number"
              placeholder="例如：3600 (1小时)"
              :disabled="creatingSchedule"
            />
          </div>
          <div class="flex items-center space-x-2">
            <input
              id="schedule-active"
              v-model="newSchedule.is_active"
              type="checkbox"
              class="h-4 w-4 rounded border-gray-300"
              :disabled="creatingSchedule"
            >
            <Label for="schedule-active" class="cursor-pointer">创建后立即激活</Label>
          </div>
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="creatingSchedule">
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            :disabled="creatingSchedule"
            @click="createSchedule"
          >
            <Icon
              v-if="creatingSchedule"
              name="lucide:loader-2"
              class="mr-2 h-4 w-4 animate-spin"
            />
            <Icon
              v-else
              name="lucide:plus"
              class="mr-2 h-4 w-4"
            />
            创建
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <!-- 删除全部股票确认对话框 -->
    <AlertDialog v-model:open="showDeleteAllDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认删除</AlertDialogTitle>
          <AlertDialogDescription>
            此操作将删除数据库中的所有股票记录，此操作不可撤销。确定要继续吗？
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="deletingAll">
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            :disabled="deletingAll"
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            @click="deleteAllStocks"
          >
            <Icon
              v-if="deletingAll"
              name="lucide:loader-2"
              class="mr-2 h-4 w-4 animate-spin"
            />
            <Icon
              v-else
              name="lucide:trash-2"
              class="mr-2 h-4 w-4"
            />
            确认删除
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
