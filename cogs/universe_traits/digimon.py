import crown_utilities
import random

def digivolve(player_card, battle_config, opponent_card):
    if not player_card.used_resolve and player_card.used_focus and player_card.universe == "Digimon":
        # if battle_config.is_tutorial_game_mode and opponent_card.used_resolve is False:
        #     opponent_card.used_resolve = True
        #     embedVar = interactions.Embed(title=f"⚡**Resolve Transformation**!",
        #                             description=f"**Heal**, Boost **ATK**, and gain the ability to 🧬**Summon**!",
        #                             color=0xe91e63)
        #     embedVar.add_field(name=f"Trade Offs!",
        #                     value="Sacrifice **DEF** and **Focusing** will not increase **ATK** or **DEF**")
        #     embedVar.add_field(name=f"🧬 Summons",
        #                     value=f"🧬**Summons** will use their 🦠**Enhancers** to assist you in battle!")
        #     embedVar.set_footer(
        #         text=f"You can only enter ⚡Resolve once per match! Use the Heal Wisely!!!")
        #     battle_config.tutorial_message = embedVar

        
        fortitude = 0.0
        low = player_card.health - (player_card.health * .75)
        high = player_card.health - (player_card.health * .66)
        fortitude = round(random.randint(int(low), int(high)))
        # Resolve Scaling
        resolve_health = round(fortitude + (.5 * player_card.resolve_value))
        resolve_attack_value = round((.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))
        resolve_defense_value = round((.30 * player_card.defense) * (player_card.resolve_value / (.50 * player_card.defense)))

        player_card.stamina = player_card.stamina + player_card.resolve_value
        player_card.health = player_card.health + resolve_health
        player_card.damage_healed = player_card.damage_healed + resolve_health
        player_card.attack = round(player_card.attack + resolve_attack_value)
        player_card.defense = round(player_card.defense - resolve_defense_value)
        player_card.attack = round(player_card.attack * 1.5)
        player_card.defense = round(player_card.defense * 1.5)
        player_card.used_resolve = True
        player_card.usedsummon = False
        if battle_config.turn_total <= 5:
            player_card.attack = round(player_card.attack * 2)
            player_card.defense = round(player_card.defense * 2 )
            player_card.health = player_card.health + 500
            player_card.damage_healed = player_card.damage_healed + 500
            player_card.max_health = player_card.max_health + 500
            battle_config.add_to_battle_log(f"(**⚡**) **{player_card.name}** 🩸 Transformation: Mega Digivolution!!!")
        else:
            battle_config.add_to_battle_log(f"(**⚡**) **{player_card.name}** 🩸 Transformation: Digivolve")
    
