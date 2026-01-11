<script setup lang="ts">
import type { Stock, StocksQueryParams, PaginatedResponse } from '~/api/types'
import { useStocksService } from '~/composables/useApi'
import { handleApiError } from '~/composables/useApiError'
import { toast } from 'vue-sonner'

const stocksService = useStocksService()
const router = useRouter()

// 数据状态
const stocks = ref<Stock[]>([])
const pagination = ref({
  total: 0,
  page: 1,
  page_size: 20,
  total_pages: 0,
})
const loading = ref(false)
const error = ref<string | null>(null)

// 查询参数
const queryParams = ref<StocksQueryParams>({
  page: 1,
  page_size: 20,
})

// 搜索和筛选
const searchQuery = ref('')
const selectedMarket = ref<string>('')
const selectedMarketType = ref<string>('')
const selectedSector = ref<string>('')

// 排序
const sortBy = ref<'last_updated' | 'market_cap' | null>(null)
const sortOrder = ref<'asc' | 'desc'>('desc')

// 批量选择
const selectedStocks = ref<Set<string>>(new Set())
const isAllSelected = computed(() => {
  return stocks.value.length > 0 && selectedStocks.value.size === stocks.value.length
})
const isIndeterminate = computed(() => {
  return selectedStocks.value.size > 0 && selectedStocks.value.size < stocks.value.length
})

// 批量操作状态
const batchUpdating = ref(false)
const batchDeleting = ref(false)
const showDeleteDialog = ref(false)

// 加载股票列表
async function loadStocks() {
  loading.value = true
  error.value = null
  try {
    // 构建查询参数
    const params: StocksQueryParams = {
      page: queryParams.value.page,
      page_size: queryParams.value.page_size,
    }

    // 搜索：如果搜索框有值，尝试按 ticker 或 name 搜索
    if (searchQuery.value.trim()) {
      // 如果搜索内容看起来像股票代码（纯字母或字母+数字），按 ticker 搜索
      if (/^[A-Za-z0-9]+$/.test(searchQuery.value.trim())) {
        params.ticker = searchQuery.value.trim()
      } else {
        // 否则按 name 搜索
        params.name = searchQuery.value.trim()
      }
    }

    // 筛选
    if (selectedMarket.value) {
      params.market = selectedMarket.value
    }
    if (selectedMarketType.value) {
      params.market_type = selectedMarketType.value
    }
    if (selectedSector.value) {
      params.sector = selectedSector.value
    }

    const response: PaginatedResponse<Stock> = await stocksService.getStocks(params)
    stocks.value = response.items || []
    pagination.value = {
      total: response.total || 0,
      page: response.page || 1,
      page_size: response.page_size || 20,
      total_pages: response.total_pages || 0,
    }

    // 客户端排序
    if (sortBy.value) {
      stocks.value.sort((a, b) => {
        let aValue: any = a[sortBy.value!]
        let bValue: any = b[sortBy.value!]

        // 处理日期排序
        if (sortBy.value === 'last_updated') {
          aValue = aValue ? new Date(aValue).getTime() : 0
          bValue = bValue ? new Date(bValue).getTime() : 0
        }

        // 处理数字排序
        if (sortBy.value === 'market_cap') {
          aValue = aValue || 0
          bValue = bValue || 0
        }

        if (sortOrder.value === 'asc') {
          return aValue > bValue ? 1 : aValue < bValue ? -1 : 0
        } else {
          return aValue < bValue ? 1 : aValue > bValue ? -1 : 0
        }
      })
    }

    // 清空选择
    selectedStocks.value.clear()
  } catch (err) {
    console.error('loadStocks error:', err)
    error.value = '无法加载股票列表'
    handleApiError(err, { defaultMessage: '无法加载股票列表' })
  } finally {
    loading.value = false
  }
}

// 搜索处理
function handleSearch() {
  queryParams.value.page = 1
  loadStocks()
}

// 筛选处理
function handleFilter() {
  queryParams.value.page = 1
  loadStocks()
}

// 排序处理
function handleSort(column: 'last_updated' | 'market_cap') {
  if (sortBy.value === column) {
    // 切换排序顺序
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    // 设置新的排序列
    sortBy.value = column
    sortOrder.value = 'desc'
  }
  loadStocks()
}

// 分页处理
function handlePageChange(page: number) {
  queryParams.value.page = page
  loadStocks()
}

function handlePageSizeChange(pageSize: number) {
  queryParams.value.page_size = pageSize
  queryParams.value.page = 1
  loadStocks()
}

// 批量选择
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedStocks.value.clear()
  } else {
    stocks.value.forEach(stock => selectedStocks.value.add(stock.ticker))
  }
}

function toggleSelect(ticker: string) {
  if (selectedStocks.value.has(ticker)) {
    selectedStocks.value.delete(ticker)
  } else {
    selectedStocks.value.add(ticker)
  }
}

