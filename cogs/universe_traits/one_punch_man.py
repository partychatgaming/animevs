import crown_utilities
import random


def rank_hero(player_card, battle_config, opponent_card):
    if player_card.universe == "One Punch Man":
        bottom_tier_cards = [1, 2, 3]
        bot_low_tier_cards = [4, 5]
        mid_tier_cards = [6, 7]
        high_tier_cards = [8, 9]
        rank = "F"
        ap_boost = 15 * player_card.tier
        
        if player_card.tier == 10:
            ap_boost = 100
            rank = "🇸 Rank Hero"
        elif player_card.tier in high_tier_cards:
            rank = "🇦 Rank Hero"
        elif player_card.tier in mid_tier_cards:
            rank = "🇧 Rank Hero"
        elif player_card.tier in bot_low_tier_cards:
            rank = "🇨 Rank Hero"
        elif player_card.tier in bottom_tier_cards:
            rank = "🇩 Rank Hero"
        if player_card.is_monstrosity:
            ap_boost = 30 * player_card.tier
            if player_card.tier == 10:
                ap_boost = 300
                rank = "God Level Threat"
            elif player_card.tier in high_tier_cards:
                rank = "Dragon Level Threat"
            elif player_card.tier in mid_tier_cards:
                rank = "Demon Level Threat"
            elif player_card.tier in bot_low_tier_cards:
                rank = "Tiger Level Threat"
            elif player_card.tier in bottom_tier_cards:
                rank = "Wolf Level Threat"
        
        player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + ap_boost
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {rank} {player_card.name} increased ap by {ap_boost}")

        
def hero_reinforcements(player_card, battle_config, opponent_card):
    if opponent_card.universe == "One Punch Man":
        rank = "Hero Reinforcements"
        r_points = 50
        factor = (r_points * opponent_card.tier)
        if player_card.is_monstrosity:
            rank = "Monsterous Rejuvination"
            r_points = 25
            factor = (r_points * player_card.tier)
        opponent_card.health = round(opponent_card.health + factor)
        opponent_card.max_health = round(opponent_card.max_health + factor)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {rank}! {opponent_card.name} increased health and max health by ❤️ {factor}")

