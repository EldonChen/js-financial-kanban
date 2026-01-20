"""数据准确性检查服务."""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class AccuracyChecker:
    """数据准确性检查服务."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """初始化准确性检查服务.
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db["kline_data"]
    
    async def check_abnormal_values(
        self,
        ticker: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """检查异常值（价格突变、成交量异常）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 异常值列表
        """
        logger.info(f"检查 {ticker} 的异常值（{start_date} - {end_date}）")
        
        abnormal_data = []
        
        # 查询数据
        cursor = self.collection.find(
            {
                "metadata.ticker": ticker,
                "metadata.period": period,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        ).sort("timestamp", 1)
        
        prev_close = None
        data_list = []
        
        async for doc in cursor:
            data_list.append(doc)
        
        if not data_list:
            return abnormal_data
        
        # 计算平均值，用于检测异常
        avg_close = sum(d.get("close", 0) for d in data_list) / len(data_list)
        avg_volume = sum(d.get("volume", 0) for d in data_list) / len(data_list)
        
        # 检查每条数据
        for doc in data_list:
            timestamp = doc.get("timestamp")
            close_price = doc.get("close")
            volume = doc.get("volume")
            
            # 检查价格突变（与平均值偏离超过 50%）
            if close_price and avg_close:
                deviation = abs(close_price - avg_close) / avg_close
                if deviation > 0.5:
                    abnormal_data.append({
                        "ticker": ticker,
                        "timestamp": timestamp,
                        "type": "price_deviation",
                        "value": close_price,
                        "average": avg_close,
                        "deviation": deviation,
                        "description": f"收盘价偏离平均值 {deviation * 100:.2f}%"
                    })
            
            # 检查成交量异常（超过平均值 10 倍）
            if volume and avg_volume:
                if volume > avg_volume * 10:
                    abnormal_data.append({
                        "ticker": ticker,
                        "timestamp": timestamp,
                        "type": "volume_spike",
                        "value": volume,
                        "average": avg_volume,
                        "ratio": volume / avg_volume,
                        "description": f"成交量异常高（是平均值的 {volume / avg_volume:.2f} 倍）"
                    })
            
            # 检查与前一天的价格突变（涨跌幅超过 30%）
            if prev_close and close_price:
                change = abs(close_price - prev_close) / prev_close
                if change > 0.3:
                    abnormal_data.append({
                        "ticker": ticker,
                        "timestamp": timestamp,
                        "type": "price_change",
                        "prev_close": prev_close,
                        "close": close_price,
                        "change": change,
                        "description": f"价格突变（涨跌幅 {change * 100:.2f}%）"
                    })
            
            prev_close = close_price
        
        if abnormal_data:
            logger.warning(f"{ticker} 发现 {len(abnormal_data)} 个异常值")
        else:
            logger.info(f"{ticker} 数据正常，无异常值")
        
        return abnormal_data
    
    async def check_price_reasonableness(
        self,
        ticker: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """检查价格合理性（价格范围、涨跌幅限制）.
        
        Args:
            ticker: 股票代码
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 不合理的数据列表
        """
        logger.info(f"检查 {ticker} 的价格合理性（{start_date} - {end_date}）")
        
        unreasonable_data = []
        
        # 查询数据
        cursor = self.collection.find(
            {
                "metadata.ticker": ticker,
                "metadata.period": period,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        ).sort("timestamp", 1)
        
        async for doc in cursor:
            timestamp = doc.get("timestamp")
            open_price = doc.get("open")
            close_price = doc.get("close")
            
            # 检查价格是否为 0 或负数
            if open_price is not None and open_price <= 0:
                unreasonable_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "invalid_price",
                    "field": "open",
                    "value": open_price,
                    "description": "开盘价为 0 或负数"
                })
            
            if close_price is not None and close_price <= 0:
                unreasonable_data.append({
                    "ticker": ticker,
                    "timestamp": timestamp,
                    "type": "invalid_price",
                    "field": "close",
                    "value": close_price,
                    "description": "收盘价为 0 或负数"
                })
        
        if unreasonable_data:
            logger.warning(f"{ticker} 发现 {len(unreasonable_data)} 个不合理的价格")
        else:
            logger.info(f"{ticker} 价格合理")
        
        return unreasonable_data
