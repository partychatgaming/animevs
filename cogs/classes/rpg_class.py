import db
import crown_utilities
import custom_logging
import interactions
import datetime
import textwrap
import time
import random
from logger import loggy
now = time.asctime()
import unique_traits as ut
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
import asyncio

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
        self.start_x = 8
        self.start_y = 4
        self.starting_position = (8, 5)
        self.player_position = (8, 5)  # Initial position of universe_crest

        self._player = _player
        self.player1 = _player
        self.player_name = self.player1.disname
        self.player1_did = self.player1.did

        self.player1_card_name = self.player1.equipped_card
        self.player_card_data = crown_utilities.create_card_from_data(db.queryCard({'NAME': self.player1_card_name}))
        self.player_avatar = self.player1.avatar
        self.player_health = self.player_card_data.health
        self.player_attack = self.player_card_data.attack
        self.player_defense = self.player_card_data.defense
        self.player_speed = self.player_card_data.speed
        self.player_stamina = self.player_card_data.stamina
        self.player_card_image = self.player_card_data.path

        self.universe = self.player_card_data.universe
        self.universe_data = db.queryUniverse({'TITLE': self.universe})

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
        self.universe_npc_token = crown_utilities.crest_dict[self.player_card_data.universe]
        self.civ_tokens = [
                            # Man emojis
                            "👨", "👨‍⚕️", "👨‍🌾", "👨‍🍳", "👨‍🎓", "👨‍🎤", "👨‍🏫", "👨‍🏭", "👨‍💻", "👨‍💼", "👨‍🔧", "👨‍🔬",
                            "👨‍🚀", "👨‍🚒", "👮‍♂️", "🕵️‍♂️", "👷‍♂️", "🤴", "👳‍♂️", "👲", "🧔", "👱‍♂️", "👨‍🦰", "👨‍🦱", 
                            "👨‍🦳", "👨‍🦲", "🧓", "👴", "👶‍♂️",
                            # Woman emojis
                            "👩", "👩‍⚕️", "👩‍🌾", "👩‍🍳", "👩‍🎓", "👩‍🎤", "👩‍🏫", "👩‍🏭", "👩‍💻", "👩‍💼", "👩‍🔧", "👩‍🔬",
                            "👩‍🚀", "👩‍🚒", "👮‍♀️", "🕵️‍♀️", "👷‍♀️", "👸", "👳‍♀️", "👲", "🧕", "👱‍♀️", "👩‍🦰", "👩‍🦱",
                            "👩‍🦳", "👩‍🦲", "🧓", "👵", "👶‍♀️",
                            # Child emojis
                            "👶", "🧒", "👦", "👧", "🧑‍🍼", "👶‍♂️", "👶‍♀️", "🧒‍♂️", "🧒‍♀️", "👦‍♂️", "👦‍♀️", "👧‍♂️", "👧‍♀️",
                            # Family emojis
                            "👪", "👨‍👩‍👦", "👨‍👩‍👧", "👨‍👩‍👧‍👦", "👨‍👩‍👦‍👦", "👨‍👩‍👧‍👧", "👨‍👨‍👦", "👨‍👨‍👧", "👨‍👨‍👧‍👦", 
                            "👨‍👨‍👦‍👦", "👨‍👨‍👧‍👧", "👩‍👩‍👦", "👩‍👩‍👧", "👩‍👩‍👧‍👦", "👩‍👩‍👦‍👦", "👩‍👩‍👧‍👧", "👨‍👦", 
                            "👨‍👦‍👦", "👨‍👧", "👨‍👧‍👧", "👩‍👦", "👩‍👦‍👦", "👩‍👧", "👩‍👧‍👧"
                        ]
        
        self.difficulty = _player.difficulty
        self.is_easy_difficulty = False
        self.is_hard_difficulty = False
        self.is_normal_difficulty = False
        if self.difficulty == "EASY":
            self.is_easy_difficulty = True


        
        self.player_gold = 0
        self.player_gems = 0
        self.player_keys = 0
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
        self.engineer = False 


        self.inventory_active = False
        self.currency_active = False
        self.skills_active = False

        self.closest_warp_points = []
        self.walls = ["🟫", "⬛"]
        self.movement_buttons = []
        self.passable_points = ["🟩", "⬜","🟨"]

        self.climable_mountains = ["🏞️"]
        self.looted_mountain = ["⛰️"]
        self.mountains = ["🏔️"]
        self.walls.extend(self.mountains)
        self.mountains.extend(self.climable_mountains)
        self.mountains.extend(self.looted_mountain)

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
        self.merchants = ["🏪","🧙", "🕴️","🏯"]
        self.wildlife = ["🦊", "🦇"]

        self.doors = ["🚪"]
        self.open_door = "🛗"
        self.keys = ["🗝️"]
        self.gems = ["💎"]

        self.common_items = ["💰","🪙","👛"]
        self.rare_items = ["🎁","🎒"]
        self.legendary_items = ["🎒"]
        self.items = []
        self.items.extend(self.common_items)
        self.items.extend(self.rare_items)
        self.items.extend(self.legendary_items)

        self.common_drops = ["🦾","🆙"]
        self.rare_drops = ["🎴","🧬"]
        self.legendary_drops = ["🎗️"]
        self.drops = []
        self.drops.extend(self.common_drops)
        self.drops.extend(self.rare_drops)  
        self.drops.extend(self.legendary_drops)
        
        self.tutorial = ["🥋"]
        self.combat_points = ["🏴‍☠️","⚔️","🆚"]
        self.combat_points.extend(self.tutorial)

        self.loot_rolls = ["🎲","🎯","🎰"]
        self.skills = ['🏊','🪜','🪓','🎣','⛏️','🔨','⚒️']
        self.remains = ["💀","🦴", "☠️"]
        self.food = ["🥩", "🍖", "🥕"]
        self.resources = ['🪨','🧱']
        self.resources.extend(self.gems)


        self.interaction_points = []
        self.interaction_points.extend(self.bridges)
        self.interaction_points.extend(self.moving_water)
        self.interaction_points.extend(self.still_water)
        self.interaction_points.extend(self.trees)
        self.interaction_points.extend(self.merchants)
        self.interaction_points.extend(self.wildlife)
        self.interaction_points.extend(self.doors)
        self.interaction_points.extend(self.keys)
        self.interaction_points.extend(self.items)
        self.interaction_points.extend(self.remains)
        self.interaction_points.extend(self.food)
        self.interaction_points.extend(self.resources)
        self.interaction_points.extend(self.drops)
        self.interaction_points.extend(self.mountains)
        self.interaction_points.extend(self.cactus)

        self.warp_points = []
        self.warp_points.extend(self.merchants)
        self.warp_points.extend(self.doors)
        self.warp_points.extend(self.keys)
        self.warp_points.extend(self.items)
        self.warp_points.extend(self.remains)
        self.warp_points.extend(self.universe_npc_token)
        self.warp_points.extend(self.civ_tokens)
        self.warp_points.extend(self.combat_points)
        self.warp_points.extend(self.wildlife)
        self.warp_points.extend(self.resources)
        self.warp_points.extend(self.bridges)

        self.active_warp_points = []
        self.warp_point_position = 0



        #Merchants sell arms
        #Wildlife drop food
        #Magical merchants sell titles
        #black market merchants sell summons
        self.previous_moves = ["🗺️ Adventure has begun!"]
        self.previous_moves_len = len(self.previous_moves)
        
        self.action_buttons = []
        self.world_buttons = []
        self.encounter_buttons = []
        self.warp_buttons = []
        self.warp_active = False

        self.standing_on = "🟩"
        self.spawn_portal = "🟩"
        self.map_name = "Damp Woodlands"
        self.map_area = "Forest Training Grounds"
        self.embed_color = 0x00FF00

        def map1(self):
            self.standing_on = "🟩"
            self.spawn_portal = "🟩"
            self.map_name = "Damp Woodlands"
            self.map_area = "Forest Training Grounds"
            self.embed_color = 0x00FF00
            return [
                ["🌳", "🌳", "🟩", "🟦", "🟫", "🟫", "🟫", "🏪", "🌳", "🌳", "🌳"],
                ["🌳", "🟩", "🟩", "🟦", "🟫", "🚪", "🟫", "🟩", "🌳", "🧙", "🌳"],
                ["🌳", "🟩", "🗝️", "🟦", "🟩", "🟩", "🎁", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🌳", "🟩", "🏴‍☠️"],
                ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳"],
                ["🟩", "🟩", "🌉", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🌳", "🌳", "🟩", "🆚", "🟩", "🌳", "🪨", "🌳"],
                ["🌳", "🌳", "🟦", "🌳", f"🌳", f"{self.player_token}", "🌳", "🌳", "🏔️", "🌳", "🌳"]

        ]

        def map2(self):
            self.standing_on = "🟨"
            self.map_name = "Scorched Lands"
            self.map_area = "Fiery Training Grounds"
            self.embed_color = 0xFFD700
            return [
                ["🌵", "⬛", "⬛", "⬛", "🟨", "🟨", "🟦", "🟦", "🟨", "🟨", "🟨"],
                ["🟨", "⬛", "🚪", "⬛", "🧙", "🏪", "🟦", "🟦", "🟨", "🟨", "🌵"],
                ["🟨", "🦊", "🟨", "🟨", "🟨", "🟨", "🟦", "🌵", "🟨", "🌵", "🟨"],
                ["🟨", "🟨", "🟨", "🟨", "🟨", "🆚", "🟦", "🟨", "🟨", "🟨", "🟨"],
                ["🟨", "🟨", "💰", "🟨", "🦴", "🟦", "🟦", "🟨", "🌵", "🟨", "🌵"],
                ["🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🌵", "🟨", "🟨", "🟨", "🟨"],
                ["🟨", "🗝️", "🟦", "🌉", "🟦", "🌵", "🟨", "🟨", "🟨", "🌵", "🟨"],
                ["🟨", "🟦", "🟦", "🟨", "🟨", "🟨", "🟨", "🦇", "🟨", "🪨", "🟨"],
                ["🟨", "🟦", "🟨", "🟨", "🟨", f"{self.player_token}", "🟨", "🌵", "🟨", "🟨", "🟨"]
        ]

        def map3(self):
            self.standing_on = "⬜"
            self.map_name = "Frosty Peaks"
            self.map_area = "Frozen Training Grounds"
            self.embed_color = 0xFFFFFF
            return [
                ["🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "⬜", "🏔️", "🏔️"],
                ["🏔️", "🏪", "🌲", "🌲", "🦊", "🌲", "🦇", "🆚", "⬜", "🎄", "🏔️"],
                ["🏔️", "⬜", "🌲", "⬜", "⬜", "🌲", "🗝️", "⬜", "⬜", "💰", "🏔️"],
                ["🏔️", "⬜", "🌲", "⬜", "⬛", "⬛", "⬛", "⬜", "⬜", "⬜", "🏔️"],
                ["⬜", "⬜", "🌲", "⬜", "⬛", "🚪", "⬛", "⬜", "⬜", "⬜", "⬜"],
                ["⬜", "⬜", "🧙", "⬜", "⬜", "⬜", "🟦", "⬜", "🏔️", "⬜", "🏔️"],
                ["⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "🌉", "⬜", "🏔️", "⬜", "🏔️"],
                ["🦴", "⬜", "🧱", "⬜", "⬜", "⬜", "🟦", "🎁", "🏔️", "🪨", "🏔️"],
                ["⬜", "⬜", "⬜", "⬜", "⬜", f"{self.player_token}", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️"]
        ]

        def map4(self):
            self.standing_on = "🟩"
            self.map_name = "Weatherlands"
            self.map_area = "Geostorm"
            self.embed_color = 0xFFFFFF
            return [
                ["💎", "🌵", "🟨", "🟦", "🟦", "🟩", "🟩", "🟩", "⬜", "⬜", "⬜"],
                ["🟨", "🏪", "🟨", "🟦", "🟦", "🟩", "🗝️", "🟩", "⬜", "⬜", "⬜"],
                ["🟨", "🟨", "🟨", "🌉", "🟩", "🟩", "🟩", "🟩", "⬜", "⬜", "⬜"],
                ["🌵", "🟨", "💰", "🟦", "⬛", "⬛", "⬛", "🟩", "⬜", "⬜", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "⬛", "🚪", "⬛", "🟩", "⬜", "⬜", "🆚"],
                ["🟨", "🪨", "🟨", "🟦", "🧙", "🟩", "🟦", "🟩", "⬜", "⬜", "⬜"],
                ["🟨", "🟨", "🟦", "🟩", "🟩", "🟩", "🌉", "🟩", "🦊", "⬜", "⬜"],
                ["🌵", "🟦", "🟩", "🟩", "🌲", "🟩", "🟦", "🎁", "⬜", "⬜", "⬜"],
                ["🟦", "🟦", "🟩", "🟩", "🟩", f"{self.player_token}", "🟦", "🟦", "⬜", "⬜", "☠️"]
        ]

        def tutorial_map(self):
            self.standing_on = "🟩"
            self.map_name = "Tutorial"
            self.map_area = "Testing Area"
            self.embed_color = 0xFFFFFF
            return [
                    ["⬛", "👛", "💰", "🎁", "🎒", "🚪", "🗝️", "☠️", "💀", "🦴", "⬛"],
                    ["🎄", "⬜", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🏪"],
                    ["🌳", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🏯"],
                    ["🌲", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🧙"],
                    ["🌴", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟫", "🟩", "🕴️"],
                    ["🌵", "🟨", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🏔️", "🟩", "⚔️"],
                    ["🏜️", "🟨", "🟩", "🌉", "🟩", "🥋", "🟩", "🟩", "🏞️", "🟩", "🏴‍☠️"],
                    ["⬛", "🦇", "🟩", "🟦", "🎒", "🟩", "🎒", "🟩", "⛰️", "🆚", "⬛"],
                    ["⬛", "⬛", "⬛", "⬛", "⬛", f"{self.player_token}", "⬛", "⬛", "⬛", "⬛", "⬛"]

            ]
        
        def select_random_map(self):
            random_number = random.randint(1, 100)
            if random_number <= 25:
                return map1(self)
            elif random_number <= 50:
                return map2(self)
            elif random_number <= 75:
                return map3(self)
            else:
                return map4(self)
            
        # self.map =  select_random_map(self)

        if self.is_easy_difficulty:
            self.map =  tutorial_map(self)
        elif self.is_hard_difficulty:
            self.map =  map4(self)
        else:
            self.map =  select_random_map(self)

        # self.map = self.generate_random_map()
        self.previous_map = self.map
        self.next_map = []
        
    #Functions begin here
    @listen()
    async def on_ready(self):
        print('RPG Cog is ready!')

    
    async def create_rpg(self, ctx, rpg_config):
        from cogs.play import Play as play
        await play.rpg_commands(self, ctx, rpg_config)

    
    def display_map(self):
        return "\n".join("".join(str(cell) for cell in row) for row in self.map)

    
    async def move_player(self, ctx, private_channel,  direction, rpg_msg, deferred=False):
        from ai import rpg_movement_ai_message
        self.warp_active = False
        # if not deferred:
        #     await ctx.defer()
        #     deferred = True
        interaction_points = self.interaction_points
        x, y = self.player_position
        start_x = x
        start_y = y
        new_x, new_y = x, y

        player_moved = False
        player_action = False
        player_warped = False
        if direction in ["5","6","7","8","9"]:
            player_warped = True


        cardinal = "in front of you"
        if direction == "2" and x >= 0:#up
            player_moved = True
            new_x -= 1
        elif direction == "3" and x < len(self.map):#down
            cardinal = "behind you"
            player_moved = True
            new_x += 1
        elif direction == "1" and y >= 0:#left
            cardinal = "on your left"
            player_moved = True
            new_y -= 1
        elif direction == "4" and y < len(self.map[0]):#right
            cardinal = "on your right"
            player_moved = True
            new_y += 1       
        
        if direction == "Q":
            self.moving = False
            self.adventuring = False
            self.previous_moves.append("🏁 Adventure has ended!")
            await crown_utilities.bless(self.player_gold, self.player1_did)
            if self.player1.gems:
                for universe in self.player1.gems:
                    query = {"DID": str(ctx.author.id)}
                    update_query = {
                        '$inc': {'GEMS.$[type].' + "GEMS": self.player_gems}
                    }
                    filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
                    res = await asyncio.to_thread(db.updateUser,query, update_query, filter_query)
            else:
               universe_to_add_gems = self.universe
               self.player1.save_gems(universe_to_add_gems, self.player_gems)
            
            embedVar = Embed(title=f"🗺️ | {self.universe} Adventure Ended!", description=textwrap.dedent(f"""
                """))           
            embedVar.set_footer(text="🗺️ | Reach the end of the map to complete the adventure!")

            await rpg_msg.edit(embed=embedVar,components=[])
            paginator = await self.leave_adventure_embed(ctx)
            await paginator.send(ctx)
            
        elif direction == "0":
            self.moving = False
            player_action = True
            self.warp_active = True
            self.previous_moves.append("🔍 Checking Nearby...")
            self.closest_warp_points = self.get_closest_warp_points(self.player_position)
            if self.above_position in interaction_points:
                cardinal = "⬆️ In front of you"
                self.previous_moves.append(f"{cardinal} there is a {self.map[x-1][y]}{get_emoji_label(self.map[x-1][y])}!")
            if self.below_position in interaction_points:
                cardinal = "⬇️ Behind you"
                self.previous_moves.append(f"{cardinal} there is a {self.map[x+1][y]}{get_emoji_label(self.map[x+1][y])}!")
            if self.left_position in interaction_points:
                cardinal = "⬅️ On your left"
                self.previous_moves.append(f"{cardinal} there is a {self.map[x][y-1]}{get_emoji_label(self.map[x][y-1])}!")
            if self.right_position in interaction_points:
                cardinal = "➡️ On your right"
                self.previous_moves.append(f"{cardinal} there is a {self.map[x][y+1]}{get_emoji_label(self.map[x][y+1])}!")
            if self.standing_on in interaction_points:
                self.previous_moves.append(f"You standing on a {self.standing_on}{get_emoji_label(self.standing_on)}!")
        elif direction == "u" or direction == "d" or direction == "l" or direction == "r" or direction == "s":
            player_action = True
            if direction == "u":
                npc = self.above_position
                await self.rpg_action_handler(ctx, private_channel, self.player_position, npc, (x-1, y), direction)
            if direction == "d":
                npc = self.below_position
                await self.rpg_action_handler(ctx, private_channel, self.player_position, npc, (x+1, y), direction)
            if direction == "l":
                npc = self.left_position
                await self.rpg_action_handler(ctx, private_channel, self.player_position, npc, (x, y-1), direction)
            if direction == "r":
                npc = self.right_position
                await self.rpg_action_handler(ctx, private_channel, self.player_position, npc, (x, y+1), direction)
            if direction == "s":#standing on
                npc = self.standing_on
                await self.rpg_action_handler(ctx, private_channel, self.player_position, npc, (x, y))
            self.moving = False
        # Update map with new player position
        if player_moved:
            # print("Player moved to:", new_x, new_y, "There is a", self.map[new_x][new_y], "there.")
            # print("Starting position:", self.player_position)
            if new_x < 0 or new_x >= len(self.map) or new_y < 0 or new_y >= len(self.map[0]):
                self.previous_moves.append(f"(🚫) You can't leave this area yet!")
                self.player_position = (x, y)  # Keep the player in the same position
            else:
                self.above_position = self.map[new_x - 1][new_y] if new_x > 0 else None
                self.below_position = self.map[new_x + 1][new_y] if new_x < len(self.map) - 1 else None
                self.left_position = self.map[new_x][new_y - 1] if new_y > 0 else None
                self.right_position = self.map[new_x][new_y + 1] if new_y < len(self.map[0]) - 1 else None

                if self.map[new_x][new_y] in self.passable_points:  # Only move to open paths
                    self.map[x][y] = f"{self.standing_on}"  # Reset old position
                    if (new_x, new_y) == self.starting_position:
                        self.previous_moves.append(f"(🏠) You are back at the starting position.")
                    self.standing_on = self.map[new_x][new_y]
                    self.map[new_x][new_y] = f"{self.player_token}"  # New position
                    self.player_position = (new_x, new_y)

                    # movement_msg = await rpg_movement_ai_message(self.player1_card_name, self.player_card_data.universe, direction, self.map[x-1][y], self.map[x+1][y], self.map[x][y-1], self.map[x][y+1])
                    # self.previous_moves.append(movement_msg)
                elif self.map[new_x][new_y] in self.open_door:  # Can't move to doors
                    self.previous_moves.append(f"({self.open_door}) Moving into the next room {cardinal}")
                    next_map, changing_map = self.generate_new_map()
                    self.map = self.next_map
                    self.get_player_sorroundings(changing_map)
                    
                    #Create action to generate a randomly generated new map for the next room create a linked list to store the previous map and the new map and connect the entrance via the door

                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.walls:  # Can't move to walls
                    self.previous_moves.append(f"(🚫) There is a wall {cardinal}...")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.looted_trees:  # Can't move to looted trees
                    self.previous_moves.append(f"(🌴) There is a looted tree {cardinal}...if I had an Axe....")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.trees:  # Can't move to trees
                    self.previous_moves.append(f"(🌲) There is a tree {cardinal}...Try checking it out?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.resources:  # Can't move to resources
                    self.previous_moves.append(f"(🪨) There is a resource {cardinal}...maybe you can mine it?")
                elif self.map[new_x][new_y] in self.moving_water:  # Can't move to water
                    self.previous_moves.append(f"(🌊) There is moving water {cardinal}...wish I had a bridge...")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.still_water:  # Can't move to water
                    self.previous_moves.append(f"(🟦) There is still water {cardinal}...wish I had a bridge...or a pole?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.merchants:  # Can't move to merchants
                    self.previous_moves.append(f"(🏪) There is a merchant {cardinal}...maybe you can buy something?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.wildlife:  # Can't move to wildlife
                    self.previous_moves.append(f"(🦊) There is a wildlife {cardinal}...maybe you can hunt it?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.doors:  # Can't move to doors
                    self.previous_moves.append(f"(🚪) There is a door {cardinal}...maybe you can open it?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.keys:  # Can't move to keys
                    self.previous_moves.append(f"(🗝️) There is a key {cardinal}...maybe you can pick it up?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.items:  # Can't move to items
                    self.previous_moves.append(f"(🎒) There is an item {cardinal}...maybe you can pick it up?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.remains:  # Can't move to remains
                    self.previous_moves.append(f"(💀) There is a remains {cardinal}...maybe you can check it out?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.food:  # Can't move to food
                    self.previous_moves.append(f"(🥩) There is food {cardinal}...maybe you can pick it up?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.combat_points:  # Can't move to combat points
                    self.previous_moves.append(f"(⚔️) There is a combat point {cardinal}...maybe you can fight?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.mountains:  # Can't move to mountains
                    self.previous_moves.append(f"(⛰️) There is a mountain {cardinal}...maybe there is an area you can climb?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.climable_mountains:  # Can't move to mountains
                    self.previous_moves.append(f"(🏞️) There is a mountain.. I can see some rope! {cardinal}...if only I had climbing gear?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.bridges:  # Can't move to bridges
                    self.previous_moves.append(f"(🌉) There is a bridge {cardinal}...maybe you can cross it?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in self.civ_tokens:  # Can't move to civilians
                    self.previous_moves.append(f"(👥) There is a civilian {cardinal}...maybe you can talk to them?")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in crown_utilities.rpg_npc_emojis:
                    self.previous_moves.append(f"(👥) There is a {crown_utilities.rpg_npc[self.map[new_x][new_y]]} {cardinal}.")
                    self.player_position = self.player_position
                elif self.map[new_x][new_y] in interaction_points:
                    self.previous_moves.append(f"(🔍) You found a {self.map[new_x][new_y]} {cardinal}!")
                    self.player_position = self.player_position
                elif not player_action:
                    self.previous_moves.append(f"(👁️‍🗨️) There is a {self.map[new_x][new_y]} {cardinal}.")
                    self.player_position = self.player_position
                elif player_action and not player_moved:
                    return
                else:
                    self.previous_moves.append("Create action for this interaction!")
                await self.get_player_sorroundings()
        
        if player_warped:
            # self.previous_moves.append(f"(🌀) You warped to a new location!")
            await self.handle_warp_movement(ctx, int(direction)-5)
            #self.player_position = (new_x, new_y)
            await self.get_player_sorroundings()
            relative_direction = self.get_relative_direction(self.player_position,self.warp_point_position)
            await self.rpg_action_handler(ctx, ctx.channel, self.player_position, self.warp_target_type, self.warp_point_position, relative_direction)
            self.warp_active = False   


    async def get_player_sorroundings(self, new_map = False):
        x, y = self.player_position
        self.above_position = self.map[x-1][y] if x-1 >= 0 else None
        self.below_position = self.map[x+1][y] if x+1 < len(self.map) - 1 else None
        self.left_position = self.map[x][y-1] if y-1 >= 0 else None
        self.right_position = self.map[x][y+1] if y+1 < len(self.map[0]) - 1 else None
    
    #movement
    def get_map_message(self):
        map_display = self.display_map()
        # flavor_text = "The adventurer roams the mysterious labyrinth. Each step brings new discoveries and hidden dangers."
        # self.previous_moves.append(flavor_text)
        return f"{map_display}"

    
    def set_rpg_options(self, left=None, right=None, up=None, down=None):
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
        if self.encounter:
            encounter_buttons = [
                    Button(
                        style=ButtonStyle.BLUE,
                        label="💬 Talk",
                        custom_id="talk"
                    ),
                    Button(
                        style=ButtonStyle.GREEN,
                        label="👑 Fight",
                        custom_id="fight"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="💨Run",
                        custom_id="run"
                    )
        ]
        else:
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
                    label="🔍Check Nearby",
                    custom_id=f"{self._uuid}|0"
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="Save & Quit",
                    custom_id=f"{self._uuid}|Q"
                ),
            ]

            #Add world interaction Buttons
            if left and (left in self.interaction_points or left in self.combat_points):
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"{self.left_position}",
                        custom_id=f"{self._uuid}|l"
                    )
                )
            if right and (right in self.interaction_points or right in self.combat_points):
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"{self.right_position}",
                        custom_id=f"{self._uuid}|r"
                    )
                )
            if up and (up in self.interaction_points or up in self.combat_points):
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"{self.above_position}",
                        custom_id=f"{self._uuid}|u"
                    )
                )
            if down and (down in self.interaction_points or down in self.combat_points):
                world_buttons.append(
                    Button(
                        style=ButtonStyle.GREEN,
                        label=f"{self.below_position}",
                        custom_id=f"{self._uuid}|d"
                    )
                )
        
            #Add Warp Buttons
            if self.warp_active:
                warp_points = self.get_closest_warp_points(self.player_position)
                for i, point in enumerate(warp_points):
                    warp_buttons.append(
                        Button(
                            style=ButtonStyle.GRAY,
                            label=f"{point['type']}{emoji_labels[point['type']]}",
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
                 
    
    async def rpg_player_move_embed(self, ctx, private_channel, rpg_msg):
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
        
        self.set_rpg_options()
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

        equipment_message = f""
        currency_message = f""
        skill_message = f""
        if len(self.player_inventory) > 0:
            self.inventory_active = True
            equipment_message = f"__[🎒]Your Equipment__"
            for item in self.player_inventory:
                equipment_message += f"\n|{item['USE']} {item['ITEM']}"
        if self.player_gold > 0 or self.player_gems > 0:
            self.currency_active = True
            if self.player_gold > 0:
                currency_message += f"\n|{self.get_gold_icon(self.player_gold)}{self.player_gold} gold"
            if self.player_gems > 0:
                currency_message += f"\n|{self.get_gem_icon(self.player_gems)}{self.player_gems} gems"
        if len(self.player_skills) > 0:
            self.skills_active = True 
            for skill in self.player_skills:
                skill_message += f"|{skill}"
        rpg_map_embed = self.get_map_message()
        embedVar = Embed(title=f"[🌎]Exploring: {self.map_name}",description=f"**[🗺️]** *{self.map_area}*", color=0xFFD700)
        embedVar.set_author(name=f"{self.player1.disname}'s Adventure", icon_url=f"{self.player1.avatar}")
        if self.inventory_active:
            embedVar.add_field(name=f"**[🎒]Inventory**", value=f"{equipment_message}")
        if self.currency_active:
            embedVar.add_field(name=f"**[👛]Currency**", value=f"{currency_message}")
        if self.skills_active:
            embedVar.add_field(name=f"**[🥋]Skills**", value=f"{skill_message}")
        embedVar.add_field(name=f"[{self.player_token}]My Player Token", value=f"**[{self.standing_on}]** *Standing On {get_ground_type(self.standing_on)}*\n{rpg_map_embed}")
        embedVar.set_thumbnail(url=self.player_card_image)
        embedVar.set_footer(text=self.get_previous_moves_embed())
        # await rpg_msg.delete(delay=1)
        # await asyncio.sleep(1)
        await rpg_msg.edit(embed=embedVar, components=components)
        self._rpg_msg = rpg_msg
        return rpg_msg, components

    
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
                await self.rpg_player_move_embed(ctx, private_channel, rpg_msg)
        
    #Interactions
    async def rpg_action_handler(self,ctx, private_channel, player_position, npc, npc_position, direction=None):
        x, y = player_position

        if npc in self.interaction_points:
            if npc in self.items:
                random_number = random.randint(1, 100)
                if npc == "🎒":
                    self.previous_moves.append(f"(🎒) You found lost inventory!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                    await self.rpg_action_handler(ctx, private_channel, player_position, "👛", npc_position, direction)
                    if random_number <= 75:
                        self.previous_moves.append(f"(🎁) There's alot here! You found a 💰!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "💰", npc_position, direction)
                    if random_number <= 25:
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🎁", npc_position, direction)
                elif npc == "🎁":
                    self.previous_moves.append(f"(🎁) You found a treasure chest!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "💰", npc_position, direction)
                    if random_number <= 50:
                        self.previous_moves.append(f"(🎁) This chest is pretty full! You found another 👛!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "👛", npc_position, direction)
                    if random_number <= 10:
                        self.previous_moves.append(f"(🎁) There is a hidden compartment!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🎰", npc_position, direction)
                elif npc == "💰":
                    gold_found = random.randint(10, 100)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(💰) You gained {gold_found} gold!")
                    if random_number <= 25:
                        self.previous_moves.append(f"(💰) Something hidden deep in the bag...")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "👛", npc_position, direction)
                    elif random_number <= 50:
                        self.previous_moves.append(f"(💰) Something hidden in the bag...")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🪙", npc_position, direction)
                elif npc == "👛":
                    gold_found = random.randint(5, 50)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(👛) You found a bag of {gold_found} gold!")
                elif npc == "🪙":
                    gold_found = random.randint(1, 10)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(🪙) You found {gold_found} gold!")
                self.map[npc_position[0]][npc_position[1]] = f"{self.standing_on}" #upadte map with new position
            elif npc in self.drops:
                success = None
                if npc == "🎴":
                    all_available_drop_cards = db.querySpecificDropCards(self.universe)
                    cards = [x for x in all_available_drop_cards]
                    selected_card = crown_utilities.create_card_from_data(random.choice(cards))
                    success = self.player1.save_card(selected_card)
                    if success:
                        self.card_drops.append(f"|🎴{selected_card.name}")
                        self.previous_moves.append(f"You found 🎴{selected_card.name}!")
                if npc == "🎗️":
                    title_drop = db.get_random_title({"UNIVERSE": self.universe}, self.player1)
                    success = self.player1.save_title(self.universe, title_drop)
                    if success:
                        self.title_drops.append(f"|🎗️{title_drop}**")
                        self.previous_moves.append(f"You found 🎗️{title_drop}!")
                    else:
                        self.previous_moves.append(f"You found 🎗️{title_drop} but you already have the maximum amount!!")
                if npc == "🦾":
                    arm_query = {'UNIVERSE': self.universe, 'DROP_STYLE': "TALES", 'ELEMENT': ""}
                    arm_drop = db.get_random_arm(arm_query, self.player1)
                    success = self.player1.save_arm(arm_drop, True)
                    if success:
                        self.arm_drops.append(f"|🦾{arm_drop}")
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
                        self.summon_drops.append(f"|🧬{summon_drop.name}")
                        self.previous_moves.append(f"You found 🧬{summon_drop.name}!")
                    else:
                        self.previous_moves.append(f"You found 🧬{summon_drop.name} but you already have the maximum amount!!")
                if npc == "🆙":  
                    self.previous_moves.append(f"(🆙) You found a XP Boost!")
                    await crown_utilities.cardlevel(self.player1, "RPG", 1)
            elif npc in self.merchants:
                if npc == "🏪":
                    #Send embed here with merchant options to buy after making a choice, sent the map message again for interaction
                    self.previous_moves.append(f"(🏪) Interacting with Merchant")
                    if self.player_gold > 100:
                        self.previous_moves.append(f"(🏪) The Merchant sells you a hammer for 🪙100")
                        self.player_gold -= 100
                        self.player_inventory.append({'ITEM': "🔨", 'USE': "*Infinite*"})
                        self.hammer = True
                    else:  
                        self.previous_moves.append(f"(🏪) This Merchant sells you a hammer for 🪙100....come back later")
                if npc == "🧙":
                    #Send embed here with merchant options to buy after making a choice, sent the map message again for interaction
                    self.previous_moves.append(f"(🧙) Interacting with Magic Merchant")
                if npc == "🕴️":
                    #Send embed here with merchant options to buy after making a choice, sent the map message again for interaction
                    self.previous_moves.append(f"(🕴️) Interacting with Black Market Dealer")
                if npc == "🏯":
                    #Send embed here with merchant options to buy after making a choice, sent the map message again for interaction
                    self.previous_moves.append(f"(🏯) Interacting with Skill Merchant")
            elif npc in self.wildlife:
                if npc == "🦊":
                    self.previous_moves.append(f"(🦊) You encountered a fox!")
                    random_number = random.randint(1, 50)
                    if random_number <= 50:
                        self.previous_moves.append(f"(🆚) You are under attack!")
                        await self.create_rpg_battle(ctx, private_channel)
                        if self.combat_victory:
                            self.previous_moves.append(f"({self.universe_npc_token}) You loot the body and find a key!")
                            await self.rpg_action_handler(ctx, private_channel, player_position, "🗝️", npc_position, direction)
                    else:
                        self.previous_moves.append(f"(🌲) The fox ran off after a crack in the woods...best to keep a lookout")
                if npc == "🦇":
                    self.previous_moves.append(f"(🦇) You encountered a bat!")
                    random_number = random.randint(1, 100)
                    if random_number <= 50:
                        self.previous_moves.append(f"(🆚) You are under attack!")
                        await self.create_rpg_battle(ctx, private_channel)
                        if self.combat_victory:
                            self.previous_moves.append(f"(🕴️) The bat is transforming... it was a Black Market Dealer!")
                            self.map[npc_position[0]][npc_position[1]] = f"🕴️"
                            self.combat_victory = False
                            await self.rpg_action_handler(ctx, private_channel, player_position, "🕴️", npc_position, direction)
                    else:
                        self.previous_moves.append(f"(🦇) The bat flew off...")
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
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎯", npc_position, direction)
                    #find book and learn skill
                self.map[npc_position[0]][npc_position[1]] = f"{self.standing_on}"
            elif npc in self.food:
                if npc == "🥩":
                    self.previous_moves.append(f"(🥩) You found a steak!")
                if npc == "🍖":
                    self.previous_moves.append(f"(🍖) You found a roast!")
                if npc == "🥕":
                    self.previous_moves.append(f"(🥕) You found a carrot!")
                elif npc in self.inventory:
                    self.previous_moves.append(f"({npc}) added to inventory")
                    food_found = False
                    for item in self.player_inventory:
                        if item['ITEM'] == npc:
                            item['USE'] += 1
                            food_found = True
                            break
                    if not food_found:
                        self.player_inventory.append({'ITEM': npc, 'USE': 1})
                    self.map[npc_position[0]][npc_position[1]] = f"{self.standing_on}"
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
                self.map[npc_position[0]][npc_position[1]] = f"{self.standing_on}"
            elif npc in self.doors:
                for item in self.player_inventory:
                    if item['ITEM'] == "🗝️":
                        if item['USE'] > 0:
                            self.previous_moves.append(f"(🚪) You unlocked the door!")
                            item['USE'] -= 1
                            if item['USE'] <= 0:
                                self.player_inventory.remove(item)
                            self.map[npc_position[0]][npc_position[1]] = f"{self.open_door}"
                        break
                else:
                    self.previous_moves.append(f"(🚪) You need a key to unlock this door!")
            elif npc in self.bridges:
                crossed = False
                random_number = random.randint(1, 100)
                #Get direction of bridge
                if direction == "u":
                    new_position = (npc_position[0] - 1, npc_position[1])
                elif direction == "d":
                    new_position = (npc_position[0] + 1, npc_position[1])
                elif direction == "l":
                    new_position = (npc_position[0], npc_position[1] - 1)
                elif direction == "r":
                    new_position = (npc_position[0], npc_position[1] + 1)

                if random_number <= 25:
                    self.previous_moves.append(f"(🌉) There is some loot on the bridge...")
                    random_number_combat = random.randint(1, 100)
                    if random_number_combat <= 50:
                        self.previous_moves.append(f"(🆚) It's a trap! You are under attack!")
                        #if battle won give loot, else lose coin and cross
                        await self.create_rpg_battle(ctx, private_channel)
                        if self.combat_victory:
                            self.previous_moves.append(f"(🌉) You found a hidden chest!")
                            self.combat_victory = False
                            await self.rpg_action_handler(ctx, private_channel, player_position, "🎁", npc_position)
                    else:
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🎲", npc_position, direction)
                elif random_number <= 50:
                    self.previous_moves.append(f"(🆚) There is a roadblock on the bridge...You are under attack!")
                    await self.create_rpg_battle(ctx, private_channel)
                    if self.combat_victory:
                        self.previous_moves.append(f"(🌉) You found a hidden chest!")
                        self.combat_victory = False
                        await self.rpg_action_handler(ctx, private_channel, player_position, "🎁", npc_position)
                elif random_number <= 75:
                    self.previous_moves.append(f"(🌉) There is a hole in the bridge...")
                    if self.hammer:
                        self.previous_moves.append(f"(🌉) You fixed the bridge with your Hammer!")
                        if self.engineer:
                            self.previous_moves.append(f"(🌉) The Civilians pay you for your service! [💰+1000]")
                        self.map[npc_position[0]][npc_position[1]] = f"{self.standing_on}"
                    else:
                        self.previous_moves.append(f"(🌉) There is a hole in the bridge...if only I had a hammer")
                else:
                    self.previous_moves.append(f"(🌉) You crossed the bridge!")
                    crossed = True
                if crossed:
                    self.map[new_position[0]][new_position[1]] = f"{self.player_token}"
                    self.map[x][y] = f"{self.standing_on}"
                    self.player_position = new_position
            elif npc in self.moving_water:
                self.previous_moves.append(f"(🌊) You can't swim in moving water! If only you had a boat...But maybe there is a bridge?")
            elif npc in self.still_water:
                self.previous_moves.append(f"(🟦) You can't swim yet...If only you had a pole??")
            elif npc in self.trees:
                self.previous_moves.append(f"({npc}) You searched a tree!")
                if self.map[npc_position[0]][npc_position[1]] in self.looted_trees:
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
                    await self.rpg_action_handler(ctx, private_channel, player_position, random_item, npc_position, direction)
                elif random.random() < 0.66:
                    self.previous_moves.append(f"({npc}) You found nothing...")
                else:
                    self.previous_moves.append(f"(🆚) You are under attack!")
                    await self.create_rpg_battle(ctx, private_channel)
                    if self.combat_victory:
                        self.previous_moves.append(f"({npc}) You loot the body!")
                        await self.rpg_action_handler(ctx, private_channel, player_position, "👛", npc_position, direction)
                self.map[npc_position[0]][npc_position[1]] = f"🌴"
            elif npc in self.cactus:
                self.previous_moves.append(f"({npc}) You searched a cactus!")
                if self.map[npc_position[0]][npc_position[1]] in self.looted_cactus:
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
                    self.map[npc_position[0]][npc_position[1]] = f"{self.looted_mountain}"
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
                        miner_bonus = random.randint(1000, 5000)
                        miner_bonus_message = f"[⚒️+{miner_bonus} Gems!]"
                    gems_gained = random.randint(100,1000) + miner_bonus
                    if npc in self.gems:
                        gems_gained = gems_gained * 2
                        self.previous_moves.append(f"({npc}) You found Raw Gems!")
                    else:
                        self.previous_moves.append(f"({npc}) You found Gemstone!")
                    self.player_gems += gems_gained
                    self.previous_moves.append(f"(⛏️) You mined 💎{gems_gained} Gems! [{miner_bonus_message}]")
                    if not self.miner:
                        self.miner = True
                        self.previous_moves.append(f"(⛏️) You gained the Miner Skill! [⛏️]")
                    self.map[npc_position[0]][npc_position[1]] = f"{self.standing_on}"
                else:
                    self.previous_moves.append(f"({npc}) Inspecting the stone you found a ⛏️Pickaxe!")
                    self.pickaxe = True
                    self.player_inventory.append({'ITEM': "⛏️", 'USE': "*Infinite*"})
                    self.player_skills.append("⛏️")
            elif npc in self.civ_tokens:
                self.previous_moves.append(f"({npc}) You encountered a civilian!")
                gender, identity = search_emoji(emojis, npc)
                #add identity handler that looks at emoji and returns a unique identifier that can later be replaced by our ai, this is for a demo
                self.previous_moves.append(f"({npc}) The {identity} {gender} says hi.")
        elif npc in self.loot_rolls:#if not interactino then loot roll or combats
            if npc == "🎲":
                roll = random.randint(1, 6)
                if roll == 1:
                    gold_found = random.randint(1, 10)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(🪙) You got {gold_found} gold!")
                elif roll == 2:
                    gold_found = random.randint(5, 50)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(👛) You got a empty bag of {gold_found} gold!")
                elif roll == 3:
                    gold_found = random.randint(40, 50)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(👛) You got a full bag of {gold_found} gold!")
                elif roll == 4:
                    gold_found = random.randint(50, 100)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(💰) You got a bonus sack {gold_found} gold!")
                elif roll == 5:
                    gold_found = random.randint(100, 200)
                    self.player_gold += gold_found
                    self.previous_moves.append(f"(💰) You got a heavy sack of {gold_found} gold!")
                elif roll == 6:
                    self.previous_moves.append(f"(🔍) Checking their inventory....")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎯", npc_position, direction)
            if npc == "🎯":
                random_number = random.randint(1, 100)
                if random_number <= 80:
                    self.previous_moves.append(f"(🎁) You got a chest")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎁", npc_position, direction)
                else:
                    self.previous_moves.append(f"(🎒) You got lost Inventory!")
                    await self.rpg_action_handler(ctx, private_channel, player_position, "🎒", npc_position, direction)
            if npc == "🎰":
                random_number = random.randint(1, 100)
                if random_number <= 1:
                    self.previous_moves.append(f"(🎰) You got a jackpot!")
                    gold_found = random.randint(100, 1000)
                    self.player_gold += gold_found
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
            #After combat turn into remains based on combat type for additional loot rolls
            self.encounter = True
            self.previous_moves.append(f"(🆚) Entering Encounter Mode!")
            if npc == "🥋":
                self.previous_moves.append(f"(🥋) You encountered a training dummy!")
                await self.create_rpg_battle(ctx, private_channel, tutorial=True)
            else:
                await self.create_rpg_battle(ctx, private_channel)
            if (npc == "⚔️" or npc == "🆚") and self.combat_victory:
                self.previous_moves.append(f"(🆚) You defeated the enemy!")
                self.map[npc_position[0]][npc_position[1]] = f"💀"
                self.combat_victory = False

        if self.combat_victory:
            self.combat_victory = False

        await self.get_player_sorroundings()
    
    
    async def create_rpg_battle(self, ctx, private_channel, tutorial = False):
        from cogs.classes.battle_class import Battle
        from cogs.battle_config import BattleConfig
        if not self.battling and not self.encounter:
            return
        if tutorial:
            from cogs.game_modes import tutorial
            tutorial_match = await tutorial(self, ctx,self._player, "Tutorial")
            # self.battling = False
            self.encounter = True
            self.set_rpg_options()
            await self.rpg_player_move_embed(ctx, private_channel, self._rpg_msg)
        else:
            self.encounter = True
            # self.battling = True
            battle = Battle("RPG", self._player)
            battle.rpg_map = self.display_map()
            battle.rpg_config = self
            await self.rpg_player_move_embed(ctx, private_channel, self._rpg_msg)
            battle.rpg_msg = self._rpg_msg
            all_available_drop_cards = db.querySpecificDropCards(self.universe)
            cards = [x for x in all_available_drop_cards]
            selected_card = crown_utilities.create_card_from_data(random.choice(cards))
            selected_card.set_affinity_message()
            selected_card.set_explore_bounty_and_difficulty(battle)

            battle.is_rpg_game_mode = True
            battle.set_explore_config(self.universe_data, selected_card)
            #battle.is_explore_game_mode = False

            battle.bounty = selected_card.bounty

            self.set_rpg_options()
        
            encounter_buttons_action_row = ActionRow(*self.encounter_buttons)

            embedVar = Embed(title=f"**{selected_card.approach_message}{selected_card.name}**",
                                        description=textwrap.dedent(f"""\
            **Rewards** **{selected_card.bounty_message}**
            {selected_card.battle_message}
            """), color=0xf1c40f)

            embedVar.set_image(url="attachment://image.png")
            embedVar.set_thumbnail(url=self.player_avatar)
            embedVar.set_footer(text=f"Use /quit to flee this encounter",icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
            
            image_binary = selected_card.showcard()
            image_binary.seek(0)
            card_file = File(file_name="image.png", file=image_binary)

            #setchannel = interactions.utils.get(channel_list, name=server_channel)
            player_ping = await private_channel.send(f"🌌{ctx.author.mention}")
            await player_ping.delete(delay=3) 
            msg = await private_channel.send(embed=embedVar, file=card_file, components=[encounter_buttons_action_row])     

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx  = await self.bot.wait_for_component(components=[encounter_buttons_action_row], timeout=300, check=check)
                await button_ctx.ctx.defer(edit_origin=True)
                if button_ctx.ctx.custom_id == "fight":
                    self.battling = True
                    await BattleConfig.create_rpg_battle(self, ctx, battle)
                    await msg.edit(components=[])
                    await msg.delete()

                if button_ctx.ctx.custom_id == "talk":
                    #if talk works reward else batttle
                    randum_number = random.randint(1, 100)
                    if randum_number <= 75:
                        embedVar = Embed(title=f"**{selected_card.name}** Says hello and allows you to leave", description="Maybe I need to complete a quest?", color=0xf1c40f)
                        self.battling = False
                        self.encounter = False
                    else:
                        embedVar = Embed(title=f"**{selected_card.name}** Doesn't want to talk", description="It's time to fight!", color=0xf1c40f)
                        self.battling = True # For Now
                        await private_channel.send(embed=embedVar)
                        await BattleConfig.create_rpg_battle(self, ctx, battle)
                        await msg.edit(components=[])
                        await msg.delete()
                if button_ctx.ctx.custom_id == "run":
                    randum_number = random.randint(1, 100)
                    randum_number += self.player_speed
                    if randum_number >= 25:
                        self.previous_moves.append(f"(💨) You ran away!")
                        self.battling = False
                        self.encounter = False
                    else:
                        self.previous_moves.append(f"(🆚) You failed to run away!")
                        self.battling = True
                        await BattleConfig.create_rpg_battle(self, ctx, battle)
                    await msg.edit(components=[])
                    await msg.delete()
                    return
            except Exception as ex:
                await msg.edit(components=[])
                custom_logging.debug(ex)

    #Warp Movement
    async def handle_warp_movement(self, ctx, warp_index):
        warp_target = self.closest_warp_points[int(warp_index)]
        warp_point_position = warp_target['position']
        self.warp_point_position = warp_point_position
        new_position = self.get_closest_passable_space(warp_point_position)
        #Check if new position is a valid position , within range and on a passable square
        self.map[self.player_position[0]][self.player_position[1]] = self.standing_on
        self.standing_on = self.map[new_position[0]][new_position[1]]
        self.map[new_position[0]][new_position[1]] = self.player_token
        self.player_position = new_position
        self.warp_target_type = warp_target['type']
        self.previous_moves.append(f"Warped to the {warp_target['type']}{get_emoji_label(warp_target['type'])}!")
 

    def get_closest_warp_points(self, current_position, num_points=5):
        warp_distances = []
        cx, cy = current_position
        index = 5
        for warp in self.warp_points:
            for i in range(len(self.map)):
                for j in range(len(self.map[i])):
                    if self.map[i][j] == warp:
                        distance = abs(cx - i) + abs(cy - j)
                        warp_distances.append({'position': (i, j), 'type': warp, 'distance': distance})
                        index+= 1
        warp_distances.sort(key=lambda x: x['distance'])
        return warp_distances[:num_points]
    
    
    def get_closest_passable_space(self, position):
        x, y = position
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.map) and 0 <= ny < len(self.map[0]) and self.map[nx][ny] in self.passable_points:
                return (nx, ny)
        return position  # Return the original position if no passable space found

    
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
        
    
    async def leave_adventure_embed(self, ctx):
        from cogs.classes.custom_paginator import Paginator
        gold_message = f"[{self.get_gold_icon(self.player_gold)}] {self.player_gold} Coins"
        gem_message = f"[{self.get_gem_icon(self.player_gems)}] {self.player_gems} Gems"
        
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

        embedVar = Embed(title=f"👤 Adventure Inventory!", description="🏆 You have completed your adventure! 🏆\n*Your Equipment, Currency and Skills Below*", color=0xFFD700)
        embedVar.add_field(name=f"**[🎒]Your Equipment**", value=f"|{inventory_message}")
        embedVar.add_field(name=f"**[🥋]Skills**", value=f"|{skills_message}")
        embedVar.add_field(name=f"**[👛]Currency**", value=f"{gold_message}\n{gem_message}")
        embedVar.set_footer(text="🃏 Build Details on the next page!")

        lootEmbed = Embed(title=f"🎉 Adventure Rewards!", description="🏆 You have completed your adventure! 🏆\n*Your Adventure rewards will be shown below*", color=0xFFD700)
        if len(self.card_drops) > 0:
            lootEmbed.add_field(name=f"**🎴 Cards**", value=f"{self.card_drops}")
        if len(self.title_drops) > 0:
            lootEmbed.add_field(name=f"**🎗️ Titles**", value=f"{self.title_drops}")
        if len(self.arm_drops) > 0:
            lootEmbed.add_field(name=f"**🦾 Arms**", value=f"{self.arm_drops}")
        if len(self.summon_drops) > 0:
            lootEmbed.add_field(name=f"**🧬 Summons**", value=f"{self.summon_drops}")
        lootEmbed.set_footer(text="👤 Adventure Summary on the Next Page!")

        buildEmbed = Embed(title=f"🃏 Adventure Build!", description="🏆 You have completed your adventure! 🏆\n*Your Adventure Build will be shown below*", color=0xFFD700)
        buildEmbed.add_field(name=f"**🎗️ Title**", value=f"{self.player1_title}")
        buildEmbed.add_field(name=f"**🎴 Card**", value=f"{self.player1_card_name}")
        buildEmbed.add_field(name=f"**🦾 Arm**", value=f"{self.player1_arm}")
        buildEmbed.add_field(name=f"**🧬 Summon**", value=f"{self.player1_summon_name}")
        buildEmbed.add_field("**📿 Talisman**", value=f"{self.player1_talisman}")
        buildEmbed.set_footer(text="🗺️ Adventure Map on the next page!")


        map_embed = Embed(title=f"🗺️ Adventure Log", description=f"**🌎** | *{self.map_name}*\n**🗺️** | *{self.map_area}*\n{self.get_map_message()}", color=0xFFD700)
        map_embed.set_footer(text=f"{self.get_previous_moves_embed()}")

        embed_list = [lootEmbed,embedVar,buildEmbed,map_embed]
        paginator = Paginator.create_from_embeds(self.bot, *embed_list)
        paginator.show_select_menu = True
        return paginator


    def get_gold_icon(self,balance):
        icon = "🪙"

        if balance >=100:
            icon = "👛"
        if balance >= 1000:
            icon = "💰"
        return icon
    

    def get_gem_icon(self,balance):
        icon = "💎"

        if balance >=5000:
            icon = "💍"
        if balance >= 25000:
            icon = "👑"
        return icon

    
    def close_rpg_embed(self, player_card, opponent_card):
        if self.is_rpg:
            close_message = "Adventure Battle"
            picon = "🗺️"
            f_message = f"🗺️ | Adventure Cut Short..."
            
            
        embedVar = Embed(title=f"{picon} {opponent_card.universe} {close_message} Ended!", description=textwrap.dedent(f"""
            """))
        return embedVar


emojis = {
    'man': [
        "👨", "👨‍⚕️", "👨‍🌾", "👨‍🍳", "👨‍🎓", "👨‍🎤", "👨‍🏫", "👨‍🏭", "👨‍💻", "👨‍💼", "👨‍🔧", "👨‍🔬",
        "👨‍🚀", "👨‍🚒", "👮‍♂️", "🕵️‍♂️", "👷‍♂️", "🤴", "👳‍♂️", "👲", "🧔", "👱‍♂️", "👨‍🦰", "👨‍🦱", 
        "👨‍🦳", "👨‍🦲", "🧓", "👴", "👶‍♂️"
    ],
    'woman': [
        "👩", "👩‍⚕️", "👩‍🌾", "👩‍🍳", "👩‍🎓", "👩‍🎤", "👩‍🏫", "👩‍🏭", "👩‍💻", "👩‍💼", "👩‍🔧", "👩‍🔬",
        "👩‍🚀", "👩‍🚒", "👮‍♀️", "🕵️‍♀️", "👷‍♀️", "👸", "👳‍♀️", "👲", "🧕", "👱‍♀️", "👩‍🦰", "👩‍🦱",
        "👩‍🦳", "👩‍🦲", "🧓", "👵", "👶‍♀️"
    ],
    'little': [
        "👶", "🧒", "👦", "👧", "🧑‍🍼", "👶‍♂️", "👶‍♀️", "🧒‍♂️", "🧒‍♀️", "👦‍♂️", "👦‍♀️", "👧‍♂️", "👧‍♀️"
    ],
    'family': [
        "👪", "👨‍👩‍👦", "👨‍👩‍👧", "👨‍👩‍👧‍👦", "👨‍👩‍👦‍👦", "👨‍👩‍👧‍👧", "👨‍👨‍👦", "👨‍👨‍👧", "👨‍👨‍👧‍👦", 
        "👨‍👨‍👦‍👦", "👨‍👨‍👧‍👧", "👩‍👩‍👦", "👩‍👩‍👧", "👩‍👩‍👧‍👦", "👩‍👩‍👦‍👦", "👩‍👩‍👧‍👧", "👨‍👦", 
        "👨‍👦‍👦", "👨‍👧", "👨‍👧‍👧", "👩‍👦", "👩‍👦‍👦", "👩‍👧", "👩‍👧‍👧"
    ]
}

ground_types = {
    '🟨':'Sand',
    '⬜':'Snow',
    '🟩':'Grass',
}

emoji_labels = {
            "👨": "Man", "👨‍⚕️": "Man Doctor", "👨‍🌾": "Man Farmer", "👨‍🍳": "Man Cook", "👨‍🎓": "Man Student", 
            "👨‍🎤": "Man Singer", "👨‍🏫": "Man Teacher", "👨‍🏭": "Man Factory Worker", "👨‍💻": "Man Office Worker", 
            "👨‍💼": "Man Businessman", "👨‍🔧": "Man Mechanic", "👨‍🔬": "Man Scientist", "👨‍🚀": "Man Astronaut", 
            "👨‍🚒": "Man Firefighter", "👮‍♂️": "Policeman", "🕵️‍♂️": "Man Detective", "👷‍♂️": "Man Construction Worker", 
            "🤴": "Prince", "👳‍♂️": "Man with Turban", "👲": "Man with Hat", "🧔": "Bearded Man", "👱‍♂️": "Blond Man", 
            "👨‍🦰": "Red-Haired Man", "👨‍🦱": "Curly-Haired Man", "👨‍🦳": "White-Haired Man", "👨‍🦲": "Bald Man", "🧓": "Old Man", 
            "👴": "Elderly Man", "👶‍♂️": "Baby Boy", "👩": "Woman", "👩‍⚕️": "Woman Doctor", "👩‍🌾": "Woman Farmer", 
            "👩‍🍳": "Woman Cook", "👩‍🎓": "Woman Student", "👩‍🎤": "Woman Singer", "👩‍🏫": "Woman Teacher", 
            "👩‍🏭": "Woman Factory Worker", "👩‍💻": "Woman Office Worker", "👩‍💼": "Woman Businesswoman", 
            "👩‍🔧": "Woman Mechanic", "👩‍🔬": "Woman Scientist", "👩‍🚀": "Woman Astronaut", "👩‍🚒": "Woman Firefighter", 
            "👮‍♀️": "Policewoman", "🕵️‍♀️": "Woman Detective", "👷‍♀️": "Woman Construction Worker", "👸": "Princess", 
            "👳‍♀️": "Woman with Turban", "🧕": "Woman with Headscarf", "👱‍♀️": "Blond Woman", "👩‍🦰": "Red-Haired Woman", 
            "👩‍🦱": "Curly-Haired Woman", "👩‍🦳": "White-Haired Woman", "👩‍🦲": "Bald Woman", "👵": "Elderly Woman", 
            "👶‍♀️": "Baby Girl", "👶": "Baby", "🧒": "Child", "👦": "Boy", "👧": "Girl", "🧑‍🍼": "Person Feeding Baby", 
            "👶‍♂️": "Baby Boy", "👶‍♀️": "Baby Girl", "🧒‍♂️": "Boy", "🧒‍♀️": "Girl", "👦‍♂️": "Boy", "👦‍♀️": "Girl", 
            "👧‍♂️": "Boy", "👧‍♀️": "Girl", "👪": "Family", "👨‍👩‍👦": "Family", "👨‍👩‍👧": "Family", 
            "👨‍👩‍👧‍👦": "Family", "👨‍👩‍👦‍👦": "Family", "👨‍👩‍👧‍👧": "Family", "👨‍👨‍👦": "Family", 
            "👨‍👨‍👧": "Family", "👨‍👨‍👧‍👦": "Family", "👨‍👨‍👦‍👦": "Family", "👨‍👨‍👧‍👧": "Family", 
            "👩‍👩‍👦": "Family", "👩‍👩‍👧": "Family", "👩‍👩‍👧‍👦": "Family", "👩‍👩‍👦‍👦": "Family", 
            "👩‍👩‍👧‍👧": "Family", "👨‍👦": "Family", "👨‍👦‍👦": "Family", "👨‍👧": "Family", "👨‍👧‍👧": "Family", 
            "👩‍👦": "Family", "👩‍👦‍👦": "Family", "👩‍👧": "Family", "👩‍👧‍👧": "Family",
            # Other labels
            "🟫": "Wall", "⬛": "Wall", "🟩": "Grass", "⬜": "Snow", "🟨": "Sand", "🏞️": "Climable Mountain",
            "🏔️": "Mountain", "⛰️": "Mountain", "🌲": "Tree", "🌳": "Tree", "🎄": "Tree", "🌴": "Looted Tree",
            "🌊": "Moving Water", "🟦": "Still Water", "🌉": "Bridge", "🏪": "Merchant", "🧙": "Merchant", 
            "🕴️": "Merchant", "🏯": "Merchant", "🦊": "Wildlife", "🦇": "Wildlife", "🚪": "Door", "🛗": "Open Door", 
            "🗝️": "Key", "💰": "Sack o' Coin", "🪙": "Coin", "👛": "Coin Bag", "🎁": "Chest", 
            "🎒": "Lost Loot", "🦾": "Arm Drop", "🆙": "Xp Drop", "🎴": "Rare Drop", "🧬": "Rare Drop", 
            "🎗️": "Title Drop", "🎲": "Loot Roll", "🎯": "Loot Roll", "🎰": "Loot Roll", "🏊": "Swim", 
            "🪜": "Climbing", "🪓": "Cutting", "🎣": "Fishing","⛏️": "Mining", "🔨": "Repairing", "⚒️": "Engineer" , "💀": "Remains", "🦴": "Remains", "☠️": "Remains", 
            "🥩": "Food", "🍖": "Food", "🥕": "Food", "⚔️": "Combat Encounter", "🏴‍☠️": "Combat Encounter","🆚": "Combat Encounter", '🧱': "Ore",'🪨': "Rock",'🌵': 'Cactus',
            "🏜️": "Looted Cactus","🥋" : "Training Dummy"
        }

def get_emoji_label(emoji):
    return emoji_labels[emoji]


def get_ground_type(ground):
    return ground_types[ground]

# Function to search for an emoji
def search_emoji(emojis_dict, target_emoji):
    for category, emoji_list in emojis_dict.items():
        if target_emoji in emoji_list:
            return category, target_emoji
    return None, None

#