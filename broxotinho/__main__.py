# -*- coding: utf-8 -*-
from broxotinho.bot import Broxotinho
from broxotinho.ext.config import config

__all__ = ("bot", )

try:
    bot = Broxotinho(
        token=config.token,
        client_secret=config.secret,
        prefix=config.prefix,
        case_insensitive=True,
    )
    bot.load_modules(cogs=[f"{config.cogs_path}.{cog}" for cog in config.cogs])
    bot.start()
except KeyboardInterrupt:
    pass
finally:
    bot.stop()
