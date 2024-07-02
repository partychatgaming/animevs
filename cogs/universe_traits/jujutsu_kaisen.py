import crown_utilities
import random


def cursed_energy(player_card, current_hit_roll, battle_config):
    crit = current_hit_roll
    if player_card.universe == "Jujutsu Kaisen":
        crit = current_hit_roll
        if not player_card.jujutsu_kaisen_focus_crit_used:
            crit = 20
            player_card.jujutsu_kaisen_focus_crit_used = True
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} is preparing their cursed energy for a critical hit")
        if player_card.used_resolve and crit <= 1:
            crit = 10
        return crit
    return crit
        
def cursed_energy_reset(player_card, battle_config):
    if player_card.universe == "Jujutsu Kaisen":
        player_card.jujutsu_kaisen_focus_crit_used = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} has reset their cursed energy")
        return


def domain_expansion(player_card, battle_config, player_title, opponent_card):
    if player_card.universe == "Jujutsu Kaisen":  # JJK Trait
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


        player_card.stamina = 160
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.used_resolve = True
        player_card.usedsummon = False
        if opponent_card.used_resolve:
            player_card.jujutsu_kaisen_oppenent_resolved_before_self = True
        player_card.jujutsu_kaisen_domain_expansion_active = True
        player_card.jujutsu_kaisen_damage_check_turn_count = 10 - opponent_card.focus_count
        player_card.jujutsu_kaisen_damage_meter = round((player_card.max_health * 0.5) + player_card.level)
        player_card.jujutsu_kaisen_damage_meter_max = round((player_card.max_health * 0.5) + player_card.level)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} has activated their Domain Expansion [Deal {player_card.jujutsu_kaisen_damage_meter:,} damage in {player_card.jujutsu_kaisen_damage_check_turn_count} turns to break the domain]")

        battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True


def domain_expansion_check(opponent_card, player_card, battle_config, damage=None):
    if opponent_card.universe == "Jujutsu Kaisen":
        if opponent_card.jujutsu_kaisen_domain_expansion_active:
            if damage is None:
                battle_config.next_turn()
                return {"TURN": battle_config.is_turn}
            if opponent_card.jujutsu_kaisen_damage_check_turn_count == 0 and damage < opponent_card.jujutsu_kaisen_damage_meter:
                opponent_card.jujutsu_kaisen_domain_expansion_active = False
                opponent_card.jujutsu_kaisen_damage_check_turn_count = 0
                opponent_card.jujutsu_kaisen_damage_meter = 0
                player_card.health = 0
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} has been executed in {opponent_card.name}'s Domain")

            if opponent_card.jujutsu_kaisen_damage_check_turn_count == 0 and damage >= opponent_card.jujutsu_kaisen_damage_meter:
                opponent_card.jujutsu_kaisen_domain_expansion_active = False
                opponent_card.jujutsu_kaisen_damage_check_turn_count = 0
                opponent_card.jujutsu_kaisen_damage_meter = 0
                opponent_card.health = opponent_card.health - round(damage + opponent_card.jujutsu_kaisen_damage_meter_max)
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {opponent_card.name}'s Domain has been broken by {player_card.name} [{opponent_card.name} was dealt {(damage + opponent_card.jujutsu_kaisen_damage_meter_max):,} damage]")

            if opponent_card.jujutsu_kaisen_damage_check_turn_count > 0:
                opponent_card.max_health = opponent_card.max_health - round(opponent_card.max_health * (opponent_card.tier / 100))
                opponent_card.jujutsu_kaisen_damage_check_turn_count -= 1
                opponent_card.jujutsu_kaisen_damage_meter -= damage
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) {opponent_card.name}'s Domain is still active for {opponent_card.jujutsu_kaisen_damage_check_turn_count} turns [{opponent_card.jujutsu_kaisen_damage_meter:,} damage remaining]")

        return