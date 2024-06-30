import crown_utilities


def devilization(player_card, battle_config):
    if player_card.universe == "Chainsawman":
        if player_card._chainsawman_activated == True:
            if player_card.health <= (player_card.max_health * .50):
                if player_card._atk_chainsawman_buff == False:
                    player_card._atk_chainsawman_buff = True
                    player_card._chainsawman_activated = False
                    base_max_health = player_card.max_health
                    player_card.max_health += round(player_card.card_tier * player_card.contract_buff)
                    player_card.health += round(player_card.contract_buff) 
                    player_card.arbitrary_ap_buff += round(player_card.contract_buff) 
                    player_card.attack = round(player_card.health + (player_card.contract_buff / 2))
                    player_card.defense = round(player_card.health + (player_card.contract_buff / 2))
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name}'s Devilization [+{round(player_card.contract_buff)}]")
        elif player_card._atk_chainsawman_buff == True and player_card.used_resolve:
            player_card.attack = player_card.health + player_card.contract_buff
            player_card.defense = player_card.health + player_card.contract_buff
        elif player_card._atk_chainsawman_buff == True:
            player_card.attack = round(player_card.health + (player_card.contract_buff / 2))
            player_card.defense = round(player_card.health + (player_card.contract_buff /2))
        


def contracts(player_card, dmg, battle_config):
    if player_card.universe == "Chainsawman":
        #Since chainsawman is contractual and using the devil abilities requires you to lose vitality in the show in some way, I was thinking… Chainsawman cards attack and defense are always equal to their health. Each attack decreases health (in some way). 
        player_card.max_health -= round(dmg['DMG'] * .10)
        player_card.contract_buff += round(dmg['DMG'] * .10)
        player_card.universe_trait_value = player_card.contract_buff
        player_card.attack += round(player_card.contract_buff / 2)
        player_card.defense += round(player_card.contract_buff / 2)
        if player_card.used_resolve:
            player_card.attack = player_card.health + player_card.contract_buff
            player_card.defense = player_card.health + player_card.contract_buff

def devils_endurance(player_card, battle_config):
    if player_card.universe == "Chainsawman":
        if player_card._chainsawman_revive_active == True:
            player_card._chainsawman_revive_active == False
            player_card.devils_endurance_active = True
            player_card.devils_endurance_timer += player_card.tier
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} has fallen but the devil lives for {player_card.devils_endurance_timer} turns")
        elif player_card.devils_endurance_active == True:
            player_card.health = 666
            player_card.devils_endurance_timer -= 1
            if player_card.devils_endurance_timer <= 0:
                player_card.devils_endurance_active = False
                player_card.health = -1000
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 The Devil returns to Hell")
            else:
                 battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 {player_card.name} has fallen but the devil lives for {player_card.devils_endurance_timer} turns")
