import os
import apexpy
import coc
import logging
import disnake
from apexpy import ApexApi
from dotenv import load_dotenv
from disnake.ext import commands

from utils.dutils import paginate
from apexpy.exceptions import PlayerNotFoundError

load_dotenv("secrets.env")
apitoken = os.getenv("apextoken")


async def looper(stats):
    totalstring = ""
    avoidable = ["specific", "Specific1", "Specific2", "specific3", "rank"]
    for stat in stats:
        for key in stat.keys():
            if key in avoidable:
                continue
            totalstring += f"> **{key}**: `{stat[key]}` \n"
    return totalstring


class Gaming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player = ApexApi(key=apitoken)

    @commands.command(
        description="gets info about a player using their username accepted platforms are: psn, xbl, pc"
    )
    async def apexprofile(
        self,
        ctx: commands.Context,
        platform="pc",
        *,
        username,
    ) -> None:
        await ctx.trigger_typing()
        try:
            await self.player.search(username, platform)
        except PlayerNotFoundError:
            await ctx.send(
                f"player `{username}` not found in database. check the spelling and try again"
            )
            return

        main_embed = disnake.Embed(
            title=f"***{username}***",
            description="remember its about skills not about kills",
        )

        legend_names = "\n".join(f"> {legend.name}" for legend in self.player.legends)
        totalstatsstring = await looper(self.player.stats)

        main_embed.add_field(
            name="Details",
            value=f"""
            ***__stats__***
            {totalstatsstring}
            ***__legends__***
            {legend_names}
            """,
        )
        embedlist = [main_embed]
        for legend in self.player.legends:
            emby = disnake.Embed(title=f"{legend.name}")
            emby.set_thumbnail(url=legend.icon)
            emby.set_image(url=legend.bgimage)
            totalstatsstring = await looper(legend.stats)
            emby.add_field(
                name="Stats",
                value=f"""
                {totalstatsstring}
                """,
            )
            embedlist.append(emby)
        await paginate(ctx, embedlist)

    logging.basicConfig(level=logging.ERROR)

   

def setup(bot):
    bot.add_cog(Gaming(bot))
