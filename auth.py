""" auth.py """
import http.server
import os
import time
import socketserver
import threading
import webbrowser
import urllib.parse
import random
import string
import hashlib
import base64
from dotenv import load_dotenv
import requests

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = "playlist-read-private playlist-read-collaborative user-read-email user-read-private"
REDIRECT_URI = "http://127.0.0.1:8501/"

AUTH_CODE = None
CODE_VERIFIER = None


def refresh_access_token(refresh_token):
    """Refresh the Spotify access token using the refresh token."""
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
        },
        timeout=60,
    )

    data = response.json()

    # Spotify may or may not return a new refresh token
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", refresh_token),
        "expires_at": time.time() + data.get("expires_in", 3600)
    }

# -------------------------
# PKCE generator
# -------------------------
def generate_pkce():
    """Generate a PKCE code challenge and verifier."""
    global CODE_VERIFIER

    CODE_VERIFIER = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(CODE_VERIFIER.encode()).digest()
    ).decode().replace("=", "")

    return challenge


# -------------------------
# Callback HTTP handler
# -------------------------
class Handler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler to capture the authorization code from Spotify callback."""
    def do_GET(self):
        global AUTH_CODE
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            AUTH_CODE = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"You can close this window now.")
        else:
            self.send_response(400)
            self.end_headers()


def start_server():
    """Start a temporary HTTP server to handle the Spotify callback."""
    with socketserver.TCPServer(("127.0.0.1", 8080), Handler) as httpd:
        httpd.handle_request()  # one request, then quit


def login_and_get_token(st):
    """Perform the OAuth2 login flow and return the token data."""
    global AUTH_CODE
    AUTH_CODE = None

    challenge = generate_pkce()

    url = (
        "https://accounts.spotify.com/authorize?"
        f"client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&code_challenge={challenge}"
        "&code_challenge_method=S256"
        f"&scope={SCOPES}"
    )

    # Start callback server in background
    threading.Thread(target=start_server, daemon=True).start()

    # Open Browser
    webbrowser.open(url)

    # Wait until AUTH_CODE is set
    while AUTH_CODE is None:
        time.sleep(1)

    # Exchange code for token
    token_res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": AUTH_CODE,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "code_verifier": CODE_VERIFIER,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )

    data =  token_res.json()

    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", "No refresh token returned"),
        "expires_at": time.time() + data.get("expires_in", 3600)
    }
