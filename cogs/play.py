import time
import textwrap
import crown_utilities
import custom_logging
from cogs.game_state import GameState as gs
import db
import dataclasses as data
import messages as m
import numpy as np
import unique_traits as ut
import help_commands as h
import uuid
import asyncio
from PIL import Image
import io
import re
import ai
from logger import loggy
# import bot as main
import cogs.tactics as tactics
from cogs.universe_traits.death_note import set_deathnote_message
from cogs.universe_traits.solo_leveling import activate_solo_leveling_trait
from cogs.universe_traits.souls import souls_third_phase
from interactions import Client, ActionRow, Button, File, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Play(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Play Cog is ready!')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
        

    async def battle_commands(self, ctx, battle_config, opponent_1=None, partner1=None):
        """
        Handles the logic for a battle in the game.

        Parameters:
        - self: The instance of the class.
        - ctx: The context of the command.
        - battle_config: Configuration object for the battle.
        - opponent_1: Optional PvP opponent.
        - partner1: Optional partner in co-op mode.

        Returns:
        None
        """
        private_channel = ctx.channel

        try:
            battle_config._uuid = uuid.uuid4()
            # starttime = time.asctime()
            # h_gametime, m_gametime, s_gametime = starttime[11:13], starttime[14:16], starttime[17:19]
            h_gametime, m_gametime, s_gametime = set_battle_start_time()
            if not hasattr(self, 'bot'):
                self.bot = self.client

            while battle_config.continue_fighting:
                await battle_config.configure_battle_players(ctx, opponent_1, partner1)
                start_buttons_action_rows = config_battle_starting_buttons(battle_config)
                battle_config.set_who_starts_match()
                
                user1, user2, opponent_ping, user3 = await get_users_and_opponent_ping(self, battle_config)
                match_start_embed = await build_match_start_embed(battle_config, user1, user2)
                battle_config.turn_zero_has_happened = False

                if battle_config.is_pvp_game_mode:
                    image_binary = await asyncio.to_thread(
                        battle_config.player1_card.showcard, battle_config.player1_arm, battle_config.turn_total, battle_config.player2_card.defense, battle_config.mode
                    )
                else:
                    image_binary = await asyncio.to_thread(
                        battle_config.player2_card.showcard, battle_config.player2_arm, battle_config.turn_total, battle_config.player1_card.defense, battle_config.mode
                    )

                image_binary.seek(0)
                card_file = File(file_name="image.png", file=image_binary)
                battle_start_msg = await private_channel.send(
                    content=f"{user1.mention} 🆚 {opponent_ping}",
                    embed=match_start_embed,
                    components=[start_buttons_action_rows],
                    file=card_file
                )
                image_binary.close()

                def check(component: Button) -> bool:
                    if battle_config.is_pvp_game_mode and not battle_config.is_tutorial_game_mode:
                        return component.ctx.author == user2
                    else:
                        return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.bot.wait_for_component(components=[start_buttons_action_rows], timeout=300, check=check)
                    await battle_start_msg.edit(components=[])

                    custom_id = button_ctx.ctx.custom_id
                    if custom_id == f"{battle_config._uuid}|quit_game":
                        battle_config.player1.make_available()
                        await battle_start_msg.delete()
                        await exit_battle_embed(battle_config, button_ctx, private_channel)
                        return

                    if custom_id == f"{battle_config._uuid}|save_game":
                        await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
                        await button_ctx.ctx.send(embed=battle_config.saved_game_embed(battle_config.player1_card, battle_config.player2_card))
                        return

                    if custom_id in {f"{battle_config._uuid}|start_game", f"{battle_config._uuid}|start_game_auto_battle_mode"}:
                        if battle_config.match_can_be_saved and battle_config.player1.autosave:
                            await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)

                        if custom_id == f"{battle_config._uuid}|start_game_auto_battle_mode":
                            battle_config.is_auto_battle_game_mode = True
                            embedVar = Embed(title=f"Auto Battle has started", color=0xe74c3c)
                            embedVar.set_thumbnail(url=ctx.author.avatar_url)
                            await asyncio.sleep(2)
                            battle_msg = await private_channel.send(embed=embedVar)
                        else:
                            embedVar = Embed(title=f"Battle is starting", color=0xe74c3c)
                            battle_msg = await private_channel.send(embed=embedVar)

                        tactics.tactics_set_base_stats(battle_config.player2_card)
                        
                        game_over_check = False
                        while not game_over_check:
                            
                            if check_if_game_over(battle_config):
                                game_over_check = True
                                break
                            configure_battle_log(battle_config)
                            
                            # Uncommenting this will add the ai messages at the start of the game
                            await add_ai_start_messages(battle_config)

                            early_game_tactics(battle_config)
                            if check_if_game_over(battle_config):
                                game_over_check = True
                                break



                            if battle_config.is_turn == 0:
                                if await health_check(battle_config):
                                    continue
                                
                                damage_check_activated = damage_check_turn_check(battle_config)
                                if damage_check_activated:
                                    continue

                                focusing = await start_to_focus(battle_msg, private_channel, battle_config)

                                if focusing:
                                    continue
                                    
                                else:
                                    auto_battle_handler_done = await auto_battle_handler(ctx, battle_config, battle_msg, private_channel, button_ctx)
                                    if auto_battle_handler_done:
                                        continue
                                    
                                    battle_msg, components = await player_move_embed(ctx, battle_config, private_channel, battle_msg)
                                    
                                    # Make sure user is responding with move
                                    def check(component: Button) -> bool:
                                        return component.ctx.author == user1

                                    try:
                                        button_ctx = await self.bot.wait_for_component(components=components, timeout=300, check=check)
                                        await button_ctx.ctx.defer(edit_origin=True)
                                        save_and_end = await player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx)
                                        if save_and_end:
                                            battle_config.player1.make_available()
                                            return
                                        
                                        quit_and_end = await player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx)
                                        if quit_and_end:
                                            battle_config.player1.make_available()
                                            return

                                        player_use_card_boost_ability(battle_config, button_ctx)

                                        await player_move_handler(battle_config, private_channel, button_ctx, battle_msg)
                                        
                                    except asyncio.TimeoutError:
                                        battle_config.player1.make_available()
                                        await timeout_handler(self, ctx, battle_msg, battle_config)
                        
                            if check_if_game_over(battle_config):
                                game_over_check = True
                                break

                            pre_turn_one = tactics.beginning_of_turn_stat_trait_affects(battle_config.player2_card, battle_config.player2_title, battle_config.player1_card, battle_config, battle_config.player3_card)

                            if check_if_game_over(battle_config):
                                game_over_check = True
                                break

                            if battle_config.is_turn == 1: 
                                if await health_check(battle_config):
                                    continue
                                
                                damage_check_activated = damage_check_turn_check(battle_config)
                                if damage_check_activated:
                                    continue

                                focusing = await start_to_focus(battle_msg, private_channel, battle_config)

                                if focusing:
                                    continue

                                else:
                                    if battle_config.is_pvp_game_mode and not battle_config.is_tutorial_game_mode:
                                        auto_battle_handler_done = await auto_battle_handler(ctx, battle_config, battle_msg, private_channel, button_ctx)
                                        if auto_battle_handler_done:
                                            continue
                                        
                                        battle_msg, components = await player_move_embed(ctx, battle_config, private_channel, battle_msg)
                                        
                                        # Make sure user is responding with move
                                        def check(component: Button) -> bool:
                                            return component.ctx.author == user2

                                        try:
                                            button_ctx  = await self.bot.wait_for_component(components=[components], timeout=300, check=check)
                                            await button_ctx.ctx.defer(edit_origin=True)
                                            save_and_end = await player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx)
                                            if save_and_end:
                                                battle_config.player1.make_available()
                                                battle_config.player2.make_available()
                                                return
                                            
                                            quit_and_end = await player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx)
                                            if quit_and_end:
                                                battle_config.player1.make_available()
                                                battle_config.player2.make_available()
                                                return

                                            player_use_card_boost_ability(battle_config, button_ctx)

                                            await player_move_handler(battle_config, private_channel, button_ctx, battle_msg)
                                                        
                                        except asyncio.TimeoutError:
                                            battle_config.player1.make_available()
                                            battle_config.player2.make_available()
                                            await timeout_handler(self, ctx, battle_msg, battle_config)
                                    
                                    # Play Bot
                                    if not battle_config.is_pvp_game_mode or battle_config.is_tutorial_game_mode:
                                        auto_battle_handler_done = await auto_battle_handler(ctx, battle_config, battle_msg, private_channel, button_ctx)
                                        if auto_battle_handler_done:
                                            continue
                                        
                                        await ai_move_handler(ctx, battle_config, private_channel, battle_msg)
                                        
                            
                            if battle_config.is_co_op_mode or battle_config.is_duo_mode:
                                if check_if_game_over(battle_config):
                                    game_over_check = True
                                    break
                                pre_turn_two = tactics.beginning_of_turn_stat_trait_affects(battle_config.player3_card, battle_config.player3_title, battle_config.player2_card, battle_config, battle_config.player1_card)

                                if check_if_game_over(battle_config):
                                    game_over_check = True
                                    break
                                if battle_config.is_turn == 2:
                                    if await health_check(battle_config):
                                        continue
                                    
                                    damage_check_activated = damage_check_turn_check(battle_config)
                                    if damage_check_activated:
                                        continue

                                    focusing = await start_to_focus(battle_msg, private_channel, battle_config)

                                    if focusing:
                                        continue
                                        
                                    else:
                                        auto_battle_handler_done = await auto_battle_handler(ctx, battle_config, battle_msg, private_channel, button_ctx)
                                        if auto_battle_handler_done:
                                            continue

                                        if battle_config.is_co_op_mode:
                                            battle_msg, components = await player_move_embed(ctx, battle_config, private_channel, battle_msg)
                                            
                                            # Make sure user is responding with move
                                            def check(component: Button) -> bool:
                                                return component.ctx.author == user2

                                            try:
                                                button_ctx  = await self.bot.wait_for_component(components=[components], timeout=300, check=check)

                                                save_and_end = await player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx)
                                                if save_and_end:
                                                    battle_config.player1.make_available()
                                                    battle_config.player3.make_available()
                                                    return
                                                
                                                quit_and_end = await player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx)
                                                if quit_and_end:
                                                    battle_config.player1.make_available()
                                                    battle_config.player3.make_available()
                                                    return

                                                player_use_card_boost_ability(battle_config, button_ctx)

                                                await player_move_handler(battle_config, private_channel, button_ctx, battle_msg)
                                            except Exception as ex:
                                                battle_config.player1.make_available()
                                                battle_config.player3.make_available()
                                                custom_logging.debug(ex)

                                        if battle_config.is_duo_mode:
                                            await ai_move_handler(ctx, battle_config, private_channel, battle_msg)
                                            continue
                                                        
                                if check_if_game_over(battle_config):
                                    game_over_check = True
                                    break

                                pre_turn_three = tactics.beginning_of_turn_stat_trait_affects(battle_config.player2_card, battle_config.player2_title, battle_config.player3_card, battle_config, battle_config.player1_card)

                                if check_if_game_over(battle_config):
                                    game_over_check = True
                                    break
                                if battle_config.is_turn == 3: 
                                    if await health_check(battle_config):
                                        continue
                                    
                                    damage_check_activated = damage_check_turn_check(battle_config)
                                    if damage_check_activated:
                                        continue

                                    focusing = await start_to_focus(battle_msg, private_channel, battle_config)

                                    if focusing:
                                        continue

                                    else:
                                        auto_battle_handler_done = await auto_battle_handler(ctx, battle_config, battle_msg, private_channel, button_ctx)
                                        if auto_battle_handler_done:
                                            continue

                                        if battle_config.is_pvp_game_mode:                                            
                                            battle_msg, components = await player_move_embed(ctx, battle_config, private_channel, battle_msg)
                                            
                                            # Make sure user is responding with move
                                            def check(component: Button) -> bool:
                                                return component.ctx.author == user2

                                            try:
                                                button_ctx  = await self.bot.wait_for_component(components=[components], timeout=300, check=check)

                                                save_and_end = await player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx)
                                                if save_and_end:
                                                    return
                                                
                                                quit_and_end = await player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx)
                                                if quit_and_end:
                                                    return

                                                player_use_card_boost_ability(battle_config, button_ctx)

                                                await player_move_handler(battle_config, private_channel, button_ctx, battle_msg)
                                                            
                                            except asyncio.TimeoutError:
                                                await timeout_handler(self, ctx, battle_msg, battle_config)
                                        
                                        # Play Bot
                                        if not battle_config.is_pvp_game_mode:                                            
                                            await ai_move_handler(ctx, battle_config, private_channel, battle_msg)
                                            continue

                        if game_over_check:
                            gameClock = get_battle_time(h_gametime, m_gametime, s_gametime)
                            await gs.pvp_end_game(self, battle_config, private_channel, battle_msg, gameClock)

                            await gs.you_lose_non_pvp(self, battle_config, private_channel, battle_msg, gameClock, user1, user2=None)

                            await gs.you_win_non_pvp(self, ctx, battle_config, private_channel, battle_msg, gameClock, user1, user2=None)

                except asyncio.TimeoutError:
                    battle_config.player1.make_available()
                    await timeout_handler(self, ctx, battle_msg, battle_config)

                except Exception as ex:
                    loggy.critical(f"Battle timed out or ended unexpectedly with an error {ex}")
                    battle_config.player1.make_available()
                    custom_logging.debug(ex)
                    
        except asyncio.TimeoutError:
            loggy.critical(f"Battle timed out")
            battle_config.player1.make_available()
            await timeout_handler(self, ctx, battle_msg, battle_config)

        except Exception as ex:
            loggy.critical(f"Battle timed out")
            battle_config.player1.make_available()
            custom_logging.debug(ex)


