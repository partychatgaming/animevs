import render_cache
import battle_view
import time
import traceback
import crown_utilities
import custom_logging
from cogs.game_state import GameState as gs
import uuid
import asyncio
from io import BytesIO
from logger import loggy
# import bot as main
import cogs.tactics as tactics
from cogs.universe_traits.bleach import second_release
from cogs.universe_traits.death_note import set_deathnote_message
from cogs.universe_traits.solo_leveling import activate_solo_leveling_trait
from cogs.universe_traits.souls import souls_third_phase
from interactions import ActionRow, Button, File, ButtonStyle, listen, Embed, Extension
from interactions.client.errors import HTTPException

# --------------------------------------------------------------------------- pacing
# Seconds the bot deliberately waits so players can read what happened.  The old
# loop slept ~5s on every AI turn and ~3s on every player turn (on top of the
# time spent rendering and talking to Discord); these are the only waits left.
AI_TURN_READ_DELAY = 1.5      # the AI's card stays on screen this long before it moves
SUMMON_READ_DELAY = 1.5       # summon splash
INFO_EMBED_DELAY = 2          # tutorial / boss story embeds
COMPONENT_TIMEOUT = 300       # seconds a player has to press a button

# A real battle lasts a few dozen actions.  This is only a safety net so a
# stalemate (two cards that cannot hurt each other) can never run forever.
MAX_BATTLE_ACTIONS = 600

_BATTLE_OVER = object()       # sentinel: the whole battle session is finished


