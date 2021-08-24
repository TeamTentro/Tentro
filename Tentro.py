# Import Discord Package

import discord, datetime, os, random, sqlite3
from discord import *
from discord.ext import commands
from pathlib import Path
import lib.database as db
from discord_components import *
from discord_components import DiscordComponents, Button, ButtonStyle, component, InteractionEventType
intents = discord.Intents.all()
path = "./data/Tentro.db"
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

# Bot
def get_prefix(bot, message):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(f"SELECT prefix FROM prefix WHERE guild_id = {message.guild.id}")
    prefix = c.fetchone()
    if prefix is not None:
        prefix = prefix[0]
    else:
        prefix = "t!" #return default prefix if guild not saved in database.
        c.execute(f"SELECT prefix FROM prefix WHERE guild_id = {message.guild.id}")
        result = c.fetchone()
        print(result)
        sql = ("INSERT INTO prefix(guild_id, prefix) VALUES(?,?)")
        val = (message.guild.id, prefix)
        c.execute(sql, val)
    if prefix is None:
        prefix = "t!" #return default prefix if guild not saved in database.
        c.execute(f"SELECT prefix FROM prefix WHERE guild_id = {message.guild.id}")
        result = c.fetchone()
        print(result)
        sql = ("INSERT INTO prefix(guild_id, prefix) VALUES(?,?)")
        val = (message.guild.id, prefix)

        
        c.execute(sql, val)
        conn.commit()
        c.close()
    conn.close()
    return prefix


owners = [668423998777982997, 391936025598885891, 620690744897699841, 804970459561066537, 216260005827969024, 671791003065384987] # Allows us to run commands with the @commands.is_owner() decorator.
bot = commands.Bot(command_prefix = get_prefix, owner_ids = owners, intents = intents, case_insensitive = True)
print(f"Tentro is connecting..\n-----")
print("Tentro Database setting up.. please hold.\n-----")
db.setup()
print(f'Tentro has connected successfully.')

# le status

@bot.remove_command("help")
@bot.event
async def on_ready():
    
    DiscordComponents(bot)
    general_channel = bot.get_channel(745925853229350975)
    await general_channel.send("Bot is online!")
    await bot.change_presence(activity=discord.Game(name="t!help for Help!"))

@bot.event
async def on_message(message):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    if message.content =="!t":
        await message.channel.send("This is the default prefix")

    
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        c.execute(f"SELECT prefix FROM prefix WHERE guild_id = {message.guild.id}")
        result = c.fetchone()
        await message.channel.send(f"My prefix is ``{result[0]}``")
    elif bot.user.mentioned_in(message) and message.mention_everyone is False:
        await message.channel.send(f"My prefix is ``t!``")


    
    

    await bot.process_commands(message)

@bot.command()
async def prefix(ctx, prefix):
    if ctx.author.guild_permissions.administrator:
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute(f"SELECT prefix FROM prefix WHERE guild_id = {ctx.guild.id}")
        result = c.fetchone()
        if result is None:
            sql = ("INSERT INTO prefix(guild_id, prefix) VALUES(?,?)")
            val = (ctx.guild.id, prefix)
            await ctx.send(f"Prefix has been set to {prefix}")
        elif result is not None:
            sql = ("UPDATE prefix SET prefix = ? WHERE guild_id = ?")
            val = (prefix, ctx.guild.id)
            await ctx.send(f"Prefix has been set to {prefix}") 
        else:
            result = "t!"
        c.execute(sql, val)
        conn.commit()
        c.close()
        conn.close()




    
         

# C O M M A N D S

for file in os.listdir(cwd+"/cogs"):
    if file.endswith(".py") and not file.startswith("_"):
        bot.load_extension(f"cogs.{file[:-3]}")

with open("token.0", "r", encoding="utf-8") as f:
    TOKEN = f.read()

bot.run(TOKEN)

