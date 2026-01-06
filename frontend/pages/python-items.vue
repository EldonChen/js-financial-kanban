<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <div class="mb-6">
        <NuxtLink
          to="/"
          class="text-blue-600 hover:text-blue-800 mb-4 inline-block"
        >
          ← 返回首页
        </NuxtLink>
        <h1 class="text-3xl font-bold text-gray-900">
          Python FastAPI 服务 - Items 管理
        </h1>
      </div>

      <!-- 创建表单 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">
          {{ editingItem ? '编辑 Item' : '创建新 Item' }}
        </h2>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              名称 *
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入 item 名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              描述
            </label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入 item 描述"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              价格
            </label>
            <input
              v-model.number="form.price"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入价格"
            />
          </div>
          <div class="flex gap-2">
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {{ editingItem ? '更新' : '创建' }}
            </button>
            <button
              v-if="editingItem"
              type="button"
              @click="cancelEdit"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              取消
            </button>
          </div>
        </form>
      </div>

      <!-- 错误提示 -->
      <div
        v-if="error"
        class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
      >
        {{ error }}
      </div>

      <!-- 成功提示 -->
      <div
        v-if="successMessage"
        class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"
      >
        {{ successMessage }}
      </div>

      <!-- Items 列表 -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Items 列表</h2>
        <div v-if="loading" class="text-center py-8">
          <p class="text-gray-500">加载中...</p>
        </div>
        <div v-else-if="items.length === 0" class="text-center py-8">
          <p class="text-gray-500">暂无 items</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="item in items"
            :key="item.id"
            class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ item.name }}
                </h3>
                <p v-if="item.description" class="text-gray-600 mt-1">
                  {{ item.description }}
                </p>
                <div class="mt-2 flex gap-4 text-sm text-gray-500">
                  <span v-if="item.price">价格: ¥{{ item.price }}</span>
                  <span>创建时间: {{ formatDate(item.created_at) }}</span>
                </div>
              </div>
              <div class="flex gap-2 ml-4">
                <button
                  @click="startEdit(item)"
                  class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                >
                  编辑
                </button>
                <button
                  @click="handleDelete(item.id)"
                  class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Item, CreateItemDto, UpdateItemDto } from '~/api/python';
import {
  getItems,
  createItem,
  updateItem,
  deleteItem,
} from '~/api/python';

definePageMeta({
  layout: false,
});

const items = ref<Item[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const successMessage = ref<string | null>(null);
const editingItem = ref<Item | null>(null);

const form = reactive<CreateItemDto & UpdateItemDto>({
  name: '',
  description: '',
  price: undefined,
});

// 加载 items
async function loadItems() {
  loading.value = true;
  error.value = null;
  try {
    const response = await getItems();
    items.value = response.data || [];
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败';
  } finally {
    loading.value = false;
  }
}

// 提交表单
async function handleSubmit() {
  error.value = null;
  successMessage.value = null;

  try {
    if (editingItem.value) {
      // 更新
      await updateItem(editingItem.value.id, form);
      successMessage.value = 'Item 更新成功';
    } else {
      // 创建
      await createItem(form);
      successMessage.value = 'Item 创建成功';
    }

    // 重置表单
    form.name = '';
    form.description = '';
    form.price = undefined;
    editingItem.value = null;

    // 重新加载列表
    await loadItems();

    // 清除成功消息
    setTimeout(() => {
      successMessage.value = null;
    }, 3000);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '操作失败';
  }
}

// 开始编辑
function startEdit(item: Item) {
  editingItem.value = item;
  form.name = item.name;
  form.description = item.description || '';
  form.price = item.price;
  // 滚动到表单
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 取消编辑
function cancelEdit() {
  editingItem.value = null;
  form.name = '';
  form.description = '';
  form.price = undefined;
}

// 删除 item
async function handleDelete(id: string) {
  if (!confirm('确定要删除这个 item 吗？')) {
    return;
  }

  error.value = null;
  try {
    await deleteItem(id);
    successMessage.value = 'Item 删除成功';
    await loadItems();
    setTimeout(() => {
      successMessage.value = null;
    }, 3000);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败';
  }
}

// 格式化日期
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-CN');
}

// 页面加载时获取数据
onMounted(() => {
  loadItems();
});
</script>
