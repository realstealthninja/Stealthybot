""" The main file for the activity cog """

import disnake
from disnake.ext import commands

from .activityhelpers import ActivityHelper

class Activity(commands.Cog):
    """ Main cog for all the activity commands and detection"""

    def __init__(self, bot):
        self.bot = bot
        self.database = self.bot.act_database    
        self.act_helper = ActivityHelper(self.database)
        self.cooldown = commands.CooldownMapping.from_cooldown(5.0, 10.0, commands.BucketType.user)


    @commands.Cog.listener("on_message")
    async def activity_listener(self, message :disnake.Message):
        """Activity listener it listens for activity in the server

        Args:
            message (disnake.Message): Message the the user provides
        """
        # main anti spam
        retry_after = self.cooldown.get_bucket(message).update_rate_limit()

        if retry_after or message.author.bot:
            return

        await self.act_helper.select_one("Users", filter_column="")
def setup(bot):
    """Adding the cog to the bot

    Args:
        bot (Stealthybot): The bot that the cog must be inserted into
    """
    bot.add_cog(Activity(bot))
