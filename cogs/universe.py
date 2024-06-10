import textwrap
import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import unique_traits as ut
import help_commands as h
import uuid
import asyncio
import random
import custom_logging
from logger import loggy
from .classes.custom_paginator import CustomPaginator
from .classes.arm_class import Arm
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.player_class import Player
from .classes.battle_class import Battle
from .classes.summon_class import Summon
from cogs.battle_config import BattleConfig as bc
from cogs.game_state import GameState as gs
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Universe(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        loggy.info('Universe Cog is ready!')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    """
    Creates a list of all available tales/dungeons for the player to select from.
    This is only for non preselected universes in the command
    """
    async def universe_selector_paginator(self, ctx, mode, player):
        try:
            completed_message = f"**Completed**: {crown_utilities.utility_emojis['OFF']}"
            save_spot_text = "No Save Data"
            count = 0
            fight_emoji = "⚔️"
            list_of_opponents = "CROWN_TALES"
            save_spot_check = crown_utilities.TALE_M
            mode_check = "HAS_CROWN_TALES"
            completed_check = player.completed_tales
            all_universes = ""
            universe_paginator_type = "Universe Tales"
            
            # if mode in crown_utilities.DUNGEON_M and player.level <= 40:
            #     dungeon_unavailable_response = create_dungeon_locked_embed()
            #     await ctx.send(embed=dungeon_unavailable_response)
            #     return

            prestige_slider, prestige_message = calculate_prestige(player.prestige, player.rebirth)

            if mode in crown_utilities.DUNGEON_M:
                fight_emoji = "🔥"
                list_of_opponents = "DUNGEONS"
                save_spot_check = crown_utilities.DUNGEON_M
                mode_check = "HAS_DUNGEON"
                completed_check = player.completed_dungeons
                universe_paginator_type = "Universe Dungeon"

            def get_dungeons(universes):
                all_universes = []
                for universe in universes:
                    if universe['TITLE'] in player.completed_tales:
                        all_universes.append(universe)
                if not all_universes:
                    return None
                else:
                    return all_universes
                
            def get_tales(universes):
                all_universes = []
                for universe in universes:
                    all_universes.append(universe)
                if not all_universes:
                    return None
                else:
                    return all_universes
                    
            def get_rifts(universes):
                rift_universes = []
                for universe in universes:
                    if universe['TIER'] == 9:
                        rift_universes.append(universe)
                return rift_universes
                
            if player.rift_on:
                if mode in crown_utilities.DUNGEON_M:
                    _all_universes = await asyncio.to_thread(db.queryDungeonAllUniverse)
                    all_universes = get_dungeons(_all_universes)
                    if not all_universes:
                        return None
                if mode in crown_utilities.TALE_M:
                    _all_universes = await asyncio.to_thread(db.queryAllUniverse)
                    all_universes = get_tales(_all_universes)
                rift_universes = get_rifts(all_universes)
                num_rift_universes = len(rift_universes)
                if len(rift_universes) > 1:
                    num_rift_universes = random.randint(1, min(len(rift_universes), 3))
                selected_universes = random.sample(rift_universes, num_rift_universes)

                max_non_rift_universes = 25 - num_rift_universes
                non_rift_universes = [universe for universe in all_universes if universe['TIER'] != 9]
                selected_universes.extend(random.sample(non_rift_universes, min(len(non_rift_universes), max_non_rift_universes)))
                
                corruption_message = "🔮 *Crown Rifts*"

            if not player.rift_on:
                if mode in crown_utilities.DUNGEON_M:
                    _all_universes = await asyncio.to_thread(db.queryDungeonUniversesNotRift)
                    all_universes = get_dungeons(_all_universes)
                    if not all_universes:
                        return None
                if mode in crown_utilities.TALE_M:
                    _all_universes = await asyncio.to_thread(db.queryTaleUniversesNotRift)
                    all_universes = get_tales(_all_universes)
                selected_universes = random.sample(all_universes, min(len(all_universes), 25))
                    

            universe_embed_list = []
            can_fight_message = ""
            for universe in selected_universes:
                if count < 25:
                    can_fight_message = f"🔥 Dungeon | {universe['TITLE']} : /universes to view all Dungeon Drops."
                    universe_crest_owner_message = f"{crown_utilities.crest_dict[universe['TITLE']]} *Crest Unclaimed*"
                    if universe[mode_check] == True:
                        if universe['TITLE'] in completed_check:
                            completed_message = f"**Completed**: {crown_utilities.utility_emojis['ON']}"
                            can_fight_message = f"🔥 Dungeon | Conquer {universe['TITLE']} Dungeon again for a Boss Key and Minor Reward."

                        if player.difficulty != "EASY":
                            for save in player.save_spot:
                                if save['UNIVERSE'] == universe['TITLE'] and save['MODE'] in save_spot_check:
                                    save_spot_text = str((int(save['CURRENTOPPONENT']) + 1))

                        if universe['GUILD'] != "PCG":
                            universe_crest_owner_message = f"{crown_utilities.crest_dict[universe['TITLE']]} **Crest Owned**: {universe['GUILD']}"
                            
                        universe_embed_list.append(create_universe_embed(universe, ctx, mode, save_spot_text, completed_message, universe_crest_owner_message, fight_emoji, list_of_opponents, prestige_message, player))
                        count += 1   
                else:
                    break
            # paginator = CustomPaginator.create_from_embeds(self.bot, *universe_embed_list, custom_buttons=["Start", "Co-op Start", "Duo Start", "Delete Save", "Quit"], paginator_type=universe_paginator_type)
            paginator = CustomPaginator.create_from_embeds(self.bot, *universe_embed_list, custom_buttons=["Start", "Delete Save", "Quit"], paginator_type=universe_paginator_type)
            paginator.show_select_menu = True
            await paginator.send(ctx)
        except Exception as ex:
            print(ex)
            player.make_available()
            custom_logging.debug(ex)


    """
    Creates the embed for the selected universe
    This is only for universes that are preselected in the command
    """
    async def universe_selector(self, ctx, mode, universe_title, player):
        try:
            _uuid = uuid.uuid4()
            completed_message = f"**Completed**: {crown_utilities.utility_emojis['OFF']}"
            save_spot_text = "No Save Data"
            fight_emoji = "⚔️"
            list_of_opponents = "CROWN_TALES"
            can_fight_message = ""
            save_spot_check = crown_utilities.TALE_M
            currentopponent = 0
            entrance_fee = 5000
            mode_check = "HAS_CROWN_TALES"
            completed_check = player.completed_tales
            if not universe_title[0].isdigit():
                universe_title = universe_title
            universe = await asyncio.to_thread(db.queryUniverse, {"TITLE": {"$regex": f"^{str(universe_title)}$", "$options": "i"}})
            if not universe:
                embed = Embed(title= f"{universe_title} does not exist.", description="You may have misspelled the universe name. Please try again.")
                await ctx.send(embed=embed)
                player.make_available()
                return
            # if mode in crown_utilities.DUNGEON_M and player.level <= 40:
            #     dungeon_unavailable_response = create_dungeon_locked_embed()
            #     await ctx.send(embed=dungeon_unavailable_response)
            #     return
            
            buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="Start Battle",
                    custom_id = f"{_uuid}|start"
                ),
                # Button(
                #     style=ButtonStyle.BLUE,
                #     label="Start Co-op Tales",
                #     custom_id = f"{_uuid}|coop"
                # ),
                # Button(
                #     style=ButtonStyle.BLUE,
                #     label="Start Duo Tales",
                #     custom_id = f"{_uuid}|duo"
                # ),
                Button(
                    style=ButtonStyle.GRAY,
                    label="Quit",
                    custom_id = f"{_uuid}|quit"
                ),
            ]

            
            prestige_slider, prestige_message = calculate_prestige(player.prestige, player.rebirth)
            
            if mode in crown_utilities.DUNGEON_M:
                entrance_fee = 20000
                fight_emoji = "🔥"
                list_of_opponents = "DUNGEONS"
                save_spot_check = crown_utilities.DUNGEON_M
                mode_check = "HAS_DUNGEON"
                completed_check = player.completed_dungeons
                # If this universe's tales has not been completed
                # if universe_title not in player.completed_tales:
                #     embed = Embed(title= f"{crown_utilities.crest_dict[universe['TITLE']]} Dungeon Locked.", description="You must complete the Tales for this Universe before you can enter the Dungeon.")
                #     await ctx.send(embed=embed)
                #     player.make_available()
                #     return
                if universe_title in player.completed_dungeons:
                    completed_message = f"**Completed**: {crown_utilities.utility_emojis['ON']}"
                    can_fight_message = f"🔥 Dungeon | Conquer {universe['TITLE']} Dungeon again for a Boss Key and Minor Reward."

            if universe[mode_check] == True:
                if player.difficulty != "EASY":
                    for save in player.save_spot:
                        if save['UNIVERSE'] == universe['TITLE'] and save['MODE'] in save_spot_check:
                            currentopponent = save['CURRENTOPPONENT']
                            save_spot_text = str((int(save['CURRENTOPPONENT']) + 1))
                            buttons.append(
                                Button(
                                    style=ButtonStyle.RED,
                                    label="Delete Save",
                                    custom_id = f"{_uuid}|deletesave"
                                )
                            )

                if universe['GUILD'] != "PCG":
                    universe_crest_owner_message = f"{crown_utilities.crest_dict[universe['TITLE']]} **Crest Owned**: {universe['GUILD']}"
                else: 
                    universe_crest_owner_message = f"{crown_utilities.crest_dict[universe['TITLE']]} *Crest Unclaimed*"

                embedVar = create_universe_embed(universe, ctx, mode, save_spot_text, completed_message, universe_crest_owner_message, fight_emoji, list_of_opponents, prestige_message, player)
                msg = await ctx.send(embed=embedVar, components=buttons)

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author
                        
                try:
                    button_ctx = await self.bot.wait_for_component(components=[buttons], timeout=30,check=check)
                    await button_ctx.ctx.defer(edit_origin=True)
                    if button_ctx.ctx.custom_id == f"{_uuid}|start":
                        await msg.edit(components=[])
                        await bc.create_universe_battle(self, ctx, mode, universe, player, currentopponent, entrance_fee)
                        return

                    if button_ctx.ctx.custom_id == f"{_uuid}|coop":
                        await button_ctx.ctx.send("Starting")
                        await msg.edit(components=[])

                    if button_ctx.ctx.custom_id == f"{_uuid}|duo":
                        await button_ctx.ctx.send("Starting")
                        await msg.edit(components=[])

                    if button_ctx.ctx.custom_id == f"{_uuid}|deletesave":
                        player.make_available()
                        # await button_ctx.ctx.send("Deleting Save")
                        embed = Embed(title= f"{universe['TITLE']} Save Deleted.", description="You have deleted your save data for this Universe.")
                        await gs.delete_save_spot(self, player, universe['TITLE'], mode, 0)
                        await msg.edit(embeds=[embed],components=[])
                    
                    if button_ctx.ctx.custom_id == f"{_uuid}|quit":
                        player.make_available()
                        embed = Embed(title= f"{universe['TITLE']} Match Making Cancelled.", description="You have cancelled the match making process.")
                        await button_ctx.ctx.send(embed=embed)
                        await msg.edit(components=[])
                        return
                
                except asyncio.TimeoutError:
                    loggy.critical("Timeout Error")
                    await msg.edit(components=[])
                    return
            else:
                embed = Embed(title= f"{universe_title} does not exist.", description="You may have misspelled the universe name. Please try again.")
                await ctx.send(embed=embed)
                player.make_available()
                return
        except Exception as ex:
            player.make_available()
            custom_logging.debug(ex)
            loggy.error(ex)
            embed = Embed(title= f"{universe['TITLE']} Match Making Cancelled.", description="You have cancelled the match making process.")
            await ctx.send(embed=embed)


