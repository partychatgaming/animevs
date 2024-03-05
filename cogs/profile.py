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
import custom_logging
import destiny as d
import random
import uuid
from .classes.custom_paginator import CustomPaginator
from interactions.ext.paginators import Paginator
from interactions import Client, ActionRow, Button, ButtonStyle, File, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension, slash_option


emojis = ['👍', '👎']

class Profile(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Profile Cog is ready!')


    @slash_command(description="Delete your account")
    async def deleteaccount(self, ctx):
        _uuid = uuid.uuid4()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            await ctx.send("You are not registered. Please register with /register", ephemeral=True)
        
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

        msg = await ctx.send(f"{ctx.author.mention}, are you sure you want to delete your account?\nAll of your stats, purchases and other earnings will be removed from the system and can not be recovered.", ephemeral=True, components=[accept_buttons_action_row])

        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author

        try:
            button_ctx = await self.bot.wait_for_component(components=[accept_buttons_action_row], timeout=300, check=check)

            if button_ctx.ctx.custom_id == f"{_uuid}|no":
                await button_ctx.send("Account not deleted.")
                return

            if button_ctx.ctx.custom_id == f"{_uuid}|yes":
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
            custom_logging.debud(ex)
            embed = Embed(title="Error", description="Something went wrong. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed, ephemeral=True)

    # @slash_command(description="main menu where all your important game items and builds are",
    #                 options=[
    #                     SlashCommandOption(
    #                         name="selection",
    #                         description="select an option to continue",
    #                         type=OptionType.STRING,
    #                         required=True,
    #                         choices=[
    #                             SlashCommandChoice(
    #                                 name="🎴 My Cards",
    #                                 value="cards",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="🎗️ My Titles",
    #                                 value="titles",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="🦾 My Arms",
    #                                 value="arms",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="🧬 My Summons",
    #                                 value="summons",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="⚔️ Current Build",
    #                                 value="build",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="💼 Check Card Storage",
    #                                 value="storage",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="✨⚔️ Quick Build",
    #                                 value="quickbuild",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="💰 My Money",
    #                                 value="balance",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="💎 Gem Bag",
    #                                 value="gems"
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="🪔 Essence",
    #                                 value="essence",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="📤 Load Presets",
    #                                 value="presets",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="📥 Save Current Preset",
    #                                 value="savepreset",
    #                             ),
    #                             SlashCommandChoice(
    #                                 name="⚒️ Visit the Blacksmith",
    #                                 value="blacksmith",
    #                             ),
    #                         ]
    #                     )
    #                 ]
    #     )
    # async def menu(self, ctx, selection):
    #     if selection == "cards":
    #         await self.cards(ctx)
    #     if selection == "titles":
    #         await self.titles(ctx)
    #     if selection == "arms":
    #         await self.arms(ctx)
    #     if selection == "build":
    #         await self.build(ctx)
    #     if selection == "summons":
    #         await self.summons(ctx)
    #     if selection == "storage":
    #         await self.storage(ctx)
    #     if selection == "quickbuild":
    #         await self.quickbuild(ctx)
    #     if selection == "balance":
    #         await self.balance(ctx)
    #     if selection == "presets":
    #         await self.preset(ctx)
    #     if selection == "savepreset":
    #         await self.savepreset(ctx)
    #     if selection == "gems":
    #         await self.gems(ctx)
    #     if selection == "blacksmith":
    #         await self.blacksmith(ctx)
    #     if selection == "essence":
    #         await self.essence(ctx)

            
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
                        image_binary = c.showcard()
                        image_binary.seek(0)
                        card_file = File(file_name="image.png", file=image_binary)

                        embedVar = Embed(title=f"".format(self), color=000000)
                        embedVar.add_field(name="__Evasion__", value=f"🏃 | {c.evasion_message}")
                        embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                        embedVar.add_field(name=f"__Title Effects__\n🎗️ {t.name}", value=f"{title_message}", inline=False)
                        embedVar.set_image(url="attachment://image.png")
                        embedVar.set_author(name=textwrap.dedent(f"""\
                        Equipment
                        {a.arm_message} | ⚒️ {a.durability}
                        {player.talisman_message}
                        {player.summon_power_message}
                        {player.summon_lvl_message}
                        """))
                        embedVar.set_thumbnail(url=player.avatar)
                        if c.card_lvl < 1000:
                            embedVar.set_footer(text=f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}\n♾️ | {c.set_trait_message()}")
                        else:
                            embedVar.set_footer(text=f"{level_up_message}\n♾️ | {c.set_trait_message()}")
                        
                        await ctx.send(file=card_file, embed=embedVar)
                        image_binary.close()
                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title="Build Error", description="There was an error with your build command. Please try again later.", color=000000)
                    await ctx.send(embed=embed)
                    return
            else:
                embed = Embed(title="Build Error", description="You do not have a card registered. Please register a card before using /register.", color=000000)
                await ctx.send(embed=embed)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Build Error", description="There was an error with your build command. Please try again later.", color=000000)
            await ctx.send(embed=embed)


    @slash_command(description="Generate build")
    async def quickbuild(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        try:
            player = crown_utilities.create_player_from_data(a_registered_player)

            # Find random card from the list of cards in player.cards, queryCard using the random card name, and create_card_from_data
            random_card = random.choice(player.cards)
            card = db.queryCard({'NAME': random_card})
            c = crown_utilities.create_card_from_data(card)
            c.set_card_level_buffs(player.card_levels)

            # For each title in player.titles list queryTitle using the title name and select a random title from only the titles that have the same universe as card.universe
            
            title_list = []
            for title in player.titles:
                t = db.queryTitle({'TITLE': title})
                if t["UNIVERSE"] == c.universe:
                    title_list.append(t)
            if not title_list:
                embed = Embed(title="🎗️ Quick Build Cancelled", description=f"Your card was {c.name} - You do not have any titles from {c.universe_crest} {c.universe}.", color=000000)
                await ctx.send(embed=embed, ephemeral=True)
                return
            
            random_title = random.choice(title_list)
            t = crown_utilities.create_title_from_data(random_title)

            # For each arm in player.arms list queryArm using the arm name and select a random arm from only the arms that have the same universe as card.universe
            arm_list = []
            for arm in player.arms:
                a = db.queryArm({'ARM': arm["ARM"]})
                if a["UNIVERSE"] == c.universe:
                    arm_list.append(a)
            
            if not arm_list:
                embed = Embed(title="🦾 Quick Build Cancelled", description=f"Your card was {c.name} - You do not have any arms from {c.universe_crest} {c.universe}.", color=000000)
                await ctx.send(embed=embed, ephemeral=True)
                return
            
            random_arm = random.choice(arm_list)
            a = crown_utilities.create_arm_from_data(random_arm)


            random_summon = random.choice(player.summons)
            summon = db.querySummon({'PET': random_summon["NAME"]})
            s = crown_utilities.create_summon_from_data(summon)

            # Equip the card, title, arm and summon
            db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': c.name, 'TITLE': t.name, 'ARM': a.name, 'PET': s.name}})
            
            # Create embed that tells what has been equipped
            embed = Embed(title="Quick Build Complete", description=f"A build has been generated for you based on your inventory.", color=000000)
            embed.add_field(name="🎴 Card", value=f"{c.name}")
            embed.add_field(name="🎗️ Title", value=f"{t.name}")
            embed.add_field(name="🦾 Arm", value=f"{a.name}")
            embed.add_field(name="🧬 Summon", value=f"{s.name}")
            embed.set_image(url="attachment://image.png")
            embed.set_footer(text=f"Use /build to view your new build in more detail.")
            embed.set_thumbnail(url=ctx.author.avatar_url)
            image_binary = c.showcard()
            image_binary.seek(0)
            card_file = File(file_name="image.png", file=image_binary)
            await ctx.send(embed=embed, file=card_file)
            return
        
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Quick Build Error", description=f"There was an error with your quick build command. Please try again later.", color=000000)
            await ctx.send(embed=embed, ephemeral=True)
            return
    

    
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
                                    name="🧿 Energy",
                                    value="ENERGY",
                                ),
                                SlashCommandChoice(
                                    name="♻️ Reckless",
                                    value="RECKLESS",
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
                    title_data = crown_utilities.create_title_from_data(title)                    
                    all_titles.append(f"{title_data.universe_crest}: **{title_data.name}**\n")

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

                sorted_arms = sorted(arms, key=lambda arm: arm["ARM"])
                for index, arm in enumerate(sorted_arms):
                    durability = 0
                    arm_data = crown_utilities.create_arm_from_data(arm)
                    arm_data.set_drop_style()
                    for name in user['ASTORAGE']:
                        if name['ARM'] == arm_data.name:
                            arm_data.durability = int(name['DUR'])
                   
                    index = user['ASTORAGE'].index({'ARM': arm_data.name, 'DUR' : arm_data.durability})



                    all_arms.append(f"[{str(index)}] {arm_data.universe_crest} {arm_data.element_emoji}: **{arm_data.name}** ⚒️*{arm_data.durability}*\n**{arm_data.passive_type}** : *{arm_data.passive_value}*\n")


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
                    currently_on_market = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": c.name})
                    embedVar = Embed(title= f"{c.name}", description=textwrap.dedent(f"""\
                    {c.drop_emoji} **[{index}]** 
                    {c.class_emoji} {c.class_message}
                    🀄 {c.tier}: {c.level_icon} {c.card_lvl}
                    ❤️ **{c.health}** 🗡️ **{c.attack}** 🛡️ **{c.defense}** 🏃 **{c.evasion_message}**
                    
                    {c.move1_emoji} **{c.move1}:** {c.move1ap}
                    {c.move2_emoji} **{c.move2}:** {c.move2ap}
                    {c.move3_emoji} **{c.move3}:** {c.move3ap}
                    🦠 **{c.move4}:** {c.move4enh} {c.move4ap}{c.move4enh_suffix}

                    """), color=0x7289da)
                    embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                    embedVar.set_thumbnail(url=c.universe_image)
                    embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                    if currently_on_market:
                        embedVar.add_field(name="🏷️__Currently On Market__", value=f"Press the market button if you'd like to remove this product from the Market.")
                    embed_list.append(embedVar)
                    count += 1
                else:
                    update_storage_query = {
                                    '$pull': {'CARDS': card},
                                    '$addToSet': {'STORAGE': card},
                                }
                    response = db.updateUserNoFilter(query, update_storage_query)

            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=['Equip', 'Dismantle', 'Trade', 'Storage', 'Market'], paginator_type="Cards")
            if len(embed_list) <= 25:
                paginator.show_select_menu = True
            await paginator.send(ctx)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🎴 Cards Error", description="There's an issue with loading your cards. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0xff0000)
            await ctx.send(embed=embed)
            return


    @slash_command(description="View all of your titles", options=[
        SlashCommandOption(
            name="filtered",
            description="Filter by Universe of the card you have equipped",
            type=OptionType.BOOLEAN,
            required=True,
        )
    ])
    async def titles(self, ctx, filtered):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        player = crown_utilities.create_player_from_data(a_registered_player)
        card = crown_utilities.create_card_from_data(db.queryCard({"NAME": player.equipped_card}))
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
                if filtered:
                    if resp['UNIVERSE'] != card.universe:
                        continue
                index = player.titles.index(title)
                t = crown_utilities.create_title_from_data(resp)
                embedVar = Embed(title=f"{t.name}", description=f"{crown_utilities.crest_dict[t.universe]} | {t.universe} Title", color=0x7289da)
                embedVar.add_field(name=f"**Title Effects**", value="\n".join(t.title_messages), inline=False)
                # embedVar.add_field(name=f"**How To Unlock**", value=f"{t.unlock_method_message}", inline=False)                
                embed_list.append(embedVar)
            
            buttons = ["Equip"]
            
            custom_action_row = ActionRow(*buttons)
            if not embed_list and filtered:
                embed = Embed(title="🎗️ Titles", description=f"You currently own no Titles in {card.universe_crest} {card.universe}.", color=0x7289da)
                await ctx.send(embed=embed, ephemeral=True)
                return
            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=buttons, paginator_type="Titles")
            paginator.show_select_menu = True
            await paginator.send(ctx)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🎗️ Titles Error", description="There's an issue with loading your titles. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0xff0000)
            await ctx.send(embed=embed)


    @slash_command(description="View all of your arms", options=[
        SlashCommandOption(
            name="filtered",
            description="Filter by Universe of the card you have equipped",
            type=OptionType.BOOLEAN,
            required=True,
        )
    ])
    async def arms(self, ctx, filtered):
        await ctx.defer()
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            query = {'DID': str(ctx.author.id)}
            d = db.queryUser(query)
            player = crown_utilities.create_player_from_data(d)
            c = db.queryCard({"NAME": player.equipped_card})
            card = crown_utilities.create_card_from_data(c)
            if player:
                try:
                    current_gems = []
                    for gems in player.gems:
                        current_gems.append(gems['UNIVERSE'])

                    embed_list = []
                    sorted_arms = sorted(player.arms, key=lambda arm: arm['ARM'])
                    for index, arm in enumerate(sorted_arms):
                        resp = db.queryArm({"ARM": arm['ARM']})
                        if filtered:
                            if resp['UNIVERSE'] != card.universe:
                                continue
                        arm_data = crown_utilities.create_arm_from_data(resp)
                        arm_data.set_durability(arm_data.name, player.arms)
                        arm_data.set_arm_message(player.performance, card.universe)

                        embedVar = Embed(title= f"{arm_data.name}", description=textwrap.dedent(f"""
                        {arm_data.armicon} **[{index}]**

                        {arm_data.arm_type}
                        {arm_data.arm_message}
                        {arm_data.universe_crest} **Universe:** {arm_data.universe}
                        ⚒️ {arm_data.durability}
                        """), 
                        color=0x7289da)
                        embedVar.set_footer(text=f"{arm_data.footer}")
                        currently_on_market = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": arm_data.name})
                        if currently_on_market:
                            embedVar.add_field(name="🏷️__Currently On Market__", value=f"Press the market button if you'd like to remove this product from the Market.")

                        embed_list.append(embedVar)
                    
                    if not embed_list and filtered:
                        embed = Embed(title="🦾 Arms", description=f"You currently own no Arms in {card.universe_crest} {card.universe}.", color=0x7289da)
                        await ctx.send(embed=embed, ephemeral=True)
                        return
                    paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=['Equip', 'Dismantle', 'Trade', 'Storage', 'Market'], paginator_type="Arms")
                    if len(embed_list) <= 25:
                        paginator.show_select_menu = True
                    await paginator.send(ctx)
                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title="Arms Error", description="There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0x00ff00)
                    await ctx.send(embed=embed)
                    return
            else:
                embed = Embed(title="You are not registered.", description="Please register with the command /register", color=0x00ff00)
                await ctx.send(embed=embed)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Arms Error", description="There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", color=0x00ff00)
            await ctx.send(embed=embed)
            return
            

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
                paginator.show_select_menu = True
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
            _uuid = uuid.uuid4()
            user_query = {'DID': str(ctx.author.id)}
            user = crown_utilities.create_player_from_data(db.queryUser(user_query))
            card = crown_utilities.create_card_from_data(db.queryCard({"NAME": user.equipped_card}))
            card.set_card_level_buffs(user.card_levels)
            arm = crown_utilities.create_arm_from_data(db.queryArm({"ARM": user.equipped_arm}))
            arm.set_durability(user.equipped_arm, user.arms)

            preset_message = "Preset Upgraded!"
            if not user.preset_upgraded:
                preset_message = "10,000,000"

            boss_arm = False
            dungeon_arm = False
            boss_message = "Nice Arm!"
            abyss_arm = False
            boss_message = "Nice Arm!"
            arm_cost = '{:,}'.format(100000)
            durability_message = f"{arm_cost}"
            if arm.universe == "Unbound":
                abyss_arm= True
                arm_cost = '{:,}'.format(1000000)
                durability_message = f"{arm_cost}"
            if arm.drop_style == "Boss Drop":
                boss_arm = True
            
            if arm.drop_style == "Dungeon Drop":
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

            # has_gabes_purse = user['TOURNAMENT_WINS']
            # if not has_gabes_purse:
            #     gabes_message = "25,000,000"
            #     gabes_explain = "Purchase **Gabe's Purse** to Keep ALL ITEMS during **/rebirth**"
            balance = 0
            icon = "💎"

            for gems in user.gems:
                if gems['UNIVERSE'] == card.universe:
                    balance = gems['GEMS']
                    break   
            
            if not balance:
                embed = Embed(title="Blacksmith", description=f"You currently own no 💎 in {card.universe}.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            
            def get_level_icons(level):
                levels_icons = {
                    200: "🔱",
                    700: "⚜️",
                    999: "🏅"
                }
                for threshold, icon in sorted(levels_icons.items(), reverse=True):
                    if card.card_lvl >= threshold:
                        return icon
                return "🔰"

            def get_level_values(level):
                levels_values = {
                    200: (30000000, 20000000, 10000000),
                    300: (70000000, 50000000, 25000000),
                    400: (90000000, 75000000, 50000000),
                    500: (150000000, 100000000, 75000000),
                    600: (300000000, 200000000, 100000000),
                    700: (750000000, 500000000, 250000000),
                    800: (1000000000, 800000000, 500000000),
                    900: (5000000000, 2500000000, 1000000000),
                    1000: (20000000000, 5000000000, 5000000000),
                    2000: (80000000000, 13000000000, 9000000000)
                }
                for threshold, values in sorted(levels_values.items(), reverse=True):
                    if card.card_lvl >= threshold:
                        return values
                return 5000000, 1600000, 500000

            licon = get_level_icons(card.card_lvl)
            hundred_levels, thirty_levels, ten_levels = get_level_values(card.card_lvl)

            sell_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="🔋 1️⃣",
                        custom_id=f"{_uuid}|1"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="🔋 2️⃣",
                        custom_id=f"{_uuid}|2"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="🔋 3️⃣",
                        custom_id=f"{_uuid}|3"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="⚒️ 4️⃣",
                        custom_id=f"{_uuid}|5"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Cancel",
                        custom_id=f"{_uuid}|cancel"
                    )
                ]
            
            util_sell_buttons = [
                    Button(
                        style=ButtonStyle.GREY,
                        label="Gabe's Purse 👛",
                        custom_id=f"{_uuid}|4"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Storage 💼",
                        custom_id=f"{_uuid}|6"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Preset 🔖",
                        custom_id=f"{_uuid}|7"
                    )
            ]
            
            sell_buttons_action_row = ActionRow(*sell_buttons)
            util_sell_buttons_action_row = ActionRow(*util_sell_buttons)
            embedVar = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
            Welcome {ctx.author.mention}!
            Use Universe Gems to purchase **Card XP** and **Arm Durability**!
            🎴 Card:  **{card.name}** {licon}**{str(card.card_lvl)}**
            🦾 Arm: **{arm.name}** ⚒️*{str(arm.durability)}*
            
            **Card Level Boost**
            🔋 1️⃣ **10 Levels** for 🪙 **{'{:,}'.format(ten_levels)}**
            🔋 2️⃣ **30 Levels** for 💵 **{'{:,}'.format(thirty_levels)}**
            🔋 3️⃣ **100 Levels** for 💰 **{'{:,}'.format(hundred_levels)}**
            ⚒️ 4️⃣ **50 Durability** for 💵 **{durability_message}**
            
            **Miscellaneous Upgrades**
            💼 **Storage Tier {user.storage_message}**: 💸 **{user.storage_pricing_text}**
            🔖 **Preset Upgrade**: 💸 **{preset_message}**
            
            What would you like to buy?
            """), color=0xf1c40f)
            embedVar.set_footer(text="Boosts are used immediately upon purchase. Click cancel to exit purchase.", icon_url="https://cdn.discordapp.com/emojis/784402243519905792.gif?v=1")
            msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row, util_sell_buttons_action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.bot.wait_for_component(components=[sell_buttons_action_row, util_sell_buttons_action_row], timeout=120,check=check)
                await button_ctx.ctx.defer(edit_origin=True)
                option = button_ctx.ctx.custom_id
                levels_gained = 0
                price = 0
                exp_boost_buttons = [f"{_uuid}|1", f"{_uuid}|2", f"{_uuid}|3"]
                if option == f"{_uuid}|1":
                    levels_gained = 10
                    price = ten_levels
                if option == f"{_uuid}|2":
                    levels_gained = 30
                    price = thirty_levels
                if option == f"{_uuid}|3":
                    levels_gained = 100
                    price=hundred_levels
                if option == f"{_uuid}|5":
                    levels_gained = 50
                    price=100000
                if option == f"{_uuid}|cancel":
                    embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description="Blacksmith cancelled.", color=0xf1c40f)
                    await msg.edit(embed=embed, components=[])
                    return
                if option in exp_boost_buttons:
                    gems_left = balance - price
                    if price > balance:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"You do not have enough {card.universe} gems to make this purcahse.", color=0xf1c40f)
                        await msg.edit(embed=embed,components=[])
                        return

                    max_lvl = 1000
                    if card.card_lvl >= max_lvl:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"**{card.name}** is already at max smithing level. You may level up in battle, but you can no longer purchase levels for this card.", color=0xf1c40f)
                        await msg.edit(embed=embed, components=[])
                        return

                    if (levels_gained + card.card_lvl) > max_lvl:
                        levels_gained =  max_lvl - card.card_lvl


                    atk_def_buff = round(levels_gained / 2)
                    ap_buff = round(levels_gained / 3)
                    hlt_buff = (round(levels_gained / 20) * 25)

                    update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0}, '$inc': {'CARD_LEVELS.$[type].' + "LVL": levels_gained, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff, 'CARD_LEVELS.$[type].' + "DEF": atk_def_buff, 'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                    filter_query = [{'type.'+ "CARD": str(card.name)}]
                    response = db.updateUser(user.user_query, update_query, filter_query)
                    user.remove_gems(card.universe, price)
                    embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"**{card.name}** gained {levels_gained} levels!\nYou have {icon}{'{:,}'.format(gems_left)} gems left.", color=0xf1c40f)
                    await msg.edit(embed=embed, components=[])
                    if option == "cancel":
                        embed = Embed(title=f"{card.universe_crest} | {card.universe} Blacksmith - {icon}{'{:,}'.format(balance)} ", description="Blacksmith cancelled.", color=0xf1c40f)
                        await msg.edit(embed=embed, components=[])
                        return

                if option == f"{_uuid}|4":
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
                    
                if option == f"{_uuid}|7":
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
                
                if option == f"{_uuid}|5":
                    if dungeon_arm:
                        price = 250000
                    if abyss_arm:
                        price = 1000000

                    gems_left = balance - price
                    # if boss_arm:
                    #     await button_ctx.send("Sorry I can't repair **Boss** Arms ...", ephemeral=True)
                    #     await msg.edit(components=[])
                    #     return
                    if price > balance:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"You do not have enough {card.universe} gems to make this purcahse.", color=0xf1c40f)
                        await msg.edit(embed=embed,components=[])
                        return
                    
                    if arm.durability >= 100:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"{arm.name} is already at Max Durability ⚒️", color=0xf1c40f)
                        await msg.edit(embed=embed, components=[])
                        return
                    else:
                        try:
                            new_durability = arm.durability + levels_gained
                            full_repair = False
                            if new_durability > 100:
                                levels_gained = 100 - arm.durability
                                full_repair=True
                            update_query = {'$inc': {'ARMS.$[type].' + 'DUR': levels_gained}}
                            filter_query = [{'type.' + "ARM": str(arm.name)}]
                            resp = db.updateUser(user.user_query, update_query, filter_query)

                            user.remove_gems(card.universe, price)
                            if full_repair:
                                embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"🦾 | {arm.name}'s ⚒️ durability has increased by **{levels_gained}**!\n*Maximum Durability Reached!*\n\nYou have {icon}{'{:,}'.format(gems_left)} gems left.", color=0xf1c40f)
                            else:
                                embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"🦾 | {arm.name}'s ⚒️ durability has increased by **{levels_gained}**!\nYou have {icon}{'{:,}'.format(gems_left)} gems left.", color=0xf1c40f)
                            await msg.edit(embed=embed, components=[])
                            return
                        except:
                            await ctx.send("Unsuccessful to purchase durability boost.", ephemeral=True)

                if option == f"{_uuid}|6":
                    if user.storage_pricing > balance:
                        await button_ctx.send("Insufficent funds.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                        
                    if not user.patron and user.storage_type >= 2:
                        await button_ctx.send("💞 | Only Patrons may purchase more than 30 additional storage. To become a Patron, visit https://www.patreon.com/partychatgaming?fan_landing=true.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                        
                    if user.storage_type == 10:
                        await button_ctx.send("💼 | You already have max storage.", ephemeral=True)
                        await msg.edit(components=[])
                        return
                        
                    else:
                        update = db.updateUserNoFilterAlt(user_query, {'$inc': {'STORAGE_TYPE': 1}})
                        user.remove_gems(card.universe, user.storage_pricing)
                        await button_ctx.send(f"💼 | Storage Tier {str(user.storage_type + 1)} has been purchased!")
                        await msg.edit(components=[])
                        return
            except asyncio.TimeoutError:
                await ctx.send("Blacksmith closed.", ephemeral=True)
            except Exception as ex:
                custom_logging.debug(ex)
                await ctx.send("Blacksmith closed unexpectedly. Seek support.", ephemeral=True)
        except asyncio.TimeoutError:
            await ctx.send("Blacksmith closed.", ephemeral=True)
        except Exception as ex:
            custom_logging.debug(ex)
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
                currently_on_market = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": summon.name})
                if currently_on_market:
                    embedVar.add_field(name="🏷️__Currently On Market__", value=f"Press the market button if you'd like to remove this product from the Market.")

                embed_list.append(embedVar)

            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Equip", "Trade", "Dismantle", "Market"], paginator_type="Summons")
            
            if len(embed_list) <= 25:
                paginator.show_select_menu = True
            await paginator.send(ctx)
            
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Summons Error", description="There's an issue with your Summons list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
            await ctx.send(embed=embed)
            return


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
                    await ctx.send(f"{ctx.author.mention} Preset Menu closed.", ephemeral=True)
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
                    embed = Embed(title=f"🔖 | Whoops!", description=f"Timed out. Please try again later.")
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
                    embed = Embed(title=f"🔖 | Whoops!", description=f"Something went wrong. Please try again later.")
                    await ctx.send(embed=embed)
                    return
            else:
                embed = Embed(title=f"🔖 | Whoops!", description=f"You are unable to save presets without an account.")
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
            embed = Embed(title=f"🔖 | Whoops!", description=f"Something went wrong. Please try again later.")
            await ctx.send(embed=embed)
            return

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

def setup(bot):
    Profile(bot)
