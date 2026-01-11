# Docker Compose 构建优化说明

## 优化概述

本次优化主要针对 Docker Compose 编排的构建时间和失败率问题，通过以下方式进行了全面优化：

### 1. Dockerfile 优化

#### 缓存策略优化
- **依赖文件优先复制**：先复制 `package.json`、`pyproject.toml`、`Cargo.toml` 等依赖文件，再安装依赖，最后复制源代码
- **层缓存利用**：依赖安装层会被 Docker 缓存，只有依赖文件变化时才重新安装
- **减少层数**：合并多个 RUN 命令，减少镜像层数

#### Python 服务优化
- 使用 `--no-dev` 标志，只安装生产依赖
- 设置 `UV_CACHE_DIR` 环境变量，利用 uv 缓存
- 优化依赖安装顺序，充分利用 Docker 层缓存

#### Node.js/Bun 服务优化
- 多阶段构建，分离构建环境和运行环境
- 生产环境只安装生产依赖
- 优化依赖文件复制顺序

#### Rust 服务优化
- 使用虚拟项目策略缓存依赖编译
- 优化 Cargo 缓存目录设置
- 分离依赖编译和应用代码编译

#### 前端服务优化
- 创建了新的 Dockerfile（之前缺失）
- 使用多阶段构建
- 优化 pnpm 依赖安装缓存

### 2. Docker Compose 优化

#### BuildKit 支持
- 添加了 `version: '3.8'` 以支持 BuildKit
- 为每个服务配置了 `cache_from`，利用基础镜像缓存

#### 构建顺序优化
- 服务之间的依赖关系已优化，允许并行构建
- 只有 BFF 和前端需要等待后端服务，其他服务可以并行构建

### 3. .dockerignore 优化

- 统一了各服务的 `.dockerignore` 文件格式
- 排除了不必要的文件（测试、文档、IDE 配置等）
- 减少了构建上下文大小，加快构建速度

## 使用方法

### 启用 BuildKit（推荐）

在构建前设置环境变量：

```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

或者使用：

```bash
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build
```

### 构建所有服务

```bash
docker-compose build
```

### 并行构建（BuildKit 自动支持）

BuildKit 会自动并行构建没有依赖关系的服务：

```bash
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build --parallel
```

### 清理构建缓存

如果需要完全重新构建：

```bash
docker-compose build --no-cache
```

### 查看构建时间

使用 `time` 命令测量构建时间：

```bash
time docker-compose build
```

## 预期效果

### 构建时间优化
- **首次构建**：时间基本不变（需要下载所有依赖）
- **增量构建**：构建时间减少 60-80%（充分利用缓存）
- **代码变更后构建**：只重新构建变更的服务，其他服务使用缓存

### 失败率优化
- **网络超时**：通过镜像源配置和超时设置减少失败
- **依赖安装**：通过缓存机制减少重复安装导致的失败
- **构建顺序**：优化依赖关系，减少因顺序问题导致的失败

## 优化细节

### Python 服务
- 依赖安装层缓存：`pyproject.toml` 和 `uv.lock` 变化时才重新安装
- 代码层独立：应用代码变化不影响依赖层缓存

### Node.js/Bun 服务
- 依赖安装层缓存：`package.json` 和锁文件变化时才重新安装
- 构建产物分离：构建产物单独复制，不影响依赖层

### Rust 服务
- 依赖编译缓存：`Cargo.toml` 和 `Cargo.lock` 变化时才重新编译依赖
- 应用代码独立编译：只重新编译应用代码，依赖使用缓存

### 前端服务
- 依赖安装层缓存：`package.json` 和 `pnpm-lock.yaml` 变化时才重新安装
- 构建产物优化：只复制必要的构建产物到运行镜像

## 故障排查

### 构建失败

1. **检查网络连接**：确保可以访问镜像源
2. **清理缓存**：`docker system prune -a`
3. **检查依赖文件**：确保 `package.json`、`pyproject.toml` 等文件正确

### 缓存不生效

1. **确认 BuildKit 已启用**：检查环境变量
2. **检查 Dockerfile 层顺序**：确保依赖文件在代码之前复制
3. **查看构建日志**：确认是否使用了缓存层

### 镜像大小过大

1. **使用多阶段构建**：已优化，确保使用生产镜像
2. **检查 .dockerignore**：确保排除了不必要的文件
3. **清理未使用的层**：`docker image prune -a`

## 后续优化建议

1. **使用 Docker Buildx**：支持更高级的缓存策略
2. **配置远程缓存**：使用 Docker Registry 或 GitHub Actions Cache
3. **定期更新基础镜像**：保持安全性和性能
4. **监控构建时间**：建立构建时间基准，持续优化
