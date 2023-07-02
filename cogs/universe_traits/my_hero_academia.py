import crown_utilities
import random

def quirk_awakening(player_card, battle_config, player_title):
    if player_card.universe == "My Hero Academia":  # My Hero Trait
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


        player_card.my_hero_academia_buff = player_card.my_hero_academia_buff_counter * player_card.focus_count
        player_card.stamina = 160
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.used_resolve = True
        player_card.usedsummon = False
        
        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{player_card.name}** 🩸 Resolved: Quirk Awakening! Ap has been increased by **{player_card.my_hero_academia_buff}** 🔺{title_message}")

        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True


def plus_ultra(player_card, battle_config):
    if player_card.universe == "My Hero Academia" and not player_card.used_block:
        player_card.my_hero_academia_buff_counter += 20
        battle_config.add_to_battle_log(f"(**{battle_config.turn_total}**) **{player_card.name}** 🩸 went Plus Ultra, increasing their dormant ap to {player_card.my_hero_academia_buff_counter}")


def activate_my_hero_academia_trait(player_card):
    if player_card.universe == "My Hero Academia" and not player_card.used_resolve:
        player_card.my_hero_academia_buff_counter += 10
    
    if player_card.universe == "My Hero Academia" and player_card.used_resolve and player_card.my_hero_academia_buff > 50:
        player_card.my_hero_academia_buff -= 50



