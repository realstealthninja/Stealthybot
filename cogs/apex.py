import os
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands
from utilities.pagination import *
load_dotenv(dotenv_path=".env")
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
class Apex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description="gets info about a player using their username accepted platforms are: psn, xbl, orgin")
    async def getplayer(self, ctx, username, platform= "psn" or "xbl" or "orgin"):
        ctx.trigger_typing
        r= requests.get(f"https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{username}", headers={"TRN-Api-Key": f"{apitoken}", "Accept": "application/json", "Accept-Encoding":"gzip"})
        respcode = r.status_code
        if respcode != 200:
            await ctx.reply("a error occured try checking your spelling or wait a while and try again")
        else:
            Datakek = r.json()
            data = Datakek["data"]
            
            social = get_socials(data["userInfo"]["socialAccounts"])            
            embed = discord.Embed(title=data["platformInfo"]["platformUserId"], description=f"{social}")
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
            
            emby = discord.Embed(title ="Over View")
            killspermatch = ""
            winningkills =""
            killsaskillleader =""
            totaldamage = ""
            revives = ""
            sniperkills = ""
            if "killsPerMatch" in data["segments"][0]["stats"]:
                killspermatch = data["segments"][0]["stats"]["killsPerMatch"]["displayValue"]
            else: killspermatch = "no data"
            if "winningKills" in data["segments"][0]["stats"]:
                winningkills = data["segments"][0]["stats"]["winningKills"]["displayValue"]
            else: winningkills ="no data"
            if "killsAsKillLeader" in data["segments"][0]["stats"]:
                killsaskillleader = data["segments"][0]["stats"]["killsAsKillLeader"]["displayValue"]
            else: killsaskillleader = "none"
            if "damage" in data["segments"][0]["stats"]:
                totaldamage = data["segments"][0]["stats"]["damage"]["displayValue"]
            else: totaldamage = "0"
            if "revives" in data["segments"][0]["stats"]:
                revives =  data["segments"][0]["stats"]["revives"]["displayValue"]
            else: revives = "0"
            if "sniperKills" in data["segments"][0]["stats"]:
                sniperkills = data["segments"][0]["stats"]["sniperKills"]["displayValue"]
            else: sniperkills = "0"
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
            em = discord.Embed(title=data["segments"][1]["metadata"]["name"], description="hey there i make this bot for free! you can check out its code in s?help ")
            em.set_thumbnail(url=data["segments"][1]["metadata"]["imageUrl"])
            em.add_field(name="active legend", value=data["segments"][1]["metadata"]["isActive"])
            em.set_image(url=data["segments"][1]["metadata"]["bgImageUrl"])
            listofem = [embed, emby,em]
            
            await paginate(ctx=ctx,embeds=listofem)
            

def setup(bot):
    bot.add_cog(Apex(bot))
