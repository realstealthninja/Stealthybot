""" The main file for the activity cog """

import disnake
from disnake.ext import commands

from .activityhelpers import ActivityHelper
from .views import SetupActivity


class Activity(commands.Cog):
    """ Main cog for all the activity commands and detection"""

    def __init__(self, bot):
        self.bot = bot
        self.database = self.bot.act_database
        self.act_helper = ActivityHelper(self.bot)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            5.0,
            10.0,
            commands.BucketType.user
        )

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
        server = await self.act_helper.fetch_server(
            message.guild.id
        )

        if not server or message.author.bot or retry_after:
            return

        user = await self.act_helper.create_or_fetch_user(
            message.author.id,
            message.guild.id
        )

        await self.act_helper.update_set(
            "Users",
            column=[
                "MsgCount",
                "TotalMsgCount"
            ],
            values=(
                user[3] + 1,
                user[4] + 1
            ),
            filter_columns=[
                "ServerID",
                "UserID"
            ],
            filter_values=(
                user[0],
                user[1]
            )
        )

        if user[3] + 1 == server[1]:
            await self.act_helper.update_set(
                "Users",
                column=[
                    "ActScore"
                ],
                values=(
                    user[2] + 1,
                ),
                filter_columns=[
                    "ServerID",
                    "UserID"
                ],
                filter_values=(
                    user[0],
                    user[1]
                )
            )
            msg = await self.act_helper.fetch_message(server[0])
            embed = await self.act_helper.fetch_embed(server[0])
            if msg:
                await message.channel.send(
                    msg.replace(
                        "MENTION_USER",
                        f"{message.author.mention}"
                    ).replace(
                        "MSG_COUNT",
                        f"{user[3]}"
                    ).replace(
                        "TOTAL_MSG_COUNT",
                        f"{user[4]}"
                    ).replace(
                        "MSG_GOAL",
                        f"{server[1]}"
                    ).replace(
                        "USERNAME",
                        f"{message.author.display_name}"
                    )
                )
            if embed:
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
                """
            ),
            view=SetupActivity(ctx, self.act_helper)
        )


def setup(bot):
    """Adding the cog to the bot

    Parameters
    ==========
    bot (Stealthybot): The bot that the cog must be inserted into
    """
    bot.add_cog(Activity(bot))
