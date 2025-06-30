from app.crud import fetch_market_indices, CACHE, fetch_fomc_next, FOMC_NEXT_CACHE


def test_market_indices_cache(mocker):
    CACHE.clear()
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.return_value.fast_info = {"last_price": 42, "last_volume": 1}
    first = fetch_market_indices()
    second = fetch_market_indices()
    assert first is second
    assert mock_ticker.call_count == 3


def test_fomc_next_cache(mocker):
    FOMC_NEXT_CACHE.clear()
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.text = (
        "<rss><channel>"
        "<item><title>A</title><link>u</link><start>2099-01-01T00:00:00Z</start></item>"
        "</channel></rss>"
    )
    mock_get.return_value.raise_for_status.return_value = None
    first = fetch_fomc_next()
    second = fetch_fomc_next()
    assert first is second
    assert mock_get.call_count == 1
