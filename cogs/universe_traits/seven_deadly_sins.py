import crown_utilities


def increase_power(player_card, battle_config, opponent_card):
    if opponent_card.universe == "7ds":
        opponent_card.stamina = opponent_card.stamina + 60
        opponent_card.usedsummon = False
        battle_config.add_to_battle_log(f"({battle_config.turn_total}) 🩸 power of friendship 🧬 {opponent_card.name}' summon rested, {opponent_card.name} increased their stamina 🌀")