async def add_ai_start_messages(battle_config):
    if not battle_config.turn_zero_has_happened:
        class_effects = {
            "ASSASSIN": "{name} the {class_message} gained {class_value} sneak attacks",
            "MAGE": "{name} the {class_message} gained a {class_value}% boost to elemental attacks",
            "RANGER": "{name} the {class_message} gained 💠 {class_value} barriers",
            "TANK": "{name} the {class_message} gained a 🌐 {class_value} shield",
            "HEALER": "{name} the {class_message} boosted their healing by {class_value}%",
            "SUMMONER": "{name} the {class_message} calls forth {summon_name} with {summoner_value}% increased ability",
            "FIGHTER": "{name} the {class_message} gained 🔁 {class_value} parries",
            "TACTICIAN": "{name} the {class_message} Can Enter focus using Block to strategize against their opponent!",
        }

        def append_previous_moves(card, player_name):
            if card.card_class in class_effects:
                battle_config.previous_moves.append(
                    class_effects[card.card_class].format(
                        name=card.name, 
                        summon_name=card.summon_name,
                        class_message=card.class_message, 
                        class_value= card.class_value,
                        summoner_value= card.class_value * 10
                    )
                )


        # player1_ai_start_message = await ai.match_start_message(battle_config.player1_card.name, battle_config.player1_card.universe, battle_config.player2_card.name, battle_config.player2_card.universe)
        # battle_config.previous_moves.append(f"[{battle_config.player1_card.name}] - {player1_ai_start_message}")
        # # For player1_card
        append_previous_moves(battle_config.player1_card, "player1")

        # player2_ai_start_message = await ai.match_start_message(battle_config.player2_card.name, battle_config.player2_card.universe, battle_config.player1_card.name, battle_config.player1_card.universe)
        # battle_config.previous_moves.append(f"[{battle_config.player2_card.name}] - {player2_ai_start_message}")
        # # For player2_card
        append_previous_moves(battle_config.player2_card, "player2")

        battle_config.turn_zero_has_happened = True
        return
    
