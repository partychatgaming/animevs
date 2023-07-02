import crown_utilities


def increase_power(player_card, battle_config, opponent_card):
    if opponent_card.universe == "7ds":
        opponent_card.stamina = opponent_card.stamina + 60
        opponent_card.usedsummon = False
        battle_config.add_to_battle_log(f"(**🌀**) 🩸 Power Of Friendship! 🧬 {opponent_card.name} Summon Rested, **{opponent_card.name}** Increased Stamina 🌀")






