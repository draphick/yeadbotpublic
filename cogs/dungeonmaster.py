import discord
from discord.ext import commands
from .dataIO import fileIO
import os
import asyncio
from datetime import datetime, timedelta
import logging

dmjson = "data/dungeonmaster/dungeonmaster.json"
dmlog = "data/dungeonmaster/dungeonmaster.log"
playerjson = "data/player/player.json"
stattype = ["str", "prc", "knw", "mvm", "dpl"]

class YeadDM:
    """The things for YEAD DM"""

    def __init__(self, bot):
        self.bot = bot
        self.dungeonmaster = fileIO(dmjson, "load")
        self.player = fileIO(playerjson, "load")

    @commands.command(pass_context=True)
    async def newday(self, ctx, numberofdays : int=None):
        """It's a new day!
        Usage:
            yeadnewday 298
                Updates the current running day to 298 and prints the new day post.
            yeadnewday
                If you run the command without a number it'll print the new day post and increment the counter by one."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        self.player = fileIO(playerjson, "load")
        self.dungeonmaster = fileIO(dmjson, "load")
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                playerIDs = []
                if numberofdays:
                    dm["Day"] = numberofdays
                else:
                    dm["Day"] = dm["Day"] + 1
                for userID in self.dungeonmaster:
                    dmID = "<@" + userID["DungeonMaster"] + ">"
                    howmanydays = str(userID["Day"])
                for playersID in self.player:
                    playerIDs.append("<@" + playersID["discordID"] + ">")
                totalplayers = len(playerIDs)
                msg = "Welcome to TARP, a Text Action Role Playing game, "
                msg = msg + "where the rolls don't matter and the stats mean squat!\nYour DM today is:\n"
                msg = msg + dmID
                msg = msg + "\nIn this week's campaign we have " + str(totalplayers) + " player(s):"
                msg = msg + "\n" + "\n".join([str(x) for x in playerIDs])
                msg = msg + "\n We have been running TARP now for **" + howmanydays + "** days. Let's see what they get into today!"
                messagetopin = await self.bot.say(msg)
                await self.bot.pin_message(messagetopin)
                fileIO(dmjson, "save", self.dungeonmaster)
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmxp(self, ctx, changeuser : discord.User, amount : int=None):
        """The DM has the ability to add/remove XP from a player.  The player cannot.
        Usage:
            yeaddmxp @playername 100
                This will add 100 experience points to this character
            yeaddmxp @playername -100
                This will subtract 100 experience points from this character
        Note: Total max xp is 1000, if that number is breached the user will gain a level.
        Note: Players can also lose a level if their current XP value is negative."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        self.player = fileIO(playerjson, "load")
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                for user in self.player:
                    if user["discordID"] == changeuser.id:
                        if amount == None:
                            totpercent = 100 * float(user["xpcurrent"])/float(user["xpmax"])
                            await self.bot.say("<@" + changeuser.id + ">" + " is currently level " + str(user["level"]) + " at " + str(totpercent) + "% of their current level (" + str(user["xpcurrent"]) + "/" + str(user["xpmax"]) + ").")
                        else:
                            if "level" not in user:
                                user["level"] = 1
                                user["xpcurrent"] = 0
                                user["xpmax"] = 1000
                            xp, level, totpercent = addmyxp(user["xpcurrent"], amount, user["xpmax"], user["level"])
                            user["level"] = level
                            user["xpcurrent"] = xp
                            fileIO(playerjson, "save", self.player)
                            await self.bot.say("<@" + changeuser.id + ">" + " is currently level " + str(user["level"]) + " at " + str(totpercent) + "% of their current level (" + str(user["xpcurrent"]) + "/" + str(user["xpmax"]) + ").")
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmstats(self, ctx, changeuser : discord.User, type : str, amount : int):
        """The DM can update player stats
        Usage:
            yeaddmbag @discordname int 5
                This adds 5 to @discordname's character's int.
            yeaddmbag @discordname str -2
                This removes 2 from @discordname's character's str."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        self.player = fileIO(playerjson, "load")
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                for user in self.player:
                    if user["discordID"] == changeuser.id:
                        if type in stattype:
                            user["stats"][type] = user["stats"][type] + amount
                            await self.bot.say(str(user["playerName"]) + "'s stats updated and now has " + str(user["stats"][type]) + " " + type)
                            fileIO(playerjson, "save", self.player)
                        else:
                            await self.bot.say(author.mention + " " + "Bad stat type.  Needs to be " + ", ".join([str(x) for x in stattype]) + ".")
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmbag(self, ctx, changeuser : discord.User, newitem : str, amount : int):
        """The DM can update player bag.
        Usage:
            yeaddmbag @discordname toys 5
                This add 5 toys to @discordname's inventory.
            yeaddmbag @discordname -2
                This removes 2 toys from @discordname's inventory."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        self.player = fileIO(playerjson, "load")
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                for user in self.player:
                    if user["discordID"] == changeuser.id:
                        if newitem in user["inventory"]:
                            user["inventory"][newitem] = user["inventory"][newitem] + amount
                            if user["inventory"][newitem] < 1:
                                del user["inventory"][newitem]
                                await self.bot.say(str(user["playerName"]) + " now has less than 1 " + newitem + ".  It is being deleted from their inventory.")
                            else:
                                await self.bot.say(str(user["playerName"]) + ": " + str(amount) + " to " + newitem + " in their inventory.")
                            fileIO(playerjson, "save", self.player)
                        else:
                            if amount < 1:
                                await self.bot.say("Can't remove items because " + str(user["playerName"]) + " doesn't have " + newitem + ".")
                            else:
                                user["inventory"][newitem] = amount
                                await self.bot.say(str(user["playerName"]) + ": " + str(amount) + " " + newitem + " to their inventory.")
                                fileIO(playerjson, "save", self.player)
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def whodm(self, ctx):
        """Checks to see who is currently the DM."""
        author = ctx.message.author
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                await self.bot.say("You are already the DM, " + author.mention)
            else:
                dmis = "<@" + str(dm["DungeonMaster"]) + ">"
                await self.bot.say(dmis + " is the DM.")

    @commands.command(pass_context=True)
    async def imdm(self, ctx):
        """Setup the DM for this campaign."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        if any(user for user in self.dungeonmaster):
            for dm in self.dungeonmaster:
                if dm["DungeonMaster"] == author.id:
                    await self.bot.say(author.mention + " is already the DM ")
                else:
                    # self.dungeonmaster.remove(dm)
                    dm["DungeonMaster"] = author.id
                    dm["Wait"] = "N"
                    dm["ChannelID"] = channel
                    dm["Day"] = dm["Day"]
                    # self.dungeonmaster.append({"DungeonMaster" : author.id, "Wait" : "N", "ChannelID" : channel})
                    logger.info("{} ({}) set themselves as DM.".format(author.name, author.id))
                    await self.bot.say(author.mention + " is the new DM.")
                    fileIO(dmjson, "save", self.dungeonmaster)
        else:
            self.dungeonmaster.append({"DungeonMaster" : author.id, "Wait" : "N", "ChannelID" : channel})
            logger.info("{} ({}) set themselves as DM.".format(author.name, author.id))
            await self.bot.say("No DM assigned. " + author.mention + " is now the DM.")
            fileIO(dmjson, "save", self.dungeonmaster)

    @commands.command(pass_context=True)
    async def stop(self, ctx):
        """Stops everyone from posting.  It will check in every 5 seconds to delete."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                dm["Wait"] = "Y"
                dm["ChannelID"] = channel
                timeago = datetime.utcnow()
                dm["datetime"] = str(timeago)
                fileIO(dmjson, "save", self.dungeonmaster)
                await self.bot.send_message(discord.Object(id=dm["ChannelID"]), author.mention + " placed a hold on chat until they are ready.")
                await self.bot.delete_message(ctx.message)
                logger.info("{} ({}) placed a hold on chat.".format(author.name, author.id))
                while dm["Wait"] == "Y":
                    for wait in self.dungeonmaster:
                        if wait["Wait"] == "Y":
                            async for messagelog in self.bot.logs_from(discord.Object(id=dm["ChannelID"]), after=timeago):
                                if messagelog.author != author and messagelog.author != self.bot.user:
                                    await self.bot.delete_message(messagelog)

                    await asyncio.sleep(5)

            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")
    @commands.command(pass_context=True)
    async def go(self, ctx):
        """Let's people start posting again."""
        author = ctx.message.author
        channel = ctx.message.channel.id
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                dm["Wait"] = "N"
                dm["ChannelID"] = channel
                fileIO(dmjson, "save", self.dungeonmaster)
                await self.bot.send_message(discord.Object(id=dm["ChannelID"]), author.mention + " lifted the hold on chat.")
                await self.bot.delete_message(ctx.message)
                logger.info("{} ({}) lifted a hold on chat.".format(author.name, author.id))
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmshowstats(self, ctx, changeuser : discord.User=None):
        """Show character stats"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                if changeuser:
                    for user in self.player:
                        if user["discordID"] == changeuser.id:
                            msg = """**All Stats**\n"""
                            msg = msg + "```"
                            msg = msg + "Stats:"
                            for stat in user["stats"]:
                                msg = msg + "\n" + str(stat) + " - " + str(user["stats"][stat])
                            msg = msg + "```"
                            await self.bot.say(str(user["playerName"]) + " " + msg)
                else:
                    for user in self.player:
                        msg = """**All Stats**\n"""
                        msg = msg + "```"
                        msg = msg + "Stats:"
                        for stat in user["stats"]:
                            msg = msg + "\n" + str(stat) + " - " + str(user["stats"][stat])
                        msg = msg + "```"
                        await self.bot.say(str(user["playerName"]) + " " + msg)
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmshowbag(self, ctx, changeuser : discord.User=None):
        """Show character bags"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                if changeuser:
                    for user in self.player:
                        if user["discordID"] == changeuser.id:
                            msg = """**Bags**\n"""
                            msg = msg + "```"
                            msg = msg + "Bag:"
                            if len(user["inventory"]) > 0:
                                for item in user["inventory"]:
                                    msg = msg + "\n" + str(user["inventory"][item]) + "x   " + item
                            else:
                                msg = msg + "\n Oooooo, such empty!\n"
                            msg = msg + "```"
                            await self.bot.say(str(user["playerName"]) + " " + msg)
                else:
                    for user in self.player:
                        msg = """**Bags**\n"""
                        msg = msg + "```"
                        msg = msg + "Bag:"
                        if len(user["inventory"]) > 0:
                            for item in user["inventory"]:
                                msg = msg + "\n" + str(user["inventory"][item]) + "x   " + item
                        else:
                            msg = msg + "\n Oooooo, such empty!\n"
                        msg = msg + "```"
                        await self.bot.say(str(user["playerName"]) + " " + msg)
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmwho(self, ctx):
        """Show all character things"""
        self.player = fileIO(playerjson, "load")
        author = ctx.message.author
        channel = ctx.message.channel.id
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                for user in self.player:
                    msg = "**" + str(user["playerName"]) + "**" + " Details: \n"
                    msg = msg + "```Bag:"
                    if len(user["inventory"]) > 0:
                        for item in user["inventory"]:
                            msg = msg + "\n" + str(user["inventory"][item]) + "x   " + item
                    else:
                        msg = msg + "\n Oooooo, such empty!\n"
                    msg = msg + "```"
                    msg = msg + "```"
                    msg = msg + "Stats:"
                    for stat in user["stats"]:
                        msg = msg + "\n" + str(stat) + " - " + str(user["stats"][stat])
                    msg = msg + "```\n\n"
                    await self.bot.say(msg)
            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

    @commands.command(pass_context=True)
    async def dmreadjson(self, ctx):
        """Checks to see who is currently the DM."""
        author = ctx.message.author
        for dm in self.dungeonmaster:
            if dm["DungeonMaster"] == author.id:
                print(dm)
                await self.bot.say(str(dm))

            else:
                await self.bot.say(author.mention + " is not the DM and cannot perform his action.")

def addmyxp(oldxp, newxp, maxxp, level):
    xp = oldxp + newxp
    if xp > maxxp:
        while xp > maxxp:
            level = level + 1
            xp = xp - maxxp
    elif xp < 0:
        while xp < 0:
            level = level - 1
            xp = maxxp + xp
    totpercent = 100 * float(xp)/float(maxxp)
    return xp, level, totpercent

def check_folders():
    if not os.path.exists("data/dungeonmaster"):
        print("Creating data/dungeonmaster folder...")
        os.makedirs("data/dungeonmaster")

def check_files():
    f = dmjson
    if not fileIO(f, "check"):
        print("Creating empty dungeonmaster.json...")
        fileIO(f, "save", [])

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("dungeonmaster")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename=dmlog, encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = YeadDM(bot)
    bot.add_cog(n)
