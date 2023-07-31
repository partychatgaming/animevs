import crown_utilities
import db
import messages as m
from interactions import User
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Hall(Extension):
    def __init__(self, bot):
        self.bot = bot



    @listen()
    async def on_ready(self):
        print('Hall Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Buy a Hall for your guild")
    async def buyhall(self, ctx, hall: str):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        hall_name = hall
        leadername = str(ctx.author.id)
        user_query = {'DID' : leadername}
        leader_info = db.queryUser(user_query)
        guildname = leader_info['GUILD']
        if guildname == 'PCG':
            await ctx.send(m.NOT_LEADER, delete_after=5)
            return
        guild_query = {'GNAME' : guildname}
        guild = db.queryGuildAlt(guild_query)
        hall = db.queryHall({'HALL': {"$regex": f"^{str(hall)}$", "$options": "i"}})
        currentBalance = guild['BANK']
        cost = hall['PRICE']
        hall_name = hall['HALL']
        if hall:
            if hall_name in guild['HALL']:
                await ctx.send(m.USERS_ALREADY_HAS_HALL, delete_after=5)
            else:
                newBalance = currentBalance - cost
                if newBalance < 0 :
                    await ctx.send("You have an insufficent Balance")
                else:
                    await crown_utilities.curseguild(cost, str(guildname))
                    response = db.updateGuildAlt(guild_query,{'$set':{'HALL': str(hall_name)}})
                    await ctx.send(m.PURCHASE_COMPLETE_H + "Enjoy your new Hall!")
                    return
        else:
            await ctx.send(m.HALL_DOESNT_EXIST)

def setup(bot):
    Hall(bot)