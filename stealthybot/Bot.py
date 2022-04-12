"""stealthy bot module"""


import os
import coc
import dotenv
import disnake

import aiosqlite
from disnake.ext import commands


dotenv.load_dotenv("secrets.env")


class Stealthybot(commands.Bot):
    """Stealthy bot class"""
    coc_client = coc.login(
        email=os.getenv("cocemail"),
        password=os.getenv("cocpass"),
        key_names="test",
        client=coc.EventsClient,
    )

    def __init__(self):
        super().__init__(
            command_prefix="sb?",
            description="worst bot ever lol",
            intents=disnake.Intents.all(),
            case_insensitive=True,
            owner_ids=[521226389559443461],
        )
        self.eco_base = None
        self.config = None
        self.act_database = None
        self.loop.create_task(self.connect_databases())

        for filename in os.listdir("./cogs/"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")
            else:
                if filename.startswith("_"):
                    continue
                self.load_extension(f"cogs.{filename}")

    # connecting the db
    async def connect_databases(self):
        self.eco_base = await aiosqlite.connect("database/economy.db")
        self.config = await aiosqlite.connect("database/config.db")
        self.act_database = await aiosqlite.connect("database/config.db")

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

        await self.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=f"{self.command_prefix}help on {len(self.guilds)} servers",
            )
        )
        print(disnake.__version__)

    async def on_guild_join(self, guild):

        embed = disnake.Embed(
            title="Thank you for using stealthy bot",
            description="""
            its means alot to me that you invited my bot.
            it keeps me motivated to work on it more.

            **`s?help`** for the help menu
            **`s?help setupact`** to read up on how to setup activity for your server.

            hope you enjoy using stealthy bot! 🤗
            join the [offical support server](https://discord.gg/HAbStFeVAj) for any questions or help 🙂
            """,
        )
        names = [
            "general",
            "genchat",
            "generalchat",
            "general-chat",
            "general-talk",
            "gen",
            "talk",
            "general-1",
            "🗣general-chat",
            "🗣",
            "🗣general",
        ]
        for k in guild.text_channels:
            if k.name in names or "general" in k.name:
                return await k.send(embed=embed)

        await guild.system_channel.send(embed=embed)
