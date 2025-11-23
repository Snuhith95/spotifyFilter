import streamlit as st
from auth import login_and_get_token, get_token
from spotify_client import SpotifyClient
from window import display

st.title("Spotify Manager")

@st.cache_resource
def get_token_data():
    """Retrieve token data from session state."""
    return None

token_data = get_token_data() #pylint: disable=

if not token_data and st.query_params.get("code"):
    token_data = get_token(st.query_params.get("code"))

if token_data and token_data.get("access_token"):
    client = SpotifyClient(token_data, st.session_state)
    display(st , client)
else :
    st.write("Waiting for authentication...")
    if st.button("Login with Spotify"):
        login_and_get_token(st)
