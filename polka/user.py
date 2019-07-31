# from spotipy.client import SpotifyException
import os
import numpy as np
import pprint


def acquire_tafs(sp, username):
    tafs_json = []
    playlists = sp.user_playlists(username, limit=1)
    while playlists:
        for playlist in playlists['items']:
            result_playlist = sp.user_playlist(username, playlist['id'], fields="tracks,next")
            result_tracks = result_playlist['tracks']
            tracks_uri = []
            for t in result_tracks['items']:
                track = t['track']
                tracks_uri.append(track['uri'])
                # print("(%s) %s %s" % (playlist['name'], track['artists'][0]['name'], track['name']))
            tracks_afs = sp.audio_features(tracks_uri)
            tafs_json.append(tracks_afs)
            if result_tracks['next']:
                result_tracks = sp.next(result_tracks)
        if playlists['next']:
            break
            playlists = sp.next(playlists)
        else:
            playlists = None
    tafs_int = []
    tafs_float = []
    tafs_str = []
    for track in tafs_json:
        for afs in track:
            tafs_int.append((afs['duration_ms'], afs['key'], afs['mode'], afs['time_signature']))
            tafs_float.append((afs['acousticness'], afs['danceability'], afs['energy'], afs['instrumentalness'], afs['liveness'],
                               afs['loudness'], afs['speechiness'], afs['valence'], afs['tempo']))
            tafs_str.append((afs['id'], afs['uri'], afs['track_href'], afs['analysis_url'], afs['type']))
    return User(username, tafs_int, tafs_float, tafs_str)


def load_tafs(username, filepath):
    npz_file = np.load(filepath)
    return User(username, npz_file['tafs_int'], npz_file['tafs_float'], npz_file['tafs_str'])


class User(object):
    def __init__(self, username, tafs_int, tafs_float, tafs_str):
        self._username = username
        self._np_tafs_int = np.array(tafs_int)
        self._np_tafs_float = np.array(tafs_float)
        self._np_tafs_str = np.array(tafs_str)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, u):
        self._username = u

    @property
    def np_tafs_int(self):
        return self._np_tafs_int

    @np_tafs_int.setter
    def np_tafs_int(self, i):
        self._np_tafs_int = i

    @property
    def np_tafs_float(self):
        return self._np_tafs_float

    @np_tafs_float.setter
    def np_tafs_float(self, f):
        self._np_tafs_float = f

    @property
    def np_tafs_str(self):
        return self._np_tafs_str

    @np_tafs_str.setter
    def np_tafs_str(self, s):
        self._np_tafs_str = s

    def print_tafs(self):
        np.set_printoptions(suppress=True, linewidth=160, formatter={"int_kind": lambda x: "%6d" % x, "float_kind": lambda x: "%08.4f" % x})
        for r in range(0, len(self.np_tafs_int)):
            print(self.np_tafs_int[r], self.np_tafs_float[r], self.np_tafs_str[r][0])

    def store_tafs(self, datapath):
        if not os.path.exists(datapath):
            os.makedirs(datapath)
        filepath = datapath + "/" + self.username + ".npz"
        np.savez(filepath, tafs_int=self.np_tafs_int, tafs_float=self.np_tafs_float, tafs_str=self.np_tafs_str)

    def print_user(self, sp):
        pprint.pprint(sp.user(User.username))
