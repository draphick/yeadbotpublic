# Work w# Work with Python 3.6
from discord.ext import commands
import requests
import urllib3
import json
import random
import re
from bs4 import BeautifulSoup
urllib3.disable_warnings()
import socket

if socket.gethostname() == "win-testpy":
    debug = "y"
else:
    debug = "n"



if debug == "y":
    TOKEN = '{DISCORD TOKEN FOR TEST}'
else:
    TOKEN = '{DISCORD TOKEN FOR PROD}'


# this specifies what extensions to load when the bot starts up
startup_extensions = ["cogs.rng", "cogs.dungeonmaster", "cogs.player"]

bot = commands.Bot(command_prefix=['yy', 'yead', ','])

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    message.content = message.content.lower()
    await bot.process_commands(message)

    rollregex = re.compile('^[0-9]{1,3}[d][0-9]{1,5}$')
    if rollregex.match(message.content):
        try:
            rolls, limit = map(int, message.content.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return
        author = message.author
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await bot.send_message(message.channel, author.mention + " rolled: " + result)

    rollregex2 = re.compile('^[d][0-9]{1,5}$')
    if rollregex2.match(message.content.lower()):
        fullstr = message.content.lower()
        justnumber = fullstr.replace("d", "")
        dice = int(justnumber)
        await bot.send_message(message.channel, message.author.mention + " rolled: " + "**" + str(random.randint(1, dice)) + "**")

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        await bot.send_message(ctx.message.channel, "Yikes! No such command exists.  \nCheck `yeadhelp` for more info.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await bot.send_message(ctx.message.channel, "Whoopsies - _{}_".format(error) + "\nCheck `yeadhelp <command>` for more info.")
    elif isinstance(error, commands.BadArgument):
        await bot.send_message(ctx.message.channel, "Whoopsies - Bad argument provided.\nCheck `yeadhelp <command>` for more info.")
    else:
        raise error


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(TOKEN)
