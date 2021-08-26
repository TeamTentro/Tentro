import sqlite3
from cogs.channelmoderation import channel
from operator import is_not, not_
from discord.ext import commands
from discord import Embed, Member, User, channel, client, colour, guild, message, user, utils
import asyncio, discord
from discord.ext.commands import bot
from discord.ext.commands.errors import MissingPermissions
import random, Toggle
from typing import Dict, List, Pattern, Set, Tuple, Union
import re, unicodedata
import cmath as math
from typing import List
import lib.automod as mod
path = "./data/Tentro.db"

ACTIVATED_COLOR = 0x00ff00
DEACTIVATED_COLOR = 0xff0000
RED = 0xff0000
DELETE_TIME: float = 5

_BLACK_LIST = ["dood", "nigga", "nigger"]
_FILLERS = [" ", "\-", "_"]


class automod(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    activated: bool
    blacklist: List[str]
    
# Example event
    Toggle = False
    @commands.command(name="automod")
    async def _automod(self, ctx):
        conn = sqlite3.connect(path)
        c = conn.cursor()
       
        if not eligible(ctx.author):
            await ctx.send("You do not have the required permissions to do that!", delete_after=5)
            return
        
        global Toggle   
        await ctx.message.add_reaction("✅")
        if Toggle is not True and Toggle is not False:
            Toggle = False
            
        Toggle = not Toggle

        if Toggle:
            embed = Embed(title="Automod has been enabled!", color=RED)
            await ctx.send(embed=embed)
        elif not Toggle:
            embed = Embed(title="Automod has been disabled!", color=RED)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        
        if Toggle == True:
            try:
                member: discord.Member
                message = message
                bl_words = mod.check_bl(str(message.content), _BLACK_LIST, bl_algorithms=[
                mod.check_bl_direct(), mod.check_bl_fillers()], fillers=_FILLERS)
                
                if bl_words:
                    embed = discord.Embed(title = "You said a blacklisted word.")
                    await message.channel.send(embed=embed, delete_after=3)
                    await message.delete()
                
                spam_probability = mod.get_spam_probability(str(message.content), spam_algorithms=[mod.check_spam_alternating_cases(
                ), mod.check_spam_by_repetition(), mod.check_spam_repeating_letters(), mod.check_spam_caps()])
                
                if spam_probability > 0.5 and spam_probability < 0.7: 
                    embed = discord.Embed(title="Don't spam in this channel!")
                    await message.channel.send(embed=embed, delete_after=3)  
                    await message.delete()  
                
                if spam_probability > 0.8:
                    embed = discord.Embed(title="Don't spam or you'll get muted!")
                    await message.channel.send(embed=embed, delete_after=3)
                    mutedRole = utils.get(guild.roles, name="Muted")
                    if not mutedRole:
                        mutedRole = await guild.create_role(name="Muted")
                    await member.add_roles(mutedRole)
                    muted_role = utils.get(message.guild.roles, name="Muted")
                    await member.add_roles(muted_role)           
            except:
                pass
        elif Toggle is False: 
            pass

def eligible(member: Member) -> bool:
    return member.guild_permissions.administrator

async def bot_activation(self, activated: bool, ctx):
    color, activation_text = (ACTIVATED_COLOR, "Activated") if activated else(
        DEACTIVATED_COLOR, "Deactivated")
    embed = Embed(title=f"Automod {activation_text}", color=color)
    await bot_activation(self.activated, ctx)
    await ctx.send(embed = embed, delete_after=DELETE_TIME)

def setup(bot):
    bot.add_cog(automod(bot))