class Play(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        # print('Play Cog is ready!')
        loggy.info('Play Cog is ready')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    async def battle_commands(self, ctx, battle_config, opponent_1=None, partner1=None):
        """
        Runs a battle session (one or more consecutive matches) from the start
        screen to the results screen.

        Parameters:
        - self: The cog (or RPG instance) that started the battle.
        - ctx: The context of the command.
        - battle_config: Configuration object for the battle.
        - opponent_1: Optional PvP opponent.
        - partner1: Optional partner in co-op mode.

        Whatever happens inside a match, this function always leaves the session
        in a clean state: the players are released, the loop stops, and the
        player is told what happened.  It never restarts a broken match.
        """
        private_channel = ctx.channel
        state = {"battle_msg": None, "start_msg": None}
        if not hasattr(self, 'bot'):
            self.bot = self.client

        try:
            battle_config._uuid = uuid.uuid4()
            game_start = set_battle_start_time()

            while battle_config.continue_fighting:
                state["battle_msg"] = None
                state["start_msg"] = None
                outcome = await run_match(self, ctx, battle_config, private_channel, state, game_start, opponent_1, partner1)
                if outcome is _BATTLE_OVER:
                    return

        except asyncio.TimeoutError:
            loggy.warning("Battle timed out waiting for a player")
            await end_battle_on_timeout(self, ctx, private_channel, state, battle_config)

        except Exception as ex:
            loggy.critical(f"Battle ended unexpectedly: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")
            custom_logging.debug(ex)
            await end_battle_on_error(self, private_channel, state, battle_config, ex)


    async def rpg_commands(self, ctx, rpg_starter_message):
        """
        Handles the logic for an RPG game in the game.

        Parameters:
        - self: The instance of the class.
        - ctx: The context of the command.
        - rpg_config: Configuration object for the RPG game.

        Returns:
        None
        """
        private_channel = ctx.channel
        rpg_config = self
        rpg_msg = rpg_starter_message
        try:
            rpg_config._uuid = uuid.uuid4()
            if not hasattr(self, 'bot'):
                self.bot = self.client

            user = await get_rpg_user(rpg_config)
            while rpg_config.adventuring:
                if check_if_rpg_over(rpg_config):
                    break
                configure_battle_log(rpg_config)
                rpg_config.set_rpg_options()

                rpg_msg, components = await rpg_config.rpg_player_move_embed(ctx, private_channel, rpg_msg)

                def check(component: Button) -> bool:
                    return component.ctx.author == user

                if not components:
                    # Nothing to press (an encounter flag left behind by a battle that
                    # ended abnormally): drop back to the map instead of crashing.
                    loggy.warning("Adventure had no buttons to show; clearing the encounter state")
                    rpg_config.encounter = False
                    rpg_config.battling = False
                    continue
                button_ctx = await self.bot.wait_for_component(components=components, timeout=COMPONENT_TIMEOUT, check=check)
                await button_ctx.ctx.defer(edit_origin=True, suppress_error=True)

                await rpg_config.rpg_move_handler(ctx, private_channel, button_ctx, rpg_msg)

        except asyncio.TimeoutError:
            loggy.warning("Adventure timed out waiting for the player")
            rpg_config.previous_moves.append("🏁 Adventure has ended!")
            rpg_config.adventuring = False
            release_player(getattr(rpg_config, "player1", None) or getattr(rpg_config, "_player", None))
            try:
                await timeout_handler(self, ctx, rpg_msg, rpg_config)
            except Exception as ex:
                custom_logging.debug(ex)

        except Exception as ex:
            loggy.critical(f"Adventure ended unexpectedly: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")
            rpg_config.adventuring = False
            release_player(getattr(rpg_config, "player1", None) or getattr(rpg_config, "_player", None))
            custom_logging.debug(ex)


# --------------------------------------------------------------------------- session plumbing
def release_player(player):
    """Mark a player as free to start another battle.  Never raises.

    The database write runs in a worker thread so it does not stall every other
    battle while it waits on MongoDB.
    """
    try:
        if player is not None and hasattr(player, "make_available"):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop is not None:
                loop.run_in_executor(None, player.make_available)
            else:
                player.make_available()
    except Exception as ex:
        custom_logging.debug(ex)


def release_all_players(battle_config):
    for name in ("player1", "player2", "player3"):
        player = getattr(battle_config, name, None)
        # AI opponents are plain cards / have no account to release
        if player is not None and getattr(player, "did", None):
            release_player(player)


async def safe_delete(message):
    """Delete a message if it still exists; a missing message is not an error."""
    if message is None:
        return
    try:
        await message.delete()
    except Exception:
        pass


async def show_battle_view(private_channel, battle_msg, container, image_bytes=None, file_name=battle_view.SCENE_FILE):
    """
    Put the current state of the battle on screen.

    The battle lives in ONE Components V2 message that is edited in place
    (uploading a file on edit replaces the previous attachment).  If the
    message is gone (deleted by a moderator, or never created) a new one is
    sent instead.
    """
    def payload():
        data = {"components": [container]}
        if image_bytes is not None:
            data["file"] = battle_view.scene_file(image_bytes, file_name)
        return data

    if battle_msg is not None:
        try:
            await battle_msg.edit(**payload())
            return battle_msg
        except HTTPException as ex:
            loggy.warning(f"Could not edit the battle message ({ex}); sending a new one")
            await safe_delete(battle_msg)
    return await private_channel.send(**payload())


def battle_setup_problem(battle_config):
    """Return a description of what is missing if the fighters could not be built, else None."""
    needed = [("player1_card", "your card"), ("player1_title", "your title"), ("player1_arm", "your arm"),
              ("player2_card", "the opponent's card"), ("player2_title", "the opponent's title"), ("player2_arm", "the opponent's arm")]
    if battle_config.is_co_op_mode or battle_config.is_duo_mode:
        needed += [("player3_card", "your partner's card"), ("player3_title", "your partner's title"), ("player3_arm", "your partner's arm")]
    for attr, label in needed:
        if not getattr(battle_config, attr, None):
            return label
    return None


async def end_battle_on_error(self, private_channel, state, battle_config, ex):
    """A match hit an unexpected error: stop cleanly and tell the player instead of looping."""
    battle_config.continue_fighting = False
    release_all_players(battle_config)
    if getattr(battle_config, "is_rpg", False) and getattr(battle_config, "rpg_config", None) is not None:
        restore_rpg_after_battle(self, battle_config, "⚠️ The encounter ended unexpectedly. Resuming Adventure...")
    try:
        can_save = (battle_config.player1_card is not None and battle_config.match_can_be_saved
                    and not battle_config.is_rpg and battle_config.selected_universe)
        if can_save:
            await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
        embed = Embed(title="⚠️ This battle ran into a problem and had to end",
                      description=("Your progress in this run was saved, so you can pick up where you left off." if can_save
                                   else "You can start a new battle right away."),
                      color=0xE74C3C)
        embed.set_footer(text=crown_utilities.clip(f"{type(ex).__name__}: {ex}", 300))
        for key in ("battle_msg", "start_msg"):
            if state.get(key) is not None:
                await safe_delete(state.get(key))
                state[key] = None
        await private_channel.send(embed=embed)
    except Exception as notify_error:
        custom_logging.debug(notify_error)


async def end_battle_on_timeout(self, ctx, private_channel, state, battle_config):
    battle_config.continue_fighting = False
    release_all_players(battle_config)
    try:
        await timeout_handler(self, ctx, state.get("battle_msg") or state.get("start_msg"), battle_config)
    except Exception as ex:
        custom_logging.debug(ex)


def restore_rpg_after_battle(self, battle_config, log_line=None):
    """Hand control back to the adventure after an RPG encounter ends early."""
    rpg = getattr(battle_config, "rpg_config", None)
    for target in (self, rpg):
        if target is None:
            continue
        try:
            target.battling = False
            target.adventuring = True
            target.encounter = False
        except Exception:
            pass
    try:
        if rpg is not None and battle_config.player1_card is not None:
            rpg.player_health = round(battle_config.player1_card.health)
        if log_line and rpg is not None:
            rpg.previous_moves.append(log_line)
    except Exception as ex:
        custom_logging.debug(ex)


# --------------------------------------------------------------------------- one match
async def run_match(self, ctx, battle_config, private_channel, state, game_start, opponent_1, partner1):
    """
    Play one match: set up the fighters, show the start screen, run the turns,
    then hand over to the results handlers.

    Returns _BATTLE_OVER when the session should stop; otherwise the caller
    loops again if battle_config.continue_fighting is still set (next opponent,
    rematch...).
    """
    await battle_config.configure_battle_players(ctx, opponent_1, partner1)
    missing = battle_setup_problem(battle_config)
    if missing:
        loggy.error(f"Battle setup failed: could not load {missing} (mode={battle_config.mode})")
        battle_config.continue_fighting = False
        release_all_players(battle_config)
        if battle_config.is_rpg and battle_config.rpg_config is not None:
            restore_rpg_after_battle(self, battle_config, "⚠️ The encounter could not be set up. Resuming Adventure...")
        if not battle_config.abyss_player_card_tier_is_banned:
            await private_channel.send(embed=Embed(
                title="⚠️ This battle could not be set up",
                description=f"I couldn't load {missing}. Check your equipped card, title, arm and summon with /build and try again.",
                color=0xE74C3C))
        return _BATTLE_OVER

    start_buttons_action_rows = config_battle_starting_buttons(battle_config)
    battle_config.set_who_starts_match()

    user1, user2, opponent_ping, user3 = await get_users_and_opponent_ping(self, battle_config)
    battle_config.turn_zero_has_happened = False
    battle_config._actions_taken = 0

    # The old start screen drew this card, which also set its per-turn move
    # values for turn 0; keep that so nothing changes in the first turn.
    battle_view.refresh_move_values(battle_config.player1_card if battle_config.is_pvp_game_mode else battle_config.player2_card,
                                    battle_config.turn_total)
    if opponent_ping == "...":
        opponent_ping = f"**{battle_config.player2_card.name}**"
    image_bytes = await battle_view.render_matchup(battle_config)
    battle_start_msg = await private_channel.send(
        components=[battle_view.start_view(battle_config, start_buttons_action_rows, f"{user1.mention} 🆚 {opponent_ping}")],
        file=battle_view.scene_file(image_bytes, battle_view.START_FILE),
    )
    state["start_msg"] = battle_start_msg

    def start_check(component: Button) -> bool:
        if battle_config.is_pvp_game_mode and not battle_config.is_tutorial_game_mode:
            return component.ctx.author == user2
        return component.ctx.author == ctx.author

    # asyncio.TimeoutError propagates to battle_commands, which closes the session
    button_ctx = await self.bot.wait_for_component(components=[start_buttons_action_rows], timeout=COMPONENT_TIMEOUT, check=start_check)
    await button_ctx.ctx.defer(edit_origin=True, suppress_error=True)
    custom_id = button_ctx.ctx.custom_id

    if custom_id == f"{battle_config._uuid}|quit_game":
        battle_config.continue_fighting = False
        if battle_config.is_rpg:
            await safe_delete(battle_start_msg)
            restore_rpg_after_battle(self, battle_config, "💨Fleeing Encounter...Resuming Adventure...!")
            return _BATTLE_OVER
        release_all_players(battle_config)
        await safe_delete(battle_start_msg)
        await exit_battle_embed(battle_config, button_ctx, private_channel)
        return _BATTLE_OVER

    if custom_id == f"{battle_config._uuid}|save_game":
        battle_config.continue_fighting = False
        await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
        release_all_players(battle_config)
        try:
            await battle_start_msg.edit(components=[battle_view.start_banner(battle_config, "💾 Saved. Pick up from this match next time.")], files=[])
        except HTTPException:
            pass
        await private_channel.send(embed=battle_config.saved_game_embed(battle_config.player1_card, battle_config.player2_card))
        return _BATTLE_OVER

    if custom_id not in {f"{battle_config._uuid}|start_game", f"{battle_config._uuid}|start_game_auto_battle_mode"}:
        # Unknown button: nothing sensible to do but stop.
        battle_config.continue_fighting = False
        release_all_players(battle_config)
        return _BATTLE_OVER

    if battle_config.is_rpg:
        await safe_delete(battle_start_msg)
        state["start_msg"] = None
    else:
        started = "🤖 Auto battle" if custom_id.endswith("|start_game_auto_battle_mode") else "▶️ Match started"
        try:
            await battle_start_msg.edit(components=[battle_view.start_banner(battle_config, started)], files=[])
        except HTTPException:
            pass

    if battle_config.match_can_be_saved and battle_config.player1.autosave:
        await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)

    if custom_id == f"{battle_config._uuid}|start_game_auto_battle_mode":
        battle_config.is_auto_battle_game_mode = True
        embedVar = Embed(title=f"The battle is being simulated...", color=0xe74c3c)
        embedVar.set_thumbnail(url=ctx.author.avatar_url)
        battle_msg = await private_channel.send(embed=embedVar)
    else:
        battle_msg = await private_channel.send(components=[battle_view.notice_panel("### ⚔️ The battle is starting…", 0x2ECC71)])
    state["battle_msg"] = battle_msg

    tactics.tactics_set_base_stats(battle_config.player2_card)

    result = await run_turns(self, ctx, battle_config, private_channel, state, user1, user2, button_ctx)
    if result is _BATTLE_OVER:
        return _BATTLE_OVER
    battle_msg = state["battle_msg"]

    # ---- the match is over: results, rewards, next opponent / rematch
    gameClock = get_battle_time(*game_start)

    await gs.pvp_end_game(self, battle_config, private_channel, battle_msg, gameClock)

    await gs.you_win_non_pvp(self, ctx, battle_config, private_channel, battle_msg, gameClock, user1, user2=None)

    if battle_config.is_rpg:
        self.battling = False
        self.adventuring = True
        self.encounter = False
        battle_config.continue_fighting = False
        battle_config.rpg_config.player_health = round(battle_config.player1_card.health)
        if battle_config.rpg_config.player_health <= 0:
            paginator = await battle_config.rpg_config.lose_adventure_embed(ctx)
            await paginator.send(ctx)
            await safe_delete(battle_msg)
            await safe_delete(battle_config.rpg_config._rpg_msg)
            self.previous_moves.append(f"💨Fleeing Encounter...!")
            return _BATTLE_OVER
        embedVar = Embed(title=f"🆚 Encounter Victory", color=0x2ECC71)
        victory_msg = await private_channel.send(embed=embedVar)
        try:
            await victory_msg.delete(delay=5)
        except Exception:
            pass
        return _BATTLE_OVER

    await gs.you_lose_non_pvp(self, battle_config, private_channel, battle_msg, gameClock, user1, user2=None)

    if not (battle_config.player1_wins or battle_config.player2_wins) and battle_config.match_has_ended and battle_config.continue_fighting:
        # A finished match that nobody won (should not happen) must not be replayed forever.
        battle_config.continue_fighting = False
    if not battle_config.continue_fighting:
        release_all_players(battle_config)
    return None


