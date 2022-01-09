import json
import discord
import random
from discord.ext import commands
from discord.ext.commands.core import cooldown
from utils.dutils import jsonwriter as Json

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profiles = "Jsons/economy/profiles.json"
        self.jobs = "Jsons/economy/jobs.json"
        self.items = "Jsons/economy/items.json" 
        self.defaultstrings = ["frustra etiam in morte!","https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300"]
    async def citnara(self, num1, num2):
        """this returns if num 1 is greater than or equals to num2
            useless
        Args:
            num1 (int): firstnumber
            num2 (int): secondnumber

        Returns:
            True or False
        """     
        if num1 >= num2:
            return True
        else: return False
    
    async def add_or_find_account(self, userid:int):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if str(userid) in datakek:
                return None, datakek[userid]
            else:
                datakek[str(userid)] = {
                    "balance": 100,
                    "bank": 0,
                    "bank_cap": 100,
                    "job_id": "0",
                    "level": 0,
                    "inventory": []
                }   
                Json(f, datakek)
                return True
    async def addorremovemoney(self, userid:int, money:int):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if str(userid) in datakek:
                datakek[str(userid)]["balance"] = money
                Json(f, datakek)
    
    

    
    @commands.command()
    async def profile(self, ctx, member:discord.Member=""):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if member=="":

                if str(ctx.author.id) in datakek:
                    embed = discord.Embed(title=ctx.author.name)
                    embed.set_author(name=self.defaultstrings[0], icon_url=self.defaultstrings[1])
                    embed.set_thumbnail(url= ctx.author.avatar_url)
                    bal = datakek[str(ctx.author.id)]["balance"]
                    bank = datakek[str(ctx.author.id)]["bank"]
                    embed.add_field(name="Balance and bank",value=f"> <:stealthycoin:897331306013286440> {bal} || <:stealthycoin:897331306013286440> {bank}", inline=False)
                    with open(self.jobs, "r+") as jobjson:
                        jobkek = json.load(jobjson)
                    jobid = datakek[str(ctx.author.id)]["job_id"]
                    if jobid != "0":
                        jobname = jobkek[jobid]["name"]
                        embed.add_field(name="job", value=f"> {jobname}", inline=False)
                    else:
                        embed.add_field(name="Job",value="> this user has no job", inline=False)
                    listofitems = datakek[str(ctx.author.id)]["inventory"]
                    if bool(listofitems):
                        with open(self.items, "r+") as k:
                                itemkek = json.load(k)
                        betterstring=""
                        for item in listofitems:
                            itemname = itemkek[item]["name"]
                            emojiname = itemkek[item]["emoji"]
                            betterstring+= f"> {itemname} :: {emojiname}\n"
                        embed.add_field(name="Inventory", value=betterstring,inline=False)
                    else:
                        embed.add_field(name="Inventory", value="> No items in inventory")    
                    
                    await ctx.send(embed=embed)
                    
                else:
                    await self.add_or_find_account(ctx.author.id)
                    embed = discord.Embed(title="welcome to stealthy economy user", description="do the command again to look at your new profile")
                    await ctx.send(embed=embed)
            else:
                if str(member.id) in datakek:
                    embed = discord.Embed(title=member.name)
                    embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
                    embed.set_thumbnail(url= member.avatar_url)
                    bal = datakek[str(member.id)]["balance"]
                    bank = datakek[str(member.id)]["bank"]
                    embed.add_field(name="Balance and bank",value=f"> <:stealthycoin:897331306013286440>  {bal} || <:stealthycoin:897331306013286440>  {bank}", inline=False)
                    with open(self.jobs, "r+") as jobjson:
                        jobkek = json.load(jobjson)
                    jobid = datakek[str(member.id)]["job_id"]
                    if jobid != "0":
                        jobname = jobkek[jobid]["name"]
                        embed.add_field(name="job", value=f"> {jobname}", inline=False)
                        
                    else:
                        embed.add_field(name="Job",value="> this user has no job", inline=False)
                    listofitems = datakek[str(member.id)]["inventory"]
                    if bool(listofitems):
                        with open(self.items, "r+") as k:
                                itemkek = json.load(k)
                        betterstring=""
                        for item in listofitems:
                            itemname = itemkek[item]["name"]
                            emojiname = itemkek[item]["emoji"]
                            betterstring+= f"> {itemname} :: {emojiname}\n"
                        embed.add_field(name="Inventory", value=betterstring,inline=False)
                    else:
                        embed.add_field(name="Inventory", value="> No items in inventory")
                    await ctx.send(embed=embed)
                else:
                    embed= discord.Embed(name="account not found!",description="the peron who you mentioned dont have an account!")
                    await ctx.send(embed=embed)
            
    @commands.command()
    async def iteminfo(self, ctx, *,item = None):
        print(item)
        with open(self.items, "r+") as f:
            datakek = json.load(f)
        if not item:
            embed = discord.Embed(title="Itemlist",timestamp=ctx.message.created_at)
            embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
            betterstring = "**Items currently in the bot**:\n"
            for k in datakek:
                itemname = datakek[k]["name"]
                betterstring += f"> {itemname}\n"
            embed.add_field(name="⠀",value=betterstring)    
            await ctx.send(embed=embed)
        else:
            for k in datakek:
                if item == datakek[k]["name"]:
                    embed = discord.Embed(title="Item info",timestamp=ctx.message.created_at)
                    embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
                    embed.set_footer(text=f"command issued by: {ctx.author.name}",icon_url=ctx.author.avatar_url)
                    embed.add_field(name=datakek[k]["name"],value=datakek[k]["item_desc"], inline=True)
                    value = datakek[k]["value"]
                    embed.add_field(name="value:", value=f"<:stealthycoin:897331306013286440> {value}")
                    image = datakek[k]["thumbnail"]
                    embed.set_thumbnail(url=image)
                    itemtype = datakek[k]["item_type"]
                    match itemtype:
                        case 1:
                            embed.add_field(name="type:", value="> amour <:armour:897329092444192768>",inline=False)
                            stats = [datakek[k]["stats"]["defence"], datakek[k]["stats"]["s_res"], datakek[k]["stats"]["b_res"], datakek[k]["stats"]["health_inc"]]
                            stats = f"> defence = {stats[0]},\n > sharp resistance ={stats[1]},\n > blunt resistance = {stats[2]},\n > health increase = {stats[3]} "
                            embed.add_field(name="stats", value=stats,inline=False)
                        case 2:
                            embed.add_field(name="type:", value="> weapon <:attack:897321966640439296>",inline=False)
                            stats = [datakek[k]["stats"]["attack"],datakek[k]["stats"]["s_dam"],datakek[k]["stats"]["b_dam"]]
                            stats = f"> defence = {stats[0]},\n > sharp damage ={stats[1]},\n > blunt damage = {stats[2]}"
                            embed.add_field(name="stats", value=stats)
                    await ctx.send(embed=embed)
                    break
    @cooldown(1, 200, commands.BucketType.user)
    @commands.command()
    async def work(self, ctx):
        with open (self.profiles, "r+") as f:
            profilekek = json.load(f)
        with open (self.jobs, "r+") as k:
            jobkek = json.load(k)
        if str(ctx.author.id) in profilekek and profilekek[str(ctx.author.id)]["job_id"] != "0":
            jobid = profilekek[str(ctx.author.id)]["job_id"]
            jobmaxpay = jobkek[jobid]["Base_pay"]
            jobminpay = jobkek[jobid]["min_pay"]
            currentbal = profilekek[str(ctx.author.id)]["balance"]
            await self.addorremovemoney(ctx.author.id, currentbal + jobmaxpay )
            
            await ctx.send(f"added <:stealthycoin:897331306013286440> {jobmaxpay} to your balance!")
        elif str(ctx.author.id) not in profilekek:
            await self.add_or_find_account(ctx.author.id)
            embed = discord.Embed(title="welcome to stealthy economy user", description="do the command again")
            await ctx.send(embed=embed)
    @commands.command()
    async def job(self, ctx,*, job =""):
        with open (self.jobs, "r+") as f:
            jobkek = json.load(f)
        
        if job == "":
            with open (self.profiles, "r+") as k:
                profilekek = json.load(k)
            userlvl= profilekek[str(ctx.author.id)]["level"]
            #they want the list of jobs
            betterstring = ""
            for job_id in jobkek:
                bettername = jobkek[job_id]["name"]
                basepay = jobkek[job_id]["Base_pay"]
                levelreq = jobkek[job_id]["level_req"]
                canwork = await self.citnara(userlvl, levelreq)
                if canwork == True:
                    betterstring +=f"> {bettername} | :green_circle: level req: {levelreq} | Pay: <:stealthycoin:897331306013286440> {basepay}" 
                else:
                    betterstring +=f"> {bettername} | :red_circle: level req: {levelreq} | Pay: <:stealthycoin:897331306013286440> {basepay}" 

            embed = discord.Embed()
            embed.add_field(name="Jobs:", value=betterstring)
            embed.set_footer(text=":red_circle: means level req is high and :green_circle: means you can get this job")
            await ctx.send(embed= embed)
        else:
            #they want to work asa a certain job
            with open(self.profiles, "r+") as b:
                datakek = json.load(b)
                userlvl= datakek[str(ctx.author.id)]["level"]
                for jobid in jobkek:
                    # i could prolly just make all the jobid and put them in string but i am not bothered so go fuck yourself
                    if jobkek[jobid]["name"] == job:
                        levelreqe = jobkek[jobid]["level_req"]
                        canworkjob = await self.citnara(userlvl, levelreqe)
                        if canworkjob == True:
                            datakek[str(ctx.author.id)]["job_id"] = str(jobid)
                            embed = discord.Embed(title="You are hired!", description="you need to work every 1 hour unless you get fired")
                            Json(b,datakek)

                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(title="the level requirement is too high for you D:")
                            await ctx.send(embed=embed)
    @commands.command()
    async def gamble(self, ctx, amount:int):
        if amount <= 20:
            await ctx.send("you need atleast 21 coins to gamble why? idk just have it")
        else:
            with open(self.profiles, "r+") as b:
                datakek = json.load(b)
                
                
                if str(ctx.author.id) in datakek:
                    
                    
                    if amount <= datakek[str(ctx.author.id)]['balance']:
                        x = random.randint(1, 3)
                        if x == 1:
                            embed = discord.Embed(description=f" you have a gambling addiction now because you won **{amount * 2 }** ")
                            embed.set_author(icon_url=ctx.author.avatar_url, name="You won!")
                            datakek[str(ctx.author.id)]['balance'] += amount * 2
                            Json(b, datakek) 
                        else:
                            embed = discord.Embed(description=f" you need to win back the money now now because you lost **{amount}** ")
                            embed.set_author(icon_url=ctx.author.avatar_url, name="You Lost nub git gud!")
                            datakek[str(ctx.author.id)]['balance'] -= amount
                            Json(b, datakek)
                    else:
                        embed = discord.Embed(description=" uho not enough money for gambling get more money do s?profile to see your money")
                    
                    await ctx.send(embed=embed)          
                else:
                    await self.add_or_find_account(ctx.author.id)
                    embed = discord.Embed(title="welcome to stealthy economy user", description="do the command again")
                    await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))
