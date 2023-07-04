import textwrap
import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import unique_traits as ut
import help_commands as h
import uuid
import asyncio
import random
import custom_logging
from .classes.custom_paginator import CustomPaginator
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class Scenario(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Scenario Cog is ready!')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
        
    """
    Creates the embed list for the selected universe
    """
    async def scenario_selector(self, ctx, universe_title, player):
        try:
            scenarios = db.queryAllScenariosByUniverse(universe_title)

            embed_list = []
            for scenario in scenarios:
                embed = create_scenario_embed(scenario, player)
                embed_list.append(embed)

            paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=["Start", "Quit"], paginator_type="Scenario")
            paginator.show_select_menu = True
            await paginator.send(ctx)
        except Exception as ex:
            player.make_available()
            custom_logging.debug(ex)


def create_scenario_embed(scenario, player):
    """
    Instead of must completes, only show scenarios for cards 250 levels above and below your current equipped card level
    """
    try:
        must_complete = scenario['MUST_COMPLETE']
        title = scenario['TITLE']
        image = scenario['IMAGE']
        enemy_level = scenario['ENEMY_LEVEL']
        universe = scenario['UNIVERSE']
        available = scenario['AVAILABLE']
        is_raid = scenario['IS_RAID']
        is_destiny = scenario['IS_DESTINY']
        destiny_cards = scenario['DESTINY_CARDS']
        easy_drops = scenario['EASY_DROPS']
        normal_drops = scenario['NORMAL_DROPS']
        hard_drops = scenario['HARD_DROPS']
        enemies = scenario['ENEMIES']
        number_of_fights = len(enemies)
        completed_scenarios = player.scenario_history
        difficulty = player.difficulty
        scenario_gold = crown_utilities.scenario_gold_drop(enemy_level, number_of_fights, title, completed_scenarios, difficulty)
        rewards, type_of_battle, enemey_level_message, gold_reward_message, difficulty_message = create_scenario_messages(universe, enemy_level, scenario_gold, is_raid, is_destiny, easy_drops, normal_drops, hard_drops, player)
        reward_message = get_scenario_reward_list(rewards)
        
        if (is_destiny and player.equipped_card in destiny_cards) or not is_destiny:
            embedVar = Embed(title= f"{title}", description=textwrap.dedent(f"""
            {type_of_battle}
            {enemey_level_message}
            {gold_reward_message}

            {difficulty_message}

            ⚔️ {str(number_of_fights)}
            """), 
            color=0x7289da)
            embedVar.add_field(name="__**Potential Rewards**__", value=f"{reward_message}")
            embedVar.set_image(url=image)
            # embedVar.set_footer(text=f"")
            return embedVar

    except Exception as ex:
        player.make_available()
        custom_logging.debug(ex)


def create_scenario_messages(universe, enemy_level, scenario_gold, is_raid, is_destiny, easy_drops, normal_drops, hard_drops, player):
    if player.difficulty == "EASY":
        scenario_gold = round(scenario_gold / 5)
        rewards = easy_drops
    
    if player.difficulty == "NORMAL":
        scenario_gold = round(scenario_gold / 2)
        rewards = normal_drops

    if player.difficulty == "HARD":
        scenario_gold = round(scenario_gold * 1.5)
        rewards = hard_drops
    
    type_of_battle = f"📽️ **{universe} Scenario Battle!**"
    enemy_level_message = f"🔱 **Enemy Level:** {enemy_level}"
    gold_reward_message = f"🪙 **Reward** {'{:,}'.format(scenario_gold)}"
    difficulty_message = f"⚙️ **Difficulty:** {player.difficulty.lower().capitalize()}"

    if is_raid:
        type_of_battle = f"<:Raid_Emblem:1088707240917221399> **{universe} RAID BATTLE!**"
        enemy_level_message = f"👹 **NEMESIS LEVEL:** {enemy_level}"
        gold_reward_message = f"<a:Shiney_Gold_Coins_Inv:1085618500455911454> **EARNINGS** {'{:,}'.format(scenario_gold)}"
        difficulty_message = f"<a🔥777975890172837898> **DIFFICULTY:** {player.difficulty.title()}"

    if is_destiny:
        type_of_battle = f"✨ **{universe} RAID BATTLE!**"
        enemy_level_message = f"✨ **NEMESIS LEVEL:** {enemy_level}"
        gold_reward_message = f"<a:Shiney_Gold_Coins_Inv:1085618500455911454> **EARNINGS** {'{:,}'.format(scenario_gold)}"
        difficulty_message = f"✨**DIFFICULTY:** {player.difficulty.title()}"

    return rewards, type_of_battle, enemy_level_message, gold_reward_message, difficulty_message


def get_scenario_reward_list(rewards):
    reward_list = []
     
    for reward in rewards:
        # Add Check for Cards and make Cards available in Easy Drops
        arm = db.queryArm({"ARM": reward})
        if arm:
            arm_name = arm['ARM']
            element_emoji = crown_utilities.set_emoji(arm['ELEMENT'])
            arm_passive = arm['ABILITIES'][0]
            arm_passive_type = list(arm_passive.keys())[0]
            arm_passive_value = list(arm_passive.values())[0]
            if arm_passive_type == "SHIELD":
                reward_list.append(f"🌐 {arm_passive_type.title()} **{arm_name}** Shield: Absorbs **{arm_passive_value}** Damage.")
            elif arm_passive_type == "BARRIER":
                reward_list.append(f"💠  {arm_passive_type.title()} **{arm_name}** Negates: **{arm_passive_value}** attacks.")
            elif arm_passive_type == "PARRY":
                reward_list.append(f"🔁 {arm_passive_type.title()} **{arm_name}** Parry: **{arm_passive_value}** attacks.")
            elif arm_passive_type == "SIPHON":
                reward_list.append(f"💉 {arm_passive_type.title()} **{arm_name}** Siphon: **{arm_passive_value}** + 10% Health.")
            elif arm_passive_type == "MANA":
                reward_list.append(f"🦠 {arm_passive_type.title()} **{arm_name}** Mana: Multiply Enhancer by **{arm_passive_value}**%.")
            elif arm_passive_type == "ULTIMAX":
                reward_list.append(f"〽️ {arm_passive_type.title()} **{arm_name}** Ultimax: Increase all move AP by **{arm_passive_value}**.")
            else:
                reward_list.append(f"{element_emoji} {arm_passive_type.title()} **{arm_name}** Attack: **{arm_passive_value}** Damage.")
        else:
            card = db.queryCard({"NAME": reward})
            senario_only_message = "🌟" if card['DROP_STYLE'] == "SCENARIO" else "" 
            moveset = card['MOVESET']
            move3 = moveset[2]
            move2 = moveset[1]
            move1 = moveset[0]
            basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
            super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
            ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])
            reward_list.append(f"🀄 {card['TIER']} **{card['NAME']}** {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}{senario_only_message}\n❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}")

    reward_message = "\n\n".join(reward_list)
    return reward_message


def setup(bot):
    Scenario(bot)
              