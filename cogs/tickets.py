
from enum import IntEnum
from discord import Embed
from discord.ext import commands
import discord.utils, sqlite3

from discord_components import DiscordComponents, Button, ButtonStyle, component
from operator import is_not, not_
from discord_components import *
from discord import Embed, Member, User, channel, client, colour, guild, message, user, utils
path = "./data/Tentro.db"
class tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
     
    
    @commands.command(name="test1")
    async def button(self, ctx):
        await ctx.send(
        "Hello, World!",
        components = [
            Button(label = "WOW button!", custom_id = "button1")
        ]
    )

        interaction = await self.bot.wait_for("button_click", check = lambda i: i.custom_id == "button1")
        await interaction.send(content = "Button clicked!")      
            

 




    @commands.command(name="help_tickets")
    async def help_ticket(self, ctx):
        embed = Embed(title="Tickets", description="ticket_add: Creates a ticket channel and category, you can also add a custom message to it, if not it will use a default message we have set\nticket_remove: Deletes the ticket channel and category\nticket_addrole: Adds a role that will be able to see the tickets\nticket_removerole: Removes the role's permissions  to view tickets", colour=0xff0000)
        await ctx.send(embed=embed)

    @commands.command(name="tickets_add")
    @commands.is_owner()
    async def tickets_add(self, ctx, *, text=None):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        
       
        # Check if the category already exists
        ticketcat_e = discord.utils.get(ctx.guild.categories, name="🎫-Tickets")
        if ticketcat_e:
            return await ctx.send("Ticket category already exists, setup aborted.")
        else:
            ticketcat = await ctx.guild.create_category(name="🎫-Tickets")

        # Check if the text channel already exists
        ticketchannel_e = discord.utils.get(ctx.guild.text_channels, name="ticketinfo")
        if ticketchannel_e:
            return await ctx.send("Ticket channel already exists, setup aborted.")
        else:
            ticketchannel = await ctx.guild.create_text_channel(name="ticketinfo", category=ticketcat)

        default_role = ctx.guild.default_role
        await ticketchannel.set_permissions(target=default_role, speak=False, send_messages=False, read_message_history=True, read_messages=True, add_reactions=False)
        if text:
            embedticket = Embed(title=f"Tickets for {ctx.guild.name}", description=f"{text}", color =0xff0000)
            ticketmsg = await ticketchannel.send(embed=embedticket)
            await ticketmsg.add_reaction("🎫")
            addedembed = Embed(title="✅| Succesfully added the Tentro ticket system to this server. Run t!help_tickets for more info.", colour = 0x00ff00)
            await ctx.send(embed=addedembed)
            
            
            c.execute(f"SELECT msg_id FROM ticket WHERE guild_id = {ctx.guild.id}")
            result2 = c.fetchone()
            if result2 is None:
                sql = ("INSERT INTO ticket(guild_id, msg_id) VALUES(?,?)")
                val = (ctx.guild.id, ticketmsg.id)
                await ctx.send(f"Msg id has been set")
               
            elif result2 is not None:
                sql = ("UPDATE ticket SET msg_id = ? WHERE guild_id = ?")
                val = (ticketmsg.id, ctx.guild.id)
                await ctx.send(f"Msg id  has been set")
              

        elif text==None:
            embedticketchannel = Embed(title=f"Tickets for {ctx.guild.name}", description="React to this message with '🎫' to open a ticket. Use tickets wisely and don't open them for dumb reasons.", color=0xc4f21d)
            ticketmsg = await ticketchannel.send(embed=embedticketchannel)
            await ticketmsg.add_reaction("🎫")

            addedembed = Embed(title="✅| Succesfully added the Tentro ticket system to this server. Run t!help_tickets for more info.", colour = 0x00ff00)
            await ctx.reply(embed=addedembed)

        c.execute(sql, val)
        conn.commit()
        c.close()
        conn.close()

      


    @commands.command(name="tickets_remove")
    @commands.is_owner()
    async def tickets_remove(self, ctx):
        
        ticketcategory = discord.utils.get(ctx.guild.categories, name="🎫-Tickets")
        ticketchannel = discord.utils.get(ctx.guild.text_channels, name="ticketinfo")
        if ticketcategory == None or ticketchannel == None:
            embed = Embed(title="✅| There are no ticket utils", colour = 0x00ff00)
            await ctx.reply(embed=embed)
        
        else:
          await ticketcategory.delete()
          await ticketchannel.delete()
          embed = Embed(title="✅| Successfully removed the ticket utilities from this server", colour = 0x00ff00)
          await ctx.reply(embed=embed)

    @commands.command(name="roleperm")
    @commands.is_owner()
    async def roleperm(self, ctx, role: discord.Role):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute(f"SELECT role_id FROM ticket WHERE guild_id = {ctx.guild.id}")
        result = c.fetchone()
        if result is None:
            sql = ("INSERT INTO ticket(guild_id, role_id) VALUES(?,?)")
            val = (ctx.guild.id, role)
            await ctx.send(f"Role_id has been set to {role}")
        elif result is not None:
            sql = ("UPDATE ticket SET role_id = ? WHERE guild_id = ?")
            val = (role, ctx.guild.id)
            await ctx.send(f"Role_id has been updated to {role}") 
        c.execute(sql, val)
        conn.commit()
        c.close()
        conn.close()

    
    @commands.group(invoke_without_command=True)
    async def ticketlog(self, ctx):
        await ctx.send('Setup command: t!ticketlog (channel)') 

    @ticketlog.command()
    async def channel(self, ctx, channel: discord.TextChannel):  
        if ctx.message.author.guild_permissions.administrator:
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute(f"SELECT channel_id FROM ticketlogcmd WHERE guild_id = {ctx.guild.id}")
            result = c.fetchone()
            if result is None:
                sql = ("INSERT INTO ticketlogcmd(guild_id, channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Ticket log channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE ticketlogcmd SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Ticket log channel has been updated to {channel.mention}") 
            c.execute(sql, val)
            conn.commit()
            c.close()
            conn.close()
        
            

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member

        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("SELECT msg_id FROM ticket WHERE EXISTS(SELECT msg_id FROM ticket WHERE guild_id=?)", (payload.guild_id,))
        result_3 = c.fetchone()
        
      
        
        if payload.message_id==result_3[0]:
            
            guild_id = payload.guild_id
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            guild = discord.utils.find(lambda g : g.id == guild_id, self.bot.guilds)
            emoji = payload.emoji.name
            
 
            name = payload.member.name     
            role2 = discord.utils.get(guild.roles, name="@everyone")
            ticketcategory = discord.utils.get(guild.categories, name="🎫-Tickets")

            tick = await guild.create_text_channel(name=f"ticket-{name}", category=ticketcategory)
            channel = self.bot.get_channel(tick)
            
            await message.remove_reaction(emoji, user)         
            await tick.set_permissions(target=role2, speak=False, send_messages=False, read_message_history=False, read_messages=False, add_reactions=False, view_channel=False)##permissions
            await tick.set_permissions(target=user, speak=True, send_messages=True, read_message_history=True, read_messages=True, view_channel=True, add_reactions=False)


            embed = discord.Embed(title="Ticket utils (staff only)", color=0xf7fcfd)
            embed.add_field(name="📄 Claim the Ticket!", value="Claim the ticket so that the other supporters know that it is already being processed.", inline=False)
            embed.add_field(name="🗑️ Delete the ticket!", value="Delete the current ticket.", inline=False)
            embed.add_field(name="🔒 Lock the Ticket!", value="Lock the ticket from the perso who has opened it.", inline=False)
            components = [[Button(style=3, label="📄 Claim", custom_id="button2"),Button(style=4, label="🗑️ Delete", custom_id="deletebutton"), Button(style=2, label="🔒 Lock", custom_id="lockbutton")]]
            await tick.send(embed=embed, components=components)

            interaction = await self.bot.wait_for("button_click", check = lambda i: i.custom_id == "button2")
            await interaction.send(content = "You have claimed the ticket!")
            await tick.send("Ticket has been claimed by a staff member!")
            await tick.edit(name="Claimed Ticket", category=ticketcategory)
            

            interaction = await self.bot.wait_for("button_click", check = lambda i: i.custom_id == "lockbutton")
            await interaction.send(content = "Ticket has been locked!")
            await tick.send("Ticket has been locked!")
            await tick.set_permissions(target=user, speak=False, send_messages=False, read_message_history=False, read_messages=False, view_channel=False, add_reactions=False)

            interaction = await self.bot.wait_for("button_click", check = lambda i: i.custom_id == "deletebutton")
            await tick.delete()
            

            
         

        guild_id = payload.guild_id
        guild = self.bot.get_guild(guild_id)

        user_id = payload.user_id
        user = self.bot.get_user(user_id)

        channel_id = payload.channel_id
        channel = self.bot.get_channel(channel_id)

        message_id = payload.message_id
        emoji = payload.emoji.name

        conn.commit()
        c.close()
        conn.close()



   

   

    

def setup(bot):
    bot.add_cog(tickets(bot))
    