""" auth.py """
import os
import time
import urllib.parse
import random
import string
import hashlib
import base64
import streamlit
from dotenv import load_dotenv
import requests

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = "playlist-read-private playlist-read-collaborative user-read-email user-read-private"
REDIRECT_URI = "http://127.0.0.1:8501/"

AUTH_CODE = None
CODE_VERIFIER = ''.join(random.choices(string.ascii_letters + string.digits, k=64))


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
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(CODE_VERIFIER.encode()).digest()
    ).decode().replace("=", "")

    return challenge


def login_and_get_token(st : streamlit):
    """Perform the OAuth2 login flow and return the token data."""
    st.write("Opening browser for Spotify login...")
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

    # Open Browser
    st.write(
        f"<meta http-equiv='refresh' content='0; url={url}'>",
        unsafe_allow_html=True
    )


def get_token(auth_code):
    """Exchange authorization code for access token."""

    token_res = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "code_verifier": CODE_VERIFIER,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )
    token_res.raise_for_status()
    data =  token_res.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", "No refresh token returned"),
        "expires_at": time.time() + data.get("expires_in", 3600)
    }

