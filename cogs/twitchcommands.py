import disnake
import json
from disnake.ext import commands
from utils.dutils import jsonwriter as Json

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(aliases=["ac"], description="adds twitch chat to a specified channel")
    async def addchat(self, ctx, channelid=None):
            with open("Jsons/chatchannel.json", "r+") as f:
                datakek = json.load(f)
                if (channelid == None):
           
                    datakek[str(ctx.channel.id)] = {
                    "channelid": f"{ctx.guild.id}"
                    }
                    Json(f, datakek)
                    await ctx.send("channel added")
                if(channelid != None):
                    datakek[str(channelid)] = {
                        "guild": f"{ctx.guild.id}"
                    }
                    Json(f, datakek)
                    await ctx.send("channel added")
                    
    @commands.command(aliases=["achannel"], description="adds your channel to the the twitch bot ")
    async def addchannel(self, ctx, channelname:str):
        with open("Jsons/Twitchchannels.json", "r+") as f:
            datakek = json.load(f)
            datakek[str(channelname)]
            Json(f, datakek)
            await ctx.send("channel added to the bot")
 
def setup(bot):
    bot.add_cog(Twitch(bot))
