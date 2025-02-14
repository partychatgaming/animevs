import db
import crown_utilities
import custom_logging
from .map_class import Map
import interactions
import datetime
import json
import textwrap
import time
import random
import re
from logger import loggy
from functools import lru_cache
now = time.asctime()
import importlib
import unique_traits as ut
import uuid
import cogs.classes.maps.bleach_maps as bleach_maps
import cogs.classes.maps.naruto_maps as naruto_maps
import cogs.classes.maps.unbound as unbound
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
import asyncio
from copy import deepcopy


@lru_cache(maxsize=128)
def query_rpg_cards(universe, start, end):
    return db.queryRPGCards(universe, start, end)

# @lru_cache(maxsize=32)
# async def cached_rpg_story(player_name, universe, combatants_tuple, map_name):
#     from ai import rpg_story
#     return await rpg_story(player_name, universe, list(combatants_tuple), map_name)

class RPG:
    def __init__(self,bot, _player):
        self._uuid = None
        self.bot = bot
        self.mode = "RPG"
        self.is_rpg = True
        self.start_second = 0
        self.start_minute = 0
        self.start_hour = 0
        self.end_second = 0
        self.end_minute = 0
        self.end_hour = 0
        self.adventuring = True
        self.encounter = False
        self.battling = False
        self.moving = False
        self._rpg_msg = None
        self.combat_victory = False

        self.above_position = None
        self.below_position = None
        self.left_position = None
        self.right_position = None
        self.last_move = None

        self.last_thought = None
        self.train_of_thought = None

        self.start_x = 8
        self.start_y = 4
        self.starting_position = (10, 5)
        self.player_position = (10, 5)  # Initial position of universe_crest
        self.spawn_portal = (10,5)

        self._player = _player
        self.player1 = _player
        self.player_name = self.player1.disname
        self.player1_did = self.player1.did
        self.explore_location = self.player1.explore_location
        # print(f"Player1 Explore Location: {self.explore_location}")
        self.user = self.bot.get_user(self.player1_did)
        self.list_of_combatants = []
        self.names_of_combatants = []
        self.number_of_vs_combatants = 0
        self.current_opponent_name = ""
        self.map_level = 0
        self.story = {}
        self._talking_uuid = ""
        self.talking_encounter = False
        self.quest_type = None
        self.mission_type = None
        # The quest counts the total amount of quests completed  
        self.quest_count = 0
        self.quest_complete = 0
        self.quest_message = ""
        self.quest_message_list = ["[📜]Quest Log"]
        self.quest_completed = False

        #The Mission is the overall mission required to level up
        self.mission_requirements = 3
        self.mission_count = 0
        self.mission_message = ""
        self.mission_completed = False


        self.player1_card_name = self.player1.equipped_card
        self.player_card_data = crown_utilities.create_card_from_data(db.queryCard({'NAME': self.player1_card_name}))
        self.player_card_data.set_card_level_buffs(self.player1.card_levels)
        self.player_avatar = self.player1.avatar

        self.player_health = self.player_card_data.health
        self.player_max_health = self.player_card_data.health
        self.player_attack = self.player_card_data.attack
        self.player_defense = self.player_card_data.defense
        self.player_speed = self.player_card_data.speed
        self.player_stamina = self.player_card_data.stamina
        self.player_card_image = self.player_card_data.path

        self.player_atk_boost = False
        self.player_def_boost = False
        self.player_hp_boost = False

        #self.universe = self.player_card_data.universe
        self.universe = self._player.explore_location
        self.universe_data = db.queryUniverse({'TITLE': self.universe})
        if self.universe in ['NULL','Null','null']:
            self.universe = "Unbound"
        self.player1_title = self.player1.equipped_title    
        self.player_title_data = crown_utilities.create_title_from_data(db.queryTitle({'TITLE': self.player1_title}))

        self.player1_arm = self.player1.equipped_arm
        self.player_arm_data = crown_utilities.create_arm_from_data(db.queryArm({'ARM': self.player1_arm}))


        self.player1_summon_name = self.player1.equipped_summon
        self.player_summon_data = crown_utilities.create_summon_from_data(db.querySummon({'PET': self.player1_summon_name}))
        self.player1_summon_element = self.player_summon_data.emoji

        self.player1_talisman = self.player1.equipped_talisman
        if self.player1_talisman in ['NONE','NULL','Null','null']:
            self.player1_talisman = 'None'

        self.build_name = f"🎗️{self.player1_title} 🎴{self.player1_card_name}"
        self.build_equipment = f"🦾{self.player1_arm} & 🧬{self.player1_summon_name}"

        self.player_token = crown_utilities.crest_dict[self.player_card_data.universe]
        self.npc = crown_utilities.crest_dict[self.player_card_data.universe]
        print(f"Emoji: {self.player_token}")
        print(f"Emoji ID: {self.player_token.id}")
        self.civ_tokens = [
                            # Male emojis
                            "👨", "👨‍⚕️", "👨‍🌾", "👨‍🍳","👨‍🏭" "👨‍💼", "👨‍🔧",
                            "🕵️‍♂️", "👷‍♂️", "🤴", "👳‍♂️", "👲", "🧔", "👱‍♂️", "👨‍🦰", "👨‍🦱", 
                            "👨‍🦳", "👨‍🦲", "🧓", "👴",
                            # Female emojis
                            "👩", "👩‍⚕️", "👩‍🌾", "👩‍🍳","👩‍🏭", "👩‍💼", "👩‍🔧",
                            "🕵️‍♀️", "👷‍♀️", "👸", "👳‍♀️", "👲", "🧕", "👱‍♀️", "👩‍🦰", "👩‍🦱",
                            "👩‍🦳", "👩‍🦲", "🧓", "👵",
                            # Child emojis
                            "👦", "👧",
                        ]
        
        self.difficulty = _player.difficulty
        self.is_easy_difficulty = False
        self.is_hard_difficulty = False
        self.is_normal_difficulty = False
        if self.difficulty == "EASY":
            self.is_easy_difficulty = True
        elif self.difficulty == "HARD":
            self.is_hard_difficulty = True


        
        self.player_gold = 0
        self.player_gems = 0
        self.player_keys = 0
        self.coin_emoji = "🪙"
        self.gem_emoji = "💎"
        self.player_inventory = []
        self.player_skills = []
        self.card_drops = []
        self.title_drops = []
        self.arm_drops = []
        self.summon_drops = []
        self.pickaxe = False
        self.miner = False
        self.hammer = False
        self.fishing_pole = False
        self.fishing = False
        self.engineer = False 
        self.swimmer = False
        self.climber = False
        self.has_quest = False
        self.has_investigation = False
        self.my_quest = None

        self.vs_count = 0
        self.civ_count = 0
        self.wild_count = 0

        self.loot_drop = False

        self.quest_giver_position = None
        self.encounter_position = None

        self.inventory_active = False
        self.currency_active = False
        self.skills_active = False

        self.closest_warp_points = []
        self.walls = [ "⬛", "🌀"]
        self.movement_buttons = []

        self.roads = ["◼️"]
        self.paths = ["🟩", "⬜","🟨","🟫", "🟪"]
        self.passable_points = []
        self.passable_points.extend(self.roads)
        self.passable_points.extend(self.paths)

        self.climable_mountains = ["🏞️"]
        self.looted_mountain = ["⛰️"]
        self.mountains = ["🏔️"]
        self.buildings = ["🏢","🌆","🌃"]
        self.walls.extend(self.mountains)
        self.mountains.extend(self.climable_mountains)
        self.mountains.extend(self.looted_mountain)

        self.cars = [
        "🚗",  # Car
        "🚕",  # Taxi
        "🚙",  # SUV
        "🚌",  # Bus
        "🚎",  # Trolleybus
        "🏎️",  # Racing Car
        "🚓",  # Police Car
        "🚑",  # Ambulance
        "🚒",  # Fire Engine
        "🚐",  # Minibus
        "🚚",  # Delivery Truck
        "🚛",  # Articulated Lorry
        "🚜",  # Tractor
        "🛻",  # Pickup Truck
        ]
        self.fruit_trees = ["🎄"]
        self.looted_trees = ["🌴"]
        self.trees = ["🌲", "🌳"]
        self.looted_cactus = ["🏜️"]
        self.cactus = ["🌵"]
        self.cactus.extend(self.looted_cactus)
        self.trees.extend(self.fruit_trees)
        self.trees.extend(self.looted_trees)

        self.moving_water = ["🌊"]
        self.still_water = ["🟦"]
        self.bridges = ["🌉"]
        self.crossed_bridges = []
        self.merchants = ["🏪","🧙", "🕴️","🏯","🏥"]
        self.wildlife = ["🦊", "🦇","🐍", "🦂","🦌","🐇"]
        self.grave = ["🪦"]

        self.doors = ["🚪"]
        self.open_door = "🛗"
        self.keys = ["🗝️"]
        self.gem_icon = f"<a:b_crystal:1085618488942547024>"
        self.uncut_gems = ["<a:b_crystal:1085618488942547024>"]
        self.gems = ["💎"]
        self.gems.extend(self.uncut_gems)

        self.gold = f"<a:Shiney_Gold_Coins_Inv:1085618500455911454>"
        self.coin_item = "🪙"
        self.gold_item = [f"<a:Shiney_Gold_Coins_Inv:1085618500455911454>"]
        self.common_items = ["💰","🪙","👛"]
        self.common_items.extend(self.gold_item)
        self.rare_items = ["🎁","🎒"]
        self.legendary_items = ["🎒"]
        self.items = []
        self.items.extend(self.common_items)
        self.items.extend(self.rare_items)
        self.items.extend(self.legendary_items)

        self.stat_boosts = ["🗡️","🛡️","💗"]
        self.common_drops = ["🦾","🆙"]
        self.rare_drops = ["🎴","🧬"]
        self.legendary_drops = ["🎗️"]
        self.drops = []
        self.drops.extend(self.common_drops)
        self.drops.extend(self.rare_drops)  
        self.drops.extend(self.legendary_drops)
        self.drops.extend(self.stat_boosts)
        
        self.tutorial = ["🥋"]
        self.combat_points = ["🏴‍☠️","⚔️","🆚","🎯"]
        self.combat_points.extend(self.tutorial)
        self.combat_points.extend(f"{self.npc}")

        self.loot_rolls = ["🎲","🃏","🎰"]
        self.encounter_rolls =["💫"]
        self.quest = ["🎯", "🔎"]
        self.skills = ['🏊6','🪜','🪓','🎣','⛏️','🔨','⚒️']
        self.remains = ["💀","🦴", "☠️"]
        self.food = ["🥩", "🍖", "🥕"]
        self.cooked_food = ["🍲","🍛","🍚"]
        self.healing_items = []
        self.healing_items.extend(self.food)
        self.healing_items.extend(self.cooked_food)
        self.raw_resources = ['🪨','🧱']
        self.resources = []
        self.resources.extend(self.raw_resources)
        self.resources.extend(self.gems)
        self.pumpkin = "🎃"
        self.pumpkin_array = ["🎃"]

        self.random_loot_point = []
        self.random_loot_point.extend(self.items)
        self.random_loot_point.extend(self.remains)


        self.interaction_points = []
        self.interaction_points.extend(self.bridges)
        self.interaction_points.extend(self.moving_water)
        self.interaction_points.extend(self.still_water)
        self.interaction_points.extend(self.trees)
        self.interaction_points.extend(self.merchants)
        self.interaction_points.extend(self.wildlife)
        self.interaction_points.extend(self.doors)
        self.interaction_points.extend(self.open_door)
        self.interaction_points.extend(self.keys)
        self.interaction_points.extend(self.items)
        self.interaction_points.extend(self.remains)
        self.interaction_points.extend(self.food)
        self.interaction_points.extend(self.resources)
        self.interaction_points.extend(self.drops)
        self.interaction_points.extend(self.mountains)
        self.interaction_points.extend(self.cactus)
        self.interaction_points.extend(self.pumpkin_array)

        self.warp_points = []
        self.warp_points.extend(self.merchants)
        self.warp_points.extend(self.doors)
        self.warp_points.extend(self.open_door)
        self.warp_points.extend(self.keys)
        self.warp_points.extend(self.items)
        self.warp_points.extend(self.remains)
        #self.warp_points.extend(self.npc)
        self.warp_points.extend(self.civ_tokens)
        self.warp_points.extend(self.combat_points)
        self.warp_points.extend(self.wildlife)
        self.warp_points.extend(self.resources)
        self.warp_points.extend(self.bridges)
        self.warp_points.extend(self.quest)

        self.active_warp_points = []
        self.warp_point_position = 0

        self.world_interaction_buttons = []
        self.world_interaction_buttons.extend(self.interaction_points)
        self.world_interaction_buttons.extend(self.combat_points)
        self.world_interaction_buttons.extend(self.civ_tokens)
        self.world_interaction_buttons.extend(self.quest)

        #Other Players & Universes
        self.rpg_npc = crown_utilities.rpg_npc_emojis
        self.world_interaction_buttons.extend(self.rpg_npc)

        #Merchants sell arms
        #Wildlife drop food
        #Magical merchants sell titles
        #black market merchants sell summons
        self.previous_moves = ["[🗺️] Adventurer's log..."]
        self.previous_moves_len = len(self.previous_moves)
        
        self.action_buttons = []
        self.world_buttons = []
        self.encounter_buttons = []
        self.warp_buttons = []
        self.warp_active = False

        self.standing_on = "🟩"
        self.spawn_portal = (10,5)
        self.map =self.initialize_map() # Unique map for this RPG instance
        self.map_name = "Damp Woodlands"
        self.map_area = "Forest Training Grounds"
        self.embed_color = 0x00FF00
        
        self.map_states = {}  # Dictionary to hold the state of each map
        self.map_change = False
        self.new_map = False

        self.area_task = None
        self.floor_task = None
        self.floor_task_msg = None
        self.floor = 0
        self.map_doors = None
        self.exit_points = None
        self.north_exits = None
        self.south_exits = None
        self.east_exits = None
        self.west_exits = None
        self.door_exit = None

        #self.player_tokens = {}  # Key: token, Value: player object
        #self.player_tokens[self.player_token] = self.player1_did  # Link token to player


        
    #Functions begin here
    @listen()
    async def on_ready(self):
        loggy.info('RPG Cog is ready!')
        print('RPG Cog is ready!')

    
    async def create_rpg(self, ctx, rpg_msg):
        from cogs.play import Play as play
        await self.configure_map(self._player)
        await play.rpg_commands(self, ctx, rpg_msg)

    
    async def initialize_map(self):
        # Create a new map for this specific instance
        map_data = await self.configure_map(self._player)
        return map_data

    def find_nearest_passable(self, i, j):
        """Finds the nearest passable token from a given position."""
        grid = self._player.map['map']
        rows = len(grid)
        cols = len(grid[0])
        visited = set()
        queue = [(i, j)]

        while queue:
            r, c = queue.pop(0)
            if (r, c) in visited:
                continue
            visited.add((r, c))
            if grid[r][c] in self.passable_points:
                return grid[r][c]
            # Add neighboring cells to the queue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    queue.append((nr, nc))
        return self._player.standing_on  # Fallback if no passable token is found

    def clean_player_tokens(self):
        """Cleans stray player tokens from the map."""
        correct_position = self._player.player_position
        grid = self._player.map['map']

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                # If a cell has the player token but isn't the correct position
                if grid[i][j] == self.player_token and (i, j) != correct_position:
                    replacement = self.find_nearest_passable(i, j)
                    grid[i][j] = replacement

    def display_map(self):
        """Cleans stray tokens and displays the map."""
        self.clean_player_tokens()  # Clean the map before displaying
        return "\n".join("".join(str(cell) for cell in row) for row in self._player.map['map'])


    
    # def display_map(self):
    #     return "\n".join("".join(str(cell) for cell in row) for row in self._player.map['map'])

    
    async def change_map(self, direction, location):
        self.map_change = True
        self.save_map_state(self._player.map["map_name"])  # Save the current map state before changing
        if location == self._player.map["map_doors"]:
            self._player.floor += 1 
            await self.load_map(self._player.map["door_exit"])
            return True
        elif direction == "2" and self._player.map["north_exits"]:
            next_map = self._player.map.get("north_exits")
            self._player.floor += 1
            await self.load_map(self._player.map["north_exits"])
            return True
        elif direction == "3" and self._player.map["south_exits"]:
            self._player.floor += 1
            await self.load_map(self._player.map["south_exits"])
            return True
        elif direction == "4" and self._player.map["east_exits"]:
            self._player.floor += 1
            await self.load_map(self._player.map["east_exits"])
            return True
        elif direction == "1" and self._player.map["west_exits"]:
            self._player.floor += 1
            await self.load_map(self._player.map["west_exits"])
            return True
        else:
            self.previous_moves.append(f"Cannot move {direction}, no exit found.")
            self.map_change = False
            return False


    def save_map_state(self, map_name):
        x, y = self._player.player_position
        self._player.map['map'][x][y] = self._player.standing_on
        self._player.map['spawn_portal'] = self._player.player_position
        map_copy = deepcopy(self._player.map)
        # Break circular references
        # map_copy['north_exits'] = None
        # map_copy['south_exits'] = None
        # map_copy['east_exits'] = None
        # map_copy['west_exits'] = None
        self._player.map_states[map_name] = map_copy



        #loggy.info(f"Saved map state: {map_name} - {self._player.map_states[map_name]}")
    
    
    async def load_map(self, new_map):
        # Save the current map state before loading the new map
        x, y = self._player.player_position
        self._player.map['map'][x][y] = self._player.standing_on
        # Check if the new map has been visited before
        if new_map['map_name'] in self._player.map_states:
            loggy.info(f"Loading saved map: {new_map['map_name']} - {new_map['map_area']}")
            # Load the saved state of the new map
            saved_map = deepcopy(self._player.map_states[new_map['map_name']])
            self._player.map["standing_on"] = saved_map['standing_on']
            self._player.map["spawn_portal"] = saved_map['spawn_portal']
            self._player.map["map_name"] = saved_map['map_name']
            self._player.map["map_area"] = saved_map['map_area']
            self._player.map["embed_color"] = saved_map['embed_color']
            self._player.map["map_doors"] = saved_map['map_doors']
            self._player.map["exit_points"] = saved_map['exit_points']
            self._player.map["north_exits"] = saved_map['north_exits']
            self._player.map["south_exits"] = saved_map['south_exits']
            self._player.map["east_exits"] = saved_map['east_exits']
            self._player.map["west_exits"] = saved_map['west_exits']
            self._player.map["door_exit"] = saved_map['door_exit']
            self._player.map['map'] = saved_map['map']
            self._player.player_position = saved_map['spawn_portal']
            self._player.new_map = False
            # This method is called when the map is configured to programmatically place "🆚" emojis on the map
            await self.place_emojis()
        else:
            # Load the new map as usual
            loggy.info(f"Loading new map: {new_map['map_name']} - {new_map['map_area']}")
            self._player.map["standing_on"] = new_map['standing_on']
            self._player.map["spawn_portal"] = new_map['spawn_portal']
            self._player.map["map_name"] = new_map['map_name']
            self._player.map["map_area"] = new_map['map_area']
            self._player.map["embed_color"] = new_map['embed_color']
            self._player.map["map_doors"] = new_map['map_doors']
            self._player.map["exit_points"] = new_map['exit_points']
            self._player.map["north_exits"] = new_map['north_exits']
            self._player.map["south_exits"] = new_map['south_exits']
            self._player.map["east_exits"] = new_map['east_exits']
            self._player.map["west_exits"] = new_map['west_exits']
            self._player.map["door_exit"] = new_map['door_exit']
            self._player.map['map'] = new_map['map']
            self._player.player_position = self._player.map['spawn_portal']
            self._player.new_map = True
            # This method is called when the map is configured to programmatically place "🆚" emojis on the map
            await self.place_emojis()


        # Set the player token on the map at the player's position
        loggy.info(f"Player position: {self._player.player_position}")
        x, y = self._player.player_position
        self._player.standing_on = self._player.map['map'][x][y]  # Save the tile the player will be standing on
        self._player.map['map'][x][y] = self.player_token  # Place the player token on the map

        self.previous_moves.append(f"Entered {self._player.map['map_name']} - {self._player.map['map_area']}")
        
 
    def get_current_map_data(self):
        return {
            'standing_on': self._player.standing_on,
            'spawn_portal': self.spawn_portal,
            'map_name': self._player.map["map_name"],
            'map_area': self.self._player.map['map_area'],
            'embed_color': self.embed_color,
            'map_doors': self.map_doors,
            'exit_points': self.exit_points,
            'north_exits': self.north_exits,
            'south_exits': self.south_exits,
            'east_exits': self.east_exits,
            'west_exits': self.west_exits,
            'door_exit': self.door_exit,
            'map': self.map
        }
    

    def count_emojis_on_map(self, map, civ_tokens):
        vs_count = 0
        civ_count = 0
        wild_count = 0
        loot_count = 0
        resource_count = 0
        civ_set = set(civ_tokens)  # Convert civ_tokens list to a set for faster lookup
        wildlife_set = set(self.wildlife)  # Convert wildlife_tokens list to a set for faster lookup
        loot_set = set(self.random_loot_point)
        resource_set = set(self.raw_resources)

        for row in map:
            for cell in row:
                if cell == "🆚":
                    vs_count += 1
                elif cell in civ_set:
                    civ_count += 1
                elif cell in wildlife_set:
                    wild_count += 1
                elif cell in loot_set:
                    loot_count += 1
                elif cell in resource_set:
                    resource_count += 1

        total_count = vs_count + civ_count + wild_count 
        return total_count, vs_count, civ_count, loot_count, resource_count
    
    async def place_emojis(self):
        total, vs, civ, loot, res = self.count_emojis_on_map(self._player.map['map'], self.civ_tokens)
        if vs <= 2:
            await self.place_vs_emojis(self._player.map['map'], self.configure_map_level_layout())
        if civ < 1:
            await self.place_civ_emojis(self._player.map['map'], self.configure_map_level_layout())
        if loot <=1:
            num = random.randint(1,100)
            if num <= 50:
                await self.place_loot_emojis(self._player.map['map'], 1)
            elif num == 100:
                await self.place_loot_emojis(self._player.map['map'], 2)
        if res <= 1:
            await self.place_resource_emojis(self._player.map['map'], 1)
        if total <= 4:
            await self.place_wildlife_emojis(self._player.map['map'])


    async def generate_combatants(self):
        number_of_combatants, vs_count, civ_count, loot_count, resource_count = self.count_emojis_on_map(self._player.map['map'], self.civ_tokens)
        self.vs_count = vs_count
        self.civ_count = civ_count
        # Fetch combatants
        self.list_of_combatants = await self.fetch_combatants(number_of_combatants)
        self.names_of_combatants = [combatant["NAME"] for combatant in self.list_of_combatants]


    async def fetch_combatants(self, number_of_combatants):
        return query_rpg_cards(self.universe, 1, number_of_combatants)


    def remove_combatant(self):
        if self.current_opponent_name:
            for i, combatant in enumerate(self.list_of_combatants):
                if combatant["NAME"] == self.current_opponent_name:
                    loggy.info(f"Removing {self.current_opponent_name} from the list of combatants")
                    self.list_of_combatants.pop(i)
                    break
                
            for i, combatant in enumerate(self.names_of_combatants):
                if combatant == self.current_opponent_name:
                    loggy.info(f"Removing {self.current_opponent_name} from the names of combatants")
                    self.names_of_combatants.pop(i)
                    break
            
            self.current_opponent_name = ""

    
    async def configure_map(self, player, map_dict=None):
        """
        Configures a map for the player and saves the entire map dictionary to their profile.

        Args:
            player (Player): The player object.
            map_dict (dict): Optional map dictionary to directly configure the map.
        """
        if not map_dict:
            max_attempts = 2
            universe = player.explore_location.lower()  # Use player's explore_location
            for attempt in range(max_attempts):
                try:
                    # Dynamically import the correct maps module
                    module_name = f"cogs.classes.maps.{universe}_maps"
                    loggy.info(f"Attempting to import module: {module_name}")
                    maps_module = importlib.import_module(module_name)

                    # Get all attributes of the module
                    all_attributes = dir(maps_module)

                    # Filter to only get the map dictionaries
                    map_dicts = [
                        getattr(maps_module, attr) for attr in all_attributes 
                        if isinstance(getattr(maps_module, attr), dict) and 'map_name' in getattr(maps_module, attr)
                    ]

                    if map_dicts:
                        # Randomly select a map dictionary
                        map_dict = random.choice(map_dicts)
                        break  # Exit the loop if a valid map is found

                except ImportError:
                    loggy.warning(f"Module {module_name} not found. Falling back to unbound.py.")
                
                # Attempt to load from unbound.py as fallback
                try:
                    module_name = "cogs.classes.maps.unbound"
                    loggy.info(f"Attempting to import module: {module_name}")
                    maps_module = importlib.import_module(module_name)
                    all_attributes = dir(maps_module)
                    map_dicts = [
                        getattr(maps_module, attr) for attr in all_attributes 
                        if isinstance(getattr(maps_module, attr), dict) and 'map_name' in getattr(maps_module, attr)
                    ]

                    if hasattr(maps_module, "default_map"):
                        # map_dict = random.choice(map_dicts)
                        map_dict = maps_module.default_map
                        loggy.info(f"Loaded default map from unbound.py: {map_dict['map_name']}")
                        break

                except ImportError as e:
                    loggy.error(f"Failed to import fallback module {module_name}: {e}")
                    continue

            if not map_dict:
                loggy.error("No valid map dictionary found after multiple attempts. Using default map.")
                map_dict = self.get_default_map()

        # Save the entire map dictionary to the player's profile
        player.map = deepcopy(map_dict)
        loggy.info(f"Map configured and saved for player {player.disname}: {player.map['map_name']}")
        x, y = self.spawn_portal
        if player.map["map"][x][y] in self.passable_points:
            loggy.info(f"Player token placed at spawn portal: {player.map['map'][x][y]}{player.map['spawn_portal']}")
            player.map["map"][x][y] = f"{self.player_token}"
            self._player.standing_on = player.map["standing_on"]

        self._player.map_level = self.rpg_universe_level_check()
    
        # This method is called when the map is configured to programmatically place "🆚" emojis on the map
        #total, vs, civ, loot, res = self.count_emojis_on_map(self._player.map['map'], self.civ_tokens)
        await self.place_emojis()

        # This method is called when the map is configured to programmatically generate combatants based on the number of "🆚" emojis on the map
        await self.generate_combatants()
        await self.rpg_set_completetion_quest()


        return player.map




    async def increment_mission_count(self, ctx, private_channel):
        #print(f"Mission count: {self._player.mission_count} / Mission requirements: {self._player.mission_requirements}")
        if self.mission_type == "DEFEAT_ALL_ENEMIES":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "DEFEAT_ENEMIES":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "COLLECT_ALL_ITEMS":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "COLLECT_ITEMS":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "DEFEAT_BOSS":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)

        elif self.mission_type == "COLLECT_CRYSTAL":
            self._player.mission_count = self.player_gems
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "COLLECT_GOLD":
            self._player.mission_count = self.player_gold
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "HUNT":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        elif self.mission_type == "QUEST" and self.has_quest:
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)

        elif self.mission_type == "INVESTIGATION" and self.has_investigation:
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)

        elif self.mission_type == "EXPLORE":
            self._player.mission_count += 1
            if self._player.mission_count >= self._player.mission_requirements:
                await self.complete_quest(ctx, private_channel)
        
        #print(f"Quest count: {self._player.mission_count} / Quest requirements: {self._player.mission_requirements}")

        # Add more quest types and their increment logic here


    async def complete_quest(self, ctx, private_channel):
        #print("Mission completed! Incrementing RPG level")
        self._player.inc_rpg_level(self.universe)
        self._player.save_rpg_levels()
        x, y = self._player.player_position
        self._player.map['map'][x][y] = self._player.standing_on # Reset the player token on the map
        self.adventuring = False
        self.mission_completed = True
        currency_modifier = self.rpg_universe_level_check()
        gold_to_coin = self.player_gold * currency_modifier
        await crown_utilities.bless(gold_to_coin, self.player1_did)
        if self.player_gems > 0:
            gems_earned = self.player_gems * currency_modifier
            universe_to_add_gems = self.universe
            self.player1.save_gems(universe_to_add_gems, gems_earned)

        embedVar = Embed(title=f"🗺️ | {self.universe} Adventure Ended!", description=textwrap.dedent(f"""
            """))           
        embedVar.set_footer(text="🗺️ | Reach the end of the map to complete the adventure!")

        await self._rpg_msg.delete()
        paginator = await self.leave_adventure_embed(ctx)
        await paginator.send(ctx)

   
    async def rpg_set_completetion_quest(self):
        #self.mission_type = "DEFEAT_ENEMIES"  # Example, you can change this dynamically
        mission_select = random.choice(["DEFEAT_ENEMIES","COLLECT_SKILLS", "COLLECT_CRYSTAL", "COLLECT_GOLD", "HUNT", "QUEST", "INVESTIGATION", "EXPLORE"]) #Boss and All enemies inactive
        if self.mission_type not in ["DEFEAT_ENEMIES", "COLLECT_SKILLS", "COLLECT_CRYSTAL", "COLLECT_GOLD", "HUNT", "QUEST", "INVESTIGATION", "EXPLORE"]:
            self.mission_type = mission_select
            self._player.mission_count = 0
            self.number_of_vs_combatants = self.vs_count
        
            if self.mission_type == "DEFEAT_ALL_ENEMIES":
                # Set the quest to defeat all enemies
                loggy.info(f"Defeating all enemies")
                amount_of_combatants = self.number_of_vs_combatants
                self._player.mission_requirements = amount_of_combatants
                self.mission_message = "Defeat all enemies"
                
            if self.mission_type == "DEFEAT_ENEMIES":#good
                # Set the quest to defeat a specific number of enemies
                loggy.info(f"Defeating enemies")
                amount_of_combatants = self.number_of_vs_combatants
                self._player.mission_requirements = random.randint(1, amount_of_combatants)
                self.mission_message = f"Defeat {self._player.mission_requirements} enemies" if self._player.mission_requirements > 1 else "Defeat an enemy"
                
            # Add more quest types and their corresponding messages here
            if self.mission_type == "COLLECT_ALL_ITEMS":
                loggy.info(f"Collecting all items")
                self._player.mission_requirements = len(self.skills)  # Assuming list_of_items exists
                self.mission_message = "Learn all skills"
                
            if self.mission_type == "COLLECT_SKILLS":
                loggy.info(f"Collecting skills")
                self._player.mission_requirements = random.randint(1, 3)  # Assuming list_of_items exists
                self.mission_message = f"Learn {self._player.mission_requirements} skills" if self._player.mission_requirements > 1 else "Learn a skill"
                
            # Example for another quest type
            if self.mission_type == "DEFEAT_BOSS":
                loggy.info(f"Defeating the boss")
                self._player.mission_requirements = 1  # Typically defeating a boss would be a single task
                self.mission_message = "Defeat the boss"

            if self.mission_type == "COLLECT_CRYSTAL": #Good
                loggy.info(f"Collecting crystals")
                self._player.mission_requirements = random.randint(200, 500)
                self.mission_message = f"Collect {self._player.mission_requirements} crystals"

            if self.mission_type == "COLLECT_GOLD":
                loggy.info(f"Collecting gold")
                self._player.mission_requirements = random.randint(500, 1000)
                self.mission_message = f"Collect {self._player.mission_requirements} gold"

            if self.mission_type == "HUNT": #Good
                loggy.info(f"Hunting animals")
                self._player.mission_requirements = random.randint(1, 5)
                self.mission_message = f"Hunt {self._player.mission_requirements} animals" if self._player.mission_requirements > 1 else "Hunt an animal"

            if self.mission_type == "QUEST":
                loggy.info(f"Completing quests")
                self._player.mission_requirements = random.randint(1, 5)
                self.mission_message = f"Complete {self._player.mission_requirements} quests" if self._player.mission_requirements > 1 else "Complete a quest"

            if self.mission_type == "INVESTIGATION":
                self._player.mission_requirements = random.randint(1, 3)
                self.mission_message = f"Complete {self._player.mission_requirements} investigations" if self._player.mission_requirements > 1 else "Complete an investigation"

            if self.mission_type == "EXPLORE":
                self._player.mission_requirements = random.randint(3, 5)
                self.mission_message = "Explore the map"


        # You can continue adding more quest types and their messages as needed

    
    def rpg_universe_level_check(self):
        exists = False
        level = 1
        for level in self._player.rpg_levels:
            if level["UNIVERSE"] == self.universe:
                exists = True
                level = level["LEVEL"]
                break
        
        if not exists:
            self._player.rpg_levels.append({
                "UNIVERSE": self.universe,
                "LEVEL": 1
            })
            self._player.save_rpg_levels()
        
        return level

    
    def configure_map_level_layout(self):
        # This method determines how many opponents will be placed on the map based on the map level
        number_of_combatants = 0
        if int(self._player.map_level) < 10:
            number_of_combatants = random.randint(1, 2)
        elif int(self._player.map_level) < 40:
            number_of_combatants = random.randint(2, 3)
        elif int(self._player.map_level) < 80:
            number_of_combatants = random.randint(3, 5)
        else:
            number_of_combatants = random.randint(4, 10)
        return number_of_combatants


    async def place_vs_emojis(self, map_data, num_vs):
        try:
            # Get all possible positions for placing "🆚"
            available_positions = [(i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell in self.passable_points]
            
            if num_vs > len(available_positions):
                raise ValueError("Number of '🆚' emojis to place exceeds the available positions.")
            
            # Randomly select positions to place "🆚"
            vs_positions = random.sample(available_positions, num_vs)
            
            # Place "🆚" emojis on the map
            for i, j in vs_positions:
                map_data[i][j] = "🆚"
            
            return map_data
        except Exception as e:
            loggy.error(f"Failed to place '🆚' emojis on the map: {e}")
            return 
        
    
    async def place_wildlife_emojis(self, map_data, max_wildlife=2):
        """
        Places up to `max_wildlife` wildlife emojis randomly on the map.

        Parameters:
        - map_data: 2D list representing the current map.
        - max_wildlife: Maximum number of wildlife emojis to place on the map.

        Returns:
        - Updated map_data with wildlife emojis placed.
        """
        try:
            # Get all possible positions for placing wildlife
            available_positions = [(i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell in self.passable_points]
            
            if max_wildlife > len(available_positions):
                loggy.warning("Number of wildlife to place exceeds the available positions. Adjusting to available spots.")
                max_wildlife = len(available_positions)

            # Randomly select positions for wildlife
            wildlife_positions = random.sample(available_positions, max_wildlife)

            # Randomly select wildlife emojis to place
            wildlife_emojis = random.choices(self.wildlife, k=max_wildlife)
            
            # Place wildlife emojis on the map
            for (i, j), emoji in zip(wildlife_positions, wildlife_emojis):
                map_data[i][j] = emoji
            
            return map_data
        except Exception as e:
            loggy.error(f"Failed to place wildlife emojis on the map: {e}")
            return 
        

    async def place_civ_emojis(self, map_data, num_npcs):
        try:
            # Get all possible positions for placing "👥"
            available_positions = [(i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell in self.passable_points]
            
            if num_npcs > len(available_positions):
                raise ValueError("Number of '👥' emojis to place exceeds the available positions.")
            
            # Randomly select positions to place "👥"
            npc_positions = random.sample(available_positions, num_npcs)
            
            # Place "👥" emojis on the map
            for i, j in npc_positions:
                random_npc = random.choice(self.civ_tokens)
                map_data[i][j] = random_npc
            
            return map_data
        except Exception as e:
            loggy.error(f"Failed to place '👥' emojis on the map: {e}")
            return
    
    async def place_loot_emojis(self, map_data, num_loot):
        try:
            # Get all possible positions for placing "💰"
            available_positions = [(i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell in self.passable_points]
            
            if num_loot > len(available_positions):
                raise ValueError("Number of '💰' emojis to place exceeds the available positions.")
            
            # Randomly select positions to place "💰"
            loot_positions = random.sample(available_positions, num_loot)
            
            # Place "💰" emojis on the map
            for i, j in loot_positions:
                random_loot = random.choice(self.random_loot_point)
                map_data[i][j] = random_loot
            
            return map_data
        except Exception as e:
            loggy.error(f"Failed to place '💰' emojis on the map: {e}")
            return

    async def place_resource_emojis(self, map_data, num_rock):
        try:
            # Get all possible positions for placing "🪨"
            available_positions = [(i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell in self.paths]
            
            if num_rock > len(available_positions):
                raise ValueError("Number of '🪨' emojis to place exceeds the available positions.")
            
            # Randomly select positions to place "🪨"
            rock_positions = random.sample(available_positions, num_rock)
            
            # Place "🪨" emojis on the map
            for i, j in rock_positions:
                random_rock = random.choice(self.raw_resources)
                map_data[i][j] = random_rock
            
            return map_data
        except Exception as e:
            loggy.error(f"Failed to place '🪨' emojis on the map: {e}")
            return



    def get_default_map(self):
        # Grabs default Open map from RPG_Maps
        self._player.map = unbound.default_map
        return self._player.map


    # def check_for_other_players(self, x, y):
    #     """
    #     Checks if the position (x, y) is occupied by another player's token.

    #     Args:
    #         x (int): The x-coordinate of the map position.
    #         y (int): The y-coordinate of the map position.

    #     Returns:
    #         str: The player1_did (Discord ID) of the encountered player, or None if empty or not a player token.
    #     """
    #     try:
    #         # Retrieve the token at the specified position
    #         token = self._player.map['map'][x][y]
    #         # print(f"Token from map: {token} (type: {type(token)})")
    #         # print(f"Player tokens: {self.player_tokens}")

    #         # Check if the token exists in the player tokens dictionary
    #         # if token in self.player_tokens:
    #         #     return self.player_tokens[token]  # Return the player1_did
    #         # else:
    #         #     print(f"Token '{token}' does not belong to any player.")
    #         #     return None
    #     except IndexError:
    #         print(f"Invalid map coordinates: ({x}, {y})")
    #         return None
    #     except Exception as e:
    #         print(f"Error during token lookup: {e}")
    #         return None


    async def move_player(self, ctx, private_channel,  direction, rpg_msg, deferred=False):
        # from ai import rpg_movement_ai_message
        self.warp_active = False
        # if not deferred:
        #     await ctx.defer()
        #     deferred = True
        interaction_points = self.interaction_points
        x, y = self._player.player_position
        start_x = x
        start_y = y
        new_x, new_y = x, y

        player_moved = False
        player_action = False
        player_warped = False
        # self.fishing = False
        # self.loot_drop = False
        if direction in ["5","6","7","8","9"]:
            player_warped = True

        self.direction = "up"
        cardinal = "in front of you"
        if direction == "2" and x >= 0:#up
            player_moved = True
            new_x -= 1
        elif direction == "3" and x < len(self._player.map['map']):#down
            cardinal = "behind you"
            player_moved = True
            new_x += 1
        elif direction == "1" and y >= 0:#left
            cardinal = "to your left"
            player_moved = True
            new_y -= 1
        elif direction == "4" and y < len(self._player.map['map'][0]):#right
            cardinal = "to your right"
            player_moved = True
            new_y += 1       
        
        if direction == "Q":
            self.moving = False
            self.adventuring = False
            self.previous_moves.append("🏁 Adventure has ended!")
            #self._player.map['map'][x][y] = f"{self._player.standing_on}"
            currency_modifier = self.rpg_universe_level_check()
            gold_to_coin = self.player_gold
            await crown_utilities.bless(gold_to_coin, self.player1_did)
            if self.player_gems > 0:
                gems_earned = self.player_gems
                universe_to_add_gems = self.universe
                self.player1.save_gems(universe_to_add_gems, gems_earned)
            
            embedVar = Embed(title=f"🗺️ | {self.universe} Adventure Ended!", description=textwrap.dedent(f"""
                """))           
            embedVar.set_footer(text=f"🗺️ | Reach the end of the map to complete the adventure and earn currency Modifiers! [{currency_modifier}x]")

            await rpg_msg.edit(embed=embedVar,components=[])
            paginator = await self.leave_adventure_embed(ctx)
            await paginator.send(ctx)
            
        elif direction == "0":
            self.moving = False
            player_action = True
            self.warp_active = True
            self.previous_moves.append("👀 Checking Nearby...")
            self.closest_warp_points = self.get_closest_warp_points(self._player.player_position)
            if self.above_position in self.world_interaction_buttons:
                cardinal = "⬆️ In front of you"
                self.previous_moves.append(f"{cardinal} there is a {self._player.map['map'][x-1][y]}{get_emoji_label(self._player.map['map'][x-1][y])}!")
            if self.below_position in self.world_interaction_buttons:
                cardinal = "⬇️ Behind you"
                self.previous_moves.append(f"{cardinal} there is a {self._player.map['map'][x+1][y]}{get_emoji_label(self._player.map['map'][x+1][y])}!")
            if self.left_position in self.world_interaction_buttons:
                cardinal = "⬅️ On your left"
                self.previous_moves.append(f"{cardinal} there is a {self._player.map['map'][x][y-1]}{get_emoji_label(self._player.map['map'][x][y-1])}!")
            if self.right_position in self.world_interaction_buttons:
                cardinal = "➡️ On your right"
                self.previous_moves.append(f"{cardinal} there is a {self._player.map['map'][x][y+1]}{get_emoji_label(self._player.map['map'][x][y+1])}!")
            if self._player.standing_on in self.world_interaction_buttons:
                self.previous_moves.append(f"You standing on a {self._player.standing_on}{get_emoji_label(self._player.standing_on)}!")
        elif direction == "u" or direction == "d" or direction == "l" or direction == "r" or direction == "s":
            player_action = True
            if direction == "u":
                npc = self.above_position
                await self.rpg_action_handler(ctx, private_channel, self._player.player_position, npc, (x-1, y), direction)
            if direction == "d":
                npc = self.below_position
                await self.rpg_action_handler(ctx, private_channel, self._player.player_position, npc, (x+1, y), direction)
            if direction == "l":
                npc = self.left_position
                await self.rpg_action_handler(ctx, private_channel, self._player.player_position, npc, (x, y-1), direction)
            if direction == "r":
                npc = self.right_position
                await self.rpg_action_handler(ctx, private_channel, self._player.player_position, npc, (x, y+1), direction)
            if direction == "s":#standing on
                npc = self._player.standing_on
                await self.rpg_action_handler(ctx, private_channel, self._player.player_position, npc, (x, y))
            self.moving = False
        # Update map with new player position
        if player_moved:
            # print("Player moved to:", new_x, new_y, "There is a", self.map[new_x][new_y], "there.")
            # print("Starting position:", self._player.player_position)
            # After player movement and before ending the turn, call the new function

            if new_x < 0 or new_x >= len(self._player.map['map']) or new_y < 0 or new_y >= len(self._player.map['map'][0]):
                map_change = await self.change_map(direction, (new_x, new_y))
                await self.place_emojis()
                if not map_change:
                    self.previous_moves.append(f"(🚫) You can't leave this area yet!")
                    self._player.player_position = (x, y)  # Keep the player in the same position
                else:
                    if self.mission_type == "EXPLORE":
                        await self.increment_mission_count(ctx, private_channel)
            else:
                self._player.above_position = self._player.map['map'][new_x - 1][new_y] if new_x > 0 else None
                self._player.below_position = self._player.map['map'][new_x + 1][new_y] if new_x < len(self._player.map['map']) - 1 else None
                self._player.left_position = self._player.map['map'][new_x][new_y - 1] if new_y > 0 else None
                self._player.right_position = self._player.map['map'][new_x][new_y + 1] if new_y < len(self._player.map['map'][0]) - 1 else None

                await self.move_dynamic_emojis(ctx, private_channel, self._player.player_position)
                self._player.map_position = (new_x, new_y)


                # Make a 30% chance of encountering a VS emoji when moving
                if random.randint(1, 100) <= 30 and self._player.map['map'][x][y] == f"{self.player_token}":
                    # Check for VS emojis within a 2-cell radius
                    vs_positions = [
                        (i, j) for i in range(max(0, x-2), min(len(self._player.map['map']), x+3))
                        for j in range(max(0, y-2), min(len(self._player.map['map'][0]), y+3))
                        if self._player.map['map'][i][j] == "🆚"
                    ]

                    if vs_positions:
                        # Find the closest VS emoji
                        closest_vs = min(vs_positions, key=lambda pos: abs(pos[0] - x) + abs(pos[1] - y))
                        vs_x, vs_y = closest_vs

                        # Store the terrain the VS was on
                        original_terrain = self._player.standing_on if self._player.map['map'][vs_x][vs_y] == "🆚" else self._player.map['map'][vs_x][vs_y]

                        # Move the VS emoji to the closest walkable cell near the player
                        adjacent_cells = [
                            (i, j) for i in range(max(0, x-1), min(len(self._player.map['map']), x+2))
                            for j in range(max(0, y-1), min(len(self._player.map['map'][0]), y+2))
                            if self._player.map['map'][i][j] in [self._player.standing_on, "🟩", "🟫", "🟨", "⬜", "🟪"]  # Add other walkable terrains as needed
                        ]

                        if adjacent_cells:
                            new_vs_pos = min(adjacent_cells, key=lambda pos: abs(pos[0] - x) + abs(pos[1] - y))
                            self._player.map['map'][vs_x][vs_y] = original_terrain
                            self._player.map['map'][new_vs_pos[0]][new_vs_pos[1]] = "🆚"
                            self.encounter_position = new_vs_pos[0], new_vs_pos[1]
                            #print(f"VS emoji moved from {vs_x, vs_y} to {new_vs_pos}")
                            # Start the encounter
                            self.previous_moves.append(f"(🆚) An enemy approaches!")
                            await self.encounter_handler(ctx, private_channel, "🆚", new_vs_pos)
                            self.encounter = True
                            await self.create_rpg_battle(ctx, private_channel)
                            if self.combat_victory:
                                drop = random.choice(self.remains)
                                self._player.map['map'][new_vs_pos[0]][new_vs_pos[1]] = drop
                                self.previous_moves.append(f"(🏆) You defeated the enemy!")
                                self.previous_moves.append(f"(👀) Check Nearby to loot! [{drop}!]")
                                # await self.get_player_sorroundings()
                            return  # End the function here to avoid processing the rest of the handler
            



                if self._player.map['map'][new_x][new_y] in self.passable_points:  # Only move to open paths
                    self._player.map['map'][x][y] = f"{self._player.standing_on}"  # Reset old position
                    if (new_x, new_y) == self.starting_position:
                        self.previous_moves.append(f"(🏠) You are back at the starting position.")
                    self._player.standing_on = self._player.map['map'][new_x][new_y]
                    self._player.map['map'][new_x][new_y] = f"{self.player_token}"  # New position
                    self._player.player_position = (new_x, new_y)
                
                    # movement_msg = await rpg_movement_ai_message(self.player1_card_name, self.player_card_data.universe, direction, self.map[x-1][y], self.map[x+1][y], self.map[x][y-1], self.map[x][y+1])
                    # self.previous_moves.append(movement_msg)
                elif self._player.map['map'][new_x][new_y] in self.open_door:  # Can't move to doors
                    self.previous_moves.append(f"({self.open_door}) Moving into the next room {cardinal}")
                    next_map = await self.change_map(direction, (new_x, new_y))
                    await self.place_emojis()
                    if not next_map:
                        self.previous_moves.append(f"(🚫) You can't leave this area yet!")
                        self._player.player_position = (x, y)
                    
                    #Create action to generate a randomly generated new map for the next room create a linked list to store the previous map and the new map and connect the entrance via the door

                    # self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.walls:  # Can't move to walls
                    self.previous_moves.append(f"(🚫) There is a wall {cardinal}...")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] == "🔎":
                    self.previous_moves.append(f"(🔎) Investigation Quest Complete!")
                    x, y = self.quest_giver_position
                    self._player.map['map'][x][y] = f"🗝️"
                    self._player.quest_complete += 1
                    if self.mission_type == "INVESTIGATION":
                        await self.increment_mission_count(ctx, private_channel)
                    self.has_quest = False
                    await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "🃏", (new_x, new_y), direction)
                    self._player.map['map'][new_x][new_y] = f"{self._player.standing_on}"
                elif self._player.map['map'][new_x][new_y] in self.looted_trees:  # Can't move to looted trees
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a looted tree {cardinal}...if I had an Axe....")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.trees:  # Can't move to trees
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a tree {cardinal}...Try checking it out?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.resources:  # Can't move to resources
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a resource {cardinal}...maybe you can mine it?")
                elif self._player.map['map'][new_x][new_y] in self.moving_water:  # Can't move to water
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is moving water {cardinal}...wish I had a bridge...")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.grave:  # Can't move to grave
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a grave {cardinal}...maybe you can dig it?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.buildings:  # Can't move to buildings
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a building {cardinal}...maybe you can enter it?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.cars:  # Can't move to cars
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a car {cardinal}...maybe you can drive it?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.still_water:  # Can't move to water
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is still water {cardinal}...wish I had a bridge...or a pole?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] == "🎃":
                    self.previous_moves.append(f"(🎃) You found a pumpkin {cardinal}! Spooky!")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.merchants:  # Can't move to merchants
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a merchant {cardinal}...maybe you can buy something?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.wildlife:  # Can't move to wildlife
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a wildlife {cardinal}...maybe you can hunt it?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.doors:  # Can't move to doors
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a door {cardinal}...maybe you can open it?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.keys:  # Can't move to keys
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a key {cardinal}...maybe you can pick it up?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.items:  # Can't move to items
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is an item {cardinal}...maybe you can pick it up?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.remains:  # Can't move to remains
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a remains {cardinal}...maybe you can check it out?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.food:  # Can't move to food
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is food {cardinal}...maybe you can pick it up?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.combat_points:  # Can't move to combat points
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a combat point {cardinal}...maybe you can fight?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.mountains:  # Can't move to mountains
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a mountain {cardinal}...maybe there is an area you can climb?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.climable_mountains:  # Can't move to mountains
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a mountain.. I can see some rope! {cardinal}...if only I had climbing gear?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.bridges:  # Can't move to bridges
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a bridge {cardinal}...maybe you can cross it?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in self.civ_tokens:  # Can't move to civilians
                    self.previous_moves.append(f"({self._player.map['map'][new_x][new_y]}) There is a civilian {cardinal}...maybe you can talk to them?")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in crown_utilities.rpg_npc_emojis:
                    # encountered_player = self.check_for_other_players(new_x, new_y)
                    # if encountered_player:
                    #     print(f"You encountered {encountered_player}!")
                    self.previous_moves.append(f"(👻) There is a {crown_utilities.rpg_npc[self._player.map['map'][new_x][new_y]]} {cardinal}.")
                    self._player.player_position = self._player.player_position
                elif self._player.map['map'][new_x][new_y] in interaction_points:
                    self.previous_moves.append(f"(👀) You found a {self._player.map['map'][new_x][new_y]} {cardinal}!")
                    self._player.player_position = self._player.player_position
                elif not player_action:
                    self.previous_moves.append(f"(👁️‍🗨️) There is a {self._player.map['map'][new_x][new_y]} {cardinal}.")
                    self._player.player_position = self._player.player_position
                elif player_action and not player_moved:
                    return
                else:
                    self.previous_moves.append("Create action for this interaction!")
                if self._player.map['map'][new_x][new_y] not in self.open_door:
                    await self.get_player_sorroundings()

        if player_warped:
            await self.handle_warp_movement(ctx, int(direction)-5)
            await self.get_player_sorroundings()
            relative_direction = self.get_relative_direction(self._player.player_position,self.warp_point_position)
            await self.rpg_action_handler(ctx, ctx.channel, self._player.player_position, self.warp_target_type, self.warp_point_position, relative_direction)
            self.warp_active = False


    async def get_player_sorroundings(self, new_map = False):
        x, y = self._player.player_position
        self.above_position = self._player.map['map'][x-1][y] if x-1 >= 0 else None
        self.below_position = self._player.map['map'][x+1][y] if x+1 <= len(self._player.map['map']) - 1 else None
        self.left_position = self._player.map['map'][x][y-1] if y-1 >= 0 else None
        self.right_position = self._player.map['map'][x][y+1] if y+1 <= len(self._player.map['map'][0]) - 1 else None
    
    #movement
    def get_map_message(self):
        map_display = self.display_map()
        # flavor_text = "The adventurer roams the mysterious labyrinth. Each step brings new discoveries and hidden dangers."
        # self.previous_moves.append(flavor_text)
        return f"{map_display}"

    
    def set_rpg_options(self, left=None, right=None, up=None, down=None):
        self._talking_uuid = uuid.uuid4()
        movement_buttons = []
        action_buttons = []
        world_buttons = []
        encounter_buttons = []
        battle_buttons = []
        warp_buttons = []
        options = ["Q", "0", "1", "2", "3", "4"]
        left = self.left_position
        right = self.right_position
        up = self.above_position
        down = self.below_position
        if self.talking_encounter:
            encounter_buttons = [
                # Create buttons A and B for the player to choose from
                Button(
                    style=ButtonStyle.BLUE,
                    label="Option A",
                    custom_id=f"{self._talking_uuid}|A"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="Option B",
                    custom_id=f"{self._talking_uuid}|B"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="Option C",
                    custom_id=f"{self._talking_uuid}|C"
                )
            ]
        if self.encounter  and not self.talking_encounter:
            encounter_buttons = [
                    Button(
                        style=ButtonStyle.BLUE,
                        label="💬 Talk",
                        custom_id="talk"
                    ),
                    Button(
                        style=ButtonStyle.GREEN,
                        label="🆚 Fight",
                        custom_id="fight"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="💨Run",
                        custom_id="run"
                    )
        ]
        
        if not self.encounter and not self.talking_encounter:
            #Add token movement buttons
            movement_buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="⬅️Left",
                    custom_id=f"{self._uuid}|1"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="⬆️Up",
                    custom_id=f"{self._uuid}|2"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="⬇️Down",
                    custom_id=f"{self._uuid}|3"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="➡️Right",
                    custom_id=f"{self._uuid}|4"
                )
            ]
            #Add Basic Action Buttons Jump and Climb will be added if you have the skill
            action_buttons = [
                Button(
                    style=ButtonStyle.GREEN,
                    label="👀Check Nearby",
                    custom_id=f"{self._uuid}|0"
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="Save & Quit",
                    custom_id=f"{self._uuid}|Q"
                ),
            ]

            #Add world interaction Buttons
            if left and left in self.world_interaction_buttons:
                v_label=f"{self.left_position}" 
                if left in self.rpg_npc:
                    v_label = f"👻{crown_utilities.rpg_npc[self.left_position]}"
                if left in self.gold:
                    v_label = f"🪙Gold"
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=v_label,
                        custom_id=f"{self._uuid}|l"
                    )
                )
            if right and right in self.world_interaction_buttons:
                v_label = f"{self.right_position}"
                if right in self.rpg_npc:
                    v_label = f"👻{crown_utilities.rpg_npc[self.right_position]}"
                if right in self.gold:
                    v_label = f"🪙Gold"
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=v_label,
                        custom_id=f"{self._uuid}|r"
                    )
                )
            if up and up in self.world_interaction_buttons:
                v_label = f"{self.above_position}"
                if up in self.rpg_npc:
                    v_label = f"👻{crown_utilities.rpg_npc[self.above_position]}"
                if up in self.gold:
                    v_label = f"🪙Gold"
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=v_label,
                        custom_id=f"{self._uuid}|u"
                    )
                )
            if down and down in self.world_interaction_buttons:
                v_label = f"{self.below_position}"
                if down in self.rpg_npc:
                    v_label = f"👻{crown_utilities.rpg_npc[self.below_position]}"
                if down in self.gold:
                    v_label = f"🪙Gold"
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=v_label,
                        custom_id=f"{self._uuid}|d"
                    )
                )
        
            #Add Warp Buttons
            if self.warp_active:
                warp_points = self.get_closest_warp_points(self._player.player_position)
                for i, point in enumerate(warp_points):
                    v_label=f"{point['type']}{emoji_labels[point['type']]}"
                    if point['type'] in self.rpg_npc:
                        v_label = f"👻{crown_utilities.rpg_npc[point['type']]}"
                    warp_buttons.append(
                        Button(
                            style=ButtonStyle.GRAY,
                            label=v_label,
                            custom_id=f"{self._uuid}|{i+5}"
                        )
                    )
                    self.active_warp_points.append(warp_points)

        if self.adventuring:
            self.movement_buttons = movement_buttons
            self.action_buttons = action_buttons
            self.world_buttons = world_buttons
            self.encounter_buttons = encounter_buttons
            self.warp_buttons = warp_buttons
        else:
            return
                 
    
    async def rpg_player_move_embed(self, ctx, private_channel, rpg_msg=None):
        import ai
        ai_area_msg = None
        """
        Displays the player move embed.

        Parameters:
        - ctx: The context object for the current command.
        - battle_config: Configuration object for the battle.
        - private_channel: The private channel for the battle.
        - battle_msg: The message object for the battle.

        Returns:
        Tuple: The updated battle message and the components used in the embed.

        Steps:
        1. Get the battle positions of players, cards, titles, and arms.
        2. Configure the start of moves for the battle.
        3. Create action rows for battle buttons, utility buttons, and co-op buttons (if it's co-op mode).
        4. Set battle arm messages and stat icons for the turn player's card and partner player's card (if it's co-op mode).
        5. Determine the components to be used in the embed based on the game mode.
        6. Set the footer text for the embed.
        7. Create the embed with the previous moves, current turn information, image, and thumbnail.
        8. If it's a performance turn, add the performance header and moveset to the embed.
        Otherwise, set the author and add the instruction to select a move.
        9. Delete the previous battle message with a delay and sleep for 2 seconds.
        10. If it's not a performance turn, attach the card image to the message.
        11. Send the updated battle message with the embed and components.
        12. Return the updated battle message and components as a tuple.
        """     
        if not self.moving:
            current_map = self.display_map()
        
        if not self.encounter:
            movement_action_row = ActionRow(*self.movement_buttons)
            rpg_action_row = ActionRow(*self.action_buttons)
            components = [movement_action_row, rpg_action_row]
        else:
            components = []
        if len(self.world_buttons) > 0 and self.adventuring:
            world_action_row = ActionRow(*self.world_buttons)
            components.append(world_action_row)

        if self.warp_active and self.adventuring:
            warp_action_row = ActionRow(*self.warp_buttons)
            components.append(warp_action_row)

        equipment_message = ""
        currency_message = ""
        skill_message = ""
        if len(self.player_inventory) > 0:
            self.inventory_active = True
            equipment_message = "__[🎒]Your Equipment__"
            for item in self.player_inventory:
                equipment_message += f"\n|{item['USE']} {item['ITEM']}"
        if self.player_gold > 0 or self.player_gems > 0:
            self.currency_active = True
            if self.player_gold > 0:
                currency_message += f"\n|{self.get_gold_icon(self.player_gold)}{self.player_gold:,} Gold"
            if self.player_gems > 0:
                currency_message += f"\n|{self.get_gem_icon(self.player_gems)}{self.player_gems:,} Crystals"
        if len(self.player_skills) > 0:
            self.skills_active = True 
            for skill in self.player_skills:
                skill_message += f"|{skill}"
        rpg_map_embed = self.get_map_message()
        
        embedVar = Embed(title=f"[🌎]Exploring: {self._player.map['map_name']}",description=f"**[🗺️]** *{self._player.map['map_area']}*", color=0xFFD700)
        print(self.mission_message)
        embedVar.set_author(name=f"Level {self._player.map_level} Adventure - 🎖️{self.mission_message} ({self._player.mission_count}/{self._player.mission_requirements})", icon_url=f"{self.player1.avatar}")
        
        
        if self.inventory_active:
            embedVar.add_field(name=f"**[🎒]Inventory**", value=equipment_message or "No items in inventory", inline=False)
        if self.currency_active:
            embedVar.add_field(name=f"**[👛]Currency**", value=currency_message or "No currency available", inline=False)
        if self.skills_active:
            embedVar.add_field(name=f"**[🥋]Skills**", value=skill_message or "No skills acquired", inline=False)
        
        # if any([self.above_position, self.below_position, self.left_position, self.right_position, self.last_move]):
        #     # Prepare common arguments
        #     common_args = [
        #         self.player1_card_name,
        #         self.universe,
        #         self.last_move,
        #         self._player.standing_on,
        #         self._player.map["map_name"],
        #         get_emoji_label(self.above_position),
        #         get_emoji_label(self.below_position),
        #         get_emoji_label(self.left_position),
        #         get_emoji_label(self.right_position)
        #     ]

        #     # Check for last_thought
        #     if self.last_thought:
        #         common_args.append(self.last_thought)
        #         if self.train_of_thought:
        #             common_args.append(self.train_of_thought)
        #         else:
        #             self.train_of_thought = self.last_thought
        #     # Make the single call
        #     ai_area_msg = await ai.rpg_movement_ai_message(*common_args)
        # if ai_area_msg:
        #     embedVar.add_field(name=f"**[💭]{self.player1_card_name}'s Thoughts**", value=f"*{ai_area_msg}*", inline=False)
        #     self.last_thought = ai_area_msg

        embedVar.add_field(name=f"[{self.player_token}]My Player Token\n[❤️]{self.player_health:,} HP", value=f"**[{self.standing_on}]** *Standing On {get_ground_type(self._player.standing_on)}*\n{rpg_map_embed}", inline=False)
        # embedVar.set_thumbnail(url=self.player_card_image)
        embedVar.set_footer(text=self.get_previous_moves_embed() or "No previous moves")

        if rpg_msg:
            await rpg_msg.edit(embed=embedVar, components=components)
            self._rpg_msg = rpg_msg
            return rpg_msg, components
        if not rpg_msg:
            return embedVar, components

    
    async def rpg_move_handler(self, ctx, private_channel, button_ctx, rpg_msg):
        """
        Handles the player moves in the RPG.

        Parameters:
        - ctx: The context object for the current command.
        - private_channel: The private channel for the RPG.
        - button_ctx: The context object for the button interaction.
        - rpg_msg: The message object for the RPG.

        1. Check the custom ID of the button context to determine the selected move.
        2. Call the move_player function to update the player positions on the map.
        3. Await the updated map.
        """
        if self.adventuring:
            custom_id = button_ctx.ctx.custom_id
            move = custom_id.split("|")[1]
            await self.move_player(ctx,private_channel,  move, rpg_msg)
            if self.adventuring:
                self.set_rpg_options()
                self.moving = True
                await asyncio.sleep(1)
                if self.map_change:
                    await self.rpg_player_move_embed(ctx, private_channel, rpg_msg)
                    self.map_change = False
                    return
                #await self.rpg_player_move_embed(ctx, private_channel, rpg_msg)
                return
        
    #Interactions
    async def rpg_action_handler(self,ctx, private_channel, player_position, npc, npc_position, direction=None):
        x, y = player_position
        self.encounter_position = npc_position
        if npc in self.interaction_points:
            if npc in self.items:
                random_number = random.randint(1, 100)
                if npc == "🎒":
                    self.previous_moves.append(f"(🎒) You found lost inventory!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                    gold_found = random.randint(10, 250)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(👛) You found a bag of {gold_found} gold!")
                    if random_number <= 25:
                        gold_found = random.randint(250, 500)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(🎁) You found a treasure chest! [+🪙{gold_found}]")
                    elif random_number <= 75:
                        self.previous_moves.append(f"(🎁) There's alot here! You found a 💰!")
                        gold_found = random.randint(50, 500)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(💰) You found a Sack o' Gold +🪙{gold_found}!")
                elif npc == "🎁":
                    gold_found = random.randint(200, 500)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(🎁) You found a treasure chest! [+🪙{gold_found}]")
                    if random_number <= 10:
                        self.previous_moves.append(f"(🎁) There is a hidden compartment!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                    elif random_number <= 50:
                        gold_found = random.randint(25, 150)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(🎁) This chest is pretty full! You found another 👛! [+🪙{gold_found}]")
                elif npc == "💰":
                    gold_found = random.randint(25, 500)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(💰) You gained {gold_found} gold!")
                    if random_number <= 25:
                        gold_found = random.randint(5, 50)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(💰) Something hidden deep in the bag...You found a 👛bag of {gold_found} gold!")
                    elif random_number <= 50:
                        gold_found = random.randint(1, 10)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(💰) Something else hidden in the bag...You found 🪙{gold_found} gold!")
                elif npc == "👛":
                    gold_found = random.randint(5, 50)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(👛) You found a bag of {gold_found} gold!")
                elif npc == self.gold or npc == "🪙":
                    gold_found = random.randint(1, 10)
                    if npc == self.gold:
                        gold_found = gold_found * random.randint(1, 10)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"({self.coin_item}) You found {gold_found} gold!")
                if self.mission_type == "COLLECT_GOLD":
                    await self.increment_mission_count(ctx, private_channel)
                # if not self.loot_drop:
                    #self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}" #upadte map with new position
                self.loot_drop = False
            elif npc in self.drops:
                success = None
                if npc == "🎴":
                    all_available_drop_cards = db.querySpecificDropCards(self.universe)
                    cards = [x for x in all_available_drop_cards]
                    selected_card = crown_utilities.create_card_from_data(random.choice(cards))
                    success = self.player1.save_card(selected_card, True)
                    if success:
                        self._player.card_drops.append(f"|🎴{selected_card.name}")
                        self.previous_moves.append(f"You found 🎴{selected_card.name}!")
                # if npc == "🎗️":
                #     title_drop = db.get_random_title({"UNIVERSE": self.universe}, self.player1)
                #     message, success = self.player1.save_title(self.universe, title_drop)
                #     if success:
                #         self._player.title_drops.append(f"|🎗️{title_drop}**")
                #         self.previous_moves.append(f"You found 🎗️{title_drop}!")
                #     else:
                #         self.previous_moves.append(f"You found 🎗️{title_drop} but you already have the maximum amount!!")
                if npc == "🦾":
                    arm_query = {'UNIVERSE': self.universe, 'DROP_STYLE': "TALES", 'ELEMENT': ""}
                    arm_drop = db.get_random_arm(arm_query, self.player1)
                    success = self.player1.save_arm(arm_drop, True)
                    if success:
                        self._player.arm_drops.append(f"|🦾{arm_drop}")
                        self.previous_moves.append(f"You found 🦾{arm_drop}!")
                    else:
                        self.previous_moves.append(f"You found 🦾{arm_drop} but you already have the maximum amount!!")
                if npc == "🧬":
                    summon_query = {'UNIVERSE': self.universe, 'DROP_STYLE': "TALES"}
                    summon_drop_name = db.get_random_summon_name(summon_query)
                    summon_info = db.querySummon({'PET': summon_drop_name})
                    summon_drop = crown_utilities.create_summon_from_data(summon_info)
                    success = self.player1.save_summon(summon_drop)
                    if success:
                        self._player.summon_drops.append(f"|🧬{summon_drop.name}")
                        self.previous_moves.append(f"You found 🧬{summon_drop.name}!")
                    else:
                        self.previous_moves.append(f"You found 🧬{summon_drop.name} but you already have the maximum amount!!")
                if npc == "🆙":  
                    self.previous_moves.append(f"(🆙) You found a XP Boost! Full Heal!")
                    self.player_health = self.player_max_health
                    await crown_utilities.cardlevel(self.user, "RPG", 1)
            elif npc in self.wildlife:
                wildlife_msg = ""
                random_number = random.randint(1, 100)
                self.previous_moves.append(f"({npc}) You encountered a {emoji_labels[npc]}!")
                if random_number <= 33:
                    self.previous_moves.append(f"({npc}) The {emoji_labels[npc]} ran off...")
                    self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}"
                elif random_number <= 75:
                    #You successfully hunt the animal and gain some food
                    self.previous_moves.append(f"({npc}) You successfully hunt the {emoji_labels[npc]}!")
                    if self.mission_type == "HUNT":
                        await self.increment_mission_count(ctx, private_channel)
                    if npc == "🦌":
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🥩", npc_position, direction)
                    elif npc == "🐇":
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🥕", npc_position, direction)
                    elif npc == "🦊":
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🍖", npc_position, direction)
                    elif npc in ["🐍", "🦂","🦇"]:
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🦴", npc_position, direction)
                else:
                    #The animal is friendly and leaves a item for the player using the drop system
                    self.previous_moves.append(f"({npc}) The {emoji_labels[npc]} left a gift!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🃏", npc_position, direction)
            elif npc in self.remains:
                if npc == "💀":
                    self.previous_moves.append(f"(💀) You found a lootable body")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                if npc == "🦴":
                    self.previous_moves.append(f"(🦴) You found some remains")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎲", npc_position, direction)
                    #learn Skill
                if npc == "☠️":
                    self.previous_moves.append(f"(☠️) You found a skeleton!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🃏", npc_position, direction)
                    #find book and learn skill
                self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}"
            elif npc in self.food:
                health_msg = ""
                if npc == "🥩":
                    health_gained = round(self.player_max_health * .50)
                    health_msg = f"{health_gained}HP"
                    self.player_health += health_gained
                    if self.player_health >= self.player_max_health:
                        self.player_health = self.player_max_health
                        health_msg = "Max Health!"
                    self.previous_moves.append(f"(🥩) You found a raw steak!  [{health_gained}]")
                if npc == "🍖":
                    health_gained = round(self.player_max_health * .25)
                    health_msg = f"{health_gained}HP"
                    self.player_health += health_gained
                    if self.player_health >= self.player_max_health:
                        self.player_health = self.player_max_health
                        health_msg = "Max Health!"
                    self.previous_moves.append(f"(🍖) You found a roast! [{health_gained}]")
                if npc == "🥕":
                    health_gained = round(self.player_max_health * .10)
                    health_msg = f"{health_gained}HP"
                    self.player_health += health_gained
                    if self.player_health >= self.player_max_health:
                        self.player_health = self.player_max_health
                        health_msg = "Max Health!"
                    self.previous_moves.append(f"(🥕) You found a carrot! [{health_gained}]")
                elif npc in self.player_inventory:
                    self.previous_moves.append(f"({npc}) added to inventory")
                    food_found = False
                    # for item in self.player_inventory:
                    #     if item['ITEM'] == npc:
                    #         item['USE'] += 1
                    #         food_found = True
                    #         break
                    # if not food_found:
                    #     self.player_inventory.append({'ITEM': npc, 'USE': 1})
                self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}"
            elif npc in self.keys:
                self.previous_moves.append(f"(🗝️) You found a key!")
                key_found = False
                for item in self.player_inventory:
                    if item['ITEM'] == npc:
                        item['USE'] += 1
                        key_found = True
                        break
                if not key_found:
                    self.player_inventory.append({'ITEM': npc, 'USE': 1})
                self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}"
            elif npc in self.doors:
                for item in self.player_inventory:
                    if item['ITEM'] == "🗝️":
                        if item['USE'] > 0:
                            self.previous_moves.append(f"(🚪) You unlocked the door!")
                            item['USE'] -= 1
                            if item['USE'] <= 0:
                                self.player_inventory.remove(item)
                            self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self.open_door}"
                        break
                else:
                    self.previous_moves.append(f"(🚪) You need a key to unlock this door!")
            elif npc in self.bridges:
                await self.cross_bridge(ctx, private_channel, player_position, npc, npc_position, direction)
            elif npc in self.moving_water:
                self.previous_moves.append(f"(🌊) You can't swim in moving water! If only you had a boat...But maybe there is a bridge?")
            elif npc in self.still_water:
                if self.fishing_pole:
                    self.previous_moves.append(f"(🎣) You cast your line and found some loot!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎲", npc_position, direction)
                    self.loot_drop = True
                else:
                    self.previous_moves.append(f"(🟦) You can't swim yet...If only you had a pole??")
            elif npc in self.trees:
                self.previous_moves.append(f"({npc}) You searched a tree!")
                if self._player.map['map'][npc_position[0]][npc_position[1]] in self.looted_trees:
                    self.previous_moves.append(f"({npc}) This tree has been looted...if only you had an axe...")
                elif random.random() < 0.33:  # 50% chance
                    random_item = random.choice(self.items)
                    if random_item == "🎒":
                        self.previous_moves.append(f"(🎒) You found lost loot!")
                        
                    elif random_item == "🎁":
                        self.previous_moves.append(f"(🎁) You found a treasure chest!")
                    elif random_item == "💰":
                        gold_found = random.randint(10, 100)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(💰) You gained {gold_found} gold!")
                        if self.mission_type == "COLLECT_GOLD":
                            await self.increment_mission_count(ctx, private_channel)
                    await self.rpg_action_handler(ctx, private_channel, player_position, random_item, npc_position, direction)
                else:
                    self.previous_moves.append(f"(🆚) You are under attack!")
                    # self.encounter = True
                    # self.encounter_position = npc_position
                    await self.trigger_battle(ctx, private_channel, npc)
                    if self.combat_victory:
                        self.remove_combatant()
                        self.previous_moves.append(f"({npc}) You loot the body!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "👛", npc_position, direction)
                self._player.map['map'][npc_position[0]][npc_position[1]] = f"🌴"
            elif npc in self.cactus:
                self.previous_moves.append(f"({npc}) You searched a cactus!")
                if self._player.map['map'][npc_position[0]][npc_position[1]] in self.looted_cactus:
                    self.previous_moves.append(f"({npc}) This cactus has been looted...if only you had a knife...")
                elif random.random() < 0.33:  # 50% chance
                    random_item = random.choice(self.items)
                    if random_item == "🎒":
                        self.previous_moves.append(f"(🎒) You found lost loot!")
                    elif random_item == "🎁":
                        self.previous_moves.append(f"(🎁) You found a treasure chest!")
                    elif random_item == "💰":
                        gold_found = random.randint(10, 100)
                        self.player_gold += gold_found
                        self.previous_moves.append(f"(💰) You gained {gold_found} gold!")
                        if self.mission_type == "COLLECT_GOLD":
                            await self.increment_mission_count(ctx, private_channel)
                    await self.rpg_action_handler(ctx, private_channel, player_position, random_item, npc_position, direction)
            elif npc in self.climable_mountains:
                if self.climber:
                    self.previous_moves.append(f"({npc}) You climbed the mountain!")
                    random_number = random.randint(1, 100)
                    if random_number <= 25:
                        self.previous_moves.append(f"({npc}) You found a hidden cave!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                    else:
                        self.previous_moves.append(f"({npc}) You found nothing...")
                    self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self.looted_mountain}"
                else:
                    self.previous_moves.append(f"({npc}) You can't climb the mountain...if only you had climbing gear...")
            elif npc in self.mountains:
                self.previous_moves.append(f"({npc}) You can't climb the mountain...if only you could fly...")
            elif npc in self.resources:
                miner_bonus = 0
                #get different amounts for diffrent resources
                miner_bonus_message = ""
                if self.pickaxe:
                    if self.miner:
                        miner_bonus = random.randint(100, 500)
                        miner_bonus_message = f"[⚒️+{miner_bonus} Gems!]"
                    gems_gained = random.randint(1,500) + miner_bonus
                    if npc in self.gems:
                        gems_gained = gems_gained * 2
                        self.previous_moves.append(f"({npc}) You found Raw Gems!")
                    else:
                        self.previous_moves.append(f"({npc}) You found Gemstone!")
                    self.player_gems += gems_gained
                    self.previous_moves.append(f"(⛏️) You mined 💎{gems_gained} Gems! {miner_bonus_message}")
                    if self.mission_type == "COLLECT_GEMS":
                        await self.increment_mission_count(ctx, private_channel)
                    # if not self.miner:
                    #     self.miner = True
                    #     self.previous_moves.append(f"You gained the Miner Skill! [⛏️]")
                    self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}"
                else:
                    self.previous_moves.append(f"({npc}) Inspecting the stone you found a ⛏️Pickaxe!")
                    self.pickaxe = True
                    #self.player_inventory.append({'ITEM': "⛏️", 'USE': 1})
                    self.player_skills.append("⛏️")
            else:
                await self.encounter_handler(ctx, private_channel, npc, npc_position)
        elif npc == "🔎":
            self.previous_moves.append(f"(🔎) Investigation Quest Complete!")
            self.quest_message_list.append(f"(🔎) Investigation Quest Complete!")
            if self.mission_type == "INVESTIGATION" or self.mission_type == "QUEST":
                await self.increment_mission_count(ctx, private_channel)
            self.has_quest = False
            self.has_investigation = False
            x, y = self.quest_giver_position
            new_x, new_y = npc_position
            self._player.map['map'][x][y] = f"🗝️"
            await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "🃏", (new_x, new_y), direction)
            self._player.map['map'][new_x][new_y] = f"{self._player.standing_on}"
        elif npc in self.loot_rolls:#if not interactino then loot roll or combats
            if npc == "🎲":
                roll = random.randint(1, 6)
                if roll == 1:
                    gold_found = random.randint(1, 10)
                    self.player_gold += gold_found
                    if self.mission_type == "COLLECT_GOLD":
                        await self.increment_mission_count(ctx, private_channel)
                    self.previous_moves.append(f"({self.coin_item}) You got {gold_found} gold!")
                elif roll == 2:
                    gold_found = random.randint(5, 25)
                    self.player_gold += gold_found
                    if self.mission_type == "COLLECT_GOLD":
                        await self.increment_mission_count(ctx, private_channel)
                    self.previous_moves.append(f"(👛) You got a empty bag of {gold_found} gold!")
                elif roll == 3:
                    gold_found = random.randint(10, 50)
                    self.player_gold += gold_found
                    if self.mission_type == "COLLECT_GOLD":
                        await self.increment_mission_count(ctx, private_channel)
                    self.previous_moves.append(f"(👛) You got a full bag of {gold_found} gold!")
                elif roll == 4:
                    gold_found = random.randint(25, 100)
                    self.player_gold += gold_found
                    if self.mission_type == "COLLECT_GOLD":
                        await self.increment_mission_count(ctx, private_channel)
                    self.previous_moves.append(f"(💰) You got a bonus sack {gold_found} gold!")
                elif roll == 5:
                    gold_found = random.randint(50, 500)
                    self.player_gold += gold_found
                    if self.mission_type == "COLLECT_GOLD":
                        await self.increment_mission_count(ctx, private_channel)
                    self.previous_moves.append(f"(💰) You got a heavy sack of {gold_found} gold!")
                elif roll == 6:
                    self.previous_moves.append(f"(🔍) Checking their inventory....")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🃏", npc_position, direction)
            if npc == "🃏":
                random_number = random.randint(1, 100)
                if random_number <= 80:
                    #self.previous_moves.append(f"(🎁) You got a chest")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎁", npc_position, direction)
                else:
                    #self.previous_moves.append(f"(🎒) You got lost Inventory!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎒", npc_position, direction)
            if npc == "🎰":
                random_number = random.randint(1, 100)
                if random_number <= 1:
                    self.previous_moves.append(f"(🎰) You got a jackpot!")
                    gold_found = random.randint(100, 1000)
                    self.player_gold += gold_found
                    if self.mission_type == "COLLECT_GOLD":
                        await self.increment_mission_count(ctx, private_channel)
                    self.previous_moves.append(f"(💰) You gained {gold_found} gold!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎒", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎴", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎗️", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🦾", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🧬", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🆙", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                elif random_number <= 10:
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎗️", npc_position, direction)
                elif random_number <= 25:
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎴", npc_position, direction)
                elif random_number <= 45:
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🧬", npc_position, direction)
                elif random_number <= 75:
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🦾", npc_position, direction)
                else:
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🆙", npc_position, direction)
        elif npc in self.combat_points:
            self.encounter_position = npc_position
            await self.encounter_handler(ctx, private_channel,npc, npc_position)
            #After combat turn into remains based on combat type for additional loot rolls
            self.encounter = True
            #self.previous_moves.append(f"(🆚) Entering Encounter Mode!")
            if npc == "🥋":
                self.previous_moves.append(f"(🥋) You encountered a training dummy!")
                await self.create_rpg_battle(ctx, private_channel, tutorial=True)
            else:
                await self.create_rpg_battle(ctx, private_channel)
            if (npc == "⚔️" or npc == "🆚") and self.combat_victory:
                extra_loot_roll = random.randint(1, 100)
                if extra_loot_roll <= 25:
                    self.previous_moves.append(f"(🎲) You found a lootable body!")
                    drop = random.choice(self.remains)
                    self._player.map['map'][npc_position[0]][npc_position[1]] = drop
        else:
            await self.encounter_handler(ctx, private_channel, npc, npc_position)
        
        if self.combat_victory:
            #print("Combat victory was invoked")
            self.previous_moves.append(f"(✅) You defeated the enemy!")
            self._player.map['map'][npc_position[0]][npc_position[1]] = f"{self._player.standing_on}"
            self.combat_victory = False
            if npc in self.quest:
                self.previous_moves.append(f"(🎯) Target Eliminated!")
                self.quest_message_list.append(f"🎯 Target Eliminated")
                if self.mission_type == "QUEST":
                    await self.increment_mission_count(ctx, private_channel)
                self.has_quest = False
                self.my_quest = ""
                self.loot_drop = True
                self._player.quest_complete += 1
            self.player_atk_boost = False
            self.player_def_boost = False
            self.player_hp_boost = False
            self.remove_combatant()
            if self.mission_type in ["DEFEAT_ENEMIES", "DEFEAT_ALL_ENEMIES"]:
                await self.increment_mission_count(ctx, private_channel)
            await self.rpg_action_handler(ctx, private_channel, player_position, "🃏", npc_position, direction)

        await self.get_player_sorroundings()
    
    
    async def encounter_handler(self, ctx, private_channel, npc, npc_position=None):
        self._encounter = True
        random_number = random.randint(1, 100)
        if npc != "💫":
            self.previous_moves.append(f"(🆚) Entering Encounter Mode!")
            x, y = npc_position
            # encountered_player = self.check_for_other_players(x,y)
            # print(encountered_player)
            # if encountered_player:
            #     print(f"You encountered {encountered_player}!")
            #     # Optionally: Trigger PvP or other interaction

        if npc in self.merchants:
            await self.open_shop(ctx, private_channel, npc)
        elif npc in self.civ_tokens:
            if not self.has_quest:
                await self.generate_quest(ctx, private_channel, npc, npc_position)
            else:
                self.previous_moves.append(f"({self.my_quest}) You already have a quest!")
        elif npc in self.combat_points:
            if npc == "🥋":
                self.previous_moves.append(f"(🥋) You encountered a training dummy!")
                await self.create_rpg_battle(ctx, private_channel, tutorial=True)
            else:
                if npc == "🎯":
                    self.has_quest = True
                await self.create_rpg_battle(ctx, private_channel)
        else:
            if npc == "💫":
                x, y = self.encounter_position
                embedVar = Embed(title=f"[💬] You spend some time talking with {npc_position}, but before you go...", description=f"", color=0xf1c40f)
                self.previous_moves.append(f"(💬) You spend some time talking with {npc_position}, before you go...")
                random_number = random.randint(1, 100)
                if random_number <= 5:
                    self.previous_moves.append(f"(🆚) It's a trap! You are under attack!")
                    embedVar.add_field(name=f"[🆚)] You are under attack!", value=f"Prepare for battle!")
                    talk_msg = await private_channel.send(embed=embedVar)
                    await talk_msg.delete(delay=3)      
                    self.battling = True
                    await self.create_rpg_battle(ctx, private_channel)
                elif random_number <= 10:
                    self.previous_moves.append(f"(🧙) As you leave a magic merchant appears to sell you some items!")
                    embedVar.add_field(name=f"[🧙)] They have a shop!", value=f"Check out their wares!")
                    self.battling = False
                    self.encounter = False
                    await self.open_shop(ctx, private_channel, '🧙')
                    self._player.map['map'][x][y] = f"{self._player.standing_on}"
                elif random_number <= 50:
                    self.previous_moves.append(f"(🎁) They have a gift for you!")
                    embedVar.add_field(name=f"[🎁)] They have a gift for you!", value=f"Check out your new stuff!")
                    self.battling = False
                    self.encounter = False
                    await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "🎁", npc_position)
                    self._player.map['map'][x][y] = f"{self._player.standing_on}"
                elif random_number <= 90:
                    if not self.has_quest:
                        self.previous_moves.append(f"(🗺️) They have a quest for you!")
                        self.quest_message_list.append(f"({npc}) You have a quest!")
                        embedVar.add_field(name=f"[🗺️)] They have a quest for you!", value=f"Check out your new quest!")
                        await self.generate_quest(ctx, private_channel, npc, npc_position)
                    else:
                        self.previous_moves.append(f"({self.my_quest}) They give you some information about your quest!")
                        embedVar.add_field(name=f"[🗺️)] You already have a quest!", value=f"Check out your current quest!")
                    self.battling = False
                    self.encounter = False
                    await self.generate_quest(ctx, private_channel, self._player.player_position, '🆚', npc_position)
                elif random_number <= 100:
                    self.previous_moves.append(f"(🎰) They have a rare item for you!")
                    embedVar.add_field(name=f"[🎰)] They have a rare item for you!", value=f"Lets earn some loot!")
                    self.battling = False
                    self.encounter = False
                    await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "🎰", npc_position)
                    self._player.map['map'][x][y] = f"{self._player.standing_on}"
                talk_msg = await private_channel.send(embed=embedVar)
                await talk_msg.delete(delay=3)
            

    async def open_shop(self, ctx, private_channel, npc):
        # Logic to display the shop embed with buttons for purchasing items
        p_1 = random.randint(250, 500)
        p_2 = random.randint(250, 500)
        p_3 = random.randint(250, 500)
        if npc == "🏪":
            item1 = "🗡️"
            item2 = "🛡️"
            item3 = "💗"
        elif npc == "🧙":
            item1 = "🆙"
            item2 = "🦾"
            item3 = "🧬"
            p_1 = random.randint(400, 750)
            p_2 = random.randint(400, 900)  
            p_3 = random.randint(400, 1000)
        elif npc == "🕴️":
            item1 = "🎴"
            item2 = "🎗️"
            item3 = "🎰"
            p_1 = random.randint(1000, 2000)
            p_2 = random.randint(2000, 3000)
            p_3 = random.randint(1500, 2500)
        elif npc == "🏯":
            item1 = "⛏️"
            item2 = "🔨"
            item3 = "🎣"
            p_1 = random.randint(100, 250)
            p_2 = random.randint(100, 250)
            p_3 = random.randint(100, 250)
        elif npc == "🏥":
            item1 = "🍚"
            item2 = "🍛"
            item3 = "🍲"
            p_1 = random.randint(500, 750)
            p_2 = random.randint(680, 1000)
            p_3 = random.randint(1000, 1200)
        self.previous_moves.append(f"({npc}) You are interacting with a {get_emoji_label(npc)}!")
        shop_embed = Embed(title=f"{npc}{get_emoji_label(npc)} Shop", description=f"Choose your items to purchase:\n{self.get_gold_icon(self.player_gold)}{self.player_gold}\n", color=0xFFD700)
        # Add items to the shop based on the npc type
        equipment_message = ""
        for item in self.player_inventory:
            equipment_message += f"|{item['USE']} {item['ITEM']}"
        if self.player_inventory:
            shop_embed.add_field(name=f"**[🎒]My Inventory**", value=f"{equipment_message}")
        shop_embed.add_field(name="Items for Sale", value=f"1. {item1}{get_emoji_label(item1)} - {self.gold}{p_1}\n2. {item2}{get_emoji_label(item2)} - {self.gold}{p_2}\n3. {item3}{get_emoji_label(item3)} - {self.gold}{p_3}")
        components = [
            ActionRow(
                Button(style=ButtonStyle.GREEN, label=f"{item1}{get_emoji_label(item1)}", custom_id=f"buy|{item1}"),
                Button(style=ButtonStyle.GREEN, label=f"{item2}{get_emoji_label(item2)}", custom_id=f"buy|{item2}"),
                Button(style=ButtonStyle.GREEN, label=f"{item3}{get_emoji_label(item3)}", custom_id=f"buy|{item3}"),
                Button(style=ButtonStyle.RED, label="Cancel", custom_id="cancel|🚫")
            )
        ]
        shop_msg = await private_channel.send(embed=shop_embed, components=components)

        def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

        try:
            button_ctx  = await self.bot.wait_for_component(components=[components], timeout=300, check=check)
            await button_ctx.ctx.defer(edit_origin=True)
            custom_id = button_ctx.ctx.custom_id
            choice = custom_id.split("|")[1]

            purchase = False
            purchase_item = None
            stat_boost = False
            if choice == item1:
                if self.player_gold >= p_1:
                    self.player_gold -= p_1
                    purchase_item = item1
                    cost = p_1
                    if choice in self.healing_items:
                        health_gained = round(self.player_max_health * .33)
                        self.player_health += health_gained
                        self.player_health += health_gained
                        self.previous_moves.append(f"({npc}) You purchased {item1}{get_emoji_label(item1)} for {p_1} gold! (+250 HP)")
                        purchase = True
                    elif choice in self.skills:
                        for skill in self.player_skills:
                            if skill == item1:
                                purchase = False
                                self.previous_moves.append(f"({npc}) You already have the {item1}{get_emoji_label(item1)} skill!")
                                break
                            else:
                                purchase = True
                                self.player_skills.append(item1)
                                self.previous_moves.append(f"({npc}) You purchased the {item1}{get_emoji_label(item1)} skill for {p_1} gold!")
                                break          
                    elif choice in self.stat_boosts:
                        self.player_atk_boost = True
                        self.previous_moves.append(f"({npc}) You purchased the {item1}{get_emoji_label(item1)} boost for {p_1} gold!")
                    elif choice in self.drops:
                        self.previous_moves.append(f"({npc}) You purchased the {item1}{get_emoji_label(item1)} drop for {p_1} gold!")
                        self.loot_drop = True
                        await self.rpg_action_handler(ctx, private_channel, self._player.player_position, item1, None)               
                else:
                    self.previous_moves.append(f"({npc}) You don't have enough gold to purchase {item1}")
                    purchase = False
                await asyncio.sleep(1)
                await shop_msg.edit(components=[])
                await shop_msg.delete(2)


            if choice == item2:
                if self.player_gold >= p_2:
                    self.player_gold -= p_2
                    purchase_item = item2
                    cost = p_2
                    #Create method for adding items and their specific uses  and add to inventory
                    if choice in self.healing_items:
                        health_gained = round(self.player_max_health * .66)
                        self.player_health += health_gained
                        self.previous_moves.append(f"({npc}) You purchased {item2}{get_emoji_label(item2)} for {p_2} gold! (+500 HP)")
                    elif choice in self.skills:              
                        for skill in self.player_skills:
                            if skill == item2:
                                purchase = False
                                self.previous_moves.append(f"({npc}) You already have the {item2}{get_emoji_label(item2)} skill!")
                                break
                            else:
                                purchase = True
                                self.player_skills.append(item2)
                                self.previous_moves.append(f"({npc}) You purchased the {item2}{get_emoji_label(item2)} skill for {p_2} gold!")
                                break    
                    elif choice in self.stat_boosts:
                        self.player_def_boost = True
                        self.previous_moves.append(f"({npc}) You purchased the {item2}{get_emoji_label(item2)} boost for {p_2} gold!")
                    elif choice in self.drops:
                        self.previous_moves.append(f"({npc}) You purchased the {item2}{get_emoji_label(item2)} drop for {p_2} gold!")
                        self.loot_drop = True
                        await self.rpg_action_handler(ctx, private_channel, self._player.player_position, item2, None)                
                else:
                    self.previous_moves.append(f"({npc}) You don't have enough gold to purchase {item2}")
                await asyncio.sleep(1)
                await shop_msg.edit(components=[])
                await shop_msg.delete(2)

            
            if choice == item3:
                if self.player_gold >= p_3:
                    self.player_gold -= p_3
                    purchase_item = item3
                    cost = p_3
                    if choice in self.food:
                        missing_health_gained = self.player_max_health - self.player_health
                        self.player_health = self.player_max_health
                        self.previous_moves.append(f"({npc}) You purchased cooked {item3}{get_emoji_label(item3)} for {p_3} gold! (+{missing_health_gained} HP)")
                    elif choice in self.skills:
                        for skill in self.player_skills:
                            if skill == item3:
                                purchase = False
                                self.previous_moves.append(f"({npc}) You already have the {item3}{get_emoji_label(item3)} skill!")
                                break
                            else:
                                purchase = True
                                self.player_skills.append(item3)
                                self.previous_moves.append(f"({npc}) You purchased the {item3}{get_emoji_label(item3)} skill for {p_3} gold!")
                                break
                    elif choice in self.stat_boosts:
                        self.player_hp_boost = True
                        self.previous_moves.append(f"({npc}) You purchased the {item3}{get_emoji_label(item3)} boost for {p_3} gold!")
                    elif choice in self.drops:
                        self.previous_moves.append(f"({npc}) You purchased the {item3}{get_emoji_label(item3)} drop for {p_3} gold!")
                        self.loot_drop = True
                        await self.rpg_action_handler(ctx, private_channel, self._player.player_position, item3, None)
                    elif choice in self.loot_rolls:
                        self.loot_drop = True
                        self.previous_moves.append(f"({npc}) You purchased the {item3}{get_emoji_label(item3)} roll for {p_3} gold!")
                        await self.rpg_action_handler(ctx, private_channel, self._player.player_position, item3, None)
                    else:
                        purchase = False
                        self.previous_moves.append(f"({npc}) You can't purchase {item3}{get_emoji_label(item3)}!")
                else:
                    self.previous_moves.append(f"({npc}) You don't have enough gold to purchase {item3}")
                await asyncio.sleep(1)
                await shop_msg.edit(components=[])
                await shop_msg.delete(2)
            

            if choice == "🚫":
                self.previous_moves.append(f"({npc}) Shop Closed...")
                await shop_msg.edit(components=[])
                await shop_msg.delete(2)
                purchase_item = None
                purchase = False
                return

            
            if purchase_item == "⚒️":
                self.engineer = True
            elif purchase_item == "⛏️":
                self.miner = True
                self.pickaxe = True
            elif purchase_item == "🎣":
                self.fishing_pole = True
            elif purchase_item == "🔨":
                self.hammer = True
            elif purchase_item == "🏊":
                self.swimmer = True
            elif purchase_item == "🪜":
                self.climber = True
            else:
                purchase_item = None
            if purchase:
                shopping_checkout_embed = Embed(title=f"{npc}{get_emoji_label(npc)} Shop", description="*Thank you for shopping!*", color=0x00FF00)
                shopping_checkout_embed.add_field(name="[🧾]Receipt", value=f"{purchase_item}{get_emoji_label(purchase_item)} - {self.gold}{cost}\n")
            else:
                shopping_checkout_embed = Embed(title=f"{npc}{get_emoji_label(npc)} Shop", description=f"*You don't have enough gold to purchase {purchase_item}*", color=0x00FF00)
                shopping_checkout_embed.add_field(name="[🧾]Receipt", value="*No items purchased*\n")
            #cart_msg = await private_channel.send(embed=shopping_checkout_embed)
            #await asyncio.sleep(1)
            #await cart_msg.edit(components=[])
            #await cart_msg.delete(2)
            self.encounter = False
            return
        except Exception as ex:
            await shop_msg.edit(components=[])
            custom_logging.debug(ex)
        except asyncio.TimeoutError:
            await shop_msg.edit(components=[])
            custom_logging.debug(ex)
            self.encounter = False
            return 

    
    async def generate_quest(self, ctx, private_channel, npc, npc_position):
        # Logic to generate a quest and place a random emoji on the map
        if self.has_quest:
            return
        self._player.quest_count += 1
        q_type = ""
        self.has_quest = True
        quest_npc_msg = f"an {get_emoji_label(npc)}!"
        if npc == "🆚":
            quest_npc_msg = f"a {self.universe} Rival!"
        quest_options = random.choice(self.quest)
        self.previous_moves.append(f"({npc}) You received a quest from {quest_npc_msg}!")
        self.quest_message_list.append(f"({npc}) You received a quest from {quest_npc_msg}!")
        quest_embed = Embed(title=f"New Quest", description=f"Find and complete the [{quest_options}]Quest objective on the map.", color=0x00FF00)
        if quest_options == "🎯":
            quest_embed.add_field(name="Objective", value="Find and eliminate the target.")
            self.my_quest = "🎯"
            q_type = "Elimination"
        elif quest_options == "🔎":
            quest_embed.add_field(name="Objective", value="Find the hidden treasure.")
            self.my_quest = "🔎"
            q_type = "Treasure Hunt"
            self.has_investigation = True
        # Ensure the quest marker is placed on a passable space
        while True:
            quest_location = (random.randint(0, len(self._player.map['map']) - 1), random.randint(0, len(self._player.map['map'][0]) - 1))
            if self._player.map['map'][quest_location[0]][quest_location[1]] in self.passable_points:
                break
        
        self.quest_giver_position = npc_position
        self._player.map['map'][quest_location[0]][quest_location[1]] = f"{quest_options}"  # Example quest marker
        #quest_msg = await private_channel.send(embed=quest_embed)
        #await quest_msg.delete(3)
        self.previous_moves.append(f"({self.my_quest}) {q_type} Quest marker placed at {quest_location}!")
        self.quest_message_list.append(f"({self.my_quest}) {q_type} Quest marker placed at {quest_location} on {self._player.map['map_name']}!")

    
    async def trigger_failed_talk(self, ctx, private_channel, npc):
        # Logic to handle a failed talk attempt that triggers a battle
        self.previous_moves.append(f"(🗨️) Talk attempt failed, starting a battle!")
        await self.create_rpg_battle(ctx, private_channel)

    
    async def trigger_battle(self, ctx, private_channel, npc):
        # Logic to start a battle
        self.encounter = True
        self.previous_moves.append(f"(⚔️) You have encountered a battle point!")
        await self.create_rpg_battle(ctx, private_channel)
    
    
    async def create_rpg_battle(self, ctx, private_channel, tutorial=False):
        from cogs.classes.battle_class import Battle
        from cogs.battle_config import BattleConfig

        if not self.battling and not self.encounter:
            return

        if tutorial:
            from cogs.game_modes import tutorial
            tutorial_match = await tutorial(self, ctx, self._player, "Tutorial")
            self.encounter = True
            self.set_rpg_options()
            await self.rpg_player_move_embed(ctx, private_channel, self._rpg_msg)
        else:
            self.encounter = True
            battle = Battle("RPG", self._player)
            battle.rpg_map = self.display_map()
            battle.rpg_config = self
            battle.rpg_atk_boost = self.player_atk_boost
            battle.rpg_def_boost = self.player_def_boost
            battle.rpg_hp_boost = self.player_hp_boost
            battle.rpg_health = self.player_health
            await self.rpg_player_move_embed(ctx, private_channel, self._rpg_msg)
            battle.rpg_msg = self._rpg_msg

            selected_card = crown_utilities.create_card_from_data(random.choice(self.list_of_combatants))
            dialogue_option = random.choice(selected_card.descriptions)
            selected_card.set_affinity_message()
            selected_card.set_explore_bounty_and_difficulty(battle, self._player.map_level)
            self.current_opponent_name = selected_card.name
            
            if dialogue_option:
                selected_card.ai_encounter_message = dialogue_option["message"]
            else:
                selected_card.ai_encounter_message = f"🆚 {selected_card.name} has appeared!"

            battle.is_rpg_game_mode = True
            battle.set_explore_config(self.universe_data, selected_card)
            battle.bounty = selected_card.bounty
            x, y = self.encounter_position
            self.set_rpg_options()
            encounter_buttons_action_row = ActionRow(*self.encounter_buttons)

            embedVar = Embed(title=f"**{selected_card.name} Encounter**", color=0xf1c40f)
            embedVar.set_image(url="attachment://image.png")
            embedVar.set_footer(text=f"{selected_card.battle_message}\n💨Run to flee this encounter and return to Adventure.", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
            
            image_binary = selected_card.showcard(mode="RPG", encounter=True)
            image_binary.seek(0)
            card_file = File(file_name="image.png", file=image_binary)

            msg = await private_channel.send(embed=embedVar, file=card_file, components=[encounter_buttons_action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.bot.wait_for_component(components=[encounter_buttons_action_row], timeout=300, check=check)
                await button_ctx.ctx.defer(edit_origin=True)
                if button_ctx.ctx.custom_id == "fight":                    
                    self.battling = True
                    # await msg.edit(components=[])
                    await msg.delete()
                    await BattleConfig.create_rpg_battle(self, ctx, battle)
                    return

                if button_ctx.ctx.custom_id == "talk":
                    # await asyncio.sleep(2)
                    await msg.delete()
                    self.talking_encounter = True
                    option_a = dialogue_option["dialogue_options"][0]["response"]
                    option_b = dialogue_option["dialogue_options"][1]["response"]
                    option_c = dialogue_option["dialogue_options"][2]["response"]
                    self.set_rpg_options()
                    encounter_buttons_action_row = ActionRow(*self.encounter_buttons)
                    embedVar = Embed(title=f"**{selected_card.name} Encounter**", color=0xf1c40f)
                    embedVar.set_image(url="attachment://image.png")
                    embedVar.set_footer(text=f"OPTION A - {option_a}\nOPTION B - {option_b}\nOPTION C - {option_c}", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
                    
                    image_binary = selected_card.showcard(mode="RPG", encounter=True)
                    image_binary.seek(0)
                    card_file = File(file_name="image.png", file=image_binary)

                    player_ping = await private_channel.send(f"🆚{ctx.author.mention}⬇️")
                    await player_ping.delete(delay=10)
                    talk_msg = await private_channel.send(embed=embedVar, file=card_file, components=[encounter_buttons_action_row])

                    try:
                        talking_button_ctx = await self.bot.wait_for_component(components=[encounter_buttons_action_row], timeout=300, check=check)
                        await talking_button_ctx.ctx.defer(edit_origin=True)
                        if talking_button_ctx.ctx.custom_id == f"{self._talking_uuid}|A":
                            self._player.map['map'][x][y] = f"{self._player.standing_on}"
                            if not dialogue_option["dialogue_options"][0]["fight"]:
                                # await msg.edit(components=[])
                                # await self.increment_mission_count(ctx, private_channel)
                                randum_number = random.randint(1, 100)
                                if randum_number <= 50:
                                    await self.encounter_handler(ctx, private_channel, '💫', selected_card.name)
                                    await talk_msg.delete()
                                    self.battling = False
                                    self.encounter = False
                                else:
                                    self.previous_moves.append(f"({selected_card.name}) has laid down their arms... for now.")
                                    await talk_msg.delete()
                                    self.battling = False
                                    self.encounter = False
                                    

                            if dialogue_option["dialogue_options"][0]["fight"]:
                                self.battling = True
                                await talk_msg.delete()
                                await BattleConfig.create_rpg_battle(self, ctx, battle)
                        if talking_button_ctx.ctx.custom_id == f"{self._talking_uuid}|B":
                            self._player.map['map'][x][y] = f"{self._player.standing_on}"

                            if not dialogue_option["dialogue_options"][1]["fight"]:
                                # await self.increment_mission_count(ctx, private_channel)
                                # await msg.edit(components=[])
                                randum_number = random.randint(1, 100)
                                if randum_number <= 50:
                                    await self.encounter_handler(ctx, private_channel, '💫', selected_card.name)
                                    await talk_msg.delete()
                                    self.battling = False
                                    self.encounter = False
                                else:
                                    self.previous_moves.append(f"({selected_card.name}) has laid down their arms... for now.")
                                    await talk_msg.delete()
                                    self.battling = False
                                    self.encounter = False

                            if dialogue_option["dialogue_options"][1]["fight"]:
                                self.battling = True
                                # await msg.edit(components=[])
                                await talk_msg.delete()
                                await BattleConfig.create_rpg_battle(self, ctx, battle)
                        if talking_button_ctx.ctx.custom_id == f"{self._talking_uuid}|C":
                            self._player.map['map'][x][y] = f"{self._player.standing_on}"
                            if not dialogue_option["dialogue_options"][2]["fight"]:
                                # await self.increment_mission_count(ctx, private_channel)
                                # await msg.edit(components=[])
                                randum_number = random.randint(1, 100)
                                randum_number = 5
                                if randum_number <= 50:
                                    await self.encounter_handler(ctx, private_channel, '💫', selected_card.name)
                                    await talk_msg.delete()
                                    self.battling = False
                                    self.encounter = False
                                else:
                                    self.previous_moves.append(f"({selected_card.name}) has laid down their arms... for now.")
                                    await talk_msg.delete()
                                    self.battling = False
                                    self.encounter = False

                            if dialogue_option["dialogue_options"][2]["fight"]:
                                self.battling = True
                                # await msg.edit(components=[])
                                await talk_msg.delete()
                                await BattleConfig.create_rpg_battle(self, ctx, battle)
                        self.talking_encounter = False
                        return
                    except Exception as ex:
                        await talk_msg.edit(components=[])
                        custom_logging.debug(ex)
                        self.encounter = False
                        return

                if button_ctx.ctx.custom_id == "run":
                    randum_number = random.randint(1, 100)
                    randum_number += self.player_speed
                    if randum_number >= 25:
                        self.previous_moves.append(f"(💨) After a short fight you ran away! [-25%HP]")
                        self.player_health-= round(self.player_health * .25)
                        self.battling = False
                        self.encounter = False
                    else:
                        self.previous_moves.append(f"(🆚) You failed to run away! Get ready to fight!")
                        run_msg = await private_channel.send(f"🆚{ctx.author.mention} You failed to run away!")
                        await run_msg.delete(delay=3)
                        self.battling = True
                        await BattleConfig.create_rpg_battle(self, ctx, battle)
                    # await msg.edit(components=[])
                    await msg.delete()
                    return
            except Exception as ex:
                await msg.edit(components=[])
                await msg.delete()
                custom_logging.debug(ex)
                self.encounter = False
                return
            except asyncio.TimeoutError:
                await msg.edit(components=[])
                custom_logging.debug(ex)
                self.encounter = False
                await msg.delete()
                return
        
        
    async def move_dynamic_emojis(self, ctx, private_channel, player_position):
        dynamic_emojis = ["🦌", "👻", "🐍", "🦂", "🚗", "🌿","🦊", "🦇"]  # Add or remove emojis as needed
        movement_chance = 0.5  # 50% chance to move, adjust as needed

        for i in range(len(self._player.map['map'])):
            for j in range(len(self._player.map['map'][i])):
                if self._player.map['map'][i][j] in dynamic_emojis:
                    if random.random() < movement_chance:
                        await self.move_single_emoji(ctx, private_channel, (i, j), player_position)

    async def move_single_emoji(self, ctx, private_channel, emoji_position, player_position):
        x, y = emoji_position
        emoji = self._player.map['map'][x][y]

        # Define possible directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < len(self._player.map['map']) and 0 <= new_y < len(self._player.map['map'][0]) and
                self._player.map['map'][new_x][new_y] == self._player.standing_on):
                # Move the emoji
                self._player.map['map'][x][y] = self._player.standing_on
                self._player.map['map'][new_x][new_y] = emoji

                # Check if the emoji moved adjacent to the player
                # if abs(new_x - player_position[0]) <= 1 and abs(new_y - player_position[1]) <= 1:
                #     self.previous_moves.append(f"({emoji}) An enemy approaches!")
                #     await self.encounter_handler(ctx, private_channel, emoji, (new_x, new_y))
                #     self.encounter = True
                #     await self.create_rpg_battle(ctx, private_channel)
                
                break  # Stop after moving once



    def update_bridge_state(self, bridge_position):
        if bridge_position not in self.crossed_bridges:
            self.crossed_bridges.append(bridge_position)

    
    #Warp Movement
    async def handle_warp_movement(self, ctx, warp_index):
        warp_target = self.closest_warp_points[int(warp_index)]
        warp_point_position = warp_target['position']
        self.warp_point_position = warp_point_position
        new_position = self.get_closest_passable_space(warp_point_position)
        #print("new_position", new_position)

        # Check if the new position is a valid position, within range, and on a passable square
        if not self.is_reachable_without_bridge_or_water(self._player.player_position, new_position):
            # Find the nearest valid position that is reachable
            new_position = self.find_nearest_reachable_position(warp_point_position)
            #print("Adjusted new_position", new_position)

        self._player.map['map'][self._player.player_position[0]][self._player.player_position[1]] = self._player.standing_on
        self._player.standing_on = self._player.map['map'][new_position[0]][new_position[1]]
        self._player.map['map'][new_position[0]][new_position[1]] = self.player_token
        self._player.player_position = new_position
        self.warp_target_type = warp_target['type']
        self.previous_moves.append(f"Warped to the {warp_target['type']}{get_emoji_label(warp_target['type'])}!")

        # Update bridge state if a bridge was crossed
        if warp_target['type'] in self.bridges:
            self.update_bridge_state(warp_point_position)
    

    def is_reachable_without_bridge_or_water(self, start, goal):
        from collections import deque

        rows = len(self._player.map['map'])
        cols = len(self._player.map['map'][0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        queue = deque([start])
        visited = set()
        visited.add(start)

        while queue:
            x, y = queue.popleft()
            
            if (x, y) == goal:
                return True
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                    if self._player.map['map'][nx][ny] not in self.bridges and self._player.map['map'][nx][ny] not in self.still_water and self._player.map['map'][nx][ny] not in self.walls:  # Exclude bridges, water, and walls
                        queue.append((nx, ny))
                        visited.add((nx, ny))

        return False

    
    def is_bridge_directly_accessible(self, start, bridge_position):
        from collections import deque

        rows = len(self._player.map['map'])
        cols = len(self._player.map['map'][0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        queue = deque([start])
        visited = set()
        visited.add(start)

        while queue:
            x, y = queue.popleft()
            
            if (x, y) == bridge_position:
                return True
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                    if self._player.map['map'][nx][ny] not in self.still_water and self._player.map['map'][nx][ny] not in self.walls:  # Allow bridges
                        queue.append((nx, ny))
                        visited.add((nx, ny))

        return False
        
    
    async def cross_bridge(self, ctx, private_channel, player_position, npc, npc_position, direction):
        x,y = player_position
        crossed = False
        random_number = random.randint(1, 100)
        if random_number <= 15:
            self.previous_moves.append(f"(🌉) As you cross you notice there is some loot on the bridge...")
            random_number_combat = random.randint(1, 100)
            if random_number_combat <= 50:
                self.previous_moves.append(f"(🆚) It's a trap! You are under attack!")
                self.encounter = True
                await self.create_rpg_battle(ctx, private_channel)
                if self.combat_victory:
                    self.previous_moves.append(f"(🌉) You found a hidden chest!")
                    self.loot_drop = True
                    self.remove_combatant()
                    await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "🎁", npc_position)
                    crossed = True
                else:
                    self.previous_moves.append(f"(🌉) You lost 100 gold!")
                    self.player_gold -= 100
            else:
                crossed = True
                self.loot_drop = True
                await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "👛", npc_position, direction)
        elif random_number <= 25:
            self.previous_moves.append(f"(🆚) There is a roadblock on the bridge...You are under attack!")
            self.encounter = True
            await self.create_rpg_battle(ctx, private_channel)
            if self.combat_victory:
                self.remove_combatant()
                self.previous_moves.append(f"(🌉) You crossed the Bridge!")
                crossed = True
            else:
                self.previous_moves.append(f"(🌉) You lost 100 gold!")
                self.player_gold -= 100
        elif random_number <= 40:
            self.previous_moves.append(f"(🌉) There is a crew fixing the bridge...")
            if self.hammer:
                self.previous_moves.append(f"(🌉) You volunteer to help and cross after assisting!")
                if self.engineer:
                    self.previous_moves.append(f"(🌉) The crew pays you for your service! [💰+1000]")
                crossed = True
            else:
                self.previous_moves.append(f"(🌉) I'll have to wait...if only I could assist")
                return
        else:
            self.previous_moves.append(f"(🌉) You crossed the bridge!")
            crossed = True  
        if direction == "u":
            new_position = (npc_position[0] - 1, npc_position[1])
        elif direction == "d":
            new_position = (npc_position[0] + 1, npc_position[1])
        elif direction == "l":
            new_position = (npc_position[0], npc_position[1] - 1)
        elif direction == "r":
            new_position = (npc_position[0], npc_position[1] + 1)

        if crossed:
            original_tile = self._player.map['map'][new_position[0]][new_position[1]]
            if original_tile in self.quest:
                if original_tile == "🔎":
                    self.previous_moves.append(f"(🔎) You found a hidden path....")
                    self.previous_moves.append(f"(🔎) Investigation Quest Complete!")
                    self.quest_message_list.append(f"🔎 Investigation Quest Complete!")
                    self.has_quest = False
                    self.has_investigation = False
                    self._player.quest_complete += 1
                    self.keys += 1
                    await self.rpg_action_handler(ctx, private_channel, self._player.player_position, "🃏", new_position, direction)
                elif original_tile == "🎯":
                    self.previous_moves.append(f"(🎯) You found a target!")
                    await self.create_rpg_battle(ctx, private_channel)
                    if self.combat_victory:
                        self.remove_combatant()
                        self.previous_moves.append(f"(🎯) Target Eliminated!")
                        self.quest_message_list.append(f"🎯 Target Eliminated")
                        self.has_quest = False
                        self._player.quest_complete += 1
                        self.keys += 1
                    else:
                        self.previous_moves.append(f"(🎯) Target Escaped!")
                        self.quest_message_list.append(f"🎯 Target Escaped")
                        return
            self._player.map['map'][new_position[0]][new_position[1]] = f"{self.player_token}"
            self._player.map['map'][x][y] = f"{self._player.standing_on}"
            self._player.player_position = new_position
            self._player.standing_on = original_tile  # Update the standing_on to the original tile color

            # Update bridge state
            if npc in self.bridges:
                self.update_bridge_state(npc_position)

    
    def get_closest_warp_points(self, current_position, num_points=5):
        warp_distances = []
        cx, cy = current_position
        seen_positions = set()

        for warp in self.warp_points:
            for i in range(len(self._player.map['map'])):
                for j in range(len(self._player.map['map'][i])):
                    if self._player.map['map'][i][j] == warp:
                        distance = abs(cx - i) + abs(cy - j)
                        if self.is_reachable_without_bridge_or_water(current_position, (i, j)):
                            position_tuple = (i, j)
                            if position_tuple not in seen_positions:
                                warp_distances.append({'position': position_tuple, 'type': warp, 'distance': distance})
                                seen_positions.add(position_tuple)

        bridges = []
        for i in range(len(self._player.map['map'])):
            for j in range(len(self._player.map['map'][i])):
                if self._player.map['map'][i][j] in self.bridges:
                    distance = abs(cx - i) + abs(cy - j)
                    if self.is_bridge_directly_accessible(current_position, (i, j)):
                        bridges.append({'position': (i, j), 'type': self._player.map['map'][i][j], 'distance': distance})

        bridges.sort(key=lambda x: x['distance'])

        for bridge in bridges:
            if self.is_bridge_directly_accessible(current_position, bridge['position']):
                if bridge['position'] not in seen_positions:
                    warp_distances.append(bridge)
                    seen_positions.add(bridge['position'])
                    break

        warp_distances.sort(key=lambda x: x['distance'])

        return warp_distances[:num_points]
    
    
    def get_closest_passable_space(self, position):
        x, y = position
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self._player.map['map']) and 0 <= ny < len(self._player.map['map'][0]):
                if self._player.map['map'][nx][ny] in self.passable_points:
                    return (nx, ny)
                elif self._player.map['map'][nx][ny] in self.bridges:
                    # Ensure to return the accessible side of the bridge
                    for ddx, ddy in directions:
                        nnx, nny = nx + ddx, ny + ddy
                        if 0 <= nnx < len(self._player.map['map']) and 0 <= nny < len(self._player.map['map'][0]) and self._player.map['map'][nnx][nny] in self.passable_points:
                            # Check if the initial position is directly accessible to the bridge
                            if self.is_bridge_directly_accessible((x, y), (nx, ny)):
                                return (nx, ny)
                            else:
                                return (nnx, nny)
        return position  # Return the original position if no passable space found
    
    
    def find_nearest_reachable_position(self, start):
        from collections import deque

        rows = len(self._player.map['map'])
        cols = len(self._player.map['map'][0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        queue = deque([start])
        visited = set()
        visited.add(start)

        while queue:
            x, y = queue.popleft()

            for dx, dy in directions:
                nx, ny = x + dx, y + dy

                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                    if self._player.map['map'][nx][ny] in self.passable_points:
                        if self.is_reachable_without_bridge_or_water(self._player.player_position, (nx, ny)):
                            return (nx, ny)

                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return start  # Fallback to the original point if no reachable passable space is found


    def get_relative_direction(self, old_position, new_position):
        old_x, old_y = old_position
        new_x, new_y = new_position
        if new_x < old_x:
            return "u"  # up
        elif new_x > old_x:
            return "d"  # down
        elif new_y < old_y:
            return "l"  # left
        elif new_y > old_y:
            return "r"  # right
        else:
            return "s"  # standing on the same position
  
    #Random Generation
    def generate_new_map(self):
        width, height = 9, 10  # Consistent dimensions

        # Initialize the map with walls
        new_map = [[random.choice(self.walls) for _ in range(width)] for _ in range(height)]

        # Set the player's start position
        start_x, start_y = 8, 4
        new_map[start_x][start_y] = self.player_token

        # Ensure navigability by creating a random path starting from (8, 4)
        path_length = random.randint(int(width * height * 0.2), int(width * height * 0.4))
        x, y = start_x, start_y
        for _ in range(path_length):
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up' and x > 1:
                x -= 1
            elif direction == 'down' and x < height - 2:
                x += 1
            elif direction == 'left' and y > 1:
                y -= 1
            elif direction == 'right' and y < width - 2:
                y += 1
            new_map[x][y] = random.choice(self.passable_points)  # Navigable path

        # Ensure the initial start position (8, 4) is navigable
        new_map[7][4] = random.choice(self.passable_points)  # Path above the starting position
        new_map[8][3] = random.choice(self.passable_points)  # Path left of the starting position
        new_map[8][5] = random.choice(self.passable_points)  # Path right of the starting position
        new_map[9][4] = random.choice(self.passable_points)  # Path below the starting position

        # Place random features and items
        features = self.interaction_points + self.trees + self.still_water + self.bridges + self.merchants + self.wildlife + self.doors + self.keys + self.items + self.remains + self.food
        num_features = random.randint(int(width * height * 0.1), int(width * height * 0.2))
        for _ in range(num_features):
            fx, fy = random.randint(1, height - 2), random.randint(1, width - 2)
            if new_map[fx][fy] in self.walls:  # Only place features in wall spots
                new_map[fx][fy] = random.choice(features)

        return new_map, True

    
    def get_previous_moves_embed(self):
        updated_list = crown_utilities.replace_matching_numbers_with_arrow(self.previous_moves)
        msg = "\n\n".join(updated_list)
        if msg:
            return msg
        else:
            return ""
        
    def get_quest_list_embed(self):
        #print(self.quest_message_list)
        if self.quest_message_list:
            return "\n".join(self.quest_message_list)
        else:
            return "No Quests Taken"
        
    
    async def lose_adventure_embed(self, ctx):
        from cogs.classes.custom_paginator import Paginator
        gold_message = f"[{self.get_gold_icon(self.player_gold)}] {round(self.player_gold):,} Gold 💱 [{self.coin_item}] {0} Coins"
        gem_message = f"[{self.get_gem_icon(self.player_gems)}] {round(self.player_gems):,} Crystal 💱 [💎] {0} Gems"
        
        inventory_message = "No Items Aquired"
        skills_message = "No Skills Aquired"
        if self.inventory_active:
            inventory_message = ""
            for item in self.player_inventory:
                inventory_message += f"|{item['USE']} {item['ITEM']}"
        if self.skills_active:
            skills_message = ""
            for skill in self.player_skills:
                skills_message += f"|{skill}"
      

        embedVar = Embed(title=f"👤 Adventure Inventory", description="*You lost all currency Gold and Crystal*", color=0xFFD700)
        embedVar.add_field(name=f"**[❤️] {self.player_health:,} HP\n[🎒]Your Equipment**", value=f"|{inventory_message}")
        embedVar.add_field(name=f"**[🥋] Skills**", value=f"|{skills_message}")
        embedVar.add_field(name=f"**[💹] Currency Conversion**", value=f"{gold_message}\n{gem_message}")
        embedVar.set_footer(text="🃏 Build Details on the next page!")

        lootEmbed = Embed(title=f"☠️ You Died!", description="No worries any items you earned via drops you get to keep!\n*Your Adventure rewards will be shown below*", color=0xFFD700)
        if len(self._player.card_drops) > 0:
            card_msg = ""
            for cards in self._player.card_drops:
                card_msg += f"|{cards}\n"
            lootEmbed.add_field(name=f"**🎴 Cards**", value=f"{card_msg}")
        if len(self._player.title_drops) > 0:
            title_msg = ""
            for titles in self._player.title_drops:
                title_msg += f"|{titles}\n"
            lootEmbed.add_field(name=f"**🎗️ Titles**", value=f"{title_msg}")
        if len(self._player.arm_drops) > 0:
            arm_msg = ""
            for arms in self._player.arm_drops:
                arm_msg += f"|{arms}\n"
            lootEmbed.add_field(name=f"**🦾 Arms**", value=f"{arm_msg}")
        if len(self._player.summon_drops) > 0:
            summon_msg = ""
            for summons in self._player.summon_drops:
                summon_msg += f"|{summons}\n"
            lootEmbed.add_field(name=f"**🧬 Summons**", value=f"{summon_msg}")
        lootEmbed.set_footer(text="👤 Adventure Summary on the Next Page!")

        buildEmbed = Embed(title=f"🃏 Adventure Build", description="*Your Adventure Build will be shown below*", color=0xFFD700)
        buildEmbed.add_field(name=f"**🎗️ Title**", value=f"{self.player1_title}")
        buildEmbed.add_field(name=f"**🎴 Card**", value=f"{self.player1_card_name}")
        buildEmbed.add_field(name=f"**🦾 Arm**", value=f"{self.player1_arm}")
        buildEmbed.add_field(name=f"**🧬 Summon**", value=f"{self.player1_summon_name}")
        buildEmbed.add_field("**📿 Talisman**", value=f"{self.player1_talisman.title()}")
        buildEmbed.set_footer(text="🗺️ Adventure Map on the next page!")


        map_embed = Embed(title=f"🗺️ Adventure Log", description=f"**🌎** | *{self._player.map['map_name']}*\n**🗺️** | *{self._player.map['map_area']}*\n{self.get_map_message()}", color=0xFFD700)
        map_embed.set_footer(text=f"{self.get_previous_moves_embed()}")

        quest_embed = Embed(title=f"🔍Adventure Mission Progress...", description="*Your Mission & Quest progress will be shown below*", color=0xFFD700)
        quest_embed.add_field(name=f"🪜 Floor Mission: **{self.mission_message}!**", value=f"Mission count: {self._player.mission_count} / Mission requirements: {self._player.mission_requirements}")
        quest_embed.add_field(name=f"**🔍 Quests Comeplete/Taken: {self._player.quest_complete}/ {self._player.quest_count}**", value=f"{self.get_quest_list_embed()}")
        quest_embed.set_footer(text="☠️ You Died!")


        embed_list = [lootEmbed,quest_embed,embedVar,buildEmbed,map_embed]
        paginator = Paginator.create_from_embeds(self.bot, *embed_list)
        paginator.show_select_menu = True
        return paginator

    async def leave_adventure_embed(self, ctx):
        from cogs.classes.custom_paginator import Paginator
        gold_message = f"[{self.get_gold_icon(self.player_gold)}] {round(self.player_gold):,} Gold 💱 [{self.coin_item}] {round(self.player_gold * 10):,} Coins"
        gem_message = f"[{self.get_gem_icon(self.player_gems)}] {round(self.player_gems):,} Crystal 💱 [💎] {round(self.player_gems * 10):,} Gems"
        
        inventory_message = "No Items Aquired"
        skills_message = "No Skills Aquired"
        if self.inventory_active:
            inventory_message = ""
            for item in self.player_inventory:
                inventory_message += f"|{item['USE']} {item['ITEM']}"
        if self.skills_active:
            skills_message = ""
            for skill in self.player_skills:
                skills_message += f"|{skill}"


        
        

        embedVar = Embed(title=f"👤 Adventure Inventory!", description="🏧 Complete the Adventure Mission to earn/increase Gold and Crystal Multipliers!\n*Your Equipment, Currency and Skills Below*", color=0x00FF00)
        if self.mission_completed:
            embedVar = Embed(title=f"🪜 Floor {self._player.map_level} Completed!", description="🏆 Good luck on the next floor!\n*Your Equipment, Currency and Skills Below*", color=0xFFD700)
        embedVar.add_field(name=f"**[❤️] {self.player_health:,} HP\n[🎒]Your Equipment**", value=f"|{inventory_message}")
        embedVar.add_field(name=f"**[🥋] Skills**", value=f"|{skills_message}")
        embedVar.add_field(name=f"**[💹] Currency Conversion**", value=f"{gold_message}\n{gem_message}")
        embedVar.set_footer(text="🃏 Build Details on the next page!")

        # create rpg_completed embed 
        
        lootEmbed = Embed(title=f"💾 Progress Saved!", description=f"🎖️Floor {self._player.map_level}\n🎉*Your Adventure rewards will be shown below*", color=0x00FF00)
        if self.mission_completed:
            lootEmbed = Embed(title=f"🪜 Floor {self._player.map_level} Completed!", description="🏆 Good luck on the next floor!\n🎉*Your Adventure rewards will be shown below*", color=0xFFD700)

        if len(self._player.card_drops) > 0:
            card_msg = ""
            for cards in self._player.card_drops:
                card_msg += f"|{cards}\n"
            lootEmbed.add_field(name=f"**🎴 Cards**", value=f"{card_msg}")
        if len(self._player.title_drops) > 0:
            title_msg = ""
            for titles in self._player.title_drops:
                title_msg += f"|{titles}\n"
            lootEmbed.add_field(name=f"**🎗️ Titles**", value=f"{title_msg}")
        if len(self._player.arm_drops) > 0:
            arm_msg = ""
            for arms in self._player.arm_drops:
                arm_msg += f"|{arms}\n"
            lootEmbed.add_field(name=f"**🦾 Arms**", value=f"{arm_msg}")
        if len(self._player.summon_drops) > 0:
            summon_msg = ""
            for summons in self._player.summon_drops:
                summon_msg += f"|{summons}\n"
            lootEmbed.add_field(name=f"**🧬 Summons**", value=f"{summon_msg}")
        lootEmbed.set_footer(text="👤 Adventure Summary on the Next Page!")

        buildEmbed = Embed(title=f"🃏 Adventure Build!", description="❤️ You Survived!\n*Your Adventure Build will be shown below*", color=0x00FF00)
        if self.mission_completed:
            buildEmbed = Embed(title=f"🪜 Floor {self._player.map_level} Completed!", description="🏆 Good luck on the next floor!\n🃏*Your Adventure Build! will be shown below*", color=0xFFD700)
        buildEmbed.add_field(name=f"**🎗️ Title**", value=f"{self.player1_title}")
        buildEmbed.add_field(name=f"**🎴 Card**", value=f"{self.player1_card_name}")
        buildEmbed.add_field(name=f"**🦾 Arm**", value=f"{self.player1_arm}")
        buildEmbed.add_field(name=f"**🧬 Summon**", value=f"{self.player1_summon_name}")
        buildEmbed.add_field("**📿 Talisman**", value=f"{self.player1_talisman.title()}")
        buildEmbed.set_footer(text="🗺️ Adventure Map on the next page!")


        map_embed = Embed(title=f"🗺️ Adventure Log", description=f"**🌎** | *{self._player.map['map_name']}*\n**🗺️** | *{self._player.map['map_area']}*\n{self.get_map_message()}", color=0x00FF00)
        if self.mission_completed:
            map_embed = Embed(title=f"🪜 Floor {self._player.map_level} Completed!", description="🏆 Good luck on the next floor!\n🗺️*Your Adventure Map will be shown below*", color=0xFFD700)
            map_embed.add_field(name=f"**🗺️ Final Map", value=f"{self.get_map_message()}")
        map_embed.set_footer(text=f"{self.get_previous_moves_embed()}")


        quest_embed = Embed(title=f"🔍Adventure Mission Progress!", description="🪜 Complete the floor mission to increase your map level!\n*Your Mission & Quests progress will be shown below*", color=0x00FF00)
        if self.mission_completed:
            quest_embed = Embed(title=f"🪜 Floor {self._player.map_level} Completed!", description="🏆 Good luck on the next floor!\n🔍*Your Mission & Quests progress will be shown below*", color=0xFFD700)
        quest_embed.add_field(name=f"🪜 Floor Mission: **{self.mission_message}!**", value=f"Mission count: {self._player.mission_count} / Mission requirements: {self._player.mission_requirements}")
        quest_embed.add_field(name=f"**🔍 Quests Complete/Taken: {self._player.quest_complete}/ {self._player.quest_count}**", value=f"{self.get_quest_list_embed()}")
        quest_embed.set_footer(text="🎉 Adventure Completed!")

        if self.mission_completed:
            embed_list = [lootEmbed,quest_embed,embedVar,buildEmbed,map_embed]
        else:
            embed_list = [lootEmbed,quest_embed,embedVar,buildEmbed,map_embed]
        paginator = Paginator.create_from_embeds(self.bot, *embed_list)
        paginator.show_select_menu = True
        return paginator


    def get_gold_icon(self,balance):
        icon = f"<a:Shiney_Gold_Coins_Inv:1085618500455911454>"

        # if balance >=500:
        #     icon = "👛"
        # if balance >= 1000:
        #     icon = "💰"
        return icon
    

    def get_gem_icon(self,balance):
        icon = "<a:b_crystal:1085618488942547024>"

        # if balance >=5000:
        #     icon = "💍"
        # if balance >= 25000:
        #     icon = "👑"
        return icon

    
    def close_rpg_embed(self):
        if self.is_rpg:
            close_message = "Adventure Battle"
            picon = "🗺️"
            f_message = f"🗺️ | Adventure Cut Short..."
            
            
        embedVar = Embed(title=f"{picon} {self.universe} {close_message} Ended!", description=textwrap.dedent(f"""
            """))
        return embedVar

#Start Non Class Functions
def get_emoji_label(emoji):
    return emoji_labels[emoji]


def get_ground_type(ground):
    if ground in ground_types:
        return ground_types[ground]
    return ground

# Function to search for an emoji
def search_emoji(emojis_dict, target_emoji):
    for category, emoji_list in emojis_dict.items():
        if target_emoji in emoji_list:
            return category, target_emoji
    return None, None


emojis = {
    'man': [
        "👨", "👨‍⚕️", "👨‍🌾", "👨‍🍳","👨‍🏭","👨‍💼", "👨‍🔧",
        "🕵️‍♂️", "👷‍♂️", "🤴", "👳‍♂️", "👲", "🧔", "👱‍♂️", "👨‍🦰", "👨‍🦱", 
        "👨‍🦳", "👨‍🦲", "🧓", "👴",
    ],
    'woman': [
        "👩", "👩‍⚕️", "👩‍🌾", "👩‍🍳","👩‍🏭","👩‍💼", "👩‍🔧",
        "🕵️‍♀️", "👷‍♀️", "👸", "👳‍♀️", "👲", "🧕", "👱‍♀️", "👩‍🦰", "👩‍🦱",
        "👩‍🦳", "👩‍🦲", "🧓", "👵",
    ],
    'little': [
        "🧒", "👦", "👧",
    ]
}


ground_types = {
    '🟨':'Sand',
    '⬜':'Snow',
    '🟩':'Grass',
    '🟫':'Dirt',
    '◼️':'Road',
    '🟦':'Water',
    '🟪': 'Ethereal Plane'
}


emoji_labels = {
            "👨": "Male", "👨‍⚕️": "Male Doctor", "👨‍🌾": "Male Farmer", "👨‍🍳": "Male Cook", "👨‍🎓": "Male Student", 
            "👨‍🎤": "Male Singer", "👨‍🏫": "Male Teacher", "👨‍🏭": "Male Factory Worker", "👨‍💻": "Male Office Worker", 
            "👨‍💼": "Male Businessman", "👨‍🔧": "Male Mechanic", "👨‍🔬": "Male Scientist", "👨‍🚀": "Male Astronaut", 
            "👨‍🚒": "Male Firefighter", "👮‍♂️": "Policeman", "🕵️‍♂️": "Male Detective", "👷‍♂️": "Male Construction Worker", 
            "🤴": "Prince", "👳‍♂️": "Desert Man", "👲": "Male with Hat", "🧔": "Bearded Male", "👱‍♂️": "Blond Male", 
            "👨‍🦰": "Red-Haired Male", "👨‍🦱": "Curly-Haired Male", "👨‍🦳": "White-Haired Male", "👨‍🦲": "Bald Male", "🧓": "Old Male", 
            "👴": "Elderly Male", "👩": "Female", "👩‍⚕️": "Female Doctor", "👩‍🌾": "Female Farmer", 
            "👩‍🍳": "Female Cook", "👩‍🎓": "Female Student", "👩‍🎤": "Female Singer", "👩‍🏫": "Female Teacher", 
            "👩‍🏭": "Female Factory Worker", "👩‍💻": "Female Office Worker", "👩‍💼": "Female Businesswoman", 
            "👩‍🔧": "Female Mechanic", "👩‍🔬": "Female Scientist", "👩‍🚀": "Female Astronaut", "👩‍🚒": "Female Firefighter", 
            "👮‍♀️": "Policewoman", "🕵️‍♀️": "Female Detective", "👷‍♀️": "Female Construction Worker", "👸": "Princess", 
            "👳‍♀️": "Desert Woman", "🧕": "Female with Headscarf", "👱‍♀️": "Blond Female", "👩‍🦰": "Red-Haired Female", 
            "👩‍🦱": "Curly-Haired Female", "👩‍🦳": "White-Haired Female", "👩‍🦲": "Bald Female", "👵": "Elderly Female", 
            "👶": "Baby", "🧒": "Child", "👦": "Boy", "👧": "Girl",
            # Other labels
            "🟫": "Dirt", "⬛": "Wall", "🟩": "Grass", "⬜": "Snow", "🟨": "Sand","◼️": "Road", "🏞️": "Climable Mountain",
            "🏔️": "Mountain", "⛰️": "Mountain", "🌲": "Tree", "🌳": "Tree", "🎄": "Tree", "🌴": "Looted Tree",
            "🌊": "Moving Water", "🟦": "Still Water", "🌉": "Bridge", "🏪": "Merchant", "🧙": "Magic Merchant", 
            "🕴️": "Black Market", "🏯": "Skill Trainer", "🦊": "Fox", "🦇": "Bat", "🦌": "Deer", "🦂": "Scorpion","🐍": "Snake","🐇":"Rabbit", "🚪": "Door", "🛗": "Open Door", 
            "🗝️": "Key", "💰": "Sack o' Coin", "🪙": "Coin", "👛": "Coin Bag", "🎁": "Chest", 
            "🎒": "Lost Loot", "🦾": "Arm Drop", "🆙": "Xp Drop", "🎴": "Card Drop", "🧬": "Summon Drop", 
            "🎗️": "Title Drop", "🎲": "Loot Roll", "🃏": "Loot Box", "🎰": "Jackpot Roll", "🏊": "Swimming Skill", 
            "🪜": "Climbing Gear", "🪓": "Chopping Axe", "🎣": "Fishing Pole","⛏️": "Pickaxe", "🔨": "Hammer", "⚒️": "Engineer Kit" , "💀": "Remains", "🦴": "Remains", "☠️": "Remains", 
            "🥩": "Food", "🍖": "Food", "🥕": "Food", "⚔️": "Combat Encounter", "🏴‍☠️": "Combat Encounter","🆚": "Vs+ Encounter", '🧱': "Ore",'🪨': "Rock",'🌵': 'Cactus',
            "🏜️": "Looted Cactus","🥋" : "Training Dummy", "None": "Nothing", "🎯" : "Elimination Quest", "🔎" : "Investigation Quest", f"<a:Shiney_Gold_Coins_Inv:1085618500455911454>" : "Gold",
            "🗡️": "Attack Up!","🛡️": "Defense Up!","💗":"Health Up!", "🚗": "Car", "🪦":"Grave", "🛣️":"Motorway","Car": "🚗"
            
        }


terrain_emojis = {
    "ice": "<:ice:1260038220058464318>",
    "grass": "<:grass:1260036651371991040>",
    "sand": "<:sand:1260038221144784998>"
}



#