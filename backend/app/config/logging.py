import logging

from logging.handlers import RotatingFileHandler

import os

def configure_logging(app):

    if not os.path.exists("logs"):
        os.mkdir("logs")

    handler = RotatingFileHandler(
        "logs/natifine.log",
        maxBytes=10485760,
        backupCount=10
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s"
    )

    handler.setFormatter(formatter)

    handler.setLevel(logging.INFO)

    app.logger.addHandler(handler)

    app.logger.setLevel(logging.INFO)

    app.logger.info("NatiFine Started")