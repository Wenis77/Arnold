import discord
import asyncio
import datetime
import sqlite3
import os
from discord.ext import commands
from discord.utils import get
from .lib import check_block, get_id, has_moderator, has_administrator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_log(self, moderator: discord.Member, user: discord.Member, command, reason):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        date = datetime.datetime.now()

        c.execute("INSERT INTO logs (user_id, moderator_id, action, reason, date) VALUES (?,?,?,?, ?)", (user.id, moderator.id, command, reason, date,))
        conn.commit()

        #image = user.avatar_url
        #embed = discord.Embed(title=command, timestamp=date, color=0x2403fc)
        #embed.set_thumbnail(url=image)
        #embed.add_field(name="Moderator", value=moderator, inline=True)
        #embed.add_field(name="User", value=user, inline=True)
        #embed.add_field(name="Reason", value=reason, inline=False)


        #channel = self.bot.get_channel(789724879809019904)
        #await channel.send(embed=embed)



    def get_length(self, textTime):
        textTime = textTime.lower()
        milliseconds = 0

        if textTime.find("d") != -1:
            intTime = textTime.replace("d","")
            intTime = int(intTime)
            milliseconds = 86400 * (int(intTime))

        elif textTime.find("h") != -1:
            intTime = textTime.replace("h","")
            intTime = int(intTime)
            milliseconds = milliseconds + 3600 * (int(intTime))

        elif textTime.find("m") != -1:
            intTime = textTime.replace("m","")
            intTime = int(intTime)
            milliseconds = 60  * (intTime)

        return milliseconds

    async def not_blocked(ctx):
        return check_block(ctx.author.id, ctx.command.name)
        #85,579

    @commands.command(name="purge")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def purge(self, ctx, amount: int):
        if amount <= 100:
            await ctx.channel.purge(limit=amount+1, bulk=True)
            msg = await ctx.send("Purged {}".format(amount))
            await asyncio.sleep(2)
            await msg.delete()
            return
        msg = await ctx.send("Purge limit is 100")
        await asyncio.sleep(2)
        await msg.delete()

    @commands.command(name="rapsheet")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def rapsheet(self, ctx, user):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            user_id = int(user)

        except:
            try:
                user_id=ctx.message.mentions[0].id
            except:
                await ctx.send("You need to mention the user or type their id")
                return
        try:
            user = self.bot.get_user(user_id)
            image = user.avatar_url

            embed = discord.Embed(title="Rapsheet for {}".format(user.name), color=0x2403fc)

            embed.set_thumbnail(url=image)
        except:
            embed = discord.Embed(title="Rapsheet for {}".format(user), color=0x2403fc)

        c.execute("SELECT * FROM logs WHERE user_id=?", (user_id,))
        rows = c.fetchall()

        if not rows:
            await ctx.send("That user has no infractions")
            return

        for x in range(5):
            row = rows[x]
            moderator = self.bot.get_user(row[2])
            action = row[3]
            date = row[4]
            reason = row[5]
            embed.add_field(name=row[3], value="Moderator: {}\nReason: {}\nDate: {}".format(moderator.name, reason, date), inline=False)
        embed.add_field(name="Account Created", value=user.created_at, inline=False)
        embed.set_footer(text="Total Infractions: {}".format(len(rows)))

        await ctx.send(embed=embed)

    @commands.command("poll")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def poll(self, ctx, question, timeLimit):
        yes_count = 0
        no_count = 0
        winner = ""

        await ctx.message.delete()
        origMsg = await ctx.send("**NEW Poll**\n*Open for {} seconds*\n\n**QUESTION**: {}".format(timeLimit, question))
        origMsg = discord.utils.get(self.bot.cached_messages, id=origMsg.id)

        await origMsg.add_reaction("✅")
        await origMsg.add_reaction("❌")

        await asyncio.sleep(int(timeLimit))

        for reaction in origMsg.reactions:
            if str(reaction.emoji) == "✅":
                yes_count = reaction.count
            elif str(reaction.emoji) == "❌":
                no_count = reaction.count

        if yes_count > no_count:
            winner = "Yes"
        elif no_count > yes_count:
            winner = "No"
        else:
            winner = "Tied"

        await origMsg.edit(content="**NEW Poll**\n*Closed*\n\n**QUESTION**: {}\n**WINNER**: {}".format(question, winner))
        return

    @commands.command(name="mute")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def mute(self, ctx, member: discord.Member, length, *, reason):
        try:
            role_id = await get_id(ctx.guild, "Mute")
            role = get(member.guild.roles, id=role_id)

            await member.add_roles(role, reason=reason, atomic=True)

            await ctx.message.delete()
            await ctx.send("{} has been muted for {}".format(member.mention, length))

            await asyncio.sleep(self.get_length(length))

            await member.remove_roles(role, reason = "time's up ")
        except Exception as e:
            await ctx.send(e)
        #await create_log(ctx.author.id, member.id, ctx.invoked_subcommand, reason)


    @commands.command(name="unmute")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def unmute(self, ctx, member: discord.Member):
        role_id = await get_id(ctx.guild, "Mute")
        role = get(member.guild.roles, id=role_id)

        await member.remove_roles(role, reason = "time's up ")

        await ctx.send("<@{}> has been unmuted!".format(member.id))

        #await create_log(ctx.author.id, member.id, ctx.invoked_subcommand, "unmuted")


    @commands.command(name="ban")
    @commands.check(has_administrator)
    @commands.check(not_blocked)
    async def ban(self, ctx, member: discord.Member, speed, *, reason):
        if member.id == 344666116456710144:
            await ctx.send("you cant ban my master <:OB_pogO:737105405976772680>")
            return
        if speed == "slow":
            await ctx.send("DRUMROLLLLL PLEASE.... <@{}> is being banned!".format(member.id))
            await ctx.send("Banning <@{}> in: ".format(member.id))
            for x in reversed(range(1, 6)):
                await asyncio.sleep(1)
                await ctx.send(str(x))
        await member.ban(reason=reason)
        #await create_log(ctx.author.id, member.id, ctx.invoked_subcommand, reason)

        await ctx.send("<a:OB_pogfish:776527819093180466> <a:OB_pogfish:776527819093180466> <a:OB_pogfish:776527819093180466> {} is banned! <a:OB_pogfish:776527819093180466> <a:OB_pogfish:776527819093180466> <a:OB_pogfish:776527819093180466>".format(member.name))

    @commands.command(name="dungeon")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def dungeon(self, ctx, member: discord.Member, *, reason):
        role_id = await get_id(ctx.guild, "Dungeon")
        role = get(member.guild.roles, id=role_id)

        await member.add_roles(role, reason=reason, atomic=True)

        await ctx.message.delete()
        await ctx.send("{} has been dungeoned".format(member.mention))

        #await create_log(ctx.author.id, member.id, ctx.invoked_subcommand, reason)


    @commands.command(name="release")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def release(self, ctx, member: discord.Member):
        role_id = await get_id(ctx.guild, "Dungeon")
        role = get(member.guild.roles, id=role_id)

        await member.remove_roles(role, reason = "released")

        await ctx.send("<@{}> has been released!".format(member.id))

        #await create_log(ctx.author.id, member.id, ctx.invoked_subcommand, "released")


def setup(bot):
    bot.add_cog(ModerationCog(bot))
