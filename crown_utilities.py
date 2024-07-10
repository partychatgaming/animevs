import db
# import bot as main
from functools import wraps
from cachetools import cached, LRUCache
from cogs.classes.card_class import Card
from cogs.classes.arm_class import Arm
from cogs.classes.title_class import Title
from cogs.classes.player_class import Player
from cogs.classes.summon_class import Summon
import time
from logger import loggy
import destiny as d
import classes as data
from PIL import Image, ImageFont, ImageDraw
import textwrap
from io import BytesIO
from pilmoji import Pilmoji
import textwrap
from decouple import config
now = time.asctime()
import re
import random
import asyncio
import requests
import interactions 
import custom_logging
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

print("Crown Utilities initiated")


# Create separate caches
cache_universes = LRUCache(maxsize=100)
cache_cards = LRUCache(maxsize=100)

guild_ids = None
guild_id = None
guild_channel = None

if config('ENV') == "production":
   guild_id = 543442011156643871
   guild_channel = 957061470192033812
else:
   guild_ids = [839352855000776735]
   guild_id = 839352855000776735
   guild_channel = 962580388432195595

# Decorator to use a specific cache
def cached_with_key(cache, key):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            cache_key = key
            if cache_key not in cache:
                cache[cache_key] = func(*args, **kwargs)
            return cache[cache_key]
        return wrapped
    return decorator


@cached_with_key(cache_universes, 'universes_cache')
def get_cached_universes():
    try:
        response = db.queryAllUniverses()
        list_of_universes = []
        for universe in response:
            list_of_universes.append({"name": universe["TITLE"], "value": universe["TITLE"]})
        my_data = sorted(list_of_universes, key=lambda x: x['name'])
        return my_data
    except Exception as e:
        print(e)
        return False

@cached_with_key(cache_cards, 'cards_cache')
def get_cached_cards():
    try:
        response = db.getCardsFromAvailableUniverses()
        list_of_cards = []
        for card in response:
            list_of_cards.append({"name": card["NAME"], "value": card["NAME"]})
        for item in autocomplete_advanced_search:
            list_of_cards.append(item)
        my_data = sorted(list_of_cards, key=lambda x: x['name'])
        return my_data
    except Exception as e:
        print(e)
        return False


def storage_limit_hit(player_info, vault, type):
    if type == "cards":
        storage_amount = len(vault['STORAGE'])
        storage_allowed_amount = player_info['STORAGE_TYPE'] * 15
        limit_hit = False

        if storage_amount >= storage_allowed_amount:
            limit_hit = True
    elif type == "titles":
        storage_amount = len(vault['TSTORAGE'])
        storage_allowed_amount = player_info['STORAGE_TYPE'] * 15
        limit_hit = False

        if storage_amount >= storage_allowed_amount:
            limit_hit = True
    elif type == "arms":
        storage_amount = len(vault['ASTORAGE'])
        storage_allowed_amount = player_info['STORAGE_TYPE'] * 15
        limit_hit = False

        if storage_amount >= storage_allowed_amount:
            limit_hit = True
    return limit_hit


def replace_matching_numbers_with_arrow(text_list):
    # Dictionary to keep track of first occurrence of each number
    first_occurrence = set()

    # Updated list to store the modified text
    updated_list = []

    for text in text_list:
        match = re.match(r'\((\d+)\)', text)
        if match:
            number = match.group(1)
            if number in first_occurrence:
                # Replace the number with :plus1: if it's a duplicate
                text = re.sub(r'\(\d+\)', '↘️', text, count=1)
            else:
                # Mark the number as seen for the first time
                first_occurrence.add(number)
        updated_list.append(text)
    return updated_list


def update_save_spot(ctx, saved_spots, selected_universe, modes):
    try:
        currentopponent = 0
        if saved_spots:
            for save in saved_spots:
                if save['UNIVERSE'] == selected_universe and save['MODE'] in modes:
                    currentopponent = save['CURRENTOPPONENT']
                    query = {'DID': str(ctx.author.id)}
                    update_query = {'$pull': {'SAVE_SPOT': {"UNIVERSE": selected_universe}}}
                    resp = db.updateUserNoFilter(query, update_query)
        return currentopponent
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
        return


def calculate_speed_modifier(speed):
    if speed <= 10:
        return 3
    elif speed <= 20:
        return 2
    elif speed <= 30:
        return 1
    elif speed >= 90:
        return -3
    elif speed >= 80:
        return -2
    elif speed >= 70:
        return -1
    else:
        return 0


async def summonlevel(player, player_card):    
    xp_inc = 1
    bxp_inc = 1
    protections = ['BARRIER', 'PARRY']
    if player.family != 'PCG':
        family_info = db.queryFamily({'HEAD':str(player.did)})
        familysummon = family_info['SUMMON']
        if familysummon['NAME'] == str(player.equipped_summon):
            xp_inc = 2
            bxp_inc = 5
            summon_object = familysummon
            summon_name = summon_object['NAME']
            summon_ability = ""
            summon_ability_power = 0
            for key in summon_object:
                if key not in ["NAME", "LVL", "EXP", "TYPE", "BOND", "BONDEXP", "PATH"]:
                    summon_ability_power = summon_object[key]
                    summon_ability = key
            summon_type = summon_object['TYPE']
            summon_lvl = summon_object['LVL']
            summon_exp = summon_object['EXP']
            summon_bond = summon_object['BOND']
            summon_bond_exp = summon_object['BONDEXP']
            bond_req = ((summon_ability_power * 5) * (summon_bond + 1))
            if bond_req <= 0:
                bond_req = 5
            lvl_req = (int(summon_lvl) * 25) * (1 + summon_bond)
            if lvl_req <= 0:
                lvl_req = 25
            
            power = ((1 + summon_bond) * summon_lvl) + int(summon_ability_power)
            if summon_type in protections:
                power = summon_bond + int(summon_ability_power)
                
            summon_path = summon_object['PATH']
            # lvl = familysummon['LVL']  # To Level Up -(lvl * 10 = xp required)
            # lvl_req = lvl * 10
            # exp = familysummon['EXP']
            # summon_name
            # petmove_text = list(familysummon.keys())[3]  # Name of the ability
            # petmove_ap = list(familysummon.values())[3]  # Ability Power
            # petmove_type = familysummon['TYPE']
            # bond = familysummon['BOND']
            # bondexp = familysummon['BONDEXP']
            # bond_req = ((petmove_ap * 5) * (bond + 1))
            summon_info = {'NAME': summon_name, 'LVL': summon_lvl, 'EXP': summon_exp, summon_ability: summon_ability_power, 'TYPE': summon_type, 'BOND': summon_bond, 'BONDEXP': summon_bond_exp, 'PATH': summon_path}
            query = {'HEAD':str(family_info['HEAD'])}
            
            if summon_lvl< 10:
                # Non Level Up Code
                if summon_exp < (lvl_req - 1):
                    #print("yay!")
                    summon_exp = summon_exp + xp_inc
                    summon_info = {'NAME': summon_name, 'LVL': summon_lvl, 'EXP': summon_exp, summon_ability: summon_ability_power, 'TYPE': summon_type, 'BOND': summon_bond, 'BONDEXP': summon_bond_exp, 'PATH': summon_path}
                    transaction_message = f"🧬 | {player.disname} trained {summon_name}."
                    update_query = {'$set': {'SUMMON': summon_info}, '$push': {'TRANSACTIONS': transaction_message}}
                    response = db.updateFamily(query, update_query)

                # Level Up Code
                if summon_exp >= (lvl_req - 1):
                    summon_exp = 0
                    summon_lvl = summon_lvl + 1
                    summon_info = {'NAME': summon_name, 'LVL': summon_lvl, 'EXP': summon_exp, summon_ability: summon_ability_power, 'TYPE': summon_type, 'BOND': summon_bond, 'BONDEXP': summon_bond_exp, 'PATH': summon_path}
                    transaction_message = f"🧬 | {player.disname} trained {summon_name} to Level **{summon_lvl}**."
                    update_query = {'$set': {'SUMMON': summon_info}, '$push': {'TRANSACTIONS': transaction_message}}
                    response = db.updateFamily(query, update_query)

            if summon_bond < 3:
                # Non Bond Level Up Code
                if summon_bond_exp < (bond_req - 1):
                    #print("bonding")
                    summon_bond_exp = summon_bond_exp + bxp_inc
                    
                    summon_info = {'NAME': summon_name, 'LVL': summon_lvl, 'EXP': summon_exp, summon_ability: summon_ability_power, 'TYPE': summon_type, 'BOND': summon_bond, 'BONDEXP': summon_bond_exp, 'PATH': summon_path}
                    transaction_message = f"🧬 | {player.disname} bonded with {summon_name}."
                    update_query = {'$set': {'SUMMON': summon_info}, '$push': {'TRANSACTIONS': transaction_message}}
                    response = db.updateFamily(query, update_query)

                # Bond Level Up Code
                if summon_bond_exp >= (bond_req - 1):
                    summon_bond_exp = 0
                    summon_bond = summon_bond + 1
                    summon_info = {'NAME': summon_name, 'LVL': summon_lvl, 'EXP': summon_exp, summon_ability: summon_ability_power, 'TYPE': summon_type, 'BOND': summon_bond, 'BONDEXP': summon_bond_exp, 'PATH': summon_path}
                    
                    transaction_message = f"🧬 | {player.disname} bonded with {summon_name} to Level **{summon_bond}**."
                    update_query = {'$set': {'SUMMON': summon_info}, '$push': {'TRANSACTIONS': transaction_message}}
                    response = db.updateFamily(query, update_query)
            #return False
    try:
        protections = ['BARRIER', 'PARRY']
        query = {'DID': str(player.did)}
        summon_type = player_card.summon_type
        lvl_req = ((player_card.summon_lvl * (1 + player_card.summon_bond)) * (player_card.summon_bond + 1)) +  round(.10 * player_card.base_summon_power)
        if lvl_req <= 0:
            lvl_req = 25
        bond_req = ((player_card.summon_power * (player_card.summon_bond + 1)))
        if summon_type in protections:
            bond_req = ((player_card.summon_power + player_card.summon_bond)) * (player_card.summon_bond + 1)
        if bond_req <= 0:
            bond_req = 100
        new_ap = player_card.summon_power  
        level_message = f"Level: {player_card.summon_lvl} | XP: {player_card.summon_exp}/{lvl_req}"
        bond_message = f"Bond: {player_card.summon_bond}"

        if player_card.summon_lvl <= 100:
            # Non Level Up Code
            if player_card.summon_exp < (lvl_req - 1):
                update_query = {'$inc': {'PETS.$[type].' + "EXP": xp_inc}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)
                level_message = f"Level: {player_card.summon_lvl} | XP: +🆙{player_card.summon_exp}/{lvl_req}"
                player_card.summon_exp = player_card.summon_exp + xp_inc

            # Level Up Code
            if player_card.summon_exp >= (lvl_req):
                update_query = {'$set': {'PETS.$[type].' + "EXP": 0}, '$inc': {'PETS.$[type].' + "LVL": 1}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)
                level_message = f"Level: +🆙{player_card.summon_lvl} | XP: {player_card.summon_exp}/{lvl_req}"
                new_ap = calculate_summon__ability_power(player_card.summon_power, player_card.summon_lvl, player_card.summon_bond)
        if player_card.summon_lvl % 10 == 0:
            if player_card.summon_bond < 10:
                # Non Bond Level Up Code
                # if player_card.summon_bondexp < (bond_req - 1):
                #     update_query = {'$inc': {'PETS.$[type].' + "BONDEXP": bxp_inc}}
                #     filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                #     response = db.updateUser(query, update_query, filter_query)
                # Bond Level Up Code
                # if player_card.summon_bondexp >= (bond_req - 1):
                update_query = {'$set': {'PETS.$[type].' + "BONDEXP": 0}, '$inc': {'PETS.$[type].' + "BOND": 1}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)
                bond_message = f"Bond: +🆙{player_card.summon_bond}"
                new_ap = calculate_summon__ability_power(player_card.summon_power, player_card.summon_lvl, player_card.summon_bond)
                
        

        if player_card.summon_bond >= 10:
            bond_message = "🌟"
        if player_card.summon_lvl  >= 100:
            level_message = "⭐"
        ap_message = f"{new_ap}"
        summon_level_message = f"{bond_message} | {level_message}\n{player_card.summon_name} | {player_card.summon_emoji}{ap_message}"
        return summon_level_message

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
    
