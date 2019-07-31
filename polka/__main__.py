# crm 2019 = trying out spotipy

import os
import sys
import datetime
import core
import user


def main():
    sp = core.do_auth()
    datpath = "dat/" + str(datetime.date.today())
    user_list = []
    for username in sys.argv[1:]:
        filepath = datpath + "/" + username
        if os.path.exists(filepath):
            u = user.load_tafs(username, filepath)
        else:
            os.makedirs(filepath)
            u = user.acquire_tafs(sp, username)
            u.store_tafs(datpath)
            u.print_tafs()
        user_list.append(u)


if __name__ == "__main__":
    main()
