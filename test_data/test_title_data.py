# UNLOCK METHOD
# Tales completed in TALES_STATS
# Tales run in TALES_STATS
# Dungeons completed in DUNGEON_STATS
# Dungeons run in DUNGEON_STATS
# Healed in TALES_STATS
# Damage Taken in TALES_STATS
# Damage Dealt in TALES_STATS
# Healed in DUNGEON_STATS
# Damage Taken in DUNGEON_STATS
# Damage Dealt in DUNGEON_STATS
# Healed in BOSS_STATS
# Damage Taken in BOSS_STATS
# Damage Dealt in BOSS_STATS
# Specific Element Damage Dealt in universe
# None / Picked from scenario window

title_explanations = {
    'ATK': 'Increases your attack by % each turn',
    'DEF': 'Increases your defense by % each turn',
    'STAM': 'Increases your stamina by % each turn',
    'HLT': 'Heals you for % of your current health each turn',
    'LIFE': 'Steals % of your opponent\'s health each turn',
    'DRAIN': 'Drains % each turn',
    'FLOG': 'Steals % each turn',
    'WITHER': 'Steals % each turn',
    'RAGE': 'Decreases your defense to increase your AP by % each turn',
    'BRACE': 'Decreases your attack to increase your AP by % each turn',
    'BZRK': 'Decreases your health to increase your attack by % each turn',
    'CRYSTAL': 'Decreases your health to increase your defense by % each turn',
    'GROWTH': 'Decreases your max health to increase your attack, defense, and AP by % each turn',
    'FEAR': 'Decreases your max health to decrease your opponents attack, defense, and AP by % each turn',
    'STANCE': 'Swaps your attack and defense stats, increasing your attack by % each turn',
    'CONFUSE': 'Swaps opponents attack and defense stats, decreasing their attack by % each turn',
    'CREATION': 'Increases your max health by % each turn',
    'DESTRUCTION': 'Decreases opponent max health by % each turn',
    'SPEED': 'Increases your speed by % each focus',
    'SLOW': 'Decreases turn count by Turn',
    'HASTE': 'Increases turn count by Turn',
    'SOULCHAIN': 'Prevents focus stat buffs',
    'GAMBLE': 'Randomizes focus stat buffs',
    'SINGULARITY': 'Increases resolve buff by %',
    'IQ': 'Increases focus buffs by %',
    'HIGH IQ': 'Continues focus buffs after resolve',
    'BLITZ': 'Hit through parries',
    'FORESIGHT': 'Parried hits deal 10% damage to yourself',
    'OBLITERATE': 'Hit through shields',
    'IMPENETRABLE SHIELD': 'Shields cannot be penetrated',
    'PIERCE': 'Hit through all barriers',
    'SYNTHESIS': 'Hits to your barriers store 50% of damage dealt, you heal from this amount on resolve.',
    'SPELL SHIELD': 'All shields will absorb elemental damage healing you',
    'ELEMENTAL BUFF': 'Increase elemental damage by 35% each turn',
    'ELEMENTAL DEBUFF': 'Decrease elemental damage by 35% each turn',
    'ENHANCED GUARD': 'Negates 80% of damage when blocking, prevents critical hits.',
    'STRATEGIST': 'Hits through all guards',
    'SHARPSHOOTER': 'Attacks never miss',
    'DIVINITY': 'Ignore elemental effects until resolved',
}


test_title_1 = {
    "TITLE": 'Uzumaki',
    "ABILITIES": [
        {
            "ABILITY": "ATK",
            "POWER": 10,
            "ELEMENT": "",
            "DURATION": 0,
        }
    ],
    "UNIVERSE": "Naruto",
    "TIMESTAMP": "Thu Jun 17 01:11:44 2021",
    "AVAILABLE": True,
    "RARITY": 5,
    "UNLOCK_METHOD": {
        "METHOD": "TALES COMPLETED",
        "VALUE": 1,
        "ELEMENT": "",
        "SCENARIO_DROP": False
    }
}


test_title_2 = {
    "TITLE": 'Uchiha',
    "ABILITIES": [
        {
            "ABILITY": "FORESIGHT",
            "POWER": 0,
            "ELEMENT": "",
            "DURATION": 0,
        }
    ],
    "UNIVERSE": "Naruto",
    "TIMESTAMP": "Thu Jun 17 01:11:44 2021",
    "AVAILABLE": True,
    "RARITY": 4,
    "UNLOCK_METHOD": {
        "METHOD": "ELEMENTAL DAMAGE DEALT",
        "VALUE": 5000,
        "ELEMENT": "FIRE",
        "SCENARIO_DROP": False
    }
}


test_title_3 = {
    "TITLE": 'Hyuga',
    "ABILITIES": [
        {
            "ABILITY": "SINGULARITY",
            "POWER": 0,
            "ELEMENT": "",
            "DURATION": 0,
        }
    ],
    "UNIVERSE": "Naruto",
    "TIMESTAMP": "Thu Jun 17 01:11:44 2021",
    "AVAILABLE": True,
    "RARITY": 4,
    "UNLOCK_METHOD": {
        "METHOD": "DUNGEONS COMPLETED",
        "VALUE": 15,
        "ELEMENT": "",
        "SCENARIO_DROP": False
    }
}


test_title_4 = {
    "TITLE": 'Hokage',
    "ABILITIES": [
        {
            "ABILITY": "PIERCE",
            "POWER": 0,
            "ELEMENT": "",
            "DURATION": 0,
        },
        {
            "ABILITY": "IMPENETRABLE SHIELD",
            "POWER": 0,
            "ELEMENT": "",
            "DURATION": 0,
        },
        {
            "ABILITY": "BLITZ",
            "POWER": 0,
            "ELEMENT": "",
            "DURATION": 0,
        }
    ],
    "UNIVERSE": "Naruto",
    "TIMESTAMP": "Thu Jun 17 01:11:44 2021",
    "AVAILABLE": True,
    "RARITY": 5,
    "UNLOCK_METHOD": {
        "METHOD": "",
        "VALUE": 0,
        "ELEMENT": "",
        "SCENARIO_DROP": True
    }
}





