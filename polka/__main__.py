# crm 2019
import os
import logging
import datetime

import core


def main():
    # info level from notebook, debug level from CLI
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    logger = logging.getLogger("main")

if __name__ == "__main__":
    main()
