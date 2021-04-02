from discord.ext import commands, tasks
import discord
import datetime
import time
import sqlite3
import os
import asyncio
import requests
from discord.utils import get
from .classes.UserAccount import UserAccount

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")
print("PATH: ", db_path)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_check.start()

    async def is_server(self, ctx):
        return ctx.guild.id == 774751718754877480

    async def get_user(self, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id=?", (id,))
        return c.fetchone()


    async def create_log(self, title, name):

        embed = discord.Embed(title=title, timestamp=datetime.datetime.now(), color=0x2403fc)
        embed.add_field(name="Name", value=name)

        channel = self.bot.get_channel(789724879809019904)
        await channel.send(embed=embed)

    @tasks.loop(seconds=5.0)
    async def reminder_check(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        myGen = self.bot.get_channel(503741758564335621)

        c.execute("SELECT * FROM reminders WHERE time < ?", (int(time.time()),))
        rows = c.fetchall()

        for row in rows:
            try:
                id = row[0]
                user_id = row[1]
                reminder = row[3]
                channel_id = row[4]

                channel = self.bot.get_channel(channel_id)
                user = self.bot.get_user(user_id)

                c.execute("DELETE FROM reminders WHERE id=?", (id,))
                conn.commit()

                await channel.send(f"{user.mention} {reminder}")
            except Exception as e:
                await myGen.send(e)
                continue

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)

        game = discord.Game("with the ban command!")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = await ctx.send("You're on cooldown")
            await asyncio.sleep(2)
            await msg.delete()
        if isinstance(error, commands.MissingRequiredArgument):
            msg = f"${ctx.command}"

            for key, value in ctx.command.clean_params.items():
                msg = msg + f" <{key}>"

            await ctx.send(f"The proper command is `{msg}`")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if member.id ==344666116456710144 and after.channel == None:
                voiceClient = get(self.bot.voice_clients, guild=before.channel.guild)
                await voiceClient.disconnect()
                return
            if member.id ==344666116456710144:
                channel = after.channel
                voiceClient = get(self.bot.voice_clients, guild=channel.guild)
                if voiceClient and voiceClient.is_connected():
                    await voiceClient.move_to(channel)
                else:
                    vc = await channel.connect()
        except:
            return
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            user = UserAccount(message.author.id)
            user.add_points(len(message.content.split()))
        return


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 774751718754877480:
            channel = self.bot.get_channel(774799606889447504)
            await channel.send("{} has joined the server!".format(member.mention))

        member_account = await self.get_user(member.id)
        if member_account:
            return

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO users (user_id) VALUES (?)", (member.id,))
        conn.commit()

        return

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"joined {guild.name}")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM servers WHERE server_id=?", (guild.id,))

        if not c.fetchone():
            c.execute("INSERT INTO servers (server_id, prefix) VALUES (?,?)", (guild.id, '$',))
            conn.commit()

        for member in guild.members:
            print(member.name)

            member_account = await self.get_user(member.id)
            print(member_account)
            if not member_account == None:
                continue

            print(f"doesnt exist {member.name}")
            c.execute("INSERT INTO users (user_id) VALUES (?)", (member.id,))
            conn.commit()

        return



def setup(bot):
    bot.add_cog(Events(bot))
