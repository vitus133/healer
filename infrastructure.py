#!/bin/python3
import logging
from logging.handlers import RotatingFileHandler


def get_logger():
    LOG_FILENAME = 'healer.log'
    logger = logging.getLogger('vbs healer')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)s]: %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    
    # logging to file
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=10)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # logging to console
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

