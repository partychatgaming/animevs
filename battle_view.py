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

import battle_fx
import battle_scene
import crown_utilities
import custom_logging
import render_cache

SCENE_FILE = "battle.jpg"
POWER_UP_FILE = "battle.gif"
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


_RANK = {"normal": 0, "focus": 1, "resolve": 2}


def power_ups(battle_config, sides):
    """Which sides just entered Focus or Resolve since the last screen.

    ``sides`` maps "left"/"right" to (card, snapshot).  States are remembered
    per card object, so a new opponent in the next match starts fresh.
    """
    seen = getattr(battle_config, "_scene_fx_states", None)
    if seen is None:
        seen = {}
        try:
            battle_config._scene_fx_states = seen
        except Exception:
            pass
    changed = {}
    for side, (card, snap) in sides.items():
        if card is None or snap is None:
            continue
        state = battle_fx.state_of(snap)
        before = seen.get(id(card), "normal")
        if _RANK[state] > _RANK.get(before, 0):
            changed[side] = state
        seen[id(card)] = state
    return changed


def power_up_text(changed, snaps):
    lines = []
    for side, state in changed.items():
        name = snaps[side]["name"]
        lines.append(f"## ⚡ {name} has RESOLVED!" if state == "resolve" else f"### 💖 {name} enters Focus!")
    return "\n".join(lines)


async def render_scene(battle_config):
    """Battle scene for the current state: (image bytes, file name, announcement text).

    On the screen right after a fighter enters Focus or Resolve, the image is a
    short animated GIF of the power-up (it plays once and holds on the final
    frame); otherwise a still JPEG.  Never raises.
    """
    left, right, ally, active = scene_positions(battle_config)
    left_snap = battle_scene.snapshot(left, right)
    right_snap = battle_scene.snapshot(right, left)
    ally_snap = battle_scene.snapshot(ally, right) if ally is not None else None
    snaps = {"left": left_snap, "right": right_snap}
    changed = power_ups(battle_config, {"left": (left, left_snap), "right": (right, right_snap)})
    if changed:
        out, ext = await render_cache.render_async(battle_scene.render_power_up, left_snap, right_snap, changed,
                                                   turn_total=battle_config.turn_total, active=active, left_ally=ally_snap)
        name = POWER_UP_FILE if ext == "gif" else SCENE_FILE
        announcement = power_up_text(changed, snaps)
    else:
        out = await render_cache.render_async(battle_scene.render, left_snap, right_snap,
                                              turn_total=battle_config.turn_total, active=active, left_ally=ally_snap)
        name, announcement = SCENE_FILE, ""
    try:
        return out.getvalue(), name, announcement
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


def human_turn_view(battle_config, turn_card, tutorial_text=None, image_name=SCENE_FILE, announcement=""):
    rows = move_rows(battle_config)
    extra = [announcement] if announcement else []
    if tutorial_text:
        extra.append(f"-# 🧠 **Tutorial task:** {_one_line(tutorial_text)}")
    container = battle_container(header_text(battle_config, turn_card, True, "\n".join(extra) or None),
                                 recent_log_text(battle_config), rows, turn_card.health_color, image_name=image_name)
    return container, listen_ids(rows, battle_config)


def ai_turn_view(battle_config, turn_card, image_name=SCENE_FILE, announcement=""):
    return battle_container(header_text(battle_config, turn_card, False, announcement or None), recent_log_text(battle_config), [],
                            turn_card.health_color, image_name=image_name)


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


def damage_help_line():
    import damage
    return (f"-# 💥 Damage ≈ move AP × {damage.DAMAGE_SCALE:g}, more when your ATK beats their DEF (up to ×{damage.STAT_FACTOR_MAX:g}), "
            f"less when it doesn't. Strong ×{damage.STRONG:g} · Crit ×{damage.CRITICAL:g} · Weakness ×{damage.WEAKNESS:g} · "
            f"Resist ×{damage.RESISTANCE:g}. One hit can't take more than {round(damage.MAX_HIT_SHARE * 100)}% of max HP.")


def more_panel(battle_config):
    """Private panel: full kit for both sides, longer log, Save & quit, Surrender."""
    positions = crown_utilities.get_battle_positions(battle_config)
    (turn_player, turn_card, turn_title, turn_arm, opponent_player, opponent_card, opponent_title,
     opponent_arm, partner_player, partner_card, partner_title, partner_arm) = positions

    sections = [f"### 🎒 {turn_card.name}"]
    sections += _move_lines(turn_card)
    sections.append(damage_help_line())
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


# --------------------------------------------------------------------------- match start screen
START_FILE = "matchup.jpg"

_RELATIONS = (
    ("weaknesses", "is **weak** to", "✅"),
    ("immunity", "is **immune** to", "🚫"),
    ("repels", "**repels**", "↩️"),
    ("absorbs", "**absorbs**", "💚"),
    ("resistances", "**resists**", "🛡️"),
)


def _elements(values):
    return {str(v).upper() for v in (values or []) if v}


def move_matchups(attacker, defender, limit=4):
    """Lines like '✅ Crablante is weak to 👊 Scissor Punch' for the attacker's three attacks."""
    lines = []
    try:
        for i in (1, 2, 3):
            element = str(getattr(attacker, f"move{i}_element", "") or "").upper()
            name = getattr(attacker, f"move{i}", "")
            if not element:
                continue
            for attr, verb, icon in _RELATIONS:
                if element in _elements(getattr(defender, attr, None)):
                    lines.append(f"{icon} {defender.name} {verb} {crown_utilities.set_emoji(element)} {name}")
                    break
    except Exception as ex:
        custom_logging.debug(ex)
    return lines[:limit]


