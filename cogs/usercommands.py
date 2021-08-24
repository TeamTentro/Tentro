from discord.ext import commands
from discord import Embed, Member, User, channel, client, role, utils
import asyncio
import discord, sqlite3
from discord.ext.commands import bot
red = 0xff0000
green = 0x34eb40

intents = discord.Intents.all()

intents.members = True

path = "./data/Tentro.db"



class user(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    



    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        conn = sqlite3.connect(path)
        c = conn.cursor()

        c.execute("SELECT role_id FROM rolejoin WHERE EXISTS(SELECT role_id FROM rolejoin WHERE guild_id=?)", (member.guild.id,))
        result_4 = c.fetchone()

        
   
        role = discord.utils.get(member.guild.roles, id=result_4[0])
        await member.add_roles(role)
        conn.commit()
        c.close()
        conn.close()


             

    @commands.command(name="nickname", aliases=["nick"])
    async def _Nickname(self, ctx, member: discord.Member, *,nick):
        if ctx.author.guild_permissions.manage_messages and member.guild_permissions!=ctx.author.guild_permissions:
            await member.edit(nick=nick)
            embed = discord.Embed(title=f"Name changed", description=f"Succesfully changed {member.mention}'s name.", colour=0xff0000)
            await ctx.send(embed=embed)
    

    @commands.command(name="giverole", aliases=["gr"])
    async def _GiveRole(self, ctx, user : discord.Member, *, role : discord.Role):
        member = Member
        if ctx.author.guild_permissions.manage_messages and member.guild_permissions!=ctx.author.guild_permissions:
            await user.add_roles(role)
            embed = discord.Embed(title="Success!", description=f"Given {role.mention} to {user.mention}.", colour=0xff0000)
            embed.set_footer(text="Role Given")
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="You do not have the required permissions to do that!", colour=0xff0000)
            await ctx.send(embed=embed, delete_after=5)


    @commands.command(name="takerole", aliases=["tr"])
    async def _TakeRole(self, ctx, user : discord.Member, *, role : discord.Role):
        member = Member
        if ctx.author.guild_permissions.administrator and member.guild_permissions!=ctx.author.guild_permissions:
            await user.remove_roles(role)
            embed = discord.Embed(title="Success!", description=f"Taken {role.mention} from {user.mention}.", colour=0xff0000)
            embed.set_footer(text="Role Taken")
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="You do not have the required permissions to do that!", colour=0xff0000)
            await ctx.send(embed=embed, delete_after=5)

    @commands.group(invoke_without_command=True, name='rolejoin', aliases=['rj'])
    async def rolejoin(self, ctx):
        await ctx.send('Setup commands:\nrolejoin role <role.id> or <role.mention>')

    @rolejoin.command(pass_context=True)
    async def role(self, ctx, role: discord.Role):
        if ctx.message.author.guild_permissions.administrator:
            conn = sqlite3.connect(path)
            c = conn.cursor() 

            c.execute(f"SELECT role_id FROM rolejoin WHERE guild_id = {ctx.guild.id}")
            result = c.fetchone()

            if result is None:
                sql = ("INSERT INTO rolejoin(guild_id, role_id) VALUES(?,?)")
                val = (ctx.guild.id, role.id)
                c.execute(sql, val)
                await ctx.send(f"Role has been set to {role}!")
            elif result is not None:
                sql = ("UPDATE rolejoin SET role_id = ? WHERE guild_id = ?")
                val = (role.id, ctx.guild.id)
                c.execute(sql, val)
                await ctx.send(f"Role has been updated to {role}!")

            conn.commit()
            c.close()
            
        else:
            await ctx.send("You do not have the required permissions to do that!")

   

            



def setup(bot):
    bot.add_cog(user(bot))