def set_battle_start_time():
    # Get the current local time when the battle starts
    start_time = time.localtime()
    h_gametime = start_time.tm_hour
    m_gametime = start_time.tm_min
    s_gametime = start_time.tm_sec
    # print(f"{str(h_gametime)} : {str(m_gametime)} : {str(s_gametime)}")
    return h_gametime, m_gametime, s_gametime

def get_battle_time(h_gametime, m_gametime, s_gametime):
    current_time = time.localtime()
    h_playtime = current_time.tm_hour
    m_playtime = current_time.tm_min
    s_playtime = current_time.tm_sec

    # print(f"{str(h_playtime)} : {str(m_playtime)} : {str(s_playtime)}")

    gameClock = crown_utilities.getTime(h_gametime, m_gametime, s_gametime, h_playtime, m_playtime, s_playtime)
    # print(gameClock)
    return gameClock


def config_battle_starting_buttons(battle_config):
    """
    Configures the starting buttons for the battle.

    Parameters:
    - battle_config: Configuration object for the battle.

    Returns:
    ActionRow: ActionRow containing the configured buttons.

    Steps:
    1. Initialize a list for the starting buttons.
    2. Add a "Start Match" button and an "End" button to the list.
    3. If auto battle is allowed and the battle mode is not co-op or duo, add an "Auto Battle" button.
    4. If it's not a tutorial mode and saving the match is turned on, and the current opponent number is greater than 0, add a "Save Game" button.
    5. Create an ActionRow with the configured buttons.
    6. Return the ActionRow.
    """
    start_message = "Start The Match"
    if battle_config.is_pvp_game_mode:
        start_message = f"{battle_config.player2.disname} Press This To Begin"
    
    if battle_config.is_tutorial_game_mode:
        start_message = "Start Your Tutorial ❤️"

    # start_message = "Start Match" if not battle_config.is_pvp_game_mode or battle_config.is_tutorial_game_mode else f"{battle_config.player2.disname} Press This To Begin"

    start_tales_buttons = [
        Button(
            style=ButtonStyle.BLUE,
            label=f"{start_message}",
            custom_id=f"{battle_config._uuid}|start_game"
        ),
        Button(
            style=ButtonStyle.RED,
            label="End",
            custom_id=f"{battle_config._uuid}|quit_game"
        ),
    ]

    if battle_config.can_auto_battle and not battle_config.is_co_op_mode and not battle_config.is_duo_mode:
        start_tales_buttons.append(
            Button(
                style=ButtonStyle.GREY,
                label="Auto Battle",
                custom_id=f"{battle_config._uuid}|start_game_auto_battle_mode"
            )

        )
    
    if not battle_config.is_tutorial_game_mode and battle_config.save_match_turned_on():
        if battle_config.current_opponent_number > 0:
            start_tales_buttons.append(
                Button(
                    style=ButtonStyle.GREEN,
                    label="Save Game",
                    custom_id=f"{battle_config._uuid}|save_game"
                )
            )

    start_tales_buttons_action_row = ActionRow(*start_tales_buttons)    

    return start_tales_buttons_action_row


async def get_users_and_opponent_ping(self, battle_config):
    if hasattr(self, 'bot'):
        pass
    else:
        self.bot = self.client
    user1 = await self.bot.fetch_user(battle_config.player1.did)
    user2 = None
    user3 = None

    if battle_config.is_pvp_game_mode:
        user2 = await self.bot.fetch_user(battle_config.player2.did)
        opponent_ping = user2.mention
    elif battle_config.is_co_op_mode:
        user2 = await self.bot.fetch_user(battle_config.player3.did)
        opponent_ping = user2.mention
    else:
        opponent_ping = "..."

    return user1, user2, opponent_ping, user3


async def timeout_handler(self, ctx, battle_msg, battle_config):
    battle_config.continue_fighting = False
    await battle_msg.delete()
    if not any((battle_config.is_abyss_game_mode, 
                battle_config.is_scenario_game_mode, 
                battle_config.is_explore_game_mode, 
                battle_config.is_pvp_game_mode, 
                battle_config.is_tutorial_game_mode,
                battle_config.is_boss_game_mode)):
        await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
        await ctx.send(embed = battle_config.saved_game_embed(battle_config.player1_card,battle_config.player2_card))
    elif any((battle_config.is_pvp_game_mode, 
                battle_config.is_tutorial_game_mode)):
        await ctx.send(embed = battle_config.close_pvp_embed(battle_config.player1,battle_config.player2))
    else:
        await ctx.send(embed = battle_config.close_pve_embed(battle_config.player1_card,battle_config.player2_card))
    await ctx.send(f"{ctx.author.mention} {battle_config.error_end_match_message()}")

    return


async def build_match_start_embed(battle_config, user1, user2):
    """
    Builds the match start embed for the battle.

    Parameters:
    - battle_config: Configuration object for the battle.
    - user1: User object representing the first player.
    - user2: User object representing the second player.

    Returns:
    Embed: The built match start embed.

    Steps:
    1. Get the title and level message for the starting match.
    2. Create an embed with the starting match title and level message.
    3. Add a field for the player's affinities.
    4. If it's co-op or duo mode, add a field for the companion's affinities.
    5. Add a field for the opponent's affinities.
    6. Set the image of the embed to the card image.
    7. Set the thumbnail of the embed based on the game mode (PvP or not).
    8. Set the footer text of the embed.
    9. Return the built embed.
    """
    try:
        title_lvl_msg = f"{battle_config.set_levels_message()}"
        # starting_battle_ai_message = await ai.starting_battle_ai_message(battle_config.player1_card.name, battle_config.player1_card.universe, battle_config.player2_card.name, battle_config.player2_card.universe)

        embed = Embed(title=f"{title_lvl_msg}")
        embed.set_author(name=f"{battle_config.get_starting_match_title()}")

        if battle_config.is_co_op_mode or battle_config.is_duo_mode:
            embed.set_footer(text=textwrap.dedent(f"""\                                                  
Your Affinities:
{battle_config.player1_card.set_battle_menu_affinity_message()}

Opponent Affinities:
{battle_config.player2_card.set_battle_menu_affinity_message()}

Companion Affinities:
{battle_config.player3_card.set_battle_menu_affinity_message()}
            """), icon_url="https://cdn.discordapp.com/emojis/789290881654980659.gif?v=1")
        else:
            embed.set_footer(text=f"Your Affinities:\n"f"{battle_config.player1_card.set_battle_menu_affinity_message()}\n\n"f"Opponent Affinities:\n"f"{battle_config.player2_card.set_battle_menu_affinity_message()}\n\n")


        embed.set_image(url="attachment://image.png")
        
        if battle_config.is_pvp_game_mode:
            embed.set_thumbnail(url=user2.avatar_url)
        else:
            embed.set_thumbnail(url=user1.avatar_url)
        
        return embed
    except Exception as ex:
        custom_logging.debug(ex)


