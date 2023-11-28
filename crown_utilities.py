import db
# import bot as main
from cachetools import cached, LRUCache, TTLCache
from cogs.classes.card_class import Card
from cogs.classes.arm_class import Arm
from cogs.classes.title_class import Title
from cogs.classes.player_class import Player
from cogs.classes.summon_class import Summon
import time
import destiny as d
import classes as data
from PIL import Image, ImageFont, ImageDraw
import textwrap
from io import BytesIO
from pilmoji import Pilmoji
import textwrap
now = time.asctime()
import random
import requests
import interactions 
import custom_logging
cache = TTLCache(maxsize=1000, ttl=87400)
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

print("Crown Utilities initiated")


@cached(cache)
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
            lvl_req = int(summon_lvl) * 10
            if lvl_req <= 0:
                lvl_req = 2
            
            power = (summon_bond * summon_lvl) + int(summon_ability_power)
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
        lvl_req = player_card.summon_lvl * 10
        if lvl_req <= 0:
            lvl_req = 2
        bond_req = ((player_card.summon_power * 5) * (player_card.summon_bond + 1))
        if bond_req <= 0:
            bond_req = 5
        summon_type = player_card.summon_type


        if player_card.summon_lvl < 10:
            # Non Level Up Code
            if player_card.summon_exp < (lvl_req - 1):
                update_query = {'$inc': {'PETS.$[type].' + "EXP": xp_inc}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)

            # Level Up Code
            if player_card.summon_exp >= (lvl_req):
                update_query = {'$set': {'PETS.$[type].' + "EXP": 0}, '$inc': {'PETS.$[type].' + "LVL": 1}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)

        if player_card.summon_bond < 3:
            # Non Bond Level Up Code
            if player_card.summon_bondexp < (bond_req - 1):
                update_query = {'$inc': {'PETS.$[type].' + "BONDEXP": bxp_inc}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)

            # Bond Level Up Code
            if player_card.summon_bondexp >= (bond_req - 1):
                update_query = {'$set': {'PETS.$[type].' + "BONDEXP": 0}, '$inc': {'PETS.$[type].' + "BOND": 1}}
                filter_query = [{'type.' + "NAME": str(player_card.summon_name)}]
                response = db.updateUser(query, update_query, filter_query)
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
    if element == "ENERGY" or element == "SPIRIT":
        emoji = "🧿"
    if element == "BLEED":
        emoji = "🅱️"
    if element == "RECKLESS":
        emoji = "♻️"
    if element == "TIME":
        emoji = "⌛"
    if element == "GRAVITY":
        emoji = "🪐"
    if element == "None" or element == "NULL":
        emoji = "📿"
    if element == "SHIELD":
        emoji = "🛡️"
    if element == "PARRY":
        emoji = "🔄"
    if element == "BARRIER":
        emoji = "💠"
    
        
    return emoji


