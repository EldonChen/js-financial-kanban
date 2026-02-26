# 模块 01：服务骨架

## 目标

建立独立可部署的数据源服务**最小可运行骨架**：目录结构、FastAPI 应用、配置骨架、健康检查、以及可构建/运行的 Docker 镜像与 docker-compose 集成。

## 任务拆解

| 序号 | 任务 | 可验收产出 | 状态 |
|------|------|------------|------|
| 1.1 | 创建 `services/data-source-service/` 目录及 `app/` 子结构（见 architecture/service-layout.md） | 存在 app/main.py, app/config.py, app/api/routes, app/domain, app/providers, app/services | 待开始 |
| 1.2 | 配置 pyproject.toml（或 requirements.txt）：FastAPI、uvicorn、pydantic、pydantic-settings | 依赖可安装，`uv run uvicorn app.main:app` 可启动 | 待开始 |
| 1.3 | 实现 app/config.py：仅端口、ENABLE_AKSHARE/ENABLE_YFINANCE 等布尔与占位凭证，暂不做「至少一个启用」校验 | .env 可覆盖，应用能加载 | 待开始 |
| 1.4 | 实现 app/main.py：创建 FastAPI 应用、挂载健康检查 GET /health（或 /api/v1/health）、无业务路由 | 请求 /health 返回 200 | 待开始 |
| 1.5 | 编写 Dockerfile：基于 python:3.11-slim，uv 安装依赖，复制代码，CMD 启动 uvicorn | 镜像可 build 并 run，/health 可访问 | 待开始 |
| 1.6 | 编写 .env.example 与 README：列出端口、ENABLE_* 等变量说明；README 含启动命令与 Docker 说明 | 文档与示例齐全 | 待开始 |
| 1.7 | 可选：docker-compose.yml 单服务，build 本目录并暴露端口 | compose up 可访问 /health | 待开始 |

## 依赖关系

- 无前置模块依赖。

## 注意事项

- 不实现任何 Provider、Router、Registry；仅空壳与配置占位。
- 端口与 py-stock-info-service 区分（如 8002）。
- 健康检查路径与后续 K8s/网关约定一致即可。

## 任务状态

- 整体状态：**待开始**
- 最后更新：-
