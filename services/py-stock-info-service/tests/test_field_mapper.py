"""字段映射器测试."""

import pytest
from datetime import datetime
from app.services.providers.field_mapper import FieldMapper


class TestFieldMapper:
    """FieldMapper 测试类."""

    def test_map_yfinance(self):
        """测试映射 yfinance 数据."""
        yfinance_data = {
            "symbol": "AAPL",
            "longName": "Apple Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "currency": "USD",
            "country": "United States",
            "marketCap": 3000000000000,
            "trailingPE": 30.5,
            "priceToBook": 45.2,
            "dividendYield": 0.005,
        }

        result = FieldMapper.map_yfinance(yfinance_data)

        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["market"] == "NASDAQ"
        assert result["market_type"] == "美股"
        assert result["sector"] == "Technology"
        assert result["industry"] == "Consumer Electronics"
        assert result["currency"] == "USD"
        assert result["country"] == "United States"
        assert result["market_cap"] == 3000000000000
        assert result["pe_ratio"] == 30.5
        assert result["pb_ratio"] == 45.2
        assert result["dividend_yield"] == 0.005
        assert result["data_source"] == "yfinance"

    def test_map_yfinance_short_name(self):
        """测试映射 yfinance 数据（使用 shortName）."""
        yfinance_data = {
            "symbol": "AAPL",
            "shortName": "Apple",
            "exchange": "NASDAQ",
        }

        result = FieldMapper.map_yfinance(yfinance_data)

        assert result["name"] == "Apple"

    def test_map_akshare(self):
        """测试映射 akshare 数据."""
        akshare_data = {
            "code": "000001",
            "名称": "平安银行",
            "行业": "银行",
            "地区": "深圳",
            "交易所": "SZSE",
            "上市日期": "1991-04-03",
        }

        result = FieldMapper.map_akshare(akshare_data)

        assert result["ticker"] == "000001"
        assert result["name"] == "平安银行"
        assert result["market"] == "SZSE"
        assert result["market_type"] == "A股"
        assert result["sector"] == "银行"
        assert result["industry"] == "银行"
        assert result["currency"] == "CNY"
        assert result["exchange"] == "SZSE"
        assert result["country"] == "China"
        assert result["data_source"] == "akshare"

    def test_map_akshare_english_fields(self):
        """测试映射 akshare 数据（英文字段名）."""
        akshare_data = {
            "code": "000001",
            "name": "平安银行",
            "industry": "银行",
            "exchange": "SZSE",
        }

        result = FieldMapper.map_akshare(akshare_data)

        assert result["ticker"] == "000001"
        assert result["name"] == "平安银行"

    def test_map_tushare(self):
        """测试映射 Tushare 数据."""
        tushare_data = {
            "ts_code": "000001.SZ",
            "name": "平安银行",
            "exchange": "SZSE",
            "industry": "银行",
            "list_date": "19910403",
        }

        result = FieldMapper.map_tushare(tushare_data)

        assert result["ticker"] == "000001"
        assert result["name"] == "平安银行"
        assert result["market"] == "SZSE"
        assert result["market_type"] == "A股"
        assert result["currency"] == "CNY"
        assert result["exchange"] == "SZSE"
        assert result["country"] == "China"
        assert result["data_source"] == "tushare"

    def test_map_easyquotation(self):
        """测试映射 easyquotation 数据."""
        easyquotation_data = {
            "name": "平安银行",
            "now": 12.34,
            "open": 12.00,
        }

        result = FieldMapper.map_easyquotation(easyquotation_data, "000001")

        assert result["ticker"] == "000001"
        assert result["name"] == "平安银行"
        assert result["market_type"] == "A股"
        assert result["currency"] == "CNY"
        assert result["country"] == "China"
        assert result["data_source"] == "easyquotation"

    def test_determine_market_type(self):
        """测试市场类型判断."""
        assert FieldMapper._determine_market_type("NASDAQ") == "美股"
        assert FieldMapper._determine_market_type("NYSE") == "美股"
        assert FieldMapper._determine_market_type("HKEX") == "港股"
        assert FieldMapper._determine_market_type("SSE") == "A股"
        assert FieldMapper._determine_market_type("SZSE") == "A股"
        assert FieldMapper._determine_market_type("UNKNOWN") == "未知"

    def test_parse_date_yyyymmdd(self):
        """测试解析日期（YYYYMMDD 格式）."""
        result = FieldMapper._parse_date("19910403")

        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 1991
        assert result.month == 4
        assert result.day == 3

    def test_parse_date_yyyy_mm_dd(self):
        """测试解析日期（YYYY-MM-DD 格式）."""
        result = FieldMapper._parse_date("1991-04-03")

        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 1991
        assert result.month == 4
        assert result.day == 3

    def test_parse_date_invalid(self):
        """测试解析无效日期."""
        result = FieldMapper._parse_date("invalid")

        assert result is None

    def test_parse_date_none(self):
        """测试解析 None 日期."""
        result = FieldMapper._parse_date(None)

        assert result is None

    def test_clean_fields(self):
        """测试字段清洗."""
        data = {
            "ticker": "AAPL",
            "name": "Apple",
            "market": "",
            "sector": None,
            "industry": "Technology",
        }

        result = FieldMapper.clean_fields(data)

        assert result["ticker"] == "AAPL"
        assert result["name"] == "Apple"
        assert result["market"] is None  # 空字符串转换为 None
        assert result["sector"] is None
        assert result["industry"] == "Technology"
