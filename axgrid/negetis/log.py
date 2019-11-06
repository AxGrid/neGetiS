# coding:utf-8

import logging
import sys


def init_logger(verbose):
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    log_format = '%(asctime)-7s [%(levelname)-5s] %(message)s'
    logging.basicConfig(format=log_format, level=level, datefmt="%H:%M:%S")


def get_logger(name="negetis"):
    return logging.getLogger(name)

def fatal(text):
    get_logger().fatal(text)
    sys.exit(128)