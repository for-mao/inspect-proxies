import logging
from logging import Logger

formatter = logging.Formatter(
    '%(asctime)s [%(name)s] %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
)

root_logger = logging.getLogger('inspect-proxies')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
root_logger.addHandler(ch)
root_logger.setLevel(logging.INFO)


def create_logger(logger_name: str) -> Logger:
    logger = root_logger.getChild(logger_name)

    return logger
