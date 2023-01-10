import discord
from discord.ext import commands
from aiohttp import request
import os
import asyncio


class Misc(commands.Cog, description="fun commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def cat(self, ctx):  # sends a random cat gif
        URL = "https://cataas.com/cat/"
        async with request("GET", URL, headers={}) as response:
            if response.status == 200:
                self.data = await response.json()
                await ctx.send(self.data["cat"])
            else:
                await ctx.send("Error. API website is down")


async def setup(bot):
    await bot.add_cog(Misc(bot))
