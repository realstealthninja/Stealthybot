"""Main cog module for fun commands."""

import disnake
from disnake.ext import commands

from .views import Truthordare


class Fun(commands.Cog, name="fun"):
    """Fun cog Has commands which is fun to use."""

    def __init__(self, bot):
        """For setting bot."""
        self.bot = bot

    @commands.command()
    async def truthordare(self, ctx: commands.Context):
        """Truth or dare command click the button of the question you want."""
        await ctx.send(
            embed=disnake.Embed(
                title="Truth or dare?",
                description="Pick what type of question/dare you want",
            ),
            view=Truthordare(ctx, self.bot),
        )


def setup(bot):
    """Add the cog to the bot."""
    bot.add_cog(Fun(bot))
