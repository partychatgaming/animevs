from numpy import save
import db
import crown_utilities
import discord
from discord import Embed
import textwrap


class Player:
    def __init__(self, disname, did, avatar, association, guild, family, equipped_title, equipped_card, equipped_arm, equipped_summon, equipped_talisman,completed_tales, completed_dungeons, boss_wins, rift, rebirth, level, explore, save_spot, performance, trading, boss_fought, difficulty, storage_type, used_codes, battle_history, pvp_wins, pvp_loss, retries, prestige, patron, family_pet):
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
        self.patron = patron
        self.family_pet = family_pet

        self.talisman_message = "No Talisman Equipped"

        self.summon_power_message = ""
        self.summon_lvl_message = ""
        self.rift_on = False
        self.auto_battle = False
        
        # Guild Config
        self._default_guild = ""
        self.guild_info = "" 
        self.guild_buff = ""
        self.guild_buff_update_query = ""
        self.filter_query = ""

        # Association Config
        self.association_info = ""
        self.crestlist = ""
        self.crestsearch = False

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


    def set_explore(self):
        if self.level < 25 and self.prestige == 0:             
            return "🔓 Unlock the Explore Mode by completing Floor 25 of the 🌑 Abyss! Use **Abyss** in /solo to enter the abyss."
        
        if not self.explore:
            db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'EXPLORE': True}})
            return "Entering Explorer Mode :milky_way: "
        
        if self.explore:
            db.updateUserNoFilter({'DID': str(self.did)}, {'$set': {'EXPLORE': False}})
            return "Exiting Explorer Mode :rotating_light: "

    
    def set_rift_on(self):
        if self.rift == 1:
            self.rift_on = True
        return self.rift_on


    async def set_guild_data(self):
        if self.guild != "PCG":
            self.guild_info = db.queryTeam({'TEAM_NAME': self.guild.lower()})
            self.guild_buff = await crown_utilities.guild_buff_update_function(self.guild)
            if self.guild_buff:
                if self.guild_buff['Rift']:
                    self.rift_on = True
                    self.guild_buff_update_query = guild_buff['UPDATE_QUERY']
                    self.filter_query = guild_buff['FILTER_QUERY']

            if self.association != "PCG":
                self.association_info = db.queryGuildAlt({'GNAME': self.association})
                if self.association_info:
                    self.crestlist = self.association_info['CREST']
                    self.crestsearch = True


    def set_auto_battle_on(self, mode):
        if self.patron != True and mode in crown_utilities.AUTO_BATTLE_M:
            self.auto_battle = True
        return self.auto_battle


    def set_selectable_universes(self, ctx, mode):
        try:
            completed_message = f"**Completed**: 🔴"
            save_spot_text = "No Save Data"
            corruption_message = "📢 Not Corrupted"
            title = "UTITLE"
            title_message = "Universe Title"
            arm_message = "Universe Arm"
            summon_message = "Universe Summon"
            arm = "UARM"
            summon = "UPET"
            list_of_opponents = "CROWN_TALES"
            save_spot_check = crown_utilities.TALE_M
            mode_check = "HAS_CROWN_TALES"
            completed_check = self.completed_tales

            if mode in crown_utilities.DUNGEON_M:
                title = "DTITLE"
                title_message = "Dungeon Title"
                arm_message = "Dungeon Arm"
                summon_message = "Dungeon Summon"
                arm = "DARM"
                summon = "DPET"
                list_of_opponents = "DUNGEONS"
                save_spot_check = crown_utilities.DUNGEON_M
                mode_check = "HAS_DUNGEON"
                completed_check = self.completed_dungeons



            if self.rift:
                if mode in crown_utilities.DUNGEON_M:
                    all_universes = db.queryDungeonAllUniverse()
                if mode in crown_utilities.TALE_M:
                    all_universes = db.queryTaleAllUniverse()
                
                corruption_message = "📢 Not Corrupted | 🔮 *Crown Rifts*"

            if not self.rift:
                if mode in crown_utilities.DUNGEON_M:
                    all_universes = db.queryDungeonUniversesNotRift()
                if mode in crown_utilities.TALE_M:
                    all_universes = db.queryTaleUniversesNotRift()
            

            universe_embed_list = []
            
            for uni in all_universes:
                if uni[mode_check] == True and uni['TIER'] != 9:
                    if uni['TITLE'] in completed_check:
                        completed_message = f"**Completed**: 🟢"

                    if self.difficulty != "EASY":
                        for save in self.save_spot:
                            if save['UNIVERSE'] == uni['TITLE'] and save['MODE'] in save_spot_check:
                                save_spot_text = str(save['CURRENTOPPONENT'])
                    
                    if uni['CORRUPTED']:
                        corruption_message = "👾 **Corrupted**"

                    if uni['GUILD'] != "PCG":
                        owner_message = f"{crown_utilities.crest_dict[uni['TITLE']]} **Crest Owned**: {uni['GUILD']}"
                    else: 
                        owner_message = f"{crown_utilities.crest_dict[uni['TITLE']]} *Crest Unclaimed*"


                    embedVar = discord.Embed(title= f"{uni['TITLE']}", description=textwrap.dedent(f"""
                    {crown_utilities.crest_dict[uni['TITLE']]} **Number of Fights**: :crossed_swords: **{len(uni[list_of_opponents])}**
                    🎗️ **{title_message}**: {uni[title]}
                    🦾 **{arm_message}**: {uni[arm]}
                    🧬 **{summon_message}**: {uni[summon]}

                    **Saved Game**: :crossed_swords: *{save_spot_text}*
                    **Difficulty**: ⚙️ {self.difficulty.lower().capitalize()}
                    {completed_message}
                    {corruption_message}
                    {owner_message}
                    """))
                    embedVar.set_image(url=uni['PATH'])
                    embedVar.set_thumbnail(url=ctx.author.avatar_url)
                    universe_embed_list.append(embedVar)

            return universe_embed_list

        except Exception as ex:
            trace = []
            tb = ex.__traceback__
            while tb is not None:
                trace.append({
                    "filename": tb.tb_frame.f_code.co_filename,
                    "name": tb.tb_frame.f_code.co_name,
                    "lineno": tb.tb_lineno
                })
                tb = tb.tb_next
            print(str({
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))


    async def set_guild_buff(self):
        guild_buff = await crown_utilities.guild_buff_update_function(self.guild.lower())
        if guild_buff['Auto Battle']:
            self.auto_battle = True
            update_team_response = db.updateTeam(guild_buff['QUERY'], guild_buff['UPDATE_QUERY'])
