"""Displays the user's Spotify profile and playlists in a Streamlit app."""

import streamlit
import uuid
from spotify_client import SpotifyClient

def display(st: streamlit, client: SpotifyClient):
    """Display the user's Spotify profile and playlists."""



    user = client.get_user()
    profile_img_url = client.get_profile_image_url(user)
    col1, col2 = st.columns([1, 3])
    with col1:
        if profile_img_url:
            st.image(profile_img_url, width=96)
        else:
            st.write("👤")
    with col2:
        st.markdown(f"### {user.get('display_name', 'Spotify user')}")
        if user.get("country"):
            st.write(f"**{user.get('country')}**")



    if "playlists" not in st.session_state:
        st.session_state.playlists = []
    st.subheader("📝 Create Playlists")
    if st.button("➕ Playlist"):
        st.session_state.playlists.append({"id": uuid.uuid4(), "name": "", "description": "", "public": False})
        print("add")
        print(st.session_state.playlists)

    for index, playlist in enumerate(st.session_state.playlists):
        with st.container():
            cols = st.columns([8, 1])
            with cols[0]:
                playlist["name"] = st.text_input(f"Playlist Name #{index+1}", value=playlist["name"])
                playlist["description"] = st.text_area(f"Description #{index+1}", value=playlist["description"])
                playlist["public"] = st.checkbox("Public ?", value=playlist["public"], key=f"public_{index}")
            with cols[1]:
                if st.button("❌", key=f"del_{playlist['id']}"):
                    st.session_state.playlists.pop(index)
                    print("remove")
                    print(st.session_state.playlists)
                    st.rerun()

            st.write("---")


    # if st.button("Create All Playlists"):
    #     if not playlists:
    #         st.warning("Please add at least one playlist form.")
    #     else:
    #         for p in playlists:
    #             if not p["name"]:
    #                 st.error("Playlist name cannot be empty.")
    #                 continue

    #             with st.spinner(f"Creating playlist '{p['name']}'..."):
    #                 result = client.create_playlist(
    #                     name=p["name"],
    #                     description=p["description"],
    #                     public=p["public"]
    #                 )

    #             if "id" in result:
    #                 st.success(f"Playlist '{p['name']}' created successfully!")
    #             else:
    #                 st.error(f"Failed to create playlist: {result}")

            # Optionally clear the forms after creation
            # st.session_state.playlist_forms = []
