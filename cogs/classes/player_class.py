from numpy import save
import db
import crown_utilities

class Player:
    def __init__(self, disname, did, avatar, association, guild, family, equipped_title, equipped_card, equipped_arm, equipped_summon, equipped_talisman,completed_tales, completed_dungeons, boss_wins, rift, rebirth, level, explore, save_spot, performance, trading, boss_fought, difficulty, storage_type, used_codes, battle_history, pvp_wins, pvp_loss, retries, prestige):
        self.disname = disname
        self.did = did
        self.avatar = avatar
        self.association = association
        self.guild = guild
        self.family = family
        self.equipped_title = equipped_title
        self.equipped_card = equipped_card
        self.equipped_arm = equipped_arm
        self.equipped_summon = equipped_summon
        self.equipped_talisman = equipped_talisman
        self.completed_tales = completed_tales
        self.completed_dungeons = completed_dungeons
        self.boss_wins = boss_wins
        self.rift = rift
        self.rebirth = rebirth
        self.rebirthBonus = rebirth * 10
        self.level = level
        self.explore = explore
        self.save_spot = save_spot
        self.performance = performance
        self.trading = trading
        self.boss_fought = boss_fought
        self.difficulty = difficulty
        self.storage_type = storage_type
        self.used_codes = used_codes
        self.battle_history = battle_history
        self.pvp_wins = pvp_wins
        self.pvp_loss = pvp_loss
        self.retries = retries
        self.prestige = prestige

        self.talisman_message = "No Talisman Equipped"

        self.summon_power_message = ""
        self.summon_lvl_message = ""
        
    
    def set_talisman_message(self, list_of_talismans):
        try:
            if self.equipped_talisman != "NULL":
                for t in list_of_talismans:
                    if t["TYPE"].upper() == self.equipped_talisman.upper():
                        talisman_emoji = crown_utilities.set_emoji(self.equipped_talisman.upper())
                        talisman_durability = t["DUR"]
                self.talisman_message = f"{talisman_emoji} {self.equipped_talisman.title()} Talisman Equipped ⚒️ {talisman_durability}"
            
            return self.talisman_message

        except:
            print("Error setting talisman message.")
            return self.talisman_message
        

    def set_summon_messages(self, list_of_summons):
        try:
            for summon in list_of_summons:
                if summon['NAME'] == self.equipped_summon:
                    active_summon = summon

            power = list(active_summon.values())[3]
            bond = active_summon['BOND']
            lvl = active_summon['LVL']
            s_type = active_summon['TYPE']
            if bond == 3:
                bond_message = "🌟"
            else:
                bond_message = " "
            
            if lvl == 10:
                lvl_message = "⭐"
            else:
                lvl_message = " "

            summon_ability_power = (bond * lvl) + power

            self.summon_power_message = f"🧬 {self.equipped_summon}: {s_type.title()}: {summon_ability_power}{crown_utilities.enhancer_suffix_mapping[s_type]}"


            self.summon_lvl_message = f"🧬 Bond {bond_message}{str(bond)} & Level {lvl_message}{str(lvl)}"

        except:
            print("Error setting summon message")
            return "Error"



