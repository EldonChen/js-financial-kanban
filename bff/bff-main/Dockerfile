# BFF 服务 Dockerfile
FROM oven/bun:latest AS builder

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（利用 Docker 层缓存）
# 只有当依赖文件变化时才重新安装依赖
COPY package.json ./
COPY bun.lock* ./

# 安装依赖（这一层会被缓存，除非依赖文件变化）
RUN bun install --frozen-lockfile || bun install

# 复制源代码（代码变化不会触发依赖重新安装）
COPY . .

# 构建应用
RUN bun run build

# 生产环境镜像
FROM oven/bun:slim

# 安装健康检查工具（合并到一层以减少层数）
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package.json ./
COPY bun.lock* ./

# 只安装生产依赖（利用缓存）
RUN bun install --frozen-lockfile --production || bun install --production

# 从构建阶段复制构建产物
COPY --from=builder /app/dist ./dist

# 暴露端口
EXPOSE 4000

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=4000

# 启动服务
CMD ["bun", "run", "start:prod"]
