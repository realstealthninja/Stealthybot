import discord
import aiosqlite
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont
from discord.ext import tasks,commands


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connecttodb())
        self.periodicsacrifice.start()
        
    async def connecttodb(self):
        self.db = await aiosqlite.connect("./database/activity.db")
        
    @tasks.loop(seconds=400.0)
    async def periodicsacrifice(self):
        cursor = await self.db.cursor()
        await cursor.execute("UPDATE activity SET activitypoints = 0")
        await cursor.execute("UPDATE activity SET cando = 1")
        await self.db.commit()
    
    @periodicsacrifice.before_loop
    async def beforesacrifice(self):
        await self.bot.wait_until_ready()
        if self.db != None:
            return
        else:
            asyncio.sleep(1)
            

    async def timeoutuser(self,userid,guildid):
        await asyncio.sleep(120)
        cursor = await self.db.cursor()
        await cursor.execute("update activity set cando=? where userid=? and guildid=?",( 1, userid, guildid))
        await self.db.commit()

    async def findorinsert(self, member: discord.member):
        cursor = await self.db.cursor()
        await cursor.execute("Select * from activity where userid = ? and guildid =?", (member.id, member.guild.id))
        result = await cursor.fetchone()
        if result is None:
            result = (member.id, 0, member.guild.id, 100, 1, 0)
            await cursor.execute("insert into activity values(?,?,?,?,?,?)", result)
            await self.db.commit()
        return result    

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.bot is True or message.guild is None:
            return
        
        
        result = await self.findorinsert(message.author)
        userid, activitypoints, guildid, maximum, cando, total = result
        cursor = await self.db.cursor()
        if cando == 1 and activitypoints != 100:
            total += 1
            activitypoints += 1
            cando = 0
            await cursor.execute("update activity set activitypoints=?, cando=?, total = ?  where userid=? and guildid=?",(activitypoints, cando, total, userid,guildid))
            await self.db.commit()
            await self.timeoutuser(userid,guildid)
            
    
    @commands.command()
    async def leaderboard(self, ctx):
        emeby = discord.Embed()
        emeby.set_author(name="the most active people of the day", icon_url= ctx.author.avatar_url)
        cursor = await self.db.cursor()
        await cursor.execute("Select userid, activitypoints from activity where guildid = ? ORDER BY activitypoints ASC",(ctx.guild.id,))
        result = await cursor.fetchall()
        desc = ""
        for k, people in enumerate(result[::-1], start = 1):
          desc += f"\n**{k}.** {self.bot.get_user(people[0]).display_name}:  activity points:- **{people[1]}**"
          #now we put this because we know that user exists
          if k == 10:
              break
        emeby.description = desc
        await ctx.send(embed = emeby)    
    
    @commands.command()
    async def activity(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        cursor = await self.db.cursor()
        await cursor.execute("select * from activity where guildid =? and userid=?",(member.guild.id,member.id))
        result = await cursor.fetchone()
        bytese = await self.make_rank_image(member, result[1], result[5])
        file = discord.File(bytese, 'rank.png')
        await ctx.send(file=file)
        
        
    #hippty hoppity your code is now my property @caeden
    async def make_rank_image(self, member: discord.Member, activitypoints, total):
        user_avatar_image = str(member.avatar_url_as(format='png', size=512))
        async with aiohttp.ClientSession() as session:
            async with session.get(user_avatar_image) as resp:
                avatar_bytes = io.BytesIO(await resp.read())

        img = Image.new('RGB', (1366, 768))
        background = Image.open("assets/backgrounds/neon-sunset-4k-eh-1366x768.jpg")
        logo = Image.open(avatar_bytes).resize((300, 300))
        img.paste(background)
        
        
        
        # Stack overflow helps :)
        bigsize = (logo.size[0] * 3, logo.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(logo.size, Image.ANTIALIAS)
        logo.putalpha(mask)
        ##############################
        img.paste(logo, (20, 20), mask=logo)


        
        # Black Circle
        draw = ImageDraw.Draw(img, 'RGB')
        draw.ellipse((200, 200, 300, 300), fill='#000')

        # Placing offline or Online Status
        # Discord Colors (Online: '#43B581')
        draw.ellipse((200, 200, 300, 300), fill='#43B581')
        ##################################

        # Working with fonts
        font = 'assets/fonts/Exo-Regular.otf'
        big_font = ImageFont.FreeTypeFont(font, 60)
        medium_font = ImageFont.FreeTypeFont(font, 40)
        small_font = ImageFont.FreeTypeFont(font, 30)
        
        
        draw.text((605, 350), f"{activitypoints} /100", font=big_font, fill="#11ebf2")
        draw.text((610, 300), "Activity Points:", font=medium_font, fill="#11ebf2")
        
        draw.text((235, 350), f"{total}", font=big_font, fill="#11ebf2")
        draw.text((210, 300), "Total Activity Points:", font=medium_font, fill="#11ebf2")
        
        
        
        # Placing User Name
        text = member.display_name
        text_size = draw.textsize(text, font=medium_font)
        text_offset_x = text_size[0] + 100
        text_offset_y = text_size[1] - 10
        draw.text((text_offset_x, text_offset_y), text, font=medium_font, fill="#fff")

        # Placing Discriminator
        text = f'#{member.discriminator}'
        text_offset_x += text_size[0] + 10
        text_size = draw.textsize(text, font=small_font)
        text_offset_y = text_size[1] - 5
        draw.text((text_offset_x, text_offset_y), text, font=small_font, fill="#727175")

        
        # Drawing total
        
        
        bytese = io.BytesIO()
        img.save(bytese, 'PNG')
        bytese.seek(0)
        return bytese

def setup(bot):
    bot.add_cog(Activity(bot))
