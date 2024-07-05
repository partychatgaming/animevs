import db
import crown_utilities
import interactions
import datetime
import textwrap
import time
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
        self._universe = "Unbound"
        self.adventuring = True
        self.moving = False

        self.above_position = None
        self.below_position = None
        self.left_position = None
        self.right_position = None
        self.starting_position = (8, 4)
    
        self._player = _player
        self.player1 = _player
        self.player_name = self.player1.disname
        self.player1_did = self.player1.did

        self.player1_card_name = self.player1.equipped_card
        self.player_card_data = crown_utilities.create_card_from_data(db.queryCard({'NAME': self.player1_card_name}))
        self.player_health = self.player_card_data.health
        self.player_attack = self.player_card_data.attack
        self.player_defense = self.player_card_data.defense
        self.player_speed = self.player_card_data.speed
        self.player_stamina = self.player_card_data.stamina

        self.player1_title = self.player1.equipped_title
        self.player1_arm = self.player1.equipped_arm
        self.player1_talisman = self.player1.equipped_talisman
        self.player1_summon_name = self.player1.equipped_summon
        self.player_summon_data = crown_utilities.create_summon_from_data(db.querySummon({'PET': self.player1_summon_name})) 

        self.difficulty = _player.difficulty
        self.player_token = crown_utilities.crest_dict[self.player_card_data.universe]
        self.is_easy_difficulty = False
        self.is_hard_difficulty = False
        self.is_normal_difficulty = False

        self.movement_buttons = []
        self.action_buttons = []
        self.world_buttons = []
        self.previous_moves = ["🗺️ Adventure has begun!"]
        self.previous_moves_len = len(self.previous_moves)

        self.interaction_points = ["🗝️", "🚪", "🦇", "🧙", "🦊", "🦴"]

        self.map =  [
            ["🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫"],
            ["🟫", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟫"],
            ["🟫", "🟩", "🗝️", "🟩", "🟩", "🟩", "🟩", "🟩", "🦴", "🟫"],
            ["🟫", "🟩", "🟩", "🟩", "🧙", "🧙", "🟩", "🟩", "🟩", "🟫"],
            ["🟫", "🟩", "🟩", "🟩", "🟩", "🟩", "🦇", "🟩", "🟩", "🟫"],
            ["🟫", "🟩", "🚪", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟫"],
            ["🟫", "🟩", "🟩", "🟩", "🦊", "🟩", "🟩", "🟩", "🟩", "🟫"],
            ["🟫", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟫"],
            ["🟫", "🟫", "🟫", "🟫", f"{self.player_token}", "🟫", "🟫", "🟫", "🟫", "🟫"]
        ]
        self.player_position = (8, 4)  # Initial position of universe_crest

    @listen()
    async def on_ready(self):
        print('RPG Cog is ready!')

    async def create_rpg(self, ctx, rpg_config):
        from cogs.play import Play as play
        await play.rpg_commands(self, ctx, rpg_config)

    def display_map(self):
        return "\n".join("".join(row) for row in self.map)

    async def move_player(self, direction, rpg_msg):
        from ai import rpg_movement_ai_message
        interaction_points = self.interaction_points
        x, y = self.player_position
        new_x, new_y = x, y
        player_moved = False

        if direction == "2" and x > 0:#up
            player_moved = True
            new_x -= 1
        elif direction == "3" and x < len(self.map) - 1:#down
            player_moved = True
            new_x += 1
        elif direction == "1" and y > 0:#left
            player_moved = True
            new_y -= 1
        elif direction == "4" and y < len(self.map[0]) - 1:#right
            player_moved = True
            new_y += 1

        if player_moved:
            self.above_position = self.map[new_x-1][new_y]
            if self.player_position != self.starting_position:
                self.below_position = self.map[new_x+1][new_y]
                self.left_position = self.map[new_x][new_y-1]
                self.right_position = self.map[new_x][new_y+1]
            
        
        if direction == "Q":
            self.moving = False
            self.adventuring = False
            self.previous_moves.append("🏁 Adventure has ended!")
            rpg_msg.edit(components=[])
        
        elif direction == "0":
            self.moving = False
            self.previous_moves.append("🔍 Checking Nearby...")
            if self.above_position in interaction_points:
                self.previous_moves.append(f"Above you found a {self.map[x-1][y]}!")
            if self.below_position in interaction_points:
                self.previous_moves.append(f"Below you found a {self.map[x+1][y]}!")
            if self.left_position in interaction_points:
                self.previous_moves.append(f"To the left you found a {self.map[x][y-1]}!")
            if self.right_position in interaction_points:
                self.previous_moves.append(f"To the right you found a {self.map[x][y+1]}!")
        elif direction == "u" or direction == "d" or direction == "l" or direction == "r":
            if direction == "u":
                npc = self.above_position
            if direction == "d":
                npc = self.below_position
            if direction == "l":
                npc = self.left_position
            if direction == "r":
                npc = self.right_position
            self.moving = False
            self.previous_moves.append(f"💬 talking to {npc}")

        # Update map with new player position
        if self.map[new_x][new_y] == "🟩":  # Only move to open paths
            self.map[x][y] = "🟩"  # Reset old position
            self.map[new_x][new_y] = f"{self.player_token}"  # New position
            self.player_position = (new_x, new_y)
            # movement_msg = await rpg_movement_ai_message(self.player1_card_name, self.player_card_data.universe, direction, self.map[x-1][y], self.map[x+1][y], self.map[x][y-1], self.map[x][y+1])
            # self.previous_moves.append(movement_msg)

    def get_map_message(self):
        map_display = self.display_map()
        # flavor_text = "The adventurer roams the mysterious labyrinth. Each step brings new discoveries and hidden dangers."
        # self.previous_moves.append(flavor_text)
        return f"{map_display}"

    def set_rpg_options(self, left=None, right=None, up=None, down=None):
        movement_buttons = []
        action_buttons = []
        world_buttons = []
        options = ["Q", "0", "1", "2", "3", "4"]
        left = self.left_position
        right = self.right_position
        up = self.above_position
        down = self.below_position
        movement_buttons = [
            Button(
                style=ButtonStyle.BLUE,
                label="Left",
                custom_id=f"{self._uuid}|1"
            ),
            Button(
                style=ButtonStyle.BLUE,
                label="Up",
                custom_id=f"{self._uuid}|2"
            ),
            Button(
                style=ButtonStyle.BLUE,
                label="Down",
                custom_id=f"{self._uuid}|3"
            ),
            Button(
                style=ButtonStyle.BLUE,
                label="Right",
                custom_id=f"{self._uuid}|4"
            )
        ]
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
        if left and left in self.interaction_points:
            world_buttons.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{self.left_position}",
                    custom_id=f"{self._uuid}|l"
                )
            )
        if right and right in self.interaction_points:
            world_buttons.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{self.right_position}",
                    custom_id=f"{self._uuid}|r"
                )
            )
        if up and up in self.interaction_points:
            world_buttons.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{self.above_position}",
                    custom_id=f"{self._uuid}|u"
                )
            )
        if down and down in self.interaction_points:
            world_buttons.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"{self.below_position}",
                    custom_id=f"{self._uuid}|d"
                )
            )
        self.movement_buttons = movement_buttons
        self.action_buttons = action_buttons
        self.world_buttons = world_buttons

    async def rpg_player_move_embed(self, ctx, private_channel, rpg_msg):
        """
        Displays the player move embed during their turn in the battle.

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
        movement_action_row = ActionRow(*self.movement_buttons)
        rpg_action_row = ActionRow(*self.action_buttons)
        components = [movement_action_row, rpg_action_row]
        if len(self.world_buttons) > 0:
            world_action_row = ActionRow(*self.world_buttons)
            components.append(world_action_row)

        player1_arm_message = f"**[🎒]Your Equipment**\n"
        rpg_map_embed = self.get_map_message()
        embedVar = Embed(title=f"", color=0xFFD700)
        embedVar.add_field(name=f"➡️ **Current Map**\nLootas bae", value=f"Welcome!\n{rpg_map_embed}")
        embedVar.set_thumbnail(url=ctx.author.avatar_url)
        embedVar.set_footer(
            text=self.get_previous_moves_embed())
        # await rpg_msg.delete(delay=1)
        # await asyncio.sleep(1)
        await rpg_msg.edit(embed=embedVar, components=components)
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
        custom_id = button_ctx.ctx.custom_id
        move = custom_id.split("|")[1]
        await self.move_player(move, rpg_msg)
        self.set_rpg_options()
        self.moving = True
        await self.rpg_player_move_embed(ctx, private_channel, rpg_msg)

    def get_previous_moves_embed(self):
        updated_list = crown_utilities.replace_matching_numbers_with_arrow(self.previous_moves)
        msg = "\n\n".join(updated_list)
        if msg:
            return msg
        else:
            return ""
        




#