def create_universe_embed(universe, ctx, mode, save_spot_text, completed_message, universe_crest_owner_message, fight_emoji, list_of_opponents, p_message, player):
    embedVar = Embed(title= f"{universe['TITLE']}", description=textwrap.dedent(f"""
        {crown_utilities.crest_dict[universe['TITLE']]} **Number of Fights**: {fight_emoji} **{len(universe[list_of_opponents])}**

        **Saved Game**: ⚔️ *{save_spot_text}*
        **Difficulty**: ⚙️ {player.difficulty.lower().capitalize()} {p_message}
        {completed_message}
        {universe_crest_owner_message}
        """))
    embedVar.set_image(url=universe['PATH'])
    embedVar.set_thumbnail(url=ctx.author.avatar_url)
    if mode not in crown_utilities.DUNGEON_M:
        if player.rift_on:
            if universe['TIER'] == 9:
                embedVar.set_footer(text=f"🔮 Rift | Traverse {universe['TITLE']} : /universes to view all Rift Drops.")
            else:
                embedVar.set_footer(text=f"⚔️ Tales | Traverse {universe['TITLE']} : /universes to view all Tales Drops.")
        else:
            embedVar.set_footer(text=f"⚔️ Tales | Traverse {universe['TITLE']} : /universes to view all Tales Drops.")
    # else:
    #     embedVar.set_author(name="test")
        # embedVar.set_footer(text=f"{can_fight_message}")
    
    return embedVar


def create_dungeon_locked_embed():
    return Embed(
        title=f"🔒 Dungeons are locked until level 40.",
        description=textwrap.dedent(f"""
            \n__How to unlock Dungeons?__
            \nYou unlock Bosses by completing floor 40 of :new_moon: The Abyss. Once a Tale has been completed, the Dungeon for that universe will be unlocked for you to fight!
            \nDungeons offer rarer item drops and Summons.
            \nAssociated players can earn Universe Crest by completing Dungeons, granting their Association additional Gold.
        """)
    )


def calculate_prestige(prestige, rebirth):
    if prestige > 0:
        prestige_slider = ((((prestige + 1) * (10 + rebirth)) / 100))
        p_percent = (prestige_slider * 100)
        prestige_message = f"*{crown_utilities.prestige_icon(prestige)} x{round(p_percent)}%*"
        return prestige_slider, prestige_message
    return 0, ''



def setup(bot):
    Universe(bot)
              