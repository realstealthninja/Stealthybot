""" The main file for the activity cog """

import datetime

import disnake
from disnake.ext import commands
from disnake.ext import tasks

from .activityhelpers import ActivityHelper
from .views import SetupActivity

NAMES = [
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
    "chat",
    "main-chat",
]


class Activity(commands.Cog, name="activity"):
    """Main cog for all the activity commands and detection"""

    def __init__(self, bot):
        self.bot = bot
        self.database = self.bot.act_database
        self.act_helper = ActivityHelper(self.bot)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            5.0, 10.0, commands.BucketType.user
        )
        self.reset.start()

    @tasks.loop(seconds=1.0)
    async def reset(self):
        """
        Resets the msg count after the time runs out
        """
        async with self.bot.act_database.execute("SELECT * FROM Time") as cursor:
            async for row in cursor:
                unixtime = datetime.datetime.fromtimestamp(row[1])
                now = datetime.datetime.utcnow()
                if unixtime.replace(microsecond=0) != now.replace(microsecond=0):
                    continue
                await self.act_helper.set_time(row[0])
                guild: disnake.Guild = self.bot.get_guild(row[0])

                userlist = await self.act_helper.fetch_users(guild.id)
                for user in userlist:
                    user = await guild.getch_member(user[1])
                    if not user:
                        await self.act_helper.delete(
                            "Users",
                            filter_columns=[
                                "ServerID",
                                "UserID",
                            ],
                            filter_values=(userlist[0][0], userlist[0][1]),
                        )
                leaderboard_text = (
                    "`Sl.|                  Name                  | Msg `\n```\n"
                )
                leaderboard_text = await self.leaderboard_maker(
                    guild, 3, leaderboard_text
                )
                embed = disnake.Embed().add_field(
                    name="⠀­", value=f"{leaderboard_text}```"
                )

                await self.act_helper.update_set(
                    "Users",
                    column=[
                        "MsgCount",
                    ],
                    values=(0,),
                )

                for k in guild.text_channels:
                    if k.name in NAMES or "general" in k.name or "chat" in k.name:
                        await k.send(embed=embed)
                        return await k.send(
                            embed=disnake.Embed(
                                title="The leaderboard has been reset",
                                description="Thank you for being active",
                            )
                        )

    @commands.command()
    async def activity(self, ctx: commands.Context, member: disnake.Member = None):
        """
        Activity rank command
        """

        if not await self.act_helper.fetch_server(ctx.guild.id):
            return

        if not member:
            member = ctx.guild.get_member(ctx.author.id)

        await self.act_helper.create_or_fetch_user(member.id, ctx.guild.id)
        image = await self.act_helper.create_act_image(member)

        await ctx.send(
            file=disnake.File(
                fp=image,
                filename="Activity.png",
                description="You know its bad when you have activity points",
            )
        )

    @reset.before_loop
    async def before_reset(self):
        """
        wait until the bot is ready before starting the loop
        """
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_message")
    async def activity_listener(self, message: disnake.Message):
        """
        Activity listener it listens for activity in the server

        Parameters
        ==========
        message (disnake.Message): Message the the user provides
        """
        # main anti spam
        retry_after = self.cooldown.get_bucket(message).update_rate_limit()

        if not message.guild:
            return

        server = await self.act_helper.fetch_server(message.guild.id)

        if not server or message.author.bot or retry_after:
            return

        user = await self.act_helper.create_or_fetch_user(
            message.author.id, message.guild.id
        )

        await self.act_helper.update_set(
            "Users",
            column=["MsgCount", "TotalMsgCount"],
            values=(user[3] + 1, user[4] + 1),
            filter_columns=["ServerID", "UserID"],
            filter_values=(user[0], user[1]),
        )

        if user[3] + 1 == server[1]:
            await self.act_helper.update_set(
                "Users",
                column=["ActScore"],
                values=(user[2] + 1,),
                filter_columns=["ServerID", "UserID"],
                filter_values=(user[0], user[1]),
            )
            msg = await self.act_helper.fetch_message(server[0])
            embed = await self.act_helper.fetch_embed(server[0])
            msg = msg[0]
            if msg:
                await message.channel.send(
                    msg.replace("MENTION_USER", f"{message.author.mention}")
                    .replace("MSG_COUNT", f"{user[3]}")
                    .replace("TOTAL_MSG_COUNT", f"{user[4]}")
                    .replace("MSG_GOAL", f"{server[1]}")
                    .replace("USERNAME", f"{message.author.display_name}")
                )
            if embed:
                embed.title.replace(
                    "MENTION_USER", f"{message.author.mention}"
                ).replace("MSG_COUNT", f"{user[3]}").replace(
                    "TOTAL_MSG_COUNT", f"{user[4]}"
                ).replace(
                    "MSG_GOAL", f"{server[1]}"
                ).replace(
                    "USERNAME", f"{message.author.display_name}"
                )
                embed.description.replace(
                    "MENTION_USER", f"{message.author.mention}"
                ).replace("MSG_COUNT", f"{user[3]}").replace(
                    "TOTAL_MSG_COUNT", f"{user[4]}"
                ).replace(
                    "MSG_GOAL", f"{server[1]}"
                ).replace(
                    "USERNAME", f"{message.author.display_name}"
                )
                await message.channel.send(embed=embed)

    @commands.command(name="setup")
    @commands.has_permissions(manage_messages=True)
    async def _setup_act_(self, ctx: commands.Context):
        """
        Setup command for activity.
        This is used to setup the activity in a server.
        It makes use of buttons for easier time setting up!
        """
        await ctx.send(
            embed=disnake.Embed(
                title="Welcome to the setup!",
                description="""
                press the `confirm` button to continue with the setup!
                """,
            ),
            view=SetupActivity(ctx, self.act_helper),
        )

    @commands.group(name="leaderboard", aliases=["lb", "board"], pass_context=True)
    async def leaderboard(self, ctx: commands.Context):
        """
        checks for the leaderboard sub commands
        """
        if not ctx.invoked_subcommand:
            return

        server = await self.act_helper.fetch_server(ctx.guild.id)
        if not server:
            return await ctx.send(
                "Uh oh! this server wasnt found in my database! \
                ask an admin to add it by sb?setup !"
            )

    @leaderboard.command(name="msg")
    async def msg_count(self, ctx: commands.Context):
        """
        Leaderboard command shows the ranking of each user
        in the server accoring to their amount of messages
        """

        leaderboard_text = "`Sl.|                  Name                  | Msg `\n```\n"
        leaderboard_text = await self.leaderboard_maker(ctx.guild, 3, leaderboard_text)
        embed = disnake.Embed().add_field(name="⠀­", value=f"{leaderboard_text}```")
        await ctx.send(embed=embed)

    @leaderboard.command(name="act")
    async def act_count(self, ctx: commands.Context):
        """
        Leaderboard command shows the ranking of each user
        in the server accoring to their amount of ACT POINTS
        """

        leaderboard_text = "`Sl.|                  Name                  | ACT `\n```\n"
        leaderboard_text = await self.leaderboard_maker(ctx.guild, 2, leaderboard_text)
        embed = disnake.Embed().add_field(name="⠀­", value=f"{leaderboard_text}```")
        await ctx.send(embed=embed)

    @leaderboard.command(name="total")
    async def total_count(self, ctx: commands.Context):
        """
        Leaderboard command shows the ranking of each user
        in the server accoring to their amount of total messages
        """

        leaderboard_text = "`Sl.|                  Name                  | Msg `\n```\n"
        leaderboard_text = await self.leaderboard_maker(ctx.guild, 4, leaderboard_text)
        embed = disnake.Embed().add_field(name="⠀­", value=f"{leaderboard_text}```")
        await ctx.send(embed=embed)

    async def check_user_pop(self, guild: disnake.Guild, userlist: list) -> list:
        """
        checks the list of users then pops the ones that have left the guild or dont exist
        """
        for user in userlist:
            member = guild.get_member(user[1])
            if not member:
                userlist.pop(userlist.index(user))
        return userlist

    async def leaderboard_maker(
        self, guild: disnake.Guild, index: int, toptext: str
    ) -> str:
        """
        Creates a leaderboard based on the parameter given

        Parameter
        =========
        guild: `disnake.Guild`
        index: `int`
        toptext: `str`
        """
        users = await self.act_helper.fetch_users(guild.id)
        users = await self.check_user_pop(guild, users)
        users.sort(key=lambda i: i[index], reverse=True)
        if len(users) > 10:
            while len(users) != 10:
                users.pop(len(users) - 1)

        for count, user in enumerate(users):
            if count + 1 == 11:
                break
            name = await guild.getch_member(user[1])
            name = name.display_name
            msg_count = str(user[index])
            if len(name) != 32:
                name += "".join(" " for num in range(32 - len(name)))
            toptext += str(count + 1) + " | " + name + " | " + msg_count + "\n"
        return toptext


def setup(bot):
    """Adding the cog to the bot

    Parameters
    ==========
    bot (Stealthybot): The bot that the cog must be inserted into
    """
    bot.add_cog(Activity(bot))
