# Python 编程规范

与项目 `.cursorrules` 及通用 Python 最佳实践对齐；格式与风格可工具化执行。

## 风格与格式化

- **格式化工具**：Black（项目规范约定 Python 使用 Black）。  
  - 配置：建议行宽 88（Black 默认），或与 monorepo 其他 Python 服务一致。  
  - 运行：`uv run black app/ tests/`，CI 中建议 `--check`。
- **导入顺序**：标准库 → 第三方 → 本地；每组内按字母序。可选用 isort 与 Black 兼容配置。
- **命名**：  
  - 模块/文件：小写 + 下划线（如 `field_mapper.py`）。  
  - 类：大驼峰（如 `StockDataRouter`）。  
  - 函数/方法/变量：小写 + 下划线（如 `fetch_stock_info`）。  
  - 常量：全大写下划线（如 `DEFAULT_TIMEOUT_SECONDS`）。  
  - 与 SPEC 接口一致时，可保留 camelCase 的**方法语义**在实现中用 snake_case（如接口 `fetchStockInfo` → 实现 `fetch_stock_info`）。

## 类型注解

- **原则**：公开函数、方法、API 入参/出参应有类型注解；内部简单逻辑可放宽。  
- **方式**：使用 `typing` 或 3.10+ 的 `list[...]`、`dict[k, v]` 等；异步用 `Coroutine`/`Awaitable` 或直接 `async def` 返回类型。  
- **Optional**：`Optional[T]` 与 `T | None` 二选一，项目内统一即可。  
- **参考**：[PEP 484](https://peps.python.org/pep-0484/)、[PEP 585](https://peps.python.org/pep-0585/)。  
- 运行静态检查：`uv run pyright` 或 `uv run mypy app/`（若已配置）。

## 异步

- **统一异步**：与 FastAPI/Motor 一致，Provider 与 Router 的 I/O 操作使用 `async def` 与 `await`；避免在异步路径中混用阻塞调用（若必须，使用 `run_in_executor`）。  
- **超时**：使用 `asyncio.wait_for` 或 httpx/aiohttp 等库的超时参数，避免无限等待。  
- **取消**：对长时间操作考虑 `asyncio.CancelledError` 与资源清理。

## 抽象与接口

- **SPEC 接口**：`IProviderMetadata`、`IStockMetaProvider`、`IKlineProvider`、`IRegistry`、`IRouter` 使用 `abc.ABC` 与 `@abstractmethod`，或 `typing.Protocol`（结构性子类型）。  
- **依赖注入**：Router 依赖 IRegistry、API 层依赖 Router/AppService，通过 FastAPI `Depends()` 或构造函数注入，便于测试与替换。  
- **单一职责**：Provider 只负责「调用外部 API + 字段映射」；Router 只负责「选择 + 调用 + 容错」；不在 API 层直接操作 Registry。

## 项目结构约定

- **领域与 API 分离**：`app/domain/` 不依赖 `app/api/`；`app/api/` 依赖 `app/domain/` 与 `app/services/`。  
- **配置**：集中放在 `app/config.py`，使用 pydantic-settings；不在业务代码中散落 `os.getenv`。  
- **日志**：使用 `logging.getLogger(__name__)`，不 print；级别与内容见 [api-error-handling.md](api-error-handling.md) 与 spec/error/exception-handling.md。

## 参考

- [PEP 8](https://peps.python.org/pep-0008/)  
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)（可选参考）  
- 项目根目录 `.cursorrules`（技术栈与测试要求）
