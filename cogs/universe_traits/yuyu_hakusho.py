import crown_utilities
import random

def spirit_resolved(player_card, battle_config, opponent_card, player_title):
    if player_card.universe == "YuYu Hakusho":  # My Hero Trait
        fortitude = 0.0
        low = player_card.health - (player_card.health * .75)
        high = player_card.health - (player_card.health * .66)
        fortitude = round(random.randint(int(low), int(high)))
        # Resolve Scaling
        resolve_health = round(fortitude + (.5 * player_card.resolve_value))
        resolve_attack_value = round(
            (.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        resolve_defense_value = round(
            (.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        
        # boost = 0
        # if player_card.health >= 0.8 * player_card.max_base_health:
        #     boost = 0.15
        # elif player_card.health <= 0.4 * player_card.max_base_health:
        #     boost = 1
        # else:
        #     boost = .30
        
        title_message = ""
        
        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)

        player_card.stamina = 160
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack * 2)
        player_card.yuyu_1ap_buff = round(player_card.move1ap * 2)
        player_card.yuyu_2ap_buff = round(player_card.move2ap * 2)
        player_card.yuyu_3ap_buff = round(player_card.move3ap * 2)
        player_card.defense = 100
        player_card.used_resolve = True
        player_card.usedsummon = False
        
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} activated ⚡Spirit Energy doubling their attack and ap at the cost of defense 🔺{title_message}")

        # battle_config.turn_total = battle_config.turn_total + 1
        battle_config.repeat_turn()
        return True


def meditation(player_card, battle_config):
    if player_card.universe == "Yu Yu Hakusho" and not player_card.used_resolve:
        defense_increase = 100 * player_card.tier
        player_card.yuyu_1ap_buff += 10 * player_card.tier
        player_card.yuyu_2ap_buff += 10 * player_card.tier
        player_card.yuyu_3ap_buff += 10 * player_card.tier
        player_card.defense = player_card.defense + defense_increase
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} increased their defense by {defense_increase} and ap by {10 * player_card.tier}")