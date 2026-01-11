<script setup lang="ts">
import type { Stock } from '~/api/types'
import { ApiError } from '~/api/types'
import { useStocksService } from '~/composables/useApi'
import { handleApiError } from '~/composables/useApiError'
import { toast } from 'vue-sonner'

const route = useRoute()
const router = useRouter()
const stocksService = useStocksService()

const ticker = computed(() => route.params.ticker as string)
const stock = ref<Stock | null>(null)
const loading = ref(false)
const updating = ref(false)
const deleting = ref(false)
const showDeleteDialog = ref(false)
const notFound = ref(false) // 股票不存在标志

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
    const isNotFound = error instanceof ApiError && error.code === 404
      || error?.code === 404
      || error?.status === 404
      || (error?.data && error.data.code === 404)
      || (error?.response?.status === 404)
    
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

// 格式化数字
function formatNumber(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN', {
    maximumFractionDigits: 2,
  }).format(value)
}

// 格式化货币
function formatCurrency(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
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
  return formatCurrency(value)
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

// 获取市场类型的 Badge 样式
function getMarketTypeVariant(marketType?: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (!marketType)
    return 'outline'
  if (marketType.includes('A股'))
    return 'destructive' // 红色表示 A 股
  if (marketType.includes('港股'))
    return 'secondary' // 灰色表示港股
  if (marketType.includes('美股'))
    return 'default' // 默认样式表示美股
  return 'outline'
}

// 数据源链接映射
const dataSourceLinks: Record<string, string> = {
  akshare: 'https://github.com/akfamily/akshare',
  yfinance: 'https://github.com/ranaroussi/yfinance',
  easyquotation: 'https://github.com/shidenggui/easyquotation',
  tushare: 'https://tushare.pro/',
  'iex-cloud': 'https://iexcloud.io/',
  'alpha-vantage': 'https://www.alphavantage.co/',
}

// 获取数据源链接
function getDataSourceUrl(dataSource?: string): string | null {
  if (!dataSource)
    return null
  // 处理可能的变体名称
  const normalized = dataSource.toLowerCase().replace(/_/g, '-')
  return dataSourceLinks[normalized] || dataSourceLinks[dataSource.toLowerCase()] || null
}

onMounted(() => {
  loadStock()
})
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <!-- 页面头部 -->
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" @click="goBack">
          <Icon name="lucide:arrow-left" class="h-4 w-4" />
        </Button>
        <div>
          <h2 class="text-2xl font-bold tracking-tight">
            {{ stock?.name || ticker }}
          </h2>
          <div class="flex flex-wrap items-center gap-2 mt-1">
            <p class="text-muted-foreground">
              {{ ticker }}
            </p>
            <!-- 市场类型标签 -->
            <Badge
              v-if="stock?.market_type"
              :variant="getMarketTypeVariant(stock.market_type)"
            >
              {{ stock.market_type }}
            </Badge>
            <!-- 国家标签 -->
            <Badge
              v-if="stock?.country"
              variant="outline"
            >
              {{ stock.country }}
            </Badge>
            <!-- 市场标签 -->
            <Badge
              v-if="stock?.market"
              variant="secondary"
            >
              {{ stock.market }}
            </Badge>
          </div>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          variant="outline"
          :disabled="loading || updating || notFound"
          @click="updateStock"
        >
          <Icon
            :name="updating ? 'lucide:loader-2' : 'lucide:refresh-cw'"
            :class="['h-4 w-4 mr-2', updating && 'animate-spin']"
          />
          更新数据
        </Button>
        <Button
          variant="destructive"
          :disabled="loading || deleting || notFound"
          @click="openDeleteDialog"
        >
          <Icon name="lucide:trash-2" class="h-4 w-4 mr-2" />
          删除
        </Button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="space-y-4">
      <Card>
        <CardHeader>
          <Skeleton class="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-full" />
            <Skeleton class="h-4 w-3/4" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <Skeleton class="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-2 gap-4">
            <Skeleton class="h-20 w-full" />
            <Skeleton class="h-20 w-full" />
            <Skeleton class="h-20 w-full" />
            <Skeleton class="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- 股票不存在提示 -->
    <Card v-else-if="!loading && notFound">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Icon name="lucide:alert-circle" class="h-5 w-5 text-destructive" />
          股票不存在
        </CardTitle>
        <CardDescription>
          未找到股票代码为 "{{ ticker }}" 的股票信息
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="space-y-4">
          <p class="text-muted-foreground">
            可能的原因：
          </p>
          <ul class="list-disc list-inside space-y-2 text-muted-foreground">
            <li>股票代码输入错误</li>
            <li>该股票尚未添加到系统中</li>
            <li>该股票可能已被删除</li>
          </ul>
          <div class="flex gap-2 pt-4">
            <Button variant="outline" @click="goBack">
              <Icon name="lucide:arrow-left" class="h-4 w-4 mr-2" />
              返回
            </Button>
            <Button @click="loadStock">
              <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
              重新加载
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- 股票详情 -->
    <template v-else-if="stock">
      <!-- 基本信息 -->
      <Card>
        <CardHeader>
          <CardTitle>基本信息</CardTitle>
          <CardDescription>
            股票的基本信息和标识
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <Label class="text-muted-foreground">股票代码</Label>
              <p class="text-lg font-semibold">{{ stock.ticker }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">股票名称</Label>
              <p class="text-lg font-semibold">{{ stock.name || '-' }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">行业</Label>
              <p class="text-lg">{{ stock.industry || '-' }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">板块</Label>
              <p class="text-lg">{{ stock.sector || '-' }}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 财务指标 -->
      <Card>
        <CardHeader>
          <CardTitle>财务指标</CardTitle>
          <CardDescription>
            股票的价格、市值等财务数据
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="space-y-1">
              <Label class="text-muted-foreground">当前价格</Label>
              <p class="text-2xl font-bold">{{ formatCurrency(stock.price) }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">市值</Label>
              <p class="text-2xl font-bold">{{ formatMarketCap(stock.market_cap) }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">成交量</Label>
              <p class="text-2xl font-bold">{{ formatNumber(stock.volume) }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">市值（原始值）</Label>
              <p class="text-lg">{{ formatCurrency(stock.market_cap) }}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- 数据源信息 -->
      <Card>
        <CardHeader>
          <CardTitle>数据源信息</CardTitle>
          <CardDescription>
            数据的来源和更新时间
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="space-y-1">
              <Label class="text-muted-foreground">数据源来源</Label>
              <div class="text-lg">
                <a
                  v-if="stock.data_source && getDataSourceUrl(stock.data_source)"
                  :href="getDataSourceUrl(stock.data_source)!"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:underline inline-flex items-center gap-1"
                >
                  {{ stock.data_source }}
                  <Icon name="lucide:external-link" class="h-4 w-4" />
                </a>
                <span v-else>{{ stock.data_source || '-' }}</span>
              </div>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">创建时间</Label>
              <p class="text-lg">{{ formatDate(stock.created_at) }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">最后更新时间</Label>
              <p class="text-lg">{{ formatDate(stock.last_updated) }}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </template>

    <!-- 删除确认对话框 -->
    <AlertDialog v-model:open="showDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认删除</AlertDialogTitle>
          <AlertDialogDescription>
            确定要删除股票 "<strong>{{ stock?.name || ticker }}</strong>" ({{ ticker }}) 吗？此操作无法撤销。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="deleting">
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            :disabled="deleting"
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            @click="confirmDelete"
          >
            <Icon
              v-if="deleting"
              name="lucide:loader-2"
              class="mr-2 h-4 w-4 animate-spin"
            />
            <Icon
              v-else
              name="lucide:trash-2"
              class="mr-2 h-4 w-4"
            />
            删除
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
