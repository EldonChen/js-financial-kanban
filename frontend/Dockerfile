# Nuxt.js 前端 Dockerfile
FROM node:20-slim AS base

# 安装 pnpm
RUN corepack enable && corepack prepare pnpm@10.10.0 --activate

# 设置工作目录
WORKDIR /app

# 构建阶段
FROM base AS builder

# 配置腾讯云镜像源并安装构建依赖（合并到一层以减少层数）
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用 Docker 层缓存）
# 只有当依赖文件变化时才重新安装依赖
COPY package.json pnpm-lock.yaml* ./

# 安装依赖（这一层会被缓存，除非依赖文件变化）
RUN pnpm install --frozen-lockfile || pnpm install

# 复制源代码（代码变化不会触发依赖重新安装）
COPY . .

# 构建应用
# 使用构建参数传递环境变量
ARG NUXT_PUBLIC_PYTHON_API_URL
ARG NUXT_PUBLIC_NODE_API_URL
ARG NUXT_PUBLIC_RUST_API_URL
ENV NUXT_PUBLIC_PYTHON_API_URL=${NUXT_PUBLIC_PYTHON_API_URL}
ENV NUXT_PUBLIC_NODE_API_URL=${NUXT_PUBLIC_NODE_API_URL}
ENV NUXT_PUBLIC_RUST_API_URL=${NUXT_PUBLIC_RUST_API_URL}

RUN pnpm run build

# 生产环境镜像
FROM base AS runner

# 安装健康检查工具（合并到一层以减少层数）
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3001
ENV HOST=0.0.0.0
ENV NITRO_PRESET=node-server

# 从构建阶段复制构建产物和必要文件
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package.json ./package.json

# 暴露端口
EXPOSE 3001

# 启动服务
CMD ["node", ".output/server/index.mjs"]
