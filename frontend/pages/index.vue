<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">
          金融看板系统
        </h1>
        <p class="text-xl text-gray-600">
          Financial Kanban System
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ServiceCard
          title="Python FastAPI 服务"
          description="使用 FastAPI 构建的 RESTful API 服务"
          link="/python-items"
          color="bg-blue-500"
        />
        <ServiceCard
          title="Node.js Nest.js 服务"
          description="使用 Bun + Nest.js 构建的 RESTful API 服务"
          link="/node-items"
          color="bg-green-500"
        />
        <ServiceCard
          title="Rust Axum 服务"
          description="使用 Rust + Axum 构建的高性能 RESTful API 服务"
          link="/rust-items"
          color="bg-orange-500"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
});
</script>
