import discord
import asyncio
import datetime
import sqlite3
import berserk
import chess
import chess.pgn
import chess.svg
import os
import io
from cairosvg import svg2png
from discord.ext import commands
from discord.utils import get
from .lib import check_block, get_id, has_administrator, get_value

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        session = berserk.TokenSession(get_value("lichess-token"))
        self.client = berserk.Client(session=session)

    async def not_blocked(ctx):
        return check_block(ctx.author.id, ctx.command.name)

    def create_pgn(self, moves):
        pgn = io.StringIO(moves)
        game = chess.pgn.read_game(pgn)
        board = game.board()

        for move in game.mainline_moves():
            board.push(move)

        return board

    def create_svg(board):
        svg_file = chess.svg.board(board)

    async def stream_game(self, id, ctx):
        loop_count = 0
        while True:
            await asyncio.sleep(5)
            if loop_count == 30:
                break
            loop_count += 1
            print(1)
            try:
                live_game = self.client.board.stream_game_state(id)
                next(live_game)
            except Exception as e:
                print(12, e)
                continue

            board_msg = discord.Message
            try:
                for event in live_game:

                    print(3)
                    moves = ""
                    try:
                        moves = event["moves"]
                        print(moves)
                    except:
                        moves = event["state"]["moves"]
                        print("here")
                        print(moves)
                    print(4)
                    board = self.create_pgn(moves)
                    svg_file = chess.svg.board(board, lastmove=board.peek())
                    b = io.BytesIO(svg2png(bytestring=svg_file))

                    try:
                        await board_msg.delete()
                    except:
                        pass
                    board_msg = await ctx.send(file=discord.File(b, "chess.png"))


            except Exception as e:
                print(e)

    @commands.group(pass_context=True)
    @commands.check(not_blocked)
    async def game(self, ctx):
        return

    @game.command(pass_context=True)
    async def create(self, ctx, time=None, increment=None):
        loop_count = 0


        challenge = self.client.challenges.create_open(clock_limit=time, clock_increment=increment)
        msg = await ctx.send(challenge["challenge"]["url"])
        try:
            await self.stream_game(challenge["challenge"]["id"], ctx.channel)
        except Exception as e:
            print(e)






def setup(bot):
    bot.add_cog(Chess(bot))
