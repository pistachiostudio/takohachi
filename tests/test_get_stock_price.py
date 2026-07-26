from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from libs.utils import get_stock_price


def _mock_history(closes):
    df = pd.DataFrame({"Close": closes})
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = df
    return mock_ticker


@patch("libs.utils.yf.Ticker")
def test_get_stock_price_normal(mock_ticker_cls):
    mock_ticker_cls.return_value = _mock_history([100.0, 105.0])

    day_before_ratio, stock_today = get_stock_price("DUMMY")

    assert stock_today == 105.0
    assert day_before_ratio == "+5.0"


@patch("libs.utils.yf.Ticker")
def test_get_stock_price_single_row(mock_ticker_cls):
    # ^N225 で実際に発生したケース: 1行しか返らない
    mock_ticker_cls.return_value = _mock_history([100.0])

    with pytest.raises(ValueError):
        get_stock_price("^N225")


@patch("libs.utils.yf.Ticker")
def test_get_stock_price_latest_close_is_nan(mock_ticker_cls):
    # ^GSPC / ^IXIC で実際に発生したケース: 最新のCloseがNaN
    mock_ticker_cls.return_value = _mock_history([100.0, 105.0, None])

    day_before_ratio, stock_today = get_stock_price("^GSPC")

    assert stock_today == 105.0
    assert day_before_ratio == "+5.0"


@patch("libs.utils.yf.Ticker")
def test_get_stock_price_all_nan(mock_ticker_cls):
    mock_ticker_cls.return_value = _mock_history([None, None])

    with pytest.raises(ValueError):
        get_stock_price("DUMMY")
