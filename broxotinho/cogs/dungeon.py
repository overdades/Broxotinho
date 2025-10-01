# -*- coding: utf-8 -*-
from broxotinho.bot import Broxotinho
from broxotinho.ext.commands import Bucket, Cog, Context, cooldown, command, helper, usage
from broxotinho.utils.convert import json_to_dict
from broxotinho.utils.rand import random_choice, random_choices, random_number
from broxotinho.utils.time import timeago, timedelta

CLASSES = json_to_dict("broxotinho//data//classes.json")
DUNGEONS = json_to_dict("broxotinho//data//dungeons.json")


class Dungeon(Cog):
    """Dungeon

    Participe de um mini RPG com os outros usuários, escolha sua classe e aumente seu nível
    """

    def __init__(self, bot: Broxotinho) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.args and isinstance(ctx.args[0], str):
            ctx.args[0] = ctx.args[0].lstrip("@").rstrip(",").lower()
        return True

    @helper("entre na dungeon, faça sua escolha e adquira experiência")
    @cooldown(rate=2, per=30, bucket=Bucket.member)
    @command(aliases=["ed"])
    async def enterdungeon(self, ctx: Context, *, content: str = "") -> None:
        if not ctx.user.dungeons:
            check = lambda message: (
                message.author
                and message.author.id == ctx.author.id
                and message.channel.name == ctx.channel.name
                and message.content.lower() in ("guerreiro", "arqueiro", "mago", "guerreira", "arqueira", "maga")
            )
            await ctx.reply("antes de continuar, você quer ser um guerreiro(a), arqueiro(a) ou mago(a)?")
            try:
                response = await self.bot.wait_for("message", check, timeout=60)
            except Exception:
                return None
            else:
                message = response[0]
                option = message.content.lower()
                main_class = [key for key, value in CLASSES.items() if value[0].lower() == option][0]
                ctx.user.update_dungeon(main_class=main_class)
                _class = CLASSES[ctx.user.dungeons._class][min(ctx.user.dungeons.level, 60) // 10]
                await ctx.reply(f"agora você é um {_class}")

        if ctx.user.dungeons.main_class and not ctx.user.dungeons.sub_class and ctx.user.dungeons.level >= 30:
            i = list(CLASSES).index(ctx.user.dungeons._class)
            class_1 = CLASSES[list(CLASSES)[i]]
            class_2 = CLASSES[list(CLASSES)[i + 1]]
            options = (class_1[3].title(), class_2[3].title())
            check = lambda message: (
                message.author
                and message.author.id == ctx.author.id
                and message.channel.name == ctx.channel.name
                and message.content.title() in options
            )
            await ctx.reply(f"antes de continuar, você deve escolher sua nova classe: {options[0]} ou {options[1]}?")
            try:
                response = await self.bot.wait_for("message", check, timeout=60)
            except Exception:
                return None
            else:
                message = response[0]
                option = message.content.lower()
                main_class = [key for key, value in CLASSES.items() if value[3].lower() == option][0]
                ctx.user.update_dungeon(main_class=main_class)
                _class = CLASSES[ctx.user.dungeons._class][min(ctx.user.dungeons.level, 60) // 10]
                await ctx.reply(f"agora você é um {_class}")

        if (
            timeago(ctx.user.dungeons.updated_on).total_in_seconds() < 10800
            and ctx.user.dungeons.created_on.isoformat()[:18] != ctx.user.dungeons.updated_on.isoformat()[:18]
        ):
            delta = timeago(ctx.user.dungeons.updated_on + timedelta(seconds=10800), reverse=True).humanize()
            return await ctx.reply(f"aguarde {delta} para entrar em outra dungeon ⌛")

        i = random_number(min=0, max=len(DUNGEONS) - 1)
        dungeon = DUNGEONS[i]
        check = lambda message: (
            message.author
            and message.author.id == ctx.author.id
            and message.channel.name == ctx.channel.name
            and message.content.lower() in ("1", "2", f"{ctx.prefix}ed 1", f"{ctx.prefix}ed 2")
        )
        await ctx.reply(f'{dungeon["quote"]} você quer {dungeon["1"]["option"]} ou {dungeon["2"]["option"]}? (1 ou 2)')
        try:
            response = await self.bot.wait_for("message", check, timeout=60)
        except Exception:
            return None
        else:
            message = response[0]
            option = message.content.lower().replace(f"{ctx.prefix}ed ", "")

        result = random_choices(["win", "lose"], w=(0.66, 0.33))[0]
        if result == "win":
            experience = int(random_number(min=50, max=75) + 3 * ctx.user.dungeons.level)
            if ctx.user.dungeons.experience + experience > 100 * (ctx.user.dungeons.level) + 25 * sum(range(1, ctx.user.dungeons.level + 1)):
                ctx.user.update_dungeon(win=True, experience=experience, level_up=True)
                return await ctx.reply(f"{dungeon[option][result]}! +{experience} XP e alcançou level {ctx.user.dungeons.level} ⬆")
            else:
                ctx.user.update_dungeon(win=True, experience=experience)
                return await ctx.reply(f"{dungeon[option][result]}! +{experience} XP")
        else:
            ctx.user.update_dungeon(defeat=True)
            return await ctx.reply(f"{dungeon[option][result]}! +0 XP")

    @helper("entre na dungeon e adquira experiência sem precisar tomar uma escolha")
    @cooldown(rate=1, per=30, bucket=Bucket.member)
    @command(aliases=["fed", "fd"])
    async def fastdungeon(self, ctx: Context) -> None:
        if not ctx.user.dungeons:
            check = lambda message: (
                message.author
                and message.author.id == ctx.author.id
                and message.channel.name == ctx.channel.name
                and message.content.lower() in ("guerreiro", "arqueiro", "mago", "guerreira", "arqueira", "maga")
            )
            await ctx.reply("antes de continuar, você quer ser um guerreiro(a), arqueiro(a) ou mago(a)?")
            try:
                response = await self.bot.wait_for("message", check, timeout=60)
            except Exception:
                return None
            else:
                message = response[0]
                option = message.content.lower()
                main_class = [key for key, value in CLASSES.items() if value[0].lower() == option][0]
                ctx.user.update_dungeon(main_class=main_class)
                _class = CLASSES[ctx.user.dungeons._class][min(ctx.user.dungeons.level, 60) // 10]
                await ctx.reply(f"agora você é um {_class}")

        if ctx.user.dungeons.main_class and not ctx.user.dungeons.sub_class and ctx.user.dungeons.level >= 30:
            i = list(CLASSES).index(ctx.user.dungeons._class)
            class_1 = CLASSES[list(CLASSES)[i]]
            class_2 = CLASSES[list(CLASSES)[i + 1]]
            options = (class_1[3].title(), class_2[3].title())
            check = lambda message: (
                message.author
                and message.author.id == ctx.author.id
                and message.channel.name == ctx.channel.name
                and message.content.title() in options
            )
            await ctx.reply(f"antes de continuar, você deve escolher sua nova classe: {options[0]} ou {options[1]}?")
            try:
                response = await self.bot.wait_for("message", check, timeout=60)
            except Exception:
                return None
            else:
                message = response[0]
                option = message.content.lower()
                main_class = [key for key, value in CLASSES.items() if value[3].lower() == option][0]
                ctx.user.update_dungeon(main_class=main_class)
                _class = CLASSES[ctx.user.dungeons._class][min(ctx.user.dungeons.level, 60) // 10]
                await ctx.reply(f"agora você é um {_class}")

        if (
            timeago(ctx.user.dungeons.updated_on).total_in_seconds() < 10800
            and ctx.user.dungeons.created_on.isoformat()[:18] != ctx.user.dungeons.updated_on.isoformat()[:18]
        ):
            delta = timeago(ctx.user.dungeons.updated_on + timedelta(seconds=10800), reverse=True).humanize()
            return await ctx.reply(f"aguarde {delta} para entrar em outra dungeon ⌛")

        i = random_number(min=0, max=len(DUNGEONS) - 1)
        dungeon = DUNGEONS[i]
        option = random_choice(["1", "2"])
        result = random_choices(["win", "lose"], w=(0.66, 0.33))[0]
        quote = f'{dungeon["quote"]} você decide {dungeon[option]["option"]}'
        if result == "win":
            experience = int(random_number(min=50, max=75) + 3 * ctx.user.dungeons.level)
            if ctx.user.dungeons.experience + experience > 100 * (ctx.user.dungeons.level) + 25 * sum(range(1, ctx.user.dungeons.level + 1)):
                ctx.user.update_dungeon(win=True, experience=experience, level_up=True)
                return await ctx.reply(f"{quote} e {dungeon[option][result]}! +{experience} XP e alcançou level {ctx.user.dungeons.level} ⬆")
            else:
                ctx.user.update_dungeon(win=True, experience=experience)
                return await ctx.reply(f"{quote} e {dungeon[option][result]}! +{experience} XP")
        else:
            ctx.user.update_dungeon(defeat=True)
            return await ctx.reply(f"{quote} e {dungeon[option][result]}! +0 XP")

    @helper("veja qual o seu level (ou de alguém) e outras estatísticas da dungeon")
    @usage("para usar: %level <nome_do_usuario|autor>")
    @cooldown(rate=3, per=10, bucket=Bucket.member)
    @command(aliases=["lvl"])
    async def level(self, ctx: Context, name: str = "") -> None:
        name = name or ctx.author.name
        if name == self.bot.nick:
            return await ctx.reply("eu apenas crio as dungeons...")
        if name == ctx.author.name:
            user = ctx.user
        else:
            user = await self.bot.fetch_user_db(name)
            if not user:
                return await ctx.reply(f"@{name} ainda não foi registrado (não usou nenhum comando)")
        if user.settings and not user.settings.mention:
            return await ctx.reply("esse usuário optou por não permitir ser mencionado")
        mention = "você" if name == ctx.author.name else f"@{name}"
        if user.dungeons:
            _class = CLASSES[ctx.user.dungeons._class][min(ctx.user.dungeons.level, 60) // 10]
            winrate = user.dungeons.wins / (user.dungeons.total or 1) * 100
            return await ctx.reply(
                f"{mention} é {_class} (LVL {user.dungeons.level}), com {user.dungeons.total} dungeons "
                f"({user.dungeons.wins} vitórias, {user.dungeons.defeats} derrotas, {winrate:.2f}% winrate) ♦"
            )
        return await ctx.reply(f"{mention} ainda não entrou em nenhuma dungeon")

    @helper("saiba quais são os melhores jogadores da dungeon")
    @cooldown(rate=3, per=10, bucket=Bucket.member)
    @command()
    async def rank(self, ctx: Context, order_by: str = "") -> None:
        # TODO: %rank
        raise NotImplementedError()


def prepare(bot: Broxotinho) -> None:
    bot.add_cog(Dungeon(bot))
