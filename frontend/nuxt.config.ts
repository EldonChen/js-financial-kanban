// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      pythonApiUrl: process.env.NUXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000',
      nodeApiUrl: process.env.NUXT_PUBLIC_NODE_API_URL || 'http://localhost:3000',
      rustApiUrl: process.env.NUXT_PUBLIC_RUST_API_URL || 'http://localhost:8080',
    },
  },
  app: {
    head: {
      title: 'Financial Kanban System',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
  },
});
