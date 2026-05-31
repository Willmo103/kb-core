import pytest
from kb_core.notifier import Gotify


def test_gotify_init():
    # Test initialization with various parameters
    g_disabled = Gotify(None, None)
    assert not g_disabled.POST_ENABLED
    assert not g_disabled.FETCH_ENABLED

    g_post_only = Gotify("token_123", "http://gotify.local")
    assert g_post_only.POST_ENABLED
    assert not g_post_only.FETCH_ENABLED

    g_both = Gotify("token_123", "http://gotify.local", client_token="client_456")
    assert g_both.POST_ENABLED
    assert g_both.FETCH_ENABLED


def test_send_notification_disabled(mocker):
    mock_post = mocker.patch("httpx.post")
    g = Gotify(None, None)
    g.send_notification("Title", "Message")
    mock_post.assert_not_called()


def test_send_notification_success(mocker):
    mock_post = mocker.patch("httpx.post")
    mock_post.return_value.raise_for_status = mocker.Mock()

    g = Gotify("token_123", "http://gotify.local")
    g.send_notification("Test Title", "Test Message")

    mock_post.assert_called_once_with(
        "http://gotify.local/message?token=token_123",
        json={"title": "Test Title", "message": "Test Message", "priority": 5},
    )


def test_send_notification_error(mocker, capsys):
    mock_post = mocker.patch("httpx.post", side_effect=Exception("Connection refused"))
    g = Gotify("token_123", "http://gotify.local")
    g.send_notification("Test Title", "Test Message")

    # Check that error was handled gracefully and printed
    captured = capsys.readouterr()
    assert "Error sending Gotify notification: Connection refused" in captured.out


def test_fetch_notifications_disabled(mocker):
    mock_get = mocker.patch("httpx.get")
    g = Gotify(None, None)
    messages = g.fetch_notifications()
    assert messages == []
    mock_get.assert_not_called()


def test_fetch_notifications_success(mocker):
    mock_get = mocker.patch("httpx.get")
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "messages": [
            {"id": 1, "title": "Msg 1", "message": "Hello"},
            {"id": 2, "title": "Msg 2", "message": "World"},
        ]
    }
    mock_response.raise_for_status = mocker.Mock()
    mock_get.return_value = mock_response

    g = Gotify("token_123", "http://gotify.local", client_token="client_456")
    messages = g.fetch_notifications()

    mock_get.assert_called_once_with("http://gotify.local/message?token=client_456")
    assert len(messages) == 2
    assert messages[0]["title"] == "Msg 1"


def test_fetch_notifications_error(mocker, capsys):
    mock_get = mocker.patch("httpx.get", side_effect=Exception("HTTP Error"))
    g = Gotify("token_123", "http://gotify.local", client_token="client_456")
    messages = g.fetch_notifications()

    assert messages == []
    captured = capsys.readouterr()
    assert "Error fetching Gotify notifications: HTTP Error" in captured.out