def early_game_tactics(battle_config):
    """
    Performs early game tactics for the battle.

    Parameters:
    - battle_config: Configuration object for the battle.

    Returns:
    None

    Steps:
    1. If it's co-op mode, perform beginning of turn stat trait effects for player 1 with player 2 and player 3.
       Otherwise, perform it for player 1 with player 2.
    2. Check for petrified or fear effects and handle them accordingly.
    3. Perform bloodlust check, enrage check, damage check, stagger check, almighty will check,
       death blow check, and intimidation check on player 2's card with player 1's card.
    """
    if battle_config.is_co_op_mode:
        pre_turn_zero = tactics.beginning_of_turn_stat_trait_affects(battle_config.player1_card, battle_config.player1_title, battle_config.player2_card, battle_config, battle_config.player3_card)
    else:
        pre_turn_zero = tactics.beginning_of_turn_stat_trait_affects(battle_config.player1_card, battle_config.player1_title, battle_config.player2_card, battle_config)
    
    pretrified_check = tactics.tactics_petrified_fear_check(battle_config.player2_card, battle_config.player1_card, battle_config)
    if not pretrified_check:
        tactics.tactics_bloodlust_check(battle_config.player2_card, battle_config)
        tactics.tactics_enrage_check(battle_config.player2_card, battle_config)
        tactics.tactics_damage_check(battle_config.player2_card, battle_config)
        tactics.tactics_stagger_check(battle_config.player2_card, battle_config.player1_card, battle_config)
        tactics.tactics_almighty_will_check(battle_config.player2_card, battle_config)
        tactics.tactics_death_blow_check(battle_config.player2_card, battle_config.player1_card, battle_config) 
        tactics.tactics_intimidation_check(battle_config.player2_card, battle_config.player1_card, battle_config)


async def exit_battle_embed(battle_config, button_ctx, private_channel):
    if battle_config.player1.autosave and battle_config.match_can_be_saved:
        await private_channel.send(embed=battle_config.saved_game_embed(battle_config.player1_card, battle_config.player2_card))
    elif not battle_config.is_pvp_game_mode:
        await private_channel.send(embed=battle_config.close_pve_embed(battle_config.player1_card, battle_config.player2_card))
    else:
        await private_channel.send(embed=battle_config.close_pvp_embed(battle_config.player1, battle_config.player2))
    return


def check_if_game_over(battle_config):
    player3_card = battle_config.player3_card if battle_config.is_duo_mode or battle_config.is_co_op_mode else None
    if battle_config.is_tutorial_game_mode and battle_config.player2_card.health <= 0 and not battle_config.all_tutorial_tasks_complete:
        battle_config.turn_total -= 1
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ❌ Tutorial Task Incomplete!\nComplete your Tutorial Task to defeat the Training Dummy!")
        battle_config.turn_total += 1
    game_over_check = battle_config.set_game_over(battle_config.player1_card, battle_config.player2_card, player3_card)
    
    return bool(game_over_check)


def configure_battle_log(battle_config):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if battle_config.previous_moves:
        battle_config.previous_moves_len = len(battle_config.previous_moves)
        if battle_config.previous_moves_len >= battle_config.player1.battle_history:
            battle_config.previous_moves = battle_config.previous_moves[-battle_config.player1.battle_history:]


# def getTime(hgame, mgame, sgame, hnow, mnow, snow):
#     hoursPassed = hnow - hgame
#     minutesPassed = mnow - mgame
#     secondsPassed = snow - sgame
#     if hoursPassed > 0:
#         minutesPassed = mnow
#         if minutesPassed > 0:
#             secondsPassed = snow
#         else:
#             secondsPassed = snow - sgame
#     else:
#         minutesPassed = mnow - mgame
#         if minutesPassed > 0:
#             secondsPassed = snow
#         else:
#             secondsPassed = snow - sgame
#     gameTime = str(hoursPassed) + str(minutesPassed) + str(secondsPassed)
#     return gameTime


async def start_to_focus(battle_msg, private_channel, battle_config):
    """
    Performs the start-to-focus actions at the beginning of the player's turn.

    Parameters:
    - battle_msg: The message object for the battle.
    - private_channel: The private channel for the battle.
    - battle_config: Configuration object for the battle.

    Returns:
    bool: True if focusing occurs, False otherwise.

    Steps:
    1. Sleep for 1 second.
    2. Initialize the `focusing` variable as False.
    3. Get the positions of the battle entities (players, cards, titles, arms).
    4. If it's turn 1, perform death blow check on the turn player's card with the opponent player's card.
    5. Set the deathnote message for the turn player's card, opponent player's card, and partner player's card (if it's co-op mode).
    6. Perform first turn experience for the battle.
    7. If the turn player's card stamina is less than 10, perform focusing actions.
       - Call the focusing method on the turn player's card.
       - Sleep for 1 second.
       - Perform tutorial focusing.
       - Perform boss focusing.
       - Set the `focusing` variable to True.
    8. Return the `focusing` variable.
    """
    await asyncio.sleep(1)
    focusing = False

    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if battle_config.is_turn == 1:
        tactics.tactics_death_blow_check(turn_card, opponent_card, battle_config)

    set_deathnote_message(turn_card, battle_config)
    set_deathnote_message(opponent_card, battle_config)

    if battle_config.is_co_op_mode:
        set_deathnote_message(partner_card, battle_config)

    await first_turn_experience(battle_config, private_channel)

    if turn_card.stamina < 10:
        await turn_card.focusing(turn_title, opponent_title, opponent_card, battle_config)
        await asyncio.sleep(1)
        #if not turn_card.used_blitz:
        await tutorial_focusing(turn_card, battle_config, private_channel)
        await boss_focusing(battle_config, private_channel)
        focusing = True

    return focusing


async def health_check(battle_config):
    try:
        turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
        if turn_card.health <= 0:
            return False
        if opponent_card.health <= 0:
            return False
    except Exception as ex:
        custom_logging.debug(ex)


def damage_check_turn_check(battle_config):
    damage_check_activated = False
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    if battle_config.is_turn == 1:
        if turn_card.damage_check_activated:
            battle_config.is_turn = 0
            damage_check_activated = True
    return damage_check_activated


async def tutorial_focusing(turn_card, battle_config, private_channel):
    if battle_config.is_tutorial_game_mode:
        #print(battle_config.is_turn)
        if turn_card.name == "Training Dummy" and battle_config.tutorial_focus and not battle_config.tutorial_opponent_focus:
            await private_channel.send(embed=battle_config._tutorial_message)
            battle_config.tutorial_opponent_focus = True  
            await asyncio.sleep(2)
        if turn_card.name != "Training Dummy" and not battle_config.tutorial_focus:
            await private_channel.send(embed=battle_config._tutorial_message)
            battle_config.tutorial_focus = True
            await asyncio.sleep(2)


