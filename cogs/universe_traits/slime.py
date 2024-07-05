import crown_utilities
import random


def skill_evolution(player_card, battle_config, player_title):
    if player_card.universe == "That Time I Got Reincarnated as a Slime":  # That Time I Got Reincarnated as a Slime Trait
        # fortitude or luck is based on health
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

        title_message = ""

        if player_title.singularity_effect:
            resolve_health, resolve_attack_value, resolve_defense_value, title_message = player_title.singularity_handler(resolve_health, resolve_attack_value, resolve_defense_value)

        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.slime_buff = player_card.slime_buff + player_card.move1ap + player_card.move2ap
        player_card.move1ap = 25
        player_card.move2ap = 25
        player_card.card_lvl_ap_buff = 0
        player_card.shock_buff = 0
        player_card.basic_water_buff = 0
        player_card.arbitrary_ap_buff = 0
        player_card.used_resolve = True
        player_card.usedsummon = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s ⚡Skill Evolution, Converting {player_card.slime_buff} AP from Basic and Special attacks into Ultimate move AP!'{title_message}")

        # battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True

def summon_slime(player_card, battle_config, opponent_card):
    if player_card.universe == "That Time I Got Reincarnated as a Slime":
        battle_config.turn_total -= 1
        slime_bonus = (5 * player_card.tier)
        player_card.stamina = player_card.stamina + slime_bonus
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.summon_name} increased {player_card.name}'s stamina by {slime_bonus}.")
        opponent_card.usedsummon = True
        battle_config.turn_total += 1
    else:
        return False
    
def beezlebub(player_card, battle_config, opponent_card):
    if player_card.universe == "That Time I Got Reincarnated as a Slime":
        beezlebub_value = (((player_card.tier) / 100 )) * (player_card.focus_count + 1)
        # print(opponent_card.attack)
        # print(opponent_card.defense)
        # print(beezlebub_value)
        opponent_card.attack -= round(opponent_card.attack * beezlebub_value)
        opponent_card.defense -= round(opponent_card.defense * beezlebub_value)
        player_card.attack += round(opponent_card.attack * beezlebub_value)
        player_card.defense += round(opponent_card.defense * beezlebub_value)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s Beezlebuth Steals {round(opponent_card.attack * beezlebub_value)} ATK and {round(opponent_card.defense * beezlebub_value)} DEF from {opponent_card.name}")