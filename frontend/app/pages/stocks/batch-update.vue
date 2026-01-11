<script setup lang="ts">
import { toast } from 'vue-sonner'
import { useStocksService } from '~/composables/useApi'

const config = useRuntimeConfig()
const stocksService = useStocksService()

// 更新选项
const updateOption = ref<'all' | 'selected' | 'market'>('all')
const selectedMarket = ref<string>('')

// 延迟设置
const delay = ref<number>(1.0)

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

  // 验证参数
  if (updateOption.value === 'market' && !selectedMarket.value) {
    toast.error('请选择市场类型')
    return
  }

  if (delay.value < 0 || delay.value > 10) {
    toast.error('延迟时间必须在 0.0-10.0 秒之间')
    return
  }

  // 重置状态
  progressData.value = null
  errorMessage.value = null
  isConnecting.value = true

  try {
    // 构建 URL
    const baseUrl = config.public.bffApiUrl
    const url = new URL(`${baseUrl}/api/bff/v1/views/stocks/fetch-all`)

    // 添加查询参数
    if (updateOption.value === 'market' && selectedMarket.value) {
      url.searchParams.append('market', selectedMarket.value)
    }
    url.searchParams.append('delay', delay.value.toString())

    // 创建 AbortController 用于取消请求
    abortController.value = new AbortController()

    // 创建 EventSource 连接
    // 注意：EventSource 只支持 GET 请求，但我们需要 POST
    // 所以需要使用 fetch API 并手动处理 SSE 流
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

    // 读取 SSE 流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // 解码数据
        buffer += decoder.decode(value, { stream: true })

        // 处理完整的 SSE 消息
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留最后不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as ProgressData
              progressData.value = data

              // 如果完成或出错，结束连接
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
      // 如果是取消操作，不显示错误
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
    // 如果是取消操作，不显示错误
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

// 取消批量更新
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

// 格式化数字
function formatNumber(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN').format(value)
}

// 格式化百分比
function formatPercent(value?: number): string {
  if (value === undefined || value === null)
    return '0%'
  return `${Math.round(value)}%`
}
</script>

<template>
  <div class="w-full flex flex-col gap-6">
    <!-- 页面头部 -->
    <div>
      <h2 class="text-2xl font-bold tracking-tight">
        批量更新股票
      </h2>
      <p class="text-muted-foreground">
        批量更新股票数据，支持实时进度显示
      </p>
    </div>

    <!-- 配置卡片 -->
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

        <!-- 市场选择（仅在按市场更新时显示） -->
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
            <span class="text-sm text-muted-foreground">{{ delay }} 秒</span>
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

    <!-- 进度展示卡片 -->
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

        <!-- 详细统计（fetching/saving 阶段） -->
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

        <!-- 完成结果 -->
        <div v-if="progressData?.stage === 'completed' && progressData.result" class="space-y-2">
          <p class="text-sm font-medium">
            更新结果
          </p>
          <div class="rounded-lg bg-muted p-4">
            <pre class="text-xs">{{ JSON.stringify(progressData.result, null, 2) }}</pre>
          </div>
        </div>

        <!-- 错误信息 -->
        <Alert v-if="errorMessage || progressData?.stage === 'error'" variant="destructive">
          <Icon name="lucide:alert-circle" class="h-4 w-4" />
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>
            {{ errorMessage || progressData?.message || '未知错误' }}
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  </div>
</template>
