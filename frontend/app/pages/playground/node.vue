<script setup lang="ts">
import type { CreateItemDto, Item } from '~/api/types'
import { toast } from 'vue-sonner'
import { useNodeService } from '~/composables/useApi'
import { handleApiError } from '~/composables/useApiError'
import { usePlaygroundShortcuts } from '~/composables/usePlaygroundShortcuts'

const nodeService = useNodeService()
const searchInputRef = ref<HTMLInputElement | null>(null)

const items = ref<Item[]>([])
const filteredItems = ref<Item[]>([])
const selectedItems = ref<Set<string>>(new Set())
const loading = ref(false)
const creating = ref(false)
const updating = ref(false)
const deleting = ref<string | null>(null)
const batchDeleting = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const showBatchDeleteDialog = ref(false)
const editingItem = ref<Item | null>(null)
const deletingItem = ref<Item | null>(null)
const searchQuery = ref('')

const formData = ref<CreateItemDto>({
  name: '',
  description: '',
  price: undefined,
})

// 加载数据
async function loadItems() {
  loading.value = true
  try {
    items.value = await nodeService.getItems()
    applyFilter()
  }
  catch (error) {
    handleApiError(error, { defaultMessage: '无法加载数据' })
  }
  finally {
    loading.value = false
  }
}

// 应用搜索过滤
function applyFilter() {
  if (!searchQuery.value.trim()) {
    filteredItems.value = items.value
    return
  }

  const query = searchQuery.value.toLowerCase()
  filteredItems.value = items.value.filter(item =>
    item.name.toLowerCase().includes(query)
    || item.description?.toLowerCase().includes(query)
    || item.id.toLowerCase().includes(query),
  )
  // 清除不在过滤结果中的选中项
  selectedItems.value.forEach((id) => {
    if (!filteredItems.value.find(item => item.id === id)) {
      selectedItems.value.delete(id)
    }
  })
}

// 监听搜索查询变化
watch(searchQuery, () => {
  applyFilter()
})

// 全选/取消全选
function toggleSelectAll() {
  if (selectedItems.value.size === filteredItems.value.length) {
    selectedItems.value.clear()
  }
  else {
    filteredItems.value.forEach(item => selectedItems.value.add(item.id))
  }
}

// 切换单个项目选中状态
function toggleSelect(itemId: string) {
  if (selectedItems.value.has(itemId)) {
    selectedItems.value.delete(itemId)
  }
  else {
    selectedItems.value.add(itemId)
  }
}

// 批量删除
async function confirmBatchDelete() {
  if (selectedItems.value.size === 0) {
    return
  }

  batchDeleting.value = true
  const ids = Array.from(selectedItems.value)
  let successCount = 0
  let failCount = 0

  try {
    await Promise.allSettled(
      ids.map(async (id) => {
        try {
          await nodeService.deleteItem(id)
          successCount++
        }
        catch {
          failCount++
        }
      }),
    )

    if (successCount > 0) {
      toast.success(`成功删除 ${successCount} 个项目`)
    }
    if (failCount > 0) {
      toast.error(`删除失败 ${failCount} 个项目`)
    }

    showBatchDeleteDialog.value = false
    selectedItems.value.clear()
    await loadItems()
  }
  catch (error) {
    handleApiError(error, { defaultMessage: '批量删除失败' })
  }
  finally {
    batchDeleting.value = false
  }
}

// 创建项目
async function createItem() {
  if (!formData.value.name.trim()) {
    toast.error('名称不能为空')
    return
  }

  creating.value = true
  try {
    await nodeService.createItem(formData.value)
    toast.success('创建成功')
    showCreateDialog.value = false
    resetForm()
    await loadItems()
  }
  catch (error) {
    handleApiError(error, { defaultMessage: '无法创建项目' })
  }
  finally {
    creating.value = false
  }
}

// 编辑项目
function openEditDialog(item: Item) {
  editingItem.value = item
  formData.value = {
    name: item.name,
    description: item.description || '',
    price: item.price,
  }
  showEditDialog.value = true
}

// 更新项目
async function updateItem() {
  if (!editingItem.value || !formData.value.name.trim()) {
    toast.error('名称不能为空')
    return
  }

  updating.value = true
  try {
    await nodeService.updateItem(editingItem.value.id, formData.value)
    toast.success('更新成功')
    showEditDialog.value = false
    resetForm()
    editingItem.value = null
    await loadItems()
  }
  catch (error) {
    handleApiError(error, { defaultMessage: '无法更新项目' })
  }
  finally {
    updating.value = false
  }
}

// 打开删除确认对话框
function openDeleteDialog(item: Item) {
  deletingItem.value = item
  showDeleteDialog.value = true
}

// 删除项目
async function confirmDelete() {
  if (!deletingItem.value) {
    return
  }

  deleting.value = deletingItem.value.id
  try {
    await nodeService.deleteItem(deletingItem.value.id)
    toast.success('删除成功')
    showDeleteDialog.value = false
    deletingItem.value = null
    await loadItems()
  }
  catch (error) {
    handleApiError(error, { defaultMessage: '无法删除项目' })
  }
  finally {
    deleting.value = null
  }
}