// 批量更新
async function batchUpdate() {
  if (selectedStocks.value.size === 0) {
    toast.warning('请先选择要更新的股票')
    return
  }

  batchUpdating.value = true
  try {
    const tickers = Array.from(selectedStocks.value)
    let successCount = 0
    let failCount = 0

    for (const ticker of tickers) {
      try {
        await stocksService.updateStock(ticker)
        successCount++
      } catch (err) {
        console.error(`Failed to update ${ticker}:`, err)
        failCount++
      }
    }

    toast.success(`批量更新完成：成功 ${successCount}，失败 ${failCount}`)
    selectedStocks.value.clear()
    await loadStocks()
  } catch (err) {
    handleApiError(err, { defaultMessage: '批量更新失败' })
  } finally {
    batchUpdating.value = false
  }
}

// 批量删除
function openDeleteDialog() {
  if (selectedStocks.value.size === 0) {
    toast.warning('请先选择要删除的股票')
    return
  }
  showDeleteDialog.value = true
}

async function confirmDelete() {
  batchDeleting.value = true
  try {
    const tickers = Array.from(selectedStocks.value)
    let successCount = 0
    let failCount = 0

    for (const ticker of tickers) {
      try {
        await stocksService.deleteStock(ticker)
        successCount++
      } catch (err) {
        console.error(`Failed to delete ${ticker}:`, err)
        failCount++
      }
    }

    toast.success(`批量删除完成：成功 ${successCount}，失败 ${failCount}`)
    selectedStocks.value.clear()
    showDeleteDialog.value = false
    await loadStocks()
  } catch (err) {
    handleApiError(err, { defaultMessage: '批量删除失败' })
  } finally {
    batchDeleting.value = false
  }
}

// 跳转到股票详情页
function goToStockDetail(ticker: string) {
  router.push(`/stocks/${ticker}`)
}

