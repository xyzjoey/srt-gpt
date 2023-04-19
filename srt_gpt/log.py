import logging
import sys


class Log:
    logger = logging.getLogger()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s [%(name)-6s] %(message)s",
        datefmt="%H:%M:%S",
    )

    @classmethod
    def init(cls):
        cls.logger.setLevel(logging.INFO)

        default_handler = logging.StreamHandler(sys.stdout)
        default_handler.setFormatter(cls.formatter)

        cls.logger.addHandler(default_handler)