// 重置表单
function resetForm() {
  formData.value = {
    name: '',
    description: '',
    price: undefined,
  }
}

// 键盘快捷键
const { metaSymbol, handleEscape } = usePlaygroundShortcuts({
  onCreate: () => {
    if (!showCreateDialog.value && !showEditDialog.value) {
      showCreateDialog.value = true
    }
  },
  onRefresh: () => {
    if (!loading.value) {
      loadItems()
    }
  },
  onSearch: () => {
    searchInputRef.value?.focus()
  },
})

// Escape 键关闭对话框
onMounted(() => {
  loadItems()

  // 关闭创建对话框
  handleEscape(() => {
    if (showCreateDialog.value && !creating.value) {
      showCreateDialog.value = false
      resetForm()
    }
  })

  // 关闭编辑对话框
  handleEscape(() => {
    if (showEditDialog.value && !updating.value) {
      showEditDialog.value = false
      resetForm()
      editingItem.value = null
    }
  })

  // 关闭删除对话框
  handleEscape(() => {
    if (showDeleteDialog.value && deleting.value === null) {
      showDeleteDialog.value = false
      deletingItem.value = null
    }
  })
})
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 class="text-2xl font-bold tracking-tight">
          Node.js Service
        </h2>
        <p class="text-muted-foreground">
          Nest.js + Bun 后端服务测试页面
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <Button
          v-if="selectedItems.size > 0"
          variant="destructive"
          :disabled="batchDeleting"
          @click="showBatchDeleteDialog = true"
        >
          <Icon name="lucide:trash-2" class="mr-2 h-4 w-4" />
          删除选中 ({{ selectedItems.size }})
        </Button>
        <Button variant="outline" :disabled="loading" @click="loadItems">
          <Icon
            :name="loading ? 'lucide:loader-2' : 'lucide:refresh-cw'"
            class="h-4 w-4" :class="[loading && 'animate-spin']"
          />
        </Button>
        <Button @click="showCreateDialog = true">
          <Icon name="lucide:plus" class="mr-2 h-4 w-4" />
          创建项目
        </Button>
      </div>
    </div>

    <Card>
      <CardHeader>
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex-1">
            <CardTitle>Items 列表</CardTitle>
            <CardDescription class="hidden sm:block">
              显示所有 items，支持创建、更新、删除操作
              <span class="ml-2 text-xs">
                ({{ metaSymbol }}+N 创建, {{ metaSymbol }}+R 刷新, {{ metaSymbol }}+K 搜索)
              </span>
            </CardDescription>
            <CardDescription class="sm:hidden">
              支持创建、更新、删除操作
            </CardDescription>
          </div>
          <div class="w-full md:max-w-sm">
            <div class="relative">
              <Icon name="lucide:search" class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                ref="searchInputRef"
                v-model="searchQuery"
                placeholder="搜索名称、描述或 ID... ({{ metaSymbol }}+K)"
                class="pl-9"
              />
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div v-if="loading" class="space-y-2">
          <Skeleton class="h-12 w-full" />
          <Skeleton class="h-12 w-full" />
          <Skeleton class="h-12 w-full" />
        </div>
        <div v-else-if="items.length === 0" class="flex flex-col items-center justify-center py-8 text-center">
          <Icon name="lucide:inbox" class="h-12 w-12 text-muted-foreground mb-4" />
          <p class="text-muted-foreground">
            暂无数据
          </p>
          <Button variant="outline" class="mt-4" @click="showCreateDialog = true">
            创建第一个项目
          </Button>
        </div>
        <div v-else-if="filteredItems.length === 0" class="flex flex-col items-center justify-center py-8 text-center">
          <Icon name="lucide:search-x" class="h-12 w-12 text-muted-foreground mb-4" />
          <p class="text-muted-foreground">
            未找到匹配的项目
          </p>
          <Button variant="outline" class="mt-4" @click="searchQuery = ''">
            清除搜索
          </Button>
        </div>
        <div v-else class="space-y-2">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span>共 <strong class="text-foreground">{{ filteredItems.length }}</strong> 个项目</span>
              <span v-if="filteredItems.length !== items.length">
                (已过滤 {{ items.length - filteredItems.length }} 个)
              </span>
              <span v-if="selectedItems.size > 0" class="text-primary">
                已选中 <strong>{{ selectedItems.size }}</strong> 个
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              @click="toggleSelectAll"
            >
              {{ selectedItems.size === filteredItems.length ? '取消全选' : '全选' }}
            </Button>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="w-12">
                  <Checkbox
                    :checked="selectedItems.size === filteredItems.length && filteredItems.length > 0"
                    :indeterminate="selectedItems.size > 0 && selectedItems.size < filteredItems.length"
                    @update:checked="toggleSelectAll"
                  />
                </TableHead>
                <TableHead class="hidden sm:table-cell">
                  ID
                </TableHead>
                <TableHead>名称</TableHead>
                <TableHead class="hidden md:table-cell">
                  描述
                </TableHead>
                <TableHead class="text-right">
                  价格
                </TableHead>
                <TableHead class="text-right">
                  操作
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="item in filteredItems"
                :key="item.id"
                :class="{ 'bg-muted/50': selectedItems.has(item.id) }"
              >
                <TableCell>
                  <Checkbox
                    :checked="selectedItems.has(item.id)"
                    @update:checked="() => toggleSelect(item.id)"
                  />
                </TableCell>
                <TableCell class="hidden sm:table-cell font-mono text-sm">
                  {{ item.id.slice(0, 8) }}...
                </TableCell>
                <TableCell class="font-medium">
                  {{ item.name }}
                </TableCell>
                <TableCell class="hidden md:table-cell">
                  {{ item.description || '-' }}
                </TableCell>
                <TableCell class="text-right">
                  {{ item.price ? `$${item.price.toFixed(2)}` : '-' }}
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex justify-end gap-2">
                    <Button variant="ghost" size="sm" @click="openEditDialog(item)">
                      <Icon name="lucide:edit" class="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      :disabled="deleting === item.id"
                      @click="openDeleteDialog(item)"
                    >
                      <Icon
                        v-if="deleting !== item.id"
                        name="lucide:trash-2"
                        class="h-4 w-4"
                      />
                      <Icon
                        v-else
                        name="lucide:loader-2"
                        class="h-4 w-4 animate-spin"
                      />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- 创建对话框 -->
    <Dialog v-model:open="showCreateDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>创建项目</DialogTitle>
          <DialogDescription>
            创建一个新的 item
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="name">名称 *</Label>
            <Input
              id="name"
              v-model="formData.name"
              placeholder="输入名称"
              :class="{ 'border-destructive': !formData.name.trim() && creating }"
            />
            <p v-if="!formData.name.trim() && creating" class="text-sm text-destructive">
              名称不能为空
            </p>
          </div>
          <div class="space-y-2">
            <Label for="description">描述</Label>
            <Textarea
              id="description"
              v-model="formData.description"
              placeholder="输入描述"
            />
          </div>
          <div class="space-y-2">
            <Label for="price">价格</Label>
            <Input
              id="price"
              v-model.number="formData.price"
              type="number"
              step="0.01"
              min="0"
              placeholder="输入价格"
            />
            <p v-if="formData.price !== undefined && formData.price < 0" class="text-sm text-destructive">
              价格不能为负数
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            :disabled="creating"
            @click="showCreateDialog = false; resetForm()"
          >
            取消
          </Button>
          <Button :disabled="creating" @click="createItem">
            <Icon
              v-if="creating"
              name="lucide:loader-2"
              class="mr-2 h-4 w-4 animate-spin"
            />
            <Icon
              v-else
              name="lucide:plus"
              class="mr-2 h-4 w-4"
            />
            创建
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 编辑对话框 -->
    <Dialog v-model:open="showEditDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>编辑项目</DialogTitle>
          <DialogDescription>
            更新 item 信息
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="edit-name">名称 *</Label>
            <Input
              id="edit-name"
              v-model="formData.name"
              placeholder="输入名称"
            />
          </div>
          <div class="space-y-2">
            <Label for="edit-description">描述</Label>
            <Textarea
              id="edit-description"
              v-model="formData.description"
              placeholder="输入描述"
            />
          </div>
          <div class="space-y-2">
            <Label for="edit-price">价格</Label>
            <Input
              id="edit-price"
              v-model.number="formData.price"
              type="number"
              step="0.01"
              placeholder="输入价格"
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            :disabled="updating"
            @click="showEditDialog = false; resetForm(); editingItem = null"
          >
            取消
          </Button>
          <Button :disabled="updating" @click="updateItem">
            <Icon
              v-if="updating"
              name="lucide:loader-2"
              class="mr-2 h-4 w-4 animate-spin"
            />
            <Icon
              v-else
              name="lucide:save"
              class="mr-2 h-4 w-4"
            />
            更新
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 删除确认对话框 -->
    <AlertDialog v-model:open="showDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认删除</AlertDialogTitle>
          <AlertDialogDescription>
            确定要删除 "<strong>{{ deletingItem?.name }}</strong>" 吗？此操作无法撤销。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="deleting !== null">
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            :disabled="deleting !== null"
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            @click="confirmDelete"
          >
            <Icon
              v-if="deleting !== null"
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

    <!-- 批量删除确认对话框 -->
    <AlertDialog v-model:open="showBatchDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认批量删除</AlertDialogTitle>
          <AlertDialogDescription>
            确定要删除选中的 <strong>{{ selectedItems.size }}</strong> 个项目吗？此操作无法撤销。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="batchDeleting">
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            :disabled="batchDeleting"
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            @click="confirmBatchDelete"
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
            删除 ({{ selectedItems.size }})
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
