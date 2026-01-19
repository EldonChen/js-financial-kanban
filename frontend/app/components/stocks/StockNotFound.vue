<script setup lang="ts">
interface Props {
  ticker: string
}

interface Emits {
  (e: 'go-back'): void
  (e: 'reload'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()
</script>

<template>
  <Card>
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
          <Button variant="outline" @click="emit('go-back')">
            <Icon name="lucide:arrow-left" class="h-4 w-4 mr-2" />
            返回
          </Button>
          <Button @click="emit('reload')">
            <Icon name="lucide:refresh-cw" class="h-4 w-4 mr-2" />
            重新加载
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>

