# -*- coding: utf-8 -*-
from broxotinho.ext.config import config
from broxotinho.ext.logger import logger
from broxotinho.services.bugsnag import bugsnag_handler

__title__ = "broxotinho"
__author__ = "Leandro César"
__license__ = "GNU"
__copyright__ = "Copyright 2020 broxotinho"
__version__ = config.version

__all__ = ("config", "logger")

try:
    if config.bugsnag_key is None:
        raise KeyError("'BUGSNAG_KEY' env var not set, couldn't notify")
    handler = bugsnag_handler(key=config.bugsnag_key, version=config.version, stage=config.stage)
except Exception as error:
    logger.warning(error)
else:
    logger.addHandler(handler)
