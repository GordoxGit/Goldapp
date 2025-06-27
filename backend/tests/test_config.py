from importlib import reload
from app import config


def test_settings_default(monkeypatch):
    monkeypatch.delenv("TTL", raising=False)
    reload(config)
    assert config.settings.ttl == 300


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("TTL", "10")
    reload(config)
    assert config.settings.ttl == 10
