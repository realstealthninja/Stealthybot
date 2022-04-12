import io
import aiohttp
import disnake
import asyncio
import aiosqlite

from disnake.ext import tasks, commands
from PIL import Image, ImageDraw, ImageFont


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.conf = None
        self.bot.loop.create_task(self.connect_db())
        # self.periodic_sacrifice.start()

    async def connect_db(self):
        self.db = await aiosqlite.connect("./database/activity.db")
        self.conf = await aiosqlite.connect("./database/config.db")

    @tasks.loop(seconds=86400.0)
    async def periodic_sacrifice(self):
        cursor = await self.db.cursor()
        await cursor.execute("UPDATE activity SET activitypoints = 0")
        await cursor.execute("UPDATE activity SET cando = 1")
        await self.db.commit()
        await cursor.execute("SELECT * FROM activity")
        async for row in cursor:
            try:
                member = await self.bot.get_guild(row[2]).getch_member(row[0])
                await self.removeactrole(member, row[2])
            except AttributeError:
                pass
        cur = await self.conf.cursor()
        await cur.execute("SELECT * FROM servers")
        embed = disnake.Embed(
            title="🎉 Activty point reset 🎉",
            description="""
            Your activty points have been `reset` it has been `24 hours`
            Congrats to the people who have reached the goal of `100 points` 🥳\n            
            Thank you for being active!
             - Server Owner
            """,
        )
        async for row in cur:
            if row[4]:
                await self.bot.get_guild(row[0]).get_channel(row[4]).send(embed=embed)
            else:
                for channel in self.bot.get_guild(row[0]).channels:
                    try:
                        await channel.send(embed=embed)
                        break
                    except AttributeError:
                        continue

    @periodic_sacrifice.before_loop
    async def beforesacrifice(self):
        await self.bot.wait_until_ready()
        if self.db != None and await self.db.cursor() != None:
            return
        else:
            await asyncio.sleep(1)

    async def timeoutuser(self, user_id, guild_id):
        await asyncio.sleep(120)
        cursor = await self.db.cursor()
        await cursor.execute(
            "UPDATE activity SET cando=? WHERE user_id=? AND guild_id=?",
            (1, user_id, guild_id),
        )
        await self.db.commit()

    async def findorinsert(self, member: disnake.member):
        cursor = await self.db.cursor()
        await cursor.execute(
            "SELECT * FROM activity WHERE user_id = ? AND guild_id =?",
            (member.id, member.guild.id),
        )
        result = await cursor.fetchone()
        if result is None:
            result = (member.id, 0, member.guild.id, 100, 1, 0)
            await cursor.execute("INSERT INTO activity values(?,?,?,?,?,?)", result)
            await self.db.commit()
        return result

    # TODO: make the goal settable by the user

    @commands.command(
        description="""
        **setup activity for your server. Make sure that the bot can see and type in the channel**
        > `message`: message that it sends when the user reaches the Goal(100)
        > `channel` (optional): channel that it sends to.
        > `role` (optional): the role that the bot assigns to the user. if no role is provided none will be given.
        **message: __docs__**
        > `USERMENTION` adds a mention of the user who got to the goal 
        > ..more coming soon..
        ***IMPORTANT***
        > Make sure that the `role` you are trying to give is below the `bot's role.`
        > Make sure that the `channel` you are trying to send the message to is `accessable` by the bot.
        `suggest more features and improvements on the offical server`
        """
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def setupact(
        self,
        ctx: commands.Context,
        channel: disnake.TextChannel = None,
        role: disnake.Role = None,
        *,
        message,
    ):
        cur = await self.conf.cursor()
        await cur.execute("select * from servers WHERE id = ?", (ctx.guild.id,))
        result = await cur.fetchone()

        try:
            channel_id = channel.id
        except AttributeError:
            channel_id = 0

        if not role:
            roleid = 0
        else:
            roleid = role.id

        if not result:
            result = (ctx.guild.id, "s?", roleid, message, channel_id)
            await cur.execute("INSERT INTO servers values(?,?,?,?,?)", result)
            await self.conf.commit()
        else:
            await cur.execute(
                "UPDATE SET roleid = ?, message = ? WHERE id = ?",
                (roleid, message, ctx.guild.id),
            )
            await self.conf.commit()

    async def actdone(self, guild_id, message) -> None:
        cur = await self.conf.cursor()
        await cur.execute(
            "SELECT message, roleid, channel_id FROM servers WHERE id = ?", (guild_id,)
        )
        result = await cur.fetchone()
        mes = f"{message.author.mention} reached 100 points! thank you for being active!"
        if result:
            mes = result[0]
            try:
                role = message.guild.get_role(result[1])
                await message.author.add_roles(role, reason="reached 100 points")
            except AttributeError:
                pass

            try:
                return await message.guild.get_channel(result[2]).send(
                    mes.replace("USERMENTION", f"{message.author.mention}")
                )
            except AttributeError:
                pass
            except disnake.errors.Forbidden:
                await message.send(
                    "Hey i cannot send the message to the channel specified"
                )
        await message.channel.send(mes)

    async def removeactrole(self, member: disnake.Member, guild_id: int):
        cur = await self.conf.cursor()
        await cur.execute("SELECT message, roleid FROM servers WHERE id = ?", (guild_id,))
        result = await cur.fetchone()

        if result and member.get_role(result[1]):
            try:
                role = self.bot.get_guild(guild_id).get_role(result[1])
                await member.remove_roles(role, reason="activity reset")
            except AttributeError:
                pass

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot is True or message.guild is None:
            return
        result = await self.findorinsert(message.author)
        user_id, activitypoints, guild_id, maximum, cando, total = result
        cursor = await self.db.cursor()

        if cando == 1 and activitypoints != 100:

            total += 1
            activitypoints += 1
            cando = 0
            if activitypoints == 100:
                await self.actdone(message.guild.id, message)

            await cursor.execute(
                "UPDATE activity SET activitypoints=?, cando=?, total = ?  WHERE user_id=? and guild_id=?",
                (activitypoints, cando, total, user_id, guild_id),
            )
            await self.db.commit()
            await self.timeoutuser(user_id, guild_id)

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        emeby = disnake.Embed()
        emeby.set_author(
            name="the most active people of the day", icon_url=ctx.author.avatar
        )
        cursor = await self.db.cursor()
        await cursor.execute(
            "SELECT user_id, activitypoints FROM activity WHERE guild_id = ? ORDER BY activitypoints ASC",
            (ctx.guild.id,),
        )
        result = await cursor.fetchall()
        desc = ""
        for k, people in enumerate(result[::-1], start=1):
            if self.bot.get_user(people[0]) == None:
                await cursor.execute(
                    "DELETE FROM activity WHERE user_id=? AND guild_id=?",
                    (people[0], ctx.guild.id),
                )
                await self.db.commit()
                continue
            desc += f"\n**{k}.** {self.bot.get_user(people[0]).display_name} | **{people[1]}**"
            if k == 10:
                break
        emeby.description = desc
        await ctx.send(embed=emeby)

    @commands.command()
    async def activity(self, ctx: commands.Context, member: disnake.Member = None):
        if member is not None and member.bot:
            return await ctx.send("hey a bot's activity is not counted!")
        if member is None:
            member = ctx.author
        cursor = await self.db.cursor()
        await cursor.execute(
            "SELECT * FROM activity WHERE guild_id = ? AND user_id = ?",
            (member.guild.id, member.id),
        )
        result = await cursor.fetchone()
        bytese = await self.make_rank_image(member, result[1], result[5])
        file = disnake.File(bytese, "rank.png")
        await ctx.send(file=file)

    async def make_rank_image(self, member: disnake.Member, activitypoints, total):
        user_avatar_image = str(member.avatar.with_size(512))
        async with aiohttp.ClientSession() as session:
            async with session.get(user_avatar_image) as resp:
                avatar_bytes = io.BytesIO(await resp.read())

        img = Image.new("RGB", (800, 240))
        logo = Image.open(avatar_bytes).resize((200, 200))
        background = Image.open("assets/backgrounds/death.png")
        img.paste(background)
        img.paste(logo, (20, 20))

        draw = ImageDraw.Draw(img, "RGB")

        # preloading fonts
        font = "assets/fonts/Exo-Regular.otf"
        medium_font = ImageFont.FreeTypeFont(font, 40)
        small_font = ImageFont.FreeTypeFont(font, 30)

        # drawing text
        draw.text(
            (250, 50),
            f"{member.name}#{member.discriminator}",
            font=medium_font,
            fill="#fff",
        )
        draw.text(
            (250, 100),
            f"Act: {activitypoints} /100   Total: {total}",
            font=small_font,
            fill="#fff",
        )

        # drawing rectangle
        draw.rectangle([248, 148, 652, 182], outline="white")
        draw.rectangle([250, 150, 250 + (400 * activitypoints / 100), 180], fill="white")

        # Drawing total
        bytese = io.BytesIO()
        img.save(bytese, "PNG")
        bytese.seek(0)
        return bytese


def setup(bot):
    bot.add_cog(Activity(bot))
