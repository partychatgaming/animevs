import copy

default_map = {
    "standing_on": "🟩",
    "spawn_portal": (10, 5),
    "map_name": "Damp Woodlands",
    "map_area": "Forest Training Grounds",
    "embed_color": 0x00FF00,
    "map_doors": (1, 5),
    "exit_points": [(0, 3), (0, 7), (1, 5)],
    "north_exits": None,  # Map 4
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "playerid": None,
    "map": [
        ["🌳", "🌳", "🟩", "🟦", "⬛", "⬛", "⬛", "🟩", "🌳", "🌳", "🌳"],
        ["🌳", "🟩", "🟩", "🟦", "⬛", "🚪", "⬛", "🟩", "🌳", "🏯", "🌳"],
        ["🌳", "🟩", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟦", "🟩", "🟩", "🌳", "🌳", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🌳", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🌳", "🌳", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🌉", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🪨", "🌳"],
        ["🌳", "🌳", "🟦", "🏪", f"🌳", "🟩", "🌳", "🌳", "🌳", "🌳", "🌳"]
        ]
    }

damp_woodlands = {
    "standing_on": "🟩",
    "spawn_portal": (10, 5),
    "map_name": "Damp Woodlands",
    "map_area": "Forest Training Grounds",
    "embed_color": 0x00FF00,
    "map_doors": (1, 5),
    "exit_points": [(0, 3), (0, 7), (1, 5)],
    "north_exits": None,  # Map 4
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "playerid": None,
    "map": [
        ["🌳", "🌳", "🟩", "🟦", "⬛", "⬛", "⬛", "🟩", "🌳", "🌳", "🌳"],
        ["🌳", "🟩", "🟩", "🟦", "⬛", "🚪", "⬛", "🟩", "🌳", "🏯", "🌳"],
        ["🌳", "🟩", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟦", "🟩", "🟩", "🌳", "🌳", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🌳", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🌳", "🌳", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🌉", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🪨", "🌳"],
        ["🌳", "🌳", "🟦", "🏪", f"🌳", "🟩", "🌳", "🌳", "🌳", "🌳", "🌳"]
        ]
    }

eerie_graveyard = {
    "standing_on": "🟫",
    "spawn_portal": (0, 6),
    "map_name": "Eerie Graveyard",
    "map_area": "Graveyard Training Grounds",
    "embed_color": 0x8B4513,  # Brown color
    "map_doors": None,
    "exit_points": [],
    "north_exits": copy.deepcopy(damp_woodlands),
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🌲", "🌲", "🌲", "🌲", "🌲", "🌲", "🟫", "🌲", "🌲", "🌲", "🌲"],
        ["🌲", "🪦", "🟫", "🟫", "🪦", "🟫", "🟫", "🪦", "🟫", "🎃", "🌲"],
        ["🌲", "🟫", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🌲"],
        ["🌲", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🌲"],
        ["🌲", "🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🌲"],
        ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🪦", "🌲"],
        ["🌲", "🕴️", "🟫", "🟫", "🟦", "🌉", "🟦", "🟫", "🪦", "🌲", "🌲"],
        ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦", "🪦", "🌲"],
        ["🌲", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🟫", "🟫", "🪦", "🌲"],
        ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "☠️", "🪦", "🌲"],
        ["🌲", "🪦", "🪦", "🪦", "🪦","🪦" , "🪦", "🪦", "🪦", "🪦", "🌲"]
        ]
    }

large_tunnel = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Large Tunnel",
    "map_area": "Underground Passage",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(0, 6)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🆚", "⬛", "⬛", "🪨", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🪨", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "⬛", "🟫", "🟫", "🟫", "⬛", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "⬛", "🟫", "🟫", "🟫", "⬛", "⬛", "🟫", "🟦"],
        ["🟦", "🟦", "🌉", "🟦", "🟦", "🌉", "🟦", "🟦", "🟦", "🌉", "🟦"],
        ["🟦", "🟫", "🟫", "⬛", "⬛", "🟫", "⬛", "⬛", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }

crystal_caverns = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Crystal Caverns",
    "map_area": "Underground Training Grounds",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(10, 5)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🟫", "🪨", "🟫", "⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🪨", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🆚", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🪨", "🟫", "🟫", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "🟫", "🪨", "⬛", "⬛", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "⬛", "🟫", "⬛", "⬛", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🪨", "⬛", "🟫", "⬛", "⬛", "🧙", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛", "⬛", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }





frosty_peaks = {
    "standing_on": "⬜",
    "spawn_portal": (9, 0),
    "map_name": "Frosty Peaks",
    "map_area": "Frozen Training Grounds",
    "embed_color": 0xFFFFFF,
    "map_doors": (4, 5),
    "exit_points": [(9, 0), (0, 9), (5,4)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🟦", "🏔️", "⬜", "🏔️", "🏔️"],
        ["🏔️", "🏪", "⬜", "⬜", "⬜", "⬜", "🌉", "⬜", "⬜", "🏯", "🏔️"],
        ["🏔️", "⬜", "⬜", "⬜", "⬜", "⬜", "🟦", "🟦", "⬜", "⬜", "🏔️"],
        ["🏔️", "⬜", "⬜", "⬜", "⬛", "⬛", "⬛", "🟦", "⬜", "⬜", "🏔️"],
        ["🟦", "⬜", "⬜", "⬜", "⬛", "🚪", "⬛", "🟦", "⬜", "⬜", "⬜"],
        ["🟦", "🌉", "🟦", "⬜", "🎄", "⬜", "🟦", "🟦", "⬜", "⬜", "🏔️"],
        ["🏔️", "⬜", "🟦", "⬜", "⬜", "⬜", "🟦", "⬜", "⬜", "👩‍🦰", "🏔️"],
        ["🏔️", "⬜", "🟦", "🟦", "🟦", "🟦", "🟦", "⬜", "🏔️", "⬜", "🏔️"],
        ["🏔️", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "🏔️", "⬜", "🏔️"],
        ["⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "🎁", "🏔️", "💰", "🏔️"],
        ["🏔️", "🏔️", "🏔️", "🏔️", "🏔️","🏔️" , "🏔️", "🏔️", "🏔️", "🏔️", "🏔️"]
    ]
    }

mountain_mines = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Mountain Mines",
    "map_area": "Underground Training Grounds",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(10, 5)],
    "north_exits": None,
    "south_exits": copy.deepcopy(frosty_peaks),
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "💎", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "💎", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "💎", "🆚", "🟫", "🟫", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "💎", "💎", "🟫", "🟫", "🟫", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "💎", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "🟫", "🟫", "💎", "💎", "💎", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "🟫", "💎", "🟫", "🟫", "🟫", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "🟫", "💎", "💎", "💎", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "💎", "🆚", "🟫", "🟫", "🟫", "💎", "🟫", "🆚", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }

scorched_lands = {
    "standing_on": "🟨",
    "spawn_portal": (5, 10),
    "map_name": "Scorched Lands",
    "map_area": "Fiery Training Grounds",
    "embed_color": 0xFFD700,
    "map_doors": (1, 2),
    "exit_points": [(5, 10), (0, 5), (1, 2)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🟨", "⬛", "⬛", "⬛", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "⬛", "🚪", "⬛", "🟨", "🟨", "🌉", "🟨", "🏪", "🟨", "🟨"],
        ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🌵", "🟨"],
        ["🟦", "🟦", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "🟦", "💰", "🟨", "🟨", "🟦", "🟦", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "🟦", "🟦", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "🟨", "🟦", "🌉", "🟦", "🟦", "🟦", "🟨", "🟨", "🌵", "🟨"],
        ["🟨", "🌵", "🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🟨", "🟨", "🟨"],
        ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨"],
        ["🟨", "🟨", "🌵", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🪨", "🟨"],
        ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🟦"]
    ]
    }
desert_dunes = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Desert Dunes",
    "map_area": "Underground Training Grounds",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(10, 5)],
    "north_exits": None,
    "south_exits": copy.deepcopy(scorched_lands),
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🎒", "🎒", "💎", "🎁", "🎁", "🎁", "💎", "🎒", "🎒", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🎁", "🎁", "🎁", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🎁", "🆚", "🎁", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟨", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟨", "🟨", "🟨", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟨", "⚔️", "🟨", "⚔️", "🟨", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟨", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }

pocket_dimension = {
        "standing_on": "🟩",
        "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
        "map_name": "Pocket Dimension",
        "map_area": "Geostorm",
        "embed_color": 0xFFFFFF,
        "map_doors": None,
        "exit_points": [(10, 5)],
        "north_exits": None,
        "south_exits": copy.deepcopy(damp_woodlands),
        "east_exits": copy.deepcopy(frosty_peaks),
        "west_exits": copy.deepcopy(scorched_lands),
        "door_exit": None,
        "map": [
                ["🟨", "🟨", "🟨", "🟦", "🟦", "🏯", "🟦", "🟦", "⬜", "◼️", "⬜"],
                ["◼️", "◼️", "◼️", "🌉", "◼️", "◼️", "◼️", "🌉", "◼️", "◼️", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "🟫", "🟩", "🟩", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "🌳", "🟩", "🌳", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "🟫", "🟩", "🟩", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟦", "🟦", "🟫", "🟩", "🟩", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟦", "🌳", "🟫", "🟩", "🟩", "🌉", "◼️", "◼️", "⬜"],
                ["🟨", "🟨", "🟦", "🟫", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"],
                ["🟨", "🟦", "🟦", "🟫", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"],
                ["🟨", "🟦", "🟫", "🟫", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"],
                ["🟦", "🟦", "🟫", "🟩", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"]
            ]
        }



concrete_jungle = {
        "standing_on": "◼️",
        "spawn_portal": (10, 5),
        "map_name": "Concrete Jungle (PM)",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": [(10,5)],
        "north_exits": None,
        "south_exits": copy.deepcopy(pocket_dimension),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
            ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
            ["🏢", "🟦", "🟩", "🟩", "◼️", "◼️", "🏢", "◼️", "◼️", "◼️", "🏢"],
            ["🏢", "🟩", "🟩", "🟩", "◼️", "◼️", "🏢", "◼️", "◼️", "◼️", "🏢"],
            ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
            ["🏢", "🏢", "◼️", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
            ["🏢", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🏢"],
            ["🏢", "◼️", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "◼️", "🏢"],
            ["🏢", "◼️", "🏢", "🏯", "🏢", "◼️", "🏢", "🏪", "🏢", "◼️", "🏢"],
            ["🏢", "◼️", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢", "◼️", "🏢"],
            ["🏢", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🏢"],
            ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "🏢", "🏢", "🏢", "🏢"]
        ]
    }

concrete_jungle_am = {
        "standing_on": "◼️",
        "spawn_portal": (10, 5),
        "map_name": "Concrete Jungle (AM)",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": [(10,5)],
        "north_exits": None,
        "south_exits": copy.deepcopy(pocket_dimension),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
        ["🌆", "🟦", "🟩", "🟩", "◼️", "◼️", "🌆", "◼️", "◼️", "🧱", "🌆"],
        ["🌆", "🟩", "🟩", "🟩", "◼️", "◼️", "🌆", "◼️", "◼️", "◼️", "🌆"],
        ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
        ["🌆", "🌆", "◼️", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
        ["🌆", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🌆"],
        ["🌆", "◼️", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆"],
        ["🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆", "🏪", "🌆", "◼️", "🌆"],
        ["🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆", "◼️", "🌆"],
        ["🌆", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🌆"],
        ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "🌆", "🌆", "🌆", "🌆"]
        ]
    }

concrete_jungle_pm = {
        "standing_on": "◼️",
        "spawn_portal": (10, 5),
        "map_name": "Concrete Jungle (Nightlife)",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": [(10,5)],
        "north_exits": None,
        "south_exits": copy.deepcopy(pocket_dimension),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
        ["🌃", "🟦", "🟩", "🟩", "◼️", "◼️", "🌃", "◼️", "🧙", "◼️", "🌃"],
        ["🌃", "🟩", "🟩", "🟩", "◼️", "◼️", "🌃", "◼️", "◼️", "◼️", "🌃"],
        ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
        ["🌃", "🌃", "🕵️‍♂️", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
        ["🌃", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🌃"],
        ["🌃", "◼️", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "◼️", "🌃"],
        ["🌃", "◼️", "🌃", "🏯", "🌃", "◼️", "🌃", "🏪", "🌃", "◼️", "🌃"],
        ["🌃", "◼️", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃", "◼️", "🌃"],
        ["🌃", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🌃"],
        ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "🌃", "🌃", "🌃", "🌃"]
        ]
    }

boss_room_1 = {
        "standing_on": "🟪",
        "spawn_portal": (10, 5),
        "map_name": "Ethereal Plane",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": "Boss",
        "north_exits": None,
        "south_exits": None,
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃"],
        ["🌃", "☠️", "🦴", "🟪", "⚔️", "⚔️", "⚔️", "🟪", "🦴", "☠️", "🌃"],
        ["🌃", "🆚", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🆚", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "🟪", "👹", "🟪", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "☠️", "🟪", "☠️", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "☠️", "🟪", "☠️", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "🆚", "🟪", "🟪", "☠️", "🟪", "☠️", "🟪", "🟪", "🆚", "🌃"],
        ["🌃", "☠️", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "☠️", "🌃"],
        ["🌃", "🌃", "🌃", "🌃", "🌃", "🟪", "🌃", "🌃", "🌃", "🌃", "🌃"]
        ]
    }

boss_room_2 = {
        "standing_on": "🟪",
        "spawn_portal": (10, 5),
        "map_name": "Ethereal Plane",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": "Boss",
        "north_exits": None,
        "south_exits": None,
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "👹", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "⚔️", "🟪", "⚔️", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🌆", "🌆", "🌆", "🌆", "🟪", "🌆", "🌆", "🌆", "🌆", "🌆"]
        ]
    }

boss_room_1 = {
        "standing_on": "🟪",
        "spawn_portal": (10, 5),
        "map_name": "Ethereal Plane",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": "Boss",
        "north_exits": None,
        "south_exits": None,
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "👹", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🆙", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "💗", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🏢", "🏢", "🏢", "🏢", "🟪", "🏢", "🏢", "🏢", "🏢", "🏢"]
        ]
    }

def get_damp_woodlands():
    damp_woodlands = {
    "standing_on": "🟩",
    "spawn_portal": (10, 5),
    "map_name": "Damp Woodlands",
    "map_area": "Forest Training Grounds",
    "embed_color": 0x00FF00,
    "map_doors": (1, 5),
    "exit_points": [(0, 3), (0, 7), (1, 5)],
    "north_exits": None,  # Map 4
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "playerid": None,
    "map": [
        ["🌳", "🌳", "🟩", "🟦", "⬛", "⬛", "⬛", "🟩", "🌳", "🌳", "🌳"],
        ["🌳", "🟩", "🟩", "🟦", "⬛", "🚪", "⬛", "🟩", "🌳", "🏯", "🌳"],
        ["🌳", "🟩", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟦", "🟩", "🟩", "🌳", "🌳", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🌳", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🌳", "🌳", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🌉", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
        ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🪨", "🌳"],
        ["🌳", "🌳", "🟦", "🏪", f"🌳", "🟩", "🌳", "🌳", "🌳", "🌳", "🌳"]
        ]
    }
    damp_woodlands['south_exits'] = get_eerie_graveyard()
    damp_woodlands['north_exits'] = get_pocket_dimension()
    damp_woodlands['door_exit'] = get_large_tunnel()
    damp_woodlands_map = copy.deepcopy(damp_woodlands)
    return damp_woodlands_map

def get_eerie_graveyard():
    eerie_graveyard = {
    "standing_on": "🟫",
    "spawn_portal": (0, 6),
    "map_name": "Eerie Graveyard",
    "map_area": "Graveyard Training Grounds",
    "embed_color": 0x8B4513,  # Brown color
    "map_doors": None,
    "exit_points": [],
    "north_exits": copy.deepcopy(damp_woodlands),
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🌲", "🌲", "🌲", "🌲", "🌲", "🌲", "🟫", "🌲", "🌲", "🌲", "🌲"],
        ["🌲", "🪦", "🟫", "🟫", "🪦", "🟫", "🟫", "🪦", "🟫", "🎃", "🌲"],
        ["🌲", "🟫", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🌲"],
        ["🌲", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🌲"],
        ["🌲", "🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🌲"],
        ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🪦", "🌲"],
        ["🌲", "🕴️", "🟫", "🟫", "🟦", "🌉", "🟦", "🟫", "🪦", "🌲", "🌲"],
        ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦", "🪦", "🌲"],
        ["🌲", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🟫", "🟫", "🪦", "🌲"],
        ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "☠️", "🪦", "🌲"],
        ["🌲", "🪦", "🪦", "🪦", "🪦","🪦" , "🪦", "🪦", "🪦", "🪦", "🌲"]
        ]
    }
    #eerie_graveyard['north_exits'] = get_damp_woodlands()
    eerie_graveyard_map = copy.deepcopy(eerie_graveyard)
    return eerie_graveyard_map

def get_large_tunnel():
    large_tunnel = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Large Tunnel",
    "map_area": "Underground Passage",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(0, 6)],
    "north_exits": None,
    "south_exits": copy.deepcopy(damp_woodlands),
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🆚", "⬛", "⬛", "🪨", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🪨", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "⬛", "🟫", "🟫", "🟫", "⬛", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "⬛", "🟫", "🟫", "🟫", "⬛", "⬛", "🟫", "🟦"],
        ["🟦", "🟦", "🌉", "🟦", "🟦", "🌉", "🟦", "🟦", "🟦", "🌉", "🟦"],
        ["🟦", "🟫", "🟫", "⬛", "⬛", "🟫", "⬛", "⬛", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }
    large_tunnel['north_exits'] = get_crystal_caverns()
    #large_tunnel['south_exits'] = get_damp_woodlands()
    large_tunnel_map = copy.deepcopy(large_tunnel)
    return large_tunnel_map

def get_crystal_caverns():
    crystal_caverns = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Crystal Caverns",
    "map_area": "Underground Training Grounds",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(10, 5)],
    "north_exits": None,
    "south_exits": copy.deepcopy(large_tunnel),
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🟫", "🪨", "🟫", "⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🪨", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🆚", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🪨", "🟫", "🟫", "🟫", "🟫", "🟫", "🪨", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "🟫", "🪨", "⬛", "⬛", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "⬛", "🟫", "⬛", "⬛", "🟫", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🪨", "⬛", "🟫", "⬛", "⬛", "🧙", "⬛", "🟫", "⬛"],
        ["⬛", "⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛", "⬛", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }
    #crystal_caverns['south_exits'] = get_large_tunnel()
    crystal_caverns_map = copy.deepcopy(crystal_caverns)
    return crystal_caverns_map


def get_pocket_dimension():
    pocket_dimension = {
        "standing_on": "🟩",
        "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
        "map_name": "Pocket Dimension",
        "map_area": "Geostorm",
        "embed_color": 0xFFFFFF,
        "map_doors": None,
        "exit_points": [(10, 5)],
        "north_exits": None,
        "south_exits": copy.deepcopy(damp_woodlands),
        "east_exits": copy.deepcopy(frosty_peaks),
        "west_exits": copy.deepcopy(scorched_lands),
        "door_exit": None,
        "map": [
                ["🟨", "🟨", "🟨", "🟦", "🟦", "🏯", "🟦", "🟦", "⬜", "◼️", "⬜"],
                ["◼️", "◼️", "◼️", "🌉", "◼️", "◼️", "◼️", "🌉", "◼️", "◼️", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "🟫", "🟩", "🟩", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "🌳", "🟩", "🌳", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟨", "🟦", "🟫", "🟩", "🟩", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟦", "🟦", "🟫", "🚪", "🟩", "🟦", "⬜", "◼️", "⬜"],
                ["🟨", "🟨", "🟦", "🌳", "🟫", "🟩", "🟩", "🌉", "◼️", "◼️", "⬜"],
                ["🟨", "🟨", "🟦", "🟫", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"],
                ["🟨", "🟦", "🟦", "🟫", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"],
                ["🟨", "🟦", "🟫", "🟫", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"],
                ["🟦", "🟦", "🟫", "🟩", "🟩", "🟩", "🟩", "🟦", "⬜", "⬜", "⬜"]
            ]
        }
    city_time = choose_map_time()
    pocket_dimension['north_exits'] = copy.deepcopy(city_time)
    pocket_dimension['east_exits'] = get_frosty_peaks()
    pocket_dimension['west_exits'] = get_scorched_lands()
    #pocket_dimension["south_exits"] = get_damp_woodlands()
    pocket_dimension_map = copy.deepcopy(pocket_dimension)
    return pocket_dimension_map



def get_scorched_lands():
    scorched_lands = {
    "standing_on": "🟨",
    "spawn_portal": (5, 10),
    "map_name": "Scorched Lands",
    "map_area": "Fiery Training Grounds",
    "embed_color": 0xFFD700,
    "map_doors": (1, 2),
    "exit_points": [(5, 10), (0, 5), (1, 2)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": copy.deepcopy(pocket_dimension),
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🟨", "⬛", "⬛", "⬛", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "⬛", "🚪", "⬛", "🟨", "🟨", "🌉", "🟨", "🏪", "🟨", "🟨"],
        ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🌵", "🟨"],
        ["🟦", "🟦", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "🟦", "🟨", "🟨", "🟨", "🟦", "🟦", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "🟦", "🟦", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨", "🟨"],
        ["🟨", "🟨", "🟦", "🌉", "🟦", "🟦", "🟦", "🟨", "🟨", "🌵", "🟨"],
        ["🟨", "🌵", "🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🟨", "🟨", "🟨"],
        ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨"],
        ["🟨", "🟨", "🌵", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🪨", "🟨"],
        ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🟦"]
    ]
    }
    #scorched_lands['south_exits'] = get_pocket_dimension()
    scorched_lands['door_exit'] = get_desert_dunes()
    scorched_lands_map = copy.deepcopy(scorched_lands)
    return scorched_lands_map


def get_frosty_peaks():
    frosty_peaks = {
    "standing_on": "⬜",
    "spawn_portal": (9, 0),
    "map_name": "Frosty Peaks",
    "map_area": "Frozen Training Grounds",
    "embed_color": 0xFFFFFF,
    "map_doors": (4, 5),
    "exit_points": [(9, 0), (0, 9), (5,4)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": copy.deepcopy(pocket_dimension),
    "door_exit": None,
    "map": [
        ["🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🟦", "🏔️", "⬜", "🏔️", "🏔️"],
        ["🏔️", "🏪", "⬜", "⬜", "⬜", "⬜", "🌉", "⬜", "⬜", "🏯", "🏔️"],
        ["🏔️", "⬜", "⬜", "⬜", "⬜", "⬜", "🟦", "🟦", "⬜", "⬜", "🏔️"],
        ["🏔️", "⬜", "⬜", "⬜", "⬛", "⬛", "⬛", "🟦", "⬜", "⬜", "🏔️"],
        ["🟦", "⬜", "⬜", "⬜", "⬛", "🚪", "⬛", "🟦", "⬜", "⬜", "⬜"],
        ["🟦", "🌉", "🟦", "⬜", "🎄", "⬜", "🟦", "🟦", "⬜", "⬜", "🏔️"],
        ["🏔️", "⬜", "🟦", "⬜", "⬜", "⬜", "🟦", "⬜", "⬜", "⬜", "🏔️"],
        ["🏔️", "⬜", "🟦", "🟦", "🟦", "🟦", "🟦", "⬜", "🏔️", "⬜", "🏔️"],
        ["🏔️", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "🏔️", "⬜", "🏔️"],
        ["⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "⬜", "🎁", "🏔️", "💰", "🏔️"],
        ["🏔️", "🏔️", "🏔️", "🏔️", "🏔️","🏔️" , "🏔️", "🏔️", "🏔️", "🏔️", "🏔️"]
    ]
    }
    #frosty_peaks['west_exits'] = get_pocket_dimension()
    frosty_peaks['door_exit'] = get_mountain_mines()
    frosty_peaks_map = copy.deepcopy(frosty_peaks)
    return frosty_peaks_map



def get_concrete_jungle():
    concrete_jungle = {
        "standing_on": "◼️",
        "spawn_portal": (10, 5),
        "map_name": "Concrete Jungle (PM)",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": [(10,5)],
        "north_exits": copy.deepcopy(choose_boss_room()),
        "south_exits": copy.deepcopy(pocket_dimension),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
            ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
            ["🏢", "🟦", "🟩", "🟩", "◼️", "◼️", "🏢", "◼️", "◼️", "◼️", "🏢"],
            ["🏢", "🟩", "🟩", "🟩", "◼️", "◼️", "🏢", "◼️", "◼️", "◼️", "🏢"],
            ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
            ["🏢", "🏢", "🕵️‍♂️", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
            ["🏢", "🚓", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🏢"],
            ["🏢", "◼️", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "◼️", "🏢"],
            ["🏢", "◼️", "🏢", "🏯", "🏢", "◼️", "🏢", "🏪", "🏢", "◼️", "🏢"],
            ["🏢", "◼️", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢", "◼️", "🏢"],
            ["🏢", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🏢"],
            ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "🏢", "🏢", "🏢", "🏢"]
        ]
        }
    #concrete_jungle['south_exits'] = get_pocket_dimension()
    concrete_jungle_map = copy.deepcopy(concrete_jungle)
    return concrete_jungle_map


def get_concrete_jungle_am():
    concrete_jungle_am = {
        "standing_on": "◼️",
        "spawn_portal": (10, 5),
        "map_name": "Concrete Jungle (AM)",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": [(10,5)],
        "north_exits": copy.deepcopy(choose_boss_room()),
        "south_exits": copy.deepcopy(pocket_dimension),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
        ["🌆", "🟦", "🟩", "🟩", "◼️", "◼️", "🌆", "◼️", "◼️", "🧱", "🌆"],
        ["🌆", "🟩", "🟩", "🟩", "◼️", "◼️", "🌆", "◼️", "◼️", "◼️", "🌆"],
        ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
        ["🌆", "🌆", "◼️", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
        ["🌆", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🌆"],
        ["🌆", "◼️", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆"],
        ["🌆", "◼️", "🌆", "🏯", "🌆", "◼️", "🌆", "🏪", "🌆", "◼️", "🌆"],
        ["🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆", "◼️", "🌆"],
        ["🌆", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🌆"],
        ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "🌆", "🌆", "🌆", "🌆"]
        ]
    }
    concrete_jungle_am['south_exits'] = get_pocket_dimension()
    concrete_jungle_am_map = copy.deepcopy(concrete_jungle_am)
    return concrete_jungle_am_map

def get_concrete_jungle_pm():
    concrete_jungle_pm = {
        "standing_on": "◼️",
        "spawn_portal": (10, 5),
        "map_name": "Concrete Jungle (Nightlife)",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": [(10,5)],
        "north_exits": copy.deepcopy(choose_boss_room()),
        "south_exits": copy.deepcopy(pocket_dimension),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌃", "🌃", "🌃", "🌃", "🌃", "🚓", "🌃", "◼️", "🌃", "🌃", "🌃"],
        ["🌃", "🟦", "🟩", "🟩", "◼️", "◼️", "🌃", "◼️", "🧙", "◼️", "🌃"],
        ["🌃", "🟩", "🟩", "🟩", "◼️", "◼️", "🌃", "◼️", "◼️", "◼️", "🌃"],
        ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
        ["🌃", "🌃", "🕵️‍♂️", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
        ["🌃", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🌃"],
        ["🌃", "🚓", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "◼️", "🌃"],
        ["🌃", "◼️", "🌃", "🏯", "🌃", "◼️", "🌃", "🏪", "🌃", "◼️", "🌃"],
        ["🌃", "◼️", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃", "◼️", "🌃"],
        ["🌃", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🌃"],
        ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "🌃", "🌃", "🌃", "🌃"]
        ]
    }
    concrete_jungle_pm['south_exits'] = get_pocket_dimension()
    concrete_jungle_pm_map = copy.deepcopy(concrete_jungle_pm)
    return concrete_jungle_pm_map

def get_desert_dunes():
    desert_dunes = {
    "standing_on": "🟨",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Desert Dunes",
    "map_area": "Underground Training Grounds",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(10, 5)],
    "north_exits": None,
    "south_exits": copy.deepcopy(scorched_lands),
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🎒", "🎒", "💎", "🎁", "🎁", "🎁", "💎", "🎒", "🎒", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🎁", "🎁", "🎁", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🎁", "🆚", "🎁", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟨", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟨", "🟨", "🟨", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟨", "⚔️", "🟨", "⚔️", "🟨", "🟫", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟨", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }
    #desert_dunes['south_exits'] = get_scorched_lands()
    desert_dunes_map = copy.deepcopy(desert_dunes)
    return desert_dunes_map

def get_mountain_mines():
    mountain_mines = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
    "map_name": "Mountain Mines",
    "map_area": "Underground Training Grounds",
    "embed_color": 0x8B4513,
    "map_doors": None,
    "exit_points": [(10, 5)],
    "north_exits": None,
    "south_exits": copy.deepcopy(frosty_peaks),
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "💎", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "💎", "🟫", "🟫", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "💎", "🆚", "🟫", "🟫", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "💎", "💎", "🟫", "🟫", "🟫", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "💎", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "🟫", "🟫", "💎", "💎", "💎", "🟫", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "🟫", "💎", "🟫", "🟫", "🟫", "💎", "🟫", "⬛"],
        ["⬛", "🟫", "💎", "🟫", "💎", "💎", "💎", "🟫", "🟫", "🟫", "⬛"],
        ["⬛", "💎", "🆚", "🟫", "🟫", "🟫", "💎", "🟫", "🆚", "🟫", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]
    }
    #mountain_mines['south_exits'] = get_frosty_peaks()
    mountain_mines_map = copy.deepcopy(mountain_mines)
    return mountain_mines_map

def get_boss_room_1():
    boss_room_1 = {
        "standing_on": "🟪",
        "spawn_portal": (10, 5),
        "map_name": "Ethereal Plane",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": "Boss",
        "north_exits": None,
        "south_exits": None,
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃", "🌃"],
        ["🌃", "☠️", "🦴", "🟪", "⚔️", "⚔️", "⚔️", "🟪", "🦴", "☠️", "🌃"],
        ["🌃", "🆚", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🆚", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "🟪", "👹", "🟪", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "☠️", "🟪", "☠️", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "☠️", "🟪", "☠️", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "⚔️", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "⚔️", "🌃"],
        ["🌃", "🆚", "🟪", "🟪", "☠️", "🟪", "☠️", "🟪", "🟪", "🆚", "🌃"],
        ["🌃", "☠️", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "☠️", "🌃"],
        ["🌃", "🌃", "🌃", "🌃", "🌃", "🟪", "🌃", "🌃", "🌃", "🌃", "🌃"]
        ]
    }
    # boss_room_1['south_exits'] = choose_map_time()
    boss_room_1_map = copy.deepcopy(boss_room_1)
    return boss_room_1_map

def get_boss_room_2():
    boss_room_2 = {
        "standing_on": "🟪",
        "spawn_portal": (10, 5),
        "map_name": "Ethereal Plane",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": "Boss",
        "north_exits": None,
        "south_exits": None,
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "👹", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🟪", "🟪", "🟪", "⚔️", "🟪", "⚔️", "🟪", "🟪", "🟪", "🌆"],
        ["🌆", "🌆", "🌆", "🌆", "🌆", "🟪", "🌆", "🌆", "🌆", "🌆", "🌆"]
        ]
    }
    # boss_room_2['south_exits'] = choose_map_time()
    boss_room_2_map = copy.deepcopy(boss_room_2)
    return boss_room_2_map

def get_boss_room_3():
    boss_room_3 = {
        "standing_on": "🟪",
        "spawn_portal": (10, 5),
        "map_name": "Ethereal Plane",
        "map_area": "City Training Grounds",
        "embed_color": 0x808080,
        "map_doors": None,
        "exit_points": "Boss",
        "north_exits": None,
        "south_exits": None,
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
        ["🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "👹", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🆙", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "💗", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🟪", "🟪", "🟦", "🟪", "🟪", "🟪", "🟦", "🟪", "🟪", "🏢"],
        ["🏢", "🏢", "🏢", "🏢", "🏢", "🟪", "🏢", "🏢", "🏢", "🏢", "🏢"]
        ]
    }
    # boss_room_3['south_exits'] = choose_map_time()
    boss_room_3_map = copy.deepcopy(boss_room_3)
    return boss_room_3_map

def choose_map_time_alternate():
    import random
    random_number = random.randint(1,3)
    if random_number == 1:
        return concrete_jungle_am
    elif random_number == 2:
        return concrete_jungle
    else:
        return concrete_jungle_pm

def choose_map_time():
    import random
    random_number = random.randint(1,3)
    if random_number == 1:
        return get_concrete_jungle_am()
    elif random_number == 2:
        return get_concrete_jungle
    else:
        return get_concrete_jungle_pm()
    
def choose_boss_room():
    import random
    random_number = random.randint(1,3)
    if random_number == 1:
        return get_boss_room_1()
    elif random_number == 2:
        return get_boss_room_2()
    else:
        return get_boss_room_3()
    
city_time = choose_map_time()
pocket_dimension['north_exits'] = copy.deepcopy(city_time)
default_map['south_exits'] = get_eerie_graveyard()
default_map['door_exit'] = get_large_tunnel()
default_map['north_exits'] = get_pocket_dimension()
default_map = copy.deepcopy(default_map)

# # map_4_dict["south_exits"] = default_map # Map 1
# # map_4_dict["west_exits"] = map_2_dict # Map 2
# # map_4_dict["east_exits"] = map_3_dict # Map 3
# # map_4_dict["north_exits"] = choose_map_time() # Map 6
# # default_map["door_exit"] = map_5_5_dict
# # default_map["south_exits"] = map_7_dict # Map 3
# # map_5_5_dict["north_exits"] = map_5_dict
# # map_5_5_dict["south_exits"] = default_map