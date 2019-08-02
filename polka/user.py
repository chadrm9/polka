# crm 2019
from spotipy.client import SpotifyException
import numpy as np

# import pprint
import logging


# logger attribute metaclass
class LoggedClassMeta(type):

    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, bases, dict(namespace))
        result.logger = logging.getLogger(result.__qualname__)
        return result


# mixin inherited super
class LoggedClass(metaclass=LoggedClassMeta):
    logger: logging.Logger


# derived User extends base LoggedClass
class User(LoggedClass):

    def __init__(self, username=""):
        self._username = username
        self._npz_path = ""
        self._tracks_count = 0
        self._np_tracks_af_int = np.empty([0, 4], dtype="int64")
        self._np_tracks_af_float = np.empty([0, 9], dtype="float64")
        self._np_tracks_af_str = np.empty([0, 5], dtype="<U64")

    # username
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, x):
        self._username = x

    # npz_path
    @property
    def npz_path(self):
        return self._npz_path

    @npz_path.setter
    def npz_path(self, x):
        self._npz_path = x

    # tracks_count
    @property
    def tracks_count(self):
        return self._tracks_count

    @tracks_count.setter
    def tracks_count(self, x):
        self._tracks_count = x

    # np_tracks_af_int
    @property
    def np_tracks_af_int(self):
        return self._np_tracks_af_int

    @np_tracks_af_int.setter
    def np_tracks_af_int(self, x):
        self._np_tracks_af_int = np.array(x)

    # np_tracks_af_float
    @property
    def np_tracks_af_float(self):
        return self._np_tracks_af_float

    @np_tracks_af_float.setter
    def np_tracks_af_float(self, x):
        self._np_tracks_af_float = np.array(x)

    # np_tracks_af_str
    @property
    def np_tracks_af_str(self):
        return self._np_tracks_af_str

    @np_tracks_af_str.setter
    def np_tracks_af_str(self, x):
        self._np_tracks_af_str = np.array(x)

    # legibly print interesting feature matrix
    def print_af(self):
        # set global numpy print options
        np.set_printoptions(suppress=True, linewidth=160, formatter={"int_kind": lambda x: "%6d" % x, "float_kind": lambda x: "%08.4f" % x})
        for r in range(0, self.tracks_count):
            print(self.np_tracks_af_int[r], self.np_tracks_af_float[r], self.np_tracks_af_str[r][0])
        return self

    # use spotipy instance to fetch data including
    # audio features as three lists (integers, floats, strings)
    # returns new User
    def fetch(self, sp):
        tracks_af = []
        try:
            playlists = sp.user_playlists(self.username, limit=50)
        except SpotifyException:
            self.logger.exception("Can't fetch public playlists for " + self.username)
        while playlists:
            for playlist in playlists['items']:

                # retreive tracks of relevant playlists
                if playlist['owner']['id'] == self.username:
                    try:
                        result_playlist = sp.user_playlist(self.username, playlist['id'], fields="tracks,next")
                    except SpotifyException:
                        self.logger.exception("Can't fetch public playlist %s (%s) for %s", playlist['name'], playlist['id'], self.username)

                    # fetch and accumulate track features
                    result_tracks = result_playlist['tracks']
                    result_uris = []
                    for t in result_tracks['items']:
                        result_uris.append(t['track']['uri'])
                        # print("(%s) %s %s" % (playlist['name'], track['artists'][0]['name'], track['name']))
                    try:
                        tracks_af.extend(sp.audio_features(result_uris))
                    except SpotifyException:
                        self.logger.exception("Can't fetch track features of public playlist %s (%s) for %s", playlist['name'], playlist['id'], self.username)

                    # check more tracks
                    while result_tracks['next']:
                        try:
                            result_tracks = sp.next(result_tracks)
                        except SpotifyException:
                            self.logger.exception("Can't fetch next tracks of public playlist %s (%s) for %s", playlist['name'], playlist['id'], self.username)

            # check more playlists
            if playlists['next']:
                # break
                try:
                    playlists = sp.next(playlists)
                except SpotifyException:
                    self.logger.exception("Can't fetch next public playlists for %s", self.username)

            # split features to dtype lists
            tracks_af_int = []
            tracks_af_float = []
            tracks_af_str = []
            for track in tracks_af:
                tracks_af_int.append((track['duration_ms'], track['key'], track['mode'], track['time_signature']))
                tracks_af_float.append((track['acousticness'], track['danceability'], track['energy'], track['instrumentalness'], track['liveness'],
                                        track['loudness'], track['speechiness'], track['valence'], track['tempo']))
                tracks_af_str.append((track['id'], track['uri'], track['track_href'], track['analysis_url'], track['type']))

            # tracks count sanity check before numpy array setters
            if len(tracks_af_int) == len(tracks_af_float) == len(tracks_af_str):
                self.tracks_count = len(tracks_af_int)
                self.np_tracks_af_int = tracks_af_int
                self.np_tracks_af_float = tracks_af_float
                self.np_tracks_af_str = tracks_af_str
            else:
                self.logger.error("Audio feature track counts not equal")
            return self

    # load user from npz file path
    def load(self, npz_path):
        npz_file = np.load(npz_path)
        # self.username = os.path.basename(npz_path).rsplit('.', 1)[0]
        self.npz_path = npz_path
        self.np_tracks_af_int = npz_file['np_tracks_af_int']
        self.np_tracks_af_float = npz_file['np_tracks_af_float']
        self.np_tracks_af_str = npz_file['np_tracks_af_str']
        self.tracks_count = len(self.np_tracks_af_int)
        self.logger.info("Loaded %s from %s", self.username, npz_path)
        return self

    # store user to npz file path and set user's npz_path
    def store(self, npz_path):
        np.savez(npz_path, np_tracks_af_int=self.np_tracks_af_int, np_tracks_af_float=self.np_tracks_af_float, np_tracks_af_str=self.np_tracks_af_str)
        self.npz_path = npz_path
        self.logger.info("Stored %s to %s", self.username, npz_path)
        return self
