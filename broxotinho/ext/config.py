# -*- coding: utf-8 -*-
import os

__all__ = ("config",)


class Config:
    stage = os.environ.get("STAGE", "dev")
    version = os.environ.get("VERSION", "0.0.0")

    token = os.environ["BOT_TOKEN"]
    secret = os.environ["BOT_SECRET"]
    prefix = os.environ.get("BOT_PREFIX", "%")
    dev = os.environ["DEV_NICK"]

    cogs_path = os.environ.get("COGS_PATH", "broxotinho/cogs")
    cogs = [
        module[:-3]
        for module in os.listdir(cogs_path)
        if not module.startswith("_") and module.endswith(".py")
    ]

    redis_url = os.environ.get("REDIS_URL")

    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_region_name = os.environ.get("AWS_REGION_NAME", "us-east-1")

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    site_url = os.environ.get("SITE_URL", "")
    doc_url = os.environ.get("DOC_URL", f"{site_url}/docs/help")
    invite_url = os.environ.get("INVITE_URL", f"{site_url}/invite")

    bugsnag_key = os.environ.get("BUGSNAG_KEY", "")
    currency_key = os.environ.get("CURRENCY_KEY", "")
    dashbot_key = os.environ.get("DASHBOT_KEY", "")
    genius_key = os.environ.get("GENIUS_KEY", "")
    spotify_client = os.environ.get("SPOTIFY_CLIENT_ID", "")
    spotify_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    weather_key = os.environ.get("WEATHER_KEY", "")
    witai_duration_key = os.environ.get("WITAI_DURATION_KEY", "")
    witai_datetime_key = os.environ.get("WITAI_DATETIME_KEY", "")

config = Config()
