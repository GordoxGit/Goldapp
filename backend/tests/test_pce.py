import requests
import pytest

from app.crud import fetch_pce, PCE_CACHE
from app.config import settings


def _mock_response(mocker, payload):
    resp = mocker.Mock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_pce_success(mocker):
    """fetch_pce should return the most recent PCE value."""
    PCE_CACHE.clear()
    mock_get = mocker.patch("requests.get")
    payload = {
        "BEAAPI": {
            "Results": {
                "Data": [
                    {"TimePeriod": "2024M04", "DataValue": "0.2"},
                    {"TimePeriod": "2024M05", "DataValue": "0.1"},
                ]
            }
        }
    }
    mock_get.return_value = _mock_response(mocker, payload)
    mocker.patch.object(settings, "bea_api_key", "KEY")

    data = fetch_pce()

    assert data.name == "PCE"
    assert data.value == 0.1
    assert data.date == "2024-05"
    assert data.unit == "%"
    assert data.source == "BEA"


def test_pce_no_key(mocker):
    """Missing API key should raise RuntimeError."""
    PCE_CACHE.clear()
    mocker.patch.object(settings, "bea_api_key", None)
    with pytest.raises(RuntimeError):
        fetch_pce()


def test_pce_unavailable(mocker):
    """Network issues should bubble up as RuntimeError."""
    PCE_CACHE.clear()
    mocker.patch.object(settings, "bea_api_key", "KEY")
    mocker.patch("requests.get", side_effect=requests.RequestException)
    with pytest.raises(RuntimeError):
        fetch_pce()
