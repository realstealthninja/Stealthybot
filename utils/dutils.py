import asyncio
import json


def jsonwriter(file1, data1):
    file1.truncate(0)
    file1.seek(0)
    file1.write(json.dumps(data1, indent=4))


async def paginate(ctx, embeds: list):
    current = 0
    msg = await ctx.send(embed=embeds[0])
    await msg.add_reaction("<:left:898911001158750229>")
    await msg.add_reaction("<:right:898910929264214076>")
    await msg.add_reaction("<:stop:898911046918627379>")

    def check(e, u):
        return u == ctx.author and e.message == msg

    e, u = await ctx.bot.wait_for("reaction_add", check=check)

    while str(e.emoji) != "<:stop:898911046918627379>":
        name = str(e.emoji)
        if name == "<:left:898911001158750229>":
            current -= 1

        elif name == "<:right:898910929264214076>":
            current += 1

        await msg.remove_reaction(member=ctx.author, emoji=e.emoji)
        try:
            await msg.edit(embed=embeds[current])
        except IndexError:
            if current == -1:
                current = len(embeds)
                await msg.edit(embed=embeds[current])
            else:
                current = 0
                await msg.edit(embed=embeds[current])
        e, u = await ctx.bot.wait_for("reaction_add", check=check)
    else:
        return await msg.clear_reactions()


# button.py into disnake
import asyncio
import disnake
import inspect
from disnake.ext import commands
from functools import partial
from typing import Union

__all__ = (
    "Session",
    "Paginator",
    "button",
    "inverse_button",
)


class Button:
    __slots__ = ("_callback", "_inverse_callback", "emoji", "position", "try_remove")

    def __init__(self, **kwargs):
        self._callback = kwargs.get("callback")
        self._inverse_callback = kwargs.get("inverse_callback")

        self.emoji = kwargs.get("emoji")
        self.position = kwargs.get("position")
        self.try_remove = kwargs.get("try_remove", True)


class Session:
    """Interactive session class, which uses reactions as buttons.

    timeout: int
        The timeout in seconds to wait for reaction responses.
    try_remove: bool
        A bool indicating whether or not the session should try to remove reactions after they have been pressed.
    """

    def __init__(self, *, timeout: int = 180, try_remove: bool = True):
        self._buttons = {}
        self._gather_buttons()

        self.page: disnake.Message = None
        self._session_task = None
        self._cancelled = False
        self._try_remove = try_remove

        self.timeout = timeout
        self.buttons = self._buttons

        self._defaults = {}
        self._default_stop = {}

    def __init_subclass__(cls, **kwargs):
        # i dont fucking know why its empty stfu
        pass

    def _gather_buttons(self):
        for _, member in inspect.getmembers(self):
            if hasattr(member, "__button__"):
                button = member.__button__

                sorted_ = self.sort_buttons(buttons=self._buttons)
                try:
                    button_ = sorted_[button.emoji]
                except KeyError:
                    self._buttons[button.position, button.emoji] = button
                    continue

                if button._inverse_callback:
                    button_._inverse_callback = button._inverse_callback
                else:
                    button_._callback = button._callback

                self._buttons[button.position, button.emoji] = button_

    def sort_buttons(self, *, buttons: dict = None):
        if buttons is None:
            buttons = self._buttons

        return {k[1]: v for k, v in sorted(buttons.items(), key=lambda t: t[0])}

    async def start(self, ctx, page=None):
        """Start the session with the given page.

        Parameters
        -----------
        page: Optional[str, disnake.Embed, disnake.Message]
            If no page is given, the message used to invoke the command will be used. Otherwise if
            an embed or str is passed, a new message will be created.
        """
        if not page:
            page = ctx.message

        if isinstance(page, disnake.Embed):
            self.page = await ctx.send(embed=page)
        elif isinstance(page, disnake.Message):
            self.page = page
        else:
            self.page = await ctx.send(page)

        self._session_task = ctx.bot.loop.create_task(self._session(ctx))

    async def _session(self, ctx: commands.Context):
        self.buttons = self.sort_buttons()

        ctx.bot.loop.create_task(self._add_reactions(self.buttons.keys()))

        await self._session_loop(ctx)

    async def _session_loop(self, ctx: commands.Context):
        while True:
            _add = asyncio.ensure_future(
                ctx.bot.wait_for("raw_reaction_add", check=lambda _: self.check(_)(ctx))
            )
            _remove = asyncio.ensure_future(
                ctx.bot.wait_for(
                    "raw_reaction_remove", check=lambda _: self.check(_)(ctx)
                )
            )

            done, pending = await asyncio.wait(
                (_add, _remove),
                return_when=asyncio.FIRST_COMPLETED,
                timeout=self.timeout,
            )

            for future in pending:
                future.cancel()

            if not done:
                return ctx.bot.loop.create_task(self.cancel())

            try:
                result = done.pop()
                payload = result.result()

                if result == _add:
                    action = True
                else:
                    action = False
            except Exception:
                return ctx.bot.loop.create_task(self.cancel())

            emoji = self.get_emoji_as_string(payload.emoji)
            button = self.buttons[emoji]

            if self._try_remove and button.try_remove:
                try:
                    await self.page.remove_reaction(
                        payload.emoji, ctx.guild.get_member(payload.user_id)
                    )
                except disnake.HTTPException:
                    pass

            member = ctx.guild.get_member(payload.user_id)

            if (
                action
                and button in self._defaults.values()
                or button in self._default_stop.values()
            ):
                await button._callback(ctx, member)
            elif action and button._callback:
                await button._callback(self, ctx, member)
            elif not action and button._inverse_callback:
                await button._inverse_callback(self, ctx, member)

    @property
    def is_cancelled(self):
        """Return True if the session has been cancelled."""
        return self._cancelled

    async def cancel(self):
        """Cancel the session."""
        self._cancelled = True
        await self.teardown()

    async def teardown(self):
        """Clean the session up."""
        self._session_task.cancel()

        try:
            await self.page.delete()
        except disnake.NotFound:
            pass

    async def _add_reactions(self, reactions):
        for reaction in reactions:
            try:
                await self.page.add_reaction(reaction)
            except disnake.NotFound:
                pass

    def get_emoji_as_string(self, emoji):
        return f'{emoji.name}{":" + str(emoji.id) if emoji.is_custom_emoji() else ""}'

    def check(self, payload):
        """Check which takes in a raw_reaction payload. This may be overwritten."""
        emoji = self.get_emoji_as_string(payload.emoji)

        def inner(ctx: commands.Context):
            if (
                emoji not in self.buttons.keys()
                or payload.user_id == ctx.bot.user.id
                or payload.message_id != self.page.id
                or payload.user_id != ctx.author.id
            ):
                return False
            return True

        return inner


