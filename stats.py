import crown_utilities
import db
import custom_logging


def update_stats(player, battle_config, damage_dealt, damage_received, damage_healed, moves, total_complete):
    """
    This function updates the in-game statistics for the player.
    """
    try:
        player_stats = db.query_stats_by_player(player.did)

        if not player_stats:
            stats_dict = create_initial_stats(player)

            game_modes = [
                ('is_abyss_game_mode', 'ABYSS_STATS'),
                ('is_dungeon_game_mode', 'DUNGEON_STATS'),
                ('is_boss_game_mode', 'BOSS_STATS'),
                ('is_pvp_game_mode', 'PVP_STATS'),
                ('is_explore_game_mode', 'EXPLORE_STATS'),
                ('is_tales_game_mode', 'TALES_STATS'),
                ('is_scenario_game_mode', 'SCENARIO_STATS'),
                ('self.is_raid_scenario', 'RAID_STATS')
            ]

            for game_mode, stat_name in game_modes:
                if getattr(battle_config, game_mode):
                    stats_dict[stat_name].append(create_stat_entry(battle_config, damage_dealt, damage_received, damage_healed, total_completion))

            for i in range(3):
                move_element = moves[i]['element']
                move_damage_dealt = moves[i]['damage_dealt']
                
                if move_element in crown_utilities.elements:
                    stat_key = f'{move_element}_DAMAGE_DONE'
                    stats_dict[stat_key].append({
                        'UNIVERSE': battle_config.selected_universe,
                        'DAMAGE': move_damage_dealt
                    })

            response = db.create_stats(stats_dict)
        
        else:
            # Code to update existing stats
            game_modes = [
                ('is_abyss_game_mode', 'ABYSS_STATS'),
                ('is_dungeon_game_mode', 'DUNGEON_STATS'),
                ('is_boss_game_mode', 'BOSS_STATS'),
                ('is_pvp_game_mode', 'PVP_STATS'),
                ('is_explore_game_mode', 'EXPLORE_STATS'),
                ('is_tales_game_mode', 'TALES_STATS'),
                ('is_scenario_game_mode', 'SCENARIO_STATS'),
                ('self.is_raid_scenario', 'RAID_STATS')
            ]

            for game_mode, stat_name in game_modes:
                if getattr(battle_config, game_mode):
                    for universe_stats in player_stats[stat_name]:
                        if universe_stats['UNIVERSE'] == battle_config.selected_universe:
                            total_complete_inc = 0
                            if total_complete:
                                total_complete_inc = 1
                            universe_stats['TOTAL_RUNS'] += 1
                            universe_stats['TOTAL_CLEARS'] += total_complete_inc
                            universe_stats['DAMAGE_DEALT'] += damage_dealt
                            universe_stats['DAMAGE_TAKEN'] += damage_received
                            universe_stats['DAMAGE_HEALED'] += damage_healed
                            break
                    else:
                        player_stats[stat_name].append(create_stat_entry(battle_config, damage_dealt, damage_received, damage_healed, total_complete))

            for i in range(3):
                move_element = moves[i]['element']
                move_damage_dealt = moves[i]['damage_dealt']
                
                if move_element in crown_utilities.elements:
                    stat_key = f'{move_element}_DAMAGE_DONE'
                    for element_damage in player_stats[stat_key]:
                        if element_damage['UNIVERSE'] == battle_config.selected_universe:
                            element_damage['DAMAGE'] += move_damage_dealt
                            break
                    else:
                        player_stats[stat_key].append({
                            'UNIVERSE': battle_config.selected_universe,
                            'DAMAGE': move_damage_dealt
                        })

            response = db.update_stats_by_player(player.did, player_stats)

    except Exception as ex:
        custom_logging.debug(ex)
        return False


def create_initial_stats(player):
    stats_dict = {
        'DID': player.did,
        'ABYSS_STATS': [],
        'DUNGEON_STATS': [],
        'BOSS_STATS': [],
        'PVP_STATS': [],
        'EXPLORE_STATS': [],
        'TALES_STATS': [],
        'SCENARIO_STATS': [],
        'RAID_STATS': [],
        'DAMAGE_DONE': [],
        'FIRE_DAMAGE_DONE': [],
        'WATER_DAMAGE_DONE': [],
        'EARTH_DAMAGE_DONE': [],
        'WIND_DAMAGE_DONE': [],
        'LIGHT_DAMAGE_DONE': [],
        'DARK_DAMAGE_DONE': [],
        'DAMAGE_TAKEN': [],
        'ELECTRIC_DAMAGE_DONE': [],
        'ICE_DAMAGE_DONE': [],
        'POISON_DAMAGE_DONE': [],
        'BLEED_DAMAGE_DONE': [],
        'GRAVITY_DAMAGE_DONE': [],
        'TIME_DAMAGE_DONE': [],
        'PSYCHIC_DAMAGE_DONE': [],
        'RANGED_DAMAGE_DONE': [],
        'PHYSICAL_DAMAGE_DONE': [],
        'ENERGY_DAMAGE_DONE': [],
        'RECKLESS_DAMAGE_DONE': [],
        'DEATH_DAMAGE_DONE': [],
        'LIFE_DAMAGE_DONE': [],
    }
    return stats_dict


def create_stat_entry(battle_config, damage_dealt, damage_received, damage_healed, total_completion):
    total_complete_inc = 0
    if total_completion:
        total_complete_inc = 1
    stat_entry = {
        'UNIVERSE': battle_config.selected_universe,
        'TOTAL_RUNS': 1,
        'TOTAL_CLEARS': total_complete_inc,
        'DAMAGE_DEALT': damage_dealt,
        'DAMAGE_TAKEN': damage_received,
        'DAMAGE_HEALED': damage_healed
    }
    return stat_entry


