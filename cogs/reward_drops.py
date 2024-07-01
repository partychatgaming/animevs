import textwrap
import crown_utilities
import custom_logging
import db
import dataclasses as data
import messages as m
import numpy as np
import unique_traits as ut
import help_commands as h
import uuid
import asyncio
import random
from logger import loggy
from .quests import Quests
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension

class RewardDrops(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Drops Cog is ready!')


    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)
        

async def scenario_drop(player, scenario, difficulty):
    try:
        scenario_level = scenario["ENEMY_LEVEL"]
        fight_count = len(scenario['ENEMIES'])
        scenario_gold = crown_utilities.scenario_gold_drop(scenario_level, fight_count, scenario['TITLE'], player.scenario_history, player.difficulty)

        owned_arms = [arm['ARM'] for arm in player.arms]

        easy = "EASY_DROPS"
        normal = "NORMAL_DROPS"
        hard = "HARD_DROPS"
        rewards = []
        rewarded = ""
        mode = ""

        if difficulty == "EASY":
            rewards = scenario.get(easy, [])
            mode = "TALES"
            scenario_gold = round(scenario_gold / 3)
        if difficulty == "NORMAL" and scenario_level < 1500:
            rewards = scenario.get(normal, [])
            mode = "TALES"
        if difficulty == "HARD" or scenario_level >= 1500:
            rewards = scenario.get(hard, [])
            mode = "DUNGEON"
            scenario_gold = round(scenario_gold * 3)

        if rewards:
            if len(rewards) > 1:
                num_of_potential_rewards = len(rewards) - 1
                selection = round(random.randint(0, num_of_potential_rewards))
                rewarded = rewards[selection]
            else:
                rewarded = rewards[0]
        else:
            rewarded = None

        await crown_utilities.bless(scenario_gold, player.did)
        reward_money_message = f"You earned 🪙 **{round(scenario_gold):,}**!"

        if rewarded:
            arm = db.queryArm({"ARM": rewarded})
            if arm:
                if rewarded in owned_arms:
                    return f"You already own 🦾 **{rewarded}**!\n{reward_money_message}"
                else:
                    durability = random.randint(5, 125)
                    arm = crown_utilities.create_arm_from_data(arm)
                    arm.durability = durability
                    response = player.save_arm(arm)
                    if not response:
                        return f"You are maxed out on 🦾 Arms!\n{reward_money_message}"
                    else:
                        return f"You earned 🦾 **{rewarded}** with ⚒️**{str(durability)} Durability**!\n{reward_money_message}"
            else:
                card_data = db.queryCard({"NAME": rewarded})
                if rewarded in (player.cards or player.storage):
                    return f"You already own 🎴 **{rewarded}**!\n{reward_money_message}"
                else:
                    lvl = random.randint(1, 100)
                    card = crown_utilities.create_card_from_data(card_data)
                    card.card_lvl = lvl
                    response = player.save_card(card)
                    if not response:
                        return f"You are maxed out on 🎴 Cards!\n{reward_money_message}"
                    else:
                        return f"You earned 🎴 {card.name}!\n{reward_money_message}"
        else:
            return reward_money_message

    except Exception as ex:
        custom_logging.debug(ex)



async def reward_money(battle_config, player):
    amount = (1000 + (1000 * battle_config.current_opponent_number)) * (1 + player.rebirth)
    gem_amount = 100 + (100 * battle_config.current_opponent_number) * (1 + player.rebirth)

    if battle_config.is_tales_game_mode:
        gem_amount = gem_amount * 1.25
    
    if battle_config.is_dungeon_game_mode:
        amount = amount * 3
        gem_amount = gem_amount * 2.25

    if battle_config.is_scenario_game_mode:
        gem_amount = gem_amount * 1.80

    if battle_config.is_hard_difficulty:
        amount = amount * 5
    
    if battle_config.is_boss_game_mode:
        amount = amount * 1000
    
    if battle_config.is_easy_difficulty:
        amount = (1000 + (1000 * battle_config.current_opponent_number)) 

    try:
        player.save_gems(battle_config.selected_universe, round(gem_amount))
        await crown_utilities.bless(amount, player.did)
        return f"You earned 🪙 **{'{:,}'.format(amount)}**\nYou earned 💎 **{'{:,}'.format(round(gem_amount))}** {battle_config.selected_universe} Gems"
    except Exception as e:
        custom_logging.debug(e)
        return "There was an issue with reward money function"


def get_drop_rate(battle_config, player):
    # Constant values organized in a list of tuples
    drop_values = [("GOLD", 0), ("REMATCH", 100), ("ARM", 150), ("SUMMON", 190), ("CARD", 200)]
    
    # Calculate drop rate
    drop_rate = random.randint(player.rebirth * 10, 200)

    # Assign bonus to drop_rate if in hard difficulty
    if battle_config.is_hard_difficulty:
        drop_rate += 80

    # Initialize drop_style and tiers
    tiers, drop_style = None, None

    # Check game mode and assign corresponding drop style and tiers
    if battle_config.is_dungeon_game_mode:
        drop_style = "DUNGEON"
        tiers = list(range(1, 8))
    elif battle_config.is_boss_game_mode:
        drop_style = "BOSS"
        tiers = list(range(5, 8))
        db.updateUserNoFilter({'DID': player.did}, {'$set': {'BOSS_FOUGHT': True}})
    elif battle_config.is_tales_game_mode:
        drop_style = "TALES"
        tiers = list(range(1, 6))
    elif battle_config.is_scenario_game_mode:
        drop_style = "SCENARIO"
        # Not clear from original code what tiers should be in this case

    # Determine drop type based on drop rate
    for drop_type, value in drop_values:
        if drop_rate >= 200:
            return "CARD", drop_style
        elif drop_rate >= value:
            return drop_type, drop_style

    # Log a warning if no drop type was determined
    loggy.warning(f"No drop type determined for drop rate: {drop_rate}")

    # Return default values if no conditions are met
    return "NO_DROP", drop_style


