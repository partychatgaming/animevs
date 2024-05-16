import crown_utilities


def devilization(player_card, battle_config):
    if player_card.universe == "Chainsawman":
        if player_card.health <= (player_card.max_health * .25):
            if player_card._chainsawman_activated == True:
                if player_card._atk_chainsawman_buff == False:
                    player_card._atk_chainsawman_buff = True
                    player_card._chainsawman_activated = False
                    player_card.defense = player_card.defense * 2
                    player_card.attack = player_card.attack * 2
                    player_card.max_health = player_card.max_health * 2
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} entered devilization")

        elif player_card.health <= (player_card.max_health * .50):
            if player_card._chainsawman_activated == True:
                if player_card._atk_chainsawman_buff == False:
                    player_card._atk_chainsawman_buff = True
                    player_card._chainsawman_activated = False
                    player_card.defense = player_card.defense * 2
                    player_card.attack = player_card.attack * 2
                    player_card.max_health = player_card.max_health * 2
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} entered devilization")