def calculate_summon__ability_power(ability_power_potential, level, bond):
        ability_power = round(ability_power_potential * (1 + level / 18.25) * (1 + bond / 18.25))
        return ability_power


async def updateRetry(player_id, mode, math_calc):
    player_info = db.queryUser({'DID' : str(player_id)})
    if player_info:
        try:
            mode = mode
            math = math_calc
        
            if math == "INC":
                if player_info['RETRIES'] >=25:
                    return print('You already have 25 Retries...')
                if mode == "U":
                    update_query = {"DID": player_info['DID']}
                    new_value = {'$inc' : {"RETRIES": 1}}
                    update_player = db.updateUserNoFilter(update_query, new_value)
                    return update_player
                elif mode == "D":
                    update_query = {"DID": player_info['DID']}
                    new_value = {'$inc' : {"RETRIES": 3}}
                    update_player = db.updateUserNoFilter(update_query, new_value)
                    return update_player
                elif mode == "B":
                    update_query = {"DID": player_info['DID']}
                    new_value = {'$inc' : {"RETRIES": 5}}
                    update_player = db.updateUserNoFilter(update_query, new_value)
                    return update_player
                else:
                    print("Unable to find game mode")
                    return False
                    
            elif math == "DEC":
                
                if player_info['RETRIES'] >= 1:
                    update_query = {"DID": player_info['DID']}
                    new_value = {'$inc' : {"RETRIES": -1}}
                    update_player = db.updateUserNoFilter(update_query, new_value)
                    return update_player 
                else:
                    print("You have no retries avaialable")
            else:
                print("Could not find math_calc")
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
    else:
        print("Could not find player info")
        return False
    
def set_class_emoji(card_class):
    emoji = class_emojis[card_class]
    return emoji

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
    if element == "ENERGY" or element == "SPIRIT" or element == "SPIRIT ENERGY":
        emoji = "🧿"
    if element == "BLEED":
        emoji = "🅱️"
    if element == "RECKLESS" or element == "RECOIL":
        emoji = "♻️"
    if element == "TIME":
        emoji = "⌛"
    if element == "GRAVITY":
        emoji = "🪐"
    if element == "SHIELD":
        emoji = "🌐"
    if element == "PARRY":
        emoji = "🔄"
    if element == "BARRIER":
        emoji = "💠"
    if element == "SIPHON":
        emoji = "💉"
    if element == "GUN":
        emoji = "🔫"
    if element == "ROT":
        emoji = "🩻"
    if element == "NATURE":
        emoji = "🌿"
    if element == "SWORD":
        emoji = "⚔️"
    if element == "SLEEP":
        emoji = "💤"
    if element == "DRACONIC":
        emoji = "🐲"
    if element == "BASIC":
        emoji = "💥"
    if element == "SPECIAL":
        emoji = "☄️"
    if element == "ULTIMATE":
        emoji = "🏵️"
    if element == "ULTIMAX":
        emoji = "💮"
    if element == "MANA":
        emoji = "🪬"
    if element == "None" or element == "NULL" or element == "NONE":
        emoji = "📿"
    
        
    return emoji


def getTime(hgame, mgame, sgame, hnow, mnow, snow):
    # Calculate the differences between the current time and game time
    hoursPassed = hnow - hgame
    minutesPassed = mnow - mgame
    secondsPassed = snow - sgame

    # Adjust for negative values
    if secondsPassed < 0:
        secondsPassed += 60
        minutesPassed -= 1

    if minutesPassed < 0:
        minutesPassed += 60
        hoursPassed -= 1

    # Convert to strings and return the result concatenated
    gameTime = str(hoursPassed) + ":" + str(minutesPassed) + ":" + str(secondsPassed)
    #print(gameTime)
    return gameTime



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
        

        header = ImageFont.truetype("fonts/YesevaOne-Regular.ttf", name_font_size)
        s = ImageFont.truetype("fonts/Roboto-Bold.ttf", 22)
        h = ImageFont.truetype("fonts/YesevaOne-Regular.ttf", 37)
        m = ImageFont.truetype("fonts/Roboto-Bold.ttf", 25)
        r = ImageFont.truetype("fonts/Freedom-10eM.ttf", 40)
        lvl_font = ImageFont.truetype("fonts/Neuton-Bold.ttf", 68)
        health_and_stamina_font = ImageFont.truetype("fonts/Neuton-Light.ttf", 41)
        attack_and_shield_font = ImageFont.truetype("fonts/Neuton-Bold.ttf", 48)
        moveset_font = ImageFont.truetype("fonts/antonio.regular.ttf", 40)
        rhs = ImageFont.truetype("fonts/destructobeambb_bold.ttf", 35)
        stats = ImageFont.truetype("fonts/Freedom-10eM.ttf", 30)
        card_details_font_size = ImageFont.truetype("fonts/destructobeambb_bold.ttf", 25)
        card_levels = ImageFont.truetype("fonts/destructobeambb_bold.ttf", 40)

        draw.text((600, 160), summon, (255, 255, 255), font=header, stroke_width=1, stroke_fill=(0, 0, 0), align="left")

        # Level
        lvl_sizing = (89, 70)
        if int(lvl) > 9:
            lvl_sizing = (75, 70)

        draw.text(lvl_sizing, f"{lvl}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0), align="center")
        draw.text((1096, 65), f"{bond}", (255, 255, 255), font=lvl_font, stroke_width=1, stroke_fill=(0, 0, 0), align="center")

        lines = textwrap.wrap(message, width=28)
        y_text = 330
        pilmoji = Pilmoji(im)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=moveset_font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            x_position = round((1730 - width) / 2)
            pilmoji.text((x_position, y_text), line, (255, 255, 255), font=moveset_font, stroke_width=2, stroke_fill=(0, 0, 0))
            y_text += height


        image_binary = BytesIO()
        im.save(image_binary, "PNG")
        return image_binary

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
                    res = db.updateUser(query, update_query, filter_query)
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
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))

    
async def cardlevel(user, mode: str, extra_exp = 0):
    print(mode)
    try:
        # if mode == "RPG":
        #     player = create_player_from_data(db.queryUser({'DID': user.did}))
            
        # else:
        player = create_player_from_data(db.queryUser({'DID': str(user.id)}))
        card = create_card_from_data(db.queryCard({'NAME': player.equipped_card}))
        # guild_buff = await guild_buff_update_function(player.guild.lower())
        # arm = create_arm_from_data(db.queryArm({'ARM': player.equipped_arm}))
        # title = create_title_from_data(db.queryTitle({'TITLE': player.equipped_title}))
        card.set_card_level_buffs(player.card_levels)
        # has_universe_heart, has_universe_soul = get_level_boosters(player, card)
        exp_gain, lvl_req = get_exp_gain(player, mode, card, extra_exp)

        if player.difficulty == "EASY":
            return

        number_of_level_ups, card = await update_experience(card, player, exp_gain, lvl_req)
        # print(f"Number of Level Ups - {number_of_level_ups}")

        if number_of_level_ups > 0:
            loggy.info(f"Card Leveling - {user} - {number_of_level_ups} Level Ups")
            if player is None:
                player = create_player_from_data(db.queryUser({'DID': str(user.id)}))
            card = create_card_from_data(db.queryCard({'NAME': player.equipped_card}))
            card.set_card_level_buffs(player.card_levels)
            lvl_req = get_level_up_exp_req(card)
            embed = Embed(title=f"🎴 **{card.name}** leveled up {str(number_of_level_ups)} times!", color=0x00ff00)
            embed.set_footer(text=f"{lvl_req} EXP to next level")
            embed.set_image(url="attachment://image.png")
            image_binary = card.showcard()
            image_binary.seek(0)
            card_file = File(file_name="image.png", file=image_binary)
            await user.send(embed=embed, file=card_file)
            image_binary.close()
            return number_of_level_ups
        else:
            return None
    except Exception as ex:
        print(ex)
        custom_logging.debug(ex)
        await user.send("Issue with leveling up card")
        return


def get_buffs(card_lvl, level_sync):
    atk_def_buff = 1 if (card_lvl + 1) % 2 == 0 else 0
    ap_buff = 1 if (card_lvl + 1) % 3 == 0 else 0
    hlt_buff = 25 if (card_lvl + 1) % 20 == 0 else 0
    if card_lvl < 200:
        atk_def_buff = level_sync["ATK_DEF"] if atk_def_buff else 0
        ap_buff = level_sync["AP"] if ap_buff else 0
        hlt_buff = level_sync["HLT"] if hlt_buff else 0
    return atk_def_buff, ap_buff, hlt_buff


async def update_experience(card, player, exp, lvl_req):
    try:
        total_exp_gain = exp
        initial_level = card.card_lvl
        exp_for_next_level = lvl_req

        # Calculate new level and remaining exp
        while total_exp_gain >= exp_for_next_level and card.card_lvl < MAX_LEVEL:
            total_exp_gain -= exp_for_next_level
            card.card_lvl += 1
            exp_for_next_level = get_level_up_exp_req(card)

        # Update remaining exp
        remaining_exp = total_exp_gain

        # Calculate buffs for the new level
        atk_def_buff, ap_buff, hlt_buff = get_buffs(card.card_lvl, level_sync)

        # Prepare update query
        update_query = {
            '$set': {'CARD_LEVELS.$[type].EXP': remaining_exp},
            '$inc': {
                'CARD_LEVELS.$[type].LVL': card.card_lvl - initial_level,
                'CARD_LEVELS.$[type].ATK': atk_def_buff * (card.card_lvl - initial_level),
                'CARD_LEVELS.$[type].DEF': atk_def_buff * (card.card_lvl - initial_level),
                'CARD_LEVELS.$[type].AP': ap_buff * (card.card_lvl - initial_level),
                'CARD_LEVELS.$[type].HLT': hlt_buff * (card.card_lvl - initial_level)
            }
        }

        filter_query = [{'type.CARD': card.name}]
        response = await asyncio.to_thread(db.updateUser, player.user_query, update_query, filter_query)

        return card.card_lvl - initial_level, card
    except Exception as ex:
        custom_logging.debug(ex)
        return 0, card


def get_level_boosters(player, card):
    has_universe_heart = False
    has_universe_soul = False

    for gems in player.gems:
        if gems['UNIVERSE'] == card.universe and gems['UNIVERSE_HEART']:
            has_universe_heart = True
        if gems['UNIVERSE'] == card.universe and gems['UNIVERSE_SOUL']:
            has_universe_soul = True

    return has_universe_heart, has_universe_soul


def get_level_up_exp_req(card):
    x = 0.099
    y = 1.25
    lvl_req = round((float(card.card_lvl)/x)**y)
    return lvl_req


