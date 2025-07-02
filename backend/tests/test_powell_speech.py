import requests
from datetime import datetime, timedelta

import pytest

from app.crud import fetch_powell_speech, POWELL_SPEECH_CACHE
from app.schemas import PowellSpeech


def _mock_response(mocker, text: str):
    resp = mocker.Mock()
    resp.text = text
    resp.raise_for_status.return_value = None
    return resp


def test_powell_speech_success(mocker):
    POWELL_SPEECH_CACHE.clear()
    now = datetime.utcnow()
    dt1 = (now + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S +0000")
    xml = (
        "<rss><channel>"
        f"<item><title>Powell remarks</title><link>https://a</link><description>x</description><pubDate>{dt1}</pubDate></item>"
        "</channel></rss>"
    )
    mocker.patch("requests.get", return_value=_mock_response(mocker, xml))

    data = fetch_powell_speech()

    assert isinstance(data, PowellSpeech)
    assert data.title == "Powell remarks"
    assert data.url == "https://a"
    assert data.date == (now + timedelta(days=1)).strftime("%Y-%m-%d")
    assert data.time == (now + timedelta(days=1)).strftime("%H:%M")


def test_powell_speech_none(mocker):
    POWELL_SPEECH_CACHE.clear()
    now = datetime.utcnow()
    past = (now - timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S +0000")
    xml = (
        "<rss><channel>"
        f"<item><title>No powell</title><link>x</link><description></description><pubDate>{past}</pubDate></item>"
        "</channel></rss>"
    )
    mocker.patch("requests.get", return_value=_mock_response(mocker, xml))

    data = fetch_powell_speech()

    assert data is None


def test_powell_speech_error(mocker):
    POWELL_SPEECH_CACHE.clear()
    mocker.patch("requests.get", side_effect=requests.RequestException)
    with pytest.raises(RuntimeError):
        fetch_powell_speech()


def test_powell_speech_parse_error(mocker):
    POWELL_SPEECH_CACHE.clear()
    xml = "<rss><channel><item>"
    mocker.patch("requests.get", return_value=_mock_response(mocker, xml))
    with pytest.raises(RuntimeError):
        fetch_powell_speech()


def test_powell_speech_cache(mocker):
    POWELL_SPEECH_CACHE.clear()
    future = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S +0000")
    xml = (
        "<rss><channel>"
        f"<item><title>Powell</title><link>u</link><description></description><pubDate>{future}</pubDate></item>"
        "</channel></rss>"
    )
    mock_get = mocker.patch("requests.get", return_value=_mock_response(mocker, xml))

    first = fetch_powell_speech()
    second = fetch_powell_speech()

    assert first is second
    assert mock_get.call_count == 1
