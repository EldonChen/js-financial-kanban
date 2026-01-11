<script setup lang="ts">
const route = useRoute()

function setLinks() {
  // 使用 route.path 而不是 route.fullPath，避免包含查询参数
  const path = route.path
  
  if (path === '/') {
    return [{ title: 'Home', href: '/' }]
  }

  // 移除查询参数部分（如果有的话）
  const pathWithoutQuery = path.split('?')[0]
  const segments = pathWithoutQuery.split('/').filter(item => item !== '')

  const breadcrumbs = segments.map((item, index) => {
    // 移除 URL 编码的查询参数（如果路径段包含 ? 或 &）
    const cleanItem = item.split('?')[0].split('&')[0]
    const str = decodeURIComponent(cleanItem).replace(/-/g, ' ')
    const title = str
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')

    return {
      title,
      href: `/${segments.slice(0, index + 1).join('/')}`,
    }
  })

  return [{ title: 'Home', href: '/' }, ...breadcrumbs]
}

const links = ref<{
  title: string
  href: string
}[]>(setLinks())

// 监听 path 变化而不是 fullPath，避免查询参数变化时更新面包屑
watch(() => route.path, (val) => {
  if (val) {
    links.value = setLinks()
  }
})
</script>

<template>
  <header class="sticky top-0 md:peer-data-[variant=inset]:top-2 z-10 h-(--header-height) flex items-center gap-4 border-b bg-background px-4 md:px-6 md:rounded-tl-xl md:rounded-tr-xl">
    <div class="w-full flex items-center gap-4 h-4">
      <SidebarTrigger />
      <Separator orientation="vertical" />
      <BaseBreadcrumbCustom :links="links" />
    </div>
    <div class="ml-auto">
      <slot />
    </div>
  </header>
</template>

<style scoped>

</style>
