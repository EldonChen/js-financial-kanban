import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.spec.ts'],
    exclude: ['node_modules', 'dist', '**/*.integration.spec.ts', '**/*.e2e.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.spec.ts',
        '**/*.interface.ts',
        '**/*.dto.ts',
        '**/*.schema.ts',
        '**/main.ts',
      ],
    },
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    pool: 'forks',
    // poolOptions 在 Vitest 4.x 中可能需要通过其他方式配置
    // 暂时移除以避免构建时的类型错误
  },
  esbuild: {
    target: 'node18',
  },
});
