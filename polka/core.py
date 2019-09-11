# crm 2019
from spotipy.util import prompt_for_user_token
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.client import SpotifyException
import spotipy

from user import User

import os
import numpy as np
import pprint
import logging
logger = logging.getLogger(__name__)

# copy tracks from source_pl_names array to dest_pl_name
# maintain order of tracks and do not add duplicates
# new destination playlist is created as private by default
# TODO possible refactor
def copy_tracks(sp, username, src_pl_names, dst_pl_name, public=False):
    src_tids = []
    dst_tids = []
    dst_pl_uri = ''

    # accumulate track ids from source playlist(s)
    for src_pl in src_pl_names:
        found = False
        try:
            playlists = sp.current_user_playlists()
        except SpotifyException:
            logger.exception("Can't fetch playlists for " + username)

        # iterate user playlists
        while playlists:
            for playlist in playlists['items']:

                # retrieve tracks of matching source playlist
                if playlist['name'] == src_pl:
                    found = True
                    logger.debug("%s (%s)", playlist['name'], playlist['id'])

                    try:
                        result_playlist = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                    except SpotifyException:
                        logger.exception("Can't fetch playlist %s for %s", playlist['name'], username)

                    result_tracks = result_playlist['tracks']

                    #accumulate source(s) track ids
                    while result_tracks:
                        for t in result_tracks['items']:
                            src_tids.append(t['track']['id'])
                            logger.debug("%s - %s", t['track']['artists'][0]['name'], t['track']['name'])

                        # check for more tracks
                        if result_tracks['next']:
                            try:
                                result_tracks= sp.next(result_tracks)
                                logger.debug("Fetched next tracks of playlist %s for %s", playlist['name'], username)
                            except SpotifyException:
                                logger.exception("Can't fetch next tracks of playlist %s for %s", playlist['name'], username)
                        else:
                            result_tracks = None

            # check for more playlists
            if (not playlists['next']) or found == True:
                playlists = None
            else:
                playlists = sp.next(playlists)

    # accumulate track ids from destination playlist if it exists
    try:
        playlists = sp.current_user_playlists()
    except SpotifyException:
        logger.exception("Can't fetch user playlists for " + username)

    # iterate user playlists
    while playlists:
        for playlist in playlists['items']:

            # retrieve tracks of matching destination playlist
            if playlist['name'] == dst_pl_name:
                logger.debug("%s (%s)", playlist['name'], playlist['id'])

                try:
                    result_playlist = sp.user_playlist(username, playlist['id'], fields="uri,tracks,next")
                except SpotifyException:
                    logger.exception("Can't fetch playlist %s for %s", playlist['name'], username)

                dst_pl_uri = result_playlist['uri']
                result_tracks = result_playlist['tracks']

                # accumulate destination track ids
                while result_tracks:
                    for t in result_tracks['items']:
                        dst_tids.append(t['track']['id'])
                        logger.debug("%s - %s", t['track']['artists'][0]['name'], t['track']['name'])

                    # check for more tracks
                    if result_tracks['next']:
                        try:
                            result_tracks = sp.next(result_tracks)
                            logger.debug("Fetched next tracks of playlist %s for %s", playlist['name'], username)
                        except SpotifyException:
                            logger.exception("Can't fetch next tracks of playlist %s for %s", playlist['name'], username)
                    else:
                        result_tracks = None

        # check for more playlists
        if (not playlists['next']) or dst_pl_name != '':
            playlists = None
        else:
            playlists = sp.next(playlists)

    # unique source track ids dictionary
    src_tids_dct = dict.fromkeys(src_tids)

    # destination playlist DNE
    if dst_pl_uri == '':

        # no possible duplicates in new destination (all are unique)
        unq_tids = list(src_tids_dct)

        # create new destination playlist (default public=False)
        try:
            playlist = sp.user_playlist_create(username, dst_pl_name, public=public)
        except SpotifyException:
            logger.exception("Can't create playlist %s for %s", dst_pl_name, username)

        logger.info("Playlist %s created for %s", dst_pl_name, username)

        # store uri
        dst_pl_uri = playlist['uri']

    # destination playlist does exist
    else:

        # unique destination track ids dictionary
        dst_tids_dct = dict.fromkeys(dst_tids)

        # final unique list
        unq_tids = []
        for key in src_tids_dct.keys():
            if not key in dst_tids_dct:
                unq_tids.append(key)

    # add unique to destination playlist
    if len(unq_tids) > 0:

        # mind spotify limit of 100/req
        for i in range(0, len(unq_tids), 100):
            try:
                results = sp.user_playlist_add_tracks(username, dst_pl_uri, unq_tids[i:i+100])
            except SpotifyException:
                logger.exception("Can't add tracks to playlist %s for %s", dst_pl_name, username)

    logger.info("%d tracks copied to %s for %s", len(unq_tids), dst_pl_name, username)

