import logging
import os
from dotenv.main import load_dotenv

from utils.pagination import *
import discord
from discord.ext import commands


import coc
from coc import utils



load_dotenv(dotenv_path="secrets.env")
print(os.getenv('cocemail'))
print(os.getenv('cocpass'))
coc_client = coc.login(

    email = os.getenv('cocemail'),

    password =os.getenv('cocpass'),

    key_names="test",

    client=coc.EventsClient,

)
class Coc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # TODO: add more commands and figure out pagination
    
    
    logging.basicConfig(level=logging.ERROR)
    @commands.command()
    async def claninfo(self, ctx, clan_tag):
        ctx.trigger_typing
        if not utils.is_valid_tag(clan_tag):

            await ctx.send("You didn't give me a proper tag!")
            return


        try:

            clan = await coc_client.get_clan(clan_tag)

        except coc.NotFound:

            await ctx.send("This clan doesn't exist!")

            return



        if clan.public_war_log is False:

            log = "Private"

        else:

            log = "Public"


        e = discord.Embed(title="Clan details",colour=discord.Colour.green())

        e.set_thumbnail(url=clan.badge.url)
        
        e.add_field(name="Clan Name", value=f"{clan.name}({clan.tag})\n[Open in game]({clan.share_link})", inline=False)

        e.add_field(name="Clan Level", value=clan.level, inline=False)

        e.add_field(name="Description", value=clan.description, inline=False)

        e.add_field(name="Leader", value=clan.get_member_by(role=coc.Role.leader), inline=False)

        e.add_field(name="Clan Type", value=clan.type, inline=False)

        e.add_field(name="Location", value=clan.location, inline=False)

        e.add_field(name="Total Clan Trophies", value=clan.points, inline=False)

        e.add_field(name="Total Clan Versus Trophies", value=clan.versus_points, inline=False)

        e.add_field(name="WarLog Type", value=log, inline=False)

        e.add_field(name="Required Trophies", value=clan.required_trophies, inline=False)

        e.add_field(name="War Win Streak", value=clan.war_win_streak, inline=False)

        e.add_field(name="War Frequency", value=clan.war_frequency, inline=False)

        e.add_field(name="Clan War League Rank", value=clan.war_league, inline=False)

        e.add_field(name="Clan Labels", value="\n".join(label.name for label in clan.labels), inline=False)

        e.add_field(name="Member Count", value=f"> {clan.member_count}/50", inline=False)

        e.add_field(

            name="Clan Record",

            value=f"Won - {clan.war_wins}\nLost - {clan.war_losses}\n Draw - {clan.war_ties}",

            inline=False

        )
        e2= ""
        async for player in clan.get_detailed_members():
            e2.join(f",{player.name}")
        
        await ctx.send(embed=e)
        y = Paginator(ctx)
        
        await y.paginate(content=f"{e2}")
    #commands.command()
    #async def player_heroes(ctx, player_tag):
    #   if not utils.is_valid_tag(player_tag):
    #       await ctx.send("You didn't give me a proper tag!")
    #       return
    #   try:
    #       player = await coc_client.get_player(player_tag)
    #   except coc.NotFound:
    #       await ctx.send("This player doesn't exist!")
    #       return
    #
    #   to_send = ""
    #   for hero in player.heroes:
    #    to_send += "{}: Lv{}/{}\n".format(str(hero), hero.level, hero.max_level)
    #   await ctx.send(to_send)
       
def setup(bot):
    bot.add_cog(Coc(bot))
