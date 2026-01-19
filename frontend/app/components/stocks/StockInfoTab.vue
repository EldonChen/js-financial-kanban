<script setup lang="ts">
import type { Stock } from '~/api/types'
import StockBasicInfo from './StockBasicInfo.vue'
import StockFinancialMetrics from './StockFinancialMetrics.vue'
import StockDataSourceInfo from './StockDataSourceInfo.vue'

interface Props {
  stock: Stock
}

defineProps<Props>()
</script>

<template>
  <div class="space-y-4">
    <StockBasicInfo :stock="stock" />
    <StockFinancialMetrics :stock="stock" />
    <StockDataSourceInfo :stock="stock" />
  </div>
</template>