async def boss_focusing(battle_config, private_channel):
    if battle_config.is_boss_game_mode:
        if battle_config.is_turn == 0:
            await private_channel.send(embed=battle_config._boss_embed_message)
            await asyncio.sleep(2)

        if battle_config.is_turn == 1:
            if battle_config.is_boss_game_mode:
                embedVar = Embed(title=f"**{battle_config.player2_card.name}** Enters Focus State",
                                        description=f"{battle_config._powerup_boss_description}", color=0xe91e63)
                embedVar.add_field(name=f"A great aura starts to envelop **{battle_config.player2_card.name}** ",
                                value=f"{battle_config._aura_boss_description}")
                embedVar.set_footer(text=f"{battle_config.player2_card.name} Says: 'Now, are you ready for a real fight?'")
                await private_channel.send(embed=embedVar)

                if battle_config.player2_card.universe == "Digimon" and battle_config.player2_card.used_resolve is False:
                    embedVar = Embed(title=f"({battle_config.turn_total}) ⚡ **{battle_config.player2_card.name}** Resolved!", description=f"{battle_config._rmessage_boss_description}",
                                            color=0xe91e63)
                    embedVar.set_footer(text=f"{battle_config.player1_card.name} this will not be easy...")
                    await private_channel.send(embed=embedVar)
                    await asyncio.sleep(2)


def speed_title_handler(player_title, player_card, opponent_title, opponent_card):
    p1_spd_msg = None
    p2_spd_msg = None
    p1_spd_msg = player_title.speed_handler(player_card)
    p2_spd_msg = opponent_title.speed_handler(opponent_card)
    return p1_spd_msg, p2_spd_msg



async def first_turn_experience(battle_config, private_channel):
    """
    Performs the first turn experience at the beginning of the battle.

    Parameters:
    - battle_config: Configuration object for the battle.
    - private_channel: The private channel for the battle.

    Returns:
    None

    Steps:
    1. If it's the first turn and the turn is 0:
       - If it's a tutorial game mode, send a welcome embed with instructions and player details.
    2. If it's the first turn and the turn is 1:
       - If it's a boss game mode, send a boss introduction embed with boss details.
       - If it's a tutorial game mode, send a welcome embed with instructions and player details.
    3. Sleep for 2 seconds after each message is sent.
    """
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if battle_config.turn_total == 0:
        p1_spd_msg, p2_spd_msg = speed_title_handler(turn_title, turn_card, opponent_title, opponent_card)

        if battle_config.is_turn == 0:
            if battle_config.is_tutorial_game_mode:
                #Insert Health Based Traits Here
                battle_config.player2_card.stamina = 20
                block_message = f"🛡️ - **Block**: 2x DEF for one Turn *⚡20 ST*"
                if battle_config.player1_card.card_class == "TANK":
                    block_message = f"🛡️ - **Heavy Block**: 3x DEF for one Turn *⚡20 ST*"
                embedVar = Embed(title=f"Welcome to **Anime VS+**!",
                                        description=f"Follow the instructions to learn how to play the Game!",
                                        color=0xe91e63)
                embedVar.add_field(name=f"\n[{crown_utilities.class_emojis[battle_config.player1_card.card_class]}] **{battle_config.player1_card.name}'s Class**",value=f"*The {battle_config.player1_card.class_message}\n{crown_utilities.class_mapping[battle_config.player1_card.card_class]}*\n{battle_config.player1_card.class_tutorial_message}\n\n")
                if battle_config.player1_card.universe in crown_utilities.starting_traits:
                    title, text = battle_config.starting_trait_handler(battle_config.player1_card, battle_config.player2_card)
                    
                    embedVar.add_field(name=f"\n[{battle_config.player1_card.universe_crest}] {battle_config.player1_card.universe} Trait: {title}\n",
                                value=f"{text}")
                embedVar.add_field(name="\n**[Moveset]**",value=f"{battle_config.player1_card.move1_emoji} - **Basic {battle_config.player1_card.move1_element.title()} Attack** *⚡10 ST*\n{battle_config.player1_card.move2_emoji} - **Special {battle_config.player1_card.move2_element.title()} Attack** *⚡30 ST*\n{battle_config.player1_card.move3_emoji} - **Ultimate {battle_config.player1_card.move3_element.title()} Attack** *⚡80 ST*\n🦠 - **{battle_config.player1_card.move4enh.title()} Enhancer** *⚡20 ST*\n\n**[Skills]**\n{block_message}\n💢 - **Blitz**: Boost ATK and DEF by SPD ⚡ All\n\n**[Transformations]**\n🌀 - **Focus**: Increase ST, ATK, DEF and Heal\n⚡ - **Resolve**: Heal and Activate Summon\n🧬 - ** {battle_config.player1_card.summon_type.title()} Summon** : {battle_config.player1.equipped_summon}\n")
                #embedVar.add_field(name=f"🧠**Tutorial Task!**", value=f"*Interactively learn about your Elemental Attacks and Card Abilities!*")
                embedVar.set_footer(text="Focus State: When your ST(Stamina) is < 10, You will FOCUS to gain ATK and DEF and heal a portion of missing HP(Health)")
                await private_channel.send(embed=embedVar)
                await asyncio.sleep(2)
        
        if battle_config.is_turn == 1:
            if battle_config.is_boss_game_mode:
                embedVar = Embed(title=f"**{battle_config.player2_card.name}** Boss of `{battle_config.player2_card.universe}`",
                                        description=f"*{battle_config._description_boss_description}*", color=0xe91e63)
                embedVar.add_field(name=f"{battle_config._arena_boss_description}", value=f"{battle_config._arenades_boss_description}")
                embedVar.add_field(name=f"Entering the {battle_config._arena_boss_description}", value=f"{battle_config._entrance_boss_description}", inline=False)
                embedVar.set_footer(text=f"{battle_config.player2_card.name} waits for you to strike....")
                await private_channel.send(embed=embedVar)
                await asyncio.sleep(2)
            if battle_config.is_tutorial_game_mode:
                block_message = f"🛡️ - **Block**: 2x DEF for one Turn *⚡20 ST*"
                if battle_config.player1_card.card_class == "TANK":
                    block_message = f"🛡️ - **Heavy Block**: 3x DEF for one Turn *⚡20 ST*"
                embedVar = Embed(title=f"Welcome to **Anime VS+**!",
                                        description=f"Follow the instructions to learn how to play the Game!",
                                        color=0xe91e63)
                embedVar.add_field(name=f"\n[{crown_utilities.class_emojis[battle_config.player1_card.card_class]}] **{battle_config.player1_card.name}'s Class**",value=f"*The {battle_config.player1_card.class_message}\n{crown_utilities.class_mapping[battle_config.player1_card.card_class]}*\n{battle_config.player1_card.class_tutorial_message}\n\n")
                if battle_config.player1_card.universe in crown_utilities.starting_traits:
                    title, text = battle_config.starting_trait_handler(battle_config.player1_card, battle_config.player2_card)
                    
                    embedVar.add_field(name=f"[{battle_config.player1_card.universe_crest}] {battle_config.player1_card.universe} Trait: {title}",
                                value=f"{text}")
                embedVar.add_field(name="\n**[Moveset]**",value=f"{battle_config.player1_card.move1_emoji} - **Basic {battle_config.player1_card.move1_element.title()} Attack** *⚡10 ST*\n{battle_config.player1_card.move2_emoji} - **Special {battle_config.player1_card.move2_element.title()} Attack** *⚡30 ST*\n{battle_config.player1_card.move3_emoji} - **Ultimate {battle_config.player1_card.move3_element.title()} Attack** *⚡80 ST*\n🦠 - **{battle_config.player1_card.move4enh.title()} Enhancer** *⚡20 ST*\n\n**[Skills]**\n{block_message}\n💢 - **Blitz**: Boost ATK and DEF by SPD ⚡ All\n\n**[Transformations]**\n🌀 - **Focus**: Increase ST, ATK, DEF and Heal\n⚡ - **Resolve**: Heal and Activate Summon\n🧬 - ** {battle_config.player1_card.summon_type.title()} Summon** : {battle_config.player1.equipped_summon}\n")
                #embedVar.add_field(name=f"🧠**Tutorial Task!**", value=f"*Interactively learn about your Elemental Attacks and Card Abilities!*")
                embedVar.set_footer(text="Focus State: When your ST(Stamina) is < 10, You will FOCUS to gain ATK and DEF and heal a portion of missing HP(Health)")
                await private_channel.send(embed=embedVar)
                await asyncio.sleep(2)


