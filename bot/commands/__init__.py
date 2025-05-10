import logging

import twitchio
from twitchio.ext import commands

from config import Config
from services.nba_service import NBAService


class CommandComponent(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _parse_message(self, ctx: commands.Context, error: str) -> str | None:
        parts = ctx.message.text.strip().split(" ", 1)
        if len(parts) < 2:
            await ctx.send(f"@{ctx.author.name}, {error}")
            return None
        return parts[1].strip()

    @commands.command(name="career")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def career(self, ctx: commands.Context) -> None:
        player = await self._parse_message(ctx, "provide a player name.")
        if player is None:
            return
        await ctx.send(f"@{ctx.author.name} {NBAService.get_player_career_averages(player)}")

    @commands.command(name="commands")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def documentation(self, ctx: commands.Context) -> None:
        await ctx.send(f"@{ctx.author.name}, {Config.DOCUMENTATION_URL}")

    @commands.command(name="record")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def record(self, ctx: commands.Context) -> None:
        team = await self._parse_message(ctx, "provide a team name.")
        if team is None:
            return
        await ctx.send(f"@{ctx.author.name} {NBAService.get_team_record(team)}")

    @commands.command(name="score")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def score(self, ctx: commands.Context) -> None:
        team = await self._parse_message(ctx, "provide a team name.")
        if team is None:
            return
        await ctx.send(f"@{ctx.author.name} {NBAService.get_game_score(team)}")

    async def statline(self, ctx: commands.Context) -> None:
        player = await self._parse_message(ctx, "provide a player name.")
        if player is None:
            return
        await ctx.send(f"@{ctx.author.name} {NBAService.get_player_statline(player)}")

    @commands.command(name="schedule")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def schedule(self, ctx: commands.Context) -> None:
        await ctx.send(f"@{ctx.author.name} {NBAService.get_schedule()}")
