# crm 2019
import os
import logging


def main():
    # Info level from notebook, Debug level from CLI
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    logger = logging.getLogger("main")

if __name__ == "__main__":
    main()
