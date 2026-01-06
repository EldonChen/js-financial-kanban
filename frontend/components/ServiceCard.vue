<template>
  <NuxtLink :to="link" class="block">
    <div
      class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200"
    >
      <div :class="[color, 'w-12 h-12 rounded-lg mb-4']"></div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">
        {{ title }}
      </h3>
      <p class="text-gray-600">
        {{ description }}
      </p>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  description: string;
  link: string;
  color: string;
}

defineProps<Props>();
</script>
