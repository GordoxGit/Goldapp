from app.crud import fetch_market_indices


def test_market_values_positive():
    data = fetch_market_indices()
    assert data.dxy_proxy_uup.value > 0
    assert data.volume_aggregated.value > 0
