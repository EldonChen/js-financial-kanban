"""字段映射器，将不同数据源的字段映射到统一格式."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FieldMapper:
    """字段映射器，将不同数据源的字段映射到统一格式."""

    @staticmethod
    def map_yfinance(info: Dict[str, Any]) -> Dict[str, Any]:
        """映射 yfinance 数据.
        
        Args:
            info: yfinance 返回的股票信息字典
        
        Returns:
            统一格式的股票数据字典
        """
        return {
            "ticker": info.get("symbol", "").strip().upper(),
            "name": (
                info.get("longName")
                or info.get("shortName")
                or info.get("name")
                or ""
            ).strip(),
            "market": (info.get("exchange") or "").strip(),
            "market_type": FieldMapper._determine_market_type(
                info.get("exchange", "")
            ),
            "sector": (info.get("sector") or "").strip(),
            "industry": (info.get("industry") or "").strip(),
            "currency": (info.get("currency") or "").strip().upper(),
            "exchange": (info.get("exchange") or "").strip(),
            "country": (info.get("country") or "").strip(),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "data_source": "yfinance",
        }

    @staticmethod
    def map_akshare(data: Dict[str, Any]) -> Dict[str, Any]:
        """映射 akshare 数据.
        
        Args:
            data: akshare 返回的股票信息字典
        
        Returns:
            统一格式的股票数据字典
        """
        # akshare 返回的数据可能是 DataFrame 转换的字典，字段名可能是中文
        # 需要处理不同的字段名格式
        # stock_zh_a_spot_em 返回的字段：代码、名称、最新价、涨跌幅等
        # stock_individual_info_em 返回的字段：股票简称、行业、地区等
        ticker = (
            data.get("code")
            or data.get("代码")
            or data.get("ts_code", "").split(".")[0]
            or ""
        ).strip()

        name = (
            data.get("name")
            or data.get("名称")
            or data.get("股票简称")
            or data.get("name", "")
            or ""
        ).strip()

        # 从代码判断交易所（A股：6位数字，0/3开头是深交所，6开头是上交所）
        market_type = "A股"
        if ticker and len(ticker) == 6 and ticker.isdigit():
            if ticker.startswith(("0", "3")):
                market = "SZSE"
                exchange = "SZSE"
            elif ticker.startswith("6"):
                market = "SSE"
                exchange = "SSE"
            else:
                market = "SSE"  # 默认
                exchange = "SSE"
        else:
            # 尝试从其他字段获取
            exchange = (
                data.get("exchange")
                or data.get("交易所")
                or data.get("exchange", "")
                or ""
            ).strip()
            if exchange in ["SSE", "上交所", "上海"]:
                market = "SSE"
            elif exchange in ["SZSE", "深交所", "深圳"]:
                market = "SZSE"
            else:
                market = exchange or "SSE"

        # 行业信息（可能来自不同接口）
        sector = (
            data.get("industry")
            or data.get("行业")
            or data.get("sector", "")
            or data.get("所属行业", "")
            or ""
        ).strip()

        industry = (
            data.get("industry")
            or data.get("行业")
            or data.get("industry", "")
            or data.get("所属行业", "")
            or ""
        ).strip()

        return {
            "ticker": ticker.upper(),
            "name": name,
            "market": market,
            "market_type": market_type,
            "sector": sector,
            "industry": industry,
            "currency": "CNY",
            "exchange": exchange,
            "country": "China",
            "listing_date": FieldMapper._parse_date(
                data.get("list_date") or data.get("上市日期")
            ),
            "data_source": "akshare",
        }

    @staticmethod
    def map_tushare(data: Dict[str, Any]) -> Dict[str, Any]:
        """映射 Tushare 数据.
        
        Args:
            data: Tushare 返回的股票信息字典
        
        Returns:
            统一格式的股票数据字典
        """
        ts_code = data.get("ts_code", "")
        ticker = ts_code.split(".")[0] if ts_code else ""

        exchange = data.get("exchange", "")
        market = exchange
        if exchange == "SSE":
            market = "SSE"
        elif exchange == "SZSE":
            market = "SZSE"

        return {
            "ticker": ticker.upper(),
            "name": (data.get("name") or "").strip(),
            "market": market,
            "market_type": "A股",
            "sector": (data.get("industry") or "").strip(),
            "industry": (data.get("industry") or "").strip(),
            "currency": "CNY",
            "exchange": exchange,
            "country": "China",
            "listing_date": FieldMapper._parse_date(data.get("list_date")),
            "data_source": "tushare",
        }

    @staticmethod
    def map_easyquotation(data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """映射 easyquotation 数据.
        
        Args:
            data: easyquotation 返回的股票信息字典
            ticker: 股票代码
        
        Returns:
            统一格式的股票数据字典
        """
        return {
            "ticker": ticker.upper(),
            "name": (data.get("name") or "").strip(),
            "market": "A股",  # easyquotation 主要用于 A 股
            "market_type": "A股",
            "currency": "CNY",
            "country": "China",
            "data_source": "easyquotation",
        }

    @staticmethod
    def _determine_market_type(exchange: str) -> str:
        """根据交易所判断市场类型.
        
        Args:
            exchange: 交易所代码
        
        Returns:
            市场类型
        """
        exchange_upper = exchange.upper()
        if exchange_upper in ["NASDAQ", "NYSE", "AMEX"]:
            return "美股"
        elif exchange_upper in ["HKEX", "SEHK"]:
            return "港股"
        elif exchange_upper in ["SSE", "SZSE"]:
            return "A股"
        return "未知"

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串.
        
        Args:
            date_str: 日期字符串（格式可能是 YYYYMMDD 或 YYYY-MM-DD）
        
        Returns:
            datetime 对象，如果解析失败返回 None
        """
        if not date_str:
            return None

        try:
            # 尝试 YYYYMMDD 格式
            if len(date_str) == 8 and date_str.isdigit():
                return datetime.strptime(date_str, "%Y%m%d")
            # 尝试 YYYY-MM-DD 格式
            elif len(date_str) == 10:
                return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            logger.warning(f"解析日期失败: {date_str}, 错误: {e}")

        return None

    @staticmethod
    def clean_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗字段：处理空字符串和 None.
        
        Args:
            data: 股票数据字典
        
        Returns:
            清洗后的股票数据字典
        """
        cleaned = {}
        for key, value in data.items():
            if value == "":
                cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
