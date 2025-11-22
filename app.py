""" # app.py """
import streamlit as st
from auth2 import login_and_get_token, get_token
from spotify_client import SpotifyClient
from window import display

st.title("Spotify Manager")

if "token_data" not in st.session_state:
    st.session_state.token_data = None

if not st.session_state.token_data and st.query_params.get("code"):
    st.session_state.token_data = get_token(st.query_params)

if st.session_state.token_data and st.session_state.token_data.get("access_token"):
    client = SpotifyClient(st.session_state.token_data, st.session_state)
    display(st , client)
else :
    st.write("Waiting for authentication...")
    if st.button("Login with Spotify"):
        login_and_get_token()
