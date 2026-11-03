import pytest
import requests


@pytest.fixture(autouse=True)
def disallow_network(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("Offline tests must mock HTTP requests.")

    monkeypatch.setattr(requests.sessions.Session, "request", fail)
