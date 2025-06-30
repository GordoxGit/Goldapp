import requests
from datetime import datetime, timedelta

import pytest

from app.crud import fetch_fomc_next, FOMC_NEXT_CACHE
from app.schemas import FomcNext


def _mock_response(mocker, text: str):
    resp = mocker.Mock()
    resp.text = text
    resp.raise_for_status.return_value = None
    return resp


def test_fomc_next_success(mocker):
    FOMC_NEXT_CACHE.clear()
    now = datetime.utcnow()
    dt1 = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    dt2 = (now + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    xml = f"""
    <rss><channel>
        <item><title>First</title><link>https://a</link><start>{dt1}</start></item>
        <item><title>Second</title><link>https://b</link><start>{dt2}</start></item>
    </channel></rss>
    """
    mocker.patch("requests.get", return_value=_mock_response(mocker, xml))

    data = fetch_fomc_next()

    assert isinstance(data, FomcNext)
    assert data.title == "First"
    assert data.url == "https://a"
    assert data.date == (now + timedelta(days=1)).strftime("%Y-%m-%d")
    assert data.time == (now + timedelta(days=1)).strftime("%H:%M")


def test_fomc_next_none(mocker):
    FOMC_NEXT_CACHE.clear()
    now = datetime.utcnow()
    past = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    xml = f"<rss><channel><item><title>Past</title><link>x</link><start>{past}</start></item></channel></rss>"
    mocker.patch("requests.get", return_value=_mock_response(mocker, xml))

    data = fetch_fomc_next()

    assert data is None


def test_fomc_next_error(mocker):
    FOMC_NEXT_CACHE.clear()
    mocker.patch("requests.get", side_effect=requests.RequestException)
    with pytest.raises(RuntimeError):
        fetch_fomc_next()


def test_fomc_next_parse_error(mocker):
    FOMC_NEXT_CACHE.clear()
    xml = "<rss><channel><item>"
    mocker.patch("requests.get", return_value=_mock_response(mocker, xml))
    with pytest.raises(RuntimeError):
        fetch_fomc_next()
