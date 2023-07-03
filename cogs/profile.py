import emoji
from pymongo import response
import asyncio
import crown_utilities
import db
import classes as data #
import messages as m
import numpy as np
import help_commands as h
import unique_traits as ut
from PIL import Image, ImageFont, ImageDraw
import requests
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.arm_class import Arm
from .classes.summon_class import Summon
from .classes.player_class import Player
from .classes.battle_class  import Battle
from .game_modes import enhancer_mapping, title_enhancer_mapping, enhancer_suffix_mapping, title_enhancer_suffix_mapping, passive_enhancer_suffix_mapping
import random
import textwrap
import uuid

import destiny as d
import random
from .classes.custom_paginator import CustomPaginator
from interactions.ext.paginators import Paginator
from interactions import Client, ActionRow, Button, ButtonStyle, File, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension


emojis = ['👍', '👎']

class Profile(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Profile Cog is ready!')


    @slash_command(description="Delete your account")
    async def deleteaccount(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        user = str(ctx.author)
        query = {'DID': str(ctx.author.id)}
        user_is_validated = db.queryUser(query)
        if user_is_validated:
            accept_buttons = [
                Button(
                    style=ButtonStyle.GREEN,
                    label="Yes",
                    custom_id="yes"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="No",
                    custom_id="no"
                )
            ]
            accept_buttons_action_row = ActionRow(*accept_buttons)

            team = db.queryTeam({'TEAM_NAME': user_is_validated['TEAM'].lower()})

            await ctx.send(f"{ctx.author.mention}, are you sure you want to delete your account? " + "\n" + "All of your wins, purchases and other earnings will be removed from the system and can not be recovered. ", ephemeral=True, components=[accept_buttons_action_row])

            def check(button_ctx):
                return button_ctx.author == ctx.author

            try:
                button_ctx  = await self.bot.wait_for_component(components=[accept_buttons_action_row], timeout=120,check=check)

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
            await ctx.send("You aren't registered.", ephemeral=True)


    @slash_command(description="main menu where all your important game items and builds are",
                    options=[
                        SlashCommandOption(
                            name="selection",
                            description="select an option to continue",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="🎴 My Cards",
                                    value="cards",
                                ),
                                SlashCommandChoice(
                                    name="🎗️ My Titles",
                                    value="titles",
                                ),
                                SlashCommandChoice(
                                    name="🦾 My Arms",
                                    value="arms",
                                ),
                                SlashCommandChoice(
                                    name="🧬 My Summons",
                                    value="summons",
                                ),
                                SlashCommandChoice(
                                    name="⚔️ Current Build",
                                    value="build",
                                ),
                                SlashCommandChoice(
                                    name="💼 Check Card Storage",
                                    value="storage",
                                ),
                                SlashCommandChoice(
                                    name="🖨️ Draw Card From Storage",
                                    value="draw",
                                ),
                                SlashCommandChoice(
                                    name="✨ View Destinies",
                                    value="destinies",
                                ),
                                SlashCommandChoice(
                                    name="📜 Start Quests",
                                    value="quests",
                                ),
                                SlashCommandChoice(
                                    name="💰 My Money",
                                    value="balance",
                                ),
                                SlashCommandChoice(
                                    name="💎 Gem Bag",
                                    value="gems"
                                ),
                                SlashCommandChoice(
                                    name="🪔 Essence",
                                    value="essence",
                                ),
                                SlashCommandChoice(
                                    name="📤 Load Presets",
                                    value="presets",
                                ),
                                SlashCommandChoice(
                                    name="📥 Save Current Preset",
                                    value="savepreset",
                                ),
                                SlashCommandChoice(
                                    name="🛍️ Open the Shop",
                                    value="shop",
                                ),
                                SlashCommandChoice(
                                    name="⚒️ Visit the Blacksmith",
                                    value="blacksmith",
                                ),
                                SlashCommandChoice(
                                    name="💎 Start Crafting",
                                    value="craft",
                                ),

                            ]
                        )
                    ]
        )
    async def menu(self, ctx, selection):
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

            
    @slash_command(description="View your or a players current build", options=[
        SlashCommandOption(
            name="player",
            description="Select a player to view their build",
            type=OptionType.USER,
            required=False
        )
    ])
    async def build(self, ctx, player = None):
        try:
            await ctx.defer()
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return
            if player:
                uid = player.id
            else:
                uid = ctx.author.id
            query = {'DID': str(uid)}
            d = db.queryUser(query)
            card = db.queryCard({'NAME':str(d['CARD'])})
            title = db.queryTitle({'TITLE': str(d['TITLE'])})
            arm = db.queryArm({'ARM': str(d['ARM'])})
            if not all([card, title, arm, d]):
                # Handle error if one of the database calls fails
                return "Error: One or more of the required data is not available."

            if card:
                try:
                    c = crown_utilities.create_card_from_data(card)
                    t = crown_utilities.create_title_from_data(title)
                    a = crown_utilities.create_arm_from_data(arm)
                    player = crown_utilities.create_player_from_data(d)

                    title_message = "\n".join(t.title_messages)
                    
                    durability = a.set_durability(player.equipped_arm, player.arms)
                    
                    c.set_card_level_buffs(player.card_levels)
                    c.set_affinity_message()
                    c.set_arm_config(a.passive_type, a.name, a.passive_value, a.element)
                    c.set_evasion_message(player)
                    c.set_card_level_icon(player)

                    x = 0.0999
                    y = 1.25
                    lvl_req = round((float(c.card_lvl)/x)**y)
                    
                    player.set_talisman_message()
                    player.setsummon_messages()
                    
                    a.set_arm_message(player.performance, c.universe)
                    t.set_title_message(player.performance, c.universe)
                    
                    
                    has_universe_heart = False
                    has_universe_soul = False
                    pokemon_uni =crown_utilities.pokemon_universes
                    
                    if c.universe != "n/a":
                        for gems in player.gems:
                            if gems['UNIVERSE'] == c.universe and gems['UNIVERSE_HEART']:
                                has_universe_heart = True
                            if gems['UNIVERSE'] == c.universe and gems['UNIVERSE_SOUL']:
                                has_universe_soul = True
                    
                    trebirth_message = f"_⚔️Tales: +0_"
                    drebirth_message = f"_🔥Dungeon: +0_"
                    trebirthBonus = (player.rebirth + (player.prestige * 10) + 25)
                    drebirthBonus = ((player.rebirth + 1) * ((player.prestige * 10) + 100))
                    if player.prestige > 0:
                        trebirthBonus = trebirthBonus * player.prestige
                        drebirthBonus = drebirthBonus * player.prestige
                    if player.rebirth > 0:
                        trebirth_message = f"_⚔️Tales: {trebirthBonus}xp_"
                        drebirth_message = f"_🔥Dungeon: {drebirthBonus}xp_"
                    if has_universe_soul:
                        trebirthBonus = (player.rebirth + (player.prestige * 10) + 25) * 4
                        drebirthBonus = ((player.rebirth + 1) * ((player.prestige * 10) + 100)) * 4
                        trebirth_message = f"_🌹⚔️Tales: {trebirthBonus}xp_"
                        drebirth_message = f"_🌹🔥Dungeon: {drebirthBonus}xp_"

                    level_up_message = lvl_req - c.card_exp
                    if lvl_req - c.card_exp <= 0:
                        level_up_message = "🎆 Battle To Level Up!"
                    if c.card_lvl >= 1000:
                        level_up_message = "👑 | Max Level!!"

                    if player.performance:
                        embedVar = Embed(title=f"{c.level_icon} | {c.card_lvl} {c.name}".format(self), description=textwrap.dedent(f"""\
                        {crown_utilities.class_emojis[c.card_class]} | **{c.class_message}**
                        🀄 | **{c.tier}**
                        ❤️ | **{c.max_health}**
                        🗡️ | **{c.attack}**
                        🛡️ | **{c.defense}**
                        🏃 | **{c.evasion_message}**
                        🎗️ | **{t.name}**
                        **{title_message}**
                        **{a.arm_message}**
                        **{player.talisman_message}**
                        {player.summon_power_message}
                        {player.summon_lvl_message}

                        {c.move1_emoji} | **{c.move1}:** {c.move1ap}
                        {c.move2_emoji} | **{c.move2}:** {c.move2ap}
                        {c.move3_emoji} | **{c.move3}:** {c.move3ap}
                        🦠 | **{c.move4}:** {c.move4enh} {c.move4ap}{enhancer_suffix_mapping[c.move4enh]}

                        🩸 | **{c.passive_name}:** {c.passive_type} {c.passive_num} {passive_enhancer_suffix_mapping[c.passive_type]}
                        """),color=000000)
                        embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                        embedVar.set_image(url="attachment://image.png")
                        if c.card_lvl < 1000:
                            embedVar.set_footer(text=f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}")
                        else:
                            embedVar.set_footer(text=f"{level_up_message}")
                        embedVar.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
                        
                        await ctx.send(embed=embedVar)
                    
                    else:
                        image_binary = c.showcard("non-battle", a, t, 0, 0)
                        image_binary.seek(0)
                        card_file = File(file_name="image.png", file=image_binary)

                        embedVar = Embed(title=f"".format(self), color=000000)
                        embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                        embedVar.add_field(name=f"__Title Effects__\n🎗️ {t.name}", value=f"{title_message}", inline=False)
                        embedVar.set_image(url="attachment://image.png")
                        embedVar.set_author(name=textwrap.dedent(f"""\
                        Equipment
                        {a.arm_message}
                        {player.talisman_message}
                        {player.summon_power_message}
                        {player.summon_lvl_message}
                        
                        Passives
                        🩸 | {c.passive_name}      
                        🏃 | {c.evasion_message}
                        """))
                        embedVar.set_thumbnail(url=ctx.author.avatar_url)
                        if c.card_lvl < 1000:
                            embedVar.set_footer(text=f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}\n♾️ | {c.set_trait_message()}")
                        else:
                            embedVar.set_footer(text=f"{level_up_message}\n♾️ | {c.set_trait_message()}")
                        
                        await ctx.send(file=card_file, embed=embedVar)
                        image_binary.close()
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
                    embed = Embed(title="Build Error", description="There was an error with your build command. Please try again later.", color=000000)
                    await ctx.send(embed=embed)
                    return
            else:
                embed = Embed(title="Build Error", description="You do not have a card registered. Please register a card before using /register.", color=000000)
                await ctx.send(embed=embed)
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
            embed = Embed(title="Build Error", description="There was an error with your build command. Please try again later.", color=000000)
            await ctx.send(embed=embed)

    
    @slash_command(description="Infuse Elemental Essence into Talisman's for aid",
                    options=[
                        SlashCommandOption(
                            name="selection",
                            description="select an option to continue",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="👊 Physical",
                                    value="PHYSICAL",
                                ),
                                SlashCommandChoice(
                                    name="🔥 Fire",
                                    value="FIRE",
                                ),
                                SlashCommandChoice(
                                    name="❄️ Ice",
                                    value="ICE",
                                ),
                                SlashCommandChoice(
                                    name="💧 Water",
                                    value="WATER",
                                ),
                                SlashCommandChoice(
                                    name="⛰️ Earth",
                                    value="EARTH",
                                ),
                                SlashCommandChoice(
                                    name="⚡️ Electric",
                                    value="ELECTRIC",
                                ),
                                SlashCommandChoice(
                                    name="🌪️ Wind",
                                    value="WIND",
                                ),
                                SlashCommandChoice(
                                    name="🔮 Psychic",
                                    value="PSYCHIC",
                                ),
                                SlashCommandChoice(
                                    name="☠️ Death",
                                    value="DEATH",
                                ),
                                SlashCommandChoice(
                                    name="❤️‍🔥 Life",
                                    value="LIFE"
                                ),
                                SlashCommandChoice(
                                    name="🌕 Light",
                                    value="LIGHT",
                                ),
                                SlashCommandChoice(
                                    name="🌑 Dark",
                                    value="DARK",
                                ),
                                SlashCommandChoice(
                                    name="🧪 Poison",
                                    value="POISON",
                                ),
                                SlashCommandChoice(
                                    name="🏹 Ranged",
                                    value="RANGED",
                                ),
                                SlashCommandChoice(
                                    name="🧿 Spirit",
                                    value="SPIRIT",
                                ),
                                SlashCommandChoice(
                                    name="♻️ Recoil",
                                    value="RECOIL",
                                ),
                                SlashCommandChoice(
                                    name="⌛ Time",
                                    value="TIME",
                                ),
                                SlashCommandChoice(
                                    name="🅱️ Bleed",
                                    value="BLEED",
                                ),
                                SlashCommandChoice(
                                    name="🪐 Gravity",
                                    value="GRAVITY",
                                ),
                            ]
                        )
                    ]
        )
    async def attune(self, ctx, selection):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return
            query = {'DID': str(ctx.author.id)}
            user = db.queryUser(query)
            talismans = user["TALISMANS"]
            essence_list = user["ESSENCE"]
            if crown_utilities.is_maxed_out(talismans):
                embed = Embed(title="📿 Talisman", description="You have maxed out your talisman's. You can't infuse any more essence into them.", color=0x00ff00)
                await ctx.send(embed=embed)
            else:
                response = crown_utilities.essence_cost(user, selection)
                embed = Embed(title="📿 Talisman", description=response, color=0x00ff00)
                await ctx.send(embed=embed)
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
            embed = Embed(title="📿 Talisman", description="There was an error with your request. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0x00ff00)
            await ctx.send(embed=embed)
            return


    @slash_command(description="View your talismen that are in storage")
    async def talismans(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            user = db.queryUser({"DID": str(ctx.author.id)})
            talismans = user["TALISMANS"]
           
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
                    embedVar = Embed(title= f"{name}", description=textwrap.dedent(f"""\
                    🔅 Element: {emoji} **{name.title()}**
                    ⚒️ {durability}
                    *{name} damage will ignore enemy Affinities.*
                    {m}
                    """), color=0x7289da)
                    embed_list.append(embedVar)

                paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Equip", "Unequip"], paginator_type="Talisman")
                paginator.show_select_menu = True
                await paginator.send(ctx)
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


    @slash_command(description="View Card, Title and Arm Storage",
                    options=[
                        SlashCommandOption(
                            name="mode",
                            description="Card: View Card Storage, Title: View Title Storage, Arm: View Arm Storage",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="🎴 Card Storage",
                                    value="card"
                                ),
                                SlashCommandChoice(
                                    name="🎗️ Title Storage",
                                    value="title"
                                ),
                                SlashCommandChoice(
                                    name="🦾 Arm Storage",
                                    value="arm"
                                ),
                            ]
                        )
                    ]
        )
    async def storage(self, ctx, mode):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            storage_allowed_amount = user['STORAGE_TYPE'] * 15
            player = crown_utilities.create_player_from_data(user)
            if mode == "card":
                if not user['STORAGE']:
                    embed = Embed(title="Card Storage", description="Your Card storage is empty.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return

                list_of_cards = db.querySpecificCards(player.storage)
                cards = [x for x in list_of_cards]
                all_cards = []
                embed_list = []
                
                sorted_card_list = sorted(cards, key=lambda card: card["NAME"])
                for index, card in enumerate(sorted_card_list):
                    c = crown_utilities.create_card_from_data(card)
                    c.set_card_level_icon(player)
                    index = player.storage.index(c.name)
                    all_cards.append(f"[{str(index)}] {c.universe_crest} : 🀄 **{c.tier}** **{c.name}** [{c.class_emoji}] {c.move1_emoji} {c.move2_emoji} {c.move3_emoji}\n{c.drop_emoji} **{c.level_icon}**: {str(c.card_lvl)} ❤️ {c.health} 🗡️ {c.attack} 🛡️ {c.defense}\n")
                
                for i in range(0, len(all_cards), 10):
                    sublist = all_cards[i:i+10]
                    embedVar = Embed(title=f"💼 {player.disname}'s Card Storage", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"{len(all_cards)} Total Cards\n{str(storage_allowed_amount - len(user['STORAGE']))} Storage Available")
                    embed_list.append(embedVar)

                pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                await pagination.send(ctx)

            if mode == "title":
                if not player.tstorage:
                    embed = Embed(title="Title Storage", description="Your Title storage is empty.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return

                list_of_titles = db.querySpecificTitles(player.tstorage)
                titles = [x for x in list_of_titles]
                all_titles = []
                embed_list = []

                sorted_titles = sorted(titles, key=lambda title: title["TITLE"])
                for index, title in enumerate(sorted_titles):
                    title_title = title['TITLE']
                    title_show = title['UNIVERSE']
                    exclusive = title['EXCLUSIVE']
                    available = title['AVAILABLE']
                    title_passive = title['ABILITIES'][0]
                    title_passive_type = list(title_passive.keys())[0]
                    title_passive_value = list(title_passive.values())[0]

                    universe_crest = crown_utilities.crest_dict[title_show]
                    index = player.tstorage.index(title_title)
                    
                    if title_show == "Unbound":
                        emoji = "👑"
                    elif exclusive and available:
                        emoji = "🔥"
                    elif available:
                        emoji = "🎗️"
                    else:
                        emoji = "👹"   

                    all_titles.append(f"[{str(index)}] {universe_crest} {emoji} : **{title_title}**\n**🦠 {title_passive_type}**:  *{title_passive_value}*\n")

                for i in range(0, len(all_titles), 10):
                    sublist = all_titles[i:i+10]           
                    embedVar = Embed(title=f"💼 {player.disname}'s Title Storage", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(
                        text=f"{len(all_titles)} Total Titles\n{str(storage_allowed_amount - len(player.tstorage))} Storage Available")
                    embed_list.append(embedVar)

                pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                await pagination.send(ctx)

            if mode == "arm":
                if not user['ASTORAGE']:
                    embed = Embed(title="Arm Storage", description="Your Arm storage is empty.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return

                storage_card_names = []
                for name in user['ASTORAGE']:
                    storage_card_names.append(name['ARM'])
                list_of_arms = db.querySpecificArms(storage_card_names)
                arms = [x for x in list_of_arms]
                all_arms = []
                embed_list = []

                icon = ""
                sorted_arms = sorted(arms, key=lambda arm: arm["ARM"])
                for index, arm in enumerate(sorted_arms):
                    durability = 0
                    for name in user['ASTORAGE']:
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
                    index = user['ASTORAGE'].index({'ARM': arm_name, 'DUR' : durability})

                    if arm_show == "Unbound":
                        emoji = "👑"
                    elif exclusive and available:
                        emoji = "🔥"
                    elif available:
                        emoji = "🦾"
                    else:
                        emoji = "👹"

                    all_arms.append(f"[{str(index)}] {universe_crest} {emoji} {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** : *{arm_passive_value}*\n")


                for i in range(0, len(all_arms), 10):
                    sublist = all_arms[i:i+10]
                    embedVar = Embed(title=f"💼 {player.disname}'s Arm Storage", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"{len(all_arms)} Total Arms\n{str(storage_allowed_amount - len(user['ASTORAGE']))} Storage Available")
                    embed_list.append(embedVar)
                    
                    pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                    await pagination.send(ctx)
            
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
            embed = Embed(title="Error", description="Something went wrong with the storage command. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)


    @slash_command(description="View all of your cards")
    async def cards(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)#Storage Update
        storage_type = d['STORAGE_TYPE']
        player = crown_utilities.create_player_from_data(d)
        try: 
            embed_list = []
            count = 0
            for card in sorted(player.cards):
                if count < 25:
                    index = player.cards.index(card)
                    resp = db.queryCard({"NAME": str(card)})
                    c = crown_utilities.create_card_from_data(resp)
                    c.set_card_level_buffs(player.card_levels)
                    c.set_affinity_message()
                    c.set_evasion_message(player)
                    c.set_card_level_icon(player)


                    embedVar = Embed(title= f"{c.name}", description=textwrap.dedent(f"""\
                    {c.drop_emoji} **[{index}]** 
                    {c.class_emoji} {c.class_message}
                    🀄 {c.tier}: {c.level_icon} {c.card_lvl}
                    ❤️ **{c.health}** 🗡️ **{c.attack}** 🛡️ **{c.defense}** 🏃 **{c.evasion_message}**
                    
                    {c.move1_emoji} **{c.move1}:** {c.move1ap}
                    {c.move2_emoji} **{c.move2}:** {c.move2ap}
                    {c.move3_emoji} **{c.move3}:** {c.move3ap}
                    🦠 **{c.move4}:** {c.move4enh} {c.move4ap}{c.move4enh_suffix}

                    🩸 **{c.passive_name}:** {c.passive_type.title()} {c.passive_num}{c.passive_suffix}
                    """), color=0x7289da)
                    embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                    embedVar.set_thumbnail(url=c.universe_image)
                    embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                    embed_list.append(embedVar)
                    count += 1
                else:
                    update_storage_query = {
                                    '$pull': {'CARDS': card},
                                    '$addToSet': {'STORAGE': card},
                                }
                    response = db.updateUserNoFilter(query, update_storage_query)

            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=['Equip', 'Dismantle', 'Trade', 'Storage'], paginator_type="Cards")
            if len(embed_list) <= 25:
                paginator.show_select_menu = True
            await paginator.send(ctx)
            
            # async def custom_function(self, button_ctx):
            #     if button_ctx.author == ctx.author:
            #         updated_vault = db.queryVault({'DID': d['DID']})
            #         sell_price = 0
            #         selected_card = str(button_ctx.origin_message.embeds[0].title)
            #         # THIS MAKES NO FUCKING SENSE ROC
            #         if button_ctx.custom_id == "Trade":
            #             card_data = db.queryCard({'NAME' : selected_card})
            #             card_name= card_data['NAME']
            #             sell_price = card_data['PRICE'] * .10
            #             mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
            #             mvalidation=False
            #             bvalidation=False
            #             item_already_in_trade=False
            #             if card_name == current_card:
            #                 await button_ctx.send("You cannot trade equipped cards.")
            #             else:
            #                 if mtrade:
            #                     if selected_card in mtrade['MCARDS']:
            #                         await ctx.send(f"{ctx.author.mention} card already in **Trade**")
            #                         item_already_in_trade=True
            #                     mvalidation=True
            #                 else:
            #                     btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
            #                     if btrade:
            #                         if selected_card in btrade['BCARDS']:
            #                             await ctx.send(f"{ctx.author.mention} card already in **Trade**")
            #                             item_already_in_trade=True
            #                         bvalidation=True
            #                     else:
            #                         await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
            #                         return
            #                 if item_already_in_trade:
            #                     trade_buttons = [
            #                         Button(
            #                             style=ButtonStyle.GREEN,
            #                             label="Yes",
            #                             custom_id="yes"
            #                         ),
            #                         Button(
            #                             style=ButtonStyle.BLUE,
            #                             label="No",
            #                             custom_id="no"
            #                         )
            #                     ]
            #                     trade_buttons_action_row = ActionRow(*trade_buttons)
            #                     await button_ctx.send(f"Would you like to remove **{selected_card}** from the **Trade**?", components=[trade_buttons_action_row])
                                
            #                     def check(button_ctx):
            #                         return button_ctx.author == ctx.author

                                
            #                     try:
            #                         button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
            #                         if button_ctx.custom_id == "no":
            #                                 await button_ctx.send("Happy Trading")
            #                                 self.stop = True
            #                         if button_ctx.custom_id == "yes":
            #                             neg_sell_price = 0 - abs(int(sell_price))
            #                             if mvalidation:
            #                                 trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
            #                                 update_query = {"$pull" : {'MCARDS': selected_card}, "$inc" : {'TAX' : int(neg_sell_price)}}
            #                                 resp = db.updateTrade(trade_query, update_query)
            #                                 await button_ctx.send("Returned.")
            #                                 self.stop = True
            #                             elif bvalidation:
            #                                 trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
            #                                 update_query = {"$pull" : {'BCARDS': selected_card}, "$inc" : {'TAX' : int(neg_sell_price)}}
            #                                 resp = db.updateTrade(trade_query, update_query)
            #                                 await button_ctx.send("Returned.")
            #                                 self.stop = True
            #                     except Exception as ex:
            #                         trace = []
            #                         tb = ex.__traceback__
            #                         while tb is not None:
            #                             trace.append({
            #                                 "filename": tb.tb_frame.f_code.co_filename,
            #                                 "name": tb.tb_frame.f_code.co_name,
            #                                 "lineno": tb.tb_lineno
            #                             })
            #                             tb = tb.tb_next
            #                         print(str({
            #                             'PLAYER': str(ctx.author),
            #                             'type': type(ex).__name__,
            #                             'message': str(ex),
            #                             'trace': trace
            #                         }))
            #                         await ctx.send("There's an issue with trading one or all of your items.")
            #                         return   
            #                 elif mvalidation == True or bvalidation ==True:    #If user is valid
            #                     sell_price = card_data['PRICE'] * .10
            #                     trade_buttons = [
            #                         Button(
            #                             style=ButtonStyle.GREEN,
            #                             label="Yes",
            #                             custom_id="yes"
            #                         ),
            #                         Button(
            #                             style=ButtonStyle.BLUE,
            #                             label="No",
            #                             custom_id="no"
            #                         )
            #                     ]
            #                     trade_buttons_action_row = ActionRow(*trade_buttons)
            #                     await button_ctx.send(f"Are you sure you want to trade **{selected_card}**", components=[trade_buttons_action_row])
            #                     try:
            #                         button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120)
            #                         if button_ctx.custom_id == "no":
            #                                 await button_ctx.send("Not this time. ")
            #                                 self.stop = True
            #                         if button_ctx.custom_id == "yes":
            #                             if mvalidation:
            #                                 trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
            #                                 update_query = {"$push" : {'MCARDS': selected_card}, "$inc" : {'TAX' : int(sell_price)}}
            #                                 resp = db.updateTrade(trade_query, update_query)
            #                                 await button_ctx.send("Trade staged.")
            #                                 self.stop = True
            #                             elif bvalidation:
            #                                 trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
            #                                 update_query = {"$push" : {'BCARDS': selected_card}, "$inc" : {'TAX' : int(sell_price)}}
            #                                 resp = db.updateTrade(trade_query, update_query)
            #                                 await button_ctx.send("Trade staged.")
            #                                 self.stop = True
            #                     except Exception as ex:
            #                         trace = []
            #                         tb = ex.__traceback__
            #                         while tb is not None:
            #                             trace.append({
            #                                 "filename": tb.tb_frame.f_code.co_filename,
            #                                 "name": tb.tb_frame.f_code.co_name,
            #                                 "lineno": tb.tb_lineno
            #                             })
            #                             tb = tb.tb_next
            #                         print(str({
            #                             'PLAYER': str(ctx.author),
            #                             'type': type(ex).__name__,
            #                             'message': str(ex),
            #                             'trace': trace
            #                         }))
            #                         await ctx.send("There's an issue with trading one or all of your items.")
            #                         return   

            #     else:
            #         await ctx.send("This is not your card list.")       
       
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
            embed = Embed(title="🎴 Cards Error", description="There's an issue with loading your cards. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0xff0000)
            await ctx.send(embed=embed)
            return


    @slash_command(description="View all of your titles")
    async def titles(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        player = crown_utilities.create_player_from_data(a_registered_player)
        try:
            """
            Unlock Methods
            # Tales completed {TYPE: "TALES", "VALUE": "1"}
            # Dungeons completed {TYPE: "DUNGEONS", "VALUE": "1"}
            # Scenarios completed {TYPE: "SCENARIOS", "VALUE": "1"}
            # Specific Element Damage Dealt in universe {TYPE: "ELEMENT", "VALUE": "100"}
            # Total Damage Dealt in universe {TYPE: "TOTAL_DAMAGE", "VALUE": "100"}
            # Bosses beat in universe {TYPE: "BOSS", "VALUE": "1"}
            # None / Picked from scenario window
            {TYPE: "", "VALUE": ""}
            """
            embed_list = []
            for title in sorted(player.titles):
                resp = db.queryTitle({"TITLE": str(title)})
                index = player.titles.index(title)
                t = crown_utilities.create_title_from_data(resp)
                embedVar = Embed(title=f"{t.name}", description=f"{crown_utilities.crest_dict[t.universe]} | {t.universe} Title", color=0x7289da)
                embedVar.add_field(name=f"**Title Effects**", value="\n".join(t.title_messages), inline=False)
                embedVar.add_field(name=f"**How To Unlock**", value=f"{t.unlock_method_message}", inline=False)                
                embed_list.append(embedVar)
            
            buttons = ["Equip", "Charge"]
            
            custom_action_row = ActionRow(*buttons)

            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=buttons, paginator_type="Titles")
            paginator.show_select_menu = True
            await paginator.send(ctx)

            # async def custom_function(self, button_ctx):
            #     if button_ctx.author == ctx.author:
            #         updated_vault = db.queryVault({'DID': d['DID']})
            #         sell_price = 0
            #         selected_title = str(button_ctx.origin_message.embeds[0].title)

            #         if button_ctx.custom_id == "Storage":
            #             await button_ctx.defer(ignore=True)
            #             storage_buttons = [
            #                         Button(
            #                             style=ButtonStyle.GREEN,
            #                             label="Swap Storage Title",
            #                             custom_id="swap"
            #                         ),
            #                         Button(
            #                             style=ButtonStyle.RED,
            #                             label="Add to Storage",
            #                             custom_id="store"
            #                         )
            #                     ]
            #             storage_buttons_action_row = ActionRow(*storage_buttons)
            #             msg = await ctx.send(f"Would you like to Swap Titles or Add Title to Storage", components=[storage_buttons_action_row])
            #             def check(button_ctx):
            #                 return button_ctx.author == ctx.author
            #             try:
            #                 button_ctx: ComponentContextStorage = await self.bot.wait_for_component(components=[storage_buttons_action_row], timeout=120, check=check)

            #                 if button_ctx.custom_id == "swap":
            #                     await button_ctx.defer(ignore=True)
            #                     await msg.delete()
            #                     await ctx.send(f"{ctx.author.mention}, Which title number would you like to swap with in storage?")
            #                     def check(msg):
            #                         return msg.author == ctx.author

            #                     try:
            #                         msg = await self.bot.wait_for('on_message_create', check=check, timeout=30)
            #                         author = msg.author
            #                         content = msg.content

            #                         if storage[int(msg.content)]:
            #                             swap_with = storage[int(msg.content)]
            #                             query = {'DID': str(msg.author.id)}
            #                             update_storage_query = {
            #                                 '$pull': {'TITLES': selected_title},
            #                                 '$addToSet': {'TSTORAGE': selected_title},
            #                             }
            #                             response = db.updateUserNoFilter(query, update_storage_query)

            #                             update_storage_query = {
            #                                 '$pull': {'TSTORAGE': swap_with},
            #                                 '$addToSet': {'TCARDS': swap_with}
            #                             }
            #                             response = db.updateUserNoFilter(query, update_storage_query)

            #                             await msg.delete()
            #                             await ctx.send(f"**{selected_title}** has been swapped with **{swap_with}**")
            #                             return
            #                         else:
            #                             await ctx.send("The card number you want to swap with does not exist.")
            #                             return

            #                     except Exception as e:
            #                         return False
            #                 if button_ctx.custom_id == "store":
            #                     await button_ctx.defer(ignore=True)
                                
            #                     try:
            #                         author = msg.author
            #                         content = msg.content
            #                         # print("Author: " + str(author))
            #                         # print("Content: " + str(content))
            #                         if len(storage) <= (storage_type * 15):
            #                             query = {'DID': str(ctx.author.id)}
            #                             update_storage_query = {
            #                                 '$pull': {'TITLES': selected_title},
            #                                 '$addToSet': {'TSTORAGE': selected_title},
            #                             }
            #                             response = db.updateUserNoFilter(query, update_storage_query)
                                        
            #                             await msg.delete()
            #                             await ctx.send(f"**{selected_title}** has been added to storage")
            #                             return
            #                         else:
            #                             await ctx.send("Not enough space in storage")
            #                             return

            #                     except Exception as e:
            #                         return False
            #             except Exception as ex:
            #                 trace = []
            #                 tb = ex.__traceback__
            #                 while tb is not None:
            #                     trace.append({
            #                         "filename": tb.tb_frame.f_code.co_filename,
            #                         "name": tb.tb_frame.f_code.co_name,
            #                         "lineno": tb.tb_lineno
            #                     })
            #                     tb = tb.tb_next
            #                 print(str({
            #                     'type': type(ex).__name__,
            #                     'message': str(ex),
            #                     'trace': trace
            #                 }))
                        
            #             self.stop = True
            #     else:
            #         await ctx.send("This is not your Title list.")


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
            await ctx.send("There's an issue with your Titles list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
            return


    @slash_command(description="View all of your arms")
    async def arms(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        player = crown_utilities.create_player_from_data(d)
        card = db.queryCard({"NAME": player.equipped_card})
        if player:
            try:
                current_gems = []
                for gems in player.gems:
                    current_gems.append(gems['UNIVERSE'])

                embed_list = []
                sorted_arms = sorted(player.arms, key=lambda arm: arm['ARM'])
                for index, arm in enumerate(sorted_arms):
                    resp = db.queryArm({"ARM": arm['ARM']})
                    arm_data = crown_utilities.create_arm_from_data(resp)
                    arm_data.set_durability(arm_data.name, player.arms)
                    arm_data.set_arm_message(player.performance, card['UNIVERSE'])

                    embedVar = Embed(title= f"{arm_data.name}", description=textwrap.dedent(f"""
                    {arm_data.armicon} **[{index}]**

                    {arm_data.arm_type}
                    {arm_data.arm_message}
                    {arm_data.universe_crest} **Universe:** {arm_data.universe}
                    ⚒️ {arm_data.durability}
                    """), 
                    color=0x7289da)

                    embedVar.set_footer(text=f"{arm_data.footer}")
                    embed_list.append(embedVar)
                
                paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=['Equip', 'Dismantle', 'Trade', 'Storage'], paginator_type="Arms")
                if len(embed_list) <= 25:
                    paginator.show_select_menu = True
                await paginator.send(ctx)
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
                embed = discord.Embed(title="Arms Error", description="There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0x00ff00)
                await ctx.send(embed=embed)
                return
        else:
            embed = discord.Embed(title="You are not registered.", description="Please register with the command /register", color=0x00ff00)
            await ctx.send(embed=embed)


    @slash_command(description="View all of your gems")
    async def gems(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            current_gems = user['GEMS']
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

                    gem_details.append(f"{crown_utilities.crest_dict[gd['UNIVERSE']]} **{gd['UNIVERSE']}**\n💎 {'{:,}'.format(gd['GEMS'])}\nUniverse Heart {heart}\nUniverse Soul {soul}\n")

                embed_list = []
                for i in range(0, len(gem_details), 5):
                    sublist = gem_details[i:i + 5]
                    embedVar = Embed(title=f"Gems", description="\n".join(sublist), color=0x7289da)
                    embed_list.append(embedVar)

                paginator = Paginator.create_from_embeds(self.bot, *embed_list)
                await paginator.send(ctx)
            else:
                embed = Embed(title="Gems", description="You currently own no 💎.", color=0x7289da)
                await ctx.send(embed=embed)
        except Exception as ex:
            print(ex)
            embed = Embed(title="Gems", description="There was an error retrieving your 💎.", color=0x7289da)
            await ctx.send(embed=embed)
            return


    @slash_command(description="View all of your collected essence")
    async def essence(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            current_essence = user['ESSENCE']
            if current_essence:
                essence_details = []
                for ed in current_essence:
                    element = ed["ELEMENT"]
                    essence = ed["ESSENCE"]
                    element_emoji = crown_utilities.set_emoji(element)
                    essence_details.append(f"{element_emoji} **{element.title()} Essence: ** {'{:,}'.format(essence)}\n")

                embed_list = []
                for i in range(0, len(essence_details), 5):
                    sublist = essence_details[i:i+5]
                    embedVar = Embed(title=f"🪔 Essence", description="\n".join(sublist), color=0x7289da)
                    embed_list.append(embedVar)
                paginator = Paginator.create_from_embeds(self.bot, *embed_list)
                await paginator.send(ctx)
            else:
                embed = Embed(title=f"🪔 Essence", description="You currently own no 🪔 Essence.", color=0x7289da)
                await ctx.send(embed=embed)
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🪔 Essence", description="There was an issue loading your essence.", color=0x7289da)
            await ctx.send(embed=embed)
            return


    @slash_command(description="Open the blacksmith")
    async def blacksmith(self, ctx):
        try:
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
            abyss_arm = False
            boss_message = "Nice Arm!"
            arm_cost = '{:,}'.format(100000)
            durability_message = f"{arm_cost}"
            if arm_info['UNIVERSE'] == "Unbound":
                abyss_arm= True
                arm_cost = '{:,}'.format(1000000)
                durability_message = f"{arm_cost}"
            elif arm_info['AVAILABLE'] == False and arm_info['EXCLUSIVE'] == False:
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
            elif abyss_arm:
                boss_message = "That's Abyssal!!"
            vault_query = {'DID' : str(ctx.author.id)}
            vault = db.altQueryVault(vault_query)
            current_card = user['CARD']
            current_title = user['TITLE']
            current_pet = user['PET']
            current_talisman = user['TALISMAN']
            has_gabes_purse = user['TOURNAMENT_WINS']
            if not has_gabes_purse:
                gabes_message = "25,000,000"
                gabes_explain = "Purchase **Gabe's Purse** to Keep ALL ITEMS during **/rebirth**"
            balance = vault['BALANCE']
            icon = "🪙"
            if balance >= 1000000:
                icon = "💸"
            elif balance >=650000:
                icon = "💰"
            elif balance >= 150000:
                icon = "💵"
            
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
            

            
            hundred_levels = 5000000
            thirty_levels = 1600000
            ten_levels = 500000
            
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
            elif lvl >= 700 and lvl <= 799:
                hundred_levels = 750000000
                thirty_levels = 500000000
                ten_levels = 250000000
            elif lvl >= 800 and lvl <= 899:
                hundred_levels = 1000000000
                thirty_levels = 800000000
                ten_levels = 500000000
            elif lvl >= 900 and lvl <= 999:
                hundred_levels = 5000000000
                thirty_levels = 2500000000
                ten_levels = 1000000000
            elif lvl >= 1000 and lvl <= 1999:
                hundred_levels = 20000000000
                thirty_levels = 5000000000
                ten_levels = 5000000000
            elif lvl >= 2000 and lvl <= 2999:
                hundred_levels = 80000000000
                thirty_levels = 13000000000
                ten_levels = 9000000000
            sell_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="🔋 1️⃣",
                        custom_id="1"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="🔋 2️⃣",
                        custom_id="2"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="🔋 3️⃣",
                        custom_id="3"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="⚒️ 4️⃣",
                        custom_id="5"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Cancel",
                        custom_id="cancel"
                    )
                ]
            
            util_sell_buttons = [
                    Button(
                        style=ButtonStyle.GREY,
                        label="Gabe's Purse 👛",
                        custom_id="4"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Storage 💼",
                        custom_id="6"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Preset 🔖",
                        custom_id="7"
                    )
            ]
            
            sell_buttons_action_row = ActionRow(*sell_buttons)
            util_sell_buttons_action_row = ActionRow(*util_sell_buttons)
            embedVar = Embed(title=f"🔨 | **Blacksmith** - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
            Welcome {ctx.author.mention}!
            Purchase **Card XP** and **Arm Durability**!
            🎴 Card:  **{current_card}** {licon}**{lvl}**
            🦾 Arm: **{current_arm}** *{boss_message}* ⚒️*{current_durability}*
            
            **Card Level Boost**
            🔋 1️⃣ **10 Levels** for 🪙 **{'{:,}'.format(ten_levels)}**
            🔋 2️⃣ **30 Levels** for 💵 **{'{:,}'.format(thirty_levels)}**
            🔋 3️⃣ **100 Levels** for 💰 **{'{:,}'.format(hundred_levels)}**
            ⚒️ 4️⃣ **50 Durability** for 💵 **{durability_message}**
            
            **Vault Upgrades**
            💼 **Storage Tier {storage_message}**: 💸 **{storage_pricing_text}**
            🔖 **Preset Upgrade**: 💸 **{preset_message}**
            👛 **Gabe's Purse**: 💸 **{gabes_message}**
            {gabes_explain}
            
            What would you like to buy?
            """), color=0xf1c40f)
            embedVar.set_footer(text="Boosts are used immediately upon purchase. Click cancel to exit purchase.", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")
            msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row, util_sell_buttons_action_row])

            def check(button_ctx):
                return button_ctx.author == ctx.author

            try:
                button_ctx  = await self.bot.wait_for_component(components=[sell_buttons_action_row, util_sell_buttons_action_row], timeout=120,check=check)
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
                        await button_ctx.send("You're too broke to buy. Get your money up.", ephemeral=True)
                        await msg.edit(components=[])
                        return

                    card_info = {}
                    for level in vault['CARD_LEVELS']:
                        if level['CARD'] == current_card:
                            card_info = level

                    lvl = card_info['LVL']
                    max_lvl = 1000
                    if lvl >= max_lvl:
                        await button_ctx.send(f"🎴: **{current_card}** is already at max Smithing level. You may level up in **battle**, but you can no longer purchase levels for this card.", ephemeral=True)
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
                    response = db.updateUser(query, update_query, filter_query)
                    await crown_utilities.curse(price, str(ctx.author.id))
                    await button_ctx.send(f"🔋🎴 | **{str(current_card)}** gained {levels_gained} levels!")
                    await msg.edit(components=[])
                    if button_ctx.custom_id == "cancel":
                        await button_ctx.send("Sell ended.", ephemeral=True)
                        await msg.edit(components=[])
                        return

                if button_ctx.custom_id == "4":
                    price = 25000000
                    if price > balance:
                        await button_ctx.send("Insufficent funds.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                    if has_gabes_purse:
                        await button_ctx.send("You already own Gabes Purse. You cannot purchase more than one.", ephemeral=True)
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
                        await button_ctx.send("Insufficent funds.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                    if preset_upgrade:
                        await button_ctx.send("You already have 5 Presets!", ephemeral=True)
                        await msg.edit(components=[])
                        return
                    else:
                        await crown_utilities.curse(price, str(ctx.author.id))
                        response = db.updateUserNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' : str(current_card), 'TITLE': "Preset Upgrade Ver 4.0",'ARM': str(current_arm), 'PET': "Chick", 'TALISMAN': str(current_talisman)}}})
                        response = db.updateUserNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' : str(current_card), 'TITLE': "Preset Upgrade Ver 5.0",'ARM': str(current_arm), 'PET': "Chick", 'TALISMAN': str(current_talisman)}}})
                        #response = db.updateUserNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' :str(current_card), 'TITLE': str(current_title),'ARM': str(current_arm), 'PET': str(current_pet)}}})
                        update = db.updateUserNoFilterAlt(user_query, {'$set': {'U_PRESET': True}})
                        await button_ctx.send("🔖 | Preset Upgraded")
                        await msg.edit(components=[])
                        return
                
                if button_ctx.custom_id == "5":
                    if dungeon_arm:
                        price = 250000
                    if abyss_arm:
                        price = 1000000
                    if boss_arm:
                        await button_ctx.send("Sorry I can't repair **Boss** Arms ...", ephemeral=True)
                        await msg.edit(components=[])
                        return
                    if price > balance:
                        await button_ctx.send("Insufficent funds.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                    if current_durability >= 100:
                        await button_ctx.send(f"🦾 | {current_arm} is already at Max Durability. ⚒️",ephemeral=True)
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
                            resp = db.updateUser(query, update_query, filter_query)

                            await crown_utilities.curse(price, str(ctx.author.id))
                            if full_repair:
                                    await button_ctx.send(f"🦾 | {current_arm}'s ⚒️ durability has increased by **{levels_gained}**!\n*Maximum Durability Reached!*")
                            else:
                                    await button_ctx.send(f"🦾 | {current_arm}'s ⚒️ durability has increased by **{levels_gained}**!")
                            await msg.edit(components=[])
                            return
                        except:
                            await ctx.send("Unsuccessful to purchase durability boost.", ephemeral=True)

                if button_ctx.custom_id == "6":
                    if storage_pricing > balance:
                        await button_ctx.send("Insufficent funds.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                        
                    if not patron_flag and storage_type >= 2:
                        await button_ctx.send("💞 | Only Patrons may purchase more than 30 additional storage. To become a Patron, visit https://www.patreon.com/partychatgaming?fan_landing=true.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                        
                    if storage_type == 10:
                        await button_ctx.send("💼 | You already have max storage.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                        
                    else:
                        update = db.updateUserNoFilterAlt(user_query, {'$inc': {'STORAGE_TYPE': 1}})
                        await crown_utilities.curse(storage_pricing, str(ctx.author.id))
                        await button_ctx.send(f"💼 | Storage Tier {str(storage_type + 1)} has been purchased!")
                        await msg.edit(components=[])
                        return
            except asyncio.TimeoutError:
                await ctx.send("Blacksmith closed.", ephemeral=True)
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
                await ctx.send("Blacksmith closed unexpectedly. Seek support.", ephemeral=True)
        except asyncio.TimeoutError:
            await ctx.send("Blacksmith closed.", ephemeral=True)
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
            await ctx.send("Blacksmith closed unexpectedly. Seek support.", ephemeral=True)
    

    @slash_command(description="View your summons")
    async def summons(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        d = db.queryUser({'DID': str(ctx.author.id)})
        player = crown_utilities.create_player_from_data(d)

        try:
            embed_list = []

            sorted_summons = sorted(player.summons, key=lambda summon: summon['NAME'])
            for index, summons in enumerate(sorted_summons):
                #cpetmove_ap= (cpet_bond * cpet_lvl) + list(cpet.values())[3] # Ability Power
                s = db.querySummon({'PET': summons['NAME']})
                summon = crown_utilities.create_summon_from_data(s)
                summon.set_player_summon_info(player)

                embedVar = Embed(title= f"{summon.name}", description=textwrap.dedent(f"""
                🧬
                _Bond_ **{summon.bond}** | {summon.bond_message}
                _Level_ **{summon.level}** | {summon.level_message}

                {summon.emoji} {summon.ability_type.capitalize()} Ability 
                **{summon.ability}:** {summon.ability_power}

                {summon.universe_crest} {summon.universe.capitalize()} Universe Summon
                """))
                embed_list.append(embedVar)

            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Equip", "Trade", "Dismantle"], paginator_type="Summons")
            
            if len(embed_list) <= 25:
                paginator.show_select_menu = True
            await paginator.send(ctx)

            # async def custom_function(self, button_ctx):
            #     if button_ctx.author == ctx.author:
            #         updated_vault = db.queryVault({'DID': d['DID']})
            #         sell_price = 0
            #         selectedsummon = str(button_ctx.origin_message.embeds[0].title)
            #         user_query = {'DID': str(ctx.author.id)}
                    
            #         if button_ctx.custom_id == "Equip":
            #             response = db.updateUserNoFilter(user_query, {'$set': {'FAMILY_PET': False, 'PET': str(button_ctx.origin_message.embeds[0].title)}})
            #             await button_ctx.send(f"🧬 **{str(button_ctx.origin_message.embeds[0].title)}** equipped.")
            #             self.stop = True
                    
            #         elif button_ctx.custom_id =="Trade":
            #             summon_data = db.querySummon({'PET' : selectedsummon})
            #             summon_name = summon_data['PET']
            #             if summon_name == currentsummon:
            #                 await button_ctx.send("You cannot trade equipped summons.")
            #                 return
            #             sell_price = 5000
            #             mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
            #             mvalidation=False
            #             bvalidation=False
            #             item_already_in_trade=False
            #             if mtrade:
            #                 if selectedsummon in mtrade['MSUMMONS']:
            #                     await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
            #                     item_already_in_trade=True
            #                 mvalidation=True
            #             else:
            #                 btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
            #                 if btrade:
            #                     if selectedsummon in btrade['BSUMMONS']:
            #                         await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
            #                         item_already_in_trade=True
            #                     bvalidation=True
            #                 else:
            #                     await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
            #                     return
            #             if item_already_in_trade:
            #                 trade_buttons = [
            #                     Button(
            #                         style=ButtonStyle.GREEN,
            #                         label="Yes",
            #                         custom_id="yes"
            #                     ),
            #                     Button(
            #                         style=ButtonStyle.BLUE,
            #                         label="No",
            #                         custom_id="no"
            #                     )
            #                 ]
            #                 trade_buttons_action_row = ActionRow(*trade_buttons)
            #                 await button_ctx.send(f"Woudl you like to remove **{selectedsummon}** from the **Trade**?", components=[trade_buttons_action_row])
                            
            #                 def check(button_ctx):
            #                     return button_ctx.author == ctx.author
                                                            
            #                 try:
            #                     button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
            #                     if button_ctx.custom_id == "no":
            #                             await button_ctx.send("Happy Trading")
            #                             self.stop = True
            #                     if button_ctx.custom_id == "yes":
            #                         neg_sell_price = 0 - abs(int(sell_price))
            #                         if mvalidation:
            #                             trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
            #                             update_query = {"$pull" : {'MSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(neg_sell_price)}}
            #                             resp = db.updateTrade(trade_query, update_query)
            #                             await button_ctx.send("Returned.")
            #                             self.stop = True
            #                         elif bvalidation:
            #                             trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
            #                             update_query = {"$pull" : {'BSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(neg_sell_price)}}
            #                             resp = db.updateTrade(trade_query, update_query)
            #                             await button_ctx.send("Returned.")
            #                             self.stop = True
            #                 except Exception as ex:
            #                     trace = []
            #                     tb = ex.__traceback__
            #                     while tb is not None:
            #                         trace.append({
            #                             "filename": tb.tb_frame.f_code.co_filename,
            #                             "name": tb.tb_frame.f_code.co_name,
            #                             "lineno": tb.tb_lineno
            #                         })
            #                         tb = tb.tb_next
            #                     print(str({
            #                         'PLAYER': str(ctx.author),
            #                         'type': type(ex).__name__,
            #                         'message': str(ex),
            #                         'trace': trace
            #                     }))
            #                     await ctx.send("There's an issue with trading one or all of your items.")
            #                     return   
            #             elif mvalidation == True or bvalidation ==True:    #If user is valid
            #                 sell_price = 5000
            #                 trade_buttons = [
            #                     Button(
            #                         style=ButtonStyle.GREEN,
            #                         label="Yes",
            #                         custom_id="yes"
            #                     ),
            #                     Button(
            #                         style=ButtonStyle.BLUE,
            #                         label="No",
            #                         custom_id="no"
            #                     )
            #                 ]
            #                 trade_buttons_action_row = ActionRow(*trade_buttons)
            #                 await button_ctx.send(f"Are you sure you want to trade **{selectedsummon}**", components=[trade_buttons_action_row])
            #                 try:
            #                     button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120)
            #                     if button_ctx.custom_id == "no":
            #                             await button_ctx.send("Not this time. ")
            #                             self.stop = True
            #                     if button_ctx.custom_id == "yes":
            #                         if mvalidation:
            #                             trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
            #                             update_query = {"$push" : {'MSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(sell_price)}}
            #                             resp = db.updateTrade(trade_query, update_query)
            #                             await button_ctx.send("Traded.")
            #                             self.stop = True
            #                         elif bvalidation:
            #                             trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
            #                             update_query = {"$push" : {'BSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(sell_price)}}
            #                             resp = db.updateTrade(trade_query, update_query)
            #                             await button_ctx.send("Traded.")
            #                             self.stop = True
            #                 except Exception as ex:
            #                     trace = []
            #                     tb = ex.__traceback__
            #                     while tb is not None:
            #                         trace.append({
            #                             "filename": tb.tb_frame.f_code.co_filename,
            #                             "name": tb.tb_frame.f_code.co_name,
            #                             "lineno": tb.tb_lineno
            #                         })
            #                         tb = tb.tb_next
            #                     print(str({
            #                         'PLAYER': str(ctx.author),
            #                         'type': type(ex).__name__,
            #                         'message': str(ex),
            #                         'trace': trace
            #                     }))
            #                     await ctx.send("There's an issue with trading one or all of your items.")
            #                     return   
                    
            #         elif button_ctx.custom_id == "Dismantle":
            #             summon_data = db.querySummon({'PET' : selectedsummon})
            #             summon_name = summon_data['PET']
            #             if summon_name == currentsummon:
            #                 await button_ctx.send("You cannot dismantle equipped summonss.")
            #                 return
            #             dismantle_price = 10000   
            #             level = int(pet['LVL'])
            #             bond = int(pet['BOND'])
            #             dismantle_amount = round((1000* level) + (dismantle_price * bond) + dismantle_price)
            #             dismantle_buttons = [
            #                 Button(
            #                     style=ButtonStyle.GREEN,
            #                     label="Yes",
            #                     custom_id="yes"
            #                 ),
            #                 Button(
            #                     style=ButtonStyle.BLUE,
            #                     label="No",
            #                     custom_id="no"
            #                 )
            #             ]
            #             dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
            #             msg = await button_ctx.send(f"Are you sure you want to dismantle **{summon_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
            #             def check(button_ctx):
            #                 return button_ctx.author == ctx.author

                        
            #             try:
            #                 button_ctx  = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

            #                 if button_ctx.custom_id == "no":
            #                     await button_ctx.send("Dismantle cancelled. ")
            #                     self.stop = True
            #                 if button_ctx.custom_id == "yes":
            #                     if pet_universe in current_gems:
            #                         query = {'DID': str(ctx.author.id)}
            #                         family_query = {'HEAD':d['FAMILY']}
            #                         if d['FAMILY'] != 'PCG':
            #                             family_info = db.queryFamily(family_query)
            #                             if summon_name == family_info['SUMMON']:
            #                                 update_query = {'$set' : {'SUMMON': d['PET']}}
            #                                 family_update = db.updateFamily(family_query,update_query)
            #                         update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
            #                         filter_query = [{'type.' + "UNIVERSE": pet_universe}]
            #                         response = db.updateUser(query, update_query, filter_query)
            #                     else:
            #                         response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': pet_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                
            #                     db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'PETS': {"NAME": str(summon_name)}}})
            #                     #await crown_utilities.bless(sell_price, ctx.author.id)
            #                     await msg.delete()
            #                     await button_ctx.send(f"**{summon_name}** has been dismantled for 💎 {'{:,}'.format(dismantle_amount)}.")
            #                     self.stop = True
            #             except Exception as ex:
            #                 trace = []
            #                 tb = ex.__traceback__
            #                 while tb is not None:
            #                     trace.append({
            #                         "filename": tb.tb_frame.f_code.co_filename,
            #                         "name": tb.tb_frame.f_code.co_name,
            #                         "lineno": tb.tb_lineno
            #                     })
            #                     tb = tb.tb_next
            #                 print(str({
            #                     'type': type(ex).__name__,
            #                     'message': str(ex),
            #                     'trace': trace
            #                 }))
            #                 #await ctx.send(f"ERROR:\nTYPE: {type(ex).__name__}\nMESSAGE: {str(ex)}\nLINE: {trace} ")
            #                 return
            #         elif button_ctx.custom_id =="Exit":
            #             await button_ctx.defer(ignore=True)
            #             self.stop = True
            #     else:
            #         await ctx.send("This is not your Summons list.")
            
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
            embed = Embed(title="Summons Error", description="There's an issue with your Summons list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
            await ctx.send(embed=embed)
            return


    @slash_command(description="View your destinies")
    async def destinies(self, ctx):
        
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
                icon = "🪙"
                if balance >= 150000:
                    icon = "💸"
                elif balance >=100000:
                    icon = "💰"
                elif balance >= 50000:
                    icon = "💵"
                for d in destiny:
                    if not d['COMPLETED']:
                        destiny_messages.append(textwrap.dedent(f"""\
                        :sparkles: **{d["NAME"]}**
                        Defeat **{d['DEFEAT']}** with **{" ".join(d['USE_CARDS'])}** | **Current Progress:** {d['WINS']}/{d['REQUIRED']}
                        Win 🎴 **{d['EARN']}**
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
                    embedVar = Embed(title= f"Destiny Lines\n**Balance**: 🪙{'{:,}'.format(balance)}", description="\n".join(destiny_messages), color=0x7289da)
                    embedVar.set_thumbnail(url=avatar)
                    # embedVar.set_footer(text=f".equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                    await ctx.send(embed=embedVar)

                embed_list = []
                for i in range(0, len(destinies_broken_up)):
                    embedVar = Embed(title= f":sparkles: Destiny Lines\n**Balance**: {icon}{'{:,}'.format(balance)}", description="\n".join(destinies_broken_up[i]), color=0x7289da)
                    embedVar.set_thumbnail(url=avatar)
                    # embedVar.set_footer(text=f"{total_pets} Total Pets\n.equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                    embed_list.append(embedVar)

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


    @slash_command(description="View your quests")
    async def quests(self, ctx):
        
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        vault = db.queryVault({'DID': d['DID']})
        prestige = d['PRESTIGE']
        exchange = int(100 - (prestige * 10))
        # server = db.queryServer({"GNAME": str(ctx.author.guild)})
        if not vault['QUESTS']:
            await ctx.send("You have no quests available at this time!", ephemeral=True)
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
                    icon = "🪙"
                    if quest['REWARD'] >= 3000000:
                        icon = ":credit_card:"
                    if quest['REWARD'] >= 2000000:
                        icon = "💸"
                    elif quest['REWARD'] >=1000000:
                        icon = "💰"
                    elif quest['REWARD'] >= 200000:
                        icon = "💵"
                    

                    embedVar = Embed(title=f"{opponent_name}", description=textwrap.dedent(f"""\
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
                    if guild_buff:
                        if guild_buff['Quest']:
                            if int(goal) > 1:
                                embedVar.set_footer(text=f"🌑 | Conquer Abyss **{exchange}** and Prestige to reduce Quest Requirements!")
                            else:
                                embedVar.set_footer(text=f"☀️ | You can use /daily every 12 Hours for More Quest!")
                        else:
                            embedVar.set_footer(text=f"🪖 | Purchase a Guild Quest Buff and skip to the Quest Fight!")
                    else:
                        embedVar.set_footer(text=f"🪖 | Create a Guild and purchase Quest Buff! Skip to the quest fight!")
                    # embedVar.set_footer(text="Use /tales to complete daily quest!", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")

                    if quest['GOAL'] != quest['WINS']:
                        embed_list.append(embedVar)

                if not embed_list:
                    await ctx.send(" 👑 | All quests have been completed today!")
                    return

                buttons = [Button(style=3, label="Start Quest Tales", custom_id="quests_tales"),]
                custom_action_row = ActionRow(*buttons)

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
                            player = db.queryUser({'DID': str(ctx.author.id)})
                            p = Player(player['AUTOSAVE'],player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'],player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'],
                            player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'],
                            player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'], player['EXPLORE_LOCATION'], player['SCENARIO_HISTORY'])

                            #print(currentopponent)
                            mode  = "Tales"
                            battle = Battle(mode, p)
                            response = {'SELECTED_UNIVERSE': selected_universe,
                            'UNIVERSE_DATA': universe, 'CREST_LIST': p.crestlist, 'CREST_SEARCH': p.crestsearch,
                            'COMPLETED_TALES': p.completed_tales, 'OGUILD': p.association_info, 'CURRENTOPPONENT': currentopponent}
                            battle.set_universe_selection_config(response)
                            
                            await battle_commands(self, ctx, battle, p, None, player2=None, player3=None)
                            
                            self.stop = True
                    else:
                        await ctx.send("This is not your Quest list.")

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
                await ctx.send("There's an issue with your Quest list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                return
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
            

    @slash_command(description="View your balance")
    async def balance(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            query = {'DID': str(ctx.author.id)}
            user = db.queryUser(query)
            icon = "🪙"
            balance = int(user['BALANCE'])

            if user['TEAM'] != 'PCG':
                t = db.queryTeam({'TEAM_NAME' : user['TEAM'].lower()})
                tbal = round(t['BANK'])

            if user['FAMILY'] != 'PCG':
                f = db.queryFamily({'HEAD': user['DID']})
                fbal = round(f['BANK'])

            def get_balance_emoji(balance):
                if balance >= 50000000:
                    icon = "💸"
                elif balance >=10000000:
                    icon = "💰"
                elif balance >= 500000:
                    icon = "💵"
                return icon

            embedVar = Embed(title= f"Account Balances", description=textwrap.dedent(f"""
            **Account Balance:** {get_balance_emoji(balance)}{'{:,}'.format(balance)}
            **Team Bank Balance:** {get_balance_emoji(tbal)}{'{:,}'.format(tbal)}
            **Family Bank Balance:** {get_balance_emoji(fbal)}{'{:,}'.format(fbal)}
            """))
            await ctx.send(embed=embedVar)

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
            embed = Embed(title="Balance Error", description="There was an error with your balance. Please contact support.")
            await ctx.send(embed=embed)
            return


    @slash_command(description="Load a saved preset")
    async def preset(self, ctx):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            _uuid = uuid.uuid4()
            query = {'DID': str(ctx.author.id)}
            user = db.queryUser(query)
            if user['DECK']:
                ownedcards = []
                ownedtitles = []
                ownedarms = []
                ownedpets = []
                ownedtalismans = []
                for cards in user['CARDS']:
                    ownedcards.append(cards)
                for titles in user['TITLES']:
                    ownedtitles.append(titles)
                for arms in user['ARMS']:
                    ownedarms.append(arms['ARM'])
                for pets in user['PETS']:
                    ownedpets.append(pets['NAME'])
                for talismans in user['TALISMANS']:
                    ownedtalismans.append(talismans['TYPE'])

                name = user['DISNAME'].split("#",1)[0]
                avatar = user['AVATAR']
                cards = user['CARDS']
                titles = user['TITLES']
                deck = user['DECK']
                preset_length = len(deck)
                preset_update = user['U_PRESET']
                
                
                preset1_card = list(deck[0].values())[0]
                preset1_title = list(deck[0].values())[1]
                preset1_arm = list(deck[0].values())[2]
                preset1_pet = list(deck[0].values())[3]
                preset1_talisman = list(deck[0].values())[4]

                preset2_card = list(deck[1].values())[0]
                preset2_title = list(deck[1].values())[1]
                preset2_arm = list(deck[1].values())[2]
                preset2_pet = list(deck[1].values())[3]
                preset2_talisman = list(deck[1].values())[4]

                preset3_card = list(deck[2].values())[0]
                preset3_title = list(deck[2].values())[1]
                preset3_arm = list(deck[2].values())[2]
                preset3_pet = list(deck[2].values())[3]    
                preset3_talisman = list(deck[2].values())[4]
                
                preset3_message = "📿"
                preset3_element = "None"
                if preset3_talisman != "NULL":
                    preset3_message = crown_utilities.set_emoji(preset3_talisman)
                    preset3_element = preset3_talisman.title()
                    
                preset2_message = "📿"
                preset2_element = "None"
                if preset2_talisman != "NULL":
                    preset2_message = crown_utilities.set_emoji(preset2_talisman)
                    preset2_element = preset2_talisman.title()
                    
                preset1_message = "📿"
                preset1_element = "None"
                if preset1_talisman != "NULL":
                    preset1_message = crown_utilities.set_emoji(preset1_talisman)
                    preset1_element = preset1_talisman.title()
                
                if preset_update:
                    preset4_card = list(deck[3].values())[0]
                    preset4_title = list(deck[3].values())[1]
                    preset4_arm = list(deck[3].values())[2]
                    preset4_pet = list(deck[3].values())[3]
                    preset4_talisman = list(deck[3].values())[4]

                    preset5_card = list(deck[4].values())[0]
                    preset5_title = list(deck[4].values())[1]
                    preset5_arm = list(deck[4].values())[2]
                    preset5_pet = list(deck[4].values())[3]  
                    preset5_talisman = list(deck[4].values())[4]
                    
                    preset5_message = "📿"
                    preset5_element = "None"
                    if preset5_talisman != "NULL":
                        preset5_message = crown_utilities.set_emoji(preset5_talisman)
                        preset5_element = preset5_talisman.title()
                        
                    preset4_message = "📿"
                    preset4_element = "None"
                    if preset4_talisman != "NULL":
                        preset4_message = crown_utilities.set_emoji(preset4_talisman)
                        preset4_element = preset4_talisman.title()
                        
                    listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n**Talisman**: {preset1_message}{preset1_element}\n\n", 
                    f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n**Talisman**: {preset2_message}{preset2_element}\n\n", 
                    f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n**Talisman**: {preset3_message}{preset3_element}\n\n", 
                    f"4️⃣| {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n**Talisman**: {preset4_message}{preset4_element}\n\n", 
                    f"5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n**Talisman**: {preset5_message}{preset5_element}\n\n"]  
                else:
                    listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n**Talisman**: {preset1_message}{preset1_element}\n\n", 
                    f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n**Talisman**: {preset2_message}{preset2_element}\n\n", 
                    f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n**Talisman**: {preset3_message}{preset3_element}\n\n"]
            
                embedVar = Embed(title="🔖 | Preset Menu", description=textwrap.dedent(f"""
                {"".join(listed_options)}
                """))
                embedVar.set_thumbnail(url=avatar)
                util_buttons = [
                    Button(
                        style=ButtonStyle.BLUE,
                        label="1️⃣",
                        custom_id = f"{_uuid}|1"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="2️⃣",
                        custom_id = f"{_uuid}|2"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="3️⃣",
                        custom_id = f"{_uuid}|3"
                    )
                ]
                
                if preset_update:
                    util_buttons.append(
                        Button(
                            style=ButtonStyle.BLUE,
                            label="4️⃣",
                            custom_id=f"{_uuid}|4"
                        )
                    )
                    util_buttons.append(
                        Button(
                            style=ButtonStyle.BLUE,
                            label="5️⃣",
                            custom_id=f"{_uuid}|5"
                        )
                    )
                    
                util_action_row = ActionRow(*util_buttons)
                msg = await ctx.send(embed=embedVar,components=[util_action_row])
                
                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author
                
                try:
                    button_ctx  = await self.bot.wait_for_component(components=[util_action_row], timeout=30,check=check)
                    equipped_items = []
                    not_owned_items = []
                    update_data = {}
                    if  button_ctx.ctx.custom_id == "0":
                        embed = Embed(title="🔖 | Preset Menu", description="No change has been made")
                        await button_ctx.send(f"{ctx.author.mention}, No change has been made", ephemeral=True)
                        return
                    elif  button_ctx.ctx.custom_id == f"{_uuid}|1":
                        equipped_items = []
                        not_owned_items = []
                        update_data = {}
                        if preset1_card in ownedcards:
                            equipped_items.append(f"🎴 **Card** | {preset1_card}")
                            update_data['CARD'] = str(preset1_card)
                        else:
                            not_owned_items.append(f"❌ {preset1_card}")

                        if preset1_title in ownedtitles:
                            equipped_items.append(f"🎗️ **Title** | {preset1_title}")
                            update_data['TITLE'] = str(preset1_title)
                        elif preset1_title is not None:
                            not_owned_items.append(f"❌ | {preset1_title}")

                        if preset1_arm in ownedarms:
                            equipped_items.append(f"🦾 **Arm** | {preset1_arm}")
                            update_data['ARM'] = str(preset1_arm)
                        elif preset1_arm is not None:
                            not_owned_items.append(f"❌ | {preset1_arm}")

                        if preset1_pet in ownedpets:
                            equipped_items.append(f"🧬 **Summon** | {preset1_pet}")
                            update_data['PET'] = str(preset1_pet)
                        elif preset1_pet is not None:
                            not_owned_items.append(f"❌ | {preset1_pet}")

                        if preset1_talisman in ownedtalismans or preset1_talisman == "NULL":
                            equipped_items.append(f"{preset1_message} **Talisman** | {preset1_element}")
                            update_data['TALISMAN'] = str(preset1_talisman)
                        elif preset1_talisman is not None:
                            not_owned_items.append(f"❌ | {preset1_message}{preset1_element}")

                    elif  button_ctx.ctx.custom_id == f"{_uuid}|2":
                        # Check if items are owned
                        equipped_items = []
                        not_owned_items = []
                        update_data = {}
                        if preset2_card in ownedcards:
                            equipped_items.append(f"🎴 **Card** | {preset2_card}")
                            update_data['CARD'] = str(preset2_card)
                        else:
                            not_owned_items.append(f"❌ {preset2_card}")

                        if preset2_title in ownedtitles:
                            equipped_items.append(f"🎗️ **Title** | {preset2_title}")
                            update_data['TITLE'] = str(preset2_title)
                        else:
                            not_owned_items.append(f"❌ | {preset2_title}")

                        if preset2_arm in ownedarms:
                            equipped_items.append(f"🦾 **Arm** | {preset2_arm}")
                            update_data['ARM'] = str(preset2_arm)
                        else:
                            not_owned_items.append(f"❌ | {preset2_arm}")

                        if preset2_pet in ownedpets:
                            equipped_items.append(f"🧬 **Summon** | {preset2_pet}")
                            update_data['PET'] = str(preset2_pet)
                        else:
                            not_owned_items.append(f"❌ | {preset2_pet}")

                        if preset2_talisman in ownedtalismans or preset2_talisman == "NULL":
                            equipped_items.append(f"{preset2_message} **Talisman** | {preset2_element}")
                            update_data['TALISMAN'] = str(preset2_talisman)
                        else:
                            not_owned_items.append(f"❌ | {preset2_message}{preset2_element}")

                    elif  button_ctx.ctx.custom_id == f"{_uuid}|3":
                        equipped_items = []
                        not_owned_items = []
                        update_data = {}
                        if preset3_card in ownedcards:
                            equipped_items.append(f"🎴 **Card** | {preset3_card}")
                            update_data['CARD'] = str(preset3_card)
                        else:
                            not_owned_items.append(f"❌ {preset3_card}")

                        if preset3_title in ownedtitles:
                            equipped_items.append(f"🎗️ **Title** | {preset3_title}")
                            update_data['TITLE'] = str(preset3_title)
                        else:
                            not_owned_items.append(f"❌ | {preset3_title}")

                        if preset3_arm in ownedarms:
                            equipped_items.append(f"🦾 **Arm** | {preset3_arm}")
                            update_data['ARM'] = str(preset3_arm)
                        else:
                            not_owned_items.append(f"❌ | {preset3_arm}")

                        if preset3_pet in ownedpets:
                            equipped_items.append(f"🧬 **Summon** | {preset3_pet}")
                            update_data['PET'] = str(preset3_pet)
                        else:
                            not_owned_items.append(f"❌ | {preset3_pet}")

                        if preset3_talisman in ownedtalismans or preset3_talisman == "NULL":
                            equipped_items.append(f"{preset3_message} **Talisman** | {preset3_element}")
                            update_data['TALISMAN'] = str(preset3_talisman)
                        else:
                            not_owned_items.append(f"❌ | {preset3_message}{preset3_element}")

                    elif  button_ctx.ctx.custom_id == f"{_uuid}|4":
                        equipped_items = []
                        not_owned_items = []
                        update_data = {}
                        if preset4_card in ownedcards:
                            equipped_items.append(f"🎴 **Card** | {preset4_card}")
                            update_data['CARD'] = str(preset4_card)
                        else:
                            not_owned_items.append(f"❌ {preset4_card}")

                        if preset4_title in ownedtitles:
                            equipped_items.append(f"🎗️ **Title** | {preset4_title}")
                            update_data['TITLE'] = str(preset4_title)
                        else:
                            not_owned_items.append(f"❌ | {preset4_title}")

                        if preset4_arm in ownedarms:
                            equipped_items.append(f"🦾 **Arm** | {preset4_arm}")
                            update_data['ARM'] = str(preset4_arm)
                        else:
                            not_owned_items.append(f"❌ | {preset4_arm}")

                        if preset4_pet in ownedpets:
                            equipped_items.append(f"🧬 **Summon** | {preset4_pet}")
                            update_data['PET'] = str(preset4_pet)
                        else:
                            not_owned_items.append(f"❌ | {preset4_pet}")

                        if preset4_talisman in ownedtalismans or preset4_talisman == "NULL":
                            equipped_items.append(f"{preset4_message} **Talisman** | {preset4_element}")
                            update_data['TALISMAN'] = str(preset4_talisman)
                        else:
                            not_owned_items.append(f"❌ | {preset4_message}{preset4_element}")
                        
                    elif  button_ctx.ctx.custom_id == f"{_uuid}|5":
                        equipped_items = []
                        not_owned_items = []
                        update_data = {}

                        if preset5_card in ownedcards:
                            equipped_items.append(f"🎴 **Card** | {preset5_card}")
                            update_data['CARD'] = str(preset5_card)
                        else:
                            not_owned_items.append(f"❌ {preset5_card}")

                        if preset5_title in ownedtitles:
                            equipped_items.append(f"🎗️ **Title** | {preset5_title}")
                            update_data['TITLE'] = str(preset5_title)
                        else:
                            not_owned_items.append(f"❌ | {preset5_title}")

                        if preset5_arm in ownedarms:
                            equipped_items.append(f"🦾 **Arm** | {preset5_arm}")
                            update_data['ARM'] = str(preset5_arm)
                        else:
                            not_owned_items.append(f"❌ | {preset5_arm}")

                        if preset5_pet in ownedpets:
                            equipped_items.append(f"🧬 **Summon** | {preset5_pet}")
                            update_data['PET'] = str(preset5_pet)
                        else:
                            not_owned_items.append(f"❌ | {preset5_pet}")

                        if preset5_talisman in ownedtalismans or preset5_talisman == "NULL":
                            equipped_items.append(f"{preset5_message} **Talisman** | {preset5_element}")
                            update_data['TALISMAN'] = str(preset5_talisman)
                        else:
                            not_owned_items.append(f"❌ | {preset5_message}{preset5_element}")
                    
                    response = db.updateUserNoFilter(query, {'$set': update_data})


                    embed = Embed(title=f"🔖 | Build Updated")
                    if equipped_items:
                        embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)
                        if not not_owned_items:
                            embed.set_footer(text="👥 | Conquer Universes with this preset in /duo!")
                    if not_owned_items:
                        embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                        embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    

                    # Send the response
                    await msg.edit(embed=embed, components=[])
                    return
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", ephemeral=True)
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
                    await ctx.send("Preset Issue Seek support.", ephemeral=True)
            else:
                embed = Embed(title=f"🔖 | Whoops!", description=f"You do not have a preset saved yet. Use /savepreset to save your current build as a preset.")
                await ctx.send(embed=embed)
                return
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", ephemeral=True)
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
            await ctx.send("Preset Issue Seek support.", ephemeral=True)


    @slash_command(description="Save your current build as a preset")
    async def savepreset(self, ctx):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            _uuid = uuid.uuid4()
            query = {'DID': str(ctx.author.id)}
            user = db.queryUser(query)
            
            if user:
                name = user['DISNAME'].split("#",1)[0]
                avatar = user['AVATAR']
                cards = user['CARDS']
                titles = user['TITLES']
                deck = user['DECK']


                current_card = user['CARD']
                current_title = user['TITLE']
                current_arm= user['ARM']
                current_pet = user['PET']
                current_talisman = user['TALISMAN']
                current_talisman_message = "📿"
                current_talisman_element = "None"
                if current_talisman != "NULL":
                    current_talisman_message = crown_utilities.set_emoji(current_talisman)
                    current_talisman_element = current_talisman.title()
                preset_update = user['U_PRESET']

                
                preset1_card = list(deck[0].values())[0]
                preset1_title = list(deck[0].values())[1]
                preset1_arm = list(deck[0].values())[2]
                preset1_pet = list(deck[0].values())[3]
                preset1_talisman = list(deck[0].values())[4]

                preset2_card = list(deck[1].values())[0]
                preset2_title = list(deck[1].values())[1]
                preset2_arm = list(deck[1].values())[2]
                preset2_pet = list(deck[1].values())[3]
                preset2_talisman = list(deck[1].values())[4]

                preset3_card = list(deck[2].values())[0]
                preset3_title = list(deck[2].values())[1]
                preset3_arm = list(deck[2].values())[2]
                preset3_pet = list(deck[2].values())[3]    
                preset3_talisman = list(deck[2].values())[4]
                
                preset3_message = "📿"
                preset3_element = "None"
                if preset3_talisman != "NULL":
                    preset3_message = crown_utilities.set_emoji(preset3_talisman)
                    preset3_element = preset3_talisman.title()
                    
                preset2_message = "📿"
                preset2_element = "None"
                if preset2_talisman != "NULL":
                    preset2_message = crown_utilities.set_emoji(preset2_talisman)
                    preset2_element = preset2_talisman.title()
                    
                preset1_message = "📿"
                preset1_element = "None"
                if preset1_talisman != "NULL":
                    preset1_message = crown_utilities.set_emoji(preset1_talisman)
                    preset1_element = preset1_talisman.title()
                
                if preset_update:
                    preset4_card = list(deck[3].values())[0]
                    preset4_title = list(deck[3].values())[1]
                    preset4_arm = list(deck[3].values())[2]
                    preset4_pet = list(deck[3].values())[3]
                    preset4_talisman = list(deck[3].values())[4]

                    preset5_card = list(deck[4].values())[0]
                    preset5_title = list(deck[4].values())[1]
                    preset5_arm = list(deck[4].values())[2]
                    preset5_pet = list(deck[4].values())[3]  
                    preset5_talisman = list(deck[4].values())[4]
                    
                    preset5_message = "📿"
                    preset5_element = "None"
                    if preset5_talisman != "NULL":
                        preset5_message = crown_utilities.set_emoji(preset5_talisman)
                        preset5_element = preset5_talisman.title()
                        
                    preset4_message = "📿"
                    preset4_element = "None"
                    if preset4_talisman != "NULL":
                        preset4_message = crown_utilities.set_emoji(preset4_talisman)
                        preset4_element = preset4_talisman.title()
                    
                    listed_options = [f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n**Talisman**: {current_talisman_message}{current_talisman_element}\n\n",
                    f"📝1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n**Talisman**: {preset1_message}{preset1_element}\n\n", 
                    f"📝2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n**Talisman**: {preset2_message}{preset2_element}\n\n", 
                    f"📝3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n**Talisman**: {preset3_message}{preset3_element}\n\n", 
                    f"📝4️⃣ | {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n**Talisman**: {preset4_message}{preset4_element}\n\n", 
                    f"📝5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n**Talisman**: {preset5_message}{preset5_element}\n\n"]  
                else:
                    listed_options = [f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n**Talisman**: {current_talisman_message}{current_talisman_element}\n\n",
                    f"📝1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n**Talisman**: {preset1_message}{preset1_element}\n\n", 
                    f"📝2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n**Talisman**: {preset2_message}{preset2_element}\n\n", 
                    f"📝3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n**Talisman**: {preset3_message}{preset3_element}\n\n"]
            
                embedVar = Embed(title=f"📝 | Save Current Build", description=textwrap.dedent(f"""
                {"".join(listed_options)}
                """), color=discord.Color.green())
                util_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="📝 1️⃣",
                        custom_id = f"{_uuid}|1"
                    ),
                    Button(
                        style=ButtonStyle.GREEN,
                        label="📝 2️⃣",
                        custom_id = f"{_uuid}|2"
                    ),
                    Button(
                        style=ButtonStyle.GREEN,
                        label="📝 3️⃣",
                        custom_id = f"{_uuid}|3"
                    )
                ]
                
                if preset_update:
                    util_buttons.append(
                        Button(
                            style=ButtonStyle.GREEN,
                            label="📝4️⃣",
                            custom_id=f"{_uuid}|4"
                        )
                    )
                    util_buttons.append(
                        Button(
                            style=ButtonStyle.GREEN,
                            label="📝5️⃣",
                            custom_id=f"{_uuid}|5"
                        )
                    )
                util_action_row = ActionRow(*util_buttons)
                msg = await ctx.send(embed=embedVar,components=[util_action_row])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx  = await self.bot.wait_for_component(components=[util_action_row], timeout=120,check=check)

                    if button_ctx.ctx.custom_id == f"{_uuid}|0":
                        embed = Embed(title=f"🔖 | Preset Not Saved", description=f"No change has been made")
                        await msg.edit(embed=embed,components=[])
                        return
                    
                    if button_ctx.ctx.custom_id in [f"{_uuid}|1", f"{_uuid}|2", f"{_uuid}|3", f"{_uuid}|4", f"{_uuid}|5"]:
                        preset_number = button_ctx.ctx.custom_id
                        response = db.updateUserNoFilter(query, {'$set': {f'DECK.{int(preset_number) - 1}.CARD': str(current_card), f'DECK.{int(preset_number) - 1}.TITLE': str(current_title), f'DECK.{int(preset_number) - 1}.ARM': str(current_arm), f'DECK.{int(preset_number) - 1}.PET': str(current_pet), f'DECK.{int(preset_number) - 1}.TALISMAN': str(current_talisman)}})
                        if response:
                            talisman_message = crown_utilities.set_emoji(current_talisman)
                            embed = Embed(title=f"🔖 | Preset Saved to {preset_number} Slot")
                            embed.add_field(name="Card", value=f"🎴 | {current_card}", inline=False)
                            embed.add_field(name="Title", value=f"🎗️ | {current_title}", inline=False)
                            embed.add_field(name="Arm", value=f"🦾 | {current_arm}", inline=False)
                            embed.add_field(name="Summons", value=f"🧬 | {current_pet}", inline=False)
                            embed.add_field(name="Talisman", value=f"{talisman_message} | {current_talisman_element}", inline=False)
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await msg.edit(embed=embed,components=[])
                            return

                except asyncio.TimeoutError:
                    embed = Embed(title=f"🔖 | Whoops!", description=f"Timed out. Please try again later.", color=discord.Color.red())
                    await ctx.send(embed=embed)
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
                    embed = Embed(title=f"🔖 | Whoops!", description=f"Something went wrong. Please try again later.", color=discord.Color.red())
                    await ctx.send(embed=embed)
                    return
            else:
                embed = Embed(title=f"🔖 | Whoops!", description=f"You are unable to save presets without an account.", color=discord.Color.red())
                await ctx.send(embed=embed)
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
            embed = Embed(title=f"🔖 | Whoops!", description=f"Something went wrong. Please try again later.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return


    # @slash_command(description="Open the shop")
    # async def shop(self, ctx):
    #     a_registered_player = await crown_utilities.player_check(ctx)
    #     if not a_registered_player:
    #         return

    #     try:
    #         all_universes = db.queryAllUniverse()
    #         user = db.queryUser({'DID': str(ctx.author.id)})
    #         storage_allowed_amount = user['STORAGE_TYPE'] * 15
    #         guild_buff = "NULL"
    #         if user["TEAM"] != "PCG":
    #             guild_info = db.queryTeam({"TEAM_NAME": str(user["TEAM"].lower())})
    #             guild_buff = guild_info["ACTIVE_GUILD_BUFF"]

    #         # if user['LEVEL'] < 1 and user['PRESTIGE'] < 1:
    #         #     await ctx.send("🔓 Unlock the Shop by completing Floor 0 of the 🌑 Abyss! Use /solo to enter the abyss.")
    #         #     return

    #         completed_tales = user['CROWN_TALES']
    #         completed_dungeons = user['DUNGEONS']
    #         available_universes = []
    #         riftShopOpen = False
    #         shopName = ':shopping_cart: Shop'
    #         if user['RIFT'] == 1 or guild_buff == "Rift":
    #             riftShopOpen = True
    #             shopName = ':crystal_ball: Rift Shop'

    #         if riftShopOpen:
    #             close_rift = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'RIFT': 0}})

                
    #         if riftShopOpen:    
    #             for uni in all_universes:
    #                 if uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
    #                     available_universes.append(uni)
    #         else:
    #             for uni in all_universes:
    #                 if uni['TIER'] != 9 and uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
    #                     available_universes.append(uni)
    #         universe_subset = random.sample(available_universes, k=min(len(available_universes), 25))
            
    #         vault_query = {'DID' : str(ctx.author.id)}
    #         vault = db.altQueryVault(vault_query)
    #         storage_amount = len(vault['STORAGE'])
    #         hand_length = len(vault['CARDS'])
    #         current_titles = vault['TITLES']
    #         current_cards = vault['CARDS']
    #         current_arms = []
    #         for arm in vault['ARMS']:
    #             current_arms.append(arm['ARM'])

    #         owned_card_levels_list = []
    #         for c in vault['CARD_LEVELS']:
    #             owned_card_levels_list.append(c['CARD'])

    #         owned_destinies = []
    #         for destiny in vault['DESTINY']:
    #             owned_destinies.append(destiny['NAME'])
                
    #         card_message = ""
    #         title_message = ""
    #         arm_message = ""
            
    #         if len(current_cards) >= 25:
    #             card_message = "🎴 *25 Full*"
    #         else:
    #             card_message = f"🎴 {len(current_cards)}"
                
    #         if len(current_titles) >= 25:
    #             title_message = "🎗️ *25 Full*"
    #         else:
    #             title_message = f"🎗️ {len(current_titles)}"
                
    #         if len(current_arms) >= 25:
    #             arm_message = "🦾 *25 Full*"
    #         else:
    #             arm_message = f"🦾 {len(current_arms)}"


    #         balance = vault['BALANCE']
    #         icon = "🪙"
    #         if balance >= 150000:
    #             icon = "💸"
    #         elif balance >=100000:
    #             icon = "💰"
    #         elif balance >= 50000:
    #             icon = "💵"


    #         embed_list = []
    #         for universe in universe_subset:
    #             t1_pre_list_of_cards = False
    #             t2_pre_list_of_cards = False
    #             t3_pre_list_of_cards = False
    #             #Universe Image and Adjusted Pricing
    #             universe_name = universe['TITLE']
    #             universe_image = universe['PATH']
    #             adjusted_prices = price_adjuster(15000, universe_name, completed_tales, completed_dungeons)
                
                
    #             #Shop Messages and Card Count
    #             t1_acceptable = [1,2,3]
    #             t2_acceptable = [3,4,5]
    #             t3_acceptable = [5,6,7]
                
                
                
    #             t1_pre_list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_name), 'TIER': {'$in': t1_acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
    #             t1_card_message = (f"💵 {'{:,}'.format(adjusted_prices['C1'])} *🎴{len(t1_pre_list_of_cards)}*")
    #             if not t1_pre_list_of_cards:
    #                 t1_card_message = ("Unavailable")
                    
    #             t2_pre_list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_name), 'TIER': {'$in': t2_acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
    #             t2_card_message = (f"💰 {'{:,}'.format(adjusted_prices['C2'])} *🎴{len(t2_pre_list_of_cards)}*")
    #             if not t2_pre_list_of_cards:
    #                 t2_card_message = ("Unavailable")
                    
    #             t3_pre_list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_name), 'TIER': {'$in': t3_acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
    #             t3_card_message = (f"💸 {'{:,}'.format(adjusted_prices['C3'])} *🎴{len(t3_pre_list_of_cards)}*")
    #             if not t3_pre_list_of_cards:
    #                 t3_card_message = ("Unavailable")

                
                
    #             embedVar = Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
    #             *Welcome {ctx.author.mention}! {adjusted_prices['MESSAGE']}
    #             You have {icon}{'{:,}'.format(balance)} coins!*
    #             {card_message} | {title_message} | {arm_message}
                
    #             🎗️ **Title:** Title Purchase for 💵 {'{:,}'.format(adjusted_prices['TITLE_PRICE'])}
    #             🦾 **Arm:** Arm Purchase for 💵 {'{:,}'.format(adjusted_prices['ARM_PRICE'])}
    #             1️⃣ **1-3 Tier Card:** for {t1_card_message}
    #             2️⃣ **3-5 Tier Card:** for {t2_card_message}
    #             3️⃣ **5-7 Tier Card:** for {t3_card_message}
    #             """), color=0x7289da)
    #             embedVar.set_image(url=universe_image)
    #             #embedVar.set_thumbnail(url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236723/PCG%20LOGOS%20AND%20RESOURCES/Party_Chat_Shop.png")
    #             embed_list.append(embedVar)

            
    #         # Pull all cards that don't require tournaments
    #         # resp = db.queryShopCards()

    #         buttons = [
    #             Button(style=3, label="🎗️", custom_id="title"),
    #             Button(style=1, label="🦾", custom_id="arm"),
    #             Button(style=2, label="1️⃣", custom_id="t1card"),
    #             Button(style=2, label="2️⃣", custom_id="t2card"),
    #             Button(style=2, label="3️⃣", custom_id="t3card"),
    #         ]

    #         custom_action_row = ActionRow(*buttons)

    #         async def custom_function(self, button_ctx):
    #             if button_ctx.author == ctx.author:
    #                 updated_vault = db.queryVault({'DID': user['DID']})
    #                 balance = updated_vault['BALANCE']        
    #                 universe = str(button_ctx.origin_message.embeds[0].title)
                    
    #                 if button_ctx.custom_id == "title":
    #                     updated_vault = db.queryVault({'DID': user['DID']})
    #                     current_titles = updated_vault['TITLES']
    #                     price = price_adjuster(50000, universe, completed_tales, completed_dungeons)['TITLE_PRICE']
    #                     bless_amount = price
    #                     # if len(current_titles) >=25:
    #                     #     await button_ctx.send("You have max amount of Titles. Transaction cancelled.")
    #                     #     self.stop = True
    #                     #     return

    #                     if price > balance:
    #                         await button_ctx.send("Insufficent funds.")
    #                         self.stop = True
    #                         return
    #                     list_of_titles =[x for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
    #                     if not list_of_titles:
    #                         await button_ctx.send("There are no titles available for purchase in this range.")
    #                         self.stop = True
    #                         return

    #                     selection_length = len(list(list_of_titles)) - 1
    #                     if selection_length ==0:
    #                         title = list_of_titles[0]
    #                     else:
    #                         selection = random.randint(0,selection_length)
    #                         title = list_of_titles[selection]  
    #                     if title['TITLE'] in current_titles:                 
    #                         bless_amount = price
    #                         bless_reduction = 0
    #                         if universe_name in completed_tales:
    #                             bless_reduction = bless_amount * .25
    #                             bless_amount = round((bless_amount - bless_reduction)/2)
    #                         if universe_name in completed_dungeons:
    #                             bless_reduction = bless_amount * .50
    #                             bless_amount = round((bless_amount - bless_reduction)/2)
    #                         else: 
    #                             bless_amount = round(bless_amount /2) #Send bless amount for price in utilities
                                
    #                     response = await crown_utilities.store_drop_card(str(ctx.author.id), title['TITLE'], universe_name, updated_vault, "Titles_NoDestinies", bless_amount, bless_amount, "Purchase", True, int(price), "titles")
    #                     await button_ctx.send(response)
    #                         # await button_ctx.send(f"You already own **{title['TITLE']}**. You get a 🪙**{'{:,}'.format(bless_amount)}** refund!") 
    #                     #     #await crown_utilities.curse(bless_amount, str(ctx.author.id)) 
    #                     # else:
    #                     #     response = db.updateUserNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})   
    #                     #     await crown_utilities.curse(price, str(ctx.author.id))
    #                     #     await button_ctx.send(f"You purchased **{title['TITLE']}**.")


    #                 elif button_ctx.custom_id == "arm":
    #                     updated_vault = db.queryVault({'DID': user['DID']})
    #                     current_arms = []
    #                     for arm in updated_vault['ARMS']:
    #                         current_arms.append(arm['ARM'])
    #                     price = price_adjuster(25000, universe, completed_tales, completed_dungeons)['ARM_PRICE']
    #                     # if len(current_arms) >=25:
    #                     #     await button_ctx.send("You have max amount of Arms. Transaction cancelled.")
    #                     #     self.stop = True
    #                     #     return
    #                     if price > balance:
    #                         await button_ctx.send("Insufficent funds.")
    #                         self.stop = True
    #                         return
    #                     list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
    #                     if not list_of_arms:
    #                         await button_ctx.send("There are no arms available for purchase in this range.")
    #                         self.stop = True
    #                         return

    #                     selection_length = len(list(list_of_arms)) - 1

    #                     if selection_length ==0:
    #                         arm = list_of_arms[0]
    #                     else:
    #                         selection = random.randint(0,selection_length)
    #                         arm = list_of_arms[selection]['ARM']
    #                     response = await crown_utilities.store_drop_card(str(ctx.author.id), arm, universe_name, updated_vault, 25, price, price, "Purchase", True, int(price), "arms")
    #                     await button_ctx.send(response)
                        
    #                     # if arm not in current_arms:
    #                     #     response = db.updateUserNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 25}}})
    #                     #     await crown_utilities.curse(price, str(ctx.author.id))
    #                     #     await button_ctx.send(f"You purchased **{arm}**.")
    #                     # else:
    #                     #     update_query = {'$inc': {'ARMS.$[type].' + 'DUR': 10}}
    #                     #     filter_query = [{'type.' + "ARM": str(arm)}]
    #                     #     resp = db.updateUser(vault_query, update_query, filter_query)
    #                     #     await crown_utilities.curse(price, str(ctx.author.id))
    #                     #     await button_ctx.send(f"You purchased **{arm}**. Increased durability for the arm by 10 as you already own it.")


    #                 elif button_ctx.custom_id == "t1card":
    #                     price = price_adjuster(100000, universe, completed_tales, completed_dungeons)['C1']
    #                     acceptable = [1,2,3]
    #                     if price > balance:
    #                         await button_ctx.send("Insufficent funds.")
    #                         self.stop = True
    #                         return
    #                     list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
    #                     if not list_of_cards:
    #                         await button_ctx.send("There are no cards available for purchase in this range.")
    #                         self.stop = True
    #                         return

    #                     selection_length = len(list(list_of_cards)) - 1
    #                     if selection_length ==0:
    #                         card = list_of_cards[0]
    #                     else:
    #                         selection = random.randint(0,selection_length)
    #                         card = list_of_cards[selection]
    #                     card_name = card['NAME']
    #                     tier = 0

    #                     response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
    #                     await button_ctx.send(response)


    #                 elif button_ctx.custom_id == "t2card":
    #                     price = price_adjuster(450000, universe, completed_tales, completed_dungeons)['C2']
    #                     acceptable = [3,4,5]
    #                     if price > balance:
    #                         await button_ctx.send("Insufficent funds.")
    #                         self.stop = True
    #                         return
    #                     list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                        
    #                     if not list_of_cards:
    #                         await button_ctx.send("There are no cards available for purchase in this range.")
    #                         self.stop = True
    #                         return
                        
    #                     selection_length = len(list(list_of_cards)) - 1

    #                     if selection_length ==0:
    #                         card = list_of_cards[0]
    #                     else:
    #                         selection = random.randint(0,selection_length)
    #                         card = list_of_cards[selection]
    #                     card_name = card['NAME']
    #                     tier = 0
                        
    #                     response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
    #                     await button_ctx.send(response)


    #                 elif button_ctx.custom_id == "t3card":
    #                     price = price_adjuster(6000000, universe, completed_tales, completed_dungeons)['C3']
    #                     acceptable = [5,6,7]
    #                     if price > balance:
    #                         await button_ctx.send("Insufficent funds.")
    #                         self.stop = True
    #                         return
    #                     card_list_response = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
    #                     if not card_list_response:
    #                         await button_ctx.send("There are no cards available for purchase in this range.")
    #                         self.stop = True
    #                         return
    #                     else:
    #                         list_of_cards = []
    #                         for card in card_list_response:
    #                             if card['AVAILABLE'] and not card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
    #                                 list_of_cards.append(card)


    #                     if not list_of_cards:
    #                         await button_ctx.send("There are no cards available for purchase in this range.")
    #                         self.stop = True
    #                         return

    #                     selection_length = len(list(list_of_cards)) - 1
    #                     if selection_length ==0:
    #                         card = list_of_cards[0]
    #                     else:
    #                         selection = random.randint(0,selection_length)
    #                         card = list_of_cards[selection]
    #                     card_name = card['NAME']
    #                     tier = 0

    #                     response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
    #                     await button_ctx.send(response)

    #             else:
    #                 await ctx.send("This is not your Shop.")
    #         await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
    #             custom_action_row,
    #             custom_function,
    #         ]).run()
    #     except Exception as ex:
    #         trace = []
    #         tb = ex.__traceback__
    #         while tb is not None:
    #             trace.append({
    #                 "filename": tb.tb_frame.f_code.co_filename,
    #                 "name": tb.tb_frame.f_code.co_name,
    #                 "lineno": tb.tb_lineno
    #             })
    #             tb = tb.tb_next
    #         print(str({
    #             'type': type(ex).__name__,
    #             'message': str(ex),
    #             'trace': trace
    #         }))


    @slash_command(description="Start crafting")
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
            guild_buff = "NONE"
            if guild_info:
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
            universe_subset = random.sample(available_universes, k=min(len(available_universes), 25))
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
            for universe in universe_subset:
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
                elif gems >= 5000000:
                    heart_message = "Craftable"
                if universe_soul:
                    soul_message = "Owned"
                elif gems >= 20000000:
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
                    
                embedVar = Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
                Welcome {ctx.author.mention}!
                You have 💎 *{'{:,}'.format(gems)}* **{universe_name}** gems !
                
                Equipped Card:  **{card_info['NAME']}** *{card_info['UNIVERSE']}*
                *{destiny_alert_message}*
                
                💟 **Universe Heart:** 💎 5,000,000 *{heart_message}*
                *Grants ability to level past 200*
                
                🌹 **Universe Soul:** 💎 20,000,000 *{soul_message}*
                *Grants double exp in this Universe*
                
                ✨ **Destiny Line:** 💎 1,500,000 *{destiny_message}*
                *Grants wins for a Destiny Line*
                
                🃏 **Card Skins:** 💎 12,000,000 *{card_skin_message}*
                *Grants Card Skin*
                
                ✨🎴 **Craft Card:** 💎 6,000,000 *{craft_card_message}*
                *Craft a random Shop or Dungeon card from this Universe*
                """), color=0x7289da)
                embedVar.set_image(url=universe_image)
                if gems == 0:
                    embedVar.set_footer(
                        text=f"💎 | Dismantle Cards or Accessories from {universe_name} to create Gems!")
                else:
                    embedVar.set_footer(
                        text=f"👾 | Fight Battles during Corruption Hour to Earn Bonus Gems!")
                embed_list.append(embedVar)
            buttons = [
                Button(style=3, label="💟", custom_id="UNIVERSE_HEART"),
                Button(style=1, label="🌹", custom_id="UNIVERSE_SOUL"),
                Button(style=1, label="✨", custom_id="Destiny"),
                Button(style=1, label="🃏", custom_id="Skin"),
                Button(style=1, label="🎴", custom_id="Card")
            ]

            custom_action_row = ActionRow(*buttons)

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
                        price = 20000000
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
                        price = 12000000
                        response = await craft_adjuster(self, ctx, vault, universe, price, card_info, new_skin_list, completed_tales)
                        await button_ctx.send(f"{response['MESSAGE']}")
                        self.stop = True
                    if button_ctx.custom_id == "Card":
                        await button_ctx.defer(ignore=True)
                        price = 6000000
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


    @slash_command(description="Draw, Dismantle or Resell cards from storage",
                    options=[
                        SlashCommandOption(
                            name="mode",
                            description="Draw: Draw card, Dismantle:  Dismantle storage card, Resll: Resell storage card",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="💼🎴 Draw Card",
                                    value="cdraw"
                                ),
                                SlashCommandChoice(
                                    name="💎🎴 Dismantle Card",
                                    value="cdismantle"
                                ),
                                SlashCommandChoice(
                                    name="🪙🎴 Resell Card",
                                    value="cresell"
                                ),SlashCommandChoice(
                                    name="💼🎗️ Draw Title",
                                    value="tdraw"
                                ),
                                SlashCommandChoice(
                                    name="💎🎗️ Dismantle Title",
                                    value="tdismantle"
                                ),
                                SlashCommandChoice(
                                    name="🪙🎗️ Resell Title",
                                    value="tresell"
                                ),SlashCommandChoice(
                                    name="💼🦾 Draw Arm",
                                    value="adraw"
                                ),
                                SlashCommandChoice(
                                    name="💎🦾 Dismantle Arm",
                                    value="adismantle"
                                ),
                                SlashCommandChoice(
                                    name="🪙🦾 Resell Arm",
                                    value="aresell"
                                )
                            ]
                        ),SlashCommandOption(
                            name="item",
                            description="Storage Item Name",
                            type=OptionType.STRING,
                            required=True,
                        )
                    ]
        )
    async def draw(self, ctx, mode : str, item : str ):
        
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
                            response = db.updateUserNoFilter(query, update_storage_query)
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
                            response = db.updateUserNoFilter(query, update_storage_query)
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
                                    #print(durability)
                            query = {'DID': str(ctx.author.id)}
                            update_storage_query = {
                                '$pull': {'ASTORAGE': {'ARM' : str(storage_arm['ARM'])}},
                                '$addToSet': {'ARMS': {'ARM' : str(storage_arm['ARM']) , 'DUR': int(durability)}},
                            }
                            response = db.updateUserNoFilter(query, update_storage_query)
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
                    essence_amount = (1000 * card_tier)
                    o_enhancer = o_moveset[3]

                    dismantle_amount = (10000 * card_tier) + card_health
                    if card_name in vault['STORAGE']:
                        dismantle_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                        msg = await ctx.send(f"Are you sure you want to dismantle **{card_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextDismantle = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                            if button_ctx.custom_id == "yes":
                                if selected_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                    response = db.updateUser(query, update_query, filter_query)
                                else:
                                    response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'STORAGE': card_name}})
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
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
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                            return
                    else:
                        await ctx.send(f"**{card_name}** not in storage.. Please check spelling", ephemeral=True)
                        return
                if mode == 'tdismantle':
                    title_data = storage_title
                    title_name = title_data['TITLE']
                    dismantle_amount = 1000
                    selected_universe = title_data['UNIVERSE']
                    if title_name in vault['TSTORAGE']:
                        dismantle_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                        msg = await ctx.send(f"Are you sure you want to dismantle **{title_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextDismantle = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                            if button_ctx.custom_id == "yes":
                                if selected_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                    response = db.updateUser(query, update_query, filter_query)
                                else:
                                    response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TSTORAGE': title_name}})
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
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                            return
                    else:
                        await ctx.send(f"**{title_name}** not in storage.. Please check spelling", ephemeral=True)
                        return
                if mode == 'adismantle':
                    arm_data = storage_arm
                    arm_name = arm_data['ARM']
                    element = arm_data['ELEMENT']
                    essence_amount = 1000
                    arm_passive = arm_data['ABILITIES'][0]
                    arm_passive_type = list(arm_passive.keys())[0]
                    arm_passive_value = list(arm_passive.values())[0]
                    move_types = ["BASIC", "SPECIAL", "ULTIMATE"]
                    if arm_data["EXCLUSIVE"]:
                        essence_amount = 2000
                    selected_universe = arm_data['UNIVERSE']
                    dismantle_amount = 10000
                    storage_arm_names = []
                    for names in vault['ASTORAGE']:
                        if arm_name == names['ARM']:
                            storage_arm_names = names['ARM']
                    if arm_name == storage_arm_names:
                        dismantle_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                        msg = await ctx.send(f"Are you sure you want to dismantle **{arm_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextDismantle = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Dismantle cancelled. ")
                            if button_ctx.custom_id == "yes":
                                if selected_universe in current_gems:
                                    query = {'DID': str(ctx.author.id)}
                                    update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                    filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                    response = db.updateUser(query, update_query, filter_query)
                                else:
                                    response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ASTORAGE': {'ARM' : str(arm_name)}}})
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
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                            return
                    else:
                        await ctx.send(f"**{card_name}** not in storage.. Please check spelling", ephemeral=True)
                        return
                if mode == 'cresell':
                    card_data = storage_card
                    card_name = card_data['NAME']
                    sell_price = 0
                    sell_price = sell_price + (card_data['PRICE'] * .15)
                    if card_name in vault['STORAGE']:
                        sell_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        sell_buttons_action_row = ActionRow(*sell_buttons)
                        msg = await ctx.send(f"Are you sure you want to sell **{card_name}** for 🪙{round(sell_price)}?", components=[sell_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx: ComponentContextSell = await self.bot.wait_for_component(components=[sell_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Sell cancelled. ")
                            if button_ctx.custom_id == "yes":
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'STORAGE': card_name}})
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
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
                        await ctx.send(f"**{card_name}** not in storage.. Please check spelling", ephemeral=True)
                        return
                if mode == 'tresell':
                    title_data = storage_title
                    title_name = title_data['TITLE']
                    sell_price = 1
                    sell_price = sell_price + (title_data['PRICE'] * .10)
                    selected_universe = title_data['UNIVERSE']
                    if title_name in vault['TSTORAGE']:
                        sell_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        sell_buttons_action_row = ActionRow(*sell_buttons)
                        msg = await ctx.send(f"Are you sure you want to sell **{title_name}** for 🪙 {round(sell_price)}?", components=[sell_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx  = await self.bot.wait_for_component(components=[sell_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Sell cancelled. ")
                            if button_ctx.custom_id == "yes":
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TSTORAGE': title_name}})
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
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                            return
                    else:
                        await ctx.send(f"**{title_name}** not in storage.. Please check spelling", ephemeral=True)
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
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        sell_buttons_action_row = ActionRow(*sell_buttons)
                        msg = await ctx.send(f"Are you sure you want to sell **{arm_name}** for 🪙 {round(sell_price)}?", components=[sell_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx  = await self.bot.wait_for_component(components=[sell_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "no":
                                await button_ctx.send("Sell cancelled. ")
                            if button_ctx.custom_id == "yes":
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ASTORAGE': {'ARM' :str(arm_name)}}})
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
                            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                            return
                    else:
                        await ctx.send(f"**{title_name}** not in storage.. Please check spelling", ephemeral=True)
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
            await ctx.send(f"Error with Storage. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
            return


    @slash_command(description="Draw Items from Association Armory",
                options=[
                    SlashCommandOption(
                        name="mode",
                        description="Draw: Draw card, Dismantle:  Dismantle storage card, Resll: Resell storage card",
                        type=OptionType.STRING,
                        required=True,
                        choices=[
                            SlashCommandChoice(
                                name="🕋 🎴 Draw Armory Card",
                                value="cdraw"
                            ),SlashCommandChoice(
                                name="🕋 🎗️ Draw Armory Title",
                                value="tdraw"
                            ),SlashCommandChoice(
                                name="🕋 🦾 Draw Armory Arm",
                                value="adraw"
                            ),
                        ]
                    ),SlashCommandOption(
                        name="item",
                        description="Storage Item Name",
                        type=OptionType.STRING,
                        required=True,
                    )
                ]
        )
    async def armory(self, ctx, mode:str, item:str):
        
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)#Storage Update
        team = db.queryTeam({'TEAM_NAME': d['TEAM'].lower()})
        guild = db.queryGuildAlt({'GNAME': team['GUILD']})
        guild_name = ""
        if guild:
            guild_name = guild['GNAME']
            #in_guild = True
            guild_query = {"GNAME": guild['GNAME']}
        else:
            await ctx.send("Your Guild is not Associated.")
            return
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
                card_levels = vault['CARD_LEVELS']
                title_list = vault['TITLES']
                arm_list = vault['ARMS']
                arm_list_names = []
                for names in arm_list:
                    arm_list_names.append(names['ARM'])
                total_cards = len(cards_list)
                total_titles = len(title_list)
                total_arms = len(arm_list)
                cstorage = guild['CSTORAGE']
                cstorage_levels = guild['S_CARD_LEVELS']
                tstorage = guild['TSTORAGE']
                astorage = guild['ASTORAGE']
                storage_arm_names = []
                item_owned = False
                levels_owned = False
                for snames in astorage:
                    storage_arm_names.append(snames['ARM'])
                
                storage_card = db.queryCard({'NAME': {"$regex": f"^{str(item)}$", "$options": "i"}})
                storage_title = db.queryTitle({'TITLE':{"$regex": f"^{str(item)}$", "$options": "i"} })
                storage_arm = db.queryArm({'ARM':{"$regex": f"^{str(item)}$", "$options": "i"}})
                lvl = 0
                tier = 0
                exp = 0
                ap_buff = 0
                atk_buff = 0
                def_buff = 0
                hlt_buff = 0
                if mode == 'cdraw':
                    if total_cards > 24:
                        await ctx.send("You already have 25 cards.")
                        return
                    if storage_card:                  
                        if storage_card['NAME'] in cstorage:
                            if storage_card['NAME'] in cards_list:
                                item_owned = True
                            if not item_owned:
                                for levels in cstorage_levels:
                                    if levels['CARD'] == storage_card['NAME']:
                                        lvl = levels['LVL']
                                        tier = levels['TIER']
                                        exp = levels['EXP']
                                        ap_buff = levels['AP']
                                        atk_buff = levels['ATK']
                                        def_buff = levels['DEF']
                                        hlt_buff = levels['HLT']
                                for c in card_levels:
                                    if c['CARD'] == storage_card['NAME']:
                                        levels_owned = True
                                                            
                            
                            if not item_owned:
                                transaction_message = f"{ctx.author} claimed 🎴**{storage_card['NAME']}**."
                                query = {'DID': str(ctx.author.id)}
                                update_gstorage_query = {
                                    '$pull': {'CSTORAGE': storage_card['NAME'], 'S_CARD_LEVELS' : {'CARD' :  storage_card['NAME']}},
                                    '$push': {'TRANSACTIONS': transaction_message}
                                }
                                response = db.updateGuildAlt(guild_query, update_gstorage_query)
                                update_storage_query = {
                                    '$addToSet': {'CARDS': storage_card['NAME']},
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)
                                if not levels_owned:
                                    update_glevel_query = {
                                    '$addToSet' : {
                                            'CARD_LEVELS': {'CARD': str(storage_card['NAME']), 'LVL': lvl, 'TIER': tier, 'EXP': exp,
                                                            'HLT': hlt_buff, 'ATK': atk_buff, 'DEF': def_buff, 'AP': ap_buff}}
                                    }
                                    response = db.updateUserNoFilter(query, update_glevel_query)
                            else:
                                await ctx.send(f"🎴**{storage_card['NAME']}** already owned**")
                                return
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
                            if storage_title['TITLE'] in title_list:
                                item_owned = True
                            if not item_owned:
                                transaction_message = f"{ctx.author} claimed 🎗️ **{storage_title['TITLE']}**."
                                query = {'DID': str(ctx.author.id)}
                                update_storage_query = {
                                    '$addToSet': {'TITLES': storage_title['TITLE']},
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)
                                update_gstorage_query = {
                                        '$pull': {'TSTORAGE': storage_title['TITLE']},
                                        '$push': {'TRANSACTIONS': transaction_message}
                                    }
                                response = db.updateGuildAlt(guild_query, update_gstorage_query)
                                transaction_message = f"{ctx.author} claimed 🎗️ **{storage_title['TITLE']}****."
                            else:
                                await ctx.send(f"🎗️ **{storage_title['TITLE']}** already owned**")
                                return
                            
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
                            if storage_arm['ARM'] in arm_list_names:
                                item_owned = True
                            durability = 0
                            for arms in astorage:
                                if storage_arm['ARM'] == arms['ARM']:
                                    durability = arms['DUR']
                                    #print(durability)
                            if not item_owned:
                                transaction_message = f"{ctx.author} claimed 🦾 **{storage_arm['ARM']}**."
                                query = {'DID': str(ctx.author.id)}
                                update_storage_query = {
                                    '$addToSet': {'ARMS': {'ARM' : str(storage_arm['ARM']) , 'DUR': int(durability)}},
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)
                                update_gstorage_query = {
                                    '$pull': {'ASTORAGE': {'ARM' : str(storage_arm['ARM'])}},
                                    '$push': {'TRANSACTIONS': transaction_message}
                                }
                                response = db.updateGuildAlt(guild_query, update_gstorage_query)
                            else:
                                await ctx.send(f"🦾 **{storage_arm['ARM']}** already owned**")
                                return
                            await ctx.send(f"🦾 **{storage_arm['ARM']}** has been added to **/arms**")
                            return
                        else:
                            await ctx.send(f"🦾 :{storage_arm['ARM']} does not exist in storage.")
                            return
                    else:
                        await ctx.send(f"🦾 :{storage_arm['ARM']} does not exist.")
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
            await ctx.send(f"Error with Armory. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
            return


    @slash_command(description="Equip an Arm")
    async def equiparm(self, ctx, arm_name: str):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        resp = db.queryArm({'ARM': {"$regex": f"^{str(arm_name)}$", "$options": "i"}})

        player = crown_utilities.create_player_from_data(user)
        a = crown_utilities.create_arm_from_data(resp)

        
        if a:
            try:
                equipped = False
                for arm in player.arms:
                    if a.name == arm['ARM']:
                        response = db.updateUserNoFilter(user_query, {'$set': {'ARM': str(a.name)}})
                        equipped = True
                        embed = Embed(title="🦾 Arm Successfully Equipped", description=f"**{a.name}** has been equipped.", color=0x00ff00)
                        await ctx.send(embed=embed)

                if not equipped:
                    embed = Embed(title="🦾 Arm Not Equipped", description=f"You do not own the arm {a.name}", color=0x00ff00)
                    await ctx.send(embed=embed)
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
            embed = Embed(title="Whoops!", description="Arm not found.", color=0x00ff00)
            await ctx.send(embed=embed)
            return


    @slash_command(description="Equip a Summon")
    async def equipsummon(self, ctx, summon: str): 
        user = await crown_utilities.player_check(ctx)
        if not user:
            return
        try:
            pet_name = summon.upper()
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)

            selected_pet = next((pet for pet in player.summons if pet_name == pet['NAME'].upper()), None)

            if selected_pet:
                response = db.updateUserNoFilter(user_query, {'$set': {'PET': selected_pet['NAME']}})
                embed = Embed(title=f"🐦 Summon Equipped!", description=f"{selected_pet['NAME']} is now your active summon!", color=0x00ff00)
                await ctx.send(embed=embed)
            else:
                embed = Embed(title=f"🐦 Summon Not Found!", description=f"You do not have a summon named {summon}!", color=0xff0000)
                await ctx.send(embed=embed)
                return
        except Exception as e:
            print(e)
            embed = Embed(title=f"🐦 Summon Not Found!", description=f"You do not have a summon named {summon}!", color=0xff0000)
            await ctx.send(embed=embed)
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
                            res = db.updateUser(query, update_query, filter_query)
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
                            #print(price_)
                            embed_list = []
                            for destiny in cards_destiny_list:
                                embedVar = Embed(title= f"{destiny['DEFEAT']}", description=textwrap.dedent(f"""
                                ✨ **{destiny['NAME']}**

                                **Wins** - *{destiny['WINS']}*
                                **Wins Required To Complete** - *{destiny['REQUIRED']}*
                                **Defeat** - *{destiny['DEFEAT']}*
                                **Reward** - **{destiny['EARN']}**
                                """), color=0x7289da)
                                embedVar.set_footer(text=f"Select a Destiny Line to apply win to")
                                embed_list.append(embedVar)
                            

                            try:

                                buttons = [
                                    Button(style=3, label="Craft Win", custom_id="craft_d_win"),
                                    Button(style=3, label="Craft +5 Wins", custom_id="craft_d_win5"),
                                    Button(style=3, label="Craft +10 Wins", custom_id="craft_d_win10")
                                ]
                                custom_action_row = ActionRow(*buttons)

                                async def custom_function(self, button_ctx):
                                    if button_ctx.author == player.author:
                                        price_ = 1500000
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
                                                    res = db.updateUser(query, update_query, filter_query)
                                                    await button_ctx.send(f":sparkles: | Crafting 1 Destiny Win....Success!")
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
                                            #print(price_)
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
                                                    res = db.updateUser(query, update_query, filter_query)
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
                                                    res = db.updateUser(query, update_query, filter_query)
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
                                response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Craft Unsuccessful!"}
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
                                        passive_num = passive_num
                                    if passive_type == "HASTE":
                                        passive_num = passive_num
                                    if passive_type == "GAMBLE":
                                        passive_num = passive_num
                                    if passive_type == "SOULCHAIN":
                                        passive_num = passive_num + 90
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
                                embedVar = Embed(title= f"{skins['NAME']}", description=textwrap.dedent(f"""
                                🀄 {skins['TIER']}: 🃏 **{skins['SKIN_FOR']}** 
                                ❤️ **{skins['HLT']}** 🗡️ **{skins['ATK']}** 🛡️ **{skins['DEF']}**
                                
                                {basic_attack_emoji} **{move1name}:** {move1ap}
                                {super_attack_emoji} **{move2name}:** {move2ap}
                                {ultimate_attack_emoji} **{move3name}:** {move3ap}
                                🦠 **{enhmove}:** {enh} {enhap}{enhancer_suffix_mapping[enh]}

                                🩸 **{passive_name}:** {passive_type} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}
                                ♾️ {traitmessage}
                                **Universe** - *{skins['UNIVERSE']}*
                                """), color=0x7289da)
                                embedVar.set_footer(text=f"Select a Skin!")
                                embedVar.set_image(url="attachment://image.png")
                                embed_list.append(embedVar)
                        try:

                            buttons = [
                                Button(style=3, label="Craft Skin", custom_id="craft_skin")
                            ]
                            custom_action_row = ActionRow(*buttons)

                            async def custom_function(self, button_ctx):
                                if button_ctx.author == player.author:
                                    selected_skin = str(button_ctx.origin_message.embeds[0].title)
                                    if button_ctx.custom_id == "craft_skin":
                                        #r = await update_destiny_call(button_ctx.author, selected_destiny, "Tales")
                                        
                                        query = {'DID': str(vault['DID'])}
                                        skin_response = db.updateUserNoFilter(query,{'$addToSet': {'CARDS': str(selected_skin)}})
                                        
                                        # Add Card Level config
                                        if selected_skin not in owned_card_levels_list:
                                            update_query = {'$addToSet': {
                                                'CARD_LEVELS': {'CARD': str(selected_skin), 'LVL': 0, 'TIER': int(0),
                                                                'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                                            r = db.updateUserNoFilter(query, update_query)
                                        
                                        #Add Destiny
                                        for destiny in d.destiny:
                                            if selected_skin in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                                                db.updateUserNoFilter(query, {'$addToSet': {'DESTINY': destiny}})
                                                await button_ctx.send(
                                                    f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.", ephemeral=True)
                                        update_query = {
                                            '$inc': {'GEMS.$[type].' + "GEMS": int(negPriceAmount)}
                                        }
                                        filter_query = [{'type.' + "UNIVERSE": universe}]
                                        res = db.updateUser(query, update_query, filter_query)
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
                            response = {"HAS_GEMS_FOR": True, "SUCCESS":  False, "MESSAGE": f"Craft Unsuccessful!"}
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
                    res = db.updateUser(query, update_query, filter_query)

                    if item == "UNIVERSE_HEART":
                        response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "💟 | Heart Crafting Success!"}
                        return response
                    elif item == "UNIVERSE_SOUL":
                        response = {"HAS_GEMS_FOR": True, "SUCCESS":  True, "MESSAGE": "🌹 | Soul Crafting Success!"}
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
        
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        card = db.queryCard({'NAME':str(d['CARD'])})
        title = db.queryTitle({'TITLE': str(d['TITLE'])})
        arm = db.queryArm({'ARM': str(d['ARM'])})
        vault = db.queryVault({'DID': d['DID']})
        if not all([card, title, arm, d]):
            # Handle error if one of the database calls fails
            return "Error: One or more of the required data is not available."

        if card:
            try:
                #print(d['TALISMAN'])
                c = Card(card['NAME'], card['PATH'], card['PRICE'], card['EXCLUSIVE'], card['AVAILABLE'], card['IS_SKIN'], card['SKIN_FOR'], card['HLT'], card['HLT'], card['STAM'], card['STAM'], card['MOVESET'], card['ATK'], card['DEF'], card['TYPE'], card['PASS'][0], card['SPD'], card['UNIVERSE'], card['HAS_COLLECTION'], card['TIER'], card['COLLECTION'], card['WEAKNESS'], card['RESISTANT'], card['REPEL'], card['ABSORB'], card['IMMUNE'], card['GIF'], card['FPATH'], card['RNAME'], card['RPATH'], False, card['CLASS'])
                t = Title(title['TITLE'], title['UNIVERSE'], title['PRICE'], title['EXCLUSIVE'], title['AVAILABLE'], title['ABILITIES'])            
                a = Arm(arm['ARM'], arm['UNIVERSE'], arm['PRICE'], arm['ABILITIES'], arm['EXCLUSIVE'], arm['AVAILABLE'], arm['ELEMENT'])
                player = Player(d['AUTOSAVE'], d['DISNAME'], d['DID'], d['AVATAR'], d['GUILD'], d['TEAM'], d['FAMILY'], d['TITLE'], d['CARD'], d['ARM'], d['PET'], d['TALISMAN'], d['CROWN_TALES'], d['DUNGEONS'], d['BOSS_WINS'], d['RIFT'], d['REBIRTH'], d['LEVEL'], d['EXPLORE'], d['SAVE_SPOT'], d['PERFORMANCE'], d['TRADING'], d['BOSS_FOUGHT'], d['DIFFICULTY'], d['STORAGE_TYPE'], d['USED_CODES'], d['BATTLE_HISTORY'], d['PVP_WINS'], d['PVP_LOSS'], d['RETRIES'], d['PRESTIGE'], d['PATRON'], d['FAMILY_PET'], d['EXPLORE_LOCATION'], d['SCENARIO_HISTORY'])                 
                
                durability = a.set_durability(player.equipped_arm, player.arms)
                
                c.set_card_level_buffs(player.card_levels)
                c.set_affinity_message()
                c.set_arm_config(a.passive_type, a.name, a.passive_value, a.element)
                # c.set_passive_values()
                
                x = 0.0999
                y = 1.25
                lvl_req = round((float(c.card_lvl)/x)**y)

                player.set_talisman_message()
                player.setsummon_messages()

                a.set_arm_message(player.performance, c.universe)
                t.set_title_message(player.performance, c.universe)
                
                has_universe_heart = False
                has_universe_soul = False
                pokemon_uni =["Kanto Region","Johto Region","Hoenn Region","Sinnoh Region","Kalos Region","Unova Region","Alola Region","Galar Region"]
                
                if card['UNIVERSE'] != "n/a":
                    for gems in vault['GEMS']:
                        if gems['UNIVERSE'] == card['UNIVERSE'] and gems['UNIVERSE_HEART']:
                            has_universe_heart = True
                        if gems['UNIVERSE'] == card['UNIVERSE'] and gems['UNIVERSE_SOUL']:
                            has_universe_soul = True
                
                trebirth_message = f"_⚔️Tales: +0_"
                drebirth_message = f"_🔥Dungeon: +0_"
                trebirthBonus = (player.rebirth + (player.prestige * 10) + 25)
                drebirthBonus = ((player.rebirth + 1) * ((player.prestige * 10) + 100))
                if player.prestige > 0:
                    trebirthBonus = trebirthBonus * player.prestige
                    drebirthBonus = drebirthBonus * player.prestige
                if player.rebirth > 0:
                    trebirth_message = f"_⚔️Tales: {trebirthBonus}xp_"
                    drebirth_message = f"_🔥Dungeon: {drebirthBonus}xp_"
                if has_universe_soul:
                    trebirthBonus = (player.rebirth + (player.prestige * 10) + 25) * 4
                    drebirthBonus = ((player.rebirth + 1) * ((player.prestige * 10) + 100)) * 4
                    trebirth_message = f"_🌹⚔️Tales: {trebirthBonus}xp_"
                    drebirth_message = f"_🌹🔥Dungeon: {drebirthBonus}xp_"

                level_up_message = lvl_req - c.card_exp
                if lvl_req - c.card_exp <= 0:
                    level_up_message = "🎆 Battle To Level Up!"
                if c.card_lvl >= 1000:
                    level_up_message = "👑 | Max Level!!"

                if player.performance:
                    embedVar = Embed(title=f"{c.set_card_level_icon()} | {c.card_lvl} {c.name}".format(self), description=textwrap.dedent(f"""\
                    🀄 | **{c.tier}**
                    {crown_utilities.class_emojis[c.card_class]} | **{c.class_message}**
                    ❤️ | **{c.max_health}**
                    🗡️ | **{c.attack}**
                    🛡️ | **{c.defense}**
                    🏃 | **{c.speed}**


                    **{t.title_message}**
                    **{a.arm_message}**
                    **{player.talisman_message}**
                    {player.summon_power_message}
                    {player.summon_lvl_message}

                    🩸 | **{c.passive_name}:** {c.passive_type} {c.passive_num} {passive_enhancer_suffix_mapping[c.passive_type]}                
                    
                    {c.move1_emoji} **{c.move1}:** {c.move1ap}
                    {c.move2_emoji} **{c.move2}:** {c.move2ap}
                    {c.move3_emoji} **{c.move3}:** {c.move3ap}
                    🦠 | **{c.move4}:** {c.move4enh} {c.move4ap}{enhancer_suffix_mapping[c.move4enh]}

                    ♾️ {c.set_trait_message()}
                    """),color=000000)
                    embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                    embedVar.set_image(url="attachment://image.png")
                    if c.card_lvl < 1000:
                        embedVar.set_footer(text=f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}")
                    else:
                        embedVar.set_footer(text=f"{level_up_message}")
                    embedVar.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
                    
                    await ctx.send(embed=embedVar)
                
                else:
                    card_file = c.showcard("non-battle", a, t, 0, 0)

                    embedVar = Embed(title=f"".format(self), color=000000)
                    embedVar.add_field(name="__Class__", value=f"{crown_utilities.class_emojis[c.card_class]} {c.class_message}", inline=False)
                    embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                    embedVar.set_image(url="attachment://image.png")
                    embedVar.set_author(name=textwrap.dedent(f"""\
                    __Equipment__
                    {t.title_message}
                    {a.arm_message}
                    {player.talisman_message}
                    {player.summon_power_message}
                    {player.summon_lvl_message}
                    __Passives__
                    🩸 | {c.passive_name}      
                    🏃 | {c.speed}
                    """))
                    embedVar.set_thumbnail(url=ctx.author.avatar_url)
                    if c.card_lvl < 1000:
                        embedVar.set_footer(text=f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}\n♾️ | {c.set_trait_message()}")
                    else:
                        embedVar.set_footer(text=f"{level_up_message}\n♾️ | {c.set_trait_message()}")
                    
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
                await ctx.send("There's an issue with your build. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                return
        else:
            await ctx.send(m.USER_NOT_REGISTERED, ephemeral=True)
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


async def menuessence(self, ctx: InteractionContext):
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
            embedVar = Embed(title=f"🪔 Essence", description="\n".join(essence_details),
                                    color=0x7289da)
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(essence_broken_up)):
            embedVar = Embed(title=f"🪔 Essence",
                                                        description="\n".join(essence_broken_up[i]), color=0x7289da)
            embed_list.append(embedVar)

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
            icon = "🪙"
            if balance >= 150000:
                icon = "💸"
            elif balance >=100000:
                icon = "💰"
            elif balance >= 50000:
                icon = "💵"
            
            embed_list = []

            for card in cards_list:
                index = cards_list.index(card)
                resp = db.queryCard({"NAME": str(card)})
                card_tier = 0
                lvl = ""
                tier = ""
                speed = 0
                card_tier = f"🀄 {resp['TIER']}"
                card_available = resp['AVAILABLE']
                card_exclusive = resp['EXCLUSIVE']
                card_collection = resp['HAS_COLLECTION']
                show_img = db.queryUniverse({'TITLE': resp['UNIVERSE']})['PATH']
                affinity_message = crown_utilities.set_affinities(resp)
                o_show = resp['UNIVERSE']
                icon = "🎴"
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
                    traitmessage = f"**{mytrait['EFFECT']}|** {mytrait['TRAIT']}"


                embedVar = Embed(title= f"{resp['NAME']}", description=textwrap.dedent(f"""\
                {icon} **[{index}]** 
                {card_tier}: {lvl}
                🥋 {resp["CLASS"].title()}
                ❤️ **{resp['HLT']}** 🗡️ **{resp['ATK']}** 🛡️ **{resp['DEF']}** 🏃 **{resp['SPD']}**

                {move1_emoji} **{move1}:** {move1ap}
                {move2_emoji} **{move2}:** {move2ap}
                {move3_emoji} **{move3}:** {move3ap}
                🦠 **{move4}:** {move4enh} {move4ap}{enhancer_suffix_mapping[move4enh]}

                🩸 **{passive_name}:** {passive_type.title()} {passive_num}{passive_enhancer_suffix_mapping[passive_type]}
                ♾️ {traitmessage}
                """), color=0x7289da)
                embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                embedVar.set_thumbnail(url=show_img)
                embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                embed_list.append(embedVar)

            buttons = [
                Button(style=3, label="Equip", custom_id="Equip"),
                Button(style=1, label="Resell/Dismantle", custom_id="Econ"),
                Button(style=1, label="Trade", custom_id="Trade"),
                Button(style=2, label="Swap/Store", custom_id="Storage")
            ]
            custom_action_row = ActionRow(*buttons)
            # custom_button = Button(style=3, label="Equip")

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
                            await button_ctx.send(f"🎴 **{selected_card}** equipped.")
                            self.stop = True
                        else:
                            await button_ctx.send(f"**{selected_card}** is no longer in your vault.")
                    
                    elif button_ctx.custom_id == "Econ":
                        await button_ctx.defer(ignore=True)
                        econ_buttons = [
                                    Button(
                                        style=ButtonStyle.GREEN,
                                        label="Resell",
                                        custom_id="resell"
                                    ),
                                    Button(
                                        style=ButtonStyle.RED,
                                        label="Dismantle",
                                        custom_id="dismantle"
                                    )
                                ]
                        econ_buttons_action_row = ActionRow(*econ_buttons)
                        msg = await ctx.send(f"Would you like to Resell or Dismantle", components=[econ_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx  = await self.bot.wait_for_component(components=[econ_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "resell":
                                await button_ctx.defer(ignore=True)
                                card_data = db.queryCard({'NAME': selected_card})
                                card_name = card_data['NAME']
                                sell_price = sell_price + (card_data['PRICE'] * .15)
                                if sell_price >= 25000000:
                                    sell_price = 25000000
                                if card_name == current_card:
                                    await button_ctx.send("You cannot resell equipped cards.")
                                elif card_name in updated_vault['CARDS']:
                                    sell_buttons = [
                                        Button(
                                            style=ButtonStyle.GREEN,
                                            label="Yes",
                                            custom_id="yes"
                                        ),
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label="No",
                                            custom_id="no"
                                        )
                                    ]
                                    sell_buttons_action_row = ActionRow(*sell_buttons)
                                    msg = await button_ctx.send(f"Are you sure you want to sell **{card_name}** for 🪙{round(sell_price)}?", components=[sell_buttons_action_row])
                                    
                                    def check(button_ctx):
                                        return button_ctx.author == ctx.author

                                    
                                    try:
                                        button_ctx: ComponentContextSell = await self.bot.wait_for_component(components=[sell_buttons_action_row], timeout=120, check=check)

                                        if button_ctx.custom_id == "no":
                                            await button_ctx.send("Sell cancelled. ")
                                        if button_ctx.custom_id == "yes":
                                            db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARDS': card_name}})
                                            db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
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
                                essence_amount = (1000 * card_tier)
                                o_enhancer = o_moveset[3]

                                dismantle_amount = (10000 * card_tier) + card_health
                                if card_name == current_card:
                                    await button_ctx.send("You cannot dismantle equipped cards.")
                                elif card_name in updated_vault['CARDS']:
                                    dismantle_buttons = [
                                        Button(
                                            style=ButtonStyle.GREEN,
                                            label="Yes",
                                            custom_id="yes"
                                        ),
                                        Button(
                                            style=ButtonStyle.BLUE,
                                            label="No",
                                            custom_id="no"
                                        )
                                    ]
                                    dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                                    msg = await button_ctx.send(f"Are you sure you want to dismantle **{card_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                                    
                                    def check(button_ctx):
                                        return button_ctx.author == ctx.author

                                    
                                    try:
                                        button_ctx: ComponentContextDismantle = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

                                        if button_ctx.custom_id == "no":
                                            await button_ctx.send("Dismantle cancelled. ")
                                        if button_ctx.custom_id == "yes":
                                            if selected_universe in current_gems:
                                                query = {'DID': str(ctx.author.id)}
                                                update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                                filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                                response = db.updateUser(query, update_query, filter_query)
                                            else:
                                                response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                            em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                            db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARDS': card_name}})
                                            db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'CARD_LEVELS': {'CARD': card_name}}})
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
                                    Button(
                                        style=ButtonStyle.GREEN,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = ActionRow(*trade_buttons)
                                await button_ctx.send(f"Would you like to remove **{selected_card}** from the **Trade**?", components=[trade_buttons_action_row])
                                
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author

                                
                                try:
                                    button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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
                                    Button(
                                        style=ButtonStyle.GREEN,
                                        label="Yes",
                                        custom_id="yes"
                                    ),
                                    Button(
                                        style=ButtonStyle.BLUE,
                                        label="No",
                                        custom_id="no"
                                    )
                                ]
                                trade_buttons_action_row = ActionRow(*trade_buttons)
                                await button_ctx.send(f"Are you sure you want to trade **{selected_card}**", components=[trade_buttons_action_row])
                                try:
                                    button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120)
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
                                    Button(
                                        style=ButtonStyle.GREEN,
                                        label="Swap Storage Card",
                                        custom_id="swap"
                                    ),
                                    Button(
                                        style=ButtonStyle.RED,
                                        label="Add to Storage",
                                        custom_id="store"
                                    )
                                ]
                        storage_buttons_action_row = ActionRow(*storage_buttons)
                        msg = await ctx.send(f"Would you like to Swap Cards or Add Card to Storage", components=[storage_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContextStorage = await self.bot.wait_for_component(components=[storage_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "swap":
                                await button_ctx.defer(ignore=True)
                                await msg.delete()
                                await ctx.send(f"{ctx.author.mention}, Which card number would you like to swap with in storage?\n*Discord has changed their policy on message intents..while we troubleshoot this issue please use this command in DMS.\nIt will not work in server...*")
                                def check(msg):
                                    return msg.author == ctx.author

                                try:
                                    msg = await self.bot.wait_for('on_message_create', check=check, timeout=30)
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
                                        response = db.updateUserNoFilter(query, update_storage_query)

                                        update_storage_query = {
                                            '$pull': {'STORAGE': swap_with},
                                            '$addToSet': {'CARDS': swap_with}
                                        }
                                        response = db.updateUserNoFilter(query, update_storage_query)

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
                                        response = db.updateUserNoFilter(query, update_storage_query)
                                        
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
        await ctx.send("There's an issue with loading your cards. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
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
            await ctx.send("Your storage is empty.", ephemeral=True)
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
                    f"[{str(index)}] 🀄 {card['TIER']} **{card['NAME']}**\n**{level_icon}**: {str(level)} ❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")
            elif not card['HAS_COLLECTION']:
                tales_card_details.append(
                    f"[{str(index)}] 🀄 {card['TIER']} **{card['NAME']}**\n**{level_icon}**: {str(level)} ❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")
            elif card['HAS_COLLECTION']:
                destiny_card_details.append(
                    f"[{str(index)}] 🀄 {card['TIER']} **{card['NAME']}**\n**{level_icon}**: {str(level)} ❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")

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
            embedVar = Embed(title=f"💼 {user['DISNAME']}'s Storage", description="\n".join(all_cards), color=0x7289da)
            embedVar.set_footer(
                text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(vault['STORAGE']))} Storage Available")
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(cards_broken_up)):
            embedVar = Embed(
                title=f"💼 {user['DISNAME']}'s Storage",
                description="\n".join(cards_broken_up[i]), color=0x7289da)
            embedVar.set_footer(
                text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(vault['STORAGE']))} Storage Available")
            embed_list.append(embedVar)

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
            icon = "🪙"
            if balance >= 150000:
                icon = "💸"
            elif balance >=100000:
                icon = "💰"
            elif balance >= 50000:
                icon = "💵"


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
                
                
                embedVar = Embed(title= f"{resp['TITLE']}", description=textwrap.dedent(f"""
                {icon} **[{index}]**
                🦠 **{title_passive_type}:** {title_passive_value}
                🌍 **Universe:** {resp['UNIVERSE']}"""), 
                color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                embedVar.set_footer(text=f"{title_passive_type}: {title_enhancer_mapping[title_passive_type]}")
                embed_list.append(embedVar)
            
            buttons = [
                Button(style=3, label="Equip", custom_id="Equip"),
                Button(style=1, label="Resell", custom_id="Resell"),
                Button(style=1, label="Dismantle", custom_id="Dismantle"),
                Button(style=1, label="Trade", custom_id="Trade"),
                Button(style=2, label="Swap/Store", custom_id="Storage")
            ]
            custom_action_row = ActionRow(*buttons)

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
                        if sell_price >= 5000000:
                            sell_price = 5000000
                        if title_name == current_title:
                            await button_ctx.send("You cannot resell equipped titles.")
                        elif title_name in updated_vault['TITLES']:
                            sell_buttons = [
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            sell_buttons_action_row = ActionRow(*sell_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to sell **{title_name}** for 🪙{round(sell_price)}?", components=[sell_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[sell_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Sell cancelled. Please press the Exit button if you are done reselling titles.")
                                if button_ctx.custom_id == "yes":
                                    db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TITLES': title_name}})
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
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to dismantle **{title_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Dismantle cancelled. ")
                                if button_ctx.custom_id == "yes":
                                    if selected_universe in current_gems:
                                        query = {'DID': str(ctx.author.id)}
                                        update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                        filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                        response = db.updateUser(query, update_query, filter_query)
                                    else:
                                        response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})

                                    db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'TITLES': title_name}})
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
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"Woudl you like to remove **{selected_title}** from the **Trade**?", components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"Are you sure you want to trade **{selected_title}**", components=[trade_buttons_action_row])
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120)
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
                                    Button(
                                        style=ButtonStyle.GREEN,
                                        label="Swap Storage Title",
                                        custom_id="swap"
                                    ),
                                    Button(
                                        style=ButtonStyle.RED,
                                        label="Add to Storage",
                                        custom_id="store"
                                    )
                                ]
                        storage_buttons_action_row = ActionRow(*storage_buttons)
                        msg = await ctx.send(f"Would you like to Swap Titles or Add Title to Storage", components=[storage_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContextStorage = await self.bot.wait_for_component(components=[storage_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "swap":
                                await button_ctx.defer(ignore=True)
                                await msg.delete()
                                await ctx.send(f"{ctx.author.mention}, Which title number would you like to swap with in storage?")
                                def check(msg):
                                    return msg.author == ctx.author

                                try:
                                    msg = await self.bot.wait_for('on_message_create', check=check, timeout=30)
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
                                        response = db.updateUserNoFilter(query, update_storage_query)

                                        update_storage_query = {
                                            '$pull': {'TSTORAGE': swap_with},
                                            '$addToSet': {'TCARDS': swap_with}
                                        }
                                        response = db.updateUserNoFilter(query, update_storage_query)

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
                                        response = db.updateUserNoFilter(query, update_storage_query)
                                        
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
            await ctx.send("There's an issue with your Titles list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})


async def menuarms(self, ctx):
    
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

            icon = "🪙"
            if balance >= 150000:
                icon = "💸"
            elif balance >=100000:
                icon = "💰"
            elif balance >= 50000:
                icon = "💵"

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



                embedVar = Embed(title= f"{resp['ARM']}", description=textwrap.dedent(f"""
                {icon} **[{index}]**

                {arm_type}
                {arm_message}
                🌍 **Universe:** {resp['UNIVERSE']}
                ⚒️ {arm['DUR']}
                """), 
                color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                embedVar.set_footer(text=f"{footer}")
                embed_list.append(embedVar)
            
            buttons = [
                Button(style=3, label="Equip", custom_id="Equip"),
                Button(style=1, label="Resell", custom_id="Resell"),
                Button(style=1, label="Dismantle", custom_id="Dismantle"),
                Button(style=1, label="Trade", custom_id="Trade"),
                Button(style=2, label="Swap/Store", custom_id="Storage")
            ]
            custom_action_row = ActionRow(*buttons)

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
                        if sell_price >= 10000000:
                            sell_price = 10000000
                        if arm_name == current_arm:
                            await button_ctx.send("You cannot resell equipped arms.")
                        elif arm_name in updated_vault:
                            sell_buttons = [
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            sell_buttons_action_row = ActionRow(*sell_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to sell **{arm_name}** for 🪙{round(sell_price)}?", components=[sell_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[sell_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Sell cancelled. Please press the Exit button if you are done reselling titles.")
                                if button_ctx.custom_id == "yes":
                                    db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ARMS': {'ARM': str(arm_name)}}})
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
                        essence_amount = 1000
                        arm_passive = arm_data['ABILITIES'][0]
                        arm_passive_type = list(arm_passive.keys())[0]
                        arm_passive_value = list(arm_passive.values())[0]
                        move_types = ["BASIC", "SPECIAL", "ULTIMATE"]
                        if arm_data["EXCLUSIVE"]:
                            essence_amount = 2000
                        selected_universe = arm_data['UNIVERSE']
                        dismantle_amount = 10000
                        if arm_name == current_arm:
                            await button_ctx.send("You cannot dismantle equipped arms.")
                        elif arm_name == "Stock" or arm_name == "Reborn Stock" or arm_name == "Deadgun" or arm_name == "Glaive" or arm_name == "Kings Glaive" or arm_name == "Legendary Weapon":
                            await button_ctx.send("You cannot dismantle Stock arms.")
                        elif arm_name in updated_vault:
                            dismantle_buttons = [
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                            msg = await button_ctx.send(f"Are you sure you want to dismantle **{arm_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Dismantle cancelled. ")
                                if button_ctx.custom_id == "yes":
                                    if selected_universe in current_gems:
                                        query = {'DID': str(ctx.author.id)}
                                        update_query = {'$inc': {'GEMS.$[type].' + "GEMS": dismantle_amount}}
                                        filter_query = [{'type.' + "UNIVERSE": selected_universe}]
                                        response = db.updateUser(query, update_query, filter_query)
                                    else:
                                        response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                    mess = ""
                                    if arm_passive_type in move_types:
                                        em = crown_utilities.inc_essence(str(ctx.author.id), element, essence_amount)
                                        mess = f" Acquired **{'{:,}'.format(essence_amount)}** {em} {element.title()} Essence."
                                    db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'ARMS': {'ARM': str(arm_name)}}})
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
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"Woudl you like to remove **{selected_arm}** from the **Trade**?", components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"Are you sure you want to trade **{selected_arm}**", components=[trade_buttons_action_row])
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120)
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
                                    Button(
                                        style=ButtonStyle.GREEN,
                                        label="Swap Storage Arm",
                                        custom_id="swap"
                                    ),
                                    Button(
                                        style=ButtonStyle.RED,
                                        label="Add to Storage",
                                        custom_id="store"
                                    )
                                ]
                        storage_buttons_action_row = ActionRow(*storage_buttons)
                        msg = await ctx.send(f"Would you like to Swap Arms or Add Arm to Storage", components=[storage_buttons_action_row])
                        def check(button_ctx):
                            return button_ctx.author == ctx.author
                        try:
                            button_ctx: ComponentContextStorage = await self.bot.wait_for_component(components=[storage_buttons_action_row], timeout=120, check=check)

                            if button_ctx.custom_id == "swap":
                                await button_ctx.defer(ignore=True)
                                await msg.delete()
                                await ctx.send(f"{ctx.author.mention}, Which arm number would you like to swap with in storage?")
                                def check(msg):
                                    return msg.author == ctx.author

                                try:
                                    msg = await self.bot.wait_for('on_message_create', check=check, timeout=30)
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
                                        response = db.updateUserNoFilter(query, update_storage_query)

                                        update_storage_query = {
                                            '$pull': {'ASTORAGE': swap_with},
                                            '$addToSet': {'ARMS': swap_with}
                                        }
                                        response = db.updateUserNoFilter(query, update_storage_query)

                                        await msg.delete()
                                        await ctx.send(f"**{selected_arm}** has been swapped with **{swap_with}**")
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
                                    await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
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
                                        response = db.updateUserNoFilter(query, update_storage_query)
                                        
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
                                    await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92.", ephemeral=True)
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
                            await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
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
            await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})


async def menugems(self, ctx: InteractionContext):
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
            embedVar = Embed(title=f"Gems", description="\n".join(gem_details),
                                    color=0x7289da)
            await ctx.send(embed=embedVar)

        embed_list = []
        for i in range(0, len(gems_broken_up)):
            embedVar = Embed(title=f"Gems",
                                                        description="\n".join(gems_broken_up[i]), color=0x7289da)
            embed_list.append(embedVar)

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
    abyss_arm = False
    boss_message = "Nice Arm!"
    arm_cost = '{:,}'.format(100000)
    durability_message = f"{arm_cost}"
    if arm_info['UNIVERSE'] == "Unbound":
        abyss_arm= True
        arm_cost = '{:,}'.format(1000000)
        durability_message = f"{arm_cost}"
    elif arm_info['AVAILABLE'] == False and arm_info['EXCLUSIVE'] == False:
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
    elif abyss_arm:
        boss_message = "That's Abyssal!!"
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
    icon = "🪙"
    if balance >= 1000000:
        icon = "💸"
    elif balance >=650000:
        icon = "💰"
    elif balance >= 150000:
        icon = "💵"
    
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
            Button(
                style=ButtonStyle.GREEN,
                label="🔋 1️⃣",
                custom_id="1"
            ),
            Button(
                style=ButtonStyle.BLUE,
                label="🔋 2️⃣",
                custom_id="2"
            ),
            Button(
                style=ButtonStyle.RED,
                label="🔋 3️⃣",
                custom_id="3"
            ),
            Button(
                style=ButtonStyle.RED,
                label="⚒️ 4️⃣",
                custom_id="5"
            ),
            Button(
                style=ButtonStyle.GREY,
                label="Cancel",
                custom_id="cancel"
            )
        ]
    
    util_sell_buttons = [
            Button(
                style=ButtonStyle.GREY,
                label="Gabe's Purse 👛",
                custom_id="4"
            ),
            Button(
                style=ButtonStyle.GREY,
                label="Storage 💼",
                custom_id="6"
            ),
            Button(
                style=ButtonStyle.GREY,
                label="Preset 🔖",
                custom_id="7"
            )
    ]
    
    sell_buttons_action_row = ActionRow(*sell_buttons)
    util_sell_buttons_action_row = ActionRow(*util_sell_buttons)
    embedVar = Embed(title=f"🔨 | **Blacksmith** - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
    Welcome {ctx.author.mention}!
    Purchase **Card XP** and **Arm Durability**!
    🎴 Card:  **{current_card}** {licon}**{lvl}**
    🦾 Arm: **{current_arm}** *{boss_message}* ⚒️*{current_durability}*
    
    **Card Level Boost**
    🔋 1️⃣ **10 Levels** for 🪙 **{'{:,}'.format(ten_levels)}**
    🔋 2️⃣ **30 Levels** for 💵 **{'{:,}'.format(thirty_levels)}**
    🔋 3️⃣ **100 Levels** for 💰 **{'{:,}'.format(hundred_levels)}**
    ⚒️ 4️⃣ **50 Durability** for 💵 **{durability_message}**
    
    **Vault Upgrades**
    💼 **Storage Tier {storage_message}**: 💸 **{storage_pricing_text}**
    🔖 **Preset Upgrade**: 💸 **{preset_message}**
    👛 **Gabe's Purse**: 💸 **{gabes_message}**
    {gabes_explain}
    
    What would you like to buy?
    """), color=0xf1c40f)
    embedVar.set_footer(text="Boosts are used immediately upon purchase. Click cancel to exit purchase.", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")
    msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row, util_sell_buttons_action_row])

    def check(button_ctx):
        return button_ctx.author == ctx.author

    try:
        button_ctx  = await self.bot.wait_for_component(components=[sell_buttons_action_row, util_sell_buttons_action_row], timeout=120,check=check)
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
                await button_ctx.send("You're too broke to buy. Get your money up.", ephemeral=True)
                await msg.edit(components=[])
                return

            card_info = {}
            for level in vault['CARD_LEVELS']:
                if level['CARD'] == current_card:
                    card_info = level

            lvl = card_info['LVL']
            max_lvl = 700
            if lvl >= max_lvl:
                await button_ctx.send(f"🎴: **{current_card}** is already at max Smithing level. You may level up in **battle**, but you can no longer purchase levels for this card.", ephemeral=True)
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
            response = db.updateUser(query, update_query, filter_query)
            await crown_utilities.curse(price, str(ctx.author.id))
            await button_ctx.send(f"🔋🎴 | **{str(current_card)}** gained {levels_gained} levels!")
            await msg.edit(components=[])
            if button_ctx.custom_id == "cancel":
                await button_ctx.send("Sell ended.", ephemeral=True)
                await msg.edit(components=[])
                return

        if button_ctx.custom_id == "4":
            price = 25000000
            if price > balance:
                await button_ctx.send("Insufficent funds.", ephemeral=True)
                await msg.edit(components=[])
                return
            if has_gabes_purse:
                await button_ctx.send("You already own Gabes Purse. You cannot purchase more than one.", ephemeral=True)
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
                await button_ctx.send("Insufficent funds.", ephemeral=True)
                await msg.edit(components=[])
                return
            if preset_upgrade:
                await button_ctx.send("You already have 5 Presets!", ephemeral=True)
                await msg.edit(components=[])
                return
            else:
                await crown_utilities.curse(price, str(ctx.author.id))
                response = db.updateUserNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' : str(current_card), 'TITLE': "Preset Upgrade Ver 4.0",'ARM': str(current_arm), 'PET': "Chick"}}})
                response = db.updateUserNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' : str(current_card), 'TITLE': "Preset Upgrade Ver 5.0",'ARM': str(current_arm), 'PET': "Chick"}}})
                #response = db.updateUserNoFilter(vault_query, {'$addToSet': {'DECK' : {'CARD' :str(current_card), 'TITLE': str(current_title),'ARM': str(current_arm), 'PET': str(current_pet)}}})
                update = db.updateUserNoFilterAlt(user_query, {'$set': {'U_PRESET': True}})
                await button_ctx.send("🔖 | Preset Upgraded")
                await msg.edit(components=[])
                return
        
        if button_ctx.custom_id == "5":
            if dungeon_arm:
                price = 250000
            if abyss_arm:
                price = 1000000
            if boss_arm:
                await button_ctx.send("Sorry I can't repair **Boss** Arms ...", ephemeral=True)
                await msg.edit(components=[])
                return
            if price > balance:
                await button_ctx.send("Insufficent funds.", ephemeral=True)
                await msg.edit(components=[])
                return
            if current_durability >= 100:
                await button_ctx.send(f"🦾 | {current_arm} is already at Max Durability. ⚒️",ephemeral=True)
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
                    resp = db.updateUser(query, update_query, filter_query)

                    await crown_utilities.curse(price, str(ctx.author.id))
                    if full_repair:
                            await button_ctx.send(f"🦾 | {current_arm}'s ⚒️ durability has increased by **{levels_gained}**!\n*Maximum Durability Reached!*")
                    else:
                            await button_ctx.send(f"🦾 | {current_arm}'s ⚒️ durability has increased by **{levels_gained}**!")
                    await msg.edit(components=[])
                    return
                except:
                    await ctx.send("Unsuccessful to purchase durability boost.", ephemeral=True)

        if button_ctx.custom_id == "6":
            if storage_pricing > balance:
                await button_ctx.send("Insufficent funds.", ephemeral=True)
                await msg.edit(components=[])
                return
                
            if not patron_flag and storage_type >= 2:
                await button_ctx.send("💞 | Only Patrons may purchase more than 30 additional storage. To become a Patron, visit https://www.patreon.com/partychatgaming?fan_landing=true.", ephemeral=True)
                await msg.edit(components=[])
                return
                
            if storage_type == 10:
                await button_ctx.send("💼 | You already have max storage.", ephemeral=True)
                await msg.edit(components=[])
                return
                
            else:
                update = db.updateUserNoFilterAlt(user_query, {'$inc': {'STORAGE_TYPE': 1}})
                await crown_utilities.curse(storage_pricing, str(ctx.author.id))
                await button_ctx.send(f"💼 | Storage Tier {str(storage_type + 1)} has been purchased!")
                await msg.edit(components=[])
                return
    except asyncio.TimeoutError:
        await ctx.send("Blacksmith closed.", ephemeral=True)
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
        await ctx.send("Blacksmith closed unexpectedly. Seek support.", ephemeral=True)


async def menusummons(self, ctx):
    
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
            currentsummon = d['PET']
            pets_list = vault['PETS']

            total_pets = len(pets_list)

            pets=[]
            licon = "🪙"
            if balance >= 150000:
                licon = "💸"
            elif balance >=100000:
                licon = "💰"
            elif balance >= 50000:
                licon = "💵"
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
                if lvl_req <= 0:
                    lvl_req = 2
                if bond_req <= 0:
                    bond_req = 5
                
                bond_message = f"*{pet_exp}/{lvl_req}*"
                lvl_message = f"*{bond_exp}/{bond_req}*"
                
                if pet['BOND'] == 3:
                    bond_message = ":star2:"
                if pet['LVL'] == 10:
                    lvl_message = ":star:"
                
                pet_ability = list(pet.keys())[3]
                pet_ability_power = list(pet.values())[3]
                power = (pet['BOND'] * pet['LVL']) + pet_ability_power
                pet_info = db.querySummon({'PET' : pet['NAME']})
                if pet_info:
                    pet_available = pet_info['AVAILABLE']
                    pet_exclusive = pet_info['EXCLUSIVE']
                    pet_universe = pet_info['UNIVERSE']
                icon = "🧬"
                if pet_available and pet_exclusive:
                    icon = ":fire:"
                elif pet_available == False and pet_exclusive ==False:
                    icon = ":japanese_ogre:"

                embedVar = Embed(title= f"{pet['NAME']}", description=textwrap.dedent(f"""
                {icon}
                _Bond_ **{pet['BOND']}** {bond_message}
                _Level_ **{pet['LVL']} {lvl_message}**
                :small_blue_diamond: **{pet_ability}:** {power}
                🦠 **Type:** {pet['TYPE']}"""), 
                color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                embedVar.set_footer(text=f"{pet['TYPE']}: {enhancer_mapping[pet['TYPE']]}")
                embed_list.append(embedVar)
            
            buttons = [
                Button(style=3, label="Equip", custom_id="Equip"),
                Button(style=1, label="Trade", custom_id="Trade"),
                Button(style=1, label="Dismantle", custom_id="Dismantle"),
                Button(style=2, label="Exit", custom_id="Exit")
            ]
            custom_action_row = ActionRow(*buttons)

            async def custom_function(self, button_ctx):
                if button_ctx.author == ctx.author:
                    updated_vault = db.queryVault({'DID': d['DID']})
                    sell_price = 0
                    selectedsummon = str(button_ctx.origin_message.embeds[0].title)
                    user_query = {'DID': str(ctx.author.id)}
                    
                    if button_ctx.custom_id == "Equip":
                        response = db.updateUserNoFilter(user_query, {'$set': {'FAMILY_PET': False, 'PET': str(button_ctx.origin_message.embeds[0].title)}})
                        await button_ctx.send(f"🧬 **{str(button_ctx.origin_message.embeds[0].title)}** equipped.")
                        self.stop = True
                    
                    elif button_ctx.custom_id =="Trade":
                        summon_data = db.querySummon({'PET' : selectedsummon})
                        summon_name = summon_data['PET']
                        if summon_name == currentsummon:
                            await button_ctx.send("You cannot trade equipped summons.")
                            return
                        sell_price = 5000
                        mtrade = db.queryTrade({'MDID' : str(ctx.author.id), 'OPEN' : True})
                        mvalidation=False
                        bvalidation=False
                        item_already_in_trade=False
                        if mtrade:
                            if selectedsummon in mtrade['MSUMMONS']:
                                await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
                                item_already_in_trade=True
                            mvalidation=True
                        else:
                            btrade = db.queryTrade({'BDID' : str(ctx.author.id), 'OPEN' : True})
                            if btrade:
                                if selectedsummon in btrade['BSUMMONS']:
                                    await ctx.send(f"{ctx.author.mention} summon already in **Trade**")
                                    item_already_in_trade=True
                                bvalidation=True
                            else:
                                await ctx.send(f"{ctx.author.mention} use **/trade** to open a **trade**")
                                return
                        if item_already_in_trade:
                            trade_buttons = [
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"Woudl you like to remove **{selectedsummon}** from the **Trade**?", components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == ctx.author
                                                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Happy Trading")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    neg_sell_price = 0 - abs(int(sell_price))
                                    if mvalidation:
                                        trade_query = {'MDID' : str(button_ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$pull" : {'MSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(neg_sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Returned.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(button_ctx.author.id), 'OPEN' : True}
                                        update_query = {"$pull" : {'BSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(neg_sell_price)}}
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
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Yes",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"Are you sure you want to trade **{selectedsummon}**", components=[trade_buttons_action_row])
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120)
                                if button_ctx.custom_id == "no":
                                        await button_ctx.send("Not this time. ")
                                        self.stop = True
                                if button_ctx.custom_id == "yes":
                                    if mvalidation:
                                        trade_query = {'MDID' : str(ctx.author.id), 'BDID' : str(mtrade['BDID']), 'OPEN' : True}
                                        update_query = {"$push" : {'MSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(sell_price)}}
                                        resp = db.updateTrade(trade_query, update_query)
                                        await button_ctx.send("Traded.")
                                        self.stop = True
                                    elif bvalidation:
                                        trade_query = {'MDID' : str(btrade['MDID']),'BDID' : str(ctx.author.id), 'OPEN' : True}
                                        update_query = {"$push" : {'BSUMMONS': selectedsummon}, "$inc" : {'TAX' : int(sell_price)}}
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
                        summon_data = db.querySummon({'PET' : selectedsummon})
                        summon_name = summon_data['PET']
                        if summon_name == currentsummon:
                            await button_ctx.send("You cannot dismantle equipped summonss.")
                            return
                        dismantle_price = 5000   
                        level = int(pet['LVL'])
                        bond = int(pet['BOND'])
                        dismantle_amount = round((1000* level) + (dismantle_price * bond))
                        dismantle_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Yes",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.BLUE,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        dismantle_buttons_action_row = ActionRow(*dismantle_buttons)
                        msg = await button_ctx.send(f"Are you sure you want to dismantle **{summon_name}** for 💎 {round(dismantle_amount)}?", components=[dismantle_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        
                        try:
                            button_ctx  = await self.bot.wait_for_component(components=[dismantle_buttons_action_row], timeout=120, check=check)

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
                                    response = db.updateUser(query, update_query, filter_query)
                                else:
                                    response = db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$addToSet':{'GEMS': {'UNIVERSE': pet_universe, 'GEMS': dismantle_amount, 'UNIVERSE_HEART': False, 'UNIVERSE_SOUL': False}}})
                                
                                db.updateUserNoFilter({'DID': str(ctx.author.id)},{'$pull':{'PETS': {"NAME": str(summon_name)}}})
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
            await ctx.send("There's an issue with your Summons list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
            return
    else:
        newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})


async def menudestinies(self, ctx):
    
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
            icon = "🪙"
            if balance >= 150000:
                icon = "💸"
            elif balance >=100000:
                icon = "💰"
            elif balance >= 50000:
                icon = "💵"
            for d in destiny:
                if not d['COMPLETED']:
                    destiny_messages.append(textwrap.dedent(f"""\
                    :sparkles: **{d["NAME"]}**
                    Defeat **{d['DEFEAT']}** with **{" ".join(d['USE_CARDS'])}** | **Current Progress:** {d['WINS']}/{d['REQUIRED']}
                    Win 🎴 **{d['EARN']}**
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
                embedVar = Embed(title= f"Destiny Lines\n**Balance**: 🪙{'{:,}'.format(balance)}", description="\n".join(destiny_messages), color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                # embedVar.set_footer(text=f".equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                await ctx.send(embed=embedVar)

            embed_list = []
            for i in range(0, len(destinies_broken_up)):
                embedVar = Embed(title= f":sparkles: Destiny Lines\n**Balance**: {icon}{'{:,}'.format(balance)}", description="\n".join(destinies_broken_up[i]), color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                # embedVar.set_footer(text=f"{total_pets} Total Pets\n.equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                embed_list.append(embedVar)

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
            icon = "🪙"
            if balance >= 150000:
                icon = "💸"
            elif balance >=100000:
                icon = "💰"
            elif balance >= 50000:
                icon = "💵"
            for d in destiny:
                if not d['COMPLETED']:
                    destiny_messages.append(textwrap.dedent(f"""\
                    :sparkles: **{d["NAME"]}**
                    Defeat **{d['DEFEAT']}** with **{" ".join(d['USE_CARDS'])}** | **Current Progress:** {d['WINS']}/{d['REQUIRED']}
                    Win 🎴 **{d['EARN']}**
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
                embedVar = Embed(title= f"Destiny Lines\n**Balance**: 🪙{'{:,}'.format(balance)}", description="\n".join(destiny_messages), color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                # embedVar.set_footer(text=f".equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                await ctx.send(embed=embedVar)

            embed_list = []
            for i in range(0, len(destinies_broken_up)):
                embedVar = Embed(title= f":sparkles: Destiny Lines\n**Balance**: {icon}{'{:,}'.format(balance)}", description="\n".join(destinies_broken_up[i]), color=0x7289da)
                embedVar.set_thumbnail(url=avatar)
                # embedVar.set_footer(text=f"{total_pets} Total Pets\n.equippet pet name: Equip Pet\n.viewpet pet name: View Pet Details")
                embed_list.append(embedVar)

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


@slash_command(description="View your quests")
async def quests(self, ctx):
    
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return

    query = {'DID': str(ctx.author.id)}
    d = db.queryUser(query)
    vault = db.queryVault({'DID': d['DID']})
    prestige = d['PRESTIGE']
    exchange = int(100 - (prestige * 10))
    # server = db.queryServer({"GNAME": str(ctx.author.guild)})
    if not vault['QUESTS']:
        await ctx.send("You have no quests available at this time!", ephemeral=True)
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
                icon = "🪙"
                if quest['REWARD'] >= 3000000:
                    icon = ":credit_card:"
                if quest['REWARD'] >= 2000000:
                    icon = "💸"
                elif quest['REWARD'] >=1000000:
                    icon = "💰"
                elif quest['REWARD'] >= 200000:
                    icon = "💵"
                

                embedVar = Embed(title=f"{opponent_name}", description=textwrap.dedent(f"""\
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
                if guild_buff:
                    if guild_buff['Quest']:
                        if int(goal) > 1:
                            embedVar.set_footer(text=f"🌑 | Conquer Abyss {exchange} and Prestige to reduce Quest Requirements!")
                        else:
                            embedVar.set_footer(text=f"☀️ | You can use /daily every 12 Hours for More Quest!")
                    else:
                        embedVar.set_footer(text=f"🪖 | Purchase a Guild Quest Buff and skip to the Quest Fight!")
                else:
                    embedVar.set_footer(text=f"🪖 | Create a Guild and purchase Quest Buff! Skip to the quest fight!")
                # embedVar.set_footer(text="Use /tales to complete daily quest!", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")

                if quest['GOAL'] != quest['WINS']:
                    embed_list.append(embedVar)

            if not embed_list:
                await ctx.send(" 👑 | All quests have been completed today!")
                return

            buttons = [Button(style=3, label="Start Quest Tales", custom_id="quests_tales"),]
            custom_action_row = ActionRow(*buttons)

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
                        player = db.queryUser({'DID': str(ctx.author.id)})
                        p = Player(player['AUTOSAVE'], player['DISNAME'], player['DID'], player['AVATAR'], player['GUILD'], player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'],player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'],
                        player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'], player['EXPLORE_LOCATION'], player['SCENARIO_HISTORY'])

                        #print(currentopponent)
                        mode  = "Tales"
                        battle = Battle(mode, p)
                        response = {'SELECTED_UNIVERSE': selected_universe,
                        'UNIVERSE_DATA': universe, 'CREST_LIST': p.crestlist, 'CREST_SEARCH': p.crestsearch,
                        'COMPLETED_TALES': p.completed_tales, 'OGUILD': p.association_info, 'CURRENTOPPONENT': currentopponent}
                        battle.set_universe_selection_config(response)
                        
                        await battle_commands(self, ctx, battle, p, None, player2=None, player3=None)
                        
                        self.stop = True
                else:
                    await ctx.send("This is not your Quest list.")

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
            await ctx.send("There's an issue with your Quest list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
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
        icon = "🪙"
        if vault:
            name = d['DISNAME'].split("#",1)[0]
            avatar = d['AVATAR']
            balance = vault['BALANCE']
            if balance >= 50000000:
                icon = "💸"
            elif balance >=10000000:
                icon = "💰"
            elif balance >= 500000:
                icon = "💵"
            if d['TEAM'] != 'PCG':
                t = db.queryTeam({'TEAM_NAME' : d['TEAM'].lower()})
                tbal = t['BANK']
                if d['FAMILY'] != 'PCG':
                    f = db.queryFamily({'HEAD': d['FAMILY']})
                    fbal = f['BANK']
            embedVar = Embed(title= f"{icon}{'{:,}'.format(balance)}", color=0x7289da)
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
            ownedtalismans = []
            for cards in vault['CARDS']:
                ownedcards.append(cards)
            for titles in vault['TITLES']:
                ownedtitles.append(titles)
            for arms in vault['ARMS']:
                ownedarms.append(arms['ARM'])
            for pets in vault['PETS']:
                ownedpets.append(pets['NAME'])
            for talismans in vault['TALISMANS']:
                ownedtalismans.append(talismans['TYPE'])

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
            preset1_talisman = list(deck[0].values())[4]

            preset2_card = list(deck[1].values())[0]
            preset2_title = list(deck[1].values())[1]
            preset2_arm = list(deck[1].values())[2]
            preset2_pet = list(deck[1].values())[3]
            preset2_talisman = list(deck[1].values())[4]

            preset3_card = list(deck[2].values())[0]
            preset3_title = list(deck[2].values())[1]
            preset3_arm = list(deck[2].values())[2]
            preset3_pet = list(deck[2].values())[3]    
            preset3_talisman = list(deck[2].values())[4]
            
            preset3_message = "📿"
            if preset3_talisman != "NULL":
                preset3_message = crown_utilities.set_emoji(preset3_talisman)
                
            preset2_message = "📿"
            if preset2_talisman != "NULL":
                preset2_message = crown_utilities.set_emoji(preset2_talisman)
                
            preset1_message = "📿"
            if preset1_talisman != "NULL":
                preset1_message = crown_utilities.set_emoji(preset1_talisman)
            
            if preset_update:
                preset4_card = list(deck[3].values())[0]
                preset4_title = list(deck[3].values())[1]
                preset4_arm = list(deck[3].values())[2]
                preset4_pet = list(deck[3].values())[3]
                preset4_talisman = list(deck[3].values())[4]

                preset5_card = list(deck[4].values())[0]
                preset5_title = list(deck[4].values())[1]
                preset5_arm = list(deck[4].values())[2]
                preset5_pet = list(deck[4].values())[3]  
                preset5_talisman = list(deck[4].values())[4]
                
                preset5_message = "📿"
                if preset5_talisman != "NULL":
                    preset5_message = crown_utilities.set_emoji(preset5_talisman)
                    
                preset4_message = "📿"
                if preset4_talisman != "NULL":
                    preset4_message = crown_utilities.set_emoji(preset4_talisman)
                    
                

                    
                
                listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n**Talisman**: {preset1_message}\n\n", 
                f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n**Talisman**: {preset2_message}\n\n", 
                f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n**Talisman**: {preset3_message}\n\n", 
                f"4️⃣| {preset4_title} {preset4_card} and {preset4_pet}\n**Card**: {preset4_card}\n**Title**: {preset4_title}\n**Arm**: {preset4_arm}\n**Summon**: {preset4_pet}\n**Talisman**: {preset4_message}\n\n", 
                f"5️⃣ | {preset5_title} {preset5_card} and {preset5_pet}\n**Card**: {preset5_card}\n**Title**: {preset5_title}\n**Arm**: {preset5_arm}\n**Summon**: {preset5_pet}\n**Talisman**: {preset5_message}\n\n"]  
            else:
                listed_options = [f"1️⃣ | {preset1_title} {preset1_card} and {preset1_pet}\n**Card**: {preset1_card}\n**Title**: {preset1_title}\n**Arm**: {preset1_arm}\n**Summon**: {preset1_pet}\n**Talisman**: {preset1_message}\n\n", 
                f"2️⃣ | {preset2_title} {preset2_card} and {preset2_pet}\n**Card**: {preset2_card}\n**Title**: {preset2_title}\n**Arm**: {preset2_arm}\n**Summon**: {preset2_pet}\n**Talisman**: {preset2_message}\n\n", 
                f"3️⃣ | {preset3_title} {preset3_card} and {preset3_pet}\n**Card**: {preset3_card}\n**Title**: {preset3_title}\n**Arm**: {preset3_arm}\n**Summon**: {preset3_pet}\n**Talisman**: {preset3_message}\n\n"]
        
            embedVar = Embed(title="🔖 | Preset Menu", description=textwrap.dedent(f"""
            {"".join(listed_options)}
            """), color=discord.Color.blue())
            embedVar.set_thumbnail(url=avatar)
            # embedVar.add_field(name=f"Preset 1:{preset1_title} {preset1_card} and {preset1_pet}", value=f"Card: {preset1_card}\nTitle: {preset1_title}\nArm: {preset1_arm}\nSummon: {preset1_pet}", inline=False)
            # embedVar.add_field(name=f"Preset 2:{preset2_title} {preset2_card} and {preset2_pet}", value=f"Card: {preset2_card}\nTitle: {preset2_title}\nArm: {preset2_arm}\nSummon: {preset2_pet}", inline=False)
            # embedVar.add_field(name=f"Preset 3:{preset3_title} {preset3_card} and {preset3_pet}", value=f"Card: {preset3_card}\nTitle: {preset3_title}\nArm: {preset3_arm}\nSummon: {preset3_pet}", inline=False)
            util_buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="1️⃣",
                    custom_id = "1"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="2️⃣",
                    custom_id = "2"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="3️⃣",
                    custom_id = "3"
                )
            ]
            
            if preset_update:
                util_buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label="4️⃣",
                        custom_id="4"
                    )
                )
                util_buttons.append(
                    Button(
                        style=ButtonStyle.BLUE,
                        label="5️⃣",
                        custom_id="5"
                    )
                )
                
                    

            util_action_row = ActionRow(*util_buttons)
            components = [util_action_row]
            await ctx.send(embed=embedVar,components=[util_action_row])
            
            def check(button_ctx):
                return button_ctx.author == ctx.author
            try:
                button_ctx  = await self.bot.wait_for_component(components=[util_action_row], timeout=30,check=check)

                if  button_ctx.custom_id == "0":
                    await button_ctx.send(f"{ctx.author.mention}, No change has been made", ephemeral=True)
                    return
                elif  button_ctx.custom_id == "1":
                    equipped_items = []
                    not_owned_items = []
                    update_data = {}
                    if preset1_card in ownedcards:
                        equipped_items.append(f"🎴 **Card** | {preset1_card}")
                        update_data['CARD'] = str(preset1_card)
                    else:
                        not_owned_items.append(f"❌ {preset1_card}")

                    if preset1_title in ownedtitles:
                        equipped_items.append(f"🎗️ **Title** | {preset1_title}")
                        update_data['TITLE'] = str(preset1_title)
                    elif preset1_title is not None:
                        not_owned_items.append(f"❌ | {preset1_title}")

                    if preset1_arm in ownedarms:
                        equipped_items.append(f"🦾 **Arm** | {preset1_arm}")
                        update_data['ARM'] = str(preset1_arm)
                    elif preset1_arm is not None:
                        not_owned_items.append(f"❌ | {preset1_arm}")

                    if preset1_pet in ownedpets:
                        equipped_items.append(f"🧬 **Summon** | {preset1_pet}")
                        update_data['PET'] = str(preset1_pet)
                    elif preset1_pet is not None:
                        not_owned_items.append(f"❌ | {preset1_pet}")

                    if preset1_talisman in ownedtalismans:
                        equipped_items.append(f":prayer_beads: | {preset1_message}")
                        update_data['TALISMAN'] = str(preset1_talisman)
                    elif preset1_talisman is not None:
                        not_owned_items.append(f"❌ |{preset1_message}{preset1_talisman.title()}")

                    # Update the user's build in the database with owned items
                    response = db.updateUserNoFilter(query, {'$set': update_data})
                    if not_owned_items:
                        ecolor = discord.Color.red()
                    # Create the embed
                    embed = Embed(title=f"{ctx.author.display_name}'s Build Updated", color=discord.Color.gold())
                    if equipped_items:
                        embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)
                        if not not_owned_items:
                            embed.set_footer(text="👥 | Conquer Universes with this preset in /duo!")
                    if not_owned_items:
                        embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                        embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    

                    # Send the response
                    await button_ctx.send(embed=embed)

                elif  button_ctx.custom_id == "2":
                    # Check if items are owned
                    equipped_items = []
                    not_owned_items = []
                    update_data = {}
                    if preset2_card in ownedcards:
                        equipped_items.append(f"🎴 **Card** | {preset2_card}")
                        update_data['CARD'] = str(preset2_card)
                    else:
                        not_owned_items.append(f"❌ {preset2_card}")

                    if preset2_title in ownedtitles:
                        equipped_items.append(f"🎗️ **Title** | {preset2_title}")
                        update_data['TITLE'] = str(preset2_title)
                    else:
                        not_owned_items.append(f"❌ | {preset2_title}")

                    if preset2_arm in ownedarms:
                        equipped_items.append(f"🦾 **Arm** | {preset2_arm}")
                        update_data['ARM'] = str(preset2_arm)
                    else:
                        not_owned_items.append(f"❌ | {preset2_arm}")

                    if preset2_pet in ownedpets:
                        equipped_items.append(f"🧬 **Summon** | {preset2_pet}")
                        update_data['PET'] = str(preset2_pet)
                    else:
                        not_owned_items.append(f"❌ | {preset2_pet}")

                    if preset2_talisman in ownedtalismans:
                        equipped_items.append(f":prayer_beads: | {preset2_message}")
                        update_data['TALISMAN'] = str(preset2_talisman)
                    else:
                        not_owned_items.append(f"❌ | {preset2_talisman}")

                    # Update the user's build in the database with owned items
                    response = db.updateUserNoFilter(query, {'$set': update_data})

                    # Create the embed
                    embed = Embed(title=f"{ctx.author.display_name}'s Build Updated", color=discord.Color.gold())
                    if equipped_items:
                        embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)
                        if not not_owned_items:
                            embed.set_footer(text="👥 | Conquer Universes with this preset in /duo!")
                    if not_owned_items:
                        embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                        embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    

                    # Send the response
                    await button_ctx.send(embed=embed)

                elif  button_ctx.custom_id == "3":
                    equipped_items = []
                    not_owned_items = []
                    update_data = {}
                    if preset3_card in ownedcards:
                        equipped_items.append(f"🎴 **Card** | {preset3_card}")
                        update_data['CARD'] = str(preset3_card)
                    else:
                        not_owned_items.append(f"❌ {preset3_card}")

                    if preset3_title in ownedtitles:
                        equipped_items.append(f"🎗️ **Title** | {preset3_title}")
                        update_data['TITLE'] = str(preset3_title)
                    else:
                        not_owned_items.append(f"❌ | {preset3_title}")

                    if preset3_arm in ownedarms:
                        equipped_items.append(f"🦾 **Arm** | {preset3_arm}")
                        update_data['ARM'] = str(preset3_arm)
                    else:
                        not_owned_items.append(f"❌ | {preset3_arm}")

                    if preset3_pet in ownedpets:
                        equipped_items.append(f"🧬 **Summon** | {preset3_pet}")
                        update_data['PET'] = str(preset3_pet)
                    else:
                        not_owned_items.append(f"❌ | {preset3_pet}")

                    if preset3_talisman in ownedtalismans:
                        equipped_items.append(f":prayer_beads: | {preset3_message}")
                        update_data['TALISMAN'] = str(preset3_talisman)
                    else:
                        not_owned_items.append(f"❌ | {preset3_talisman}")

                    # Update the user's build in the database with owned items
                    response = db.updateUserNoFilter(query, {'$set': update_data})

                    # Create the embed
                    embed = Embed(title=f"{ctx.author.display_name}'s Build Updated", color=discord.Color.gold())
                    if equipped_items:
                        embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)
                        if not not_owned_items:
                            embed.set_footer(text="👥 | Conquer Universes with this preset in /duo!")
                    if not_owned_items:
                        embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                        embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    

                    # Send the response
                    await button_ctx.send(embed=embed)

                elif  button_ctx.custom_id == "4":
                    equipped_items = []
                    not_owned_items = []
                    update_data = {}
                    if preset4_card in ownedcards:
                        equipped_items.append(f"🎴 **Card** | {preset4_card}")
                        update_data['CARD'] = str(preset4_card)
                    else:
                        not_owned_items.append(f"❌ {preset4_card}")

                    if preset4_title in ownedtitles:
                        equipped_items.append(f"🎗️ **Title** | {preset4_title}")
                        update_data['TITLE'] = str(preset4_title)
                    else:
                        not_owned_items.append(f"❌ | {preset4_title}")

                    if preset4_arm in ownedarms:
                        equipped_items.append(f"🦾 **Arm** | {preset4_arm}")
                        update_data['ARM'] = str(preset4_arm)
                    else:
                        not_owned_items.append(f"❌ | {preset4_arm}")

                    if preset4_pet in ownedpets:
                        equipped_items.append(f"🧬 **Summon** | {preset4_pet}")
                        update_data['PET'] = str(preset4_pet)
                    else:
                        not_owned_items.append(f"❌ | {preset4_pet}")

                    if preset4_talisman in ownedtalismans:
                        equipped_items.append(f":prayer_beads: | {preset4_message}")
                        update_data['TALISMAN'] = str(preset4_talisman)
                    else:
                        not_owned_items.append(f"❌ | {preset4_talisman}")

                    # Update the user's build in the database with owned items
                    response = db.updateUserNoFilter(query, {'$set': update_data})

                    # Create the embed
                    embed = Embed(title=f"{ctx.author.display_name}'s Build Updated", color=discord.Color.gold())
                    if equipped_items:
                        embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)
                        if not not_owned_items:
                            embed.set_footer(text="👥 | Conquer Universes with this preset in /duo!")
                    if not_owned_items:
                        embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                        embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    

                    # Send the response
                    await button_ctx.send(embed=embed)
                    
                elif  button_ctx.custom_id == "5":
                    equipped_items = []
                    not_owned_items = []
                    update_data = {}

                    if preset5_card in ownedcards:
                        equipped_items.append(f"🎴 **Card** | {preset5_card}")
                        update_data['CARD'] = str(preset5_card)
                    else:
                        not_owned_items.append(f"❌ {preset5_card}")

                    if preset5_title in ownedtitles:
                        equipped_items.append(f"🎗️ **Title** | {preset5_title}")
                        update_data['TITLE'] = str(preset5_title)
                    else:
                        not_owned_items.append(f"❌ | {preset5_title}")

                    if preset5_arm in ownedarms:
                        equipped_items.append(f"🦾 **Arm** | {preset5_arm}")
                        update_data['ARM'] = str(preset5_arm)
                    else:
                        not_owned_items.append(f"❌ | {preset5_arm}")

                    if preset5_pet in ownedpets:
                        equipped_items.append(f"🧬 **Summon** | {preset5_pet}")
                        update_data['PET'] = str(preset5_pet)
                    else:
                        not_owned_items.append(f"❌ | {preset5_pet}")

                    if preset5_talisman in ownedtalismans:
                        equipped_items.append(f":prayer_beads: | {preset5_message}")
                        update_data['TALISMAN'] = str(preset5_talisman)
                    else:
                        not_owned_items.append(f"❌ | {preset5_talisman}")

                    # Update the user's build in the database with owned items
                    response = db.updateUserNoFilter(query, {'$set': update_data})

                    # Create the embed
                    embed = Embed(title=f"{ctx.author.display_name}'s Build Updated", color=discord.Color.gold())
                    if equipped_items:
                        embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)
                        if not not_owned_items:
                            embed.set_footer(text="👥 | Conquer Universes with this preset in /duo!")
                    if not_owned_items:
                        embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                        embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    

                    # Send the response
                    await button_ctx.send(embed=embed)

            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", ephemeral=True)
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
                await ctx.send("Preset Issue Seek support.", ephemeral=True)
        else:
            newVault = db.createVault({'OWNER': d['DISNAME'], 'DID' : d['DID']})
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", ephemeral=True)
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
        await ctx.send("Preset Issue Seek support.", ephemeral=True)


# async def menushop(self, ctx):
#     a_registered_player = await crown_utilities.player_check(ctx)
#     if not a_registered_player:
#         return

#     try:
#         all_universes = db.queryAllUniverse()
#         user = db.queryUser({'DID': str(ctx.author.id)})
#         storage_allowed_amount = user['STORAGE_TYPE'] * 15
#         guild_buff = "NULL"
#         if user["TEAM"] != "PCG":
#             guild_info = db.queryTeam({"TEAM_NAME": str(user["TEAM"].lower())})
#             guild_buff = guild_info["ACTIVE_GUILD_BUFF"]

#         if user['LEVEL'] < 1 and user['PRESTIGE'] < 1:
#             await ctx.send("🔓 Unlock the Shop by completing Floor 0 of the 🌑 Abyss! Use /solo to enter the abyss.")
#             return

#         completed_tales = user['CROWN_TALES']
#         completed_dungeons = user['DUNGEONS']
#         available_universes = []
#         riftShopOpen = False
#         shopName = ':shopping_cart: Shop'
#         if user['RIFT'] == 1 or guild_buff == "Rift":
#             riftShopOpen = True
#             shopName = ':crystal_ball: Rift Shop'

#         if riftShopOpen:
#             close_rift = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'RIFT': 0}})

            
#         if riftShopOpen:    
#             for uni in all_universes:
#                 if uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
#                     available_universes.append(uni)
#         else:
#             for uni in all_universes:
#                 if uni['TIER'] != 9 and uni['HAS_CROWN_TALES'] and uni['HAS_DUNGEON']:
#                     available_universes.append(uni)
#         universe_subset = random.sample(available_universes, k=min(len(available_universes), 25))
        
#         vault_query = {'DID' : str(ctx.author.id)}
#         vault = db.altQueryVault(vault_query)
#         storage_amount = len(vault['STORAGE'])
#         hand_length = len(vault['CARDS'])
#         current_titles = vault['TITLES']
#         current_cards = vault['CARDS']
#         current_arms = []
#         for arm in vault['ARMS']:
#             current_arms.append(arm['ARM'])

#         owned_card_levels_list = []
#         for c in vault['CARD_LEVELS']:
#             owned_card_levels_list.append(c['CARD'])

#         owned_destinies = []
#         for destiny in vault['DESTINY']:
#             owned_destinies.append(destiny['NAME'])
            
#         card_message = ""
#         title_message = ""
#         arm_message = ""
        
#         if len(current_cards) >= 25:
#             card_message = "🎴 *25 Full*"
#         else:
#             card_message = f"🎴 {len(current_cards)}"
            
#         if len(current_titles) >= 25:
#             title_message = "🎗️ *25 Full*"
#         else:
#             title_message = f"🎗️ {len(current_titles)}"
            
#         if len(current_arms) >= 25:
#             arm_message = "🦾 *25 Full*"
#         else:
#             arm_message = f"🦾 {len(current_arms)}"


#         balance = vault['BALANCE']
#         icon = "🪙"
#         if balance >= 150000:
#             icon = "💸"
#         elif balance >=100000:
#             icon = "💰"
#         elif balance >= 50000:
#             icon = "💵"


#         embed_list = []
#         for universe in universe_subset:
#             t1_pre_list_of_cards = False
#             t2_pre_list_of_cards = False
#             t3_pre_list_of_cards = False
#             #Universe Image and Adjusted Pricing
#             universe_name = universe['TITLE']
#             universe_image = universe['PATH']
#             adjusted_prices = price_adjuster(15000, universe_name, completed_tales, completed_dungeons)
            
            
#             #Shop Messages and Card Count
#             t1_acceptable = [1,2,3]
#             t2_acceptable = [3,4,5]
#             t3_acceptable = [5,6,7]
            
#             t1_pre_list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_name), 'TIER': {'$in': t1_acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
#             t1_card_message = (f"💵 {'{:,}'.format(adjusted_prices['C1'])} *🎴{len(t1_pre_list_of_cards)}*")
#             if not t1_pre_list_of_cards:
#                 t1_card_message = ("Unavailable")
                
#             t2_pre_list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_name), 'TIER': {'$in': t2_acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
#             t2_card_message = (f"💰 {'{:,}'.format(adjusted_prices['C2'])} *🎴{len(t2_pre_list_of_cards)}*")
#             if not t2_pre_list_of_cards:
#                 t2_card_message = ("Unavailable")
                
#             t3_pre_list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_name), 'TIER': {'$in': t3_acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
#             t3_card_message = (f"💸 {'{:,}'.format(adjusted_prices['C3'])} *🎴{len(t3_pre_list_of_cards)}*")
#             if not t3_pre_list_of_cards:
#                 t3_card_message = ("Unavailable")

            
            
#             embedVar = Embed(title= f"{universe_name}", description=textwrap.dedent(f"""
#             *Welcome {ctx.author.mention}! {adjusted_prices['MESSAGE']}
#             You have {icon}{'{:,}'.format(balance)} coins!*
#             {card_message} | {title_message} | {arm_message}
            
#             🎗️ **Title:** Title Purchase for 💵 {'{:,}'.format(adjusted_prices['TITLE_PRICE'])}
#             🦾 **Arm:** Arm Purchase for 💵 {'{:,}'.format(adjusted_prices['ARM_PRICE'])}
#             1️⃣ **1-3 Tier Card:** for {t1_card_message}
#             2️⃣ **3-5 Tier Card:** for {t2_card_message}
#             3️⃣ **5-7 Tier Card:** for {t3_card_message}
#             """), color=0x7289da)
#             embedVar.set_image(url=universe_image)
#             #embedVar.set_thumbnail(url="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620236723/PCG%20LOGOS%20AND%20RESOURCES/Party_Chat_Shop.png")
#             embed_list.append(embedVar)

        
#         # Pull all cards that don't require tournaments
#         # resp = db.queryShopCards()

#         buttons = [
#             Button(style=3, label="🎗️", custom_id="title"),
#             Button(style=1, label="🦾", custom_id="arm"),
#             Button(style=2, label="1️⃣", custom_id="t1card"),
#             Button(style=2, label="2️⃣", custom_id="t2card"),
#             Button(style=2, label="3️⃣", custom_id="t3card"),
#         ]

#         custom_action_row = ActionRow(*buttons)

#         async def custom_function(self, button_ctx):
#             if button_ctx.author == ctx.author:
#                 updated_vault = db.queryVault({'DID': user['DID']})
#                 balance = updated_vault['BALANCE']        
#                 universe = str(button_ctx.origin_message.embeds[0].title)
                
#                 if button_ctx.custom_id == "title":
#                     updated_vault = db.queryVault({'DID': user['DID']})
#                     current_titles = updated_vault['TITLES']
#                     price = price_adjuster(50000, universe, completed_tales, completed_dungeons)['TITLE_PRICE']
#                     bless_amount = price
#                     # if len(current_titles) >=25:
#                     #     await button_ctx.send("You have max amount of Titles. Transaction cancelled.")
#                     #     self.stop = True
#                     #     return

#                     if price > balance:
#                         await button_ctx.send("Insufficent funds.")
#                         self.stop = True
#                         return
#                     list_of_titles =[x for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
#                     if not list_of_titles:
#                         await button_ctx.send("There are no titles available for purchase in this range.")
#                         self.stop = True
#                         return

#                     selection_length = len(list(list_of_titles)) - 1
#                     if selection_length ==0:
#                         title = list_of_titles[0]
#                     else:
#                         selection = random.randint(0,selection_length)
#                         title = list_of_titles[selection]  
#                     if title['TITLE'] in current_titles:                 
#                         bless_amount = price
#                         bless_reduction = 0
#                         if universe_name in completed_tales:
#                             bless_reduction = bless_amount * .25
#                             bless_amount = round((bless_amount - bless_reduction)/2)
#                         if universe_name in completed_dungeons:
#                             bless_reduction = bless_amount * .50
#                             bless_amount = round((bless_amount - bless_reduction)/2)
#                         else: 
#                             bless_amount = round(bless_amount /2) #Send bless amount for price in utilities
                            
#                     response = await crown_utilities.store_drop_card(str(ctx.author.id), title['TITLE'], universe_name, updated_vault, "Titles_NoDestinies", bless_amount, bless_amount, "Purchase", True, int(price), "titles")
#                     await button_ctx.send(response)
#                         # await button_ctx.send(f"You already own **{title['TITLE']}**. You get a 🪙**{'{:,}'.format(bless_amount)}** refund!") 
#                     #     #await crown_utilities.curse(bless_amount, str(ctx.author.id)) 
#                     # else:
#                     #     response = db.updateUserNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})   
#                     #     await crown_utilities.curse(price, str(ctx.author.id))
#                     #     await button_ctx.send(f"You purchased **{title['TITLE']}**.")


#                 elif button_ctx.custom_id == "arm":
#                     updated_vault = db.queryVault({'DID': user['DID']})
#                     current_arms = []
#                     for arm in updated_vault['ARMS']:
#                         current_arms.append(arm['ARM'])
#                     price = price_adjuster(25000, universe, completed_tales, completed_dungeons)['ARM_PRICE']
#                     # if len(current_arms) >=25:
#                     #     await button_ctx.send("You have max amount of Arms. Transaction cancelled.")
#                     #     self.stop = True
#                     #     return
#                     if price > balance:
#                         await button_ctx.send("Insufficent funds.")
#                         self.stop = True
#                         return
#                     list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE']]
#                     if not list_of_arms:
#                         await button_ctx.send("There are no arms available for purchase in this range.")
#                         self.stop = True
#                         return

#                     selection_length = len(list(list_of_arms)) - 1

#                     if selection_length ==0:
#                         arm = list_of_arms[0]
#                     else:
#                         selection = random.randint(0,selection_length)
#                         arm = list_of_arms[selection]['ARM']
#                     response = await crown_utilities.store_drop_card(str(ctx.author.id), arm, universe_name, updated_vault, 25, price, price, "Purchase", True, int(price), "arms")
#                     await button_ctx.send(response)
                    
#                     # if arm not in current_arms:
#                     #     response = db.updateUserNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 25}}})
#                     #     await crown_utilities.curse(price, str(ctx.author.id))
#                     #     await button_ctx.send(f"You purchased **{arm}**.")
#                     # else:
#                     #     update_query = {'$inc': {'ARMS.$[type].' + 'DUR': 10}}
#                     #     filter_query = [{'type.' + "ARM": str(arm)}]
#                     #     resp = db.updateUser(vault_query, update_query, filter_query)
#                     #     await crown_utilities.curse(price, str(ctx.author.id))
#                     #     await button_ctx.send(f"You purchased **{arm}**. Increased durability for the arm by 10 as you already own it.")


#                 elif button_ctx.custom_id == "t1card":
#                     price = price_adjuster(100000, universe, completed_tales, completed_dungeons)['C1']
#                     acceptable = [1,2,3]
#                     if price > balance:
#                         await button_ctx.send("Insufficent funds.")
#                         self.stop = True
#                         return
#                     list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
#                     if not list_of_cards:
#                         await button_ctx.send("There are no cards available for purchase in this range.")
#                         self.stop = True
#                         return

#                     selection_length = len(list(list_of_cards)) - 1
#                     if selection_length ==0:
#                         card = list_of_cards[0]
#                     else:
#                         selection = random.randint(0,selection_length)
#                         card = list_of_cards[selection]
#                     card_name = card['NAME']
#                     tier = 0

#                     response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
#                     await button_ctx.send(response)


#                 elif button_ctx.custom_id == "t2card":
#                     price = price_adjuster(450000, universe, completed_tales, completed_dungeons)['C2']
#                     acceptable = [3,4,5]
#                     if price > balance:
#                         await button_ctx.send("Insufficent funds.")
#                         self.stop = True
#                         return
#                     list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
                    
#                     if not list_of_cards:
#                         await button_ctx.send("There are no cards available for purchase in this range.")
#                         self.stop = True
#                         return
                    
#                     selection_length = len(list(list_of_cards)) - 1

#                     if selection_length ==0:
#                         card = list_of_cards[0]
#                     else:
#                         selection = random.randint(0,selection_length)
#                         card = list_of_cards[selection]
#                     card_name = card['NAME']
#                     tier = 0
                    
#                     response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
#                     await button_ctx.send(response)


#                 elif button_ctx.custom_id == "t3card":
#                     price = price_adjuster(6000000, universe, completed_tales, completed_dungeons)['C3']
#                     acceptable = [5,6,7]
#                     if price > balance:
#                         await button_ctx.send("Insufficent funds.")
#                         self.stop = True
#                         return
#                     card_list_response = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION']]
#                     if not card_list_response:
#                         await button_ctx.send("There are no cards available for purchase in this range.")
#                         self.stop = True
#                         return
#                     else:
#                         list_of_cards = []
#                         for card in card_list_response:
#                             if card['AVAILABLE'] and not card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
#                                 list_of_cards.append(card)


#                     if not list_of_cards:
#                         await button_ctx.send("There are no cards available for purchase in this range.")
#                         self.stop = True
#                         return

#                     selection_length = len(list(list_of_cards)) - 1
#                     if selection_length ==0:
#                         card = list_of_cards[0]
#                     else:
#                         selection = random.randint(0,selection_length)
#                         card = list_of_cards[selection]
#                     card_name = card['NAME']
#                     tier = 0

#                     response = await crown_utilities.store_drop_card(str(ctx.author.id), card_name, universe, updated_vault, owned_destinies, 0, 0, "Purchase", True, int(price), "cards")
#                     await button_ctx.send(response)

#             else:
#                 await ctx.send("This is not your Shop.")
#         await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
#             custom_action_row,
#             custom_function,
#         ]).run()
#     except Exception as ex:
#         trace = []
#         tb = ex.__traceback__
#         while tb is not None:
#             trace.append({
#                 "filename": tb.tb_frame.f_code.co_filename,
#                 "name": tb.tb_frame.f_code.co_name,
#                 "lineno": tb.tb_lineno
#             })
#             tb = tb.tb_next
#         print(str({
#             'type': type(ex).__name__,
#             'message': str(ex),
#             'trace': trace
#         }))

        

def setup(bot):
    Profile(bot)
