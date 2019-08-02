# crm 2019
from spotipy.util import prompt_for_user_token
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.client import SpotifyException
import spotipy

import logging
logger = logging.getLogger(__name__)


# do oauth2 authorization or client credentials flow
def do_auth(username=""):
    token = None
    if username:
        scope = "playlist-read-collaborative playlist-modify-public"
        token = prompt_for_user_token(username, scope)
        if not token:
            logger.warn("Can't authorize %s", username)
    try:
        sp = spotipy.Spotify(auth=token, requests_session=True, client_credentials_manager=SpotifyClientCredentials())
        if token:
            logger.info("User %s authorized!", username)
        logger.info("Client credentialized!")
        return sp
    except SpotifyException:
        logger.exception("Can't credentialize")
