from typing import Optional

import httpx


class Gotify:
    _gotify_url: Optional[str]
    _gotify_token: Optional[str]
    _client_token: Optional[str]

    POST_ENABLED: bool = False
    FETCH_ENABLED: bool = False

    def __init__(
        self,
        token: Optional[str],
        url: Optional[str],
        client_token: Optional[str] = None,
    ):
        self._gotify_token = token
        self._gotify_url = url
        self._client_token = client_token
        self.POST_ENABLED = bool(token and url)
        self.FETCH_ENABLED = bool(client_token and url)

    def send_notification(self, title: str, message: str):
        if not self.POST_ENABLED:
            print("Gotify is not enabled. Skipping notification.")
            return
        if self._gotify_token and self._gotify_url:
            try:
                response = httpx.post(
                    f"{self._gotify_url}/message?token={self._gotify_token}",
                    json={"title": title, "message": message, "priority": 5},
                )
                response.raise_for_status()
            except Exception as e:
                print(f"Error sending Gotify notification: {e}")
        else:
            print("Gotify token or URL not configured. Skipping notification.")

    def fetch_notifications(self):
        if not self.POST_ENABLED:
            print("Gotify fetching is not enabled. Skipping fetch.")
            return []
        if self._gotify_token and self._gotify_url:
            try:
                response = httpx.get(
                    f"{self._gotify_url}/message?token={self._gotify_token}"
                )
                response.raise_for_status()
                return response.json().get("messages", [])
            except Exception as e:
                print(f"Error fetching Gotify notifications: {e}")
                return []
        else:
            print("Gotify token or URL not configured. Skipping fetch.")
            return []
