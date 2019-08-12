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


if __name__ == "__main__":
    main()
