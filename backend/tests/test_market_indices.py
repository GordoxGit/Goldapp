from app.crud import fetch_market_indices


def test_market_values_positive(mocker):
    """fetch_market_indices should aggregate mocked yfinance data"""
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.return_value.fast_info = {
        "last_price": 100,
        "last_volume": 1_000_000,
    }

    data = fetch_market_indices()

    assert data.dxy_proxy_uup.value == 100
    assert data.volume_aggregated.value == 2_000_000
