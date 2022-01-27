import os
import apexpy
import coc
import logging
import disnake

from coc import utils
from apexpy import ApexApi
from dotenv import load_dotenv
from disnake.ext import commands

from utils.dutils import paginate
from apexpy.exceptions import PlayerNotFoundError

load_dotenv("secrets.env")
apitoken = os.getenv('apextoken')

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

    @commands.command(description="gets info about a player using their username accepted platforms are: psn, xbl, pc")
    async def apexprofile(self, ctx, platform="pc",*,username,) -> None:
        await ctx.trigger_typing()
        try:
            await self.player.search(username, platform)
        except PlayerNotFoundError:
            await ctx.send(f"player `{username}` not found in database. check the spelling and try again")
            return

        main_embed = disnake.Embed(
            title=f"***{username}***",
            description="remember its about skills not about kills"
        )

        legend_names = '\n'.join(
            f'> {legend.name}' for legend in self.player.legends)
        totalstatsstring = await looper(self.player.stats)

        main_embed.add_field(
            name="Details",
            value=f"""
            ***__stats__***
            {totalstatsstring}
            ***__legends__***
            {legend_names}
            """
        )
        embedlist = [main_embed]
        for legend in self.player.legends:
            emby = disnake.Embed(
                title=f"{legend.name}"
            )
            emby.set_thumbnail(url=legend.icon)
            emby.set_image(url=legend.bgimage)
            totalstatsstring = await looper(legend.stats)
            emby.add_field(
                name="Stats",
                value=f"""
                {totalstatsstring}
                """
            )
            embedlist.append(emby)
        await paginate(ctx, embedlist)

    logging.basicConfig(level=logging.ERROR)

    @commands.command(description="gets the clan detailed about the specified clan")
    async def clanprofile(self, ctx, clan_tag, ):
        await ctx.trigger_typing()
        if not utils.is_valid_tag(clan_tag):
            await ctx.send("You didn't give me a proper tag!")
            return

        try:
            clan = await self.bot.coc_client.get_clan(clan_tag)
        except coc.NotFound:
            await ctx.send("This clan doesn't exist!")
            return

        e = disnake.Embed(
            title="Clan details"
        )

        e.set_thumbnail(url=clan.badge.url)

        coleaders = clan.get_member_by(role=coc.Role.co_leader)
        labels = "\n".join(f"> {label.name}" for label in clan.labels)

        e.add_field(
            name=f"**{clan.name} {clan.tag}**   | {clan.type}",
            value=f"""
               `{clan.description}`
            > **location**: {clan.location}
            
            > **Total players**: **`{clan.member_count}/50`**
            
            > **Join requirement**: `{clan.required_trophies} <:Trophy:896983724686737439>`
            > **Trophies**: `{clan.points} <:Trophy:896983724686737439>`
            > **Verses Trophies**: `{clan.points} <:Trophy:896983724686737439>`
            
            > **Leader**: `{clan.get_member_by(role=coc.Role.leader)}`
            > **Co-Leader(s)**:
            > `{coleaders}`

            **labels**: 
            {labels}
            
            > **Win Streak**: `{clan.war_win_streak}`
            > **League war rank**: `{clan.war_league}` 
            """
        )
        e.add_field(
            name="Clan Record",
            value=f"> Wins - `{clan.war_wins}`\n> Losses - `{clan.war_losses}`\n> Draws - `{clan.war_ties}`",
            inline=False
        )

        e.add_field(
            name="Members",
            value="\n".join(
                f"> {player.name}" async for player in clan.get_detailed_members())
        )
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Gaming(bot))
