<script setup lang="ts">
import NumberFlow from '@number-flow/vue'
import { TrendingUp, BarChart3, Building2, Globe, Database, Clock } from 'lucide-vue-next'
import type { DashboardData } from '~/api/types'
import { useDashboardService } from '~/composables/useApi'
import { handleApiError } from '~/composables/useApiError'
import { toast } from 'vue-sonner'

const dashboardService = useDashboardService()
const router = useRouter()

// 数据状态
const dashboardData = ref<DashboardData | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const refreshing = ref(false)

// 加载 Dashboard 数据
async function loadDashboardData() {
  loading.value = true
  error.value = null
  try {
    const data = await dashboardService.getDashboardData()
    dashboardData.value = data
  }
  catch (err) {
    console.error('loadDashboardData error:', err)
    error.value = '无法加载 Dashboard 数据'
    handleApiError(err, { defaultMessage: '无法加载 Dashboard 数据' })
  }
  finally {
    loading.value = false
  }
}

// 刷新数据
async function refreshData() {
  refreshing.value = true
  try {
    const data = await dashboardService.getDashboardData()
    dashboardData.value = data
    toast.success('数据已刷新')
  }
  catch (err) {
    console.error('refreshData error:', err)
    handleApiError(err, { defaultMessage: '刷新数据失败' })
  }
  finally {
    refreshing.value = false
  }
}

// 跳转到股票详情
function goToStockDetail(ticker: string) {
  router.push(`/stocks/${ticker}`)
}

// 跳转到股票列表
function goToStocksList() {
  router.push('/stocks/list')
}

// 格式化数字
function formatNumber(value: number): string {
  return new Intl.NumberFormat('zh-CN').format(value)
}

// 格式化日期
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

