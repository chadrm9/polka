# crm 2019
import logging

from spotipy.client import SpotifyException
import numpy as np

# set global numpy print options
np.set_printoptions(suppress=True, linewidth=160, formatter={"int_kind": lambda x: "%6d" % x, "float_kind": lambda x: "%08.4f" % x})


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
    def __init__(self, username, tracks_af_int, tracks_af_float, tracks_af_str, npz_path=""):
        self._username = username
        self._npz_path = npz_path
        self._tracks_count = len(tracks_af_int)
        self._np_tracks_af_int = tracks_af_int
        self._np_tracks_af_float = tracks_af_float
        self._np_tracks_af_str = tracks_af_str

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
        for r in range(0, self.tracks_count):
            print(self.np_tracks_af_int[r], self.np_tracks_af_float[r])
        return self

    # store user to npz file path and set user's npz_path
    def store(self, npz_path):
        np.savez(npz_path, np_tracks_af_int=self.np_tracks_af_int, np_tracks_af_float=self.np_tracks_af_float, np_tracks_af_str=self.np_tracks_af_str)
        self.npz_path = npz_path
        self.logger.info("Stored %s to %s", self.username, npz_path)
        return self
