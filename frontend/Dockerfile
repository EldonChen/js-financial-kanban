# Nuxt.js 前端 Dockerfile
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖文件
COPY package.json ./
COPY pnpm-lock.yaml* package-lock.json* yarn.lock* ./

# 安装依赖
RUN pnpm install --frozen-lockfile || pnpm install

# 复制源代码
COPY . .

# 构建应用（Nuxt 3 会生成 .output 目录）
RUN pnpm build

# 生产环境镜像
FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 从构建阶段复制构建产物和必要的文件
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package.json ./package.json

# 安装生产依赖（如果需要）
RUN npm install -g pnpm && \
    pnpm install --prod --frozen-lockfile || true

# 暴露端口
EXPOSE 3001

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3001
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3001

# 启动服务（Nuxt 3 生产模式）
CMD ["node", ".output/server/index.mjs"]
