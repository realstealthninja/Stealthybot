import json
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown



def Json(file1, data1):
    file1.truncate(0)
    file1.seek(0)
    file1.write(json.dumps(data1, indent=4))
    
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profiles = "Jsons/economy/profiles.json"
        self.jobs = "Jsons/economy/jobs.json"
        self.items = "Jsons/economy/items.json" 
    
    async def citnara(self, num1, num2):
        """this returns if num 1 is greater than or equals to num2

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
    async def start(self, ctx):
        
        acc = await self.add_or_find_account(ctx.author.id)
        if acc == True:
            embed=discord.Embed(title="Account made!", description="`you have been registered to stealthy economy, have fun!`",timestamp = ctx.message.created_at)
            embed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
            embed.add_field(name="Balance", value="> 100", inline=False)
            embed.set_footer(text=f" issued by {ctx.author.name}")
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(timestamp = ctx.message.created_at)
            embed.add_field(name="You already have a acccount!", value="bal: in progress", inline=False)
            await ctx.send(embed=embed)       

    
    @commands.command()
    async def profile(self, ctx, member:discord.Member=""):
        with open (self.profiles, "r+") as f:
            datakek = json.load(f)
            if member=="":

                if str(ctx.author.id) in datakek:
                    embed = discord.Embed(title=ctx.author.name)
                    embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
                    embed.set_thumbnail(url= ctx.author.avatar_url)
                    bal = datakek[str(ctx.author.id)]["balance"]
                    bank = datakek[str(ctx.author.id)]["bank"]
                    embed.add_field(name="Balance and bank",value=f"> :stealthycoin:897331306013286440> {bal} || <:stealthycoin:897331306013286440> {bank}", inline=False)
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
                    embed= discord.Embed(name="account not found!",description="you dont have an account!")
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
                    listofitems = datakek[str(ctx.author.id)]["inventory"]
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
        if item ==None:
            embed = discord.Embed(title="Itemlist",timestamp=ctx.message.created_at)
            embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
            betterstring = "**Items currently in the bot**:\n"
            for k in datakek:
                itemname = datakek[k]["name"]
                betterstring += f"> {itemname}\n"
            embed.add_field(name="⠀",value=betterstring)
            await ctx.send(embed=embed)
        else:
            
            #https://ibb.co/9c6r496
            for k in datakek:
                if item == datakek[k]["name"]:
                    embed = discord.Embed(title="Item info",timestamp=ctx.message.created_at)
                    embed.set_author(name="frustra etiam in morte!", icon_url="https://cdn.discordapp.com/avatars/889922820317007928/9182f4cfa68a27628dc9927fd1459b93.webp?size=300")
                    embed.set_footer(text=f"command issued by: {ctx.author.name}",icon_url=ctx.author.avatar_url)
                    embed.add_field(name=datakek[k]["name"],value=datakek[k]["item_desc"], inline=True)
                    value=datakek[k]["value"]
                    embed.add_field(name="value:", value=f"<:stealthycoin:897331306013286440> {value}")
                    image = datakek[k]["thumbnail"]
                    embed.set_thumbnail(url=image)
                    if datakek[k]["item_type"] == 1:
                        embed.add_field(name="type:", value="> amour <:armour:897329092444192768>",inline=False)
                        defence = datakek[k]["stats"]["defence"]
                        sharpres = datakek[k]["stats"]["s_res"]
                        bluntres = datakek[k]["stats"]["b_res"]
                        health_increasse = datakek[k]["stats"]["health_inc"]
                        stats = f"> defence = {defence},\n > sharp resistance ={sharpres},\n > blunt resistance = {bluntres},\n > health increase = {health_increasse} "
                        embed.add_field(name="stats", value=stats,inline=False)
                    if datakek[k]["item_type"] == 2:
                        embed.add_field(name="type:", value="> weapon <:attack:897321966640439296>",inline=False)
                        attack = datakek[k]["stats"]["attack"]
                        sharpdam = datakek[k]["stats"]["s_dam"]
                        bluntdam = datakek[k]["stats"]["b_dam"]
                        stats = f"> defence = {attack},\n > sharp damage ={sharpdam},\n > blunt damage = {bluntdam}"
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
        else:
            await ctx.send("You dont have a job or you didnt make an account!")
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
                            embed = discord.Embed(title="You are hired!")
                            Json(b,datakek)

                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(title="the level requirement is too high for you D:")
                            await ctx.send(embed=embed)
 

def setup(bot):
    bot.add_cog(Economy(bot))
