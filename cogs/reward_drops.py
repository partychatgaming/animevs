import asyncio
import crown_utilities
import custom_logging
import db
import random
from logger import loggy
from .quests import Quests
from interactions import listen, Extension
from logger import loggy

class RewardDrops(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        # print('Drops Cog is ready!')
        loggy.info('Drops Cog is ready')


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
            arm = await asyncio.to_thread(db.queryArm, {"ARM": rewarded})
            if arm:
                if rewarded in owned_arms:
                    return f"You already own 🦾 **{rewarded}**!\n{reward_money_message}"
                else:
                    durability = random.randint(5, 125)
                    arm = crown_utilities.create_arm_from_data(arm)
                    arm.durability = durability
                    response = await asyncio.to_thread(player.save_arm, arm)
                    if response is not True:
                        return f"You are maxed out on 🦾 Arms!\n{reward_money_message}"
                    else:
                        return f"You earned 🦾 **{rewarded}** with ⚒️**{str(durability)} Durability**!\n{reward_money_message}"
            card_data = await asyncio.to_thread(db.queryCard, {"NAME": rewarded})
            if card_data:
                if rewarded in (player.cards or []) or rewarded in (player.storage or []):
                    return f"You already own 🎴 **{rewarded}**!\n{reward_money_message}"
                lvl = random.randint(1, 100)
                card = crown_utilities.create_card_from_data(card_data)
                card.card_lvl = lvl
                response = await asyncio.to_thread(player.save_card, card)
                if response is not True:
                    return f"You are maxed out on 🎴 Cards!\n{reward_money_message}"
                return f"You earned 🎴 {card.name}!\n{reward_money_message}"
            summon_data = await asyncio.to_thread(db.querySummon, {"PET": rewarded})
            if summon_data:
                summon = crown_utilities.create_summon_from_data(summon_data)
                response = await asyncio.to_thread(player.save_summon, summon)
                if response is True:
                    return f"You earned 🧬 **{rewarded}**!\n{reward_money_message}"
                if response is False:
                    return f"You already own 🧬 **{rewarded}**!\n{reward_money_message}"
                return f"You are maxed out on 🧬 Summons!\n{reward_money_message}"
            title_data = await asyncio.to_thread(db.queryTitle, {"TITLE": rewarded})
            if title_data:
                if rewarded in (player.titles or []):
                    return f"You already own 🎗️ **{rewarded}**!\n{reward_money_message}"
                await asyncio.to_thread(db.updateUserNoFilter, {'DID': str(player.did)}, {'$addToSet': {'TITLES': rewarded}})
                return f"You earned 🎗️ **{rewarded}**!\n{reward_money_message}"
            loggy.warning(f"Scenario reward '{rewarded}' is not a card, arm, summon or title")
            return reward_money_message
        else:
            return reward_money_message

    except Exception as ex:
        custom_logging.debug(ex)
        return "⚠️ The scenario reward could not be delivered."



async def reward_money(battle_config, player):
    amount = (10000 + (1000 * battle_config.current_opponent_number)) * (1 + player.rebirth)
    gem_amount = 1000 + (100 * battle_config.current_opponent_number) * (1 + player.rebirth)

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
        await asyncio.to_thread(player.save_gems, battle_config.selected_universe, round(gem_amount))
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

    # Determine drop type based on drop rate: the highest threshold reached wins.
    # (This used to walk the table from the bottom, so the first row - GOLD at 0 -
    # always matched and arms, summons and rematches could never drop.)
    for drop_type, value in reversed(drop_values):
        if drop_rate >= value:
            return drop_type, drop_style

    # Log a warning if no drop type was determined
    loggy.warning(f"No drop type determined for drop rate: {drop_rate}")

    # Return default values if no conditions are met
    return "NO_DROP", drop_style


async def reward_message(battle_config, player, drop_type=None, reward_item=None, owned=None):
    user_query = {'DID': str(player.did)}
    reward_money_message = await reward_money(battle_config, player)
    title_drop_message = await asyncio.to_thread(player.save_title, battle_config.selected_universe)
    message = ""

    if drop_type == "GOLD" or drop_type is None:
        message = f"**{reward_money_message}**!"

    elif drop_type == "REMATCH":
        response = await asyncio.to_thread(db.updateUserNoFilter, user_query, {'$inc': {'RETRIES': 1}})
        message = f"You earned 1 Rematch!\n{reward_money_message}"
    
    elif drop_type == "ARM":
        # reward_item is the arm's NAME; the arm object has to be built from its data
        arm_data = await asyncio.to_thread(db.queryArm, {'ARM': reward_item})
        arm = crown_utilities.create_arm_from_data(arm_data) if arm_data else False
        if reward_item in owned:
            message = f"You already own 🦾 **{reward_item}**!"
        elif not arm:
            message = ""
        else:
            durability = random.randint(5, 150)
            arm.durability = durability
            response = await asyncio.to_thread(player.save_arm, arm)
            if response is not True:
                message = "You are maxed out on 🦾 Arms!"
            else:
                message = f"You earned 🦾 **{reward_item}** with ⚒️**{str(durability)} Durability**!"

                milestone_message = await Quests.milestone_check(player, "ARMS_OWNED", 1)
                if milestone_message:
                    message += f"\n🏆 {milestone_message}"
        message = f"{message}\n{reward_money_message}".strip()
    
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
                selected_pet = await asyncio.to_thread(db.querySummon, {'PET': reward_item})
                summon = crown_utilities.create_summon_from_data(selected_pet)
                await asyncio.to_thread(player.save_summon, summon)
                await crown_utilities.bless(50, player.did)
                message = f"You earned 🐦 **{reward_item}** + 🪙 50!"
                milestone_message = await Quests.milestone_check(player, "SUMMONS_OWNED", 1)
                if milestone_message:
                    message += f"\n🏆 {milestone_message}"
        message += f"\n{reward_money_message}"
    elif drop_type == "CARD":
        # reward_item is the card's NAME; the card object has to be built from its data
        card_data = await asyncio.to_thread(db.queryCard, {'NAME': reward_item})
        card = crown_utilities.create_card_from_data(card_data) if card_data else False
        if reward_item in owned or reward_item in (player.storage or []):
            message = f"You already own 🎴 **{reward_item}**!"
        elif not card:
            message = ""
        else:
            lvl = random.randint(1, 100)
            card.card_lvl = lvl
            response = await asyncio.to_thread(player.save_card, card)
            if response is not True:
                message = "You are maxed out on 🎴 Cards!"
            else:
                message = f"You earned 🎴 {card.name}!"
                milestone_message = await Quests.milestone_check(player, "CARDS_OWNED", 1)
                if milestone_message:
                    message += f"\n🏆 {milestone_message}"
        message = f"{message}\n{reward_money_message}".strip()

    if message and title_drop_message:
        message = f"{message}\n{title_drop_message}"
        milestone_message = await Quests.milestone_check(player, "TITLES_OWNED", 1)
    elif title_drop_message:
        message = title_drop_message
        milestone_message = await Quests.milestone_check(player, "TITLES_OWNED", 1)
        if milestone_message:
            message += f"\n🏆 {milestone_message}"
    else:
        message = f"{message}"
    return message

async def reward_drop(self, battle_config, player, guranteed_drop=None, guranteed_drop_type=None):
    if guranteed_drop:
        return "message"
    else:
        drop_type, drop_style = get_drop_rate(battle_config, player)
        if battle_config.is_easy_difficulty:
            return await reward_money(battle_config, player)
        owned_arms = [arm['ARM'] for arm in player.arms]
        try:
            if drop_type == "REMATCH":
                if player.retries <= 25:
                    message = await reward_message(battle_config, player, drop_type)
                else:
                    message = await reward_money(battle_config, player)
                return message
            elif drop_type == "ARM":
                all_available_drop_arms_cursor = await asyncio.to_thread(db.queryDropArms, battle_config.selected_universe, drop_style)
                all_available_drop_arms = list(all_available_drop_arms_cursor)  # Convert cursor to list
                if all_available_drop_arms:
                    rand_arm = random.choice(all_available_drop_arms)['ARM']
                    message = await reward_message(battle_config, player, drop_type, rand_arm, owned_arms)
                else:
                    message = await reward_money(battle_config, player)
                return message
            elif drop_type == "SUMMON":
                all_available_drop_summons_cursor = await asyncio.to_thread(db.queryDropSummons, battle_config.selected_universe, drop_style)
                all_available_drop_summons = list(all_available_drop_summons_cursor)  # Convert cursor to list
                if all_available_drop_summons:
                    rand_summon = random.choice(all_available_drop_summons)['PET']
                    message = await reward_message(battle_config, player, drop_type, rand_summon, player.summons)
                else:
                    message = await reward_message(battle_config, player)
                return message
            elif drop_type == "CARD":
                all_available_drop_cards_cursor = await asyncio.to_thread(db.queryDropCards, battle_config.selected_universe, drop_style)
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
    
              
