import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath } from 'url'
import { resolve } from 'path'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  css: ['~/assets/css/tailwind.css'],
  vite: {
    plugins: [
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': resolve(fileURLToPath(new URL('.', import.meta.url)), 'app'),
      },
    },
  },

  components: [
    {
      path: '~/components',
      extensions: ['.vue'],
    },
  ],

  modules: [
    'shadcn-nuxt',
    '@vueuse/nuxt',
    '@nuxt/eslint',
    '@nuxt/icon',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    '@nuxt/fonts',
  ],

  shadcn: {
    /**
     * Prefix for all the imported component
     */
    prefix: '',
    /**
     * Directory that the component lives in.
     * @default "~/components/ui"
     */
    componentDir: '~/components/ui',
  },

  colorMode: {
    classSuffix: '',
  },

  eslint: {
    config: {
      standalone: false,
    },
  },

  fonts: {
    defaults: {
      weights: [300, 400, 500, 600, 700, 800],
    },
  },

  routeRules: {
    '/components': { redirect: '/components/accordion' },
    '/settings': { redirect: '/settings/profile' },
  },

  imports: {
    dirs: [
      './lib',
    ],
  },

  compatibilityDate: '2024-12-14',

  runtimeConfig: {
    public: {
      // 注意：在开发模式下，如果 Nuxt 前端运行在 3000 端口，
      // 后端 Node.js 服务应该运行在不同的端口（例如 3001）以避免端口冲突
      // 可以通过环境变量 NUXT_PUBLIC_NODE_API_URL 来覆盖默认值
      // Docker 环境中，后端服务运行在 3000，前端运行在 3001
      nodeApiUrl: process.env.NUXT_PUBLIC_NODE_API_URL || 'http://localhost:3001',
      pythonApiUrl: process.env.NUXT_PUBLIC_PYTHON_API_URL || 'http://localhost:8000',
      rustApiUrl: process.env.NUXT_PUBLIC_RUST_API_URL || 'http://localhost:8080',
      bffApiUrl: process.env.NUXT_PUBLIC_BFF_API_URL || 'http://localhost:4000',
    },
  },
})
