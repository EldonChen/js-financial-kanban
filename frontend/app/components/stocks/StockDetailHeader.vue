<script setup lang="ts">
import type { Stock } from '~/api/types'
import { getMarketTypeVariant } from '~/composables/useStockFormatters'

interface Props {
  stock: Stock | null
  ticker: string
  loading?: boolean
  updating?: boolean
  deleting?: boolean
  notFound?: boolean
}

interface Emits {
  (e: 'update'): void
  (e: 'delete'): void
  (e: 'go-back'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  updating: false,
  deleting: false,
  notFound: false,
})

const emit = defineEmits<Emits>()
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="emit('go-back')">
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
          <Badge v-if="stock?.country" variant="outline">
            {{ stock.country }}
          </Badge>
          <!-- 市场标签 -->
          <Badge v-if="stock?.market" variant="secondary">
            {{ stock.market }}
          </Badge>
        </div>
      </div>
    </div>
    <div class="flex gap-2">
      <Button
        variant="outline"
        :disabled="loading || updating || notFound"
        @click="emit('update')"
      >
        <Icon
          :name="updating ? 'lucide:loader-2' : 'lucide:refresh-cw'"
          class="h-4 w-4 mr-2"
          :class="[updating && 'animate-spin']"
        />
        更新数据
      </Button>
      <Button
        variant="destructive"
        :disabled="loading || deleting || notFound"
        @click="emit('delete')"
      >
        <Icon name="lucide:trash-2" class="h-4 w-4 mr-2" />
        删除
      </Button>
    </div>
  </div>
</template>