async def auto_battle_handler(ctx, battle_config, battle_msg, private_channel, button_ctx):
    """
    Handles the auto-battle experience in the battle.

    Parameters:
    - ctx: The context object for the current command.
    - battle_config: Configuration object for the battle.
    - battle_msg: The message object for the battle.
    - private_channel: The private channel for the battle.
    - button_ctx: The context object for the button interaction.

    Returns:
    bool: Indicates whether the auto-battle experience was successfully executed.

    Steps:
    1. Get the battle positions of players, cards, titles, and arms.
    2. Check if the auto-battle game mode is enabled.
    3. Configure the start of moves for the battle.
    4. Create the auto-battle embed and starting traits using the auto_battle_embed_and_starting_traits function.
    5. Send a new message or edit the existing message with the embed and no components.
    6. Sleep for 2 seconds.
    7. Determine the selected move based on the AI battle command.
    8. Perform damage calculation and update the battle log for specific moves.
    9. Handle special moves (resolving, summoning, blocking) and double strike for monstrosity.
    10. If the move is summoning, update the damage calculation and perform damage done.
    11. Execute player damage calculation asynchronously.
    12. Return True to indicate a successful auto-battle experience execution.
    """
    try:
        turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

        if battle_config.is_auto_battle_game_mode:
            await start_of_moves_config(battle_config)
            embedVar = await tactics.auto_battle_embed_and_starting_traits(ctx, turn_card, turn_title, opponent_card, opponent_title, battle_config, partner_card, partner_title)
            if battle_msg is None:
                # If the message does not exist, send a new message
                battle_msg = await private_channel.send(embed=embedVar, components=[])
            else:
                # If the message exists, edit it
                await battle_msg.edit(embed=embedVar, components=[])
            await asyncio.sleep(2)

            selected_move = battle_config.ai_battle_command(turn_card, opponent_card)

            if selected_move in [1, 2, 3, 4, 7]:
                damage_calculation_response = turn_card.damage_cal(selected_move, battle_config, opponent_card)


            if selected_move == 5:
                await turn_card.resolving(battle_config, turn_title, opponent_card, battle_config.player1)
                if battle_config.is_boss_game_mode:
                    await button_ctx.ctx.send(embed=battle_config._boss_embed_message)
                return

            if selected_move == 6:
                summon_response = turn_card.usesummon(battle_config, opponent_card)
                return

            if selected_move == 0:
                turn_card.use_block(battle_config, opponent_card)
                damage_calculation_response = None


            complete_damage_calculation = await player_damage_calculation(battle_config, button_ctx, damage_calculation_response)
            return True                         
        else:
            return False                   
    except Exception as ex:
        custom_logging.debug(ex)


async def ai_move_handler(ctx, battle_config, private_channel, battle_msg=None):
    """
    Displays the AI move embed during its turn in the battle.

    Parameters:
    - ctx: The context object for the current command.
    - battle_config: Configuration object for the battle.
    - private_channel: The private channel for the battle.
    - battle_msg: The message object for the battle (optional).

    Returns:
    bool: Indicates whether the AI move was successfully executed.

    Steps:
    1. Get the battle positions of players, cards, titles, and arms.
    2. Configure the start of moves for the battle.
    3. Create the AI move embed and starting traits using the auto_battle_embed_and_starting_traits function.
    4. Attach the turn player's card image to the embed.
    5. Send a new message or edit the existing message with the embed and no components.
    6. Sleep for 2 seconds.
    7. Determine the selected move based on the AI battle command.
    8. Perform damage calculation and update the battle log for specific moves.
    9. Handle special moves (resolving, summoning, blocking) and double strike for monstrosity.
    10. If the move is summoning, update the damage calculation and perform damage done.
    11. Execute AI damage calculation asynchronously.
    12. Return True to indicate a successful AI move execution.
    """
    try:
        turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
        await start_of_moves_config(battle_config)
        embedVar = await tactics.auto_battle_embed_and_starting_traits(ctx, turn_card, turn_title, opponent_card, opponent_title, battle_config, partner_card, partner_title)
        image_binary = turn_card.showcard(turn_arm, battle_config.turn_total, opponent_card.defense, battle_config.mode)

        if hasattr(image_binary, 'seekable') and image_binary.seekable():
            image_binary.seek(0)
            card_file = File(file_name="image.png", file=image_binary)
            if battle_msg is None:
                # If the message does not exist, send a new message
                battle_msg = await private_channel.send(embed=embedVar, components=[], file=card_file)
            else:
                # If the message exists, edit it
                await battle_msg.edit(embed=embedVar, components=[], file=card_file)
        else:
            if battle_msg is None:
                # If the message does not exist, send a new message
                battle_msg = await private_channel.send(embed=embedVar, components=[])
            else:
                # If the message exists, edit it
                await battle_msg.edit(embed=embedVar, components=[])
        # if image_binary:
        image_binary.close()
        await asyncio.sleep(2)

        selected_move = battle_config.ai_battle_command(turn_card, opponent_card)
        if selected_move in [1, 2, 3, 4, 7]:
            damage_calculation_response = turn_card.damage_cal(selected_move, battle_config, opponent_card)

            # This is unnecessary and causes the monstrosity effect to run multiple times
            # if selected_move != 7:
            #     if turn_card._monstrosity_active and turn_card.used_resolve:
            #         turn_card._monstrosity_value = turn_card._monstrosity_value - 1
            #         if turn_card._monstrosity_value <= 0:
            #             turn_card._monstrosity_active = False
            #             turn_card._monstrosity_value = 0
            #         battle_config.add_to_battle_log(f"{turn_card.name} has {turn_card._monstrosity_value} double strikes left")
            #         turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)

        if selected_move == 5:
            await turn_card.resolving(battle_config, turn_title, opponent_card, turn_player)
            if battle_config.is_boss_game_mode:
                await private_channel.send(embed=battle_config._boss_embed_message)
            return

        if selected_move == 6:
            summon_response = turn_card.usesummon(battle_config, opponent_card)
            return

        if selected_move == 0:
            turn_card.use_block(battle_config, opponent_card)
            return

        complete_damage_calculation = await ai_damage_calculation(battle_config, damage_calculation_response)
        return True                         
    except Exception as ex:
        custom_logging.debug(ex)



