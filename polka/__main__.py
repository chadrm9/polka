# crm 2019
import core
from user import User

import os
import sys
import datetime
import logging


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    logger = logging.getLogger("main")
    date_str = datetime.datetime.now().strftime("%Y%m%d")

    # data directory path
    npz_dir = "dat/" + date_str

    # spotipy auth or client credentials flow
    username = sys.argv[1]
    sp = core.do_auth(sys.argv[1])

    # copy discover weekly
    dest = "DW" + date_str
    core.copy_playlist(sp, username, "Discover Weekly", dest, "spotify")

    # read username args and build user list
    user_list = []
    for username in sys.argv[1:]:

        # user load or fetch & store
        npz_path = npz_dir + '/' + username + '.npz'
        if os.path.exists(npz_path):
            u = core.load_user(npz_path)
        else:
            if not os.path.exists(npz_dir):
                os.makedirs(npz_dir)
            u = core.fetch_user(sp, username)
            u.store(npz_path)
        user_list.append(u)
        logger.debug("User %s added to current session", u.username)


if __name__ == "__main__":
    main()
