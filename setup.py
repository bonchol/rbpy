
# >>> MAIN SETUP >> Runs the bot
import discord
import os
import datetime
import contextlib
from discord import app_commands
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from os import getenv
import asyncio

load_dotenv()
token = getenv("roberta_token")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="+", intents=discord.Intents.all())
game = discord.Game("Hello World!")
embed = discord.Embed()


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Bot is online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="hello")
async def helloWorld(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hey {interaction.user.mention}! This is your first slash command!",
        ephemeral=True,
    )


@bot.tree.command(name="say")
async def say(interaction: discord.Interaction, say_something: str):
    await interaction.response.send_message(
        f"{interaction.user.name} said: `{say_something}`"
    )


@bot.event
async def on_message(message):
    if message.author.bot:  # checks if the message author is a bot
        return
    msg = message.content.lower()
    if msg == "hi":
        await message.channel.send("hallo!")
    await bot.process_commands(message)


class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Send Message", style=discord.ButtonStyle.grey)
    async def menuOne(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("Hallo World!")


@bot.command()
async def menu(ctx):
    view = Menu()
    await ctx.reply(view=view)


class HelpEmbed(
    discord.Embed
):  # Our embed with some preset attributes to avoid setting it multiple times
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional"
        self.set_footer(text=text)
        self.color = discord.Color.red()


class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__(  # create our class with some aliases and cooldown
            command_attrs={
                "help": "The help command for Roberta",
                "cooldown": commands.CooldownMapping.from_cooldown(
                    1.0, 3.0, type=commands.BucketType.user
                ),
                "aliases": ["commands"],
            }
        )

    async def send(self, **kwargs):
        """a short cut to sending to get_destination"""
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        """triggers when a `<prefix>help` is called"""
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.avatar.url)
        usable = 0

        for (
            cog,
            commands,
        ) in mapping.items():  # iterating through our mapping of cog: commands
            if filtered_commands := await self.filter_commands(commands):
                # if no commands are usable in this category, we don't want to display it
                amount_commands = len(filtered_commands)
                usable += amount_commands
                if cog:  # getting attributes dependent on if a cog exists or not
                    name = cog.qualified_name
                    description = cog.description or "No description"
                else:
                    name = "Uncategorized"
                    description = "Commands with no category"

                embed.add_field(
                    name=f"{name} Category [{amount_commands}]", value=description
                )

        embed.description = f"{len(bot.commands)} commands | {usable} usable"

        await self.send(embed=embed)

    async def send_command_help(self, command):
        """triggers when a `<prefix>help <command>` is called"""
        signature = self.get_command_signature(
            command
        )  # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(
            title=signature, description=command.help or "No help found..."
        )

        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)

        can_run = "No"
        # command.can_run to test if the cog is usable
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"

        embed.add_field(name="Usable", value=can_run)

        if command._buckets and (
            cooldown := command._buckets._cooldown
        ):  # use of internals to get the cooldown of the command
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )

        await self.send(embed=embed)

    async def send_help_embed(
        self, title, description, commands
    ):  # a helper function to add commands to an embed
        embed = HelpEmbed(title=title, description=description or "No help found...")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.help or "No help found...",
                )

        await self.send(embed=embed)

    async def send_group_help(self, group):
        """triggers when a `<prefix>help <group>` is called"""
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):
        """triggers when a `<prefix>help <cog>` is called"""
        title = cog.qualified_name or "No"
        await self.send_help_embed(
            f"{title} Category", cog.description, cog.get_commands()
        )


bot.help_command = Help()


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    await load()
    await bot.start(token)


asyncio.run(main())
# bot.run(os.environ['token']) #When dynos replenish
