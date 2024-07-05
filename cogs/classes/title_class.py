import db
import crown_utilities
import custom_logging

class Title:
    def __init__(self, title, universe, abilities, rarity, unlock_method, title_id, available):
        self.name = title
        self.universe = universe
        self.available = available
        self.abilities = abilities
        self.rarity = rarity
        self.unlock_method = unlock_method
        self.id = title_id
        self.title_img = ""
        self.universe_crest = crown_utilities.crest_dict[self.universe]
        self.title_messages = []
        self.title_battle_messages = []
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
        self.unlock_method_message = f"🔒 This title can not be unlocked at this time."
        self.atk_effect = False
        self.def_effect = False
        self.stam_effect = False
        self.hlt_effect = False
        self.life_effect = False
        self.drain_effect = False
        self.flog_effect = False
        self.wither_effect = False
        self.rage_effect = False
        self.brace_effect = False
        self.bzrk_effect = False
        self.crystal_effect = False
        self.growth_effect = False
        self.fear_effect = False
        self.stance_effect = False
        self.confuse_effect = False
        self.blink_effect = False
        self.creation_effect = False
        self.destruction_effect = False
        self.blast_effect = False
        self.wave_effect = False
        self.speed_effect = False
        self.slow_effect = False
        self.haste_effect = False
        self.soulchain_effect = False
        self.gamble_effect = False
        self.singularity_effect = False
        self.iq_effect = False
        self.high_iq_effect = False
        self.blitz_effect = False
        self.foresight_effect = False
        self.obliterate_effect = False
        self.impenetrable_shield_effect = False
        self.pierce_effect = False
        self.synthesis_effect = False
        self.spell_shield_effect = False
        self.elemental_buff_effect = False
        self.elemental_debuff_effect = False
        self.enhanced_guard_effect = False
        self.strategist_effect = False
        self.sharpshooter_effect = False
        self.divinity_effect = False
        self.synthesis_damage_stored = 0

        # Abilities
        for i in range(min(3, len(abilities))):
            ability_attr = self.set_ability_attributes(abilities, i)
            self.add_title_message(ability_attr)
            self.set_instance_attributes(i + 1, ability_attr)
            self.set_title_effect(ability_attr)


        self.type_message = ""
        self.type2_message = ""
        self.message = ""
        self.pokemon_title = False
        self.active_message_sent = False
        self.region_trait = False
        self.title_active = False

        self.title_message = f"⚠️ | {self.name} ~ INEFFECTIVE"
        if self.universe in crown_utilities.pokemon_universes:
            self.pokemon_title = True
        self.title_icon = "⚠️"


    def set_title_image(self):
        if self.universe != 'Unbound':
            self.title_img = db.queryUniverse({'TITLE': self.universe})['PATH']
        return self.title_img


    def set_pokemon_title(self):
        if self.universe in crown_utilities.pokemon_universes:
            self.pokemon_title = True


    def set_ability_attributes(self, abilities, ability_index):
        ability = abilities[ability_index]
        ability_attr = {
            'ability': ability.get('ABILITY', ''),
            'prefix': crown_utilities.title_prefix_mapping[ability.get('ABILITY', '')],
            'suffix': crown_utilities.title_enhancer_suffix_mapping[ability.get('ABILITY', '')],
            'power': ability.get('POWER', 0),
            'element': ability.get('ELEMENT', ''),
            'duration': ability.get('DURATION', 0),
            'element_emoji': crown_utilities.set_emoji(ability.get('ELEMENT', ''))
        }
        return ability_attr


    def add_title_message(self, ability_attr):
        if ability_attr['power'] > 0:
            self.title_messages.append(f"🔸 {ability_attr['ability'].title()}: {ability_attr['prefix']} {ability_attr['power']}{ability_attr['suffix']}")
        elif ability_attr['ability'] in ['ELEMENTAL BUFF', 'ELEMENTAL DEBUFF']:
            self.title_messages.append(f"🔸 {ability_attr['ability'].title()}: {ability_attr['prefix']} {ability_attr['element_emoji']} {ability_attr['element'].capitalize()} {ability_attr['suffix']}")
        else:
            self.title_messages.append(f"🔸 {ability_attr['ability'].title()}: {ability_attr['prefix']} {ability_attr['suffix']}")


    def set_instance_attributes(self, index, ability_attr):
        setattr(self, f'ability{index}_ability', ability_attr['ability'])
        setattr(self, f'ability{index}_prefix', ability_attr['prefix'])
        setattr(self, f'ability{index}_suffix', ability_attr['suffix'])
        setattr(self, f'ability{index}_power', ability_attr['power'])
        setattr(self, f'ability{index}_element', ability_attr['element'])
        setattr(self, f'ability{index}_duration', ability_attr['duration'])
        setattr(self, f'ability{index}_element_emoji', ability_attr['element_emoji'])


    def set_title_effect(self, ability_attr):
        if ability_attr['ability'] == 'ATK':
            self.atk_effect = True
        elif ability_attr['ability'] == 'DEF':
            self.def_effect = True
        elif ability_attr['ability'] == 'STAM':
            self.stam_effect = True
        elif ability_attr['ability'] == 'HLT':
            self.hlt_effect = True
        elif ability_attr['ability'] == 'LIFE':
            self.life_effect = True
        elif ability_attr['ability'] == 'DRAIN':
            self.drain_effect = True
        elif ability_attr['ability'] == 'FLOG':
            self.flog_effect = True
        elif ability_attr['ability'] == 'WITHER':
            self.wither_effect = True
        elif ability_attr['ability'] == 'RAGE':
            self.rage_effect = True
        elif ability_attr['ability'] == 'BRACE':
            self.brace_effect = True
        elif ability_attr['ability'] == 'BZRK':
            self.bzrk_effect = True
        elif ability_attr['ability'] == 'CRYSTAL':
            self.crystal_effect = True
        elif ability_attr['ability'] == 'GROWTH':
            self.growth_effect = True
        elif ability_attr['ability'] == 'FEAR':
            self.fear_effect = True
        elif ability_attr['ability'] == 'STANCE':
            self.stance_effect = True
        elif ability_attr['ability'] == 'CONFUSE':
            self.confuse_effect = True
        elif ability_attr['ability'] == 'CREATION':
            self.creation_effect = True
        elif ability_attr['ability'] == 'DESTRUCTION':
            self.destruction_effect = True
        elif ability_attr['ability'] == 'SPEED':
            self.speed_effect = True
        elif ability_attr['ability'] == 'BLINK':
            self.blink_effect = True
        elif ability_attr['ability'] == 'SLOW':
            self.slow_effect = True
        elif ability_attr['ability'] == 'HASTE':
            self.haste_effect = True
        elif ability_attr['ability'] == 'SOULCHAIN':
            self.soulchain_effect = True
        elif ability_attr['ability'] == 'GAMBLE':
            self.gamble_effect = True
        elif ability_attr['ability'] == 'WAVE':
            self.wave_effect = True
        elif ability_attr['ability'] == 'BLAST':
            self.blast_effect = True
        elif ability_attr['ability'] == 'SINGULARITY':
            self.singularity_effect = True
        elif ability_attr['ability'] == 'IQ':
            self.iq_effect = True
        elif ability_attr['ability'] == 'HIGH IQ':
            self.high_iq_effect = True
        elif ability_attr['ability'] == 'BLITZ':
            self.blitz_effect = True
        elif ability_attr['ability'] == 'FORESIGHT':
            self.foresight_effect = True
        elif ability_attr['ability'] == 'OBLITERATE':
            self.obliterate_effect = True
        elif ability_attr['ability'] == 'IMPENETRABLE SHIELD':
            self.impenetrable_shield_effect = True
        elif ability_attr['ability'] == 'PIERCE':
            self.pierce_effect = True
        elif ability_attr['ability'] == 'SYNTHESIS':
            self.synthesis_effect = True
        elif ability_attr['ability'] == 'SPELL SHIELD':
            self.spell_shield_effect = True
        elif ability_attr['ability'] == 'ELEMENTAL BUFF':
            self.elemental_buff_effect = True
        elif ability_attr['ability'] == 'ELEMENTAL DEBUFF':
            self.elemental_debuff_effect = True
        elif ability_attr['ability'] == 'ENHANCED GUARD':
            self.enhanced_guard_effect = True
        elif ability_attr['ability'] == 'STRATEGIST':
            self.strategist_effect = True
        elif ability_attr['ability'] == 'SHARPSHOOTER':
            self.sharpshooter_effect = True
        elif ability_attr['ability'] == 'DIVINITY':
            self.divinity_effect = True


    def set_unlock_method_message(self, player):
        """
        Query stats using player info
        """
        if self.name in player.titles or self.name in player.tstorage:
            self.unlock_method_message = f"🔷 You already unlocked {self.name}"
            return

        if not self.unlock_method:
            return
        formatted_number = format(int(self.unlock_method['VALUE']), ',')
        if self.unlock_method['METHOD'] == "TALES" or self.unlock_method['METHOD'] == "TALES COMPLETED":
            self.unlock_method_message = f"🔹 Complete {formatted_number} Tales in {self.universe_crest} {self.universe}"
            
        if self.unlock_method['METHOD'] == "TALES RUN":
            self.unlock_method_message = f"🔹 Complete {formatted_number} Tales matches in {self.universe_crest} {self.universe}"
        
        if self.unlock_method['METHOD'] == "HEALED IN TALES":
            self.unlock_method_message = f"🔹 Heal {formatted_number} health in {self.universe_crest} {self.universe} Tales matches"
        
        if self.unlock_method['METHOD'] == "DAMAGE TAKEN IN TALES":
            self.unlock_method_message = f"🔹 Take {formatted_number} damage in {self.universe_crest} {self.universe} Tales matches"
        
        if self.unlock_method['METHOD'] == "DAMAGE DEALT IN TALES":
            self.unlock_method_message = f"🔹 Deal {formatted_number} damage in {self.universe_crest} {self.universe} Tales matches"
                    
        if self.unlock_method['METHOD'] == "DUNGEONS" or self.unlock_method['METHOD'] == "DUNGEONS COMPLETED":
            self.unlock_method_message = f"🔹 Complete {formatted_number} Dungeons in {self.universe_crest} {self.universe}"
        
        if self.unlock_method['METHOD'] == "DUNGEONS RUN":
            self.unlock_method_message = f"🔹 Complete {formatted_number} Dungeons matches in {self.universe_crest} {self.universe}"

        if self.unlock_method['METHOD'] == "HEALED IN DUNGEONS":
            self.unlock_method_message = f"🔹 Heal {formatted_number} health in {self.universe_crest} {self.universe} Dungeons matches"
        
        if self.unlock_method['METHOD'] == "DAMAGE TAKEN IN DUNGEONS":
            self.unlock_method_message = f"🔹 Take {formatted_number} damage in {self.universe_crest} {self.universe} Dungeons matches"

        if self.unlock_method['METHOD'] == "DAMAGE DEALT IN DUNGEONS":
            self.unlock_method_message = f"🔹 Deal {formatted_number} damage in {self.universe_crest} {self.universe} Dungeons matches"


        if self.unlock_method['METHOD'] == "SCENARIOS":
            r1 = db.queryScenarios({"NORMAL_DROPS": self.name})
            r2 = db.queryScenarios({"HARD_DROPS": self.name})

            list_of_scenarios = [
                f"🔹 {scenario['TITLE']} [Normal Difficulty]" for scenario in r1
            ] + [
                f"🔹 {scenario['TITLE']} [Hard Difficulty]" for scenario in r2
            ]

            message = "\n".join(list_of_scenarios)
            if not message:
                self.unlock_method_message = f"Will be added to a scenario soon!"
            self.unlock_method_message = f"**Complete any of the following scenarios:**\n{message}"


        if self.unlock_method['METHOD'] == "ELEMENTAL DAMAGE DEALT":
            formatted_number = format(int(self.unlock_method['VALUE']), ',')
            self.unlock_method_message = f"🔹 Deal {formatted_number} {crown_utilities.set_emoji(self.unlock_method['ELEMENT'])} {self.unlock_method['ELEMENT'].capitalize()} damage in {self.universe_crest} {self.universe}"
    
        if self.unlock_method['METHOD'] == "TOTAL_DAMAGE":
            formatted_number = format(int(self.unlock_method['VALUE']), ',')
            self.unlock_method_message = f"🔹 Deal {formatted_number} total damage in {self.universe_crest} {self.universe}"
    

        if self.unlock_method['METHOD'] == "BOSS":
            self.unlock_method_message = f"🔹 Defeat the boss in {self.universe_crest} {self.universe} for a chance to earn this title"

        return


    def set_title_suffix(self):
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
        return title_enhancer_suffix_mapping[self.passive_type]
        

    def set_title_message(self, performance_mode, card_universe):
        try:
            if self.universe == "Unbound" or (card_universe in crown_utilities.pokemon_universes) or card_universe == "Crown Rift Awakening":
                self.title_message = f"👑 | {self.name}" 

            elif self.universe == card_universe or (card_universe in crown_utilities.pokemon_universes and self.pokemon_title==True):
                self.title_message = f"🎗️ | {self.name}"
                        
        except:
            print("error setting title message")


    def get_title_icon(self, card_universe):
        try:
            if self.universe == "Unbound" or (card_universe in crown_utilities.pokemon_universes) or card_universe == "Crown Rift Awakening":
                return "👑" 

            elif self.universe == card_universe or (card_universe in crown_utilities.pokemon_universes and self.pokemon_title==True):
                return "🎗️"
            else:
                return self.title_icon
                        
        except:
            print("error setting title message")


    def set_title_embed_message(self):
        if self.passive_type == "ATK" or self.passive_type == "DEF" or self.passive_type == "HLT" or self.passive_type == "STAM":
            self.message = f"On your turn, Increases **{self.type_message}** by **{self.passive_value}{self.set_title_suffix()}**"
        
        elif self.passive_type == "FLOG" or self.passive_type == "WITHER" or self.passive_type == "LIFE" or self.passive_type == "DRAIN":
            self.message = f"On your turn, Steals **{self.passive_value}{self.set_title_suffix()} {self.type_message}**"
        
        elif self.passive_type == "RAGE" or self.passive_type == "BRACE" or self.passive_type == "BZRK" or self.passive_type == "CRYSTAL" or self.passive_type == "GROWTH" or self.passive_type == "FEAR":
            self.message = f"On your turn, Sacrifice **{self.passive_value}{self.set_title_suffix()} {self.type_message}**"
        
        elif self.passive_type == "STANCE" or self.passive_type == "CONFUSE":
            self.message = f"On your turn, Swap {self.type_message} Defense by **{self.passive_value}**"
            self.message = value=f"On your turn, **{self.type_message}** by **{self.passive_value}**, **{self.type2_message}** by **{self.passive_value}**"
        
        elif self.passive_type == "SLOW" or self.passive_type == "HASTE" or self.passive_type == "BLINK":
            self.message = f"On your turn, **{self.type_message}** by **{self.passive_value}**"
        
        elif self.passive_type == "SOULCHAIN" or self.passive_type == "GAMBLE":
            self.message = f"During Focus, **{self.type_message}** equal **{self.passive_value}**"
        
        return self.message
    

    def title_active_check(self, player_card):
        if self.universe == "Unbound":
            self.title_active = True
            return True
        elif player_card.universe == "Crown Rift Awakening":
            self.title_active = True
            return True
        elif (self.universe in crown_utilities.pokemon_universes and player_card.universe in crown_utilities.pokemon_universes):
            self.region_trait = True
            self.title_active = True
            return True
        elif self.universe == player_card.universe:
            self.title_active = True
            return True
        else:
            self.title_active = False
            return False

             
    def activate_ability(self, ability_name, ability_power, ability_element, player_card, opponent_card, battle):
        if hasattr(self, ability_name) and getattr(self, ability_name):
            self.title_effects_handler(player_card, opponent_card, battle, getattr(self, ability_power), getattr(self, ability_name))

            ability_effects = {
                "IQ": f"🔸 Focus Buffs +{round(getattr(self, ability_power))}%",
                "HIGH IQ": "🔸 Focus Buffs Continue On Resolve",
                "BLITZ": "🔸 Attacks Go Through Parries",
                "FORESIGHT": "🔸 Parried Attacks Hurt Less",
                "OBLITERATE": "🔸 Attacks Go Through Shields",
                "IMPENETRABLE SHIELD": "🔸 Shields Are Always Hit",
                "PIERCE": "🔸 Attacks Go Through Barriers",
                "SYNTHESIS": "🔸 Barriers Stores Damage For Later Heals",
                "SPELL SHIELD": f"🔸 Shields Absorb {crown_utilities.set_emoji(getattr(self, ability_element))} Damage",
                "ELEMENTAL BUFF": f"🔸 {crown_utilities.set_emoji(getattr(self, ability_element))} Attacks Deal 50% more Damage",
                "ELEMENTAL DEBUFF": f"🔸 Opponent {crown_utilities.set_emoji(getattr(self, ability_element))} Attacks Deal 50% less Damage",
                "ENHANCED GUARD": f"🔸 Blocking Blocks 80% Of Total Damage",
                "SHARPSHOOTER": "🔸 Attacks Don't Miss",
            }

            ability_message = ability_effects.get(getattr(self, ability_name))

            if ability_message not in self.title_battle_messages:
                self.title_battle_messages.append(ability_message)


    def activate_title_passive(self, battle, player_card, opponent_card, partner_card=None):
        self.activate_ability('ability1_ability', 'ability1_power', 'ability1_element', player_card, opponent_card, battle)
        self.activate_ability('ability2_ability', 'ability2_power', 'ability2_element', player_card, opponent_card, battle)
        self.activate_ability('ability3_ability', 'ability3_power', 'ability3_element', player_card, opponent_card, battle)


    def title_effects_handler(self, player_card, opponent_card, battle, power, ability=None):
        try:
            active = self.title_active_check(player_card)
            if not active:
                if not self.active_message_sent:
                    self.active_message_sent = True
                    battle.add_to_battle_log(f"(⚠️) {player_card.name} cannot equip the 🎗️ {self.name} title")
                return

            if ability == "HLT":
                equation = (power / 100) * player_card.health
                if player_card.max_health > player_card.health + (equation):
                    player_card.health = round(player_card.health + (equation))
                    self.title_battle_messages.append(f"🔸 +{round(equation):,} ❤️ health")

                if player_card.health >= player_card.max_health:
                    player_card.health = player_card.max_health

            if ability == "LIFE":
                equation = (power / 100) * opponent_card.health
                if player_card.max_health > (player_card.health + (equation)):
                    opponent_card.health = round(opponent_card.health - (equation))
                    player_card.health = round(player_card.health + (equation))
                    player_card.damage_healed = round(player_card.damage_healed + (equation))
                    player_card.damage_dealt = round(player_card.damage_dealt + (equation))
                    self.title_battle_messages.append(f"🔸 stole +{round(equation):,} ❤️ health")

            if ability == "ATK":
                equation = (power / 100) * player_card.attack
                player_card.attack = player_card.attack + round(equation)
                self.title_battle_messages.append(f"🔸 +{round(equation):,} 🗡️ attack")

            if ability == "DEF":
                equation = (power / 100) * player_card.defense
                player_card.defense = player_card.defense + (equation)
                self.title_battle_messages.append(f"🔸 +{round(equation):,} 🛡️ defense")
    
            if ability == "STAM":
                if player_card.stamina > 15:
                    player_card.stamina = player_card.stamina + power
                    self.title_battle_messages.append(f"🔸 +{power:,} 🌀 stamina")

            if ability == "DRAIN":
                if opponent_card.stamina > 15 and player_card.stamina >=10:
                    opponent_card.stamina = opponent_card.stamina - power
                    player_card.stamina = player_card.stamina + power
                    self.title_battle_messages.append(f"🔸 drained +{power:,} 🌀 stamina from opponent")

            if ability == "FLOG":
                equation = (power / 100) * opponent_card.attack
                opponent_card.attack = round(opponent_card.attack - (equation))
                player_card.attack = round(player_card.attack + (equation))
                self.title_battle_messages.append(f"🔸 stole +{round(equation):,} 🗡️ attack from opponent")

            if ability == "WITHER":
                equation = (power / 100) * opponent_card.defense
                opponent_card.defense = round(opponent_card.defense - (equation))
                player_card.defense = round(player_card.defense + (equation))
                self.title_battle_messages.append(f"🔸 stole +{round(equation):,} 🛡️ defense from opponent")

            if ability == "RAGE":
                equation = (power / 100) * player_card.defense
                player_card.defense = round(player_card.defense - (equation))
                player_card.card_lvl_ap_buff = round(player_card.card_lvl_ap_buff + (equation))
                self.title_battle_messages.append(f"🔸 -{round(equation)} 🛡️ defense / +{round(equation):,} ability points")
             
            if ability == "BRACE":
                equation = (power / 100) * player_card.attack
                player_card.card_lvl_ap_buff = round(player_card.card_lvl_ap_buff + (equation))
                player_card.attack = round(player_card.attack - (equation))
                self.title_battle_messages.append(f"🔸 -{round(equation)} 🗡️ attack / +{round(equation):,} ability points")

            if ability == "BZRK":
                equation = (power / 100) * player_card.health
                player_card.health = round(player_card.health - (equation))
                player_card.attack = round(player_card.attack + (equation))
                self.title_battle_messages.append(f"🔸 -{round(equation)} ❤️ health / +{round(equation):,} 🗡️ attack")

            if ability == "CRYSTAL":
                equation = (power / 100) * player_card.health
                player_card.health = round(player_card.health - (equation))
                player_card.defense = round(player_card.defense + (equation))
                self.title_battle_messages.append(f"🔸 -{round(equation)} ❤️ health / +{round(equation):,} 🛡️ defense")

            if ability == "FEAR":
                equation = 0
                if player_card.universe != "Chainsawman":
                    equation = (player_card.max_health * .03)
                    player_card.max_health = player_card.max_health - (player_card.max_health * .03)
                    if player_card.health > player_card.max_health:
                        player_card.health = player_card.max_health
                if player_card.health > player_card.max_health:
                    player_card.health = player_card.max_health
                opponent_card.defense = opponent_card.defense - power
                opponent_card.attack = opponent_card.attack - power
                opponent_card.card_lvl_ap_buff = opponent_card.card_lvl_ap_buff - power
                if opponent_card.attack <= 25:
                    opponent_card.attack = 25
                if opponent_card.defense <= 25:
                    opponent_card.defense = 25
                if opponent_card.card_lvl_ap_buff <= 0:
                    opponent_card.card_lvl_ap_buff = 1
                self.title_battle_messages.append(f"🔸 -{round(equation)} ❤️ max health / -{round(power):,} opponent 🗡️ attack and 🛡️ defense")
            
            if ability == "GROWTH":
                equation = round(player_card.max_health * .03)
                player_card.max_health = player_card.max_health - (player_card.max_health * .03)
                if player_card.health > player_card.max_health:
                    player_card.health = player_card.max_health
                player_card.defense = player_card.defense + power
                player_card.attack = player_card.attack + power
                player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + power
                self.title_battle_messages.append(f"🔸 -{round(equation)} ❤️ max health / +{round(power):,} opponent 🗡️ attack and 🛡️ defense")
            
            if ability == "SLOW":
                if battle.turn_total != 0:
                    battle.turn_total = battle.turn_total - power
                    if battle.turn_total <= 0:
                        battle.turn_total = 0
                    self.title_battle_messages.append(f"🔸 -{power:,} Turns")

            if ability == "HASTE":
                battle.turn_total = battle.turn_total + power
                self.title_battle_messages.append(f"🔸 +{power:,} Turns")

            if ability == "STANCE":
                tempattack = player_card.attack + power
                player_card.attack = player_card.defense
                player_card.defense = tempattack
                self.title_battle_messages.append(f"🔸 swapped  🗡️ attack and 🛡️ defense / +{power:,} 🛡️ defense")

            if ability == "CONFUSE":
                tempattack = opponent_card.attack - power
                opponent_card.attack = opponent_card.defense
                opponent_card.defense = tempattack
                self.title_battle_messages.append(f"🔸 swapped opponent 🗡️ attack and 🛡️ defense / -{power:,} opponent 🛡️ defense")

            if ability == "BLINK":
                player_card.stamina = player_card.stamina - player_card.passive_value
                if opponent_card.stamina >=10:
                    opponent_card.stamina = opponent_card.stamina + power
                self.title_battle_messages.append(f"🔸 swapped {power:,} stamina with opponent")

            if ability == "CREATION":
                equation = (power / 100) * player_card.max_health
                player_card.max_health = round(round(player_card.max_health + (equation)))
                player_card.damage_healed = round(player_card.damage_healed + (equation))
                self.title_battle_messages.append(f"🔸 +{round(equation):,} ❤️ max health")
          
            if ability == "DESTRUCTION":
                equation = (power / 100) * opponent_card.max_health
                opponent_card.max_health = round(opponent_card.max_health - (equation))
                player_card.damage_dealt = round(player_card.damage_dealt + (equation))
                self.title_battle_messages.append(f"🔸 -{round(equation):,} ❤️ opponent max health")

            if ability == "BLAST":
                opponent_card.health = round(opponent_card.health - power)
                player_card.damage_dealt = round(player_card.damage_dealt + power)
                self.title_battle_messages.append(f"🔸 -{power:,} ❤️ opponent health")
            
            if ability == "WAVE":
                if battle.turn_total % 10 == 0:
                    opponent_card.health = round(opponent_card.health - 100)
                    player_card.damage_dealt = player_card.damage_dealt + 100
                    self.title_battle_messages.append(f"🔸 -100 ❤️ opponent health")

        except Exception as ex:
            custom_logging.debug(ex)


    def title_battle_message_handler(self):
        # Remove None values from the list
        self.title_battle_messages = list(filter(None, self.title_battle_messages))
        
        # Get the latest 2 messages
        latest_messages = self.title_battle_messages[-2:]
        
        # Join the messages if there are any
        m = "\n".join(latest_messages) if latest_messages else ""
        
        if m:
            title_m = f"🎗️ {self.name}\n{m}"
        else:
            title_m = f"🎗️ {self.name}"
        
        # Clear the list
        self.title_battle_messages = []

        return title_m


    def iq_handler(self, health_calculation, attack_calculation, defense_calculation):
        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            if ability and ability == "IQ":
                health_calculation += health_calculation * (power / 100)
                attack_calculation += attack_calculation * (power / 100)
                defense_calculation += defense_calculation * (power / 100)
                title_message = f"🎗️ *IQ Effect has activated!*"
                return health_calculation, attack_calculation, defense_calculation, title_message


    def synthesis_handler(self, dmg, battle_config):
        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            if ability and ability == "SYNTHESIS":
                self.synthesis_damage_stored = self.synthesis_damage_stored + round(dmg / 2)
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🎗️ **{self.name}** : {self.synthesis_damage_stored:,} damage stored")
                title_message = f"🎗️ synthesis effect activated"


    def singularity_handler(self, resolve_health_buff, resolve_attack_buff, resolve_defense_buff):
        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            if ability and ability == "SINGULARITY":
                resolve_health_buff += resolve_health_buff * (power / 100)
                resolve_attack_buff += resolve_attack_buff * (power / 100)
                resolve_defense_buff += resolve_defense_buff * (power / 100)
                title_message = f"🎗️ singularity effect activated"
                return resolve_health_buff, resolve_attack_buff, resolve_defense_buff, title_message


    def elem_buff_handler(self, move_element, true_dmg):
        """
        Checks for elemental buffs based on move element and applies a 50% damage increase
        if a match is found. Returns the original or buffed true_dmg.

        Args:
            move_element (str): The element of the move being used.
            true_dmg (float): The base true damage value.

        Returns:
            float: The buffed true damage (if applicable) or the original value.
        """

        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            element = getattr(self, f'ability{i}_element', None)

            if ability == "ELEMENTAL BUFF" and element is not None:
                if move_element == element:
                    # Buff the damage by 50%
                    true_dmg = round(true_dmg + (true_dmg * .50))
                    return true_dmg

        # No matching buff found, return the original true_dmg
        return true_dmg


    def elem_debuff_handler(self, move_element, true_dmg):
        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            element = getattr(self, f'ability{i}_element', None)
            if ability and ability == "ELEMENTAL DEBUFF":
                if move_element == element:
                    # Debuff the damage by 50%
                    true_dmg = round(true_dmg - (true_dmg * .50))
                    return true_dmg

        # No matching buff found, return the original true_dmg
        return true_dmg
                

    def spell_shield_handler(self, card, dmg, battle_config):
        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            element = getattr(self, f'ability{i}_element', None)
            if ability and ability == "SPELL SHIELD":
                if dmg["ELEMENT"] == element:
                    card.health = card.health + (dmg["DMG"] * .25)
                    card.max_health = card.max_health + (dmg["DMG"] * .25)
                    title_message = f"🎗️ spell shield activated, 25% of damage dealt to the shield was absorbed"
                    return title_message


    def speed_handler(self, card):
        for i in range(1, 4):
            ability = getattr(self, f'ability{i}_ability', None)
            power = getattr(self, f'ability{i}_power', None)
            if ability and ability == "SPEED":
                card.speed = card.speed + power
                title_message = f"🎗️ speed effect activated"
                return title_message



