import disnake
from disnake.ext import commands


class Misc(commands.Cog, name="misc"):
    """
    miscellanous,
    Contains commands that dont fit other groups
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description=" sends the ping of the bot")
    async def ping(self, ctx: commands.Context):
        embed = disnake.Embed(title="Pong!", timestamp=ctx.message.created_at)
        embed.add_field(
            name="⮚ current ping", value=f"> ` {round(self.bot.latency*1000,1)} `"
        )
        y = 0
        for m in self.bot.guilds:
            y += len(m.members)
        embed.set_footer(text=f"Servers in: {len(self.bot.guilds)} │ Overall users: {y}")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
