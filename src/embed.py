import discord 
import os 
from discord.ext import commands 
import json 
import datetime 
import logging 

bot = commands.Bot(command_prefix="+")

@bot.command()
async def msg(ctx):
    #embed = discord.Embed(title=title, description)
