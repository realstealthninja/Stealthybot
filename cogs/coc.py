import logging
import discord
from dotenv.main import load_dotenv
from discord.ext import commands
import stealthybot.utils.images as images
import os
import coc
from coc import utils


load_dotenv(dotenv_path="secrets.env")

class Coc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # TODO: add more commands 
    
    
    
    logging.basicConfig(level=logging.ERROR)
    @commands.command(description="gets the clan detailed about the specified clan")
    async def claninfo(self, ctx, clan_tag, ):
        ctx.trigger_typing
        if not utils.is_valid_tag(clan_tag):

            await ctx.send("You didn't give me a proper tag!")
            return


        try:

            clan = await self.coc_client.get_clan(clan_tag)

        except coc.NotFound:

            await ctx.send("This clan doesn't exist!")

            return



        if clan.public_war_log is False:

            log = "Private"

        else:

            log = "Public"


        e = discord.Embed(title="Clan details")

        e.set_thumbnail(url=clan.badge.url)
        
        e.add_field(name="Clan Name", value=f"{clan.name}({clan.tag})\n[Open in game]({clan.share_link})", inline=False)
        e.add_field(name="Description", value=clan.description, inline=False)
        e.add_field(name="Leader", value=clan.get_member_by(role=coc.Role.leader))
        e.add_field(name="Clan Type", value=clan.type)
        e.add_field(name="Location", value=clan.location)
        e.add_field(name="Total Clan Trophies", value=f"{clan.points} <:Trophy:896983724686737439>")
        e.add_field(name="Total Clan Versus Trophies", value=f"{clan.versus_points}  <:Icon_Versus_Trophy:896979379094184016>")
        e.add_field(name="Required Trophies", value=f" {clan.required_trophies} <:Trophy:896983724686737439>" , inline=False)
        e.add_field(name="War Win Streak", value=clan.war_win_streak, inline=False)
        e.add_field(name="War Frequency", value=clan.war_frequency, inline=False)
        e.add_field(name="Clan War League Rank", value=clan.war_league, inline=False)
        e.add_field(name="Clan Labels", value="\n".join(f"> {label.name}" for label in clan.labels), inline=False)
        e.add_field(name="Member Count", value=f"> {clan.member_count}/50", inline=False)
        e.add_field(

            name="Clan Record",

            value=f"> Won - {clan.war_wins}\n> Lost - {clan.war_losses}\n> Draw - {clan.war_ties}",

            inline=False

        )
        e2= ""
        async for player in clan.get_detailed_members():
            e2 += f"> {player.name} \n"
        e.add_field(name="Members", value=e2)
        await ctx.send(embed=e)
      
    @commands.command()
    async def playerheroes(self,ctx, player_tag):
        if not utils.is_valid_tag(player_tag):
           await ctx.send("You didn't give me a proper tag!")
           return
        try:
           player = await self.bot.coc_client.get_player(player_tag)
        except coc.NotFound:
           await ctx.send("This player doesn't exist!")
           return
    
        to_send = ""
        listofimages =[]
        if len(player.heroes) == 1:
           embed = discord.Embed(title="Player heros")
           embed.set_image(url=f"attachment://assets/heros/{player.heroes[0]}.png")
           embed.add_field(name=str(player.heroes[0]), value="Lv{}/{}".format(player.heroes[0].level,player.heroes[0].max_level))
           await ctx.send(embed=embed)
        
        else:
            for hero in player.heroes:
                listofimages.append(f"assets/heros/{str(hero)}.png")
                to_send += "{}: Lv{}/{}   ".format(str(hero), hero.level, hero.max_level)
            imgpath = images.stichimgs(listofimages,"herostiched")
            embed = discord.Embed(title="Player Heroes")
            embed.set_image(url=f"attachment://{imgpath}")
            embed.add_field(name=to_send,value="⠀")
            
            file = discord.File("assets/stichedimages/herostiched.png")
            await ctx.send(file=file,embed=embed)
            os.remove(imgpath)
       
def setup(bot):
    bot.add_cog(Coc(bot))
