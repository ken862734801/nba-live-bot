from twitchio.ext import commands
from services.nba_api_service import NBAService

class CoreCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="record")
    async def get_record(self, ctx: commands.Context):
        response = await NBAService.get_team_record("LAL")
        await ctx.send(response)
    
    @commands.command(name="score")
    async def get_score(self, ctx: commands.Context):
        response = await NBAService.get_game_score("LAL")
        await ctx.send(response)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(CoreCommands(bot))