async def run_turns(self, ctx, battle_config, private_channel, state, user1, user2, button_ctx):
    """
    The turn loop of a single match.  Returns _BATTLE_OVER if the session ended
    during play (surrender, save, timeout); returns None when the match reached
    a normal end and the results handlers should run.
    """
    while True:
        if check_if_game_over(battle_config):
            return None
        configure_battle_log(battle_config)

        await add_ai_start_messages(battle_config)

        early_game_tactics(battle_config)
        if check_if_game_over(battle_config):
            return None

        if battle_config.is_auto_battle_game_mode:
            winning_card, message = calculate_instant_winner(battle_config, battle_config.player1_card, battle_config.player2_card)
            battle_config.auto_battle_result_message = message
            battle_config.continue_fighting = False
            battle_config.match_has_ended = True
            return None

        if stalemate_check(battle_config):
            return None

        # ---------------------------------------------------------------- player 1
        if battle_config.is_turn == 0:
            if damage_check_turn_check(battle_config):
                continue
            if await start_to_focus(state["battle_msg"], private_channel, battle_config):
                continue

            outcome = await human_turn(self, ctx, battle_config, private_channel, state, user1, (battle_config.player1,))
            if outcome is _BATTLE_OVER:
                return _BATTLE_OVER

        if check_if_game_over(battle_config):
            return None

        tactics.beginning_of_turn_stat_trait_affects(battle_config.player2_card, battle_config.player2_title, battle_config.player1_card, battle_config, battle_config.player3_card)

        if check_if_game_over(battle_config):
            return None

        # ---------------------------------------------------------------- player 2 / AI
        if battle_config.is_turn == 1:
            if damage_check_turn_check(battle_config):
                continue
            if await start_to_focus(state["battle_msg"], private_channel, battle_config):
                continue

            if battle_config.is_pvp_game_mode and not battle_config.is_tutorial_game_mode:
                outcome = await human_turn(self, ctx, battle_config, private_channel, state, user2, (battle_config.player1, battle_config.player2))
                if outcome is _BATTLE_OVER:
                    return _BATTLE_OVER
            else:
                state["battle_msg"] = await ai_move_handler(ctx, battle_config, private_channel, state["battle_msg"])

        if battle_config.is_co_op_mode or battle_config.is_duo_mode:
            if check_if_game_over(battle_config):
                return None
            tactics.beginning_of_turn_stat_trait_affects(battle_config.player3_card, battle_config.player3_title, battle_config.player2_card, battle_config, battle_config.player1_card)

            if check_if_game_over(battle_config):
                return None

            # ------------------------------------------------------------ partner
            if battle_config.is_turn == 2:
                if damage_check_turn_check(battle_config):
                    continue
                if await start_to_focus(state["battle_msg"], private_channel, battle_config):
                    continue

                if battle_config.is_co_op_mode and not battle_config.is_duo_mode:
                    outcome = await human_turn(self, ctx, battle_config, private_channel, state, user2, (battle_config.player1, battle_config.player3))
                    if outcome is _BATTLE_OVER:
                        return _BATTLE_OVER
                else:
                    state["battle_msg"] = await ai_move_handler(ctx, battle_config, private_channel, state["battle_msg"])
                    continue

            if check_if_game_over(battle_config):
                return None

            tactics.beginning_of_turn_stat_trait_affects(battle_config.player2_card, battle_config.player2_title, battle_config.player3_card, battle_config, battle_config.player1_card)

            if check_if_game_over(battle_config):
                return None

            # ------------------------------------------------------------ opponent vs partner
            if battle_config.is_turn == 3:
                if damage_check_turn_check(battle_config):
                    continue
                if await start_to_focus(state["battle_msg"], private_channel, battle_config):
                    continue

                if battle_config.is_pvp_game_mode:
                    outcome = await human_turn(self, ctx, battle_config, private_channel, state, user2, (battle_config.player1, battle_config.player2))
                    if outcome is _BATTLE_OVER:
                        return _BATTLE_OVER
                else:
                    state["battle_msg"] = await ai_move_handler(ctx, battle_config, private_channel, state["battle_msg"])
                    continue


