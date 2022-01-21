import disnake
import aiosqlite
import asyncio
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont
from disnake.ext import tasks,commands


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.connecttodb())
        self.periodicsacrifice.start()
        
    async def connecttodb(self):
        self.db = await aiosqlite.connect("./database/activity.db")
      
    @tasks.loop(seconds=86400.0)
    async def periodicsacrifice(self):
        cursor = await self.db.cursor()
        await cursor.execute("UPDATE activity SET activitypoints = 0")
        await cursor.execute("UPDATE activity SET cando = 1")
        await self.db.commit()
    
    @periodicsacrifice.before_loop
    async def beforesacrifice(self):
        await self.bot.wait_until_ready()
        if self.db != None and await self.db.cursor() != None:
            return
        else:
            await asyncio.sleep(1)
            
    async def timeoutuser(self,userid,guildid):
        await asyncio.sleep(120)
        cursor = await self.db.cursor()
        await cursor.execute("update activity set cando=? where userid=? and guildid=?",( 1, userid, guildid))
        await self.db.commit()

    async def findorinsert(self, member: disnake.member):
        cursor = await self.db.cursor()
        await cursor.execute("Select * from activity where userid = ? and guildid =?", (member.id, member.guild.id))
        result = await cursor.fetchone()
        if result is None:
            result = (member.id, 0, member.guild.id, 100, 1, 0)
            await cursor.execute("insert into activity values(?,?,?,?,?,?)", result)
            await self.db.commit()
        return result    

    @commands.Cog.listener()
    async def on_message(self, message:disnake.Message):
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
        emeby = disnake.Embed()
        emeby.set_author(name="the most active people of the day", icon_url= ctx.author.avatar)
        cursor = await self.db.cursor()
        await cursor.execute("Select userid, activitypoints from activity where guildid = ? ORDER BY activitypoints ASC",(ctx.guild.id,))
        result = await cursor.fetchall()
        desc = ""
        for k, people in enumerate(result[::-1], start = 1):
            if self.bot.get_user(people[0]) == None:
               await cursor.execute("delete from activity where userid=? and guildid=?",(people[0], ctx.guild.id))
               await self.db.commit()
               continue
            desc += f"\n**{k}.** {self.bot.get_user(people[0]).display_name} | **{people[1]}**"
            if k == 10:
              break
        emeby.description = desc
        await ctx.send(embed = emeby)    
    
    @commands.command()
    async def activity(self, ctx, member:disnake.Member = None):
        if member is None:
            member = ctx.author
        cursor = await self.db.cursor()
        await cursor.execute("select * from activity where guildid =? and userid=?",(member.guild.id,member.id))
        result = await cursor.fetchone()
        bytese = await self.make_rank_image(member, result[1], result[5])
        file = disnake.File(bytese, 'rank.png')
        await ctx.send(file=file)
        
        

    async def make_rank_image(self, member: disnake.Member, activitypoints, total):
        user_avatar_image = str(member.avatar.with_size(512))
        async with aiohttp.ClientSession() as session:
            async with session.get(user_avatar_image) as resp:
                avatar_bytes = io.BytesIO(await resp.read())

        img = Image.new('RGB', (800, 240))
        logo = Image.open(avatar_bytes).resize((200, 200))
        background = Image.open("assets/backgrounds/death.png")
        img.paste(background)
        img.paste(logo, (20, 20))
        
        draw = ImageDraw.Draw(img, 'RGB')


        # preloading fonts
        font = 'assets/fonts/Exo-Regular.otf'
        medium_font = ImageFont.FreeTypeFont(font, 40)
        small_font = ImageFont.FreeTypeFont(font, 30)
    
        # drawing text    
        draw.text((250, 50), f"{member.name}#{member.discriminator}", font=medium_font, fill="#fff")
        draw.text((250, 100), f"Act: {activitypoints} /100   Total: {total}", font=small_font, fill="#fff")
        
        #drawing rectangle
        draw.rectangle([248,148,652,182], outline="white")
        draw.rectangle([250,150, 250 + ( 400 * activitypoints / 100 ),180], fill="white")
        
        # Drawing total
        bytese = io.BytesIO()
        img.save(bytese, 'PNG')
        bytese.seek(0)
        return bytese

def setup(bot):
    bot.add_cog(Activity(bot))
