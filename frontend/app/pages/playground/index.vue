<script setup lang="ts">
const services = [
  {
    name: 'Node.js Service',
    description: 'Nest.js + Bun 后端服务',
    icon: 'i-lucide-server',
    link: '/playground/node',
    color: 'bg-green-500/10 text-green-500',
  },
  {
    name: 'Python Service',
    description: 'FastAPI 后端服务',
    icon: 'i-lucide-code',
    link: '/playground/python',
    color: 'bg-blue-500/10 text-blue-500',
  },
  {
    name: 'Rust Service',
    description: 'Axum 后端服务',
    icon: 'i-lucide-cog',
    link: '/playground/rust',
    color: 'bg-orange-500/10 text-orange-500',
  },
]
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <div class="flex flex-col gap-2">
      <h2 class="text-2xl font-bold tracking-tight">
        Playground
      </h2>
      <p class="text-muted-foreground">
        测试和访问三个后端服务的统一入口
      </p>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card
        v-for="service in services"
        :key="service.name"
        class="cursor-pointer transition-all hover:shadow-md"
        @click="navigateTo(service.link)"
      >
        <CardHeader>
          <div class="flex items-center gap-3">
            <div :class="['p-2 rounded-lg', service.color]">
              <Icon :name="service.icon" class="h-6 w-6" />
            </div>
            <CardTitle>{{ service.name }}</CardTitle>
          </div>
          <CardDescription>
            {{ service.description }}
          </CardDescription>
        </CardHeader>
        <CardFooter>
          <Button variant="outline" class="w-full">
            进入测试页面
            <Icon name="lucide:arrow-right" class="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
