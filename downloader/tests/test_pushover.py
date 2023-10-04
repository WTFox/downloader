import os

from downloader.constants import Constants as c
from downloader.pushover import notify


def test__pushover_url_constant():
    assert c.PUSHOVER_URL == "https://api.pushover.net/1/messages.json"


def test__notify__missing_credentials__no_notification(mock_http_post, mocker):
    mocker.patch.object(os.environ, "get", return_value=None)
    notify("test message", post=mock_http_post)
    assert not mock_http_post.called


def test__notify__sends_notification(mock_http_post):
    notify("test message", user="user", token="token", post=mock_http_post)
    assert mock_http_post.called is True
    mock_http_post.assert_called_once_with(
        c.PUSHOVER_URL,
        data={
            "user": "user",
            "token": "token",
            "title": "Downloader",
            "message": "test message",
        },
    )
