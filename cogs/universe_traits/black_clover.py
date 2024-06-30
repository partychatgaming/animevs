import crown_utilities

def grimoire(player_card, battle_config):
    if player_card.universe == "Black Clover":        
        grimoire_buff = 25 * player_card.tier
        player_card.stamina = player_card.stamina + 50
        player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + grimoire_buff
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) {player_card.name} ♾️ increased their stamina by 50 & ap by {grimoire_buff:,}")


def mana_zone(player_card, battle_config):
    if player_card.universe == "Black Clover":                
        player_card.stamina = 100
        mana_zone_buff = round((player_card.card_lvl + 49) * .1)
        player_card.card_lvl_ap_buff = player_card.card_lvl_ap_buff + mana_zone_buff
        battle_config.add_to_battle_log(f"(🌀) ♾️ {player_card.name} mana zone increased their stamina to 100 & ap by 🔺{mana_zone_buff:,}")



