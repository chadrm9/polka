# crm 2019 = trying out spotipy

import sys
import pprint
import json
import time

from spotipy.util import prompt_for_user_token
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.client import SpotifyException
import spotipy
import numpy as np

#from .helpers import Base64Decode

np.set_printoptions(suppress=True, linewidth=160, formatter={"int_kind": lambda x: "%6d" % x, "float_kind": lambda x: "%08.4f" % x})

username = 'chadrm9'
scope = 'user-library-read'
#token = prompt_for_user_token(username, scope)
token = None
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth=token, requests_session=True, client_credentials_manager=client_credentials_manager)

tracks_afs_json = []
start = time.time()

#playlists = sp.current_user_playlists()
playlists = sp.user_playlists(username)
while playlists:
    for playlist in playlists['items']:
        result_playlist= sp.user_playlist(username, playlist['id'], fields="tracks,next")
        result_tracks = result_playlist['tracks']
        tracks_uri= []
        for t in result_tracks['items']:
            track = t['track']
            tracks_uri.append(track['uri'])
            #print("(%s) %s %s" % (playlist['name'], track['artists'][0]['name'], track['name']))
            
        tracks_afs = sp.audio_features(tracks_uri)
        #tracks_count += len(tracks_afs)
        tracks_afs_json.append(tracks_afs)
        if result_tracks['next']:
            result_tracks = sp.next(result_tracks)
        #playlists_count += len(result_playlist)
    if playlists['next']:
        #break
        playlists = sp.next(playlists)
    else:
        playlists = None

tracks_afs_int = []
tracks_afs_float = []
tracks_afs_str = []
for track in tracks_afs_json:
    for afs in track:
        tracks_afs_int.append((afs['duration_ms'], afs['key'], afs['mode'], afs['time_signature']))
        tracks_afs_float.append((afs['acousticness'], afs['danceability'], afs['energy'], afs['instrumentalness'], afs['liveness'], 
                                 afs['loudness'], afs['speechiness'], afs['valence'], afs['tempo']))
        tracks_afs_str.append((afs['id'], afs['uri'], afs['track_href'], afs['analysis_url'], afs['type']))

np_tracks_afs_int = np.array(tracks_afs_int)
np_tracks_afs_float = np.array(tracks_afs_float)
np_tracks_afs_str = np.array(tracks_afs_str)
np_tracks_afs_count = len(np_tracks_afs_int)
#for r in range(0, np_tracks_afs_count):
    #print(np_tracks_afs_int[r], np_tracks_afs_float[r], np_tracks_afs_str[r][0])
 
delta = time.time() - start
print("%.2f seconds | %d tracks | %s" % (delta, np_tracks_afs_count, username))
