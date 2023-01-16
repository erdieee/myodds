#!/usr/bin/env python3
"""
Main myodds script
"""

import logging
from datetime import datetime

from myodds.constants import REFRESH_TIME_SECONDS
from myodds.myoddsbot import MyOddsBot
from myodds.utils import load_config

logger = logging.getLogger('myodds')
LOGFORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOGFORMAT)


def main() -> None:
    logger.info('Starting myodds..')

    config = load_config()
    myoddsbot = MyOddsBot(config=config)

    myoddsbot.runner()
    time = datetime.now()
    while True:
        delta = datetime.now() - time
        if delta.seconds >= REFRESH_TIME_SECONDS:
            logger.info(f'Bot is running')
            myoddsbot.runner()
            time = datetime.now()

    
if __name__ == '__main__':
    main()