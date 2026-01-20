"""技术指标计算服务（使用 pandas-ta）."""

import logging
from datetime import datetime
from typing import Any, Optional

import numpy as np
import pandas as pd

try:
    import pandas_ta as ta

    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False
    logging.warning("pandas-ta 未安装，技术指标计算功能将不可用")

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """技术指标计算服务（使用 pandas-ta 计算指标）."""

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """初始化指标计算服务.

        Args:
            db: MongoDB 数据库对象（可选）
        """
        self.db = db
        if not HAS_PANDAS_TA:
            logger.warning("pandas-ta 未安装，技术指标计算功能将不可用")

    def _prepare_dataframe(self, kline_data: list[dict[str, Any]]) -> pd.DataFrame:
        """准备 DataFrame 用于指标计算.

        Args:
            kline_data: K线数据列表

        Returns:
            pd.DataFrame: 准备好的 DataFrame
        """
        if not kline_data:
            return pd.DataFrame()

        # 转换为 DataFrame
        df = pd.DataFrame(kline_data)

        # 确保必需字段存在
        required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
        for field in required_fields:
            if field not in df.columns:
                raise ValueError(f"K线数据缺少必需字段：{field}")

        # 设置时间索引
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df = df.set_index("timestamp")

        return df

    async def calculate_ma(
        self, ticker: str, period: int, kline_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """计算移动平均线（MA）.

        Args:
            ticker: 股票代码
            period: 周期参数（如 5, 10, 20）
            kline_data: K线数据列表

        Returns:
            list[dict]: 指标数据列表
        """
        if not HAS_PANDAS_TA:
            raise RuntimeError("pandas-ta 未安装")

        df = self._prepare_dataframe(kline_data)
        if df.empty:
            return []

        # 计算 MA
        ma_values = ta.sma(df["close"], length=period)

        # 转换为列表格式
        results = []
        for timestamp, value in ma_values.items():
            if pd.notna(value):
                results.append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(value),
                        "params": {"period": period},
                    }
                )

        return results

    async def calculate_ema(
        self, ticker: str, period: int, kline_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """计算指数移动平均线（EMA）.

        Args:
            ticker: 股票代码
            period: 周期参数（如 12, 26）
            kline_data: K线数据列表

        Returns:
            list[dict]: 指标数据列表
        """
        if not HAS_PANDAS_TA:
            raise RuntimeError("pandas-ta 未安装")

        df = self._prepare_dataframe(kline_data)
        if df.empty:
            return []

        # 计算 EMA
        ema_values = ta.ema(df["close"], length=period)

        # 转换为列表格式
        results = []
        for timestamp, value in ema_values.items():
            if pd.notna(value):
                results.append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(value),
                        "params": {"period": period},
                    }
                )

        return results

    async def calculate_rsi(
        self, ticker: str, period: int, kline_data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """计算相对强弱指标（RSI）.

        Args:
            ticker: 股票代码
            period: 周期参数（如 6, 12, 14）
            kline_data: K线数据列表

        Returns:
            list[dict]: 指标数据列表
        """
        if not HAS_PANDAS_TA:
            raise RuntimeError("pandas-ta 未安装")

        df = self._prepare_dataframe(kline_data)
        if df.empty:
            return []

        # 计算 RSI
        rsi_values = ta.rsi(df["close"], length=period)

        # 转换为列表格式
        results = []
        for timestamp, value in rsi_values.items():
            if pd.notna(value):
                results.append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(value),
                        "params": {"period": period},
                    }
                )

        return results

    async def calculate_macd(
        self,
        ticker: str,
        fast: int,
        slow: int,
        signal: int,
        kline_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """计算 MACD 指标.

        Args:
            ticker: 股票代码
            fast: 快速周期（如 12）
            slow: 慢速周期（如 26）
            signal: 信号周期（如 9）
            kline_data: K线数据列表

        Returns:
            dict: 包含 MACD_DIF, MACD_DEA, MACD_HIST 三个指标的数据
        """
        if not HAS_PANDAS_TA:
            raise RuntimeError("pandas-ta 未安装")

        df = self._prepare_dataframe(kline_data)
        if df.empty:
            return {"MACD_DIF": [], "MACD_DEA": [], "MACD_HIST": []}

        # 计算 MACD
        macd_df = ta.macd(df["close"], fast=fast, slow=slow, signal=signal)

        # 转换为列表格式
        results = {"MACD_DIF": [], "MACD_DEA": [], "MACD_HIST": []}

        # 检查 macd_df 是否为 None 或空
        if macd_df is None or macd_df.empty:
            return results

        # 获取实际的列名（pandas-ta 可能使用不同的命名格式）
        columns = macd_df.columns.tolist()
        macd_col = next((col for col in columns if "MACD_" in col and "s_" not in col and "h_" not in col), None)
        signal_col = next((col for col in columns if "MACDs_" in col), None)
        hist_col = next((col for col in columns if "MACDh_" in col), None)

        if not all([macd_col, signal_col, hist_col]):
            logger.warning(f"MACD 列名不匹配，可用列：{columns}")
            return results

        for timestamp in macd_df.index:
            params = {"fast": fast, "slow": slow, "signal": signal}

            # MACD_DIF (MACD line)
            macd_value = macd_df.loc[timestamp, macd_col]
            if pd.notna(macd_value):
                results["MACD_DIF"].append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(macd_value),
                        "params": params,
                    }
                )

            # MACD_DEA (Signal line)
            signal_value = macd_df.loc[timestamp, signal_col]
            if pd.notna(signal_value):
                results["MACD_DEA"].append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(signal_value),
                        "params": params,
                    }
                )

            # MACD_HIST (Histogram)
            hist_value = macd_df.loc[timestamp, hist_col]
            if pd.notna(hist_value):
                results["MACD_HIST"].append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(hist_value),
                        "params": params,
                    }
                )

        return results

    async def calculate_bollinger_bands(
        self,
        ticker: str,
        period: int,
        std_dev: float,
        kline_data: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """计算布林带（Bollinger Bands）.

        Args:
            ticker: 股票代码
            period: 周期参数（如 20）
            std_dev: 标准差倍数（如 2.0）
            kline_data: K线数据列表

        Returns:
            dict: 包含 BOLL_UP, BOLL_MID, BOLL_LOW 三个指标的数据
        """
        if not HAS_PANDAS_TA:
            raise RuntimeError("pandas-ta 未安装")

        df = self._prepare_dataframe(kline_data)
        if df.empty:
            return {"BOLL_UP": [], "BOLL_MID": [], "BOLL_LOW": []}

        # 计算布林带
        bbands_df = ta.bbands(df["close"], length=period, std=std_dev)

        # 转换为列表格式
        results = {"BOLL_UP": [], "BOLL_MID": [], "BOLL_LOW": []}

        # 检查 bbands_df 是否为 None 或空
        if bbands_df is None or bbands_df.empty:
            return results

        # 获取实际的列名（pandas-ta 可能使用不同的命名格式）
        columns = bbands_df.columns.tolist()
        # pandas-ta 实际返回的列名格式：BBL_20_2.0_2.0, BBM_20_2.0_2.0, BBU_20_2.0_2.0
        upper_col = next((col for col in columns if "BBU_" in col), None)
        mid_col = next((col for col in columns if "BBM_" in col), None)
        lower_col = next((col for col in columns if "BBL_" in col), None)

        if not all([upper_col, mid_col, lower_col]):
            logger.warning(f"布林带列名不匹配，可用列：{columns}")
            return results

        for timestamp in bbands_df.index:
            params = {"period": period, "std_dev": std_dev}

            # BOLL_UP (上轨)
            upper_value = bbands_df.loc[timestamp, upper_col]
            if pd.notna(upper_value):
                results["BOLL_UP"].append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(upper_value),
                        "params": params,
                    }
                )

            # BOLL_MID (中轨)
            mid_value = bbands_df.loc[timestamp, mid_col]
            if pd.notna(mid_value):
                results["BOLL_MID"].append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(mid_value),
                        "params": params,
                    }
                )

            # BOLL_LOW (下轨)
            lower_value = bbands_df.loc[timestamp, lower_col]
            if pd.notna(lower_value):
                results["BOLL_LOW"].append(
                    {
                        "timestamp": timestamp.to_pydatetime(),
                        "value": float(lower_value),
                        "params": params,
                    }
                )

        return results

    def get_supported_indicators(self) -> list[dict[str, Any]]:
        """获取支持的指标列表.

        Returns:
            list[dict]: 支持的指标列表
        """
        return [
            {
                "type": "MA",
                "name": "MA5",
                "description": "5日移动平均线",
                "params": {"period": 5},
            },
            {
                "type": "MA",
                "name": "MA10",
                "description": "10日移动平均线",
                "params": {"period": 10},
            },
            {
                "type": "MA",
                "name": "MA20",
                "description": "20日移动平均线",
                "params": {"period": 20},
            },
            {
                "type": "MA",
                "name": "MA60",
                "description": "60日移动平均线",
                "params": {"period": 60},
            },
            {
                "type": "EMA",
                "name": "EMA12",
                "description": "12日指数移动平均线",
                "params": {"period": 12},
            },
            {
                "type": "EMA",
                "name": "EMA26",
                "description": "26日指数移动平均线",
                "params": {"period": 26},
            },
            {
                "type": "RSI",
                "name": "RSI6",
                "description": "6日相对强弱指标",
                "params": {"period": 6},
            },
            {
                "type": "RSI",
                "name": "RSI12",
                "description": "12日相对强弱指标",
                "params": {"period": 12},
            },
            {
                "type": "RSI",
                "name": "RSI14",
                "description": "14日相对强弱指标",
                "params": {"period": 14},
            },
            {
                "type": "MACD",
                "name": "MACD_DIF",
                "description": "MACD 差离值（DIF）",
                "params": {"fast": 12, "slow": 26, "signal": 9},
            },
            {
                "type": "MACD",
                "name": "MACD_DEA",
                "description": "MACD 信号线（DEA）",
                "params": {"fast": 12, "slow": 26, "signal": 9},
            },
            {
                "type": "MACD",
                "name": "MACD_HIST",
                "description": "MACD 柱状图（HIST）",
                "params": {"fast": 12, "slow": 26, "signal": 9},
            },
            {
                "type": "BOLL",
                "name": "BOLL_UP",
                "description": "布林带上轨",
                "params": {"period": 20, "std_dev": 2.0},
            },
            {
                "type": "BOLL",
                "name": "BOLL_MID",
                "description": "布林带中轨",
                "params": {"period": 20, "std_dev": 2.0},
            },
            {
                "type": "BOLL",
                "name": "BOLL_LOW",
                "description": "布林带下轨",
                "params": {"period": 20, "std_dev": 2.0},
            },
        ]
