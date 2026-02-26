# 端到端服务 - 验收方案

整体验收：独立启动、Docker、与契约及现有行为一致性。

## 验收方法

1. **手工**：从零启动服务、构建并运行 Docker 镜像、使用 docker-compose 与其他服务一起启动；调用所有契约 API 并抽查响应。
2. **自动化**：E2E 脚本或 CI 步骤：启动服务 → 请求 /health、/api/v1/providers/status、/api/v1/stocks/{ticker} 等 → 断言状态码与基本结构。
3. **契约**：抽样响应与 spec/model/schemas.yaml 及 error 规范一致。

## 验收标准

### 独立启动与部署

- [ ] **AC-1** 服务可独立启动，不依赖股票信息服务、历史数据服务或 MongoDB；仅依赖配置与网络（访问外部数据源）。
- [ ] **AC-2** 可通过 `uv run uvicorn app.main:app` 或约定命令启动，监听约定端口；GET /health（或 /api/v1/health）返回 200。
- [ ] **AC-3** 可打包成 Docker 镜像并运行，容器内请求 /health 返回 200。
- [ ] **AC-4** 可通过 docker-compose 与其他服务一起部署；本服务不依赖其他服务启动顺序，仅需网络可达供上游调用。

### 配置与文档

- [ ] **AC-5** 提供 .env.example 与配置说明文档，列出端口、ENABLE_*、凭证、超时等变量及说明；不含真实凭证。
- [ ] **AC-6** README 包含：项目说明、启动命令、环境变量、Docker 构建与运行、API 文档路径（如 /docs）。

### 契约一致性

- [ ] **AC-7** 提供契约中定义的股票元信息、股票列表、历史 K 线、能力查询等 API；路径与 SPEC 一致。
- [ ] **AC-8** 上述 API 的响应格式符合设计（统一 ApiResponse、data 结构符合 schemas.yaml）；错误时 code/message/data 符合 error-codes.md。
- [ ] **AC-9** 支持按 market、优先级、首选 data_source 路由与回退；行为与 spec/architecture/routing.md 及现有 py-stock-info-service 的 router 一致或符合设计变更。

### 测试与行为

- [ ] **AC-10** 相关单元测试与 API 测试通过；行为与现有 py-stock-info-service 的 providers、historical_data_fetcher、field_mapper 一致或符合设计变更。
- [ ] **AC-11** 可选：集成测试（真实数据源）可被环境变量或标记控制执行或跳过，不阻塞 CI。