async def human_turn(self, ctx, battle_config, private_channel, state, user, players_to_release):
    """
    Show the move buttons to `user`, wait for the choice and resolve it.
    Returns _BATTLE_OVER when the session ended (save, surrender or timeout).

    The More panel (details, full log, Save & quit, Surrender) is private to
    the player and does not use up the turn; the turn's timer keeps running
    while it is open.
    """
    battle_msg, listen = await player_move_embed(ctx, battle_config, private_channel, state["battle_msg"])
    state["battle_msg"] = battle_msg

    def check(component: Button) -> bool:
        return component.ctx.author == user

    panel = battle_view.panel_ids(battle_config)
    loop = asyncio.get_running_loop()
    deadline = loop.time() + COMPONENT_TIMEOUT
    while True:
        try:
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise asyncio.TimeoutError()
            button_ctx = await self.bot.wait_for_component(components=listen, timeout=remaining, check=check)
        except asyncio.TimeoutError:
            battle_config.continue_fighting = False
            for player in players_to_release:
                release_player(player)
            try:
                await timeout_handler(self, ctx, battle_msg, battle_config)
            except Exception as ex:
                custom_logging.debug(ex)
            return _BATTLE_OVER
        if button_ctx.ctx.custom_id not in panel:
            break
        await more_panel_action(battle_config, button_ctx.ctx)

    # Acknowledge inside Discord's 3 second window; a late ack must not kill the battle.
    if button_ctx.ctx.custom_id in battle_view.end_ids(battle_config):
        # pressed inside the private panel: close the panel
        notice = "💾 Saving your battle…" if button_ctx.ctx.custom_id == battle_view.save_id(battle_config) else "🏳️ You left the battle."
        try:
            await button_ctx.ctx.edit_origin(components=[battle_view.notice_panel(notice, 0x95A5A6)])
        except Exception:
            await button_ctx.ctx.defer(edit_origin=True, suppress_error=True)
    else:
        await button_ctx.ctx.defer(edit_origin=True, suppress_error=True)

    if await player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx):
        battle_config.continue_fighting = False
        for player in players_to_release:
            release_player(player)
        return _BATTLE_OVER

    if await player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx):
        battle_config.continue_fighting = False
        if not battle_config.is_rpg:
            for player in players_to_release:
                release_player(player)
        else:
            restore_rpg_after_battle(self, battle_config)
        return _BATTLE_OVER

    player_use_card_boost_ability(battle_config, button_ctx)

    await player_move_handler(battle_config, private_channel, button_ctx, battle_msg)
    return None


async def more_panel_action(battle_config, interaction_ctx):
    """Open / work the private More panel.  Never raises and never ends the turn."""
    custom_id = interaction_ctx.custom_id
    try:
        if custom_id == battle_view.more_id(battle_config):
            await interaction_ctx.send(components=[battle_view.more_panel(battle_config)], ephemeral=True)
        elif custom_id == battle_view.surrender_ask_id(battle_config):
            await interaction_ctx.edit_origin(components=[battle_view.surrender_confirm_panel(battle_config)])
        elif custom_id == battle_view.cancel_id(battle_config):
            await interaction_ctx.edit_origin(components=[battle_view.notice_panel("⚔️ Back to the fight!")])
    except Exception as ex:
        loggy.warning(f"More panel action {custom_id} failed: {type(ex).__name__}: {ex}")
        try:
            await interaction_ctx.defer(ephemeral=True, suppress_error=True)
        except Exception:
            pass


