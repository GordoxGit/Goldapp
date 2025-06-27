import requests

import pytest

from app.crud import fetch_latest_macro, MACRO_CACHE


def _mock_response(mocker, payload):
    resp = mocker.Mock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_latest_macro_success(mocker):
    """Return the most recent between CPI and NFP."""
    MACRO_CACHE.clear()
    mock_get = mocker.patch("requests.get")

    cpi_payload = {
        "Results": {"series": [{"data": [{"year": "2024", "period": "M05", "value": "310"}]}]}
    }
    nfp_payload = {
        "Results": {"series": [{"data": [{"year": "2024", "period": "M06", "value": "150000"}]}]}
    }

    mock_get.side_effect = [
        _mock_response(mocker, cpi_payload),
        _mock_response(mocker, nfp_payload),
    ]

    data = fetch_latest_macro()

    assert data.latest_macro.name == "NFP"
    assert data.latest_macro.date == "2024-06"
    assert data.latest_macro.unit == "k jobs"


def test_latest_macro_unavailable(mocker):
    """Any request error should bubble up as RuntimeError."""
    MACRO_CACHE.clear()
    mock_get = mocker.patch("requests.get", side_effect=requests.RequestException)

    with pytest.raises(RuntimeError):
        fetch_latest_macro()

