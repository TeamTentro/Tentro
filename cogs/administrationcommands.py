from operator import is_not
from discord import Embed, Member, User, utils
from discord.ext import commands
import asyncio, discord
from discord.ext.commands import bot
from discord.ext.commands.core import has_role
from discord.ext.commands.errors import MissingPermissions
import random, sqlite3
from typing import Dict, List, Tuple, Union
import re, unicodedata
import cmath as math
from typing import List
import lib as mod
from typing import Dict, List, Tuple, Union


red = 0xff0000
green = 0x34eb40

time_convert = {"s":1, "m":60, "h":3600,"d":86400}

__MINUTES = 60
__HOURS = __MINUTES * 60
__DAYS = __HOURS * 24


class Command:
    __arguments: Dict[str, Union[str, int]]

    def get_value_of(self, name: str) -> Union[None, str, int]:
        if name in self.__arguments:
            return self.__arguments[name]
        return None

    def get_content(self) -> Union[None, str]:
        if "content" in self.__arguments:
            return self.__arguments["content"]
        return None


def get_time(command: Command) -> Union[None, int]:
    seconds: int = 0
    time_given: bool = False
    for (name, ratio) in _RATIOS:
        time: Union[str, int] = command.get_value_of(name)
        if time is not None and isinstance(time, int):
            time_given = True
            seconds += time * ratio
    if time_given:
        return seconds
    return None

def eligible(member: Member) -> bool:
    return member.guild_permissions.administrator or member.guild_permissions.manage_messages

class admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='mutesetup', aliases=['ms'])
    async def mutesetup(self, ctx, role: discord.Role):
        db = sqlite3.connect('tentro.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT muterole FROM mute WHERE guild_id = {ctx.guild.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO mute(guild_id, muterole) VALUES(?,?)")
            val = (ctx.guild.id, role.id)
            await ctx.send(f"MutedRole has been set to {role}")
        elif result is not None:
            sql = ("UPDATE mute SET muterole = ? WHERE guild_id = ?")
            val = (role.id, ctx.guild.id)
            await ctx.send(f"MutedRole has been updated to {role}") 
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command(name='mute', aliases=["m"])
    @commands.has_permissions(manage_messages=True, administrator=True)
    async def _Mute(self, ctx, member: discord.Member, time=None, *, reason=None):
        db = sqlite3.connect('tentro.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT muterole FROM mute WHERE EXISTS(SELECT muterole FROM mute WHERE guild_id=?)", (ctx.guild.id,))
        result = cursor.fetchone()
        print(result[0])
        mutedrole = discord.utils.get(ctx.guild.roles, id=result[0])

        cursor.execute(f"SELECT user_id FROM ismuted WHERE guild_id = {ctx.guild.id}") ##GETS USER ID 
        result_1 = cursor.fetchone()
        if result_1 is None:
            sql = ("INSERT INTO ismuted(guild_id, user_id) VALUES(?,?)")
            val = (ctx.guild.id, member.id)
        elif result_1 is not None:
            sql = ("UPDATE ismuted SET user_id = ? WHERE guild_id = ?")
            val = (member.id, ctx.guild.id)

        cursor.execute(sql, val)

        if time==None and reason==None: ##IF NO TIME AND NO REASON
            await member.add_roles(mutedrole)
            cursor.execute("SELECT user_id FROM ismuted WHERE EXISTS(SELECT user_id FROM ismuted WHERE guild_id=?)", (ctx.guild.id,)) ##GETS USER ID
            resultuser = cursor.fetchone()
            print(resultuser[0])
            cursor.execute("SELECT ismuted FROM ismuted WHERE EXISTS(SELECT ismuted FROM ismuted WHERE guild_id=?)", (ctx.guild.id,))## GETS ISMUTED : TRUE/FALSE
            resultismuted = cursor.fetchone()
            print(resultismuted)
            
            embed = Embed(description=f"**{member.mention} has been muted indefinitely.**", color=red) #embed of the information
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)

            embed = Embed(title=f"You have been muted in: {ctx.guild.name}.\n**Time period:** indefinitely.", colour=red)
            await member.send(embed=embed)

        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
   
    @commands.command(name="unban", aliases=["ub", "bebis4u"])
    async def _Unban(self, ctx, *, user: User):
        member = Member

        if ctx.author.guild_permissions.administrator:
            await ctx.guild.unban(user=user)
            embed = Embed(title="Success!", description=f"{user} has been sucessfully unbanned!", colour=red)
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="You do not have the required permissions to do that!", colour=red)
            await ctx.send(embed=embed, delete_after=5)

    @commands.command(description="Unmutes a specified user.")
    async def unmute(self, ctx, member: Member):

        if ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator and ctx.member.guild_permissions!=ctx.author.guild_permissions:
            mutedRole = utils.get(ctx.guild.roles, name="Muted")
            await member.remove_roles(mutedRole)

            embed = Embed(title="Unmuted", description=f"{member.mention} has been unmuted.",colour=red)
            embed.set_footer(text="Unmute") # Inconsistant use of footers and timestamps
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)

            embed = Embed(title = (f"You have been unmuted in: **{ctx.guild.name}.**"), colour=red)
            await member.send(embed=embed)
        else:
            embed = Embed(title="You do not have the required permissions to do that!", colour=red)
            await ctx.send(embed=embed, delete_after=5)

    @commands.command(name="warn")
    async def warn(self, ctx, member: Member, *, reason=None):
        if ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator and ctx.author.guild_permissions!=ctx.member.guild_permissions:
            embed = Embed(title="Warn", description=f"{member.mention} has been succesfully warned.", color=red )
            embed.set_footer(text="Warn")
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)
            embed = Embed(title=f"You have been warned in {ctx.guild.name}. Reason: {reason}.", color=red )
            try:              
               await member.send(embed=embed)
            except:
                pass
        else:
            embed = Embed(title="You do not have the required permissions to do that!", colour=red)
            await ctx.send(embed=embed, delete_after=5)
  
    @commands.command(name="kick", aliases=["k", "yeet"])
    async def kick(self, ctx, member: Member, *, reason=None):
        guild = ctx.guild
        if ctx.author.guild_permissions.kick_members or ctx.author.guild_permissions.administrator:
            
            await member.kick(reason=reason)
            embed = Embed(title="Kicked", description=f"{member.mention} has been kicked from the server.", colour=red)
            embed.add_field(name="Reason:", value=reason, inline=False)
            embed.set_footer(text="Kick")
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)
            embed = discord.Embed(title=f"You have been kicked from {guild.name}\nReason: {reason}", colour=red)
            try:
                await member.send(embed=embed)
            except:
                pass
            # Not needed
            #embed = Embed(title = (f"You have been kicked from: {ctx.guild.name}.\n**Reason:** {reason}."), colour=red)
            #await member.send(embed=embed)
      
    @commands.command(name="ban", aliases=["b", "nobebis4u", "daban"])
    async def ban(self, ctx, member: Member, *,time=None, reason=None):
        guild = ctx.guild
        user = User

        if ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.administrator and ctx.author.guild_permissions!=ctx.member.guild_permissions:
            if time==None: 
                await member.ban(reason=reason) 
                embed = Embed(title="Banned", description=f"{member.mention} has been banned from the server indefinitely.", colour=red)
                embed.add_field(name="Reason:", value=reason, inline=False)
                embed.set_footer(text="Ban")
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)  
                embed = discord.Embed(title=f"You have been banned from {guild.name}\nReason: {reason}\nTime period: indefinitely", colour=red)
                try: 
                    await member.send(embed=embed)
                except:
                    pass
            else:     ## IF TIME IS WRITTEN
                await member.ban(reason=reason)
                embed = Embed(title="Banned", description=f"{member.mention} has been banned from the server.", colour=red)
                embed.add_field(name="Reason:", value=reason, inline=False)
                embed.add_field(name=f"Time period:", value=time)
                embed.set_footer(text="Ban")
                embed.timestamp = ctx.message.created_at
                await ctx.send(embed=embed)               
                embed = discord.Embed(title=f"You have been banned from {guild.name}\nReason: {reason}\nTime period:{time}", colour=red)
                try:
                    await member.send(embed=embed)
                except:
             
                    await ctx.send("Member is not in any mutual server or has dm's blocked!", delete_after=4)

                
                duration = int(time[0: -1]) * time_convert[time[-1]]
                await asyncio.sleep(duration)
                await ctx.guild.unban(user=member)
        else:
            embed = Embed(title="You do not have the required permissions to do that!", colour=red)
            await ctx.send(embed=embed, delete_after=5)

        
           # Not needed
            #embed = Embed(title = (f"You have been banned from: {ctx.guild.name}.\n**Reason:** {reason}."), colour=red)
            #await member.send(embed=embed)


__MINUTES = 60
__HOURS = __MINUTES * 60
__DAYS = __HOURS * 24


_TYPES: List[Tuple[str, str]] = [
    ("seconds", "s"), ("minutes", "m"), ("hours", "h"), ("days", "d")]
_RATIOS: List[Tuple[str, int]] = [
    ("seconds", 1), ("minutes", __MINUTES), ("hours", __HOURS), ("days", __DAYS)]


def setup(bot):
    bot.add_cog(admin(bot)) 
    
