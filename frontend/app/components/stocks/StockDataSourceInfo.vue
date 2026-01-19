<script setup lang="ts">
import type { Stock } from '~/api/types'
import { formatDate, getDataSourceUrl } from '~/composables/useStockFormatters'

interface Props {
  stock: Stock
}

defineProps<Props>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>数据源信息</CardTitle>
      <CardDescription> 数据的来源和更新时间 </CardDescription>
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
            <span v-else>{{ stock.data_source || "-" }}</span>
          </div>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">创建时间</Label>
          <p class="text-lg">
            {{ formatDate(stock.created_at) }}
          </p>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">最后更新时间</Label>
          <p class="text-lg">
            {{ formatDate(stock.last_updated) }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

