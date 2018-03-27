import logging
from logging import Logger

formatter = logging.Formatter()


def create_logger(logger_name: str) -> Logger:
    logger = logging.getLogger(logger_name)

    return logger
