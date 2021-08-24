import discord, datetime, os, random
from discord import *
from discord.ext import commands
from pathlib import Path
import lib.database as db

intents = discord.Intents.all()

red = 0xff0000

embed_8ball = Embed(title="8ball", color=red)
embed_8ball.add_field(name="Description: ", value="Ask tentro anything!", inline=False)
embed_8ball.add_field(name="Usage: ", value="t!8ball <question>", inline=False)
embed_8ball.set_footer(text="<> - required; [] - optional")

embed_clear = Embed(title="Clear", color=red)
embed_clear.add_field(name="Description: ", value="le clear", inline=False)
embed_clear.add_field(name="Usage: ", value="t!clear <amount of messages you want to clear>", inline=False)
embed_clear.set_footer(text="<> - required; [] - optional")

embed_ban = Embed(title="Ban", color=red)
embed_ban.add_field(name="Description: ", value="You can ban users temporary and indefinitely!", inline=False)
embed_ban.add_field(name="Usage: ", value="t!ban <@someone/member id> [time] [reason]", inline=False)
embed_ban.set_footer(text="<> - required; [] - optional")

embed_kick = Embed(title="Kick", color=red)
embed_kick.add_field(name="Description: ", value="You can kick users from the server!", inline=False)
embed_kick.add_field(name="Usage: ", value="t!kick <user id or ping user> [reason]", inline=False)
embed_kick.set_footer(text="<> - required; [] - optional")

embed_mute = Embed(title="Mute", color=red)
embed_mute.add_field(name="Description: ", value="Give someone a break from breaking the rules by muting them. When the command is ran, a new role called 'muted' is created. ", inline=False)
embed_mute.add_field(name="Usage: ", value="t!mute <@someone/member id> [time] [reason]", inline=False)
embed_mute.set_footer(text="<> - required; [] - optional")

embed_nickname = Embed(title="Nickname", color=red)
embed_nickname.add_field(name="Description: ", value="Change the nickname of a server member. ", inline=False)
embed_nickname.add_field(name="Usage: ", value="t!nickname <@someone/member id> <new nickname>", inline=False)
embed_nickname.set_footer(text="<> - required; [] - optional")

embed_warn = Embed(title="Warn", color=red)
embed_warn.add_field(name="Description: ", value="You can warn users in the server! Next time you check someones logs you can see what they got warned for!", inline=False)
embed_warn.add_field(name="Usage: ", value="t!warn <@someone/member id> [reason]", inline=False)
embed_warn.set_footer(text="<> - required; [] - optional")

embed_createchannel = Embed(title="Create Channel", color=red)
embed_createchannel.add_field(name="Description: ", value="Create a new channel for the server with this simple command.", inline=False)
embed_createchannel.add_field(name="Usage: ", value="t!createchannel <name>", inline=False)
embed_createchannel.set_footer(text="<> - required; [] - optional")

embed_sus = Embed(title="Sus", color=red)
embed_sus.add_field(name="Description: ", value="Mesure your sus!", inline=False)
embed_sus.add_field(name="Usage: ", value="t!sus [@someone/user id]", inline=False)
embed_sus.set_footer(text="<> - required; [] - optional")

embed_invite = Embed(title="Invite", color=red)
embed_invite.add_field(name="Description:", value="Invite Tentro to your server by using this command", inline=False)
embed_invite.add_field(name="Usage: ", value="t!invite", inline=False)
embed_invite.set_footer(text="<> - required; [] - optional")

#TEMPlATE
"""embed_ = Embed(title="", color=red)
embed_.add_field(name="Description: ", value="", inline=False)
embed_.add_field(name="Usage: ", value="", inline=False)
embed_.set_footer(text="<> - required; [] - optional")"""




embed_dictionary = {
"8ball" : embed_8ball,
"clear" : embed_clear,
"ban" : embed_ban,
"kick" : embed_kick,
"mute" : embed_mute,
"warn" : embed_warn,
"nickname" : embed_nickname,
"sus" : embed_sus,
"invite" : embed_invite
}


class help(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
    


    

    @commands.command(name="help")
    async def _Help(self, ctx, cmd=None, dm = None):
        author = ctx.author
        if cmd == None and (dm == None or dm != "dm"):

            embed = discord.Embed(title="These are all the commands", color=0xFF0000)
            embed.add_field(name="Moderation", value="`t!clear, t!ban, t!kick, t!mutet, !timedmute, t!unmute, t!ban, t!unban, t!slowmode, t!slowmodecheck, t!slowmodereset, t!createchannel, t!deletechannel, t!giverole, t!takerole, t!nickname, t!lockdown`", inline=False)
            embed.add_field(name="Information", value="`avatar, servername`", inline=False)
            embed.add_field(name="Misc", value="`8ball`", inline=False)
            embed.add_field(name="System", value="`help, ping, invite, server`", inline=False)
            embed.add_field(name="Bot version:", value="v1.0", inline=False)
            embed.add_field(name="Date released:", value="July 6th, 2021", inline=False)
            embed.set_footer(text="Still in progress!")
            embed.set_author(name=ctx.author.name)
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)

        elif cmd == "-dm":
            embed1 = discord.Embed(title="These are all the commands", color=0xFF0000)
            embed1.add_field(name="Moderation", value="`t!clear, t!ban, t!kick, t!mute, !timedmute, t!unmute, t!ban, t!unban, t!slowmode, t!slowmodecheck, t!slowmodereset, t!createchannel, t!deletechannel, t!giverole, t!takerole, t!nickname, t!lockdown`", inline=False)
            embed1.add_field(name="Information", value="`avatar, servername`", inline=False)
            embed1.add_field(name="Misc", value="`8ball`", inline=False)
            embed1.add_field(name="System", value="`help, ping, invite, server`", inline=False)
            embed1.add_field(name="Bot version:", value="v1.0", inline=False)
            embed1.add_field(name="Date released:", value="July 6th, 2021", inline=False)
            embed1.set_footer(text="Still in progress!")
            embed1.set_author(name=ctx.author.name)
            embed1.timestamp = ctx.message.created_at
            await author.send(embed=embed1)


        elif cmd in embed_dictionary.keys():
            await(ctx.send(embed = embed_dictionary[cmd]))
        else:
            embed = discord.Embed(title="These are all the commands", color=0xFF0000)
            embed.add_field(name="Moderation", value="`t!clear, t!ban, t!kick, t!mutet, !timedmute, t!unmute, t!ban, t!unban, t!slowmode, t!slowmodecheck, t!slowmodereset, t!createchannel, t!deletechannel, t!giverole, t!takerole, t!nickname, t!lockdown`", inline=False)
            embed.add_field(name="Information", value="`avatar, servername`", inline=False)
            embed.add_field(name="Misc", value="`8ball`", inline=False)
            embed.add_field(name="System", value="`help, ping, invite, server`", inline=False)
            embed.add_field(name="Bot version:", value="v1.0", inline=False)
            embed.add_field(name="Date released:", value="July 6th, 2021", inline=False)
            embed.set_footer(text="Still in progress!")
            embed.set_author(name=ctx.author.name)
            embed.timestamp = ctx.message.created_at
            await ctx.send(embed=embed)
            print("That's not a valid help command!")





def setup(bot):
    bot.add_cog(help(bot))