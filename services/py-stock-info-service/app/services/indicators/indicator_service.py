"""技术指标核心服务（协调各个子服务）."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.services.historical_data.historical_data_service import HistoricalDataService
from app.services.indicators.indicator_calculator import IndicatorCalculator
from app.services.indicators.indicator_query import IndicatorQuery
from app.services.indicators.indicator_storage import IndicatorStorage

logger = logging.getLogger(__name__)


class IndicatorService:
    """技术指标核心服务（协调各个子服务）."""

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化技术指标服务.

        Args:
            db: MongoDB 数据库对象（可选）
        """
        self.db = db if db is not None else get_database()
        self.calculator = IndicatorCalculator(self.db)
        self.storage = IndicatorStorage(self.db)
        self.query = IndicatorQuery(self.db)
        self.historical_data_service = HistoricalDataService(self.db)

    def get_supported_indicators(self) -> list[dict[str, Any]]:
        """获取支持的指标列表.

        Returns:
            list[dict]: 支持的指标列表
        """
        return self.calculator.get_supported_indicators()

    async def calculate_indicator(
        self,
        ticker: str,
        indicator_type: str,
        indicator_name: str,
        period: str = "1d",
        params: Optional[dict[str, Any]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        use_cache: bool = True,
    ) -> list[dict[str, Any]]:
        """计算单个技术指标.

        Args:
            ticker: 股票代码
            indicator_type: 指标类型（MA, EMA, RSI, MACD, BOLL）
            indicator_name: 指标名称（MA5, MA10, RSI14等）
            period: 时间周期（默认 1d）
            params: 指标参数（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            use_cache: 是否使用缓存（默认 True）

        Returns:
            list[dict]: 指标数据列表
        """
        # 1. 如果使用缓存，先检查数据库是否已有数据
        if use_cache:
            existing_data = await self.query.query_by_indicator(
                ticker, indicator_name, period, start_date, end_date
            )
            if existing_data:
                logger.info(
                    f"使用缓存的指标数据：{ticker} {indicator_name} {period} - {len(existing_data)} 条"
                )
                return existing_data

        # 2. 获取历史K线数据
        kline_data = await self.historical_data_service.query_kline_data(
            ticker, period, start_date, end_date
        )

        if not kline_data:
            logger.warning(f"历史K线数据不足：{ticker} {period}")
            return []

        # 3. 计算指标
        indicator_data = await self._calculate_indicator_by_type(
            ticker, indicator_type, indicator_name, params or {}, kline_data
        )

        # 4. 保存到数据库（异步，不等待）
        if indicator_data:
            asyncio.create_task(
                self.storage.upsert_indicator_data(
                    ticker, period, indicator_type, indicator_name, indicator_data
                )
            )

        return indicator_data

    async def _calculate_indicator_by_type(
        self,
        ticker: str,
        indicator_type: str,
        indicator_name: str,
        params: dict[str, Any],
        kline_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """根据指标类型计算指标.

        Args:
            ticker: 股票代码
            indicator_type: 指标类型
            indicator_name: 指标名称
            params: 指标参数
            kline_data: K线数据

        Returns:
            list[dict]: 指标数据
        """
        if indicator_type == "MA":
            period_param = params.get("period", 5)
            return await self.calculator.calculate_ma(ticker, period_param, kline_data)

        elif indicator_type == "EMA":
            period_param = params.get("period", 12)
            return await self.calculator.calculate_ema(ticker, period_param, kline_data)

        elif indicator_type == "RSI":
            period_param = params.get("period", 14)
            return await self.calculator.calculate_rsi(ticker, period_param, kline_data)

        elif indicator_type == "MACD":
            fast = params.get("fast", 12)
            slow = params.get("slow", 26)
            signal = params.get("signal", 9)
            macd_results = await self.calculator.calculate_macd(
                ticker, fast, slow, signal, kline_data
            )
            # 返回指定的 MACD 子指标
            if indicator_name in macd_results:
                return macd_results[indicator_name]
            return []

        elif indicator_type == "BOLL":
            period_param = params.get("period", 20)
            std_dev = params.get("std_dev", 2.0)
            boll_results = await self.calculator.calculate_bollinger_bands(
                ticker, period_param, std_dev, kline_data
            )
            # 返回指定的 BOLL 子指标
            if indicator_name in boll_results:
                return boll_results[indicator_name]
            return []

        else:
            logger.warning(f"不支持的指标类型：{indicator_type}")
            return []

    async def query_indicator_data(
        self,
        ticker: str,
        indicator_name: str,
        period: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """查询技术指标数据.

        Args:
            ticker: 股票代码
            indicator_name: 指标名称
            period: 时间周期
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            limit: 返回数量限制（可选）

        Returns:
            list[dict]: 指标数据列表
        """
        return await self.query.query_by_indicator(
            ticker, indicator_name, period, start_date, end_date, limit
        )

    async def calculate_batch_indicators(
        self,
        ticker: str,
        indicator_names: list[str],
        period: str = "1d",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        progress_callback: Optional[Callable] = None,
    ) -> dict[str, Any]:
        """批量计算多个技术指标.

        Args:
            ticker: 股票代码
            indicator_names: 指标名称列表
            period: 时间周期（默认 1d）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            progress_callback: 进度回调函数（可选）

        Returns:
            dict: 包含统计信息和结果的字典
        """
        total = len(indicator_names)
        success = 0
        failed = 0
        results = {}

        # 发送初始化进度
        if progress_callback:
            await progress_callback(
                {
                    "stage": "init",
                    "message": f"开始批量计算指标：{ticker}",
                    "progress": 0,
                    "total": total,
                }
            )

        # 遍历指标列表
        for idx, indicator_name in enumerate(indicator_names):
            try:
                # 解析指标类型和参数
                indicator_info = self._parse_indicator_name(indicator_name)
                if not indicator_info:
                    logger.warning(f"无法解析指标名称：{indicator_name}")
                    failed += 1
                    continue

                # 计算指标
                indicator_data = await self.calculate_indicator(
                    ticker=ticker,
                    indicator_type=indicator_info["type"],
                    indicator_name=indicator_name,
                    period=period,
                    params=indicator_info["params"],
                    start_date=start_date,
                    end_date=end_date,
                    use_cache=False,  # 批量计算不使用缓存
                )

                results[indicator_name] = indicator_data
                success += 1

                # 发送进度更新
                if progress_callback:
                    progress = int((idx + 1) / total * 100)
                    await progress_callback(
                        {
                            "stage": "calculating",
                            "message": f"正在计算指标... ({idx + 1}/{total})",
                            "progress": progress,
                            "current": idx + 1,
                            "total": total,
                            "success": success,
                            "failed": failed,
                            "current_indicator": indicator_name,
                        }
                    )

            except Exception as e:
                logger.error(f"计算指标失败：{indicator_name} - {e}")
                failed += 1

        # 发送完成通知
        if progress_callback:
            await progress_callback(
                {
                    "stage": "completed",
                    "message": f"批量计算完成：总数 {total}，成功 {success}，失败 {failed}",
                    "progress": 100,
                    "total": total,
                    "success": success,
                    "failed": failed,
                    "result": {
                        "ticker": ticker,
                        "period": period,
                        "total": total,
                        "success": success,
                        "failed": failed,
                    },
                }
            )

        return {
            "ticker": ticker,
            "period": period,
            "total": total,
            "success": success,
            "failed": failed,
            "results": results,
        }

    def _parse_indicator_name(self, indicator_name: str) -> Optional[dict[str, Any]]:
        """解析指标名称，提取指标类型和参数.

        Args:
            indicator_name: 指标名称（如 MA5, RSI14, MACD_DIF）

        Returns:
            dict: {"type": 指标类型, "params": 参数字典}，解析失败返回 None
        """
        # 获取支持的指标列表
        supported = self.get_supported_indicators()

        # 查找匹配的指标
        for indicator in supported:
            if indicator["name"] == indicator_name:
                return {"type": indicator["type"], "params": indicator["params"]}

        return None