def getTime(hgame, mgame, sgame, hnow, mnow, snow):
    hoursPassed = hnow - hgame
    minutesPassed = mnow - mgame
    secondsPassed = snow - sgame
    if hoursPassed > 0:
        minutesPassed = mnow
        if minutesPassed > 0:
            secondsPassed = snow
        else:
            secondsPassed = snow - sgame
    else:
        minutesPassed = mnow - mgame
        if minutesPassed > 0:
            secondsPassed = snow
        else:
            secondsPassed = snow - sgame
    gameTime = str(hoursPassed) + str(minutesPassed) + str(secondsPassed)
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
            font = moveset_font
            width, height = font.getsize(line)
            x_position = round((1730 - width) / 2)
            pilmoji.text((x_position, y_text), line, (255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
            y_text += height


        image_binary = BytesIO()
        im.save(image_binary, "PNG")
        return image_binary

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
    try:
        player = create_player_from_data(db.queryUser({'DID': str(user.id)}))
        card = create_card_from_data(db.queryCard({'NAME': player.equipped_card}))
        guild_buff = await guild_buff_update_function(player.guild.lower())
        arm = create_arm_from_data(db.queryArm({'ARM': player.equipped_arm}))
        title = create_title_from_data(db.queryTitle({'TITLE': player.equipped_title}))
        card.set_card_level_buffs(player.card_levels)
        has_universe_heart, has_universe_soul = get_level_boosters(player, card)
        exp_gain, lvl_req = get_exp_gain(player, mode, card, has_universe_soul, extra_exp)

        if player.difficulty == "EASY":
            return

        number_of_level_ups, card = await update_experience(card, player, exp_gain, lvl_req)

        if number_of_level_ups > 0:
            print(f"Card {card.name} leveled up {str(number_of_level_ups)} times!")
            lvl_req = get_level_up_exp_req(card)
            embed = Embed(title=f"🎴 **{card.name}** leveled up {str(number_of_level_ups)} times!", color=0x00ff00)
            embed.set_footer(text=f"{lvl_req} EXP to next level")
            embed.set_image(url="attachment://image.png")
            image_binary = card.showcard()
            image_binary.seek(0)
            card_file = File(file_name="image.png", file=image_binary)
            await user.send(embed=embed, file=card_file)
            image_binary.close()
            return
        else:
            return
    except Exception as ex:
        custom_logging.debug(ex)
        await user.send("Issue with leveling up card")
        return


# if card.card_lvl < 500 and card.card_lvl >= 200:
#     if guild_buff:
#         if guild_buff['Level']:
#             exp_gain = round(lvl_req)
#             update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])
# elif card.card_lvl < 700 and card.card_lvl >= 500:
#     if guild_buff:
#         if guild_buff['Level']:
#             exp_gain = round(lvl_req/2)
#             update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])
            
# elif card.card_lvl < 1000 and card.card_lvl >= 700:
#     if guild_buff:
#         if guild_buff['Level']:
#             exp_gain = round(lvl_req/3)
#             update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])


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
    number_of_level_ups = 0
    exp_gain = exp
    while exp_gain >= 0:
        atk_def_buff, ap_buff, hlt_buff = get_buffs(card.card_lvl, level_sync)
        if card.card_lvl < 200 or (200 < card.card_lvl < 1000):
            # Experience Code
            if exp_gain <= (lvl_req - 1):
                update_query = {'$inc': {'CARD_LEVELS.$[type].' + "EXP": exp_gain}}
                filter_query = [{'type.' + "CARD": card.name}]
                response = db.updateUser(player.user_query, update_query, filter_query)
                break
                
            # Level Up Code
            if exp_gain >= (lvl_req - exp_gain):
                atk_def_buff, ap_buff, hlt_buff = get_buffs(card.card_lvl, level_sync)
                update_query = {'$set': {'CARD_LEVELS.$[type].' + "EXP": 0},
                                '$inc': {'CARD_LEVELS.$[type].' + "LVL": 1, 'CARD_LEVELS.$[type].' + "ATK": atk_def_buff,
                                         'CARD_LEVELS.$[type].' + "DEF": atk_def_buff,
                                         'CARD_LEVELS.$[type].' + "AP": ap_buff, 'CARD_LEVELS.$[type].' + "HLT": hlt_buff}}
                filter_query = [{'type.' + "CARD": card.name}]
                response = db.updateUser(player.user_query, update_query, filter_query)
                exp_gain = exp_gain - lvl_req
                number_of_level_ups += 1
                card.card_lvl += 1
                lvl_req = get_level_up_exp_req(card)
                print(f"New Level Required - {lvl_req}")

    return number_of_level_ups, card


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


def get_exp_gain(player, mode, card, has_universe_soul, extra_exp):
    lvl_req = get_level_up_exp_req(card)
    exp_gain = 0
    t_exp_gain = 100 + (player.rebirth) + player.prestige_buff
    d_exp_gain = ((5000 + player.prestige_buff) * (1 + player.rebirth))
    b_exp_gain = 500000 + ((100 + player.prestige_buff) * (1 + player.rebirth))
    if has_universe_soul:
        if mode in DUNGEON_M:
            exp_gain = (d_exp_gain * 5) + extra_exp
        elif mode in TALE_M:
            exp_gain = (t_exp_gain * 5) + extra_exp
        elif mode in BOSS_M:
            exp_gain = (b_exp_gain * 5) + extra_exp
        else:
            exp_gain = extra_exp
    else:
        if mode in DUNGEON_M:
            exp_gain = d_exp_gain + extra_exp
        elif mode in TALE_M:
            exp_gain = t_exp_gain + extra_exp
        elif mode in BOSS_M:
            exp_gain = b_exp_gain + extra_exp
        else:
            exp_gain = extra_exp

    if mode == "Purchase":
        exp_gain = lvl_req + 100 + extra_exp

    print(f"Extra Exp: {extra_exp}")
    print(f"Exp Gain: {exp_gain} | Level Req: {lvl_req}")

    return exp_gain, lvl_req


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
    valid = db.queryUser(query)
    if valid:
        return valid
    else:
        await ctx.send(f"{ctx.author.mention}, you must register using /register to play Anime VS+.")
        return False


def scenario_gold_drop(scenario_lvl, fight_count, scenario_title, completed_scenarios, difficulty):
    gold = scenario_lvl * (500 * fight_count)
    if difficulty == "HARD":
        gold = gold * 2

    if scenario_lvl > 500:
        gold = gold + (gold * .25)

    if scenario_lvl > 900:
        gold = gold + (gold * .35)

    if scenario_lvl > 1500:
        gold = gold + (gold * .45)
    
    if scenario_lvl > 2500:
        gold = gold + (gold * .60)
    
    if scenario_lvl > 3500:
        gold = gold + (gold * .75)
    
    if scenario_title in completed_scenarios:
        gold = gold * 0.3
    
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
        for e in essence_list:
            if e["ELEMENT"] == element:
                essence = e["ESSENCE"]

        for t in talisman_list:
            if t["TYPE"] == element.upper():
                talisman_exists = True

        
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
                '$addToSet': {
                    "TALISMANS": {
                        "TYPE": element.upper(),
                        "DUR": 30
                    }
                }
            }
        tresponse = db.updateUserNoFilter(query, talisman_query)
        msg = f"You have successfully attuned a {set_emoji(element)} {element.title()} Talisman!"
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
    card = Card(card_data['NAME'], card_data['PATH'], card_data['PRICE'], card_data['AVAILABLE'], card_data['SKIN_FOR'], card_data['HLT'], card_data['HLT'], card_data['STAM'], card_data['STAM'], card_data['MOVESET'], card_data['ATK'], card_data['DEF'], card_data['TYPE'], card_data['PASS'][0], card_data['SPD'], card_data['UNIVERSE'], card_data['TIER'], card_data['WEAKNESS'], card_data['RESISTANT'], card_data['REPEL'], card_data['ABSORB'], card_data['IMMUNE'], card_data['GIF'], card_data['FPATH'], card_data['RNAME'], card_data['RPATH'], is_boss, card_data['CLASS'], card_data['DROP_STYLE'])
    return card

def create_title_from_data(title_data):
    title = Title(title_data['TITLE'], title_data['UNIVERSE'], title_data['ABILITIES'], title_data['RARITY'], title_data['UNLOCK_METHOD'], title_data['AVAILABLE'], title_data['ID'])
    return title

def create_arm_from_data(arm_data):
    arm = Arm(arm_data['ARM'], arm_data['UNIVERSE'], arm_data['PRICE'], arm_data['ABILITIES'], arm_data['DROP_STYLE'], arm_data['AVAILABLE'], arm_data['ELEMENT'])
    return arm

def create_player_from_data(player_data):
    player = Player(player_data['AUTOSAVE'], player_data['AVAILABLE'], player_data['DISNAME'], player_data['DID'], player_data['AVATAR'], player_data['GUILD'], player_data['TEAM'], player_data['FAMILY'], player_data['TITLE'], player_data['CARD'], player_data['ARM'], player_data['PET'], player_data['TALISMAN'], player_data['CROWN_TALES'], player_data['DUNGEONS'], player_data['BOSS_WINS'], player_data['RIFT'], player_data['REBIRTH'], player_data['LEVEL'], player_data['EXPLORE'], player_data['SAVE_SPOT'], player_data['PERFORMANCE'], player_data['TRADING'], player_data['BOSS_FOUGHT'], player_data['DIFFICULTY'], player_data['STORAGE_TYPE'], player_data['USED_CODES'], player_data['BATTLE_HISTORY'], player_data['PVP_WINS'], player_data['PVP_LOSS'], player_data['RETRIES'], player_data['PRESTIGE'], player_data['PATRON'], player_data['FAMILY_PET'], player_data['EXPLORE_LOCATION'], player_data['SCENARIO_HISTORY'], player_data['BALANCE'], player_data['CARDS'], player_data['TITLES'], player_data['ARMS'], player_data['PETS'], player_data['DECK'], player_data['CARD_LEVELS'], player_data['QUESTS'], player_data['DESTINY'], player_data['GEMS'], player_data['STORAGE'], player_data['TALISMANS'], player_data['ESSENCE'], player_data['TSTORAGE'], player_data['ASTORAGE'], player_data['U_PRESET'])
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
        arm_price = player_arm.price
        card = player_card

        # Check if the difficulty is easy, return if so
        if player.difficulty == "EASY":
            return

        # Set arm universe to card universe if it is part of the pokemon universes
        if player_card.universe in pokemon_universes and player_arm.universe in pokemon_universes:
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

    return turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm


def get_trade_eligibility(trader, trade_player):
    if trader.level < 11 and trader.prestige == 0:
        return "🔓 Unlock Trading by completeing Floor 10 of the 🌑 Abyss! Use /solo to enter the abyss."

    if trade_player.level < 11 and trade_player.prestige == 0:
        return f"🔓 <@{trade_player.did}> has not unlocked Trading by completing Floor 10 of the 🌑."
    
    return False


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
    'STANCE': '% each turn',
    'CONFUSE': '% each turn',
    'CREATION': '% each turn',
    'DESTRUCTION': '% each turn',
    'SPEED': '% each focus',
    'SLOW': ' Turn',
    'HASTE': ' Turn',
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
    'ELEMENTAL BUFF': 'elemental damage by 35%',
    'ELEMENTAL DEBUFF': 'elemental damage by 35%',
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
    'STRATEGIST': 'Hits through all guards',
    'SHARPSHOOTER': 'Attacks never miss',
    'DIVINITY': 'Ignore elemental effects until resolved',
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


enhancer_mapping = {
'ATK': 'Increase Attack %',
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
'GROWTH': 'Lose 10% Max Health, Increase Attack, Defense and AP',
'STANCE': 'Swap your Attack & Defense, Increase Defense',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your  Stamina, Increase Target Stamina',
'SLOW': 'Increase Opponent Stamina, Decrease Your Stamina then Swap Stamina with Opponent',
'HASTE': 'Increase your Stamina, Decrease Opponent Stamina then Swap Stamina with Opponent',
'FEAR': 'Lose 10% Max Health, Decrease Opponent Attack, Defense and AP',
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


title_enhancer_mapping = {
'ATK': 'Increase Attack',
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
'WATER': 'Each strike increases all water move AP by 100.',
'EARTH': 'Cannot be Parried. Increases Def by 25% AP. Grants Shield - Increase by 50% DMG',
'ELECTRIC': 'Add 35% DMG Dealt to Shock damage, added to all Move AP.',
'WIND': 'On Miss, Use Wind Attack, boosts all wind damage by 35% of damage dealt.',
'PSYCHIC': 'Penetrates Barriers. Reduce opponent ATK & DEF by 35% DMG. After 3 Hits gain a Barrier',
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
'GRAVITY': 'Disables Opponent Block, Reduce opponent DEF by 50% DMG, Decrease Turn Count By 3.',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
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
    "GRAVITY"
]


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
    {'name': 'ENERGY', 'value': 'ENERGY'},
    {'name': 'RANGED', 'value': 'RANGED'},
    {'name': 'RECKLESS', 'value': 'RECKLESS'},
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
]


class_mapping = {
'ASSASSIN' : 'First [1-3] Attack cost 0 Stamina',  
'FIGHTER' : 'Starts each fight with up to 3 additional Parries',
'MAGE' : 'Increases Elemental Damage up to 30%',
'TANK' : ' Starts each fight with 300 * Card Tier Shield',
'RANGER' : 'Starts each fight with up to 3 additional Barriers',
'SWORDSMAN' : 'On Resolve, Gain up to 3 Critical Strikes',
'SUMMONER' : 'Starts each fight with summons available',
'MONSTROSITY' : 'On Resolve, Gain up to 3 Double Strikes',
'HEALER' : 'Stores up to 35% Damage recieved and increases healing on focus by that amount'
}


pokemon_universes = ['Kanto Region', 'Johto Region','Hoenn Region','Sinnoh Region','Kalos Region','Alola Region','Galar Region']


crest_dict = { 'Unbound': '🉐',
              'My Hero Academia': '<:mha:1088699056420835419>',
              'League Of Legends': '<:3873_league_of_legends_logo:1088701143921729567>',
              'Kanto Region': '<:pokemon:1088966251541450752>',
              'Naruto': '<:naruto_103:1088703639973015573>',
              'Bleach': '<:bleach:1088701142487285781>',
              'God Of War': '<:kratos:1088701141753274408>',
              'Chainsawman': '<:denji:1088701139886817311>',
              'One Punch Man': '<:pngaaa:1085072765587030027>',
              'Johto Region': '<:johto:1090448443723501729>',
              'Black Clover': '<:Black_Clover:1088699058262114314>',
              'Demon Slayer': '<:Demon_Slayer:1088702009709973565>',
              'Attack On Titan': '<:AOT:1088702007717658674>',
              '7ds': '<:7ds:1088702006581006377>',
              'Hoenn Region': '<:hoenn:1090448753233756292>',
              'Digimon': '<:digimon_sparkle:1088702667703988316>',
              'Fate': '<:fate:1092176982277632032>',
              'Solo Leveling': '<:jin:1090240014891352114>',
              'Souls': '<:dark_souls_icon:1088702666688966726>',
              'Dragon Ball Z': '<:dbz:1088698675338952774>',
              'Sinnoh Region': '<:sinnoh:1090448834435481650>',
              'Death Note': '<:death_note:1088702980682956800>',
              'Crown Rift Awakening': ':u7a7a:',
              'Crown Rift Slayers': ':sa:',
              'Crown Rift Madness': ':m:',
              'Persona': '<:persona:1090238487028047913>',
              'YuYu Hakusho': '<:yusuke:1088702663861993503>',
              'One Piece': '<:one_piece:1088702665581670451>',
              'Overlord': '<:overlord:1091223691729305681>',
              'Fairy Tail': '<:FairyTail:1091223690445865062>',
              'That Time I Got Reincarnated as a Slime': '<:slime:1091223689007210517>'
}


EASY_BLOCKED = ['CDungeon', 'DDungeon', 'Dungeon', 'ADungeon', 'Boss', 'CBoss', 'Abyss', 'PVP', 'EXPLORE']

BASIC_ATTACK = "BASIC"
SPECIAL_ATTACK = "SUPER"
ULTIMATE_ATTACK = "ULTIMATE"
ABILITY_ARMS = ['BASIC', 'SUPER', 'ULTIMATE', 'SPECIAL']

LOW_TIER_CARDS = [1, 2, 3]
MID_TIER_CARDS = [4, 5]
HIGH_TIER_CARDS = [6, 7]

NOT_SAVE_MODES = ['Boss', 'CBoss', 'PVP', 'Abyss', 'SCENARIO', 'EXPLORE', 'RAID']
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
    'MONSTROSITY': '<:monster:1085347567384154172>'
}

