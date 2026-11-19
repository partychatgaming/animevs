"""The battle message: one Components V2 container per turn.

    ┌ accent = health colour of the fighter whose turn it is ─────────────┐
    │ ### Naruto's move                                                   │
    │ -# Turn 12 · Tales                                                  │
    │ [ battle scene image: both fighters, HP/ST bars, ATK/DEF, effects ] │
    │ -# (11) Sasuke used Chidori for 1,240 damage                        │
    │ (12) Naruto focused and recovered 90 stamina                        │
    │ ─────────────────────────────────────────────────────────────────── │
    │ [🔥 Rasengan · 10] [💨 Shadow Clone · 30] [🌀 Sage Art · 80] [🦠 …] │
    │ [🛡️ Block · 20] [⚡ Resolve!] [⚙️ More]                             │
    └─────────────────────────────────────────────────────────────────────┘

"More" opens a private (ephemeral) panel with the full kit (talisman, arm,
title, summon, universe stacks, both sides), the longer battle log, and the
Save & quit / Surrender actions.  Surrender asks to confirm.

Everything here only *presents* state: the battle rules live in battle_class /
card_class and are untouched, apart from ``refresh_move_values`` which keeps a
side effect the old per-turn card render used to perform (see its docstring).
"""
from io import BytesIO

from interactions import (ActionRow, Button, ButtonStyle, ContainerComponent, File, MediaGalleryComponent,
                          MediaGalleryItem, SeparatorComponent, TextDisplayComponent)

import battle_scene
import crown_utilities
import custom_logging
import render_cache

SCENE_FILE = "battle.jpg"
SUMMON_FILE = "summon.png"
TEXT_LIMIT = 4000          # Discord: total characters of text in one V2 message
LOG_LINES_ON_SCREEN = 3
LOG_LINES_IN_PANEL = 15

MODE_NAMES = {
    "EXPLORE": "Explore", "SCENARIO": "Scenario", "RAID": "Raid", "ABYSS": "Abyss", "TUTORIAL": "Tutorial",
    "PVP": "PvP", "BOSS": "Boss", "RPG": "Adventure", "DUNGEON": "Dungeon", "TALES": "Tales",
}


# --------------------------------------------------------------------------- ids
def more_id(battle_config):
    return f"{battle_config._uuid}|more"


def surrender_ask_id(battle_config):
    return f"{battle_config._uuid}|surrender_ask"


def cancel_id(battle_config):
    return f"{battle_config._uuid}|panel_close"


def save_id(battle_config):
    return f"{battle_config._uuid}|s"


def surrender_id(battle_config):
    return f"{battle_config._uuid}|Q"


def panel_ids(battle_config):
    """Buttons that open / work the More panel.  They never use up the turn."""
    return {more_id(battle_config), surrender_ask_id(battle_config), cancel_id(battle_config)}


def end_ids(battle_config):
    """Buttons that end the session from the More panel (handled by play.py)."""
    return {save_id(battle_config), surrender_id(battle_config)}


# --------------------------------------------------------------------------- state helpers
def refresh_move_values(card, turn_total):
    """Advance the per-turn move values exactly as the old card render did.

    ``Card.showcard`` was called once per turn for the card about to act, and
    besides drawing it recalculated WAVE / CREATION / BLAST / DESTRUCTION
    enhancer power and DRACONIC ultimate power (and trimmed long move names).
    The battle screen no longer draws that card, so the same calculation is run
    here, at the same moment in the turn, to keep the numbers identical.
    """
    try:
        if card is None or card.health <= 0:
            return              # showcard returned before these steps for a defeated card
        from cogs.classes.card_class import calculate_move_text_and_font_sizes
        card.get_evasion()
        calculate_move_text_and_font_sizes(card, turn_total, "", "", "")
    except Exception as ex:
        custom_logging.debug(ex)


def scene_positions(battle_config):
    """(left card, right card, left ally, active) for the current turn.

    The player's side is always on the left and the opponent on the right, so
    nothing swaps places between turns; the gold ring shows who is acting.
    """
    left = battle_config.player1_card
    right = battle_config.player2_card
    ally = battle_config.player3_card if (battle_config.is_co_op_mode or battle_config.is_duo_mode) else None
    active = {0: "left", 1: "right", 2: "left_ally" if ally is not None else "left", 3: "right"}.get(battle_config.is_turn, None)
    return left, right, ally, active


async def render_scene(battle_config):
    """PNG/JPEG bytes of the battle scene for the current state (never raises)."""
    left, right, ally, active = scene_positions(battle_config)
    left_snap = battle_scene.snapshot(left, right)
    right_snap = battle_scene.snapshot(right, left)
    ally_snap = battle_scene.snapshot(ally, right) if ally is not None else None
    out = await render_cache.render_async(battle_scene.render, left_snap, right_snap,
                                          turn_total=battle_config.turn_total, active=active, left_ally=ally_snap)
    try:
        return out.getvalue()
    finally:
        out.close()


