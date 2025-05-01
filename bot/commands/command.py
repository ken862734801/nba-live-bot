import logging

import twitchio
from twitchio.ext import commands

from config import Config
from services.nba import NBAService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class CommandComponent(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="commands")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def help(self, ctx: commands.Context) -> None:
        logging.info(f"[{ctx.channel.name}] - {ctx.author.name}: !commands")
        await ctx.send(f"@{ctx.author.name}, {Config.DOCUMENTATION_URL}")
    
    @commands.command(name="record")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def record(self, ctx: commands.Context) -> None:
        text = ctx.message.text.strip().split(" ", 1)
        if len(text) < 2:
            logging.warning(f"[{ctx.channel.name}] - {ctx.author.name}: !record (missing team name)")
            await ctx.send(f"@{ctx.author.name}, provide a team name.")
            return
        team_name = text[1].strip()
        logging.info(f"[{ctx.channel.name}] - {ctx.author.name}: !record {team_name}")
        await ctx.send(f"@{ctx.author.name} {NBAService.get_team_record(team_name)}")

    @commands.command(name="score")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def score(self, ctx: commands.Context) -> None:
        text = ctx.message.text.strip().split(" ", 1)
        if len(text) < 2:
            logging.warning(f"[{ctx.channel.name}] - {ctx.author.name}: !score (missing team name)")
            await ctx.send(f"@{ctx.author.name}, provide a team name.")
            return
        team_name = text[1].strip()
        logging.info(f"[{ctx.channel.name}] - {ctx.author.name}: !score {team_name}")
        await ctx.send(f"@{ctx.author.name} {NBAService.get_game_score(team_name)}")

    @commands.command(name="stats")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def boxscore(self, ctx: commands.Context) -> None:
        text = ctx.message.text.strip().split(" ", 1)
        if len(text) < 2:
            logging.warning(f"[{ctx.channel.name}] - {ctx.author.name}: !stats (missing player name)")
            await ctx.send(f"@{ctx.author.name}, provide a player name.")
            return
        player_name = text[1].strip()
        logging.info(f"[{ctx.channel.name}] - {ctx.author.name}: !stats {player_name}")
        await ctx.send(f"@{ctx.author.name} {NBAService.get_player_statline(player_name)}")
