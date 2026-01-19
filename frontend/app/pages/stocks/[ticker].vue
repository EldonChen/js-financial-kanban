<script setup lang="ts">
import StockDeleteDialog from '~/components/stocks/StockDeleteDialog.vue'
import StockDetailHeader from '~/components/stocks/StockDetailHeader.vue'
import StockHistoryTab from '~/components/stocks/StockHistoryTab.vue'
import StockInfoTab from '~/components/stocks/StockInfoTab.vue'
import StockNotFound from '~/components/stocks/StockNotFound.vue'
import { useStockDetail } from '~/composables/useStockDetail'

const route = useRoute()
const ticker = computed(() => route.params.ticker as string)

// 使用股票详情 composable
const {
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
} = useStockDetail(ticker)

// Tab 切换
const activeTab = ref('info')

onMounted(() => {
  loadStock()
  // 如果 URL 中有 tab 参数，切换到对应的 tab
  const tab = route.query.tab as string
  if (tab && ['info', 'history'].includes(tab)) {
    activeTab.value = tab
  }
})
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <!-- 页面头部 -->
    <StockDetailHeader
      :stock="stock"
      :ticker="ticker"
      :loading="loading"
      :updating="updating"
      :deleting="deleting"
      :not-found="notFound"
      @update="updateStock"
      @delete="openDeleteDialog"
      @go-back="goBack"
    />

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
    <StockNotFound
      v-else-if="!loading && notFound"
      :ticker="ticker"
      @go-back="goBack"
      @reload="loadStock"
    />

    <!-- 股票详情 -->
    <template v-else-if="stock">
      <Tabs v-model="activeTab" class="w-full">
        <TabsList class="grid w-full grid-cols-2">
          <TabsTrigger value="info">
            基本信息
          </TabsTrigger>
          <TabsTrigger value="history">
            历史数据
          </TabsTrigger>
        </TabsList>

        <!-- 基本信息 Tab -->
        <TabsContent value="info">
          <StockInfoTab :stock="stock" />
        </TabsContent>

        <!-- 历史数据 Tab -->
        <TabsContent value="history">
          <StockHistoryTab :ticker="ticker" />
        </TabsContent>
      </Tabs>
    </template>

    <!-- 删除确认对话框 -->
    <StockDeleteDialog
      v-model:open="showDeleteDialog"
      :stock-name="stock?.name"
      :ticker="ticker"
      :deleting="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>
