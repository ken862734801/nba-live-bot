import logging
from twitchio.ext import commands
from api.nba import NBAClient
from config import Config

logger = logging.getLogger(__name__)

class CommandManager(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def handler(self, ctx: commands.Context, message: str):
        await ctx.send(message)
        try:
            await self.bot.database_manager.increment_command_count(
                ctx.channel.id,
                ctx.command.name,
            )
        except Exception as e:
            logger.error(
                f"Failed to increment command count for {ctx.command.name}: {e}"
            )

    @commands.command(name="career")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def career(self, ctx: commands.Context, *, player: str):
        response = NBAClient.get_player_career(player)
        await self.handler(ctx, f"@{ctx.author.name} {response}")

    @commands.command(name="commands")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def documentation(self, ctx: commands.Context):
        await self.handler(
            ctx,
            f"@{ctx.author.name}, {Config.DOCUMENTATION_URL}"
        )

    @commands.command(name="score")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def score(self, ctx: commands.Context, *, team: str):
        response = NBAClient.get_game_score(team)
        await self.handler(ctx, f"@{ctx.author.name} {response}")

    @commands.command(name="statline")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def statline(self, ctx: commands.Context, *, player: str):
        response = NBAClient.get_player_statline(player)
        await self.handler(ctx, f"@{ctx.author.name} {response}")

    @commands.command(name="record")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def record(self, ctx: commands.Context, *, team: str):
        response = NBAClient.get_team_record(team)
        await self.handler(ctx, f"@{ctx.author.name} {response}")

    @commands.command(name="schedule")
    @commands.cooldown(rate=1, per=10, key=commands.BucketType.channel)
    async def schedule(self, ctx: commands.Context):
        response = f"@{ctx.author.name} {NBAClient.get_schedule()}"
        await self.handler(ctx, response)
