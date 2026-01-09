# Python FastAPI 股票信息服务 Dockerfile
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 配置腾讯云镜像源以加速下载
RUN sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i "s@http://deb.debian.org/debian@http://mirrors.tencent.com/debian@g" /etc/apt/sources.list 2>/dev/null || true

# 安装系统依赖
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml ./
# 注意：uv.lock 文件可能不存在，uv sync 会在没有 lock 文件时自动生成
COPY .env.example ./

# 安装 Python 依赖
RUN uv sync --frozen || uv sync

# 复制应用代码
COPY app ./app

# 暴露端口
EXPOSE 8001

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8001
ENV HOST=0.0.0.0

# 启动服务
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
