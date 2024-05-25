import textwrap
import crown_utilities
from cogs.universe_traits.my_hero_academia import activate_my_hero_academia_trait
from cogs.universe_traits.demon_slayer import activate_demon_slayer_trait
from cogs.universe_traits.one_piece import observation_haki
from cogs.universe_traits.chainsawman import devilization
from cogs.universe_traits.solo_leveling import set_solo_leveling_config, activate_solo_leveling_trait
import db
import dataclasses as data
import messages as m
import numpy as np
import unique_traits as ut
import help_commands as h
import uuid
import asyncio
import random
import re
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Tactics(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Tactics Cog is ready!')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
        

def tactics_set_base_stats(boss_card):
    boss_card.max_base_health = boss_card.max_health


def tactics_petrified_fear_check(boss_card, player_card, battle_config):
    if boss_card.petrified_fear and boss_card.petrified_fear_counter < boss_card.petrified_fear_turns:
        boss_card.petrified_fear_counter = boss_card.petrified_fear_counter + 1
        battle_config.is_turn = 1
        petrified_fear_message = f"(🆚) [{player_card.name} is petrified with fear and cannot move for [{str((boss_card.petrified_fear_turns - boss_card.petrified_fear_counter) + 1)}] turns]"
        battle_config.add_to_battle_log(petrified_fear_message)
        return True
    else:
        return False


def tactics_bloodlust_check(boss_card, battle_config):
    if boss_card.bloodlust:
        if not boss_card.bloodlust_activated:
            if boss_card.health <= (0.75 * boss_card.max_base_health):
                print("bloodlust check")
                boss_card.bloodlust_activated = True
                boss_card.attack = boss_card.attack + 3000
                bloodlust_message = f"(🆚) [{boss_card.name} is bloodlusted. Attacks will now lifesteal]"
                battle_config.add_to_battle_log(bloodlust_message)


def tactics_enrage_check(boss_card, battle_config):
    if boss_card.enraged:
        if not boss_card.enrage_activated:
            if boss_card.health <= (0.50 * boss_card.max_base_health):
                boss_card.enrage_activated = True
                boss_card.attack = boss_card.attack + 9999
                boss_card.defense = boss_card.defense + 1000
                boss_card.arbitrary_ap_buff = boss_card.arbitrary_ap_buff + 600
                boss_card.max_health = boss_card.max_health + 10000
                boss_card.stamina = 260
                enrage_message = f"(🆚) [{boss_card.name} is enraged! Attacks will now deal much more damage to the enemy]"
                battle_config.add_to_battle_log(enrage_message)


def tactics_intimidation_check(boss_card, player_card, battle_config):
    if boss_card.intimidation:
        if not boss_card.intimidation_activated:
            if boss_card.health <= (0.50 * boss_card.max_base_health):
                boss_card.intimidation_activated = True
                player_card.temporary_attack = player_card.attack
                player_card.temporary_defense = player_card.defense
                player_card.attack = 0
                player_card.defense = 0
        if boss_card.intimidation_activated:
            if boss_card.intimidation_turns > 0:
                boss_card.intimidation_turns = boss_card.intimidation_turns - 1
                player_card.attack = 0
                player_card.defense = 0
                intimidation_message = f"(🆚) [{player_card.name} is intimidated by {boss_card.name} for {str(boss_card.intimidation_turns + 1)} turns\n{player_card.name}'s Attack and Defense are booth 0 out of fear]"
                battle_config.add_to_battle_log(intimidation_message)
            else:
                player_card.attack = player_card.temporary_attack
                player_card.defense = player_card.temporary_defense
                boss_card.intimidation_activated = False
                boss_card.intimidation = False
                boss_card.intimidation_counter = 0
                intimidation_message = f"(🆚) [{player_card.name} is no longer intimidated by {boss_card.name}\n{player_card.name}'s Attack and Defense is restored]"
                battle_config.add_to_battle_log(intimidation_message)


def tactics_damage_check(boss_card, battle_config):
    if boss_card.damage_check:
        if not boss_card.damage_check_activated:
            if boss_card.focus_count in [3]:
                boss_card.damage_check_activated = True
                boss_card.damage_check_limit = round(boss_card.max_health * .10)
                boss_card.damage_check_turns = round(random.randint(3, 6))
        if boss_card.damage_check_activated:
            battle_config.is_turn = 0
            battle_config.add_to_battle_log(f"(🆚) [{boss_card.name} Damage Check\nDamage Dealt [{str(boss_card.damage_check_counter)} / {str(boss_card.damage_check_limit)}]\n[{str(boss_card.damage_check_turns)}] turns to go]")


def tactics_regeneration_check(boss_card, battle_config):
    if boss_card.regeneration:
        if not boss_card.regeneration_activated:
            if battle_config.turn_total >= 50 and boss_card.health <= 0:
                battle_config.game_over_check = False
                boss_card.regeneration_activated = True
                boss_card.health = boss_card.max_base_health
                regeneration_message = f"(🆚) [{boss_card.name} has regenerated]"
                battle_config.add_to_battle_log(regeneration_message)


def tactics_death_blow_check(boss_card, player_card, battle_config):
    if boss_card.death_blow:
        if battle_config.turn_total in [10,30, 60, 90, 120, 150, 180, 200, 220, 240, 250]:
            boss_card.death_blow_activated = True

        if battle_config.turn_total in [9,10,29,30, 59,60, 89, 90, 119, 120, 149, 150, 179, 180,  199, 200, 219, 220, 239, 240,  249, 250]:
            #sif battle_config.is_turn in [0,2]:
            warning_message = f"(🆚) [{boss_card.name} is preparing a death blow. Protect yourself with shields, parries, barriers, or block]"
            battle_config.add_to_battle_log(warning_message)

        if boss_card.death_blow_activated and battle_config.is_turn in [1,3]:
            if any({player_card.shield_active, player_card.parry_active, player_card.barrier_active, player_card.used_block}):
                player_card.shield_active = False
                player_card.parry_active = False
                player_card.barrier_active = False
                player_card._shield_value = 0
                player_card._parry_value = 0
                player_card._barrier_value = 0
                player_card._arm_message = ""
                death_blow_message = f"(🆚) [{boss_card.name} destroyed {player_card.name} protections with a destructive blow!]"
                if player_card.used_block:
                    player_card.used_block = False
                    player_card.defense = player_card.defense - (player_card.defense * 0.25)
                    death_blow_message = f"(🆚) [{player_card.name} blocked a destructive blow, but lost some defense in the process]"
                battle_config.add_to_battle_log(death_blow_message)
                boss_card.death_blow_activated = False
            else:
                player_card.health = 0
                death_blow_message = f"(🆚) [{boss_card.name} dealt a fatal blow to {player_card.name}]"
                battle_config.add_to_battle_log(death_blow_message)
                boss_card.death_blow_activated = False


def tactics_stagger_check(boss_card, player_card, battle_config):
    if boss_card.stagger:
        if boss_card.stagger_activated:
            battle_config.is_turn = 1
            stagger_message = f"(🆚) [{player_card.name} is staggered and cannot move]"
            battle_config.add_to_battle_log(stagger_message)
            boss_card.stagger_activated = False


def tactics_almighty_will_check(boss_card, battle_config):
    if boss_card.almighty_will:
        if battle_config.turn_total in boss_card.almighty_will_turns:
            battle_config.is_turn = random.randint(3, 80)
            boss_card.focus_count = random.randint(3, 30)
            almighty_will_message = f"(🆚) [⏳ {boss_card.name} manipulated the flow of battle\nIt is now turn {str(battle_config.is_turn)} and {boss_card.name} has focused {str(boss_card.focus_count)} times]"
            battle_config.add_to_battle_log(almighty_will_message)


def beginning_of_turn_stat_trait_affects(player_card, player_title, opponent_card, battle_config, companion = None):
    #If any damage happened last turn that would kill
    player_card.reset_stats_to_limiter(opponent_card)
    battle_config.add_to_battle_log(player_card.set_poison_hit(opponent_card))
    burn_turn = player_card.set_burn_hit(opponent_card)
    if burn_turn != None:
        battle_config.add_to_battle_log(player_card.set_burn_hit(opponent_card))
    battle_config.add_to_battle_log(player_card.set_bleed_hit(battle_config.turn_total, opponent_card))
    player_card.damage_dealt = round(player_card.damage_dealt)
    opponent_card.damage_dealt = round(opponent_card.damage_dealt)
    player_card.damage_healed = round(player_card.damage_healed)
    opponent_card.damage_healed = round(opponent_card.damage_healed)
    activate_my_hero_academia_trait(player_card)
    activate_my_hero_academia_trait(opponent_card)

    devilization(player_card, battle_config)
    devilization(opponent_card, battle_config)
    if opponent_card.freeze_enh:
        new_turn = player_card.frozen(battle_config, opponent_card)
        battle_config.is_turn = new_turn['TURN']
        battle_config.add_to_battle_log(new_turn['MESSAGE'])
        
        if player_card.ice_duration > 0:
            player_card.ice_duration = player_card.ice_duration - 1

        if player_card.ice_duration == 0:
            opponent_card.freeze_enh = False
    
    player_card.set_gravity_hit()
    if not opponent_card.wind_element_activated:
        player_title.activate_title_passive(battle_config, player_card, opponent_card)
    opponent_card.wind_element_activated = False
    
    activate_demon_slayer_trait(player_card, battle_config, opponent_card)
    activate_demon_slayer_trait(opponent_card, battle_config, player_card)

    observation_haki(player_card, battle_config, opponent_card)
    observation_haki(opponent_card, battle_config, player_card)

    set_solo_leveling_config(player_card, opponent_card.shield_active, opponent_card._shield_value, opponent_card.barrier_active, opponent_card._barrier_value, opponent_card.parry_active, opponent_card._parry_value)
    set_solo_leveling_config(opponent_card, player_card.shield_active, player_card._shield_value, player_card.barrier_active, player_card._barrier_value, player_card.parry_active, player_card._parry_value)


    if companion:
        activate_my_hero_academia_trait(companion)
        companion.reset_stats_to_limiter(opponent_card)
        devilization(companion, battle_config)
        activate_demon_slayer_trait(companion, battle_config, opponent_card)
        observation_haki(companion, battle_config, opponent_card)
        set_solo_leveling_config(companion, opponent_card.shield_active, opponent_card._shield_value, opponent_card.barrier_active, opponent_card._barrier_value, opponent_card.parry_active, opponent_card._parry_value)

        if companion.used_block == True:
            companion.defense = int(companion.defense / 2)
            companion.used_block = False
        if companion.used_defend == True:
            companion.defense = int(companion.defense / 2)
            companion.used_defend = False
        
    if player_card.used_block == True:
        player_card.defense = int(player_card.defense / 2)
        player_card.used_block = False
    if player_card.used_defend == True:
        player_card.defense = int(player_card.defense / 2)
        player_card.used_defend = False
    return False


async def auto_battle_embed_and_starting_traits(ctx, player_card, player_title, opponent_card, opponent_title, battle_config, companion_card=None, companion_title=None):
    player_card.set_battle_arm_messages(opponent_card)
    player_card.set_stat_icons()

    activate_solo_leveling_trait(player_card, battle_config, opponent_card)
            
    embedVar = Embed(title=f"➡️ Current Turn {battle_config.turn_total}", color=0xe74c3c)
    await asyncio.sleep(2)
    embedVar.set_thumbnail(url=ctx.author.avatar_url)
    footer_text = battle_config.get_battle_author_text(opponent_card, opponent_title, player_card, player_title, companion_card, companion_title)
    # footer_text = battle_config.get_battle_window_title_text(player_card,opponent_card)
    embedVar.set_author(name=f"{player_card.summon_resolve_message}\n{footer_text}")
    embedVar.set_footer(
        text=f"{battle_config.get_previous_moves_embed()}")

    if not battle_config.is_auto_battle_game_mode:
        embedVar.set_image(url="attachment://image.png")
    return embedVar



def setup(bot):
    Tactics(bot)
              