import crown_utilities

def pentakill(player_card, battle_config, opponent_card):
    if player_card.universe == "League Of Legends":
        opponent_card.health = opponent_card.health - (150 * (player_card.focus_count + opponent_card.focus_count))
        player_card.damage_dealth = player_card.damage_dealt + (150 * (player_card.focus_count + opponent_card.focus_count))
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} resolved and executed a pentakill dealing {(150 * (player_card.focus_count + opponent_card.focus_count))} damage")
        return True
    else:
        return False


def turret_shot(player_card, battle_config, opponent_card):
    if player_card.universe == "League Of Legends":                
        opponent_card.health = round(opponent_card.health - (60 + battle_config.turn_total))
        player_card.damage_dealth = player_card.damage_dealt + (60 + battle_config.turn_total)
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {opponent_card.name}'s turret shot hits {opponent_card.name} for {60 + battle_config.turn_total} damage")

