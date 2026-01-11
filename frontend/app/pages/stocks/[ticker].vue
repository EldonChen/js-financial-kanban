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

// 加载股票详情
async function loadStock() {
  loading.value = true
  try {
    stock.value = await stocksService.getStock(ticker.value)
  }
  catch (error) {
    // 如果股票不存在（404），跳转到 404 页面
    if (error instanceof ApiError && error.code === 404) {
      throw createError({
        statusCode: 404,
        statusMessage: `股票 ${ticker.value} 不存在`,
      })
    }
    handleApiError(error, { defaultMessage: '无法加载股票信息' })
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
          <p class="text-muted-foreground">
            {{ ticker }}
          </p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          variant="outline"
          :disabled="loading || updating"
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
          :disabled="loading || deleting"
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
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
