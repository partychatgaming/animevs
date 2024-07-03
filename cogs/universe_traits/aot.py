import crown_utilities
import random

def titan_mode(player_card, battle_config, player_title):
    if player_card.universe == "Attack On Titan":
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
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.used_resolve = True
        player_card.usedsummon = False
        health_boost = 100 * (player_card.focus_count * player_card.card_tier)
        player_card.health = player_card.health + health_boost
        player_card.damage_healed = player_card.damage_healed + resolve_health + health_boost

        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} resolved, entering their titan form, healing for {health_boost} {title_message}")

        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True


def rally(player_card, battle_config):
    if player_card.universe == "Attack On Titan":
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} gained {(50 * player_card.tier)} health and max health rallying the survey corps ❤️")
        player_card.max_health = round(player_card.max_health + (50 * player_card.tier))
        player_card.health = player_card.health + (50 * player_card.tier)

def omnigear(player_card, battle_config):
    if player_card.universe == "Attack On Titan":
        class_level = crown_utilities.get_class_value(player_card.tier)
        speed_boost = round(player_card.speed * (.05 * class_level))
        ap_boost = round(player_card.arbitrary_ap_buff * (.05 * class_level))
        player_card.speed += round(speed_boost)
        if player_card.arbitrary_ap_buff <= 0:
            ap_boost = round(player_card.speed * (.05 * class_level))
            player_card.arbitrary_ap_buff += round(ap_boost)
        player_card.arbitrary_ap_buff += round(ap_boost)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} activated their omnigear, gaining {(ap_boost)} ap and {(speed_boost)} speed bonus")