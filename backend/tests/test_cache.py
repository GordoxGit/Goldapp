from app.crud import fetch_market_indices, CACHE


def test_market_indices_cache(mocker):
    CACHE.clear()
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.return_value.fast_info = {"last_price": 42, "last_volume": 1}
    first = fetch_market_indices()
    second = fetch_market_indices()
    assert first is second
    assert mock_ticker.call_count == 3
