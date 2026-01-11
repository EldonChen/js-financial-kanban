# Python FastAPI 股票信息服务 Dockerfile
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 配置腾讯云镜像源以加速下载（合并到一层以减少层数）
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv（使用缓存友好的方式）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# 设置 uv 环境变量：增加超时时间以应对网络问题
ENV UV_HTTP_TIMEOUT=300
ENV UV_CONSTRAINT=0
ENV UV_CACHE_DIR=/root/.cache/uv

# 先复制依赖文件（利用 Docker 层缓存）
# 只有当依赖文件变化时才重新安装依赖
COPY pyproject.toml ./
COPY uv.lock* ./
COPY .env.example ./

# 安装 Python 依赖（这一层会被缓存，除非依赖文件变化）
# 使用 --frozen 模式以加快安装速度，如果 lock 文件不存在则使用 sync
RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-dev || uv sync --no-dev; \
    else \
        uv sync --no-dev; \
    fi

# 复制应用代码（代码变化不会触发依赖重新安装）
COPY app ./app

# 暴露端口
EXPOSE 8001

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8001
ENV HOST=0.0.0.0

# 启动服务
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