// 格式化数字
function formatNumber(value?: number): string {
  if (value === undefined || value === null)
    return '-'
  return new Intl.NumberFormat('zh-CN', {
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
  return `$${value.toFixed(2)}`
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
  } catch {
    return dateString
  }
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

// 获取唯一的市场类型列表
const marketTypes = computed(() => {
  const types = new Set<string>()
  stocks.value.forEach(stock => {
    if (stock.market_type) {
      types.add(stock.market_type)
    }
  })
  return Array.from(types).sort()
})

// 获取唯一的行业列表
const sectors = computed(() => {
  const sectorSet = new Set<string>()
  stocks.value.forEach(stock => {
    if (stock.sector) {
      sectorSet.add(stock.sector)
    }
  })
  return Array.from(sectorSet).sort()
})

// 初始化加载
onMounted(() => {
  loadStocks()
})
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <!-- 页面头部 -->
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-2xl font-bold tracking-tight">
          股票列表
        </h2>
        <p class="text-muted-foreground">
          查看和管理股票信息
        </p>
      </div>
      <div class="flex gap-2">
        <Button
          v-if="selectedStocks.size > 0"
          variant="outline"
          :disabled="batchUpdating"
          @click="batchUpdate"
        >
          <Icon
            :name="batchUpdating ? 'lucide:loader-2' : 'lucide:refresh-cw'"
            :class="['h-4 w-4 mr-2', batchUpdating && 'animate-spin']"
          />
          批量更新 ({{ selectedStocks.size }})
        </Button>
        <Button
          v-if="selectedStocks.size > 0"
          variant="destructive"
          :disabled="batchDeleting"
          @click="openDeleteDialog"
        >
          <Icon name="lucide:trash-2" class="h-4 w-4 mr-2" />
          批量删除 ({{ selectedStocks.size }})
        </Button>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <Card>
      <CardContent class="pt-6">
        <div class="flex flex-wrap gap-4">
          <!-- 搜索框 -->
          <div class="flex-1 min-w-[200px] relative">
            <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              v-model="searchQuery"
              placeholder="搜索股票代码或名称..."
              class="pl-9"
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- 市场类型筛选 -->
          <Select v-model="selectedMarketType" placeholder="市场类型" @update:model-value="handleFilter">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="市场类型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">
                全部
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

          <!-- 行业筛选 -->
          <Select v-model="selectedSector" placeholder="行业" @update:model-value="handleFilter">
            <SelectTrigger class="w-[150px]">
              <SelectValue placeholder="行业" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">
                全部
              </SelectItem>
              <SelectItem
                v-for="sector in sectors"
                :key="sector"
                :value="sector"
              >
                {{ sector }}
              </SelectItem>
            </SelectContent>
          </Select>

          <!-- 搜索按钮 -->
          <Button @click="handleSearch">
            <Icon name="lucide:search" class="h-4 w-4 mr-2" />
            搜索
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- 股票列表 -->
    <Card>
      <CardContent class="p-0">
        <!-- 加载状态 -->
        <div v-if="loading" class="p-8 text-center">
          <Spinner class="mx-auto mb-4" />
          <p class="text-muted-foreground">加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="p-8 text-center">
          <Icon name="lucide:alert-circle" class="h-12 w-12 mx-auto mb-4 text-destructive" />
          <p class="text-destructive mb-4">{{ error }}</p>
          <Button variant="outline" @click="loadStocks">
            <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
            重试
          </Button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="stocks.length === 0" class="p-8 text-center">
          <Icon name="lucide:inbox" class="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <p class="text-muted-foreground mb-4">暂无股票数据</p>
          <Button variant="outline" @click="loadStocks">
            <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
            刷新
          </Button>
        </div>

        <!-- 表格 -->
        <Table v-else>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[50px]">
                <Checkbox
                  :checked="isAllSelected"
                  :indeterminate="isIndeterminate"
                  @update:checked="toggleSelectAll"
                />
              </TableHead>
              <TableHead class="cursor-pointer" @click="handleSort('last_updated')">
                <div class="flex items-center gap-2">
                  股票代码
                  <Icon
                    v-if="sortBy === 'last_updated'"
                    :name="sortOrder === 'asc' ? 'lucide:arrow-up' : 'lucide:arrow-down'"
                    class="h-4 w-4"
                  />
                </div>
              </TableHead>
              <TableHead>股票名称</TableHead>
              <TableHead>市场类型</TableHead>
              <TableHead>行业</TableHead>
              <TableHead class="cursor-pointer text-right" @click="handleSort('market_cap')">
                <div class="flex items-center justify-end gap-2">
                  市值
                  <Icon
                    v-if="sortBy === 'market_cap'"
                    :name="sortOrder === 'asc' ? 'lucide:arrow-up' : 'lucide:arrow-down'"
                    class="h-4 w-4"
                  />
                </div>
              </TableHead>
              <TableHead>价格</TableHead>
              <TableHead>最后更新</TableHead>
              <TableHead class="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow
              v-for="stock in stocks"
              :key="stock.ticker"
              class="cursor-pointer"
              @click="goToStockDetail(stock.ticker)"
            >
              <TableCell @click.stop>
                <Checkbox
                  :checked="selectedStocks.has(stock.ticker)"
                  @update:checked="() => toggleSelect(stock.ticker)"
                />
              </TableCell>
              <TableCell class="font-medium">
                {{ stock.ticker }}
              </TableCell>
              <TableCell>{{ stock.name || '-' }}</TableCell>
              <TableCell>
                <Badge
                  v-if="stock.market_type"
                  :variant="getMarketTypeVariant(stock.market_type)"
                >
                  {{ stock.market_type }}
                </Badge>
                <span v-else>-</span>
              </TableCell>
              <TableCell>{{ stock.sector || '-' }}</TableCell>
              <TableCell class="text-right">
                {{ formatMarketCap(stock.market_cap) }}
              </TableCell>
              <TableCell>{{ formatNumber(stock.price) }}</TableCell>
              <TableCell>{{ formatDate(stock.last_updated) }}</TableCell>
              <TableCell class="text-right" @click.stop>
                <div class="flex items-center justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    @click="goToStockDetail(stock.ticker)"
                  >
                    <Icon name="lucide:eye" class="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>

    <!-- 分页 -->
    <div v-if="!loading && !error && stocks.length > 0" class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-sm text-muted-foreground">每页显示：</span>
        <Select
          :model-value="pagination.page_size.toString()"
          @update:model-value="(value) => handlePageSizeChange(Number(value))"
        >
          <SelectTrigger class="w-[100px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="20">20</SelectItem>
            <SelectItem value="50">50</SelectItem>
            <SelectItem value="100">100</SelectItem>
          </SelectContent>
        </Select>
        <span class="text-sm text-muted-foreground">
          共 {{ pagination.total }} 条，第 {{ pagination.page }} / {{ pagination.total_pages }} 页
        </span>
      </div>
      <Pagination
        v-slot="{ page }"
        :total="pagination.total"
        :sibling-count="1"
        :default-page="pagination.page"
        :page-size="pagination.page_size"
        @update:page="handlePageChange"
      >
        <PaginationContent v-slot="{ items }" class="flex items-center gap-1">
          <PaginationFirst />
          <PaginationPrevious />

          <template v-for="(item, index) in items" :key="index">
            <PaginationItem
              v-if="item.type === 'page'"
              :value="item.value"
              as-child
            >
              <Button
                class="h-9 w-9 p-0"
                :variant="item.value === page ? 'default' : 'outline'"
                @click="handlePageChange(item.value)"
              >
                {{ item.value }}
              </Button>
            </PaginationItem>
            <PaginationEllipsis v-else :key="item.type" :index="index" />
          </template>

          <PaginationNext />
          <PaginationLast />
        </PaginationContent>
      </Pagination>
    </div>

    <!-- 批量删除确认对话框 -->
    <AlertDialog v-model:open="showDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认删除</AlertDialogTitle>
          <AlertDialogDescription>
            确定要删除选中的 {{ selectedStocks.size }} 只股票吗？此操作无法撤销。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="batchDeleting">
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            :disabled="batchDeleting"
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            @click="confirmDelete"
          >
            <Icon
              v-if="batchDeleting"
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
