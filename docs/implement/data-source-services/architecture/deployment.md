# 部署设计

## 独立启动

- **命令**：在 `services/data-source-service/` 下执行 `uv run uvicorn app.main:app --host 0.0.0.0 --port <PORT>`，或通过 `pyproject.toml` 的 script 封装（如 `uv run start`）。
- **端口**：与 py-stock-info-service（如 8001）区分，建议单独端口（如 8002），可在配置或环境变量中指定。
- **依赖**：不依赖股票信息服务、历史数据服务或 MongoDB；仅依赖配置（环境变量/可选文件）与网络（访问外部数据源 API）。

## 配置与环境变量

- 遵循 [spec/prd/05-config-auth.md](../../../spec/data-source-service/prd/05-config-auth.md) 的表格：
  - `ENABLE_AKSHARE`、`ENABLE_YFINANCE`、`ENABLE_EASYQUOTATION`、`ENABLE_TUSHARE`、`TUSHARE_TOKEN`、`ENABLE_IEX_CLOUD`、`IEX_CLOUD_API_KEY`、`ENABLE_ALPHA_VANTAGE`、`ALPHA_VANTAGE_API_KEY`
  - `DATA_SOURCE_REQUEST_TIMEOUT`（默认 30）、`DATA_SOURCE_MAX_RETRIES`（默认 1）
- 启动时执行配置校验：至少一个第一优先级数据源启用；若需凭证则凭证非空（否则不注册该 Provider 并打 warning）。
- 提供 `.env.example`，列出所有变量及说明，不含真实凭证。

## Docker 镜像

- **Dockerfile 位置**：`services/data-source-service/Dockerfile`。
- **基础镜像**：建议 `python:3.11-slim` 或与团队约定一致。
- **构建**：使用 uv 时可在镜像内安装 uv，复制 `pyproject.toml` 与 lock 文件，执行 `uv sync --frozen`，再复制 `app/` 等代码。
- **运行**：镜像内启动命令为 `uvicorn app.main:app --host 0.0.0.0 --port 8000`（或从环境变量读取端口）；不包含数据库或队列启动。
- **镜像标签**：建议包含版本或 git sha，便于与 docker-compose 或 K8s 配合。

## docker-compose 集成

- 在 monorepo 根或 `services/data-source-service/` 下提供 `docker-compose.yml`（或片段），将本服务定义为独立 service：
  - `build: context: . dockerfile: Dockerfile`
  - `ports: "8002:8000"`（或约定端口）
  - `environment` 从 `.env` 或 env_file 注入，不写死凭证。
- 可与 `python-service`、`py-stock-info-service`、前端等在同一 compose 中编排；本服务不依赖其他服务的启动顺序，仅需网络可达（供上游调用）。

## 健康检查

- **存活**：`GET /health` 或 `GET /api/v1/health` 返回 200，表示进程存活。
- **就绪（可选）**：可基于「至少一个已注册 Provider 的 is_available() 为 true」返回 200，否则 503，便于负载均衡或 K8s 就绪探针。

## 与 SPEC 的对应

- 配置与凭证：PRD 05。
- 错误与可用性：无可用 Provider 时 503；错误码见 [spec/error/error-codes.md](../../../spec/data-source-service/error/error-codes.md)。