class Paginator(Session):
    """Paginator class, that used an interactive session to display buttons.

    title: str
        Only available when embed=True. The title of the embeded pages.
    length: int
        The number of entries per page.
    entries: list
        The entries to paginate.
    extra_pages: list
        Extra pages to append to our entries.
    prefix: Optional[str]
        The formatting prefix to apply to our entries.
    suffix: Optional[str]
        The formatting suffix to apply to our entries.
    format: Optional[str]
        The format string to wrap around our entries. This should be the first half of the format only,
        E.g to wrap **Entry**, we would only provide **.
    colour: disnake.Colour
        Only available when embed=True. The colour of the embeded pages.
    use_defaults: bool
        Option which determines whether we should use default buttons as well. This is True by default.
    embed: bool
        Option that indicates that entries should embeded.
    joiner: str
        Option which allows us to specify the entries joiner. E.g self.joiner.join(self.entries)
    timeout: int
        The timeout in seconds to wait for reaction responses.
    thumbnail:
        Only available when embed=True. The thumbnail URL to set for the embeded pages.
    """

    def __init__(
        self,
        *,
        title: str = "",
        length: int = 10,
        entries: list = None,
        extra_pages: list = None,
        prefix: str = "",
        suffix: str = "",
        format: str = "",
        colour: Union[int, disnake.Colour] = None,
        color: Union[int, disnake.Colour] = None,
        use_defaults: bool = True,
        embed: bool = True,
        joiner: str = "\n",
        timeout: int = 180,
        thumbnail: str = None,
    ):
        super().__init__()
        self._defaults = {
            (0, "⏮"): Button(
                emoji="⏮", position=0, callback=partial(self._default_indexer, "start")
            ),
            (1, "◀"): Button(
                emoji="◀", position=1, callback=partial(self._default_indexer, -1)
            ),
            (2, "⏹"): Button(
                emoji="⏹", position=2, callback=partial(self._default_indexer, "stop")
            ),
            (3, "▶"): Button(
                emoji="▶", position=3, callback=partial(self._default_indexer, +1)
            ),
            (4, "⏭"): Button(
                emoji="⏭", position=4, callback=partial(self._default_indexer, "end")
            ),
        }
        self._default_stop = {
            (0, "⏹"): Button(
                emoji="⏹", position=0, callback=partial(self._default_indexer, "stop")
            )
        }

        self.buttons = {}

        self.page: disnake.Message = None
        self._pages = []
        self._session_task = None
        self._cancelled = False
        self._index = 0

        self.title = title
        self.colour = colour or color
        self.thumbnail = thumbnail
        self.length = length
        self.timeout = timeout
        self.entries = entries
        self.extra_pages = extra_pages or []

        self.prefix = prefix
        self.suffix = suffix
        self.format = format
        self.joiner = joiner
        self.use_defaults = use_defaults
        self.use_embed = embed

    def chunker(self):
        """Create chunks of our entries for pagination."""
        for x in range(0, len(self.entries), self.length):
            yield self.entries[x : x + self.length]

    def formatting(self, entry: str):
        """Format our entries, with the given options."""
        return f"{self.prefix}{self.format}{entry}{self.format[::-1]}{self.suffix}"

    async def start(self, ctx: commands.Context, page=None):
        """Start our Paginator session."""
        if not self.use_defaults and not self._buttons:
            raise AttributeError(
                "Session has no buttons."
            )  # Raise a custom exception at some point.

        await self._paginate(ctx)

    async def _paginate(self, ctx: commands.Context):
        if not self.entries and not self.extra_pages:
            raise AttributeError(
                "You must provide atleast one entry or page for pagination."
            )  # ^^

        if self.entries:
            self.entries = [self.formatting(entry) for entry in self.entries]
            entries = list(self.chunker())
        else:
            entries = []

        for chunk in entries:
            if not self.use_embed:
                self._pages.append(self.joiner.join(chunk))
            else:
                embed = disnake.Embed(
                    title=self.title,
                    description=self.joiner.join(chunk),
                    colour=self.colour,
                )

                if self.thumbnail:
                    embed.set_thumbnail(url=self.thumbnail)

                self._pages.append(embed)

        self._pages = self._pages + self.extra_pages

        if isinstance(self._pages[0], disnake.Embed):
            self.page = await ctx.send(embed=self._pages[0])
        else:
            self.page = await ctx.send(self._pages[0])

        self._session_task = ctx.bot.loop.create_task(self._session(ctx))

    async def _session(self, ctx: commands.Context):
        if self.use_defaults:
            if len(self._pages) == 1:
                self._buttons = {**self._default_stop, **self._buttons}
            else:
                self._buttons = {**self._defaults, **self._buttons}

        self.buttons = self.sort_buttons()

        ctx.bot.loop.create_task(self._add_reactions(self.buttons))

        await self._session_loop(ctx)

    async def _default_indexer(self, control, ctx, member):
        previous = self._index

        if control == "stop":
            return await self.cancel()

        if control == "end":
            self._index = len(self._pages) - 1
        elif control == "start":
            self._index = 0
        else:
            self._index += control

        if self._index > len(self._pages) - 1 or self._index < 0:
            self._index = previous

        if self._index == previous:
            return

        if isinstance(self._pages[self._index], disnake.Embed):
            await self.page.edit(embed=self._pages[self._index])
        else:
            await self.page.edit(content=self._pages[self._index])


