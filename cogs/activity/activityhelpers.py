"""
Helper for activity cog of stealthy bot

"""
import datetime
import io
from sqlite3 import Row
import aiohttp

import aiosqlite
import disnake
from PIL import Image, ImageDraw, ImageFont

class ActivityHelper():
    """
    Activity Helper class has functions that help with the activity feature.
    It is seperated from the main cog file for readability better organiaztion.
    """

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.act_database

    async def fetch_server(self, serverid: int) -> tuple | Row:
        """
        creates or returns a server from the activity table.
        This is for better developer experiance
        """
        cur: aiosqlite.Cursor = await self.bot.act_database.cursor()
        await cur.execute(
            "SELECT * FROM activity WHERE ServerID = ?",
            (serverid,)
        )
        result = await cur.fetchone()
        return result

    async def fetch_users(self, serverid: int) -> tuple | Row:
        """
        Fetches the users in the User table.
        """
        cur: aiosqlite.Cursor = await self.bot.act_database.cursor()
        await cur.execute(
            "SELECT * FROM Users WHERE ServerID = ?",
            (serverid,)
        )
        result = await cur.fetchall()
        return result

    async def create_or_fetch_user(self, userid: int, serverid: int):
        """
        Creates or fetches a user from the database

        parameters
        ==========
        userid (int): The user's id
        serverid (int): The server's Id
        """
        result = await self.select_one(
            "Users",
            filter_columns=[
                "ServerID",
                "UserID"
            ],
            filter_values=(
                serverid,
                userid
            )
        )

        if not result:
            result = (serverid, userid, 0, 0, 0, 0)
            await self.insert_into("Users", result)
        return result

    async def create_act_image(self, member: disnake.Member):
        """
        Creates the Image
        """
        image = await self.select_one(
            "activity",
            "BgImage",
            ["ServerID", ],
            (member.guild.id,)
        )
        user = await self.select_one(
            "Users",
            filter_columns=["UserID", "ServerID"],
            filter_values=[member.id, member.guild.id]
        )


        msgGoal = await self.select_one(
            "activity",
            "MsgGoal",
            ["ServerID", ],
            (member.guild.id,)
        )
        msgGoal = msgGoal[0]
        image = image[0]

        logo = str(member.display_avatar.with_format("png").with_size(512))
        async with aiohttp.ClientSession() as session:
            async with session.get(logo) as resp:
                logo = io.BytesIO(await resp.read())
            async with session.get(image) as resp:
                image = io.BytesIO(await resp.read())

        image = Image.open(image)
        image.crop((0, 0, 240, 800))
        logo = Image.open(logo).resize((150, 150))

        logo_mask_size = (logo.size[0] * 3, logo.size[1] * 3)
        logo_mask = Image.new("L", logo_mask_size)
        circle_mask = ImageDraw.Draw(logo_mask)
        circle_mask.ellipse((0, 0) + logo_mask_size, fill=255)
        circle_mask = logo_mask.resize(logo.size, Image.ANTIALIAS)
        logo.putalpha(circle_mask)

        image.paste(logo, (20, 20), mask=logo)
        font = ImageFont.truetype("assets/fonts/Exo-Regular.otf", 48)
        smallFont = ImageFont.truetype(
            "assets/fonts/Exo-Regular.otf", 32)
        ImageDraw.Draw(image).text(
            xy=(logo.size[0] + 5, logo.size[1] - 90),
            text=f"{member.name}#{member.discriminator}",
            font=font
        )
        ImageDraw.Draw(image).rounded_rectangle(
            xy=((45, 180), (400, 300)),
            radius=7,
            width=3
        )
        ImageDraw.Draw(image).rectangle(
            xy=((50, 185),(395, 295)),
            fill="black"
        )
        ImageDraw.Draw(image).text(
            xy=(50, 200),
            text=f"ACT Points: {user[2]}",
            font=smallFont,
            fill="white"
        )
        ImageDraw.Draw(image).text(
            xy=(50, 240),
            text=f"Total msg: {user[4]}",
            font=smallFont,
            fill="white"
        )

        ImageDraw.Draw(image).rounded_rectangle(
            xy=((50, 300),(500, 350)),
            radius=7,
            width=3
        )
        #495 = 100%
        percent = round((user[3]/msgGoal) * 100)
        if percent >= 100: percent = 100
        percent = (percent*495)/100


        
        ImageDraw.Draw(image).rectangle(
            xy=((55, 305),( percent, 345)),
            fill="white"
        )
        
        ImageDraw.Draw(image).text(
            xy=(130, 310),
            text=f"Messages: {user[3]}/{msgGoal}",
            fill="black",
            font=smallFont
        )

        file = io.BytesIO()
        image.save(file, "PNG")
        file.seek(0)
        return file

    async def set_time(self, serverid: int):
        """
        Sets the unix epoch
        """
        timeframe = await self.fetch_server(serverid)
        timeframe = timeframe[2]
        next_reset = datetime.datetime.utcnow() + datetime.timedelta(hours=timeframe)
        next_reset_epoch = datetime.datetime.timestamp(next_reset)

        previous_reset = await self.select_one(
            "Time",
            filter_columns=["ServerID", ],
            filter_values=(serverid,)
        )

        if previous_reset:
            await self.update_set(
                "Time",
                column=["Time", ],
                values=(next_reset_epoch,),
                filter_columns=["ServerID", ],
                filter_values=(serverid,)
            )
        else:
            await self.insert_into(
                "Time",
                values=(serverid, next_reset_epoch)
            )

    async def fetch_message(self, serverid: int) -> str:
        """
        Fetches the message for activity completion
        """
        message = await self.select_one(
            "Messages",
            column="Message",
            filter_columns=["ServerID"],
            filter_values=(serverid,)
        )
        return message

    async def fetch_embed(self, serverid: int) -> disnake.Embed | None:
        """ Returns an Embed if it exists from the database"""
        embed_raw = await self.select_one(
            "Embeds",
            filter_columns=["ServerID", ],
            filter_values=(serverid,)
        )

        if not embed_raw:
            return None

        embed = disnake.Embed(
            title=embed_raw[1],
            description=embed_raw[2]
        )
        if embed_raw[3] != "NONE":
            embed.set_image(url=embed_raw[3])
        if embed_raw[4] != "NONE":
            embed.set_thumbnail(url=embed_raw[4])

        return embed

    async def insert_into(self, table: str, values: tuple):
        """
        Inserts values into the specifed table.
        For easier access to the tables.
        ( This looks suspiciously like orm behaviour dont tell anyone 🤫)

        Args:
        table (str): The table in which the values must be inserted into
        values (tuple): The values that must be inserted
        """

        cur: aiosqlite.Cursor = await self.bot.act_database.cursor()
        await cur.execute(f"INSERT INTO {table} VALUES{values}")
        await self.bot.act_database.commit()

    async def select_one(
        self,
        table: str,
        column: str = None,
        filter_columns: list | None = None,
        filter_values: tuple | None = None
    ):
        """
        Select a single row from the specifed arguments

        Parameters
        ==========
        table (str): The table that the selection must happen in
        column (str, optional): The column that you need to be selected. Defaults to None.
        filter_column (str | None, optional): The column in which you specify
        the value that disqualifies a row . Defaults to None.
        filter_value (any, optional): The value that you need to filtered. Defaults to None.
        """
        where_statement = "WHERE"

        if not column:
            column = "*"

        if filter_columns:
            for count, item in enumerate(filter_columns):
                if count == len(filter_columns)-1:
                    where_statement += f" {item} = ?"
                    break

                where_statement += f" {item} = ? AND"
        else:
            where_statement = ""

        cur: aiosqlite.Cursor = await self.bot.act_database.cursor()
        await cur.execute(f"SELECT {column} FROM {table} {where_statement}", filter_values)
        result = await cur.fetchone()
        return result

    async def update_set(
        self,
        table: str,
        column: list,
        values: tuple,
        filter_columns: list = None,
        filter_values: tuple = None
    ):
        """
        Updates a column(s) in a table with the specifed value(s).

        Parameters
        ==========
        table(str) : The table in which the update takes place.
        column(list): The column(s) which should be updated.
        values(tuple): The values that should be inserted.
        filter_columns(list)(Optional): The columns that should be used for filtering.
        filter_values(tuple)(Optional): The values taht should be used for filtering.

        WARNING: If you do not use a filter it will update the whole table!!!
        """

        where_statement = "WHERE"
        set_statement = "SET"

        if filter_columns:
            for count, item in enumerate(filter_columns):
                if count == len(filter_columns)-1:
                    where_statement += f" {item} = ?"
                    break

                where_statement += f" {item} = ? AND"
        else:
            where_statement = ""

        for count, item in enumerate(column):
            if count == len(column) - 1:
                set_statement += f" {item} = ?"
                break
            set_statement += f" {item} = ?, "

        endval = values
        if filter_values != None:
            endval += filter_values
        cur = await self.bot.act_database.cursor()
        await cur.execute(f"UPDATE {table} {set_statement} {where_statement}",
                          endval
                          )
        await self.bot.act_database.commit()

    async def delete(
        self,
        table: str,
        filter_columns: list | None = None,
        filter_values: tuple | None = None
    ):
        """
        Deletes either a row or the entire record from a table,

        Parameters:
        ============
        table(str): Table to be deleted from
        filter_coloumns(list): The column to be filtered defaults to none
        filter_values(tuple): The value to be filtered from. defaults to none

        WARNING: NOT PROVIDING A FILTER WILL DELETE THE ENTIRE RECORD!
        """

        where_statement = "WHERE"

        if filter_columns:
            for count, item in enumerate(filter_columns):
                if count == len(filter_columns)-1:
                    where_statement += f" {item} = ?"
                    break

                where_statement += f" {item} = ? AND"
        else:
            where_statement = ""
        
        cur = await self.bot.act_database.cursor()
        if filter_values == None:
            await cur.execute(f"DELETE FROM {table} {where_statement}")
        else:
            await cur.execute(f"DELETE FROM {table} {where_statement}", filter_values)
        await self.bot.act_database.commit()