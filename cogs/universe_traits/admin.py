import custom_logging
import os
import datetime
from cogs.classes.custom_paginator import CustomPaginator
from ai import suggested_title_scenario
import db
import time
import classes as data
import translation_manager as tm
from language_cache import LanguageCache
from choicemanager import ChoicesManager
import messages as m
import help_commands as h
import aiohttp
from bson.int64 import Int64
import textwrap
import logging
from logger import loggy
from decouple import config
import textwrap
import random
import unique_traits as ut
now = time.asctime()
import asyncio
from characters import character_list
import requests
import json
import uuid
from interactions.ext.paginators import Paginator
from interactions import Task, IntervalTrigger, Client, ActionRow, Button, ButtonStyle, Intents, const, Status, Activity, listen, slash_command, global_autocomplete, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, AutocompleteContext, slash_option, Extension
import crown_utilities


emojis = ['👍', '👎']

class Admin(Extension):
    def __init__(self, bot):
        self.bot = bot


    @listen()
    async def on_ready(self):
        # print('Lookup Cog is ready!')
        loggy.info('Admin Cog is ready')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Create Code for Droppables", options=[
    SlashCommandOption(name="code_input", description="Code to create", type=OptionType.STRING, required=True),
    SlashCommandOption(name="coin", description="Coin amount", type=OptionType.INTEGER, required=False),
    SlashCommandOption(name="gems", description="Gem amount", type=OptionType.INTEGER, required=False),
    SlashCommandOption(name="card", description="Card to give", type=OptionType.STRING, required=False),
    SlashCommandOption(name="arm", description="Arm to give", type=OptionType.STRING, required=False),
    SlashCommandOption(name="summon", description="Summon to give", type=OptionType.STRING, required=False),
    SlashCommandOption(name="exp_to_give", description="Exp to give", type=OptionType.INTEGER, required=False),

    ], scopes=crown_utilities.guild_ids)
    @slash_default_member_permission(Permissions.ADMINISTRATOR)
    async def createcode(ctx, code_input, coin=None, gems=None, card=None, exp_to_give=0):
        is_creator = db.queryUser({'DID': str(ctx.author.id)})['CREATOR']
        if not is_creator:
            await ctx.send("Creator only command.", ephemeral=True)
            return
            
        code_exist = db.queryCodes({'CODE_INPUT': code_input})
        if card:
            card_exist = db.queryCard({'NAME': card})
            if not card_exist:
                await ctx.send("Card does not exist")
                return
        if code_exist:
            await ctx.send("Code already exist")
            return
        else:
            try:
                query = {
                    'CODE_INPUT': code_input,
                    'COIN': coin,
                    'GEMS': gems,
                    'AVAILABLE': True, 
                    'CARD': card,
                    'EXP': exp_to_give
                }
                response = db.createCode(data.newCode(query))
                await ctx.send(f"**{code_input}** Code has been created")
                loggy.info(f"Code {code_input} has been created by {ctx.author}")
            except Exception as e:
                loggy.error(f"Error in Create Code command: {e}")
                await ctx.send("There's an issue with your Code. Seek support in the Anime 🆚+ support server", ephemeral=True)
                return


    @slash_command(description="admin only", options=[
    SlashCommandOption(name="collection", description="Collection to update", type=OptionType.STRING, required=True),
    SlashCommandOption(name="new_field", description="New Field to add", type=OptionType.STRING, required=True),
    SlashCommandOption(name="field_type", description="Field Type", type=OptionType.STRING, required=True),
    ], scopes=crown_utilities.guild_ids)
    @slash_default_member_permission(Permissions.ADMINISTRATOR)
    async def addfield(ctx, collection, new_field, field_type):
        if ctx.author.id not in [306429381948211210, 263564778914578432]:
            await ctx.send("🛑 You know damn well this command isn't for you.")
            return
        
        if field_type == "fix":
            field_type = True
        elif field_type == 'string':
            field_type = "en"
        elif field_type == 'int':
            field_type = 0
        elif field_type == 'list':
            field_type = [
                {"ELEMENT": "PHYSICAL", "ESSENCE": 5000},
                {"ELEMENT": "FIRE", "ESSENCE": 5000},
                {"ELEMENT": "ICE", "ESSENCE": 5000},
                {"ELEMENT": "WATER", "ESSENCE": 5000},
                {"ELEMENT": "EARTH", "ESSENCE": 5000},
                {"ELEMENT": "ELECTRIC", "ESSENCE": 5000},
                {"ELEMENT": "WIND", "ESSENCE": 5000},
                {"ELEMENT": "PSYCHIC", "ESSENCE": 5000},
                {"ELEMENT": "DEATH", "ESSENCE": 5000},
                {"ELEMENT": "LIFE", "ESSENCE": 5000},
                {"ELEMENT": "LIGHT", "ESSENCE": 5000},
                {"ELEMENT": "DARK", "ESSENCE": 5000},
                {"ELEMENT": "POISON", "ESSENCE": 5000},
                {"ELEMENT": "RANGED", "ESSENCE": 5000},
                {"ELEMENT": "ENERGY", "ESSENCE": 5000},
                {"ELEMENT": "RECKLESS", "ESSENCE": 5000},
                {"ELEMENT": "TIME", "ESSENCE": 5000},
                {"ELEMENT": "BLEED", "ESSENCE": 5000},
                {"ELEMENT": "GRAVITY", "ESSENCE": 5000}
            ]
        elif field_type == 'deck':
            new_field = "DECK.$[].TALISMAN"
            field_type = "NULL"
        elif field_type == 'blank_list':
            field_type = []
        elif field_type == 'bool':
            field_type = False

        elif field_type == 'dict':
            field_type = {}
            
        if collection == 'fix':
            response = db.updateManyUsers({'$set': {'BOSS_FOUGHT': True}})
        elif collection == 'cards':
            response = db.updateManyCards({'$set': {new_field: field_type}})
        elif collection == 'scenarios':
            response = db.updateManyScenarios({'$set': {new_field: field_type}})
        elif collection == 'titles':
            response = db.updateManyTitles({'$set': {new_field: field_type}})
        elif collection == 'vault':
            response = db.updateManyVaults({'$set': {new_field: field_type}})
        elif collection == 'users':
            response = db.updateManyUsers({'$set': {new_field: field_type}})
        elif collection == 'universe':
            response = db.updateManyUniverses({'$set': {new_field: field_type}})
        elif collection == 'boss':
            response = db.updateManyBosses({'$set': {new_field: field_type}})
        elif collection == 'arms':
            response = db.updateManyArms({'$set': {new_field: field_type}})
        elif collection == 'pets':
            response = db.updateManySummons({'$set': {new_field: field_type}})
        elif collection == 'teams':
            response = db.updateManyTeams({'$set': {new_field: field_type}})
        elif collection == 'house':
            response = db.updateManyHouses({'$set': {new_field: field_type}})
        elif collection == 'hall':
            response = db.updateManyHalls({'$set': {new_field: field_type}})
        elif collection == 'family':
            response = db.updateManyFamily({'$set': {new_field: field_type}})
        elif collection == 'guild':
            response = db.updateManyGuild({'$set': {new_field: field_type}})
        
        await ctx.send("Update completed.")



    @slash_command(description="admin only", scopes=crown_utilities.guild_ids)
    @slash_default_member_permission(Permissions.ADMINISTRATOR)
    async def combinegems(ctx):
        if ctx.author.id not in [306429381948211210, 263564778914578432]:
            await ctx.send("🛑 You know damn well this command isn't for you.")
            return
        
        all_user_informations = db.queryAllUsers()
        for user_data in all_user_informations:
            user = crown_utilities.create_player_from_data(user_data)
            user.combine_duplicate_universes()
        
        
        await ctx.send("combined uni gems that are dupes")
        

    @slash_command(description="admin only", scopes=crown_utilities.guild_ids)
    @slash_default_member_permission(Permissions.ADMINISTRATOR)
    async def fixspaces(ctx):
        await ctx.defer()
        if ctx.author.id not in [306429381948211210, 263564778914578432]:
            await ctx.send("🛑 You know damn well this command isn't for you.")
            return

        all_arm_names = db.queryAllArms()
        all_card_names = db.queryAllCards()
        all_title_names = db.queryAllTitles()
        all_pet_names = db.queryAllSummons()
        count = 0
            
        def update_names(items, key, update_function):
            nonlocal count
            for item in items:
                original_name = item[key]
                new_name = original_name.strip()  # Remove leading and trailing spaces
                
                if new_name != original_name:  # Only update if there's a change
                    update_function(original_name, {"$set": {key: new_name}})
                    count += 1
                    # print(f"Updated {key}: '{original_name}' -> '{new_name}'")

        # Update ARM names
        update_names(all_arm_names, 'ARM', db.updateArm)

        # Update CARD names
        update_names(all_card_names, 'NAME', db.updateCard)

        # Update TITLE names
        update_names(all_title_names, 'TITLE', db.updateTitle)

        # Update PET names
        update_names(all_pet_names, 'PET', db.updateSummon)

        print(f"Updated {count} total names")

        await ctx.send(f"Fixed {count} names.")

    @slash_command(name="createscenarios", description="create scenarios", scopes=crown_utilities.guild_ids)
    @slash_option(name="mode", description="Mode to create scenarios for", opt_type=OptionType.STRING, choices=[
    SlashCommandChoice(name="Scenario", value="normal"),
    SlashCommandChoice(name="Raid", value="raid")
    ], required=True)
    @slash_option(name="scenario_universe", description="Universe to create scenarios for", opt_type=OptionType.STRING, required=True, autocomplete=True)
    @slash_default_member_permission(Permissions.ADMINISTRATOR)
    async def createscenarios(ctx: InteractionContext, mode, scenario_universe: str=""):
        loggy.info("createscenarios command")

        if ctx.author.id not in [306429381948211210, 263564778914578432]:
            await ctx.send("🛑 You know damn well this command isn't for you.")
            return
        
        await ctx.defer()
        try:
            universes = db.queryAllUniversesForScenario({'TITLE': scenario_universe})

            async def process_universe(universe, mode):
                cards = db.queryAllCardsBasedOnUniverse({"UNIVERSE": universe['TITLE']})
                valid_cards = [card for card in cards if 1 <= card['TIER'] <= 10]
                used_cards = set()
                
                low_end = 25
                high_end = 30

                if mode == "raid":
                    low_end = 4
                    high_end = 8

                async def create_scenario(mode):
                    nonlocal used_cards
                    available_cards = [card for card in valid_cards if card['NAME'] not in used_cards]

                    if not available_cards:
                        loggy.warning(f"No more available cards for universe {universe['TITLE']}")
                        return
                    
                    enemy_count = min(random.randint(1, 4), len(available_cards))
                    selected_cards = random.sample(available_cards, enemy_count)
                    used_cards.update(card['NAME'] for card in selected_cards)

                    if mode == "raid":
                        level = random.randint(1500, 5000)
                    else:
                        level = random.randint(1, 500)

                    if level < 500:
                        tier_range = range(1, 8)
                    else:
                        tier_range = range(5, 11)

                    selected_cards = [card for card in selected_cards if card['TIER'] in tier_range]
                    
                    if len(selected_cards) == 1:
                        title = f"Defeat {selected_cards[0]['NAME']} in battle!"
                    else:
                        title = await suggested_title_scenario(universe['TITLE'], [card['NAME'] for card in selected_cards])
                        if not title:
                                ran_number_for_secret_files = random.randint(10, 5000)
                                title = f"Secret Files # {str(ran_number_for_secret_files)}"
                        await asyncio.sleep(1)
                    existing_scenario = db.queryScenario({"TITLE": title})
                    if existing_scenario:
                        loggy.info(f"Scenario with title '{title}' already exists. Skipping.")
                        return


                    scenario = {
                        "TITLE": title,
                        "UNIVERSE": universe['TITLE'],
                        "ENEMIES": [card['NAME'] for card in selected_cards],
                        "NORMAL_DROPS": [],
                        "EASY_DROPS": [],
                        "HARD_DROPS": [],
                        "IS_DESTINY": False,
                        "TACTICS": [],
                        "LOCATIONS": [],
                        "IS_RAID": mode == "raid",
                        "MUST_COMPLETE": False,
                        "IMAGE": universe['PATH'],
                        "DESTINY_CARDS": [],
                        "AVAILABLE": True,
                        "ENEMY_LEVEL": level
                    }
                    loggy.info(f"Creating scenario: {title}")
                    db.insertScenario(scenario)

                await asyncio.gather(*(create_scenario(mode) for _ in range(random.randint(low_end, high_end))))

            await asyncio.gather(*(process_universe(universe, mode) for universe in universes))
            await ctx.send("Scenarios created.")
        
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
            loggy.error(f"Error in createscenarios command: {ex}")
            await ctx.send("Issue with command.")
            return


    @createscenarios.autocomplete("scenario_universe")
    async def createscenarios_autocomplete(ctx: AutocompleteContext):
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


    # this command will take in a universe parameter
    @slash_command(description="update characters with descriptions", scopes=crown_utilities.guild_ids)
    async def updatecharacters(ctx):
        await ctx.defer()
        if ctx.author.id not in [306429381948211210, 263564778914578432]:
            await ctx.send("🛑 You know damn well this command isn't for you.")
            return
        
        # get all cards from universe
        count = 0
        for card in character_list:
            name = card["name"]
            descriptions = card["descriptions"]
            encounter_options = card["options"]
            # update card with descriptions
            db.updateCard({"NAME": name}, {"$set": {"DESCRIPTIONS": descriptions}})
            count += 1
            if count % 10 == 0:
                await asyncio.sleep(2)

        await ctx.send(f"Updated {count} characters with descriptions.")
        return

