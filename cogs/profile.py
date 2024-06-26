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
from .quests import Quests
from .game_modes import enhancer_mapping, title_enhancer_mapping, enhancer_suffix_mapping, title_enhancer_suffix_mapping, passive_enhancer_suffix_mapping
import random
import textwrap
import uuid
import asyncio
import custom_logging
import destiny as d
from logger import loggy
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

        msg = await ctx.send(f"{ctx.author.mention}, are you sure you want to delete your account?\nAll of your stats, purchases and other earnings will be removed from the system and can not be recovered.", components=[accept_buttons_action_row])

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

            
    @slash_command(description="View your or a player's current build", options=[
        SlashCommandOption(
            name="player",
            description="Select a player to view their build",
            type=OptionType.USER,
            required=False
        )
    ])
    async def build(self, ctx, player=None):
        try:
            await ctx.defer()
            d = await crown_utilities.player_check(ctx)
            if not d:
                return

            player_name = ctx.author
            if player:
                uid = player.id
                query = {'DID': str(uid)}
                d = await asyncio.to_thread(db.queryUser, query)
                player_name = player
            else:
                uid = ctx.author.id

            # Batch queries
            card_data, title_data, arm_data = await asyncio.gather(
                asyncio.to_thread(db.queryCard, {'NAME': str(d['CARD'])}),
                asyncio.to_thread(db.queryTitle, {'TITLE': str(d['TITLE'])}),
                asyncio.to_thread(db.queryArm, {'ARM': str(d['ARM'])})
            )

            if not all([card_data, title_data, arm_data, d]):
                await ctx.send("Error: One or more of the required data is not available.")
                return

            try:
                c = crown_utilities.create_card_from_data(card_data)
                t = crown_utilities.create_title_from_data(title_data)
                a = crown_utilities.create_arm_from_data(arm_data)
                player = crown_utilities.create_player_from_data(d)

                title_message = "\n".join(t.title_messages)
                durability = a.set_durability(player.equipped_arm, player.arms)

                c.set_card_level_buffs(player.card_levels)
                c.set_affinity_message()
                c.set_arm_config(a.passive_type, a.name, a.passive_value, a.element)
                c.set_evasion_message(player)
                c.set_card_level_icon(player)

                lvl_req = round((float(c.card_lvl) / 0.0999) ** 1.25)
                player.set_talisman_message()
                player.setsummon_messages()

                a.set_arm_message(player.performance, c.universe)
                t.set_title_message(player.performance, c.universe)

                has_universe_heart = any(gem['UNIVERSE_HEART'] for gem in player.gems if gem['UNIVERSE'] == c.universe)
                has_universe_soul = any(gem['UNIVERSE_SOUL'] for gem in player.gems if gem['UNIVERSE'] == c.universe)

                rebirth_bonus = (player.rebirth + (player.prestige * 10) + 25) * (4 if has_universe_soul else 1)
                drebirth_bonus = ((player.rebirth + 1) * ((player.prestige * 10) + 100)) * (4 if has_universe_soul else 1)

                trebirth_message = f"_🌹⚔️Tales: {rebirth_bonus}xp_" if has_universe_soul else f"_⚔️Tales: {rebirth_bonus}xp_"
                drebirth_message = f"_🌹🔥Dungeon: {drebirth_bonus}xp_" if has_universe_soul else f"_🔥Dungeon: {drebirth_bonus}xp_"

                level_up_message = lvl_req - c.card_exp if c.card_lvl < crown_utilities.MAX_LEVEL else "👑 | Max Level!!"
                level_up_message = "🎆 Battle To Level Up!" if lvl_req - c.card_exp <= 0 else level_up_message

                embed_list = []
                common_embed_kwargs = {
                    "title": f"{c.level_icon} | {c.card_lvl} {c.name}",
                    "description": f"{crown_utilities.class_emojis[c.card_class]} | **{c.class_message}**\n"
                                f"🀄 | **{c.tier}**\n"
                                f"❤️ | **{c.max_health}**\n"
                                f"🗡️ | **{c.attack}**\n"
                                f"🛡️ | **{c.defense}**\n"
                                f"🏃 | **{c.evasion_message}**\n"
                                f"🎗️ | **{t.name}**\n"
                                f"**{title_message}**\n"
                                f"**{a.arm_message}**\n"
                                f"**{player.talisman_message}**\n"
                                f"{player.summon_power_message}\n"
                                f"{player.summon_lvl_message}\n"
                                f"{c.move1_emoji} | **{c.move1}:** {c.move1ap}\n"
                                f"{c.move2_emoji} | **{c.move2}:** {c.move2ap}\n"
                                f"{c.move3_emoji} | **{c.move3}:** {c.move3ap}\n"
                                f"🦠 | **{c.move4}:** {c.move4enh} {c.move4ap}{enhancer_suffix_mapping[c.move4enh]}\n",
                    "color": 0x000000,
                    "thumbnail": {"url": ctx.author.avatar_url},
                    "footer": {"text": f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}"}
                }

                if player.performance:
                    embedVar = Embed(**common_embed_kwargs)
                    embedVar.add_field(name="__Affinities__", value=c.affinity_message)
                    embedVar.set_image(url="attachment://image.png")
                    embed_list.append(embedVar)
                    await ctx.send(embed=embedVar)
                    loggy.info(f"Build command executed by {ctx.author} successfully with performance on")
                else:
                    image_binary = c.showcard()
                    image_binary.seek(0)
                    card_file = File(file_name="image.png", file=image_binary)

                    embed_pages = [
                        Embed(title=f"{player_name} Build Overview", description="For details, please check the other pages.", color=0x000000)
                            .add_field(name="__Build Summary__", value=f"Equipped Title 🎗️ **{t.name}**\n"
                            f"Equipped Arm 🦾 **{a.name}**\n"
                            f"Equipped Summon 🧬 **{player.equipped_summon}**\n"
                            f"Equipped Talisman **{player.talisman_message}**\n", inline=False)
                            .set_image(url="attachment://image.png")
                    ]

                    embed_pages.extend([
                        Embed(title=f"{player_name} Build Title View", description="Titles are buffs or boosts for your card, or against your opponents card, initiated each turn, focus, or resolve.", color=0x000000)
                            .add_field(name=f"__Title Name & Effects__\n🎗️ {t.name}", value=title_message, inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Arm View", description="Arms are protections for your card that are initiated by themselves until broken in battle, or they swappable abilities.", color=0x000000)
                            .add_field(name=f"__Arm Name & Effects__\n🦾 {a.name.capitalize()}", value=f"{a.arm_message}\n⚒️ {a.durability} *Durability*", inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Summon View", description="Summons are powerful companions that can be called upon to aid you in battle after you resolve, unless you're a summoner.", color=0x000000)
                            .add_field(name=f"__Summon Name & Effects__\n🧬 {player.equipped_summon}", value=f"{player.summon_power_message}\n📶 {player.summon_lvl_message}", inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Ability Breakdown", description="List of element effects per ability.", color=0x000000)
                            .add_field(name=f"__Basic Attack__", value=f"{c.move1_emoji} {c.move1_element.title()} - {crown_utilities.element_mapping[c.move1_element]}\n")
                            .add_field(name=f"__Special Attack__", value=f"{c.move2_emoji} {c.move2_element.title()} - {crown_utilities.element_mapping[c.move2_element]}\n")
                            .add_field(name=f"__Ultimate Attack__", value=f"{c.move3_emoji} {c.move3_element.title()} - {crown_utilities.element_mapping[c.move3_element]}\n")
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Talisman View", description="Talismans are powerful accessories that can be attuned to your card to bypass a single affinity.", color=0x000000)
                            .add_field(name="__Talisman Name & Effects__", value=player.talisman_message, inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Class View", description="Each card class has a unique ability or passive that activates during battle.", color=0x000000)
                            .add_field(name="__Card Class Effect__", value=crown_utilities.class_descriptions[c.card_class], inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Evasion View", description="Evasion is a stat that improves your evasiveness against attacks. With high evasion you will be hit less often.", color=0x000000)
                            .add_field(name="__Evasion Stat & Boost__", value=f"🏃 | {c.evasion_message}", inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Affinity View", description="Affinities are elemental strengths and weaknesses that can be exploited in battle.", color=0x000000)
                            .add_field(name="__Affinity List__", value=c.affinity_message, inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Level Up View", description="Leveling up your card will increase its attack, defense, health, and ability points.", color=0x000000)
                            .add_field(name="__Level Up Information__", value=f"EXP Until Next Level: {level_up_message}\nEXP Buff: {trebirth_message} | {drebirth_message}" if c.card_lvl < 1000 else f"Level Up Information: {level_up_message}", inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url),

                        Embed(title=f"{player_name} Build Trait View", description="Each universe has a unique ability or passive that can be activated in battle.", color=0x000000)
                            .add_field(name="__Trait List__", value=f"♾️ | {c.set_trait_message()}", inline=True)
                            .set_image(url="attachment://image.png")
                            .set_thumbnail(url=ctx.author.avatar_url)
                    ])

                    paginator = Paginator.create_from_embeds(self.bot, *embed_pages)
                    paginator.show_select_menu = True
                    await paginator.send(ctx, file=card_file)
                    image_binary.close()
                    loggy.info(f"Build command executed by {ctx.author} successfully")
            except Exception as ex:
                custom_logging.debug(ex)
                loggy.error(ex)
                embed = Embed(title="Build Error", description="There was an error with your build command. Please try again later.", color=0x000000)
                await ctx.send(embed=embed)
                return
        except Exception as ex:
            custom_logging.debug(ex)
            loggy.error(ex)
            embed = Embed(title="Build Error", description="There was an error with your build command. Please try again later.", color=0x000000)
            await ctx.send(embed=embed)

    @slash_command(description="Generate build")
    async def quickbuild(self, ctx):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        try:
            loggy.info(f"Quick Build command executed by {ctx.author}")
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
                                    name="⚔️ Sword",
                                    value="SWORD",
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
                                    name="🌿 Nature",
                                    value="NATURE",
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
                                    name="🩻 Rot",
                                    value="ROT",
                                ),
                                SlashCommandChoice(
                                    name="🔫 Gun",
                                    value="GUN",
                                ),
                                SlashCommandChoice(
                                    name="🏹 Ranged",
                                    value="RANGED",
                                ),
                                SlashCommandChoice(
                                    name="🧿 Energy / Spirit",
                                    value="ENERGY",
                                ),
                                SlashCommandChoice(
                                    name="♻️ Reckless",
                                    value="RECKLESS",
                                ),
                                SlashCommandChoice(
                                    name="💤 Sleep",
                                    value="SLEEP",
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
                                SlashCommandChoice(
                                    name="🔫 Gun",
                                    value="GUN",
                                ),
                                SlashCommandChoice(
                                    name="🩻 Rot",
                                    value="ROT",
                                ),
                                SlashCommandChoice(
                                    name="⚔️ Sword",
                                    value="SWORD",
                                ),
                                SlashCommandChoice(
                                    name="🌿 Nature",
                                    value="NATURE",
                                )
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
            player = crown_utilities.create_player_from_data(user)
            talismans = user["TALISMANS"]
            essence_list = user["ESSENCE"]
            if crown_utilities.is_maxed_out(talismans):
                embed = Embed(title="📿 Talisman", description="You have maxed out your talisman's. You can't infuse any more essence into them.", color=0x00ff00)
                await ctx.send(embed=embed)
            else:
                quest_message = await Quests.milestone_check(player, "TALISMANS_OWNED", 1)
                response = crown_utilities.essence_cost(user, selection)
                embed = Embed(title="📿 Talisman", description=response, color=0x00ff00)
                if quest_message:
                    embed.add_field(name="🏆 Milestone", value=quest_message)
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

                pagination = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Draw", "Market", "Dismantle"], paginator_type="Card Storage")
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
                    all_titles.append(f"{title_data.universe_crest} [{str(index)}] **{title_data.name}**\n")

                for i in range(0, len(all_titles), 10):
                    sublist = all_titles[i:i+10]           
                    embedVar = Embed(title=f"💼 {player.disname}'s Title Storage", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(
                        text=f"{len(all_titles)} Total Titles\n{str(storage_allowed_amount - len(player.tstorage))} Storage Available")
                    embed_list.append(embedVar)

                pagination = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Draw", "Market", "Dismantle"], paginator_type="Title Storage")
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
                    
                    pagination = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Draw", "Market", "Dismantle"], paginator_type="Arm Storage")
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


    @slash_command(description="View all of your cards", options=[
        SlashCommandOption(
            name="element_filter",
            description="select an option to continue",
            type=OptionType.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="👊 Physical", value="PHYSICAL"),
                SlashCommandChoice(name="🔥 Fire", value="FIRE"),
                SlashCommandChoice(name="❄️ Ice", value="ICE"),
                SlashCommandChoice(name="💧 Water", value="WATER"),
                SlashCommandChoice(name="⛰️ Earth", value="EARTH"),
                SlashCommandChoice(name="⚡️ Electric", value="ELECTRIC"),
                SlashCommandChoice(name="🌪️ Wind", value="WIND"),
                SlashCommandChoice(name="🔮 Psychic", value="PSYCHIC"),
                SlashCommandChoice(name="☠️ Death", value="DEATH"),
                SlashCommandChoice(name="❤️‍🔥 Life", value="LIFE"),
                SlashCommandChoice(name="🌕 Light", value="LIGHT"),
                SlashCommandChoice(name="🌑 Dark", value="DARK"),
                SlashCommandChoice(name="🧪 Poison", value="POISON"),
                SlashCommandChoice(name="🔫 Gun", value="GUN"),
                SlashCommandChoice(name="🩻 Rot", value="ROT"),
                SlashCommandChoice(name="⚔️ Sword", value="SWORD"),
                SlashCommandChoice(name="🌿 Nature", value="NATURE"),
                SlashCommandChoice(name="🏹 Ranged", value="RANGED"),
                SlashCommandChoice(name="🧿 Energy / Spirit", value="ENERGY"),
                SlashCommandChoice(name="♻️ Reckless", value="RECKLESS"),
                SlashCommandChoice(name="⌛ Time", value="TIME"),
                SlashCommandChoice(name="🅱️ Bleed", value="BLEED"),
                SlashCommandChoice(name="🪐 Gravity", value="GRAVITY"),
                SlashCommandChoice(name="💤 Sleep", value="SLEEP"),
            ]
        )
    ])
    async def cards(self, ctx, element_filter=None):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        
        query = {'DID': str(ctx.author.id)}
        d = db.queryUser(query)
        player = crown_utilities.create_player_from_data(d)
        
        try:
            # Fetch all cards and market data in batches
            card_names = player.cards
            card_queries = [asyncio.to_thread(db.queryCard, {"NAME": name}) for name in card_names]
            market_queries = [asyncio.to_thread(db.queryMarket, {"ITEM_OWNER": player.did, "ITEM_NAME": name}) for name in card_names]
            
            card_data_list, market_data_list = await asyncio.gather(
                asyncio.gather(*card_queries),
                asyncio.gather(*market_queries)
            )
            
            embed_list = []
            
            for i, card_data in enumerate(card_data_list):
                c = crown_utilities.create_card_from_data(card_data)
                if element_filter and element_filter not in [c.move1_element, c.move2_element, c.move3_element]:
                    continue

                c.set_card_level_buffs(player.card_levels)
                c.set_affinity_message()
                c.set_evasion_message(player)
                c.set_card_level_icon(player)
                
                currently_on_market = market_data_list[i]
                
                embedVar = Embed(title=f"{c.name}", description=textwrap.dedent(f"""\
                {c.universe_crest} {c.universe}
                {c.drop_emoji} **[{i}]** 
                {c.class_emoji} {c.class_message}
                🀄 {c.tier}: {c.level_icon} {c.card_lvl}
                ❤️ **{c.health}** 🗡️ **{c.attack}** 🛡️ **{c.defense}**
                
                {c.move1_emoji} **{c.move1}:** {c.move1ap}
                {c.move2_emoji} **{c.move2}:** {c.move2ap}
                {c.move3_emoji} **{c.move3}:** {c.move3ap}
                🦠 **{c.move4}:** {c.move4enh} {c.move4ap}{c.move4enh_suffix}
                """), color=0x7289da)
                
                embedVar.add_field(name="__Evasion__", value=f"🏃 | {c.evasion_message}")
                embedVar.add_field(name="__Affinities__", value=f"{c.affinity_message}")
                embedVar.set_thumbnail(url=c.universe_image)
                embedVar.set_footer(text=f"{len(player.cards)} Total Cards")
                
                if currently_on_market:
                    embedVar.add_field(name="🏷️__Currently On Market__", value="Press the market button if you'd like to remove this product from the Market.")
                
                embed_list.append(embedVar)
            
            if not embed_list:
                embed = Embed(title="🎴 Cards", description="You currently own no Cards.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            
            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=['Equip', 'Dismantle', 'Trade', 'Market'], paginator_type="Cards")
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
                # Add count of titles in set_footer
                embedVar.set_footer(text=f"{len(player.titles)} Total Titles")
                # embedVar.add_field(name=f"**How To Unlock**", value=f"{t.unlock_method_message}", inline=False)                
                embed_list.append(embedVar)
            
            buttons = ["Equip"]
            
            custom_action_row = ActionRow(*buttons)
            if not embed_list and filtered:
                embed = Embed(title="🎗️ Titles", description=f"You currently own no Titles in {card.universe_crest} {card.universe}.", color=0x7289da)
                await ctx.send(embed=embed, ephemeral=True)
                return

            if not embed_list:
                embed = Embed(title="🎗️ Titles", description="You currently own no Titles.", color=0x7289da)
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
            ),
        SlashCommandOption(
            name="type_filter",
            description="select an option to continue",
            type=OptionType.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="👊 Physical", value="PHYSICAL"),
                SlashCommandChoice(name="🔥 Fire", value="FIRE"),
                SlashCommandChoice(name="❄️ Ice", value="ICE"),
                SlashCommandChoice(name="💧 Water", value="WATER"),
                SlashCommandChoice(name="⛰️ Earth", value="EARTH"),
                SlashCommandChoice(name="⚡️ Electric", value="ELECTRIC"),
                SlashCommandChoice(name="🌪️ Wind", value="WIND"),
                SlashCommandChoice(name="🔮 Psychic", value="PSYCHIC"),
                SlashCommandChoice(name="☠️ Death", value="DEATH"),
                SlashCommandChoice(name="❤️‍🔥 Life", value="LIFE"),
                SlashCommandChoice(name="🌕 Light", value="LIGHT"),
                SlashCommandChoice(name="🌑 Dark", value="DARK"),
                SlashCommandChoice(name="🧪 Poison", value="POISON"),
                SlashCommandChoice(name="🔫 Gun", value="GUN"),
                SlashCommandChoice(name="🩻 Rot", value="ROT"),
                SlashCommandChoice(name="⚔️ Sword", value="SWORD"),
                SlashCommandChoice(name="🌿 Nature", value="NATURE"),
                SlashCommandChoice(name="💤 Sleep", value="SLEEP"),
                SlashCommandChoice(name="🏹 Ranged", value="RANGED"),
                SlashCommandChoice(name="🧿 Energy / Spirit", value="ENERGY"),
                SlashCommandChoice(name="♻️ Reckless", value="RECKLESS"),
                SlashCommandChoice(name="⌛ Time", value="TIME"),
                SlashCommandChoice(name="🅱️ Bleed", value="BLEED"),
                SlashCommandChoice(name="🪐 Gravity", value="GRAVITY"),
                SlashCommandChoice(name="🔄 Parry", value="PARRY"),
                SlashCommandChoice(name="🌐 Shield", value="SHIELD"),
                SlashCommandChoice(name="💠 Barrier", value="BARRIER"),
                SlashCommandChoice(name="Siphon", value="SIPHON"),
            ]
        )
    ])
    async def arms(self, ctx, filtered, type_filter=None):
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
                    current_gems = [gems['UNIVERSE'] for gems in player.gems]

                    embed_list = []
                    sorted_arms = sorted(player.arms, key=lambda arm: arm['ARM'])

                    # Fetch all arms and market data in batches
                    arm_names = [arm['ARM'] for arm in sorted_arms]
                    arm_queries = [asyncio.to_thread(db.queryArm, {"ARM": name}) for name in arm_names]
                    market_queries = [asyncio.to_thread(db.queryMarket, {"ITEM_OWNER": player.did, "ITEM_NAME": name}) for name in arm_names]

                    arm_data_list, market_data_list = await asyncio.gather(
                        asyncio.gather(*arm_queries),
                        asyncio.gather(*market_queries)
                    )

                    for index, arm_data in enumerate(arm_data_list):
                        if filtered and arm_data['UNIVERSE'] != card.universe:
                            continue
                        arm = crown_utilities.create_arm_from_data(arm_data)
                        arm.set_durability(arm.name, player.arms)
                        arm.set_arm_message(player.performance, card.universe)

                        if type_filter and arm.element != type_filter and arm.passive_type != type_filter:
                            continue

                        embedVar = Embed(title=f"{arm.name}", description=textwrap.dedent(f"""
                        {arm.armicon} **[{index}]**

                        {arm.arm_type}
                        {arm.arm_message}
                        {arm.universe_crest} **Universe:** {arm.universe}
                        ⚒️ {arm.durability}
                        """), color=0x7289da)
                        
                        embedVar.set_footer(text=f"{len(player.arms)} Total Arms")

                        if market_data_list[index]:
                            embedVar.add_field(name="🏷️__Currently On Market__", value="Press the market button if you'd like to remove this product from the Market.")

                        embed_list.append(embedVar)

                    if not embed_list and filtered:
                        embed = Embed(title="🦾 Arms", description=f"You currently own no Arms in {card.universe_crest} {card.universe}.", color=0x7289da)
                        await ctx.send(embed=embed, ephemeral=True)
                        return

                    if not embed_list and not filtered:
                        embed = Embed(title="🦾 Arms", description="You currently own no Arms.", color=0x7289da)
                        await ctx.send(embed=embed, ephemeral=True)
                        return

                    paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=['Equip', 'Dismantle', 'Trade', 'Market'], paginator_type="Arms")
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
                preset_message = "1,000,000"



            boss_arm = False
            dungeon_arm = False
            boss_message = "Nice Arm!"
            abyss_arm = False
            arm_cost = '{:,}'.format(1000)
            durability_message = f"{arm_cost}"
            if arm.universe == "Unbound":
                abyss_arm= True
                arm_cost = '{:,}'.format(25000)
                durability_message = f"{arm_cost}"
            if arm.drop_style == "Boss Drop":
                boss_arm = True 
            
            if arm.drop_style == "Dungeon Drop":
                dungeon_arm= True
                arm_cost = '{:,}'.format(5000)
                durability_message = f"{arm_cost}"

            if boss_arm:
                boss_message = "Cannot Repair"
                durability_message = "UNAVAILABLE"
            elif dungeon_arm:
                boss_message = "Dungeon eh?!"
            elif abyss_arm:
                boss_message = "That's Abyssal!!"

            balance = 0
            icon = "💎"

            for gems in user.gems:
                if gems['UNIVERSE'] == card.universe:
                    balance = gems['GEMS']
                    break   
            
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
                    200: (200000, 80000, 25000),
                    300: (300000, 125000, 50000),
                    400: (600000, 250000, 100000),
                    500: (1000000, 550000, 250000),
                    600: (2750000, 1200000, 500000),
                    700: (5000000, 2500000, 1000000),
                    800: (7500000, 4000000, 2500000),
                    900: (10000000, 7500000, 5000000),
                    1000: (50000000, 25000000, 10000000),
                    2000: (500000000, 250000000, 100000000)
                }

                for threshold, values in sorted(levels_values.items(), reverse=True):
                    if card.card_lvl >= threshold:
                        return values
                return 100000, 40000, 20000
            
            tier_values = {
                2: 200000,
                3: 450000,
                4: 1000000,
                5: 5000000,
                6: 10000000,
                7: 25000000,
                8: 100000000,
                9: 500000000,
                10: 1000000000, 
            }
            level_up_card_tier_message = f"⭐ **Increase Card Tier**: 💸 **{tier_values[(card.card_tier + 1)]:,}**" if card.card_tier < 10 else f"🌟 Your card has max tiers"
            licon = get_level_icons(card.card_lvl)
            hundred_levels, thirty_levels, ten_levels = get_level_values(card.card_lvl)

            # Calculate the cost to max level
            current_level = card.card_lvl
            max_level = 1500
            levels_needed = max_level - current_level
            max_level_cost = 0
            temp_level = current_level

            while temp_level < max_level:
                _, _, cost_per_100 = get_level_values(temp_level)
                if temp_level + 100 <= max_level:
                    max_level_cost += cost_per_100
                    temp_level += 100
                else:
                    _, cost_per_30, cost_per_10 = get_level_values(temp_level)
                    if temp_level + 30 <= max_level:
                        max_level_cost += cost_per_30
                        temp_level += 30
                    else:
                        max_level_cost += cost_per_10
                        temp_level += 10

            max_level_cost = f"{max_level_cost:,}"

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
                        label="⭐ Increase Card Tier",
                        custom_id=f"{_uuid}|6"
                    ),
                    Button(
                        style=ButtonStyle.GREY,
                        label="Gabe's Preset 🔖",
                        custom_id=f"{_uuid}|7"
                    )
            ]
            
            sell_buttons_action_row = ActionRow(*sell_buttons)
            util_sell_buttons_action_row = ActionRow(*util_sell_buttons)
            embedVar = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith - {icon}{'{:,}'.format(balance)}\n{user.balance_icon} {user.balance:,}", description=textwrap.dedent(f"""\
            Welcome {ctx.author.mention}!
            Use Universe Gems to purchase **Card XP** and **Arm Durability**!
            🎴 Card:  🀄️**{card.card_tier}** **{card.name}** {licon}**{str(card.card_lvl)}**
            🦾 Arm: **{arm.name}** ⚒️*{str(arm.durability)}*
            
            **Card Level Boost**
            🔋 1️⃣ **10 Levels** for {icon} **{'{:,}'.format(ten_levels)}**
            🔋 2️⃣ **30 Levels** for {icon} **{'{:,}'.format(thirty_levels)}**
            🔋 3️⃣ **100 Levels** for {icon} **{'{:,}'.format(hundred_levels)}**
            ⚒️ 4️⃣ **50 Durability** for {icon} **{durability_message}**
            
            **Miscellaneous Upgrades**
            {level_up_card_tier_message}
            🔖 **Gabe's Preset Upgrade**: 💸 **{preset_message}**
            
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
                if option == f"{_uuid}|max":
                    levels_gained = levels_needed
                    price = max_level_cost.replace(",", "")
                    price = int(price)
                    
                    if price > balance:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"You do not have enough {card.universe} gems to make this purchase.", color=0xf1c40f)
                        await msg.edit(embed=embed, components=[])
                        return
                    
                    if card.card_lvl >= max_level:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"**{card.name}** is already at max smithing level. You may level up in battle, but you can no longer purchase levels for this card.", color=0xf1c40f)
                        await msg.edit(embed=embed, components=[])
                        return

                    if (levels_gained + card.card_lvl) > max_level:
                        levels_gained = max_level - card.card_lvl

                    atk_def_buff = round(levels_gained / 2)
                    ap_buff = round(levels_gained / 3)
                    hlt_buff = (round(levels_gained / 20) * 25)

                    update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0}, '$inc': {'CARD_LEVELS.$[type].' + "LVL": levels_gained, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff, 'CARD_LEVELS.$[type].' + "DEF": atk_def_buff, 'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                    filter_query = [{'type.'+ "CARD": str(card.name)}]
                    response = db.updateUser(user.user_query, update_query, filter_query)
                    user.remove_gems(card.universe, price)
                    gems_left = balance - price
                    embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"**{card.name}** gained {levels_gained} levels!\nYou have {icon}{'{:,}'.format(gems_left)} gems left.", color=0xf1c40f)
                    milestone_message = await Quests.milestone_check(user, "BLACKSMITH", 1)
                    if milestone_message:
                        embed.add_field(name="🏆 **Milestone**", value=milestone_message)
                    await msg.edit(embed=embed, components=[])
                    return
                
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
                    price=1000
                if option == f"{_uuid}|cancel":
                    embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description="Blacksmith cancelled.", color=0xf1c40f)
                    await msg.edit(embed=embed, components=[])
                    return
                
                if option in exp_boost_buttons:
                    gems_left = balance - price
                    if price > balance:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"You do not have enough {card.universe} gems to make this purchase.", color=0xf1c40f)
                        await msg.edit(embed=embed,components=[])
                        return

                    max_lvl = 1500
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
                    
                if option == f"{_uuid}|7":
                    price = 100000
                    if price > user.balance:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description="Insufficent funds.", color=0xf1c40f)
                        # await button_ctx.ctx.send("Insufficent funds.", ephemeral=True)
                        await msg.edit(embeds=[embed], components=[])
                        return
                    if user.preset_upgraded:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description="You already have Gabe's Preset.", color=0xf1c40f)
                        # await button_ctx.ctx.send("You already have 5 Presets!", ephemeral=True)
                        await msg.edit(embeds=[embed], components=[])
                        return
                    else:
                        await crown_utilities.curse(price, user.did)
                        await asyncio.to_thread(db.updateUserNoFilter, {'DID': user.did}, {'$push': {'DECK' : {'CARD' : user.equipped_card, 'TITLE': user.equipped_title, 'ARM': user.equipped_arm, 'PET': "Chick", 'TALISMAN': user.equipped_talisman}}})
                        await asyncio.to_thread(db.updateUserNoFilter,{'DID': user.did}, {'$push': {'DECK' : {'CARD' : user.equipped_card, 'TITLE': user.equipped_title, 'ARM': user.equipped_arm, 'PET': "Chick", 'TALISMAN': user.equipped_talisman}}})
                        await asyncio.to_thread(db.updateUserNoFilterAlt, user_query, {'$set': {'U_PRESET': True}})
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"🔖 | Preset Upgraded", color=0xf1c40f)
                        # await button_ctx.ctx.send("🔖 | Preset Upgraded")
                        await msg.edit(embeds=[embed], components=[])
                        return
                
                if option == f"{_uuid}|5":
                    if dungeon_arm:
                        price = 5000
                    if abyss_arm:
                        price = 25000

                    gems_left = balance - price

                    if price > balance:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"You do not have enough {card.universe} gems to make this purchase.", color=0xf1c40f)
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
                    if tier_values[(card.card_tier + 1)] > user.balance:
                        # await button_ctx.ctx.send("Insufficent funds.", ephemeral=True)
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description="Insufficent funds.", color=0xf1c40f)
                        await msg.edit(embeds=[embed], components=[])
                        return

                    if card.card_tier >= 10:
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"⭐ | {card.name} is already at max tiers.", color=0xf1c40f)
                        await msg.edit(embeds=[embed], components=[])
                        return
                    
                    else:
                        new_tier = card.card_tier + 1
                        await crown_utilities.curse(tier_values[new_tier], user.did)
                        update_query = {'$inc': {'CARD_LEVELS.$[type].' + "TIER": 1}}
                        filter_query = [{'type.' + "CARD": card.name}]
                        response = await asyncio.to_thread(db.updateUser, user.user_query, update_query, filter_query)
                        # await button_ctx.ctx.send(f"⭐ | Your card has been upgraded to Tier {new_tier}!", ephemeral=True)
                        embed = Embed(title=f"{card.universe_crest} {card.universe} Blacksmith", description=f"⭐ | Your card has been upgraded to Tier {new_tier}!", color=0xf1c40f)
                        await msg.edit(embeds=[embed], components=[])
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
    

    @slash_command(description="View your summons", options=[
        SlashCommandOption(
            name="type_filter",
            description="select an option to continue",
            type=OptionType.STRING,
            required=False,
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
                    name="🧿 Energy / Spirit",
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
                SlashCommandChoice(
                    name="🔫 Gun",
                    value="GUN",
                ),
                # Add ROT, NATURE, and SWORD
                SlashCommandChoice(
                    name="🌿 Nature",
                    value="NATURE",
                ),
                SlashCommandChoice(
                    name="⚔️ Sword",
                    value="SWORD",
                ),
                SlashCommandChoice(
                    name="🩻 Rot",
                    value="ROT",
                ),
                SlashCommandChoice(
                    name="💤 Sleep",
                    value="SLEEP",
                ),
            ]
        )
    ])
    async def summons(self, ctx, type_filter=None):
        await ctx.defer()
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
                if type_filter:
                    if summon.ability_type != type_filter:
                        continue

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
                # Add count of summons in set_footer
                embedVar.set_footer(text=f"{len(player.summons)} Total Summons")
                embed_list.append(embedVar)

            if not embed_list:
                embed = Embed(title="🐾 Summons", description=f"You currently own no Summons.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Equip", "Trade", "Dismantle", "Market"], paginator_type="Summons")
            
            paginator.show_select_menu = True
            await paginator.send(ctx)
            
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Summons Error", description="There's an issue with your Summons list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
            await ctx.send(embed=embed)
            return


    @slash_command(description="View your balance")
    async def balance(self, ctx):
        user = await crown_utilities.player_check(ctx)
        if not user:
            return

        try:
            user_data = crown_utilities.create_player_from_data(user)
            tbal = 0
            fbal = 0


            if user['TEAM'] != 'PCG':
                t = db.queryTeam({'TEAM_NAME' : user['TEAM'].lower()})
                tbal = round(t['BANK'])

            # if user['FAMILY'] != 'PCG':
            #     f = db.queryFamily({'HEAD': user['DID']})
            #     fbal = round(f['BANK'])


            embedVar = Embed(title= f"Account Balances", description=textwrap.dedent(f"""
            **Account Balance:** {user_data.balance_icon}{'{:,}'.format(user_data.balance)}
            **Team Bank Balance:** {user_data.balance_icon}{'{:,}'.format(tbal)}
            """))
            await ctx.send(embed=embedVar)

        except Exception as ex:
            loggy.error(ex)
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
            await ctx.defer()
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            _uuid = uuid.uuid4()
            query = {'DID': str(ctx.author.id)}
            user = db.queryUser(query)
            if not user['DECK']:
                embed = Embed(
                    title=f"🔖 | Whoops!",
                    description=f"You do not have a preset saved yet. Use /savepreset to save your current build as a preset."
                )
                await ctx.send(embed=embed)
                return

            owned_items = await get_owned_items(user)
            presets = [get_preset_items(user['DECK'], i) for i in range(5)]
            listed_options = create_listed_options(presets[:3 if not user.get('U_PRESET') else 5])

            embedVar = Embed(title="🔖 | Preset Menu", description=textwrap.dedent(f"""
            {"".join(listed_options)}
            """))
            embedVar.set_thumbnail(url=user['AVATAR'])

            util_buttons = [Button(style=ButtonStyle.BLUE, label=f"{i+1}️⃣", custom_id=f"{_uuid}|{i+1}") for i in range(len(listed_options))]
            util_action_row = ActionRow(*util_buttons)

            msg = await ctx.send(embed=embedVar, components=[util_action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.bot.wait_for_component(components=[util_action_row], timeout=30, check=check)
                equipped_items, not_owned_items, update_data = await handle_button_click(button_ctx, presets, owned_items)

                response = db.updateUserNoFilter(query, {'$set': update_data})

                embed = Embed(title=f"🔖 | Build Updated")
                if equipped_items:
                    embed.add_field(name="Equipped Items", value="\n".join(equipped_items), inline=False)

                if not_owned_items:
                    embed.add_field(name="Not Owned", value="\n".join(not_owned_items), inline=False)
                    embed.set_footer(text="🔴 | Update this Preset with /savepreset!")
                embed.set_thumbnail(url=ctx.author.avatar_url)

                await msg.edit(embed=embed, components=[])
            except asyncio.TimeoutError:
                await msg.delete()
            except Exception as ex:
                loggy.critical(ex)
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
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.authour.mention} Preset Menu closed.", ephemeral=True)
        except Exception as ex:
            loggy.critical(ex)
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
                name = user['DISNAME'].split("#", 1)[0]
                avatar = user['AVATAR']
                cards = user['CARDS']
                titles = user['TITLES']
                deck = user['DECK']

                current_card = user['CARD']
                current_title = user['TITLE']
                current_arm = user['ARM']
                current_pet = user['PET']
                current_talisman = user['TALISMAN']
                current_talisman_message = crown_utilities.set_emoji(current_talisman) if current_talisman != "NULL" else "📿"
                current_talisman_element = current_talisman.title() if current_talisman != "NULL" else "None"

                preset_update = user.get('U_PRESET', False)
                listed_options = [
                    f"📝 | {current_title} {current_card} & {current_pet}\n**Card**: {current_card}\n**Title**: {current_title}\n**Arm**: {current_arm}\n**Summon**: {current_pet}\n**Talisman**: {current_talisman_message}{current_talisman_element}\n\n"
                ]

                for i in range(3):
                    if i < len(deck):
                        preset_card = deck[i].get('CARD', 'N/A')
                        preset_title = deck[i].get('TITLE', 'N/A')
                        preset_arm = deck[i].get('ARM', 'N/A')
                        preset_pet = deck[i].get('PET', 'N/A')
                        preset_talisman = deck[i].get('TALISMAN', 'N/A')
                        preset_message = crown_utilities.set_emoji(preset_talisman) if preset_talisman != "NULL" else "📿"
                        preset_element = preset_talisman.title() if preset_talisman != "NULL" else "None"
                        listed_options.append(
                            f"📝{i+1}️⃣ | {preset_title} {preset_card} and {preset_pet}\n**Card**: {preset_card}\n**Title**: {preset_title}\n**Arm**: {preset_arm}\n**Summon**: {preset_pet}\n**Talisman**: {preset_message}{preset_element}\n\n"
                        )

                if preset_update:
                    for i in range(3, 5):
                        if i < len(deck):
                            preset_card = deck[i].get('CARD', 'N/A')
                            preset_title = deck[i].get('TITLE', 'N/A')
                            preset_arm = deck[i].get('ARM', 'N/A')
                            preset_pet = deck[i].get('PET', 'N/A')
                            preset_talisman = deck[i].get('TALISMAN', 'N/A')
                            preset_message = crown_utilities.set_emoji(preset_talisman) if preset_talisman != "NULL" else "📿"
                            preset_element = preset_talisman.title() if preset_talisman != "NULL" else "None"
                            listed_options.append(
                                f"📝{i+1}️⃣ | {preset_title} {preset_card} and {preset_pet}\n**Card**: {preset_card}\n**Title**: {preset_title}\n**Arm**: {preset_arm}\n**Summon**: {preset_pet}\n**Talisman**: {preset_message}{preset_element}\n\n"
                            )

                embedVar = Embed(title=f"📝 | Save Current Build", description=textwrap.dedent(f"""
                {"".join(listed_options)}
                """))
                util_buttons = [Button(style=ButtonStyle.GREEN, label=f"📝 {i+1}️⃣", custom_id=f"{_uuid}|{i+1}") for i in range(3)]
                
                if preset_update:
                    util_buttons.extend([
                        Button(style=ButtonStyle.GREEN, label="📝4️⃣", custom_id=f"{_uuid}|4"),
                        Button(style=ButtonStyle.GREEN, label="📝5️⃣", custom_id=f"{_uuid}|5")
                    ])

                util_action_row = ActionRow(*util_buttons)
                msg = await ctx.send(embed=embedVar, components=[util_action_row])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.bot.wait_for_component(components=[util_action_row], timeout=120, check=check)

                    if button_ctx.ctx.custom_id == f"{_uuid}|0":
                        embed = Embed(title=f"🔖 | Preset Not Saved", description=f"No change has been made")
                        await msg.edit(embed=embed, components=[])
                        return

                    preset_number = button_ctx.ctx.custom_id.split('|')[-1]
                    response = db.updateUserNoFilter(query, {'$set': {
                        f'DECK.{int(preset_number) - 1}': {
                            'CARD': str(current_card),
                            'TITLE': str(current_title),
                            'ARM': str(current_arm),
                            'PET': str(current_pet),
                            'TALISMAN': str(current_talisman)
                        }
                    }})

                    if response:
                        talisman_message = crown_utilities.set_emoji(current_talisman)
                        embed = Embed(title=f"🔖 | Preset Saved to {preset_number} Slot")
                        embed.add_field(name="Card", value=f"🎴 | {current_card}", inline=False)
                        embed.add_field(name="Title", value=f"🎗️ | {current_title}", inline=False)
                        embed.add_field(name="Arm", value=f"🦾 | {current_arm}", inline=False)
                        embed.add_field(name="Summons", value=f"🧬 | {current_pet}", inline=False)
                        embed.add_field(name="Talisman", value=f"{talisman_message} | {current_talisman_element}", inline=False)
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await msg.edit(embed=embed, components=[])
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
            loggy.critical(ex)
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
        
    # @slash_command(description="Draw Items from Association Armory",
    #             options=[
    #                 SlashCommandOption(
    #                     name="mode",
    #                     description="Draw: Draw card, Dismantle:  Dismantle storage card, Resll: Resell storage card",
    #                     type=OptionType.STRING,
    #                     required=True,
    #                     choices=[
    #                         SlashCommandChoice(
    #                             name="🕋 🎴 Draw Armory Card",
    #                             value="cdraw"
    #                         ),SlashCommandChoice(
    #                             name="🕋 🎗️ Draw Armory Title",
    #                             value="tdraw"
    #                         ),SlashCommandChoice(
    #                             name="🕋 🦾 Draw Armory Arm",
    #                             value="adraw"
    #                         ),
    #                     ]
    #                 ),SlashCommandOption(
    #                     name="item",
    #                     description="Storage Item Name",
    #                     type=OptionType.STRING,
    #                     required=True,
    #                 )
    #             ]
    #     )
    # async def armory(self, ctx, mode:str, item:str):
        
    #     a_registered_player = await crown_utilities.player_check(ctx)
    #     if not a_registered_player:
    #         return
    #     query = {'DID': str(ctx.author.id)}
    #     d = db.queryUser(query)#Storage Update
    #     team = db.queryTeam({'TEAM_NAME': d['TEAM'].lower()})
    #     guild = db.queryGuildAlt({'GNAME': team['GUILD']})
    #     guild_name = ""
    #     if guild:
    #         guild_name = guild['GNAME']
    #         #in_guild = True
    #         guild_query = {"GNAME": guild['GNAME']}
    #     else:
    #         await ctx.send("Your Guild is not Associated.")
    #         return
    #     storage_type = d['STORAGE_TYPE']
    #     vault = db.queryVault({'DID': d['DID']})
    #     card_name = item
    #     title_name = item
    #     arm_name = item
    #     current_gems = []
    #     try: 
    #         if vault:
    #             for gems in vault['GEMS']:
    #                 current_gems.append(gems['UNIVERSE'])
    #             cards_list = vault['CARDS']
    #             card_levels = vault['CARD_LEVELS']
    #             title_list = vault['TITLES']
    #             arm_list = vault['ARMS']
    #             arm_list_names = []
    #             for names in arm_list:
    #                 arm_list_names.append(names['ARM'])
    #             total_cards = len(cards_list)
    #             total_titles = len(title_list)
    #             total_arms = len(arm_list)
    #             cstorage = guild['CSTORAGE']
    #             cstorage_levels = guild['S_CARD_LEVELS']
    #             tstorage = guild['TSTORAGE']
    #             astorage = guild['ASTORAGE']
    #             storage_arm_names = []
    #             item_owned = False
    #             levels_owned = False
    #             for snames in astorage:
    #                 storage_arm_names.append(snames['ARM'])
                
    #             storage_card = db.queryCard({'NAME': {"$regex": f"^{str(item)}$", "$options": "i"}})
    #             storage_title = db.queryTitle({'TITLE':{"$regex": f"^{str(item)}$", "$options": "i"} })
    #             storage_arm = db.queryArm({'ARM':{"$regex": f"^{str(item)}$", "$options": "i"}})
    #             lvl = 0
    #             tier = 0
    #             exp = 0
    #             ap_buff = 0
    #             atk_buff = 0
    #             def_buff = 0
    #             hlt_buff = 0
    #             if mode == 'cdraw':
    #                 if total_cards > 24:
    #                     await ctx.send("You already have 25 cards.")
    #                     return
    #                 if storage_card:                  
    #                     if storage_card['NAME'] in cstorage:
    #                         if storage_card['NAME'] in cards_list:
    #                             item_owned = True
    #                         if not item_owned:
    #                             for levels in cstorage_levels:
    #                                 if levels['CARD'] == storage_card['NAME']:
    #                                     lvl = levels['LVL']
    #                                     tier = levels['TIER']
    #                                     exp = levels['EXP']
    #                                     ap_buff = levels['AP']
    #                                     atk_buff = levels['ATK']
    #                                     def_buff = levels['DEF']
    #                                     hlt_buff = levels['HLT']
    #                             for c in card_levels:
    #                                 if c['CARD'] == storage_card['NAME']:
    #                                     levels_owned = True
                                                            
                            
    #                         if not item_owned:
    #                             transaction_message = f"{ctx.author} claimed 🎴**{storage_card['NAME']}**."
    #                             query = {'DID': str(ctx.author.id)}
    #                             update_gstorage_query = {
    #                                 '$pull': {'CSTORAGE': storage_card['NAME'], 'S_CARD_LEVELS' : {'CARD' :  storage_card['NAME']}},
    #                                 '$push': {'TRANSACTIONS': transaction_message}
    #                             }
    #                             response = db.updateGuildAlt(guild_query, update_gstorage_query)
    #                             update_storage_query = {
    #                                 '$addToSet': {'CARDS': storage_card['NAME']},
    #                             }
    #                             response = db.updateUserNoFilter(query, update_storage_query)
    #                             if not levels_owned:
    #                                 update_glevel_query = {
    #                                 '$addToSet' : {
    #                                         'CARD_LEVELS': {'CARD': str(storage_card['NAME']), 'LVL': lvl, 'TIER': tier, 'EXP': exp,
    #                                                         'HLT': hlt_buff, 'ATK': atk_buff, 'DEF': def_buff, 'AP': ap_buff}}
    #                                 }
    #                                 response = db.updateUserNoFilter(query, update_glevel_query)
    #                         else:
    #                             await ctx.send(f"🎴**{storage_card['NAME']}** already owned**")
    #                             return
    #                         await ctx.send(f"🎴**{storage_card['NAME']}** has been added to **/cards**")
    #                         return
    #                     else:
    #                         await ctx.send(f"🎴:{storage_card['NAME']} does not exist in storage.")
    #                         return
    #                 else:
    #                     await ctx.send(f"🎴:{storage_card['NAME']} does not exist.")
    #                     return
    #             if mode == 'tdraw':
    #                 if total_titles > 24:
    #                     await ctx.send("You already have 25 titles.")
    #                     return
    #                 if storage_title:                  
    #                     if storage_title['TITLE'] in tstorage: #title storage update
    #                         if storage_title['TITLE'] in title_list:
    #                             item_owned = True
    #                         if not item_owned:
    #                             transaction_message = f"{ctx.author} claimed 🎗️ **{storage_title['TITLE']}**."
    #                             query = {'DID': str(ctx.author.id)}
    #                             update_storage_query = {
    #                                 '$addToSet': {'TITLES': storage_title['TITLE']},
    #                             }
    #                             response = db.updateUserNoFilter(query, update_storage_query)
    #                             update_gstorage_query = {
    #                                     '$pull': {'TSTORAGE': storage_title['TITLE']},
    #                                     '$push': {'TRANSACTIONS': transaction_message}
    #                                 }
    #                             response = db.updateGuildAlt(guild_query, update_gstorage_query)
    #                             transaction_message = f"{ctx.author} claimed 🎗️ **{storage_title['TITLE']}****."
    #                         else:
    #                             await ctx.send(f"🎗️ **{storage_title['TITLE']}** already owned**")
    #                             return
                            
    #                         await ctx.send(f"🎗️ **{storage_title['TITLE']}** has been added to **/titles**")
    #                         return
    #                     else:
    #                         await ctx.send(f"🎗️:{storage_title['TITLE']} does not exist in storage.")
    #                         return
    #                 else:
    #                     await ctx.send(f"🎗️:{storage_title['TITLE']} does not exist.")
    #                     return
    #             if mode == 'adraw':
    #                 if total_arms > 24:
    #                     await ctx.send("You already have 25 arms.")
    #                     return
    #                 if storage_arm:                  
    #                     if storage_arm['ARM'] in storage_arm_names: #title storage update
    #                         if storage_arm['ARM'] in arm_list_names:
    #                             item_owned = True
    #                         durability = 0
    #                         for arms in astorage:
    #                             if storage_arm['ARM'] == arms['ARM']:
    #                                 durability = arms['DUR']
    #                                 #print(durability)
    #                         if not item_owned:
    #                             transaction_message = f"{ctx.author} claimed 🦾 **{storage_arm['ARM']}**."
    #                             query = {'DID': str(ctx.author.id)}
    #                             update_storage_query = {
    #                                 '$addToSet': {'ARMS': {'ARM' : str(storage_arm['ARM']) , 'DUR': int(durability)}},
    #                             }
    #                             response = db.updateUserNoFilter(query, update_storage_query)
    #                             update_gstorage_query = {
    #                                 '$pull': {'ASTORAGE': {'ARM' : str(storage_arm['ARM'])}},
    #                                 '$push': {'TRANSACTIONS': transaction_message}
    #                             }
    #                             response = db.updateGuildAlt(guild_query, update_gstorage_query)
    #                         else:
    #                             await ctx.send(f"🦾 **{storage_arm['ARM']}** already owned**")
    #                             return
    #                         await ctx.send(f"🦾 **{storage_arm['ARM']}** has been added to **/arms**")
    #                         return
    #                     else:
    #                         await ctx.send(f"🦾 :{storage_arm['ARM']} does not exist in storage.")
    #                         return
    #                 else:
    #                     await ctx.send(f"🦾 :{storage_arm['ARM']} does not exist.")
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
    #         await ctx.send(f"Error with Armory. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
    #         return

    @slash_command(description="Equip a Card", options=[
            SlashCommandOption(
                name="card",
                description="Type in the name of the card you want to equip",
                type=OptionType.STRING,
                required=True,
            )
    ])
    async def equipcard(self, ctx, card: str):
        await ctx.defer()
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        card_name = card
        user_query = {'DID': str(ctx.author.id)}

        user, card_resp = await asyncio.gather(
            asyncio.to_thread(db.queryUser, user_query),
            asyncio.to_thread(db.queryCard, {'NAME': {"$regex": f"^{str(card)}$", "$options": "i"}})
        )

        if card_resp is None:
            await ctx.send("Card not found. Please check the name and try again.", ephemeral=True)
            return

        card_name = card_resp["NAME"]

        if card_name in user['CARDS']:
            player_class = crown_utilities.create_player_from_data(user)
            await asyncio.to_thread(db.updateUserNoFilter, user_query, {'$set': {'CARD': str(card_name)}})
            embed = Embed(title="🎴 Card Successfully Equipped", description=f"{card_name} has been equipped.", color=0x00ff00)
            quest_message = await Quests.milestone_check(player_class, "EQUIPPED_CARD", 1)
            if quest_message:
                embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("You do not own this card.", ephemeral=True)


    @slash_command(description="Equip an Arm", options=[
            SlashCommandOption(
                name="arm_name",
                description="Type in the name of the arm you want to equip",
                type=OptionType.STRING,
                required=True,
            )
    
    ])
    async def equiparm(self, ctx, arm_name: str):
        try:
            user_query = {'DID': str(ctx.author.id)}

            # Perform user and arm queries asynchronously
            user, resp = await asyncio.gather(
                asyncio.to_thread(db.queryUser, user_query),
                asyncio.to_thread(db.queryArm, {'ARM': {"$regex": f"^{str(arm_name)}$", "$options": "i"}})
            )

            if not resp:
                embed = Embed(title="Whoops!", description="Arm not found.", color=0xff0000)
                await ctx.send(embed=embed, ephemeral=True)
                return

            player = crown_utilities.create_player_from_data(user)
            a = crown_utilities.create_arm_from_data(resp)

            equipped = any(arm['ARM'] == a.name for arm in player.arms)
            if equipped:
                await asyncio.to_thread(db.updateUserNoFilter, user_query, {'$set': {'ARM': str(a.name)}})
                embed = Embed(title="🦾 Arm Successfully Equipped", description=f"**{a.name}** has been equipped.", color=0x00ff00)
                quest_message = await Quests.milestone_check(player, "EQUIPPED_ARM", 1)
                if quest_message:
                    embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)
            else:
                embed = Embed(title="🦾 Arm Not Equipped", description=f"You do not own the arm **{a.name}**.", color=0xff0000)

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
            embed = Embed(title="Error", description="An unexpected error occurred. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed, ephemeral=True)


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
                quest_message = await Quests.milestone_check(player, "EQUIPPED_SUMMON", 1)
                if quest_message:
                    embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

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


async def get_owned_items(user):
    """Extract owned items from the user object."""
    ownedcards = [card for card in user['CARDS']]
    ownedtitles = [title for title in user['TITLES']]
    ownedarms = [arm['ARM'] for arm in user['ARMS']]
    ownedpets = [pet['NAME'] for pet in user['PETS']]
    ownedtalismans = [talisman['TYPE'] for talisman in user['TALISMANS']]
    return ownedcards, ownedtitles, ownedarms, ownedpets, ownedtalismans


def get_preset_items(deck, index):
    """Extract preset items from the deck at the given index."""
    try:
        return {
            'card': list(deck[index].values())[0],
            'title': list(deck[index].values())[1],
            'arm': list(deck[index].values())[2],
            'pet': list(deck[index].values())[3],
            'talisman': list(deck[index].values())[4],
        }
    except IndexError:
        return {
            'card': None,
            'title': None,
            'arm': None,
            'pet': None,
            'talisman': "NULL",
        }


def build_preset_message(preset):
    """Build the message and element for the talisman in the preset."""
    message = "📿"
    element = "None"
    if preset['talisman'] != "NULL":
        message = crown_utilities.set_emoji(preset['talisman'])
        element = preset['talisman'].title()
    return message, element


def create_listed_options(presets):
    """Create a list of options for the embed."""
    listed_options = []
    for i, preset in enumerate(presets):
        message, element = build_preset_message(preset)
        listed_options.append(
            f"{i+1}️⃣ | {preset['title']} {preset['card']} and {preset['pet']}\n"
            f"**Card**: {preset['card']}\n**Title**: {preset['title']}\n"
            f"**Arm**: {preset['arm']}\n**Summon**: {preset['pet']}\n"
            f"**Talisman**: {message}{element}\n\n"
        )
    return listed_options


async def handle_button_click(button_ctx, presets, owned_items):
    """Handle the button click and return the equipped and not owned items."""
    preset_index = int(button_ctx.ctx.custom_id.split('|')[-1]) - 1
    preset = presets[preset_index]
    ownedcards, ownedtitles, ownedarms, ownedpets, ownedtalismans = owned_items

    equipped_items = []
    not_owned_items = []
    update_data = {}

    if preset['card'] in ownedcards:
        equipped_items.append(f"🎴 **Card** | {preset['card']}")
        update_data['CARD'] = str(preset['card'])
    else:
        not_owned_items.append(f"❌ {preset['card']}")

    if preset['title'] in ownedtitles:
        equipped_items.append(f"🎗️ **Title** | {preset['title']}")
        update_data['TITLE'] = str(preset['title'])
    elif preset['title']:
        not_owned_items.append(f"❌ | {preset['title']}")

    if preset['arm'] in ownedarms:
        equipped_items.append(f"🦾 **Arm** | {preset['arm']}")
        update_data['ARM'] = str(preset['arm'])
    elif preset['arm']:
        not_owned_items.append(f"❌ | {preset['arm']}")

    if preset['pet'] in ownedpets:
        equipped_items.append(f"🧬 **Summon** | {preset['pet']}")
        update_data['PET'] = str(preset['pet'])
    elif preset['pet']:
        not_owned_items.append(f"❌ | {preset['pet']}")

    if preset['talisman'] in ownedtalismans or preset['talisman'] == "NULL":
        message, element = build_preset_message(preset)
        equipped_items.append(f"{message} **Talisman** | {element}")
        update_data['TALISMAN'] = str(preset['talisman'])
    elif preset['talisman']:
        message, element = build_preset_message(preset)
        not_owned_items.append(f"❌ | {message}{element}")

    return equipped_items, not_owned_items, update_data


def setup(bot):
    Profile(bot)
