import db
import crown_utilities

class Map:
    def __init__(self, map_dict):
        self.load_map(map_dict)
    
    def load_map(self, map_dict):
        for key, value in map_dict.items():
            setattr(self, key, value)

    def display_map(self):
        return self.map