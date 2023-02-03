from faulthandler import dump_traceback_later
import discord
from discord.ext import commands
import emoji
from pymongo import response
# from soupsieve import select
import bot as main
import crown_utilities
import db
import classes as data #
import messages as m
import numpy as np
import help_commands as h
import unique_traits as ut
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from collections import ChainMap
import DiscordUtils
from .crownunlimited import showcard, cardback, enhancer_mapping, title_enhancer_mapping, enhancer_suffix_mapping, title_enhancer_suffix_mapping, passive_enhancer_suffix_mapping, battle_commands, destiny as update_destiny_call
import random
import textwrap
from discord_slash import cog_ext, SlashContext
from dinteractions_Paginator import Paginator
from discord_slash.utils.manage_commands import create_option, create_choice

import destiny as d
import random


emojis = ['👍', '👎']

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Profile Cog is ready!')

    async def cog_check(self, ctx):
        print("Here")
        return await main.validate_user(ctx)


    @cog_ext.cog_slash(description="Delete your account", guild_ids=main.guild_ids)
    async def deleteaccount(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        user = str(ctx.author)
        query = {'DID': str(ctx.author.id)}
        user_is_validated = db.queryUser(query)
        if user_is_validated:
            accept_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label="Yes",
                    custom_id="yes"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="No",
                    custom_id="no"
                )
            ]
            accept_buttons_action_row = manage_components.create_actionrow(*accept_buttons)

            team = db.queryTeam({'TEAM_NAME': user_is_validated['TEAM'].lower()})

            await ctx.send(f"{ctx.author.mention}, are you sure you want to delete your account? " + "\n" + "All of your wins, purchases and other earnings will be removed from the system and can not be recovered. ", hidden=True, components=[accept_buttons_action_row])

            def check(button_ctx):
                return button_ctx.author == ctx.author

            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[accept_buttons_action_row], timeout=120,check=check)

                if button_ctx.custom_id == "no":
                    await button_ctx.send("Account not deleted.")
                    return

                if button_ctx.custom_id == "yes":
                    response = db.deleteVault({'DID': str(ctx.author.id)})
                    delete_user_resp = db.deleteUser(user)
                    if team:
                        transaction_message = f"{user_is_validated['DISNAME']} left the game."
                        team_query = {'TEAM_NAME': team['TEAM_NAME']}
                        new_value_query = {
                            '$pull': {
                                'MEMBERS': user_is_validated['DISNAME'],
                                'OFFICERS': user_is_validated['DISNAME'],
                                'CAPTAINS': user_is_validated['DISNAME'],
                            },
                            '$addToSet': {'TRANSACTIONS': transaction_message},
                            '$inc': {'MEMBER_COUNT': -1}
                            }
                        response = db.deleteTeamMember(team_query, new_value_query, str(ctx.author.id))
                    await button_ctx.send("Account successfully deleted.")

            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
        else:
            await ctx.send("You aren't registered.", hidden=True)


    @cog_ext.cog_slash(description="main menu where all your important game items and builds are",
                    options=[
                        create_option(
                            name="selection",
                            description="select an option to continue",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="🎴 My Cards",
                                    value="cards",
                                ),
                                create_choice(
                                    name="🎗️ My Titles",
                                    value="titles",
                                ),
                                create_choice(
                                    name="🦾 My Arms",
                                    value="arms",
                                ),
                                create_choice(
                                    name="🧬 My Summons",
                                    value="summons",
                                ),
                                create_choice(
                                    name="⚔️ Current Build",
                                    value="build",
                                ),
                                create_choice(
                                    name="💼 Check Card Storage",
                                    value="storage",
                                ),
                                create_choice(
                                    name="🖨️ Draw Card From Storage",
                                    value="draw",
                                ),
                                create_choice(
                                    name="✨ View Destinies",
                                    value="destinies",
                                ),
                                create_choice(
                                    name="📜 Start Quests",
                                    value="quests",
                                ),
                                create_choice(
                                    name="💰 My Money",
                                    value="balance",
                                ),
                                create_choice(
                                    name="💎 Gem Bag",
                                    value="gems"
                                ),
                                create_choice(
                                    name="🪔 Essence",
                                    value="essence",
                                ),
                                create_choice(
                                    name="📤 Load Presets",
                                    value="presets",
                                ),
                                create_choice(
                                    name="📥 Save Current Preset",
                                    value="savepreset",
                                ),
                                create_choice(
                                    name="🛍️ Open the Shop",
                                    value="shop",
                                ),
                                create_choice(
                                    name="⚒️ Visit the Blacksmith",
                                    value="blacksmith",
                                ),
                                create_choice(
                                    name="💎 Start Crafting",
                                    value="craft",
                                ),

                            ]
                        )
                    ]
        , guild_ids=main.guild_ids)
    async def menu(self, ctx, selection, optional = None):
        if selection == "cards":
            await menucards(self, ctx)
        if selection == "titles":
            await menutitles(self, ctx)
        if selection == "arms":
            await menuarms(self, ctx)
        if selection == "build":
            await menubuild(self, ctx)
        if selection == "summons":
            await menusummons(self, ctx)
        if selection == "storage":
            await menustorage(self, ctx)
        if selection == "destinies":
            await menudestinies(self, ctx)
        if selection == "quests":
            await menuquests(self, ctx)
        if selection == "balance":
            await menubalance(self, ctx)
        if selection == "presets":
            await menupreset(self, ctx)
        if selection == "savepreset":
            await menusavepreset(self, ctx)
        if selection == "shop":
            await menushop(self, ctx)
        if selection == "craft":
            await menucraft(self, ctx)
        if selection == "gems":
            await menugems(self, ctx)
        if selection == "blacksmith":
            await menublacksmith(self, ctx)
        if selection == "essence":
            await menuessence(self, ctx)

            
    @cog_ext.cog_slash(description="View your current build", guild_ids=main.guild_ids)
    async def build(self, ctx):
        try:
            # await ctx.defer()
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return
            query = {'DID': str(ctx.author.id)}
            d = db.queryUser(query)
            card = db.queryCard({'NAME':str(d['CARD'])})
            title = db.queryTitle({'TITLE': str(d['TITLE'])})
            arm = db.queryArm({'ARM': str(d['ARM'])})
            user_info = db.queryUser(query)
            vault = db.queryVault({'DID': d['DID']})
            has_universe_heart = False
            has_universe_soul = False
            
            if card:
                try:
                    if card['UNIVERSE'] != "n/a":
                        for gems in vault['GEMS']:
                            if gems['UNIVERSE'] == card['UNIVERSE'] and gems['UNIVERSE_HEART']:
                                has_universe_heart = True
                            if gems['UNIVERSE'] == card['UNIVERSE'] and gems['UNIVERSE_SOUL']:
                                has_universe_soul = True
                    durability = ""
                    base_arm_names = ['Reborn Stock', 'Stock', 'Deadgun', 'Glaive', 'Kings Glaive', 'Legendary Weapon']
                    for a in vault['ARMS']:
                        if a['ARM'] == str(d['ARM']) and a['ARM'] in base_arm_names:
                            durability = f""
                        elif a['ARM'] == str(d['ARM']) and a['ARM'] not in base_arm_names:
                            durability = f"⚒️ {a['DUR']}"
                    
                    # Acquire Card Levels data
                    card_lvl = 0
                    card_tier = 0
                    card_exp = 0
                    card_lvl_attack_buff = 0
                    card_lvl_defense_buff = 0
                    card_lvl_ap_buff = 0
                    card_lvl_hlt_buff = 0

                    for x in vault['CARD_LEVELS']:
                        if x['CARD'] == card['NAME']:
                            card_lvl = x['LVL']
                            card_exp = x['EXP']
                            card_lvl_ap_buff = crown_utilities.level_sync_stats(card_lvl, "AP")
                            card_lvl_attack_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                            card_lvl_defense_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                            card_lvl_hlt_buff = crown_utilities.level_sync_stats(card_lvl, "HLT")
                            

                    x = 0.0999
                    y = 1.25
                    lvl_req = round((float(card_lvl)/x)**y)
                    pokemon_universes = ['Kanto Region', 'Johto Region','Hoenn Region','Sinnon Region','Kalos Region','Alola Region','Galar Region']
                    pokemon_arm=False
                    pokemon_title=False
                    oarm_universe = arm['UNIVERSE']
                    if oarm_universe in pokemon_universes:
                        pokemon_arm=True
                    o_title_universe = title['UNIVERSE']
                    if o_title_universe in pokemon_universes:
                        pokemon_title=True
                    o_card = card['NAME']
                    o_card_path=card['PATH']
                    o_max_health = card['HLT'] + card_lvl_hlt_buff
                    o_health = card['HLT'] + card_lvl_hlt_buff
                    o_stamina = card['STAM']
                    o_max_stamina = card['STAM']
                    o_moveset = card['MOVESET']
                    o_attack = card['ATK'] + card_lvl_attack_buff
                    o_defense = card['DEF'] + card_lvl_defense_buff
                    o_type = card['TYPE']
                    o_passive = card['PASS'][0]
                    o_speed = card['SPD']
                    o_show = card['UNIVERSE']
                    o_collection = card['COLLECTION']
                    o_destiny = card['HAS_COLLECTION']
                    o_rebirth = d['REBIRTH']
                    performance_mode = d['PERFORMANCE']
                    card_tier = card['TIER']
                    affinity_message = crown_utilities.set_affinities(card)
                    talisman = d['TALISMAN']
                    talisman_message = "No Talisman Equipped"
                    talisman_emoji = '🔅'
                    talisman_durability = '0'
                    if talisman == "NULL":
                        talisman_message = "No Talisman Equipped"
                    else:
                        for t in vault["TALISMANS"]:
                            if t["TYPE"].upper() == talisman.upper():
                                talisman_emoji = crown_utilities.set_emoji(talisman.upper())
                                talisman_durability = t["DUR"]
                        talisman_message = f"{talisman_emoji} {talisman.title()} Talisman Equipped ⚒️ {talisman_durability}"
                    
                    trebirth_message = f"+0"
                    drebirth_message = f""
                    trebirthBonus = o_rebirth + 25
                    drebirthBonus = (o_rebirth + 1) * 100
                    if o_rebirth > 0:
                        trebirth_message = f"_⚔️Tales: {trebirthBonus}xp_"
                        drebirth_message = f"_🔥Dungeon: {drebirthBonus}xp_"
                    if has_universe_soul:
                        trebirthBonus = (o_rebirth + 25) * 4
                        drebirthBonus = ((o_rebirth + 1) * 100) * 4
                        trebirth_message = f"_🌹⚔️Tales: {trebirthBonus}xp_"
                        drebirth_message = f"_🌹🔥Dungeon: {drebirthBonus}xp_"
                    
                    
                    traits = ut.traits
                    mytrait = {}
                    traitmessage = ''
                    pokemon_universes = False
                    for trait in traits:
                        if trait['NAME'] == o_show:
                            mytrait = trait
                        if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                            pokemon_universes =True
                            if trait['NAME'] == 'Pokemon':
                                mytrait = trait
                                
                    if mytrait:
                        traitmessage = f"{mytrait['EFFECT']}: {mytrait['TRAIT']}"#

                    pets = vault['PETS']

                    active_pet = {}
                    pet_names = []

                    for pet in pets:
                        pet_names.append(pet['NAME'])
                        if pet['NAME'] == d['PET']:
                            active_pet = pet

                    power = list(active_pet.values())[3]
                    pet_ability_power = (active_pet['BOND'] * active_pet['LVL']) + power
                    bond = active_pet['BOND']
                    lvl = active_pet['LVL']

                    bond_message = ""
                    lvl_message = ""
                    if bond == 3:
                        bond_message = "🌟"
                    
                    if lvl == 10:
                        lvl_message = "⭐"

                    # Arm Information
                    arm_name = arm['ARM']
                    arm_passive = arm['ABILITIES'][0]
                    arm_passive_type = list(arm_passive.keys())[0]
                    arm_moves_type_list = ['BASIC', 'SPECIAL', 'ULTIMATE']
                    if arm_passive_type in arm_moves_type_list:
                        arm_element = arm['ELEMENT']
                    arm_passive_value = list(arm_passive.values())[0]
                    title_name= title['TITLE']
                    title_passive = title['ABILITIES'][0]
                    title_passive_type = list(title_passive.keys())[0]
                    title_passive_value = list(title_passive.values())[0]

                    o_1 = o_moveset[0]
                    o_2 = o_moveset[1]
                    o_3 = o_moveset[2]
                    o_enhancer = o_moveset[3]
                    
                    # Move 1
                    move1 = list(o_1.keys())[0]
                    move1ap = list(o_1.values())[0] + card_lvl_ap_buff
                    move1_stamina = list(o_1.values())[1]
                    move1_element = list(o_1.values())[2]
                    move1_emoji = crown_utilities.set_emoji(move1_element)
                    if arm_passive_type == 'BASIC':
                        move1 = arm_name
                        move1ap = list(o_1.values())[0] + card_lvl_ap_buff + arm_passive_value
                        move1_stamina = list(o_1.values())[1]
                        move1_element = arm_element
                        move1_emoji = crown_utilities.set_emoji(move1_element)
                    
                    # Move 2
                    move2 = list(o_2.keys())[0]
                    move2ap = list(o_2.values())[0] + card_lvl_ap_buff
                    move2_stamina = list(o_2.values())[1]
                    move2_element = list(o_2.values())[2]
                    move2_emoji = crown_utilities.set_emoji(move2_element)
                    if arm_passive_type == 'SPECIAL':
                        move2 = arm_name
                        move2ap = list(o_2.values())[0] + card_lvl_ap_buff + arm_passive_value
                        move2_stamina = list(o_2.values())[1]
                        move2_element = arm_element
                        move2_emoji = crown_utilities.set_emoji(move2_element)


                    # Move 3
                    move3 = list(o_3.keys())[0]
                    move3ap = list(o_3.values())[0] + card_lvl_ap_buff
                    move3_stamina = list(o_3.values())[1]
                    move3_element = list(o_3.values())[2]
                    move3_emoji = crown_utilities.set_emoji(move3_element)
                    if arm_passive_type == 'ULTIMATE':
                        move3 = arm_name
                        move3ap = list(o_3.values())[0] + card_lvl_ap_buff + arm_passive_value
                        move3_stamina = list(o_3.values())[1]
                        move3_element = arm_element
                        move3_emoji = crown_utilities.set_emoji(move3_element)


                    # Move Enhancer
                    move4 = list(o_enhancer.keys())[0]
                    move4ap = list(o_enhancer.values())[0]
                    move4_stamina = list(o_enhancer.values())[1]
                    move4enh = list(o_enhancer.values())[2]


                    resolved = False
                    focused = False
                    att = 0
                    defe = 0
                    turn = 0

                    passive_name = list(o_passive.keys())[0]
                    passive_num = list(o_passive.values())[0]
                    passive_type = list(o_passive.values())[1]

               
                    if passive_type:
                        value_for_passive = card_tier * .5
                        flat_for_passive = round(10 * (card_tier * .5))
                        stam_for_passive = 5 * (card_tier * .5)
                        if passive_type == "HLT":
                            passive_num = value_for_passive
                        if passive_type == "LIFE":
                            passive_num = value_for_passive
                        if passive_type == "ATK":
                            passive_num = value_for_passive
                        if passive_type == "DEF":
                            passive_num = value_for_passive
                        if passive_type == "STAM":
                            passive_num = stam_for_passive
                        if passive_type == "DRAIN":
                            passive_num = stam_for_passive
                        if passive_type == "FLOG":
                            passive_num = value_for_passive
                        if passive_type == "WITHER":
                            passive_num = value_for_passive
                        if passive_type == "RAGE":
                            passive_num = value_for_passive
                        if passive_type == "BRACE":
                            passive_num = value_for_passive
                        if passive_type == "BZRK":
                            passive_num = value_for_passive
                        if passive_type == "CRYSTAL":
                            passive_num = value_for_passive
                        if passive_type == "FEAR":
                            passive_num = flat_for_passive
                        if passive_type == "GROWTH":
                            passive_num = flat_for_passive
                        if passive_type == "CREATION":
                            passive_num = value_for_passive
                        if passive_type == "DESTRUCTION":
                            passive_num = value_for_passive
                        if passive_type == "SLOW":
                            passive_num = "1"
                        if passive_type == "HASTE":
                            passive_num = "1"
                        if passive_type == "STANCE":
                            passive_num = flat_for_passive
                        if passive_type == "CONFUSE":
                            passive_num = flat_for_passive
                        if passive_type == "BLINK":
                            passive_num = stam_for_passive

                    atk_buff = ""
                    def_buff = ""
                    hlt_buff = ""
                    message = ""
                    if (oarm_universe == o_show) and (o_title_universe == o_show):
                        o_attack = o_attack + 20
                        o_defense = o_defense + 20
                        o_health = o_health + 100
                        o_max_health = o_max_health + 100
                        message = "_Universe Buff Applied_"
                        if o_destiny:
                            o_attack = o_attack + 25
                            o_defense = o_defense + 25
                            o_health = o_health + 150
                            o_max_health = o_max_health + 150
                            message = "_Destiny Buff Applied_"

                    #Title errors 
                    titled =False
                    titleicon="⚠️"
                    licon = "🔰"
                    armicon = "⚠️"
                    if card_lvl >= 200:
                        licon ="🔱"
                    if card_lvl >= 700:
                        licon ="⚜️"
                    if card_lvl >=999:
                        licon ="🏅"
                    titlemessage = f"{titleicon} {title_name} ~ INEFFECTIVE"
                    armmessage = f"🦾 ⚠️ {arm_name}: {durability}"
                    if arm_passive_type in arm_moves_type_list:
                        arm_emoji = crown_utilities.set_emoji(arm_element)
                        if performance_mode:
                            armmessage = f'⚠️ {arm_name}: {arm_emoji} {arm_passive_type.title()} Attack: {arm_passive_value} | {durability}'
                        else:
                            armmessage = f'⚠️ {arm_name}'
                    warningmessage = f"Use {o_show} or Unbound Titles on this card"
                    if o_title_universe == "Unbound" or (pokemon_universes==True) or o_show == "Crown Rift Awakening":
                        titled =True
                        titleicon = "👑"
                        if performance_mode:
                            titlemessage = f"👑 {title_name}: {title_passive_type} {title_passive_value}{title_enhancer_suffix_mapping[title_passive_type]}"
                        else:
                            titlemessage = f"👑 {title_name}" 
                        warningmessage= f""
                    elif o_title_universe == o_show or (pokemon_universes==True and pokemon_title==True):
                        titled =True
                        titleicon = "🎗️"
                        if performance_mode:
                            titlemessage = f"🎗️ {title_name}: {title_passive_type} {title_passive_value}{title_enhancer_suffix_mapping[title_passive_type]}"
                        else:
                            titlemessage = f"🎗️ {title_name}"
                        warningmessage= f""
                    
                    if oarm_universe == "Unbound" or o_show == "Crown Rift Slayers":
                        armicon = "💪"
                        if performance_mode:
                            armmessage = f'💪 {arm_name}: {arm_passive_type} {arm_passive_value}{enhancer_suffix_mapping[arm_passive_type]} {durability}'
                        else:
                            armmessage = f'💪 {arm_name}'

                    elif oarm_universe == o_show or (pokemon_universes==True and pokemon_arm==True):
                        armicon = "🦾"
                        if performance_mode:
                            armmessage = f'🦾 {arm_name}: {arm_passive_type} {arm_passive_value}{enhancer_suffix_mapping[arm_passive_type]} {durability}'
                        else:
                            armmessage = f'🦾 {arm_name}: {durability}'
                        

                    cardtitle = {'TITLE': title_name}
                    

                    #<:PCG:769471288083218432>
                    if performance_mode:
                        embedVar = discord.Embed(title=f"{licon}{card_lvl} {o_card}".format(self), description=textwrap.dedent(f"""\
                        :mahjong: **{card_tier}**
                        ❤️ **{o_max_health}**
                        🗡️ **{o_attack}**
                        🛡️ **{o_defense}**
                        🏃 **{o_speed}**

                        **{titlemessage}**
                        **{armmessage}**
                        **{talisman_message}**
                        🧬 **{active_pet['NAME']}:** {active_pet['TYPE']}: {pet_ability_power}{enhancer_suffix_mapping[active_pet['TYPE']]}
                        🧬 Bond {bond} {bond_message} & Level {lvl} {lvl_message}

                        🩸 **{passive_name}:** {passive_type} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}                
                        
                        {move1_emoji} **{move1}:** {move1ap}
                        {move2_emoji} **{move2}:** {move2ap}
                        {move3_emoji} **{move3}:** {move3ap}
                        🦠 **{move4}:** {move4enh} {move4ap}{enhancer_suffix_mapping[move4enh]}

                        ♾️ {traitmessage}
                        """),colour=000000)
                        embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                        embedVar.set_image(url="attachment://image.png")
                        if card_lvl != 999:
                            embedVar.set_footer(text=f"EXP Until Next Level: {'{:,}'.format(lvl_req - card_exp)}\nRebirth Buff: {trebirth_message} | {drebirth_message}\n{warningmessage}")
                        else:
                            embedVar.set_footer(text=f"Max Level\nRebirth Buff: {trebirth_message} | {drebirth_message}\n{warningmessage}")
                        embedVar.set_author(name=f"{ctx.author}", icon_url=user_info['AVATAR'])
                        
                        await ctx.send(embed=embedVar)
                    
                    else:
                        card_file = showcard("non-battle", card, arm, o_max_health, o_health, o_max_stamina, o_stamina, resolved, title, focused, o_attack, o_defense, turn, move1ap, move2ap, move3ap, move4ap, move4enh, card_lvl, None)

                        embedVar = discord.Embed(title=f"".format(self), colour=000000)
                        embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                        embedVar.set_image(url="attachment://image.png")
                        embedVar.set_author(name=textwrap.dedent(f"""\
                        🧬 {active_pet['NAME']}: {active_pet['TYPE'].title()}: {pet_ability_power}{enhancer_suffix_mapping[active_pet['TYPE']]} 
                        🧬 Bond {bond} {bond_message} & Level {lvl} {lvl_message}
                        {titlemessage}
                        {armmessage}
                        {talisman_message}

                        🩸 {passive_name}      
                        🏃 {o_speed}
                        """))
                        embedVar.set_thumbnail(url=ctx.author.avatar_url)
                        if card_lvl != 999:
                            embedVar.set_footer(text=f"EXP Until Next Level: {'{:,}'.format(lvl_req - card_exp)}\nRebirth Buff: {trebirth_message} | {drebirth_message}\n♾️ {traitmessage}\n{warningmessage}")
                        else:
                            embedVar.set_footer(text=f"Max Level")
                        
                        await ctx.send(file=card_file, embed=embedVar)
                except Exception as ex:
                    trace = []
                    tb = ex.__traceback__
                    while tb is not None:
                        trace.append({
                            "filename": tb.tb_frame.f_code.co_filename,
                            "name": tb.tb_frame.f_code.co_name,
                            "lineno": tb.tb_lineno
                        })
                        tb = tb.tb_next
                    print(str({
                        'type': type(ex).__name__,
                        'message': str(ex),
                        'trace': trace
                    }))
                    await ctx.send("There's an issue with your build. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                    return
            else:
                await ctx.send(m.USER_NOT_REGISTERED, hidden=True)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'player': str(player),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))

    @cog_ext.cog_slash(description="Infuse Elemental Essence into Talisman's for aid",
                    options=[
                        create_option(
                            name="selection",
                            description="select an option to continue",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="👊 Physical",
                                    value="PHYSICAL",
                                ),
                                create_choice(
                                    name="🔥 Fire",
                                    value="FIRE",
                                ),
                                create_choice(
                                    name="❄️ Ice",
                                    value="ICE",
                                ),
                                create_choice(
                                    name="💧 Water",
                                    value="WATER",
                                ),
                                create_choice(
                                    name="⛰️ Earth",
                                    value="EARTH",
                                ),
                                create_choice(
                                    name="⚡️ Electric",
                                    value="ELECTRIC",
                                ),
                                create_choice(
                                    name="🌪️ Wind",
                                    value="WIND",
                                ),
                                create_choice(
                                    name="🔮 Psychic",
                                    value="PSYCHIC",
                                ),
                                create_choice(
                                    name="☠️ Death",
                                    value="DEATH",
                                ),
                                create_choice(
                                    name="❤️‍🔥 Life",
                                    value="LIFE"
                                ),
                                create_choice(
                                    name="🌕 Light",
                                    value="LIGHT",
                                ),
                                create_choice(
                                    name="🌑 Dark",
                                    value="DARK",
                                ),
                                create_choice(
                                    name="🧪 Poison",
                                    value="POISON",
                                ),
                                create_choice(
                                    name="🏹 Ranged",
                                    value="RANGED",
                                ),
                                create_choice(
                                    name="🧿 Spirit",
                                    value="SPIRIT",
                                ),
                                create_choice(
                                    name="♻️ Recoil",
                                    value="RECOIL",
                                ),
                                create_choice(
                                    name="⌛ Time",
                                    value="TIME",
                                ),
                                create_choice(
                                    name="🅱️ Bleed",
                                    value="BLEED",
                                ),
                                create_choice(
                                    name="🪐 Gravity",
                                    value="GRAVITY",
                                ),
                            ]
                        )
                    ]
        ,guild_ids=main.guild_ids)
    async def attune(self, ctx, selection):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return
            query = {'DID': str(ctx.author.id)}
            d = db.queryUser(query)
            vault = db.queryVault({'DID': d['DID']})
            talismans = vault["TALISMANS"]
            essence_list = vault["ESSENCE"]
            if crown_utilities.is_maxed_out(talismans):
                await ctx.send("Your Talisman's are maxed out.")
            else:
                response = crown_utilities.essence_cost(vault, selection, ctx.author.id)
                await ctx.send(response)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                    trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
            print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
            }))


    @cog_ext.cog_slash(description="View your talismen that are in storage", guild_ids=main.guild_ids)
    async def talismans(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            user = db.queryUser({"DID": str(ctx.author.id)})
            vault = db.queryVault({'DID': str(ctx.author.id)})
            talismans = vault["TALISMANS"]
           
            if crown_utilities.does_exist(talismans):
                embed_list = []
                equipped_talisman = user["TALISMAN"]

                for t in talismans:
                    current_durability = t['DUR']
                    m = ""
                    emoji = crown_utilities.set_emoji(t["TYPE"])
                    durability = t["DUR"]
                    name = t["TYPE"].title()
                    if equipped_talisman.upper() == name.upper():
                        m = "**Equipped**"
                    embedVar = discord.Embed(title= f"{name}", description=textwrap.dedent(f"""\
                    🔅 Element: {emoji} **{name.title()}**
                    ⚒️ {durability}
                    *{name} damage will ignore enemy Affinities.*
                    {m}
                    """), colour=0x7289da)
                    # embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                    # embedVar.set_thumbnail(url=show_img)
                    # embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                    embed_list.append(embedVar)


                buttons = [
                    manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                    manage_components.create_button(style=3, label="Unequip", custom_id="Unequip"),
                    # manage_components.create_button(style=3, label="Repair", custom_id="Repair"),
                    manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                ]
                custom_action_row = manage_components.create_actionrow(*buttons)


                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        updated_vault = db.queryVault({'DID': str(ctx.author.id)})
                        selected_talisman = str(button_ctx.origin_message.embeds[0].title)
                       
                        if button_ctx.custom_id == "Equip":
                            user_query = {'DID': str(ctx.author.id)}
                            response = db.updateUserNoFilter(user_query, {'$set': {'TALISMAN': selected_talisman.upper()}})
                            await button_ctx.send(f"**{selected_talisman} Talisman** equipped.")
                            self.stop = True
                        if button_ctx.custom_id == "Dismantle":
                            if selected_talisman.upper() == equipped_talisman.upper():
                                await button_ctx.send(f"You cannot dismantle an equipped Talisman.")
                            else:
                                response = crown_utilities.dismantle_talisman(selected_talisman.upper(), ctx.author.id)
                                await button_ctx.send(response)
                        if button_ctx.custom_id == "Unequip":
                            if selected_talisman.upper() == equipped_talisman.upper():
                                query = {'DID': str(ctx.author.id)}
                                user_update_query = {'$set': {'TALISMAN': 'NULL'}}
                                db.updateUserNoFilter(query, user_update_query)
                                await button_ctx.send(f"Your Talisman has been unequipped.")
                            else:
                                await button_ctx.send(f"You cannot unequip a Talisman that isn't equipped.")
                        # if button_ctx.custom_id == "Repair":
                        #     curseAmount = int(500)
                        #     element = name
                        #     negCurseAmount = 0 - abs(int(curseAmount))
                        #     query = {'DID': str(user['DID'])}
                        #     update_query = {'$inc': {'ESSENCE.$[type].' + "ESSENCE": negCurseAmount}}
                        #     filter_query = [{'type.' + "ELEMENT": element}]
                        #     response = db.updateVault(query, update_query, filter_query)
                        #     levels_gained = int(30 - current_durability)
                        #     new_durability = current_durability + levels_gained
                        #     full_repair = False
                        #     if new_durability > 30:
                        #         levels_gained = 30 - current_durability
                        #         full_repair=True
                        #     query = {'DID': str(ctx.author.id)}
                        #     update_query = {'$inc': {'TALISMANS.$[type].' + 'DUR': levels_gained}}
                        #     filter_query = [{'type.' + "TYPE": str(t['TYPE'])}]
                        #     resp = db.updateVault(query, update_query, filter_query)
                            
                        #     await button_ctx.send(f"{name}'s ⚒️ durability has increased by **{levels_gained}**!\n*Maximum Durability Reached!*")

                    else:
                        await ctx.send("This is not your card list.")

                await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
            else:
                await ctx.send("You currently have no Talismans. Attune Talismans using /attune")
                return
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))





    @cog_ext.cog_slash(description="View Card, Title and Arm Storage",
                    options=[
                        create_option(
                            name="mode",
                            description="Card: View CArd Storage, Title: View Title Storage, Arm: View Arm Storage",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="🎴 Card Storage",
                                    value="card"
                                ),
                                create_choice(
                                    name="🎗️ Title Storage",
                                    value="title"
                                ),
                                create_choice(
                                    name="🦾 Arm Storage",
                                    value="arm"
                                ),
                            ]
                        )
                    ]
        , guild_ids=main.guild_ids)
    async def storage(self, ctx : SlashContext, mode: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            vault = db.queryVault({'DID': str(ctx.author.id)})
            storage_allowed_amount = user['STORAGE_TYPE'] * 15
            if mode == "card":
                if not vault['STORAGE']:
                    await ctx.send("Your Card storage is empty.", hidden=True)
                    return

                list_of_cards = db.querySpecificCards(vault['STORAGE'])
                cards = [x for x in list_of_cards]
                dungeon_card_details = []
                tales_card_details = []
                destiny_card_details = []
                
                for card in cards:
                    moveset = card['MOVESET']
                    move3 = moveset[2]
                    move2 = moveset[1]
                    move1 = moveset[0]
                    basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
                    super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
                    ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])

                    
                    universe_crest = crown_utilities.crest_dict[card['UNIVERSE']]
                    index = vault['STORAGE'].index(card['NAME'])
                    level = ""
                    level_icon = "🔰"
                    for c in vault['CARD_LEVELS']:
                        if card['NAME'] == c['CARD']:
                            level = str(c['LVL'])
                            card_lvl = int(c['LVL'])
                    if card_lvl >= 200:
                        level_icon = "🔱"
                    if card_lvl >= 700:
                        level_icon ="⚜️"
                    if card_lvl >=999:
                        level_icon ="🏅"
                        
                    available = ""
                    if card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
                        dungeon_card_details.append(
                            f"[{str(index)}] {universe_crest} : :mahjong: **{card['TIER']}** **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
                    elif not card['HAS_COLLECTION']:
                        tales_card_details.append(
                            f"[{str(index)}] {universe_crest} : :mahjong: **{card['TIER']}** **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
                    elif card['HAS_COLLECTION']:
                        destiny_card_details.append(
                            f"[{str(index)}] {universe_crest} : :mahjong: **{card['TIER']}** **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")

                all_cards = []
                if tales_card_details:
                    for t in tales_card_details:
                        all_cards.append(t)

                if dungeon_card_details:
                    for d in dungeon_card_details:
                        all_cards.append(d)

                if destiny_card_details:
                    for de in destiny_card_details:
                        all_cards.append(de)

                total_cards = len(all_cards)

                # Adding to array until divisible by 10
                while len(all_cards) % 10 != 0:
                    all_cards.append("")
                # Check if divisible by 10, then start to split evenly

                if len(all_cards) % 10 == 0:
                    first_digit = int(str(len(all_cards))[:1])
                    if len(all_cards) >= 89:
                        if first_digit == 1:
                            first_digit = 10
                    # first_digit = 10
                    cards_broken_up = np.array_split(all_cards, first_digit)

                # If it's not an array greater than 10, show paginationless embed
                if len(all_cards) < 10:
                    embedVar = discord.Embed(title=f"💼 {user['DISNAME']}'s Card Storage", description="\n".join(all_cards), colour=0x7289da)
                    embedVar.set_footer(
                        text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(vault['STORAGE']))} Storage Available")
                    await ctx.send(embed=embedVar)

                embed_list = []
                for i in range(0, len(cards_broken_up)):
                    globals()['embedVar%s' % i] = discord.Embed(
                        title=f"💼 {user['DISNAME']}'s Storage",
                        description="\n".join(cards_broken_up[i]), colour=0x7289da)
                    globals()['embedVar%s' % i].set_footer(
                        text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(vault['STORAGE']))} Storage Available")
                    embed_list.append(globals()['embedVar%s' % i])

                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⬅️', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('➡️', "next")
                paginator.add_reaction('⏭️', "last")
                embeds = embed_list
                await paginator.run(embeds)
            elif mode == "title":
                if not vault['TSTORAGE']:
                    await ctx.send("Your Title storage is empty.", hidden=True)
                    return

                list_of_titles = db.querySpecificTitles(vault['TSTORAGE'])
                titles = [x for x in list_of_titles]
                dungeon_title_details = []
                tales_title_details = []
                boss_title_details = []
                unbound_title_details = []
                for title in titles:
                    title_title = title['TITLE']
                    title_show = title['UNIVERSE']
                    exclusive = title['EXCLUSIVE']
                    available = title['AVAILABLE']
                    title_passive = title['ABILITIES'][0]
                    title_passive_type = list(title_passive.keys())[0]
                    title_passive_value = list(title_passive.values())[0]


                   
                    universe_crest = crown_utilities.crest_dict[title_show]
                    index = vault['TSTORAGE'].index(title_title)

                    if title_show == "Unbound":
                        unbound_title_details.append(
                            f"[{str(index)}] {universe_crest} :crown: : **{title_title}**\n**🦠 {title_passive_type}**: *{title_passive_value}*\n")
                    elif not exclusive and not available:
                        boss_title_details.append(
                            f"[{str(index)}] {universe_crest} 👹 : **{title_title}**\n**🦠 {title_passive_type}**:  *{title_passive_value}*\n")
                    elif exclusive and available:
                        dungeon_title_details.append(
                            f"[{str(index)}] {universe_crest} :fire: : **{title_title}**\n**🦠 {title_passive_type}**: *{title_passive_value}*\n")
                    elif available and not exclusive:
                        tales_title_details.append(
                            f"[{str(index)}] {universe_crest} 🎗️ : **{title_title}**\n**🦠 {title_passive_type}**:  *{title_passive_value}*\n")

                all_titles = []
                
                if unbound_title_details:
                    for u in unbound_title_details:
                        all_titles.append(u)
                        
                if tales_title_details:
                    for t in tales_title_details:
                        all_titles.append(t)

                if dungeon_title_details:
                    for d in dungeon_title_details:
                        all_titles.append(d)

                if boss_title_details:
                    for de in boss_title_details:
                        all_titles.append(de)
                
                

                total_titles = len(all_titles)

                # Adding to array until divisible by 10
                while len(all_titles) % 10 != 0:
                    all_titles.append("")
                # Check if divisible by 10, then start to split evenly

                if len(all_titles) % 10 == 0:
                    first_digit = int(str(len(all_titles))[:1])
                    if len(all_titles) >= 89:
                        if first_digit == 1:
                            first_digit = 10
                    # first_digit = 10
                    titles_broken_up = np.array_split(all_titles, first_digit)

                # If it's not an array greater than 10, show paginationless embed
                if len(all_titles) < 10:
                    embedVar = discord.Embed(title=f"💼 {user['DISNAME']}'s Title Storage", description="\n".join(all_titles), colour=0x7289da)
                    embedVar.set_footer(
                        text=f"{total_titles} Total Titles\n{str(storage_allowed_amount - len(vault['TSTORAGE']))} Storage Available")
                    await ctx.send(embed=embedVar)

                embed_list = []
                for i in range(0, len(titles_broken_up)):
                    globals()['embedVar%s' % i] = discord.Embed(
                        title=f"💼 {user['DISNAME']}'s Title Storage",
                        description="\n".join(titles_broken_up[i]), colour=0x7289da)
                    globals()['embedVar%s' % i].set_footer(
                        text=f"{total_titles} Total Titles\n{str(storage_allowed_amount - len(vault['TSTORAGE']))} Storage Available")
                    embed_list.append(globals()['embedVar%s' % i])

                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⬅️', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('➡️', "next")
                paginator.add_reaction('⏭️', "last")
                embeds = embed_list
                await paginator.run(embeds)
            elif mode == "arm":
                if not vault['ASTORAGE']:
                    await ctx.send("Your Arm storage is empty.", hidden=True)
                    return

           
                storage_card_names = []
                for name in vault['ASTORAGE']:
                    storage_card_names.append(name['ARM'])
           
                list_of_arms = db.querySpecificArms(storage_card_names)

                arms = [x for x in list_of_arms]
                dungeon_arm_details = []
                tales_arm_details = []
                boss_arm_details = []
                unbound_arm_details = []
                icon = ""
                for arm in arms:
                    durability = 0
                    for name in vault['ASTORAGE']:
                        if name['ARM'] == arm['ARM']:
                            durability = int(name['DUR'])
                    element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
                    arm_name = arm['ARM']
                    arm_show = arm['UNIVERSE']
                    exclusive = arm['EXCLUSIVE']
                    available = arm['AVAILABLE']
                    element = arm['ELEMENT']
                    if element:
                        element_name = element.title()
                        element = crown_utilities.set_emoji(element)
                    else:
                        element = "🦠"
                    arm_passive = arm['ABILITIES'][0]
                        # Arm Passive
                    arm_passive_type = list(arm_passive.keys())[0]
                    arm_passive_value = list(arm_passive.values())[0]
                    
                    icon = element
                    if arm_passive_type == "SHIELD":
                        icon = "🌐"
                    if arm_passive_type == "PARRY":
                        icon = "🔄"
                    if arm_passive_type == "BARRIER":
                        icon = "💠"
                    if arm_passive_type == "SIPHON":
                        icon = "💉"

                   
                    universe_crest = crown_utilities.crest_dict[arm_show]
                    index = vault['ASTORAGE'].index({'ARM': arm_name, 'DUR' : durability})

                    if arm_show == "Unbound":
                        unbound_arm_details.append(
                            f"[{str(index)}] {universe_crest} :muscle: {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** : *{arm_passive_value}*\n")
                    elif not exclusive and not available:
                        boss_arm_details.append(
                            f"[{str(index)}] {universe_crest} 👹 {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** :  *{arm_passive_value}*\n")
                    elif exclusive and available:
                        dungeon_arm_details.append(
                            f"[{str(index)}] {universe_crest} :fire: {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** : *{arm_passive_value}*\n")
                    elif available and not exclusive:
                        tales_arm_details.append(
                            f"[{str(index)}] {universe_crest} 🦾 {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** :  *{arm_passive_value}*\n")

                all_arms = []
                if unbound_arm_details:
                    for u in unbound_arm_details:
                        all_arms.append(u)
                        
                if tales_arm_details:
                    for t in tales_arm_details:
                        all_arms.append(t)

                if dungeon_arm_details:
                    for d in dungeon_arm_details:
                        all_arms.append(d)

                if boss_arm_details:
                    for de in boss_arm_details:
                        all_arms.append(de)

                

                total_arms = len(all_arms)

                # Adding to array until divisible by 10
                while len(all_arms) % 10 != 0:
                    all_arms.append("")
                # Check if divisible by 10, then start to split evenly

                if len(all_arms) % 10 == 0:
                    first_digit = int(str(len(all_arms))[:1])
                    if len(all_arms) >= 89:
                        if first_digit == 1:
                            first_digit = 10
                    # first_digit = 10
                    arms_broken_up = np.array_split(all_arms, first_digit)

                # If it's not an array greater than 10, show paginationless embed
                if len(all_arms) < 10:
                    embedVar = discord.Embed(title=f"💼 {user['DISNAME']}'s Arm Storage", description="\n".join(all_arms), colour=0x7289da)
                    embedVar.set_footer(
                        text=f"{total_arms} Total Arms\n{str(storage_allowed_amount - len(vault['ASTORAGE']))} Storage Available")
                    await ctx.send(embed=embedVar)

                embed_list = []
                for i in range(0, len(arms_broken_up)):
                    globals()['embedVar%s' % i] = discord.Embed(
                        title=f"💼 {user['DISNAME']}'s Arm Storage",
                        description="\n".join(arms_broken_up[i]), colour=0x7289da)
                    globals()['embedVar%s' % i].set_footer(
                        text=f"{total_arms} Total Arms\n{str(storage_allowed_amount - len(vault['ASTORAGE']))} Storage Available")
                    embed_list.append(globals()['embedVar%s' % i])

                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⬅️', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('➡️', "next")
                paginator.add_reaction('⏭️', "last")
                embeds = embed_list
                await paginator.run(embeds)
            else:
                await ctx.send("Title and Arm Storage Coming Soon!")
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'player': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            

    @cog_ext.cog_slash(description="View all of your titles", guild_ids=main.guild_ids)
    async def titles(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        storage_type = d['STORAGE_TYPE']
        if vault:
            try:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                balance = vault['BALANCE']
                current_title = d['TITLE']
                titles_list = vault['TITLES']
                total_titles = len(titles_list)
                storage = vault['TSTORAGE']
                titles=[]
                current_gems = []
                for gems in vault['GEMS']:
                    current_gems.append(gems['UNIVERSE'])
                icon = ":coin:"
                if balance >= 150000:
                    icon = ":money_with_wings:"
                elif balance >=100000:
                    icon = ":moneybag:"
                elif balance >= 50000:
                    icon = ":dollar:"


                embed_list = []
                for title in titles_list:
                    index = titles_list.index(title)
                    resp = db.queryTitle({"TITLE": str(title)})
                    title_passive = resp['ABILITIES'][0]
                    title_passive_type = list(title_passive.keys())[0]
                    title_passive_value = list(title_passive.values())[0]
                    title_available = resp['AVAILABLE']
                    title_exclusive = resp['EXCLUSIVE']
                    icon = "🎗️"
                    if resp['UNIVERSE'] == "Unbound":
                        icon = ":crown:"
                    elif title_available and title_exclusive:
                        icon = ":fire:"
                    elif title_available == False and title_exclusive ==False:
                        icon = ":japanese_ogre:"
                    
                    
                    embedVar = discord.Embed(title= f"{resp['TITLE']}", description=textwrap.dedent(f"""
                    {icon} **[{index}]**
                    🦠 **{title_passive_type}:** {title_passive_value}
                    :earth_africa: **Universe:** {resp['UNIVERSE']}"""), 
                    colour=0x7289da)
                    embedVar.set_thumbnail(url=avatar)
                    embedVar.set_footer(text=f"{title_passive_type}: {title_enhancer_mapping[title_passive_type]}")
                    embed_list.append(embedVar)
                
                buttons = [
                    manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                    manage_components.create_button(style=1, label="Resell", custom_id="Resell"),
                    manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                    manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                    manage_components.create_button(style=2, label="Swap/Store", custom_id="Storage")
                ]
                custom_action_row = manage_components.create_actionrow(*buttons)

                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        updated_vault = db.queryVault({'DID': d['DID']})
                        sell_price = 0
                        selected_title = str(button_ctx.origin_message.embeds[0].title)
                        if button_ctx.custom_id == "Equip":
                            if selected_title in updated_vault['TITLES']:
                                selected_universe = custom_function
                                custom_function.selected_universe = selected_title
                                user_query = {'DID': str(ctx.author.id)}
                                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': selected_title}})
                                await button_ctx.send(f"🎗️ **{selected_title}** equipped.")
                                self.stop = True
                            else:
                                await button_ctx.send(f"**{selected_title}** is no longer in your vault.")                           
                        
                        elif button_ctx.custom_id == "Resell":
                            title_data = db.queryTitle({'TITLE': selected_title})
                            title_name = title_data['TITLE']
                            sell_price = sell_price + (title_data['PRICE'] * .10)
                            if title_name == current_title:
                                await button_ctx.send("You cannot resell equipped titles.")
                            elif title_name in updated_vault['TITLES']:
                                sell_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                                msg = await button_ctx.send(f"Are you sure you want to sell **{title_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                                    if button_ctx.custom_id == "no":
                                        await button_ctx.send("Sell cancelled. Please press the Exit button if you are done reselling titles.")
                                    if button_ctx.custom_id == "yes":
                                        db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TITLES': title_name}})
                                        await crown_utilities.bless(sell_price, ctx.author.id)
                                        await msg.delete()
                                        await button_ctx.send(f"**{title_name}** has been sold.")
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with selling one or all of your items.")
                                    return
                            else:
                                await button_ctx.send(f"**{title_name}** is no longer in your vault.")
                        
                        elif button_ctx.custom_id == "Dismantle":
                            title_data = db.queryTitle({'TITLE': selected_title})
                            title_name = title_data['TITLE']
                            selected_universe = title_data['UNIVERSE']
                            dismantle_amount = 1000
                            if title_name == current_title:
                                await button_ctx.send("You cannot resell equipped titles.")
                            elif title_name in updated_vault['TITLES']:
                                dismantle_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                                msg = await button_ctx.send(f"Are you sure you want to dismantle **{title_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                    if button_ctx.custom_id == "no":
                                        await button_ctx.send("Dismantle cancelled. ")
                                    if button_ctx.custom_id == "yes":
                                        if selected_universe in current_gems:
                                            query = {'DID': str(ctx.author.id)}
                                            update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                            filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                            response = db.updateVault(query, update_query, filter_query)
                                        else:
                                            response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                        db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TITLES': title_name}})
                                        await crown_utilities.bless(sell_price, ctx.author.id)
                                        await msg.delete()
                                        await button_ctx.send(f"**{title_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.")
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with selling one or all of your items.")
                                    return
                            else:
                                await button_ctx.send(f"**{title_name}** is no longer in your vault.")

                        elif button_ctx.custom_id == "Trade":
                            title_data = db.queryTitle({'TITLE' : selected_title})
                            title_name = title_data['TITLE']
                            if title_name == current_title:
                                await button_ctx.send("You cannot trade equipped titles.")
                                return
                            sell = title_data['PRICE'] * .10
                            mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                            mvalidation=False
                            bvalidation=False
                            item_already_in_trade=False
                            if mtrade:
                                if selected_title in mtrade['MTITLES']:
                                    await ctx.send(f"{ctx.author.mention} title already in **Trade**")
                                    item_already_in_trade=True
                                mvalidation=True
                            else:
                                btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                                if btrade:
                                    if selected_title in btrade['BTITLES']:
                                        await ctx.send(f"{ctx.author.mention} title already in **Trade**")
                                        item_already_in_trade=True
                                    bvalidation=True
                                else:
                                    await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                    return
                            if item_already_in_trade:
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Woudl you like to remove **{selected_title}** from the **Trade**?", components=[trade_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Happy Trading")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        neg_sell_price = 0 - abs(int(sell_price))
                                        if mvalidation:
                                            trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$pull" : {'MTITLES': selected_title}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                            update_query = {"$pull" : {'BTITLES': selected_title}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                            elif mvalidation == True or bvalidation ==True:    #If user is valid
                                sell_price = title_data['PRICE'] * .10
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Are you sure you want to trade **{selected_title}**", components=[trade_buttons_action_row])
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Not this time. ")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        if mvalidation:
                                            trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$push" : {'MTITLES': selected_title}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Traded.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                            update_query = {"$push" : {'BTITLES': selected_title}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Traded.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                                                        
                        elif button_ctx.custom_id == "Storage":
                            await button_ctx.defer(ignore=True)
                            storage_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Swap Storage Title",
                                            custom_id="swap"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.red,
                                            label="Add to Storage",
                                            custom_id="store"
                                        )
                                    ]
                            storage_buttons_action_row = manage_components.create_actionrow(*storage_buttons)
                            msg = await ctx.send(f"Would you like to Swap Titles or Add Title to Storage", components=[storage_buttons_action_row])
                            def check(button_ctx):
                                return button_ctx.author == ctx.author
                            try:
                                button_ctx: ComponentContextStorage = await manage_components.wait_for_component(self.bot, components=[storage_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "swap":
                                    await button_ctx.defer(ignore=True)
                                    await msg.delete()
                                    await ctx.send(f"{ctx.author.mention}, Which title number would you like to swap with in storage?")
                                    def check(msg):
                                        return msg.author == ctx.author

                                    try:
                                        msg = await self.bot.wait_for('message', check=check, timeout=30)
                                        author = msg.author
                                        content = msg.content
                                        # print("Author: " + str(author))
                                        # print("Content: " + str(content))
                                        # print(msg)
                                        if storage[int(msg.content)]:
                                            swap_with = storage[int(msg.content)]
                                            query = {'DID': str(msg.author.id)}
                                            update_storage_query = {
                                                '$pull': {'TITLES': selected_title},
                                                '$addToSet': {'TSTORAGE': selected_title},
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)

                                            update_storage_query = {
                                                '$pull': {'TSTORAGE': swap_with},
                                                '$addToSet': {'TCARDS': swap_with}
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)

                                            await msg.delete()
                                            await ctx.send(f"**{selected_title}** has been swapped with **{swap_with}**")
                                            return
                                        else:
                                            await ctx.send("The card number you want to swap with does not exist.")
                                            return

                                    except Exception as e:
                                        return False
                                if button_ctx.custom_id == "store":
                                    await button_ctx.defer(ignore=True)
                                    
                                    try:
                                        author = msg.author
                                        content = msg.content
                                        # print("Author: " + str(author))
                                        # print("Content: " + str(content))
                                        if len(storage) <= (storage_type * 15):
                                            query = {'DID': str(ctx.author.id)}
                                            update_storage_query = {
                                                '$pull': {'TITLES': selected_title},
                                                '$addToSet': {'TSTORAGE': selected_title},
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)
                                            
                                            await msg.delete()
                                            await ctx.send(f"**{selected_title}** has been added to storage")
                                            return
                                        else:
                                            await ctx.send("Not enough space in storage")
                                            return

                                    except Exception as e:
                                        return False
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                            
                            self.stop = True
                    else:
                        await ctx.send("This is not your Title list.")


                await Paginator(bot=self.bot, ctx=ctx,useQuitButton=True, disableAfterTimeout=True,pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
        
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("There's an issue with your Titles list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                return
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

    @cog_ext.cog_slash(description="View all of your arms", guild_ids=main.guild_ids)
    async def arms(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        
        storage_type = d['STORAGE_TYPE']
        if vault:
            try:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                current_arm = d['ARM']
                balance = vault['BALANCE']
                arms_list = vault['ARMS']
                total_arms = len(arms_list)
                storage = vault['ASTORAGE']
                arms=[]
                current_gems = []
                for gems in vault['GEMS']:
                    current_gems.append(gems['UNIVERSE'])

                icon = ":coin:"
                if balance >= 150000:
                    icon = ":money_with_wings:"
                elif balance >=100000:
                    icon = ":moneybag:"
                elif balance >= 50000:
                    icon = ":dollar:"

                embed_list = []
                for arm in arms_list:
                    index = arms_list.index(arm)
                    resp = db.queryArm({"ARM": str(arm['ARM'])})
                    element = resp['ELEMENT']
                    arm_passive = resp['ABILITIES'][0]
                    arm_passive_type = list(arm_passive.keys())[0]
                    arm_passive_value = list(arm_passive.values())[0]
                    arm_available = resp['AVAILABLE']
                    arm_exclusive = resp['EXCLUSIVE']
                    icon = "🦾"
                    if arm_available and arm_exclusive:
                        icon = ":fire:"
                    elif arm_available == False and arm_exclusive ==False:
                        icon = ":japanese_ogre:"
                    element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
                    if element and arm_passive_type in element_available:
                        element_name = element
                        element = crown_utilities.set_emoji(element)
                        arm_type = f"**{arm_passive_type.title()} {element_name.title()} Attack**"
                        arm_message = f"{element} **{resp['ARM']}:** {arm_passive_value}"
                        footer = f"The new {arm_passive_type.title()} attack will reflect on your card when equipped"

                    else:
                        arm_type = f"**Unique Passive**"
                        arm_message = f"🦠 **{arm_passive_type.title()}:** {arm_passive_value}"
                        footer = f"{arm_passive_type}: {enhancer_mapping[arm_passive_type]}"



                    embedVar = discord.Embed(title= f"{resp['ARM']}", description=textwrap.dedent(f"""
                    {icon} **[{index}]**

                    {arm_type}
                    {arm_message}
                    :earth_africa: **Universe:** {resp['UNIVERSE']}
                    ⚒️ {arm['DUR']}
                    """), 
                    colour=0x7289da)
                    embedVar.set_thumbnail(url=avatar)
                    embedVar.set_footer(text=f"{footer}")
                    embed_list.append(embedVar)
                
                buttons = [
                    manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                    manage_components.create_button(style=1, label="Resell", custom_id="Resell"),
                    manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                    manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                    manage_components.create_button(style=2, label="Swap/Store", custom_id="Storage")
                ]
                custom_action_row = manage_components.create_actionrow(*buttons)

                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        u_vault = db.queryVault({'DID': d['DID']})
                        updated_vault = []
                        storage = u_vault['ASTORAGE']
                        for arm in u_vault['ARMS']:
                            updated_vault.append(arm['ARM'])
                        
                        sell_price = 0
                        selected_arm = str(button_ctx.origin_message.embeds[0].title)
                        if button_ctx.custom_id == "Equip":
                            if selected_arm in updated_vault:
                                durability = 0
                                for names in storage:
                                    if names['ARM'] == selected_arm:
                                        durability = names['DUR']
                                selected_universe = custom_function
                                custom_function.selected_universe = selected_arm
                                user_query = {'DID': str(ctx.author.id)}
                                response = db.updateUserNoFilter(user_query, {'$set': {'ARM': selected_arm}})
                                await button_ctx.send(f"🦾 **{selected_arm}** equipped.")
                                self.stop = True
                            else:
                                await button_ctx.send(f"**{selected_arm}** is no longer in your vault.")
                        
                        elif button_ctx.custom_id == "Resell":
                            arm_data = db.queryArm({'ARM': selected_arm})
                            arm_name = arm_data['ARM']
                            sell_price = sell_price + (arm_data['PRICE'] * .07)
                            if arm_name == current_arm:
                                await button_ctx.send("You cannot resell equipped arms.")
                            elif arm_name in updated_vault:
                                sell_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                                msg = await button_ctx.send(f"Are you sure you want to sell **{arm_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                                    if button_ctx.custom_id == "no":
                                        await button_ctx.send("Sell cancelled. Please press the Exit button if you are done reselling titles.")
                                    if button_ctx.custom_id == "yes":
                                        db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ARMS': {'ARM': str(arm_name)}}})
                                        await crown_utilities.bless(sell_price, ctx.author.id)
                                        await msg.delete()
                                        await button_ctx.send(f"**{arm_name}** has been sold.")
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with selling one or all of your items.")
                                    return
                            else:
                                await button_ctx.send(f"**{arm_name}** is no longer in your vault.")       
                        
                        elif button_ctx.custom_id == "Dismantle":
                            arm_data = db.queryArm({'ARM': selected_arm})
                            arm_name = arm_data['ARM']
                            element = arm_data['ELEMENT']
                            essence_amount = 100
                            arm_passive = arm_data['ABILITIES'][0]
                            arm_passive_type = list(arm_passive.keys())[0]
                            arm_passive_value = list(arm_passive.values())[0]
                            move_types = ["BASIC", "SPECIAL", "ULTIMATE"]
                            if arm_data["EXCLUSIVE"]:
                                essence_amount = 250
                            selected_universe = arm_data['UNIVERSE']
                            dismantle_amount = 10000
                            if arm_name == current_arm:
                                await button_ctx.send("You cannot dismantle equipped arms.")
                            elif arm_name == "Stock" or arm_name == "Reborn Stock" or arm_name == "Deadgun" or arm_name == "Glaive" or arm_name == "Kings Glaive" or arm_name == "Legendary Weapon":
                                await button_ctx.send("You cannot dismantle Stock arms.")
                            elif arm_name in updated_vault:
                                dismantle_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                                msg = await button_ctx.send(f"Are you sure you want to dismantle **{arm_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                    if button_ctx.custom_id == "no":
                                        await button_ctx.send("Dismantle cancelled. ")
                                    if button_ctx.custom_id == "yes":
                                        if selected_universe in current_gems:
                                            query = {'DID': str(ctx.author.id)}
                                            update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                            filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                            response = db.updateVault(query, update_query, filter_query)
                                        else:
                                            response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                        mess = ""
                                        if arm_passive_type in move_types:
                                            em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                            mess = f" Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence."
                                        db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ARMS': {'ARM': str(arm_name)}}})
                                        await crown_utilities.bless(sell_price, ctx.author.id)
                                        await msg.delete()
                                        await button_ctx.send(f"**{arm_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.{mess}")
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with selling one or all of your items.")
                                    return
                            else:
                                await button_ctx.send(f"**{arm_name}** is no longer in your vault.")

                        elif button_ctx.custom_id == "Trade":
                            arm_data = db.queryArm({'ARM' : selected_arm})
                            arm_name = arm_data['ARM']
                            if arm_name == current_arm:
                                await button_ctx.send("You cannot trade equipped arms.")
                                return
                            sell_price = arm_data['PRICE'] * .10
                            mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                            mvalidation=False
                            bvalidation=False
                            item_already_in_trade=False
                            if mtrade:
                                if selected_arm in mtrade['MARMS']:
                                    await ctx.send(f"{ctx.author.mention} arm already in **Trade**")
                                    item_already_in_trade=True
                                mvalidation=True
                            else:
                                btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                                if btrade:
                                    if selected_arm in btrade['BARMS']:
                                        await ctx.send(f"{ctx.author.mention} arm already in **Trade**")
                                        item_already_in_trade=True
                                    bvalidation=True
                                else:
                                    await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                    return
                            if item_already_in_trade:
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Woudl you like to remove **{selected_arm}** from the **Trade**?", components=[trade_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Happy Trading")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        neg_sell_price = 0 - abs(int(sell_price))
                                        if mvalidation:
                                            trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$pull" : {'MARMS': selected_arm}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                            update_query = {"$pull" : {'BARMS': selected_arm}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                            elif mvalidation == True or bvalidation ==True:    #If user is valid
                                sell_price = arm_data['PRICE'] * .10
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Are you sure you want to trade **{selected_arm}**", components=[trade_buttons_action_row])
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Not this time. ")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        if mvalidation:
                                            trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$push" : {'MARMS': selected_arm}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Traded.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                            update_query = {"$push" : {'BARMS': selected_arm}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Traded.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                                        
                        elif button_ctx.custom_id == "Storage":
                            await button_ctx.defer(ignore=True)
                            storage_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Swap Storage Arm",
                                            custom_id="swap"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.red,
                                            label="Add to Storage",
                                            custom_id="store"
                                        )
                                    ]
                            storage_buttons_action_row = manage_components.create_actionrow(*storage_buttons)
                            msg = await ctx.send(f"Would you like to Swap Arms or Add Arm to Storage", components=[storage_buttons_action_row])
                            def check(button_ctx):
                                return button_ctx.author == ctx.author
                            try:
                                button_ctx: ComponentContextStorage = await manage_components.wait_for_component(self.bot, components=[storage_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "swap":
                                    await button_ctx.defer(ignore=True)
                                    await msg.delete()
                                    await ctx.send(f"{ctx.author.mention}, Which arm number would you like to swap with in storage?")
                                    def check(msg):
                                        return msg.author == ctx.author

                                    try:
                                        msg = await self.bot.wait_for('message', check=check, timeout=30)
                                        author = msg.author
                                        content = msg.content
                                        # print("Author: " + str(author))
                                        # print("Content: " + str(content))
                                        # print(msg)
                                        durability = 0
                                        for names in storage:
                                            if names['ARM'] == selected_arm:
                                                durability = names['DUR']
                                        if storage[int(msg.content)]:
                                            swap_with = storage[int(msg.content)]
                                            query = {'DID': str(msg.author.id)}
                                            update_storage_query = {
                                                '$pull': {'ARMS': {'ARM' : str(selected_arm)}},
                                                '$addToSet': {'ASTORAGE' : { 'ARM' : str(selected_arm), 'DUR' : int(durability)}},
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)

                                            update_storage_query = {
                                                '$pull': {'ASTORAGE': swap_with},
                                                '$addToSet': {'ARMS': swap_with}
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)

                                            await msg.delete()
                                            await ctx.send(f"**{selected_card}** has been swapped with **{swap_with}**")
                                            return
                                        else:
                                            await ctx.send("The card number you want to swap with does not exist.")
                                            return

                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                                        return
                                if button_ctx.custom_id == "store":
                                    await button_ctx.defer(ignore=True)
                                    
                                    try:
                                        author = msg.author
                                        content = msg.content
                                        # print("Author: " + str(author))
                                        # print("Content: " + str(content))
                                        durability = 0
                                        for names in u_vault['ARMS']:
                                            if names['ARM'] == selected_arm:
                                                durability = names['DUR']
                                        if len(storage) <= (storage_type * 15):
                                            query = {'DID': str(ctx.author.id)}
                                            update_storage_query = {
                                                '$pull': {'ARMS': {'ARM' : str(selected_arm)}},
                                                '$addToSet': {'ASTORAGE': { 'ARM' : str(selected_arm), 'DUR' : int(durability)}},
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)
                                            
                                            await msg.delete()
                                            await ctx.send(f"**{selected_arm}** has been added to storage")
                                            return
                                        else:
                                            await ctx.send("Not enough space in storage")
                                            return

                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92.", hidden=True)
                                        return
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                                return
                    else:
                        await ctx.send("This is not your Arms list.")        

                await Paginator(bot=self.bot, ctx=ctx ,useQuitButton=True, disableAfterTimeout=True, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
        
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                return
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

    @cog_ext.cog_slash(description="View all of your gems", guild_ids=main.guild_ids)
    async def gems(self, ctx: SlashContext):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        vault = db.queryVault({'DID': str(ctx.author.id)})
        current_gems = vault['GEMS']
        if current_gems:
            number_of_gems_universes = len(current_gems)

            gem_details = []
            for gd in current_gems:
                heart = ""
                soul = ""
                if gd['UNIVERSE_HEART']:
                    heart = "💟"
                else:
                    heart = "💔"

                if gd['UNIVERSE_SOUL']:
                    soul = "🌹"
                else:
                    soul = "🥀"

                gem_details.append(
                    f"🌍 **{gd['UNIVERSE']}**\n💎 {'{:,}'.format(gd['GEMS'])}\nUniverse Heart {heart}\nUniverse Soul {soul}\n")

            # Adding to array until divisible by 10
            while len(gem_details) % 10 != 0:
                gem_details.append("")
            # Check if divisible by 10, then start to split evenly

            if len(gem_details) % 10 == 0:
                first_digit = int(str(len(gem_details))[:1])
                if len(gem_details) >= 89:
                    if first_digit == 1:
                        first_digit = 10
                gems_broken_up = np.array_split(gem_details, first_digit)

            # If it's not an array greater than 10, show paginationless embed
            if len(gem_details) < 10:
                embedVar = discord.Embed(title=f"Gems", description="\n".join(gem_details),
                                        colour=0x7289da)
                await ctx.send(embed=embedVar)

            embed_list = []
            for i in range(0, len(gems_broken_up)):
                globals()['embedVar%s' % i] = discord.Embed(title=f"Gems",
                                                            description="\n".join(gems_broken_up[i]), colour=0x7289da)
                embed_list.append(globals()['embedVar%s' % i])

            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⬅️', "back")
            paginator.add_reaction('🔐', "lock")
            paginator.add_reaction('➡️', "next")
            paginator.add_reaction('⏭️', "last")
            embeds = embed_list
            await paginator.run(embeds)
        else:
            await ctx.send("You currently own no 💎.")

    @cog_ext.cog_slash(description="View all of your collected essence", guild_ids=main.guild_ids)
    async def essence(self, ctx: SlashContext):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        vault = db.queryVault({'DID': str(ctx.author.id)})
        current_essence = vault['ESSENCE']
        if current_essence:
            # number_of_gems_universes = len(current_essence)

            essence_details = []
            for ed in current_essence:
                element = ed["ELEMENT"]
                essence = ed["ESSENCE"]
                element_emoji = crown_utilities.set_emoji(element)
                essence_details.append(
                    f"{element_emoji} **{element.title()} Essence: ** {'{:,}'.format(essence)}\n")

            # Adding to array until divisible by 10
            while len(essence_details) % 10 != 0:
                essence_details.append("")
            # Check if divisible by 10, then start to split evenly

            if len(essence_details) % 10 == 0:
                first_digit = int(str(len(essence_details))[:1])
                if len(essence_details) >= 89:
                    if first_digit == 1:
                        first_digit = 10
                essence_broken_up = np.array_split(essence_details, first_digit)

            # If it's not an array greater than 10, show paginationless embed
            if len(essence_details) < 10:
                embedVar = discord.Embed(title=f"🪔 Essence", description="\n".join(essence_details),
                                        colour=0x7289da)
                await ctx.send(embed=embedVar)

            embed_list = []
            for i in range(0, len(essence_broken_up)):
                globals()['embedVar%s' % i] = discord.Embed(title=f"🪔 Essence",
                                                            description="\n".join(essence_broken_up[i]), colour=0x7289da)
                embed_list.append(globals()['embedVar%s' % i])

            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⬅️', "back")
            paginator.add_reaction('🔐', "lock")
            paginator.add_reaction('➡️', "next")
            paginator.add_reaction('⏭️', "last")
            embeds = embed_list
            await paginator.run(embeds)
        else:
            await ctx.send("You currently own no 💎.")



    @cog_ext.cog_slash(description="Open the blacksmith", guild_ids=main.guild_ids)
    async def blacksmith(self, ctx):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        #    if user['LEVEL'] < 11:
        #       await ctx.send(f"🔓 Unlock the Trinket Shop by completing Floor 10 of the 🌑 Abyss! Use /solo to enter the abyss.")
        #       return
        patron_flag = user['PATRON']
        current_arm = user['ARM']
        storage_type = user['STORAGE_TYPE'] #Storage Update
        storage_pricing = (storage_type + 1) * 1500000
        storage_pricing_text = f"{'{:,}'.format(storage_pricing)}" 
        storage_tier_message = (storage_type + 1)
        preset_upgrade = user['U_PRESET']
        preset_message = "Preset Upgraded!"
        if preset_upgrade == False:
            preset_message = "10,000,000"
        gabes = user['TOURNAMENT_WINS']
        gabes_message = "Purse Purchased!"
        gabes_explain = ""
        
        storage_message = f"{str(storage_type + 1)}"
        
        if storage_type >=10:
            storage_pricing_text = "Max Storage Level"
            storage_tier_message = "MAX"
            storage_message = "MAX"
        
        arm_info = db.queryArm({'ARM': str(current_arm)})
        boss_arm = False
        dungeon_arm = False
        boss_message = "Nice Arm!"
        arm_cost = '{:,}'.format(100000)
        durability_message = f"{arm_cost}"
        if arm_info['AVAILABLE'] == False and arm_info['EXCLUSIVE'] == False:
            boss_arm = True
        elif arm_info['AVAILABLE'] == True and arm_info['EXCLUSIVE'] == True:
            dungeon_arm= True
            arm_cost = '{:,}'.format(250000)
            durability_message = f"{arm_cost}"
        if boss_arm:
            boss_message = "Cannot Repair"
            durability_message = "UNAVAILABLE"
        elif dungeon_arm:
            boss_message = "Dungeon eh?!"
        vault_query = {'DID' : str(ctx.author.id)}
        vault = db.altQueryVault(vault_query)
        current_card = user['CARD']
        current_title = user['TITLE']
        current_pet = user['PET']
        has_gabes_purse = user['TOURNAMENT_WINS']
        if not has_gabes_purse:
            gabes_message = "25,000,000"
            gabes_explain = "Purchase **Gabe's Purse** to Keep ALL ITEMS during **/rebirth**"
        balance = vault['BALANCE']
        icon = ":coin:"
        if balance >= 1000000:
            icon = ":money_with_wings:"
        elif balance >=650000:
            icon = ":moneybag:"
        elif balance >= 150000:
            icon = ":dollar:"
        
        owned_arms = []
        current_durability = 0
        for arms in vault['ARMS']:
            if arms['ARM'] == current_arm:
                current_durability = arms['DUR']

        card_info = {}
        for level in vault['CARD_LEVELS']:
            if level['CARD'] == current_card:
                card_info = level

        lvl = card_info['LVL']
        

        
        hundred_levels = 650000
        thirty_levels = 220000
        ten_levels = 80000
        
        licon = "🔰"
        if lvl>= 200:
            licon ="🔱"
        if lvl>= 700:
            licon ="⚜️"
        if lvl >= 999:
            licon = "🏅"

        if lvl >= 200 and lvl < 299:
            hundred_levels = 30000000
            thirty_levels = 20000000
            ten_levels = 10000000
        elif lvl >= 300 and lvl < 399:
            hundred_levels = 70000000
            thirty_levels = 50000000
            ten_levels = 25000000
        elif lvl >= 400 and lvl < 499:
            hundred_levels = 90000000
            thirty_levels = 75000000
            ten_levels = 50000000
        elif lvl >= 500 and lvl < 599:
            hundred_levels = 150000000
            thirty_levels = 100000000
            ten_levels = 75000000
        elif lvl >= 600 and lvl < 699:
            hundred_levels = 300000000
            thirty_levels = 200000000
            ten_levels = 100000000
        elif lvl >= 700 and lvl <= 800:
            hundred_levels = 750000000
            thirty_levels = 500000000
            ten_levels = 250000000
        elif lvl >= 800 and lvl <= 900:
            hundred_levels = 1000000000
            thirty_levels = 800000000
            ten_levels = 500000000
        elif lvl >= 900 and lvl <= 1000:
            hundred_levels = 5000000000
            thirty_levels = 2500000000
            ten_levels = 1000000000
        sell_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label="🔋 1️⃣",
                    custom_id="1"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="🔋 2️⃣",
                    custom_id="2"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="🔋 3️⃣",
                    custom_id="3"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="⚒️ 4️⃣",
                    custom_id="5"
                ),
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Cancel",
                    custom_id="cancel"
                )
            ]
        
        util_sell_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Gabe's Purse 👛",
                    custom_id="4"
                ),
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Storage 💼",
                    custom_id="6"
                ),
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Preset 🔖",
                    custom_id="7"
                )
        ]
        
        sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
        util_sell_buttons_action_row = manage_components.create_actionrow(*util_sell_buttons)
        embedVar = discord.Embed(title=f"🔨 | **Blacksmith** - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
        Welcome {ctx.author.mention}!
        Purchase **Card XP** and **Arm Durability**!
        🎴 Card:  **{current_card}** {licon}**{lvl}**
        🦾 Arm: **{current_arm}** *{boss_message}* ⚒️*{current_durability}*
        

        🔋 1️⃣ **10 Levels** for :coin: **{'{:,}'.format(ten_levels)}**
        
        🔋 2️⃣ **30 Levels** for :dollar: **{'{:,}'.format(thirty_levels)}**

        🔋 3️⃣ **100 Levels** for :moneybag: **{'{:,}'.format(hundred_levels)}**

        ⚒️ 4️⃣ **50 Durability** for :dollar: **{durability_message}**

        💼 **Storage Tier {storage_message}**: :money_with_wings: **{storage_pricing_text}**
        
        🔖 **Preset Upgrade** *+ 2 Slots* :money_with_wings: **{preset_message}**

        👛 **Gabe's Purse**: :money_with_wings: **{gabes_message}**
        {gabes_explain}

        What would you like to buy?
        """), colour=0xf1c40f)
        embedVar.set_footer(text="Boosts are used immediately upon purchase. Click cancel to exit purchase.", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")
        msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row, util_sell_buttons_action_row])

        def check(button_ctx):
            return button_ctx.author == ctx.author

        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row, util_sell_buttons_action_row], timeout=120,check=check)
            levels_gained = 0
            price = 0
            exp_boost_buttons = ["1", "2", "3"]
            if button_ctx.custom_id == "1":
                # if lvl >= 200:
                #     await button_ctx.send("You can only purchase option 3 when leveling past level 200.")
                #     return
                levels_gained = 10
                price = ten_levels
            if button_ctx.custom_id == "2":
                # if lvl >= 200:
                #     await button_ctx.send("You can only purchase option 3 when leveling past level 200.")
                #     return
                levels_gained = 30
                price = thirty_levels
            if button_ctx.custom_id == "3":
                levels_gained = 100
                price=hundred_levels
            if button_ctx.custom_id == "5":
                levels_gained = 50
                price=100000


            if button_ctx.custom_id == "cancel":
                await msg.edit(components=[])
                return

            if button_ctx.custom_id in exp_boost_buttons:
                if price > balance:
                    await button_ctx.send("You're too broke to buy. Get your money up.", hidden=True)
                    await msg.edit(components=[])
                    return

                card_info = {}
                for level in vault['CARD_LEVELS']:
                    if level['CARD'] == current_card:
                        card_info = level

                lvl = card_info['LVL']
                max_lvl = 700
                if lvl >= max_lvl:
                    await button_ctx.send(f"🎴: **{current_card}** is already at max Smithing level. You may level up in **battle**, but you can no longer purchase levels for this card.", hidden=True)
                    await msg.edit(components=[])
                    return

                elif (levels_gained + lvl) > max_lvl:
                    levels_gained =  max_lvl - lvl


                atk_def_buff = round(levels_gained / 2)
                ap_buff = round(levels_gained / 3)
                hlt_buff = (round(levels_gained / 20) * 25)

                query = {'DID': str(ctx.author.id)}
                update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0}, '$inc': {'CARD_LEVELS.$[type].' + "LVL": levels_gained, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff, 'CARD_LEVELS.$[type].' + "DEF": atk_def_buff, 'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                filter_query = [{'type.'+ "CARD": str(current_card)}]
                response = db.updateVault(query, update_query, filter_query)
                await crown_utilities.curse(price, str(ctx.author.id))
                await button_ctx.send(f"🔋🎴 | **{str(current_card)}** gained {levels_gained} levels!")
                await msg.edit(components=[])
                if button_ctx.custom_id == "cancel":
                    await button_ctx.send("Sell ended.", hidden=True)
                    await msg.edit(components=[])
                    return

            if button_ctx.custom_id == "4":
                price = 25000000
                if price > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                if has_gabes_purse:
                    await button_ctx.send("You already own Gabes Purse. You cannot purchase more than one.", hidden=True)
                    await msg.edit(components=[])
                    return
                else:
                    update = db.updateUserNoFilterAlt(user_query, {'$set': {'TOURNAMENT_WINS': 1}})
                    await crown_utilities.curse(price, str(ctx.author.id))
                    await button_ctx.send("👛 | Gabe's Purse has been purchased!")
                    await msg.edit(components=[])
                    return
                
            if button_ctx.custom_id == "7":
                price = 10000000
                if price > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                if preset_upgrade:
                    await button_ctx.send("You already have 5 Presets!", hidden=True)
                    await msg.edit(components=[])
                    return
                else:
                    await crown_utilities.curse(price, str(ctx.author.id))
                    response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' : str(current_card), 'TITLE': "Preset Upgrade Ver 4.0",'ARM': str(current_arm), 'PET': "Chick"}}})
                    response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' : str(current_card), 'TITLE': "Preset Upgrade Ver 5.0",'ARM': str(current_arm), 'PET': "Chick"}}})
                    #response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' :str(current_card), 'TITLE': str(current_title),'ARM': str(current_arm), 'PET': str(current_pet)}}})
                    update = db.updateUserNoFilterAlt(user_query, {'$set': {'U_PRESET': True}})
                    await button_ctx.send("🔖 | Preset Upgraded")
                    await msg.edit(components=[])
                    return
            
            if button_ctx.custom_id == "5":
                if dungeon_arm:
                    price = 250000
                if boss_arm:
                    await button_ctx.send("Sorry I can't repair **Boss** Arms ...", hidden=True)
                    await msg.edit(components=[])
                    return
                if price > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                if current_durability >= 100:
                    await button_ctx.send(f"🦾 | {current_arm} is already at Max Durability. ⚒️",hidden=True)
                    await msg.edit(components=[])
                    return
                else:
                    try:
                        new_durability = current_durability + levels_gained
                        full_repair = False
                        if new_durability > 100:
                            levels_gained = 100 - current_durability
                            full_repair=True
                        query = {'DID': str(ctx.author.id)}
                        update_query = {'$inc': {'ARMS.$[type].' + 'DUR': levels_gained}}
                        filter_query = [{'type.' + "ARM": str(current_arm)}]
                        resp = db.updateVault(query, update_query, filter_query)

                        await crown_utilities.curse(price, str(ctx.author.id))
                        if full_repair:
                                await button_ctx.send(f"🦾 | {current_arm}'s ⚒️ durability has increased by **{levels_gained}**!\n*Maximum Durability Reached!*")
                        else:
                                await button_ctx.send(f"🦾 | {current_arm}'s ⚒️ durability has increased by **{levels_gained}**!")
                        await msg.edit(components=[])
                        return
                    except:
                        await ctx.send("Failed to purchase durability boost.", hidden=True)

            if button_ctx.custom_id == "6":
                if storage_pricing > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                    
                if not patron_flag and storage_type >= 2:
                    await button_ctx.send("💞 | Only Patrons may purchase more than 30 additional storage. To become a Patron, visit https://www.patreon.com/partychatgaming?fan_landing=true.", hidden=True)
                    await msg.edit(components=[])
                    return
                    
                if storage_type == 10:
                    await button_ctx.send("💼 | You already have max storage.", hidden=True)
                    await msg.edit(components=[])
                    return
                    
                else:
                    update = db.updateUserNoFilterAlt(user_query, {'$inc': {'STORAGE_TYPE': 1}})
                    await crown_utilities.curse(storage_pricing, str(ctx.author.id))
                    await button_ctx.send(f"💼 | Storage Tier {str(storage_type + 1)} has been purchased!")
                    await msg.edit(components=[])
                    return
        except asyncio.TimeoutError:
            await ctx.send("Trinket Shop closed.", hidden=True)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("Trinket Shop closed unexpectedly. Seek support.", hidden=True)

    @cog_ext.cog_slash(description="View your summons", guild_ids=main.guild_ids)
    async def summons(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        if vault:
            try:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                balance = vault['BALANCE']
                current_summon = d['PET']
                pets_list = vault['PETS']

                total_pets = len(pets_list)

                pets=[]
                licon = ":coin:"
                if balance >= 150000:
                    licon = ":money_with_wings:"
                elif balance >=100000:
                    licon = ":moneybag:"
                elif balance >= 50000:
                    licon = ":dollar:"
                current_gems = []
                for gems in vault['GEMS']:
                    current_gems.append(gems['UNIVERSE'])
                bond_message = ""
                lvl_message = ""
                embed_list = []
                for pet in pets_list:
                    #cpetmove_ap= (cpet_bond * cpet_lvl) + list(cpet.values())[3] # Ability Power
                    bond_message = ""
                    lvl_message = ""
                    
                    pet_bond = pet['BOND']
                    bond_exp = pet['BONDEXP']
                    pet_level = pet['LVL']
                    pet_exp = pet['EXP']
                    
                    petmove_ap = list(pet.values())[3] 
                    bond_req = ((petmove_ap * 5) * (pet_bond + 1))
                    lvl_req = int(pet_level) * 10
                    
                    bond_message = f"*{pet_exp}/{lvl_req}*"
                    lvl_message = f"*{bond_exp}/{bond_req}*"
                    
                    if pet['BOND'] == 3:
                        bond_message = ":star2:"
                    if pet['LVL'] == 10:
                        lvl_message = ":star:"
                    
                         
                    
                    pet_ability = list(pet.keys())[3]
                    pet_ability_power = list(pet.values())[3]
                    power = (pet['BOND'] * pet['LVL']) + pet_ability_power
                    pet_info = db.queryPet({'PET' : pet['NAME']})
                    if pet_info:
                        pet_available = pet_info['AVAILABLE']
                        pet_exclusive = pet_info['EXCLUSIVE']
                        pet_universe = pet_info['UNIVERSE']
                    icon = "🧬"
                    if pet_available and pet_exclusive:
                        icon = ":fire:"
                    elif pet_available == False and pet_exclusive ==False:
                        icon = ":japanese_ogre:"

                    embedVar = discord.Embed(title= f"{pet['NAME']}", description=textwrap.dedent(f"""
                    {icon}
                    _Bond_ **{pet['BOND']}** | {bond_message}
                    _Level_ **{pet['LVL']}** | {lvl_message}
                    :small_blue_diamond: **{pet_ability}:** {power}
                    🦠 **Type:** {pet['TYPE']}"""), 
                    colour=0x7289da)
                    embedVar.set_thumbnail(url=avatar)
                    embedVar.set_footer(text=f"{pet['TYPE']}: {enhancer_mapping[pet['TYPE']]}")
                    embed_list.append(embedVar)
                
                buttons = [
                    manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                    manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                    manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                    manage_components.create_button(style=2, label="Exit", custom_id="Exit")
                ]
                custom_action_row = manage_components.create_actionrow(*buttons)

                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        updated_vault = db.queryVault({'DID': d['DID']})
                        sell_price = 0
                        selected_summon = str(button_ctx.origin_message.embeds[0].title)
                        user_query = {'DID': str(ctx.author.id)}
                        
                        if button_ctx.custom_id == "Equip":
                            response = db.updateUserNoFilter(user_query, {'$set': {'FAMILY_PET': False, 'PET': str(button_ctx.origin_message.embeds[0].title)}})
                            await button_ctx.send(f"🧬 **{str(button_ctx.origin_message.embeds[0].title)}** equipped.")
                            self.stop = True
                        
                        elif button_ctx.custom_id =="Trade":
                            summon_data = db.queryPet({'PET' : selected_summon})
                            summon_name = summon_data['PET']
                            if summon_name == current_summon:
                                await button_ctx.send("You cannot trade equipped summons.")
                                return
                            sell_price = 5000
                            mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                            mvalidation=False
                            bvalidation=False
                            item_already_in_trade=False
                            if mtrade:
                                if selected_summon in mtrade['MSUMMONS']:
                                    await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
                                    item_already_in_trade=True
                                mvalidation=True
                            else:
                                btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                                if btrade:
                                    if selected_summon in btrade['BSUMMONS']:
                                        await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
                                        item_already_in_trade=True
                                    bvalidation=True
                                else:
                                    await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                    return
                            if item_already_in_trade:
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Woudl you like to remove **{selected_summon}** from the **Trade**?", components=[trade_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Happy Trading")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        neg_sell_price = 0 - abs(int(sell_price))
                                        if mvalidation:
                                            trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$pull" : {'MSUMMONS': selected_summon}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                            update_query = {"$pull" : {'BSUMMONS': selected_summon}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                            elif mvalidation == True or bvalidation ==True:    #If user is valid
                                sell_price = 5000
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Are you sure you want to trade **{selected_summon}**", components=[trade_buttons_action_row])
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Not this time. ")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        if mvalidation:
                                            trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$push" : {'MSUMMONS': selected_summon}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Traded.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                            update_query = {"$push" : {'BSUMMONS': selected_summon}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Traded.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                        
                        elif button_ctx.custom_id == "Dismantle":
                            summon_data = db.queryPet({'PET' : selected_summon})
                            summon_name = summon_data['PET']
                            if summon_name == current_summon:
                                await button_ctx.send("You cannot dismanetle equipped summonss.")
                                return
                            dismantle_price = 10000   
                            level = int(pet['LVL'])
                            bond = int(pet['BOND'])
                            dismantle_amount = round((1000* level) + (dismantle_price * bond) + dismantle_price)
                            dismantle_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to dismantle **{summon_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Dismantle cancelled. ")
                                    self.stop = True
                                if button_ctx.custom_id == "yes":
                                    if pet_universe in current_gems:
                                        query = {'DID': str(ctx.author.id)}
                                        family_query = {'HEAD':d['FAMILY']}
                                        if d['FAMILY'] != 'PCG':
                                            family_info = db.queryFamily(family_query)
                                            if summon_name == family_info['SUMMON']:
                                                update_query = {'$set' : {'SUMMON': d['PET']}}
                                                family_update = db.updateFamily(family_query,update_query)
                                        update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                        filter_query = [{'type.' + "UNIVERSE": pet_universe}]
                                        response = db.updateVault(query, update_query, filter_query)
                                    else:
                                        response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': pet_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                    
                                    db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'PETS': {"NAME": str(summon_name)}}})
                                    #await crown_utilities.bless(sell_price, ctx.author.id)
                                    await msg.delete()
                                    await button_ctx.send(f"**{summon_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.")
                                    self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                #await ctx.send(f"ERROR:\nTYPE: {type(ex).__name__}\nMESSAGE: {str(ex)}\nLINE: {trace} ")
                                return
                        elif button_ctx.custom_id =="Exit":
                            await button_ctx.defer(ignore=True)
                            self.stop = True
                    else:
                        await ctx.send("This is not your Summons list.")
                await Paginator(bot=self.bot, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
            except asyncio.TimeoutError:
                await ctx.send("Summon List closed.", hidden=True)
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("There's an issue with your Summons list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                return
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

    @cog_ext.cog_slash(description="View your destinies", guild_ids=main.guild_ids)
    async def destinies(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        if not vault['DESTINY']:
            await ctx.send("No Destiny Lines available at this time!")
            return
        if vault:
            try:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                balance = vault['BALANCE']
                destiny = vault['DESTINY']

                destiny_messages = []
                icon = ":coin:"
                if balance >= 150000:
                    icon = ":money_with_wings:"
                elif balance >=100000:
                    icon = ":moneybag:"
                elif balance >= 50000:
                    icon = ":dollar:"
                for d in destiny:
                    if not d['COMPLETED']:
                        destiny_messages.append(textwrap.dedent(f"""\
                        :sparkles: **{d["NAME"]}**
                        Defeat **{d['DEFEAT']}** with **{" ".join(d['USE_CARDS'])}** | **Current Progress:** {d['WINS']}/{d['REQUIRED']}
                        Win :flower_playing_cards: **{d['EARN']}**
                        """))

                if not destiny_messages:
                    await ctx.send("No Destiny Lines available at this time!")
                    return
                # Adding to array until divisible by 10
                while len(destiny_messages) % 10 != 0:
                    destiny_messages.append("")

                # Check if divisible by 10, then start to split evenly
                if len(destiny_messages) % 10 == 0:
                    first_digit = int(str(len(destiny_messages))[:1])
                    if len(destiny_messages) >= 89:
                        if first_digit == 1:
                            first_digit = 10
                    destinies_broken_up = np.array_split(destiny_messages, first_digit)
                
                # If it's not an array greater than 10, show paginationless embed
                if len(destiny_messages) < 10:
                    embedVar = discord.Embed(title= f"Destiny Lines\n**Balance**: :coin:{'{:,}'.format(balance)}", description="\n".join(destiny_messages), colour=0x7289da)
                    embedVar.set_thumbnail(url=avatar)
                    # embedVar.set_footer(text=f".equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                    await ctx.send(embed=embedVar)

                embed_list = []
                for i in range(0, len(destinies_broken_up)):
                    globals()['embedVar%s' % i] = discord.Embed(title= f":sparkles: Destiny Lines\n**Balance**: {icon}{'{:,}'.format(balance)}", description="\n".join(destinies_broken_up[i]), colour=0x7289da)
                    globals()['embedVar%s' % i].set_thumbnail(url=avatar)
                    # globals()['embedVar%s' % i].set_footer(text=f"{total_pets} Total Pets\n.equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                    embed_list.append(globals()['embedVar%s' % i])

                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⬅️', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('➡️', "next")
                paginator.add_reaction('⏭️', "last")
                embeds = embed_list
                await paginator.run(embeds)
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("There's an issue with your Destiny Line list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
                return
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

    @cog_ext.cog_slash(description="View your quests", guild_ids=main.guild_ids)
    async def quests(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        # server = db.queryServer({"GNAME": str(ctx.author.guild)})
        if not vault['QUESTS']:
            await ctx.send("You have no quests available at this time!", hidden=True)
            return
        if vault:
            try:
                buttons = []
                guild_buff = await crown_utilities.guild_buff_update_function(d['TEAM'].lower())
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                balance = vault['BALANCE']
                quests = vault['QUESTS']
                embed_list = []
                quest_messages = []

                buff_message = ""
                virus_message = ""

                # if server:
                #     server_buff = server['SERVER_BUFF_BOOL']
                #     server_virus = server['SERVER_VIRUS_BOOL']
                #     server_name = server['GNAME']

                #     if not server_buff:
                #         buff_message = f"No active buffs in **{server_name}**"
                #     if not server_virus:
                #         virus_message = f"No active viruses in **{server_name}**"

                for quest in quests:
                    guild_buff_msg = "🔴"
                    if guild_buff:                    
                        if guild_buff['Quest']:
                            guild_buff_msg = "🟢"


                    opponent = db.queryCard({'NAME': quest['OPPONENT']})
                    opponent_universe = db.queryUniverse({'TITLE': opponent['UNIVERSE']})
                    opponent_name = opponent['NAME']
                    opponent_universe_image = opponent_universe['PATH']
                    tales = opponent_universe['CROWN_TALES']
                    dungeon = opponent_universe['DUNGEONS']
                    goal = quest['GOAL']
                    wins = quest['WINS']
                    reward = '{:,}'.format(quest['REWARD'])
                    tales_message = ""
                    dungeon_message = ""
                    tales_index = 0
                    dungeon_index = 0
                    if opponent_name in tales:
                        for opp in tales:
                            tales_index = tales.index(opponent_name)
                        tales_message = f"**{opponent_name}** is fight number ⚔️ **{tales_index + 1}** in **Tales**"
                    
                    if opponent_name in dungeon:
                        for opp in dungeon:
                            dungeon_index = dungeon.index(opponent_name)
                        dungeon_message = f"**{opponent_name}** is fight number ⚔️ **{dungeon_index + 1}** in **Dungeon**"
                    
                    completed = ""
                    
                    if quest['GOAL'] == quest['WINS']:
                        completed = "🟢"
                    else:
                        completed = "🔴"
                    icon = ":coin:"
                    if balance >= 150000:
                        icon = ":money_with_wings:"
                    elif balance >=100000:
                        icon = ":moneybag:"
                    elif balance >= 50000:
                        icon = ":dollar:"


                    embedVar = discord.Embed(title=f"{opponent_name}", description=textwrap.dedent(f"""\
                    **Quest**: Defeat {opponent_name} **{str(goal)}** times!
                    **Universe:** 🌍 {opponent['UNIVERSE']}
                    **Reward:** {icon} {reward}

                    **Guild Quest Buff:**  {guild_buff_msg}
                    
                    **Wins so far:** {str(wins)}
                    **Completed:** {completed}

                    {tales_message}
                    {dungeon_message}

                    {buff_message}
                    
                    {virus_message}
                    """))

                    embedVar.set_thumbnail(url=opponent_universe_image)
                    # embedVar.set_footer(text="Use /tales to complete daily quest!", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")

                    if quest['GOAL'] != quest['WINS']:
                        embed_list.append(embedVar)

                if not embed_list:
                    await ctx.send("All quests have been completed today! 👑")
                    return

                buttons = [manage_components.create_button(style=3, label="Start Quest Tales", custom_id="quests_tales"),]
                custom_action_row = manage_components.create_actionrow(*buttons)

                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        selected_quest = str(button_ctx.origin_message.embeds[0].title)
                        if button_ctx.custom_id == "quests_tales":
                            mode = "Tales"
                            await button_ctx.defer(ignore=True)
                            card = db.queryCard({"NAME": selected_quest})
                            sowner = db.queryUser({'DID': str(ctx.author.id)})
                            universe = db.queryUniverse({"TITLE": card['UNIVERSE']})
                            selected_universe = universe['TITLE']
                            completed_universes = sowner['CROWN_TALES']
                            oguild = "PCG"
                            crestlist = []
                            crestsearch = False
                            # guild = server_name
                            oteam = sowner['TEAM']
                            ofam = sowner['FAMILY']
                            guild_buff = await crown_utilities.guild_buff_update_function(sowner['TEAM'].lower())
                            

                            # if sowner['LEVEL'] < 4:
                            #     await button_ctx.send("🔓 Unlock **Tales** by completing **Floor 3** of the 🌑 **Abyss**! Use /solo to enter the abyss.")
                            #     self.stop = True
                            #     return

                            if oteam != 'PCG':
                                team_info = db.queryTeam({'TEAM_NAME': oteam.lower()})
                                guildname = team_info['GUILD']
                                if guildname != "PCG":
                                    oguild = db.queryGuildAlt({'GNAME': guildname})
                                    if oguild:
                                        crestlist = oguild['CREST']
                                        crestsearch = True

                            currentopponent = 0
                            if guild_buff:
                                if guild_buff['Quest']:
                                    for opp in universe['CROWN_TALES']:
                                        if opp == card['NAME']:
                                            currentopponent = universe['CROWN_TALES'].index(opp)
                                            update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])
                                        
                            await battle_commands(self, ctx, mode, universe, selected_universe, completed_universes, oguild,
                                    crestlist, crestsearch, sowner, oteam, ofam, currentopponent, None, None, None,
                                    None, None, None, None, None)
                            
                            self.stop = True
                    else:
                        await ctx.send("This is not your Title list.")

                await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()

            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("There's an issue with your Quest list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                return
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

    @cog_ext.cog_slash(description="View your balance", guild_ids=main.guild_ids)
    async def balance(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            query = {'DID': str(ctx.author.id)}
            d = db.queryUser(query)
            vault = db.queryVault({'DID': d['DID']})
            icon = ":coin:"
            if vault:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                balance = vault['BALANCE']
                if balance >= 50000000:
                    icon = ":money_with_wings:"
                elif balance >=10000000:
                    icon = ":moneybag:"
                elif balance >= 500000:
                    icon = ":dollar:"
                if d['TEAM'] != 'PCG':
                    t = db.queryTeam({'TEAM_NAME' : d['TEAM'].lower()})
                    tbal = t['BANK']
                    if d['FAMILY'] != 'PCG':
                        f = db.queryFamily({'HEAD': d['FAMILY']})
                        fbal = f['BANK']
                embedVar = discord.Embed(title= f"{icon}{'{:,}'.format(balance)}", colour=0x7289da)
                await ctx.send(embed=embedVar)
            else:
                newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
        except:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            
    @cog_ext.cog_slash(description="Load a saved preset", guild_ids=main.guild_ids)
    async def preset(self, ctx):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            query = {'DID': str(ctx.author.id)}
            d = db.queryUser(query)
            vault_query = {'DID': d['DID']}
            vault = db.queryVault(vault_query)
            if vault:
                ownedcards = []
                ownedtitles = []
                ownedarms = []
                ownedpets = []
                for cards in vault['CARDS']:
                    ownedcards.append(cards)
                for titles in vault['TITLES']:
                    ownedtitles.append(titles)
                for arms in vault['ARMS']:
                    ownedarms.append(arms['ARM'])
                for pets in vault['PETS']:
                    ownedpets.append(pets['NAME'])

                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                cards = vault['CARDS']
                titles = vault['TITLES']
                deck = vault['DECK']
                preset_length = len(deck)
                preset_update = d['U_PRESET']
                
                
                preset1_card = list(deck[0].values())[0]
                preset1_title = list(deck[0].values())[1]
                preset1_arm = list(deck[0].values())[2]
                preset1_pet = list(deck[0].values())[3]

                preset2_card = list(deck[1].values())[0]
                preset2_title = list(deck[1].values())[1]
                preset2_arm = list(deck[1].values())[2]
                preset2_pet = list(deck[1].values())[3]

                preset3_card = list(deck[2].values())[0]
                preset3_title = list(deck[2].values())[1]
                preset3_arm = list(deck[2].values())[2]
                preset3_pet = list(deck[2].values())[3]    
                
                if preset_update:
                    preset4_card = list(deck[3].values())[0]
                    preset4_title = list(deck[3].values())[1]
                    preset4_arm = list(deck[3].values())[2]
                    preset4_pet = list(deck[3].values())[3]

                    preset5_card = list(deck[4].values())[0]
                    preset5_title = list(deck[4].values())[1]
                    preset5_arm = list(deck[4].values())[2]
                    preset5_pet = list(deck[4].values())[3]  
                    
                    listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                    f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                    f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n", 
                    f"4️⃣| {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n\n", 
                    f"5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n\n"]  
                else:
                    listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                    f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                    f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n"]
            
                embedVar = discord.Embed(title="🔖 | Preset Menu", description=textwrap.dedent(f"""
                {"".join(listed_options)}
                """))
                embedVar.set_thumbnail(url=avatar)
                # embedVar.add_field(name=f"Preset 1:{preset1_title} {preset1_card} and {preset1_pet}", value=f"Card: {preset1_card}\nTitle: {preset1_title}\nArm: {preset1_arm}\nSummon: {preset1_pet}", inline=False)
                # embedVar.add_field(name=f"Preset 2:{preset2_title} {preset2_card} and {preset2_pet}", value=f"Card: {preset2_card}\nTitle: {preset2_title}\nArm: {preset2_arm}\nSummon: {preset2_pet}", inline=False)
                # embedVar.add_field(name=f"Preset 3:{preset3_title} {preset3_card} and {preset3_pet}", value=f"Card: {preset3_card}\nTitle: {preset3_title}\nArm: {preset3_arm}\nSummon: {preset3_pet}", inline=False)
                util_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="1️⃣",
                        custom_id = "1"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="2️⃣",
                        custom_id = "2"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="3️⃣",
                        custom_id = "3"
                    )
                ]
                
                if preset_update:
                    util_buttons.append(
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="4️⃣",
                            custom_id="4"
                        )
                    )
                    util_buttons.append(
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="5️⃣",
                            custom_id="5"
                        )
                    )
                    
                        

                util_action_row = manage_components.create_actionrow(*util_buttons)
                components = [util_action_row]
                await ctx.send(embed=embedVar,components=[util_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[util_action_row], timeout=30,check=check)

                    if  button_ctx.custom_id == "0":
                        await button_ctx.send(f"{ctx.author.mention}, No change has been made", hidden=True)
                        return
                    elif  button_ctx.custom_id == "1":
                        for card in ownedcards :                     
                            if preset1_card in ownedcards:
                                for title in ownedtitles:
                                    if preset1_title in ownedtitles:
                                        for arm in ownedarms:
                                            if preset1_arm in ownedarms:
                                                for pet in ownedpets:
                                                    if preset1_pet in ownedpets:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card), 'TITLE': str(preset1_title),'ARM': str(preset1_arm), 'PET': str(preset1_pet)}})
                                                        await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                        return
                                                    else:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card), 'TITLE': str(preset1_title),'ARM': str(preset1_arm)}})
                                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset1_pet}", hidden=True)
                                                        return
                                            else:
                                                response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card), 'TITLE': str(preset1_title),'PET': str(preset1_pet)}})
                                                await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset1_arm}")
                                                return
                                    else:
                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card),'ARM': str(preset1_arm), 'PET': str(preset1_pet)}})
                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset1_title}")
                                        return
                            else:
                                response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset1_title),'ARM': str(preset1_arm), 'PET': str(preset1_pet)}})
                                await button_ctx.send(f"{ctx.author.mention}'s items updated, You No Longer Own {preset1_card}")
                                return
                    elif  button_ctx.custom_id == "2":
                        for card in ownedcards :                     
                            if preset2_card in ownedcards:
                                for title in ownedtitles:
                                    if preset2_title in ownedtitles:
                                        for arm in ownedarms:
                                            if preset2_arm in ownedarms:
                                                for pet in ownedpets:
                                                    if preset2_pet in ownedpets:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card), 'TITLE': str(preset2_title),'ARM': str(preset2_arm), 'PET': str(preset2_pet)}})
                                                        await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                        return
                                                    else:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card), 'TITLE': str(preset2_title),'ARM': str(preset2_arm)}})
                                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset2_pet}")
                                                        return
                                            else:
                                                response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card), 'TITLE': str(preset2_title), 'PET': str(preset2_pet)}})
                                                await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset2_arm}")
                                                return
                                    else:
                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card),'ARM': str(preset2_arm), 'PET': str(preset2_pet)}})
                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset2_title}")
                                        return
                            else:
                                response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset2_title),'ARM': str(preset2_arm), 'PET': str(preset2_pet)}})
                                await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset2_card}.")
                                return
                    elif  button_ctx.custom_id == "3":
                        for card in ownedcards :                     
                            if preset3_card in ownedcards:
                                for title in ownedtitles:
                                    if preset3_title in ownedtitles:
                                        for arm in ownedarms:
                                            if preset3_arm in ownedarms:
                                                for pet in ownedpets:
                                                    if preset3_pet in ownedpets:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card), 'TITLE': str(preset3_title),'ARM': str(preset3_arm), 'PET': str(preset3_pet)}})
                                                        await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                        return
                                                    else:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card), 'TITLE': str(preset3_title),'ARM': str(preset3_arm)}})
                                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset3_pet}")
                                                        return
                                            else:
                                                response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card), 'TITLE': str(preset3_title),'PET': str(preset3_pet)}})
                                                await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset3_arm}")
                                                return
                                    else:
                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card),'ARM': str(preset3_arm), 'PET': str(preset3_pet)}})
                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset3_title}")
                                        return
                            else:
                                response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset3_title),'ARM': str(preset3_arm), 'PET': str(preset3_pet)}})
                                await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset3_card}")
                                return  
                    elif  button_ctx.custom_id == "4":
                        for card in ownedcards :                     
                            if preset4_card in ownedcards:
                                for title in ownedtitles:
                                    if preset4_title in ownedtitles:
                                        for arm in ownedarms:
                                            if preset4_arm in ownedarms:
                                                for pet in ownedpets:
                                                    if preset4_pet in ownedpets:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card), 'TITLE': str(preset4_title),'ARM': str(preset4_arm), 'PET': str(preset4_pet)}})
                                                        await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                        return
                                                    else:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card), 'TITLE': str(preset4_title),'ARM': str(preset4_arm)}})
                                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset4_pet}")
                                                        return
                                            else:
                                                response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card), 'TITLE': str(preset4_title),'PET': str(preset4_pet)}})
                                                await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset4_arm}")
                                                return
                                    else:
                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card),'ARM': str(preset3_arm), 'PET': str(preset4_pet)}})
                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset4_title}")
                                        return
                            else:
                                response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset4_title),'ARM': str(preset3_arm), 'PET': str(preset4_pet)}})
                                await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset4_card}")
                                return  
                    elif  button_ctx.custom_id == "5":
                        for card in ownedcards :                     
                            if preset5_card in ownedcards:
                                for title in ownedtitles:
                                    if preset5_title in ownedtitles:
                                        for arm in ownedarms:
                                            if preset5_arm in ownedarms:
                                                for pet in ownedpets:
                                                    if preset5_pet in ownedpets:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card), 'TITLE': str(preset5_title),'ARM': str(preset5_arm), 'PET': str(preset5_pet)}})
                                                        await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                        return
                                                    else:
                                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card), 'TITLE': str(preset5_title),'ARM': str(preset5_arm)}})
                                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset5_pet}")
                                                        return
                                            else:
                                                response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card), 'TITLE': str(preset5_title),'PET': str(preset5_pet)}})
                                                await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset5_arm}")
                                                return
                                    else:
                                        response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card),'ARM': str(preset5_arm), 'PET': str(preset5_pet)}})
                                        await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset5_title}")
                                        return
                            else:
                                response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset5_title),'ARM': str(preset5_arm), 'PET': str(preset5_pet)}})
                                await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset5_card}")
                                return  
                    
                except Exception as ex:
                    trace = []
                    tb = ex.__traceback__
                    while tb is not None:
                        trace.append({
                            "filename": tb.tb_frame.f_code.co_filename,
                            "name": tb.tb_frame.f_code.co_name,
                            "lineno": tb.tb_lineno
                        })
                        tb = tb.tb_next
                    print(str({
                        'type': type(ex).__name__,
                        'message': str(ex),
                        'trace': trace
                    }))
                    await ctx.send("Preset Issue Seek support.", hidden=True)
            else:
                newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", hidden=True)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("Preset Issue Seek support.", hidden=True)

    @cog_ext.cog_slash(description="Save your current build as a preset", guild_ids=main.guild_ids)
    async def savepreset(self, ctx):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            query = {'DID': str(ctx.author.id)}
            d = db.queryUser(query)
            vault_query = {'DID': d['DID']}
            vault = db.queryVault(vault_query)
            if vault:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                cards = vault['CARDS']
                titles = vault['TITLES']
                deck = vault['DECK']


                current_card = d['CARD']
                current_title = d['TITLE']
                current_arm= d['ARM']
                current_pet = d['PET']
                preset_update = d['U_PRESET']

                
                preset1_card = list(deck[0].values())[0]
                preset1_title = list(deck[0].values())[1]
                preset1_arm = list(deck[0].values())[2]
                preset1_pet = list(deck[0].values())[3]

                preset2_card = list(deck[1].values())[0]
                preset2_title = list(deck[1].values())[1]
                preset2_arm = list(deck[1].values())[2]
                preset2_pet = list(deck[1].values())[3]

                preset3_card = list(deck[2].values())[0]
                preset3_title = list(deck[2].values())[1]
                preset3_arm = list(deck[2].values())[2]
                preset3_pet = list(deck[2].values())[3]    

                if preset_update:
                    preset4_card = list(deck[3].values())[0]
                    preset4_title = list(deck[3].values())[1]
                    preset4_arm = list(deck[3].values())[2]
                    preset4_pet = list(deck[3].values())[3]

                    preset5_card = list(deck[4].values())[0]
                    preset5_title = list(deck[4].values())[1]
                    preset5_arm = list(deck[4].values())[2]
                    preset5_pet = list(deck[4].values())[3]  
                    
                    listed_options = [f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n\n",
                    f"📝1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                    f"📝2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                    f"📝3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n", 
                    f"📝4️⃣| {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n\n", 
                    f"📝5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n\n"]  
                else:
                    listed_options = [f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n\n",
                    f"📝1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                    f"📝2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                    f"📝3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n"]
            
                embedVar = discord.Embed(title=f"📝 | Save Current Build", description=textwrap.dedent(f"""
                {"".join(listed_options)}
                """))
                util_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="📝 1️⃣",
                        custom_id = "1"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="📝 2️⃣",
                        custom_id = "2"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="📝 3️⃣",
                        custom_id = "3"
                    )
                ]
                
                if preset_update:
                    util_buttons.append(
                        manage_components.create_button(
                            style=ButtonStyle.green,
                            label="📝4️⃣",
                            custom_id="4"
                        )
                    )
                    util_buttons.append(
                        manage_components.create_button(
                            style=ButtonStyle.green,
                            label="📝5️⃣",
                            custom_id="5"
                        )
                    )
                util_action_row = manage_components.create_actionrow(*util_buttons)
                components = [util_action_row]
                await ctx.send(embed=embedVar,components=[util_action_row])

                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[util_action_row], timeout=120,check=check)

                    if button_ctx.custom_id == "0":
                        await button_ctx.send(f"{ctx.author.mention}, No change has been made")
                        return
                    elif button_ctx.custom_id == "1":
                        response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.0.CARD' :str(current_card), 'DECK.0.TITLE': str(current_title),'DECK.0.ARM': str(current_arm), 'DECK.0.PET': str(current_pet)}})
                        if response:
                            await button_ctx.send("📝 1️⃣| Preset Updated!")
                            return
                    elif button_ctx.custom_id == "2":
                        response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.1.CARD' :str(current_card), 'DECK.1.TITLE': str(current_title),'DECK.1.ARM': str(current_arm), 'DECK.1.PET': str(current_pet)}})
                        if response:
                            await button_ctx.send("📝 2️⃣| Preset Updated!")
                            return
                    elif button_ctx.custom_id == "3":
                        response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.2.CARD' :str(current_card), 'DECK.2.TITLE': str(current_title),'DECK.2.ARM': str(current_arm), 'DECK.2.PET': str(current_pet)}})
                        if response:
                            await button_ctx.send("📝 3️⃣| Preset Updated!")
                            return
                    elif button_ctx.custom_id == "4":
                        response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.3.CARD' :str(current_card), 'DECK.3.TITLE': str(current_title),'DECK.3.ARM': str(current_arm), 'DECK.3.PET': str(current_pet)}})
                        if response:
                            await button_ctx.send("📝 4️⃣| Preset Updated!")
                            return
                    elif button_ctx.custom_id == "5":
                        response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.4.CARD' :str(current_card), 'DECK.4.TITLE': str(current_title),'DECK.4.ARM': str(current_arm), 'DECK.4.PET': str(current_pet)}})
                        if response:
                            await button_ctx.send("📝 5️⃣| Preset Updated!")
                            return
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", hidden=True)
                except Exception as ex:
                    trace = []
                    tb = ex.__traceback__
                    while tb is not None:
                        trace.append({
                            "filename": tb.tb_frame.f_code.co_filename,
                            "name": tb.tb_frame.f_code.co_name,
                            "lineno": tb.tb_lineno
                        })
                        tb = tb.tb_next
                    print(str({
                        'type': type(ex).__name__,
                        'message': str(ex),
                        'trace': trace
                    }))
                    await ctx.send("Preset Issue Seek support.", hidden=True)
            else:
                newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("Preset Issue Seek support.", hidden=True)

    @cog_ext.cog_slash(description="Open the shop", guild_ids=main.guild_ids)
    async def shop(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            all_universes = db.queryAllUniverse()
            user = db.queryUser({'DID': str(ctx.author.id)})
            storage_allowed_amount = user['STORAGE_TYPE'] * 15
            guild_buff = "NULL"
            if user["TEAM"] != "PCG":
                guild_info = db.queryTeam({"TEAM_NAME": str(user["TEAM"].lower())})
                guild_buff = guild_info["ACTIVE_GUILD_BUFF"]

            if user['LEVEL'] < 1:
                await ctx.send("🔓 Unlock the Shop by completing Floor 0 of the 🌑 Abyss! Use /solo to enter the abyss.")
                return

            completed_tales = user['CROWN_TALES']
            completed_dungeons = user['DUNGEONS']
            available_universes = []
            riftShopOpen = False
            shopName = ':shopping_cart: Shop'
            if user['RIFT'] == 1 or guild_buff == "Rift":
                riftShopOpen = True
                shopName = ':crystal_ball: Rift Shop'

            if riftShopOpen:
                close_rift = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'RIFT': 0}})

                
            if riftShopOpen:    
                for uni in all_universes:
                    if uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                        available_universes.append(uni)
            else:
                for uni in all_universes:
                    if uni['TIER'] != 9 and uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                        available_universes.append(uni)
            
            vault_query = {'DID' : str(ctx.author.id)}
            vault = db.altQueryVault(vault_query)
            storage_amount = len(vault['STORAGE'])
            hand_length = len(vault['CARDS'])
            current_titles = vault['TITLES']
            current_cards = vault['CARDS']
            current_arms = []
            for arm in vault['ARMS']:
                current_arms.append(arm['ARM'])

            owned_card_levels_list = []
            for c in vault['CARD_LEVELS']:
                owned_card_levels_list.append(c['CARD'])

            owned_destinies = []
            for destiny in vault['DESTINY']:
                owned_destinies.append(destiny['NAME'])
                
            card_message = ""
            title_message = ""
            arm_message = ""
            
            if len(current_cards) >= 25:
                card_message = "🎴 *25 Full*"
            else:
                card_message = f"🎴 {len(current_cards)}"
                
            if len(current_titles) >= 25:
                title_message = "🎗️ *25 Full*"
            else:
                title_message = f"🎗️ {len(current_titles)}"
                
            if len(current_arms) >= 25:
                arm_message = "🦾 *25 Full*"
            else:
                arm_message = f"🦾 {len(current_arms)}"


            balance = vault['BALANCE']
            icon = ":coin:"
            if balance >= 150000:
                icon = ":money_with_wings:"
            elif balance >=100000:
                icon = ":moneybag:"
            elif balance >= 50000:
                icon = ":dollar:"


            embed_list = []
            for universe in available_universes:
                universe_name = universe['TITLE']
                universe_image = universe['PATH']
                adjusted_prices = price_adjuster(15000, universe_name, completed_tales, completed_dungeons)
                embedVar = discord.Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
                *Welcome {ctx.author.mention}! {adjusted_prices['MESSAGE']}
                You have {icon}{'{:,}'.format(balance)} coins!*
                {card_message} | {title_message} | {arm_message}
                
                🎗️ **Title:** Title Purchase for 💵 {'{:,}'.format(adjusted_prices['TITLE_PRICE'])}
                🦾 **Arm:** Arm Purchase for 💵 {'{:,}'.format(adjusted_prices['ARM_PRICE'])}
                1️⃣ **1-3 Tier Card:** for 💵 {'{:,}'.format(adjusted_prices['C1'])}
                2️⃣ **3-5 Tier Card:** for 💰 {'{:,}'.format(adjusted_prices['C2'])}
                3️⃣ **5-7 Tier Card:** for 💸 {'{:,}'.format(adjusted_prices['C3'])}
                """), colour=0x7289da)
                embedVar.set_image(url=universe_image)
                #embedVar.set_thumbnail(url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236723/PCG%20LOGOS%20AND%20RESOURCES/Party_Chat_Shop.png")
                embed_list.append(embedVar)

            
            # Pull all cards that don't require tournaments
            # resp = db.queryShopCards()

            buttons = [
                manage_components.create_button(style=3, label="🎗️", custom_id="title"),
                manage_components.create_button(style=1, label="🦾", custom_id="arm"),
                manage_components.create_button(style=2, label="1️⃣", custom_id="t1card"),
                manage_components.create_button(style=2, label="2️⃣", custom_id="t2card"),
                manage_components.create_button(style=2, label="3️⃣", custom_id="t3card"),
            ]

            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    updated_vault = db.queryVault({'DID': user['DID']})
                    balance = updated_vault['BALANCE']        
                    universe = str(button_ctx.origin_message.embeds[0].title)
                    
                    if button_ctx.custom_id == "title":
                        updated_vault = db.queryVault({'DID': user['DID']})
                        current_titles = updated_vault['TITLES']
                        price = price_adjuster(50000, universe, completed_tales, completed_dungeons)['TITLE_PRICE']
                        bless_amount = price
                        # if len(current_titles) >=25:
                        #     await button_ctx.send("You have max amount of Titles. Transaction cancelled.")
                        #     self.stop = True
                        #     return

                        if price > balance:
                            await button_ctx.send("Insufficent funds.")
                            self.stop = True
                            return
                        list_of_titles =[x for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
                        if not list_of_titles:
                            await button_ctx.send("There are no titles available for purchase in this range.")
                            self.stop = True
                            return

                        selection_length = len(list(list_of_titles)) - 1
                        if selection_length ==0:
                            title = list_of_titles[0]
                        else:
                            selection = random.randint(0,selection_length)
                            title = list_of_titles[selection]  
                        if title['TITLE'] in current_titles:                 
                            bless_amount = price
                            bless_reduction = 0
                            if universe_name in completed_tales:
                                bless_reduction = bless_amount * .25
                                bless_amount = round((bless_amount - bless_reduction)/2)
                            if universe_name in completed_dungeons:
                                bless_reduction = bless_amount * .50
                                bless_amount = round((bless_amount - bless_reduction)/2)
                            else: 
                                bless_amount = round(bless_amount /2) #Send bless amount for price in utilities
                                
                        response = await crown_utilities.store_drop_card(str(ctx.author.id), title['TITLE'], universe_name, updated_vault, "Titles_NoDestinies", bless_amount, bless_amount, "Purchase", True, int(price), "titles")
                        await button_ctx.send(response)
                            # await button_ctx.send(f"You already own **{title['TITLE']}**. You get a :coin:**{'{:,}'.format(bless_amount)}** refund!") 
                        #     #await crown_utilities.curse(bless_amount, str(ctx.author.id)) 
                        # else:
                        #     response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})   
                        #     await crown_utilities.curse(price, str(ctx.author.id))
                        #     await button_ctx.send(f"You purchased **{title['TITLE']}**.")


                    elif button_ctx.custom_id == "arm":
                        updated_vault = db.queryVault({'DID': user['DID']})
                        current_arms = []
                        for arm in updated_vault['ARMS']:
                            current_arms.append(arm['ARM'])
                        price = price_adjuster(25000, universe, completed_tales, completed_dungeons)['ARM_PRICE']
                        # if len(current_arms) >=25:
                        #     await button_ctx.send("You have max amount of Arms. Transaction cancelled.")
                        #     self.stop = True
                        #     return
                        if price > balance:
                            await button_ctx.send("Insufficent funds.")
                            self.stop = True
                            return
                        list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
                        if not list_of_arms:
                            await button_ctx.send("There are no arms available for purchase in this range.")
                            self.stop = True
                            return

                        selection_length = len(list(list_of_arms)) - 1

                        if selection_length ==0:
                            arm = list_of_arms[0]
                        else:
                            selection = random.randint(0,selection_length)
                            arm = list_of_arms[selection]['ARM']
                        response = await crown_utilities.store_drop_card(str(ctx.author.id), arm, universe_name, updated_vault, 25, price, price, "Purchase", True, int(price), "arms")
                        await button_ctx.send(response)
                        
                        # if arm not in current_arms:
                        #     response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 25}}})
                        #     await crown_utilities.curse(price, str(ctx.author.id))
                        #     await button_ctx.send(f"You purchased **{arm}**.")
                        # else:
                        #     update_query = {'$inc': {'ARMS.$[type].' + 'DUR': 10}}
                        #     filter_query = [{'type.' + "ARM": str(arm)}]
                        #     resp = db.updateVault(vault_query, update_query, filter_query)
                        #     await crown_utilities.curse(price, str(ctx.author.id))
                        #     await button_ctx.send(f"You purchased **{arm}**. Increased durability for the arm by 10 as you already own it.")


                    elif button_ctx.custom_id == "t1card":
                        price = price_adjuster(100000, universe, completed_tales, completed_dungeons)['C1']
                        acceptable = [1,2,3]
                        if price > balance:
                            await button_ctx.send("Insufficent funds.")
                            self.stop = True
                            return
                        list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                        if not list_of_cards:
                            await button_ctx.send("There are no cards available for purchase in this range.")
                            self.stop = True
                            return

                        selection_length = len(list(list_of_cards)) - 1
                        if selection_length ==0:
                            card = list_of_cards[0]
                        else:
                            selection = random.randint(0,selection_length)
                            card = list_of_cards[selection]
                        card_name = card['NAME']
                        tier = 0

                        response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
                        await button_ctx.send(response)


                    elif button_ctx.custom_id == "t2card":
                        price = price_adjuster(450000, universe, completed_tales, completed_dungeons)['C2']
                        acceptable = [3,4,5]
                        if price > balance:
                            await button_ctx.send("Insufficent funds.")
                            self.stop = True
                            return
                        list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                        
                        if not list_of_cards:
                            await button_ctx.send("There are no cards available for purchase in this range.")
                            self.stop = True
                            return
                        
                        selection_length = len(list(list_of_cards)) - 1

                        if selection_length ==0:
                            card = list_of_cards[0]
                        else:
                            selection = random.randint(0,selection_length)
                            card = list_of_cards[selection]
                        card_name = card['NAME']
                        tier = 0
                        
                        response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
                        await button_ctx.send(response)


                    elif button_ctx.custom_id == "t3card":
                        price = price_adjuster(6000000, universe, completed_tales, completed_dungeons)['C3']
                        acceptable = [5,6,7]
                        if price > balance:
                            await button_ctx.send("Insufficent funds.")
                            self.stop = True
                            return
                        card_list_response = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                        if not card_list_response:
                            await button_ctx.send("There are no cards available for purchase in this range.")
                            self.stop = True
                            return
                        else:
                            list_of_cards = []
                            for card in card_list_response:
                                if card['AVAILABLE'] and not card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
                                    list_of_cards.append(card)


                        if not list_of_cards:
                            await button_ctx.send("There are no cards available for purchase in this range.")
                            self.stop = True
                            return

                        selection_length = len(list(list_of_cards)) - 1
                        if selection_length ==0:
                            card = list_of_cards[0]
                        else:
                            selection = random.randint(0,selection_length)
                            card = list_of_cards[selection]
                        card_name = card['NAME']
                        tier = 0

                        response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
                        await button_ctx.send(response)

                else:
                    await ctx.send("This is not your Shop.")
            await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))

    @cog_ext.cog_slash(description="Start crafting", guild_ids=main.guild_ids)
    async def craft(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        # Craft with Gems
        # Craft Universe Heart, Universe Soul, Skin Box
        poke_universes = ['Kanto Region', 'Johto Region', 'Hoenn Region', 'Sinnoh Region']
        try:
            gems = 0
            all_universes = db.queryAllUniverse()
            user = db.queryUser({'DID': str(ctx.author.id)})
            guild_info = db.queryTeam({"TEAM_NAME": str(user["TEAM"].lower())})
            guild_buff = guild_info["ACTIVE_GUILD_BUFF"]
            completed_dungeons = user['DUNGEONS']
            completed_tales = user['CROWN_TALES']
            card_info = db.queryCard({"NAME": user['CARD']})
            destiny_alert_message = f"No Skins or Destinies available for {card_info['NAME']}"
            destiny_alert = False
            # if user['LEVEL'] < 9:
            #     await ctx.send("🔓 Unlock Crafting by completing Floor 8 of the 🌑 Abyss! Use **/solo** to enter the abyss.")
            #     return

            #skin_alert_message = f"No Skins for {card_info['NAME']}"
            
            #skin_alert_message = f"No Skins for {card_info['NAME']}"
            available_universes = []
            riftShopOpen = False
            shopName = ':shopping_cart: Shop'
            if user['RIFT'] == 1 or guild_buff == "Rift":
                riftShopOpen = True
                shopName = ':crystal_ball: Rift Shop'
                
            if riftShopOpen:    
                for uni in all_universes:
                    if uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                        available_universes.append(uni)
            else:
                for uni in all_universes:
                    if uni['TIER'] != 9 and uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                        available_universes.append(uni)
            
            vault_query = {'DID' : str(ctx.author.id)}
            vault = db.altQueryVault(vault_query)
            current_cards = vault['CARDS']
            owned_card_levels_list = []
            for c in vault['CARD_LEVELS']:
                owned_card_levels_list.append(c['CARD'])
                
            #Card skin query 
            list_of_card_skins = False
            skin_alert = False
            card_skin_message = "No Skins"
            new_skin_list = []
            
            list_of_card_skins = [x for x in db.queryAllCardsBasedOnUniverse({'SKIN_FOR' : card_info['NAME']})]
            
            if list_of_card_skins: 
                for skin in list_of_card_skins:
                    
                    if skin['NAME'] not in current_cards and skin['SKIN_FOR'] == user['CARD']:
                        new_skin_list.append(skin)
                        card_skin_message = f" {card_info['UNIVERSE']} Skins Available!"
                        skin_alert = True
            
                
                

            owned_destinies = []
            for destiny in vault['DESTINY']:
                owned_destinies.append(destiny['NAME'])
                d_card = ' '.join(destiny['USE_CARDS'])
                d_card_info = db.queryCard({"NAME": str(d_card)})
                if card_info['NAME'] in destiny['USE_CARDS'] or card_info['SKIN_FOR'] in d_card_info['NAME']:
                    #destiny_alert_message = f"{card_info['UNIVERSE']} Destinies Availble"
                    destiny_alert = True
            if len(owned_destinies) >= 1:
                destiny_Alert = True
            
                    
            if skin_alert == True and destiny_alert ==True:
                destiny_alert_message = f"{card_info['NAME']} Skins and Destinies Available!"
            elif skin_alert == True:
                destiny_alert_message = f"{card_info['NAME']} Skins Available!"
            elif destiny_alert == True:
                destiny_alert_message = f"{card_info['NAME']} Destinies Available!"
            
                    
            embed_list = []
            for universe in available_universes:
                universe_name = universe['TITLE']
                universe_image = universe['PATH']
                universe_heart = False
                universe_soul = False
                gems = 0
                for uni in vault['GEMS']:
                    if uni['UNIVERSE'] == universe_name:
                        gems = uni['GEMS']
                        universe_heart = uni['UNIVERSE_HEART']
                        universe_soul = uni['UNIVERSE_SOUL']
                heart_message = "Cannot Afford"
                soul_message = "Cannot Afford"
                destiny_message = "Cannot Afford"
                craft_card_message = "Cannot Afford"
                if universe_heart:
                    heart_message = "Owned"
                elif gems >= 1000000:
                    heart_message = "Craftable"
                if universe_soul:
                    soul_message = "Owned"
                elif gems >= 500000:
                    soul_message = "Craftable"
                if gems >= 1500000 and universe_name == card_info['UNIVERSE'] and destiny_alert:
                    destiny_message = f"Destinies available"
                elif gems >= 1500000 and destiny_alert:
                    destiny_message = f"{universe_name} Destinies available"
                elif gems >= 1500000:
                    destiny_message = f"Affordable!"
                if gems >= 6000000:
                    craft_card_message = f"Affordable!"
                if universe_name != card_info['UNIVERSE'] and skin_alert:
                    card_skin_message = f"{card_info['UNIVERSE']} Skin Available!"
                    if card_info['UNIVERSE'] in poke_universes:
                        card_skin_message = f"Regional Pokemon Skins Available!"
                    
                embedVar = discord.Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
                Welcome {ctx.author.mention}!
                You have 💎 *{'{:,}'.format(gems)}* **{universe_name}** gems !
                
                Equipped Card:  **{card_info['NAME']}** *{card_info['UNIVERSE']}*
                *{destiny_alert_message}*
                
                💟 **Universe Heart:** 💎 5,000,000 *{heart_message}*
                *Grants ability to level past 200*

                🌹 **Universe Soul:** 💎 5,000,000 *{soul_message}*
                *Grants double exp in this Universe*

                ✨ **Destiny Line:** 💎 1,500,000 *{destiny_message}*
                *Grants wins for a Destiny Line*
                
                🃏 **Card Skins:** 💎 2,000,000 *{card_skin_message}*
                *Grants Card Skin*

                ✨🎴 **Craft Card:** 💎 15,000,000 *{craft_card_message}*
                *Craft a random dungeon card from this Universe*

                """), colour=0x7289da)
                embedVar.set_image(url=universe_image)
                embed_list.append(embedVar)

        
            buttons = [
                manage_components.create_button(style=3, label="💟", custom_id="UNIVERSE_HEART"),
                manage_components.create_button(style=1, label="🌹", custom_id="UNIVERSE_SOUL"),
                manage_components.create_button(style=1, label="✨", custom_id="Destiny"),
                manage_components.create_button(style=1, label="🃏", custom_id="Skin"),
                manage_components.create_button(style=1, label="🎴", custom_id="Card")
            ]

            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    universe = str(button_ctx.origin_message.embeds[0].title)
                    if button_ctx.custom_id == "UNIVERSE_HEART":
                        price = 5000000
                        response = await craft_adjuster(self, ctx, vault, universe, price, button_ctx.custom_id, completed_tales, None)
                        if response['SUCCESS']:
                            await button_ctx.send(f"{response['MESSAGE']}")
                            self.stop = True
                        else:
                            await button_ctx.send(f"{response['MESSAGE']}")
                            self.stop = True                           

                    if button_ctx.custom_id == "UNIVERSE_SOUL":
                        price = 5000000
                        response = await craft_adjuster(self, ctx, vault, universe, price, button_ctx.custom_id, None, completed_tales)
                        if response['SUCCESS']:
                            await button_ctx.send(f"{response['MESSAGE']}")
                            self.stop = True
                        else:
                            await button_ctx.send(f"{response['MESSAGE']}")
                            self.stop = True
                    if button_ctx.custom_id == "Destiny":
                        await button_ctx.defer(ignore=True)
                        price = 1500000
                        response = await craft_adjuster(self, ctx, vault, universe, price, card_info, None, completed_tales)
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True
                    if button_ctx.custom_id == "Skin":
                        await button_ctx.defer(ignore=True)
                        price = 2000000
                        response = await craft_adjuster(self, ctx, vault, universe, price, card_info, new_skin_list, completed_tales)
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True
                    if button_ctx.custom_id == "Card":
                        await button_ctx.defer(ignore=True)
                        price = 15000000
                        response = await craft_adjuster(self, ctx, vault, universe, price, "Card", new_skin_list, completed_tales)
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True                       
                    
                else:
                    await ctx.send("This is not your Craft.")

            await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))


    @cog_ext.cog_slash(description="View all of your cards", guild_ids=main.guild_ids)
    async def cards(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)#Storage Update
        storage_type = d['STORAGE_TYPE']
        vault = db.queryVault({'DID': d['DID']})
        try: 
            if vault:
                name = d['DISNAME'].split("#",1)[0]
                avatar = d['AVATAR']
                card_levels = vault['CARD_LEVELS']
                current_gems = []
                for gems in vault['GEMS']:
                    current_gems.append(gems['UNIVERSE'])
                balance = vault['BALANCE']
                cards_list = vault['CARDS']
                total_cards = len(cards_list)
                current_card = d['CARD']
                storage = vault['STORAGE']
                cards=[]
                icon = ":coin:"
                if balance >= 150000:
                    icon = ":money_with_wings:"
                elif balance >=100000:
                    icon = ":moneybag:"
                elif balance >= 50000:
                    icon = ":dollar:"
                
                embed_list = []

                for card in cards_list:
                    index = cards_list.index(card)
                    resp = db.queryCard({"NAME": str(card)})
                    card_tier = 0
                    lvl = ""
                    tier = ""
                    speed = 0
                    card_tier = f":mahjong: {resp['TIER']}"
                    card_available = resp['AVAILABLE']
                    card_exclusive = resp['EXCLUSIVE']
                    card_collection = resp['HAS_COLLECTION']
                    show_img = db.queryUniverse({'TITLE': resp['UNIVERSE']})['PATH']
                    affinity_message = crown_utilities.set_affinities(resp)
                    o_show = resp['UNIVERSE']
                    icon = ":flower_playing_cards:"
                    if card_available and card_exclusive:
                        icon = ":fire:"
                    elif card_available == False and card_exclusive ==False:
                        if card_collection:
                            icon =":sparkles:"
                        else:
                            icon = ":japanese_ogre:"
                    card_lvl = 0
                    card_exp = 0
                    card_lvl_attack_buff = 0
                    card_lvl_defense_buff = 0
                    card_lvl_ap_buff = 0
                    card_lvl_hlt_buff = 0

                    for cl in card_levels:
                        if card == cl['CARD']:
                            
                            licon = "🔰"
                            if cl['LVL'] >= 200:
                                licon ="🔱"
                            if cl['LVL'] >= 700:
                                licon ="⚜️"
                            if cl['LVL'] >= 999:
                                licon = "🏅"
                            lvl = f"{licon} **{cl['LVL']}**"
                            card_lvl = cl['LVL']
                            card_exp = cl['EXP']
                            card_lvl_ap_buff = crown_utilities.level_sync_stats(card_lvl, "AP")
                            card_lvl_attack_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                            card_lvl_defense_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                            card_lvl_hlt_buff = crown_utilities.level_sync_stats(card_lvl, "HLT")
                            
                    
                    o_passive = resp['PASS'][0] 
                    o_moveset = resp['MOVESET']
                    o_1 = o_moveset[0]
                    o_2 = o_moveset[1]
                    o_3 = o_moveset[2]
                    o_enhancer = o_moveset[3]
                    
                    # Move 1
                    move1 = list(o_1.keys())[0]
                    move1ap = list(o_1.values())[0] + card_lvl_ap_buff
                    move1_stamina = list(o_1.values())[1]
                    move1_element = list(o_1.values())[2]
                    move1_emoji = crown_utilities.set_emoji(move1_element)
                    
                    # Move 2
                    move2 = list(o_2.keys())[0]
                    move2ap = list(o_2.values())[0] + card_lvl_ap_buff
                    move2_stamina = list(o_2.values())[1]
                    move2_element = list(o_2.values())[2]
                    move2_emoji = crown_utilities.set_emoji(move2_element)


                    # Move 3
                    move3 = list(o_3.keys())[0]
                    move3ap = list(o_3.values())[0] + card_lvl_ap_buff
                    move3_stamina = list(o_3.values())[1]
                    move3_element = list(o_3.values())[2]
                    move3_emoji = crown_utilities.set_emoji(move3_element)


                    # Move Enhancer
                    move4 = list(o_enhancer.keys())[0]
                    move4ap = list(o_enhancer.values())[0]
                    move4_stamina = list(o_enhancer.values())[1]
                    move4enh = list(o_enhancer.values())[2]

                    passive_name = list(o_passive.keys())[0]
                    passive_num = list(o_passive.values())[0]
                    passive_type = list(o_passive.values())[1]
                
                    if passive_type:
                        value_for_passive = resp['TIER'] * .5
                        flat_for_passive = round(10 * (resp['TIER'] * .5))
                        stam_for_passive = 5 * (resp['TIER'] * .5)
                        if passive_type == "HLT":
                            passive_num = value_for_passive
                        if passive_type == "LIFE":
                            passive_num = value_for_passive
                        if passive_type == "ATK":
                            passive_num = value_for_passive
                        if passive_type == "DEF":
                            passive_num = value_for_passive
                        if passive_type == "STAM":
                            passive_num = stam_for_passive
                        if passive_type == "DRAIN":
                            passive_num = stam_for_passive
                        if passive_type == "FLOG":
                            passive_num = value_for_passive
                        if passive_type == "WITHER":
                            passive_num = value_for_passive
                        if passive_type == "RAGE":
                            passive_num = value_for_passive
                        if passive_type == "BRACE":
                            passive_num = value_for_passive
                        if passive_type == "BZRK":
                            passive_num = value_for_passive
                        if passive_type == "CRYSTAL":
                            passive_num = value_for_passive
                        if passive_type == "FEAR":
                            passive_num = flat_for_passive
                        if passive_type == "GROWTH":
                            passive_num = flat_for_passive
                        if passive_type == "CREATION":
                            passive_num = value_for_passive
                        if passive_type == "DESTRUCTION":
                            passive_num = value_for_passive
                        if passive_type == "SLOW":
                            passive_num = "1"
                        if passive_type == "HASTE":
                            passive_num = "1"
                        if passive_type == "STANCE":
                            passive_num = flat_for_passive
                        if passive_type == "CONFUSE":
                            passive_num = flat_for_passive
                        if passive_type == "BLINK":
                            passive_num = stam_for_passive

                    traits = ut.traits
                    mytrait = {}
                    traitmessage = ''
                    for trait in traits:
                        if trait['NAME'] == o_show:
                            mytrait = trait
                        if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                            if trait['NAME'] == 'Pokemon':
                                mytrait = trait
                    if mytrait:
                        traitmessage = f"**{mytrait['EFFECT']}:** {mytrait['TRAIT']}"


                    embedVar = discord.Embed(title= f"{resp['NAME']}", description=textwrap.dedent(f"""\
                    {icon} **[{index}]** 
                    {card_tier}: {lvl}
                    :heart: **{resp['HLT']}** :dagger: **{resp['ATK']}** :shield: **{resp['DEF']}** 🏃 **{resp['SPD']}**

                    {move1_emoji} **{move1}:** {move1ap}
                    {move2_emoji} **{move2}:** {move2ap}
                    {move3_emoji} **{move3}:** {move3ap}
                    🦠 **{move4}:** {move4enh} {move4ap}{enhancer_suffix_mapping[move4enh]}

                    🩸 **{passive_name}:** {passive_type.title()} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}
                    ♾️ {traitmessage}
                    """), colour=0x7289da)
                    embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                    embedVar.set_thumbnail(url=show_img)
                    embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                    embed_list.append(embedVar)

                buttons = [
                    manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                    manage_components.create_button(style=1, label="Resell/Dismantle", custom_id="Econ"),
                    manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                    manage_components.create_button(style=2, label="Swap/Store", custom_id="Storage")
                ]
                custom_action_row = manage_components.create_actionrow(*buttons)
                # custom_button = manage_components.create_button(style=3, label="Equip")

                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        updated_vault = db.queryVault({'DID': d['DID']})
                        sell_price = 0
                        selected_card = str(button_ctx.origin_message.embeds[0].title)
                        if button_ctx.custom_id == "Equip":
                            if selected_card in updated_vault['CARDS']:
                                selected_universe = custom_function
                                custom_function.selected_universe = selected_card
                                user_query = {'DID': str(ctx.author.id)}
                                response = db.updateUserNoFilter(user_query, {'$set': {'CARD': selected_card}})
                                await button_ctx.send(f":flower_playing_cards: **{selected_card}** equipped.")
                                self.stop = True
                            else:
                                await button_ctx.send(f"**{selected_card}** is no longer in your vault.")
                        
                        elif button_ctx.custom_id == "Econ":
                            await button_ctx.defer(ignore=True)
                            econ_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Resell",
                                            custom_id="resell"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.red,
                                            label="Dismantle",
                                            custom_id="dismantle"
                                        )
                                    ]
                            econ_buttons_action_row = manage_components.create_actionrow(*econ_buttons)
                            msg = await ctx.send(f"Would you like to Resell or Dismantle", components=[econ_buttons_action_row])
                            def check(button_ctx):
                                return button_ctx.author == ctx.author
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[econ_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "resell":
                                    await button_ctx.defer(ignore=True)
                                    card_data = db.queryCard({'NAME': selected_card})
                                    card_name = card_data['NAME']
                                    sell_price = sell_price + (card_data['PRICE'] * .15)
                                    if card_name == current_card:
                                        await button_ctx.send("You cannot resell equipped cards.")
                                    elif card_name in updated_vault['CARDS']:
                                        sell_buttons = [
                                            manage_components.create_button(
                                                style=ButtonStyle.green,
                                                label="Yes",
                                                custom_id="yes"
                                            ),
                                            manage_components.create_button(
                                                style=ButtonStyle.blue,
                                                label="No",
                                                custom_id="no"
                                            )
                                        ]
                                        sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                                        msg = await button_ctx.send(f"Are you sure you want to sell **{card_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                                        
                                        def check(button_ctx):
                                            return button_ctx.author == ctx.author

                                        
                                        try:
                                            button_ctx: ComponentContextSell = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                                            if button_ctx.custom_id == "no":
                                                await button_ctx.send("Sell cancelled. ")
                                            if button_ctx.custom_id == "yes":
                                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARDS': card_name}})
                                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
                                                await crown_utilities.bless(sell_price, ctx.author.id)
                                                await msg.delete()
                                                await button_ctx.send(f"**{card_name}** has been sold.")
                                        except Exception as ex:
                                            trace = []
                                            tb = ex.__traceback__
                                            while tb is not None:
                                                trace.append({
                                                    "filename": tb.tb_frame.f_code.co_filename,
                                                    "name": tb.tb_frame.f_code.co_name,
                                                    "lineno": tb.tb_lineno
                                                })
                                                tb = tb.tb_next
                                            print(str({
                                                'PLAYER': str(ctx.author),
                                                'type': type(ex).__name__,
                                                'message': str(ex),
                                                'trace': trace
                                            }))
                                            await ctx.send("There's an issue with selling one or all of your items.")
                                            return
                                    else:
                                        await button_ctx.send(f"**{card_name}** is no longer in your vault.")
                                if button_ctx.custom_id == "dismantle":
                                    await button_ctx.defer(ignore=True)
                                    card_data = db.queryCard({'NAME': selected_card})
                                    card_tier =  card_data['TIER']
                                    card_health = card_data['HLT']
                                    card_name = card_data['NAME']
                                    selected_universe = card_data['UNIVERSE']
                                    o_moveset = card_data['MOVESET']
                                    o_3 = o_moveset[2]
                                    element = list(o_3.values())[2]
                                    essence_amount = (200 * card_tier)
                                    o_enhancer = o_moveset[3]

                                    dismantle_amount = (10000 * card_tier) + card_health
                                    if card_name == current_card:
                                        await button_ctx.send("You cannot dismantle equipped cards.")
                                    elif card_name in updated_vault['CARDS']:
                                        dismantle_buttons = [
                                            manage_components.create_button(
                                                style=ButtonStyle.green,
                                                label="Yes",
                                                custom_id="yes"
                                            ),
                                            manage_components.create_button(
                                                style=ButtonStyle.blue,
                                                label="No",
                                                custom_id="no"
                                            )
                                        ]
                                        dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                                        msg = await button_ctx.send(f"Are you sure you want to dismantle **{card_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                                        
                                        def check(button_ctx):
                                            return button_ctx.author == ctx.author

                                        
                                        try:
                                            button_ctx: ComponentContextDismantle = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                            if button_ctx.custom_id == "no":
                                                await button_ctx.send("Dismantle cancelled. ")
                                            if button_ctx.custom_id == "yes":
                                                if selected_universe in current_gems:
                                                    query = {'DID': str(ctx.author.id)}
                                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                                    response = db.updateVault(query, update_query, filter_query)
                                                else:
                                                    response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                                em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARDS': card_name}})
                                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
                                                #await crown_utilities.bless(sell_price, ctx.author.id)
                                                await msg.delete()
                                                await button_ctx.send(f"**{card_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}. Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence.")
                                                
                                        except Exception as ex:
                                            trace = []
                                            tb = ex.__traceback__
                                            while tb is not None:
                                                trace.append({
                                                    "filename": tb.tb_frame.f_code.co_filename,
                                                    "name": tb.tb_frame.f_code.co_name,
                                                    "lineno": tb.tb_lineno
                                                })
                                                tb = tb.tb_next
                                            print(str({
                                                'PLAYER': str(ctx.author),
                                                'type': type(ex).__name__,
                                                'message': str(ex),
                                                'trace': trace
                                            }))
                                            await ctx.send("There's an issue with selling one or all of your items.")
                                            return
                                    else:
                                        await button_ctx.send(f"**{card_name}** is no longer in your vault.")
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                        
                        elif button_ctx.custom_id == "Trade":
                            
                            card_data = db.queryCard({'NAME' : selected_card})
                            card_name= card_data['NAME']
                            sell_price = card_data['PRICE'] * .10
                            mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                            mvalidation=False
                            bvalidation=False
                            item_already_in_trade=False
                            if card_name == current_card:
                                await button_ctx.send("You cannot trade equipped cards.")
                            else:
                                if mtrade:
                                    if selected_card in mtrade['MCARDS']:
                                        await ctx.send(f"{ctx.author.mention} card already in **Trade**")
                                        item_already_in_trade=True
                                    mvalidation=True
                                else:
                                    btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                                    if btrade:
                                        if selected_card in btrade['BCARDS']:
                                            await ctx.send(f"{ctx.author.mention} card already in **Trade**")
                                            item_already_in_trade=True
                                        bvalidation=True
                                    else:
                                        await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                        return
                                if item_already_in_trade:
                                    trade_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Yes",
                                            custom_id="yes"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.blue,
                                            label="No",
                                            custom_id="no"
                                        )
                                    ]
                                    trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                    await button_ctx.send(f"Would you like to remove **{selected_card}** from the **Trade**?", components=[trade_buttons_action_row])
                                    
                                    def check(button_ctx):
                                        return button_ctx.author == ctx.author

                                    
                                    try:
                                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                        if button_ctx.custom_id == "no":
                                                await button_ctx.send("Happy Trading")
                                                self.stop = True
                                        if button_ctx.custom_id == "yes":
                                            neg_sell_price = 0 - abs(int(sell_price))
                                            if mvalidation:
                                                trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                                update_query = {"$pull" : {'MCARDS': selected_card}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                                resp = db.updateTrade(trade_query, update_query)
                                                await button_ctx.send("Returned.")
                                                self.stop = True
                                            elif bvalidation:
                                                trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                                update_query = {"$pull" : {'BCARDS': selected_card}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                                resp = db.updateTrade(trade_query, update_query)
                                                await button_ctx.send("Returned.")
                                                self.stop = True
                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'PLAYER': str(ctx.author),
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        await ctx.send("There's an issue with trading one or all of your items.")
                                        return   
                                elif mvalidation == True or bvalidation ==True:    #If user is valid
                                    sell_price = card_data['PRICE'] * .10
                                    trade_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Yes",
                                            custom_id="yes"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.blue,
                                            label="No",
                                            custom_id="no"
                                        )
                                    ]
                                    trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                    await button_ctx.send(f"Are you sure you want to trade **{selected_card}**", components=[trade_buttons_action_row])
                                    try:
                                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                        if button_ctx.custom_id == "no":
                                                await button_ctx.send("Not this time. ")
                                                self.stop = True
                                        if button_ctx.custom_id == "yes":
                                            if mvalidation:
                                                trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                                update_query = {"$push" : {'MCARDS': selected_card}, "$inc" : {'TAX' : int(sell_price)}}
                                                resp = db.updateTrade(trade_query, update_query)
                                                await button_ctx.send("Trade staged.")
                                                self.stop = True
                                            elif bvalidation:
                                                trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                                update_query = {"$push" : {'BCARDS': selected_card}, "$inc" : {'TAX' : int(sell_price)}}
                                                resp = db.updateTrade(trade_query, update_query)
                                                await button_ctx.send("Trade staged.")
                                                self.stop = True
                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'PLAYER': str(ctx.author),
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        await ctx.send("There's an issue with trading one or all of your items.")
                                        return   
                            
                        elif button_ctx.custom_id == "Storage":
                            await button_ctx.defer(ignore=True)
                            storage_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Swap Storage Card",
                                            custom_id="swap"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.red,
                                            label="Add to Storage",
                                            custom_id="store"
                                        )
                                    ]
                            storage_buttons_action_row = manage_components.create_actionrow(*storage_buttons)
                            msg = await ctx.send(f"Would you like to Swap Cards or Add Card to Storage", components=[storage_buttons_action_row])
                            def check(button_ctx):
                                return button_ctx.author == ctx.author
                            try:
                                button_ctx: ComponentContextStorage = await manage_components.wait_for_component(self.bot, components=[storage_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "swap":
                                    await button_ctx.defer(ignore=True)
                                    await msg.delete()
                                    await ctx.send(f"{ctx.author.mention}, Which card number would you like to swap with in storage?")
                                    def check(msg):
                                        return msg.author == ctx.author

                                    try:
                                        msg = await self.bot.wait_for('message', check=check, timeout=30)
                                        author = msg.author
                                        content = msg.content
                                        # print("Author: " + str(author))
                                        # print("Content: " + str(content))
                                        # print(msg)
                                        if storage[int(msg.content)]:
                                            swap_with = storage[int(msg.content)]
                                            query = {'DID': str(msg.author.id)}
                                            update_storage_query = {
                                                '$pull': {'CARDS': selected_card},
                                                '$addToSet': {'STORAGE': selected_card},
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)

                                            update_storage_query = {
                                                '$pull': {'STORAGE': swap_with},
                                                '$addToSet': {'CARDS': swap_with}
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)

                                            await msg.delete()
                                            await ctx.send(f"**{selected_card}** has been swapped with **{swap_with}**")
                                            return
                                        else:
                                            await ctx.send("The card number you want to swap with does not exist.")
                                            return

                                    except Exception as e:
                                        return False
                                if button_ctx.custom_id == "store":
                                    await button_ctx.defer(ignore=True)
                                    
                                    try:
                                        author = msg.author
                                        content = msg.content
                                        # print("Author: " + str(author))
                                        # print("Content: " + str(content))
                                        if len(storage) <= (storage_type * 15):
                                            query = {'DID': str(ctx.author.id)}
                                            update_storage_query = {
                                                '$pull': {'CARDS': selected_card},
                                                '$addToSet': {'STORAGE': selected_card},
                                            }
                                            response = db.updateVaultNoFilter(query, update_storage_query)
                                            
                                            await msg.delete()
                                            await ctx.send(f"**{selected_card}** has been added to storage")
                                            return
                                        else:
                                            await ctx.send("Not enough space in storage")
                                            return

                                    except Exception as e:
                                        return False
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                            
                            self.stop = True
                    else:
                        await ctx.send("This is not your card list.")
                await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
            else:
                newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("There's an issue with loading your cards. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
            return


    @cog_ext.cog_slash(description="Draw, Dismantle or Resell cards from storage",
                    options=[
                        create_option(
                            name="mode",
                            description="Draw: Draw card, Dismantle:  Dismantle storage card, Resll: Resell storage card",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="💼🎴 Draw Card",
                                    value="cdraw"
                                ),
                                create_choice(
                                    name="💎🎴 Dismantle Card",
                                    value="cdismantle"
                                ),
                                create_choice(
                                    name="🪙🎴 Resell Card",
                                    value="cresell"
                                ),create_choice(
                                    name="💼🎗️ Draw Title",
                                    value="tdraw"
                                ),
                                create_choice(
                                    name="💎🎗️ Dismantle Title",
                                    value="tdismantle"
                                ),
                                create_choice(
                                    name="🪙🎗️ Resell Title",
                                    value="tresell"
                                ),create_choice(
                                    name="💼🦾 Draw Arm",
                                    value="adraw"
                                ),
                                create_choice(
                                    name="💎🦾 Dismantle Arm",
                                    value="adismantle"
                                ),
                                create_choice(
                                    name="🪙🦾 Resell Arm",
                                    value="aresell"
                                )
                            ]
                        ),create_option(
                            name="item",
                            description="Storage Item Name",
                            option_type=3,
                            required=True,
                        )
                    ]
        , guild_ids=main.guild_ids)
    async def draw(self, ctx: SlashContext, mode : str, item : str ):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)#Storage Update
        storage_type = d['STORAGE_TYPE']
        vault = db.queryVault({'DID': d['DID']})
        card_name = item
        title_name = item
        arm_name = item
        current_gems = []
        try: 
            if vault:
                for gems in vault['GEMS']:
                    current_gems.append(gems['UNIVERSE'])
                cards_list = vault['CARDS']
                title_list = vault['TITLES']
                arm_list = vault['ARMS']
                arm_list_names = []
                for names in arm_list:
                    arm_list_names.append(names['ARM'])
                total_cards = len(cards_list)
                total_titles = len(title_list)
                total_arms = len(arm_list)
                cstorage = vault['STORAGE']
                tstorage = vault['TSTORAGE']
                astorage = vault['ASTORAGE']
                storage_arm_names = []
                for snames in astorage:
                    storage_arm_names.append(snames['ARM'])
                
                storage_card = db.queryCard({'NAME': {"$regex": f"^{str(item)}$", "$options": "i"}})
                storage_title = db.queryTitle({'TITLE':{"$regex": f"^{str(item)}$", "$options": "i"} })
                storage_arm = db.queryArm({'ARM':{"$regex": f"^{str(item)}$", "$options": "i"}})
                
                if mode == 'cdraw':
                    if total_cards > 24:
                        await ctx.send("You already have 25 cards.")
                        return
                    if storage_card:                  
                        if storage_card['NAME'] in cstorage:
                            query = {'DID': str(ctx.author.id)}
                            update_storage_query = {
                                '$pull': {'STORAGE': storage_card['NAME']},
                                '$addToSet': {'CARDS': storage_card['NAME']},
                            }
                            response = db.updateVaultNoFilter(query, update_storage_query)
                            await ctx.send(f"🎴**{storage_card['NAME']}** has been added to **/cards**")
                            return
                        else:
                            await ctx.send(f"🎴:{storage_card['NAME']} does not exist in storage.")
                            return
                    else:
                        await ctx.send(f"🎴:{storage_card['NAME']} does not exist.")
                        return
                if mode == 'tdraw':
                    if total_titles > 24:
                        await ctx.send("You already have 25 titles.")
                        return
                    if storage_title:                  
                        if storage_title['TITLE'] in tstorage: #title storage update
                            query = {'DID': str(ctx.author.id)}
                            update_storage_query = {
                                '$pull': {'TSTORAGE': storage_title['TITLE']},
                                '$addToSet': {'TITLES': storage_title['TITLE']},
                            }
                            response = db.updateVaultNoFilter(query, update_storage_query)
                            await ctx.send(f"🎗️ **{storage_title['TITLE']}** has been added to **/titles**")
                            return
                        else:
                            await ctx.send(f"🎗️:{storage_title['TITLE']} does not exist in storage.")
                            return
                    else:
                        await ctx.send(f"🎗️:{storage_title['TITLE']} does not exist.")
                        return
                if mode == 'adraw':
                    if total_arms > 24:
                        await ctx.send("You already have 25 arms.")
                        return
                    if storage_arm:                  
                        if storage_arm['ARM'] in storage_arm_names: #title storage update
                            durability = 0
                            for arms in astorage:
                                if storage_arm['ARM'] == arms['ARM']:
                                    durability = arms['DUR']
                                    print(durability)
                            query = {'DID': str(ctx.author.id)}
                            update_storage_query = {
                                '$pull': {'ASTORAGE': {'ARM' : str(storage_arm['ARM'])}},
                                '$addToSet': {'ARMS': {'ARM' : str(storage_arm['ARM']) , 'DUR': int(durability)}},
                            }
                            response = db.updateVaultNoFilter(query, update_storage_query)
                            await ctx.send(f"🦾 **{storage_arm['ARM']}** has been added to **/arms**")
                            return
                        else:
                            await ctx.send(f"🦾 :{storage_arm['ARM']} does not exist in storage.")
                            return
                    else:
                        await ctx.send(f"🦾 :{storage_arm['ARM']} does not exist.")
                if mode == 'cdismantle':
                    card_data = storage_card
                    card_tier =  card_data['TIER']
                    card_health = card_data['HLT']
                    card_name = card_data['NAME']
                    selected_universe = card_data['UNIVERSE']
                    o_moveset = card_data['MOVESET']
                    o_3 = o_moveset[2]
                    element = list(o_3.values())[2]
                    essence_amount = (200 * card_tier)
                    o_enhancer = o_moveset[3]

                    dismantle_amount = (10000 * card_tier) + card_health
                    if card_name in vault['STORAGE']:
                        dismantle_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                        msg = await ctx.send(f"Are you sure you want to dismantle **{card_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextDismantle = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                            if button_ctx.custom_id == "yes":
                                if selected_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                    response = db.updateVault(query, update_query, filter_query)
                                else:
                                    response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'STORAGE': card_name}})
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
                                #await crown_utilities.bless(sell_price, ctx.author.id)
                                await msg.delete()
                                await button_ctx.send(f"**{card_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}. Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                            return
                    else:
                        await ctx.send(f"**{card_name}** not in storage.. Please check spelling", hidden=True)
                        return
                if mode == 'tdismantle':
                    title_data = storage_title
                    title_name = title_data['TITLE']
                    dismantle_amount = 1000
                    selected_universe = title_data['UNIVERSE']
                    if title_name in vault['TSTORAGE']:
                        dismantle_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                        msg = await ctx.send(f"Are you sure you want to dismantle **{title_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextDismantle = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                            if button_ctx.custom_id == "yes":
                                if selected_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                    response = db.updateVault(query, update_query, filter_query)
                                else:
                                    response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TSTORAGE': title_name}})
                                await msg.delete()
                                await button_ctx.send(f"**{title_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                            return
                    else:
                        await ctx.send(f"**{title_name}** not in storage.. Please check spelling", hidden=True)
                        return
                if mode == 'adismantle':
                    arm_data = storage_arm
                    arm_name = arm_data['ARM']
                    element = arm_data['ELEMENT']
                    essence_amount = 100
                    arm_passive = arm_data['ABILITIES'][0]
                    arm_passive_type = list(arm_passive.keys())[0]
                    arm_passive_value = list(arm_passive.values())[0]
                    move_types = ["BASIC", "SPECIAL", "ULTIMATE"]
                    if arm_data["EXCLUSIVE"]:
                        essence_amount = 250
                    selected_universe = arm_data['UNIVERSE']
                    dismantle_amount = 10000
                    storage_arm_names = []
                    for names in vault['ASTORAGE']:
                        if arm_name == names['ARM']:
                            storage_arm_names = names['ARM']
                    if arm_name == storage_arm_names:
                        dismantle_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                        msg = await ctx.send(f"Are you sure you want to dismantle **{arm_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextDismantle = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                            if button_ctx.custom_id == "yes":
                                if selected_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                    response = db.updateVault(query, update_query, filter_query)
                                else:
                                    response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ASTORAGE': {'ARM' : str(arm_name)}}})
                                #await crown_utilities.bless(sell_price, ctx.author.id)
                                await msg.delete()
                                await button_ctx.send(f"**{arm_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}. Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                            return
                    else:
                        await ctx.send(f"**{card_name}** not in storage.. Please check spelling", hidden=True)
                        return
                if mode == 'cresell':
                    card_data = storage_card
                    card_name = card_data['NAME']
                    sell_price = 0
                    sell_price = sell_price + (card_data['PRICE'] * .15)
                    if card_name in vault['STORAGE']:
                        sell_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                        msg = await ctx.send(f"Are you sure you want to sell **{card_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextSell = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Sell cancelled. ")
                            if button_ctx.custom_id == "yes":
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'STORAGE': card_name}})
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
                                await crown_utilities.bless(sell_price, ctx.author.id)
                                await msg.delete()
                                await button_ctx.send(f"**{card_name}** has been sold.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'PLAYER': str(ctx.author),
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send("There's an issue with selling one or all of your items.")
                            return
                    else:
                        await ctx.send(f"**{card_name}** not in storage.. Please check spelling", hidden=True)
                        return
                if mode == 'tresell':
                    title_data = storage_title
                    title_name = title_data['TITLE']
                    sell_price = 1
                    sell_price = sell_price + (title_data['PRICE'] * .10)
                    selected_universe = title_data['UNIVERSE']
                    if title_name in vault['TSTORAGE']:
                        sell_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                        msg = await ctx.send(f"Are you sure you want to sell **{title_name}** for :coin: {round(sell_price)}?", components=[sell_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Sell cancelled. ")
                            if button_ctx.custom_id == "yes":
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TSTORAGE': title_name}})
                                await crown_utilities.bless(sell_price, ctx.author.id)
                                await msg.delete()
                                await button_ctx.send(f"**{title_name}** has been sold.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                            return
                    else:
                        await ctx.send(f"**{title_name}** not in storage.. Please check spelling", hidden=True)
                        return
                if mode == 'aresell':
                    arm_data = storage_arm
                    arm_name = arm_data['ARM']
                    sell_price = 1
                    sell_price = sell_price + (arm_data['PRICE'] * .07)
                    selected_universe = arm_data['UNIVERSE']
                    storage_arm_names = []
                    for names in vault['ASTORAGE']:
                        if arm_name == names['ARM']:
                            storage_arm_names = names['ARM']
                    if arm_name in storage_arm_names:
                        sell_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                        msg = await ctx.send(f"Are you sure you want to sell **{arm_name}** for :coin: {round(sell_price)}?", components=[sell_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Sell cancelled. ")
                            if button_ctx.custom_id == "yes":
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ASTORAGE': {'ARM' :str(arm_name)}}})
                                await crown_utilities.bless(sell_price, ctx.author.id)
                                await msg.delete()
                                await button_ctx.send(f"**{arm_name}** has been sold.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                            return
                    else:
                        await ctx.send(f"**{title_name}** not in storage.. Please check spelling", hidden=True)
                        return
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
            return



async def craft_adjuster(self, player, vault, universe, price, item, skin_list, completed_tales):
    try:
        base_title = db.queryTitle({'TITLE':'Starter'})
        item_bools = [
            'UNIVERSE_HEART', 
            'UNIVERSE_SOUL'
        ]
        gems = 0
        price_ = int(price)
        print(price_)
        universe_heart = False
        universe_soul = False
        has_gems_for = False
        destiny_revive_list = []
        negPriceAmount = 0 - abs(int(price))
        response = {}
        for uni in vault['GEMS']:
            if uni['UNIVERSE'] == universe:
                gems = uni['GEMS']
                universe_heart = uni['UNIVERSE_HEART']
                universe_soul = uni['UNIVERSE_SOUL']
                has_gems_for = True

        #owned levels
        owned_card_levels_list = []
        for c in vault['CARD_LEVELS']:
            owned_card_levels_list.append(c['CARD'])
            
        #owned Destinies
        owned_destinies = []
        for destiny in vault['DESTINY']:
            owned_destinies.append(destiny['NAME'])

        if has_gems_for:
            if gems >= price:
                print(price_)
                if item == "Card":
                    if universe in completed_tales:
                        acceptable = [4,5,6,7]
                        list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}, 'HAS_COLLECTION': False, 'AVAILABLE': True})]
                        selection_length = len(list(list_of_cards)) - 1
                        if selection_length == 0:
                            card = list_of_cards[0]
                        else:
                            selection = random.randint(0,selection_length)
                            card = list_of_cards[selection]
                        card_name = card['NAME']
                        response = await crown_utilities.store_drop_card(str(player.author.id), card_name, universe, vault, owned_destinies, 0, 100000, "Purchase", False, 0, "cards")
                        if response:
                            query = {'DID': str(player.author.id)}
                            update_query = {
                                '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}
                            }
                            filter_query = [{'type.' + "UNIVERSE": universe}]
                            res = db.updateVault(query, update_query, filter_query)
                            rr = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": response}
                            return rr
                    else:
                        response = f"You need to complete the **Tale** for this universe to unlock **Dungeon Card Crafting**!"
                        rr = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": response}
                        return rr



                if item not in item_bools:
                    if not skin_list:
                        if price == 2000000: #check if price is for skins
                            response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Your **{item['NAME']}** does not have Skins in **{universe}**!"}
                            return response
                        card_universe = item['UNIVERSE']
                        card_name = item['NAME']
                        card_has_destiny = False
                        destiny_wins = 0
                        destiny_required_wins = 0
                        destiny_name = ""
                        destiny_earn = ""
                        destiny_universe = ""
                        destiny_defeat = ""
                        cards_destiny_list = []
                        
                        if card_universe != universe:
                            response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Your **{card_name}** does not have a Destiny Line in **{universe}**!"}
                            # await player.send(f"Your **{card_name}** does not have a Destiny Line in **{universe}**!")
                            return response
                        
                        if vault['DESTINY']:
                            for destiny in vault['DESTINY']:
                                d_card = ' '.join(destiny['USE_CARDS'])
                                d_card_info = db.queryCard({"NAME": str(d_card)})
                                if card_name in destiny['USE_CARDS'] and not destiny['COMPLETED'] and card_universe == universe or item['SKIN_FOR'] == d_card_info['NAME']:
                                    card_has_destiny = True
                                    cards_destiny_list.append(destiny)
                                    destiny_wins = destiny['WINS']
                                    destiny_required_wins = destiny['REQUIRED']
                                    destiny_name = destiny['NAME']
                                    destiny_earn = destiny['EARN']
                                    destiny_universe = destiny['UNIVERSE']
                                    destiny_defeat = destiny['DEFEAT']
        
                        if card_has_destiny:
                            print(price_)
                            embed_list = []
                            for destiny in cards_destiny_list:
                                embedVar = discord.Embed(title= f"{destiny['DEFEAT']}", description=textwrap.dedent(f"""
                                ✨ **{destiny['NAME']}**

                                **Wins** - *{destiny['WINS']}*
                                **Wins Required To Complete** - *{destiny['REQUIRED']}*
                                **Defeat** - *{destiny['DEFEAT']}*
                                **Reward** - **{destiny['EARN']}**
                                """), colour=0x7289da)
                                embedVar.set_footer(text=f"Select a Destiny Line to apply win to")
                                embed_list.append(embedVar)
                            

                            try:

                                buttons = [
                                    manage_components.create_button(style=3, label="Craft Win", custom_id="craft_d_win"),
                                    manage_components.create_button(style=3, label="Craft +5 Wins", custom_id="craft_d_win5"),
                                    manage_components.create_button(style=3, label="Craft +10 Wins", custom_id="craft_d_win10")
                                ]
                                custom_action_row = manage_components.create_actionrow(*buttons)

                                async def custom_function(self, button_ctx):
                                    if button_ctx.author == player.author:
                                        print(price_)
                                        selected_destiny = str(button_ctx.origin_message.embeds[0].title)
                                        updated_vault = db.queryVault({'DID': str(button_ctx.author.id)})
                                        if button_ctx.custom_id == "craft_d_win":
                                            gems = 0
                                            has_gems_for = False
                                            
                                            negPriceAmount = 0 - abs(int(price_))
                                            can_afford = False

                                            for uni in updated_vault['GEMS']:
                                                if uni['UNIVERSE'] == universe:
                                                    gems = uni['GEMS']
                                                    universe_heart = uni['UNIVERSE_HEART']
                                                    universe_soul = uni['UNIVERSE_SOUL']
                                                    has_gems_for = True
                                                    if gems >= price_:
                                                        can_afford = True
                                            
                                            if can_afford:
                                                r = await update_destiny_call(button_ctx.author, selected_destiny, "Tales", 1)
                                                
                                                if r == "Your storage is full. You are unable to completed the destiny until you have available storage for your new destiny card.":
                                                    await button_ctx.send(f"Your storage is full. You are unable to completed the destiny until you have available storage for your new destiny card.")
                                                    self.stop = True
                                                    return
                                                else:
                                                    query = {'DID': str(player.author.id)}
                                                    update_query = {
                                                        '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}
                                                    }
                                                    filter_query = [{'type.' + "UNIVERSE": universe}]
                                                    res = db.updateVault(query, update_query, filter_query)
                                                    await button_ctx.send(f":sparkles: | Crafting Destiny Win....Success!")
                                                    response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "Craft Success!"}
                                                    return response
                                                    self.stop = True
                                                    return
                                            else:
                                                await button_ctx.send(f"Insufficent 💎!")
                                                self.stop = True
                                                return
                                        if button_ctx.custom_id == "craft_d_win5":
                                            price_ = int(price_ * 5)
                                            print(price_)
                                            gems = 0
                                            has_gems_for = False
                                            negPriceAmount = 0 - abs(int(price_))
                                            can_afford = False

                                            for uni in updated_vault['GEMS']:
                                                if uni['UNIVERSE'] == universe:
                                                    gems = uni['GEMS']
                                                    universe_heart = uni['UNIVERSE_HEART']
                                                    universe_soul = uni['UNIVERSE_SOUL']
                                                    has_gems_for = True
                                                    if gems >= (price_):
                                                        can_afford = True
                                            
                                            if can_afford:
                                                r = await update_destiny_call(button_ctx.author, selected_destiny, "Tales", 5)
                                                
                                                if r == "Your storage is full. You are unable to completed the destiny until you have available storage for your new destiny card.":
                                                    await button_ctx.send(f"Your storage is full. You are unable to completed the destiny until you have available storage for your new destiny card.")
                                                    self.stop = True
                                                    return
                                                else:
                                                    query = {'DID': str(player.author.id)}
                                                    update_query = {
                                                        '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}
                                                    }
                                                    filter_query = [{'type.' + "UNIVERSE": universe}]
                                                    res = db.updateVault(query, update_query, filter_query)
                                                    await button_ctx.send(f":sparkles: | Crafting 5 Destiny Wins....Success!")
                                                    response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "Craft Success!"}
                                                    return response
                                                    self.stop = True
                                                    return
                                            else:
                                                await button_ctx.send(f"Insufficent 💎!")
                                                self.stop = True
                                                return
                                        if button_ctx.custom_id == "craft_d_win10":
                                            price_ = int(price_ * 10)
                                            gems = 0
                                            has_gems_for = False
                                            negPriceAmount = 0 - abs(int(price_))
                                            can_afford = False

                                            for uni in updated_vault['GEMS']:
                                                if uni['UNIVERSE'] == universe:
                                                    gems = uni['GEMS']
                                                    universe_heart = uni['UNIVERSE_HEART']
                                                    universe_soul = uni['UNIVERSE_SOUL']
                                                    has_gems_for = True
                                                    if gems >= (price_):
                                                        can_afford = True
                                            
                                            if can_afford:
                                                r = await update_destiny_call(button_ctx.author, selected_destiny, "Tales", 10)
                                                
                                                if r == "Your storage is full. You are unable to completed the destiny until you have available storage for your new destiny card.":
                                                    await button_ctx.send(f"Your storage is full. You are unable to completed the destiny until you have available storage for your new destiny card.")
                                                    self.stop = True
                                                    return
                                                else:
                                                    query = {'DID': str(player.author.id)}
                                                    update_query = {
                                                        '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}
                                                    }
                                                    filter_query = [{'type.' + "UNIVERSE": universe}]
                                                    res = db.updateVault(query, update_query, filter_query)
                                                    await button_ctx.send(f":sparkles: | Crafting 10 Destiny Wins....Success!")
                                                    response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "Craft Success!"}
                                                    return response
                                                    self.stop = True
                                                    return
                                            else:
                                                await button_ctx.send(f"Insufficent 💎!")
                                                self.stop = True
                                                return

                                await Paginator(bot=self.bot, disableAfterTimeout=True,useQuitButton=True, ctx=player, pages=embed_list, timeout=60, customActionRow=[
                                custom_action_row,
                                custom_function,
                                ]).run()

                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Craft Failed!"}
                                return response
                        else:
                            response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Your **{card_name}** does not have a Destiny Line in **{universe}**!"}
                            return response
                    else:
                        available_skins = skin_list
                        card_universe = item['UNIVERSE']
                        card_name = item['NAME']
                        card_has_skin = True
                        if card_universe != universe:
                            response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Your **{card_name}** does not have a Skin in **{universe}**!"}
                            return response
                        
                        if card_has_skin:
                            embed_list = []
                            for skins in skin_list:
                                s_moveset = skins['MOVESET']
                                s_passive = skins['PASS'][0]
                                s_enhancer = s_moveset[3]
                                move1 = s_moveset[0] 
                                move2 = s_moveset[1] 
                                move3 = s_moveset[2] 
                                
                                move1name = list(move1.keys())[0]
                                move2name = list(move2.keys())[0]
                                move3name = list(move3.keys())[0]
                                
                                move1ap = list(move1.values())[0]
                                move2ap = list(move2.values())[0]
                                move3ap = list(move3.values())[0]
                                
                                basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
                                super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
                                ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])
                                
                                enhmove = list(s_enhancer.keys())[0]
                                enhap = list(s_enhancer.values())[0]
                                enh = list(s_enhancer.values())[2]
                                
                                passive_name = list(s_passive.keys())[0]
                                passive_num = list(s_passive.values())[0]
                                passive_type = list(s_passive.values())[1]
    
               
                                if passive_type:
                                    value_for_passive = skins['TIER'] * .5
                                    flat_for_passive = 10 * (skins['TIER'] * .5)
                                    stam_for_passive = 5 * (skins['TIER'] * .5)
                                    if passive_type == "HLT":
                                        passive_num = value_for_passive
                                    if passive_type == "LIFE":
                                        passive_num = value_for_passive
                                    if passive_type == "ATK":
                                        passive_num = value_for_passive
                                    if passive_type == "DEF":
                                        passive_num = value_for_passive
                                    if passive_type == "STAM":
                                        passive_num = stam_for_passive
                                    if passive_type == "DRAIN":
                                        passive_num = stam_for_passive
                                    if passive_type == "FLOG":
                                        passive_num = value_for_passive
                                    if passive_type == "WITHER":
                                        passive_num = value_for_passive
                                    if passive_type == "RAGE":
                                        passive_num = value_for_passive
                                    if passive_type == "BRACE":
                                        passive_num = value_for_passive
                                    if passive_type == "BZRK":
                                        passive_num = value_for_passive
                                    if passive_type == "CRYSTAL":
                                        passive_num = value_for_passive
                                    if passive_type == "FEAR":
                                        passive_num = flat_for_passive
                                    if passive_type == "GROWTH":
                                        passive_num = flat_for_passive
                                    if passive_type == "CREATION":
                                        passive_num = value_for_passive
                                    if passive_type == "DESTRUCTION":
                                        passive_num = value_for_passive
                                    if passive_type == "SLOW":
                                        passive_num = "1"
                                    if passive_type == "HASTE":
                                        passive_num = "1"
                                    if passive_type == "STANCE":
                                        passive_num = flat_for_passive
                                    if passive_type == "CONFUSE":
                                        passive_num = flat_for_passive
                                    if passive_type == "BLINK":
                                        passive_num = stam_for_passive


                                traits = ut.traits
                                mytrait = {}
                                traitmessage = ''
                                o_show = skins['UNIVERSE']
                                for trait in traits:
                                    if trait['NAME'] == o_show:
                                        mytrait = trait
                                    if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                                        if trait['NAME'] == 'Pokemon':
                                            mytrait = trait
                                if mytrait:
                                    traitmessage = f"**{mytrait['EFFECT']}:** {mytrait['TRAIT']}"
                                    
                                skin_stats = showcard("non-battle", skins, "none", skins['HLT'],skins['HLT'], skins['STAM'],skins['STAM'], False, base_title, False, skins['ATK'], skins['DEF'], 0, move1ap, move2ap, move3ap, enhap, enh, 0, None )
                                embedVar = discord.Embed(title= f"{skins['NAME']}", description=textwrap.dedent(f"""
                                :mahjong: {skins['TIER']}: 🃏 **{skins['SKIN_FOR']}** 
                                :heart: **{skins['HLT']}** :dagger: **{skins['ATK']}** :shield: **{skins['DEF']}**
                                
                                {basic_attack_emoji} **{move1name}:** {move1ap}
                                {super_attack_emoji} **{move2name}:** {move2ap}
                                {ultimate_attack_emoji} **{move3name}:** {move3ap}
                                🦠 **{enhmove}:** {enh} {enhap}{enhancer_suffix_mapping[enh]}

                                🩸 **{passive_name}:** {passive_type} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}
                                ♾️ {traitmessage}
                                **Universe** - *{skins['UNIVERSE']}*
                                """), colour=0x7289da)
                                embedVar.set_footer(text=f"Select a Skin!")
                                embedVar.set_image(url="attachment://image.png")
                                embed_list.append(embedVar)
                        try:

                            buttons = [
                                manage_components.create_button(style=3, label="Craft Skin", custom_id="craft_skin")
                            ]
                            custom_action_row = manage_components.create_actionrow(*buttons)

                            async def custom_function(self, button_ctx):
                                if button_ctx.author == player.author:
                                    selected_skin = str(button_ctx.origin_message.embeds[0].title)
                                    if button_ctx.custom_id == "craft_skin":
                                        #r = await update_destiny_call(button_ctx.author, selected_destiny, "Tales")
                                        
                                        query = {'DID': str(vault['DID'])}
                                        skin_response = db.updateVaultNoFilter(query,{'$addToSet': {'CARDS': str(selected_skin)}})
                                        
                                        # Add Card Level config
                                        if selected_skin not in owned_card_levels_list:
                                            update_query = {'$addToSet': {
                                                'CARD_LEVELS': {'CARD': str(selected_skin), 'LVL': 0, 'TIER': int(0),
                                                                'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                                            r = db.updateVaultNoFilter(query, update_query)
                                        
                                        #Add Destiny
                                        for destiny in d.destiny:
                                            if selected_skin in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                                                db.updateVaultNoFilter(query, {'$addToSet': {'DESTINY': destiny}})
                                                await button_ctx.send(
                                                    f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.", hidden=True)
                                        update_query = {
                                            '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}
                                        }
                                        filter_query = [{'type.' + "UNIVERSE": universe}]
                                        res = db.updateVault(query, update_query, filter_query)
                                        await button_ctx.send(f"Craft Success!")
                                        response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "Craft Success!"}
                                        return response
                                        self.stop = True
                                        

                            await Paginator(bot=self.bot, disableAfterTimeout=True,useQuitButton=True, ctx=player, pages=embed_list, timeout=60, customActionRow=[
                            custom_action_row,
                            custom_function,
                            ]).run()

                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Craft Failed!"}
                            return response
                        
                if item in item_bools:
                    if item == "UNIVERSE_HEART" and universe_heart:
                        response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "You already have the Universe Heart for this universe!"}
                        return response
                    if item == "UNIVERSE_SOUL" and universe_soul:
                        response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "You already have the Universe Soul for this universe!"}
                        return response

                    query = {'DID': str(vault['DID'])}
                    update_query = {
                        '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}, 
                        '$set': {'GEMS.$[type].' + str(item): True}
                    }
                    filter_query = [{'type.' + "UNIVERSE": universe}]
                    res = db.updateVault(query, update_query, filter_query)

                    response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "Success!"}
                    return response
            else:
                    response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": "Insufficent 💎!"}
                    return response
        else:
            response = {"HAS_GEMS_FOR": False, "SUCCESS":  False, "MESSAGE": "You have no 💎 for this Universe."}
            return response

    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))


def price_adjuster(price, selected_universe, completed_tales, completed_dungeons):
    new_price = price
    title_price = 50000
    arm_price = 25000
    c1 = 100000
    c2 = 450000
    c3 = 6000000
    message = ""
    if selected_universe in completed_tales:
        new_price = price - round(price * .25)
        title_price = title_price - round(title_price * .25)
        arm_price = arm_price - round(arm_price * .25)
        c1 = c1 - round(c1 * .25)
        c2 = c2 - round(c2 * .25)
        c3 = c3 - round(c3 * .25)
        message = "**25% Sale**"
    if selected_universe in completed_dungeons:
        new_price = round(price * .50)
        title_price = round(50000 * .50)
        arm_price = round(25000 * .50)
        c1 = round(c1 * .50)
        c2 = round(c2 * .50)
        c3 = round(c3 * .50)
        message = "**50% Sale**"

    response = {'NEW_PRICE': new_price,
    'TITLE_PRICE': title_price,
    'ARM_PRICE': arm_price,
    'C1': c1,
    'C2': c2,
    'C3': c3,
    'MESSAGE': message
    }
    return response



async def menubuild(self, ctx):
    try:
        # await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        card = db.queryCard({'NAME':str(d['CARD'])})
        title = db.queryTitle({'TITLE': str(d['TITLE'])})
        arm = db.queryArm({'ARM': str(d['ARM'])})
        user_info = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        if card:
            try:
                durability = ""
                base_arm_names = ['Reborn Stock', 'Stock', 'Deadgun', 'Glaive', 'Kings Glaive', 'Legendary Weapon']
                for a in vault['ARMS']:
                    if a['ARM'] == str(d['ARM']) and a['ARM'] in base_arm_names:
                        durability = f""
                    elif a['ARM'] == str(d['ARM']) and a['ARM'] not in base_arm_names:
                        durability = f"⚒️ {a['DUR']}"
                
                # Acquire Card Levels data
                card_lvl = 0
                card_tier = 0
                card_exp = 0
                card_lvl_attack_buff = 0
                card_lvl_defense_buff = 0
                card_lvl_ap_buff = 0
                card_lvl_hlt_buff = 0

                for x in vault['CARD_LEVELS']:
                    if x['CARD'] == card['NAME']:
                        card_lvl = x['LVL']
                        card_exp = x['EXP']
                        card_lvl_ap_buff = crown_utilities.level_sync_stats(card_lvl, "AP")
                        card_lvl_attack_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                        card_lvl_defense_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                        card_lvl_hlt_buff = crown_utilities.level_sync_stats(card_lvl, "HLT")

                oarm_universe = arm['UNIVERSE']
                o_title_universe = title['UNIVERSE']
                o_card = card['NAME']
                o_card_path=card['PATH']
                o_max_health = card['HLT'] + card_lvl_hlt_buff
                o_health = card['HLT'] + card_lvl_hlt_buff
                o_stamina = card['STAM']
                o_max_stamina = card['STAM']
                o_moveset = card['MOVESET']
                o_attack = card['ATK'] + card_lvl_attack_buff
                o_defense = card['DEF'] + card_lvl_defense_buff
                o_type = card['TYPE']
                o_passive = card['PASS'][0]
                o_speed = card['SPD']
                o_show = card['UNIVERSE']
                o_collection = card['COLLECTION']
                o_destiny = card['HAS_COLLECTION']
                o_rebirth = d['REBIRTH']
                performance_mode = d['PERFORMANCE']
                card_tier = card['TIER']
                affinity_message = crown_utilities.set_affinities(card)
                talisman = d['TALISMAN']
                talisman_message = "No Talisman Equipped"
                if talisman == "NULL":
                    talisman_message = "No Talisman Equipped"
                else:
                    for t in vault["TALISMANS"]:
                        if t["TYPE"].upper() == talisman.upper():
                            talisman_emoji = crown_utilities.set_emoji(talisman.upper())
                            talisman_durability = t["DUR"]
                    talisman_message = f"{talisman_emoji} {talisman.title()} Talisman Equipped ⚒️ {talisman_durability}"
        
                rebirthBonus = o_rebirth * 10
                traits = ut.traits
                mytrait = {}
                traitmessage = ''
                for trait in traits:
                    if trait['NAME'] == o_show:
                        mytrait = trait
                    if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                        if trait['NAME'] == 'Pokemon':
                            mytrait = trait
                if mytrait:
                    traitmessage = f"{mytrait['EFFECT']}: {mytrait['TRAIT']}"

                pets = vault['PETS']

                active_pet = {}
                pet_names = []

                for pet in pets:
                    pet_names.append(pet['NAME'])
                    if pet['NAME'] == d['PET']:
                        active_pet = pet

                power = list(active_pet.values())[3]
                pet_ability_power = (active_pet['BOND'] * active_pet['LVL']) + power
                bond = active_pet['BOND']
                lvl = active_pet['LVL']

                bond_message = ""
                lvl_message = ""
                if bond == 3:
                    bond_message = "🌟"
                
                if lvl == 10:
                    lvl_message = "⭐"

                # Arm Information
                arm_name = arm['ARM']
                arm_passive = arm['ABILITIES'][0]
                arm_passive_type = list(arm_passive.keys())[0]
                arm_moves_type_list = ['BASIC', 'SPECIAL', 'ULTIMATE']
                if arm_passive_type in arm_moves_type_list:
                    arm_element = arm['ELEMENT']
                arm_passive_value = list(arm_passive.values())[0]
                title_name= title['TITLE']
                title_passive = title['ABILITIES'][0]
                title_passive_type = list(title_passive.keys())[0]
                title_passive_value = list(title_passive.values())[0]

                o_1 = o_moveset[0]
                o_2 = o_moveset[1]
                o_3 = o_moveset[2]
                o_enhancer = o_moveset[3]
                
                # Move 1
                move1 = list(o_1.keys())[0]
                move1ap = list(o_1.values())[0] + card_lvl_ap_buff
                move1_stamina = list(o_1.values())[1]
                move1_element = list(o_1.values())[2]
                move1_emoji = crown_utilities.set_emoji(move1_element)
                if arm_passive_type == 'BASIC':
                    move1 = arm_name
                    move1ap = list(o_1.values())[0] + card_lvl_ap_buff + arm_passive_value
                    move1_stamina = list(o_1.values())[1]
                    move1_element = arm_element
                    move1_emoji = crown_utilities.set_emoji(move1_element)
                # Move 2
                move2 = list(o_2.keys())[0]
                move2ap = list(o_2.values())[0] + card_lvl_ap_buff
                move2_stamina = list(o_2.values())[1]
                move2_element = list(o_2.values())[2]
                move2_emoji = crown_utilities.set_emoji(move2_element)
                if arm_passive_type == 'SPECIAL':
                    move2 = arm_name
                    move2ap = list(o_2.values())[0] + card_lvl_ap_buff + arm_passive_value
                    move2_stamina = list(o_2.values())[1]
                    move2_element = arm_element
                    move2_emoji = crown_utilities.set_emoji(move2_element)


                # Move 3
                move3 = list(o_3.keys())[0]
                move3ap = list(o_3.values())[0] + card_lvl_ap_buff
                move3_stamina = list(o_3.values())[1]
                move3_element = list(o_3.values())[2]
                move3_emoji = crown_utilities.set_emoji(move3_element)
                if arm_passive_type == 'ULTIMATE':
                    move3 = arm_name
                    move3ap = list(o_3.values())[0] + card_lvl_ap_buff + arm_passive_value
                    move3_stamina = list(o_3.values())[1]
                    move3_element = arm_element
                    move3_emoji = crown_utilities.set_emoji(move3_element)


                # Move Enhancer
                move4 = list(o_enhancer.keys())[0]
                move4ap = list(o_enhancer.values())[0]
                move4_stamina = list(o_enhancer.values())[1]
                move4enh = list(o_enhancer.values())[2]


                resolved = False
                focused = False
                att = 0
                defe = 0
                turn = 0

                passive_name = list(o_passive.keys())[0]
                passive_num = list(o_passive.values())[0]
                passive_type = list(o_passive.values())[1]

            
                if passive_type:
                    value_for_passive = card_tier * .5
                    flat_for_passive = round(10 * (card_tier * .5))
                    stam_for_passive = 5 * (card_tier * .5)
                    if passive_type == "HLT":
                        passive_num = value_for_passive
                    if passive_type == "LIFE":
                        passive_num = value_for_passive
                    if passive_type == "ATK":
                        passive_num = value_for_passive
                    if passive_type == "DEF":
                        passive_num = value_for_passive
                    if passive_type == "STAM":
                        passive_num = stam_for_passive
                    if passive_type == "DRAIN":
                        passive_num = stam_for_passive
                    if passive_type == "FLOG":
                        passive_num = value_for_passive
                    if passive_type == "WITHER":
                        passive_num = value_for_passive
                    if passive_type == "RAGE":
                        passive_num = value_for_passive
                    if passive_type == "BRACE":
                        passive_num = value_for_passive
                    if passive_type == "BZRK":
                        passive_num = value_for_passive
                    if passive_type == "CRYSTAL":
                        passive_num = value_for_passive
                    if passive_type == "FEAR":
                        passive_num = flat_for_passive
                    if passive_type == "GROWTH":
                        passive_num = flat_for_passive
                    if passive_type == "CREATION":
                        passive_num = value_for_passive
                    if passive_type == "DESTRUCTION":
                        passive_num = value_for_passive
                    if passive_type == "SLOW":
                        passive_num = "1"
                    if passive_type == "HASTE":
                        passive_num = "1"
                    if passive_type == "STANCE":
                        passive_num = flat_for_passive
                    if passive_type == "CONFUSE":
                        passive_num = flat_for_passive
                    if passive_type == "BLINK":
                        passive_num = stam_for_passive

                atk_buff = ""
                def_buff = ""
                hlt_buff = ""
                message = ""
                if (oarm_universe == o_show) and (o_title_universe == o_show):
                    o_attack = o_attack + 20
                    o_defense = o_defense + 20
                    o_health = o_health + 100
                    o_max_health = o_max_health + 100
                    message = "_Universe Buff Applied_"
                    if o_destiny:
                        o_attack = o_attack + 25
                        o_defense = o_defense + 25
                        o_health = o_health + 150
                        o_max_health = o_max_health + 150
                        message = "_Destiny Buff Applied_"

                #Title errors 
                titled =False
                titleicon="⚠️"
                licon = "🔰"
                armicon = "⚠️"
                if card_lvl >= 200:
                    licon ="🔱"
                if card_lvl >= 700:
                    licon ="⚜️"
                if card_lvl >=999:
                    licon ="🏅"
                titlemessage = f"{titleicon} {title_name} ~ INEFFECTIVE"
                armmessage = f"🦾 ⚠️ {arm_name}: {durability}"
                if arm_passive_type in arm_moves_type_list:
                    arm_emoji = crown_utilities.set_emoji(arm_element)
                    if performance_mode:
                        armmessage = f'☢️ {arm_name}: {arm_emoji} {arm_passive_type.title()} Attack: {arm_passive_value} | {durability}'
                    else:
                        armmessage = f'☢️ {arm_name}'
                warningmessage = f"Use {o_show} or Unbound Titles on this card"
                if o_title_universe == "Unbound" or o_show == "Crown Rift Awakening":
                    titled =True
                    titleicon = "👑"
                    if performance_mode:
                        titlemessage = f"👑 {title_name}: {title_passive_type} {title_passive_value}{title_enhancer_suffix_mapping[title_passive_type]}"
                    else:
                        titlemessage = f"👑 {title_name}" 
                    warningmessage= f""
                elif o_title_universe == o_show:
                    titled =True
                    titleicon = "🎗️"
                    if performance_mode:
                        titlemessage = f"🎗️ {title_name}: {title_passive_type} {title_passive_value}{title_enhancer_suffix_mapping[title_passive_type]}"
                    else:
                        titlemessage = f"🎗️ {title_name}"
                    warningmessage= f""
                
                if oarm_universe == "Unbound" or o_show == "Crown Rift Slayers":
                    armicon = "💪"
                    if performance_mode:
                        armmessage = f'💪 {arm_name}: {arm_passive_type} {arm_passive_value}{enhancer_suffix_mapping[arm_passive_type]} {durability}'
                    else:
                        armmessage = f'💪 {arm_name}'

                elif oarm_universe == o_show:
                    armicon = "🦾"
                    if performance_mode:
                        armmessage = f'🦾 {arm_name}: {arm_passive_type} {arm_passive_value}{enhancer_suffix_mapping[arm_passive_type]} {durability}'
                    else:
                        armmessage = f'🦾 {arm_name}: {durability}'
                    

                cardtitle = {'TITLE': title_name}
                

                #<:PCG:769471288083218432>
                if performance_mode:
                    embedVar = discord.Embed(title=f"{licon}{card_lvl} {o_card}".format(self), description=textwrap.dedent(f"""\
                    :mahjong: **{card_tier}**
                    ❤️ **{o_max_health}**
                    🗡️ **{o_attack}**
                    🛡️ **{o_defense}**
                    🏃 **{o_speed}**

                    **{talisman_message}**

                    **{titlemessage}**
                    **{armmessage}**
                    🧬 **{active_pet['NAME']}:** {active_pet['TYPE']}: {pet_ability_power}{enhancer_suffix_mapping[active_pet['TYPE']]}
                    🧬 Bond {bond} {bond_message} & Level {lvl} {lvl_message}

                    🩸 **{passive_name}:** {passive_type} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}                
                    
                    {move1_emoji} **{move1}:** {move1ap}
                    {move2_emoji} **{move2}:** {move2ap}
                    {move3_emoji} **{move3}:** {move3ap}
                    🦠 **{move4}:** {move4enh} {move4ap}{enhancer_suffix_mapping[move4enh]}

                    ♾️ {traitmessage}
                    """),colour=000000)
                    embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                    embedVar.set_image(url="attachment://image.png")
                    if card_lvl != 999:
                        embedVar.set_footer(text=f"EXP Until Next Level: {150 - card_exp}\nRebirth Buff: +{rebirthBonus}\n{warningmessage}")
                    else:
                        embedVar.set_footer(text=f"Max Level\nRebirth Buff: +{rebirthBonus}\n{warningmessage}")
                    embedVar.set_author(name=f"{ctx.author}", icon_url=user_info['AVATAR'])
                    
                    await ctx.send(embed=embedVar)
                
                else:
                    card_file = showcard("non-battle", card, arm, o_max_health, o_health, o_max_stamina, o_stamina, resolved, title, focused, o_attack, o_defense, turn, move1ap, move2ap, move3ap, move4ap, move4enh, card_lvl, None)

                    embedVar = discord.Embed(title=f"".format(self), colour=000000)
                    embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                    embedVar.set_image(url="attachment://image.png")
                    embedVar.set_author(name=textwrap.dedent(f"""\
                    🧬 {active_pet['NAME']}: {active_pet['TYPE'].title()}: {pet_ability_power}{enhancer_suffix_mapping[active_pet['TYPE']]} 
                    🧬 Bond {bond} {bond_message} & Level {lvl} {lvl_message}
                    {titlemessage}
                    {armmessage}
                    {talisman_message}

                    🩸 {passive_name}      
                    🏃 {o_speed}
                    """))
                    embedVar.set_thumbnail(url=ctx.author.avatar_url)
                    if card_lvl != 999:
                        embedVar.set_footer(text=f"EXP Until Next Level: {150 - card_exp}\nRebirth Buff: +{rebirthBonus}\n♾️ {traitmessage}\n{warningmessage}")
                    else:
                        embedVar.set_footer(text=f"Max Level")
                    
                    await ctx.send(file=card_file, embed=embedVar)
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("There's an issue with your build. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                return
        else:
            await ctx.send(m.USER_NOT_REGISTERED, hidden=True)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'player': str(player),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))


async def menuessence(self, ctx: SlashContext):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    vault = db.queryVault({'DID': str(ctx.author.id)})
    current_essence = vault['ESSENCE']
    if current_essence:
        # number_of_gems_universes = len(current_essence)

        essence_details = []
        for ed in current_essence:
            element = ed["ELEMENT"]
            essence = ed["ESSENCE"]
            element_emoji = crown_utilities.set_emoji(element)
            essence_details.append(
                f"{element_emoji} **{element.title()} Essence: ** {essence}\n")

        # Adding to array until divisible by 10
        while len(essence_details) % 10 != 0:
            essence_details.append("")
        # Check if divisible by 10, then start to split evenly

        if len(essence_details) % 10 == 0:
            first_digit = int(str(len(essence_details))[:1])
            if len(essence_details) >= 89:
                if first_digit == 1:
                    first_digit = 10
            essence_broken_up = np.array_split(essence_details, first_digit)

        # If it's not an array greater than 10, show paginationless embed
        if len(essence_details) < 10:
            embedVar = discord.Embed(title=f"🪔 Essence", description="\n".join(essence_details),
                                    colour=0x7289da)
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(essence_broken_up)):
            globals()['embedVar%s' % i] = discord.Embed(title=f"🪔 Essence",
                                                        description="\n".join(essence_broken_up[i]), colour=0x7289da)
            embed_list.append(globals()['embedVar%s' % i])

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⬅️', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('➡️', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = embed_list
        await paginator.run(embeds)
    else:
        await ctx.send("You currently own no 💎.")


async def menucards(self, ctx):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return
    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)#Storage Update
    storage_type = d['STORAGE_TYPE']
    vault = db.queryVault({'DID': d['DID']})
    try: 
        if vault:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            card_levels = vault['CARD_LEVELS']
            current_gems = []
            for gems in vault['GEMS']:
                current_gems.append(gems['UNIVERSE'])
            balance = vault['BALANCE']
            cards_list = vault['CARDS']
            total_cards = len(cards_list)
            current_card = d['CARD']
            storage = vault['STORAGE']
            cards=[]
            icon = ":coin:"
            if balance >= 150000:
                icon = ":money_with_wings:"
            elif balance >=100000:
                icon = ":moneybag:"
            elif balance >= 50000:
                icon = ":dollar:"
            
            embed_list = []

            for card in cards_list:
                index = cards_list.index(card)
                resp = db.queryCard({"NAME": str(card)})
                card_tier = 0
                lvl = ""
                tier = ""
                speed = 0
                card_tier = f":mahjong: {resp['TIER']}"
                card_available = resp['AVAILABLE']
                card_exclusive = resp['EXCLUSIVE']
                card_collection = resp['HAS_COLLECTION']
                show_img = db.queryUniverse({'TITLE': resp['UNIVERSE']})['PATH']
                affinity_message = crown_utilities.set_affinities(resp)
                o_show = resp['UNIVERSE']
                icon = ":flower_playing_cards:"
                if card_available and card_exclusive:
                    icon = ":fire:"
                elif card_available == False and card_exclusive ==False:
                    if card_collection:
                        icon =":sparkles:"
                    else:
                        icon = ":japanese_ogre:"
                card_lvl = 0
                card_exp = 0
                card_lvl_attack_buff = 0
                card_lvl_defense_buff = 0
                card_lvl_ap_buff = 0
                card_lvl_hlt_buff = 0

                for cl in card_levels:
                    if card == cl['CARD']:
                        licon = "🔰"
                        if cl['LVL'] >= 200:
                            licon ="🔱"
                        if cl['LVL'] >= 700:
                            licon ="⚜️"
                        if cl['LVL'] >= 999:
                            licon = "🏅"
                        
                        lvl = f"{licon} **{cl['LVL']}**"
                        card_lvl = cl['LVL']
                        card_exp = cl['EXP']
                        card_lvl_ap_buff = crown_utilities.level_sync_stats(card_lvl, "AP")
                        card_lvl_attack_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                        card_lvl_defense_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                        card_lvl_hlt_buff = crown_utilities.level_sync_stats(card_lvl, "HLT")
                        
                
                o_passive = resp['PASS'][0] 
                o_moveset = resp['MOVESET']
                o_1 = o_moveset[0]
                o_2 = o_moveset[1]
                o_3 = o_moveset[2]
                o_enhancer = o_moveset[3]
                
                # Move 1
                move1 = list(o_1.keys())[0]
                move1ap = list(o_1.values())[0] + card_lvl_ap_buff
                move1_stamina = list(o_1.values())[1]
                move1_element = list(o_1.values())[2]
                move1_emoji = crown_utilities.set_emoji(move1_element)
                
                # Move 2
                move2 = list(o_2.keys())[0]
                move2ap = list(o_2.values())[0] + card_lvl_ap_buff
                move2_stamina = list(o_2.values())[1]
                move2_element = list(o_2.values())[2]
                move2_emoji = crown_utilities.set_emoji(move2_element)


                # Move 3
                move3 = list(o_3.keys())[0]
                move3ap = list(o_3.values())[0] + card_lvl_ap_buff
                move3_stamina = list(o_3.values())[1]
                move3_element = list(o_3.values())[2]
                move3_emoji = crown_utilities.set_emoji(move3_element)


                # Move Enhancer
                move4 = list(o_enhancer.keys())[0]
                move4ap = list(o_enhancer.values())[0]
                move4_stamina = list(o_enhancer.values())[1]
                move4enh = list(o_enhancer.values())[2]

                passive_name = list(o_passive.keys())[0]
                passive_num = list(o_passive.values())[0]
                passive_type = list(o_passive.values())[1]
            
                if passive_type:
                    value_for_passive = resp['TIER'] * .5
                    flat_for_passive = round(10 * (resp['TIER'] * .5))
                    stam_for_passive = 5 * (resp['TIER'] * .5)
                    if passive_type == "HLT":
                        passive_num = value_for_passive
                    if passive_type == "LIFE":
                        passive_num = value_for_passive
                    if passive_type == "ATK":
                        passive_num = value_for_passive
                    if passive_type == "DEF":
                        passive_num = value_for_passive
                    if passive_type == "STAM":
                        passive_num = stam_for_passive
                    if passive_type == "DRAIN":
                        passive_num = stam_for_passive
                    if passive_type == "FLOG":
                        passive_num = value_for_passive
                    if passive_type == "WITHER":
                        passive_num = value_for_passive
                    if passive_type == "RAGE":
                        passive_num = value_for_passive
                    if passive_type == "BRACE":
                        passive_num = value_for_passive
                    if passive_type == "BZRK":
                        passive_num = value_for_passive
                    if passive_type == "CRYSTAL":
                        passive_num = value_for_passive
                    if passive_type == "FEAR":
                        passive_num = flat_for_passive
                    if passive_type == "GROWTH":
                        passive_num = flat_for_passive
                    if passive_type == "CREATION":
                        passive_num = value_for_passive
                    if passive_type == "DESTRUCTION":
                        passive_num = value_for_passive
                    if passive_type == "SLOW":
                        passive_num = "1"
                    if passive_type == "HASTE":
                        passive_num = "1"
                    if passive_type == "STANCE":
                        passive_num = flat_for_passive
                    if passive_type == "CONFUSE":
                        passive_num = flat_for_passive
                    if passive_type == "BLINK":
                        passive_num = stam_for_passive

                traits = ut.traits
                mytrait = {}
                traitmessage = ''
                for trait in traits:
                    if trait['NAME'] == o_show:
                        mytrait = trait
                    if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                        if trait['NAME'] == 'Pokemon':
                            mytrait = trait
                if mytrait:
                    traitmessage = f"**{mytrait['EFFECT']}:** {mytrait['TRAIT']}"


                embedVar = discord.Embed(title= f"{resp['NAME']}", description=textwrap.dedent(f"""\
                {icon} **[{index}]** 
                {card_tier}: {lvl}
                :heart: **{resp['HLT']}** :dagger: **{resp['ATK']}** :shield: **{resp['DEF']}** 🏃 **{resp['SPD']}**

                {move1_emoji} **{move1}:** {move1ap}
                {move2_emoji} **{move2}:** {move2ap}
                {move3_emoji} **{move3}:** {move3ap}
                🦠 **{move4}:** {move4enh} {move4ap}{enhancer_suffix_mapping[move4enh]}

                🩸 **{passive_name}:** {passive_type.title()} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}
                ♾️ {traitmessage}
                """), colour=0x7289da)
                embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                embedVar.set_thumbnail(url=show_img)
                embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                embed_list.append(embedVar)

            buttons = [
                manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                manage_components.create_button(style=1, label="Resell/Dismantle", custom_id="Econ"),
                manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                manage_components.create_button(style=2, label="Swap/Store", custom_id="Storage")
            ]
            custom_action_row = manage_components.create_actionrow(*buttons)
            # custom_button = manage_components.create_button(style=3, label="Equip")

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    updated_vault = db.queryVault({'DID': d['DID']})
                    sell_price = 0
                    selected_card = str(button_ctx.origin_message.embeds[0].title)
                    if button_ctx.custom_id == "Equip":
                        if selected_card in updated_vault['CARDS']:
                            selected_universe = custom_function
                            custom_function.selected_universe = selected_card
                            user_query = {'DID': str(ctx.author.id)}
                            response = db.updateUserNoFilter(user_query, {'$set': {'CARD': selected_card}})
                            await button_ctx.send(f":flower_playing_cards: **{selected_card}** equipped.")
                            self.stop = True
                        else:
                            await button_ctx.send(f"**{selected_card}** is no longer in your vault.")
                    
                    elif button_ctx.custom_id == "Econ":
                        await button_ctx.defer(ignore=True)
                        econ_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Resell",
                                        custom_id="resell"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.red,
                                        label="Dismantle",
                                        custom_id="dismantle"
                                    )
                                ]
                        econ_buttons_action_row = manage_components.create_actionrow(*econ_buttons)
                        msg = await ctx.send(f"Would you like to Resell or Dismantle", components=[econ_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[econ_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "resell":
                                await button_ctx.defer(ignore=True)
                                card_data = db.queryCard({'NAME': selected_card})
                                card_name = card_data['NAME']
                                sell_price = sell_price + (card_data['PRICE'] * .15)
                                if card_name == current_card:
                                    await button_ctx.send("You cannot resell equipped cards.")
                                elif card_name in updated_vault['CARDS']:
                                    sell_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Yes",
                                            custom_id="yes"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.blue,
                                            label="No",
                                            custom_id="no"
                                        )
                                    ]
                                    sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                                    msg = await button_ctx.send(f"Are you sure you want to sell **{card_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                                    
                                    def check(button_ctx):
                                        return button_ctx.author == ctx.author

                                    
                                    try:
                                        button_ctx: ComponentContextSell = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                                        if button_ctx.custom_id == "no":
                                            await button_ctx.send("Sell cancelled. ")
                                        if button_ctx.custom_id == "yes":
                                            db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARDS': card_name}})
                                            db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
                                            await crown_utilities.bless(sell_price, ctx.author.id)
                                            await msg.delete()
                                            await button_ctx.send(f"**{card_name}** has been sold.")
                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'PLAYER': str(ctx.author),
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        await ctx.send("There's an issue with selling one or all of your items.")
                                        return
                                else:
                                    await button_ctx.send(f"**{card_name}** is no longer in your vault.")
                            if button_ctx.custom_id == "dismantle":
                                await button_ctx.defer(ignore=True)
                                card_data = db.queryCard({'NAME': selected_card})
                                card_tier =  card_data['TIER']
                                card_health = card_data['HLT']
                                card_name = card_data['NAME']
                                selected_universe = card_data['UNIVERSE']
                                o_moveset = card_data['MOVESET']
                                o_3 = o_moveset[2]
                                element = list(o_3.values())[2]
                                essence_amount = (200 * card_tier)
                                o_enhancer = o_moveset[3]

                                dismantle_amount = (10000 * card_tier) + card_health
                                if card_name == current_card:
                                    await button_ctx.send("You cannot dismantle equipped cards.")
                                elif card_name in updated_vault['CARDS']:
                                    dismantle_buttons = [
                                        manage_components.create_button(
                                            style=ButtonStyle.green,
                                            label="Yes",
                                            custom_id="yes"
                                        ),
                                        manage_components.create_button(
                                            style=ButtonStyle.blue,
                                            label="No",
                                            custom_id="no"
                                        )
                                    ]
                                    dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                                    msg = await button_ctx.send(f"Are you sure you want to dismantle **{card_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                                    
                                    def check(button_ctx):
                                        return button_ctx.author == ctx.author

                                    
                                    try:
                                        button_ctx: ComponentContextDismantle = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                        if button_ctx.custom_id == "no":
                                            await button_ctx.send("Dismantle cancelled. ")
                                        if button_ctx.custom_id == "yes":
                                            if selected_universe in current_gems:
                                                query = {'DID': str(ctx.author.id)}
                                                update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                                filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                                response = db.updateVault(query, update_query, filter_query)
                                            else:
                                                response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                            em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                            db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARDS': card_name}})
                                            db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
                                            #await crown_utilities.bless(sell_price, ctx.author.id)
                                            await msg.delete()
                                            await button_ctx.send(f"**{card_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}. Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence.")
                                            
                                    except Exception as ex:
                                        trace = []
                                        tb = ex.__traceback__
                                        while tb is not None:
                                            trace.append({
                                                "filename": tb.tb_frame.f_code.co_filename,
                                                "name": tb.tb_frame.f_code.co_name,
                                                "lineno": tb.tb_lineno
                                            })
                                            tb = tb.tb_next
                                        print(str({
                                            'PLAYER': str(ctx.author),
                                            'type': type(ex).__name__,
                                            'message': str(ex),
                                            'trace': trace
                                        }))
                                        await ctx.send("There's an issue with selling one or all of your items.")
                                        return
                                else:
                                    await button_ctx.send(f"**{card_name}** is no longer in your vault.")
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                    
                    elif button_ctx.custom_id == "Trade":
                        
                        card_data = db.queryCard({'NAME' : selected_card})
                        card_name= card_data['NAME']
                        sell_price = card_data['PRICE'] * .10
                        mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                        mvalidation=False
                        bvalidation=False
                        item_already_in_trade=False
                        if card_name == current_card:
                            await button_ctx.send("You cannot trade equipped cards.")
                        else:
                            if mtrade:
                                if selected_card in mtrade['MCARDS']:
                                    await ctx.send(f"{ctx.author.mention} card already in **Trade**")
                                    item_already_in_trade=True
                                mvalidation=True
                            else:
                                btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                                if btrade:
                                    if selected_card in btrade['BCARDS']:
                                        await ctx.send(f"{ctx.author.mention} card already in **Trade**")
                                        item_already_in_trade=True
                                    bvalidation=True
                                else:
                                    await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                    return
                            if item_already_in_trade:
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Would you like to remove **{selected_card}** from the **Trade**?", components=[trade_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Happy Trading")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        neg_sell_price = 0 - abs(int(sell_price))
                                        if mvalidation:
                                            trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$pull" : {'MCARDS': selected_card}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                            update_query = {"$pull" : {'BCARDS': selected_card}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Returned.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                            elif mvalidation == True or bvalidation ==True:    #If user is valid
                                sell_price = card_data['PRICE'] * .10
                                trade_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.blue,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                                await button_ctx.send(f"Are you sure you want to trade **{selected_card}**", components=[trade_buttons_action_row])
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                    if button_ctx.custom_id == "no":
                                            await button_ctx.send("Not this time. ")
                                            self.stop = True
                                    if button_ctx.custom_id == "yes":
                                        if mvalidation:
                                            trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                            update_query = {"$push" : {'MCARDS': selected_card}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Trade staged.")
                                            self.stop = True
                                        elif bvalidation:
                                            trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                            update_query = {"$push" : {'BCARDS': selected_card}, "$inc" : {'TAX' : int(sell_price)}}
                                            resp = db.updateTrade(trade_query, update_query)
                                            await button_ctx.send("Trade staged.")
                                            self.stop = True
                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'PLAYER': str(ctx.author),
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with trading one or all of your items.")
                                    return   
                        
                    elif button_ctx.custom_id == "Storage":
                        await button_ctx.defer(ignore=True)
                        storage_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Swap Storage Card",
                                        custom_id="swap"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.red,
                                        label="Add to Storage",
                                        custom_id="store"
                                    )
                                ]
                        storage_buttons_action_row = manage_components.create_actionrow(*storage_buttons)
                        msg = await ctx.send(f"Would you like to Swap Cards or Add Card to Storage", components=[storage_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContextStorage = await manage_components.wait_for_component(self.bot, components=[storage_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "swap":
                                await button_ctx.defer(ignore=True)
                                await msg.delete()
                                await ctx.send(f"{ctx.author.mention}, Which card number would you like to swap with in storage?\n*Discord has changed their policy on message intents..while we troubleshoot this issue please use this command in DMS.\nIt will not work in server...*")
                                def check(msg):
                                    return msg.author == ctx.author

                                try:
                                    msg = await self.bot.wait_for('message', check=check, timeout=30)
                                    author = msg.author
                                    content = msg.content
                                    # print("Author: " + str(author))
                                    # print("Content: " + str(content))
                                    if storage[int(msg.content)]:
                                        swap_with = storage[int(msg.content)]
                                        query = {'DID': str(msg.author.id)}
                                        update_storage_query = {
                                            '$pull': {'CARDS': selected_card},
                                            '$addToSet': {'STORAGE': selected_card},
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)

                                        update_storage_query = {
                                            '$pull': {'STORAGE': swap_with},
                                            '$addToSet': {'CARDS': swap_with}
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)

                                        await msg.delete()
                                        await ctx.send(f"**{selected_card}** has been swapped with **{swap_with}**")
                                        return
                                    else:
                                        await ctx.send("The card number you want to swap with does not exist.")
                                        return

                                except Exception as e:
                                    return False
                            if button_ctx.custom_id == "store":
                                await button_ctx.defer(ignore=True)
                                
                                try:
                                    author = msg.author
                                    content = msg.content
                                    # print("Author: " + str(author))
                                    # print("Content: " + str(content))
                                    if len(storage) <= (storage_type * 15):
                                        query = {'DID': str(ctx.author.id)}
                                        update_storage_query = {
                                            '$pull': {'CARDS': selected_card},
                                            '$addToSet': {'STORAGE': selected_card},
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)
                                        
                                        await msg.delete()
                                        await ctx.send(f"**{selected_card}** has been added to storage")
                                        return
                                    else:
                                        await ctx.send("Not enough space in storage")
                                        return

                                except Exception as e:
                                    return False
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                        
                        self.stop = True
                else:
                    await ctx.send("This is not your card list.")
            await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await ctx.send("There's an issue with loading your cards. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
        return
    
async def menustorage(self, ctx):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    try:
        user = db.queryUser({'DID': str(ctx.author.id)})
        vault = db.queryVault({'DID': str(ctx.author.id)})
        storage_allowed_amount = user['STORAGE_TYPE'] * 15
        if not vault['STORAGE']:
            await ctx.send("Your storage is empty.", hidden=True)
            return

        list_of_cards = db.querySpecificCards(vault['STORAGE'])
        cards = [x for x in list_of_cards]
        dungeon_card_details = []
        tales_card_details = []
        destiny_card_details = []
        
        for card in cards:
            index = vault['STORAGE'].index(card['NAME'])
            level = ""
            level_icon = "🔰"
            for c in vault['CARD_LEVELS']:
                if card['NAME'] == c['CARD']:
                    level = str(c['LVL'])
                    card_lvl = int(c['LVL'])
            if card_lvl >= 200:
                level_icon = "🔱"
            if card_lvl >= 700:
                level_icon ="⚜️"
            if card_lvl >=999:
                level_icon ="🏅"
            available = ""
            if card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
                dungeon_card_details.append(
                    f"[{str(index)}] :mahjong: {card['TIER']} **{card['NAME']}**\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
            elif not card['HAS_COLLECTION']:
                tales_card_details.append(
                    f"[{str(index)}] :mahjong: {card['TIER']} **{card['NAME']}**\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")
            elif card['HAS_COLLECTION']:
                destiny_card_details.append(
                    f"[{str(index)}] :mahjong: {card['TIER']} **{card['NAME']}**\n**{level_icon}**: {str(level)} :heart: {card['HLT']} :dagger: {card['ATK']}  🛡️ {card['DEF']}\n")

        all_cards = []
        if tales_card_details:
            for t in tales_card_details:
                all_cards.append(t)

        if dungeon_card_details:
            for d in dungeon_card_details:
                all_cards.append(d)

        if destiny_card_details:
            for de in destiny_card_details:
                all_cards.append(de)

        total_cards = len(all_cards)

        # Adding to array until divisible by 10
        while len(all_cards) % 10 != 0:
            all_cards.append("")
        # Check if divisible by 10, then start to split evenly

        if len(all_cards) % 10 == 0:
            first_digit = int(str(len(all_cards))[:1])
            if len(all_cards) >= 89:
                if first_digit == 1:
                    first_digit = 10
            # first_digit = 10
            cards_broken_up = np.array_split(all_cards, first_digit)

        # If it's not an array greater than 10, show paginationless embed
        if len(all_cards) < 10:
            embedVar = discord.Embed(title=f"💼 {user['DISNAME']}'s Storage", description="\n".join(all_cards), colour=0x7289da)
            embedVar.set_footer(
                text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(vault['STORAGE']))} Storage Available")
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(cards_broken_up)):
            globals()['embedVar%s' % i] = discord.Embed(
                title=f"💼 {user['DISNAME']}'s Storage",
                description="\n".join(cards_broken_up[i]), colour=0x7289da)
            globals()['embedVar%s' % i].set_footer(
                text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(vault['STORAGE']))} Storage Available")
            embed_list.append(globals()['embedVar%s' % i])

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⬅️', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('➡️', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = embed_list
        await paginator.run(embeds)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'player': str(ctx.author),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))

async def menutitles(self, ctx):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return
    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    vault = db.queryVault({'DID': d['DID']})
    storage_type = d['STORAGE_TYPE']
    if vault:
        try:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            balance = vault['BALANCE']
            current_title = d['TITLE']
            titles_list = vault['TITLES']
            total_titles = len(titles_list)
            storage = vault['TSTORAGE']
            titles=[]
            current_gems = []
            for gems in vault['GEMS']:
                current_gems.append(gems['UNIVERSE'])
            icon = ":coin:"
            if balance >= 150000:
                icon = ":money_with_wings:"
            elif balance >=100000:
                icon = ":moneybag:"
            elif balance >= 50000:
                icon = ":dollar:"


            embed_list = []
            for title in titles_list:
                index = titles_list.index(title)
                resp = db.queryTitle({"TITLE": str(title)})
                title_passive = resp['ABILITIES'][0]
                title_passive_type = list(title_passive.keys())[0]
                title_passive_value = list(title_passive.values())[0]
                title_available = resp['AVAILABLE']
                title_exclusive = resp['EXCLUSIVE']
                icon = "🎗️"
                if resp['UNIVERSE'] == "Unbound":
                    icon = ":crown:"
                elif title_available and title_exclusive:
                    icon = ":fire:"
                elif title_available == False and title_exclusive ==False:
                    icon = ":japanese_ogre:"
                
                
                embedVar = discord.Embed(title= f"{resp['TITLE']}", description=textwrap.dedent(f"""
                {icon} **[{index}]**
                🦠 **{title_passive_type}:** {title_passive_value}
                :earth_africa: **Universe:** {resp['UNIVERSE']}"""), 
                colour=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                embedVar.set_footer(text=f"{title_passive_type}: {title_enhancer_mapping[title_passive_type]}")
                embed_list.append(embedVar)
            
            buttons = [
                manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                manage_components.create_button(style=1, label="Resell", custom_id="Resell"),
                manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                manage_components.create_button(style=2, label="Swap/Store", custom_id="Storage")
            ]
            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    updated_vault = db.queryVault({'DID': d['DID']})
                    sell_price = 0
                    selected_title = str(button_ctx.origin_message.embeds[0].title)
                    if button_ctx.custom_id == "Equip":
                        if selected_title in updated_vault['TITLES']:
                            selected_universe = custom_function
                            custom_function.selected_universe = selected_title
                            user_query = {'DID': str(ctx.author.id)}
                            response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': selected_title}})
                            await button_ctx.send(f"🎗️ **{selected_title}** equipped.")
                            self.stop = True
                        else:
                            await button_ctx.send(f"**{selected_title}** is no longer in your vault.")                           
                    
                    elif button_ctx.custom_id == "Resell":
                        title_data = db.queryTitle({'TITLE': selected_title})
                        title_name = title_data['TITLE']
                        sell_price = sell_price + (title_data['PRICE'] * .10)
                        if title_name == current_title:
                            await button_ctx.send("You cannot resell equipped titles.")
                        elif title_name in updated_vault['TITLES']:
                            sell_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to sell **{title_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Sell cancelled. Please press the Exit button if you are done reselling titles.")
                                if button_ctx.custom_id == "yes":
                                    db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TITLES': title_name}})
                                    await crown_utilities.bless(sell_price, ctx.author.id)
                                    await msg.delete()
                                    await button_ctx.send(f"**{title_name}** has been sold.")
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with selling one or all of your items.")
                                return
                        else:
                            await button_ctx.send(f"**{title_name}** is no longer in your vault.")
                    
                    elif button_ctx.custom_id == "Dismantle":
                        title_data = db.queryTitle({'TITLE': selected_title})
                        title_name = title_data['TITLE']
                        selected_universe = title_data['UNIVERSE']
                        dismantle_amount = 1000
                        if title_name == current_title:
                            await button_ctx.send("You cannot resell equipped titles.")
                        elif title_name in updated_vault['TITLES']:
                            dismantle_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to dismantle **{title_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Dismantle cancelled. ")
                                if button_ctx.custom_id == "yes":
                                    if selected_universe in current_gems:
                                        query = {'DID': str(ctx.author.id)}
                                        update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                        filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                        response = db.updateVault(query, update_query, filter_query)
                                    else:
                                        response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                    db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TITLES': title_name}})
                                    await crown_utilities.bless(sell_price, ctx.author.id)
                                    await msg.delete()
                                    await button_ctx.send(f"**{title_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.")
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with selling one or all of your items.")
                                return
                        else:
                            await button_ctx.send(f"**{title_name}** is no longer in your vault.")

                    elif button_ctx.custom_id == "Trade":
                        title_data = db.queryTitle({'TITLE' : selected_title})
                        title_name = title_data['TITLE']
                        if title_name == current_title:
                            await button_ctx.send("You cannot trade equipped titles.")
                            return
                        sell = title_data['PRICE'] * .10
                        mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                        mvalidation=False
                        bvalidation=False
                        item_already_in_trade=False
                        if mtrade:
                            if selected_title in mtrade['MTITLES']:
                                await ctx.send(f"{ctx.author.mention} title already in **Trade**")
                                item_already_in_trade=True
                            mvalidation=True
                        else:
                            btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                            if btrade:
                                if selected_title in btrade['BTITLES']:
                                    await ctx.send(f"{ctx.author.mention} title already in **Trade**")
                                    item_already_in_trade=True
                                bvalidation=True
                            else:
                                await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                return
                        if item_already_in_trade:
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"Woudl you like to remove **{selected_title}** from the **Trade**?", components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Happy Trading")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    neg_sell_price = 0 - abs(int(sell_price))
                                    if mvalidation:
                                        trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$pull" : {'MTITLES': selected_title}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                        update_query = {"$pull" : {'BTITLES': selected_title}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with trading one or all of your items.")
                                return   
                        elif mvalidation == True or bvalidation ==True:    #If user is valid
                            sell_price = title_data['PRICE'] * .10
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"Are you sure you want to trade **{selected_title}**", components=[trade_buttons_action_row])
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Not this time. ")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    if mvalidation:
                                        trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$push" : {'MTITLES': selected_title}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                        update_query = {"$push" : {'BTITLES': selected_title}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with trading one or all of your items.")
                                return   
                                                    
                    elif button_ctx.custom_id == "Storage":
                        await button_ctx.defer(ignore=True)
                        storage_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Swap Storage Title",
                                        custom_id="swap"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.red,
                                        label="Add to Storage",
                                        custom_id="store"
                                    )
                                ]
                        storage_buttons_action_row = manage_components.create_actionrow(*storage_buttons)
                        msg = await ctx.send(f"Would you like to Swap Titles or Add Title to Storage", components=[storage_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContextStorage = await manage_components.wait_for_component(self.bot, components=[storage_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "swap":
                                await button_ctx.defer(ignore=True)
                                await msg.delete()
                                await ctx.send(f"{ctx.author.mention}, Which title number would you like to swap with in storage?")
                                def check(msg):
                                    return msg.author == ctx.author

                                try:
                                    msg = await self.bot.wait_for('message', check=check, timeout=30)
                                    author = msg.author
                                    content = msg.content
                                    # print("Author: " + str(author))
                                    # print("Content: " + str(content))
                                    # print(msg)
                                    if storage[int(msg.content)]:
                                        swap_with = storage[int(msg.content)]
                                        query = {'DID': str(msg.author.id)}
                                        update_storage_query = {
                                            '$pull': {'TITLES': selected_title},
                                            '$addToSet': {'TSTORAGE': selected_title},
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)

                                        update_storage_query = {
                                            '$pull': {'TSTORAGE': swap_with},
                                            '$addToSet': {'TCARDS': swap_with}
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)

                                        await msg.delete()
                                        await ctx.send(f"**{selected_card}** has been swapped with **{swap_with}**")
                                        return
                                    else:
                                        await ctx.send("The card number you want to swap with does not exist.")
                                        return

                                except Exception as e:
                                    return False
                            if button_ctx.custom_id == "store":
                                await button_ctx.defer(ignore=True)
                                
                                try:
                                    author = msg.author
                                    content = msg.content
                                    # print("Author: " + str(author))
                                    # print("Content: " + str(content))
                                    if len(storage) <= (storage_type * 15):
                                        query = {'DID': str(ctx.author.id)}
                                        update_storage_query = {
                                            '$pull': {'TITLES': selected_title},
                                            '$addToSet': {'TSTORAGE': selected_title},
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)
                                        
                                        await msg.delete()
                                        await ctx.send(f"**{selected_title}** has been added to storage")
                                        return
                                    else:
                                        await ctx.send("Not enough space in storage")
                                        return

                                except Exception as e:
                                    return False
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                        
                        self.stop = True
                else:
                    await ctx.send("This is not your Title list.")


            await Paginator(bot=self.bot, ctx=ctx,useQuitButton=True, disableAfterTimeout=True,pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()
    
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("There's an issue with your Titles list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

async def menuarms(self, ctx):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    vault = db.queryVault({'DID': d['DID']})
    
    storage_type = d['STORAGE_TYPE']
    if vault:
        try:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            current_arm = d['ARM']
            balance = vault['BALANCE']
            arms_list = vault['ARMS']
            total_arms = len(arms_list)
            storage = vault['ASTORAGE']
            arms=[]
            current_gems = []
            for gems in vault['GEMS']:
                current_gems.append(gems['UNIVERSE'])

            icon = ":coin:"
            if balance >= 150000:
                icon = ":money_with_wings:"
            elif balance >=100000:
                icon = ":moneybag:"
            elif balance >= 50000:
                icon = ":dollar:"

            embed_list = []
            for arm in arms_list:
                index = arms_list.index(arm)
                resp = db.queryArm({"ARM": str(arm['ARM'])})
                element = resp['ELEMENT']
                arm_passive = resp['ABILITIES'][0]
                arm_passive_type = list(arm_passive.keys())[0]
                arm_passive_value = list(arm_passive.values())[0]
                arm_available = resp['AVAILABLE']
                arm_exclusive = resp['EXCLUSIVE']
                icon = "🦾"
                if arm_available and arm_exclusive:
                    icon = ":fire:"
                elif arm_available == False and arm_exclusive ==False:
                    icon = ":japanese_ogre:"
                element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
                if element and arm_passive_type in element_available:
                    element_name = element
                    element = crown_utilities.set_emoji(element)
                    arm_type = f"**{arm_passive_type.title()} {element_name.title()} Attack**"
                    arm_message = f"{element} **{resp['ARM']}:** {arm_passive_value}"
                    footer = f"The new {arm_passive_type.title()} attack will reflect on your card when equipped"

                else:
                    arm_type = f"**Unique Passive**"
                    arm_message = f"🦠 **{arm_passive_type.title()}:** {arm_passive_value}"
                    footer = f"{arm_passive_type}: {enhancer_mapping[arm_passive_type]}"



                embedVar = discord.Embed(title= f"{resp['ARM']}", description=textwrap.dedent(f"""
                {icon} **[{index}]**

                {arm_type}
                {arm_message}
                :earth_africa: **Universe:** {resp['UNIVERSE']}
                ⚒️ {arm['DUR']}
                """), 
                colour=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                embedVar.set_footer(text=f"{footer}")
                embed_list.append(embedVar)
            
            buttons = [
                manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                manage_components.create_button(style=1, label="Resell", custom_id="Resell"),
                manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                manage_components.create_button(style=2, label="Swap/Store", custom_id="Storage")
            ]
            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    u_vault = db.queryVault({'DID': d['DID']})
                    updated_vault = []
                    storage = u_vault['ASTORAGE']
                    for arm in u_vault['ARMS']:
                        updated_vault.append(arm['ARM'])
                    
                    sell_price = 0
                    selected_arm = str(button_ctx.origin_message.embeds[0].title)
                    if button_ctx.custom_id == "Equip":
                        if selected_arm in updated_vault:
                            durability = 0
                            for names in storage:
                                if names['ARM'] == selected_arm:
                                    durability = names['DUR']
                            selected_universe = custom_function
                            custom_function.selected_universe = selected_arm
                            user_query = {'DID': str(ctx.author.id)}
                            response = db.updateUserNoFilter(user_query, {'$set': {'ARM': selected_arm}})
                            await button_ctx.send(f"🦾 **{selected_arm}** equipped.")
                            self.stop = True
                        else:
                            await button_ctx.send(f"**{selected_arm}** is no longer in your vault.")
                    
                    elif button_ctx.custom_id == "Resell":
                        arm_data = db.queryArm({'ARM': selected_arm})
                        arm_name = arm_data['ARM']
                        sell_price = sell_price + (arm_data['PRICE'] * .07)
                        if arm_name == current_arm:
                            await button_ctx.send("You cannot resell equipped arms.")
                        elif arm_name in updated_vault:
                            sell_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to sell **{arm_name}** for :coin:{round(sell_price)}?", components=[sell_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Sell cancelled. Please press the Exit button if you are done reselling titles.")
                                if button_ctx.custom_id == "yes":
                                    db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ARMS': {'ARM': str(arm_name)}}})
                                    await crown_utilities.bless(sell_price, ctx.author.id)
                                    await msg.delete()
                                    await button_ctx.send(f"**{arm_name}** has been sold.")
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with selling one or all of your items.")
                                return
                        else:
                            await button_ctx.send(f"**{arm_name}** is no longer in your vault.")       
                    
                    elif button_ctx.custom_id == "Dismantle":
                        arm_data = db.queryArm({'ARM': selected_arm})
                        arm_name = arm_data['ARM']
                        element = arm_data['ELEMENT']
                        essence_amount = 100
                        arm_passive = arm_data['ABILITIES'][0]
                        arm_passive_type = list(arm_passive.keys())[0]
                        arm_passive_value = list(arm_passive.values())[0]
                        move_types = ["BASIC", "SPECIAL", "ULTIMATE"]
                        if arm_data["EXCLUSIVE"]:
                            essence_amount = 250
                        selected_universe = arm_data['UNIVERSE']
                        dismantle_amount = 10000
                        if arm_name == current_arm:
                            await button_ctx.send("You cannot dismantle equipped arms.")
                        elif arm_name == "Stock" or arm_name == "Reborn Stock" or arm_name == "Deadgun" or arm_name == "Glaive" or arm_name == "Kings Glaive" or arm_name == "Legendary Weapon":
                            await button_ctx.send("You cannot dismantle Stock arms.")
                        elif arm_name in updated_vault:
                            dismantle_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to dismantle **{arm_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Dismantle cancelled. ")
                                if button_ctx.custom_id == "yes":
                                    if selected_universe in current_gems:
                                        query = {'DID': str(ctx.author.id)}
                                        update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                        filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                        response = db.updateVault(query, update_query, filter_query)
                                    else:
                                        response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                    mess = ""
                                    if arm_passive_type in move_types:
                                        em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                        mess = f" Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence."
                                    db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ARMS': {'ARM': str(arm_name)}}})
                                    await crown_utilities.bless(sell_price, ctx.author.id)
                                    await msg.delete()
                                    await button_ctx.send(f"**{arm_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.{mess}")
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with selling one or all of your items.")
                                return
                        else:
                            await button_ctx.send(f"**{arm_name}** is no longer in your vault.")

                    elif button_ctx.custom_id == "Trade":
                        arm_data = db.queryArm({'ARM' : selected_arm})
                        arm_name = arm_data['ARM']
                        if arm_name == current_arm:
                            await button_ctx.send("You cannot trade equipped arms.")
                            return
                        sell_price = arm_data['PRICE'] * .10
                        mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                        mvalidation=False
                        bvalidation=False
                        item_already_in_trade=False
                        if mtrade:
                            if selected_arm in mtrade['MARMS']:
                                await ctx.send(f"{ctx.author.mention} arm already in **Trade**")
                                item_already_in_trade=True
                            mvalidation=True
                        else:
                            btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                            if btrade:
                                if selected_arm in btrade['BARMS']:
                                    await ctx.send(f"{ctx.author.mention} arm already in **Trade**")
                                    item_already_in_trade=True
                                bvalidation=True
                            else:
                                await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                return
                        if item_already_in_trade:
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"Woudl you like to remove **{selected_arm}** from the **Trade**?", components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Happy Trading")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    neg_sell_price = 0 - abs(int(sell_price))
                                    if mvalidation:
                                        trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$pull" : {'MARMS': selected_arm}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                        update_query = {"$pull" : {'BARMS': selected_arm}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with trading one or all of your items.")
                                return   
                        elif mvalidation == True or bvalidation ==True:    #If user is valid
                            sell_price = arm_data['PRICE'] * .10
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"Are you sure you want to trade **{selected_arm}**", components=[trade_buttons_action_row])
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Not this time. ")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    if mvalidation:
                                        trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$push" : {'MARMS': selected_arm}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                        update_query = {"$push" : {'BARMS': selected_arm}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with trading one or all of your items.")
                                return   
                                    
                    elif button_ctx.custom_id == "Storage":
                        await button_ctx.defer(ignore=True)
                        storage_buttons = [
                                    manage_components.create_button(
                                        style=ButtonStyle.green,
                                        label="Swap Storage Arm",
                                        custom_id="swap"
                                    ),
                                    manage_components.create_button(
                                        style=ButtonStyle.red,
                                        label="Add to Storage",
                                        custom_id="store"
                                    )
                                ]
                        storage_buttons_action_row = manage_components.create_actionrow(*storage_buttons)
                        msg = await ctx.send(f"Would you like to Swap Arms or Add Arm to Storage", components=[storage_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContextStorage = await manage_components.wait_for_component(self.bot, components=[storage_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "swap":
                                await button_ctx.defer(ignore=True)
                                await msg.delete()
                                await ctx.send(f"{ctx.author.mention}, Which arm number would you like to swap with in storage?")
                                def check(msg):
                                    return msg.author == ctx.author

                                try:
                                    msg = await self.bot.wait_for('message', check=check, timeout=30)
                                    author = msg.author
                                    content = msg.content
                                    # print("Author: " + str(author))
                                    # print("Content: " + str(content))
                                    # print(msg)
                                    durability = 0
                                    for names in storage:
                                        if names['ARM'] == selected_arm:
                                            durability = names['DUR']
                                    if storage[int(msg.content)]:
                                        swap_with = storage[int(msg.content)]
                                        query = {'DID': str(msg.author.id)}
                                        update_storage_query = {
                                            '$pull': {'ARMS': {'ARM' : str(selected_arm)}},
                                            '$addToSet': {'ASTORAGE' : { 'ARM' : str(selected_arm), 'DUR' : int(durability)}},
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)

                                        update_storage_query = {
                                            '$pull': {'ASTORAGE': swap_with},
                                            '$addToSet': {'ARMS': swap_with}
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)

                                        await msg.delete()
                                        await ctx.send(f"**{selected_card}** has been swapped with **{swap_with}**")
                                        return
                                    else:
                                        await ctx.send("The card number you want to swap with does not exist.")
                                        return

                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                                    return
                            if button_ctx.custom_id == "store":
                                await button_ctx.defer(ignore=True)
                                
                                try:
                                    author = msg.author
                                    content = msg.content
                                    # print("Author: " + str(author))
                                    # print("Content: " + str(content))
                                    durability = 0
                                    for names in u_vault['ARMS']:
                                        if names['ARM'] == selected_arm:
                                            durability = names['DUR']
                                    if len(storage) <= (storage_type * 15):
                                        query = {'DID': str(ctx.author.id)}
                                        update_storage_query = {
                                            '$pull': {'ARMS': {'ARM' : str(selected_arm)}},
                                            '$addToSet': {'ASTORAGE': { 'ARM' : str(selected_arm), 'DUR' : int(durability)}},
                                        }
                                        response = db.updateVaultNoFilter(query, update_storage_query)
                                        
                                        await msg.delete()
                                        await ctx.send(f"**{selected_arm}** has been added to storage")
                                        return
                                    else:
                                        await ctx.send("Not enough space in storage")
                                        return

                                except Exception as ex:
                                    trace = []
                                    tb = ex.__traceback__
                                    while tb is not None:
                                        trace.append({
                                            "filename": tb.tb_frame.f_code.co_filename,
                                            "name": tb.tb_frame.f_code.co_name,
                                            "lineno": tb.tb_lineno
                                        })
                                        tb = tb.tb_next
                                    print(str({
                                        'type': type(ex).__name__,
                                        'message': str(ex),
                                        'trace': trace
                                    }))
                                    await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92.", hidden=True)
                                    return
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
                            return
                else:
                    await ctx.send("This is not your Arms list.")        

            await Paginator(bot=self.bot, ctx=ctx ,useQuitButton=True, disableAfterTimeout=True, pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()
    
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

async def menugems(self, ctx: SlashContext):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return


    vault = db.queryVault({'DID': str(ctx.author.id)})
    current_gems = vault['GEMS']
    if current_gems:
        number_of_gems_universes = len(current_gems)

        gem_details = []
        for gd in current_gems:
            heart = ""
            soul = ""
            if gd['UNIVERSE_HEART']:
                heart = "💟"
            else:
                heart = "💔"

            if gd['UNIVERSE_SOUL']:
                soul = "🌹"
            else:
                soul = "🥀"

            gem_details.append(
                f"🌍 **{gd['UNIVERSE']}**\n💎 {'{:,}'.format(gd['GEMS'])}\nUniverse Heart {heart}\nUniverse Soul {soul}\n")

        # Adding to array until divisible by 10
        while len(gem_details) % 10 != 0:
            gem_details.append("")
        # Check if divisible by 10, then start to split evenly

        if len(gem_details) % 10 == 0:
            first_digit = int(str(len(gem_details))[:1])
            if len(gem_details) >= 89:
                if first_digit == 1:
                    first_digit = 10
            gems_broken_up = np.array_split(gem_details, first_digit)

        # If it's not an array greater than 10, show paginationless embed
        if len(gem_details) < 10:
            embedVar = discord.Embed(title=f"Gems", description="\n".join(gem_details),
                                    colour=0x7289da)
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(gems_broken_up)):
            globals()['embedVar%s' % i] = discord.Embed(title=f"Gems",
                                                        description="\n".join(gems_broken_up[i]), colour=0x7289da)
            embed_list.append(globals()['embedVar%s' % i])

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⬅️', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('➡️', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = embed_list
        await paginator.run(embeds)
    else:
        await ctx.send("You currently own no 💎.")
    
async def menublacksmith(self, ctx):
    try:
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        #    if user['LEVEL'] < 11:
        #       await ctx.send(f"🔓 Unlock the Trinket Shop by completing Floor 10 of the 🌑 Abyss! Use /solo to enter the abyss.")
        #       return
        patron_flag = user['PATRON']
        current_arm = user['ARM']
        storage_type = user['STORAGE_TYPE']
        storage_pricing = (storage_type + 1) * 1500000
        storage_pricing_text = f"{'{:,}'.format(storage_pricing)}" 
        arm_info = db.queryArm({'ARM': str(current_arm)})
        boss_arm = False
        dungeon_arm = False
        boss_message = "Nice Arm!"
        arm_cost = '{:,}'.format(100000)
        durability_message = f"{arm_cost}"
        if arm_info['AVAILABLE'] == False and arm_info['EXCLUSIVE'] == False:
            boss_arm = True
        elif arm_info['AVAILABLE'] == True and arm_info['EXCLUSIVE'] == True:
            dungeon_arm= True
            arm_cost = '{:,}'.format(250000)
            durability_message = f"{arm_cost}"
        if boss_arm:
            boss_message = "Cannot Repair"
            durability_message = "UNAVAILABLE"
        elif dungeon_arm:
            boss_message = "Dungeon eh?!"
        vault = db.altQueryVault({'DID' : str(ctx.author.id)})
        current_card = user['CARD']
        if storage_type >=10:
            storage_pricing_text = "Max Storage Level"
            storage_tier_message = "MAX"
        has_gabes_purse = user['TOURNAMENT_WINS']
        balance = vault['BALANCE']
        icon = ":coin:"
        if balance >= 1000000:
            icon = ":money_with_wings:"
        elif balance >=650000:
            icon = ":moneybag:"
        elif balance >= 150000:
            icon = ":dollar:"
        
        owned_arms = []
        current_durability = 0
        for arms in vault['ARMS']:
            if arms['ARM'] == current_arm:
                current_durability = arms['DUR']

        card_info = {}
        for level in vault['CARD_LEVELS']:
            if level['CARD'] == current_card:
                card_info = level

        lvl = card_info['LVL']

        
        hundred_levels = 650000
        thirty_levels = 220000
        ten_levels = 80000
        
        licon = "🔰"
        if lvl>= 200:
            licon ="🔱"
        if lvl>= 700:
            licon ="⚜️"
        if lvl >= 999:
            licon = "🏅"

        if lvl >= 200 and lvl < 299:
            hundred_levels = 30000000
            thirty_levels = 20000000
            ten_levels = 10000000
        elif lvl >= 300 and lvl < 399:
            hundred_levels = 70000000
            thirty_levels = 50000000
            ten_levels = 25000000
        elif lvl >= 400 and lvl < 499:
            hundred_levels = 90000000
            thirty_levels = 75000000
            ten_levels = 50000000
        elif lvl >= 500 and lvl < 599:
            hundred_levels = 150000000
            thirty_levels = 100000000
            ten_levels = 75000000
        elif lvl >= 600 and lvl < 699:
            hundred_levels = 300000000
            thirty_levels = 200000000
            ten_levels = 100000000
        # if lvl >= 700 and lvl <= 800:
        #     hundred_levels = hundred_levels * 2000
        sell_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label="🔋 1️⃣",
                    custom_id="1"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="🔋 2️⃣",
                    custom_id="2"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="🔋 3️⃣",
                    custom_id="3"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="⚒️ 4️⃣",
                    custom_id="5"
                ),
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Cancel",
                    custom_id="cancel"
                )
            ]
        
        util_sell_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Gabe's Purse 👛",
                    custom_id="4"
                ),
                manage_components.create_button(
                    style=ButtonStyle.grey,
                    label="Storage 💼",
                    custom_id="6"
                )
        ]
        
        sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
        util_sell_buttons_action_row = manage_components.create_actionrow(*util_sell_buttons)
        embedVar = discord.Embed(title=f"🔨 | **Blacksmith** - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
        Welcome {ctx.author.mention}!
        Purchase **Card XP** and **Arm Durability**!
        🎴 Card:  **{current_card}** {licon}**{lvl}**
        🦾 Arm: **{current_arm}** *{boss_message}*
        

        🔋 1️⃣ **10 Levels** for :coin: **{'{:,}'.format(ten_levels)}**
    
        🔋 2️⃣ **30 Levels** for :dollar: **{'{:,}'.format(thirty_levels)}**

        🔋 3️⃣ **100 Levels** for :moneybag: **{'{:,}'.format(hundred_levels)}**

        ⚒️ 4️⃣ **50 Durability** for :dollar: **{durability_message}**

        💼 **Storage Tier {str(storage_type + 1)}**: :money_with_wings: **{storage_pricing_text}**


        Purchase **Gabe's Purse** to Keep ALL ITEMS when **Rebirthing**
        *You will not be able to select a new starting universe!*

        **Gabe's Purse** 👛 for :money_with_wings: **10,000,000**

        What would you like to buy?
        """), colour=0xf1c40f)
        embedVar.set_footer(text="Boosts are used immediately upon purchase. Click cancel to exit purchase.", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")
        msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row, util_sell_buttons_action_row])

        def check(button_ctx):
            return button_ctx.author == ctx.author

        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[sell_buttons_action_row, util_sell_buttons_action_row], timeout=120,check=check)
            levels_gained = 0
            price = 0
            exp_boost_buttons = ["1", "2", "3"]
            if button_ctx.custom_id == "1":
                # if lvl >= 200:
                #     await button_ctx.send("You can only purchase option 3 when leveling past level 200.")
                #     return
                levels_gained = 10
                price = ten_levels
            if button_ctx.custom_id == "2":
                # if lvl >= 200:
                #     await button_ctx.send("You can only purchase option 3 when leveling past level 200.")
                #     return
                levels_gained = 30
                price = thirty_levels
            if button_ctx.custom_id == "3":
                levels_gained = 100
                price=hundred_levels
            if button_ctx.custom_id == "5":
                levels_gained = 50
                price=100000


            if button_ctx.custom_id == "cancel":
                await msg.edit(components=[])
                return

            if button_ctx.custom_id in exp_boost_buttons:
                if price > balance:
                    await button_ctx.send("You're too broke to buy. Get your money up.", hidden=True)
                    await msg.edit(components=[])
                    return

                card_info = {}
                for level in vault['CARD_LEVELS']:
                    if level['CARD'] == current_card:
                        card_info = level

                lvl = card_info['LVL']
                max_lvl = 700
                if lvl >= max_lvl:
                    await button_ctx.send(f"**{current_card}** is already at max Smithing level. You may level up in **battle**, but you can no longer purchase levels for this card.", hidden=True)
                    await msg.edit(components=[])
                    return

                elif (levels_gained + lvl) > max_lvl:
                    levels_gained =  max_lvl - lvl


                atk_def_buff = round(levels_gained / 2)
                ap_buff = round(levels_gained / 3)
                hlt_buff = (round(levels_gained / 20) * 25)

                query = {'DID': str(ctx.author.id)}
                update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0}, '$inc': {'CARD_LEVELS.$[type].' + "LVL": levels_gained, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff, 'CARD_LEVELS.$[type].' + "DEF": atk_def_buff, 'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                filter_query = [{'type.'+ "CARD": str(current_card)}]
                response = db.updateVault(query, update_query, filter_query)
                await crown_utilities.curse(price, str(ctx.author.id))
                await button_ctx.send(f"**{str(current_card)}** gained {levels_gained} levels!")
                await msg.edit(components=[])
                if button_ctx.custom_id == "cancel":
                    await button_ctx.send("Sell ended.", hidden=True)
                    await msg.edit(components=[])
                    return

            if button_ctx.custom_id == "4":
                price = 10000000
                if price > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                if has_gabes_purse:
                    await button_ctx.send("You already own Gabes Purse. You cannot purchase more than one.", hidden=True)
                    await msg.edit(components=[])
                    return
                else:
                    update = db.updateUserNoFilterAlt(user_query, {'$set': {'TOURNAMENT_WINS': 1}})
                    await crown_utilities.curse(10000000, str(ctx.author.id))
                    await button_ctx.send("Gabe's Purse has been purchased!")
                    await msg.edit(components=[])
                    return
            
            if button_ctx.custom_id == "5":
                if dungeon_arm:
                    price = 250000
                if boss_arm:
                    await button_ctx.send("Sorry I can't repair **Boss** Arms ...", hidden=True)
                    await msg.edit(components=[])
                    return
                if price > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                if current_durability >= 100:
                    await button_ctx.send(f"🦾 {current_arm} is already at Max Durability. ⚒️",hidden=True)
                    await msg.edit(components=[])
                    return
                else:
                    try:
                        new_durability = current_durability + levels_gained
                        full_repair = False
                        if new_durability > 100:
                            levels_gained = 100 - current_durability
                            full_repair=True
                        query = {'DID': str(ctx.author.id)}
                        update_query = {'$inc': {'ARMS.$[type].' + 'DUR': levels_gained}}
                        filter_query = [{'type.' + "ARM": str(current_arm)}]
                        resp = db.updateVault(query, update_query, filter_query)

                        await crown_utilities.curse(price, str(ctx.author.id))
                        if full_repair:
                                await button_ctx.send(f"{current_arm}'s ⚒️ durability has increased by **{levels_gained}**!\n*Maximum Durability Reached!*")
                        else:
                                await button_ctx.send(f"{current_arm}'s ⚒️ durability has increased by **{levels_gained}**!")
                        await msg.edit(components=[])
                        return
                    except:
                        await ctx.send("Failed to purchase durability boost.", hidden=True)

            if button_ctx.custom_id == "6":
                if storage_pricing > balance:
                    await button_ctx.send("Insufficent funds.", hidden=True)
                    await msg.edit(components=[])
                    return
                    
                if not patron_flag and storage_type >= 2:
                    await button_ctx.send("Only Patrons may purchase more than 30 additional storage. To become a Patron, visit https://www.patreon.com/partychatgaming?fan_landing=true.", hidden=True)
                    await msg.edit(components=[])
                    return
                    
                if storage_type == 10:
                    await button_ctx.send("You already have max storage.")
                    await msg.edit(components=[])
                    return
                    
                else:
                    update = db.updateUserNoFilterAlt(user_query, {'$inc': {'STORAGE_TYPE': 1}})
                    await crown_utilities.curse(storage_pricing, str(ctx.author.id))
                    await button_ctx.send(f"Storage Tier {str(storage_type + 1)} has been purchased!")
                    await msg.edit(components=[])
                    return

        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("Blacksmith closed unexpectedly. Seek support.", hidden=True)
    except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("Blacksmith closed unexpectedly. Seek support.", hidden=True)

async def menusummons(self, ctx):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    vault = db.queryVault({'DID': d['DID']})
    if vault:
        try:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            balance = vault['BALANCE']
            current_summon = d['PET']
            pets_list = vault['PETS']

            total_pets = len(pets_list)

            pets=[]
            licon = ":coin:"
            if balance >= 150000:
                licon = ":money_with_wings:"
            elif balance >=100000:
                licon = ":moneybag:"
            elif balance >= 50000:
                licon = ":dollar:"
            current_gems = []
            for gems in vault['GEMS']:
                current_gems.append(gems['UNIVERSE'])
            bond_message = ""
            lvl_message = ""
            embed_list = []
            for pet in pets_list:
                #cpetmove_ap= (cpet_bond * cpet_lvl) + list(cpet.values())[3] # Ability Power
                bond_message = ""
                lvl_message = ""
                
                pet_bond = pet['BOND']
                bond_exp = pet['BONDEXP']
                pet_level = pet['LVL']
                pet_exp = pet['EXP']
                
                petmove_ap = list(pet.values())[3] 
                bond_req = ((petmove_ap * 5) * (pet_bond + 1))
                lvl_req = int(pet_level) * 10
                
                bond_message = f"*{pet_exp}/{lvl_req}*"
                lvl_message = f"*{bond_exp}/{bond_req}*"
                
                if pet['BOND'] == 3:
                    bond_message = ":star2:"
                if pet['LVL'] == 10:
                    lvl_message = ":star:"
                
                pet_ability = list(pet.keys())[3]
                pet_ability_power = list(pet.values())[3]
                power = (pet['BOND'] * pet['LVL']) + pet_ability_power
                pet_info = db.queryPet({'PET' : pet['NAME']})
                if pet_info:
                    pet_available = pet_info['AVAILABLE']
                    pet_exclusive = pet_info['EXCLUSIVE']
                    pet_universe = pet_info['UNIVERSE']
                icon = "🧬"
                if pet_available and pet_exclusive:
                    icon = ":fire:"
                elif pet_available == False and pet_exclusive ==False:
                    icon = ":japanese_ogre:"

                embedVar = discord.Embed(title= f"{pet['NAME']}", description=textwrap.dedent(f"""
                {icon}
                _Bond_ **{pet['BOND']}** {bond_message}
                _Level_ **{pet['LVL']} {lvl_message}**
                :small_blue_diamond: **{pet_ability}:** {power}
                🦠 **Type:** {pet['TYPE']}"""), 
                colour=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                embedVar.set_footer(text=f"{pet['TYPE']}: {enhancer_mapping[pet['TYPE']]}")
                embed_list.append(embedVar)
            
            buttons = [
                manage_components.create_button(style=3, label="Equip", custom_id="Equip"),
                manage_components.create_button(style=1, label="Trade", custom_id="Trade"),
                manage_components.create_button(style=1, label="Dismantle", custom_id="Dismantle"),
                manage_components.create_button(style=2, label="Exit", custom_id="Exit")
            ]
            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    updated_vault = db.queryVault({'DID': d['DID']})
                    sell_price = 0
                    selected_summon = str(button_ctx.origin_message.embeds[0].title)
                    user_query = {'DID': str(ctx.author.id)}
                    
                    if button_ctx.custom_id == "Equip":
                        response = db.updateUserNoFilter(user_query, {'$set': {'FAMILY_PET': False, 'PET': str(button_ctx.origin_message.embeds[0].title)}})
                        await button_ctx.send(f"🧬 **{str(button_ctx.origin_message.embeds[0].title)}** equipped.")
                        self.stop = True
                    
                    elif button_ctx.custom_id =="Trade":
                        summon_data = db.queryPet({'PET' : selected_summon})
                        summon_name = summon_data['PET']
                        if summon_name == current_summon:
                            await button_ctx.send("You cannot trade equipped summons.")
                            return
                        sell_price = 5000
                        mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                        mvalidation=False
                        bvalidation=False
                        item_already_in_trade=False
                        if mtrade:
                            if selected_summon in mtrade['MSUMMONS']:
                                await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
                                item_already_in_trade=True
                            mvalidation=True
                        else:
                            btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                            if btrade:
                                if selected_summon in btrade['BSUMMONS']:
                                    await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
                                    item_already_in_trade=True
                                bvalidation=True
                            else:
                                await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                return
                        if item_already_in_trade:
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"Woudl you like to remove **{selected_summon}** from the **Trade**?", components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author
                                                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Happy Trading")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    neg_sell_price = 0 - abs(int(sell_price))
                                    if mvalidation:
                                        trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$pull" : {'MSUMMONS': selected_summon}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                        update_query = {"$pull" : {'BSUMMONS': selected_summon}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with trading one or all of your items.")
                                return   
                        elif mvalidation == True or bvalidation ==True:    #If user is valid
                            sell_price = 5000
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"Are you sure you want to trade **{selected_summon}**", components=[trade_buttons_action_row])
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Not this time. ")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    if mvalidation:
                                        trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$push" : {'MSUMMONS': selected_summon}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                        update_query = {"$push" : {'BSUMMONS': selected_summon}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                            except Exception as ex:
                                trace = []
                                tb = ex.__traceback__
                                while tb is not None:
                                    trace.append({
                                        "filename": tb.tb_frame.f_code.co_filename,
                                        "name": tb.tb_frame.f_code.co_name,
                                        "lineno": tb.tb_lineno
                                    })
                                    tb = tb.tb_next
                                print(str({
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
                                await ctx.send("There's an issue with trading one or all of your items.")
                                return   
                    
                    elif button_ctx.custom_id == "Dismantle":
                        summon_data = db.queryPet({'PET' : selected_summon})
                        summon_name = summon_data['PET']
                        if summon_name == current_summon:
                            await button_ctx.send("You cannot dismanetle equipped summonss.")
                            return
                        dismantle_price = 5000   
                        level = int(pet['LVL'])
                        bond = int(pet['BOND'])
                        dismantle_amount = round((1000* level) + (dismantle_price * bond))
                        dismantle_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Yes",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = manage_components.create_actionrow(*dismantle_buttons)
                        msg = await button_ctx.send(f"Are you sure you want to dismantle **{summon_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                                self.stop = True
                            if button_ctx.custom_id == "yes":
                                if pet_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    family_query = {'HEAD':d['FAMILY']}
                                    if d['FAMILY'] != 'PCG':
                                        family_info = db.queryFamily(family_query)
                                        if summon_name == family_info['SUMMON']:
                                            update_query = {'$set' : {'SUMMON': d['PET']}}
                                            family_update = db.updateFamily(family_query,update_query)
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": pet_universe}]
                                    response = db.updateVault(query, update_query, filter_query)
                                else:
                                    response = db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': pet_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                
                                db.updateVaultNoFilter({'DID': str(ctx.author.id)},{'$pull':{'PETS': {"NAME": str(summon_name)}}})
                                #await crown_utilities.bless(sell_price, ctx.author.id)
                                await msg.delete()
                                await button_ctx.send(f"**{summon_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.")
                                self.stop = True
                        except Exception as ex:
                            trace = []
                            tb = ex.__traceback__
                            while tb is not None:
                                trace.append({
                                    "filename": tb.tb_frame.f_code.co_filename,
                                    "name": tb.tb_frame.f_code.co_name,
                                    "lineno": tb.tb_lineno
                                })
                                tb = tb.tb_next
                            print(str({
                                'type': type(ex).__name__,
                                'message': str(ex),
                                'trace': trace
                            }))
                            #await ctx.send(f"ERROR:\nTYPE: {type(ex).__name__}\nMESSAGE: {str(ex)}\nLINE: {trace} ")
                            return
                    elif button_ctx.custom_id =="Exit":
                        await button_ctx.defer(ignore=True)
                        self.stop = True
                else:
                    await ctx.send("This is not your Summons list.")
            await Paginator(bot=self.bot, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()

        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("There's an issue with your Summons list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

async def menudestinies(self, ctx):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    vault = db.queryVault({'DID': d['DID']})
    if not vault['DESTINY']:
        await ctx.send("No Destiny Lines available at this time!")
        return
    if vault:
        try:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            balance = vault['BALANCE']
            destiny = vault['DESTINY']

            destiny_messages = []
            icon = ":coin:"
            if balance >= 150000:
                icon = ":money_with_wings:"
            elif balance >=100000:
                icon = ":moneybag:"
            elif balance >= 50000:
                icon = ":dollar:"
            for d in destiny:
                if not d['COMPLETED']:
                    destiny_messages.append(textwrap.dedent(f"""\
                    :sparkles: **{d["NAME"]}**
                    Defeat **{d['DEFEAT']}** with **{" ".join(d['USE_CARDS'])}** | **Current Progress:** {d['WINS']}/{d['REQUIRED']}
                    Win :flower_playing_cards: **{d['EARN']}**
                    """))

            if not destiny_messages:
                await ctx.send("No Destiny Lines available at this time!")
                return
            # Adding to array until divisible by 10
            while len(destiny_messages) % 10 != 0:
                destiny_messages.append("")

            # Check if divisible by 10, then start to split evenly
            if len(destiny_messages) % 10 == 0:
                first_digit = int(str(len(destiny_messages))[:1])
                if len(destiny_messages) >= 89:
                    if first_digit == 1:
                        first_digit = 10
                destinies_broken_up = np.array_split(destiny_messages, first_digit)
            
            # If it's not an array greater than 10, show paginationless embed
            if len(destiny_messages) < 10:
                embedVar = discord.Embed(title= f"Destiny Lines\n**Balance**: :coin:{'{:,}'.format(balance)}", description="\n".join(destiny_messages), colour=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                # embedVar.set_footer(text=f".equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                await ctx.send(embed=embedVar)

            embed_list = []
            for i in range(0, len(destinies_broken_up)):
                globals()['embedVar%s' % i] = discord.Embed(title= f":sparkles: Destiny Lines\n**Balance**: {icon}{'{:,}'.format(balance)}", description="\n".join(destinies_broken_up[i]), colour=0x7289da)
                globals()['embedVar%s' % i].set_thumbnail(url=avatar)
                # globals()['embedVar%s' % i].set_footer(text=f"{total_pets} Total Pets\n.equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                embed_list.append(globals()['embedVar%s' % i])

            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
            paginator.add_reaction('⏮️', "first")
            paginator.add_reaction('⬅️', "back")
            paginator.add_reaction('🔐', "lock")
            paginator.add_reaction('➡️', "next")
            paginator.add_reaction('⏭️', "last")
            embeds = embed_list
            await paginator.run(embeds)
        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("There's an issue with your Destiny Line list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

async def menuquests(self, ctx):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    vault = db.queryVault({'DID': d['DID']})
    # server = db.queryServer({"GNAME": str(ctx.author.guild)})
    if not vault['QUESTS']:
        await ctx.send("You have no quests available at this time!", hidden=True)
        return
    if vault:
        try:
            buttons = []
            guild_buff = await crown_utilities.guild_buff_update_function(d['TEAM'].lower())
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            balance = vault['BALANCE']
            quests = vault['QUESTS']
            embed_list = []
            quest_messages = []

            buff_message = ""
            virus_message = ""

            # if server:
            #     server_buff = server['SERVER_BUFF_BOOL']
            #     server_virus = server['SERVER_VIRUS_BOOL']
            #     server_name = server['GNAME']

            #     if not server_buff:
            #         buff_message = f"No active buffs in **{server_name}**"
            #     if not server_virus:
            #         virus_message = f"No active viruses in **{server_name}**"

            for quest in quests:
                guild_buff_msg = "🔴"
                if guild_buff:                    
                    if guild_buff['Quest']:
                        guild_buff_msg = "🟢"


                opponent = db.queryCard({'NAME': quest['OPPONENT']})
                opponent_universe = db.queryUniverse({'TITLE': opponent['UNIVERSE']})
                opponent_name = opponent['NAME']
                opponent_universe_image = opponent_universe['PATH']
                tales = opponent_universe['CROWN_TALES']
                dungeon = opponent_universe['DUNGEONS']
                goal = quest['GOAL']
                wins = quest['WINS']
                reward = '{:,}'.format(quest['REWARD'])
                tales_message = ""
                dungeon_message = ""
                tales_index = 0
                dungeon_index = 0
                if opponent_name in tales:
                    for opp in tales:
                        tales_index = tales.index(opponent_name)
                    tales_message = f"**{opponent_name}** is fight number ⚔️ **{tales_index + 1}** in **Tales**"
                
                if opponent_name in dungeon:
                    for opp in dungeon:
                        dungeon_index = dungeon.index(opponent_name)
                    dungeon_message = f"**{opponent_name}** is fight number ⚔️ **{dungeon_index + 1}** in **Dungeon**"
                
                completed = ""
                
                if quest['GOAL'] == quest['WINS']:
                    completed = "🟢"
                else:
                    completed = "🔴"
                icon = ":coin:"
                if balance >= 150000:
                    icon = ":money_with_wings:"
                elif balance >=100000:
                    icon = ":moneybag:"
                elif balance >= 50000:
                    icon = ":dollar:"


                embedVar = discord.Embed(title=f"{opponent_name}", description=textwrap.dedent(f"""\
                **Quest**: Defeat {opponent_name} **{str(goal)}** times!
                **Universe:** 🌍 {opponent['UNIVERSE']}
                **Reward:** {icon} {reward}

                **Guild Quest Buff:**  {guild_buff_msg}
                
                **Wins so far:** {str(wins)}
                **Completed:** {completed}

                {tales_message}
                {dungeon_message}

                {buff_message}
                
                {virus_message}
                """))

                embedVar.set_thumbnail(url=opponent_universe_image)
                # embedVar.set_footer(text="Use /tales to complete daily quest!", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")

                if quest['GOAL'] != quest['WINS']:
                    embed_list.append(embedVar)

            if not embed_list:
                await ctx.send("All quests have been completed today! 👑")
                return

            buttons = [manage_components.create_button(style=3, label="Start Quest Tales", custom_id="quests_tales"),]
            custom_action_row = manage_components.create_actionrow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    selected_quest = str(button_ctx.origin_message.embeds[0].title)
                    if button_ctx.custom_id == "quests_tales":
                        mode = "Tales"
                        await button_ctx.defer(ignore=True)
                        card = db.queryCard({"NAME": selected_quest})
                        sowner = db.queryUser({'DID': str(ctx.author.id)})
                        universe = db.queryUniverse({"TITLE": card['UNIVERSE']})
                        selected_universe = universe['TITLE']
                        completed_universes = sowner['CROWN_TALES']
                        oguild = "PCG"
                        crestlist = []
                        crestsearch = False
                        # guild = server_name
                        oteam = sowner['TEAM']
                        ofam = sowner['FAMILY']
                        guild_buff = await crown_utilities.guild_buff_update_function(sowner['TEAM'].lower())
                        

                        # if sowner['LEVEL'] < 4:
                        #     await button_ctx.send("🔓 Unlock **Tales** by completing **Floor 3** of the 🌑 **Abyss**! Use /solo to enter the abyss.")
                        #     self.stop = True
                        #     return

                        if oteam != 'PCG':
                            team_info = db.queryTeam({'TEAM_NAME': oteam.lower()})
                            guildname = team_info['GUILD']
                            if guildname != "PCG":
                                oguild = db.queryGuildAlt({'GNAME': guildname})
                                if oguild:
                                    crestlist = oguild['CREST']
                                    crestsearch = True

                        currentopponent = 0
                        if guild_buff:
                            if guild_buff['Quest']:
                                for opp in universe['CROWN_TALES']:
                                    if opp == card['NAME']:
                                        currentopponent = universe['CROWN_TALES'].index(opp)
                                        update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])
                                    
                        await battle_commands(self, ctx, mode, universe, selected_universe, completed_universes, oguild,
                                crestlist, crestsearch, sowner, oteam, ofam, currentopponent, None, None, None,
                                None, None, None, None, None)
                        
                        self.stop = True
                else:
                    await ctx.send("This is not your Title list.")

            await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                custom_action_row,
                custom_function,
            ]).run()

        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            await ctx.send("There's an issue with your Quest list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", hidden=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})

async def menubalance(self, ctx):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    try:
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        icon = ":coin:"
        if vault:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            balance = vault['BALANCE']
            if balance >= 50000000:
                icon = ":money_with_wings:"
            elif balance >=10000000:
                icon = ":moneybag:"
            elif balance >= 500000:
                icon = ":dollar:"
            if d['TEAM'] != 'PCG':
                t = db.queryTeam({'TEAM_NAME' : d['TEAM'].lower()})
                tbal = t['BANK']
                if d['FAMILY'] != 'PCG':
                    f = db.queryFamily({'HEAD': d['FAMILY']})
                    fbal = f['BANK']
            embedVar = discord.Embed(title= f"{icon}{'{:,}'.format(balance)}", colour=0x7289da)
            await ctx.send(embed=embedVar)
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
    except:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        
async def menupreset(self, ctx):
    try:
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault_query = {'DID': d['DID']}
        vault = db.queryVault(vault_query)
        if vault:
            ownedcards = []
            ownedtitles = []
            ownedarms = []
            ownedpets = []
            for cards in vault['CARDS']:
                ownedcards.append(cards)
            for titles in vault['TITLES']:
                ownedtitles.append(titles)
            for arms in vault['ARMS']:
                ownedarms.append(arms['ARM'])
            for pets in vault['PETS']:
                ownedpets.append(pets['NAME'])

            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            cards = vault['CARDS']
            titles = vault['TITLES']
            deck = vault['DECK']
            preset_length = len(deck)
            preset_update = d['U_PRESET']
            
            
            preset1_card = list(deck[0].values())[0]
            preset1_title = list(deck[0].values())[1]
            preset1_arm = list(deck[0].values())[2]
            preset1_pet = list(deck[0].values())[3]

            preset2_card = list(deck[1].values())[0]
            preset2_title = list(deck[1].values())[1]
            preset2_arm = list(deck[1].values())[2]
            preset2_pet = list(deck[1].values())[3]

            preset3_card = list(deck[2].values())[0]
            preset3_title = list(deck[2].values())[1]
            preset3_arm = list(deck[2].values())[2]
            preset3_pet = list(deck[2].values())[3]    
            
            if preset_update:
                preset4_card = list(deck[3].values())[0]
                preset4_title = list(deck[3].values())[1]
                preset4_arm = list(deck[3].values())[2]
                preset4_pet = list(deck[3].values())[3]

                preset5_card = list(deck[4].values())[0]
                preset5_title = list(deck[4].values())[1]
                preset5_arm = list(deck[4].values())[2]
                preset5_pet = list(deck[4].values())[3]  
                
                listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n", 
                f"4️⃣| {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n\n", 
                f"5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n\n"]  
            else:
                listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n"]
        
            embedVar = discord.Embed(title="🔖 | Preset Menu", description=textwrap.dedent(f"""
            {"".join(listed_options)}
            """))
            embedVar.set_thumbnail(url=avatar)
            # embedVar.add_field(name=f"Preset 1:{preset1_title} {preset1_card} and {preset1_pet}", value=f"Card: {preset1_card}\nTitle: {preset1_title}\nArm: {preset1_arm}\nSummon: {preset1_pet}", inline=False)
            # embedVar.add_field(name=f"Preset 2:{preset2_title} {preset2_card} and {preset2_pet}", value=f"Card: {preset2_card}\nTitle: {preset2_title}\nArm: {preset2_arm}\nSummon: {preset2_pet}", inline=False)
            # embedVar.add_field(name=f"Preset 3:{preset3_title} {preset3_card} and {preset3_pet}", value=f"Card: {preset3_card}\nTitle: {preset3_title}\nArm: {preset3_arm}\nSummon: {preset3_pet}", inline=False)
            util_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="1️⃣",
                    custom_id = "1"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="2️⃣",
                    custom_id = "2"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="3️⃣",
                    custom_id = "3"
                )
            ]
            
            if preset_update:
                util_buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="4️⃣",
                        custom_id="4"
                    )
                )
                util_buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="5️⃣",
                        custom_id="5"
                    )
                )
                
                    

            util_action_row = manage_components.create_actionrow(*util_buttons)
            components = [util_action_row]
            await ctx.send(embed=embedVar,components=[util_action_row])
            
            def check(button_ctx):
                return button_ctx.author == ctx.author
            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[util_action_row], timeout=30,check=check)

                if  button_ctx.custom_id == "0":
                    await button_ctx.send(f"{ctx.author.mention}, No change has been made", hidden=True)
                    return
                elif  button_ctx.custom_id == "1":
                    for card in ownedcards :                     
                        if preset1_card in ownedcards:
                            for title in ownedtitles:
                                if preset1_title in ownedtitles:
                                    for arm in ownedarms:
                                        if preset1_arm in ownedarms:
                                            for pet in ownedpets:
                                                if preset1_pet in ownedpets:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card), 'TITLE': str(preset1_title),'ARM': str(preset1_arm), 'PET': str(preset1_pet)}})
                                                    await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                    return
                                                else:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card), 'TITLE': str(preset1_title),'ARM': str(preset1_arm)}})
                                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset1_pet}", hidden=True)
                                                    return
                                        else:
                                            response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card), 'TITLE': str(preset1_title),'PET': str(preset1_pet)}})
                                            await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset1_arm}")
                                            return
                                else:
                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset1_card),'ARM': str(preset1_arm), 'PET': str(preset1_pet)}})
                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset1_title}")
                                    return
                        else:
                            response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset1_title),'ARM': str(preset1_arm), 'PET': str(preset1_pet)}})
                            await button_ctx.send(f"{ctx.author.mention}'s items updated, You No Longer Own {preset1_card}")
                            return
                elif  button_ctx.custom_id == "2":
                    for card in ownedcards :                     
                        if preset2_card in ownedcards:
                            for title in ownedtitles:
                                if preset2_title in ownedtitles:
                                    for arm in ownedarms:
                                        if preset2_arm in ownedarms:
                                            for pet in ownedpets:
                                                if preset2_pet in ownedpets:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card), 'TITLE': str(preset2_title),'ARM': str(preset2_arm), 'PET': str(preset2_pet)}})
                                                    await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                    return
                                                else:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card), 'TITLE': str(preset2_title),'ARM': str(preset2_arm)}})
                                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset2_pet}")
                                                    return
                                        else:
                                            response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card), 'TITLE': str(preset2_title), 'PET': str(preset2_pet)}})
                                            await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset2_arm}")
                                            return
                                else:
                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset2_card),'ARM': str(preset2_arm), 'PET': str(preset2_pet)}})
                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset2_title}")
                                    return
                        else:
                            response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset2_title),'ARM': str(preset2_arm), 'PET': str(preset2_pet)}})
                            await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset2_card}.")
                            return
                elif  button_ctx.custom_id == "3":
                    for card in ownedcards :                     
                        if preset3_card in ownedcards:
                            for title in ownedtitles:
                                if preset3_title in ownedtitles:
                                    for arm in ownedarms:
                                        if preset3_arm in ownedarms:
                                            for pet in ownedpets:
                                                if preset3_pet in ownedpets:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card), 'TITLE': str(preset3_title),'ARM': str(preset3_arm), 'PET': str(preset3_pet)}})
                                                    await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                    return
                                                else:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card), 'TITLE': str(preset3_title),'ARM': str(preset3_arm)}})
                                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset3_pet}")
                                                    return
                                        else:
                                            response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card), 'TITLE': str(preset3_title),'PET': str(preset3_pet)}})
                                            await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset3_arm}")
                                            return
                                else:
                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset3_card),'ARM': str(preset3_arm), 'PET': str(preset3_pet)}})
                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset3_title}")
                                    return
                        else:
                            response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset3_title),'ARM': str(preset3_arm), 'PET': str(preset3_pet)}})
                            await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset3_card}")
                            return  
                elif  button_ctx.custom_id == "4":
                    for card in ownedcards :                     
                        if preset4_card in ownedcards:
                            for title in ownedtitles:
                                if preset4_title in ownedtitles:
                                    for arm in ownedarms:
                                        if preset4_arm in ownedarms:
                                            for pet in ownedpets:
                                                if preset4_pet in ownedpets:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card), 'TITLE': str(preset4_title),'ARM': str(preset4_arm), 'PET': str(preset4_pet)}})
                                                    await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                    return
                                                else:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card), 'TITLE': str(preset4_title),'ARM': str(preset4_arm)}})
                                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset4_pet}")
                                                    return
                                        else:
                                            response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card), 'TITLE': str(preset4_title),'PET': str(preset4_pet)}})
                                            await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset4_arm}")
                                            return
                                else:
                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset4_card),'ARM': str(preset3_arm), 'PET': str(preset4_pet)}})
                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset4_title}")
                                    return
                        else:
                            response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset4_title),'ARM': str(preset3_arm), 'PET': str(preset4_pet)}})
                            await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset4_card}")
                            return  
                elif  button_ctx.custom_id == "5":
                    for card in ownedcards :                     
                        if preset5_card in ownedcards:
                            for title in ownedtitles:
                                if preset5_title in ownedtitles:
                                    for arm in ownedarms:
                                        if preset5_arm in ownedarms:
                                            for pet in ownedpets:
                                                if preset5_pet in ownedpets:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card), 'TITLE': str(preset5_title),'ARM': str(preset5_arm), 'PET': str(preset5_pet)}})
                                                    await button_ctx.send(f"{ctx.author.mention}, your build updated successfully!")
                                                    return
                                                else:
                                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card), 'TITLE': str(preset5_title),'ARM': str(preset5_arm)}})
                                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset5_pet}")
                                                    return
                                        else:
                                            response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card), 'TITLE': str(preset5_title),'PET': str(preset5_pet)}})
                                            await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset5_arm}")
                                            return
                                else:
                                    response = db.updateUserNoFilter(query, {'$set': {'CARD': str(preset5_card),'ARM': str(preset5_arm), 'PET': str(preset5_pet)}})
                                    await button_ctx.send(f"{ctx.author.mention}'s build updated, You No Longer Own {preset5_title}")
                                    return
                        else:
                            response = db.updateUserNoFilter(query, {'$set': {'TITLE': str(preset5_title),'ARM': str(preset5_arm), 'PET': str(preset5_pet)}})
                            await button_ctx.send(f"{ctx.author.mention}'s Items updated, You No Longer Own {preset5_card}")
                            return  
                
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("Preset Issue Seek support.", hidden=True)
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", hidden=True)
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await ctx.send("Preset Issue Seek support.", hidden=True)
async def menusavepreset(self, ctx):
    try:
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault_query = {'DID': d['DID']}
        vault = db.queryVault(vault_query)
        if vault:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            cards = vault['CARDS']
            titles = vault['TITLES']
            deck = vault['DECK']


            current_card = d['CARD']
            current_title = d['TITLE']
            current_arm= d['ARM']
            current_pet = d['PET']
            preset_update = d['U_PRESET']

            
            preset1_card = list(deck[0].values())[0]
            preset1_title = list(deck[0].values())[1]
            preset1_arm = list(deck[0].values())[2]
            preset1_pet = list(deck[0].values())[3]

            preset2_card = list(deck[1].values())[0]
            preset2_title = list(deck[1].values())[1]
            preset2_arm = list(deck[1].values())[2]
            preset2_pet = list(deck[1].values())[3]

            preset3_card = list(deck[2].values())[0]
            preset3_title = list(deck[2].values())[1]
            preset3_arm = list(deck[2].values())[2]
            preset3_pet = list(deck[2].values())[3]    

            if preset_update:
                preset4_card = list(deck[3].values())[0]
                preset4_title = list(deck[3].values())[1]
                preset4_arm = list(deck[3].values())[2]
                preset4_pet = list(deck[3].values())[3]

                preset5_card = list(deck[4].values())[0]
                preset5_title = list(deck[4].values())[1]
                preset5_arm = list(deck[4].values())[2]
                preset5_pet = list(deck[4].values())[3]  
                
                listed_options = [f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n\n",
                f"📝1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                f"📝2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                f"📝3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n", 
                f"📝4️⃣| {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n\n", 
                f"📝5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n\n"]  
            else:
                listed_options = [f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n\n",
                f"📝1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n\n", 
                f"📝2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n\n", 
                f"📝3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n\n"]
        
            embedVar = discord.Embed(title=f"📝 | Save Current Build", description=textwrap.dedent(f"""
            {"".join(listed_options)}
            """))
            util_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label="📝 1️⃣",
                    custom_id = "1"
                ),
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label="📝 2️⃣",
                    custom_id = "2"
                ),
                manage_components.create_button(
                    style=ButtonStyle.green,
                    label="📝 3️⃣",
                    custom_id = "3"
                )
            ]
            
            if preset_update:
                util_buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="📝4️⃣",
                        custom_id="4"
                    )
                )
                util_buttons.append(
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="📝5️⃣",
                        custom_id="5"
                    )
                )
            util_action_row = manage_components.create_actionrow(*util_buttons)
            components = [util_action_row]
            await ctx.send(embed=embedVar,components=[util_action_row])

            
            def check(button_ctx):
                return button_ctx.author == ctx.author

            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[util_action_row], timeout=120,check=check)

                if button_ctx.custom_id == "0":
                    await button_ctx.send(f"{ctx.author.mention}, No change has been made")
                    return
                elif button_ctx.custom_id == "1":
                    response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.0.CARD' :str(current_card), 'DECK.0.TITLE': str(current_title),'DECK.0.ARM': str(current_arm), 'DECK.0.PET': str(current_pet)}})
                    if response:
                        await button_ctx.send("📝 1️⃣| Preset Updated!")
                        return
                elif button_ctx.custom_id == "2":
                    response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.1.CARD' :str(current_card), 'DECK.1.TITLE': str(current_title),'DECK.1.ARM': str(current_arm), 'DECK.1.PET': str(current_pet)}})
                    if response:
                        await button_ctx.send("📝 2️⃣| Preset Updated!")
                        return
                elif button_ctx.custom_id == "3":
                    response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.2.CARD' :str(current_card), 'DECK.2.TITLE': str(current_title),'DECK.2.ARM': str(current_arm), 'DECK.2.PET': str(current_pet)}})
                    if response:
                        await button_ctx.send("📝 3️⃣| Preset Updated!")
                        return
                elif button_ctx.custom_id == "4":
                    response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.3.CARD' :str(current_card), 'DECK.3.TITLE': str(current_title),'DECK.3.ARM': str(current_arm), 'DECK.3.PET': str(current_pet)}})
                    if response:
                        await button_ctx.send("📝 4️⃣| Preset Updated!")
                        return
                elif button_ctx.custom_id == "5":
                    response = db.updateVaultNoFilter(vault_query, {'$set': {'DECK.4.CARD' :str(current_card), 'DECK.4.TITLE': str(current_title),'DECK.4.ARM': str(current_arm), 'DECK.4.PET': str(current_pet)}})
                    if response:
                        await button_ctx.send("📝 5️⃣| Preset Updated!")
                        return
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", hidden=True)
            except Exception as ex:
                trace = []
                tb = ex.__traceback__
                while tb is not None:
                    trace.append({
                        "filename": tb.tb_frame.f_code.co_filename,
                        "name": tb.tb_frame.f_code.co_name,
                        "lineno": tb.tb_lineno
                    })
                    tb = tb.tb_next
                print(str({
                    'type': type(ex).__name__,
                    'message': str(ex),
                    'trace': trace
                }))
                await ctx.send("Preset Issue Seek support.", hidden=True)
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        await ctx.send("Preset Issue Seek support.", hidden=True)

