# 模块 04：路由与数据规整

## 目标

实现 **IRouter**：按 market、feature、data_source 从 Registry 获取候选 Provider，按优先级依次调用并容错（失败则下一），返回统一模型；并对外提供「规整后的数据」供 API 层使用。

## 任务拆解

| 序号 | 任务 | 可验收产出 | 状态 |
|------|------|------------|------|
| 4.1 | 在 app/domain/interfaces.py 定义 IRouter：fetch_stock_info, fetch_stock_batch, fetch_stock_list, fetch_kline；签名与 spec/interfaces.md 一致 | 类型可被实现与注入 | 待开始 |
| 4.2 | 实现 app/domain/router.py：依赖 IRegistry；实现「指定 data_source」逻辑：仅派发该 Provider，不支持/不可用则返回 null 或抛业务异常 | 单元测试：指定 data_source 时仅调用该 Provider | 待开始 |
| 4.3 | 实现「未指定 data_source」逻辑：getByMarket(market, feature) 得候选，按 priority 排序，依次调用直至成功或耗尽；超时视为失败 | 单元测试：多 Provider 优先级与回退 | 待开始 |
| 4.4 | 集成超时与重试：使用 config 的 DATA_SOURCE_REQUEST_TIMEOUT、DATA_SOURCE_MAX_RETRIES；可重试错误重试后仍失败则下一 Provider；不可重试错误（如 4xx）不重试 | 行为符合 spec/error/exception-handling.md | 待开始 |
| 4.5 | 实现 app/services/data_source_app_service.py：编排 Router，对外方法与 Router 一一对应，返回契约中的数据结构（Stock、Record<ticker, Stock|null>、StockListData、KlineResponseData） | 应用服务层不依赖具体 Provider，仅依赖 IRouter | 待开始 |
| 4.6 | 将 Router 与 Registry 在 main/deps 中装配，bootstrap 后 Registry 已注册 Provider，Router 使用该 Registry | 端到端：通过 AppService 调用可得真实或 Mock 数据 | 待开始 |

## 依赖关系

- 依赖 **02-config-registry**、**03-providers-adapters**。

## 注意事项

- 路由规则严格遵循 [spec/architecture/routing.md](../../../spec/data-source-service/architecture/routing.md)。
- 数据规整出口：Router 返回的已是「统一模型」（由 Provider 内 field_mapper 保证）；AppService 仅做编排与可能的结构封装（如 KlineResponseData 含 ticker、period、data、data_source）。

## 任务状态

- 整体状态：**待开始**
- 最后更新：-