utility_emojis = {
    'OFF': '<:toggle_off:1085611427143897088>',
    'ON': '<:toggle_on:1085611434207105115>'
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
RAID_M = ['Raid', 'RAID']

# Abyss, scenario, and explore modes
ABYSS = "Abyss"
SCENARIO = "Scenario"
EXPLORE = "Explore"
TUTORIAL = "Tutorial"

ABYSS_REWARD_FLOORS = [10,20,30,40,50,60,70,80,90,100]

quest_list = [
    {
    "TYPE": "TRADE",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 50000,
    "COMPLETED": False,
    "NAME": "Complete 1 Trade",
    "MODE": "TRADE",
    "RANK": "D",
    },
    {
    "TYPE": "MARKETPLACE",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 50000,
    "COMPLETED": False,
    "NAME": "Add 1 Item to Marketplace",
    "MODE": "MARKETPLACE",
    "RANK": "D",
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
    },
    {
    "TYPE": "SCENARIOS",
    "AMOUNT": 0,
    "COMPLETE": 2,
    "REWARD": 100000,
    "COMPLETED": False,
    "NAME": "Complete 2 Scenarios",
    "MODE": "SCENARIOS",
    "RANK": "C",
    },
    {
    "TYPE": "DUNGEONS",
    "AMOUNT": 0,
    "COMPLETE": 5,
    "REWARD": 300000,
    "COMPLETED": False,
    "NAME": "Complete 5 Dungeon Battles",
    "MODE": "DUNGEONS",
    "RANK": "B",
    },
    {
    "TYPE": "PVP",
    "AMOUNT": 0,
    "COMPLETE": 2,
    "REWARD": 300000,
    "COMPLETED": False,
    "NAME": "Complete 2 PVP Battles",
    "MODE": "PVP",
    "RANK": "B",
    },
    {
    "TYPE": "FULL DUNGEONS",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 2000000,
    "COMPLETED": False,
    "NAME": "Complete a Full Dungeon",
    "MODE": "FULL DUNGEONS",
    "RANK": "A",
    },
    {
    "TYPE": "FULL TALES",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 500000,
    "COMPLETED": False,
    "NAME": "Copmlete a Full Tale",
    "MODE": "FULL TALES",
    "RANK": "A",
    },
    {
    "TYPE": "RAIDS",
    "AMOUNT": 0,
    "COMPLETE": 1,
    "REWARD": 20000000,
    "COMPLETED": False,
    "NAME": "Complete a Raid",
    "MODE": "RAIDS",
    "RANK": "S",
    }
]


