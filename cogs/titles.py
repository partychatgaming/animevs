import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import help_commands as h
from interactions import Client, ActionRow, Button, ButtonStyle, slash_option, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Titles(Extension):
    def __init__(self, bot):
        self.bot = bot



    @listen()
    async def on_ready(self):
        print('Titles Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Equip a Title")
    @slash_option(name="title", description="Title to equip", required=True, opt_type=OptionType.STRING)
    async def equiptitle(self, ctx, title: str):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        title_name = title
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)

        vault_query = {'DID' : str(ctx.author.id)}
        vault = db.altQueryVault(vault_query)

        resp = db.queryTitle({'TITLE': {"$regex": f"^{str(title_name)}$", "$options": "i"}})
        title_name = resp['TITLE']

        if resp:

            if title_name in vault['TITLES']:
                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': title_name}})
                await ctx.send(f"**{title_name}** has been equipped.")
            else:
                await ctx.send(m.USER_DOESNT_HAVE_THE_Title, ephemeral=True)
        else:

            if title_name in vault['TITLES']:
                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': str(title_name)}})
                await ctx.send(f"**{title_name}** has been equipped.")
            else:
                await ctx.send(m.USER_DOESNT_HAVE_THE_Title, ephemeral=True)

def setup(bot):
    Titles(bot)
    
