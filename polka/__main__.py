# crm 2019
import core
from user import User

import os
import sys
import datetime
import logging


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    logger = logging.getLogger("main")

    # data directory path
    npz_dir = "dat/" + str(datetime.date.today())

    # spotipy auth or client credentials flow
    sp = core.do_auth(sys.argv[1])

    # read username args and build user list
    user_list = []
    for username in sys.argv[1:]:
        u = User(username)

        # user load or fetch & store
        npz_path = npz_dir + '/' + username + '.npz'
        if os.path.exists(npz_path):
            u.load(npz_path)
        else:
            if not os.path.exists(npz_dir):
                os.makedirs(npz_dir)
            u.fetch(sp).store(npz_path)
        user_list.append(u)
        logger.debug("User %s added to current session", u.username)


if __name__ == "__main__":
    main()
