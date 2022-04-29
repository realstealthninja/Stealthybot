""" Views file contains all the buttons views and more"""
from ctypes import Union
import re
from typing import Optional
import black

from disnake import Emoji, MessageInteraction, Embed, ButtonStyle, PartialEmoji
from disnake.ui import View, button, Button
from .activityhelpers import ActivityHelper


class SetupActivity(View):
    """ set the message goal """

    def __init__(self, ctx, helper) -> None:
        self.ctx = ctx
        self.act_helper: ActivityHelper = helper
        super().__init__(timeout=2400.0)

    async def on_timeout(self) -> None:
        """ To make sure the bot doesnt randomly have alot of views to listen to"""
        for child in self.children:
            self.remove_item(child)
        self.stop()
        await self.ctx.send("uh oh! you didnt respond!")

    async def interaction_check(
        self,
        interaction: MessageInteraction
    ) -> bool:
        """ A check to make sure the interactiee is the same as the auhtor """
        if interaction.author != self.ctx.author:
            return False
        return True

    @button(
        label="Confirm",
        style=ButtonStyle.green,
        emoji="✅",
    )
    async def confirm(
        self,
        button_confirm: Button,
        interaction: MessageInteraction
    ) -> None:
        """ if the reaction is confim go to another embed """
        await interaction.response.defer()
        await interaction.edit_original_message(embed=Embed(
            title="What should be the message goal?"
        ))

        button_confirm.disabled = True

        def check(message):
            return message.author == interaction.author and re.match(r"\d", message.content)
        msg_goal = await interaction.bot.wait_for("message", check=check)
        await interaction.edit_original_message(embed=Embed(
            title="What should be the Time limit?",
            description="""
            Recommened: 24 hours \n please make sure the input is as `h.message`
            eg: 24.0
                0.5
            """
        ))

        def digit_check(message):
            return message.author == interaction.author and re.match(r"\d+\.\d+", message.content)
        time_limit = await interaction.bot.wait_for(
            "message",
            check=digit_check)

        self.add_item(EmbedBtn(label="Embed", emoji="⚗️", style=ButtonStyle.blurple))
        self.add_item(MessageBtn(label="Message", emoji="💬", style=ButtonStyle.gray))
        await interaction.edit_original_message(view=self)

        old_goal = await self.act_helper.select_one(
            "activity",
            column="MsgGoal",
            filter_columns=["ServerID", ],
            filter_values=(interaction.guild.id,)
        )

        if old_goal:
            await self.act_helper.update_set(
                "activity",
                column=["MsgGoal", "TimeLimit"],
                values=(int(msg_goal.content), float(time_limit.content)),
                filter_columns=["ServerID", ],
                filter_values=(interaction.guild.id,)
            )
        else:
            await self.act_helper.insert_into(
                "activity",
                values=(interaction.guild.id, int(
                    msg_goal.content), float(time_limit.content))
            )

        await interaction.edit_original_message(embed=Embed(
            title="Part one done!",
            description=f"""
            Your new act goal:
            {msg_goal.content} messages under {time_limit.content} hours"""
        ))


class EmbedBtn(Button):
    """
    Overriding button so we can make a callback when doing
    `.add_item`
    """

    def __init__(self, *,
                 style=...,
                 label=None,
                 disabled=False,
                 custom_id=None,
                 url=None,
                 emoji=None,
                 row=None
                 ):
        super().__init__(style=style, label=label, disabled=disabled,
                         custom_id=custom_id, url=url, emoji=emoji, row=row)

    async def callback(self, interaction: MessageInteraction):
        await interaction.response.defer()
        for child in self.view.children:
            self.view.remove_item(child)
        await interaction.edit_original_message(embed=Embed(
            title="Welcome to the Embed builder!",
            description="Check the next embed to see what an embed looks like \
            \n Please do keep  in mind we dont have alot of features in the\
            embed builder right now.."
        ))
        await interaction.send(
            embed=Embed(
                title="This is an Embed!",
                description="You can type NONE if you dont want a thumbnail or an image!"
            ).set_image(
                url="https://anidiots.guide/.gitbook/assets/first-bot-embed-example.png"
            )
        )
        await interaction.edit_original_message(embed=Embed(
            title="What should be the Embed title?"
        ))
        def check(message):
            return message.author == interaction.author
        title = await interaction.bot.wait_for(
            "message",
            check=check
        )
        await interaction.edit_original_message(embed=Embed(
            title="What should the description be?"
        ))
        description = await interaction.bot.wait_for(
            "message",
            check=check
        )
        await interaction.edit_original_message(embed=Embed(
            title="What should the image link be?"
        ))
        image = await interaction.bot.wait_for(
            "message",
            check=check
        )
        await interaction.edit_original_message(embed=Embed(
            title="What should the Thumbnail link be?"
        ))
        thumbnail = await interaction.bot.wait_for(
            "message",
            check=check
        )

        old_embed = await self.view.act_helper.select_one(
            "Embeds",
            filter_columns=["ServerID", ],
            filter_values=(interaction.guild.id,)
        )

        if old_embed:
            await self.view.act_helper.update_set(
                "Embeds",
                column=["Title", "Des", "Image", "Thumbnail"],
                values=(title.content, description.content, image.content, thumbnail.content),
                filter_columns=["ServerID", ],
                filter_values=(interaction.guild.id,)
            )
        else:
            await self.view.act_helper.insert_into(
                "Embeds",
                values=(
                    interaction.guild.id,
                    title.content,
                    description.content,
                    image.content,
                    thumbnail
                )
            )
        await interaction.edit_original_message(embed=Embed(
            title="done!",
            description="""Your new embed should shortly arrive!
            Thank you for using stealthy bot ❤️
            """
        ))
        embed = await self.view.act_helper.fetch_embed(interaction.guild.id)
        await interaction.send(embed=embed)
        for child in self.view.children:
            self.view.remove_item(child)
        self.view.stop()


class MessageBtn(Button):
    """
    Overriding button so we can make a callback when doing
    `.add_item`
    """

    def __init__(self, *,
                 style=...,
                 label=None,
                 disabled=False,
                 custom_id=None,
                 url=None,
                 emoji=None,
                 row=None
                ):
        super().__init__(style=style, label=label, disabled=disabled,
                         custom_id=custom_id, url=url, emoji=emoji, row=row)

    async def callback(self, interaction: MessageInteraction):
        print("hello!")
