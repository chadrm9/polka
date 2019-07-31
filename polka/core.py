from spotipy.util import prompt_for_user_token
from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy.client import SpotifyException
import spotipy


# do oauth2 authorization or client credentials flow
def do_auth(username="", scope="user-library-read"):
    token = None
    if username:
        token = prompt_for_user_token(username, scope)
    return spotipy.Spotify(auth=token, requests_session=True, client_credentials_manager=SpotifyClientCredentials())