def button(emoji: str, *, try_remove=True, position: int = 666):
    """A decorator that adds a button to your interactive session class.

    Parameters
    -----------
    emoji: str
        The emoji to use as a button. This could be a unicode endpoint or in name:id format,
        for custom emojis.
    position: int
        The position to inject the button into.

    Raises
    -------
    TypeError
        The button callback is not a coroutine.
    """

    def deco(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Button callback must be a coroutine.")

        if hasattr(func, "__button__"):
            button = func.__button__
            button._callback = func

            return func

        func.__button__ = Button(
            emoji=emoji, callback=func, position=position, try_remove=try_remove
        )
        return func

    return deco


def inverse_button(emoji: str = None, *, try_remove=False, position: int = 666):
    """A decorator that adds an inverted button to your interactive session class.

    The inverse button will work when a reaction is unpressed.

    Parameters
    -----------
    emoji: str
        The emoji to use as a button. This could be a unicode endpoint or in name:id format,
        for custom emojis.
    position: int
        The position to inject the button into.

    Raises
    -------
    TypeError
        The button callback is not a coroutine.
    """

    def deco(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Button callback must be a coroutine.")

        if hasattr(func, "__button__"):
            button = func.__button__
            button._inverse_callback = func

            return func

        func.__button__ = Button(
            emoji=emoji, inverse_callback=func, position=position, try_remove=try_remove
        )
        return func

    return deco
