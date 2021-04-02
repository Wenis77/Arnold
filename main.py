import discord
from cogs.lib import get_value
import sqlite3
import os
from discord.ext import commands

#Absolute path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "cogs/db.db")

#Put your token in hidden.json
token = get_value("token")

#Allows all intents, you may want to change this for your own uses
intents = discord.Intents().all()

#Files in cogs that should be ignored on initial loading
ignore_list = ["lib.py"]

#ToDo: FIX THE HARD CODED PATHS MAKE THEM FLEXIBLE!!!!


#==============GETS SERVER SPECIFIC PREFIX==============
def get_prefix(bot, message):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT prefix FROM servers WHERE server_id=?", (message.guild.id,))
        result = c.fetchone()

        if result:
            return result[0]
        else:
            return '$'

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

#Loads the cogs
if __name__ == '__main__':
    path = os.path.abspath("./cogs/")
    for file in os.listdir(path):
        if file.endswith(".py") and file not in ignore_list:
            bot.load_extension(f"cogs.{file[:-3]}")
            print("Loaded: {}".format(file))


bot.run(token, reconnect=True)
