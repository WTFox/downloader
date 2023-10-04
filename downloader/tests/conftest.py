from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def no_pushover_creds(monkeypatch):
    monkeypatch.delenv("PUSHOVER_USER", raising=False)
    monkeypatch.delenv("PUSHOVER_TOKEN", raising=False)


@pytest.fixture
def mock_http_post():
    mock = Mock()
    mock.json.return_value = {"status": 1, "request": "123"}
    return mock
