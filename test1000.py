import time
from multiprocessing import Process
import logging
from logging.handlers import RotatingFileHandler
from cloghandler import ConcurrentRotatingFileHandler


def a():
    # logger = logging.getLogger('')
    # _format=logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
    # log2file = RotatingFileHandler("CLI-LOG.txt",maxBytes = 1*1024,backupCount = 5)
    # log2file.setLevel(logging.DEBUG)
    # log2file.setFormatter(_format)
    # logger.addHandler(log2file)
    logging.warning('this is a')

def b():
    # logger = logging.getLogger('')
    # _format=logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
    # log2file = RotatingFileHandler("CLI-LOG.txt",maxBytes = 1*1024,backupCount = 5)
    # log2file.setLevel(logging.DEBUG)
    # log2file.setFormatter(_format)
    # logger.addHandler(log2file)
    logging.warning('this is b')

if __name__ == '__main__':
    logger = logging.getLogger('')
    _format=logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
    log2file = RotatingFileHandler("CLI-LOG.txt",maxBytes = 1*1024,backupCount = 5)
    log2file.setLevel(logging.DEBUG)
    log2file.setFormatter(_format)
    logger.addHandler(log2file)
    logging.warning('this is main')

    A = Process(target=a)
    B = Process(target=b)
    A.start()
    B.start()
    A.join()
    B.join()