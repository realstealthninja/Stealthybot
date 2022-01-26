import os
import coc
import logging
import disnake
import requests

from coc import utils
from dotenv import load_dotenv
from disnake.ext import commands

import utils.images as images
from utils.dutils import paginate





load_dotenv("secrets.env")
apitoken=os.getenv('apextoken')

def get_socials(list):
    bettasstring = " "
    for item in list:
        if item ["platformSlug"] == "twitter":
            userid = item["platformUserHandle"]
            bettasstring += f" <:twitter:898880366725709864> @{userid} "
        elif item["platformSlug"] =="twitch":
            userid = item["platformUserHandle"]
            bettasstring += f" <:twitch:898882021647077386>  {userid} "
            
    return bettasstring

class Gaming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(description="gets info about a player using their username accepted platforms are: psn, xbl, orgin")
    async def getplayer(self, ctx, username, platform="orgin"):
        ctx.trigger_typing
        r= requests.get(f"https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{username}", headers={"TRN-Api-Key": f"{apitoken}", "Accept": "application/json", "Accept-Encoding":"gzip"})
        respcode = r.status_code
        if respcode != 200:
            await ctx.reply("a error occured try checking your spelling or wait a while and try again")
        else:
            data = r.json()["data"]
            
            social = get_socials(data["userInfo"]["socialAccounts"])            
            embed = disnake.Embed(title=data["platformInfo"]["platformUserId"], description=f"{social}")
            embed.set_thumbnail(url=data["platformInfo"]["avatarUrl"])

            hugetext = f"""
            Country code: {data["userInfo"]["countryCode"]}
            total page views: {str(data["userInfo"]["pageviews"])}
            
            """
            embed.add_field(name="Info", value=hugetext)
            activestats = ""
            if data["metadata"]["activeLegendStats"] != None:
            
                for stats in data["metadata"]["activeLegendStats"]:
                    activestats += stats
            
            metatext = f"""
            current half: {data["metadata"]["currentSeason"]}
            Active legend: {data["metadata"]["activeLegendName"]}
            Active legend stats: {activestats}
            """
            embed.add_field(name="meta data", value=metatext)
            
            emby = disnake.Embed(title ="Over View")
            revives,sniperkills,totaldamage,killsaskillleader,winningkills,killspermatch = "0"
            try:
                killspermatch = data["segments"][0]["stats"]["killsPerMatch"]["displayValue"]
                winningkills = data["segments"][0]["stats"]["winningKills"]["displayValue"]
                killsaskillleader = data["segments"][0]["stats"]["killsAsKillLeader"]["displayValue"]
                totaldamage = data["segments"][0]["stats"]["damage"]["displayValue"]
                revives =  data["segments"][0]["stats"]["revives"]["displayValue"]
                sniperkills = data["segments"][0]["stats"]["sniperKills"]["displayValue"]
                
            except KeyError:
                pass
            overview = f"""
            NAME: `{data["segments"][0]["metadata"]["name"]}`
            
            
            > rank Score : `{data["segments"][0]["stats"]["rankScore"]["displayValue"]}`
            
            > Kills: `{data["segments"][0]["stats"]["kills"]["displayValue"]}`
            
            > kills per match: `{killspermatch}`
            
            > Winning Kills: `{winningkills}`
            
            > Kills As Kill Leader: `{killsaskillleader}`
            
            > total damage done: `{totaldamage}`
            
            > matches played: `{data["segments"][0]["stats"]["matchesPlayed"]["displayValue"]}`
            
            > revives: `{revives}`
            
            > sniper kills: `{sniperkills}`
            
            
            """
            emby.add_field(name=data["segments"][0]["metadata"]["name"], value=overview)
            em = disnake.Embed(title=data["segments"][1]["metadata"]["name"], description="hey there i make this bot for free! you can check out its code in s?help ")
            em.set_thumbnail(url=data["segments"][1]["metadata"]["imageUrl"])
            em.add_field(name="active legend", value=data["segments"][1]["metadata"]["isActive"])
            em.set_image(url=data["segments"][1]["metadata"]["bgImageUrl"])
            listofem = [embed, emby,em]
            
            await paginate(ctx=ctx,embeds=listofem)
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


        e = disnake.Embed(title="Clan details")

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
           embed = disnake.Embed(title="Player heros")
           embed.set_image(url=f"attachment://assets/heros/{player.heroes[0]}.png")
           embed.add_field(name=str(player.heroes[0]), value="Lv{}/{}".format(player.heroes[0].level,player.heroes[0].max_level))
           await ctx.send(embed=embed)
        
        else:
            for hero in player.heroes:
                listofimages.append(f"assets/heros/{str(hero)}.png")
                to_send += "{}: Lv{}/{}   ".format(str(hero), hero.level, hero.max_level)
            imgpath = images.stichimgs(listofimages,"herostiched")
            embed = disnake.Embed(title="Player Heroes")
            embed.set_image(url=f"attachment://{imgpath}")
            embed.add_field(name=to_send,value="⠀")
            
            file = disnake.File("assets/stichedimages/herostiched.png")
            await ctx.send(file=file,embed=embed)
            os.remove(imgpath)    

def setup(bot):
    bot.add_cog(Gaming(bot))
