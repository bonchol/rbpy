import discord
from discord import app_commands
from discord.ext import commands
import datetime
import asyncio


class General(commands.Cog, description = "general commands of the bot (WIP)"):

    def __init__(self,bot):
        self.bot = bot

    #Commands
    @commands.command()
    async def ping(self, ctx):
        ''' 
        displays latency
        '''
        await ctx.send(f'Pong! Your latency is {round(self.bot.latency*1000)}ms')

    @commands.command(name="avatar")
    async def avatar(self, ctx, *,  member:discord.Member=None):
        '''
        fetches the avatar of the author
        '''
        if not member:
            member = ctx.message.author
        self.userAvatar = member.avatar.url

        #AvatarEmbed
        self.avatar_embed = discord.Embed(
            title = f"**{member.name}'s avatar:**",
            colour = discord.Colour.random(),
            timestamp=datetime.datetime.utcnow()
            )
        self.avatar_embed.set_image(url = self.userAvatar)
        self.avatar_embed.set_footer(text = 'nice' )
        await ctx.send(embed = self.avatar_embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=amount)
    

async def setup(bot):
    await bot.add_cog(General(bot))
