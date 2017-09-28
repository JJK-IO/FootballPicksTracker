import datetime
import logging
import os

from ux2d_project import settings


class Log:
    def __init__(self):
        log_format = '[%(asctime)s] [%(levelname)s]: %(message)s'

        if not os.path.isdir("logs/"):
            os.makedirs("logs/")

        logging.basicConfig(
            filename='logs/%s-project.log' % datetime.date.today(),
            level=settings.LOG_LEVEL,
            format=log_format
        )

    @staticmethod
    def d(msg):
        print("[DEBUG]: %s" % msg)
        logging.debug("%s" % msg)

    @staticmethod
    def i(msg):
        print("[INFO]: %s" % msg)
        logging.info("%s" % msg)

    @staticmethod
    def w(msg):
        print("[WARNING]: %s" % msg)
        logging.warning("%s" % msg)

    @staticmethod
    def e(msg):
        print("[ERROR]: %s" % msg)
        logging.error("%s" % msg)

    @staticmethod
    def v(msg):
        print("[VERBOSE]: %s" % msg)