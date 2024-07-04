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
from cogs.play import Play as play
from cogs.universe_traits.solo_leveling import set_solo_leveling_config
from cogs.quests import Quests
import asyncio

class RPG:
    def __init__(self, mode, _player):
        self.mode = mode
        self._uuid = None
        self.start_second = 0
        self.start_minute = 0
        self.start_hour = 0
        self.end_second = 0
        self.end_minute = 0
        self.end_hour = 0
        self._universe = "Unbound"
    
        self._player = _player
        self.player1 = _player
        self.player1_card = self.player1.card
        self.player1_title = self.player1.title
        self.player1_arm = self.player1.arm
        self.difficulty = _player.difficulty
        self.player_token = crown_utilities.crest_dict[self.player1_card.universe]
        self.is_easy_difficulty = False
        self.is_hard_difficulty = False
        self.is_normal_difficulty = False

        self.movement_buttons = []
        self.active_buttons = []
        
        self.map =  [
            ["🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫"],
            ["🟫", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟫"],
            ["🟫", "🟦", "🗝️", "🟦", "🟦", "🟦", "🟦", "🟦", "🦴", "🟫"],
            ["🟫", "🟦", "🟦", "🟦", "🧙", "🟦", "🟦", "🟦", "🟦", "🟫"],
            ["🟫", "🟦", "🟦", "🟦", "🟦", "🟦", "🦇", "🟦", "🟦", "🟫"],
            ["🟫", "🟦", "🚪", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟫"],
            ["🟫", "🟦", "🟦", "🟦", "🦊", "🟦", "🟦", "🟦", "🟦", "🟫"],
            ["🟫", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟦", "🟫"],
            ["🟫", "🟫", "🟫", "🟫", f"{self.player_token}", "🟫", "🟫", "🟫", "🟫", "🟫"]
        ]
        self.player_position = (8, 4)  # Initial position of universe_crest

    def display_map(self):
        return "\n".join("".join(row) for row in self.map_layout)

    def move_player(self, direction):
        x, y = self.player_position
        new_x, new_y = x, y

        if direction == "up" and x > 0:
            new_x -= 1
        elif direction == "down" and x < len(self.map_layout) - 1:
            new_x += 1
        elif direction == "left" and y > 0:
            new_y -= 1
        elif direction == "right" and y < len(self.map_layout[0]) - 1:
            new_y += 1

        # Update map with new player position
        if self.map_layout[new_x][new_y] == "🟦":  # Only move to open paths
            self.map_layout[x][y] = "🟦"  # Reset old position
            self.map_layout[new_x][new_y] = "🌀"  # New position
            self.player_position = (new_x, new_y)

    def get_map_message(self):
        map_display = self.display_map()
        flavor_text = (
            f"The adventurer roams the mysterious labyrinth. "
            "Each step brings new discoveries and hidden dangers."
        )
        return f"{map_display}\n\n{flavor_text}"

    def set_rpg_options(self, your_card):
        movement_buttons = []
        active_buttons = []
        options = ["Q", "0", "1", "2", "3", "4"]
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
        active_buttons.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label=f"Interact",
                    custom_id=f"{self._uuid}|0"
                )
            )
        self.movement_buttons = movement_buttons
        self.active_buttons = active_buttons

    async def rpg_player_move_embed(ctx, rpg_config, private_channel, rpg_msg):
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
        current_map = rpg_config.display_map()

        movement_action_row = ActionRow(*rpg_config.movement_buttons)
        rpg_action_row = ActionRow(*rpg_config.action_buttons)
        components = [movement_action_row, rpg_action_row]

        player1_arm_message = f"**[🎒]Your Equipment**\n"
        rpg_map_embed = rpg_config.display_map()
        embedVar = Embed(title=f"", color=0xFFD700)
        embedVar.add_field(name=f"➡️ **Current Map**\nLootas bae", value=f"Welcome!\n{rpg_map_embed}")
        embedVar.set_thumbnail(url=ctx.author.avatar_url)
        embedVar.set_footer(
            text=f"Testing this")
        await rpg_msg.delete(delay=1)
        await asyncio.sleep(1)
        rpg_msg = await private_channel.send(embed=embedVar, components=components)
        return rpg_msg, components