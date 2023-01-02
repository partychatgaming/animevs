# from operator import is_
# from urllib import response
import db
import time
import classes as data
import bot as main
import messages as m
from discord.ext import commands
import numpy as np
import help_commands as h
import destiny as d
# Converters
from discord import User
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from PIL import Image, ImageFont, ImageDraw
from discord_slash.model import ButtonStyle
import textwrap
from discord_slash import cog_ext, SlashContext
from dinteractions_Paginator import Paginator
from discord_slash.utils.manage_commands import create_option, create_choice
from io import BytesIO
import io
import os
import typing
from pilmoji import Pilmoji
import logging
import textwrap
import unique_traits as ut
import discord
now = time.asctime()
import random
import requests


print("Crown Utilities initiated")

def storage_limit_hit(player_info, vault):
    storage_amount = len(vault['STORAGE'])
    storage_allowed_amount = player_info['STORAGE_TYPE'] * 15
    limit_hit = False

    if storage_amount >= storage_allowed_amount:
        limit_hit = True
    return limit_hit


async def store_drop_card(player, card_name, card_universe, vault, owned_destinies, bless_amount_if_max_cards, bless_amount_if_card_owned, mode, is_shop, price):
    try:
        user = await main.bot.fetch_user(player)
        player_info = db.queryUser({"DID": str(player)})
        storage_limit_has_been_hit = storage_limit_hit(player_info, vault)

        current_storage = vault['STORAGE']
        current_cards_in_vault = vault['CARDS']

        vault_query = {'DID': str(player)}
        hand_length = len(current_cards_in_vault)


        list1 = current_cards_in_vault
        list2 = current_storage
        list2.extend(list1)
        current_cards = list2

        card_owned = False
        for owned_card in current_cards:
            if owned_card == card_name:
                card_owned = True

        if card_owned:
            if is_shop:
                await cardlevel(card_name, player, mode, card_universe)
                await curse(int(price), str(player))
                return f"You earned experience points for 🎴: **{card_name}**"
            await cardlevel(card_name, player, mode, card_universe)
            await bless(int(bless_amount_if_card_owned), player)
            return f"You earned experience points for 🎴: **{card_name}** & :coin: **{'{:,}'.format(bless_amount_if_card_owned)}**"
        else:
            if hand_length < 25:
                response = db.updateVaultNoFilter(vault_query,{'$addToSet': {'CARDS': str(card_name)}})
                if is_shop:
                    await curse(int(price), str(player))

                # Add Card Level config
                if not card_owned:
                    update_query = {'$addToSet': {
                        'CARD_LEVELS': {'CARD': str(card_name), 'LVL': 0, 'TIER': 0,
                                        'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                    r = db.updateVaultNoFilter(vault_query, update_query)

                # Add Destiny
                for destiny in d.destiny:
                    if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                        db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
                        await user.send(
                            f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.")

                return f"You earned 🎴: **{card_name}**!"

            
            if hand_length >= 25 and not storage_limit_has_been_hit:
                if is_shop:
                    response = await route_to_storage(player, card_name, current_cards, card_owned, price, card_universe, owned_destinies, "Purchase")
                    return response
                else:
                    update_query = {'$addToSet': {
                        'CARD_LEVELS': {'CARD': card_name, 'LVL': 0, 'TIER': 0, 'EXP': 0, 'HLT': 0,
                                        'ATK': 0, 'DEF': 0, 'AP': 0}}}
                    response = db.updateVaultNoFilter(vault_query, {'$addToSet': {'STORAGE': card_name}})
                    r = db.updateVaultNoFilter(vault_query, update_query)
                    message = ""
                    for destiny in d.destiny:
                        if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                            db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
                            await user.send(
                                f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.")

                    return f"**{card_name}** has been added to your storage 💼!\n{message}"


            if hand_length >= 25 and storage_limit_has_been_hit:
                if is_shop:
                    return "You have max amount of Cards. Transaction cancelled."   
                else:
                    await bless(int(bless_amount_if_max_cards), player)
                    return f"You're maxed out on Cards! You earned :coin: {str(bless_amount_if_max_cards)} instead!"

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
        # guild = main.bot.get_guild(543442011156643871)
        # channel = guild.get_channel(957061470192033812)
        # await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")


async def route_to_storage(player, card_name, current_cards, card_owned, price, universe, owned_destinies, mode):
    try:
        user = await main.bot.fetch_user(player)
        msg = ""

        user_query = {"DID": str(player)}
        vault_query = {"DID": str(player)}
        update_query = {
            "$addToSet": {"STORAGE": card_name}
        }
        update_storage = db.updateVaultNoFilter(user_query, update_query)
        

        if card_owned:
            await cardlevel(card_name, str(player), mode, universe)
            msg = f"You received a level up for **{card_name}**!"
            await curse(int(price), str(player))
            return msg
        else:
            await curse(int(price), str(player))

            update_query = {'$addToSet': {
                'CARD_LEVELS': {'CARD': str(card_name), 'LVL': 0, 'TIER': 0,
                                'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
            r = db.updateVaultNoFilter(vault_query, update_query)

            msg = f"**{card_name}** has been purchased and added to Storage!\n"

            for destiny in d.destiny:
                if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                    db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
                    await user.send(
                        f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.")


            msg = f"**{card_name}** has been purchased and added to Storage!"
            return msg

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
        # guild = main.bot.get_guild(543442011156643871)
        # channel = guild.get_channel(957061470192033812)
        # await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")


def set_emoji(element):
    emoji = ""
    if element == "PHYSICAL":
        emoji = "👊"
    if element == "FIRE":
        emoji = "🔥"
    if element == "ICE":
        emoji = "❄️"
    if element == "WATER":
        emoji = "💧"
    if element == "EARTH":
        emoji = "⛰️"
    if element == "ELECTRIC":
        emoji = "🌩️"
    if element == "WIND":
        emoji = "🌪️"
    if element == "PSYCHIC":
        emoji = "🔮"
    if element == "RANGED":
        emoji = "🏹"
    if element == "POISON":
        emoji = "🧪"
    if element == "DEATH":
        emoji = "☠️"
    if element == "LIFE":
        emoji = "❤️‍🔥"
    if element == "LIGHT":
        emoji = "🌕"
    if element == "DARK":
        emoji = "🌑"
    if element == "SPIRIT":
        emoji = "🧿"
    if element == "BLEED":
        emoji = "🅱️"
    if element == "RECOIL":
        emoji = "♻️"
    if element == "TIME":
        emoji = "⌛"
    if element == "GRAVITY":
        emoji = "🪐"
        

    return emoji

        
        

    
    

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
        return

def check_affinities(player, card, basic_element, super_element, ultimate_element):
    # card = card you want to check
    weaknesses = card['WEAKNESS']
    resistances = card['RESISTANT']
    repels = card['REPEL']
    absorbs = card['ABSORB']
    immunity = card['IMMUNE']

    is_weak = False
    is_resistant = False
    does_repel = False
    does_absorb = False
    is_immune = False

    affinities = {
        "PLAYER": player,
        "BASIC": "",
        "SUPER": "",
        "ULTIMATE": ""
    }
    


    if basic_element in weaknesses:
        affinities['BASIC'] = "WEAKNESS"
    if basic_element in resistances:
        affinities['BASIC'] = "RESISTANT"
    if basic_element in repels:
        affinities['BASIC'] = "REPELS"
    if basic_element in absorbs:
        affinities['BASIC'] = "ABSORBS"
    if basic_element in immunity:
        affinities['BASIC'] = "IMMUNE"

    if super_element in weaknesses:
        affinities['SUPER'] = "WEAKNESS"
    if super_element in resistances:
        affinities['SUPER'] = "RESISTANT"
    if super_element in repels:
        affinities['SUPER'] = "REPELS"
    if super_element in absorbs:
        affinities['SUPER'] = "ABSORBS"
    if super_element in immunity:
        affinities['SUPER'] = "IMMUNE"

    if ultimate_element in weaknesses:
        affinities['ULTIMATE'] = "WEAKNESS"
    if ultimate_element in resistances:
        affinities['ULTIMATE'] = "RESISTANT"
    if ultimate_element in repels:
        affinities['ULTIMATE'] = "REPELS"
    if ultimate_element in absorbs:
        affinities['ULTIMATE'] = "ABSORBS"
    if ultimate_element in immunity:
        affinities['ULTIMATE'] = "IMMUNE"

    

    return affinities


def set_affinities(card):
    try:
        weaknesses = card['WEAKNESS']
        resistances = card['RESISTANT']
        repels = card['REPEL']
        absorbs = card['ABSORB']
        immunity = card['IMMUNE']

        weakness_list = []
        resistance_list = []
        repels_list = []
        absorb_list = []
        immune_list = []

        message_list = []

        weakness_msg = ""
        resistances_msg = ""
        repels_msg = ""
        absorb_msg = ""
        immune_msg = ""

        message_to = ""

        for weakness in weaknesses:
            if weakness:
                emoji = set_emoji(weakness)
                weakness_list.append(emoji)

        for resistance in resistances:
            if resistance:
                emoji = set_emoji(resistance)
                resistance_list.append(emoji)

        for repel in repels:
            if repel:
                emoji = set_emoji(repel)
                repels_list.append(emoji)

        for absorb in absorbs:
            if absorb:
                emoji = set_emoji(absorb)
                absorb_list.append(emoji)

        for immune in immunity:
            if immune:
                emoji = set_emoji(immune)
                immune_list.append(emoji)

        if weakness_list:
            weakness_msg = " ".join(weakness_list)
            message_list.append(f"**Weaknesses:** {weakness_msg}")
        
        if resistance_list:
            resistances_msg = " ".join(resistance_list)
            message_list.append(f"**Resistances:** {resistances_msg}")
        
        if repels_list:
            repels_msg = " ".join(repels_list)
            message_list.append(f"**Repels:** {repels_msg}")

        if absorb_list:
            absorb_msg = " ".join(absorb_list)
            message_list.append(f"**Absorbs:** {absorb_msg}")

        if immune_list:
            immune_msg = " ".join(immune_list)
            message_list.append(f"**Immune:** {immune_msg}")

        if message_list:
            message_to = "\n".join(message_list)
        
        if  not message_list:
            message_to = "No Affinities"

        affinity_message = textwrap.dedent(f"""\
        {message_to}
        """)

        return affinity_message
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


async def corrupted_universe_handler(ctx, universe, difficulty):
    try:
        # if universe['CORRUPTION_LEVEL'] == 499:
        # updated_corruption_level = db.updateUniverse({'TITLE': universe['TITLE']}, {'$inc': {'CORRUPTION_LEVEL': 1}})
        query = {"DID": str(ctx.author.id)}
        vault = db.queryVault(query)
        
        gem_list = vault['GEMS']
        gem_reward = 150000
        if difficulty == "HARD":
            gem_reward = 500000

        if gem_list:
            for uni in gem_list:
                if uni['UNIVERSE'] == universe:
                    update_query = {
                        '$inc': {'GEMS.$[type].' + "GEMS": gem_reward}
                    }
                    filter_query = [{'type.' + "UNIVERSE": uni['UNIVERSE']}]
                    res = db.updateVault(query, update_query, filter_query)
                    return f"You earned 💎 **{'{:,}'.format(gem_reward)}**"
        else:
            return "You must dismantle a card from this universe to enable crafting."

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

    

async def cardlevel(card: str, player, mode: str, universe: str):
    try:
        vault = db.queryVault({'DID': str(player)})
        player_info = db.queryUser({'DID': str(player)})
        guild_buff = await guild_buff_update_function(player_info['TEAM'].lower())
        if player_info['DIFFICULTY'] == "EASY":
            return


        card_uni = db.queryCard({'NAME': card})['UNIVERSE']
        user = await main.bot.fetch_user(str(player))

        cardinfo = {}
        for x in vault['CARD_LEVELS']:
            if x['CARD'] == str(card):
                cardinfo = x
        
        has_universe_heart = False
        has_universe_soul = False

        if universe != "n/a":
            for gems in vault['GEMS']:
                if gems['UNIVERSE'] == card_uni and gems['UNIVERSE_HEART']:
                    has_universe_heart = True
                if gems['UNIVERSE'] == card_uni and gems['UNIVERSE_SOUL']:
                    has_universe_soul = True

        lvl = cardinfo['LVL']
        new_lvl = lvl + 1
        lvl_req = 150
        exp = cardinfo['EXP']
        exp_gain = 0
        if has_universe_soul:
            if mode == "Dungeon":
                exp_gain = 65
            if mode == "Tales":
                exp_gain = 35
            if mode == "Purchase":
                exp_gain = 150
        else:
            if mode == "Dungeon":
                exp_gain = 30
            if mode == "Tales":
                exp_gain = 15
            if mode == "Purchase":
                exp_gain = 150


        hlt_buff = 0
        atk_def_buff = 0
        ap_buff = 0

        if lvl < 200:
            if guild_buff:
                if guild_buff['Level']:
                    exp_gain = 150
                    update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])

            # Experience Code
            if exp < (lvl_req - 1):
                query = {'DID': str(player)}
                update_query = {'$inc': {'CARD_LEVELS.$[type].' + "EXP": exp_gain}}
                filter_query = [{'type.' + "CARD": str(card)}]
                response = db.updateVault(query, update_query, filter_query)

            # Level Up Code
            if exp >= (lvl_req - exp_gain):
                if (lvl + 1) % 2 == 0:
                    atk_def_buff = level_sync["ATK_DEF"]
                if (lvl + 1) % 3 == 0:
                    ap_buff = level_sync["AP"]
                if (lvl + 1) % 20 == 0:
                    hlt_buff = level_sync["HLT"]
                query = {'DID': str(player)}
                update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0},
                                '$inc': {'CARD_LEVELS.$[type].' + "LVL": 1, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff,
                                        'CARD_LEVELS.$[type].' + "DEF": atk_def_buff,
                                        'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                filter_query = [{'type.' + "CARD": str(card)}]
                response = db.updateVault(query, update_query, filter_query)
                await user.send(f"**{card}** leveled up!")

        if lvl < 500 and lvl >= 200 and has_universe_heart:
            if guild_buff:
                if guild_buff['Level']:
                    exp_gain = 150
                    update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])

            # Experience Code
            if exp < (lvl_req - 1):
                query = {'DID': str(player)}
                update_query = {'$inc': {'CARD_LEVELS.$[type].' + "EXP": exp_gain}}
                filter_query = [{'type.' + "CARD": str(card)}]
                response = db.updateVault(query, update_query, filter_query)

            # Level Up Code
            if exp >= (lvl_req - exp_gain):
                if (lvl + 1) % 2 == 0:
                    atk_def_buff = 1
                if (lvl + 1) % 3 == 0:
                    ap_buff = 1
                if (lvl + 1) % 20 == 0:
                    hlt_buff = 25
                query = {'DID': str(player)}
                update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0},
                                '$inc': {'CARD_LEVELS.$[type].' + "LVL": 1, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff,
                                        'CARD_LEVELS.$[type].' + "DEF": atk_def_buff,
                                        'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                filter_query = [{'type.' + "CARD": str(card)}]
                response = db.updateVault(query, update_query, filter_query)
                await user.send(f"**{card}** leveled up to level **{new_lvl}**!")
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
        # guild = main.bot.get_guild(543442011156643871)
        # channel = guild.get_channel(957061470192033812)
        # await channel.send(f"'PLAYER': **{str(player)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")


async def guild_buff_update_function(team):
    try:
        team_query = {'TEAM_NAME': team.lower()}
        team_info = db.queryTeam(team_query)
        if team_info:
            guild_buff_count = len(team_info['GUILD_BUFFS'])
            guild_buff_active = team_info['GUILD_BUFF_ON']
            guild_buffs = team_info['GUILD_BUFFS']


            if guild_buff_active:
                filter_query = [{'type.' + "TYPE": guild_buff_active}]
                guild_buff_update_query = {}
                quest_buff = False
                rift_buff = False
                level_buff = False
                stat_buff = False
                auto_battle_buff = False
                index = 0

                active_guild_buff = team_info['ACTIVE_GUILD_BUFF']
                for buff in guild_buffs:
                    if buff['TYPE'] == active_guild_buff:
                        index = guild_buffs.index(buff)

                        if buff['TYPE'] == "Rift":
                            rift_buff = True
                        
                        if buff['TYPE'] == "Quest":
                            quest_buff = True

                        if buff['TYPE'] == "Level":
                            level_buff = True

                        if buff['TYPE'] == "Stat":
                            stat_buff = True

                        if buff['TYPE'] == "Auto Battle":
                            auto_battle_buff = True


                        if buff['USES'] == 1:
                            
                            if guild_buff_count == 1:
                                guild_buff_update_query = {
                                        '$pull': {
                                            'GUILD_BUFFS': {'TYPE': active_guild_buff, 'USES': 1}
                                        },
                                        '$set': {
                                            'GUILD_BUFF_ON': False,
                                            'GUILD_BUFF_AVAILABLE': False,
                                            'ACTIVE_GUILD_BUFF': "",
                                        },
                                        '$push': {
                                            'TRANSACTIONS': f"{active_guild_buff} Buff has been used up"
                                        }
                                    }

                            else:
                                guild_buff_update_query = {
                                        "$pull": {
                                            'GUILD_BUFFS': {'TYPE': active_guild_buff, 'USES': 1}
                                        },
                                        '$set': {
                                            'GUILD_BUFF_ON': False,
                                            'ACTIVE_GUILD_BUFF': "",
                                        },
                                        '$push': {
                                            'TRANSACTIONS': f"{active_guild_buff} Buff has been used up"
                                        }
                                    }
                        
                        else:
                            guild_buff_update_query = {
                                '$inc': {
                                    f"GUILD_BUFFS.{index}.USES": -1
                                }

                            }
                
                response = {
                    'Quest': quest_buff,
                    'Rift': rift_buff,
                    'Level': level_buff,
                    'Stat': stat_buff,
                    'Auto Battle': auto_battle_buff,
                    'QUERY': team_query,
                    'UPDATE_QUERY': guild_buff_update_query,
                    'FILTER_QUERY': filter_query
                    }
                
                return response
            else:
                return False                     
        else:
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
            'team': str(team),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        # guild = main.bot.get_guild(543442011156643871)
        # channel = guild.get_channel(957061470192033812)
        # await channel.send(f"'TEAM': **{str(team)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")


async def bless(amount, user):
    try:
        blessAmount = amount
        posBlessAmount = 0 + abs(int(blessAmount))
        query = {'DID': str(user)}
        vaultOwner = db.queryUser(query)
        if vaultOwner:
            vault = db.queryVault({'DID' : vaultOwner['DID']})
            update_query = {"$inc": {'BALANCE': posBlessAmount}}
            db.updateVaultNoFilter(vault, update_query)
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


async def blessteam(amount, team):
    try:
        blessAmount = amount
        posBlessAmount = 0 + abs(int(blessAmount))
        query = {'TEAM_NAME': str(team)}
        team_data = db.queryTeam(query)
        if team_data:
            update_query = {"$inc": {'BANK': posBlessAmount}}
            db.updateTeam(query, update_query)
        else:
            print("Cannot find Guild")
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


async def curseteam(amount, team):
    try:
        curseAmount = amount
        negCurseAmount = 0 - abs(int(curseAmount))
        query = {'TEAM_NAME': str(team)}
        team_data = db.queryTeam(query)
        if team_data:
            update_query = {"$inc": {'BANK': int(negCurseAmount)}}
            db.updateTeam(query, update_query)
        else:
            print("cant find team")
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


async def blessfamily(amount, family):
    try:
        blessAmount = amount
        posBlessAmount = 0 + abs(int(blessAmount))
        query = {'HEAD': str(family)}
        family_data = db.queryFamily(query)
        if family_data:
            house = family_data['HOUSE']
            house_data = db.queryHouse({'HOUSE': house})
            multiplier = house_data['MULT']
            posBlessAmount = posBlessAmount * multiplier
            update_query = {"$inc": {'BANK': posBlessAmount}}
            db.updateFamily(query, update_query)
        else:
            print("Cannot find family")
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


async def blessfamily_Alt(amount, family):
    try:
        blessAmount = amount
        posBlessAmount = 0 + abs(int(blessAmount))
        query = {'HEAD': str(family)}
        family_data = db.queryFamily(query)
        if family_data:
            house = family_data['HOUSE']
            house_data = db.queryHouse({'HOUSE': house})
            posBlessAmount = posBlessAmount
            update_query = {"$inc": {'BANK': posBlessAmount}}
            db.updateFamily(query, update_query)
        else:
            print("Cannot find family")
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


async def cursefamily(amount, family):
    try:
        curseAmount = amount
        negCurseAmount = 0 - abs(int(curseAmount))
        query = {'HEAD': str(family)}
        family_data = db.queryFamily(query)
        if family_data:
            update_query = {"$inc": {'BANK': int(negCurseAmount)}}
            db.updateFamily(query, update_query)
        else:
            print("cant find family")
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


async def blessguild(amount, guild):
    try:
        blessAmount = amount
        posBlessAmount = 0 + abs(int(blessAmount))
        query = {'GNAME': str(guild)}
        guild_data = db.queryGuildAlt(query)
        if guild_data:
            hall = guild_data['HALL']
            hall_data = db.queryHall({'HALL': hall})
            multiplier = hall_data['MULT']
            posBlessAmount = posBlessAmount * multiplier
            query = {'GNAME': str(guild_data['GNAME'])}
            update_query = {"$inc": {'BANK': int(posBlessAmount)}}
            db.updateGuildAlt(query, update_query)
        else:
            print("Cannot find guild")
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


async def curseguild(amount, guild):
    try:
        curseAmount = amount
        negCurseAmount = 0 - abs(int(curseAmount))
        query = {'GNAME': str(guild)}
        guild_data = db.queryGuildAlt(query)
        if guild_data:
            query = {'GNAME':str(guild_data['GNAME'])}
            update_query = {"$inc": {'BANK': int(negCurseAmount)}}
            db.updateGuildAlt(query, update_query)
        else:
            print("cant find guild")
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


async def curse(amount, user):
    try:
        curseAmount = int(amount)
        negCurseAmount = 0 - abs(int(curseAmount))
        query = {'DID': str(user)}
        vaultOwner = db.queryUser(query)
        if vaultOwner:
            vault = db.queryVault({'DID' : vaultOwner['DID']})
            update_query = {"$inc": {'BALANCE': int(negCurseAmount)}}
            db.updateVaultNoFilter(vault, update_query)
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


async def player_check(ctx):
    query = {'DID': str(ctx.author.id)}
    valid = db.queryUser(query)
    if valid:
        return True
    else:
        await ctx.send(f"{ctx.author.mention}, you must register using /register to play Anime VS+.")
        return False


def scenario_gold_drop(scenario_lvl):
    gold = scenario_lvl * 2000
    if scenario_lvl > 900:
        gold = gold + 100000000
    elif scenario_lvl > 500:
        gold = gold + 1000000
    
    return gold



def inc_essence(did, element, essence):
    try:
        emoji = set_emoji(element)
        query = {'DID': str(did)}
        update_query = {'$inc': {'ESSENCE.$[type].' + "ESSENCE": essence}}
        filter_query = [{'type.' + "ELEMENT": element}]
        response = db.updateVault(query, update_query, filter_query)
        return emoji
    except Exception as e:
        return False

def does_exist(data):
    if data:
        return True
    else:
        return False

def is_maxed_out(list):
    if len(list) >= 25:
        return True
    else:
        return False


def inc_talisman(did, element):
    try:
        emoji = set_emoji(element)
        query = {'DID': str(did)}
        vault = db.queryVault(query)
        current_durability = 0
        for t in vault["TALISMANS"]:
            if t["TYPE"] == element.upper():
                current_durability = t["DUR"]

        if current_durability <= 1:
            response = dismantle_talisman(element, did)
            return response
        else:
            update_query = {'$inc': {'TALISMANS.$[type].' + "DUR": -1}}
            filter_query = [{'type.' + "TYPE": element.upper()}]
            r = db.updateVault(query, update_query, filter_query)
            response = f"{emoji} {element.title()} Talisman now has {current_durability - 1} durability."
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


def does_exist(data):
    if data:
        return True
    else:
        return False

def is_maxed_out(list):
    if len(list) >= 25:
        return True
    else:
        return False


def dismantle_talisman(element, did):
    try:
        query = {'DID': str(did)}
        update_query = {'$pull': {'TALISMANS': {'TYPE': str(element.upper())}}}
        resp = db.updateVaultNoFilter(query, update_query)
        user_update_query = {'$set': {'TALISMAN': 'NULL'}}
        db.updateUserNoFilter(query, user_update_query)
        response = inc_essence(did, element, 150)
        msg = f"{response} **{element.title()} Talisman** has been dismantled into **150 {response} {element.title()} Essence**"
        return msg
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


def essence_cost(vault, element, did):
    try:
        essence_list = vault["ESSENCE"]
        talisman_list = vault["TALISMANS"]
        talisman_exists = False
        msg = ""
        for e in essence_list:
            if e["ELEMENT"] == element:
                essence = e["ESSENCE"]

        for t in talisman_list:
            if t["TYPE"] == element.upper():
                talisman_exists = True

        
        if talisman_exists:
            msg = f"You already have a **{element} Talisman**."
            return msg       

        if essence < 1500:
            msg = f"You do not have enough {element} essence to transfuse at this time."
            return msg


        curseAmount = int(1500)
        negCurseAmount = 0 - abs(int(curseAmount))
        query = {'DID': str(did)}
        update_query = {'$inc': {'ESSENCE.$[type].' + "ESSENCE": negCurseAmount}}
        filter_query = [{'type.' + "ELEMENT": element}]
        response = db.updateVault(query, update_query, filter_query)
        talisman_query = {
                '$addToSet': {
                    "TALISMANS": {
                        "TYPE": element.upper(),
                        "DUR": 30
                    }
                }
            }
        tresponse = db.updateVaultNoFilter(query, talisman_query)
        msg = f"You have successfully attuned a **{element.title()} Talisman!**"
        return msg
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


def level_sync_stats(lvl, stat):
    stat_sync = 0

    if stat == "HLT":
        stat_sync = round(lvl * level_sync["HLT"])
        return stat_sync
    if stat == "ATK_DEF":
        stat_sync = round(lvl * 2)
        return stat_sync
    if stat == "AP":
        stat_sync = round((lvl / 3) * 1)
        return stat_sync

def select_random_element(difficulty, mode):
    dungeon_modes = ["DUNGEON", "CDUNGEON"]
    essence = 100
    if difficulty == "EASY":
        essence = 10
    if difficulty == "HARD":
        essence = 500
    if mode in dungeon_modes:
        essense = essence + 500

    element = random.choice(elements)
    return {"ELEMENT": element, "ESSENCE": essence}


level_sync = {
    "HLT": 10,
    "ATK_DEF": 2,
    "AP": 2
}

elements = [
    "PHYSICAL",
    "FIRE",
    "ICE",
    "WATER",
    "EARTH",
    "ELECTRIC",
    "WIND",
    "PSYCHIC",
    "DEATH",
    "LIFE",
    "LIGHT",
    "DARK",
    "POISON",
    "RANGED",
    "SPIRIT",
    "RECOIL",
    "TIME",
    "BLEED",
    "GRAVITY"
]

crest_dict = {'Unbound': ':ideograph_advantage:',
              'My Hero Academia': ':sparkle:',
              'League Of Legends': ':u6307:',
              'Kanto Region': ':chart:',
              'Naruto': ':u7121:',
              'Bleach': ':u6709:',
              'God Of War': ':u7533:',
              'Chainsawman': ':accept:',
              'One Punch Man': ':u55b6:',
              'Johto Region': ':u6708:',
              'Black Clover': ':ophiuchus:',
              'Demon Slayer': ':aries:',
              'Attack On Titan': ':taurus:',
              '7ds': ':capricorn:',
              'Hoenn Region': ':leo:',
              'Digimon': ':cancer:',
              'Fate': ':u6e80:',
              'Solo Leveling': ':u5408:',
              'Souls': ':sos:',
              'Dragon Ball Z': ':u5272:',
              'Sinnoh Region': ':u7981:',
              'Death Note': ':white_flower:',
              'Crown Rift Awakening': ':u7a7a:',
              'Crown Rift Slayers': ':sa:',
              'Crown Rift Madness': ':m:',
              'Persona': ':o:',
              'YuYu Hakusho': ':wheel_of_dharma:',
              'One Piece': ':sailboat:'
              }