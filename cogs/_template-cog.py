import discord
from discord.ext import commands
# These are the two imports you will ALWAYS need.

class NAME_OF_COG(commands.Cog): # Simply put the cog name here too

  def __init__(self, client):
        self.client = client
        # Just some fancy cog loading code, don't worry about it.

@commands.Cog.listener()
async def on_ready(self):
    print(f"{self.__class__.__name__} has been loaded!\n-----") # Print a statement saying this cog is loaded, you can easily keep track of loaded cogs.

@commands.command(name="CMD_NAME_HERE", description="CMD_DESC_HERE") # Self explanatory
async def CMD_NAME_HERE(self, ctx): # You are almost always gonna wanna put self and ctx here. For every command self is required.
        

        
  def setup(client):
    client.add_cog(NAME_OF_COG(client))
    # Just some fancy cog loading code, don't worry about it.