# use spotipy instance to fetch data including
# audio features as three lists (integers, floats, strings)
# returns new User
# TODO refactor
def fetch_user(sp, username):
    logger.info("Fetching user %s", username)
    playlist_count = 0
    tracks_af = []
    try:
        playlists = sp.user_playlists(username)
    except SpotifyException:
        logger.exception("Can't fetch public playlists for " + username)
    while playlists:
        for playlist in playlists['items']:

            # retreive tracks of relevant playlists
            if playlist['owner']['id'] == username:
                playlist_count += 1
                try:
                    result_playlist = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                except SpotifyException:
                    logger.exception("Can't fetch public playlist %s (%s) for %s", playlist['name'], playlist['id'], username)
                result_tracks = result_playlist['tracks']

                # accumulate track uris
                result_uris = []
                for t in result_tracks['items']:
                    result_uris.append(t['track']['uri'])

                # fetch and accumulate track audio features
                try:
                    tracks_af.extend(sp.audio_features(result_uris))
                except SpotifyException:
                    logger.exception("Can't fetch track features of public playlist %s (%s) for %s", playlist['name'], playlist['id'], username)

                # check for more tracks
                while result_tracks['next']:
                    try:
                        result_tracks = sp.next(result_tracks)
                    except SpotifyException:
                        logger.exception("Can't fetch next tracks of public playlist %s (%s) for %s", playlist['name'], playlist['id'], username)

        # check for more playlists
        if playlists['next']:
            try:
                playlists = sp.next(playlists)
            except SpotifyException:
                logger.exception("Can't fetch next public playlists for %s", username)
        else:
            playlists = None

    # split features to dtype lists
    tracks_af_int = []
    tracks_af_flt = []
    tracks_af_str = []
    for track in tracks_af:
        tracks_af_int.append((track['duration_ms'], track['key'], track['mode'], track['time_signature']))
        tracks_af_flt.append((track['acousticness'], track['danceability'], track['energy'], track['instrumentalness'], track['liveness'],
                              track['loudness'], track['speechiness'], track['valence'], track['tempo']))
        tracks_af_str.append((track['id'], track['uri'], track['track_href'], track['analysis_url'], track['type']))

    # tracks count sanity check before numpy array setters
    if not len(tracks_af_int) == len(tracks_af_flt) == len(tracks_af_str):
        logger.error("Audio feature track counts not equal")
    logger.info("Retrieved %d tracks in %d public playlists", len(tracks_af_int), playlist_count)
    return User(username, tracks_af_int, tracks_af_flt, tracks_af_str)

# read username lines from file, load existing users and fetch new ones
# returns User list
def fetch_user_list(sp, list_path, npz_dir):
    user_list = []
    if os.path.exists(list_path):
        with open(list_path) as lp:
            for line in lp:
                username = line.strip()
                npz_path = os.path.join(npz_dir, username + '.npz')

                # load or fetch + store then append
                if os.path.exists(npz_path):
                    u = load_user(npz_path)
                else:
                    u = fetch_user(sp, username)

                    # make any missing intermediate directories
                    if not os.path.exists(npz_dir):
                        os.makedirs(npz_dir)

                    u.store(npz_path)
                user_list.append(u)
    else:
        logger.error("Can't read user list file '%s'", list_path)
    return user_list

# load user from npz file path
# returns new User
def load_user(npz_path):
    npz_file = np.load(npz_path)
    username = os.path.basename(npz_path).rsplit('.', 1)[0]
    logger.info("Loaded %s from %s", username, npz_path)
    return User(username, npz_file['np_af_int'], npz_file['np_af_flt'], npz_file['np_af_str'], npz_path)

# load all users from npz folder
# returns User list
def load_user_dir(npz_dir):
    user_list = []
    if os.path.exists(npz_dir):
        for filename in os.listdir(npz_dir):
            if filename.endswith(".npz"):
                username = os.path.splitext(filename)[0]
                npz_path = os.path.join(npz_dir, filename)
                u = core.load_user(npz_path)
                user_list.append(u)
                logger.info("User %s loaded from %s", username, npz_dir)
    else:
        logger.error("Can't load npz directory '%s'", npz_dir)
    return user_list

# do oauth2 authorization or client credentials flow
def do_auth(username=""):
    token = None
    if username:
        scope = "playlist-read-collaborative playlist-modify-public playlist-modify-private playlist-read-private"
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