async def menushop(self, ctx):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    try:
        all_universes = db.queryAllUniverse()
        user = db.queryUser({'DID': str(ctx.author.id)})
        storage_allowed_amount = user['STORAGE_TYPE'] * 15
        guild_buff = "NULL"
        if user["TEAM"] != "PCG":
            guild_info = db.queryTeam({"TEAM_NAME": str(user["TEAM"].lower())})
            guild_buff = guild_info["ACTIVE_GUILD_BUFF"]

        if user['LEVEL'] < 1:
            await ctx.send("🔓 Unlock the Shop by completing Floor 0 of the 🌑 Abyss! Use /solo to enter the abyss.")
            return

        completed_tales = user['CROWN_TALES']
        completed_dungeons = user['DUNGEONS']
        available_universes = []
        riftShopOpen = False
        shopName = ':shopping_cart: Shop'
        if user['RIFT'] == 1 or guild_buff == "Rift":
            riftShopOpen = True
            shopName = ':crystal_ball: Rift Shop'

        if riftShopOpen:
            close_rift = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'RIFT': 0}})

            
        if riftShopOpen:    
            for uni in all_universes:
                if uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                    available_universes.append(uni)
        else:
            for uni in all_universes:
                if uni['TIER'] != 9 and uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                    available_universes.append(uni)
        
        vault_query = {'DID' : str(ctx.author.id)}
        vault = db.altQueryVault(vault_query)
        storage_amount = len(vault['STORAGE'])
        hand_length = len(vault['CARDS'])
        current_titles = vault['TITLES']
        current_cards = vault['CARDS']
        current_arms = []
        for arm in vault['ARMS']:
            current_arms.append(arm['ARM'])

        owned_card_levels_list = []
        for c in vault['CARD_LEVELS']:
            owned_card_levels_list.append(c['CARD'])

        owned_destinies = []
        for destiny in vault['DESTINY']:
            owned_destinies.append(destiny['NAME'])
            
        card_message = ""
        title_message = ""
        arm_message = ""
        
        if len(current_cards) >= 25:
            card_message = "🎴 *25 Full*"
        else:
            card_message = f"🎴 {len(current_cards)}"
            
        if len(current_titles) >= 25:
            title_message = "🎗️ *25 Full*"
        else:
            title_message = f"🎗️ {len(current_titles)}"
            
        if len(current_arms) >= 25:
            arm_message = "🦾 *25 Full*"
        else:
            arm_message = f"🦾 {len(current_arms)}"


        balance = vault['BALANCE']
        icon = ":coin:"
        if balance >= 150000:
            icon = ":money_with_wings:"
        elif balance >=100000:
            icon = ":moneybag:"
        elif balance >= 50000:
            icon = ":dollar:"


        embed_list = []
        for universe in available_universes:
            universe_name = universe['TITLE']
            universe_image = universe['PATH']
            adjusted_prices = price_adjuster(15000, universe_name, completed_tales, completed_dungeons)
            embedVar = discord.Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
            *Welcome {ctx.author.mention}! {adjusted_prices['MESSAGE']}
            You have {icon}{'{:,}'.format(balance)} coins!*
            {card_message} | {title_message} | {arm_message}
            
            🎗️ **Title:** Title Purchase for 💵 {'{:,}'.format(adjusted_prices['TITLE_PRICE'])}
            🦾 **Arm:** Arm Purchase for 💵 {'{:,}'.format(adjusted_prices['ARM_PRICE'])}
            1️⃣ **1-3 Tier Card:** for 💵 {'{:,}'.format(adjusted_prices['C1'])}
            2️⃣ **3-5 Tier Card:** for 💰 {'{:,}'.format(adjusted_prices['C2'])}
            3️⃣ **5-7 Tier Card:** for 💸 {'{:,}'.format(adjusted_prices['C3'])}
            """), colour=0x7289da)
            embedVar.set_image(url=universe_image)
            #embedVar.set_thumbnail(url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236723/PCG%20LOGOS%20AND%20RESOURCES/Party_Chat_Shop.png")
            embed_list.append(embedVar)

        
        # Pull all cards that don't require tournaments
        # resp = db.queryShopCards()

        buttons = [
            manage_components.create_button(style=3, label="🎗️", custom_id="title"),
            manage_components.create_button(style=1, label="🦾", custom_id="arm"),
            manage_components.create_button(style=2, label="1️⃣", custom_id="t1card"),
            manage_components.create_button(style=2, label="2️⃣", custom_id="t2card"),
            manage_components.create_button(style=2, label="3️⃣", custom_id="t3card"),
        ]

        custom_action_row = manage_components.create_actionrow(*buttons)

        async def custom_function(self, button_ctx):
            if button_ctx.author == ctx.author:
                updated_vault = db.queryVault({'DID': user['DID']})
                balance = updated_vault['BALANCE']        
                universe = str(button_ctx.origin_message.embeds[0].title)
                
                if button_ctx.custom_id == "title":
                    updated_vault = db.queryVault({'DID': user['DID']})
                    current_titles = updated_vault['TITLES']
                    price = price_adjuster(50000, universe, completed_tales, completed_dungeons)['TITLE_PRICE']
                    bless_amount = price
                    # if len(current_titles) >=25:
                        # await button_ctx.send("You have max amount of Titles. Transaction cancelled.")
                        # self.stop = True
                        # return

                    if price > balance:
                        await button_ctx.send("Insufficent funds.")
                        self.stop = True
                        return
                    list_of_titles =[x for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
                    if not list_of_titles:
                        await button_ctx.send("There are no titles available for purchase in this range.")
                        self.stop = True
                        return

                    selection_length = len(list(list_of_titles)) - 1
                    if selection_length ==0:
                        title = list_of_titles[0]
                    else:
                        selection = random.randint(0,selection_length)
                        title = list_of_titles[selection]  
                    if title['TITLE'] in current_titles:                 
                        bless_amount = price
                        bless_reduction = 0
                        if universe_name in completed_tales:
                            bless_reduction = bless_amount * .25
                            bless_amount = round((bless_amount - bless_reduction)/2)
                        if universe_name in completed_dungeons:
                            bless_reduction = bless_amount * .50
                            bless_amount = round((bless_amount - bless_reduction)/2)
                        else: 
                            bless_amount = round(bless_amount /2)
                            
                    response = await crown_utilities.store_drop_card(str(ctx.author.id), title['TITLE'], universe_name, updated_vault, "Titles_NoDestinies", bless_amount, bless_amount, "Purchase", True, int(price), "titles")
                    await button_ctx.send(response)
                    #     await button_ctx.send(f"You already own **{title['TITLE']}**. You get a :coin:**{'{:,}'.format(bless_amount)}** refund!") 
                    #     await crown_utilities.curse(bless_amount, str(ctx.author.id))
                    # else:
                    #     response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})   
                    #     await crown_utilities.curse(price, str(ctx.author.id))
                    #     await button_ctx.send(f"You purchased **{title['TITLE']}**.")


                elif button_ctx.custom_id == "arm":
                    updated_vault = db.queryVault({'DID': user['DID']})
                    current_arms = []
                    for arm in updated_vault['ARMS']:
                        current_arms.append(arm['ARM'])
                    price = price_adjuster(25000, universe, completed_tales, completed_dungeons)['ARM_PRICE']
                    # if len(current_arms) >=25:
                    #     await button_ctx.send("You have max amount of Arms. Transaction cancelled.")
                    #     self.stop = True
                    #     return
                    if price > balance:
                        await button_ctx.send("Insufficent funds.")
                        self.stop = True
                        return
                    list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
                    if not list_of_arms:
                        await button_ctx.send("There are no arms available for purchase in this range.")
                        self.stop = True
                        return

                    selection_length = len(list(list_of_arms)) - 1

                    if selection_length ==0:
                        arm = list_of_arms[0]
                    else:
                        selection = random.randint(0,selection_length)
                        arm = list_of_arms[selection]['ARM']
                    response = await crown_utilities.store_drop_card(str(ctx.author.id), arm, universe_name, updated_vault, 25, price, price, "Purchase", True, int(price), "arms")
                    await button_ctx.send(response)
                    
                    # if arm not in current_arms:
                    #     response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 25}}})
                    #     await crown_utilities.curse(price, str(ctx.author.id))
                    #     await button_ctx.send(f"You purchased **{arm}**.")
                    # else:
                    #     update_query = {'$inc': {'ARMS.$[type].' + 'DUR': 10}}
                    #     filter_query = [{'type.' + "ARM": str(arm)}]
                    #     resp = db.updateVault(vault_query, update_query, filter_query)
                    #     await crown_utilities.curse(price, str(ctx.author.id))
                    #     await button_ctx.send(f"You purchased **{arm}**. Increased durability for the arm by 10 as you already own it.")


                elif button_ctx.custom_id == "t1card":
                    price = price_adjuster(100000, universe, completed_tales, completed_dungeons)['C1']
                    acceptable = [1,2,3]
                    if price > balance:
                        await button_ctx.send("Insufficent funds.")
                        self.stop = True
                        return
                    list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                    if not list_of_cards:
                        await button_ctx.send("There are no cards available for purchase in this range.")
                        self.stop = True
                        return

                    selection_length = len(list(list_of_cards)) - 1
                    if selection_length ==0:
                        card = list_of_cards[0]
                    else:
                        selection = random.randint(0,selection_length)
                        card = list_of_cards[selection]
                    card_name = card['NAME']
                    tier = 0

                    response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
                    await button_ctx.send(response)


                elif button_ctx.custom_id == "t2card":
                    price = price_adjuster(450000, universe, completed_tales, completed_dungeons)['C2']
                    acceptable = [3,4,5]
                    if price > balance:
                        await button_ctx.send("Insufficent funds.")
                        self.stop = True
                        return
                    list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                    
                    if not list_of_cards:
                        await button_ctx.send("There are no cards available for purchase in this range.")
                        self.stop = True
                        return
                    
                    selection_length = len(list(list_of_cards)) - 1

                    if selection_length ==0:
                        card = list_of_cards[0]
                    else:
                        selection = random.randint(0,selection_length)
                        card = list_of_cards[selection]
                    card_name = card['NAME']
                    tier = 0
                    
                    response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
                    await button_ctx.send(response)


                elif button_ctx.custom_id == "t3card":
                    price = price_adjuster(6000000, universe, completed_tales, completed_dungeons)['C3']
                    acceptable = [5,6,7]
                    if price > balance:
                        await button_ctx.send("Insufficent funds.")
                        self.stop = True
                        return
                    card_list_response = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                    if not card_list_response:
                        await button_ctx.send("There are no cards available for purchase in this range.")
                        self.stop = True
                        return
                    else:
                        list_of_cards = []
                        for card in card_list_response:
                            if card['AVAILABLE'] and not card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
                                list_of_cards.append(card)


                    if not list_of_cards:
                        await button_ctx.send("There are no cards available for purchase in this range.")
                        self.stop = True
                        return

                    selection_length = len(list(list_of_cards)) - 1
                    if selection_length ==0:
                        card = list_of_cards[0]
                    else:
                        selection = random.randint(0,selection_length)
                        card = list_of_cards[selection]
                    card_name = card['NAME']
                    tier = 0

                    response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
                    await button_ctx.send(response)

            else:
                await ctx.send("This is not your Shop.")
        await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
            custom_action_row,
            custom_function,
        ]).run()
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))


async def menucraft(self, ctx):
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    # Craft with Gems
    # Craft Universe Heart, Universe Soul, Skin Box
    poke_universes = ['Kanto Region', 'Johto Region', 'Hoenn Region', 'Sinnoh Region']
    try:
        gems = 0
        all_universes = db.queryAllUniverse()
        user = db.queryUser({'DID': str(ctx.author.id)})
        guild_info = db.queryTeam({"TEAM_NAME": str(user["TEAM"].lower())})
        guild_buff = guild_info["ACTIVE_GUILD_BUFF"]
        completed_dungeons = user['DUNGEONS']
        completed_tales = user['CROWN_TALES']
        card_info = db.queryCard({"NAME": user['CARD']})
        destiny_alert_message = f"No Skins or Destinies available for {card_info['NAME']}"
        destiny_alert = False
        # if user['LEVEL'] < 9:
        #     await ctx.send("🔓 Unlock Crafting by completeing Floor 8 of the 🌑 Abyss! Use /solo to enter the abyss.")
        #     return

        #skin_alert_message = f"No Skins for {card_info['NAME']}"
        
        #skin_alert_message = f"No Skins for {card_info['NAME']}"
        available_universes = []
        riftShopOpen = False
        shopName = ':shopping_cart: Shop'
        if user['RIFT'] == 1 or guild_buff == "Rift":
            riftShopOpen = True
            shopName = ':crystal_ball: Rift Shop'
            
        if riftShopOpen:    
            for uni in all_universes:
                if uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                    available_universes.append(uni)
        else:
            for uni in all_universes:
                if uni['TIER'] != 9 and uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
                    available_universes.append(uni)
        
        vault_query = {'DID' : str(ctx.author.id)}
        vault = db.altQueryVault(vault_query)
        current_cards = vault['CARDS']
        owned_card_levels_list = []
        for c in vault['CARD_LEVELS']:
            owned_card_levels_list.append(c['CARD'])
            
        #Card skin query 
        list_of_card_skins = False
        skin_alert = False
        card_skin_message = "No Skins"
        new_skin_list = []
        
        list_of_card_skins = [x for x in db.queryAllCardsBasedOnUniverse({'SKIN_FOR' : card_info['NAME']})]
        
        if list_of_card_skins: 
            for skin in list_of_card_skins:
                
                if skin['NAME'] not in current_cards and skin['SKIN_FOR'] == user['CARD']:
                    new_skin_list.append(skin)
                    card_skin_message = f" {card_info['UNIVERSE']} Skins Available!"
                    skin_alert = True
        
            
            

        owned_destinies = []
        for destiny in vault['DESTINY']:
            owned_destinies.append(destiny['NAME'])
            d_card = ' '.join(destiny['USE_CARDS'])
            d_card_info = db.queryCard({"NAME": str(d_card)})
            if card_info['NAME'] in destiny['USE_CARDS'] or card_info['SKIN_FOR'] in d_card_info['NAME']:
                #destiny_alert_message = f"{card_info['UNIVERSE']} Destinies Availble"
                destiny_alert = True
        if len(owned_destinies) >= 1:
            destiny_Alert = True
        
                
        if skin_alert == True and destiny_alert ==True:
            destiny_alert_message = f"{card_info['NAME']} Skins and Destinies Available!"
        elif skin_alert == True:
            destiny_alert_message = f"{card_info['NAME']} Skins Available!"
        elif destiny_alert == True:
            destiny_alert_message = f"{card_info['NAME']} Destinies Available!"
        
                
        embed_list = []
        for universe in available_universes:
            universe_name = universe['TITLE']
            universe_image = universe['PATH']
            universe_heart = False
            universe_soul = False
            gems = 0
            for uni in vault['GEMS']:
                if uni['UNIVERSE'] == universe_name:
                    gems = uni['GEMS']
                    universe_heart = uni['UNIVERSE_HEART']
                    universe_soul = uni['UNIVERSE_SOUL']
            heart_message = "Cannot Afford"
            soul_message = "Cannot Afford"
            destiny_message = "Cannot Afford"
            craft_card_message = "Cannot Afford"
            if universe_heart:
                heart_message = "Owned"
            elif gems >= 1000000:
                heart_message = "Craftable"
            if universe_soul:
                soul_message = "Owned"
            elif gems >= 500000:
                soul_message = "Craftable"
            if gems >= 1500000 and universe_name == card_info['UNIVERSE'] and destiny_alert:
                destiny_message = f"Destinies available"
            elif gems >= 1500000 and destiny_alert:
                destiny_message = f"{universe_name} Destinies available"
            elif gems >= 1500000:
                destiny_message = f"Affordable!"
            if gems >= 6000000:
                craft_card_message = f"Affordable!"
            if universe_name != card_info['UNIVERSE'] and skin_alert:
                card_skin_message = f"{card_info['UNIVERSE']} Skin Available!"
                if card_info['UNIVERSE'] in poke_universes:
                    card_skin_message = f"Regional Pokemon Skins Available!"
                
            embedVar = discord.Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
            Welcome {ctx.author.mention}!
            You have 💎 *{'{:,}'.format(gems)}* **{universe_name}** gems !
            
            Equipped Card:  **{card_info['NAME']}** *{card_info['UNIVERSE']}*
            *{destiny_alert_message}*
            
            💟 **Universe Heart:** 💎 5,000,000 *{heart_message}*
            *Grants ability to level past 200*

            🌹 **Universe Soul:** 💎 5,000,000 *{soul_message}*
            *Grants double exp in this Universe*

            ✨ **Destiny Line:** 💎 1,500,000 *{destiny_message}*
            *Grants wins for a Destiny Line*
            
            🃏 **Card Skins:** 💎 2,000,000 *{card_skin_message}*
            *Grants Card Skin*

            ✨🎴 **Craft Card:** 💎 15,000,000 *{craft_card_message}*
            *Craft a random dungeon card from this Universe*

            """), colour=0x7289da)
            embedVar.set_image(url=universe_image)
            embed_list.append(embedVar)

    
        buttons = [
            manage_components.create_button(style=3, label="💟", custom_id="UNIVERSE_HEART"),
            manage_components.create_button(style=1, label="🌹", custom_id="UNIVERSE_SOUL"),
            manage_components.create_button(style=1, label="✨", custom_id="Destiny"),
            manage_components.create_button(style=1, label="🃏", custom_id="Skin"),
            manage_components.create_button(style=1, label="🎴", custom_id="Card")
        ]

        custom_action_row = manage_components.create_actionrow(*buttons)

        async def custom_function(self, button_ctx):
            if button_ctx.author == ctx.author:
                universe = str(button_ctx.origin_message.embeds[0].title)
                if button_ctx.custom_id == "UNIVERSE_HEART":
                    price = 5000000
                    response = await craft_adjuster(self, ctx, vault, universe, price, button_ctx.custom_id, completed_tales, None)
                    if response['SUCCESS']:
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True
                    else:
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True                           

                if button_ctx.custom_id == "UNIVERSE_SOUL":
                    price = 5000000
                    response = await craft_adjuster(self, ctx, vault, universe, price, button_ctx.custom_id, None, completed_tales)
                    if response['SUCCESS']:
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True
                    else:
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True
                if button_ctx.custom_id == "Destiny":
                    await button_ctx.defer(ignore=True)
                    price = 1500000
                    response = await craft_adjuster(self, ctx, vault, universe, price, card_info, None, completed_tales)
                    await button_ctx.send(f"{response['MESSAGE']}")
                    self.stop = True
                if button_ctx.custom_id == "Skin":
                    await button_ctx.defer(ignore=True)
                    price = 2000000
                    response = await craft_adjuster(self, ctx, vault, universe, price, card_info, new_skin_list, completed_tales)
                    await button_ctx.send(f"{response['MESSAGE']}")
                    self.stop = True
                if button_ctx.custom_id == "Card":
                    await button_ctx.defer(ignore=True)
                    price = 15000000
                    response = await craft_adjuster(self, ctx, vault, universe, price, "Card", new_skin_list, completed_tales)
                    await button_ctx.send(f"{response['MESSAGE']}")
                    self.stop = True                       
                
            else:
                await ctx.send("This is not your Craft.")

        await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
            custom_action_row,
            custom_function,
        ]).run()
    except Exception as ex:
        trace = []
        tb = ex.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        print(str({
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))


def setup(bot):
    bot.add_cog(Profile(bot))