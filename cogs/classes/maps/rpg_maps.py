map_1_dict = {
            "standing_on": "🟩",
            "spawn_portal": (10, 5),
            "map_name": "Damp Woodlands",
            "map_area": "Forest Training Grounds",
            "embed_color": 0x00FF00,
            "map_doors": (1, 5),
            "exit_points": [(0, 3), (0, 7), (1, 5)],
            "north_exits": map_4_dict,  # Map 4
            "south_exits": None,
            "east_exits": None,
            "west_exits": None,
            "door_exit": map_5_dict,
            "map": [
                ["🌳", "🌳", "🟩", "🟦", "⬛", "⬛", "⬛", "🟩", "🌳", "🌳", "🌳"],
                ["🌳", "🤴", "🟩", "🟦", "⬛", "🚪", "⬛", "🟩", "🌳", "🏯", "🌳"],
                ["🌳", "🟩", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟦", "🟩", "🗝️", "🌳", "🌳", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🌳", "🎁", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🌳", "🌳", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🌉", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🆚", "🟦", "🟩", "🌳", "🟩", "🌳", "🎒", "🌳", "🪨", "🌳"],
                ["🌳", "🌳", "🟦", "🏪", f"🌳", f"{self.player_token}", "🌳", "🌳", "🌳", "🌳", "🌳"]
            ]
        }


        map_1_dict = {
            "standing_on": "🟩",
            "spawn_portal": (10, 5),
            "map_name": "Damp Woodlands",
            "map_area": "Forest Training Grounds",
            "embed_color": 0x00FF00,
            "map_doors": (1, 5),
            "exit_points": [(0, 3), (0, 7), (1, 5)],
            "north_exits": map_4_dict,  # Map 4
            "south_exits": None,
            "east_exits": None,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["🌳", "🌳", "🟩", "🟦", "⬛", "⬛", "⬛", "🟩", "🌳", "🌳", "🌳"],
                ["🌳", "🤴", "🟩", "🟦", "⬛", "🚪", "⬛", "🟩", "🌳", "🏯", "🌳"],
                ["🌳", "🟩", "🟩", "🟦", "🟩", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟦", "🟩", "🗝️", "🌳", "🌳", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🌳", "🎁", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🌳", "🌳", "🟩", "🟩", "🟩", "🟩", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🟦", "🟩", "🟩", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🟩", "🌉", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳", "🟩", "🌳"],
                ["🌳", "🆚", "🟦", "🟩", "🌳", "🟩", "🌳", "🎒", "🌳", "🪨", "🌳"],
                ["🌳", "🌳", "🟦", "🏪", f"🌳", "🟩", "🌳", "🌳", "🌳", "🌳", "🌳"]
            ]
        }
        
        map_2_dict = {
            "standing_on": "🟨",
            "spawn_portal": (5, 10),
            "map_name": "Scorched Lands",
            "map_area": "Fiery Training Grounds",
            "embed_color": 0xFFD700,
            "map_doors": (1, 2),
            "exit_points": [(5, 10), (0, 5), (1, 2)],
            "north_exits": None,
            "south_exits": None,
            "east_exits": map_4_dict,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["🟨", "⬛", "⬛", "⬛", "🆚", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨"],
                ["🟨", "⬛", "🚪", "⬛", "🟨", "🟨", "🌉", "🟨", "🏪", "🟨", "🟨"],
                ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🌵", "🟨"],
                ["🟦", "🟦", "🟨", "🟨", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨"],
                ["🟨", "🟦", "💰", "🟨", "🟨", "🟦", "🟦", "🟨", "👳‍♂️", "🟨", "🟨"],
                ["🟨", "🟦", "🟦", "🟨", "🟨", "🟦", "🟨", "🟨", "🟨", "🟨", "🟨"],
                ["🟨", "🟨", "🟦", "🌉", "🟦", "🟦", "🟦", "🟨", "🟨", "🌵", "🟨"],
                ["🟨", "🌵", "🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🟨", "🟨", "🟨"],
                ["🟨", "🟨", "🟨", "🟨", "🆚", "🟨", "🟨", "🟦", "🆚", "🟨", "🟨"],
                ["🟨", "🟨", "🌵", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🪨", "🟨"],
                ["🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟨", "🟦", "🟦", "🟦"]
            ]
        }

        map_3_dict = {
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
            "west_exits": map_4_dict,
            "door_exit": None,
            "map": [
                ["🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🏔️", "🟦", "🏔️", "🆚", "🏔️", "🏔️"],
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

        map_5_5_dict = {
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
                ["🟦", "🎁", "🟫", "⬛", "⬛", "🟫", "⬛", "⬛", "🎒", "🟫", "⬛"],
                ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"],
                ["⬛", "⬛", "⬛", "⬛", "⬛", "🟫", "⬛", "⬛", "⬛", "⬛", "⬛"]
            ]
        }

        map_5_dict = {
            "standing_on": "🟫",
            "spawn_portal": (10, 5),  # Adjust the spawn portal if necessary
            "map_name": "Crystal Caverns",
            "map_area": "Underground Training Grounds",
            "embed_color": 0x8B4513,
            "map_doors": None,
            "exit_points": [(10, 5)],
            "north_exits": None,
            "south_exits": map_5_5_dict,
            "east_exits": None,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
                ["⬛", "🎒", "🪨", "🟫", "⬛", "⬛", "⬛", "🟫", "🟫", "🟫", "⬛"],
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

        map_6_dict_day = {
                "standing_on": "◼️",
                "spawn_portal": (10, 5),
                "map_name": "Concrete Jungle",
                "map_area": "City Training Grounds",
                "embed_color": 0x808080,
                "map_doors": None,
                "exit_points": [(10,5)],
                "north_exits": None,
                "south_exits": map_4_dict,
                "east_exits": None,
                "west_exits": None,
                "door_exit": None,
                "map": [
                    ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
                    ["🏢", "🟦", "👨", "🟩", "◼️", "◼️", "🏢", "◼️", "🏥", "🧱", "🏢"],
                    ["🏢", "🟩", "🟩", "🟩", "◼️", "◼️", "🏢", "◼️", "◼️", "◼️", "🏢"],
                    ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "🆚", "🏢", "🏢", "🏢"],
                    ["🏢", "🏢", "🕵️‍♂️", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢"],
                    ["🏢", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🏢"],
                    ["🏢", "◼️", "🏢", "🏢", "🏢", "◼️", "🏢", "◼️", "🏢", "◼️", "🏢"],
                    ["🏢", "◼️", "🏢", "🏯", "🏢", "◼️", "🏢", "🏪", "🏢", "◼️", "🏢"],
                    ["🏢", "◼️", "🏢", "◼️", "🏢", "◼️", "🏢", "🏢", "🏢", "◼️", "🏢"],
                    ["🏢", "🎁", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🏢"],
                    ["🏢", "🏢", "🏢", "🏢", "🏢", "◼️", "🏢", "🏢", "🏢", "🏢", "🏢"]
                ]
            }
        
        map_6_dict_am = {
            "standing_on": "◼️",
            "spawn_portal": (10, 5),
            "map_name": "Concrete Jungle",
            "map_area": "Morning City Training Grounds",
            "embed_color": 0x808080,
            "map_doors": None,
            "exit_points": [],
            "north_exits": None,
            "south_exits": map_4_dict,
            "east_exits": None,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
                ["🌆", "🟦", "👨", "🟩", "◼️", "◼️", "🌆", "◼️", "🏥", "🧱", "🌆"],
                ["🌆", "🟩", "🟩", "🟩", "◼️", "◼️", "🌆", "◼️", "◼️", "◼️", "🌆"],
                ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "🆚", "🌆", "🌆", "🌆"],
                ["🌆", "🌆", "🕵️‍♂️", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆"],
                ["🌆", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🌆"],
                ["🌆", "◼️", "🌆", "🌆", "🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆"],
                ["🌆", "◼️", "🌆", "🏯", "🌆", "◼️", "🌆", "🏪", "🌆", "◼️", "🌆"],
                ["🌆", "◼️", "🌆", "◼️", "🌆", "◼️", "🌆", "🌆", "🌆", "◼️", "🌆"],
                ["🌆", "🎁", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🌆"],
                ["🌆", "🌆", "🌆", "🌆", "🌆", "◼️", "🌆", "🌆", "🌆", "🌆", "🌆"]
            ]
        }

        map_6_dict_pm = {
            "standing_on": "◼️",
            "spawn_portal": (10, 5),
            "map_name": "Concrete Jungle",
            "map_area": "Night City Training Grounds",
            "embed_color": 0x808080,
            "map_doors": None,
            "exit_points": [],
            "north_exits": None,
            "south_exits": map_4_dict,
            "east_exits": None,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
                ["🌃", "🟦", "👨", "🟩", "◼️", "◼️", "🌃", "◼️", "🧙", "🧱", "🌃"],
                ["🌃", "🟩", "🟩", "🟩", "◼️", "◼️", "🌃", "◼️", "◼️", "◼️", "🌃"],
                ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "🆚", "🌃", "🌃", "🌃"],
                ["🌃", "🌃", "🕵️‍♂️", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃"],
                ["🌃", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🚗", "◼️", "🌃"],
                ["🌃", "◼️", "🌃", "🌃", "🌃", "◼️", "🌃", "◼️", "🌃", "◼️", "🌃"],
                ["🌃", "◼️", "🌃", "🏯", "🌃", "◼️", "🌃", "🏪", "🌃", "◼️", "🌃"],
                ["🌃", "◼️", "🌃", "◼️", "🌃", "◼️", "🌃", "🌃", "🌃", "◼️", "🌃"],
                ["🌃", "🎁", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "◼️", "🌃"],
                ["🌃", "🌃", "🌃", "🌃", "🌃", "◼️", "🌃", "🌃", "🌃", "🌃", "🌃"]
            ]
        }
        
        map_7_dict = {
            "standing_on": "🟫",
            "spawn_portal": (0, 6),
            "map_name": "Eerie Graveyard",
            "map_area": "Graveyard Training Grounds",
            "embed_color": 0x8B4513,  # Brown color
            "map_doors": None,
            "exit_points": [],
            "north_exits": map_1_dict,
            "south_exits": None,
            "east_exits": None,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["🌲", "🌲", "🌲", "🌲", "🌲", "🌲", "🟫", "🌲", "🌲", "🌲", "🌲"],
                ["🌲", "🪦", "🟫", "🎒", "🪦", "🟫", "🟫", "🪦", "🟫", "🎃", "🌲"],
                ["🌲", "🟫", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🌲"],
                ["🌲", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🌲"],
                ["🌲", "🪦", "🟫", "🪦", "🟫", "💀", "🟫", "🟫", "🪦", "🎁", "🌲"],
                ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🪦", "🌲"],
                ["🌲", "🕴️", "🟫", "🆚", "🟦", "🌉", "🟦", "🆚", "🪦", "🌲", "🌲"],
                ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦", "🪦", "🌲"],
                ["🌲", "🦴", "🟫", "🟫", "🪦", "🟫", "🪦", "🟫", "🟫", "🪦", "🌲"],
                ["🌲", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "☠️", "🪦", "🌲"],
                ["🌲", "🪦", "🪦", "🪦", "🪦","🪦" , "🪦", "🪦", "🪦", "🪦", "🌲"]
            ]
        }


        cemetery_of_ash = {
            "standing_on": "🟫",
            "spawn_portal": (10, 5),
            "map_name": "Cemetery of Ash",
            "map_area": "Ashen Burial Grounds",
            "embed_color": 0x8B4513,  # Brown color
            "map_doors": None,
            "exit_points": [],
            "north_exits": map_1_dict,
            "south_exits": None,
            "east_exits": None,
            "west_exits": None,
            "door_exit": None,
            "map": [
                ["🪦", "🪦", "🪦", "🪦", "🪦", "🪦", "🟫", "🪦", "🪦", "🪦", "🪦"],
                ["🪦", "🪦", "🦴", "🟫", "🟫", "🟫", "🟫", "🟫", "🌲", "🪦", "🪦"],
                ["🪦", "🆚", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🌲", "🌲", "🪦"],
                ["🪦", "🟫", "🪦", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
                ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
                ["🪦", "🟫", "🟫", "🟫", "🪦", "🪦", "🪦", "🟫", "🟫", "🟫", "🪦"],
                ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
                ["🪦", "🟫", "🪦", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🟫", "🪦"],
                ["🪦", "🆚", "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "🟫", "🪦", "🪦"],
                ["🪦",  "🪦",  "🪦", "🟫", "🟫", "🟫", "🟫", "🪦", "☠️", "🪦", "🪦"],
                ["🪦",  "🪦",  "🪦",  "🪦",  "🪦",  "🟫",  "🪦",  "🪦",  "🪦",  "🪦",  "🪦"]
            ]
        }