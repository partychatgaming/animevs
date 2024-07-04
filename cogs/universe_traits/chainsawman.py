import crown_utilities


def devilization(player_card, battle_config):
    if player_card.universe == "Chainsawman":
        devils_endurance(player_card, battle_config)
        if not player_card._first_offering:
            player_card._first_offering = True
            player_card.contract_buff = round(player_card.max_health * .10)
            player_card.universe_trait_value = round(player_card.contract_buff / 2)
            contract_split = round(player_card.contract_buff / 2)
            player_card.max_health -= round(player_card.contract_buff)
            player_card.attack += round(contract_split)
            player_card.defense += round(contract_split)
            battle_config.add_to_battle_log(f"♾️ {player_card.name}'s contract [-❤️{player_card.contract_buff:,} | +🗡️{contract_split:,} | +🛡️{contract_split:,}]")
        if player_card._chainsawman_activated == True:
            if player_card.health <= (player_card.max_health * .40):
                if player_card._atk_chainsawman_buff == False:
                    player_card._atk_chainsawman_buff = True
                    player_card._chainsawman_activated = False
                    base_max_health = player_card.max_health
                    player_card.max_health += round(player_card.card_tier * player_card.contract_buff)
                    player_card.health += round(player_card.contract_buff) 
                    player_card.arbitrary_ap_buff += round(player_card.contract_buff/ 2) 
                    player_card.attack = round(player_card.health + (player_card.contract_buff / 2))
                    player_card.defense = round(player_card.health + (player_card.contract_buff / 2))
                    battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s devilization! [❤️{player_card.health:,} | 🗡️{player_card.attack:,} | 🛡️{player_card.defense:,}]")
        elif player_card._atk_chainsawman_buff == True and player_card.used_resolve:
            player_card.universe_trait_value = round(player_card.contract_buff)
            player_card.attack = player_card.health + player_card.contract_buff
            player_card.defense = player_card.health + player_card.contract_buff
        elif player_card._atk_chainsawman_buff == True:
            player_card.attack = round(player_card.health + (player_card.contract_buff / 2))
            player_card.defense = round(player_card.health + (player_card.contract_buff /2))
        
def contract_fulfilled(player_card, battle_config, resolve_health, title):
    if player_card._atk_chainsawman_buff == True and player_card.used_resolve:
        player_card.universe_trait_value = round(player_card.contract_buff)
        player_card.attack = player_card.health + player_card.contract_buff
        player_card.defense = player_card.health + player_card.contract_buff
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name}'s ⚡Contract Fulfilled {title} [+❤️{resolve_health:,} : [+🗡️{player_card.contract_buff:,} | +🛡️{player_card.contract_buff:,}]")
        return True
    else:
        return False

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
            if player_card.health <= 0:
                if battle_config.is_tutorial_game_mode and not battle_config.tutorial_health_check and player_card.name != "Training Dummy":
                    battle_config.tutorial_health_check = True
                    battle_config.tutorial_messages(player_card,None,"HEALTH")
                player_card._chainsawman_revive_active = False
                player_card.devils_endurance_active = True
                player_card.devils_endurance_timer = 3
                player_card.health = 666
                player_card.stamina = 100
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} has fallen but the devil lives for {player_card.devils_endurance_timer} turns [❤️{player_card.health:,} | 🌀{player_card.stamina:,}]")
        elif player_card.devils_endurance_active == True:
            if player_card.health <= 0:
                player_card.devils_endurance_active = False
                player_card.health = -1000
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ The Devil returns to Hell")
            if player_card.devils_endurance_timer == 3:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} has fallen but the devil lives for {player_card.devils_endurance_timer} turns")
                player_card.devils_endurance_timer -= 1
                return
            if player_card.devils_endurance_timer < 0:
                player_card.devils_endurance_active = False
                player_card.health = -1000
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ The Devil returns to Hell")
            else:
                battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ {player_card.name} has fallen but the devil lives for {player_card.devils_endurance_timer} turns")
                player_card.devils_endurance_timer -= 1
