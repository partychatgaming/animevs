import custom_logging
from cogs.classes.custom_paginator import CustomPaginator
import db
import time
import classes as data
import messages as m
from bson.int64 import Int64
import textwrap
from logger import loggy
import textwrap
import unique_traits as ut
now = time.asctime()
import asyncio
import uuid
from interactions import ActionRow, Button, ButtonStyle, listen, slash_command, Embed, Extension
import crown_utilities

emojis = ['👍', '👎']

class Register(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        loggy.info('Register cog is ready')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
    
    @slash_command(description="Register for Anime VS+", scopes=crown_utilities.guild_ids)
    async def register(self, ctx):
        await ctx.defer()
        server_created = db.queryServer({"GNAME": str(ctx.author.guild)})
        if db.queryUser({"DID": str(ctx.author.id)}):
            await ctx.send(f"{ctx.author.mention} You already have a Anime VS+ Account!")
            return 

        else:
            disname = str(ctx.author)
            did = str(ctx.author.id)
            name = disname.split("#",1)[0]
            is_admin = False
            is_creator = False
            admin_did = ['339423274117103617','306429381948211210','570660973640286211','263564778914578432']
            if did in admin_did:
                is_admin = True
                is_creator = True
            summon_info = {
                "NAME": "Chick",
                "LVL": 1,
                "EXP": 0,
                "Peck": 100,
                "TYPE": "PHYSICAL",
                "BOND": 0,
                "BONDEXP": 0,
                "PATH": "https://res.cloudinary.com/dkcmq8o15/image/upload/v1638814575/Pets/CHICK.png"
            }
            user = {
                'DISNAME': disname, 
                'NAME': name, 
                'DID': did, 
                'AVATAR': str(ctx.author.avatar_url), 
                'SERVER': str(ctx.author.guild), 
                'FAMILY': did,
                'FAMILY_DID': did,
                'BALANCE': Int64(100000),
                'IS_ADMIN': is_admin,
                'CREATOR': is_creator,
            }
            r_response = db.createUsers(data.newUser(user))

            if not server_created:
                create_server_query = {'GNAME': str(ctx.author.guild.name)}
                created_server = db.createServer(data.newServer(create_server_query))
                server_query = {'GNAME': str(ctx.author.guild)}
                update_server_query = {
                    '$inc': {'SERVER_BALANCE': 10000},
                    '$addToSet': {'SERVER_PLAYERS': str(ctx.author.id)}
                }
                updated_server = db.updateServer(server_query, update_server_query)


        if r_response:
            try:
                _uuid = str(uuid.uuid4())
                accept_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="Continue",
                        custom_id=f"{_uuid}|yes"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="End Registration Here",
                        custom_id=f"{_uuid}|no"
                    )
                ]

                embed = Embed(title="🆚 Anime VS+ Registration", description="Collect your favorite anime and video game characters, incredible items and unique summons to dominate the multiverse.", color=0x7289da)

                action_row = ActionRow(*accept_buttons)

                message = await ctx.send(embed=embed, components=[action_row])

                def check(component: Button):
                    return str(component.ctx.author.id) == str(ctx.author.id)

                try:
                    button_ctx = await self.bot.wait_for_component(components=[action_row], check=check, timeout=120)
                    # await button_ctx.ctx.defer()

                    if button_ctx.ctx.custom_id == f"{_uuid}|no":
                        embed = Embed(title="Anime VS+ Registration", description="Your registration has been cancelled.", color=0x7289da)
                        await message.edit(components=[], embed=embed)
                        return

                    if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                        await message.edit(components=[], embed=embed)
                        universe_data = db.queryAllUniverse()
                        universe_embed_list = []
                        for uni in universe_data:
                            available = ""
                            if uni['HAS_CROWN_TALES'] == True:
                                traits = ut.formatted_traits
                                mytrait = {}
                                traitmessage = ''
                                o_show = uni['TITLE']
                                universe = o_show
                                for trait in traits:
                                    if trait['NAME'] == o_show:
                                        mytrait = trait
                                    if o_show == 'Pokemon':
                                        if trait['NAME'] == 'Pokemon':
                                            mytrait = trait
                                if mytrait:
                                    traitmessage =f"*{mytrait['EFFECT']}*"
                                available =f"{crown_utilities.crest_dict[uni['TITLE']]}"
                                
                                embedVar = Embed(title=f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
                                **{available}** Select A Starting Universe!
                                Select a universe to earn *3* 🎴 Cards and 🦾 Arms to begin! 

                                [ℹ️]__Don't overthink it!__
                                *You can always earn cards, arms, titles and more from all universes later!*

                                """))
                                embedVar.add_field(name="♾️ | Unique Universe Trait", value=f"{traitmessage}")
                                embedVar.set_image(url=uni['PATH'])
                                embedVar.set_footer(text="You can earn items in all universes! This is just a starting point!")
                                universe_embed_list.append(embedVar)
                            
                    paginator = CustomPaginator.create_from_embeds(self.bot, *universe_embed_list, custom_buttons=["Register"], paginator_type="Register")
                    paginator.show_select_menu = True
                    await paginator.send(ctx)
                
                except asyncio.TimeoutError:
                    await message.edit(components=[], embed=embed, content="You took too long to respond.")
                    await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
                    db.deleteUser({"DID": str(ctx.author.id)})
                    return

            except Exception as ex:
                custom_logging.debug(ex)
                await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
                
        else:
            db.deleteUser(str(ctx.author.id))
            await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)


    @slash_command(description="Delete your account")
    async def deleteaccount(self, ctx):
        _uuid = uuid.uuid4()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            await ctx.send("You are not registered. Please register with /register")
        
        player = crown_utilities.create_player_from_data(a_registered_player)
        accept_buttons = [
            Button(
                style=ButtonStyle.GREEN,
                label="Yes",
                custom_id=f"{_uuid}|yes"
            ),
            Button(
                style=ButtonStyle.BLUE,
                label="No",
                custom_id=f"{_uuid}|no"
            )
        ]
        accept_buttons_action_row = ActionRow(*accept_buttons)

        team = db.queryTeam({'TEAM_NAME': player.guild.lower()})

        msg = await ctx.send(f"{ctx.author.mention}, are you sure you want to delete your account?", components=[accept_buttons_action_row])

        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author

        try:
            button_ctx = await self.bot.wait_for_component(components=[accept_buttons_action_row], timeout=300, check=check)

            if button_ctx.ctx.custom_id == f"{_uuid}|no":
                embed = Embed(title="Account Not Deleted", description="Your account has not been deleted.", color=0x00ff00)
                await button_ctx.ctx.send(embed=[embed])
                return

            if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                loggy.info(f"Delete account command executed by {ctx.author}")
                delete_user_resp = db.deleteUser(player.did)
                if player.guild != "PCG":
                    transaction_message = f"{player.did} left the game."
                    team_query = {'TEAM_NAME': player.guild}
                    new_value_query = {
                        '$pull': {
                            'MEMBERS': player.did,
                            'OFFICERS': player.did,
                            'CAPTAINS': player.did,
                        },
                        '$addToSet': {'TRANSACTIONS': transaction_message},
                        '$inc': {'MEMBER_COUNT': -1}
                        }
                    response = db.deleteTeamMember(team_query, new_value_query, str(ctx.author.id))
                market_items = db.queryAllMarketByParam({'ITEM_OWNER': player.did})
                if market_items:
                    for market_item in market_items:
                        db.deleteMarketEntry({"ITEM_OWNER": player.did, "MARKET_CODE": market_item['MARKET_CODE']})
                embed = Embed(title="Account Deleted", description="Your account has been deleted. Thank you for playing!", color=0x00ff00)
                await button_ctx.ctx.send(embed=embed)
        except Exception as ex:
            loggy.critical(ex)
            custom_logging.debud(ex)
            embed = Embed(title="Error", description="Something went wrong. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)


# # Update Later
# @slash_command(name="rebirth", description="Rebirth for permanent buffs", scopes=crown_utilities.guild_ids)
# async def rebirth(ctx):
#    query = {'DID': str(ctx.author.id)}
#    user_is_validated = db.queryUser(query)
#    try:
#       if user_is_validated:
#          rLevel = user_is_validated['REBIRTH']
#          pLevel = user_is_validated['PRESTIGE']
         
         
#          rebirthCost = round(100000000 * (1 + (1.5 * (rLevel))))
#          pReq = 100 - (pLevel * 10)
#          picon = crown_utilities.prestige_icon(pLevel)
         
#          pursemessage = " "
#          gabes_purse = user_is_validated['TOURNAMENT_WINS']
#          if gabes_purse == 1:
#             pursemessage = ":purse: | Gabe's Purse Activated! All Items Will Be Retained! *You will not be able to select a new starting universe!*"
         
         
         
#          if (rLevel > 4 and rLevel <10) and pLevel < (rLevel - 4):
#             embedVar1 = Embed(title=f"❤️‍🔥{user_is_validated['NAME']}'s Rebirth",color=0x7289da)
#             embedVar1.set_thumbnail(url=user_is_validated['AVATAR'])
#             embedVar1.add_field(name=f":angel: Rebirth Level: {user_is_validated['REBIRTH']}\n{picon}Prestige Level: {pLevel}\n\nRebirth Cost: 🪙{'{:,}'.format(rebirthCost)}", value=textwrap.dedent(f"""\
#             **Rebirth Effects**
#             New Starting Deck
#             Starting Summon Bond
#             Increase Base ATK + 100 (Max 1000)
#             Increase Base DEF + 100 (Max 1000)
#             Increase Move AP by +2% (Max 20%)
#             Increased 🪙 drops + %10
#             Increased Item Drop Rates + 50%
#             Keep All Card Levels
            
#             {pursemessage}
            
#             **You need to increase your Prestige Level to Rebirth again. 
#             Complete floor {pReq}**
#             """))
#             await ctx.send(embed=embedVar1)
#             return
#          elif rLevel < 10:
#             pursemessage = "You will lose all of your equipped and vaulted items."
            

#             util_buttons = [
#                   Button(
#                      style=ButtonStyle.BLUE,
#                      label="Yes",
#                      custom_id = "Y"
#                   ),
#                   Button(
#                      style=ButtonStyle.RED,
#                      label="No",
#                      custom_id = "N"
#                   )
#                ]
#             util_action_row = ActionRow(*util_buttons)
#             components = [util_action_row]

#             embedVar1 = Embed(title=f"❤️‍🔥{user_is_validated['NAME']}'s Rebirth",color=0x7289da)
#             embedVar1.set_thumbnail(url=user_is_validated['AVATAR'])
#             embedVar1.add_field(name=f"Rebirth Level: {user_is_validated['REBIRTH']}\nPrestige Level: {pLevel}\n\nRebirth Cost: 🪙{'{:,}'.format(rebirthCost)}", value=textwrap.dedent(f"""\
#             **Rebirth Effects**
#             New Starting Deck
#             Starting Summon Bond
#             Increase Base ATK + 100 (Max 1000)
#             Increase Base DEF + 100 (Max 1000)
#             Increase Move AP by +2% (Max 20%)
#             Increased 🪙 drops + %10
#             Increased Item Drop Rates + 50%
#             Keep All Card Levels
            
#             {pursemessage}
            
#             *Rebirth is permanent and cannot be undone*
#             """))
#             accept = await ctx.send(embed=embedVar1, components=[util_action_row])

#             def check(button_ctx):
#                   return button_ctx.author == ctx.author

#             try:
#                button_ctx  = await self.bot.wait_for_component(bot, components=[util_action_row], timeout=120,check=check)
#                if button_ctx.custom_id == "Y":
#                   try:
#                      vault = db.queryVault({'DID': user_is_validated['DID']})
#                      if vault:
#                         if vault['BALANCE'] >= rebirthCost:
#                            if rLevel == 0:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"OWNER" : user_is_validated['DISNAME']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Twice' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Twice', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Charmander' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Charmander', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Braum' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Braum', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER': user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Twice','Charmander','Braum'], 'TITLES': ['Reborn'], 'ARMS': [{'ARM': 'Reborn Stock', 'DUR': 999999}],'DECK': [{'CARD': 'Charmander', 'TITLE': 'Reborn', 'ARM': 'Reborn Stock', 'PET': 'Chick'}, {'CARD': 'Twice', 'TITLE': 'Reborn', 'ARM': 'Reborn Stock', 'PET': 'Chick'}, {'CARD': 'Braum', 'TITLE': 'Reborn', 'ARM': 'Reborn Stock', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 1, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Charmander', 'Twice', 'Braum']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Charmander', 'TITLE': 'Reborn', 'ARM':'Reborn Stock'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")                              
#                            elif rLevel == 1:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Kirishima' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Kirishima', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Squirtle' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Squirtle', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Malphite' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Malphite', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER': user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Kirishima','Squirtle','Malphite'], 'TITLES': ['Reborn Soldier'], 'ARMS': [{'ARM': 'Deadgun', 'DUR': 999999}], 'DECK': [{'CARD': 'Kirishima', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}, {'CARD': 'Squirtle', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}, {'CARD': 'Malphite', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 3, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Squirtle', 'Malphite', 'Kirishima']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Malphite', 'TITLE': 'Reborn Soldier', 'ARM':'Deadgun'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 2:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Mineta' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Mineta', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Bulbasaur' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Bulbasaur', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Shen' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Shen', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Mineta','Bulbasaur','Shen'], 'TITLES': ['Reborn Legion'], 'ARMS': [{'ARM': 'Glaive', 'DUR': 999999}], 'DECK': [{'CARD': 'Mineta', 'TITLE': 'Reborn Legion', 'ARM': 'Glaive', 'PET': 'Chick'}, {'CARD': 'Bulbasaur', 'TITLE': 'Reborn Legion', 'ARM': 'Glaive', 'PET': 'Chick'}, {'CARD': 'Shen', 'TITLE': 'Reborn Legion', 'ARM': 'Glaive', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 5, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Bulbasaur', 'Mineta', 'Shen']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Mineta', 'TITLE': 'Reborn Legion', 'ARM':'Glaive'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 3:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Hawks' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Hawks', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Clefairy' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Clefairy', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Yasuo' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Yasuo', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Hawks','Clefairy','Yasuo'], 'TITLES': ['Reborn King'], 'ARMS': [{'ARM': 'Kings Glaive', 'DUR': 999999}], 'DECK': [{'CARD': 'Hawks', 'TITLE': 'Reborn King', 'ARM': 'Kings Glaive', 'PET': 'Chick'}, {'CARD': 'Clefairy', 'TITLE': 'Reborn King', 'ARM': 'Kings Glaive', 'PET': 'Chick'}, {'CARD': 'Yasuo', 'TITLE': 'Reborn King', 'ARM': 'Kings Glaive', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 1, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Hawks', 'Clefairy', 'Yasuo']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Clefairy', 'TITLE': 'Reborn King', 'ARM':'Kings Glaive'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 4:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Stain' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Stain', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Onix' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Onix', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Xayah And Rakan' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Xayah And Rakan', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Stain','Onix','Xayah And Rakan'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Stain', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Onix', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Xayah And Rakan', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 5, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Stain', 'Onix', 'Xayah And Rakan']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Xayah And Rakan', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 5:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Meliodas' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Meliodas', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Tusk Shadow' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Tusk Shadow', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Kratos And Atreus' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Kratos And Atreus', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Meliodas','Tusk Shadow','Kratos And Atreus'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Meliodas', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Tusk Shadow', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Kratos And Atreus', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Meliodas', 'Tusk Shadow', 'Kratos And Atreus']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Kratos And Atreus', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 6:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Asta' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Asta', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Maka' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Maka', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Asuna' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Asuna', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Asta','Maka','Asuna'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Asta', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Maka', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Asuna', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Asta', 'Maka', 'Asuna']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Asuna', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 7:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Tepellin' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Tepellin', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Kyogre' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Kyogre', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Omnimon' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Omnimon', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Tepellin','Kyogre','Omnimon'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Tepellin', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Kyogre', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Omnimon', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Tepellin', 'Kyogre', 'Omnimon']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Omnimon', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 8:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Gon' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Gon', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Obito' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Obito', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Kurama' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Kurama', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Gon','Kurama','Obito'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Gon', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Obito', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Kurama', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Gon', 'Obito', 'Kurama']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Kurama', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            elif rLevel == 9:
#                               if gabes_purse == 1:
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                                  db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
#                                  return
#                               card_level_list = vault['CARD_LEVELS']
#                               owned_cards = []
#                               for card in card_level_list:
#                                  owned_cards.append(card['CARD'])
#                               if 'Meister Maka' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Meister Maka', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Byakuran' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Byakuran', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               if 'Cthulhu' not in owned_cards:
#                                  card_level_list.append({'CARD': 'Cthulhu', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

#                               delete = db.deleteVault({'DID': user_is_validated['DID']})
#                               vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Meister Maka','Byakuran','Cthulhu'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Meister Maka', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Byakuran', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Cthulhu', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
#                               if vault:
#                                  cardList = ['Meister Maka', 'Byakuran', 'Cthulhu']
#                                  for card in cardList:
#                                     for destiny in d.destiny:
#                                        if card in destiny["USE_CARDS"]:
#                                           db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
#                                           message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
#                                           await button_ctx.send(message)
#                                  nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Cthulhu', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
#                                  db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
#                                  nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
#                                  await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
#                            #Starting Selection
#                            try:
#                               if gabes_purse == 1:
#                                  await button_ctx.send(f":purse: | Gabe's Purse Activated! All Items Will Be Retained!\nNo Starting Universe Selection...")
#                                  return
#                               universe_data = db.queryAllUniverse()
#                               universe_embed_list = []
#                               for uni in universe_data:
#                                  available = ""
#                                  if uni['HAS_CROWN_TALES'] == True:
#                                     traits = ut.traits
#                                     mytrait = {}
#                                     traitmessage = ''
#                                     o_show = uni['TITLE']
#                                     universe = o_show
#                                     for trait in traits:
#                                        if trait['NAME'] == o_show:
#                                              mytrait = trait
#                                        if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
#                                              if trait['NAME'] == 'Pokemon':
#                                                 mytrait = trait
#                                     if mytrait:
#                                        traitmessage =f"**{mytrait['EFFECT']}|** {mytrait['TRAIT']}"
#                                     available =f"{crown_utilities.crest_dict[uni['TITLE']]}"
                                    
#                                     tales_list = ", ".join(uni['CROWN_TALES'])

#                                     embedVar = Embed(title=f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
#                                     **Select A Starting Universe, {ctx.author.mention}!**
#                                     Selecting a Starter Universe will give you *3* 🎴 Cards, 🎗️ Titles, and 🦾 Arms to begin!
                                    
#                                     ♾️ - Unique Universe Trait
#                                     {traitmessage}
#                                     """))
#                                     embedVar.set_image(url=uni['PATH'])
#                                     universe_embed_list.append(embedVar)
                                    
#                               buttons = [
#                                     Button(style=3, label="Select This Starter Universe", custom_id="Select")
#                                  ]
#                               custom_action_row = ActionRow(*buttons)
#                               # custom_button = Button(style=3, label="Equip")

#                               async def custom_function(self, button_ctx):
#                                  try:
#                                     if button_ctx.author == ctx.author:
#                                        universe = str(button_ctx.origin_message.embeds[0].title)
#                                        vault_query = {'DID' : str(ctx.author.id)}
#                                        vault = db.altQueryVault(vault_query)
#                                        current_titles = vault['TITLES']
#                                        current_cards = vault['CARDS']
#                                        current_arms = []
#                                        for arm in vault['ARMS']:
#                                           current_arms.append(arm['ARM'])

#                                        owned_card_levels_list = []
#                                        for c in vault['CARD_LEVELS']:
#                                           owned_card_levels_list.append(c['CARD'])
#                                        owned_destinies = []
#                                        for destiny in vault['DESTINY']:
#                                           owned_destinies.append(destiny['NAME'])
                                       
#                                        if button_ctx.custom_id == "Select":
#                                           acceptable = [1,2,3,4]
#                                           list_of_titles =[x for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE'] and x['TITLE'] not in current_titles]
#                                           count = 0
#                                           selected_titles = [1000]
#                                           while count < 3:
#                                              selectable_titles = list(range(0, len(list(list_of_titles))))
#                                              for selected in selected_titles:
#                                                 if selected in selectable_titles:
#                                                    selectable_titles.remove(selected)
#                                              selection = random.choice(selectable_titles)
#                                              selected_titles.append(selection)
#                                              title = list_of_titles[selection]
#                                              response = db.updateUserNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})
#                                              await button_ctx.send(f"🎗️ **{title['TITLE']}**.")
#                                              count = count + 1
                                          
                                          
#                                           list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE'] and x['ARM'] not in current_arms]
#                                           count = 0
#                                           selected_arms = [1000]
#                                           while count < 3:
#                                              current_arms = vault['ARMS']
#                                              selectable_arms = list(range(0, len(list(list_of_arms))))
#                                              for selected in selected_arms:
#                                                 if selected in selectable_arms:
#                                                    selectable_arms.remove(selected)
#                                              selection = random.choice(selectable_arms)
#                                              selected_arms.append(selection)
#                                              arm = list_of_arms[selection]['ARM']
#                                              db.updateUserNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 75}}})                           
#                                              await button_ctx.send(f"🦾 **{arm}**.")
#                                              count = count + 1
                                             
#                                           list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and x['AVAILABLE'] and x['NAME'] not in current_cards]
#                                           count = 0
#                                           selected_cards = [1000]
#                                           while count < 3:
#                                              current_cards = vault['CARDS']
#                                              selectable_cards = list(range(0, len(list(list_of_cards))))
#                                              for selected in selected_cards:
#                                                 if selected in selectable_cards:
#                                                    selectable_cards.remove(selected)
#                                              selection = random.choice(selectable_cards)
#                                              selectable_cards.append(selection)
#                                              card = list_of_cards[selection]
#                                              card_name = card['NAME']
#                                              tier = 0

#                                              cresponse = db.updateUserNoFilter(vault_query, {'$addToSet': {'CARDS': str(card_name)}})
#                                              if cresponse:
#                                                 if card_name not in owned_card_levels_list:
#                                                    update_query = {'$addToSet': {
#                                                          'CARD_LEVELS': {'CARD': str(card_name), 'LVL': 0, 'TIER': int(tier),
#                                                                         'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
#                                                    r = db.updateUserNoFilter(vault_query, update_query)

#                                                 await button_ctx.send(f"🎴 **{card_name}**!")

#                                                 # Add Destiny
#                                                 for destiny in d.destiny:
#                                                    if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
#                                                          db.updateUserNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
#                                                          await button_ctx.send(
#                                                             f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.", ephemeral=True)
#                                              count = count + 1
#                                           await button_ctx.send(f"Nice choice {ctx.author.mention}!\n\nCreate your first **Build**!\n**/cards** Select your 🎴  Card\n**/titles** Select your 🎗️ Title\n**/arms** Select your 🦾  Arm\n\nOnce you're done, run **/tutorial** to begin the **Tutorial Battle**! ⚔️")
#                                           self.stop = True
#                                  except Exception as ex:
#                                     # trace = []
#                                     # tb = ex.__traceback__
#                                     # while tb is not None:
#                                     #    trace.append({
#                                     #       "filename": tb.tb_frame.f_code.co_filename,
#                                     #       "name": tb.tb_frame.f_code.co_name,
#                                     #       "lineno": tb.tb_lineno
#                                     #    })
#                                     #    tb = tb.tb_next
#                                     # print(str({
#                                     #    'type': type(ex).__name__,
#                                     #    'message': str(ex),
#                                     #    'trace': trace
#                                     # }))
#                                     loggy.error(f"Error in Rebirth command: {ex}")
#                                     await ctx.send("Rebirth Issue Seek support.")
#                               await Paginator(bot=bot, ctx=ctx, disableAfterTimeout=True, pages=universe_embed_list, customActionRow=[
#                                  custom_action_row,
#                                  custom_function,
#                               ]).run()
#                            except Exception as ex:
#                               # trace = []
#                               # tb = ex.__traceback__
#                               # while tb is not None:
#                               #    trace.append({
#                               #       "filename": tb.tb_frame.f_code.co_filename,
#                               #       "name": tb.tb_frame.f_code.co_name,
#                               #       "lineno": tb.tb_lineno
#                               #    })
#                               #    tb = tb.tb_next
#                               # print(str({
#                               #    'type': type(ex).__name__,
#                               #    'message': str(ex),
#                               #    'trace': trace
#                               # }))
#                               loggy.error(f"Error in Rebirth command: {ex}")
#                               await ctx.send("Rebirth Issue Seek support.")
#                         else:
#                            await button_ctx.send(f"Not enough 🪙!\nYou need {'{:,}'.format(rebirthCost)} to Rebirth:angel:", delete_after=5)
#                      else:
#                         await button_ctx.send("No Vault:angel:", delete_after=5)
#                   except Exception as ex:
#                      # trace = []
#                      # tb = ex.__traceback__
#                      # while tb is not None:
#                      #    trace.append({
#                      #       "filename": tb.tb_frame.f_code.co_filename,
#                      #       "name": tb.tb_frame.f_code.co_name,
#                      #       "lineno": tb.tb_lineno
#                      #    })
#                      #    tb = tb.tb_next
#                      # print(str({
#                      #    'type': type(ex).__name__,
#                      #    'message': str(ex),
#                      #    'trace': trace
#                      # }))
#                      loggy.error(f"Error in Rebirth command: {ex}")
#                      await ctx.send("Rebirth Issue Seek support.")
#                elif button_ctx.custom_id == "N":
#                   await button_ctx.send(f"❤️‍🔥 | Ahhhh...another time then?", delete_after=5)
#                   return
#             except asyncio.TimeoutError:
#                await ctx.send("Rebirth Menu Closed", hidden= True)
#             except Exception as ex:
#                # trace = []
#                # tb = ex.__traceback__
#                # while tb is not None:
#                #    trace.append({
#                #       "filename": tb.tb_frame.f_code.co_filename,
#                #       "name": tb.tb_frame.f_code.co_name,
#                #       "lineno": tb.tb_lineno
#                #    })
#                #    tb = tb.tb_next
#                # print(str({
#                #    'type': type(ex).__name__,
#                #    'message': str(ex),
#                #    'trace': trace
#                # }))
#                loggy.error(f"Error in Rebirth command: {ex}")
#                await ctx.send("Rebirth Issue Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
#          else:
#             await ctx.send(f"You are at full Rebirth\n:angel:Level: {user_is_validated['REBIRTH']} ", delete_after=5)
#    except Exception as ex:
#       loggy.error(f"Error in Rebirth command: {ex}")
#       await ctx.send("Rebirth Issue Seek support in the Anime 🆚+ support server")
#       return
#       # trace = []
#       # tb = ex.__traceback__
#       # while tb is not None:
#       #    trace.append({
#       #       "filename": tb.tb_frame.f_code.co_filename,
#       #       "name": tb.tb_frame.f_code.co_name,
#       #       "lineno": tb.tb_lineno
#       #    })
#       #    tb = tb.tb_next
#       # print(str({
#       #    'type': type(ex).__name__,
#       #    'message': str(ex),
#       #    'trace': trace
#       # }))