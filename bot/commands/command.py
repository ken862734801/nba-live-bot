import twitchio
from twitchio.ext import commands
from services.nba import NBAService

class CommandComponent(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        if payload.text.startswith('!'):
            print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")
    
    @commands.command(name="record")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def record(self, ctx: commands.Context) -> None:
        text = ctx.message.text.split(" ", 1)
        if len(text) < 2:
            await ctx.send(f"@{ctx.author.name}, provide a team name.")
            return
        team_name = text[1].strip()
        await ctx.send(f"@{ctx.author.name} {NBAService.get_team_record(team_name)}")

    @commands.command(name="score")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def score(self, ctx: commands.Context) -> None:
        text = ctx.message.text.split(" ", 1)
        if len(text) < 2:
            await ctx.send(f"@{ctx.author.name}, provide a team name.")
            return
        team_name = text[1].strip()
        await ctx.send(f"@{ctx.author.name} {NBAService.get_game_score(team_name)}")

    @commands.command(name="stats")
    @commands.cooldown(rate=1, per=5, key=commands.BucketType.channel)
    async def boxscore(self, ctx: commands.Context) -> None:
        text = ctx.message.text.split(" ", 1)
        if len(text) < 2:
            return
        player_name = text[1].strip()
        await ctx.send(f"@{ctx.author.name} {NBAService.get_player_statline(player_name)}")

    