import copy 
ua_training_grounds = {
    "standing_on": "🟩",
    "spawn_portal": (10, 5),
    "map_name": "UA High School Training Grounds",
    "map_area": "UA High School",
    "embed_color": 0x0000FF,
    "map_doors": (5, 5),
    "exit_points": [(0, 5), (10, 5)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🏢", "🟩", "🟩", "🟦", "🆚", "🟩", "🆚", "🟦", "🟩", "🟩", "🏢"],
        ["🟩", "🟩", "🟩", "🟩", "🟦", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩"],
        ["🟩", "🟩", "🟦", "🟦", "🟩", "🟩", "🟩", "🟦", "🟦", "🟩", "🟩"],
        ["🟩", "🟦", "🟦", "🟦", "🟩", "🗝️", "🟩", "🟦", "🟦", "🟦", "🟩"],
        ["🟩", "🟦", "🟦", "🟩", "🆚", "🟦", "🆚", "🟩", "🟦", "🟦", "🟩"],
        ["🟦", "🟩", "🟦", "🟩", "🟩", "🚪", "🟩", "🟩", "🟦", "🟩", "🟦"],
        ["🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🆚", "🆚", "🟩", "🆚", "🆚", "🟦", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟦", "🟦", "🟩", "🟦", "🟦", "🟦", "🟦", "🟦"]
    ]
}

kamino_ward_ruins = {
    "standing_on": "🟫",
    "spawn_portal": (10, 5),
    "map_name": "Kamino Ward Ruins",
    "map_area": "Kamino Ward",
    "embed_color": 0x8B4513,
    "map_doors": (5, 5),
    "exit_points": [(0, 5), (10, 5)],
    "north_exits": None,
    "south_exits": ua_training_grounds,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🏚️", "🟫", "🟫", "🟦", "🆚", "🟫", "🟦", "🟫", "🟫", "🟫", "🏚️"],
        ["🟫", "🟫", "🟫", "🟫", "🟦", "🟫", "🟦", "🟫", "🟫", "🟫", "🟫"],
        ["🟫", "🟫", "🟦", "🟦", "🟫", "🟫", "🟫", "🟦", "🟦", "🟫", "🟫"],
        ["🟫", "🟦", "🟦", "🟦", "🟫", "🗝️", "🟫", "🟦", "🟦", "🟦", "🟫"],
        ["🟫", "🟦", "🟦", "🟫", "🆚", "🟦", "🆚", "🟫", "🟦", "🟦", "🟫"],
        ["🟦", "🟫", "🟦", "🟫", "🟫", "🚪", "🟫", "🟫", "🟦", "🟫", "🟦"],
        ["🟦", "🟦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟦", "🟦"],
        ["🟦", "🆚", "🟦", "🆚", "🆚", "🟫", "🆚", "🆚", "🟦", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟦", "🟦", "🟫", "🟦", "🟦", "🟦", "🟦", "🟦"]
    ]
}

def get_ua_training_grounds():
    ua_training_grounds = {
    "standing_on": "🟩",
    "spawn_portal": (10, 5),
    "map_name": "UA High School Training Grounds",
    "map_area": "UA High School",
    "embed_color": 0x0000FF,
    "map_doors": (5, 5),
    "exit_points": [(0, 5), (10, 5)],
    "north_exits": None,
    "south_exits": None,
    "east_exits": None,
    "west_exits": None,
    "door_exit": None,
    "map": [
        ["🏢", "🟩", "🟩", "🟦", "🆚", "🟩", "🆚", "🟦", "🟩", "🟩", "🏢"],
        ["🟩", "🟩", "🟩", "🟩", "🟦", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩"],
        ["🟩", "🟩", "🟦", "🟦", "🟩", "🟩", "🟩", "🟦", "🟦", "🟩", "🟩"],
        ["🟩", "🟦", "🟦", "🟦", "🟩", "🗝️", "🟩", "🟦", "🟦", "🟦", "🟩"],
        ["🟩", "🟦", "🟦", "🟩", "🆚", "🟦", "🆚", "🟩", "🟦", "🟦", "🟩"],
        ["🟦", "🟩", "🟦", "🟩", "🟩", "🚪", "🟩", "🟩", "🟦", "🟩", "🟦"],
        ["🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟩", "🟩", "🟩", "🟩", "🟩", "🟩", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🆚", "🆚", "🟩", "🆚", "🆚", "🟦", "🟦", "🟦"],
        ["🟦", "🟦", "🟦", "🟦", "🟦", "🟩", "🟦", "🟦", "🟦", "🟦", "🟦"]
    ]
    }
    ua_training_grounds['north_exits']  = get_kamino_ward_ruins()
    ua_training_grounds_map = copy.deepcopy(ua_training_grounds)

def get_kamino_ward_ruins():
    kamino_ward_ruins = {
        "standing_on": "🟫",
        "spawn_portal": (10, 5),
        "map_name": "Kamino Ward Ruins",
        "map_area": "Kamino Ward",
        "embed_color": 0x8B4513,
        "map_doors": (5, 5),
        "exit_points": [(0, 5), (10, 5)],
        "north_exits": None,
        "south_exits": copy.deepcopy(ua_training_grounds),
        "east_exits": None,
        "west_exits": None,
        "door_exit": None,
        "map": [
            ["🏚️", "🟫", "🟫", "🟦", "🆚", "🟫", "🟦", "🟫", "🟫", "🟫", "🏚️"],
            ["🟫", "🟫", "🟫", "🟫", "🟦", "🟫", "🟦", "🟫", "🟫", "🟫", "🟫"],
            ["🟫", "🟫", "🟦", "🟦", "🟫", "🟫", "🟫", "🟦", "🟦", "🟫", "🟫"],
            ["🟫", "🟦", "🟦", "🟦", "🟫", "🗝️", "🟫", "🟦", "🟦", "🟦", "🟫"],
            ["🟫", "🟦", "🟦", "🟫", "🆚", "🟦", "🆚", "🟫", "🟦", "🟦", "🟫"],
            ["🟦", "🟫", "🟦", "🟫", "🟫", "🚪", "🟫", "🟫", "🟦", "🟫", "🟦"],
            ["🟦", "🟦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟦", "🟦"],
            ["🟦", "🟦", "🟦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟦", "🟦"],
            ["🟦", "🟦", "🟦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟦", "🟦"],
            ["🟦", "🆚", "🟦", "🆚", "🆚", "🟫", "🆚", "🆚", "🟦", "🟦", "🟦"],
            ["🟦", "🟦", "🟦", "🟦", "🟦", "🟫", "🟦", "🟦", "🟦", "🟦", "🟦"]
        ]
    }
    kamino_ward_ruins_map = copy.deepcopy(kamino_ward_ruins)
    return kamino_ward_ruins_map

ua_training_grounds["north_exits"] = kamino_ward_ruins