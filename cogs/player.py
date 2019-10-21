import discord
from discord.ext import commands
from .dataIO import fileIO
import os
import asyncio
from datetime import datetime, timedelta
import logging
import typing
import random

playerjson = "data/player/player.json"
playerlog = "data/player/player.log"
notplaying = " is not playing. Use `yeadletsplay YourCharacterName` to create a character."
stattype = ["str", "prc", "knw", "mvm", "dpl"]

class YeadPlayer:
    """The things for the YEAD players"""

    def __init__(self, bot):
        self.bot = bot
        self.player = fileIO(playerjson, "load")

    @commands.command(pass_context=True)
    async def letsplay(self, ctx, *, name : str):
        """Setup your new player for this campaign.
        Usage:
            yeadletsplay FirstName LastName LongerName
                This will make your name 'FirstName LastName LongerName'"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            await self.bot.say(author.mention + " is already playing.  Use `yeadupdatename New Name` to update your name.")
        else:
            newname = " ".join([i.capitalize() for i in name.split()])
            self.player.append({"discordID" : author.id, "level" : 1, "xpcurrent" : 0, "xpmax" : 1000, "playerName" : newname, "comments": {}, "inventory": {}, "stats" : { "str" : 0, "prc" : 0, "knw" : 0, "mvm" : 0, "dpl" : 0}})
            logger.info("{} ({}) added their player.".format(author.name, author.id))
            await self.bot.say(author.mention + " is now playing as: " + newname + ".")
            fileIO(playerjson, "save", self.player)

    @commands.command(pass_context=True)
    async def imdead(self, ctx):
        """Your character is gone... Goodbye!"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    self.player.remove(user)
                    fileIO(playerjson, "save", self.player)
                    await self.bot.say(author.mention + " is dead. Goodbye!")
                    logger.info("{} ({}) killed themselves and restarted their character.".format(author.name, author.id))
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def updatename(self, ctx, *, name : str):
        """Update your player name for this campaign.
        Usage:
            yeadupdatename FirstName LastName WhyYourNameSoLong
                This well make your name 'FirstName LastName WhyYourNameSoLong'"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    newname = " ".join([i.capitalize() for i in name.split()])
                    user["playerName"] = newname
                    logger.info("{} ({}) Updated their player name.".format(author.name, author.id))
                    await self.bot.say(author.mention + " is now: " + newname)
                    fileIO(playerjson, "save", self.player)
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def whoami(self, ctx):
        """Get player details."""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    msg = """You forget who you are already?  """
                    msg = msg + "\n\nHi!  You are a **level " + str(user["level"]) + "** named **" + user["playerName"] + "**."
                    msg = msg + "\nYou are **" + str(100 * float(user["xpcurrent"])/float(user["xpmax"])) + "%** of the way to your next level."
                    msg = msg + "\n\nYou have a bag.  Let's see what's inside:"
                    msg = msg + "```"
                    if len(user["inventory"]) > 0:
                        for item in user["inventory"]:
                            msg = msg + "\n" + str(user["inventory"][item]) + "x   " + item
                    else:
                        msg = msg + "\n Oooooo, such empty!\n"
                    msg = msg + "```"
                    msg = msg + "\nHmm... what else... Oh, you have some stats too!"
                    msg = msg + "```"
                    for stat in user["stats"]:
                        if stat == "str":
                            longstat = stat.replace("str", "STR (STRENGTH):   ")
                        elif stat == "dpl":
                            longstat = stat.replace("dpl", "DPL (DIPLOMACY):  ")
                        elif stat == "knw":
                            longstat = stat.replace("knw", "KNW (KNOWLEDGE):  ")
                        elif stat == "mvm":
                            longstat = stat.replace("mvm", "MVM (MOVEMENT):   ")
                        elif stat == "prc":
                            longstat = stat.replace("prc", "PRC (PERCEPTION): ")
                        msg = msg + "\n" + str(longstat) + str(user["stats"][stat])
                    msg = msg + "```"
                    msg = msg + "\nStats are good and all, but what about _you_ do we really know?"
                    msg = msg + "```"
                    if len(user["comments"]) > 0:
                        for key in user["comments"]:
                            msg = msg + "\n" + str(key) + ": " + str(user["comments"][key])
                    else:
                        msg = msg + "Oh.  I guess we know nothing.  Use yeadcomm to add some flavor!"
                    msg = msg + "```"
                    embed = discord.Embed(description=author.mention + msg, color=0xFFC0CB)
                    if "avatar" in user:
                        embed.set_thumbnail(url=user["avatar"])
                    else:
                        embed.set_thumbnail(url=author.avatar_url)
                    await self.bot.send_message(ctx.message.channel, embed=embed)
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def bag(self, ctx, newitem : str, amount : int):
        """add/remove inventory
        Usage:
            yeadbag toys 5
                This add 5 toys to your inventory.
            yeadbag toys -2
                This removes 2 toys from your inventory."""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    if newitem in user["inventory"]:
                        user["inventory"][newitem] = user["inventory"][newitem] + amount
                        if user["inventory"][newitem] < 1:
                            del user["inventory"][newitem]
                            await self.bot.say(author.mention + " you have less than 1 " + newitem + ".  It is being deleted from your inventory.")
                        else:
                            await self.bot.say(author.mention + ": " + str(amount) + " to " + newitem + " in your inventory.")
                        fileIO(playerjson, "save", self.player)
                    else:
                        if amount < 1:
                            await self.bot.say(author.mention + " you can't remove items from items you don't have")
                        else:
                            user["inventory"][newitem] = amount
                            await self.bot.say(author.mention + ": " + str(amount) + " " + newitem + " to your inventory.")
                            fileIO(playerjson, "save", self.player)
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def showbag(self, ctx):
        """What's in the baaaag?!"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    msg = """**All inventory items**\n"""
                    msg = msg + "```"

                    msg = msg + "Bag:"
                    if len(user["inventory"]) > 0:
                        for item in user["inventory"]:
                            msg = msg + "\n" + str(user["inventory"][item]) + "x   " + item
                    else:
                        msg = msg + "\n Oooooo, such empty!\n"
                    msg = msg + "```"
                    await self.bot.say(author.mention + " " + msg)
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def clearbag(self, ctx):
        """Deletes all inventory."""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    user["inventory"] = {}
                    fileIO(playerjson, "save", self.player)
                    await self.bot.say(author.mention + " has emptied out their bag.")
                    logger.info("{} ({}) Cleared their bag.".format(author.name, author.id))

        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def stats(self, ctx, type : str, amount : int):
        """add/remove character stats
        Type Options: str|prc|knw|mvm|dpl
        Usage:
            yeadbag int 5
                This add 5 to your character's int.
            yeadbag str -2
                This removes 2 from your character's str.
        <type>:
            str = STRENGTH How well you carry, push, pull, or restrain objects.

            prc = PERCEPTION How well your senses will notice your surroundings.

            knw = KNOWLEDGE How well you know the history of a subject, or how a device works.

            mvm = MOVEMENT How well you can traverse or sneak past your surroundings.

            dpl = DIPLOMACY How well you can gain the trust in means of speech."""

        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    if type in stattype:
                        user["stats"][type] = user["stats"][type] + amount
                        await self.bot.say(author.mention + " now has " + str(user["stats"][type]) + " " + type)
                        fileIO(playerjson, "save", self.player)
                    else:
                        await self.bot.say(author.mention + " " + "Bad stat type.  Needs to be " + ", ".join([str(x) for x in stattype]) + ".")
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def showstats(self, ctx):
        """Show character stats"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    msg = """**All Stats**\n"""
                    msg = msg + "```"
                    msg = msg + "Stats:"
                    for stat in user["stats"]:
                        msg = msg + "\n" + str(stat) + " - " + str(user["stats"][stat])
                    msg = msg + "```"
                    await self.bot.say(author.mention + " " + msg)
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def clearstats(self, ctx):
        """Clear all character stats"""
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    for i in stattype:
                        user["stats"][i] = 0
                    fileIO(playerjson, "save", self.player)
                    await self.bot.say(author.mention + " All your stats are back to zero! GLHF, ya weakling!")
                    logger.info("{} ({}) Cleared their stats.".format(author.name, author.id))
        else:
            await self.bot.say(author.mention + notplaying)

    @commands.command(pass_context=True)
    async def roll(self, ctx, dice : str, stat : str=None):
        """Rolls some dice.
        Usage:
            yeadroll 3d20 mvm
                This will roll 3 different 20 sided dice and include your mvm modifier."""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                        try:
                            rolls, limit = map(int, dice.split('d'))
                        except Exception:
                            await self.bot.say('Format has to be in NdN!')
                            return
                        if stat in stattype:
                            if user["stats"][stat] < 0:
                                modifier = "\n Modifier: " + str(user["stats"][stat])
                            else:
                                modifier = "\n Modifier: +" + str(user["stats"][stat])
                            result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
                            await self.bot.say(author.mention + " rolled: " + result + modifier)
                        else:
                            await self.bot.say(author.mention + " Did not roll.  Bad stat type.  Needs to be " + ", ".join([str(x) for x in stattype]) + ". \n If you want to just roll a die, use just enter your dice in chat - `1d20`.")
        else:
            await self.bot.say(author.mention + notplaying + "\n If you want to just roll a die, use just enter your dice in chat - `1d20`.")

    @commands.command(pass_context=True)
    async def comm(self, ctx, addremove : str="read", type : str=None, *, desc : str=None):
        """Add comments to your profile.
        Usage:
            yeadcomm add smell like bacon
                This will add a comment for smell on your profile.  Where smell is: like bacon
            yeadcomm remove smell
                This will remove the smell comment.
            yeadcomm avatar https://this.is.an.img.jpeg
                This will set your image avatar to the URL provided.
            yeadcomm avatar none
                This will set your avatar back to default.
            yeadcomm read
                Running the command alone or with the option of read will read you all your comments."""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        if isplaying(author.id, self.player):
            for user in self.player:
                if user["discordID"] == author.id:
                    if "comments" not in user:
                        user["comments"] = {}
                    if addremove.lower() == "add":
                            user["comments"][type] = desc
                            await self.bot.say(author.mention + "  added " + str(type) + " comment.")
                    elif addremove.lower() == "remove":
                        if type in user["comments"]:
                            del user["comments"][type]
                            await self.bot.say(author.mention + "  deleted " + str(type) + " comment.")
                        else:
                            await self.bot.say(author.mention + " " + str(type) + " comment does not exist.  Try again.")
                    elif addremove.lower() == "read":
                        msg = " Here some comments people have made about you: \n"
                        if len(user["comments"]) > 0:
                            msg = msg + "```"
                            for key in user["comments"]:
                                msg = msg + str(key) + ": " + str(user["comments"][key] + "\n")
                            msg = msg + "```"
                        else:
                            msg = msg + "`Looks like no one has made any comments about you.  Use yeadcomm add <key> <value> to add a comment.`"
                        await self.bot.say(author.mention + msg)
                    elif addremove.lower() == "avatar":
                        # type in the if block below is now the image url instead of a comment type.
                        if type.lower() == "none":
                            user["avatar"] = author.avatar_url
                            await self.bot.say(author.mention + "'s avatar has been set to default.")
                        else:
                            user["avatar"] = type
                            await self.bot.say(author.mention + "'s avatar has been set.")
                    else:
                        await self.bot.say(author.mention + " you provided a bad action.  Use either add, remove, avatar or read (eg. `yeadcomm add height I am a very tall as hell person.`)")
                    fileIO(playerjson, "save", self.player)
        else:
            await self.bot.say(author.mention + notplaying)


    @commands.command(pass_context=True)
    async def readjson(self, ctx):
        """Checks to see who is currently the DM."""
        author = ctx.message.author
        self.player = fileIO(playerjson, "load")
        for user in self.player:
            await self.bot.say(str(user))

def isplaying(authorid, allplayers):
    if any(user["discordID"] == authorid for user in allplayers):
        return True

def check_folders():
    if not os.path.exists("data/player"):
        print("Creating data/player folder...")
        os.makedirs("data/player")

def check_files():
    f = playerjson
    if not fileIO(f, "check"):
        print("Creating empty player.json...")
        fileIO(f, "save", [])

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("player")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=playerlog, encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = YeadPlayer(bot)
    bot.add_cog(n)
