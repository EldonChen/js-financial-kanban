# 测试规范

与项目 `.cursorrules` 中「单元测试要求」及 SPEC 验收方案一致；测试应独立、可重复、快速。

## 测试框架与工具

- **框架**：pytest（项目规范约定 Python 使用 pytest）。  
- **异步**：pytest-asyncio，对 `async def` 测试函数使用 `@pytest.mark.asyncio` 或配置为 asyncio 模式。  
- **HTTP**：FastAPI 的 `TestClient` 或 `httpx.AsyncClient` 调用 ASGI 应用，用于 API 层测试。  
- **Mock**：`unittest.mock` 或 `pytest` 的 fixture；对外部数据源（akshare、yfinance 等）在单元测试中 mock，避免依赖网络与真实 API。

## 单元测试

- **范围**：Registry（register、getByName、getByMarket、getAll）、Router（指定/未指定 data_source、优先级与回退、超时）、Config（校验逻辑）、FieldMapper（原始 → Stock/Kline 映射）。  
- **约定**：  
  - 每个模块有对应 `tests/unit/test_<module>.py` 或按类/功能拆分。  
  - 测试命名清晰，如 `test_get_by_market_returns_sorted_by_priority`、`test_router_falls_back_when_provider_times_out`。  
  - 使用 fixture 提供 Mock Provider、Registry、Router，避免重复构造。  
- **覆盖率**：核心路径（Router、Registry、映射与校验）建议覆盖；不强制百分比，以「关键行为有断言」为准。

## API 测试

- **范围**：所有契约 API（GET/POST stocks、GET stocks/list、GET kline、GET providers/status）的正常与异常用例。  
- **方法**：  
  - 使用 TestClient 或 AsyncClient 发起请求，断言 `status_code`、`response.json()` 的 `code`、`data` 结构。  
  - 异常用例：缺参（400）、不存在的 ticker 或 data_source（404/503）、非法 period（400）等。  
- **隔离**：通过依赖注入注入 Mock Router 或「仅含 Mock Provider 的 Registry」，使 API 测试不依赖真实外部 API，且可预测结果。

## 集成测试（可选）

- **范围**：使用真实 akshare/yfinance 的端到端请求；可标记 `@pytest.mark.integration` 或通过环境变量（如 `RUN_INTEGRATION=1`）控制。  
- **约定**：  
  - CI 默认可跳过集成测试（`pytest -m "not integration"`），或单独 job 在有网络的环境执行。  
  - 不依赖固定外部数据内容，仅断言响应结构符合 schema、状态码合理。  
- **参考**：与现有 py-stock-info-service 的 test_provider_integration 等思路对齐。

## 测试数据与 Schema 校验

- **Fixture 数据**：可在 `tests/fixtures/` 或测试文件内定义「原始 akshare/yfinance 响应」的样例，用于 FieldMapper 与 Provider 的单元测试。  
- **契约校验**：若有从 spec/model/schemas.yaml 导出的 JSON Schema，可在 API 测试中校验 `response.json()["data"]` 符合对应 schema（工具可选：jsonschema、pydantic 校验）。

## 参考

- [pytest 文档](https://docs.pytest.org/)  
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)  
- 项目 `.cursorrules`：单元测试时机、覆盖范围、质量标准  
- 本实现文档 [qa/](../qa/README.md)：各模块验收标准
