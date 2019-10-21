import random
from discord.ext import commands

class RNG():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, *choices : str):
        """Chooses between multiple choices (space delimited).
        Usage:
            yeadchoose door1 door2 "a door with a hole" death
                This will randomly make a choice between door1, door2, a door with a hole, and death."""
        await self.bot.say("The bot has made a decision!  The bot has chosen: **" + random.choice(choices) + "**")

    # @commands.command()
    # async def test(self):
    #     mess = await self.bot.say("this is a test")
    #     await self.bot.pin_message(mess)
    #     print(mess)


def setup(bot):
    bot.add_cog(RNG(bot))