def get_exp_gain(player, mode, card, extra_exp):
    try:
        lvl_req = get_level_up_exp_req(card)
        exp_gain = 0
        t_exp_gain = 500 + (player.rebirth) + player.prestige_buff
        d_exp_gain = ((5000 + player.prestige_buff) * (1 + player.rebirth))
        b_exp_gain = 500000 + ((100 + player.prestige_buff) * (1 + player.rebirth))

        if mode in DUNGEON_M:
            exp_gain = d_exp_gain + extra_exp
        elif mode in TALE_M:
            exp_gain = t_exp_gain + extra_exp
        elif mode in BOSS_M:
            exp_gain = b_exp_gain + extra_exp
        elif mode == SCENARIO:
            exp_gain = extra_exp
        elif mode in RAID_M:
            exp_gain = extra_exp * 10
        else:
            exp_gain = extra_exp

        if mode == "Purchase":
            exp_gain = lvl_req + 100 + extra_exp
        if mode == "RPG":
            exp_gain = lvl_req + 100 + extra_exp

        return exp_gain, lvl_req
    except Exception as ex:
        custom_logging.debug(ex)
        return 0, 0


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
                rematch_buff = False
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

                        if buff['TYPE'] == "Rematch":
                            rematch_buff = True


                        if buff['USES'] == 1:
                            
                            if guild_buff_count <= 1:
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
                    'Rematch' : rematch_buff,
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


async def bless(amount, user_did):
    try:
        bless_total_amount = 0 + abs(int(amount))
        query = {'DID': str(user_did)}
        player = db.queryUser(query)
        if player:
            update_query = {"$inc": {'BALANCE': bless_total_amount}}
            db.updateUserNoFilter(query, update_query)
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
        query = {'TEAM_NAME': str(team.lower())}
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


async def prestige_icon(prestige = int):
    aicon = ":new_moon:"

    if prestige == 1:
        aicon = ":waxing_crescent_moon:"
    elif prestige == 2:
        aicon = ":first_quarter_moon:"
    elif prestige == 3:
        aicon = ":waxing_gibbous_moon:"
    elif prestige == 4:
        aicon = ":full_moon:"
    elif prestige == 5:
        aicon = ":waning_gibbous_moon:"
    elif prestige == 6:
        aicon = ":last_quarter_moon:"
    elif prestige == 7:
        aicon = ":waning_crescent_moon:"
    elif prestige == 8:
        aicon = ":crescent_moon:"
    elif prestige == 9:
        aicon = ":crown:"
    elif prestige >= 10:
        aicon = ":japanese_ogre:"

    return aicon


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
            print("Cannot find Association")
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


async def blessguild_Alt(amount, guild):
    try:
        blessAmount = amount
        posBlessAmount = 0 + abs(int(blessAmount))
        query = {'GNAME': str(guild)}
        guild_data = db.queryGuildAlt(query)
        if guild_data:
            hall = guild_data['HALL']
            hall_data = db.queryHall({'HALL': hall})
            multiplier = hall_data['MULT']
            posBlessAmount = posBlessAmount
            query = {'GNAME': str(guild_data['GNAME'])}
            update_query = {"$inc": {'BANK': int(posBlessAmount)}}
            db.updateGuildAlt(query, update_query)
        else:
            print("Cannot find Association")
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
        user_data = db.queryUser(query)
        if user_data:
            update_query = {"$inc": {'BALANCE': int(negCurseAmount)}}
            db.updateUserNoFilter(query, update_query)
            return True
    except Exception as ex:
        custom_logging.debug(ex)


async def player_check(ctx):
    query = {'DID': str(ctx.author.id)}
    valid = await asyncio.to_thread(db.queryUser, query)
    if valid:
        return valid
    else:
        await ctx.send(f"{ctx.author.mention}, you must register using /register to play Anime VS+.")
        return False


def scenario_gold_drop(scenario_lvl, fight_count, scenario_title, completed_scenarios, difficulty):
    gold = scenario_lvl * (500 * fight_count)
    if difficulty == "HARD":
        gold = gold * 3
    
    if scenario_title in completed_scenarios:
        gold = gold * 0.5

    return gold


def inc_essence(did, element, essence):
    try:
        emoji = set_emoji(element)
        query = {'DID': str(did)}
        update_query = {'$inc': {'ESSENCE.$[type].' + "ESSENCE": essence}}
        filter_query = [{'type.' + "ELEMENT": element}]
        response = db.updateUser(query, update_query, filter_query)
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


def decrease_talisman_count(did, element):
    try:
        emoji = set_emoji(element)
        query = {'DID': str(did)}
        vault = db.queryUser(query)
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
            r = db.updateUser(query, update_query, filter_query)
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
        resp = db.updateUserNoFilter(query, update_query)
        user_update_query = {'$set': {'TALISMAN': 'NULL'}}
        db.updateUserNoFilter(query, user_update_query)
        response = inc_essence(did, element, 500)
        msg = f"{response} **{element.title()} Talisman** has been dismantled into **500 {response} {element.title()} Essence**"
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


def essence_cost(user, element):
    try:
        did = user['DID']
        query = {'DID': did}
        essence_list = user["ESSENCE"]
        talisman_list = user["TALISMANS"]
        talisman_exists = False
        msg = ""
        essence = None
        for e in essence_list:
            if e["ELEMENT"] == element:
                essence = e["ESSENCE"]

        for t in talisman_list:
            if t["TYPE"] == element.upper():
                talisman_exists = True

        if not essence:
            msg = f"You do not have any {set_emoji(element)} {element.title()} essence."
            return msg
        if talisman_exists:
            msg = f"You already have a {set_emoji(element)} {element.title()} Talisman."
            return msg       

        if essence < 1500:
            msg = f"You do not have enough {set_emoji(element)} {element.title()} essence to transfuse at this time."
            return msg


        curseAmount = int(1500)
        negCurseAmount = 0 - abs(int(curseAmount))
        
        update_query = {'$inc': {'ESSENCE.$[type].' + "ESSENCE": negCurseAmount}}
        filter_query = [{'type.' + "ELEMENT": element}]
        response = db.updateUser(query, update_query, filter_query)
        talisman_query = {
                '$set': {
                    "TALISMAN": element.upper()
                },
                '$addToSet': {
                    "TALISMANS": {
                        "TYPE": element.upper(),
                        "DUR": 30
                    }
                }
            }
        tresponse = db.updateUserNoFilter(query, talisman_query)
        msg = f"You have successfully attuned and equipped a {set_emoji(element)} {element.title()} Talisman!"
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


def prestige_icon(prestige):
    aicon = ":new_moon:"
    if prestige == 1:
        aicon = ":waxing_crescent_moon:"
    elif prestige == 2:
        aicon = ":first_quarter_moon:"
    elif prestige == 3:
        aicon = ":waxing_gibbous_moon:"
    elif prestige == 4:
        aicon = ":full_moon:"
    elif prestige == 5:
        aicon = ":waning_gibbous_moon:"
    elif prestige == 6:
        aicon = ":last_quarter_moon:"
    elif prestige == 7:
        aicon = ":waning_crescent_moon:"
    elif prestige == 8:
        aicon = ":crescent_moon:"
    elif prestige == 9:
        aicon = ":crown:"
    elif prestige >= 10:
        aicon = ":japanese_ogre:"
    return str(aicon)


def level_sync_stats(lvl, stat):
    stat_sync = 0

    if stat == "HLT":
        stat_sync = round(lvl * level_sync["HLT"])
        return stat_sync
    if stat == "ATK_DEF":
        stat_sync = round(lvl * 2)
        return stat_sync
    if stat == "AP":
        stat_sync = round((lvl / 2) * 1)
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


async def teamwin(team):
    query = {'TEAM_NAME': str(team.lower())}
    team_data = db.queryTeam(query)
    if team_data:
        update_query = {"$inc": {'SCRIM_WINS': 1}}
        db.updateTeam(query, update_query)
    else:
        print("Cannot find Guild")


async def teamloss(team):
    query = {'TEAM_NAME': str(team.lower())}
    team_data = db.queryTeam(query)
    if team_data:
        update_query = {"$inc": {'SCRIM_LOSSES': 1}}
        db.updateTeam(query, update_query)
    else:
        print("Cannot find Guild")


async def savematch(player, card, path, title, arm, universe, universe_type, exclusive):
    matchquery = {'PLAYER': player, 'CARD': card, 'PATH': path, 'TITLE': title, 'ARM': arm, 'UNIVERSE': universe,
                  'UNIVERSE_TYPE': universe_type, 'EXCLUSIVE': exclusive}
    save_match = db.createMatch(data.newMatch(matchquery))


def create_card_from_data(card_data, is_boss = False):
    try:
        card = Card(card_data['NAME'], card_data['PATH'], card_data['PRICE'], card_data['AVAILABLE'], card_data['SKIN_FOR'], card_data['HLT'], card_data['HLT'], card_data['STAM'], card_data['STAM'], card_data['MOVESET'], card_data['ATK'], card_data['DEF'], card_data['TYPE'], card_data['PASS'], card_data['SPD'], card_data['UNIVERSE'], card_data['TIER'], card_data['WEAKNESS'], card_data['RESISTANT'], card_data['REPEL'], card_data['ABSORB'], card_data['IMMUNE'], card_data['GIF'], card_data['FPATH'], card_data['RNAME'], card_data['RPATH'], is_boss, card_data['CLASS'], card_data['DROP_STYLE'])
        return card
    except Exception as ex:
        print(card_data['NAME'])
        custom_logging.debug(ex)
        return False


def create_title_from_data(title_data):
    title = Title(title_data['TITLE'], title_data['UNIVERSE'], title_data['ABILITIES'], title_data['RARITY'], title_data['UNLOCK_METHOD'], title_data['AVAILABLE'], title_data['ID'])
    return title

def create_arm_from_data(arm_data):
    arm = Arm(arm_data['ARM'], arm_data['UNIVERSE'], arm_data['ABILITIES'], arm_data['DROP_STYLE'], arm_data['AVAILABLE'], arm_data['ELEMENT'])
    return arm

def create_player_from_data(player_data):
    player = Player(player_data['AUTOSAVE'], player_data['AVAILABLE'], player_data['DISNAME'], player_data['DID'], player_data['AVATAR'], player_data['GUILD'], player_data['TEAM'], player_data['FAMILY'], player_data['TITLE'], player_data['CARD'], player_data['ARM'], player_data['PET'], player_data['TALISMAN'], player_data['CROWN_TALES'], player_data['DUNGEONS'], player_data['BOSS_WINS'], player_data['RIFT'], player_data['REBIRTH'], player_data['LEVEL'], player_data['EXPLORE'], player_data['SAVE_SPOT'], player_data['PERFORMANCE'], player_data['TRADING'], player_data['BOSS_FOUGHT'], player_data['DIFFICULTY'], player_data['STORAGE_TYPE'], player_data['USED_CODES'], player_data['BATTLE_HISTORY'], player_data['PVP_WINS'], player_data['PVP_LOSS'], player_data['RETRIES'], player_data['PRESTIGE'], player_data['PATRON'], player_data['FAMILY_PET'], player_data['EXPLORE_LOCATION'], player_data['SCENARIO_HISTORY'], player_data['BALANCE'], player_data['CARDS'], player_data['TITLES'], player_data['ARMS'], player_data['PETS'], player_data['DECK'], player_data['CARD_LEVELS'], player_data['QUESTS'], player_data['DESTINY'], player_data['GEMS'], player_data['STORAGE'], player_data['TALISMANS'], player_data['ESSENCE'], player_data['TSTORAGE'], player_data['ASTORAGE'], player_data['U_PRESET'])
    return player

