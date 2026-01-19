<script setup lang="ts">
import type { Stock } from '~/api/types'
import { formatCurrency, formatMarketCap, formatNumber } from '~/composables/useStockFormatters'

interface Props {
  stock: Stock
}

defineProps<Props>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>财务指标</CardTitle>
      <CardDescription> 股票的价格、市值等财务数据 </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="space-y-1">
          <Label class="text-muted-foreground">当前价格</Label>
          <p class="text-2xl font-bold">
            {{ formatCurrency(stock.price) }}
          </p>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">市值</Label>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger as-child>
                <p class="text-2xl font-bold cursor-help">
                  {{ formatMarketCap(stock.market_cap) }}
                </p>
              </TooltipTrigger>
              <TooltipContent>
                <p>市值（原始值）：{{ formatCurrency(stock.market_cap) }}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">成交量</Label>
          <p class="text-2xl font-bold">
            {{ formatNumber(stock.volume) }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

