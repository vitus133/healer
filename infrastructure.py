#!/bin/python3
import logging
from logging.handlers import RotatingFileHandler
import configparser
import os


def get_logger(config):
    logger = logging.getLogger(config['logger_name'])
    logger.setLevel(config['gen_level'])
    formatter = logging.Formatter(
        '%(name)s %(asctime)s %(levelname)s [%(filename)s:%(lineno)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    # logging to file
    handler = RotatingFileHandler(
        config['log_path_file'],
        maxBytes=config['rotate_bytes'],
        backupCount=config['rotate_count'])
    handler.setLevel(config['file_level'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # logging to console
    handler = logging.StreamHandler()
    handler.setLevel(config['console_level'])
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
    cfg_dict['TIMERS']['start'] = config.getint(
        'TIMERS', 'start', fallback=300)
    cfg_dict['TIMERS']['in_healing_status_check'] = config.getint(
        'TIMERS', 'in_healing_status_check', fallback=10)
    cfg_dict['TIMERS']['net_item_invalid_response'] = config.getint(
        'TIMERS', 'net_item_invalid_response', fallback=30)
    cfg_dict['TIMERS']['cells_polling'] = config.getint(
        'TIMERS', 'cells_polling', fallback=30)
    cfg_dict['COUNTERS'] = {}
    cfg_dict['COUNTERS']['healing_retries'] = config.getint(
        'COUNTERS', 'healing_retries', fallback=3)
    cfg_dict['BACKEND'] = {}
    cfg_dict['BACKEND']['ipv4'] = config.get(
        'BACKEND', 'ipv4', fallback='127.0.0.1')
    cfg_dict['BACKEND']['port'] = config.get(
        'BACKEND', 'port', fallback='8080')
    cfg_dict['LOGGER'] = {}
    cfg_dict['LOGGER']['log_path_file'] = config.get(
        'LOGGER', 'log_path_file', fallback='healer.log')
    cfg_dict['LOGGER']['logger_name'] = config.get(
        'LOGGER', 'logger_name', fallback='vbs.healer')
    cfg_dict['LOGGER']['gen_level'] = config.getint(
        'LOGGER', 'gen_level', fallback=logging.DEBUG)
    cfg_dict['LOGGER']['file_level'] = config.getint(
        'LOGGER', 'file_level', fallback=logging.INFO)
    cfg_dict['LOGGER']['console_level'] = config.getint(
        'LOGGER', 'console_level', fallback=logging.DEBUG)
    cfg_dict['LOGGER']['rotate_bytes'] = config.getint(
        'LOGGER', 'rotate_bytes', fallback=10000000)
    cfg_dict['LOGGER']['rotate_count'] = config.getint(
        'LOGGER', 'rotate_count', fallback=3)
    upd_config = configparser.ConfigParser()
    upd_config['TIMERS'] = cfg_dict['TIMERS']
    upd_config['COUNTERS'] = cfg_dict['COUNTERS']
    upd_config['BACKEND'] = cfg_dict['BACKEND']
    upd_config['LOGGER'] = cfg_dict['LOGGER']
    with open(CONF_FILENAME, 'w') as configfile:
        upd_config.write(configfile)
    return(cfg_dict)
