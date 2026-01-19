<script setup lang="ts">
import type { Stock } from '~/api/types'

interface Props {
  stock: Stock
}

defineProps<Props>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>基本信息</CardTitle>
      <CardDescription> 股票的基本信息和标识 </CardDescription>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-1">
          <Label class="text-muted-foreground">股票代码</Label>
          <p class="text-lg font-semibold">
            {{ stock.ticker }}
          </p>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">股票名称</Label>
          <p class="text-lg font-semibold">
            {{ stock.name || "-" }}
          </p>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">行业</Label>
          <p class="text-lg">
            {{ stock.industry || "-" }}
          </p>
        </div>
        <div class="space-y-1">
          <Label class="text-muted-foreground">板块</Label>
          <p class="text-lg">
            {{ stock.sector || "-" }}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

