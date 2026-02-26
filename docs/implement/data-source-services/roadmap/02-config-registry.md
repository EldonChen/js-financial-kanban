# 模块 02：配置与注册

## 目标

实现**配置模型与校验**（满足 PRD 05），以及 **IRegistry** 的实现与**启动时 Provider 注册流程**；不实现真实数据源逻辑，可用 Mock Provider 验证注册与发现。

## 任务拆解

| 序号 | 任务 | 可验收产出 | 状态 |
|------|------|------------|------|
| 2.1 | 完善 app/config.py：所有 PRD 05 环境变量（ENABLE_*、凭证、DATA_SOURCE_REQUEST_TIMEOUT、DATA_SOURCE_MAX_RETRIES），类型与默认值一致 | 配置类可加载并校验类型 | 待开始 |
| 2.2 | 实现配置校验：至少一个第一优先级（akshare/yfinance/easyquotation）启用；若某 ENABLE_X 为 true 且该源需凭证，则凭证非空否则不注册并 warning | 启动时校验行为符合 PRD 05 | 待开始 |
| 2.3 | 在 app/domain/interfaces.py 定义 IProviderMetadata、IRegistry（getByName, getByMarket, getAll, register）；可选用 Protocol 或 ABC | 类型可被实现与依赖注入 | 待开始 |
| 2.4 | 实现 app/domain/registry.py：内存 Registry，register 按 name 唯一（覆盖或拒绝可约定），getByMarket(market, feature) 返回按 priority 排序的列表 | 单元测试：注册多个 Mock，getByMarket/getByName/getAll 正确 | 待开始 |
| 2.5 | 实现 app/bootstrap.py：从 config 读取已启用 Provider 列表，实例化（本模块可为 Mock Provider），调用 registry.register(provider) | 启动后 registry.getAll() 非空（或按配置为空） | 待开始 |
| 2.6 | 在 app/main.py 生命周期（lifespan 或 startup）中调用 bootstrap，将 registry 注入到依赖（deps）或 app.state | 应用启动后注册表已填充 | 待开始 |

## 依赖关系

- 依赖 **01-service-skeleton**（目录与 FastAPI 应用存在）。

## 注意事项

- Mock Provider 仅需实现 IProviderMetadata 及最少方法（如 is_available 返回 True），不请求真实外部 API。
- 凭证不得写入日志或错误信息；配置校验失败时行为与 spec/error 一致（启动失败或 503）。

## 任务状态

- 整体状态：**待开始**
- 最后更新：-