def create_tutorial_bot(player_data):
    player = Player(player_data['AUTOSAVE'], player_data['AVAILABLE'], player_data['DISNAME'], player_data['DID'], player_data['AVATAR'], player_data['GUILD'], player_data['TEAM'], player_data['FAMILY'], "Starter", "Training Dummy", "Stock", "Chick", "None", player_data['CROWN_TALES'], player_data['DUNGEONS'], player_data['BOSS_WINS'], player_data['RIFT'], player_data['REBIRTH'], player_data['LEVEL'], player_data['EXPLORE'], player_data['SAVE_SPOT'], player_data['PERFORMANCE'], player_data['TRADING'], player_data['BOSS_FOUGHT'], player_data['DIFFICULTY'], player_data['STORAGE_TYPE'], player_data['USED_CODES'], player_data['BATTLE_HISTORY'], player_data['PVP_WINS'], player_data['PVP_LOSS'], player_data['RETRIES'], player_data['PRESTIGE'], player_data['PATRON'], player_data['FAMILY_PET'], player_data['EXPLORE_LOCATION'], player_data['SCENARIO_HISTORY'], player_data['BALANCE'], player_data['CARDS'], player_data['TITLES'], player_data['ARMS'], player_data['PETS'], player_data['DECK'], player_data['CARD_LEVELS'], player_data['QUESTS'], player_data['DESTINY'], player_data['GEMS'], player_data['STORAGE'], player_data['TALISMANS'], player_data['ESSENCE'], player_data['TSTORAGE'], player_data['ASTORAGE'], player_data['U_PRESET'])
    return player

def create_summon_from_data(summon_data):
    summon = Summon(summon_data['PET'], summon_data['UNIVERSE'], summon_data['PATH'], summon_data['AVAILABLE'], summon_data['DROP_STYLE'], summon_data['ABILITIES'])
    return summon


def update_arm_durability(player, player_arm, player_card):
    try:
        pokemon_universes = ['Kanto Region', 'Johto Region','Hoenn Region','Sinnon Region','Kalos Region','Alola Region','Galar Region']
        decrease_value = -1
        break_value = 1
        dismantle_amount = 5000

        arm_universe = player_arm.universe
        arm_name = player_arm.name
        card = player_card

        # Check if the difficulty is easy, return if so
        if player.difficulty == "EASY":
            return

        # Set arm universe to card universe if it is part of the pokemon universes
        if player_card.universe in pokemon_universes and player_arm.universe in pokemon_universes:
            arm_universe = player_card.universe
        if player_card.universe == "Soul Eater":
            arm_universe = player_card.universe
        # Increase decrease value and break value if arm universe doesn't match card universe
        if arm_universe != player_card.universe and arm_universe != "Unbound":
            decrease_value = -5
            break_value = 5
        #vault = db.queryVault({'DID': player.did})
        # Check if arm exists in the player's vault
        for a in player.arms:
            if a['ARM'] == str(player_arm.name):
                current_durability = a['DUR']
           
                # Dismantle arm if its durability is 0 or below
                new_durability = current_durability - abs(decrease_value)
                if new_durability <= 0:
                    arm_name = player_arm.name
                    selected_universe = arm_universe
                    # for gems in player.gems:
                    #     print(gems)
                    current_gems = [gems['UNIVERSE'] for gems in player.gems]

                    # Update gems if selected universe exists in current gems
                    if selected_universe in current_gems:
                        db.updateUser({'DID': str(player.did)}, 
                                       {'$inc': {'GEMS.$[type].GEMS': dismantle_amount}},
                                       [{'type.UNIVERSE': selected_universe}])
                    else:
                        db.updateUserNoFilter({'DID': str(player.did)},
                                               {'$addToSet':{'GEMS': {'UNIVERSE': selected_universe, 
                                                                      'GEMS': dismantle_amount, 
                                                                      'UNIVERSE_HEART': False, 
                                                                      'UNIVERSE_SOUL': False}}})

                    # Remove arm from player's vault
                    db.updateUserNoFilter({'DID': str(player.did)},
                                           {'$pull': {'ARMS': {'ARM': str(arm_name)}}})

                    # Update player's arm to "Stock"
                    db.updateUserNoFilter({'DID': str(player.did)},
                                          {'$set': {'ARM': 'Stock'}})
                    player.equipped_arm = "Stock"
                    return f"**{player_arm.name}** dismantled after losing all ⚒️ durability, you earn 💎 {str(dismantle_amount)}. Your arm is now **Stock**"
                else:                   
                    query = {'DID': str(player.did)}
                    update_query = {'$inc': {'ARMS.$[type].' + 'DUR': decrease_value}}
                    filter_query = [{'type.' + "ARM": str(arm_name)}]
                    resp = db.updateUser(query, update_query, filter_query)
                    player_arm.durability = new_durability
                    for arms in player.arms:
                        if arms['ARM'] == str(player_arm.name):
                            arms['DUR'] = arms['DUR'] - abs(decrease_value)
                    if new_durability > 15:
                        return False
                    else:
                        return f"⚒️ {new_durability} | **{player_arm.name}** will lose all durability soon! Use **/blacksmith** to repair!"
                        
    except Exception as ex:
        custom_logging.debug(ex)


def get_battle_positions(battle_config):
    """
    Retrieves the positions of players, cards, titles, and arms for the battle.

    Parameters:
    - battle_config: Configuration object for the battle.

    Returns:
    Tuple: Tuple containing the battle positions in the following order:
    - turn_player: Turn player object
    - turn_card: Turn player's card object
    - turn_title: Turn player's title object
    - turn_arm: Turn player's arm object
    - opponent_player: Opponent player object
    - opponent_card: Opponent player's card object
    - opponent_title: Opponent player's title object
    - opponent_arm: Opponent player's arm object
    - partner_player: Partner player object
    - partner_card: Partner player's card object
    - partner_title: Partner player's title object
    - partner_arm: Partner player's arm object

    Steps:
    1. Define a dictionary with player configurations for different turn scenarios.
    2. Retrieve the appropriate player configurations based on the battle turn.
    3. Get the respective player, card, title, and arm objects for the turn, opponent, and partner positions.
    4. If it's co-op or duo mode and specific conditions are met, update the opponent player, card, title, and arm objects.
    5. Return the battle positions as a tuple.
    """
    player_config = {
        0: {
            'turn': ('player1', 'player1_card', 'player1_title', 'player1_arm'),
            'opponent': ('player2', 'player2_card', 'player2_title', 'player2_arm'),
            'partner': ('player3', 'player3_card', 'player3_title', 'player3_arm')
        },
        1: {
            'turn': ('player2', 'player2_card', 'player2_title', 'player2_arm'),
            'opponent': ('player1', 'player1_card', 'player1_title', 'player1_arm'),
            'partner': ('player2', 'player2_card', 'player2_title', 'player2_arm')
        },
        2: {
            'turn': ('player3', 'player3_card', 'player3_title', 'player3_arm'),
            'opponent': ('player2', 'player2_card', 'player2_title', 'player2_arm'),
            'partner': ('player3', 'player3_card', 'player3_title', 'player3_arm')
        },
        3: {
            'turn': ('player2', 'player2_card', 'player2_title', 'player2_arm'),
            'opponent': ('player3', 'player3_card', 'player3_title', 'player3_arm'),
            'partner': ('player2', 'player2_card', 'player2_title', 'player2_arm')
        }
    }

    turn = player_config[battle_config.is_turn]['turn']
    opponent = player_config[battle_config.is_turn]['opponent']
    partner = player_config[battle_config.is_turn]['partner']

    turn_player = getattr(battle_config, turn[0])
    turn_card = getattr(battle_config, turn[1])
    turn_title = getattr(battle_config, turn[2])
    turn_arm = getattr(battle_config, turn[3])
    
    opponent_player = getattr(battle_config, turn[0])
    opponent_card = getattr(battle_config, opponent[1])
    opponent_title = getattr(battle_config, opponent[2])
    opponent_arm = getattr(battle_config, opponent[3])

    if (battle_config.is_co_op_mode or battle_config.is_duo_mode):
        if battle_config.is_turn == 1:
            if opponent_card.used_defend == True:
                opponent_player = getattr(battle_config, 'player3')
                opponent_card = getattr(battle_config, 'player3_card')
                opponent_title = getattr(battle_config, 'player3_title')
                opponent_arm = getattr(battle_config, 'player3_arm')
        if battle_config.is_turn == 3:
            if opponent_card.used_defend == True:
                opponent_player = getattr(battle_config, 'player1')
                opponent_card = getattr(battle_config, 'player1_card')
                opponent_title = getattr(battle_config, 'player1_title')
                opponent_arm = getattr(battle_config, 'player1_arm')

    partner_player = getattr(battle_config, partner[0])
    partner_card = getattr(battle_config, partner[1])
    partner_title = getattr(battle_config, partner[2])
    partner_arm = getattr(battle_config, partner[3])

    # print(turn_player.summon_image)
    return turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm


def get_trade_eligibility(trader, trade_player):
    # if trader.level < 11 and trader.prestige == 0:
    #     return "🔓 Unlock Trading by completeing Floor 10 of the 🌑 Abyss! Use /solo to enter the abyss."

    # if trade_player.level < 11 and trade_player.prestige == 0:
    #     return f"🔓 <@{trade_player.did}> has not unlocked Trading by completing Floor 10 of the 🌑."
    
    return False

def get_class_value(card_class):
    tier_value = {
            1: 1, 2: 1, 3: 1,
            4: 2, 5: 2,
            6: 3, 7: 3,
            8: 4, 9: 4,
            10: 5
        }
    value = tier_value.get(card_class, 1)
    return value

def get_jjk_class_value(card_class):
    tier_value = {
            1: 10, 2: 10, 3: 10,
            4: 9, 5: 9,
            6: 8, 7: 8,
            8: 7, 9: 7,
            10: 6
        }
    value = tier_value.get(card_class, 1)
    return value
    
def card_being_traded(player_did, card_name):
    trade_data = db.queryTrade({'MERCHANT': player_did, 'OPEN': True})
    if not trade_data:
        return False
    being_traded = False
    for card in trade_data['CARDS']:
        if card['NAME'] == card_name and card['DID'] == player_did:
            being_traded = True
    return being_traded


def arm_being_traded(player_did, arm_name):
    trade_data = db.queryTrade({'MERCHANT': player_did, 'OPEN': True})
    if not trade_data:
        return False
    being_traded = False
    for arm in trade_data['ARMS']:
        if arm['NAME'] == arm_name and arm['DID'] == player_did:
            being_traded = True
    return being_traded


def summon_being_traded(player_did, arm_name):
    trade_data = db.queryTrade({'MERCHANT': player_did, 'OPEN': True})
    if not trade_data:
        return False
    being_traded = False
    for summon in trade_data['SUMMONS']:
        if summon['NAME'] == arm_name and summon['DID'] == player_did:
            being_traded = True
    return being_traded


def get_balance_icon(balance):
    icon = "🪙"
    if balance >= 150000:
        icon = "💸"
    elif balance >=100000:
        icon = "💰"
    elif balance >= 50000:
        icon = "💵"
    
    return icon