async def reward_message(battle_config, player, drop_type=None, reward_item=None, owned=None):
    user_query = {'DID': str(player.did)}
    reward_money_message = await reward_money(battle_config, player)
    title_drop_message = player.save_title(battle_config.selected_universe)
    message = ""
    print("reward_message")

    if drop_type == "GOLD" or drop_type is None:
        message = f"**{reward_money_message}**!"

    elif drop_type == "REMATCH":
        response = db.updateUserNoFilter(user_query, {'$inc': {'RETRIES': 1}})
        message = f"You earned 1 Rematch!\n{reward_money_message}"
    
    elif drop_type == "ARM":
        if reward_item in owned:
            message = f"You already own 🦾 **{reward_item}**!"
        else:
            durability = random.randint(5, 150)
            arm = crown_utilities.create_arm_from_data(reward_item)
            arm.durability = durability
            response = player.save_arm(arm)
            if not response:
                message = "You are maxed out on 🦾 Arms!"
            else:
                message = f"You earned 🦾 **{reward_item}** with ⚒️**{str(durability)} Durability**!"

                milestone_message = await Quests.milestone_check(player, "ARMS_OWNED", 1)
                if milestone_message:
                    message += f"\n🏆 {milestone_message}"
        message += f"\n{reward_money_message}"
    
    elif drop_type == "SUMMON":
        if len(player.summons) >= 25:
            message = "You're maxed out on 🐦 Summons!"
        else:
            summon_owned = False
            for s in owned:
                if s['NAME'] == reward_item:
                    summon_owned = True

            if summon_owned:
                await crown_utilities.bless(150, player.did)
                message = f"You own 🐦 **{reward_item}**! Received extra + 🪙 150!"
            else:
                selected_pet = db.querySummon({'PET': reward_item})
                summon = crown_utilities.create_summon_from_data(selected_pet)
                player.save_summon(summon)
                await crown_utilities.bless(50, player.did)
                message = f"You earned 🐦 **{reward_item}** + 🪙 50!"
                milestone_message = await Quests.milestone_check(player, "SUMMONS_OWNED", 1)
                if milestone_message:
                    message += f"\n🏆 {milestone_message}"
        message += f"\n{reward_money_message}"
    
    elif drop_type == "CARD":
        if reward_item in owned:
            message = f"You already own 🎴 **{reward_item}**!"
        else:
            lvl = random.randint(1, 100)
            card = crown_utilities.create_card_from_data(reward_item)
            card.card_lvl = lvl
            response = player.save_card(card)
            if not response:
                message = "You are maxed out on 🎴 Cards!"
            else:
                message = f"You earned 🎴 {card.name}!"
                milestone_message = await Quests.milestone_check(player, "CARDS_OWNED", 1)
                if milestone_message:
                    message += f"\n🏆 {milestone_message}"


        message += f"\n{reward_money_message}"

    if message and title_drop_message:
        message = f"{message}\n{title_drop_message}"
    elif title_drop_message:
        message = title_drop_message
        milestone_message = await Quests.milestone_check(player, "TITLES_OWNED", 1)
        if milestone_message:
            message += f"\n🏆 {milestone_message}"

    return message

async def reward_drop(self, battle_config, player, guranteed_drop=None, guranteed_drop_type=None):
    if guranteed_drop:
        return "message"
    else:
        drop_type, drop_style = get_drop_rate(battle_config, player)
        if battle_config.is_easy_difficulty:
            return reward_money(battle_config, player)
        owned_arms = [arm['ARM'] for arm in player.arms]
        try:
            if drop_type == "REMATCH":
                if player.retries <= 25:
                    message = await reward_message(battle_config, player, drop_type)
                else:
                    message = reward_money(battle_config, player)
                return message
            elif drop_type == "ARM":
                all_available_drop_arms_cursor = db.queryDropArms(battle_config.selected_universe, drop_style)
                all_available_drop_arms = list(all_available_drop_arms_cursor)  # Convert cursor to list
                if all_available_drop_arms:
                    rand_arm = random.choice(all_available_drop_arms)['ARM']
                    message = await reward_message(battle_config, player, drop_type, rand_arm, owned_arms)
                else:
                    message = reward_money(battle_config, player)
                return message
            elif drop_type == "SUMMON":
                all_available_drop_summons_cursor = db.queryDropSummons(battle_config.selected_universe, drop_style)
                all_available_drop_summons = list(all_available_drop_summons_cursor)  # Convert cursor to list
                if all_available_drop_summons:
                    rand_summon = random.choice(all_available_drop_summons)['PET']
                    message = await reward_message(battle_config, player, drop_type, rand_summon, player.summons)
                else:
                    message = await reward_message(battle_config, player)
                return message
            elif drop_type == "CARD":
                all_available_drop_cards_cursor = db.queryDropCards(battle_config.selected_universe, drop_style)
                all_available_drop_cards = list(all_available_drop_cards_cursor)  # Convert cursor to list
                if all_available_drop_cards:
                    rand_card = random.choice(all_available_drop_cards)['NAME']
                    message = await reward_message(battle_config, player, drop_type, rand_card, player.cards)
                else:
                    message = await reward_message(battle_config, player)
                return message
            else:
                message = await reward_message(battle_config, player)
                return message
        except Exception as ex:
            custom_logging.debug(ex)
            await crown_utilities.bless(5000, player.did)
            return f"You earned 🪙 **5000**!"
def setup(bot):
    RewardDrops(bot)
    
              
