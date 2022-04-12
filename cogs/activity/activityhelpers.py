"""
Helper for activity cog of stealthy bot

"""
from sqlite3 import Row
import aiosqlite

class ActivityHelper():
    """
    Activity Helper class has functions that help with the activity feature.
    It is seperated from the main cog file for readability better organiaztion.
    """

    def __init__(self, database: aiosqlite.Connection):
        self.database = database

    async def create_or_fetch_server(self, serverid: int) -> tuple | Row:
        """
        creates or returns a server from the activity table.
        This is for better developer experiance
        """
        cur: aiosqlite.Cursor = await self.database.Cursor()
        await cur.execute(
            "SELECT * FROM activity WHERE ServerID = ?",
            (serverid,)
        )
        result = await cur.fetchone()
        if not result:
            result = (serverid, 150, 86400)
            await cur.execute("INSERT INTO activity VALUES(?,?,?)", result)
            await self.database.commit()
        return result

    async def create_or_fetch_user(self, userid: int, serverid: int)  -> tuple | Row:
        """creates or fetches a user from the database

        Args:
            userid (int): The user's id
            serverid (int): The server's Id
        """
        cur: aiosqlite.Cursor = await self.database.cursor()
        await cur.execute(
            "SELECT * FROM Users WHERE ServerID = ? AND UserID = ?",
            (serverid, userid)
        )
        result = await cur.fetchone()
        if not result:
            result = (serverid, userid, 0, 0, 0, 0)
            await cur.execute(
                "INSERT INTO Users VALUES(?, ?, ?, ?, ?, ?)",
                result
            )
        return result

    async def insert_into(self, table: str, values: tuple):
        """inserts values into the specifed table.
        For easier access to the tables.
        ( This looks suspiciously like orm behaviour dont tell anyone 🤫)

        Args:
            table (str): The table in which the values must be inserted into
            values (tuple): The values that must be inserted
        """

        cur: aiosqlite.Cursor = await self.database.cursor()
        await cur.execute(f"INSERT INTO {table} VALUES{values}")

    async def select_one(
        self,
        table: str,
        column: str = None,
        filter_column: str | None = None,
        filter_value: any = None
        ):
        """Select a single row from the specifed arguments

        Args:
            table (str): The table that the selection must happen in
            column (str, optional): The column that you need to be selected. Defaults to None.
            filter_column (str | None, optional): The column in which you specify
            the value that disqualifies a row . Defaults to None.
            filter_value (any, optional): The value that you need to filtered. Defaults to None.
        """
        where_statement = ""
        if not column:
            column = "*"

        if filter_column:
            where_statement = f"WHERE {filter_column} = {filter_value}"

        cur: aiosqlite.Cursor = await self.database.cursor()


        await cur.execute(f"SELECT {column} FROM {table} {where_statement}")
        result = cur.fetch_one()
        return result