def stalemate_check(battle_config):
    """End a match that has gone on absurdly long (neither side can finish the other)."""
    battle_config._actions_taken = getattr(battle_config, "_actions_taken", 0) + 1
    if battle_config._actions_taken <= MAX_BATTLE_ACTIONS:
        return False
    p1, p2 = battle_config.player1_card, battle_config.player2_card
    p1_ratio = p1.health / max(1, p1.max_health)
    p2_ratio = p2.health / max(1, p2.max_health)
    battle_config.add_to_battle_log(f"({battle_config.turn_total}) ⏱️ The battle dragged on too long and was called off!")
    if battle_config.is_pvp_game_mode and p1_ratio > p2_ratio:
        p2.health = 0
    else:
        # In PvE the challenger has to actually win; in PvP the healthier card takes it.
        p1.health = 0
    check_if_game_over(battle_config)
    if not battle_config.match_has_ended:      # tutorial dummy etc.
        battle_config.match_has_ended = True
        battle_config.player2_wins = True
    return True


async def add_ai_start_messages(battle_config):
    if not battle_config.turn_zero_has_happened:
        class_effects = {
            "ASSASSIN": "🥋 {name} the {class_message} gained 💢Blitz and {class_value} sneak attacks",
            "MAGE": "🥋 {name} the {class_message} gained a {class_value}% boost to 🔅elemental attacks",
            "RANGER": "🥋 {name} the {class_message} gained 💠 {class_value} barriers",
            "TANK": "🥋 {name} the {class_message} gained a 🌐 {class_value} shield",
            "HEALER": "🥋 {name} the {class_message} boosted their  ❤️‍🩹healing by {class_value}%",
            "SUMMONER": "🥋 {name} the {class_message} calls forth 🧬{summon_name} with {summoner_value}% increased ability",
            "FIGHTER": "🥋 {name} the {class_message} gained 🔁 {class_value} parries & doubled protection arms",
        }

        def append_previous_moves(card, player_name):
            if card.card_class in class_effects:
                battle_config.previous_moves.append(
                    class_effects[card.card_class].format(
                        name=card.name, 
                        summon_name=card.summon_name,
                        class_message=card.class_message, 
                        class_value= card.class_value,
                        summoner_value= card.tier * 20
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


def calculate_instant_winner(battle_config, card1, card2, level_threshold=300):
    if (card1.card_lvl - card2.card_lvl) >= level_threshold:
        card2.health = 0
        battle_config.player1_wins = True
        battle_config.player2_wins = False
        return card1, "Level advantage"
    if (card2.card_lvl - card1.card_lvl) >= level_threshold:
        card1.health = 0
        battle_config.player1_wins = False
        battle_config.player2_wins = True
        return card2, "Level advantage"
    
    def calculate_battle_rating(attacker, defender):
        # Offensive Rating
        moves = [
            (attacker.move1ap, attacker.move1_element, attacker.move1_stamina),
            (attacker.move2ap, attacker.move2_element, attacker.move2_stamina),
            (attacker.move3ap, attacker.move3_element, attacker.move3_stamina)
        ]
        
        # Calculate sustainable damage considering stamina
        sustainable_power = 0
        for ap, element, stamina_cost in moves:
            if stamina_cost == 0:
                stamina_cost = 1
            turns_until_exhaustion = attacker.stamina / stamina_cost
            
            defense_power = max(0, defender.defense - attacker.attack)
            attack_power = attacker.attack + ap
            ability_power = max(ap, attack_power - defense_power)
            
            # Apply element modifiers
            if element in defender.weaknesses:
                ability_power *= 1.6
            elif element in defender.resistances:
                ability_power *= 0.45
            elif element in defender.immunity:
                ability_power = 0
            elif element in defender.repels or element in defender.absorbs:
                ability_power = 0
                
            # Consider sustainable damage over time
            sustainable_power = max(sustainable_power, ability_power * turns_until_exhaustion)
        
        # Calculate overall battle rating
        offensive_rating = sustainable_power / max(1, defender.health)
        defensive_rating = attacker.defense / max(1, defender.attack)
        stamina_rating = attacker.stamina / 100  # Normalize stamina
        
        return (offensive_rating * 0.5) + (defensive_rating * 0.3) + (stamina_rating * 0.2)

    card1_rating = calculate_battle_rating(card1, card2)
    card2_rating = calculate_battle_rating(card2, card1)
    
    # Add some randomness for close matches
    if abs(card1_rating - card2_rating) < 0.1:
        card1.health = 0
        battle_config.player2_wins = True
        return None, "Too close to call"
    elif card1_rating > card2_rating:
        card2.health = 0
        battle_config.player1_wins = True
        battle_config.player2_wins = False
        return card1, f"Better overall combat rating ({card1_rating:.2f} vs {card2_rating:.2f})"
    else:
        card1.health = 0
        battle_config.player2_wins = True
        return card2, f"Worse overall combat rating ({card2_rating:.2f} vs {card1_rating:.2f})"


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
            style=ButtonStyle.GREEN,
            label=crown_utilities.clip(f"{start_message}", 80),
            emoji="⚔️",
            custom_id=f"{battle_config._uuid}|start_game"
        ),
    ]

    if battle_config.can_auto_battle and not battle_config.is_co_op_mode and not battle_config.is_duo_mode:
        start_tales_buttons.append(
            Button(
                style=ButtonStyle.GREY,
                label="Auto Battle",
                emoji="🤖",
                custom_id=f"{battle_config._uuid}|start_game_auto_battle_mode"
            )
        )

    if not battle_config.is_tutorial_game_mode and battle_config.save_match_turned_on() and not battle_config.is_rpg:
        if battle_config.current_opponent_number > 0:
            start_tales_buttons.append(
                Button(
                    style=ButtonStyle.GREY,
                    label="Save & Quit",
                    emoji="💾",
                    custom_id=f"{battle_config._uuid}|save_game"
                )
            )

    start_tales_buttons.append(
        Button(
            style=ButtonStyle.RED,
            label="Flee" if battle_config.is_rpg else "End",
            custom_id=f"{battle_config._uuid}|quit_game"
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


async def get_rpg_user(self):
    """
    Get the user object from the context object.

    Parameters:
    - ctx: The context object for the current command.

    Returns:
    User: The user object for the context object.
    """
    if hasattr(self, 'bot'):
        pass
    else:
        self.bot = self.client
    user = await self.bot.fetch_user(self.player1_did)
    return user


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
    battle_config.auto_battle_result_message = ""
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
        if battle_config.is_rpg:
            await private_channel.send(embed=battle_config.rpg_config.close_rpg_embed(battle_config.player1_card, battle_config.player2_card))
        else:
            await private_channel.send(embed=battle_config.close_pve_embed(battle_config.player1_card, battle_config.player2_card))
    else:
        await private_channel.send(embed=battle_config.close_pvp_embed(battle_config.player1, battle_config.player2))
    return


def check_if_rpg_over(rpg_config):
    if rpg_config.player_health <= 0:
        rpg_config.adventuring = False
        return True
    else:
        return False


def configure_battle_log(battle_config):
    #Checks for RPG Game over battle_config is cosidered as rpg_config
    if battle_config.is_rpg:
        rpg_config = battle_config
        if rpg_config.previous_moves:
            rpg_config.previous_moves_len = len(rpg_config.previous_moves)
            if rpg_config.previous_moves_len >= rpg_config.player1.battle_history:
                rpg_config.previous_moves = rpg_config.previous_moves[-rpg_config.player1.battle_history:]
        return
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if battle_config.previous_moves:
        battle_config.previous_moves_len = len(battle_config.previous_moves)
        if battle_config.previous_moves_len >= battle_config.player1.battle_history:
            battle_config.previous_moves = battle_config.previous_moves[-battle_config.player1.battle_history:]


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
                    if title and text:
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
                    if title and text:
                        embedVar.add_field(name=f"[{battle_config.player1_card.universe_crest}] {battle_config.player1_card.universe} Trait: {title}",
                                    value=f"{text}")
                embedVar.add_field(name="\n**[Moveset]**",value=f"{battle_config.player1_card.move1_emoji} - **Basic {battle_config.player1_card.move1_element.title()} Attack** *⚡10 ST*\n{battle_config.player1_card.move2_emoji} - **Special {battle_config.player1_card.move2_element.title()} Attack** *⚡30 ST*\n{battle_config.player1_card.move3_emoji} - **Ultimate {battle_config.player1_card.move3_element.title()} Attack** *⚡80 ST*\n🦠 - **{battle_config.player1_card.move4enh.title()} Enhancer** *⚡20 ST*\n\n**[Skills]**\n{block_message}\n💢 - **Blitz**: Boost ATK and DEF by SPD ⚡ All\n\n**[Transformations]**\n🌀 - **Focus**: Increase ST, ATK, DEF and Heal\n⚡ - **Resolve**: Heal and Activate Summon\n🧬 - ** {battle_config.player1_card.summon_type.title()} Summon** : {battle_config.player1.equipped_summon}\n")
                #embedVar.add_field(name=f"🧠**Tutorial Task!**", value=f"*Interactively learn about your Elemental Attacks and Card Abilities!*")
                embedVar.set_footer(text="Focus State: When your ST(Stamina) is < 10, You will FOCUS to gain ATK and DEF and heal a portion of missing HP(Health)")
                await private_channel.send(embed=embedVar)
                await asyncio.sleep(2)


async def start_of_moves_config(battle_config):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    turn_card.set_battle_arm_messages(opponent_card)
    turn_card.set_stat_icons()

    activate_solo_leveling_trait(turn_card, battle_config, opponent_card)
    battle_config.set_battle_options(turn_card, opponent_card,partner_card)


def player_use_card_boost_ability(battle_config, button_ctx):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|t":
            turn_card.use_boost(battle_config, partner_card)
    else:
        return


async def timeout_handler(self, ctx, battle_msg, battle_config):
    """A player stopped responding: close the battle (saving the run where that is allowed)."""
    battle_config.continue_fighting = False
    channel = ctx.channel
    await safe_delete(battle_msg)

    if battle_config.is_rpg:
        if getattr(battle_config, "rpg_config", None) is not None:
            # An encounter inside an adventure timed out: drop back to the map.
            restore_rpg_after_battle(self, battle_config, "⌛ The encounter timed out. Resuming Adventure...")
            return
        # The adventure itself timed out (battle_config is the RPG instance).
        x, y = battle_config._player.player_position
        battle_config._player.map['map'][x][y] = battle_config._player.standing_on
        close_embded = await channel.send(embed=battle_config.close_rpg_embed())
        try:
            await close_embded.delete(delay=3)
        except Exception:
            pass
        await battle_config.leave_adventure_embed(ctx)
        return

    if not any((battle_config.is_abyss_game_mode,
                battle_config.is_scenario_game_mode,
                battle_config.is_explore_game_mode,
                battle_config.is_pvp_game_mode,
                battle_config.is_tutorial_game_mode,
                battle_config.is_boss_game_mode)):
        await gs.save_spot(self, battle_config.player1, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
        await channel.send(embed=battle_config.saved_game_embed(battle_config.player1_card, battle_config.player2_card))
    elif any((battle_config.is_pvp_game_mode,
              battle_config.is_tutorial_game_mode)):
        await channel.send(embed=battle_config.close_pvp_embed(battle_config.player1, battle_config.player2))
    else:
        await channel.send(embed=battle_config.close_pve_embed(battle_config.player1_card, battle_config.player2_card))
    await channel.send(f"{ctx.author.mention} {battle_config.error_end_match_message()}")


def check_if_game_over(battle_config):
    player3_card = battle_config.player3_card if battle_config.is_duo_mode or battle_config.is_co_op_mode else None
    if battle_config.is_tutorial_game_mode and battle_config.player2_card.health <= 0 and not battle_config.all_tutorial_tasks_complete:
        battle_config.turn_total -= 1
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ❌ Tutorial Task Incomplete!\nComplete your Tutorial Task to defeat the Training Dummy!")
        battle_config.turn_total += 1
    game_over_check = battle_config.set_game_over(battle_config.player1_card, battle_config.player2_card, player3_card)

    return bool(game_over_check)


async def start_to_focus(battle_msg, private_channel, battle_config):
    """
    Performs the start-of-turn actions for the card whose turn it is.

    Returns True if the card had to Focus (stamina below 10), which uses up its
    turn, and False if it is free to act.
    """
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
        if not turn_card.used_blitz:
            await tutorial_focusing(turn_card, battle_config, private_channel)
        await boss_focusing(battle_config, private_channel)
        focusing = True

    return focusing


async def ai_move_handler(ctx, battle_config, private_channel, battle_msg=None):
    """
    Plays the AI's turn: shows its card, pauses briefly so the player can read
    the board, then resolves the move the AI picked.

    Returns the battle message (a new one if the old one had to be replaced).
    """
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    await start_of_moves_config(battle_config)
    # starting traits / arm messages (the embed it also builds is no longer shown)
    await tactics.auto_battle_embed_and_starting_traits(ctx, turn_card, turn_title, opponent_card, opponent_title, battle_config, partner_card, partner_title)
    battle_view.refresh_move_values(turn_card, battle_config.turn_total)
    image_bytes, image_name, announcement = await battle_view.render_scene(battle_config)
    battle_msg = await show_battle_view(private_channel, battle_msg, battle_view.ai_turn_view(battle_config, turn_card, image_name, announcement),
                                        image_bytes, image_name)
    await asyncio.sleep(AI_TURN_READ_DELAY)

    selected_move = battle_config.ai_battle_command(turn_card, opponent_card)

    if selected_move == 5:
        was_resolved = turn_card.used_resolve
        await turn_card.resolving(battle_config, turn_title, opponent_card, turn_player)
        if turn_card.used_resolve == was_resolved:
            # Resolve was not available after all; don't let the AI stall on it.
            selected_move = 1
        else:
            if battle_config.is_boss_game_mode and battle_config._boss_embed_message:
                await private_channel.send(embed=battle_config._boss_embed_message)
            return battle_msg

    if selected_move == 6:
        turn_card.usesummon(battle_config, opponent_card)
        return battle_msg

    if selected_move == 0:
        if turn_card.stamina >= 20:
            turn_card.use_block(battle_config, opponent_card)
            return battle_msg
        selected_move = 1   # too tired to block: attack instead of repeating the turn forever

    if selected_move not in (1, 2, 3, 4):
        selected_move = 1

    damage_calculation_response = turn_card.damage_cal(selected_move, battle_config, opponent_card)
    await ai_damage_calculation(battle_config, damage_calculation_response)
    return battle_msg


async def player_move_embed(ctx, battle_config, private_channel, battle_msg):
    """
    Show the battle screen for a human's turn.

    Returns (battle message, custom_ids to wait for).
    """
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    await start_of_moves_config(battle_config)
    # Per-turn move values (WAVE/CREATION/BLAST/DESTRUCTION, DRACONIC) were
    # updated by the old card render at this point; keep doing it, then
    # rebuild the buttons so they show the values for this turn.
    battle_view.refresh_move_values(turn_card, battle_config.turn_total)
    battle_config.set_battle_options(turn_card, opponent_card, partner_card)

    if battle_config.is_co_op_mode:
        partner_card.set_battle_arm_messages(opponent_card)
        partner_card.set_stat_icons()
        if turn_card.stamina < 20:
            battle_config.co_op_buttons = []

    turn_card.set_battle_arm_messages(opponent_card)
    turn_card.set_stat_icons()

    tutorial_text = battle_config.get_tutorial_message(turn_card) if battle_config.is_tutorial_game_mode else None
    image_bytes, image_name, announcement = await battle_view.render_scene(battle_config)
    container, listen = battle_view.human_turn_view(battle_config, turn_card, tutorial_text, image_name, announcement)
    battle_msg = await show_battle_view(private_channel, battle_msg, container, image_bytes, image_name)
    return battle_msg, listen


async def player_move_handler(battle_config, private_channel, button_ctx, battle_msg):
    """
    Resolves the move behind the button the player pressed.

    At some point tutorial messages can be moved to handler
    """
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    move = str(button_ctx.ctx.custom_id).split('|')[-1]

    async def tutorial_tip(flag, message_type):
        if battle_config.is_tutorial_game_mode and getattr(battle_config, flag) == False:
            setattr(battle_config, flag, True)
            embedVar = battle_config.tutorial_messages(turn_card, opponent_card, message_type)
            if embedVar:
                await private_channel.send(embed=embedVar)

    if move in ("q", "Q"):
        return

    if move in ("1", "2", "3", "4"):
        if battle_config.is_turn == 1:
            await player_boss_message_ability_use(battle_config, private_channel, button_ctx)
        damage_calculation_response = turn_card.damage_cal(int(move), battle_config, opponent_card)
        await tutorial_tip({"1": "tutorial_basic", "2": "tutorial_special", "3": "tutorial_ultimate", "4": "tutorial_enhancer"}[move],
                           {"1": "BASIC", "2": "SPECIAL", "3": "ULTIMATE", "4": "ENHANCER"}[move])
        await player_damage_calculation(battle_config, button_ctx, damage_calculation_response)
        return

    if move == "6":
        await player_use_summon_ability(battle_config, private_channel, button_ctx, battle_msg)
        await tutorial_tip("tutorial_summon", "SUMMON")
        return

    if move == "5":
        await player_use_resolve(battle_config, private_channel, button_ctx, battle_msg)
        await tutorial_tip("tutorial_resolve", "RESOLVE")
        return

    if move == "0":
        await player_use_block_ability(battle_config, private_channel, button_ctx, battle_msg)
        await tutorial_tip("tutorial_block", "BLOCK")
        return

    if move == "b":
        await player_use_blitz_ability(battle_config, private_channel, button_ctx, battle_msg)
        await tutorial_tip("tutorial_blitz", "BLITZ")
        return

    if move == "bleach":
        await second_release(turn_card, opponent_card, battle_config)
        return

    if battle_config.is_co_op_mode:
        if move == "7":
            turn_card.use_companion_enhancer(battle_config, opponent_card, partner_card)
            return

        if move == "8":
            # Use companion enhancer on you
            partner_card.use_companion_enhancer(battle_config, opponent_card, turn_card)
            return

        if move == "9":
            partner_card.use_block(battle_config, opponent_card, turn_card)
            return

    # A button this battle does not know about: ignore it, the player keeps the turn.
    loggy.warning(f"Unhandled battle button '{button_ctx.ctx.custom_id}'")


async def player_use_resolve(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    # Resolve Check and Calculation
    if not turn_card.used_resolve and turn_card.used_focus:
        await turn_card.resolving(battle_config, turn_title, opponent_card, turn_player)
        if battle_config.is_boss_game_mode and battle_config._boss_embed_message:
            await private_channel.send(embed=battle_config._boss_embed_message)


async def player_use_summon_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    summon_response = turn_card.usesummon(battle_config, opponent_card)
    if not summon_response or not summon_response.get('CAN_USE_MOVE'):
        return      # the summon is resting; the battle log already says so
    if turn_player.performance or battle_config.is_auto_battle_game_mode:
        return

    image_binary = await render_cache.render_async(
        crown_utilities.showsummon, turn_card.summon_image, turn_card.summon_name, summon_response['MESSAGE'],
        turn_card.summon_lvl, turn_card.summon_bond, universe=turn_card.summon_universe,
        ability=turn_card.summon_ability_name, ability_type=turn_card.summon_type, power=turn_card.summon_power,
    )
    try:
        image_bytes = image_binary.getvalue()
    finally:
        image_binary.close()

    container = battle_view.summon_view(battle_config, turn_card, summon_response.get('MESSAGE'))
    try:
        await battle_msg.edit(components=[container], file=battle_view.scene_file(image_bytes, battle_view.SUMMON_FILE))
        await asyncio.sleep(SUMMON_READ_DELAY)
    except HTTPException as ex:
        loggy.warning(f"Could not show the summon splash: {ex}")


async def player_use_block_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    turn_card.use_block(battle_config, opponent_card, partner_card)
    return True


async def player_use_blitz_ability(battle_config, private_channel, button_ctx, battle_msg):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    turn_card.use_blitz(battle_config, opponent_card)
    return True


async def player_boss_message_ability_use(battle_config, private_channel, button_ctx):
    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)

    if button_ctx.ctx.custom_id == f"{battle_config._uuid}|5":
        if not turn_card.used_resolve and turn_card.used_focus:
            if battle_config.is_boss_game_mode and battle_config._boss_embed_message:
                await private_channel.send(embed=battle_config._boss_embed_message)

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

    if not damage_calculation_response:
        # The move could not be worked out (an error inside the damage formula).
        # Use up the turn instead of crashing the battle.
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {turn_card.name}'s move had no effect")
        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return

    turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
    if turn_card._blood_demon_art:
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {turn_card.name}'s Blood Demon Art -  Double Strike!")
        turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        turn_card._blood_demon_art = False
    elif turn_card._monstrosity_active and turn_card.used_resolve:
        turn_card._monstrosity_value = turn_card._monstrosity_value - 1
        if turn_card._monstrosity_value <= 0:
            turn_card._monstrosity_active = False
            turn_card._monstrosity_value = 0
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {turn_card.name}:  Double Strike! {turn_card._monstrosity_value} Double Strikes Left!")
        turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        if souls_third_phase(turn_card,battle_config):
            damage_calculation_response = turn_card.damage_cal("Souls", battle_config, opponent_card)
            if damage_calculation_response:
                turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        battle_config.next_turn()
    elif souls_third_phase(turn_card,battle_config):
        damage_calculation_response = turn_card.damage_cal("Souls", battle_config, opponent_card)
        if damage_calculation_response:
            turn_card.damage_done(battle_config, damage_calculation_response, opponent_card)
        battle_config.next_turn()
    else:
        battle_config.next_turn()


# This is an asynchronous function used to handle the end of the game for a player. The function 
# saves the player's game status and then ends the game.  Returns True when the game was saved
# and the battle should stop.
async def player_save_and_end_game(self, ctx, private_channel, battle_msg, battle_config, button_ctx):
    if button_ctx.ctx.custom_id != f"{battle_config._uuid}|s":
        return False

    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    try:
        release_player(turn_player)
        battle_config.game_over = True
        await gs.save_spot(self, turn_player, battle_config.selected_universe, battle_config.mode, battle_config.current_opponent_number)
        await safe_delete(battle_msg)
        await private_channel.send(embed=battle_config.saved_game_embed(turn_card, opponent_card, partner_card))
    except Exception as ex:
        custom_logging.debug(ex)
    return True

# This is an asynchronous function used to handle a player quitting the game. The function sets the 
# health of the player's card to 0, marks the game as over, and logs the event.  Returns True when
# the player surrendered and the battle should stop.
async def player_quit_and_end_game(ctx, private_channel, battle_msg, battle_config, button_ctx):
    if button_ctx.ctx.custom_id not in (f"{battle_config._uuid}|q", f"{battle_config._uuid}|Q"):
        return False

    if battle_config.is_rpg and getattr(battle_config, "rpg_config", None) is not None:
        battle_config.rpg_config.adventuring = True
        battle_config.rpg_config.battling = False
        battle_config.rpg_config.encounter = False
        battle_config.rpg_config.player_health = battle_config.player1_card.health
        await safe_delete(battle_msg)
        battle_config.rpg_config.previous_moves.append(f"💨Fleeing Encounter...Resuming Adventure...!")
        return True

    turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title, opponent_arm, partner_player, partner_card, partner_title, partner_arm = crown_utilities.get_battle_positions(battle_config)
    try:
        release_player(turn_player)
        turn_card.health = 0
        battle_config.game_over = True
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) **{turn_card.name}** quit the battle. The match is over.")
        await safe_delete(battle_msg)
        await exit_battle_embed(battle_config, button_ctx, private_channel)
    except Exception as ex:
        custom_logging.debug(ex)
    return True




def setup(bot):
    Play(bot)
