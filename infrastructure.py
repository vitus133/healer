#!/bin/python3
import logging
from logging.handlers import RotatingFileHandler
import configparser
import os


def get_logger():
    LOG_FILENAME = 'healer.log'
    logger = logging.getLogger('vbs.healer')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s [%(filename)s:%(lineno)s]: %(message)s',
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


def get_config():
    CONF_FILENAME = 'healer.conf'
    config = configparser.ConfigParser()
    if os.path.isfile(CONF_FILENAME):
        config.read(CONF_FILENAME)
    cfg_dict = {}
    cfg_dict['TIMERS'] = {}
    cfg_dict['TIMERS']['stop'] = config.getint('TIMERS', 'stop', fallback=40)
    cfg_dict['TIMERS']['start'] = config.getint('TIMERS', 'start', fallback=300)
    cfg_dict['TIMERS']['in_healing_status_check'] = config.getint('TIMERS', 'in_healing_status_check', fallback=10)
    cfg_dict['TIMERS']['net_item_invalid_response'] = config.getint('TIMERS', 'net_item_invalid_response', fallback=30)
    cfg_dict['TIMERS']['cells_polling'] = config.getint('TIMERS', 'cells_polling', fallback=30)
    cfg_dict['COUNTERS'] = {}
    cfg_dict['COUNTERS']['healing_retries'] = config.getint('COUNTERS', 'healing_retries', fallback=3)
    cfg_dict['BACKEND'] = {}
    cfg_dict['BACKEND']['ipv4'] = config.get('BACKEND', 'ipv4', fallback='127.0.0.1')
    cfg_dict['BACKEND']['port'] = config.get('BACKEND', 'port', fallback='8080')
    upd_config = configparser.ConfigParser()
    upd_config['TIMERS'] = cfg_dict['TIMERS']
    upd_config['COUNTERS'] = cfg_dict['COUNTERS']
    upd_config['BACKEND'] = cfg_dict['BACKEND']
    with open(CONF_FILENAME, 'w') as configfile:
        upd_config.write(configfile)
    return(cfg_dict)


if __name__ == '__main__':
    print(get_config())