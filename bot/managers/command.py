import twitchio
from twitchio.ext import commands

from api.nba import NBAClient
from config import Config


class CommandManager(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="career")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def career(self, ctx: commands.Context, *, player: str) -> None:
        await ctx.send(f"@{ctx.author.name} {NBAClient.get_player_career(player)}")

    @commands.command(name="commands")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def documentation(self, ctx: commands.Context) -> None:
        await ctx.send(f"@{ctx.author.name}, {Config.DOCUMENTATION_URL}")

    @commands.command(name="score")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def score(self, ctx: commands.Context, *, team: str) -> None:
        await ctx.send(f"@{ctx.author.name} {NBAClient.get_game_score(team)}")

    @commands.command(name="statline")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def statline(self, ctx: commands.Context, *, player: str) -> None:
        await ctx.send(f"@{ctx.author.name} {NBAClient.get_player_statline(player)}")

    @commands.command(name="record")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def record(self, ctx: commands.Context, *, team: str) -> None:
        await ctx.send(f"@{ctx.author.name} {NBAClient.get_team_record(team)}")

    @commands.command(name="schedule")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def schedule(self, ctx: commands.Context) -> None:
        await ctx.send(f"@{ctx.author.name} {NBAClient.get_schedule()}")
