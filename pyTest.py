# Work with Python 3.6
import discord
import requests
import urllib3
import json
import random
urllib3.disable_warnings()

readthis = [
    {
        "discordID" : "333",
        "inventory" : [],
        "playerName" : "raph the wizard"
    },
    {
        "discordID" : "253425146738638849",
        "inventory" : [
            {
                "toy" : 1,
            },
            {
                "toy2" : 5
            }
        ],
        "playerName" : "raph is raph"
    }
]

words = "here is a string of words"
newname = " ".join([i.capitalize() for i in words.split()])
print(newname)
 # print(i.capitalize())
# print(words.capitalize())

# def getPlayer(discordID, allplayers):
#     alldata = [user for user in allplayers if user['discordID'] == discordID]
#     return alldata[0]
#
# thing = getPlayer("25342514673863884999999", readthis)
# print(thing["playerName"])
# print(readthis)
# for user in readthis:
#     if user["discordID"] == "253425146738638849":
#         # user["inventory"]["newtoy"] = 5
#         for item in user["inventory"]:
#             item["toy"] = 5
#             print(item)































            ###
