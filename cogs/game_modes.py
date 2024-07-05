import time
from re import T
import db
import dataclasses as data
import destiny as d
import messages as m
import numpy as np
import help_commands as h
from PIL import Image, ImageFont, ImageDraw
import requests
import random
now = time.asctime()
import base64
from io import BytesIO
import io
import asyncio
import textwrap
import crown_utilities
import custom_logging
from .universe import Universe as universe_cog
from .scenarios import Scenario as scenario_cog
from .tactics import Tactics as tactics_cog
from .reward_drops import RewardDrops as reward_drops_cog
from .classes.player_class import Player
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.arm_class import Arm
from .classes.summon_class import Summon
from .classes.battle_class  import Battle
from cogs.battle_config import BattleConfig
from logger import loggy
from pilmoji import Pilmoji
import destiny as d
import interactions
import uuid
from .classes.custom_paginator import CustomPaginator
from interactions.api.events import MessageCreate
from interactions import User, Cooldown, ActionRow, File, Button, ButtonStyle, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, SlashCommandChoice, Buckets, Embed, Extension, slash_option, AutocompleteContext



class GameModes(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.level_up_cooldown = Cooldown(Buckets.MEMBER, 10, 3600) # (Buckets.MEMBER, 10, 3600)
        self.explore_cooldown = Cooldown(Buckets.MEMBER, 25, 3600)
        self.rpg_game = None
    max_items = 150

    @listen()
    async def on_ready(self):
        print('Anime 🆚+ Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    async def companion(user):
        user_data = db.queryUser({'DID': str(user.id)})
        companion = user_data['DISNAME']
        return companion

    @listen()
    async def on_message_create(self, event: MessageCreate):
        try:
        
            message = event.message
            if message.author == self.bot.user:
                return
            guild_id_value = getattr(message, '_guild_id')
            setattr(message, 'guild_id', guild_id_value)

            if not await self.level_up_cooldown.acquire_token(message):
                try:
                    player_that_leveled = db.queryUser({'DID': str(message.author.id)})
                    if player_that_leveled:
                        card_that_leveled = db.queryCard({'NAME': player_that_leveled['CARD']})
                        uni = card_that_leveled['UNIVERSE']
                        nam = card_that_leveled['NAME']
                        mode = "Tales"
                        user = await self.bot.fetch_user(str(message.author.id))
                        leveled_up = await crown_utilities.cardlevel(user, mode)
                        await self.level_up_cooldown.reset(message)
                    else:
                        return
                except Exception as ex:
                    custom_logging.debug(ex)
                    return

            if not await self.explore_cooldown.acquire_token(message):
                # This has been included to start the cooldown over again if the explore procs
                await self.explore_cooldown.reset_all()
                if isinstance(message.channel, interactions.DMChannel):
                    return
    
                g = message.author.guild.name
                channel_list = message.author.guild.channels
                channel_names = []
                for channel in channel_list:
                    channel_names.append(channel.name)


                server_channel_response = db.queryServer({'GNAME': str(g)})
                server_channel = ""
                if server_channel_response:
                    server_channel = str(server_channel_response['EXP_CHANNEL'])

                print(f"Server Channel: {server_channel}")
                
                if "explore-encounters" in channel_names:
                    server_channel = "explore-encounters"
                
                if not server_channel:
                    print("No explore channel set for this server.")
                    return
    
                mode = "EXPLORE"
    
                # Pull Character Information
        
                player = db.queryUser({'DID': str(message.author.id)})
                if not player:
                    print("No player found.")
                    return
                p = crown_utilities.create_player_from_data(player)
           
                battle = Battle(mode, p)
                 
                # if p.get_locked_feature(mode) or not p.explore:
                #     print("Player is locked from exploring.")
                #     return
    
                if p.explore_location == "NULL":
                    all_universes = db.queryExploreUniverses()
                    available_universes = [x for x in all_universes]
    
                    u = len(available_universes) - 1
                    rand_universe = random.randint(1, u)
                    universe = available_universes[rand_universe]
                else:
                    universe = db.queryUniverse({"TITLE": p.explore_location})


                # Select Card at Random
                all_available_drop_cards = db.querySpecificDropCards(universe['TITLE'])
                cards = [x for x in all_available_drop_cards]
                selected_card = crown_utilities.create_card_from_data(random.choice(cards))
                selected_card.set_affinity_message()
                selected_card.set_explore_bounty_and_difficulty(battle)
    
                battle.set_explore_config(universe, selected_card)
                battle.bounty = selected_card.bounty
    
                random_battle_buttons = [
                    Button(
                        style=ButtonStyle.BLUE,
                        label="🪙 Gold",
                        custom_id="gold"
                    ),
                    Button(
                        style=ButtonStyle.GREEN,
                        label="👑 Glory",
                        custom_id="glory"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="Ignore",
                        custom_id="ignore"
                    )
                ]
    
                random_battle_buttons_action_row = ActionRow(*random_battle_buttons)
    
    
                # Send Message
                embedVar = Embed(title=f"**{selected_card.approach_message}{selected_card.name}** has a bounty!",
                                         description=textwrap.dedent(f"""\
                **Bounty** **{selected_card.bounty_message}**
                {selected_card.battle_message}
                """), color=0xf1c40f)

                embedVar.set_image(url="attachment://image.png")
                embedVar.set_thumbnail(url=message.author.avatar_url)
                embedVar.set_footer(text=f"Use /explore to exit Explore Mode",icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
                
                image_binary = selected_card.showcard()
                image_binary.seek(0)
                card_file = File(file_name="image.png", file=image_binary)
    
                setchannel = interactions.utils.get(channel_list, name=server_channel)
                await setchannel.send(f"🌌{message.author.mention}") 
                msg = await setchannel.send(embed=embedVar, file=card_file, components=[random_battle_buttons_action_row])     
                print("Message sent")
                def check(component: Button) -> bool:
                    return component.ctx.author == message.author
    
                try:
                    button_ctx  = await self.bot.wait_for_component(components=[random_battle_buttons_action_row], timeout=300, check=check)
                    await button_ctx.ctx.defer(edit_origin=True)
                    if button_ctx.ctx.custom_id == "glory":
                        battle.explore_type = "glory"
                        await BattleConfig.create_explore_battle(self, message, battle)
                        await msg.edit(components=[])
    
                    if button_ctx.ctx.custom_id == "gold":
                        battle.explore_type = "gold"
                        await BattleConfig.create_explore_battle(self, message, battle)
                        await msg.edit(components=[])
                    if button_ctx.ctx.custom_id == "ignore":
                        await msg.edit(components=[])
    
                except Exception as ex:
                    await msg.edit(components=[])
                    custom_logging.debug(ex)
        
        except Exception as ex:
            # await msg.edit(components=[])
            custom_logging.debug(ex)


    @slash_command(description="Duo pve to earn cards, accessories, gold, gems, and more with your AI companion",
                       options=[
                           SlashCommandOption(
                               name="deck",
                               description="AI Preset (this is from your preset list)",
                               type=OptionType.STRING,
                               required=True,
                               choices=[
                                   SlashCommandChoice(
                                       name="Preset 1",
                                       value="1"
                                   ),
                                   SlashCommandChoice(
                                       name="Preset 2",
                                       value="2"
                                   ),
                                   SlashCommandChoice(
                                       name="Preset 3",
                                       value="3"
                                   ),SlashCommandChoice(
                                       name="Preset 4",
                                       value="4"
                                   ),
                                   SlashCommandChoice(
                                       name="Preset 5",
                                       value="5"
                                   )
                               ]
                           ),
                           SlashCommandOption(
                               name="mode",
                               description="Difficulty Level",
                               type=OptionType.STRING,
                               required=True,
                               choices=[
                                   SlashCommandChoice(
                                       name="⚔️ Duo Tales (Normal)",
                                       value="DuoTales"
                                   ),
                                   SlashCommandChoice(
                                       name="👺 Duo Dungeon (Hard)",
                                       value="DDungeon"
                                   )
                               ]
                           )
                       ]
        )
    async def duo(self, ctx: InteractionContext, deck: int, mode: str):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        try:
            # 
            deck = int(deck)
            if deck != 1 and deck != 2 and deck != 3 and deck != 4 and deck != 5:
                await ctx.send("Not a valid Deck Option")
                return
            deckNumber = deck - 1

            player = db.queryUser({'DID': str(ctx.author.id)})
            
            if not player['U_PRESET'] and int(deck) > 3:
                await ctx.send("🪙 Purchase additional **/preset** slots at the **/blacksmith**")
                return

            p = crown_utilities.create_player_from_data(player)


            if not p.is_available:
                embed = Embed(title="⚠️ You are currently in a battle!", description="You must finish your current battle before starting a new one.", color=0x696969)
                await ctx.send(embed=embed)
                return

            p3 = crown_utilities.create_player_from_data(player)

            p3.set_deck_config(deckNumber)

            if p.get_locked_feature(mode):
                await ctx.send(p._locked_feature_message)
                return

            universe_selection = await select_universe(self, ctx, p, mode, None)
            if not universe_selection:
                return
            battle = Battle(mode, p)

            battle.set_universe_selection_config(universe_selection)
            battle.is_duo_mode = True
                
            await battle_commands(self, ctx, battle, p, None, player2=None, player3=p3)
        except Exception as ex:
            custom_logging.debug(ex)


    # @slash_command(description="Co-op pve to earn cards, accessories, gold, gems, and more with friends",
    #                    options=[
    #                        SlashCommandOption(
    #                            name="user",
    #                            description="player you want to co-op with",
    #                            type=OptionType.USER,
    #                            required=True
    #                        ),
    #                        SlashCommandOption(
    #                            name="mode",
    #                            description="Difficulty Level",
    #                            type=OptionType.STRING,
    #                            required=True,
    #                            choices=[
    #                                SlashCommandChoice(
    #                                    name="⚔️ Co-Op Tales (Normal)",
    #                                    value="CoopTales"
    #                                ),
    #                                SlashCommandChoice(
    #                                    name="👺 Co-Op Dungeon (Hard)",
    #                                    value="CoopDungeon"
    #                                ),
    #                                SlashCommandChoice(
    #                                    name="👹 Co-Op Boss Enounter (Extreme)",
    #                                    value="CBoss"
    #                                ),
    #                            ]
    #                        )
    #                    ]
    #     )
    async def coop(self, ctx: InteractionContext, user: User, mode: str):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        try:
            player = db.queryUser({'DID': str(ctx.author.id)})
            player3 = db.queryUser({'DID': str(user.id)})
            p1 = crown_utilities.create_player_from_data(player)
            p3 = crown_utilities.create_player_from_data(player3)

            if not p1.is_available:
                embed = Embed(title="⚠️ You are currently in a battle!", description="You must finish your current battle before starting a new one.", color=0x696969)
                await ctx.send(embed=embed)
                return

            if not p3.is_available:
                embed = Embed(title="⚠️ Your Co-op player is currently in a battle!", description="They must finish your current battle before starting a new one.", color=0x696969)
                await ctx.send(embed=embed)
                return


            battle = Battle(mode, p1)


            universe_selection = await select_universe(self, ctx, p1, mode, p3)
            if not universe_selection:
                return
            battle.set_universe_selection_config(universe_selection)
            battle.is_co_op_mode = True

            await battle_commands(self, ctx, battle, p1, None, None, p3)
        
        except Exception as ex:
            custom_logging.debug(ex)
            return


    @slash_command(description="pve to earn cards, accessories, gold, gems, and more as a solo player")
    @slash_option(
        name="mode",
        description="abyss: climb ladder, tales: normal pve mode, dungeon: hard pve run, and boss: extreme encounters",
        opt_type=OptionType.STRING,
        required=True,
        choices=[
            SlashCommandChoice(
                name="🆘 Anime VS+ Tutorial",
                value="Tutorial"
            ),
            SlashCommandChoice(
                name="⚡Randomize",
                value="Random"
            ),
            SlashCommandChoice(
                name="⚔️ Tales Run",
                value="Tales"
            ),
            SlashCommandChoice(
                name="👺 Dungeon Run",
                value="Dungeon"
            ),
            SlashCommandChoice(
                name="🎞️ Scenario Battle",
                value="Scenario"
            ),
            SlashCommandChoice(
                name="💀 Raid Battle",
                value="Raid_Scenario"
            )
        ]
    )
    @slash_option(
        name="universe",
        description="Universe to list traits for",
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def play(self, ctx: InteractionContext, mode: str, universe: str = ""):
        await ctx.defer()
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        
        if mode == "Random":
            mode_options = ["Tales", "Dungeon", "Scenario", "Raid_Scenario"]
            mode = random.choice(mode_options)
            universe = random.choice(crown_utilities.get_cached_universes())["name"]

        if not universe and mode != "Tutorial" and mode != "RPG":
            # Create embed that says to select a universe 
            embed = Embed(title="Select a Universe", description="All PVE game modes require universe selection. Please type or select a universe you would like to play in.", color=0x696969)
            await ctx.send(embed=embed)
            return

        """
        This command will be used to send all modes to either unvierse selection or battle commands
        If sent to unvierse selection the battle will be created inside the pagination of the universe selection
        """

        
        try:
            loggy.info(f"Mode: {mode} Universe: {universe} Player: {registered_player['DID']} has initiated a battle in {mode} mode.")
            player = crown_utilities.create_player_from_data(registered_player)
            if player.difficulty == "EASY" and mode == "Scenario":
                player.difficulty = "NORMAL"
            
            if player.difficulty in ["EASY", "NORMAL"] and mode == "Raid_Scenario":
                player.difficulty = "HARD"

            await player.set_guild_data()
            
            # if not player.is_available:
            #     embed = Embed(title="⚠️ You are currently in a battle!", description="You must finish your current battle before starting a new one.", color=0x696969)
            #     await ctx.send(embed=embed)
            #     return

            player.make_unavailable()

            # if mode == crown_utilities.ABYSS:
            #     await abyss(self, ctx, registered_player, mode)
            #     return

            

            if mode == crown_utilities.TUTORIAL:
                await tutorial(self, ctx, player, mode)
                return

            if mode == crown_utilities.SCENARIO:
                await scenario_cog.scenario_selector(self, ctx, universe, player)
                return

            if mode == "Raid_Scenario":
                await scenario_cog.raid_selector(self, ctx, universe, player)
                return

            if mode in crown_utilities.REG_MODES:
                if universe:
                    await universe_cog.universe_selector(self, ctx, mode, universe, player)
                    return
                else:
                    await universe_cog.universe_selector_paginator(self, ctx, mode, player)
                    return
            
            # if mode in crown_utilities.BOSS:
            #     print("boss")


            # if player1.get_locked_feature(mode):
            #     await ctx.send(player1._locked_feature_message)
            #     return

            # universe_selection = await select_universe(self, ctx, registered_player, mode, None)
            
            # if universe_selection == None:
            #     return

            # battle = Battle(mode, player1)

            # battle.set_universe_selection_config(universe_selection)
                
            # await battle_commands(self, ctx, battle, player1, None, player2=None, player3=None)
        except Exception as ex:
            player.make_available()
            custom_logging.debug(ex)
            loggy.critical(ex)
            return


    @slash_command(description="pvp battle against a friend or rival", options=[
        SlashCommandOption(
            name="opponent",
            description="Type in your opponent",
            type=OptionType.USER,
            required=False
        )
    ])
    async def pvp(self, ctx: InteractionContext, opponent: User):
        try:
            _uuid = uuid.uuid4()

            registered_player = await crown_utilities.player_check(ctx)
            if not registered_player:
                return
            mode = "PVP"
            player = db.queryUser({'DID': str(ctx.author.id)})
            player2 = db.queryUser({'DID': str(opponent.id)})
            p1 = crown_utilities.create_player_from_data(player)
            p2 = crown_utilities.create_player_from_data(player2)

            confirmation_buttons = [
                Button(
                    style=ButtonStyle.GREEN,
                    label="Accept",
                    custom_id=f"{_uuid}|accept"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="Decline",
                    custom_id=f"{_uuid}|decline"
                )
            ]

            action_row = ActionRow(*confirmation_buttons)

            if not p1.is_available:
                embed = Embed(title="⚠️ You are currently in a battle!", description="You must finish your current battle before starting a new one.", color=0x696969)
                await ctx.send(embed=embed)
                return

            if not p2.is_available:
                embed = Embed(title="⚠️ Your opponent is currently in a battle!", description="They must finish your current battle before starting a new one.", color=0x696969)
                await ctx.send(embed=embed)
                return
            
            if p1.did == p2.did:
                await ctx.send("You cannot PVP against yourself.", ephemeral=True)
                return

            if p1.get_locked_feature(mode):
                await ctx.send(p1._locked_feature_message)
                return
            if p2.get_locked_feature(mode):
                await ctx.send(p2._locked_feature_message)
                return
            
            u2 = self.bot.get_user(p2.did)

            embed = Embed(title="🆚 PVP Battle Request", description=f"{u2.mention} do you accept the challenge?", color=0x696969)
            msg = await ctx.send(embed=embed, components=[action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == opponent
            
            try:
                button_ctx  = await self.bot.wait_for_component(components=[action_row], timeout=300, check=check)
                await button_ctx.ctx.defer(edit_origin=True)
                if button_ctx.ctx.custom_id == f"{_uuid}|accept":
                    battle = Battle(mode, p1)
                    battle.is_pvp_game_mode = True
                    battle.set_tutorial(p2.did)
                    await button_ctx.ctx.send("🆚 Building PVP Match...", delete_after=10)
                    await msg.edit(components=[])

                    await BattleConfig.create_pvp_battle(self, ctx, battle, p2)
                    return 

                if button_ctx.ctx.custom_id == f"{_uuid}|decline":
                    await msg.edit(components=[])
                    return
            except Exception as ex:
                loggy.critical(ex)
                await msg.edit(components=[])
                custom_logging.debug(ex)
                return
        except Exception as ex:
            custom_logging.debug(ex)
            await ctx.send(f"An error occurred: {ex}")
            return

    
    #@slash_command(description="Start an Association Arena Battle")
    async def arena(self, ctx, guild):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        try:
            guildname = guild
            private_channel = ctx
            if isinstance(private_channel.channel, discord.channel.DMChannel):
                await private_channel.send(m.SERVER_FUNCTION_ONLY)
                return
            starttime = time.asctime()
            h_gametime = starttime[11:13]
            m_gametime = starttime[14:16]
            s_gametime = starttime[17:19]

            # Get Session Owner Disname for scoring
            sowner = db.queryUser({'DID': str(ctx.author.id)})
            if sowner['DIFFICULTY'] == "EASY":
                await ctx.send("Raiding is unavailable on Easy Mode! Use /difficulty to change your difficulty setting.")
                return

            guild = sowner['TEAM']
            guild_info = db.queryTeam({'TEAM_NAME': guild.lower()})
            oguild_name = "PCG"
            shield_test_active = False
            shield_training_active = False
            if guild_info:
                oguild_name = guild_info['GUILD']
                oassociation = db.queryGuildAlt({'GNAME': oguild_name})
            player_guild = sowner['GUILD']

            if oguild_name == "PCG":
                await ctx.send(m.NO_GUILD, delete_after=5)
                return
            if oassociation['SHIELD'] == sowner['DISNAME']:
                shield_training_active = True
            elif player_guild == guildname:
                shield_test_active = True
                

            guild_query = {'GNAME': guildname}
            association_info = db.queryGuildAlt(guild_query)
            guild_shield = ""

            if not association_info:
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
                return
            guild_shield = association_info['SHIELD']
            shield_id = association_info['SDID']
            guild_hall = association_info['HALL']
            hall_info = db.queryHall({'HALL': str(guild_hall)})
            hall_def = hall_info['DEFENSE']
            t_user = db.queryUser({'DID': shield_id})
            tteam_name = t_user['TEAM']
            tteam_info = db.queryTeam({'TEAM_NAME': tteam_name.lower()})
            tteam = tteam_info['TEAM_NAME']
            tguild = tteam_info['GUILD']
            if tteam_info:
                tguild = tteam_info['GUILD']
            tarm = db.queryArm({'ARM': t_user['ARM']})
            ttitle = db.queryTitle({'TITLE': t_user['TITLE']})
            
            # Guild Fees
            title_match_active = False
            fee = hall_info['FEE']
            if oguild_name == tguild:
                title_match_active = True
            
            
            mode = "RAID"
            
            player = sowner
            player2 = t_user
            p1 = crown_utilities.create_player_from_data(player)
            p2 = crown_utilities.create_player_from_data(player2)
            battle = Battle(mode, p1)
            battle.create_raid(title_match_active, shield_test_active, shield_training_active, association_info, hall_info, tteam, oguild_name)

            
            if private_channel:
                await battle_commands(self, ctx, battle, p1, None, p2, player3=None)
            else:
                await ctx.send("Failed to start raid battle!")
        except Exception as ex:
            custom_logging.debug(ex)
            guild = self.bot.get_guild(self.bot.guild_id)
            channel = guild.get_channel(self.bot.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return


    @play.autocomplete("universe")
    async def play_autocomplete(self, ctx: AutocompleteContext):
        choices = []
        options = crown_utilities.get_cached_universes()
        """
        for option in options
        if ctx.input_text is empty, append the first 24 options in the list to choices
        if ctx.input_text is not empty, append the first 24 options in the list that match the input to choices as typed
        """
            # Iterate over the options and append matching ones to the choices list
        for option in options:
                if not ctx.input_text:
                    # If input_text is empty, append the first 24 options to choices
                    if len(choices) < 24:
                        choices.append(option)
                    else:
                        break
                else:
                    # If input_text is not empty, append the first 24 options that match the input to choices
                    if option["name"].lower().startswith(ctx.input_text.lower()):
                        choices.append(option)
                        if len(choices) == 24:
                            break

        await ctx.send(choices=choices)


async def tutorial(self, ctx, player, mode):
    try:
        #
        # await ctx.send("🆚 Building Tutorial Match...", delete_after=10)
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        tutorial_did = '837538366509154407'
        opponent = db.queryUser({'DID': tutorial_did})
        player2 = crown_utilities.create_tutorial_bot(opponent)
        battle = Battle(mode, player)
        battle.set_tutorial(tutorial_did)
        battle.mode = "PVP"
        await BattleConfig.create_pvp_battle(self, ctx, battle, player2)
    
    except Exception as ex:
        custom_logging.debug(ex)
        loggy.critical(ex)
        embed = Embed(title="An error occurred when setting up the tutorial battle.", description=f"Error: {ex}", color=0x696969)
        await ctx.send(embed=embed)
        return
    
    
async def raid_scenario(self, ctx, player, mode):
    try:
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        response = db.queryUser({'DID': str(ctx.author.id)})
        player = crown_utilities.create_player_from_data(response)
        battle = Battle(mode, player)
        

        # await battle_commands(self, ctx, battle, player, None, player2, None)
    except Exception as ex:
        custom_logging.debug(ex)
        guild = self.bot.get_guild(self.bot.guild_id)
        channel = guild.get_channel(self.bot.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return


async def quest(player, opponent, mode):
    user_data = db.queryVault({'DID': str(player.id)})
    quest_data = {}
    try:
        if user_data['QUESTS']:
            for quest in user_data['QUESTS']:
                if opponent == quest['OPPONENT']:
                    quest_data = quest

            if quest_data == {}:
                return
            completion = quest_data['GOAL'] - (quest_data['WINS'] + 1)
            reward = int(quest_data['REWARD'])

            if str(mode) == "Dungeon" and completion >= 0:
                message = "Quest progressed!"
                if completion == 0:
                    await crown_utilities.bless(reward, player.id)
                    message = f"Quest Completed! 🪙{reward} has been added to your balance."

                query = {'DID': str(player.id)}
                update_query = {'$inc': {'QUESTS.$[type].' + "WINS": 2}}
                filter_query = [{'type.' + "OPPONENT": opponent}]
                resp = db.updateUser(query, update_query, filter_query)
                return message

            elif str(mode) == "Tales" and completion >= 0:
                message = "Quest progressed!"
                if completion == 0:
                    await crown_utilities.bless(reward, player.id)
                    message = f"Quest Completed! 🪙{reward} has been added to your balance."

                query = {'DID': str(player.id)}
                update_query = {'$inc': {'QUESTS.$[type].' + "WINS": 1}}
                filter_query = [{'type.' + "OPPONENT": opponent}]
                resp = db.updateUser(query, update_query, filter_query)

                return message
            else:
                return False
        else:
            return False
    except Exception as ex:
        custom_logging.debug(ex)
        return


async def savematch(player, card, path, title, arm, universe, universe_type, exclusive):
    matchquery = {'PLAYER': player, 'CARD': card, 'PATH': path, 'TITLE': title, 'ARM': arm, 'UNIVERSE': universe,
                  'UNIVERSE_TYPE': universe_type, 'EXCLUSIVE': exclusive}
    save_match = db.createMatch(data.newMatch(matchquery))


async def abyss_level_up_message(did, floor, card, title, arm):
    try:
        message = ""
        drop_message = []
        maxed_out_messages = []
        new_unlock = False
        vault_query = {'DID': did}
        vault = db.altQueryVault(vault_query)
        player = db.queryUser(vault_query)
        prestige = player['PRESTIGE']
        owned_destinies = []
        for destiny in vault['DESTINY']:
            owned_destinies.append(destiny['NAME'])
        card_info = db.queryCard({'NAME': str(card)})
        title_info = db.queryTitle({'TITLE': str(title)})
        arm = db.queryArm({'ARM':str(arm)})
        arm_arm = arm['ARM']
        floor_val = int(floor)
        coin_drop = round(100000 + (floor_val * 10000))
        durability = random.randint(75, 125)
        card_drop = card
        title_drop = title
        arm_drop = arm
        # Determine first to beat floor 100
        if floor == 100:
            all_users = db.queryAllUsers()
            first = True
            for user in all_users:
                if user['LEVEL'] == 101:
                    first = False
            if first:
                winner = {
                    'PLAYER': vault['OWNER'],
                    'DID': vault['DID'],
                    'CARD': card,
                    'TITLE': title,
                    'ARM': arm
                }
                rr = db.createGods(data.newGods(winner))

        
        if floor in abyss_floor_reward_list:
            u = await self.bot.bot.fetch_user(did)
            #Drops
            tresponse = await crown_utilities.store_drop_card(did, title_drop, title_info['UNIVERSE'], vault, owned_destinies, coin_drop, coin_drop, "Abyss", False, 0, "titles")
            aresponse = await crown_utilities.store_drop_card(did, arm_arm, arm['UNIVERSE'], vault, durability, coin_drop, coin_drop, "Abyss", False, 0, "arms")  
            cresponse = await crown_utilities.store_drop_card(did, card_drop, card_info['UNIVERSE'], vault, owned_destinies, coin_drop, coin_drop, "Abyss", False, 0, "cards")
            drop_message.append(tresponse)
            drop_message.append(aresponse)
            drop_message.append(cresponse)
            
        else:
            drop_message.append(f"🪙 **{'{:,}'.format(coin_drop)}** has been added to your vault!")
        if prestige < 1:

            if floor == 3:
                message = "🎊 Congratulations! 🎊 You unlocked **PVP and Guilds**. Use /pvp to battle another player or join together to form a Guild! Use /help to learn more.!"
                new_unlock = True

            if floor == 30:
                message = "🎊 Congratulations! 🎊 You unlocked **Marriage**. You're now able to join Families!Share summons and purchase houses.Use /help to learn more about  Family commands!"
                new_unlock = True
                
            if floor == 10:
                message = "🎊 Congratulations! 🎊 You unlocked **Trading**. Use the **/trade** command to Trade Cards, Titles and Arms with other players!"
                new_unlock = True


            if floor == 20:
                message = "🎊 Congratulations! 🎊 You unlocked **Gifting**. Use the **/gift** command to gift players money!"
                new_unlock = True
            
            if floor == 15:
                message = "🎊 Congratulations! 🎊 You unlocked **Associations**. Use the **/oath** to create an association with another Guild Owner!"
                new_unlock = True

            if floor == 25:
                message = "🎊 Congratulations! 🎊 You unlocked **Explore Mode**. Explore Mode allows for Cards to spawn randomly with Bounties! If you defeat the Card you will earn that Card + it's Bounty! Happy Hunting!"
                new_unlock = True

            if floor == 40:
                message = "🎊 Congratulations! 🎊 You unlocked **Dungeons**. Use the **/solo** command and select Dungeons to battle through the Hard Mode of Universes to earn super rare Cards, Titles, and Arms!"
                new_unlock = True

            if floor == 60:
                message = "🎊 Congratulations! 🎊 You unlocked **Bosses**. Use the **/solo** command and select Boss to battle Universe Bosses too earn ultra rare Cards, Titles, and Arms!"
                new_unlock = True
        if prestige < 10:
            if floor == (100 - (10 * prestige)):
                message = "🎊 Congratulations! 🎊 You unlocked **Soul Exchange**. Use the **/exchange** command and Exchange any boss souls for cards from their respective universe! This will Reset your Abyss Level!"
                new_unlock = True


        return {"MESSAGE": message, "NEW_UNLOCK": new_unlock, "DROP_MESSAGE": drop_message}
    except Exception as ex:
        custom_logging.debug(ex)
        return         

# DONT REMOVE THIS
cache = dict()

def get_card(url, cardname, cardtype):
    try:
        # save_path = f"image_cache/{str(cardtype)}/{str(cardname)}.png"
        # # print(save_path)
        
        # if url not in cache:
        #     # print("Not in Cache")
        #     cache[url] = save_path
        #     im = Image.open(requests.get(url, stream=True).raw)
        #     im.save(f"{save_path}", "PNG")
        #     # print(f"NO : {cardname}")
        #     return im

        # else:
        #     # print("In Cache")
        #     im = Image.open(cache[url])
        #     # print(f"YES : {cardname}")
        #     return im
        im = Image.open(requests.get(url, stream=True).raw)
        return im
           
    except Exception as ex:
        custom_logging.debug(ex)
        return         
          
    except Exception as ex:
        custom_logging.debug(ex)
        return

     
def showsummon(url, summon, message, lvl, bond):
    # Card Name can be 16 Characters before going off Card
    # Lower Card Name Font once after 16 characters
    try:
        im = Image.open(requests.get(url, stream=True).raw)

        draw = ImageDraw.Draw(im)

        # Font Size Adjustments
        # Name not go over Card
        name_font_size = 80
        if len(list(summon)) >= 10:
            name_font_size = 45
        if len(list(summon)) >= 14:
            name_font_size = 36
        

        header = ImageFont.truetype("YesevaOne-Regular.ttf", name_font_size)
        s = ImageFont.truetype("Roboto-Bold.ttf", 22)
        h = ImageFont.truetype("YesevaOne-Regular.ttf", 37)
        m = ImageFont.truetype("Roboto-Bold.ttf", 25)
        r = ImageFont.truetype("Freedom-10eM.ttf", 40)
        lvl_font = ImageFont.truetype("Neuton-Bold.ttf", 68)
        health_and_stamina_font = ImageFont.truetype("Neuton-Light.ttf", 41)
        attack_and_shield_font = ImageFont.truetype("Neuton-Bold.ttf", 48)
        moveset_font = ImageFont.truetype("antonio.regular.ttf", 40)
        rhs = ImageFont.truetype("destructobeambb_bold.ttf", 35)
        stats = ImageFont.truetype("Freedom-10eM.ttf", 30)
        card_details_font_size = ImageFont.truetype("destructobeambb_bold.ttf", 25)
        card_levels = ImageFont.truetype("destructobeambb_bold.ttf", 40)

        # Pet Name
        draw.text((600, 160), summon, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0),
                    align="left")

        # Level
        lvl_sizing = (89, 70)
        if int(lvl) > 9:
            lvl_sizing = (75, 70)
 
        draw.text(lvl_sizing, f"{lvl}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0),
                    align="center")
        draw.text((1096, 65), f"{bond}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0),
                    align="center")

        lines = textwrap.wrap(message, width=28)
        y_text = 330
        for line in lines:
            font=moveset_font
            width, height = font.getsize(line)
            with Pilmoji(im) as pilmoji:
                pilmoji.text(((1730 - width) / 2, y_text), line, (255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
            y_text += height


        with BytesIO() as image_binary:
            im.save(image_binary, "PNG")
            image_binary.seek(0)
            # await ctx.send(file=discord.File(fp=image_binary,filename="image.png"))
            file = discord.File(fp=image_binary,filename="pet.png")
            return file

    except Exception as ex:
        custom_logging.debug(ex)
        return


def setup(bot):
    GameModes(bot)


async def abyss(self, ctx: InteractionContext, _player, mode):
    #
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return

    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send(m.SERVER_FUNCTION_ONLY)
        return

    try:
        abyss = Battle(mode, _player)

        abyss_embed = abyss.set_abyss_config(_player)

        if not abyss_embed:
            await ctx.send(f"{abyss.abyss_message}")
            return

        abyss_buttons = [
            Button(
                style=ButtonStyle.BLUE,
                label="Begin",
                custom_id="Yes"
            ),
            Button(
                style=ButtonStyle.RED,
                label="Quit",
                custom_id="No"
            )
        ]

        abyss_buttons_action_row = ActionRow(*abyss_buttons)


        msg = await ctx.send(embed=abyss_embed, components=[abyss_buttons_action_row])

        def check(button_ctx):
            return button_ctx.author == ctx.author

        try:
            button_ctx  = await self.bot.wait_for_component(components=[
                abyss_buttons_action_row, abyss_buttons], timeout=120, check=check)

            if button_ctx.custom_id == "Yes":
                await button_ctx.defer(ignore=True)
                await msg.edit(components=[])

                if abyss.abyss_player_card_tier_is_banned:
                    await ctx.send(
                        f"❌ We're sorry! 🎴 | **{_player.equipped_card}** is banned on floor {abyss.abyss_floor}. Please, try again with another card.")
                    return
                
                await battle_commands(self, ctx, abyss, _player, None, player2=None, player3=None)

            elif button_ctx.custom_id == "No":
                await button_ctx.send("Leaving the Abyss...")
                await msg.edit(components=[])
                return
            else:
                await button_ctx.send("Leaving the Abyss...")
                await msg.edit(components=[])
                return
        except Exception as ex:
            custom_logging.debug(ex)
            guild = self.bot.get_guild(self.bot.guild_id)
            channel = guild.get_channel(self.bot.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
            return
    
    except Exception as ex:
        custom_logging.debug(ex)
        guild = self.bot.get_guild(self.bot.guild_id)
        channel = guild.get_channel(self.bot.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return


async def cardlist(self, ctx: InteractionContext, universe: str):
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return

    universe_data = db.queryUniverse({'TITLE': {"$regex": str(universe), "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_cards = db.queryAllCardsBasedOnUniverse({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
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
           
        class_info = card['CLASS']
        class_emoji = crown_utilities.class_emojis[class_info]
        class_message = class_info.title()

        available = ""
        is_skin = ""
        if card['AVAILABLE'] and card['EXCLUSIVE']:
            available = ":purple_circle:"
        elif card['AVAILABLE'] and not card['HAS_COLLECTION']:
            available = ":green_circle:"
        elif card['HAS_COLLECTION']:
            available = ":blue_circle:"
        else:
            available = "🟠"
        if card['IS_SKIN']:
            is_skin = ":white_circle:"
        
        if card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
            dungeon_card_details.append(
                f"{is_skin}{available}  🀄 {card['TIER']} **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")
        elif not card['HAS_COLLECTION']:
            tales_card_details.append(
                f"{is_skin}{available} 🀄 {card['TIER']} **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")
        elif card['HAS_COLLECTION']:
            destiny_card_details.append(
                f"{is_skin}{available} 🀄 {card['TIER']} **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")

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
        embedVar = Embed(title=f"{universe} Card List", description="\n".join(all_cards), color=0x7289da)
        embedVar.set_footer(
            text=f"{total_cards} Total Cards\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔵 Destiny Line\n🟠 Scenario Drop\n⚪ Skin")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(cards_broken_up)):
        embedVar = Embed(
            title=f"🎴 {universe_data['TITLE']} Card List",
            description="\n".join(cards_broken_up[i]), color=0x7289da)
        embedVar.set_footer(
            text=f"{total_cards} Total Cards\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔵 Destiny Line\n🟠 Scenario Drop\n⚪ Skin\n/view [Card Name]")
        embed_list.append(embedVar)

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def titlelist(self, ctx: InteractionContext, universe: str):
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_titles = db.queryAllTitlesBasedOnUniverses({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    titles = [x for x in list_of_titles]
    dungeon_titles_details = []
    tales_titles_details = []
    for title in titles:
        title_passive = title['ABILITIES'][0]
        title_passive_type = list(title_passive.keys())[0].title()
        title_passive_value = list(title_passive.values())[0]

        available = ""
        if title['AVAILABLE'] and title['EXCLUSIVE']:
            available = ":purple_circle:"
        elif title['AVAILABLE']:
            available = ":green_circle:"
        else:
            available = ":red_circle:"
        if title['EXCLUSIVE']:
            dungeon_titles_details.append(
                f"{available} 🎗️ **{title['TITLE']}**\n**{title_passive_type}:** {title_passive_value}\n")
        else:
            tales_titles_details.append(
                f"{available} 🎗️ **{title['TITLE']}**\n**{title_passive_type}:** {title_passive_value}\n")

    all_titles = []
    if tales_titles_details:
        for t in tales_titles_details:
            all_titles.append(t)

    if dungeon_titles_details:
        for d in dungeon_titles_details:
            all_titles.append(d)

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
        titles_broken_up = np.array_split(all_titles, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_titles) < 10:
        embedVar = Embed(title=f"{universe} Title List", description="\n".join(all_titles), color=0x7289da)
        # embedVar.set_thumbnail(url={universe_data['PATH']})
        embedVar.set_footer(text=f"{total_titles} Total Titles\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(titles_broken_up)):
        embedVar = Embed(title=f"🎗️ {universe_data['TITLE']} Title List",
                                                    description="\n".join(titles_broken_up[i]), color=0x7289da)
        # embedVar.set_thumbnail(url={universe_data['PATH']})
        embedVar.set_footer(
            text=f"{total_titles} Total Titles\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop\n/view [Title Name]")
        embed_list.append(embedVar)

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def armlist(self, ctx: InteractionContext, universe: str):
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_arms = db.queryAllArmsBasedOnUniverses({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    arms = [x for x in list_of_arms]
    dungeon_arms_details = []
    tales_arms_details = []
    for arm in arms:
        arm_passive = arm['ABILITIES'][0]
        arm_passive_type = list(arm_passive.keys())[0].title()
        arm_passive_value = list(arm_passive.values())[0]

        arm_message = f"🦾 **{arm['ARM']}**\n**{arm_passive_type}:** {arm_passive_value}\n"

        element = arm['ELEMENT']
        element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
        if element and arm_passive_type.upper() in element_available:
            element_name = element
            element = crown_utilities.set_emoji(element)
            arm_message = f"🦾 **{arm['ARM']}**\n{element} **{arm_passive_type} {element_name.title()} Attack:** {arm_passive_value}\n"

        available = ""
        if arm['AVAILABLE'] and arm['EXCLUSIVE']:
            available = ":purple_circle:"
        elif arm['AVAILABLE']:
            available = ":green_circle:"
        else:
            available = ":red_circle:"

        
        if arm['EXCLUSIVE']:
            dungeon_arms_details.append(
                f"{available} {arm_message}")
        else:
            tales_arms_details.append(
                f"{available} {arm_message}")

    all_arms = []
    if tales_arms_details:
        for t in tales_arms_details:
            all_arms.append(t)

    if dungeon_arms_details:
        for d in dungeon_arms_details:
            all_arms.append(d)

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
        arms_broken_up = np.array_split(all_arms, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_arms) < 10:
        embedVar = Embed(title=f"{universe} Arms List", description="\n".join(all_arms), color=0x7289da)
        embedVar.set_footer(text=f"{total_arms} Total Arms\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(arms_broken_up)):
        embedVar = Embed(title=f"🦾 {universe_data['TITLE']} Arms List",
                                                    description="\n".join(arms_broken_up[i]), color=0x7289da)
        embedVar.set_footer(
            text=f"{total_arms} Total Arms\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop\n /view [Arm Name]")
        embed_list.append(embedVar)

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def destinylist(self, ctx: InteractionContext, universe: str):
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return


    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    destinies = []
    for destiny in d.destiny:
        if destiny["UNIVERSE"].upper() == universe.upper():
            destinies.append(destiny)

    destiny_details = []
    for de in destinies:
        destiny_details.append(
            f":sparkles: **{de['NAME']}**\nDefeat {de['DEFEAT']} with {' '.join(de['USE_CARDS'])} {str(de['REQUIRED'])} times: Unlock **{de['EARN']}**\n")

    total_destinies = len(destiny_details)
    if total_destinies <= 0:
        await ctx.send(f"There are no current Destinies in **{universe_data['TITLE']}**. Check again later")
        return

    # Adding to array until divisible by 10
    while len(destiny_details) % 10 != 0:
        destiny_details.append("")
    # Check if divisible by 10, then start to split evenly

    if len(destiny_details) % 10 == 0:
        first_digit = int(str(len(destiny_details))[:1])
        if len(destiny_details) >= 89:
            if first_digit == 1:
                first_digit = 10
        destinies_broken_up = np.array_split(destiny_details, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(destiny_details) < 10:
        embedVar = Embed(title=f"{universe} Destiny List", description="\n".join(destiny_details),
                                color=0x7289da)
        embedVar.set_footer(text=f"{total_destinies} Total Destiny Lines")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(destinies_broken_up)):
        embedVar = Embed(title=f"🏵️  {universe_data['TITLE']} Destiny List",
                                                    description="\n".join(destinies_broken_up[i]), color=0x7289da)
        embedVar.set_footer(text=f"{total_destinies} Total Destiny Lines")
        embed_list.append(embedVar)

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def summonlist(self, ctx: InteractionContext, universe: str):
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return

    universe_data = db.queryUniverse({'TITLE': {"$regex": universe, "$options": "i"}})
    user = db.queryUser({'DID': str(ctx.author.id)})
    list_of_pets = db.queryAllSummonsBasedOnUniverses({'UNIVERSE': {"$regex": str(universe), "$options": "i"}})
    pets = [x for x in list_of_pets]
    dungeon_pets_details = []
    tales_pets_details = []
    for pet in pets:
        pet_ability = list(pet['ABILITIES'][0].keys())[0]
        pet_ability_power = list(pet['ABILITIES'][0].values())[0]
        pet_ability_type = list(pet['ABILITIES'][0].values())[1]
        pet_emoji = crown_utilities.set_emoji(pet_ability_type)
        available = ""
        if pet['AVAILABLE'] and pet['EXCLUSIVE']:
            available = ":purple_circle:"
        elif pet['AVAILABLE']:
            available = ":green_circle:"
        else:
            available = ":red_circle:"
        if pet['EXCLUSIVE']:
            dungeon_pets_details.append(
                f"{available} 🧬 **{pet['PET']}**\n**{pet_ability}:** {pet_ability_power}\n{pet_emoji} {pet_ability_type.capitalize()}\n")
        else:
            tales_pets_details.append(
                f"{available} 🧬 **{pet['PET']}**\n**{pet_ability}:** {pet_ability_power}\n{pet_emoji} {pet_ability_type.capitalize()}\n")

    all_pets = []
    if tales_pets_details:
        for t in tales_pets_details:
            all_pets.append(t)

    if dungeon_pets_details:
        for d in dungeon_pets_details:
            all_pets.append(d)

    total_pets = len(all_pets)

    # Adding to array until divisible by 10
    while len(all_pets) % 10 != 0:
        all_pets.append("")

    # Check if divisible by 10, then start to split evenly
    if len(all_pets) % 10 == 0:
        first_digit = int(str(len(all_pets))[:1])
        if len(all_pets) >= 89:
            if first_digit == 1:
                first_digit = 10
        pets_broken_up = np.array_split(all_pets, first_digit)

    # If it's not an array greater than 10, show paginationless embed
    if len(all_pets) < 10:
        embedVar = Embed(title=f"{universe} Summon List", description="\n".join(all_pets), color=0x7289da)
        embedVar.set_footer(text=f"{total_pets} Total Summons\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop")
        await ctx.send(embed=embedVar)

    embed_list = []
    for i in range(0, len(pets_broken_up)):
        embedVar = Embed(title=f"🧬 {universe_data['TITLE']} Summon List",
                                                    description="\n".join(pets_broken_up[i]), color=0x7289da)
        embedVar.set_footer(
            text=f"{total_pets} Total Summons\n🟢 Tale Drop\n🟣 Dungeon Drop\n🔴 Boss Drop\n/view [Summon Name]")
        embed_list.append(embedVar)

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⬅️', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('➡️', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = embed_list
    await paginator.run(embeds)


async def select_universe(self, ctx, player_data: object, mode: str, p2: None):
    # await p.set_guild_data()

    
    # if p.set_auto_battle_on(mode):
    #     embedVar = Embed(title=f"Auto-Battles Locked", description=f"To Unlock Auto-Battles Join Patreon!",
    #                              color=0xe91e63)
    #     embedVar.add_field(
    #         name=f"Check out the #patreon channel!\nThank you for supporting the development of future games!",
    #         value="-Party Chat Dev Team")
    #     await ctx.send(embed=embedVar)
    #     return

    if mode in crown_utilities.TALE_M or mode in crown_utilities.DUNGEON_M:
        available_universes = p.set_selectable_universes(ctx, mode, None)

        try:
            # print(custom_function.selected_universez
            selected_universe = custom_function.selected_universe
            if selected_universe == "":
                return

            universe = db.queryUniverse({'TITLE': str(selected_universe)})
            universe_owner = universe['GUILD']

            #Universe Cost
            entrance_fee = 1000


            if mode in crown_utilities.DUNGEON_M:
                entrance_fee = 5000
                
            if selected_universe in p.crestlist:
                await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | 🎏 {p.association} {selected_universe} Crest Activated! No entrance fee!")
            else:
                if int(p._balance) <= entrance_fee:
                    await ctx.send(f"Tales require an 🪙 {'{:,}'.format(entrance_fee)} entrance fee!", delete_after=5)
                    db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'AVAILABLE': True}})
                    return
                else:
                    await crown_utilities.curse(entrance_fee, str(ctx.author.id))
                    if universe_owner != 'PCG':
                        crest_guild = db.queryGuildAlt({'GNAME' : universe_owner})
                        if crest_guild:
                            await crown_utilities.blessguild(entrance_fee, universe['GUILD'])
                            await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | {crest_guild['GNAME']} Universe Toll Paid! 🪙{'{:,}'.format(entrance_fee)}")
            
            currentopponent = 0
            if mode != "EASY":
                currentopponent = update_save_spot(self, ctx, p.save_spot, selected_universe, crown_utilities.TALE_M)
                if mode in crown_utilities.DUNGEON_M:
                    currentopponent = update_save_spot(self, ctx, p.save_spot, selected_universe, crown_utilities.DUNGEON_M)
            else:
                currentopponent = 0
            if p.rift_on:
                update_team_response = db.updateTeam(p.guild_query, p.guild_buff_update_query)

            response = {'SELECTED_UNIVERSE': selected_universe,
                    'UNIVERSE_DATA': universe, 'CREST_LIST': p.crestlist, 'CREST_SEARCH': p.crestsearch,
                    'COMPLETED_TALES': p.completed_tales, 'OGUILD': p.association_info, 'CURRENTOPPONENT': currentopponent}
            
            if mode in crown_utilities.DUNGEON_M:
                response.update({'COMPLETED_DUNGEONS': p.completed_dungeons})

            return response
            
        except Exception as ex:
            custom_logging.debug(ex)

    if mode in crown_utilities.BOSS_M:
        l = []
        for uni in p.completed_tales:
            if uni != "":
                l.append(uni)
        available_dungeons_list = "\n".join(l)
        if p.boss_fought:
            boss_key_embed = Embed(title= f"🗝️  Boss Arena Key Required!", description=textwrap.dedent(f"""
            \n__How to get Boss Arena Keys?__
            \nConquer any Universe Dungeon to gain a Boss Arena Key
            \n☀️ | You also earn 1 Boss Key per /daily !
            \n__🌍 Available Universe Dungeons__
            \n{available_dungeons_list}
            """))
            boss_key_embed.set_thumbnail(url=ctx.author.avatar_url)
            # embedVar.set_footer(text="Use /tutorial")
            await ctx.send(embed=boss_key_embed)
            self.stop = True
            return  
        available_bosses = p.set_selectable_bosses(ctx, mode)

        if type(available_bosses) is not list:
            await ctx.send(embed=available_bosses)
            return
        
        custom_button = Button(style=3, label="Enter Boss Arena")

        async def custom_function(self, button_ctx):
            if button_ctx.author == ctx.author:
#                 if p.boss_fought:
#                     boss_key_embed = Embed(title= f"🗝️  Boss Arena Key Required!", description=textwrap.dedent(f"""
#                     __🗝️  How to get Arena Keys?__
#                     Conquer any Universe Dungeon to gain a Boss Arena Key
                    
#                     ☀️ | You also earn 1 Boss Key per /daily !

#                     __🌍 Available Universe Dungeons__
#                     {available_dungeons_list}
#                     """))
#                     boss_key_embed.set_thumbnail(url=ctx.author.avatar_url)
#                     # embedVar.set_footer(text="Use /tutorial")
#                     await ctx.send(embed=boss_key_embed)
#                     self.stop = True
#                     return    
                await button_ctx.defer(ignore=True)
                selected_universe = custom_function
                custom_function.selected_universe = str(button_ctx.origin_message.embeds[0].title)
                self.stop = True
            else:
                await ctx.send("This is not your button.", ephemeral=True)
        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=available_bosses, timeout=120,  customButton=[
            custom_button,
            custom_function,
        ]).run()
        try:
            # Universe Cost
            selected_universe = custom_function.selected_universe
            universe = db.queryUniverse({'TITLE': str(selected_universe)})
            universe_owner = universe['GUILD']
            #Universe Cost
            entrance_fee = 10000
            if selected_universe in p.crestlist:
                await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | 🎏 {p.association} {selected_universe} Crest Activated! No entrance fee!")
            else:
                if p._balance <= entrance_fee:
                    await ctx.send(f"Bosses require an 🪙 {'{:,}'.format(entrance_fee)} entrance fee!", delete_after=5)
                    db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'AVAILABLE': True}})
                    return
                else:
                    await crown_utilities.curse(entrance_fee, str(ctx.author.id))
                    if universe['GUILD'] != 'PCG':
                        crest_guild = db.queryGuildAlt({'GNAME' : universe['GUILD']})
                        if crest_guild:
                            await crown_utilities.blessguild(entrance_fee, universe['GUILD'])
                            await ctx.send(f"{crown_utilities.crest_dict[selected_universe]} | {crest_guild['GNAME']} Universe Toll Paid! 🪙{'{:,}'.format(entrance_fee)}")
            categoryname = "Crown Unlimited"
            #category = discord.utils.get(guild.categories, name=categoryname)

            # if category is None: #If there's no category matching with the `name`
            #     category = await guild.create_category_channel(categoryname)
            # private_channel = await guild.create_text_channel(f'{str(ctx.author)}-{mode}-fight', overwrites=overwrites, category=category)
            # await private_channel.send(f"{ctx.author.mention} private channel has been opened for you.")

            currentopponent = 0
            return {'SELECTED_UNIVERSE': selected_universe,
                    'UNIVERSE_DATA': universe, 'CREST_LIST': p.crestlist, 'CREST_SEARCH': p.crestsearch,
                    'COMPLETED_DUNGEONS': p.completed_dungeons, 'OGUILD': p.association_info, 'BOSS_NAME': universe['UNIVERSE_BOSS'],
                    'CURRENTOPPONENT': currentopponent}
        except asyncio.TimeoutError:
            await ctx.send(f"**{str(ctx.author)}** Boss Arena Timed Out", ephemeral=True)
        except Exception as ex:
            custom_logging.debug(ex)
            #embedVar = Embed(title=f"Unable to start boss fight. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", delete_after=30, color=0xe91e63)
            #await ctx.send(embed=embedVar)
            guild = self.bot.get_guild(self.bot.guild_id)
            channel = guild.get_channel(self.bot.guild_channel)
            await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")

            return


def health_and_stamina_bars(health, stamina, max_health, max_stamina, resolved):
    health_response = ""
    stamina_response = ""

    if health >= max_health:
        health_response = f"❤️❤️❤️❤️❤️"
    if health >= (max_health * .80) and health < max_health:
        health_response = f"❤️❤️❤️❤️💔"
    if health >= (max_health * .60) and health < (max_health * .80):
        health_response = f"❤️❤️❤️💔💔"
    if health >= (max_health * .40) and health < (max_health * .60):
        health_response = f"❤️❤️💔💔💔"
    if health >= (max_health * .20) and health < (max_health * .40):
        health_response = f"❤️💔💔💔💔"
    if health >= 0 and health <= (max_health * .20):
        health_response = f"💔💔💔💔💔"
    if resolved:
        if stamina >= max_stamina:
            stamina_response = f"⚡⚡⚡⚡⚡"
        if stamina >= (max_stamina * .80) and stamina < max_stamina:
            stamina_response = f"⚡⚡⚡⚡💫"
        if stamina >= (max_stamina * .60) and stamina < (max_stamina * .80):
            stamina_response = f"⚡⚡⚡💫💫"
        if stamina >= (max_stamina * .40) and stamina < (max_stamina * .60):
            stamina_response = f"⚡⚡💫💫💫"
        if stamina >= (max_stamina * .10) and stamina < (max_stamina * .40):
            stamina_response = f"⚡💫💫💫💫"
        if stamina >= 0 and stamina <= (max_stamina * .10):
            stamina_response = f"💫💫💫💫💫"
    else:
        if stamina >= max_stamina:
            stamina_response = f"🌀🌀🌀🌀🌀"
        if stamina >= (max_stamina * .80) and stamina < max_stamina:
            stamina_response = f"🌀🌀🌀🌀⚫"
        if stamina >= (max_stamina * .60) and stamina < (max_stamina * .80):
            stamina_response = f"🌀🌀🌀⚫⚫"
        if stamina >= (max_stamina * .40) and stamina < (max_stamina * .60):
            stamina_response = f"🌀🌀⚫⚫⚫"
        if stamina >= (max_stamina * .10) and stamina < (max_stamina * .40):
            stamina_response = f"🌀⚫⚫⚫⚫"
        if stamina >= 0 and stamina <= (max_stamina * .10):
            stamina_response = f"⚫⚫⚫⚫⚫"

    return {"HEALTH": health_response, "STAMINA": stamina_response}


enhancer_mapping = {'ATK': 'Increase Attack %',
'DEF': 'Increase Defense %',
'STAM': 'Increase Stamina',
'HLT': 'Heal yourself or companion',
'LIFE': 'Steal Health from Opponent',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase AP',
'BRACE': 'Lose Attack, Increase AP',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose 10% Max Health, Increase Attack, Defense and AP Buffs',
'STANCE': 'Swap your Attack & Defense, Increase Defense',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your  Stamina, Increase Target Stamina',
'SLOW': 'Increase Opponent Stamina, Decrease Your Stamina then Swap Stamina with Opponent',
'HASTE': 'Increase your Stamina, Decrease Opponent Stamina then Swap Stamina with Opponent',
'FEAR': 'Lose 10% Max Health, Decrease Opponent Attack, Defense and AP Buffs',
'SOULCHAIN': 'You and Your Opponent Stamina Link',
'GAMBLE': 'You and Your Opponent Health Link',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage, Increases over time based on card tier',
'DESTRUCTION': 'Decreases Your Opponent Max Health, Increases over time based on card tier',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}


title_enhancer_mapping = {'ATK': 'Increase Attack',
'DEF': 'Increase Defense',
'STAM': 'Increase Stamina',
'HLT': 'Heal for AP',
'LIFE': 'Steal AP Health',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase AP',
'BRACE': 'Lose Attack, Increase AP',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose 5% Max Health, Increase Attack, Defense and AP',
'STANCE': 'Swap your Attack & Defense, Increase Defense',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your Stamina, Increase Target Stamina',
'SLOW': 'Decrease Turn Count by 1',
'HASTE': 'Increase Turn Count By 1',
'FEAR': 'Lose 5% MAx Health, Decrease Opponent Attack, Defense and AP',
'SOULCHAIN': 'Both players stamina regen equals AP',
'GAMBLE': 'Focusing players health regen equals to AP',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage on your turn based on card tier',
'DESTRUCTION': 'Decreases Your Opponent Max Health, Increases over time based on card tier',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}


element_mapping = {
'PHYSICAL': 'If ST(stamina) greater than 80, Deals Bonus Damage. After 3 Strike gain a Parry',
'FIRE': 'Does 50% damage of previous attack over the next opponent turns, stacks.',
'ICE': 'Every 2 attacks, opponent freezes and loses 1 turn.',
'WATER': 'Increases all water move AP by 100 Flat.',
'EARTH': 'Cannot be Parried. Increases Def by 25% AP. Grants Shield - Increase by 50% DMG',
'ELECTRIC': 'Add 35% DMG Dealt to Shock damage, added to all Move AP.',
'WIND': 'On Miss, Use Wind Attack, boosts all wind damage by 35% of damage dealt.',
'PSYCHIC': 'Penetrates Barriers. Reduce opponent ATK & DEF by 35% DMG. After 3 Hits Gain a Barrier',
'DEATH': 'Deals 45% DMG to opponent max health. Gain Attack equal to that amount.',
'LIFE': 'Create Max Health and Heal for 35% DMG.',
'LIGHT': 'Regain 50% ST(Stamina) Cost, Illumination Increases ATK by 50% of DMG.',
'DARK': 'Penetrates Shields, Barriers and Parries & decreases opponent ST(Stamina) by 15.',
'POISON': 'Penetrates shields, Poison 30 damage stacking up to (150 * Card Tier).',
'RANGED': 'If ST(stamina) greater than 30, Deals 1.7x Damage. Every 4 Ranged Attacks Increase Hit Chance by 5%',
'ENERGY': 'Has higher 35% higher chance of Crit.',
'RECKLESS': 'Deals Incredible Bonus Damage, take 60% as reckless. If Reckless would kill you reduce HP to 1',
'TIME': 'Block and Increase Turn Count by 3, If ST(Stamina) is < 50, Focus for 1 Turn.',
'BLEED': 'Every 2 Attacks deal 10x turn count damage to opponent.',
'GRAVITY': 'Disables Opponent Block, Reduce opponent DEF by 50% DMG, Decrease Turn Count By 3.'
}


passive_enhancer_suffix_mapping = {'ATK': ' %',
'DEF': ' %',
'STAM': '',
'HLT': ' %',
'LIFE': '%',
'DRAIN': '',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': '',
'STANCE': '',
'CONFUSE': '',
'BLINK': '',
'SLOW': '',
'HASTE': '',
'FEAR': '',
'SOULCHAIN': '',
'GAMBLE': '',
'WAVE': '',
'CREATION': '%',
'BLAST': '',
'DESTRUCTION': '%',
'BASIC': '',
'SPECIAL': '',
'ULTIMATE': '',
'ULTIMAX': '',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}


enhancer_suffix_mapping = {'ATK': '%',
'DEF': '%',
'STAM': '',
'HLT': '%',
'LIFE': '%',
'DRAIN': '',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': '',
'STANCE': '',
'CONFUSE': '',
'BLINK': '',
'SLOW': '',
'HASTE': '',
'FEAR': '',
'SOULCHAIN': '',
'GAMBLE': '',
'WAVE': '',
'CREATION': '',
'BLAST': '',
'DESTRUCTION': '',
'BASIC': '',
'SPECIAL': '',
'ULTIMATE': '',
'ULTIMAX': '',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}


title_enhancer_suffix_mapping = {'ATK': '',
'DEF': '',
'STAM': '',
'HLT': ' %',
'LIFE': '%',
'DRAIN': '',
'FLOG': '%',
'WITHER': '%',
'RAGE': '%',
'BRACE': '%',
'BZRK': '%',
'CRYSTAL': '%',
'GROWTH': '',
'STANCE': '',
'CONFUSE': '',
'BLINK': '',
'SLOW': ' Turn',
'HASTE': ' Turn',
'FEAR': '',
'SOULCHAIN': '',
'GAMBLE': '',
'WAVE': '',
'CREATION': '%',
'BLAST': '',
'DESTRUCTION': '%',
'BASIC': '',
'SPECIAL': '',
'ULTIMATE': '',
'ULTIMAX': '',
'MANA': ' %',
'SHIELD': ' DMG 🌐',
'BARRIER': ' Blocks 💠',
'PARRY': ' Counters 🔄',
'SIPHON': ' Healing 💉'
}


abyss_floor_reward_list = [10,20,30,40,50,60,70,80,90,100]


crown_rift_universe_mappings = {'Crown Rift Awakening': 3, 'Crown Rift Slayers': 2, 'Crown Rift Madness': 5}
Healer_Enhancer_Check = ['HLT', 'LIFE']
DPS_Enhancer_Check = ['FLOG', 'WITHER']
INC_Enhancer_Check = ['ATK', 'DEF']
TRADE_Enhancer_Check = ['RAGE', 'BRACE']
Gamble_Enhancer_Check = ['GAMBLE', 'SOULCHAIN']
SWITCH_Enhancer_Check = ['STANCE', 'CONFUSE']
Time_Enhancer_Check = ['HASTE', 'SLOW','BLINK']
Support_Enhancer_Check = ['DEF', 'ATK', 'WITHER', 'FLOG']
Sacrifice_Enhancer_Check = ['BZRK', 'CRYSTAL']
FORT_Enhancer_Check = ['GROWTH', 'FEAR']
Stamina_Enhancer_Check = ['STAM', 'DRAIN']
Control_Enhancer_Check = ['SOULCHAIN']
Damage_Enhancer_Check = ['DESTRUCTION', 'BLAST']
Turn_Enhancer_Check = ['WAVE', 'CREATION']
take_chances_messages = ['You lost immediately.', 'You got smoked!', 'You fainted before the fight even started.',
                         'That... was just sad. You got dropped with ease.', 'Too bad, so sad. You took the L.',
                         'Annnd another L. You lost.', 'Annnnnnnnnnnd another L! You lost.',
                         'How many Ls you gonna take today?', 'That was worse than the last time. You got dropped.']

pokemon_universes= ['Kanto Region', 'Johnto Region', 'Hoenn Region', 'Sinnoh Region', 'Kalos Region', 'Galar Region', 'Alola Region', 'Unova Region']