// 格式化市值
function formatMarketCap(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  if (value >= 1e12)
    return `$${(value / 1e12).toFixed(2)}T`
  if (value >= 1e9)
    return `$${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6)
    return `$${(value / 1e6).toFixed(2)}M`
  return `$${value.toFixed(2)}`
}

// 获取市场类型的 Badge 样式
function getMarketTypeVariant(marketType?: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (!marketType)
    return 'outline'
  if (marketType.includes('A股'))
    return 'destructive'
  if (marketType.includes('港股'))
    return 'secondary'
  if (marketType.includes('美股'))
    return 'default'
  return 'outline'
}

// 初始化加载
onMounted(() => {
  loadDashboardData()
})
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <!-- 页面头部 -->
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-2xl font-bold tracking-tight">
          Stock Dashboard
        </h2>
        <p class="text-muted-foreground">
          股票模块统计数据和最近更新
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button
          variant="outline"
          :disabled="loading || refreshing"
          @click="refreshData"
        >
          <Icon
            :name="refreshing ? 'lucide:loader-2' : 'lucide:refresh-cw'"
            :class="['h-4 w-4 mr-2', refreshing && 'animate-spin']"
          />
          刷新
        </Button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-12">
      <Icon name="lucide:loader-2" class="h-8 w-8 mb-4 text-muted-foreground animate-spin" />
      <p class="text-muted-foreground">加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
      <Icon name="lucide:alert-circle" class="h-12 w-12 mb-4 text-destructive" />
      <p class="text-destructive mb-4">{{ error }}</p>
      <Button variant="outline" @click="loadDashboardData">
        <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
        重试
      </Button>
    </div>

    <!-- Dashboard 内容 -->
    <template v-else-if="dashboardData">
      <main class="flex flex-1 flex-col gap-4 md:gap-8">
        <!-- 统计数据卡片 -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <!-- Total Stocks -->
          <Card>
            <CardHeader>
              <CardDescription>Total Stocks</CardDescription>
              <CardTitle class="text-2xl font-semibold tabular-nums">
                <NumberFlow :value="dashboardData.stats.totalStocks" />
              </CardTitle>
              <CardAction>
                <Badge variant="outline">
                  <BarChart3 class="h-3 w-3 mr-1" />
                  股票
                </Badge>
              </CardAction>
            </CardHeader>
            <CardFooter class="flex-col items-start gap-1.5 text-sm">
              <div class="line-clamp-1 flex gap-2 font-medium">
                股票总数
              </div>
            </CardFooter>
          </Card>

          <!-- A股 -->
          <Card>
            <CardHeader>
              <CardDescription>A股</CardDescription>
              <CardTitle class="text-2xl font-semibold tabular-nums">
                <NumberFlow :value="dashboardData.stats.aStockCount" />
              </CardTitle>
              <CardAction>
                <Badge variant="destructive" class="text-xs">
                  <Building2 class="h-3 w-3 mr-1" />
                  A股
                </Badge>
              </CardAction>
            </CardHeader>
            <CardFooter class="flex-col items-start gap-1.5 text-sm">
              <div class="line-clamp-1 flex gap-2 font-medium">
                中国A股市场
              </div>
            </CardFooter>
          </Card>

          <!-- 美股 -->
          <Card>
            <CardHeader>
              <CardDescription>美股</CardDescription>
              <CardTitle class="text-2xl font-semibold tabular-nums">
                <NumberFlow :value="dashboardData.stats.usStockCount" />
              </CardTitle>
              <CardAction>
                <Badge variant="default" class="text-xs">
                  <Globe class="h-3 w-3 mr-1" />
                  美股
                </Badge>
              </CardAction>
            </CardHeader>
            <CardFooter class="flex-col items-start gap-1.5 text-sm">
              <div class="line-clamp-1 flex gap-2 font-medium">
                美国股票市场
              </div>
            </CardFooter>
          </Card>

          <!-- 港股 -->
          <Card>
            <CardHeader>
              <CardDescription>港股</CardDescription>
              <CardTitle class="text-2xl font-semibold tabular-nums">
                <NumberFlow :value="dashboardData.stats.hkStockCount" />
              </CardTitle>
              <CardAction>
                <Badge variant="secondary" class="text-xs">
                  <Building2 class="h-3 w-3 mr-1" />
                  港股
                </Badge>
              </CardAction>
            </CardHeader>
            <CardFooter class="flex-col items-start gap-1.5 text-sm">
              <div class="line-clamp-1 flex gap-2 font-medium">
                香港股票市场
              </div>
            </CardFooter>
          </Card>

          <!-- 数据源 -->
          <Card>
            <CardHeader>
              <CardDescription>数据源</CardDescription>
              <CardTitle class="text-2xl font-semibold tabular-nums">
                <NumberFlow :value="dashboardData.stats.providerCount" />
              </CardTitle>
              <CardAction>
                <Badge variant="outline" class="text-xs">
                  <Database class="h-3 w-3 mr-1" />
                  数据源
                </Badge>
              </CardAction>
            </CardHeader>
            <CardFooter class="flex-col items-start gap-1.5 text-sm">
              <div class="line-clamp-1 flex gap-2 font-medium">
                支持的数据源个数
              </div>
            </CardFooter>
          </Card>

          <!-- 上次全量更新 -->
          <Card v-if="dashboardData.stats.lastFullUpdateTime">
            <CardHeader>
              <CardDescription>上次全量更新</CardDescription>
              <CardTitle class="text-base font-semibold tabular-nums break-words">
                {{ formatDate(dashboardData.stats.lastFullUpdateTime) }}
              </CardTitle>
              <CardAction>
                <Badge variant="outline" class="text-xs">
                  <Clock class="h-3 w-3 mr-1" />
                  更新时间
                </Badge>
              </CardAction>
            </CardHeader>
            <CardFooter class="flex-col items-start gap-1.5 text-sm">
              <div class="line-clamp-1 flex gap-2 font-medium">
                全量数据更新时间
              </div>
            </CardFooter>
          </Card>
        </div>

        <!-- 最近 Stocks 列表 -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle>最近更新的股票</CardTitle>
                <CardDescription>
                  最近更新的 5 只股票
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" @click="goToStocksList">
                查看全部
                <Icon name="lucide:arrow-right" class="h-4 w-4 ml-2" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <!-- 空状态 -->
            <div v-if="dashboardData.recentStocks.length === 0" class="py-8 text-center">
              <Icon name="lucide:inbox" class="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p class="text-muted-foreground mb-4">暂无股票数据</p>
              <Button variant="outline" @click="goToStocksList">
                前往股票列表
              </Button>
            </div>

            <!-- 股票列表 -->
            <div v-else class="space-y-2">
              <div
                v-for="stock in dashboardData.recentStocks"
                :key="stock.ticker"
                class="flex items-center justify-between p-3 rounded-lg border hover:bg-accent cursor-pointer transition-colors"
                @click="goToStockDetail(stock.ticker)"
              >
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold">{{ stock.ticker }}</span>
                    <Badge
                      v-if="stock.market_type"
                      :variant="getMarketTypeVariant(stock.market_type)"
                      class="text-xs"
                    >
                      {{ stock.market_type }}
                    </Badge>
                  </div>
                  <div class="text-sm text-muted-foreground">
                    {{ stock.name || '-' }}
                  </div>
                  <div class="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    <span v-if="stock.price">
                      价格: ${{ formatNumber(stock.price) }}
                    </span>
                    <span v-if="stock.market_cap">
                      市值: {{ formatMarketCap(stock.market_cap) }}
                    </span>
                    <span v-if="stock.last_updated">
                      更新: {{ formatDate(stock.last_updated) }}
                    </span>
                  </div>
                </div>
                <Icon name="lucide:chevron-right" class="h-5 w-5 text-muted-foreground" />
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </template>
  </div>
</template>
