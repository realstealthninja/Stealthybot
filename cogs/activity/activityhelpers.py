"""
Helper for activity cog of stealthy bot

"""
from sqlite3 import Row

import aiosqlite
import disnake


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
            filter_columns=["ServerID",],
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

        cur = await self.bot.act_database.cursor()
        await cur.execute(f"UPDATE {table} {set_statement} {where_statement}",
                          values + filter_values
                          )
        await self.bot.act_database.commit()