def scene_file(image_bytes, name=SCENE_FILE):
    return File(file_name=name, file=BytesIO(image_bytes))


# --------------------------------------------------------------------------- text pieces
def mode_name(battle_config):
    mode = str(getattr(battle_config, "mode", "") or "")
    for key, label in MODE_NAMES.items():
        if key in mode.upper():
            return label
    return mode.title() if mode else ""


def _one_line(text):
    return " ".join(str(text).split())


def log_entries(battle_config, count):
    moves = list(getattr(battle_config, "previous_moves", None) or [])
    if not moves:
        return []
    try:
        moves = crown_utilities.replace_matching_numbers_with_arrow(moves)
    except Exception:
        pass
    return [_one_line(m) for m in moves[-count:] if str(m).strip()]


def recent_log_text(battle_config, count=LOG_LINES_ON_SCREEN, limit=900):
    """Last few log lines: older ones small, the newest at normal size."""
    entries = log_entries(battle_config, count)
    if not entries:
        return "-# The battle begins!"
    per_line = max(60, limit // len(entries))
    lines = [f"-# {crown_utilities.clip(e, per_line)}" for e in entries[:-1]]
    lines.append(crown_utilities.clip(entries[-1], per_line))
    return "\n".join(lines)


def header_text(battle_config, card, acting_human=True, extra=None):
    name = getattr(card, "name", "")
    title = f"### {name}'s move" if acting_human else f"### {name} is making a move…"
    sub = []                    # the turn number is on the image
    mode = mode_name(battle_config)
    if mode:
        sub.append(mode)
    summon_msg = str(getattr(card, "summon_resolve_message", "") or "").strip()
    if summon_msg:
        sub.append(summon_msg.replace("|", "").strip())
    text = f"{title}\n-# {' · '.join(sub)}" if sub else title
    if extra:
        text += f"\n{extra}"
    return text


# --------------------------------------------------------------------------- containers
def battle_container(header, log_text, rows, accent, image_name=SCENE_FILE):
    parts = [
        TextDisplayComponent(crown_utilities.clip(header, 1500)),
        MediaGalleryComponent([MediaGalleryItem(f"attachment://{image_name}")]),
        TextDisplayComponent(crown_utilities.clip(log_text, 1500)),
    ]
    if rows:
        parts.append(SeparatorComponent(divider=True))
        parts.extend(rows)
    return ContainerComponent(*parts, accent_color=accent)


def move_rows(battle_config):
    """Action rows for the human's turn (rules come from set_battle_options)."""
    moves = list(battle_config.battle_buttons or [])
    utility = list(battle_config.utility_buttons or [])
    co_op = list(battle_config.co_op_buttons or [])
    utility.append(Button(style=ButtonStyle.GREY, label="More", emoji="⚙️", custom_id=more_id(battle_config)))
    rows = [ActionRow(*r) for r in crown_utilities.chunk_buttons(moves)]
    rows += [ActionRow(*r) for r in crown_utilities.chunk_buttons(co_op)]
    rows += [ActionRow(*r) for r in crown_utilities.chunk_buttons(utility)]
    return rows


def listen_ids(rows, battle_config):
    """custom_ids the turn waits on: every enabled button plus the panel's."""
    ids = []
    for row in rows:
        for component in getattr(row, "components", []) or []:
            custom_id = getattr(component, "custom_id", None)
            if custom_id and not getattr(component, "disabled", False):
                ids.append(custom_id)
    extra = panel_ids(battle_config) | {surrender_id(battle_config)}
    if getattr(battle_config, "can_save_battle", False):
        extra.add(save_id(battle_config))
    ids += sorted(extra)
    return ids


def human_turn_view(battle_config, turn_card, tutorial_text=None):
    rows = move_rows(battle_config)
    extra = f"-# 🧠 **Tutorial task:** {_one_line(tutorial_text)}" if tutorial_text else None
    container = battle_container(header_text(battle_config, turn_card, True, extra), recent_log_text(battle_config),
                                 rows, turn_card.health_color)
    return container, listen_ids(rows, battle_config)


def ai_turn_view(battle_config, turn_card):
    return battle_container(header_text(battle_config, turn_card, False), recent_log_text(battle_config), [],
                            turn_card.health_color)


def summon_view(battle_config, turn_card, summon_message):
    name = getattr(turn_card, "summon_name", "Summon")
    header = f"### 🧬 {name} answers the call!\n-# Turn {battle_config.turn_total}"
    return battle_container(header, crown_utilities.clip(_one_line(summon_message or ""), 1500) or recent_log_text(battle_config),
                            [], 0xE74C3C, image_name=SUMMON_FILE)


# --------------------------------------------------------------------------- More panel
def _kit_lines(card, title=None):
    lines = []
    try:
        if getattr(card, "is_tactician", False) and getattr(card, "_tactician_stack_5", False):
            lines.append("🥋 Ultimate Strategy")
        elif getattr(card, "is_tactician", False) and getattr(card, "_tactician_stack_3", False):
            lines.append("🥋 Tactician's Talisman")
        else:
            talisman = str(getattr(card, "_talisman", "") or "")
            if talisman and talisman.upper() != "NULL":
                lines.append(f"{crown_utilities.set_emoji(talisman)} {talisman.title()} Talisman")
        arm = _one_line(getattr(card, "_arm_message", "") or "")
        if arm:
            lines.append(arm)
        if title is not None:
            title_text = title.title_battle_message_handler() if hasattr(title, "title_battle_message_handler") else ""
            if title_text:
                lines.append(_one_line(title_text))
        if card.universe in crown_utilities.universe_stack_traits:
            lines.append(f"{card.universe_crest} {card.universe_trait_value_name}: {card.universe_trait_value}")
        if card.used_resolve or card.card_class == "SUMMONER":
            lines.append(f"🧬 {card.summon_name}: {card.summon_emoji}{str(card.summon_type).title()} Ability - {card.summon_power}")
    except Exception as ex:
        custom_logging.debug(ex)
    return lines


def _move_lines(card):
    try:
        suffix = crown_utilities.enhancer_suffix_mapping.get(card.move4enh, "")
        return [
            f"{card.move1_emoji} **{card.move1}** · {card.move1ap} AP · 10 ST",
            f"{card.move2_emoji} **{card.move2}** · {card.move2ap} AP · 30 ST",
            f"{card.move3_emoji} **{card.move3}** · {card.move3ap} AP · 80 ST",
            f"🦠 **{card.move4}** · {str(card.move4enh).title()} {card.move4ap}{suffix} · 20 ST",
        ]
    except Exception as ex:
        custom_logging.debug(ex)
        return []


def more_panel(battle_config):
    """Private panel: full kit for both sides, longer log, Save & quit, Surrender."""
    positions = crown_utilities.get_battle_positions(battle_config)
    (turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title,
     opponent_arm, partner_player, partner_card, partner_title, partner_arm) = positions

    sections = [f"### 🎒 {turn_card.name}"]
    sections += _move_lines(turn_card)
    sections += _kit_lines(turn_card, turn_title)
    if (battle_config.is_co_op_mode or battle_config.is_duo_mode) and partner_card is not None and partner_card is not turn_card:
        sections.append(f"### 🤝 {partner_card.name}")
        sections += _kit_lines(partner_card, partner_title)
    sections.append(f"### 🎴 {opponent_card.name}")
    sections += _kit_lines(opponent_card, opponent_title) or ["-# Nothing equipped"]
    kit_text = "\n".join(sections)

    log = log_entries(battle_config, LOG_LINES_IN_PANEL)
    log_text = "### 📜 Battle log\n" + ("\n".join(f"-# {e}" for e in log) if log else "-# Nothing has happened yet.")
    room = TEXT_LIMIT - 200
    kit_text = crown_utilities.clip(kit_text, room // 2)
    log_text = crown_utilities.clip_tail(log_text, room - len(kit_text))

    buttons = []
    if getattr(battle_config, "can_save_battle", False):
        buttons.append(Button(style=ButtonStyle.GREY, label="Save & quit", emoji="💾", custom_id=save_id(battle_config)))
    buttons.append(Button(style=ButtonStyle.RED, label="Surrender", emoji="🏳️", custom_id=surrender_ask_id(battle_config)))
    return ContainerComponent(
        TextDisplayComponent(kit_text),
        SeparatorComponent(divider=True),
        TextDisplayComponent(log_text),
        SeparatorComponent(divider=True),
        ActionRow(*buttons),
        accent_color=turn_card.health_color,
    )


def surrender_confirm_panel(battle_config):
    if battle_config.is_rpg:
        text = "### 🏳️ Flee this encounter?\nYou'll return to your adventure."
    else:
        text = "### 🏳️ Surrender?\nThe match ends as a loss."
    return ContainerComponent(
        TextDisplayComponent(text),
        ActionRow(
            Button(style=ButtonStyle.RED, label="Surrender", custom_id=surrender_id(battle_config)),
            Button(style=ButtonStyle.GREY, label="Keep fighting", custom_id=cancel_id(battle_config)),
        ),
        accent_color=0xE74C3C,
    )


def notice_panel(text, accent=0x5865F2):
    return ContainerComponent(TextDisplayComponent(text), accent_color=accent)
