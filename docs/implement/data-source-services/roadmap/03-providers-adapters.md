# 模块 03：Provider 适配器

## 目标

实现 **IStockMetaProvider** / **IKlineProvider** 接口与基类，以及 akshare、yfinance、easyquotation 的适配器与**字段映射**（原始响应 → spec/model 的 Stock、Kline），并可在启动时被 bootstrap 注册。

## 任务拆解

| 序号 | 任务 | 可验收产出 | 状态 |
|------|------|------------|------|
| 3.1 | 在 app/domain/interfaces.py 完整定义 IStockMetaProvider（fetch_stock_info, fetch_stock_list, fetch_stock_batch, is_available）、IKlineProvider（fetch_kline, is_available），与 spec/architecture/interfaces.md 一致 | 接口可被实现与类型检查 | 待开始 |
| 3.2 | 实现 app/providers/base.py：抽象基类或混入，提供 name、supported_markets、priority、features（IProviderMetadata），子类实现具体能力方法 | 子类仅实现业务方法即可 | 待开始 |
| 3.3 | 实现 app/providers/field_mappers/：将 akshare/yfinance 等原始结构映射为 Stock、Kline（Pydantic 或 dict 符合 schemas.yaml）；缺失字段填 null，不新增 schema 外字段 | 单元测试：给定原始响应，输出符合 schema | 待开始 |
| 3.4 | 实现 AkshareProvider：实现 IStockMetaProvider（及可选 IKlineProvider），内部调用 akshare API，经 field_mapper 输出 Stock/Kline，data_source 设为 name | 单元测试 mock akshare，断言返回结构符合契约 | 待开始 |
| 3.5 | 实现 YfinanceProvider：同上，针对 yfinance；支持美股/港股 | 同上 | 待开始 |
| 3.6 | 实现 EasyquotationProvider（可选）：仅实现其支持的能力（如 stock_info），不支持列表则 fetch_stock_list 返回 [] 或抛「不支持」 | 与现有 py-stock-info-service 行为对齐 | 待开始 |
| 3.7 | 在 bootstrap 中根据 config 的 ENABLE_* 与凭证实例化真实 Provider 并 register；与 02 的 Mock 可切换（通过配置或环境） | 启动后 registry 中有真实 Provider，且 is_available 可测 | 待开始 |

## 依赖关系

- 依赖 **02-config-registry**（配置与 Registry、bootstrap 已存在）。

## 注意事项

- 与 py-stock-info-service 的 providers、field_mapper 行为对齐，便于后续迁移。
- 超时与重试在 Provider 内或 Router 层统一处理（见 04）；本模块优先保证「正确映射与接口契约」。
- Kline 的 period 枚举：1m、5m、15m、30m、60m、1d、1w、1M；别名（如 daily→1d）在 API 层或 Router 层归一化。

## 任务状态

- 整体状态：**待开始**
- 最后更新：-
