import db
import crown_utilities

class Battle:
    def __init__(self, mode, difficulty):
        self.mode = mode
        self._is_tales = False
        self._is_dungeon = False
        self._is_explore = False
        self._is_abyss = False
        self._is_boss = False
        self._is_tutorial = False
        self._is_raid = False
        self._is_scenario = False

        self.list_of_opponents = [""]


        self._is_co_op = False
        self._is_duo = False
        self.is_ai_opponent = False
        
        self.difficulty = difficulty
        self._is_easy = False
        self._is_hard = False
        self._is_normal = False

        self.health_buff = 0
        self.health_debuff = 0
        self.stat_buff = 0
        self.stat_debuff = 0
        self.ap_buff = 0
        self.ap_debuff = 0

        self.summon_lvl = 0
        self.summon_bond = 0
        self._ai_opponent_card_lvl = 0

        self.scaling_stat = 0


    def set_scaling_stats(self):
        if self.difficulty == "EASY":
            self._is_easy = True
            self.health_debuff = self.health_debuff + 500
            self.stat_debuff = self.stat_debuff + 100
            self.ap_debuff = self.ap_debuff + 15

        if self.mode in crown_utilities.TALE_M:
            self.summon_lvl = 5
            self.summon_bond = 1
            self._ai_opponent_card_lvl = 30

        if self.mode in crown_utilities.DUNGEON_M:
            self.summon_lvl = 10
            self.summon_bond = 3
            self._ai_opponent_card_lvl = 400
            self.health_buff = self.health_buff + 2000
            self.stat_buff = self.stat_buff + 100
            self.ap_buff = self.ap_buff + 80

        if self.mode in crown_utilities.BOSS_M:
            self.summon_lvl = 15
            self.summon_bond = 4
            self._ai_opponent_card_lvl = 1000
            self.health_buff = self.health_buff + 5000
            self.stat_buff = self.stat_buff + 250
            self.ap_buff = self.ap_buff + 250


        if self.difficulty == "NORMAL":
            self._is_normal = True

        if self.difficulty == "HARD":
            self._is_hard = True
            self.health_buff = self.health_buff + 3000
            self.stat_buff = self.stat_buff + 200
            self.ap_buff = self.ap_buff + 150
        
             
     




    

