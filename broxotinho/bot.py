# -*- coding: utf-8 -*-
from typing import Any, Callable, Coroutine, Optional

from broxotinho import logger
from broxotinho.ext.commands import (
    Bot,
    Context,
    Message,
    User,
    routine,
)
from broxotinho.ext.exceptions import (
    CheckFailure,
    CommandNotFound,
    CommandOnCooldown,
    InvalidArgument,
)
from broxotinho.ext.redis import redis
from broxotinho.models.channel import ChannelModel
from broxotinho.models.user import UserModel


class Broxotinho(Bot):
    listeners: list[Callable[[Context,], Coroutine[Any, Any, bool]]] = []
    channels: dict[str, ChannelModel] = {channel.name: channel for channel in ChannelModel.scan()}

    async def fetch_user(self, name: str = None, id: int = None) -> Optional[User]:
        try:
            if name:
                data = await self.fetch_users(names=[name])
            elif id:
                data = await self.fetch_users(ids=[id])
            user = data[0]
            assert user.id is not None
        except Exception:
            return None
        else:
            return user

    async def fetch_user_db(self, name: str = None, id: int = None) -> Optional[UserModel]:
        if name and not id:
            twitch_user = await self.fetch_user(name)
            if not twitch_user:
                return None
            id = twitch_user.id
        return UserModel.get_or_none(id)

    def load_modules(self, cogs: list[str]) -> None:
        for cog in cogs:
            module = cog.replace("/", ".")
            self.load_module(module)

    def is_online(self, message: Message) -> bool:
        return (
            self.channels[message.channel.name].online
            or message.content.startswith(f"{self._prefix}start")
        )

    def is_enabled(self, ctx: Context, command: str = "") -> bool:
        command_name = command or ctx.command.name
        return command_name.lower() not in self.channels[ctx.channel.name].commands_disabled

    async def before_connect(self) -> None:
        self.check(self.is_enabled)

    async def after_connect(self) -> None:
        self.check_channels.start()

    async def before_close(self) -> None:
        self.check_channels.cancel()

    async def after_close(self) -> None:
        ...

    def start(self) -> None:
        self.loop.run_until_complete(self.before_connect())
        self.loop.create_task(self.connect())
        self.loop.run_until_complete(self.after_connect())
        self.loop.run_forever()

    def stop(self) -> None:
        self.loop.run_until_complete(self.before_close())
        self.loop.run_until_complete(self.close())
        self.loop.run_until_complete(self.after_close())
        self.loop.close()

    async def event_ready(self) -> None:
        ...

    async def global_before_invoke(self, ctx: Context) -> None:
        if ctx.message.content:
            ctx.message.content.replace("\U000e0000", "")
        if not ctx.user:
            ctx.user = UserModel.get_or_create(
                ctx.author.id,
                name=ctx.author.name,
                last_message=ctx.message.content,
                last_channel=ctx.channel.name,
                last_color=ctx.author.color,
            )

    async def global_after_invoke(self, ctx: Context) -> None:
        # TODO: salvar mensagem recebida no Dashbot
        # TODO: salvar mensagem enviada no Dashbot
        ...

    async def event_message(self, message: Message) -> None:
        if message.echo:
            return None
        if not self.is_online(message):
            return None
        ctx = await self.get_context(message, cls=Context)
        try:
            await self.invoke(ctx)
        except InvalidArgument:
            if ctx.command and hasattr(ctx.command, "usage"):
                return await ctx.reply(ctx.command.usage)
            return await ctx.reply("ocorreu um erro inesperado")
        except Exception as error:
            logger.error(error, extra={"ctx": dict(ctx)}, exc_info=error)
        else:
            if not ctx.user:
                ctx.user = UserModel.get_or_none(ctx.author.id)
            for listener in self.listeners:
                if await listener(ctx):
                    return None
            if ctx.user:
                ctx.user.update_user(
                    name=ctx.author.name,
                    last_message=ctx.message.content,
                    last_channel=ctx.channel.name,
                    last_color=ctx.author.color,
                )

    async def event_error(self, error: Exception, data: str = None) -> None:
        logger.error(error, exc_info=error)

    async def event_command_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, CommandNotFound):
            return None
        if isinstance(error, CheckFailure):
            return None
        if isinstance(error, CommandOnCooldown):
            return await ctx.reply(f"aguarde {error.retry_after:.1f}s para usar o comando de novo")
        if isinstance(error, NotImplementedError):
            return await ctx.reply("esse comando está temporariamente desativado")
        if isinstance(error, InvalidArgument):
            if ctx.command and hasattr(ctx.command, "usage"):
                return await ctx.reply(ctx.command.usage)
        logger.error(error, extra={"ctx": dict(ctx)}, exc_info=error)
        return await ctx.reply(f"ocorreu um erro inesperado, por favor, reporte o erro usando o comando {ctx.prefix}bug")

    @routine(seconds=30, wait_first=True)
    async def check_channels(self) -> None:
        connected_channels = [channel.name for channel in self.connected_channels]
        disconnected_channels = [channel for channel in self.channels if channel not in connected_channels]
        logger.warning(f"channels={len(connected_channels)}/{len(self.channels)} disconnected_channels={disconnected_channels}")
        for channel in disconnected_channels:
            await self._connection.send(f"JOIN #{channel}\r\n")