async def player_move_embed(ctx, battle_config, private_channel, battle_msg):
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
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    await start_of_moves_config(battle_config)

    battle_action_row = ActionRow(*battle_config.battle_buttons)
    util_action_row = ActionRow(*battle_config.utility_buttons)
    
    if battle_config.is_co_op_mode:
        partner_card.set_battle_arm_messages(opponent_card)
        partner_card.set_stat_icons()
        if turn_card.stamina >= 20:
            coop_util_action_row = ActionRow(*battle_config.co_op_buttons)
            components = [battle_action_row, coop_util_action_row, util_action_row]
        else:
            components = [battle_action_row, util_action_row]
        companion_stats = f"\n{partner_card.name}: ❤️{round(partner_card.health)} 🌀{round(partner_card.stamina)} 🗡️{round(partner_card.attack)}/🛡️{round(partner_card.defense)} {partner_card._arm_message}"
    else:
        components = [battle_action_row, util_action_row]

    turn_card.set_battle_arm_messages(opponent_card)
    turn_card.set_stat_icons()

    author_text = battle_config.get_battle_author_text(opponent_card, opponent_title, turn_card, turn_title, partner_card, partner_title)

    summon_message = f"🧬 {turn_card.summon_name}: {turn_card.summon_emoji}{turn_card.summon_type.title()} Ability: {turn_card.summon_power}" if turn_card.used_resolve or turn_card.card_class == "SUMMONER" else ""
    talisman_message = f"{crown_utilities.set_emoji(turn_card._talisman)} {turn_card._talisman.title()} Talisman"
    universe_stacks = f"{turn_card.universe_crest} {turn_card.universe_trait_value_name}: {turn_card.universe_trait_value}"
    if turn_card.is_tactician and turn_card._tactician_stack_3:
        talisman_message = f"🆚 Tactician's Talisman"
    if turn_card.is_tactician and turn_card._tactician_stack_5:
        talisman_message = f"🆚 Ultimate Strategy"
    player1_arm_message = f"**[🎒]Your Equipment**\n{talisman_message}{turn_card._arm_message}\n{summon_message}"
    if turn_card.universe in crown_utilities.universe_stack_traits:
        player1_arm_message = f"**[🎒]Your Equipment**\n{talisman_message}{turn_card._arm_message}\n{universe_stacks}\n{summon_message}"
    tutorial_embed_message = battle_config.get_tutorial_message(turn_card)
    embedVar = Embed(title=f"", color=0xe74c3c)
    # if turn_player.performance:
    #     embedVar.add_field(name=f"➡️ **Current Turn** {battle_config.turn_total}", value=f"{turn_card.get_perfomance_header(turn_title)}")
    # else:
    embedVar.set_author(name=f"{turn_card.summon_resolve_message}\n{author_text}")
    embedVar.add_field(name=f"➡️ **Current Turn** {battle_config.turn_total}", value=f"{player1_arm_message}")
    if battle_config.is_tutorial_game_mode:
        embedVar.add_field(name=f"[🧠]**Tutorial Task!**", value=f"{tutorial_embed_message}")


    # ai_results = summarize_last_moves(battle_config.previous_moves)
    embedVar.set_image(url="attachment://image.png")
    embedVar.set_thumbnail(url=ctx.author.avatar_url)
    embedVar.set_footer(
        text=f"{battle_config.get_previous_moves_embed()}")

    await battle_msg.delete(delay=1)
    await asyncio.sleep(1)
    # if turn_player.performance:
    #     embedVar.add_field(name=f"**Moves**", value=f"{turn_card.get_performance_moveset()}")
    #     battle_msg = await private_channel.send(embed=embedVar, components=components)
    # else:
    image_binary= await asyncio.to_thread(turn_card.showcard,turn_arm, battle_config.turn_total, opponent_card.defense, battle_config.mode)
    # image_binary.seek(0)
    card_file = File(file_name="image.png", file=image_binary)
    battle_msg = await private_channel.send(embed=embedVar, components=components, file=card_file)
    image_binary.close()
    return battle_msg, components


async def start_of_moves_config(battle_config):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    turn_card.set_battle_arm_messages(opponent_card)
    turn_card.set_stat_icons()

    activate_solo_leveling_trait(turn_card, battle_config, opponent_card)
    battle_config.set_battle_options(turn_card, opponent_card,partner_card)


def player_use_card_boost_ability(battle_config, button_ctx):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|s":
            turn_card.use_boost(battle_config, partner_card)
    else:
        return


async def player_move_handler(battle_config, private_channel, button_ctx, battle_msg):
    """
    Handles the player's move in the battle.

    Parameters:
    - battle_config: Configuration object for the battle.
    - private_channel: The private channel for the battle.
    - button_ctx: The context object for the button interaction.
    - battle_msg: The message object for the battle.

    Steps:
    1. Get the battle positions of players, cards, titles, and arms.
    2. Check the custom ID of the button context to determine the selected move.
    3. Call the corresponding function based on the selected move.
    4. Await the damage calculation response from the selected move function.
    5. If the move is resolving or blocking, return immediately.
    6. Handle co-op mode moves if applicable.
    7. Perform player damage calculation asynchronously.

    At some point tutorial messages can be moved to handler
    """
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|q":
        return

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|1":
        damage_calculation_response = await player_use_basic_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_basic == False:
            battle_config.tutorial_basic = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'BASIC')
            await private_channel.send(embed=embedVar)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|2":
        damage_calculation_response = await player_use_special_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_special == False:
            battle_config.tutorial_special = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'SPECIAL')
            await private_channel.send(embed=embedVar)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|3":
        damage_calculation_response = await player_use_ultimate_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_ultimate == False:
            battle_config.tutorial_ultimate = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'ULTIMATE')
            await private_channel.send(embed=embedVar)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|4":
        damage_calculation_response = await player_use_enhancer_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_enhancer == False:
            battle_config.tutorial_enhancer = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'ENHANCER')
            await private_channel.send(embed=embedVar)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|6":
        await player_use_summon_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_summon == False:
            battle_config.tutorial_summon = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'SUMMON')
            await private_channel.send(embed=embedVar)
        return

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|5":
        resolving = await player_use_resolve(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_resolve == False:
            battle_config.tutorial_resolve = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'RESOLVE')
            await private_channel.send(embed=embedVar)
        return

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|0":
        blocking = await player_use_block_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_block == False:
            battle_config.tutorial_block = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'BLOCK')
            await private_channel.send(embed=embedVar)
        return
    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|b":
        blocking = await player_use_blitz_ability(battle_config, private_channel, button_ctx, battle_msg)
        if battle_config.is_tutorial_game_mode and battle_config.tutorial_blitz == False:
            battle_config.tutorial_blitz = True
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, 'BLITZ')
            await private_channel.send(embed=embedVar)
        return
    
    if battle_config.is_co_op_mode:
        if button_ctx.ctx.custom_id == f"{battle_config._uuid}|7":
            turn_card.use_companion_enhancer(battle_config, opponent_card, partner_card)
            return
        
        if button_ctx.ctx.custom_id == f"{battle_config._uuid}|8":
            # Use companion enhancer on you
            partner_card.use_companion_enhancer(battle_config, opponent_card, turn_card)
            return

        if button_ctx.ctx.custom_id == f"{battle_config._uuid}|9":
            partner_card.use_block(battle_config, opponent_card, turn_card)
            return

    complete_damage_calculation = await player_damage_calculation(battle_config, button_ctx, damage_calculation_response)         

