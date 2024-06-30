import crown_utilities


def increase_power(player_card, battle_config, opponent_card):
    if opponent_card.universe == "7ds":
        opponent_card.stamina = opponent_card.stamina + 60

        fortitude = round(opponent_card.health * .1)
        if fortitude <= 100:
            fortitude = 100

        if opponent_card.usedsummon == False:
            attack_calculation = round((.10 * opponent_card.attack))
            defense_calculation = round((.10 * opponent_card.defense))
            opponent_card.attack = opponent_card.attack + attack_calculation
            opponent_card.defense = opponent_card.defense + defense_calculation
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ increased power! {opponent_card.name} increased their stamina 🌀 and Power [ +🗡️ {attack_calculation} | +🛡️{defense_calculation}]")
        else:
            attack_calculation = round((fortitude * (opponent_card.tier / 10)) + (.05 * opponent_card.attack))
            defense_calculation = round((fortitude * (opponent_card.tier / 10)) + (.05 * opponent_card.defense))
            opponent_card.attack = opponent_card.attack + attack_calculation
            opponent_card.defense = opponent_card.defense + defense_calculation
            battle_config.add_to_battle_log(f"({battle_config.turn_total}) ♾️ power of friendship 🧬 {opponent_card.name} summon rested, {opponent_card.name} increased their stamina 🌀 and Power [ +🗡️ {attack_calculation} | +🛡️{defense_calculation}]")
            opponent_card.usedsummon = False
        
        






