from copy import deepcopy

def get_cemetery_of_ash_map():
    cemetery_of_ash = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),
    "map_name": "Cemetery of Ash",
    "map_area": "Ashen Burial Grounds",
    "embed_color": 0x8B4513,  # Brown color
    "map_doors": None,
    "exit_points": [],
    "north_exits": default_map,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🪦", "🪦", "🪦", "🪦", "🪦", "🪦", "🟫", "🪦", "🪦", "🪦", "🪦"],
        ["🪦", "🪦", "🦴", "🟫", "🟫", "🟫", "🟫", "🟫", "🌲", "🪦", "🪦"],
        ["🪦", "🟫", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🌲", "🌲", "🪦"],
        ["🪦", "🟫", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
        ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
        ["🪦", "🟫", "🟫", "🟫", "🪦", "🪦", "🪦", "🟫", "🟫", "🟫", "🪦"],
        ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
        ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
        ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🪦"],
        ["🪦",  "🪦",  "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "☠️", "🪦", "🪦"],
        ["🪦",  "🪦",  "🪦",  "🪦",  "🪦",  "🟫",  "🪦",  "🪦",  "🪦",  "🪦",  "🪦"]
        ]
    }
    cemetery_of_ash_map = copy.deepcopy(cemetery_of_ash)
    return cemetery_of_ash_map
    