#def tutorial_message_handler(turn_card, battle_config, private_channel, message_type):

async def player_use_basic_ability(battle_config, private_channel, button_ctx, battle_msg):
    try:
        turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

        if battle_config.is_turn == 1:
            await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
        damage_calculation_response = turn_card.damage_cal(int(button_ctx.ctx.custom_id.split('|')[1]), battle_config, opponent_card)
        return damage_calculation_response
    except Exception as ex:
        custom_logging.debug(ex)


async def player_use_special_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    
    if battle_config.is_turn == 1:
        await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
    damage_calculation_response = turn_card.damage_cal(int(button_ctx.ctx.custom_id.split('|')[1]), battle_config, opponent_card)
    return damage_calculation_response  


async def player_use_ultimate_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if battle_config.is_turn == 1:
        await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
    damage_calculation_response = turn_card.damage_cal(int(button_ctx.ctx.custom_id.split('|')[1]), battle_config, opponent_card)    
    # if turn_card.gif != "N/A" and not turn_player.performance:
    #     ult_msg = await private_channel.send(f"{turn_card.gif}")
    #     await asyncio.sleep(3)
    #     await ult_msg.delete()
    return damage_calculation_response


async def player_use_enhancer_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    
    if battle_config.is_turn == 1:
        await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
    damage_calculation_response = turn_card.damage_cal(int(button_ctx.ctx.custom_id.split('|')[1]), battle_config, opponent_card)
    return damage_calculation_response


async def player_use_resolve(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    # Resolve Check and Calculation
    if not turn_card.used_resolve and turn_card.used_focus:
        if battle_config.is_turn == 1:
            await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
        await turn_card.resolving(battle_config, turn_title, opponent_card, turn_player)


async def player_use_summon_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    if turn_card.used_resolve and turn_card.used_focus or turn_card._summoner_active:
        if not turn_card.usedsummon:
            if battle_config.is_turn == 1:
                await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
    
    summon_response = turn_card.usesummon(battle_config, opponent_card)
    if not turn_player.performance and summon_response['CAN_USE_MOVE']:
        if not battle_config.is_auto_battle_game_mode:
            embedVar = Embed(title=f"🧬 Summon Executed", color=0xe74c3c)

            image_binary = crown_utilities.showsummon(turn_card.summon_image, turn_card.summon_name, summon_response['MESSAGE'], turn_card.summon_lvl, turn_card.summon_bond)
            image_binary.seek(0)

            embedVar.set_image(url="attachment://pet.png")
            embedVar.set_footer(
                text=f"{battle_config.get_previous_moves_embed()}")
            summon_file = File(file_name="pet.png", file=image_binary)
            await battle_msg.edit(embed=embedVar, components=[], file=summon_file)
            image_binary.close()
            # await battle_msg.edit(embed=embedVar, components=[])


async def player_use_block_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    
    if battle_config.is_turn == 1:
        await player_boss_message_ability_use(battle_config, private_channel, button_ctx)

    turn_card.use_block(battle_config, opponent_card, partner_card)  
    return True

async def player_use_blitz_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    
    if battle_config.is_turn == 1:
        await player_boss_message_ability_use(battle_config, private_channel, button_ctx)

    turn_card.use_blitz(battle_config, opponent_card)  
    return True



async def player_boss_message_ability_use(battle_config, private_channel, button_ctx):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    
    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|5":
        if not turn_card.used_resolve and turn_card.used_focus:
            if battle_config.is_boss_game_mode:
                await button_ctx.ctx.send(embed=battle_config._boss_embed_message)

# This asynchronous function calculates damage inflicted by a player. It checks if a specific option 
# from the main battle options is selected by the player (as indicated by the custom ID of the button 
# context). If it is, the function calls `damage_calculation` to calculate the damage.
async def player_damage_calculation(battle_config, button_ctx, damage_calculation_response=None):    
    if button_ctx.ctx.custom_id.split('|')[1] in battle_config.main_battle_options:
        damage_calculation(battle_config, damage_calculation_response)


# This asynchronous function is used to calculate damage inflicted by an AI. It directly calls 
# `damage_calculation` function to perform the damage calculation.
async def ai_damage_calculation(battle_config, damage_calculation_response=None):
    damage_calculation(battle_config, damage_calculation_response)


# This function calculates damage inflicted in a turn. It retrieves the current positions in the 
# battle and calls the `damage_done` method of the `turn_card` object to calculate the damage. If 
# the monstrosity ability of the `turn_card` is active and it has used resolve, the function 
# incrementally counts double strikes up to a limit specified by the monstrosity value, adding each 
# occurrence to the battle log, and performing additional damage calculation for each double strike. 
# After a double strike is counted, it calls `next_turn` method of `battle_config` object to 
def damage_calculation(battle_config, damage_calculation_response=None):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
    if turn_card._monstrosity_active and turn_card.used_resolve:
        turn_card._monstrosity_value = turn_card._monstrosity_value - 1
        if turn_card._monstrosity_value <= 0:
            turn_card._monstrosity_active = False
            turn_card._monstrosity_value = 0
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {turn_card.name}:  Double Strike! {turn_card._monstrosity_value} Double Strikes Left!")
        turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        if souls_third_phase(turn_card,battle_config):
            damage_calculation_response = turn_card.damage_cal("Souls", battle_config, opponent_card)
            turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        battle_config.next_turn()
    elif souls_third_phase(turn_card,battle_config):
        damage_calculation_response = turn_card.damage_cal("Souls", battle_config, opponent_card)
        turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        battle_config.next_turn()
    else:
        battle_config.next_turn()


# This is an asynchronous function used to handle the end of the game for a player. The function 
# saves the player's game status and then ends the game. The function sets the health of the player 
# to 0, marks the game as over, and saves the current state of the game. If any errors occur during 
# this process, the function captures the exception and prints a detailed traceback.
async def player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|s":
        try:
            turn_player.make_available()
            turn_player.health = 0
            battle_config.game_over = True
            await gs.save_spot(self, turn_player, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
            await battle_msg.delete(delay=1)
            await asyncio.sleep(1)
            battle_msg = await private_channel.send(embed=battle_config.saved_game_embed(turn_player,opponent_card, partner_card))
            return battle_msg
        except Exception as ex:
            custom_logging.debug(ex)
                                                    
# This is an asynchronous function used to handle a player quitting the game. The function sets the 
# health of the player's card to 0, marks the game as over, and logs the event. If the player quits, 
# a message is sent to a private channel. If any errors occur during this process, the function 
# captures the exception and prints a detailed traceback.
async def player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    try:
        if button_ctx.ctx.custom_id == f"{battle_config._uuid}|q" or button_ctx.ctx.custom_id == f"{battle_config._uuid}|Q":
            turn_player.make_available()
            turn_card.health = 0
            battle_config.game_over = True
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) **{turn_card.name}** quit the battle. The match is over.")
            await battle_msg.delete(delay=1)
            await exit_battle_embed(battle_config, button_ctx, private_channel)
            return True
    except Exception as ex:
        custom_logging.debug(ex)




def setup(bot):
    Play(bot)
              