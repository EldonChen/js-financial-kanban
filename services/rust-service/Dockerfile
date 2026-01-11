# Rust Axum 服务 Dockerfile
FROM rust:1.92.0-slim AS builder

# 配置腾讯云镜像源并安装构建依赖（合并到一层以减少层数）
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 设置 Rust 缓存目录（利用 Docker 层缓存）
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTUP_HOME=/usr/local/rustup

# 先复制 Cargo 文件（利用 Docker 层缓存）
# 只有当依赖文件变化时才重新编译依赖
COPY Cargo.toml Cargo.lock* ./

# 创建虚拟项目以缓存依赖（这一层会被缓存，除非 Cargo 文件变化）
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# 复制源代码（代码变化不会触发依赖重新编译）
COPY src ./src

# 构建应用（只重新编译应用代码，依赖已缓存）
RUN touch src/main.rs && \
    cargo build --release && \
    cp target/release/rust-service /app/rust-service

# 生产环境镜像
FROM debian:bookworm-slim

# 配置腾讯云镜像源并安装运行时依赖（合并到一层以减少层数）
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/rust-service /app/rust-service

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080

# 启动服务
CMD ["./rust-service"]
