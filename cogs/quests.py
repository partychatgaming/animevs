import crown_utilities
import custom_logging
import db
import messages as m
from interactions import User
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Quests(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Quests Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    @slash_command(name="quests", description="View your current quests")
    async def quests(self, ctx):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        try:
            player = crown_utilities.create_player_from_data(registered_player)
            quest_messages = []
            if player.quests:
                for quest in player.quests:
                    completed = "🟢" if quest["COMPLETED"] else "🔴"
                    quest_messages.append(f"{quest['NAME']} {quest['AMOUNT']}/{quest['COMPLETE']} - {completed}")
            embedVar = Embed(title=f"📜 Quest Board", description="\n".join(quest_messages), color=0x00ff00)
            await ctx.send(embed=embedVar)
        except Exception as ex:
            custom_logging.print_exception(ex)
            embed = Embed(title="Error", description="There was an error getting your quests", color=0xff0000)
            await ctx.send(embed=embed)

    
    async def quest_check(self, player, quest_type):
        quest_list = db.queryUser({"DID": str(player.did)})["QUESTS"]
        for quest in quest_list:
            if quest["TYPE"] == quest_type:
                amount_completed = quest["AMOUNT"]
                amount_required = quest["COMPLETE"]
                if (amount_completed + 1) == amount_required:
                    quest["COMPLETED"] = True
                    update_query = {'$inc': {'QUESTS.$[type].' + 'TYPE': 1, '$set': {'QUESTS.$[type].COMPLETED': True}}}
                    filter_query = [{'type.' + 'TYPE': quest["TYPE"]}]
                    response = db.updateUser({"DID": str(player.did)}, update_query, filter_query)
                    return True
                else:
                    update_query = {'$inc': {'QUESTS.$[type].' + 'TYPE': 1}}
                    filter_query = [{'type.' + 'TYPE': quest["TYPE"]}]
                    response = db.updateUser({"DID": str(player.did)}, update_query, filter_query)
                    return True
        return False

                    
            


def setup(bot):
    Quests(bot)