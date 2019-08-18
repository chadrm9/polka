# crm 2019
import os
import logging

import core


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    logger = logging.getLogger("main")

if __name__ == "__main__":
    main()
