"""spotify_client.py"""

import time
import requests
from auth import refresh_access_token

class SpotifyClient:
    """A simple Spotify API client that handles token refreshing."""
    def __init__(self, token_data, session_state):
        self.token_data = token_data
        self.session_state = session_state
        self.user = None

    def ensure_token_valid(self):
        """Refresh the access token if it has expired."""
        if time.time() >= self.token_data["expires_at"]:
            new_data = refresh_access_token(self.token_data["refresh_token"])
            self.session_state.token_data = new_data
            self.token_data = new_data

    def request(self, url, method="GET", payload=None, timeout=60, retry_attempt=0):
        """Make an authenticated GET request to the Spotify API."""
        self.ensure_token_valid()

        if method == "GET":
            r = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.token_data['access_token']}"},
                timeout=timeout
            )
        elif method == "POST":
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.token_data['access_token']}"},
                json=payload,
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # If expired unexpectedly → refresh + retry once
        if r.status_code == 401 and retry_attempt < 3:
            new_data = refresh_access_token(self.token_data["refresh_token"])
            self.session_state.token_data = new_data
            self.token_data = new_data

            self.request(url, method, payload, retry_attempt + 1)

        return r.json()

    def get_user(self):
        """Get the current user's profile information."""
        self.user = self.request("https://api.spotify.com/v1/me")
        return self.user

    def get_profile_image_url(self, user: dict | None = None) -> str | None:
        """Return the current user's profile image URL (largest image) or None."""
        if self.user is None:
            self.user = self.get_user()

        images = self.user.get("images") or []
        if not images:
            return None

        # Spotify returns list of images; first is usually largest
        return images[0].get("url")

    def get_liked_songs(self, limit=50):
        """Return the user's saved tracks."""
        url = f"https://api.spotify.com/v1/me/tracks?limit={limit}"
        return self.request(url)

    def create_playlist(self, name, description="", public=False):
        """Create a new playlist for the user."""
        if self.user is None:
            self.user = self.get_user()

        user_id = self.user.get("id")

        payload = {
            "name": name,
            "description": description,
            "public": public
        }
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

        res = self.request(url, method="POST", payload=payload)

        return res
