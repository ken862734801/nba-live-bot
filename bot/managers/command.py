import twitchio
from twitchio.ext import commands

from api.nba import NBAClient
from config import Config


class CommandManager(commands.Component):
    def __init__(self, bot: commands.Bot, nba_client: NBAClient):
        self.bot = bot
        self.nba_client = nba_client

    @commands.command(name="career")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def career(self, ctx: commands.Context, *, player: str) -> None:
        response = await self.nba_client.get_player_career(player)
        await ctx.send(f"@{ctx.author.name} {response}")

    @commands.command(name="commands")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def documentation(self, ctx: commands.Context) -> None:
        await ctx.send(f"@{ctx.author.name}, {Config.DOCUMENTATION_URL}")

    @commands.command(name="score")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def score(self, ctx: commands.Context, *, team: str) -> None:
        response = await self.nba_client.get_game_score(team)
        await ctx.send(f"@{ctx.author.name} {response}")

    @commands.command(name="statline")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def statline(self, ctx: commands.Context, *, player: str) -> None:
        response = await self.nba_client.get_player_statline(player)
        await ctx.send(f"@{ctx.author.name} {response}")

    @commands.command(name="record")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def record(self, ctx: commands.Context, *, team: str) -> None:
        response = await self.nba_client.get_team_record(team)
        await ctx.send(f"@{ctx.author.name} {response}")

    @commands.command(name="schedule")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def schedule(self, ctx: commands.Context) -> None:
        response = await self.nba_client.get_schedule()
        await ctx.send(f"@{ctx.author.name} {response}")
