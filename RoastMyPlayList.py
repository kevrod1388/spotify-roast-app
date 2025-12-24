# app.py
# Import spotipy, SpotifyOAuth, os, load_dotenv here

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import openai  # ← ADD THIS LINE

# Load environment variables from .env
load_dotenv(dotenv_path=".env")



# DEBUG: Check if keys are loading
st.write("Debug - Client ID:", os.getenv("SPOTIPY_CLIENT_ID"))
st.write("Debug - Client Secret starts with:", os.getenv("SPOTIPY_CLIENT_SECRET")[:4] if os.getenv("SPOTIPY_CLIENT_SECRET") else "None")
st.write("Current working directory:", os.getcwd())
st.write("Files in directory:", os.listdir())
st.write("Secret length:", len(os.getenv("SPOTIPY_CLIENT_SECRET") or "None"))


#st.write("Client ID:", os.getenv("SPOTIFY_CLIENT_ID"))
#st.write("Client Secret:", os.getenv("SPOTIFY_CLIENT_SECRET")[:4] + "..." if os.getenv("SPOTIFY_CLIENT_SECRET") else "None")


sp_oauth = SpotifyOAuth(
    client_id = os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri = "http://127.0.0.1:8501/",
    scope = "playlist-read-private playlist-read-collaborative"

)
# Set up Spotify OAuth
# - Use SpotifyOAuth with client_id, client_secret from env
# - redirect_uri = "http://localhost:8501"
# - scope = something that allows reading playlists (look up the exact scope)
# Handle the OAuth callback (when Spotify redirects back with ?code=...)
code = st.query_params.get("code")
if code:
    try:
        # Exchange the code for a token (this also caches it automatically)
        #sp_oauth.get_access_token(code)
        token_info = sp_oauth.get_access_token(code)
        st.success("✅ Logged in to Spotify successfully!")
        st.info("You can now paste a playlist URL below.")
        # Clean the URL and refresh the page
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

st.title("🔥 Roast My Playlist 🔥")

# Text input for user to paste Spotify playlist URL
playlist_url = st.text_area("Enter your playlist url: ")

if playlist_url:  # (check if input exists)
    try:
            token = sp_oauth.get_cached_token()
            
            # Hint: you'll probably need to handle the first-time login flow
            if token:


                sp = spotipy.Spotify(auth=token["access_token"])
                #playlist_id = playlist_url.split("/")[-1].split("?")[0]

                if "open.spotify.com/playlist/" in playlist_url:
                     playlist_id = playlist_url.split("open.spotify.com/playlist/")[1].split("?")[0].strip()

                else:
                     playlist_id = playlist_url.split("/")[-1].split("?")[0].strip()

                st.write("Extracted playlist ID:", playlist_id)  # Temporary debug — remove later
                st.write("ID length:", len(playlist_id))


                playlist = sp.playlist(playlist_id)

                playlist_name = playlist["name"]
                owner_name = playlist["owner"]["display_name"]

            
                st.write("logged in! Loading Playlist...")
                st.write("**Playlist**", playlist['name'])
                st.write("**By**", playlist['owner']['display_name'])
                
              
                
                tracks = []
                current_page = playlist['tracks']

                while current_page:
                     for item in current_page['items']:
                          if item['track']:
                               track = item['track']
                               artists = ", ".join(artist['name'] for artist in track['artists'])
                               tracks.append(f"{track['name']} by {artists}")

                     current_page = sp.next(current_page) if current_page['next'] else None

                st.write(f"**Total songs loaded:** {len(tracks)}")

                st.write("**Preview (first 20 songs):**")
                for song in tracks[:20]:
                     st.write(f"- {song}")

                st.session_state.playlist_name = playlist_name
                st.session_state.owner_name = owner_name
                st.session_state.tracks = tracks
                st.session_state.total_songs = len(tracks)

                st.success(f"Saved {st.session_state.total_songs} songs to memory! Ready for next steps.")

                st.markdown("---")

                if st.button("🔥 ROAST MY PLAYLIST 🔥", type="primary", use_container_width=True):
                     if st.session_state.total_songs > 0:
                          song_list = "\n".join(st.session_state.tracks)

                          prompt = f"""
                          You are the most savae, no-filter music cristic on the planet.
                          This person's playlist is called "{st.session_state.playlist_name}" and has {st.session_state.total_songs} songs.

                          {song_list}

                          Absolutely roast their music taste. Be hilarious, specific, brutal, and creative.
                          Call out artists, song choices, vibes, emotional damage — everything.
                          Don't hold back at all. Make it hurt (in a funny way).
                          End with a final score: "Overall music taste: X/10" and a one-line verdict.
                          """

                          #call open AI
                          try:
                               client = openai.OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
                               response = client.chat.completions.create(
                                    model = "gpt-4o-mini",
                                    messages=[{"role": "user", "content": prompt}],
                                    temperature=1.0,
                                    max_tokens=800
                               )
                               roast = response.choices[0].message.content 
                               st.markdown("## 🔥 THE ROAST 🔥")
                               st.markdown(roast)


                          except Exception as e:
                               st.error(f"AI roast failed: {e}")
                               st.info("check your OPENAI_API_KEY in .env")
                          

                     


            else:

                auth_url = sp_oauth.get_authorize_url()
                login_button = f'''
                <a href="{auth_url}" target="_blank">
                   <button style="background-color:#1DB954; color:white; padding:15px 30px; font-size:18px; border:none; border-radius:50px; cursor:pointer;">
                   Log in to Spotify
                   </button>
                </a>
                '''
                st.markdown(login_button, unsafe_allow_html=True)
                st.write("Click the button above to log in")

            # Create spotipy client with the token

            # Extract playlist ID from the URL
            # Hint: split the URL string to get the part after the last /

            # Fetch the playlist data
            # Hint: use sp.playlist() with the ID, ask for name and tracks

            # Display playlist name

            # Extract list of songs in format: "Song Name by Artist1, Artist2"
            # Loop through tracks['items'] and build a clean list

            # Show a preview of the first 10-15 songs

            # Save the song list and playlist name to st.session_state for later use
            pass

    except Exception as e:
        st.error(f"Error: {e}")
        st.error("Something went wrong")

        # Show error message if link is bad or auth fails