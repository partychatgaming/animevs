import crown_utilities

def grimoire(player_card, battle_config):
    if player_card.universe == "Black Clover":                
        player_card.stamina = player_card.stamina + 70
        player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + 50
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} 🩸 increased their stamina & ap by 50")


def mana_zone(player_card, battle_config):
    if player_card.universe == "Black Clover":                
        player_card.stamina = 100
        player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + 50 + battle_config.turn_total
        battle_config.add_to_battle_log(f"(🌀) 🩸 {player_card.name} mana zone increased their stamine & ap 🌀")



