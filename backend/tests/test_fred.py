import requests
import pytest

from app.crud import fetch_fed_rate, fetch_vix, FRED_RATE_CACHE, VIX_CACHE
from app.config import settings


def _mock_response(mocker, payload):
    resp = mocker.Mock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_fed_rate_success(mocker):
    FRED_RATE_CACHE.clear()
    mock_get = mocker.patch("requests.get")
    payload = {"observations": [{"value": "5.0", "date": "2024-06-13"}]}
    mock_get.return_value = _mock_response(mocker, payload)
    mocker.patch.object(settings, "fred_api_key", "KEY")

    data = fetch_fed_rate()

    assert data.value == 5.0
    assert data.date == "2024-06-13"
    assert data.source == "FRED"


def test_fed_rate_no_key(mocker):
    FRED_RATE_CACHE.clear()
    mocker.patch.object(settings, "fred_api_key", None)
    with pytest.raises(RuntimeError):
        fetch_fed_rate()


def test_fed_rate_unavailable(mocker):
    FRED_RATE_CACHE.clear()
    mocker.patch.object(settings, "fred_api_key", "KEY")
    mocker.patch("requests.get", side_effect=requests.RequestException)
    with pytest.raises(RuntimeError):
        fetch_fed_rate()


def test_vix_success(mocker):
    VIX_CACHE.clear()
    mock_get = mocker.patch("requests.get")
    payload = {"observations": [{"value": "15.5", "date": "2024-06-14"}]}
    mock_get.return_value = _mock_response(mocker, payload)
    mocker.patch.object(settings, "fred_api_key", "KEY")

    data = fetch_vix()

    assert data.value == 15.5
    assert data.date == "2024-06-14"
    assert data.source == "FRED"


def test_vix_no_key(mocker):
    VIX_CACHE.clear()
    mocker.patch.object(settings, "fred_api_key", None)
    with pytest.raises(RuntimeError):
        fetch_vix()


def test_vix_unavailable(mocker):
    VIX_CACHE.clear()
    mocker.patch.object(settings, "fred_api_key", "KEY")
    mocker.patch("requests.get", side_effect=requests.RequestException)
    with pytest.raises(RuntimeError):
        fetch_vix()

