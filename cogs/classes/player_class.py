from numpy import save
import db
import crown_utilities
import custom_logging
from interactions import Embed
import textwrap
from logger import loggy
import random
import uuid
from interactions import ActionRow, Button, ButtonStyle, Embed



class Player:
    def __init__(self, auto_save, available, disname, did, avatar, association, guild, family, equipped_title, equipped_card, equipped_arm, equipped_summon, equipped_talisman,completed_tales, completed_dungeons, boss_wins, rift, rebirth, level, explore, save_spot, performance, trading, boss_fought, difficulty, storage_type, used_codes, battle_history, pvp_wins, pvp_loss, retries, prestige, patron, family_pet, explore_location, scenario_history, balance, cards, titles, arms, summons, deck, card_levels, quests, destiny, gems, storage, talismans, essence, tstorage, astorage, u_preset, rpg_levels):
        self.disname = disname
        self.is_available = available
        self.did = did
        self.avatar = avatar
        self.association = association
        self.guild = guild
        self.family = family
        self.equipped_title = equipped_title
        self.equipped_card = equipped_card
        self.equipped_arm = equipped_arm
        self.equipped_summon = equipped_summon
        self.equipped_talisman = equipped_talisman
        self.completed_tales = completed_tales
        self.completed_dungeons = completed_dungeons
        self.boss_wins = boss_wins
        self.rift = rift
        self.rebirth = rebirth
        self.rebirthBonus = rebirth * 10
        self.level = level
        self.explore = explore
        self.save_spot = save_spot
        self.performance = performance
        self.trading = trading
        self.boss_fought = boss_fought
        self.difficulty = difficulty
        self.storage_type = storage_type
        self.used_codes = used_codes
        self.battle_history = battle_history
        self.pvp_wins = pvp_wins
        self.pvp_loss = pvp_loss
        self.retries = retries
        self.prestige = prestige
        self.prestige_buff = prestige * 10
        self.patron = patron
        self.family_pet = family_pet
        self._is_locked_feature = False
        self._locked_feature_message = ""
        self.explore_location = explore_location
        self.autosave = auto_save
        self.scenario_history = scenario_history
        self.balance = balance
        self.cards = cards
        self.titles = titles
        self.arms = arms
        self.summons = summons
        self.deck = deck
        self.card_levels = card_levels
        self.rpg_levels = rpg_levels
        self.quests = quests
        self.destiny = destiny
        self.gems = gems
        self.storage = storage
        self.talismans = talismans
        self.essence = essence
        self.tstorage = tstorage
        self.astorage = astorage
        self.cards_length = len(self.cards)
        self.titles_length = len(self.titles)
        self.arms_length = len(self.arms)
        self.summons_length = len(self.summons)
        self.storage_length = len(self.storage)
        self.tstorage_length = len(self.tstorage)
        self.astorage_length = len(self.astorage)
        self.card_storage_full = self.cards_length == (self.storage_length * self.storage_type)
        self.storage_pricing = (self.storage_type + 1) * 1500000
        self.storage_pricing_text = f"{'{:,}'.format(self.storage_pricing)}"
        self.storage_tier_message = (self.storage_type + 1) 
        self.preset_upgraded = u_preset
        self.storage_message = f"{str(self.storage_type + 1)}"
        if self.storage_type >=10:
            self.storage_pricing_text = "Max Storage Level"
            self.storage_tier_message = "MAX"
            self.storage_message = "MAX"


        self.talisman_message = "📿 No Talisman Equipped"
        self.summon_power_message = ""
        self.summon_lvl_message = ""
        self.rift_on = False
        self.auto_battle = False
        
        # Guild Config
        self._default_guild = ""
        self.guild_info = "" 
        self.guild_buff = ""
        self.guild_query = ""
        self.guild_buff_update_query = ""
        self.filter_query = ""

        # Association Config
        self.association_info = ""
        self.crestlist = ""
        self.crestsearch = False
            
        self.deck_card = ""
        self.deck_title = ""
        self.deck_arm = ""
        self.decksummon = ""
        self.deck_talisman = ""

        self._equipped_card_data = ""
        self._equipped_title_data = ""
        self._equipped_arm_data = ""
        self._equipped_summon_data = ""
        self._equipped_summon_power = 0
        self._equipped_summon_bond = 0
        self._equipped_summon_bondexp = 0
        self._equipped_summon_exp = 0
        self._equipped_summon_lvl = 0
        self._equipped_summon_type = ""
        self._equipped_summon_name = ""
        self._equipped_summon_ability_name = ""
        self._equipped_summon_image = ""
        self._equipped_summon_universe = ""
        self.user_query = {'DID': str(self.did)}
        
        self._universe_buff_msg = ""

        if self.rift == 1:
            self.rift_on = True

        self.balance_icon = "🪙"

        if self.balance >= 50000000:
            self.balance_icon = "💸"
        elif self.balance >=10000000:
            self.balance_icon = "💰"
        elif self.balance >= 500000:
            self.balance_icon = "💵"

        self.prestige_icon = "🌑"
        if self.prestige == 1:
            self.prestige_icon = "🌒"
        elif self.prestige == 2:
            self.prestige_icon = "🌓"
        elif self.prestige == 3:
            self.prestige_icon = "🌔"
        elif self.prestige == 4:
            self.prestige_icon = "🌕"
        elif self.prestige == 5:
            self.prestige_icon = "🌖"
        elif self.prestige == 6:
            self.prestige_icon = "🌗"
        elif self.prestige == 7:
            self.prestige_icon = "🌘"
        elif self.prestige == 8:
            self.prestige_icon = "🌙"
        elif self.prestige == 9:
            self.prestige_icon = "👑"
        elif self.prestige >= 10:
            self.prestige_icon = "👹"

        self.rebirth_icon = "❤️‍🔥"
        if self.rebirth == 0:
            self.rebirth_icon = '🚩'
        elif self.rebirth >= 6:
            self.rebirth_icon = '👼'
        elif self.rebirth >= 10:
            self.rebirth_icon = '🧚‍♂️'
        else:
            self.rebirth_icon = '🧚‍♂️'
      
        self.rpg_atk_boost = False
        self.rpg_def_boost = False  
        self.rpg_hlt_boost = False



    def set_talisman_message(self):
        try:
            if self.equipped_talisman != "NULL":
                for t in self.talismans:
                    if t["TYPE"].upper() == self.equipped_talisman.upper():
                        talisman_emoji = crown_utilities.set_emoji(self.equipped_talisman.upper())
                        talisman_durability = t["DUR"]
                        self.talisman_message = f"{talisman_emoji} {self.equipped_talisman.title()} Talisman ⚒️{talisman_durability}"
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
            print("Error setting talisman message.")
            return self.talisman_message
        
    
    def get_family_summon(self):
        family_info = db.queryFamily({'HEAD':str(self.family)})
        summon_object = family_info['SUMMON']
        summon_name = summon_object['NAME']
        summon_ability_power = list(summon_object.values())[3]
        summon_ability = list(summon_object.keys())[3]
        summon_type = summon_object['TYPE']
        summon_lvl = summon_object['LVL']
        summon_exp = summon_object['EXP']
        summon_bond = summon_object['BOND']
        summon_bond_exp = summon_object['BONDEXP']
        bond_req = ((summon_ability_power * 5) * (summon_bond + 1))
        lvl_req = int(summon_lvl) * 10
        
        power = (summon_bond * summon_lvl) + int(summon_ability_power)
        summon_path = summon_object['PATH']
        return summon_object
    

    def get_new_essence_value_from_rewards(self, element, essence_value):
        new_value = 0

        for essence in self.essence:
            if essence['ELEMENT'] == element:
                new_value = essence['VALUE'] + essence_value
                return new_value

        if new_value == 0:
            new_value = essence_value
        
        return new_value



    
    def setsummon_messages(self):
        try:
            
            for summon in self.summons:
                if summon['NAME'] == self.equipped_summon:
                    activesummon = summon
            if self.family_pet:
                activesummon = self.get_family_summon()

            power = list(activesummon.values())[3]
            bond = activesummon['BOND']
            lvl = activesummon['LVL']
            s_type = activesummon['TYPE']
            self._equipped_summon_type = s_type
            if bond >= 10:
                bond_message = "🌟"
            else:
                bond_message = " "
            
            if lvl >= 10:
                lvl_message = "⭐"
            else:
                lvl_message = " "

            if s_type in ['BARRIER', 'PARRY']:
                if bond <= 3:
                    self._equipped_summon_power = power + bond
            else:    
                self._equipped_summon_power = ((1 + bond) * (lvl)) + ((1 + bond) * power)

            self.summon_power_message = f"{crown_utilities.set_emoji(s_type)} {s_type.title()} Damage: {self._equipped_summon_power}"


            self.summon_lvl_message = f"Bond {bond_message}{str(bond)} & Level {lvl_message}{str(lvl)}"

        except:
            print("Error setting summon message")
            return "Error"

    
    def set_explore(self, universe):
        
        # if self.level < 25 and self.prestige == 0:             
        #     return "🔓 Unlock the Explore Mode by completing Floor 25 of the 🌑 Abyss! Use **Abyss** in /solo to enter the abyss."
        
        if universe.lower() == "all":
            db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'EXPLORE': True, 'EXPLORE_LOCATION': 'NULL'}})
            return f"🌌 | Exploring **All universes!**"

        universe_selected = db.queryUniverse({"TITLE": {"$regex": f"^{universe}$", "$options": "i"}})

        if universe_selected:
            db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'EXPLORE': True, 'EXPLORE_LOCATION': universe_selected['TITLE']}})
            return f"🌌 | You are Exploring **{universe_selected['TITLE']}**"

    
    def save_scenario(self, scenario):
        if not scenario in self.scenario_history:
            db.updateUserNoFilter({'DID': str(self.did)}, {'$addToSet': {'SCENARIO_HISTORY': scenario}})
            return f"\nScenario saved: {scenario}"
        else:
            return "Scenario already saved."
        
    
    def save_rpg_levels(self):
        # Add error handling later
        loggy.info(f"Saving RPG levels for {self.disname}")
        db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'RPG_LEVELS': self.rpg_levels}})
        return True
    

    def inc_rpg_level(self, universe):
        # This method is called when a player levels up in an RPG universe
        for rpg in self.rpg_levels:
            if rpg['UNIVERSE'] == universe:
                rpg['LEVEL'] += 1
                
        # Now save the updated RPG levels
        self.save_rpg_levels()
    
    async def set_guild_data(self):
        if self.guild != "PCG":
            self.guild_info = db.queryTeam({'TEAM_NAME': self.guild.lower()})
            self.guild_buff = await crown_utilities.guild_buff_update_function(self.guild)
            if self.guild_buff:
                if self.guild_buff['Rift'] is True:
                    self.rift_on = True
                    self.guild_query = self.guild_buff['QUERY']
                    self.guild_buff_update_query = self.guild_buff['UPDATE_QUERY']
                    self.filter_query = self.guild_buff['FILTER_QUERY']
                

            if self.association != "PCG":
                self.association_info = db.queryGuildAlt({'GNAME': self.association})
                if self.association_info:
                    self.crestlist = self.association_info['CREST']
                    self.crestsearch = True


    def set_auto_battle_on(self, mode):
        if self.patron != True and mode in crown_utilities.AUTO_BATTLE_M:
            self.auto_battle = True
        return self.auto_battle


    async def set_guild_buff(self):
        guild_buff = await crown_utilities.guild_buff_update_function(self.guild.lower())
        if guild_buff['Auto Battle']:
            self.auto_battle = True
            update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])


    def save_gems(self, universe_title, amount):
        current_gems = 0
        if self.gems:
            for gems in self.gems:
                if universe_title == gems['UNIVERSE']:
                    current_gems = gems['GEMS']

        if current_gems:
            update_query = {'$inc': {'GEMS.$[type].' + "GEMS": amount}}
            filter_query = [{'type.' + "UNIVERSE": universe_title}]
            response = db.updateUser(self.user_query, update_query, filter_query)
            return True
        else:
            gem_info = {'UNIVERSE': universe_title, 'GEMS' : amount, 'UNIVERSE_HEART' : False, 'UNIVERSE_SOUL' : False}
            response = db.updateUserNoFilter(self.user_query, {'$addToSet' : {'GEMS': gem_info }})
            return True


    def remove_gems(self, universe_title, amount):
        current_gems = 0
        for gems in self.gems:
            if universe_title == gems['UNIVERSE']:
                current_gems = gems['GEMS']

        negCurseAmount = 0 - abs(int(amount))

        if current_gems:
            update_query = {'$inc': {'GEMS.$[type].' + "GEMS": negCurseAmount}}
            filter_query = [{'type.' + "UNIVERSE": universe_title}]
            response = db.updateUser(self.user_query, update_query, filter_query)
            return True
        else:
            gem_info = {'UNIVERSE': universe_title, 'GEMS' : 5000, 'UNIVERSE_HEART' : False, 'UNIVERSE_SOUL' : False}
            response = db.updateUserNoFilter(self.user_query, {'$addToSet' : {'GEMS' :gem_info }})
            return True


    def save_card(self, card, rpg_mode =False):
        try:
            if len(self.cards) >= 80 and not rpg_mode:
                return "You have reached the maximum amount of cards in your inventory. Please remove a card to add a new one."
            if card.name in self.cards:
                if card.card_lvl > 1:
                    atk_def_buff = 0
                    ap_buff = 0
                    hlt_buff = 0
                    if (card.card_lvl + 1) % 2 == 0:
                        atk_def_buff = crown_utilities.level_sync["ATK_DEF"] or 2
                    if (card.card_lvl + 1) % 3 == 0:
                        ap_buff = crown_utilities.level_sync["AP"] or 2
                    if (card.card_lvl + 1) % 20 == 0:
                        hlt_buff = crown_utilities.level_sync["HLT"] or 10

                    update_query = {
                        '$set': {'CARD_LEVELS.$[type].EXP': 0},
                        '$inc': {
                            'CARD_LEVELS.$[type].LVL': card.card_lvl,
                            'CARD_LEVELS.$[type].ATK': atk_def_buff,
                            'CARD_LEVELS.$[type].DEF': atk_def_buff,
                            'CARD_LEVELS.$[type].AP': ap_buff,
                            'CARD_LEVELS.$[type].HLT': hlt_buff
                        }
                    }
                    filter_query = [{'type.CARD': str(card.name)}]
                    response = db.updateUser(self.user_query, update_query, filter_query)
                return f"Gained 1 Level for {card.name}."
            code = random.randint(1000000, 9999999)

            # First update: Push the card name to CARDS array
            db.updateUserNoFilter(self.user_query, {'$push': {'CARDS': card.name}})

            # Second update: Add card details to CARD_LEVELS array
            if rpg_mode:
                if len(self.cards) >= 80:
                    return "You have reached the maximum amount of cards in your inventory. Please remove a card to add a new one."
                lower = 10
                upper = 100
                tier = card.tier
                if self.difficulty == "HARD":
                    lowewr = 100
                    upper = 500
                    tier = card.tier + 1
                if self.difficulty == "EASY":
                    lowewr = 1
                    upper = 10
                random_lvl = random.randint(lower, upper)
                update_query = {
                    '$addToSet': {
                        'CARD_LEVELS': {
                            'CARD': card.name,
                            'LVL': random_lvl,
                            'TIER': tier,
                            'EXP': 0,
                            'ATK': 0,
                            'DEF': 0,
                            'AP': 0,
                            'HLT': 0,
                            'CLASS': card.card_class,
                            'ID': str(code)  # Convert UUID to string
                        }
                    }
                }
            else:
                update_query = {
                    '$addToSet': {
                        'CARD_LEVELS': {
                            'CARD': card.name,
                            'LVL': 1,
                            'TIER': card.tier,
                            'EXP': 0,
                            'ATK': 0,
                            'DEF': 0,
                            'AP': 0,
                            'HLT': 0,
                            'CLASS': card.card_class,
                            'ID': str(code)  # Convert UUID to string
                        }
                    },
                    '$set': {'CARD': card.name}
                }
            
            result = db.updateUserNoFilter(self.user_query, update_query)

            if card.card_lvl > 1:
                atk_def_buff = 0
                ap_buff = 0
                hlt_buff = 0
                if (card.card_lvl + 1) % 2 == 0:
                    atk_def_buff = crown_utilities.level_sync["ATK_DEF"] or 2
                if (card.card_lvl + 1) % 3 == 0:
                    ap_buff = crown_utilities.level_sync["AP"] or 2
                if (card.card_lvl + 1) % 20 == 0:
                    hlt_buff = crown_utilities.level_sync["HLT"] or 10

                update_query = {
                    '$set': {'CARD_LEVELS.$[type].EXP': 0},
                    '$inc': {
                        'CARD_LEVELS.$[type].LVL': card.card_lvl,
                        'CARD_LEVELS.$[type].ATK': atk_def_buff,
                        'CARD_LEVELS.$[type].DEF': atk_def_buff,
                        'CARD_LEVELS.$[type].AP': ap_buff,
                        'CARD_LEVELS.$[type].HLT': hlt_buff
                    }
                }
                filter_query = [{'type.CARD': str(card.name)}]
                response = db.updateUser(self.user_query, update_query, filter_query)

            return True
        except Exception as ex:
            custom_logging.debug(ex)
            return False

    
    def remove_card(self, card):
        try:
            if card.name in self.cards:
                update_query = {'$pull': {'CARDS': card.name}}
                response = db.updateUserNoFilter(self.user_query, update_query)


            for card in self.card_levels:
                if card['ID'] == card.card_id:
                    update_query = {'$pull': {'CARD_LEVELS': card}}
                    response = db.updateUserNoFilter(self.user_query, update_query)


            if card.name in self.storage:
                update_query = {'$pull': {'STORAGE': card.name}}
                response = db.updateUserNoFilter(self.user_query, update_query)


            for deck in self.deck:
                if card.name == deck['CARD']:
                    update_query = {'$pull': {'DECK': deck}}
                    response = db.updateUserNoFilter(self.user_query, update_query)


            return True
        except Exception as ex:
            custom_logging.debug(ex)
            return False


    def save_title(self, universe, rpg_title_drop=None):
        titles = [x for x in db.queryAllTitles() if x['UNIVERSE'] == universe and x['TITLE'] not in self.titles]
        stats = db.query_stats_by_player(self.did)
        message = ""
        for title in titles:
            if title['UNLOCK_METHOD'] and title['AVAILABLE']:
                unlock_method = title['UNLOCK_METHOD']['METHOD']
                value = title['UNLOCK_METHOD']['VALUE']
                element = title['UNLOCK_METHOD'].get('ELEMENT', "N/A")
                # scenario_drop = title['UNLOCK_METHOD']['SCENARIO_DROP']
                tale_title_unlock_message = self.tales_title_unlock_check(stats, universe, unlock_method, value, title)
                dungeon_title_unlock_message = self.dungeon_title_unlock_check(stats, universe, unlock_method, value, title)
                boss_title_unlock_message = self.boss_title_unlock_check(stats, universe, unlock_method, value, title)
                elemental_damage_unlock_message = self.elemental_damage_unlock_check(unlock_method, stats, universe, value, title, element)
                if tale_title_unlock_message:
                    message += tale_title_unlock_message
                if dungeon_title_unlock_message:
                    message += dungeon_title_unlock_message
                if boss_title_unlock_message:
                    message += boss_title_unlock_message
                if elemental_damage_unlock_message:
                    message += elemental_damage_unlock_message
            if title['TITLE'] == rpg_title_drop and rpg_title_drop is not None:
                rpg_title_unlock_message = self.adventure_title_unlock_check(title, "RPG")
                if rpg_title_unlock_message:
                    message += rpg_title_unlock_message
                return message, True

        return message
    

    def adventure_title_unlock_check(self, title, mode):
        if mode == "RPG":
            update_query = {'$addToSet': {'TITLES': title['TITLE']}}
            response = db.updateUserNoFilter(self.user_query, update_query)
            message = f"🎗️ {title['TITLE']} Unlocked!\n"
        return message


    def tales_title_unlock_check(self, stats, universe, unlock_method, value, title):
        message = ""
        for tale in stats['TALES_STATS']:
            if tale['UNIVERSE'] == universe:
                if unlock_method == "TALES COMPLETED" and tale['TOTAL_CLEARS'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"
                
                if unlock_method == "TALES RUN" and tale['TOTAL_RUNS'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "HEALED IN TALES" and tale['DAMAGE_HEALED'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "DAMAGE TAKEN IN TALES" and tale['DAMAGE_TAKEN'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "DAMAGE DEALT IN TALES" and round(tale['DAMAGE_DEALT']) >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"
        return message


    def dungeon_title_unlock_check(self, stats, universe, unlock_method, value, title):
        message = ""
        for dungeon in stats.get('DUNGEON_STATS', []):
            if dungeon['UNIVERSE'] == universe:
                if unlock_method == "DUNGEONS COMPLETED" and dungeon['TOTAL_CLEARS'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"
                
                if unlock_method == "DUNGEONS RUN" and dungeon['TOTAL_RUNS'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "HEALED IN DUNGEONS" and dungeon['DAMAGE_HEALED'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "DAMAGE TAKEN IN DUNGEONS" and dungeon['DAMAGE_TAKEN'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "DAMAGE DEALT IN DUNGEONS" and dungeon['DAMAGE_DEALT'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"
        return message


    def boss_title_unlock_check(self, stats, universe, unlock_method, value, title):
        message = ""
        for boss in stats['BOSS_STATS']:
            if boss['UNIVERSE'] == universe:
                if unlock_method == "BOSSES COMPLETED" and boss['TOTAL_CLEARS'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"
                
                if unlock_method == "BOSSES RUN" and boss['TOTAL_RUNS'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "HEALED IN BOSSES" and boss['DAMAGE_HEALED'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "DAMAGE TAKEN IN BOSSES" and boss['DAMAGE_TAKEN'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"

                if unlock_method == "DAMAGE DEALT IN BOSSES" and boss['DAMAGE_DEALT'] >= value:
                    update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                    message = f"🎗️ {title['TITLE']} Unlocked!\n"


    def elemental_damage_unlock_check(self, unlock_method, stats, universe, value, title, element):
        message = " "
        if unlock_method == "ELEMENTAL DAMAGE DEALT" and element != "N/A":
            for elemental_damage in stats.get(f'{element}_DAMAGE_DONE', []):
                if elemental_damage['UNIVERSE'] == universe:
                    if elemental_damage['DAMAGE'] >= value:
                        update_query = {'$addToSet': {'TITLES': title['TITLE']}}
                        response = db.updateUserNoFilter(self.user_query, update_query)
                        message = f"🎗️ {title['TITLE']} Unlocked!\n"
        return message
    

    def save_arm(self, arm, rpg_mode =False):
        
        if rpg_mode:
            if len(self.arms) >= 80:
                return "You have reached the maximum amount of arms in your inventory. Please remove an arm to add a new one"
            for a in self.arms:
                if arm == a['ARM']:
                    return False
            random_number = random.randint(5, 100)
            
            update_query = {'$addToSet': {'ARMS': {"ARM": arm, "DUR": random_number}}}
            response = db.updateUserNoFilter(self.user_query, update_query)
            return random_number
        for a in self.arms:
            if arm.name == a['ARM']:
                return False
            
        if len(self.arms) >= 80:
            return "You have reached the maximum amount of arms in your inventory. Please remove an arm to add a new one."
        # for a in self.astorage:
        #     if arm.name == a['ARM']:
        #         return False
        
        # if self.arms_length == 25:
        #     if self.storage_length == 25:
        #         return False
        #     else:
        #         update_query = {'$addToSet': {'ASTORAGE': {"ARM": arm.name, "DUR": arm.durability}}}
        #         response = db.updateUserNoFilter(self.user_query, update_query)
        # else:
        if arm.durability == 0:
            arm.durability = 25
        update_query = {'$addToSet': {'ARMS': {"ARM": arm.name, "DUR": arm.durability}}}
        response = db.updateUserNoFilter(self.user_query, update_query)
    
    
    def remove_arm(self, arm_name):
        try:
            for arm in self.arms:
                if arm['ARM'] == arm_name:
                    update_query = {'$pull': {'ARMS': arm}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
            
            for arm in self.astorage:
                if arm['ARM'] == arm_name:
                    update_query = {'$pull': {'ASTORAGE': arm}}
                    response = db.updateUserNoFilter(self.user_query, update_query)

            return True
        except Exception as ex:
            print(ex)
            return False


    def save_summon(self, summon, rpg_mode =False):
        summon_list = []
        for s in self.summons:
            if summon.name == s['NAME']:
                summon_list.append(s['NAME'])
                return False
        for s in self.storage:
            if summon.name == s['NAME']:
                return False
            
        if len(summon_list) >= 80:
            return "You have reached the maximum amount of summons in your inventory. Please remove a summon to add a new one."


        update_query = {'$addToSet': {'PETS': {"NAME": summon.name, "LVL": summon.level, "EXP": summon.exp, summon.ability: summon.passive_value, "TYPE": summon.ability_type, "BOND": summon.bond, "BONDEXP": summon.bond_exp, "PATH": summon.path}}}
        response = db.updateUserNoFilter(self.user_query, update_query)
        return True


    def remove_summon(self, summon_name):
        try:
            for summon in self.summons:
                if summon['NAME'] == summon_name:
                    update_query = {'$pull': {'PETS': summon}}
                    response = db.updateUserNoFilter(self.user_query, update_query)
                
            for deck in self.deck:
                if summon_name == deck['PET']:
                    update_query = {'$pull': {'DECK': deck}}
                    response = db.updateUserNoFilter(self.user_query, update_query)

            return True
        except Exception as ex:
            print(ex)
            return False


    def get_locked_feature(self, mode):
        if self.difficulty == "EASY" and mode in crown_utilities.EASY_BLOCKED:
            self._locked_feature_message = "Dungeons, Boss, PVP, Expplore, and Abyss fights are unavailable on Easy Mode! Use /difficulty to change your difficulty setting."
            self._is_locked_feature = True
            return
        
        if self.level < 26 and mode == "EXPLORE":
            self._locked_feature_message = "Explore fights are blocked until level 26"
            self._is_locked_feature = True
            return True

        if mode in crown_utilities.DUNGEON_M and self.level < 41 and int(self.prestige) == 0:
            self._locked_feature_message = "🔓 Unlock **Dungeons** by completing **Floor 40** of the 🌑 **Abyss**! Use **Abyss** in /solo to enter the abyss."
            self._is_locked_feature = True
            return

        if mode in crown_utilities.BOSS_M and self.level < 61 and int(self.prestige) == 0:
            self._locked_feature_message = "🔓 Unlock **Boss Fights** by completing **Floor 60** of the 🌑 **Abyss**! Use **Abyss** in /solo to enter the abyss."
            self._is_locked_feature = True
            return

        if self.level < 4:
            self._locked_feature_message = f"🔓 Unlock **PVP** by completing **Floor 3** of the 🌑 Abyss! Use **Abyss** in /solo to enter the abyss."
            self._is_locked_feature = True
            return
            
        return self._is_locked_feature


    def make_available(self):
        try:
            db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'AVAILABLE': True}})
            self.is_available = True
            return True
        except:
            return False


    def make_unavailable(self):
        try:
            db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'AVAILABLE': False}})
            self.is_available = False
            return True
        except:
            return False
            

    def get_battle_ready(self):
        try:
            self._equip_deck_data()
            self._equip_player_data()
            self._equip_summon_data()
        except Exception as ex:
            custom_logging.debug(ex)


    def _equip_deck_data(self):
        if self.deck_card:
            self._equipped_card_data = self.deck_card
            self._equipped_title_data = self.deck_title
            self._equipped_arm_data = self.deck_arm
            self.equipped_summon = self.decksummon['PET']
            self.equipped_talisman = self.deck_talisman
        else:
            return


    def _equip_player_data(self):
        if not self.deck_card:
            self._equipped_card_data = db.queryCard({'NAME': self.equipped_card})
            self._equipped_title_data = db.queryTitle({'TITLE': self.equipped_title})
            self._equipped_arm_data = db.queryArm({'ARM': self.equipped_arm})
        else:
            return


    def _equip_summon_data(self):
        if self.family_pet:
            summon_object = self.get_family_summon()
            attribute_name, power = self._get_summon_attribute_and_power(summon_object)
            self._assign_summon_attributes(summon_object, attribute_name, power)
        else:
            activesummon = self._get_active_summon()
            self._assign_summon_attributes(activesummon, "", 0)


    def _get_summon_attribute_and_power(self, summon_object):
        attributes = {key: val for key, val in summon_object.items() if key not in ["NAME", "LVL", "EXP", "TYPE", "BOND", "BONDEXP", "PATH"]}
        # Assuming there's only one other attribute and power, but adapt if needed
        attribute_name, power = next(iter(attributes.items()))
        return attribute_name, power


    def _get_active_summon(self):
        for summon in self.summons:
            if summon['NAME'] == self.equipped_summon:
                return summon
        raise ValueError(f"Summon {self.equipped_summon} not found in summons")


    def _assign_summon_attributes(self, summon_object, ability_name, power):
        common_attributes = ['BOND', 'BONDEXP', 'LVL', 'TYPE', 'NAME', 'PATH', 'EXP']

        for attr in common_attributes:
            setattr(self, f'_equipped_summon_{attr.lower()}', summon_object[attr])
        setattr(self, '_equipped_summon_ability_name', ability_name)
        setattr(self, '_equipped_summon_power', list(summon_object.values())[3])
        setattr(self, '_equipped_summon_image', summon_object['PATH'])
        setattr(self, '_equipped_summon_universe', db.querySummon({'PET': summon_object['NAME']})['UNIVERSE'])


    def getsummon_ready(self, _card):
        _card.summon_ability_name = self._equipped_summon_ability_name
        _card.summon_power = self._equipped_summon_power
        _card.base_summon_power = self._equipped_summon_power
        _card.summon_lvl = self._equipped_summon_lvl
        _card.summon_type = self._equipped_summon_type
        _card.summon_emoji = crown_utilities.set_emoji(self._equipped_summon_type)
        _card.summon_bond = self._equipped_summon_bond
        _card.summon_bondexp = self._equipped_summon_bondexp
        _card.summon_exp = self._equipped_summon_exp
        _card.summon_name = self._equipped_summon_name
        _card.summon_image = self._equipped_summon_image
        _card.summon_universe = self._equipped_summon_universe
        
    

    def get_talisman_ready(self, card):
        if self.equipped_talisman:
            card._talisman = self.equipped_talisman
        else:
            card._talisman = "None"

        if self.equipped_talisman == "NULL":
            card._talisman = "None"


    def has_storage(self):
        if self.storage:
            return True
        else:
            return False


    def set_deck_config(self, selected_deck):
        try:
            active_deck = self.deck[selected_deck]
            self.deck_card = db.queryCard({'NAME': str(active_deck['CARD'])})
            self.deck_title = db.queryTitle({'TITLE': str(active_deck['TITLE'])})
            self.deck_arm = db.queryArm({'ARM': str(active_deck['ARM'])})
            self.decksummon = db.querySummon({'PET': str(active_deck['PET'])})
            self.deck_talisman = str(active_deck['TALISMAN'])
            self._equipped_card_data = self.deck_card
            self._equipped_title_data = self.deck_title
            self._equipped_arm_data = self.deck_arm
            self._equipped_summon_data = self.decksummon
            self.equipped_talisman = self.deck_talisman
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