def affinity_line(card):
    parts = []
    try:
        for attr, label in (("weaknesses", "Weak"), ("resistances", "Resist"), ("immunity", "Immune"),
                            ("repels", "Repel"), ("absorbs", "Absorb")):
            icons = " ".join(crown_utilities.set_emoji(e) for e in (getattr(card, attr, None) or []) if e)
            if icons.strip():
                parts.append(f"{label} {icons}")
    except Exception as ex:
        custom_logging.debug(ex)
    return " · ".join(parts) or "No affinities"


def moves_line(card):
    try:
        suffix = crown_utilities.enhancer_suffix_mapping.get(card.move4enh, "")
        moves = [
            f"{card.move1_emoji} {card.move1} **{card.move1ap}**",
            f"{card.move2_emoji} {card.move2} **{card.move2ap}**",
            f"{card.move3_emoji} {card.move3} **{card.move3ap}**",
            f"🦠 {card.move4} **{str(card.move4enh).title()} {card.move4ap}{suffix}**",
        ]
        return f"{moves[0]} · {moves[1]}\n{moves[2]} · {moves[3]}"
    except Exception as ex:
        custom_logging.debug(ex)
        return ""


def match_label(battle_config):
    """Short label for the scene's centre pill, e.g. 'MATCH 3/22'."""
    if battle_config.is_tutorial_game_mode:
        return "TUTORIAL"
    if battle_config.is_pvp_game_mode:
        return "PVP"
    if battle_config.is_boss_game_mode:
        return "BOSS FIGHT"
    total = int(getattr(battle_config, "total_number_of_opponents", 0) or 0)
    number = int(getattr(battle_config, "current_opponent_number", 0) or 0) + 1
    return f"MATCH {number}/{total}" if total > 1 else "MATCH"


def match_title(battle_config):
    if battle_config.is_tutorial_game_mode:
        return "🧠 Tutorial match"
    if battle_config.is_pvp_game_mode:
        return "⚔️ PvP duel"
    if battle_config.is_boss_game_mode:
        return "👹 Boss fight"
    total = int(getattr(battle_config, "total_number_of_opponents", 0) or 0)
    number = int(getattr(battle_config, "current_opponent_number", 0) or 0) + 1
    return f"⚔️ Match {number} of {total}" if total > 1 else "⚔️ Match"


async def render_matchup(battle_config):
    left, right, ally, _ = scene_positions(battle_config)
    left_snap = battle_scene.snapshot(left, right)
    right_snap = battle_scene.snapshot(right, left)
    ally_snap = battle_scene.snapshot(ally, right) if ally is not None else None
    out = await render_cache.render_async(battle_scene.render_matchup, left_snap, right_snap,
                                          label=match_label(battle_config), left_ally=ally_snap)
    try:
        return out.getvalue()
    finally:
        out.close()


def start_view(battle_config, buttons_row, pings=""):
    """Match start screen: who fights whom, the matchup scene, intel, and Start / Auto / Save / End."""
    you = battle_config.player1_card
    opp = battle_config.player2_card
    partner = battle_config.player3_card if (battle_config.is_co_op_mode or battle_config.is_duo_mode) else None
    where = [mode_name(battle_config)]
    universe = getattr(battle_config, "selected_universe", None) or getattr(opp, "universe", "")
    if universe and str(universe) not in where:
        where.append(str(universe))
    header = f"### {match_title(battle_config)}\n-# {' · '.join(w for w in where if w)}"
    if pings:
        header += f"\n{pings}"

    intel = [f"**🎴 {opp.name}'s moves**", moves_line(opp) or "-# Unknown"]
    yours = move_matchups(you, opp)
    theirs = move_matchups(opp, you)
    if partner is not None:
        yours += [f"-# {partner.name}: " + l for l in move_matchups(partner, opp, 2)]
    intel.append("**⚔️ Your attacks**")
    intel += yours or ["-# No element advantages either way; every move hits normally."]
    intel.append(f"**⚠️ {opp.name}'s attacks**")
    intel += theirs or ["-# Nothing special against you."]
    affinities = [f"-# **You:** {affinity_line(you)}"]
    if partner is not None:
        affinities.append(f"-# **{partner.name}:** {affinity_line(partner)}")
    affinities.append(f"-# **{opp.name}:** {affinity_line(opp)}")

    accent = 0xE74C3C if battle_config.is_boss_game_mode else 0x5865F2
    return ContainerComponent(
        TextDisplayComponent(crown_utilities.clip(header, 600)),
        MediaGalleryComponent([MediaGalleryItem(f"attachment://{START_FILE}")]),
        TextDisplayComponent(crown_utilities.clip("\n".join(intel), 2000)),
        TextDisplayComponent(crown_utilities.clip("\n".join(affinities), 800)),
        SeparatorComponent(divider=True),
        buttons_row,
        accent_color=accent,
    )


def start_banner(battle_config, text):
    """What the start screen collapses to once a choice is made (no image, no buttons)."""
    you, opp = battle_config.player1_card, battle_config.player2_card
    return ContainerComponent(
        TextDisplayComponent(f"**{match_title(battle_config)}:** {you.name} 🆚 {opp.name}\n-# {text}"),
        accent_color=0x95A5A6,
    )