level_sync = {
    "HLT": 10,
    "ATK_DEF": 2,
    "AP": 2
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


title_enhancer_suffix_mapping = {'ATK': '% each turn',
    'DEF': '% each turn',
    'STAM': '% each turn',
    'HLT': ' % of your current health each turn',
    'LIFE': '% of your opponent\'s health each turn',
    'DRAIN': '% each turn',
    'FLOG': '% each turn',
    'WITHER': '% each turn',
    'RAGE': '% each turn',
    'BRACE': '% each turn',
    'BZRK': '% each turn',
    'CRYSTAL': '% each turn',
    'GROWTH': '% each turn',
    'FEAR': '% each turn',
    'STANCE': 'Flat each turn',
    'CONFUSE': 'Flat each turn',
    'CREATION': '% each turn',
    'DESTRUCTION': '% each turn',
    'SPEED': '% each focus',
    'SLOW': ' Turn',
    'HASTE': ' Turn',
    'WAVE': ' Turn',
    'BLAST': ' Turn',
    'SOULCHAIN': '',
    'GAMBLE': '',
    'SINGULARITY': '%',
    'IQ': ' %',
    'HIGH IQ': '',
    'BLITZ': '',
    'FORESIGHT': '',
    'OBLITERATE': '',
    'IMPENETRABLE SHIELD': '',
    'PIERCE': '',
    'SYNTHESIS': '',
    'SPELL SHIELD': '',
    'ELEMENTAL BUFF': 'elemental damage by 50%',
    'ELEMENTAL DEBUFF': 'elemental damage by 50%',
    'ENHANCED GUARD': '',
    'STRATEGIST': '',
    'SHARPSHOOTER': '',
    'DIVINITY': '',
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


title_prefix_mapping = {
    'ATK': 'Increases your attack by ',
    'DEF': 'Increases your defense by ',
    'STAM': 'Increases your stamina by ',
    'HLT': ' Heals you for ',
    'LIFE': 'Steals ',
    'DRAIN': 'Drains ',
    'FLOG': 'Steals ',
    'WITHER': 'Steals ',
    'RAGE': 'Decreases your defense to increase your AP by ',
    'BRACE': 'Decreases your attack to increase your AP by',
    'BZRK': 'Decreases your health to increase your attack by ',
    'CRYSTAL': 'Decreases your health to increase your defense by ',
    'GROWTH': 'Decreases your max health to increase your attack, defense, and AP by ',
    'FEAR': 'Decreases your max health to decrease your opponents attack, defense, and AP by ',
    'STANCE': 'Swaps your attack and defense stats, increasing your attack by ',
    'CONFUSE': 'Swaps opponents attack and defense stats, decreasing their attack by ',
    'CREATION': 'Increases your max health by ',
    'WAVE': 'remove this',
    'BLAST': 'remove this',
    'DESTRUCTION': 'Decreases opponent max health by',
    'SPEED': 'Increases your speed by ',
    'SLOW': ' Decreases turn count by ',
    'HASTE': ' Increases turn count by ',
    'SOULCHAIN': 'Prevents focus stat buffs',
    'GAMBLE': 'Randomizes focus stat buffs',
    'SINGULARITY': 'Increases resolve buff by ',
    'IQ': ' Increases focus buffs by ',
    'HIGH IQ': 'Continues focus buffs after resolve',
    'BLITZ': 'Hit through parries',
    'FORESIGHT': 'Parried hits deal 10% damage to yourself',
    'OBLITERATE': 'Hit through shields',
    'IMPENETRABLE SHIELD': 'Shields cannot be penetrated',
    'PIERCE': 'Hit through all barriers',
    'SYNTHESIS': 'Hits to your barriers store 50% of damage dealt, you heal from this amount on resolve.',
    'SPELL SHIELD': 'All shields will absorb elemental damage healing you',
    'ELEMENTAL BUFF': 'Increase ',
    'ELEMENTAL DEBUFF': 'Decrease opponent ',
    'ENHANCED GUARD': 'Negates 80% of damage when blocking, prevents critical hits.',
    'STRATEGIST': 'Hits through all protections.',
    'SHARPSHOOTER': 'Attacks never miss',
    'DIVINITY': 'Ignore elemental effects until resolved',
}


title_types = [
    'ATK', 'DEF', 'STAM', 'HLT', 'LIFE', 'DRAIN', 'FLOG', 'WITHER', 
    'RAGE', 'BRACE', 'BZRK', 'CRYSTAL', 'GROWTH', 'FEAR', 'STANCE', 
    'CONFUSE', 'CREATION', 'DESTRUCTION', 'SPEED', 'SLOW', 'HASTE', 
    'SOULCHAIN', 'GAMBLE', 'SINGULARITY', 'IQ', 'HIGH IQ', 'BLITZ', 
    'FORESIGHT', 'OBLITERATE', 'IMPENETRABLE SHIELD', 'PIERCE', 
    'SYNTHESIS', 'SPELL SHIELD', 'ELEMENTAL BUFF', 'ELEMENTAL DEBUFF', 
    'ENHANCED GUARD', 'STRATEGIST', 'SHARPSHOOTER', 'DIVINITY'
]

def get_title_types():
    try:
        title_type_list_of_dicts = []
        for title_type in title_types:
            title_type_list_of_dicts.append({'name': title_type, 'value': title_type})
        return title_type_list_of_dicts
    except Exception as e:
        print(e)
        return False
    

element_choices = [
    {"name": "Physical 👊", "value": "PHYSICAL"},
    {"name": "Fire 🔥", "value": "FIRE"},
    {"name": "Ice ❄️", "value": "ICE"},
    {"name": "Water 💧", "value": "WATER"},
    {"name": "Earth ⛰️", "value": "EARTH"},
    {"name": "Electric ⚡️", "value": "ELECTRIC"},
    {"name": "Wind 🌪️", "value": "WIND"},
    {"name": "Psychic 🔮", "value": "PSYCHIC"},
    {"name": "Death ☠️", "value": "DEATH"},
    {"name": "Life ❤️‍🔥", "value": "LIFE"},
    {"name": "Light 🌕", "value": "LIGHT"},
    {"name": "Dark 🌑", "value": "DARK"},
    {"name": "Poison 🧪", "value": "POISON"},
    {"name": "Gun 🔫", "value": "GUN"},
    {"name": "Rot 🩻", "value": "ROT"},
    {"name": "Sword ⚔️", "value": "SWORD"},
    {"name": "Nature 🌿", "value": "NATURE"},
    {"name": "Ranged 🏹", "value": "RANGED"},
    {"name": "Energy / Spirit 🧿", "value": "ENERGY"},
    {"name": "Reckless ♻️", "value": "RECKLESS"},
    {"name": "Time ⌛", "value": "TIME"},
    {"name": "Bleed 🅱️", "value": "BLEED"},
    {"name": "Gravity 🪐", "value": "GRAVITY"},
    {"name": "Sleep 💤", "value": "SLEEP"}
]

def get_element_types():
    try:
        element_type_list_of_dicts = []
        for element in element_choices:
            element_type_list_of_dicts.append({'name': element["name"], 'value': element["value"]})
        return element_type_list_of_dicts
    except Exception as e:
        print(e)
        return False
    
arm_choices = [
    {"name": "Physical 👊", "value": "PHYSICAL"},
    {"name": "Fire 🔥", "value": "FIRE"},
    {"name": "Ice ❄️", "value": "ICE"},
    {"name": "Water 💧", "value": "WATER"},
    {"name": "Earth ⛰️", "value": "EARTH"},
    {"name": "Electric ⚡️", "value": "ELECTRIC"},
    {"name": "Wind 🌪️", "value": "WIND"},
    {"name": "Psychic 🔮", "value": "PSYCHIC"},
    {"name": "Death ☠️", "value": "DEATH"},
    {"name": "Life ❤️‍🔥", "value": "LIFE"},
    {"name": "Light 🌕", "value": "LIGHT"},
    {"name": "Dark 🌑", "value": "DARK"},
    {"name": "Poison 🧪", "value": "POISON"},
    {"name": "Gun 🔫", "value": "GUN"},
    {"name": "Rot 🩻", "value": "ROT"},
    {"name": "Sword ⚔️", "value": "SWORD"},
    {"name": "Nature 🌿", "value": "NATURE"},
    {"name": "Sleep 💤", "value": "SLEEP"},
    {"name": "Ranged 🏹", "value": "RANGED"},
    {"name": "Energy / Spirit 🧿", "value": "ENERGY"},
    {"name": "Reckless ♻️", "value": "RECKLESS"},
    {"name": "Time ⌛", "value": "TIME"},
    {"name": "Bleed 🅱️", "value": "BLEED"},
    {"name": "Gravity 🪐", "value": "GRAVITY"},
    {"name": "Draconic 🐲", "value": "DRACONIC"},
    {"name": "Parry 🔄", "value": "PARRY"},
    {"name": "Shield 🌐", "value": "SHIELD"},
    {"name": "Barrier 💠", "value": "BARRIER"},
    {"name": "Siphon 💉", "value": "SIPHON"}
]

def get_arm_types():
    try:
        arm_type_list_of_dicts = []
        for arm in arm_choices:
            arm_type_list_of_dicts.append({'name': arm["name"], 'value': arm["value"]})
        return arm_type_list_of_dicts
    except Exception as e:
        print(e)
        return False

blocking_traits = [
    'Attack On Titan',
    'Black Clover',
    'Bleach',
    'Death Note',
    'YuYu Hakusho',
    'My Hero Academia',
]

revive_traits = [
    'Dragon Ball Z',
    'Chainsawman',
]

starting_traits = [
    'Death Note',
    'One Piece',
    'Demon Slayer',
    'Full Metal Alchemist',
    "Chainsawman",
    'My Hero Academia',
]

blitz_traits = [
    'Bleach',
    'Persona',
    'Attack On Titan',
    'Demon Slayer'
]


death_traits = [
    'Dragon Ball Z',
    'Souls',
    'Chainsawman'
]

miss_crit_traits = [
    'Jujutsu Kaisen',
    'Soul Eater',
]

summon_traits = [
    'Persona',
    'Soul Eater',
    'That Time I Got Reincarnated as a Slime'
]


opponent_focus_trait = [
    '7ds',
    'One Punch Man',
    'Souls',
    
    # Add more traits here
]

universe_stack_traits = [
    'Naruto',
    'Full Metal Alchemist',
    'My Hero Academia',
    'Chainsawman',
    'Jujustu Kaisen',
    'Attack On Titan',
]
focus_traits = [
    'Digimon',
    'Dragonball Z',
    'Solo Leveling',
    'Black Clover',
    'One Punch Man',
    'Jujutsu Kaisen',
    'Overlord',
    'Fairy Tail',
    'League Of Legends',
    'Naruto',
    'One Piece',
    'That Time I Got Reincarnated as a Slime',
    'Soul Eater',
]

resolve_traits = [
    'Digimon',
    'God of War',
    'Attack On Titan',
    'Jujutsu Kaisen',
    'Pokemon',
    'Bleach',
    'Jujutsu Kaisen',
    'Naruto',
    'My Hero Academia',
    'Demon Slayer',
    'YuYu Hakusho',
    'One Piece',
    'Souls',
    'Fate',
    'That Time I Got Reincarnated as a Slime',
    'Fairy Tail',
    'Full Metal Alchemist',
    'Soul Eater',
]



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

def get_enhancer_mapping(enhancer):
    return enhancer_mapping[enhancer]

enhancer_mapping = {
    'ATK': 'Increase Attack By AP %',
    'DEF': 'Increase Defense by AP %',
    'STAM': 'Increase Stamina by Flat AP',
    'HLT': 'Increase Health By Flat AP + 16% of Missing Health',
    'LIFE': 'Steal Opponent Health and Add it to your Current Health by Flat AP + 9% of Opponent Current Health',
    'DRAIN': 'Steal Opponent Stamina and Add it to your Stamina by Flat AP',
    'FLOG': 'Steal Opponent Attack and Add it to Your Attack by AP %',
    'WITHER': 'Steal Opponent Defense and Add it to Your Defense by AP %',
    'RAGE': 'Decrease Your Defense by AP %, Increase All Moves AP by Amount of Decreased Defense',
    'BRACE': 'Decrease Your Attack by AP %, Increase All Moves AP By Amount of Decreased Attack',
    'BZRK': 'Decrease Your Current Health by AP %, Increase Your Attack by Amount of Decreased Health',
    'CRYSTAL': 'Decrease Your Health by AP %, Increase Your Defense by Amount of Decreased Health',
    'GROWTH': 'Decrease Your Max Health by 10%, Increase Your Attack, Defense and AP Buff by AP',
    'STANCE': 'Swap Your Attack and Defense, Increase Your Defense By Flat AP',
    'CONFUSE': 'Swap Opponent Attack and Defense, Decrease Opponent Defense by Flat AP',
    'BLINK': 'Decreases Your Stamina by AP, Increases Opponent Stamina by AP',
    'SLOW': 'Decreases the turn total by AP',
    'HASTE': 'Increases the turn total by AP',
    'FEAR': 'Decrease Your Max Health and Health by 20%, Decrease Opponent Attack, Defense, and reduce Opponent AP Buffs by AP',
    'SOULCHAIN': 'You and Your Opponent\'s Stamina Equal AP',
    'GAMBLE': 'At the cost of your total stamina, You and Your Opponent\'s Health Equal between 500 & AP value',
    'WAVE': 'Deal Flat AP Damage to Opponent. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will deal 75% AP Damage*',
    'CREATION': 'Increase Max Health by Flat AP. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will heal Health & Max Health for 75% AP*',
    'BLAST': 'Deal Flat AP Damage to Opponent. AP Increases each turn',
    'DESTRUCTION': 'Decrease Your Opponent Max Health by Flat AP (only opponent on PET use). AP Increases each turn',
    'BASIC': 'Increase Basic Attack AP',
    'SPECIAL': 'Increase Special Attack AP',
    'ULTIMATE': 'Increase Ultimate Attack AP',
    'ULTIMAX': 'Increase Attack Move AP and ATK & DEF Values',
    'MANA': 'Increase Attack Move AP and Enhancer AP',
    'SHIELD': 'Blocks Incoming DMG, until broken',
    'BARRIER': 'Nullifies Incoming Attacks, until broken',
    'PARRY': 'Returns 25% Damage, until broken',
    'SIPHON': 'Heal for 10% DMG inflicted + AP'
}


title_enhancer_mapping = {
    'ATK': 'Increases your attack by % each turn',
    'DEF': 'Increases your defense by % each turn',
    'STAM': 'Increases your stamina by % each turn',
    'HLT': 'Heals you for % of your current health each turn',
    'LIFE': 'Steals % of your opponent\'s health each turn',
    'DRAIN': 'Drains % of opponent\'s stamina each turn',
    'FLOG': 'Steals % of opponent\'s attack each turn',
    'WITHER': 'Steals % of opponent\'s defense each turn',
    'RAGE': 'Decreases your defense to increase your AP by % each turn',
    'BRACE': 'Decreases your attack to increase your AP by % each turn',
    'BZRK': 'Decreases your health to increase your attack by % each turn',
    'CRYSTAL': 'Decreases your health to increase your defense by % each turn',
    'GROWTH': 'Decreases your max health to increase your attack, defense, and AP by Flat AP each turn',
    'STANCE': 'Swaps your attack and defense stats, increasing your attack by % each turn',
    'CONFUSE': 'Swaps opponent\'s attack and defense stats, decreasing their attack by % each turn',
    'BLINK': 'Decreases your stamina by AP, Increases opponent stamina by AP',
    'SLOW': 'Decreases turn count by Turn',
    'HASTE': 'Increases turn count by Turn',
    'FEAR': 'Decreases your max health to decrease your opponent\'s attack, defense, and AP by Flat AP each turn',
    'SOULCHAIN': 'Prevents focus stat buffs',
    'GAMBLE': 'Randomizes focus stat buffs',
    'WAVE': 'Deal Damage, Decreases over time',
    'CREATION': 'Heals you, Decreases over time',
    'BLAST': 'Deals Damage, Increases over time based on card tier',
    'DESTRUCTION': 'Decreases Your Opponent Max Health, Increases over time based on card tier',
    'BASIC': 'Increase Basic Attack AP',
    'SPECIAL': 'Increase Special Attack AP',
    'ULTIMATE': 'Increase Ultimate Attack AP',
    'ULTIMAX': 'Increase Attack Move AP and ATK & DEF Values',
    'MANA': 'Increase Attack Move AP and Enhancer AP',
    'SHIELD': 'Blocks Incoming DMG, until broken',
    'BARRIER': 'Nullifies Incoming Attacks, until broken',
    'PARRY': 'Returns 25% Damage, until broken',
    'SIPHON': 'Heal for 10% DMG inflicted + AP',
    'BLITZ': 'Hit through parries',
    'FORESIGHT': 'Parried hits deal 10% damage to yourself',
    'OBLITERATE': 'Hit through shields',
    'IMPENETRABLE SHIELD': 'Shields cannot be penetrated',
    'PIERCE': 'Hit through all barriers',
    'SYNTHESIS': 'Hits to your barriers store 50% of damage dealt, you heal from this amount on resolve',
    'STRATEGIST': 'Hits through all guards / protections',
    'SHARPSHOOTER': 'Attacks never miss',
    'SPELL SHIELD': 'All shields will absorb elemental damage healing you',
    'ELEMENTAL BUFF': 'Increase elemental damage by 50%',
    'ELEMENTAL DEBUFF': 'Decrease opponent\'s elemental damage by 50%',
    'DIVINITY': 'Ignore elemental effects until resolved',
    'IQ': 'Increases focus buffs by %',
    'HIGH IQ': 'Continues focus buffs after resolve',
    'SINGULARITY': 'Increases resolve buff by %'
}

def get_element_mapping(element):
    return element_mapping[element]

element_mapping = {
    'PHYSICAL': 'If ST(stamina) greater than 80, Deals Bonus Damage. After 3 Strike gain a Parry',
    'FIRE': 'Does 50% damage of previous attack over the next opponent turns, burn effect bypasses shields and stacks.',
    'ICE': 'Every 3rd attack, opponent freezes and loses 1 turn, and loses attack and defense equal to 50% of damage dealt.',
    'WATER': 'Each strike increases all water move AP by 100. Every 300 AP, gain a shield. Every 400 AP send a Tsunami Strike for True Damage.',
    'EARTH': 'Penetrates Parry. Increases Def by 25% AP. Grants Shield - Increase by 50% DMG.',
    'ELECTRIC': 'Add 35% DMG Dealt to Shock damage, Shock damage amplifies all Move AP.',
    'WIND': 'On Miss or Crit, boosts all wind damage by 75% of damage dealt.',
    'PSYCHIC': 'Penetrates Barriers. Reduce opponent ATK & DEF by 35% DMG. After 3 Hits Gain a Barrier.',
    'DEATH': 'Deals 40% DMG to opponent max health. Gain Attack equal to that amount. Executes opponent if their health equals 10% of their base max health.',
    'LIFE': 'Steal Max Health and Heal for 40% DMG.',
    'LIGHT': 'Increases ATK by 40% of DMG. 40% of DMG is stored and damages the opponent when they focus.',
    'DARK': 'Penetrates all Protections & decreases opponent ST(Stamina) by 15.',
    'POISON': 'Penetrates Shields and Parry. Stacks Poison damage equal to 35% of damage done. Stacking up to 30% of opponent max health. The Opponent takes damage when they attack.',
    'ROT': 'Penetrates Shields and Parry. Stacks Rot damage equal to 15% of damage done stacking up to 20% of max health. The Opponent takes damage when they attack.',
    'RANGED': 'If ST(stamina) greater than 30, Deals 1.7x Damage. Every 3 Ranged Attacks Increase Hit Chance by 10%',
    'ENERGY': 'Has higher 35% higher chance of Crit. This crit hit goes through all protections.',
    'SPIRIT': 'Has higher 35% higher chance of Crit. This crit hit goes through all protections.',
    'GUN': 'Penetrates Shields. Has a 40% chance to strike twice. Double striking lowers opponents defense by 35% of the current value.',
    'SPIRIT ENERGY': 'Has higher 35% higher chance of Crit. This crit hit goes through all protections.',
    'NATURE': 'Saps Opponent ATK and DEF for 35% of Damage & heals Health and Max Health for that amount as well.',
    'SLEEP': 'Penetrates Shield and Parry. Every 2nd attack adds a stack of Rest. Before Opponent focuses they must Rest, skipping their turn, for each stack of Rest. Opponent only takes sleep damage while Resting.',
    'RECKLESS': 'Deals Incredible Bonus Damage, take 40% as reckless at the cost of a turn to recover. If Reckless would kill you reduce HP to 1. Reckless is buffed when resolved, but you take more damage as well.',
    'RECOIL': 'Deals Incredible Bonus Damage, take 40% as reckless at the cost of a turn to recover. If Reckless would kill you reduce HP to 1. Reckless is buffed when resolved, but you take more damage as well.',
    'TIME': 'Strong Block and Increase Turn Count by 3, If ST(Stamina) is < 50, Focus for 1 Turn and goes through and lowers opponent barriers and parry and AP is increased by damage dealt * turn total / 100.',
    'BLEED': 'Penetrates Parry. Every 2 Attacks deal (10x turn count + 5% Health) damage to opponent.',
    'SWORD': 'Every 3rd attack will result in a Critical Strike that also increases Atack by 40% of damage dealt.',
    'GRAVITY': 'Disables Opponent Block, Reduce opponent DEF by 40% DMG, Decrease Turn Count By 3, goes through barrier and parry.',
    'DRACONIC': 'Draconic attacks can only be ULTIMATE or Summoned. Penetrates all protections. Combines the AP and Elemental Effects of your BASIC and SPECIAL attack into one powerful blow!',
    'SHIELD': 'Blocks Incoming DMG, until broken',
    'BARRIER': 'Nullifies Incoming Attacks, until broken',
    'PARRY': 'Returns 25% Damage, until broken',
    'SIPHON': 'Heal for 10% DMG inflicted + AP',
}



"""
Put all of the elements from element_mapping in an array named element_list
"""
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
    "ENERGY",
    "RECKLESS",
    "TIME",
    "BLEED",
    "GRAVITY",
    "GUN",
    "NATURE",
    "SLEEP",
    "SWORD",
    "ROT",
    "DRACONIC"
]

element_emojis = [  
    {'name': '👊Physical', 'value': 'PHYSICAL'},
    {'name': '⚔️Sword', 'value': 'SWORD'},
    {'name': '🏹Ranged', 'value': 'RANGED'},
    {'name': '🔫Gun', 'value': 'GUN'},
    {'name': '♻️Reckless', 'value': 'RECKLESS'},
    {'name': '🅱️Bleed', 'value': 'BLEED'},
    {'name': '🔥Fire', 'value': 'FIRE'},
    {'name': '❄️Ice', 'value': 'ICE'},
    {'name': '💧Water', 'value': 'WATER'},
    {'name': '⛰️Earth', 'value': 'EARTH'},
    {'name': '🌿Nature', 'value': 'NATURE'},
    {'name': '🌩️Electric', 'value': 'ELECTRIC'},
    {'name': '🌪️Wind', 'value': 'WIND'},
    {'name': '🧿Energy/Spirit', 'value': 'ENERGY'},
    {'name': '🔮Psychic', 'value': 'PSYCHIC'},
    {'name': '☠️Death', 'value': 'DEATH'},
    {'name': '❤️‍🔥Life', 'value': 'LIFE'},
    {'name': '🌕Light', 'value': 'LIGHT'},
    {'name': '🌑Dark', 'value': 'DARK'},
    {'name': '🧪Poison', 'value': 'POISON'},
    {'name': '🩻Rot', 'value': 'ROT'},
    {'name': '⌛Time', 'value': 'TIME'},
    {'name': '🪐Gravity', 'value': 'GRAVITY'},
    {'name': '💤Sleep', 'value': 'SLEEP'},
    {'name': '🐲Draconic', 'value': 'DRACONIC'},
]

# element_emojis = {
#     "👊Physical": "PHYSICAL",
#     "⚔️Sword":"SWORD",
#     "🏹Ranged": ,
#     "🔫Gun":,
#     "♻️Reckless":,
#     "🅱️Bleed",
#     "🔥Fire",
#     "❄️Ice",
#     "💧Water",
#     "⛰️Earth",
#     "🌿Nature",
#     "🌩️Electric",
#     "🌪️Wind",
#     "🧿Energy/Spirit",
#     "🔮Psychic",
#     "☠️Death",
#     "❤️‍🔥Life",
#     "🌕Light",
#     "🌑Dark",
#     "🧪Poison",
#     "🩻Rot",
#     "⌛Time",
#     "🪐Gravity",
#     "💤Sleep",
#     "🐲Draconic",
# }


protections_list = [
    'SHIELD',
    'BARRIER',
    'PARRY'
]


enhancement_list = [
    'ATK',
    'DEF',
    'STAM',
    'HLT',
    'LIFE',
    'DRAIN',
    'FLOG',
    'WITHER',
    'RAGE',
    'BRACE',
    'BZRK',
    'CRYSTAL',
    'GROWTH',
    'STANCE',
    'CONFUSE',
    'BLINK',
    'SLOW',
    'HASTE',
    'FEAR',
    'SOULCHAIN',
    'GAMBLE',
    'WAVE',
    'CREATION',
    'BLAST',
    'DESTRUCTION',
    'BASIC',
    'SPECIAL',
    'ULTIMATE',
    'ULTIMAX',
    'MANA',
    'SHIELD',
    'BARRIER',
    'PARRY',
    'SIPHON',
]


autocomplete_advanced_search = [
    {'name': 'ATK', 'value': 'ATK'},
    {'name': 'DEF', 'value': 'DEF'},
    {'name': 'STAM', 'value': 'STAM'},
    {'name': 'HLT', 'value': 'HLT'},
    {'name': 'LIFE', 'value': 'LIFE'},
    {'name': 'DRAIN', 'value': 'DRAIN'},
    {'name': 'FLOG', 'value': 'FLOG'},
    {'name': 'WITHER', 'value': 'WITHER'},
    {'name': 'RAGE', 'value': 'RAGE'},
    {'name': 'BRACE', 'value': 'BRACE'},
    {'name': 'BZRK', 'value': 'BZRK'},
    {'name': 'CRYSTAL', 'value': 'CRYSTAL'},
    {'name': 'GROWTH', 'value': 'GROWTH'},
    {'name': 'STANCE', 'value': 'STANCE'},
    {'name': 'CONFUSE', 'value': 'CONFUSE'},
    {'name': 'BLINK', 'value': 'BLINK'},
    {'name': 'SLOW', 'value': 'SLOW'},
    {'name': 'HASTE', 'value': 'HASTE'},
    {'name': 'FEAR', 'value': 'FEAR'},
    {'name': 'SOULCHAIN', 'value': 'SOULCHAIN'},
    {'name': 'GAMBLE', 'value': 'GAMBLE'},
    {'name': 'WAVE', 'value': 'WAVE'},
    {'name': 'CREATION', 'value': 'CREATION'},
    {'name': 'BLAST', 'value': 'BLAST'},
    {'name': 'DESTROY', 'value': 'DESTROY'},
    {'name': 'BASIC', 'value': 'BASIC'},
    {'name': 'SPECIAL', 'value': 'SPECIAL'},
    {'name': 'ULTIMATE', 'value': 'ULTIMATE'},
    {'name': 'ULTIMAX', 'value': 'ULTIMAX'},
    {'name': 'MANA', 'value': 'MANA'},
    {'name': 'SHIELD', 'value': 'SHIELD'},
    {'name': 'BARRIER', 'value': 'BARRIER'},
    {'name': 'PARRY', 'value': 'PARRY'},
    {'name': 'SIPHON', 'value': 'SIPHON'},
    {'name': 'PHYSICAL', 'value': 'PHYSICAL'},
    {'name': 'FIRE', 'value': 'FIRE'},
    {'name': 'ICE', 'value': 'ICE'},
    {'name': 'WATER', 'value': 'WATER'},
    {'name': 'EARTH', 'value': 'EARTH'},
    {'name': 'ELECTRIC', 'value': 'ELECTRIC'},
    {'name': 'WIND', 'value': 'WIND'},
    {'name': 'PSYCHIC', 'value': 'PSYCHIC'},
    {'name': 'DEATH', 'value': 'DEATH'},
    {'name': 'LIGHT', 'value': 'LIGHT'},
    {'name': 'DARK', 'value': 'DARK'},
    {'name': 'POISON', 'value': 'POISON'},
    # Add GUN, SWORD, NATURE, and ROT
    {'name': 'GUN', 'value': 'GUN'},
    # Add SLEEP
    {'name': 'SLEEP', 'value': 'SLEEP'},
    # Add DRACONIC
    {'name': 'DRACONIC', 'value': 'DRACONIC'},
    {'name': 'SWORD', 'value': 'SWORD'},
    {'name': 'NATURE', 'value': 'NATURE'},
    {'name': 'ROT', 'value': 'ROT'},
    {'name': 'ENERGY', 'value': 'ENERGY'},
    {'name': 'RANGED', 'value': 'RANGED'},
    {'name': 'RECKLESS', 'value': 'RECKLESS'},
    {'name': 'RECOIL', 'value': 'RECOIL'},
    {'name': 'BLEED', 'value': 'BLEED'},
    {'name': 'GRAVITY', 'value': 'GRAVITY'},
    {'name': 'TIME', 'value': 'TIME'},
    {'name': 'FIGHTER', 'value': 'FIGHTER'},
    {'name': 'ASSASSIN', 'value': 'ASSASSIN'},
    {'name': 'MAGE', 'value': 'MAGE'},
    {'name': 'TANK', 'value': 'TANK'},
    {'name': 'RANGER', 'value': 'RANGER'},
    {'name': 'SWORDSMAN', 'value': 'SWORDSMAN'},
    {'name': 'SUMMONER', 'value': 'SUMMONER'},
    {'name': 'MONSTROSITY', 'value': 'MONSTROSITY'},
    {'name': 'HEALER', 'value': 'HEALER'},
    {'name': 'TACTICIAN', 'value': 'TACTICIAN'}
]


class_mapping = {
'ASSASSIN' : 'First [2-6] Attack cost 0 Stamina and Ignore Protections',  
'FIGHTER' : 'Starts each fight with up to 7 additional Parries',
'MAGE' : 'Increases Elemental Damage up to 60%',
'TANK' : ' Starts each fight with (250 x Card Tier) + Card Level Shield',
'RANGER' : 'Starts each fight with up to 6 additional Barriers',
'SWORDSMAN' : 'On Resolve, Gain up to 6 Critical Strikes',
'SUMMONER' : 'Starts each fight with summons available',
'MONSTROSITY' : 'On Resolve, Gain up to 5 Double Strikes',
'HEALER' : 'Stores up to 70% Damage recieved and increases healing on Focus by that amount',
'TACTICIAN' : 'Enter Focus using Block to craft Strategy Points'
}


pokemon_universes = ['Kanto Region', 'Johto Region','Hoenn Region','Sinnoh Region','Kalos Region','Alola Region','Galar Region']


crest_dict = { 'Unbound': '🉐',
              'My Hero Academia': '<:mha:1088699056420835419>',
              'League Of Legends': '<:3873_league_of_legends_logo:1088701143921729567>',
              'Pokemon': '<:pokemon:1088966251541450752>',
              'Naruto': '<:naruto_103:1088703639973015573>',
              'Bleach': '<:bleach:1088701142487285781>',
              'God Of War': '<:kratos:1088701141753274408>',
              'Chainsawman': '<:denji:1088701139886817311>',
              'One Punch Man': '<:pngaaa:1085072765587030027>',
              'Black Clover': '<:Black_Clover:1088699058262114314>',
              'Demon Slayer': '<:Demon_Slayer:1088702009709973565>',
              'Attack On Titan': '<:AOT:1088702007717658674>',
              '7ds': '<:7ds:1088702006581006377>',
              'Digimon': '<:digimon_sparkle:1088702667703988316>',
              'Fate': '<:fate:1092176982277632032>',
              'Solo Leveling': '<:jin:1090240014891352114>',
              'Souls': '<:dark_souls_icon:1088702666688966726>',
              'Dragon Ball Z': '<:dbz:1088698675338952774>',
              'Pokemon': '<:pokemon:1088966251541450752>',
              'Death Note': '<:death_note:1088702980682956800>',
              'Crown Rift Awakening': ':u7a7a:',
              'Crown Rift Slayers': ':sa:',
              'Crown Rift Madness': ':m:',
              'Persona': '<:persona:1090238487028047913>',
              'YuYu Hakusho': '<:yusuke:1088702663861993503>',
              'One Piece': '<:one_piece:1088702665581670451>',
              'Overlord': '<:overlord:1091223691729305681>',
              'Fairy Tail': '<:FairyTail:1091223690445865062>',
              'That Time I Got Reincarnated as a Slime': '<:slime:1091223689007210517>',
              'Soul Eater': '<:souleater:1257056890832031756>',
              'Kill La Kill': '<:killlakill:1214431376070410281>',
              'Gurren Lagann': '<:gurren:1214432235927773205>',
              'Jujutsu Kaisen': '<:jjk:1249819520650969138>',
              'Katekyo Hitman Reborn': '<:reborn:1257057934634909817>',
              'Full Metal Alchemist': '<:fma:1256672084327792730>',
              'Unbound': '🉐',
}

rpg_npc = { 
    'Unbound': '🉐',
    '<:mha:1088699056420835419>': 'My Hero Academia NPC',
    '<:3873_league_of_legends_logo:1088701143921729567>': 'League Of Legends NPC',
    '<:pokemon:1088966251541450752>': 'Pokemon NPC',
    '<:naruto_103:1088703639973015573>': 'Naruto NPC',
    '<:bleach:1088701142487285781>': 'Bleach NPC',
    '<:kratos:1088701141753274408>': 'God Of War NPC',
    '<:denji:1088701139886817311>': 'Chainsawman NPC',
    '<:pngaaa:1085072765587030027>': 'One Punch Man NPC',
    '<:Black_Clover:1088699058262114314>': 'Black Clover NPC',
    '<:Demon_Slayer:1088702009709973565>': 'Demon Slayer NPC',
    '<:AOT:1088702007717658674>': 'Attack On Titan NPC',
    '<:7ds:1088702006581006377>': '7ds NPC',
    '<:digimon_sparkle:1088702667703988316>': 'Digimon NPC',
    '<:fate:1092176982277632032>': 'Fate NPC',
    '<:jin:1090240014891352114>': 'Solo Leveling NPC',
    '<:dark_souls_icon:1088702666688966726>': 'Souls NPC',
    '<:dbz:1088698675338952774>': 'Dragon Ball Z NPC',
    '<:death_note:1088702980682956800>': 'Death Note NPC',
    ':u7a7a:': 'Crown Rift Awakening NPC',
    ':sa:': 'Crown Rift Slayers NPC',
    ':m:': 'Crown Rift Madness NPC',
    '<:persona:1090238487028047913>': 'Persona NPC',
    '<:yusuke:1088702663861993503>': 'YuYu Hakusho NPC',
    '<:one_piece:1088702665581670451>': 'One Piece NPC',
    '<:overlord:1091223691729305681>': 'Overlord NPC',
    '<:FairyTail:1091223690445865062>': 'Fairy Tail NPC',
    '<:slime:1091223689007210517>': 'Slime NPC',
    '<:souleater:1257056890832031756>': 'Soul Eater NPC',
    '<:killlakill:1214431376070410281>': 'Kill La Kill NPC',
    '<:gurren:1214432235927773205>': 'Gurren Lagann NPC',
    '<:jjk:1249819520650969138>': 'Jujutsu Kaisen NPC',
    '<:reborn:1257057934634909817>': 'Katekyo Hitman Reborn NPC',
    '<:fma:1256672084327792730>': 'Full Metal Alchemist NPC',
}

rpg_npc_emojis = [
    '<:mha:1088699056420835419>',
    '<:3873_league_of_legends_logo:1088701143921729567>',
    '<:pokemon:1088966251541450752>',
    '<:naruto_103:1088703639973015573>',
    '<:bleach:1088701142487285781>',
    '<:kratos:1088701141753274408>',
    '<:denji:1088701139886817311>',
    '<:pngaaa:1085072765587030027>',
    '<:Black_Clover:1088699058262114314>',
    '<:Demon_Slayer:1088702009709973565>',
    '<:AOT:1088702007717658674>',
    '<:7ds:1088702006581006377>',
    '<:digimon_sparkle:1088702667703988316>',
    '<:fate:1092176982277632032>',
    '<:jin:1090240014891352114>',
    '<:dark_souls_icon:1088702666688966726>',
    '<:dbz:1088698675338952774>',
    '<:death_note:1088702980682956800>',
    '<:persona:1090238487028047913>',
    '<:yusuke:1088702663861993503>',
    '<:one_piece:1088702665581670451>',
    '<:overlord:1091223691729305681>',
    '<:FairyTail:1091223690445865062>',
    '<:slime:1091223689007210517>',
    '<:souleater:1257056890832031756>',
    '<:killlakill:1214431376070410281>',
    '<:gurren:1214432235927773205>',
    '<:jjk:1249819520650969138>',
    '<:reborn:1257057934634909817>',
    '<:fma:1256672084327792730>',
]


scenario_level_config = 1499


EASY_BLOCKED = ['CDungeon', 'DDungeon', 'Dungeon', 'ADungeon', 'Boss', 'CBoss', 'Abyss', 'PVP', 'EXPLORE']

BASIC_ATTACK = "BASIC"
SPECIAL_ATTACK = "SUPER"
ULTIMATE_ATTACK = "ULTIMATE"
ABILITY_ARMS = ['BASIC', 'SUPER', 'ULTIMATE', 'SPECIAL']

LOW_TIER_CARDS = [1, 2, 3]
MID_TIER_CARDS = [4, 5, 6, 7]
HIGH_TIER_CARDS = [8, 9, 10]

NOT_SAVE_MODES = ['Boss', 'CBoss', 'PVP', 'Abyss', 'SCENARIO', 'EXPLORE', 'RAID', 'RPG']
BATTLE_OPTIONS = [1, 2, 3, 4, 5, 0]

tactics = [
    'ENRAGE',
    'OVERWHELMING POWER',
    'DAMAGE CHECK',
    'DEVASTATING BLOW',
    'DEATH BLOW',
    'ALMIGHTY WILL',
    'STAGGER',
    'PROVOKED',
    'INTIMIDATION',
    'PETRIFIED FEAR',
    'BLOODLUST'
]


class_emojis = {
    'TANK': '<:NewUI_Class_Guardian:1085080855174725682>',
    'HEALER': '<:healer40:1085069588015874058>',
    'FIGHTER': '<:NewUI_Class_Warrior:1085080858358198323>',
    'ASSASSIN': '<:NewUI_Class_Assassin:1085080857225728020>',
    'MAGE': '<:NewUI_Class_Mage:1085070773007421451>',
    'RANGER': '<:NewUI_Class_Hunter:1085081189708210196>',
    'SUMMONER': '<:summon:1085347631108194314>',
    'SWORDSMAN': '<:Gold_Sword:1085347570282405958>',
    'MONSTROSITY': '<:monster:1085347567384154172>',
    'TACTICIAN': '<:Tactician:1085080853882884126>'
}

utility_emojis = {
    'OFF': '<:toggle_off:1085611427143897088>',
    'ON': '<:toggle_on:1085611434207105115>'
}

class_descriptions = {
    'SUMMONER': f"{class_emojis['SUMMONER']} *Summoners can use their summons from the start of battle instead of waiting to resolve. Summons deal bonus damaged based on card Tier*",
    'ASSASSIN': f"{class_emojis['ASSASSIN']} *Assassins have the ability to attack without using stamina at the beginning of the match with increase Crit Chance ignoring enemy protections.This class effect varies based on card tier. Increase Bleed, Poison and Death DMG*",
    'FIGHTER': f"{class_emojis['FIGHTER']} *Fighters start each fight with up to 7 parries. This class effect varies based on card tier. On physical damage proc, fighters gain 2 parries instead of 1.*",
    'RANGER': f"{class_emojis['RANGER']} *Rangers start each fight with up to 6 barriers. This class effect varies based on card tier. Rangers can attack through barriers.*",
    'TANK': f"{class_emojis['TANK']} *Tanks start each fight with up to 2500+ base Shield. This class effect varies based on card tier and level. Tanks gain the same shield amount on resolve and Tripled Defense on Block*",
    'SWORDSMAN': f"{class_emojis['SWORDSMAN']} *Swordsmen gain up to 6 critical strikes on resolve. This class effect varies based on card tier. Sword & Bleed damage is boosted for the swordsman class.*",
    'MONSTROSITY': f"{class_emojis['MONSTROSITY']} *Monstrosities gain up to 5 double strikes on resolve. This class effect varies based on card tier.*",
    'MAGE': f"{class_emojis['MAGE']} *Mages increase elemental damage up to 60%. This class effect varies based on card tier. Elemental effects are greatly boosted.*",
    'HEALER': f"{class_emojis['HEALER']} *Healers store up to 70% of the damage taken and heal for the total amount each focus. This class effect varies based on card tier. Lifesteal abilities are boosted for the healer class and they Remove stacked effects on focus [Bleed, Poison, Rot]*",
    'TACTICIAN': f"{class_emojis['TACTICIAN']} *Enter Focus using Block to craft Strategy Points.1- Enhance Protections, 2 - Sabotage Talisman, 3 - Enhance Talisman,4 - Sabotage Protections,5 - The Ultimate Strategy!*" 
   }

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
IMAGE_CACHE = {}

# Tactics dictionary with explanations
tactics_explanations = {
    "ENRAGE": "When the opponent's health drops below 60% of its base maximum health, it gains a boost to its stats.",
    "OVERWHELMING POWER": "Upon resolve, the opponent will parry all attacks for 10 - 15 turns.",
    "DAMAGE CHECK": "The opponent will skip its turn 5 times during the fight. If you fail to deal enough damage during those turns, you will lose the fight. This mechanic occurs when the opponent focuses 5 times.",
    "DEATH BLOW": "On turns 1, 30, 60, 90, 120, and 150, the opponent will unleash a devastating attack that destroys all of your protections, leaving you vulnerable to its attacks. If you had no protections to begin with, the attack will be fatal and you will lose the game.",
    "ALMIGHTY WILL": "The opponent has the ability to manipulate the turn order and their focus count by either increasing or decreasing the total number of turns. The exact effect is randomized and depends on the opponent.",
    "STAGGER": "When the opponent lands a critical hit, the opponent is staggered and loses their turn.",
    "INTIMIDATION": "The opponent has the ability to temporarily reduce the opponent's attack and defense stats to 0 for 3-10 turns.",
    "PETRIFIED FEAR": "At the start of the match, the opponent gains the ability to take 2 - 7 turns before you have a chance to act.",
    "REGENERATION": "At the start of turn 80, the opponent regenerates all of its health if it dies, fully restoring itself.",
    "BLOODLUST": "After the opponent's health drops below 75% of its base maximum health, it gains the ability to heal for 35% of the damage it deals for the remainder of the match.",
    "DEVASTATING BLOW": "The opponents strike will destroy all of your protections, leaving you vulnerable to its attacks.",
}


"""
A class to represent the various game modes available.
"""
# Co-op modes including tales, dungeons, and boss fights
CO_OP_M = ['CTales', 'DTales', 'CDungeon', 'DDungeon', 'CBoss']

# Duo modes including tales and dungeons
DUO_M = ['DTales', 'DDungeon']

# Auto battle modes including tales and dungeons
AUTO_BATTLE_M = ['ATales', 'ADungeon']

# Tale modes including auto, co-op, and duo tales
TALE_M = ['ATales', 'Tales', 'CTales', 'DTales']

# Dungeon modes including co-op, duo, and standard dungeons
DUNGEON_M = ['CDungeon', 'DDungeon', 'Dungeon', 'ADungeon']

# Boss modes including co-op and standard boss fights
BOSS_M = ['Boss', 'CBoss']

# Player versus player mode
PVP_M = ['PVP']

# Solo modes including tales, dungeons, and boss fights
SOLO_M = ['ATales', 'Tales', 'Dungeon', 'Boss']
REG_MODES = ['Tales', 'Dungeon']

# Modes in which opponents can summon reinforcements
OPPONENT_SUMMON_M = ['Dungeon', 'DDungeon', 'CDungeon']

# Raid mode
RAID_M = ['Raid', 'RAID', 'Raid_Scenario']

# Abyss, scenario, and explore modes
ABYSS = "Abyss"
SCENARIO = "Scenario"
EXPLORE = "Explore"
TUTORIAL = "Tutorial"
RPG = "RPG"

ABYSS_REWARD_FLOORS = [10,20,30,40,50,60,70,80,90,100]

MAX_LEVEL = 3000



# Milestones

# Quests awared Gems
# Milestones award Gold and Gems


quest_list = [
    {
    "TYPE": "MARKETPLACE",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 50000,
    "COMPLETED": False,
    "NAME": "Add 1 Item to Marketplace",
    "MODE": "MARKETPLACE",
    "RANK": "D",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },{
    "TYPE": "TRADE",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 100000,
    "COMPLETED": False,
    "NAME": "Complete 1 Trade",
    "MODE": "TRADE",
    "RANK": "D",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },
    {
    "TYPE": "TALES",
    "AMOUNT": 0,
    "COMPLETE": 5,
    "REWARD": 100000,
    "COMPLETED": False,
    "NAME": "Complete 5 Tales Battles",
    "MODE": "TALES",
    "RANK": "C",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },
    {
    "TYPE": "SCENARIOS",
    "AMOUNT": 0,
    "COMPLETE": 2,
    "REWARD": 250000,
    "COMPLETED": False,
    "NAME": "Complete 2 Scenarios",
    "MODE": "SCENARIOS",
    "RANK": "C",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },
    {
    "TYPE": "DUNGEONS",
    "AMOUNT": 0,
    "COMPLETE": 5,
    "REWARD": 500000,
    "COMPLETED": False,
    "NAME": "Complete 5 Dungeon Battles",
    "MODE": "DUNGEONS",
    "RANK": "B",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },
    {
    "TYPE": "PVP",
    "AMOUNT": 0,
    "COMPLETE": 2,
    "REWARD": 500000,
    "COMPLETED": False,
    "NAME": "Complete 2 PVP Battles",
    "MODE": "PVP",
    "RANK": "B",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },{
    "TYPE": "FULL TALES",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 1000000,
    "COMPLETED": False,
    "NAME": "Copmlete a Full Tale",
    "MODE": "FULL TALES",
    "RANK": "A",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },
    {
    "TYPE": "FULL DUNGEONS",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 5000000,
    "COMPLETED": False,
    "NAME": "Complete a Full Dungeon",
    "MODE": "FULL DUNGEONS",
    "RANK": "A",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    },{
    "TYPE": "RAIDS",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 10000000,
    "COMPLETED": False,
    "NAME": "Complete a Raid",
    "MODE": "RAIDS",
    "RANK": "S",
    "QUEST_FLAG": True,
    "MILESTONE_FLAG": False,
    }
]

def health_color(health, max_health):
    if health / max_health >= 0.80:
        return 0x2ECC71
    elif health / max_health > 0.5:
        return 0xF1C40F
    elif health / max_health > 0.25:
        return 0xE67E22
    elif health / max_health > 0.15:
        return 0xE74C3C
    else:
        return 0xE74C3C

colors = {
    'gold': 0xFFD700,
    'green': 0x2ECC71,
    'yellow': 0xF1C40F,
    'orange': 0xE67E22,
    'red': 0xE74C3C
}