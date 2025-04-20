import twitchio
from twitchio.ext import commands
from services.nba_api_service import NBAService

class CommandComponent(commands.Component):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    @commands.command(name="score")
    async def score(self, ctx: commands.Context) -> None:
        text = ctx.message.text.split(" ", 1)
        if len(text) < 2:
            await ctx.send(f"@{ctx.author.name}, provide a team name.")
            return
        team_name = text[1].strip()
        await ctx.send(f"@{ctx.author.name} {NBAService.get_game_score(team_name)}")
        
    # @commands.command(name="boxscore")
    # async def boxscore(self, ctx: commands.Context) -> None:
    #     await ctx.send("Boxscore command executed!")
    
    @commands.command(name="record")
    async def record(self, ctx: commands.Context) -> None:
        text = ctx.message.text.split(" ", 1)
        if len(text) < 2:
            await ctx.send(f"@{ctx.author.name}, provide a team name.")
            return
        team_name = text[1].strip()
        await ctx.send(f"@{ctx.author.name} {NBAService.get_team_record(team_name)}")
    
    # @commands.command(name="career")
    # async def career(self, ctx: commands.Context) -> None:
    #     await ctx.send("Career command executed!")