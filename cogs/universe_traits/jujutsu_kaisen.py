import crown_utilities
import random


def cursed_energy(player_card, current_hit_roll, battle_config):
    crit = current_hit_roll
    if player_card.universe == "Jujutsu Kaisen":
        crit = current_hit_roll
        if not player_card.jujutsu_kaisen_focus_crit_used:
            crit = 20
            player_card.jujutsu_kaisen_focus_crit_used = True
            # battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} is preparing their cursed energy for a critical hit")
        if player_card.used_resolve and crit <= 1:
            crit = 10
        return crit
    return crit
        
def cursed_energy_reset(player_card, battle_config):
    if player_card.universe == "Jujutsu Kaisen":
        player_card.jujutsu_kaisen_focus_crit_used = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} is preparing their cursed energy for a critical hit")
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
        player_card.jujutsu_kaisen_domain_expansion_active = True
        if opponent_card.used_resolve:
            player_card.jujutsu_kaisen_opponent_resolved_before_self = True
        max = crown_utilities.get_jjk_class_value(player_card.tier)
        player_card.jujutsu_kaisen_damage_check_turn_count = max - player_card.focus_count
        if player_card.jujutsu_kaisen_damage_check_turn_count <= 0:
            player_card.jujutsu_kaisen_damage_check_turn_count = 1
        player_card.jujutsu_kaisen_damage_meter = round((player_card.max_health * 0.5) + player_card.card_lvl)
        player_card.jujutsu_kaisen_damage_meter_max = round((player_card.max_health * 0.5) + player_card.card_lvl)
        message = f"({battle_config.turn_total}) ♾️ {player_card.name} activated ⚡Domain Expansion [Deal {player_card.jujutsu_kaisen_damage_meter:,} damage in {player_card.jujutsu_kaisen_damage_check_turn_count} turns to break the domain]"
        if opponent_card.jujutsu_kaisen_domain_expansion_active:
            if (player_card.attack + player_card.defense) > (opponent_card.attack + opponent_card.defense):
                opponent_card.jujutsu_kaisen_domain_expansion_active = False
                opponent_card.jujutsu_kaisen_damage_check_turn_count = 0
                opponent_card.jujutsu_kaisen_damage_meter = 0
                player_card.jujutsu_kaisen_domain_expansion_active = True
                message = f"({battle_config.turn_total}) ♾️ {player_card.name} activated ⚡Domain Expansion, breaking {opponent_card.name}'s Domain"
            else:
                # You are unable to activate your domain and will succumb to your opponents domain
                message = f"({battle_config.turn_total}) ♾️ {player_card.name}'s ⚡Domain Expansion was immediately cancelled by {opponent_card.name}'s Domain"
                player_card.jujutsu_kaisen_domain_expansion_active = False
        battle_config.add_to_battle_log(message)

        # battle_config.turn_total = battle_config.turn_total + 1
        battle_config.next_turn()
        return True
def get_domain_turns(player_card):
    if player_card.universe == "Jujutsu Kaisen":
        player_card.universe_trait_value = player_card.jujutsu_kaisen_damage_check_turn_count
        return player_card.jujutsu_kaisen_damage_check_turn_count
    return 0

def domain_expansion_check(player_card, opponent_card, battle_config, damage=0):
    if not opponent_card.jujutsu_kaisen_domain_expansion_active:
        return
    
    def deactivate_domain():
            opponent_card.jujutsu_kaisen_domain_expansion_active = False
            opponent_card.jujutsu_kaisen_damage_check_turn_count = 0
            opponent_card.jujutsu_kaisen_damage_meter = 0

    def mxhealth_and_damage_operation():
        player_card.max_health = player_card.max_health - round(player_card.max_health * (opponent_card.tier / 100))
        opponent_card.jujutsu_kaisen_damage_check_turn_count -= 1
        opponent_card.jujutsu_kaisen_damage_meter -= damage

    if opponent_card.jujutsu_kaisen_damage_check_turn_count > 0:
        mxhealth_and_damage_operation()

        if opponent_card.jujutsu_kaisen_damage_meter <= 0:
            deactivate_domain()
            if opponent_card.jujutsu_kaisen_opponent_resolved_before_self:
                opponent_card.health = opponent_card.health - round(damage + opponent_card.jujutsu_kaisen_damage_meter_max)
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {opponent_card.name}'s Domain has been broken by {player_card.name} [{opponent_card.name} was dealt {(damage + opponent_card.jujutsu_kaisen_damage_meter_max):,} damage]")
            else:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {opponent_card.name}'s Domain has been broken by {player_card.name}")
        
        if opponent_card.jujutsu_kaisen_damage_meter > 0:
            if opponent_card.jujutsu_kaisen_damage_check_turn_count > 1:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {opponent_card.name}'s Domain is still active for {opponent_card.jujutsu_kaisen_damage_check_turn_count} turns [{opponent_card.jujutsu_kaisen_damage_meter:,} damage remaining]")
            if opponent_card.jujutsu_kaisen_damage_check_turn_count == 0:
                deactivate_domain()
                player_card.health = 0
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} has been executed in {opponent_card.name}'s Domain")