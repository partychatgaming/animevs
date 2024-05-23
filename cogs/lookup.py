import time
now = time.asctime()
import crown_utilities
import db
import classes as dclass
import dataclasses as data
from .classes.player_class import Player
from .classes.card_class import Card
from .classes.title_class import Title
from .classes.arm_class import Arm
from .classes.summon_class import Summon
from .classes.battle_class  import Battle
from .classes.custom_paginator import CustomPaginator
import messages as m
from logger import loggy
import numpy as np
import help_commands as h
import asyncio
import requests
from collections import ChainMap
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension, User
from io import BytesIO
import io
import unique_traits as ut
import textwrap
from .game_modes import  enhancer_mapping, title_enhancer_mapping, enhancer_suffix_mapping, title_enhancer_suffix_mapping, passive_enhancer_suffix_mapping
from collections import Counter


emojis = ['👍', '👎']

class Lookup(Extension):
    def __init__(self, bot):
        self.bot = bot



    @listen()
    async def on_ready(self):
        print('Lookup Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    
    @slash_command(description="Lookup player stats", 
    options=[
        SlashCommandOption(
            name="player",
            description="Player to lookup",
            type=OptionType.USER,
            required=False
        )]
    )
    async def player(self, ctx, player = None):
        await ctx.defer()
        player_data = await crown_utilities.player_check(ctx)
        if not player_data:
            return

        try:
            if player:     
                player = player.id           
                user = await self.bot.fetch_user(player)
                avi = user.avatar_url
                query = {'DID': str(player)}
                player_data = db.queryUser(query)
            else:
                player = ctx.author.id
                avi = ctx.author.avatar_url


            player_class = crown_utilities.create_player_from_data(player_data)
            
            user = await self.bot.fetch_user(player_class.did)
            if player_class:
                player_stats = await asyncio.to_thread(db.query_stats_by_player, player_class.did)
                player_stat_distribution = stat_distribution(player_stats)

                bal_message = f"{player_class.balance_icon}{'{:,}'.format(player_class.balance)}"

                autosave_message = crown_utilities.utility_emojis['OFF']
                if player_class.autosave:
                    autosave_message = crown_utilities.utility_emojis['ON']
                    
                performance_message = crown_utilities.utility_emojis['OFF']
                if player_class.performance:
                    performance_message = crown_utilities.utility_emojis['ON']
                    
                explore_message = crown_utilities.utility_emojis['OFF']
                if player_class.explore:
                    location = "All"
                    if player_class.explore_location != "NULL":
                        location = player_class.explore_location
                    explore_message = f"{crown_utilities.utility_emojis['ON']} *Exploring {location}*"
                    
                # purse_message = ""
                # purse = d['TOURNAMENT_WINS']
                # if purse == 1:
                #     purse_message = "👛 | **Gabe's Purse** Activated"
                    
                patreon_message = ""
                if player_class.patron == True:
                    patreon_message = "**💞 | Patreon Supporter**"
                
                rift_message = crown_utilities.utility_emojis['OFF']
                if player_class.rift == 1:
                    rift_message = crown_utilities.utility_emojis['ON']
                if player_class.guild != "PCG":
                    team_info = db.queryTeam({'TEAM_NAME' : str(player_class.guild.lower())})
                    guild = team_info['GUILD']
                    guild_buff = team_info['ACTIVE_GUILD_BUFF']
                    guild_buff_active = team_info['GUILD_BUFF_ON']
                    if guild_buff == "Rift" and guild_buff_active:
                        rift_message = f"*{crown_utilities.utility_emojis['ON']} Guild Buff On*"
                
                join_raw = player_data['TIMESTAMP']
                year_joined = join_raw[20:]
                day_joined = join_raw[:10]
                
                prestige_message = "*No Prestige*"
                if player_class.prestige > 0 :
                    prestige_message = f"**Prestige:** *{player_class.prestige}*"

                birthday = f"🎉 Registered on {day_joined}, {year_joined}"

                player_class.set_talisman_message()

                crown_list = []
                for crown in player_class.completed_tales:
                    if crown != "":
                        crown_list.append(f"**{crown_utilities.crest_dict[crown]} |** {crown}")
                
                dungeon_list = []
                for dungeon in player_class.completed_dungeons:
                    if dungeon != "":
                        dungeon_list.append(f"**{crown_utilities.crest_dict[dungeon]} |** {dungeon}")
                
                embed1 = Embed(title=f"{player_class.disname} Profile".format(self), description=textwrap.dedent(f"""\
                ❤️‍🔥{player_class.prestige_icon} | **Rebirth**: {player_class.rebirth}
                
                🎴 | **Equipped Card:** {player_class.equipped_card}
                🎗️ | **Equipped Title:** {player_class.equipped_title}
                🦾 | **Equipped Arm:** {player_class.equipped_arm}
                🧬 | **Equipped Summon:** {player_class.equipped_summon}
                {player_class.talisman_message}

                🪖 | **Guild:** {player_class.guild} 
                """))
                embed1.set_thumbnail(url=player_class.avatar)
                
                embed2 = Embed(title=f"{player_class.disname} Settings".format(self), description=textwrap.dedent(f"""\
                🆚 | **Retries:** {player_class.retries} available
                :crystal_ball: | **Rift:** {rift_message}
                🌌 | **Explore:** {explore_message}
                
                ⚙️ | **Battle History Setting:** {str(player_class.battle_history)} messages
                ⚙️ | **Difficulty:** {player_class.difficulty.lower().capitalize()}
                ⚙️ | **Performance:** {performance_message}
                
                💾 | **Autosave:** {autosave_message}
                """))
                embed2.set_thumbnail(url=player_class.avatar)
                
                embed5 = Embed(title=f"{player_class.disname} Stats".format(self), description=textwrap.dedent(f"""\
                ⚔️ | **Tales Played: **{player_stat_distribution['TALES']['MATCHES']:,}
                ↘️ **Tales Completed: **{player_stat_distribution['TALES']['COMPLETED']:,}
                ↘️ **Damage Dealt in Tales** {player_stat_distribution['TALES']['DAMAGE_DEALT']:,}
                ↘️ **Damage Taken in Tales** {player_stat_distribution['TALES']['DAMAGE_TAKEN']:,}

                🔥 | **Dungeons Played: **{player_stat_distribution['DUNGEONS']['MATCHES']:,}
                ↘️ **Dungeons Completed: **{player_stat_distribution['DUNGEONS']['COMPLETED']:,}
                ↘️ **Damage Dealt in Dungeons** {player_stat_distribution['DUNGEONS']['DAMAGE_DEALT']:,}
                ↘️ **Damage Taken in Dungeons** {player_stat_distribution['DUNGEONS']['DAMAGE_TAKEN']:,}

                👹 | **Scenarios Played: **{player_stat_distribution['SCENARIOS']['MATCHES']:,}
                ↘️ **Scenarios Completed: **{player_stat_distribution['SCENARIOS']['COMPLETED']:,}
                ↘️ **Damage Dealt in Scenarios** {player_stat_distribution['SCENARIOS']['DAMAGE_DEALT']:,}
                ↘️ **Damage Taken in Scenarios** {player_stat_distribution['SCENARIOS']['DAMAGE_TAKEN']:,}
                """))
                embed5.set_thumbnail(url=player_class.avatar)
                
                embed3 = Embed(title=f"{player_class.disname} Equipment".format(self), description=textwrap.dedent(f"""\
                **Balance** | {bal_message}
                🎴 | **Cards:** {len(player_class.cards):,}
                🎗️ | **Titles:** {len(player_class.titles):,}
                🦾 | **Arms:** {len(player_class.arms):,}
                🧬 | **Summons:** {len(player_class.summons):,}
                """))
                embed3.set_thumbnail(url=player_class.avatar)
                
                embed6 = Embed(title=f"{player_class.disname} Avatar".format(self), description=textwrap.dedent(f"""\
                    **👤 | User:** {user.mention}
                    {player_class.prestige_icon} | {prestige_message}
                    {patreon_message}
                """), color=000000)
                embed6.set_image(url=avi)
                embed6.set_footer(text=f"{birthday}")

                if crown_list:
                    embed4 = Embed(title=f"{player_class.disname} Achievements".format(self), description="🏦 | Party Chat Gaming Database™️")
                    embed4.set_thumbnail(url=player_class.avatar)
                    embed4.add_field(name="🏅 | " + "Completed Tales" , value="\n".join(crown_list))
                    if dungeon_list:
                        embed4.add_field(name="🔥 | " + "Completed Dungeons", value="\n".join(dungeon_list))
                    else:
                        embed4.add_field(name="🔥 | " + "Completed Dungeons", value="No Dungeons Completed, yet!")
                        embed4.add_field(name="👹 | " + "Boss Souls", value="No Boss Souls Collected, yet!")
                else:
                    embed4 = Embed(title=f"{player_class.disname}'s Achievements".format(self), description="🏦 Party Chat Gaming Database™️")
                    embed4.set_thumbnail(url=player_class.avatar)
                    embed4.add_field(name="Completed Tales" + " 🏅", value="No Completed Tales, yet!")
                    embed4.add_field(name="Completed Dungeons" + " 🔥 ", value="No Dungeons Completed, yet!")
                    embed4.add_field(name="Boss Souls" + " 👹 ", value="No Boss Souls Collected, yet!")

                embeds = [embed6, embed1, embed5, embed3, embed2, embed4]
                paginator = CustomPaginator.create_from_embeds(self.bot, *embeds)
                paginator.show_select_menu = True
                await paginator.send(ctx)
            else:
                await ctx.send(m.USER_NOT_REGISTERED)
                return
        except Exception as ex:
            loggy.critical(f"Error in player lookup: {ex}")
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
            await ctx.send("There's an issue with your lookup command. Check with support.")
            return

    
    @slash_command(description="Lookup Guild stats", options=[
        SlashCommandOption(
            name="guild",
            description="Look guild up by guild name",
            type=OptionType.STRING,
            required=False
        ),
        SlashCommandOption(
            name="player",
            description="Look guild up by player",
            type=OptionType.USER,
            required=False
        )
    ])
    async def guild(self, ctx, guild = None, player = None):
        await ctx.defer()
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        try:
            if player:
                user = db.queryUser({'DID': str(player.id)})
                if user:
                    team_name = user['TEAM'].lower()
                    if team_name == 'pcg':
                        await ctx.send("This player is not a member of a guild.")
                        return
                    else:
                        guild = team_name
                    
            if guild:
                team_name = guild.lower()
                team_query = {'TEAM_NAME': team_name}
                team = db.queryTeam(team_query)
                team_display_name = team['TEAM_DISPLAY_NAME']
                if team:
                    team_name = team['TEAM_NAME']
                    team_display_name = team['TEAM_DISPLAY_NAME']
                else:
                    await ctx.send("Guild does not exist")
                    return
            
            else:
                user = db.queryUser({'DID': str(ctx.author.id)})
                team = db.queryTeam({'TEAM_NAME': user['TEAM'].lower()})
                if team:
                    team_name = team['TEAM_NAME']
                    team_display_name = team['TEAM_DISPLAY_NAME']
                else:
                    await ctx.send("You are not a part of a Guild.")
                    return

            if team:
                is_owner = False
                is_officer = False
                is_captain = False
                is_member = False
                user = db.queryUser({'DID': str(ctx.author.id)})

                owner = team['OWNER']
                shielding = team['SHIELDING']
                owner_data = db.queryUser({'DID': owner})
                officers_dids = team['OFFICERS']
                captains_dids = team['CAPTAINS']
                members_dids = team['MEMBERS']
                officers = []
                captains = []
                members = []
            
                for officer in officers_dids:
                    officer_data = db.queryUser({'DID': officer})
                    officers.append(officer_data['DISNAME'])
                for captain in captains_dids:
                    captain_data = db.queryUser({'DID': captain})
                    captains.append(captain_data['DISNAME'])
                for member in members_dids:
                    member_data = db.queryUser({'DID': member})
                    members.append(member_data['DISNAME'])
                
                owner = owner_data['DISNAME']

                member_count = len(members)
                formatted_list_of_members = []
                formatted_list_of_officers = []
                formatted_list_of_captains = []
                formatted_owner = ""
                for member in members:
                    index = members.index(member)
                    if user['DISNAME'] == member:
                        is_member = True

                    if member in officers:
                        formatted_name = f"🅾️ [{str(index)}] **{member}**"
                        formatted_list_of_officers.append(formatted_name)
                    elif member in captains:
                        formatted_name = f"🇨 [{str(index)}] **{member}**"
                        formatted_list_of_captains.append(formatted_name)
                    elif member == owner:
                        formatted_name = f"👑 [{str(index)}] **{member}**"
                        formatted_owner = formatted_name
                    elif member not in officers and member not in captains and member != owner:
                        formatted_name = f"\n🔰 [{str(index)}] **{member}**"
                        formatted_list_of_members.append(formatted_name)

                members_list_joined = "".join(formatted_list_of_members)
                captains_list_joined = ", ".join(formatted_list_of_captains)
                officers_list_joined = ", ".join(formatted_list_of_officers)
                if user['DISNAME'] in officers:
                    is_officer = True
                elif user['DISNAME'] in captains:
                    is_captain = True
                elif user['DISNAME'] == owner:
                    is_owner = True
                elif user['DISNAME'] in  members:
                    is_member = True

                transactions = team['TRANSACTIONS']
                transactions_embed = ""
                if transactions:
                    transactions_len = len(transactions)
                    if transactions_len >= 10:
                        transactions = transactions[-10:]
                        transactions_embed = "\n".join(transactions)
                    else:
                        transactions_embed = "\n".join(transactions)
                
                storage = team['STORAGE']
                balance = team['BANK']

                if balance >= 0:
                    stars = "⭐"
                    rank = "D Rank Guild"
                if balance >= 1000000:
                    stars = "⭐⭐"
                    rank = "C Rank Guild"
                if balance >= 100000000:
                    stars = "⭐⭐⭐"
                    rank = "B Rank Guild"
                if balance >= 1000000000:
                    stars = "⭐⭐⭐⭐"
                    rank = "A Rank Guild"
                if balance >= 100000000000:
                    stars = "✨✨✨✨✨"
                    rank = "S Rank Guild"

                guild_buff_available = team['GUILD_BUFF_AVAILABLE']
                guild_buff_on = team['GUILD_BUFF_ON']
                gbon_status = ""
                if guild_buff_on:
                    gbon_status ="🟢"
                else:
                    gbon_status ="🔴"
                guild_buffs = team['GUILD_BUFFS']
                active_guild_buff = team['ACTIVE_GUILD_BUFF']
                active_guild_buff_use_cases = ""
                guild_buff_message = ""
                guild_buff_message_active = "No Active Guild Buff"
                if guild_buff_available:
                    guild_buff_message = "Guild Buff Available"
                    if active_guild_buff:
                        for buff in guild_buffs:
                            if buff['TYPE'] == active_guild_buff:
                                active_guild_buff_use_cases = str(buff['USES'])
                        guild_buff_message_active = f"{gbon_status} {active_guild_buff} Buff: {active_guild_buff_use_cases} uses left!"

                else:
                    guild_buff_message = "No Guild Buff Available"
                
                association = team['GUILD']
                
                association_msg = f"{association}"
                
                if shielding:
                    association_msg= f"🛡️ {association}"
                
                hall_info = db.queryHall({'HALL': 'Mine'})
                hall_img = hall_info['PATH']
                hall_name = hall_info['HALL']
                split = hall_info['SPLIT']
                if association != "PCG":
                    association_info = db.queryGuildAlt({"GNAME" :str(association)})
                    hall = association_info['HALL']
                    hall_info = db.queryHall({'HALL':str(hall)})
                    hall_name = hall_info['HALL']
                    hall_img = hall_info['PATH']
                    split = hall_info['SPLIT']
                else:
                    association = "Not Associated */oath to create association*"

                tournament_wins = team['TOURNAMENT_WINS']
                wins = team['WINS']
                losses = team['LOSSES']
                in_war = team['WAR_FLAG']
                war_opponent = team['WAR_OPPONENT']
                war_wins = team['WAR_WINS']
                war_message = ""
                if in_war:
                    war_message = "Guild in War"
                else:
                    war_message = "No Guild War"
                


                guild_mission = team['GUILD_MISSION']
                completed_missions = team['COMPLETED_MISSIONS']
                guild_mission_message = ""
                if guild_mission:
                    guild_mission_message = "Guild Mission Active"
                else:
                    guild_mission_message = "No Active Guild Mission"


                icon = "💳"
                guild = team['GUILD']


                first_page = Embed(title=f"{team_display_name}", description=textwrap.dedent(f"""
                {stars}
                **{rank}**
                
                👑 **Owner** 
                {formatted_owner}
                
                🅾️ **Officers**
                {officers_list_joined}
                
                🇨 **Captains**
                {captains_list_joined}
                
                **Guild Membership Count** 
                {member_count}
                
                **Association**
                {association_msg}
                
                **Guild Buff**
                {guild_buff_message}
                
                **Active Buff**
                {guild_buff_message_active}
                
                **Bank** 
                {icon} {'{:,}'.format(balance)}
                """), color=0x7289da)

                
                membership_pages = Embed(title=f"Members", description=textwrap.dedent(f"""
                🔰 **Members**\n{members_list_joined}
                """), color=0x7289da)

                
                guild_mission_embed = Embed(title=f"Guild Missions", description=textwrap.dedent(f"""
                **Guild Mission** *Coming Soon*
                {guild_mission_message}
                **Completed Guild Missions**
                {str(completed_missions)}
               
                """), color=0x7289da)


                war_embed = Embed(title=f"Guild War", description=textwrap.dedent(f"""
                **War** *Coming Soon*
                {war_message}
                **Wars Won**
                {str(war_wins)}
               
                """), color=0x7289da)
                

                activity_page = Embed(title="Recent Guild Activity", description=textwrap.dedent(f"""
                {transactions_embed}
                """), color=0x7289da)
                

                association_page = Embed(title="Association", description=textwrap.dedent(f"""
                **:flags: Association** | {association}
                **:shinto_shrine: Hall** | {hall_name}
                **:yen: Split** | Earn **{split}x** 🪙 per match!
                """), color=0x7289da)
                
                association_page.set_image(url=hall_img)
                
                guild_explanations = Embed(title=f"Information", description=textwrap.dedent(f"""
                **Buff Explanations**
                - **Quest Buff**: Start Quest from the required fight in the Tale, not for dungeons
                - **Level Buff**: Each fight will grant you a level up
                - **Stat Buff**: Add 50 ATK & DEF, 30 AP, and 100 HLT
                - **Rift Buff**: Rifts will always be available
                - **Rematch Buff**: Unlimited Rematches
                
                **Guild Position Explanations**
                - **Owner**:  All operations */guildoperations*
                - **Officer**:  Can Add members, Delete members, Pay members, Buy, Swap, and Toggle Buffs
                - **Captain**:  Can Toggly Buffs, Pay members
                - **Member**:  No operations
                """), color=0x7289da)

                embed_list = [first_page, membership_pages, guild_mission_embed, war_embed, association_page, activity_page, guild_explanations]

                buttons = [] 

                if not is_member:
                    buttons = ["Apply"]
                
                if is_owner or is_officer:
                    buttons = ["Buff Toggle", "Buff Swap", "Buff Shop"]
                    
                elif is_captain:
                    buttons = ["Buff Toggle"]

            
                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        if button_ctx.custom_id == "guild_buff_shop":
                            await button_ctx.defer(ignore=True)
                            await self.bot.buffshop(ctx, user, team)
                            self.stop = True
                        self.stop = True
                    else:
                        await button_ctx.send("Not your button bucko")
                        self.stop = True


                paginator = CustomPaginator.create_from_embeds(self.bot, *embed_list, custom_buttons=buttons, paginator_type="Guild Buff")
                paginator.show_select_menu = True
                paginator.guild_buff_available = guild_buff_available
                await paginator.send(ctx)
                
            else:
                await ctx.send(m.TEAM_DOESNT_EXIST)
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
    
    
    @slash_command(description="Lookup Association")
    async def association(self, ctx, association = None):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        
        in_guild = False
        is_visitor = False
        guild_query = {}
        try:
            if association:   
                guild_name = association
                guild_query = {'GNAME': guild_name}
                guild = db.queryGuildAlt(guild_query)
                founder_name = ""
                if guild:
                    guild_name = guild['GNAME']
                else:
                    await ctx.send("Association does not exist.")
                    return
            else:
                user = db.queryUser({'DID': str(ctx.author.id)})
                team = db.queryTeam({'TEAM_NAME': user['TEAM'].lower()})
                guild = db.queryGuildAlt({'GNAME': team['GUILD']})
                if guild:
                    guild_name = guild['GNAME']
                    in_guild = True
                else:
                    await ctx.send("Your Guild is not Associated.")
                    return
                
            if guild:
                is_founder = False
                is_sworn = False
                is_shield = False
                is_guild_leader = False
                member = False
                betrayed = False
                
                hall = db.queryHall({'HALL' : guild['HALL']})
                hall_name = hall['HALL']
                hall_multipler = hall['MULT']
                hall_split = hall['SPLIT']
                hall_fee = hall['FEE']
                hall_def = hall['DEFENSE']
                hall_img = hall['PATH']
                
                guild_name = guild['GNAME']
                guild_query = {'GNAME': guild_name}
                founder_name = guild['FOUNDER']
                f_DID = guild['FDID']
                w_DID = guild['WDID']
                s_DID = guild['SDID']
                sworn_name = guild['SWORN']
                if guild['WDID'] == "BETRAYED":
                    betrayed = True
                    
                shield_name = guild['SHIELD']
                shield_info = db.queryUser({'DID' : s_DID})
                shield_card = shield_info['CARD']
                shield_arm = shield_info['ARM']
                shield_title = shield_info['TITLE']
                shield_rebirth = shield_info['REBIRTH']
                
                streak = guild['STREAK']
                crest = guild['CREST']
                balance = guild['BANK']
                bounty = guild['BOUNTY']
                bonus = int((streak/100) * bounty)
                
                estates = guild['ESTATES']
                estates_list = []
                estate_data_list = []
                for halls in estates:
                    hall_data = db.queryHall({'HALL': halls})
                    estates_list.append(halls)
                    estate_data_list.append(hall_data)
                    
                estates_list_joined = ", ".join(estates_list)
                
                picon = "🛡️"
                sicon = ":beginner:"
                
                icon = "🪙"
                if balance >= 2000000000:
                    icon = "💸"
                elif balance >=1000000000:
                    icon = "💰"
                elif balance >= 500000000:
                    icon = "💵"
                    
                if streak >= 100:
                    sicon = ":skull_crossbones:"     
                elif streak >= 50:
                    sicon = ":skull:"
                elif streak >=25:
                    sicon = ":ghost:"
                elif streak >= 10:
                    sicon = "💠"
                    
                
                sword_list = []
                owner_list = []
                owner_name_list = []
                sword_member_list = []
                sword_count = 0
                blade_count = 0
                total_blade_count = 0
                for swords in guild['SWORDS']:
                    index = guild['SWORDS'].index(swords)
                    blade_count = 0
                    sword_count = sword_count + 1
                    sword_team = db.queryTeam({'TEAM_NAME': swords})
                    swords_name = sword_team['TEAM_DISPLAY_NAME']
                    dubs = sword_team['WINS']
                    els = sword_team['LOSSES']
                    owner = sword_team['OWNER']
                    owner_DID = sword_team['DID']
                    
                    officers = sword_team['OFFICERS']
                    captains = sword_team['CAPTAINS']
                    members = sword_team['MEMBERS']
                    owner_list.append(f"{owner_DID}")
                    
                    if owner_DID == f_DID:
                        owner_name_list.append(f"🪆 | [{str(index)}] **{owner}** *{sword_team['TEAM_DISPLAY_NAME']}*")
                    elif owner_DID == w_DID:
                        owner_name_list.append(f"🎎 | [{str(index)}] **{owner}** *{sword_team['TEAM_DISPLAY_NAME']}*")
                    elif owner_DID == s_DID:
                        owner_name_list.append(f"👺 | [{str(index)}] **{owner}** *{sword_team['TEAM_DISPLAY_NAME']}*")
                    else:
                        owner_name_list.append(f"👑 | [{str(index)}] **{owner}** *{sword_team['TEAM_DISPLAY_NAME']}*")
                    for blades in sword_team['MEMBERS']:
                        bindex = sword_team['MEMBERS'].index(blades)
                        blade_count = blade_count + 1
                        total_blade_count = total_blade_count + 1
                        if blades in officers:
                            formatted_name = f"__🅾️ [{str(index)}{str(bindex)}] {blades}__"
                            sword_member_list.append(formatted_name)
                        elif blades in captains:
                            formatted_name = f"🇨 [{str(index)}{str(bindex)}] {blades}"
                            sword_member_list.append(formatted_name)
                        elif blades == owner:
                            if blades == founder_name:
                                formatted_name = f"\n🪖 | {swords_name}\n**🪆 | [{str(index)}] {owner}**"
                            elif blades == sworn_name:
                                formatted_name = f"\n🪖 | {swords_name}\n**🎎 | [{str(index)}] {owner}**"
                            elif blades == shield_name:
                                formatted_name = f"\n🪖 | {swords_name}\n**👺 | [{str(index)}] {owner}**"
                            else:
                                formatted_name = f"\n🪖 | {swords_name}\n**👑 [{str(index)}{str(bindex)}] {blades}**"
                            formatted_owner = formatted_name
                            sword_member_list.append(formatted_owner)
                        elif blades not in officers and blades not in captains and blades != owner:
                            formatted_name = f"*🔰 [{str(index)}{str(bindex)}] {blades}*"
                            sword_member_list.append(formatted_name)
                        #sword_member_list.append(f":knife: [{str(index)}{str(bindex)}] **{blades}**")
                    sword_bank = sword_team['BANK']
                    sword_list.append(f"~ {swords_name} ~ W**{dubs}** / L**{els}**\n🪙 | **Bank: **{'{:,}'.format(sword_bank)}\n:knife: | **Members: **{blade_count}\n_______________________")
                    
                guild_owner_list_joined = "\n".join(owner_name_list)
                members_list_joined =  "\n".join(sword_member_list)
                crest_list = []
                for c in crest:
                    crest_list.append(f"{crown_utilities.crest_dict[c]} | {c}")
                
                # print(ctx.author.id)
                # print(f_DID)
                # print(w_DID)
                # print(s_DID)
                if in_guild:
                    member = True
                
                if str(ctx.author.id) == f_DID:
                    is_founder = True
                    is_guild_leader = True
                    member = True
                elif str(ctx.author.id) == w_DID:
                    is_sworn = True
                    is_guild_leader = True
                    member = True
                elif str(ctx.author.id) == s_DID:
                    is_shield = True
                    if str(ctx.author.id) in owner_list:
                        is_guild_leader = True
                    member = True
                elif str(ctx.author.id) in owner_list:
                    is_guild_leader = True
                    member = True
                    
                elif member == False:
                    is_visitor = True

                transactions = guild['TRANSACTIONS']
                transactions_embed = ""
                if transactions:
                    transactions_len = len(transactions)
                    if transactions_len >= 10:
                        transactions = transactions[-10:]
                        transactions_embed = "\n".join(transactions)
                    else:
                        transactions_embed = "\n".join(transactions)

                # embed1 = Embed(title=f":flags: {guild_name} Guild Card - {icon}{'{:,}'.format(balance)}".format(self), description="🏦 Party Chat Gaming Database", color=000000)
                # if guild['LOGO_FLAG']:
                #     embed1.set_image(url=logo)
                # embed1.add_field(name="Founder :dolls:", value= founder_name.split("#",1)[0], inline=True)
                # embed1.add_field(name="Sworn :dolls:", value= sworn_name.split("#",1)[0], inline=True)
                main_page = Embed(title= f"{guild_name}".format(self), description=textwrap.dedent(f"""\
                :flags: | **Association:** {guild_name}
                {icon} | **Bank:** {icon}{'{:,}'.format(balance)}
                :nesting_dolls: | **Founder: ~** {founder_name.split("#",1)[0]}
                :dolls: | **Sworn: ~** {sworn_name.split("#",1)[0]}
                :japanese_goblin: | **Shield: ~**{shield_name.split("#",1)[0].format(self)}
                :ninja: | **Guilds: **{sword_count}
                :secret: | **Universe Crest: **{len(crest_list)} 
                    
                :shinto_shrine: | **Hall: **{hall_name}
                """), color=000000)
                main_page.set_image(url=hall_img)
                main_page.set_footer(text=f"/ally to join the {guild_name} Association")
                
                arena_page = Embed(title= f"Hall Information".format(self), description=textwrap.dedent(f"""\
                :flags: | **{guild_name} Raid Arena**
                🪙 | **Raid Fee: **{'{:,}'.format(hall_fee)}
                :yen: | **Bounty: **{'{:,}'.format(bounty)}
                💰 | **Victory Bonus: **{'{:,}'.format(bonus)}
                
                {sicon} | **Victories: **{streak}
                :japanese_goblin: | **Shield: ~**{shield_name.split("#",1)[0].format(self)}
                🎴 | **Card: **{shield_card}
                🎗️ | **Title: **{shield_title}
                🦾 | **Arm: **{shield_arm}
                    
                :shinto_shrine: | **Hall: **{hall_name} 
                🛡️ | **Raid Defenses: **{hall_def} 
                """), color=000000)
                arena_page.set_image(url=hall_img)
                arena_page.set_footer(text=f"/raid {guild_name} - Raid Association")
                
                guilds_page = Embed(title=f"Guild Information".format(self), description=f":flags: |  {guild_name} **Guild** List\n⛩️ | Guilds Earn **{hall_split}x**🪙\n🏦 |  Party Chat Gaming Database", color=000000)
                guilds_page.add_field(name=f":military_helmet: Guilds | **:ninja: ~ {sword_count}/:knife: {total_blade_count}**", value="\n".join(f'**{t}**'.format(self) for t in sword_list), inline=False)
                guilds_page.set_footer(text=f"/guild - View Association Guild")
                
                crest_page = Embed(title=f"Universe Crest".format(self), description=f":flags: |  {guild_name} **Universe Crest**\n🏦 |  Party Chat Gaming Database", color=000000)
                crest_page.add_field(name=f":secret: | **OWNED**", value="\n".join(f'**{c}**'.format(self) for c in crest_list), inline=False)
                crest_page.set_footer(text=f"Earn Universe Crest in Dungeons and Boss Fights!")
                
                activity_page = Embed(title="Recent Association Activity", description=textwrap.dedent(f"""
                {transactions_embed}
                """), color=0x7289da)
                
                ghost_page = Embed(title=f"Guild Owners", description=textwrap.dedent(f"""
                \n{guild_owner_list_joined}
                """), color=0x7289da)
                ghost_page.set_footer(text=f"🪆 | {guild['GNAME']} Founder\n🎎 | {guild['GNAME']} Sworn\n👺 | {guild['GNAME']} Shield\n👑 | Guilds Owners Sworn To {guild['GNAME']}\n👤 | /player - Lookup Guild Owners")

                blades_page = Embed(title=f"Association Members List", description=textwrap.dedent(f"""
                \n{members_list_joined}
                """), color=0x7289da)
                blades_page.set_footer(text=f"🪆 | Association Founder\n🎎 | Association Sworn\n👺 | Association Shield\n🪖 | Guild Name\n👑 | Guild Owner\n🅾️ | Guild Officer\n🇨  | Guild Captain\n🔰 | Guild Member\n👤 | /player - Lookup Guild Members")
                
                estates_page = Embed(title=f"Halls", description=textwrap.dedent(f"""
                ⛩️ | **Halls**
                {estates_list_joined}
                """), color=0x7289da)
                estates_page.set_footer(text=f"/halls - View Hall List")
                
                
                war_embed = Embed(title=f"Association War", description=textwrap.dedent(f"""
                **War** *Coming Soon*
                *None*

                **Wars Won**
                0
                """), color=0x7289da)
                war_embed.set_footer(text=f"Association Wars Coming Soon")
                
                association_mission_page = Embed(title=f"Association Missions", description=textwrap.dedent(f"""
                **Association Mission** *Coming Soon*
                *None*

                **Completed Association Missions**
                0
                """), color=0x7289da)
                association_mission_page.set_footer(text=f"Association Missions Coming Soon")
                
                association_explanations = Embed(title=f"Information", description=textwrap.dedent(f"""
                **Assocation Explanations**
                - **Earnings**: Associations earn coin for every PVP Match or Dungeon/Boss Encounter
                - **Splits**: Each Guild earns a % of the Wages Earned during these battles determined by the type of Hall
                - **Sponser**: Associations Leaders can sponsor Guilds with Association Funds
                - **Fund**: Invest money into Association from Guild
                - **Halls**: Give Coin Multipliers and Wage Multiplier in all game modes towards Association Earnings
                - **Raid Fee**: Cost to Raid this Association (Determined by Hall)
                - **Hall Defense**:  Give Bonus Defense Multiplier to Shield During Raids
                - **Bounty**: Other Associated players can raid to aquire the Bounty
                - **Victory Bonus**: Each Succesful Shield Defense increases the bounty and Victory Bonus
                - **Real Estate**: Own multiple Halls, swap your current Hall buy and sell real estate.
                - **Guild Armory**: Members share the Armory: Store Cards, Titles and Arms for all Members
                - **Armory Draw**: /armory to draw items from the Armory
                

                **Association Position Explanations**
                - **Founder**:  All operations.
                - **Sworn**:  All operations
                - **Shield**: Can set Raid Bounty, Swap Hideouts, and Knight other Blades
                """), color=0x7289da)
                association_explanations.set_footer(text=f"/help for more information on Associations")
                
                # if guild['LOGO_FLAG']:
                #     embed3.set_image(url=logo)
                
                embed_list = [main_page, arena_page, crest_page, guilds_page, ghost_page, blades_page, estates_page, association_mission_page, war_embed, activity_page, association_explanations]
                
                buttons = [] 
                if is_visitor:
                    buttons = [
                        Button(style=3, label="Say Hello", custom_id="hello"),
                        Button(style=3, label="Raid!", custom_id="raid")
                    ]
                    
                if is_founder or is_sworn:
                    buttons = [
                        Button(style=3, label="Check/Purchase Halls", custom_id="property"),
                        Button(style=3, label="View/Update Armory", custom_id="armory"),
                        Button(style=3, label="Test Shield Defenses", custom_id="raid")
                    ]
                    
                elif is_shield:
                    buttons = [
                        Button(style=3, label="View Properties", custom_id="property"),
                        Button(style=3, label="View/Update Armory", custom_id="armory"),
                        Button(style=3, label="Shield Training", custom_id="raid")
                    ]
                    
                elif is_guild_leader or member:
                    buttons = [
                        Button(style=3, label="View Properties", custom_id="property"),
                        Button(style=3, label="View Armory", custom_id="armory"),
                        Button(style=3, label="Claim The Shield!", custom_id="raid")
                    ]
                    
                custom_action_row = ActionRow(*buttons)
                async def custom_function(self, button_ctx):
                    try:
                        await button_ctx.defer(ignore=True)
                        if button_ctx.author == ctx.author:
                            if button_ctx.custom_id == "hello":
                                guild_query = {"GNAME": guild['GNAME']}
                                #await button_ctx.defer(ignore=True)
                                update_query = {
                                        '$push': {'TRANSACTIONS': f":wave: | {button_ctx.author} said 'Hello'!"}
                                    }
                                response = db.updateGuildAlt(guild_query, update_query)
                                await ctx.send(f"**{button_ctx.author.mention}** Said Hello to **{guild['GNAME']}**!")
                                self.stop = True
                                return
                            if button_ctx.custom_id == "raid":
                                guild_query = {"GNAME": guild['GNAME']}
                                #await button_ctx.defer(ignore=True)
                                update_query = {
                                        '$push': {'TRANSACTIONS': f"⚔️ | {button_ctx.author} Raided!"}
                                    }
                                response = db.updateGuildAlt(guild_query, update_query)
                                await raid(button_ctx, guild['GNAME'])
                                self.stop = True
                                return
                            elif button_ctx.custom_id == "property":
                                #await button_ctx.defer(ignore=True)
                                real_estate_message = " "
                                property_buttons = []
                                balance_message = '{:,}'.format(guild['BANK'])
                                if is_founder:
                                    real_estate_message = "\n Welcome Great Founder!\n**View Property** - View Owned Properties or make a Move!\n**Buy New Hall** - Buy a new Hall for your Association\n**Browse Hall Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    Button(style=2, label="Owned Properties", custom_id="equip"),
                                    Button(style=3, label="Buy/Sell Halls", custom_id="buy"),
                                    Button(style=1, label="Browse Hall Catalog", custom_id="browse"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                    
                                ]
                                elif is_sworn:
                                    real_estate_message = "\n Welcome Holy Sworn!\n**View Property** - View Owned Properties or make a Move!\n**Buy New Hall** - Buy a new Hall for your Association\n**Browse Hall Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    Button(style=2, label="Owned Properties", custom_id="equip"),
                                    Button(style=3, label="Buy/Sell Halls", custom_id="buy"),
                                    Button(style=1, label="Browse Hall Catalog", custom_id="browse"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                ]
                                elif is_shield:
                                    real_estate_message = "\n Welcome Noble Shield!\n**View Property** - View Owned Properties or make a Move!\n**Browse Hall Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    Button(style=1, label="Owned Properties", custom_id="equip"),
                                    Button(style=1, label="Browse Hall Catalog", custom_id="browse"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                ]
                                elif is_guild_leader:
                                    real_estate_message = "\n Welcome Oathsworn!\n**View Property** - View Owned Properties\n**Browse Hall Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    Button(style=1, label="View Properties", custom_id="view"),
                                    Button(style=1, label="Browse Hall Catalog", custom_id="browse"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                ]
                                property_action_row = ActionRow(*property_buttons)
                                real_estate_screen = Embed(title=f"Anime VS+ Real Estate", description=textwrap.dedent(f"""\
                                \n{real_estate_message}
                                \n*Current Association Bank*:
                                \n🪙 **{balance_message}**
                                """), color=0xe74c3c)
                                real_estate_screen.set_image(url="https://thumbs.gfycat.com/FormalBlankGeese-max-1mb.gif")
                                
                                msg = await ctx.send(embed=real_estate_screen, components=[property_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                try:
                                    hall_embed_list = []
                                    button_ctx  = await self.bot.wait_for_component(components=[property_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "q":
                                        await ctx.send("Real Estate Menu Closed...")
                                        return
                                    if button_ctx.custom_id == "browse":
                                        await button_ctx.defer(ignore=True)
                                        all_halls = db.queryAllHalls()
                                        for hall in all_halls:
                                            hall_name = hall['HALL']
                                            hall_price = hall['PRICE']
                                            price_message = '{:,}'.format(hall['PRICE'])
                                            hall_img = hall['PATH']
                                            hall_multiplier = hall['MULT']    
                                            hall_fee = '{:,}'.format(hall['FEE'])
                                            hall_split = hall['SPLIT']
                                            hall_def = hall['DEFENSE']                                       
                                            embedVar = Embed(title= f"{hall_name}", description=textwrap.dedent(f"""
                                            💰 | **Price**: {price_message}
                                            〽️ | **Multiplier**: {hall_multiplier}
                                            💵 | **Split**: {hall_split}
                                            :yen: | **Raid Fee**: {hall_fee}
                                            🛡️ | **Defenses**: {hall_def}
                                            
                                            **Association** earns **{hall_multiplier}x** 🪙 per match!
                                            **Raids** cost **{hall_fee}** 🪙!
                                            **Guilds** earn **{hall_split}x** 🪙 per match! 
                                            **Shield** Defense Boost: 🛡️**{hall_def}x**
                                            """))
                                            embedVar.set_image(url=hall_img)
                                            hall_embed_list.append(embedVar)
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=hall_embed_list).run()
                                    if button_ctx.custom_id == "view":
                                        await button_ctx.defer(ignore=True)
                                        for hall in estate_data_list:
                                            hall_name = hall['HALL']
                                            hall_price = hall['PRICE']
                                            price_message = '{:,}'.format(hall['PRICE'])
                                            hall_img = hall['PATH']
                                            hall_multiplier = hall['MULT']    
                                            hall_fee = '{:,}'.format(hall['FEE'])
                                            hall_split = hall['SPLIT']
                                            hall_def = hall['DEFENSE']                                            
                                            embedVar = Embed(title= f"{hall_name}", description=textwrap.dedent(f"""
                                            💰 | **Price**: {price_message}
                                            〽️ | **Multiplier**: {hall_multiplier}
                                            💵 | **Split**: {hall_split}
                                            :yen: | **Raid Fee**: {hall_fee}
                                            🛡️ | **Defenses**: {hall_def}
                                            
                                            **Association** earns **{hall_multiplier}x** 🪙 per match!
                                            **Raids** cost **{hall_fee}** 🪙!
                                            **Guilds** earn **{hall_split}x** 🪙 per match! 
                                            **Shield** Defense Boost: 🛡️**{hall_def}x**
                                            """))
                                            embedVar.set_image(url=hall_img)
                                            hall_embed_list.append(embedVar)
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=hall_embed_list).run()
                                    elif button_ctx.custom_id == "equip":
                                        await button_ctx.defer(ignore=True)
                                        for hall in estate_data_list:
                                            hall_name = hall['HALL']
                                            hall_price = hall['PRICE']
                                            price_message = '{:,}'.format(hall['PRICE'])
                                            hall_img = hall['PATH']
                                            hall_multiplier = hall['MULT']    
                                            hall_fee = '{:,}'.format(hall['FEE'])
                                            hall_split = hall['SPLIT']
                                            hall_def = hall['DEFENSE']                                               
                                            embedVar = Embed(title= f"{hall_name}", description=textwrap.dedent(f"""
                                            💰 | **Price**: {price_message}
                                            〽️ | **Multiplier**: {hall_multiplier}
                                            💵 | **Split**: {hall_split}
                                            :yen: | **Raid Fee**: {hall_fee}
                                            🛡️ | **Defenses**: {hall_def}
                                            
                                            **Association** earns **{hall_multiplier}x** 🪙 per match!
                                            **Raids** cost **{hall_fee}** 🪙!
                                            **Guilds** earn **{hall_split}x** 🪙 per match! 
                                            **Shield** Defense Boost: 🛡️**{hall_def}x**
                                            """))
                                            embedVar.set_image(url=hall_img)
                                            hall_embed_list.append(embedVar)
                                            
                                        equip_buttons = [
                                            Button(style=3, label="⛩️ Equip Hall", custom_id="equip"),

                                        ]
                                        equip_action_row = ActionRow(*equip_buttons)
                                        async def equip_function(self, button_ctx):
                                            hall_name = str(button_ctx.origin_message.embeds[0].title)
                                            guild_query = {'GNAME': guild['GNAME']}
                                            await button_ctx.defer(ignore=True)
                                            if button_ctx.author == ctx.author:
                                                if button_ctx.custom_id == "equip":
                                                    transaction_message = f"⛩️ | {ctx.author} changed the Association Hall to **{str(button_ctx.origin_message.embeds[0].title)}**."
                                                    update_query = {
                                                            '$set': {'HALL': hall_name},
                                                            '$push': {'TRANSACTIONS': transaction_message}
                                                        }
                                                    response = db.updateGuildAlt(guild_query, update_query)
                                                    await ctx.send(f"**{guild['GNAME']}** moved into their **{hall_name}**! This is much better suited for your current needs!")
                                                    self.stop = True
                                            else:
                                                await ctx.send("This is not your command.")
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=hall_embed_list, customActionRow=[
                                            equip_action_row,
                                            equip_function,
                                        ]).run()
                                                                                    
                                    elif button_ctx.custom_id == "buy":
                                        ahll_embed_list = []
                                        all_halls = db.queryAllHalls()
                                        owned = False
                                        current_savings = '{:,}'.format(guild['BANK'])
                                        for hall in all_halls:
                                            hall_name = hall['HALL']
                                            hall_price = hall['PRICE']
                                            price_message = '{:,}'.format(hall['PRICE'])
                                            hall_img = hall['PATH']
                                            hall_multiplier = hall['MULT']    
                                            hall_fee = '{:,}'.format(hall['FEE'])
                                            hall_split = hall['SPLIT']
                                            hall_def = hall['DEFENSE']       
                                            ownership_message = f"💰 **Price**: {price_message}"  
                                            sell_price = hall_price *.80
                                            sell_message = " "
                                            sell_message = f"💱 Sells for **{'{:,}'.format(hall['PRICE'])}**"                                  
                                            embedVar = Embed(title= f"{hall_name}", description=textwrap.dedent(f"""
                                            **Current Bank**: 🪙 **{current_savings}**                                                                    
                                            {ownership_message}
                                            
                                            💰 | **Price**: {price_message}
                                            〽️ | **Multiplier**: {hall_multiplier}
                                            💵 | **Split**: {hall_split}
                                            :yen: | **Raid Fee**: {hall_fee}
                                            🛡️ | **Defenses**: {hall_def}
                                            
                                            **Association** earns **{hall_multiplier}x** 🪙 per match!
                                            **Raids** cost **{hall_fee}** 🪙!
                                            **Guilds** earn **{hall_split}x** 🪙 per match! 
                                            **Shield** Defense Boost: 🛡️**{hall_def}x**
                                            
                                            {sell_message}
                                            """))
                                            embedVar.set_image(url=hall_img)
                                            hall_embed_list.append(embedVar)
                                        
                                        econ_buttons = [
                                            Button(style=3, label="💰 Buy Hall", custom_id="buy"),
                                            Button(style=3, label="💱 Sell Hall", custom_id="sell"),

                                        ]
                                        econ_action_row = ActionRow(*econ_buttons)
                                        
                                        async def econ_function(self, button_ctx):
                                            hall_name = str(button_ctx.origin_message.embeds[0].title)
                                            await button_ctx.defer(ignore=True)
                                            if button_ctx.author == ctx.author:
                                                if button_ctx.custom_id == "buy":
                                                    if hall_name in estates_list:
                                                        await ctx.send("You already own this Hall. Click 'Sell' to sell it!")
                                                        self.stop = True
                                                        return
                                                    if hall_name == 'Mine':
                                                        await button_ctx.send("You already own your **Memorial Mine.**")
                                                        #self.stop = True
                                                        return
                                                    try: 
                                                        hall = db.queryHall({'HALL': {"$regex": f"^{str(hall_name)}$", "$options": "i"}})
                                                        currentBalance = guild['BANK']
                                                        cost = hall['PRICE']
                                                        hall_name = hall['HALL']
                                                        if hall:
                                                            if hall_name == guild['HALL']:
                                                                await ctx.send(m.USERS_ALREADY_HAS_HALL, delete_after=5)
                                                            else:
                                                                newBalance = currentBalance - cost
                                                                if newBalance < 0 :
                                                                    await ctx.send("You have an insufficent Balance")
                                                                else:
                                                                    guild_query = {'GNAME': guild['GNAME']}
                                                                    await crown_utilities.curseguild(cost, guild['GNAME'])
                                                                    transaction_message = f"🪙 | {ctx.author} bought a new **{str(button_ctx.origin_message.embeds[0].title)}**."
                                                                    response = db.updateGuildAlt(guild_query,{'$set':{'HALL': str(hall_name)},'$push': {'TRANSACTIONS': transaction_message}})
                                                                    response2 = db.updateGuildAlt(guild_query,{'$addToSet':{'ESTATES': str(hall_name)}})
                                                                    await ctx.send(m.PURCHASE_COMPLETE_H + "Enjoy your new Hall!")
                                                                    return
                                                        else:
                                                            await ctx.send("Hall does not exist")
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
                                                if button_ctx.custom_id == "sell":
                                                    hall = db.queryHall({'HALL': {"$regex": f"^{str(hall_name)}$", "$options": "i"}})
                                                    cost = hall['PRICE']
                                                    formatted_cost = '{:,}'.format(cost)
                                                    if hall_name not in guild['ESTATES']:
                                                        await ctx.send("You need to Own this Hall to to sell it!")
                                                        #self.stop = True
                                                        return
                                                    if hall_name == guild['HALL']:
                                                        await button_ctx.send("You cannot sell your **Designated Hall**.")
                                                        #self.stop = True
                                                        return
                                                    if hall_name == 'Mine':
                                                        await button_ctx.send("You cannot sell your **Memorial Mine.**")
                                                        #self.stop = True
                                                        return
                                                    elif hall_name in guild['ESTATES']:
                                                        guild_query = {'GNAME': guild['GNAME']}
                                                        await crown_utilities.blessguild_Alt(cost, guild['GNAME'])
                                                        transaction_message = f"🪙 | {ctx.author} sold the Association Hall: **{str(hall_name)}**."
                                                        response = db.updateGuildAlt(guild_query,{'$pull':{'ESTATES': str(hall_name)},'$push': {'TRANSACTIONS': transaction_message}})
                                                        await ctx.send(f"{guild['GNAME']} sold their **{hall_name}** for **{formatted_cost}**")
                                                        #self.stop = True
                                                        return
                                            else:
                                                await ctx.send("This is not your command.")
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=hall_embed_list, customActionRow=[
                                            econ_action_row,
                                            econ_function,
                                        ]).run()                                 
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
                            elif button_ctx.custom_id == "armory":
                                #await button_ctx.defer(ignore=True)
                                armory_message = " "
                                armory_buttons = []
                                balance_message = '{:,}'.format(guild['BANK'])
                                if is_founder:
                                    armory_message = "\n nWelcome Great Founder!\n**View Armory** - View Items in Armory\n**Upgrade Armory** - Upgrade Armory\n**Donate Gear** - Donate Cards, Titles or Arms to the Armory"
                                    armory_buttons = [
                                    Button(style=2, label="View Armory", custom_id="view"),
                                    Button(style=3, label="Upgrade Armory", custom_id="upgrade"),
                                    Button(style=1, label="Donate Gear", custom_id="donate"),
                                    
                                ]
                                elif is_sworn:
                                    armory_message = "\n Welcome Holy Sword!\n**View Armory** - View Items in Armory\n**Upgrade Armory** - Upgrade Armory\n**Donate Gear** - Donate Cards, Titles or Arms to the Armory"
                                    armory_buttons = [
                                    Button(style=2, label="View Armory", custom_id="view"),
                                    Button(style=3, label="Upgrade Armory", custom_id="upgrade"),
                                    Button(style=1, label="Donate Gear", custom_id="donate"),
                                ]
                                elif is_shield:
                                    armory_message = "\n Welcome Noble Shield!\n**View Armory** - View Items in Armory\n**Upgrade Armory** - Upgrade Armory\n**Donate Gear** - Donate Cards, Titles or Arms to the Armory"
                                    armory_buttons = [
                                    Button(style=2, label="View Armory", custom_id="view"),
                                    Button(style=3, label="Upgrade Armory", custom_id="upgrade"),
                                    Button(style=1, label="Donate Gear", custom_id="donate"),
                                    
                                ]
                                elif is_guild_leader:
                                    armory_message = "\n Welcome Oathsworn!\n**View Armory** - View Items in Armory\n**Donate Gear** - Donate Cards, Titles or Arms to the Armory"
                                    armory_buttons = [
                                    Button(style=2, label="View Armory", custom_id="view"),
                                    Button(style=1, label="Donate Gear", custom_id="donate"),
                                    
                                ]
                                elif member:
                                    armory_message = "\n Welcome Member!\n**View Armory** - View Items in Armory\n**Donate Gear** - Donate Cards, Titles or Arms to the Armory"
                                    armory_buttons = [
                                    Button(style=2, label="View Armory", custom_id="view"),
                                    Button(style=1, label="Donate Gear", custom_id="donate"),
                                    
                                ]
                                armory_action_row = ActionRow(*armory_buttons)
                                armory_screen = Embed(title=f"{guild['GNAME']} Armory!", description=textwrap.dedent(f"""\
                                \n{armory_message}
                                 
                                \n🕋 **Armory Inventory** | 300
                                \n🎴 **Cards** |  {len(guild['CSTORAGE'])}
                                \n🎗️ **Titles** |  {len(guild['TSTORAGE'])}
                                \n🦾 **Arms** |  {len(guild['ASTORAGE'])}
                                """), color=0xe74c3c)
                                armory_screen.set_image(url="https://cdnb.artstation.com/p/assets/images/images/036/549/141/original/jonathan-dodd-mdz2-large-warehouse-port.gif?1617957276")
                                
                                msg = await ctx.send(embed=armory_screen, components=[armory_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                try:
                                    #await button_ctx.defer(ignore=True)
                                    card_storage = []
                                    title_storage = []
                                    arm_storage = []
                                    button_ctx  = await self.bot.wait_for_component(components=[armory_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "q":
                                        await ctx.send("Armory Menu Closed...")
                                        return
                                    if button_ctx.custom_id == "view":
                                        await msg.delete()
                                        armory_item_buttons = [
                                            Button(style=2, label="View Cards", custom_id="cards"),
                                            Button(style=3, label="View Titles", custom_id="titles"),
                                            Button(style=1, label="View Arms", custom_id="arms"),
                                            
                                        ]
                                        armory_item_action_row = ActionRow(*armory_item_buttons)
                                        armory_item_screen = Embed(title=f"{guild['GNAME']} Armory!", description=textwrap.dedent(f"""\
                                        {armory_message}
                                        
                                        🕋 **Armory Inventory** | 300
                                        🎴 **Cards** |  {len(guild['CSTORAGE'])}
                                        🎗️ **Titles** |  {len(guild['TSTORAGE'])}
                                        🦾 **Arms** |  {len(guild['ASTORAGE'])}
                                        """), color=0xe74c3c)
                                        armory_item_screen.set_image(url="https://cdnb.artstation.com/p/assets/images/images/036/549/141/original/jonathan-dodd-mdz2-large-warehouse-port.gif?1617957276")
                                        
                                        msg = await ctx.send(embed=armory_item_screen, components=[armory_item_action_row])
                                        def check(button_ctx):
                                            return button_ctx.author == ctx.author
                                        try:
                                            button_ctx  = await self.bot.wait_for_component(components=[armory_item_action_row], timeout=120, check=check)
                                            if button_ctx.custom_id == "cards":
                                                try:
                                                    card_storage = guild['CSTORAGE']
                                                    if len(card_storage) > 0:
                                                        storage_allowed_amount = 300
                                                        list_of_cards = db.querySpecificCards(card_storage)
                                                        cards = [x for x in list_of_cards]
                                                        dungeon_card_details = []
                                                        tales_card_details = []
                                                        destiny_card_details = []
                                                        
                                                        for card in cards:
                                                            moveset = card['MOVESET']
                                                            move3 = moveset[2]
                                                            move2 = moveset[1]
                                                            move1 = moveset[0]
                                                            basic_attack_emoji = crown_utilities.set_emoji(list(move1.values())[2])
                                                            super_attack_emoji = crown_utilities.set_emoji(list(move2.values())[2])
                                                            ultimate_attack_emoji = crown_utilities.set_emoji(list(move3.values())[2])

                                                            
                                                            class_info = card['CLASS']
                                                            class_emoji = crown_utilities.class_emojis[class_info]
                                                            class_message = class_info.title()
                                                            universe_crest = crown_utilities.crest_dict[card['UNIVERSE']]
                                                            index = card_storage.index(card['NAME'])
                                                            level = ""
                                                            level_icon = "🔰"
                                                            card_lvl = 0
                                                            for c in guild['S_CARD_LEVELS']:
                                                                if card['NAME'] == c['CARD']:
                                                                    level = str(c['LVL'])
                                                                    card_lvl = int(c['LVL'])
                                                            if card_lvl >= 200:
                                                                level_icon = "🔱"
                                                            if card_lvl >= 700:
                                                                level_icon ="⚜️"
                                                            if card_lvl >=999:
                                                                level_icon ="🏅"
                                                                
                                                            available = ""
                                                            if card['EXCLUSIVE'] and not card['HAS_COLLECTION']:
                                                                dungeon_card_details.append(
                                                                    f"[{str(index)}] {universe_crest} : 🀄 **{card['TIER']}** **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n🔥 **{level_icon}**: {str(level)} ❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")
                                                            elif not card['HAS_COLLECTION']:
                                                                tales_card_details.append(
                                                                    f"[{str(index)}] {universe_crest} : 🀄 **{card['TIER']}** **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n🎴 **{level_icon}**: {str(level)} ❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")
                                                            elif card['HAS_COLLECTION']:
                                                                destiny_card_details.append(
                                                                    f"[{str(index)}] {universe_crest} : 🀄 **{card['TIER']}** **{card['NAME']}** [{class_emoji}] {basic_attack_emoji} {super_attack_emoji} {ultimate_attack_emoji}\n✨ **{level_icon}**: {str(level)} ❤️ {card['HLT']} 🗡️ {card['ATK']}  🛡️ {card['DEF']}\n")

                                                        all_cards = []
                                                        if tales_card_details:
                                                            for t in tales_card_details:
                                                                all_cards.append(t)

                                                        if dungeon_card_details:
                                                            for d in dungeon_card_details:
                                                                all_cards.append(d)

                                                        if destiny_card_details:
                                                            for de in destiny_card_details:
                                                                all_cards.append(de)

                                                        total_cards = len(all_cards)

                                                        # Adding to array until divisible by 10
                                                        while len(all_cards) % 10 != 0:
                                                            all_cards.append("")
                                                        # Check if divisible by 10, then start to split evenly

                                                        if len(all_cards) % 10 == 0:
                                                            first_digit = int(str(len(all_cards))[:1])
                                                            if len(all_cards) >= 89:
                                                                if first_digit == 1:
                                                                    first_digit = 10
                                                            # first_digit = 10
                                                            cards_broken_up = np.array_split(all_cards, first_digit)

                                                        # If it's not an array greater than 10, show paginationless embed
                                                        if len(all_cards) < 10:
                                                            embedVar = Embed(title=f"🕋 | {guild['GNAME']}'s Card Armory", description="\n".join(all_cards), color=0x7289da)
                                                            embedVar.set_footer(
                                                                text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(card_storage))} Storage Available")
                                                            await ctx.send(embed=embedVar)

                                                        embed_list = []
                                                        for i in range(0, len(cards_broken_up)):
                                                            embedVar = Embed(
                                                                title=f"🕋 | {guild['GNAME']}'s Card Armory",
                                                                description="\n".join(cards_broken_up[i]), color=0x7289da)
                                                            embedVar.set_footer(
                                                                text=f"{total_cards} Total Cards\n{str(storage_allowed_amount - len(card_storage))} Storage Available")
                                                            embed_list.append(embedVar)

                                                        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                                                        paginator.add_reaction('⏮️', "first")
                                                        paginator.add_reaction('⬅️', "back")
                                                        paginator.add_reaction('🔐', "lock")
                                                        paginator.add_reaction('➡️', "next")
                                                        paginator.add_reaction('⏭️', "last")
                                                        embeds = embed_list
                                                        await paginator.run(embeds)
                                                    else:
                                                        await ctx.send("🕋 | Card Armory Empty...")
                                                        return
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
                                                
                                            if button_ctx.custom_id == "titles":
                                                title_storage = guild['TSTORAGE']
                                                storage_allowed_amount = 300
                                                if len(title_storage) > 0:
                                                    list_of_titles = db.querySpecificTitles(guild['TSTORAGE'])
                                                    titles = [x for x in list_of_titles]
                                                    dungeon_title_details = []
                                                    tales_title_details = []
                                                    boss_title_details = []
                                                    unbound_title_details = []
                                                    for title in titles:
                                                        title_title = title['TITLE']
                                                        title_show = title['UNIVERSE']
                                                        exclusive = title['EXCLUSIVE']
                                                        available = title['AVAILABLE']
                                                        title_passive = title['ABILITIES'][0]
                                                        title_passive_type = list(title_passive.keys())[0]
                                                        title_passive_value = list(title_passive.values())[0]


                                                    
                                                        universe_crest = crown_utilities.crest_dict[title_show]
                                                        index = guild['TSTORAGE'].index(title_title)

                                                        if title_show == "Unbound":
                                                            unbound_title_details.append(
                                                                f"[{str(index)}] {universe_crest} :crown: : **{title_title}**\n**🦠 {title_passive_type}**: *{title_passive_value}*\n")
                                                        elif not exclusive and not available:
                                                            boss_title_details.append(
                                                                f"[{str(index)}] {universe_crest} 👹 : **{title_title}**\n**🦠 {title_passive_type}**:  *{title_passive_value}*\n")
                                                        elif exclusive and available:
                                                            dungeon_title_details.append(
                                                                f"[{str(index)}] {universe_crest} 🔥 : **{title_title}**\n**🦠 {title_passive_type}**: *{title_passive_value}*\n")
                                                        elif available and not exclusive:
                                                            tales_title_details.append(
                                                                f"[{str(index)}] {universe_crest} 🎗️ : **{title_title}**\n**🦠 {title_passive_type}**:  *{title_passive_value}*\n")

                                                    all_titles = []
                                                    
                                                    if unbound_title_details:
                                                        for u in unbound_title_details:
                                                            all_titles.append(u)
                                                            
                                                    if tales_title_details:
                                                        for t in tales_title_details:
                                                            all_titles.append(t)

                                                    if dungeon_title_details:
                                                        for d in dungeon_title_details:
                                                            all_titles.append(d)

                                                    if boss_title_details:
                                                        for de in boss_title_details:
                                                            all_titles.append(de)
                                                    
                                                    

                                                    total_titles = len(all_titles)

                                                    # Adding to array until divisible by 10
                                                    while len(all_titles) % 10 != 0:
                                                        all_titles.append("")
                                                    # Check if divisible by 10, then start to split evenly

                                                    if len(all_titles) % 10 == 0:
                                                        first_digit = int(str(len(all_titles))[:1])
                                                        if len(all_titles) >= 89:
                                                            if first_digit == 1:
                                                                first_digit = 10
                                                        # first_digit = 10
                                                        titles_broken_up = np.array_split(all_titles, first_digit)

                                                    # If it's not an array greater than 10, show paginationless embed
                                                    if len(all_titles) < 10:
                                                        embedVar = Embed(title=f"🕋 | {guild['GNAME']}'s Title Armory", description="\n".join(all_titles), color=0x7289da)
                                                        embedVar.set_footer(
                                                            text=f"{total_titles} Total Titles\n{str(storage_allowed_amount - len(guild['TSTORAGE']))} Storage Available")
                                                        await ctx.send(embed=embedVar)

                                                    embed_list = []
                                                    for i in range(0, len(titles_broken_up)):
                                                        embedVar = Embed(
                                                            title=f"🕋 | {guild['GNAME']}'s Title Armory",
                                                            description="\n".join(titles_broken_up[i]), color=0x7289da)
                                                        embedVar.set_footer(
                                                            text=f"{total_titles} Total Titles\n{str(storage_allowed_amount - len(guild['TSTORAGE']))} Storage Available")
                                                        embed_list.append(embedVar)

                                                    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                                                    paginator.add_reaction('⏮️', "first")
                                                    paginator.add_reaction('⬅️', "back")
                                                    paginator.add_reaction('🔐', "lock")
                                                    paginator.add_reaction('➡️', "next")
                                                    paginator.add_reaction('⏭️', "last")
                                                    embeds = embed_list
                                                    await paginator.run(embeds)
                                                else:
                                                    await ctx.send("🕋 | Title Armory Empty...")
                                                    return
                                            if button_ctx.custom_id == "arms":
                                                arm_storage = guild['ASTORAGE']
                                                storage_allowed_amount = 300
                                                if len(arm_storage) > 0:
                                                    storage_card_names = []
                                                    for name in guild['ASTORAGE']:
                                                        storage_card_names.append(name['ARM'])
                                            
                                                    list_of_arms = db.querySpecificArms(storage_card_names)

                                                    arms = [x for x in list_of_arms]
                                                    dungeon_arm_details = []
                                                    tales_arm_details = []
                                                    boss_arm_details = []
                                                    unbound_arm_details = []
                                                    icon = ""
                                                    for arm in arms:
                                                        durability = 0
                                                        for name in guild['ASTORAGE']:
                                                            if name['ARM'] == arm['ARM']:
                                                                durability = int(name['DUR'])
                                                        element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
                                                        arm_name = arm['ARM']
                                                        arm_show = arm['UNIVERSE']
                                                        exclusive = arm['EXCLUSIVE']
                                                        available = arm['AVAILABLE']
                                                        element = arm['ELEMENT']
                                                        if element:
                                                            element_name = element.title()
                                                            element = crown_utilities.set_emoji(element)
                                                        else:
                                                            element = "🦠"
                                                        arm_passive = arm['ABILITIES'][0]
                                                            # Arm Passive
                                                        arm_passive_type = list(arm_passive.keys())[0]
                                                        arm_passive_value = list(arm_passive.values())[0]
                                                        
                                                        icon = element
                                                        if arm_passive_type == "SHIELD":
                                                            icon = "🌐"
                                                        if arm_passive_type == "PARRY":
                                                            icon = "🔄"
                                                        if arm_passive_type == "BARRIER":
                                                            icon = "💠"
                                                        if arm_passive_type == "SIPHON":
                                                            icon = "💉"

                                                    
                                                        universe_crest = crown_utilities.crest_dict[arm_show]
                                                        index = guild['ASTORAGE'].index({'ARM': arm_name, 'DUR' : durability})

                                                        if arm_show == "Unbound":
                                                            unbound_arm_details.append(
                                                                f"[{str(index)}] {universe_crest} :crown: {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** : *{arm_passive_value}*\n")
                                                        elif not exclusive and not available:
                                                            boss_arm_details.append(
                                                                f"[{str(index)}] {universe_crest} 👹 {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** :  *{arm_passive_value}*\n")
                                                        elif exclusive and available:
                                                            dungeon_arm_details.append(
                                                                f"[{str(index)}] {universe_crest} 🔥 {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** : *{arm_passive_value}*\n")
                                                        elif available and not exclusive:
                                                            tales_arm_details.append(
                                                                f"[{str(index)}] {universe_crest} 🦾 {icon} : **{arm_name}** ⚒️*{durability}*\n**{arm_passive_type}** :  *{arm_passive_value}*\n")

                                                    all_arms = []
                                                    if unbound_arm_details:
                                                        for u in unbound_arm_details:
                                                            all_arms.append(u)
                                                            
                                                    if tales_arm_details:
                                                        for t in tales_arm_details:
                                                            all_arms.append(t)

                                                    if dungeon_arm_details:
                                                        for d in dungeon_arm_details:
                                                            all_arms.append(d)

                                                    if boss_arm_details:
                                                        for de in boss_arm_details:
                                                            all_arms.append(de)

                                                    

                                                    total_arms = len(all_arms)

                                                    # Adding to array until divisible by 10
                                                    while len(all_arms) % 10 != 0:
                                                        all_arms.append("")
                                                    # Check if divisible by 10, then start to split evenly

                                                    if len(all_arms) % 10 == 0:
                                                        first_digit = int(str(len(all_arms))[:1])
                                                        if len(all_arms) >= 89:
                                                            if first_digit == 1:
                                                                first_digit = 10
                                                        # first_digit = 10
                                                        arms_broken_up = np.array_split(all_arms, first_digit)

                                                    # If it's not an array greater than 10, show paginationless embed
                                                    if len(all_arms) < 10:
                                                        embedVar = Embed(title=f"🕋 | {guild['GNAME']}'s Arm Armory", description="\n".join(all_arms), color=0x7289da)
                                                        embedVar.set_footer(
                                                            text=f"{total_arms} Total Arms\n{str(storage_allowed_amount - len(guild['ASTORAGE']))} Storage Available")
                                                        await ctx.send(embed=embedVar)

                                                    embed_list = []
                                                    for i in range(0, len(arms_broken_up)):
                                                        embedVar = Embed(
                                                            title=f"🕋 | {guild['GNAME']}'s Arm Armory",
                                                            description="\n".join(arms_broken_up[i]), color=0x7289da)
                                                        embedVar.set_footer(
                                                            text=f"{total_arms} Total Arms\n{str(storage_allowed_amount - len(guild['ASTORAGE']))} Storage Available")
                                                        embed_list.append(embedVar)

                                                    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                                                    paginator.add_reaction('⏮️', "first")
                                                    paginator.add_reaction('⬅️', "back")
                                                    paginator.add_reaction('🔐', "lock")
                                                    paginator.add_reaction('➡️', "next")
                                                    paginator.add_reaction('⏭️', "last")
                                                    embeds = embed_list
                                                    await paginator.run(embeds)
                                                else:
                                                    await ctx.send("🕋 | Arm Armory Empty...")
                                                    return
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
                                    if button_ctx.custom_id == "upgrade":   
                                        await msg.delete()    
                                        await ctx.send("🕋 | Armory Upgrades Coming Soon...")
                                        return
                                        #print("Armory Upgrades Coming Soon")  
                                    if button_ctx.custom_id == "donate":  
                                        # await msg.delete()    
                                        # await ctx.send("🕋 | Armory Donations Coming Soon...")
                                        # return  
                                        await msg.delete()
                                        donate_buttons = [
                                            Button(style=2, label="Donate Cards", custom_id="cards"),
                                            Button(style=3, label="Donate Titles", custom_id="titles"),
                                            Button(style=1, label="Donate Arms", custom_id="arms"),
                                            
                                        ]
                                        donate_action_row = ActionRow(*donate_buttons)
                                        donate_item_screen = Embed(title=f"{guild['GNAME']} Armory!", description=textwrap.dedent(f"""\
                                        {armory_message}
                                        
                                        🕋 **Armory Inventory** | 300
                                        🎴 **Cards** |  {len(guild['CSTORAGE'])}
                                        🎗️ **Titles** |  {len(guild['TSTORAGE'])}
                                        🦾 **Arms** |  {len(guild['ASTORAGE'])}
                                        """), color=0xe74c3c)
                                        donate_item_screen.set_image(url="https://cdnb.artstation.com/p/assets/images/images/036/549/141/original/jonathan-dodd-mdz2-large-warehouse-port.gif?1617957276")
                                        
                                        msg = await ctx.send(embed=donate_item_screen, components=[donate_action_row])
                                        def check(button_ctx):
                                            return button_ctx.author == ctx.author
                                        try:
                                            button_ctx  = await self.bot.wait_for_component(components=[donate_action_row], timeout=120, check=check)
                                            if button_ctx.custom_id == "cards": 
                                                query = {'DID': str(ctx.author.id)}
                                                d = db.queryUser(query)#Storage Update
                                                storage_type = d['STORAGE_TYPE']
                                                vault = db.queryVault({'DID': d['DID']})
                                                try: 
                                                    if vault:
                                                        name = d['DISNAME'].split("#",1)[0]
                                                        avatar = d['AVATAR']
                                                        card_levels = vault['CARD_LEVELS']
                                                        current_gems = []
                                                        for gems in vault['GEMS']:
                                                            current_gems.append(gems['UNIVERSE'])
                                                        balance = vault['BALANCE']
                                                        cards_list = vault['CARDS']
                                                        total_cards = len(cards_list)
                                                        current_card = d['CARD']
                                                        storage = vault['STORAGE']
                                                        cards=[]
                                                        icon = "🪙"
                                                        if balance >= 150000:
                                                            icon = "💸"
                                                        elif balance >=100000:
                                                            icon = "💰"
                                                        elif balance >= 50000:
                                                            icon = "💵"
                                                        
                                                        embed_list = []

                                                        for card in cards_list:
                                                            index = cards_list.index(card)
                                                            resp = db.queryCard({"NAME": str(card)})
                                                            card_tier = 0
                                                            lvl = ""
                                                            tier = ""
                                                            speed = 0
                                                            card_tier = f"🀄 {resp['TIER']}"
                                                            card_available = resp['AVAILABLE']
                                                            card_exclusive = resp['EXCLUSIVE']
                                                            card_collection = resp['HAS_COLLECTION']
                                                            show_img = db.queryUniverse({'TITLE': resp['UNIVERSE']})['PATH']
                                                            affinity_message = crown_utilities.set_affinities(resp)
                                                            o_show = resp['UNIVERSE']
                                                            icon = "🎴"
                                                            if card_available and card_exclusive:
                                                                icon = "🔥"
                                                            elif card_available == False and card_exclusive ==False:
                                                                if card_collection:
                                                                    icon =":sparkles:"
                                                                else:
                                                                    icon = ":japanese_ogre:"
                                                            card_lvl = 0
                                                            card_exp = 0
                                                            card_lvl_attack_buff = 0
                                                            card_lvl_defense_buff = 0
                                                            card_lvl_ap_buff = 0
                                                            card_lvl_hlt_buff = 0

                                                            for cl in card_levels:
                                                                if card == cl['CARD']:
                                                                    
                                                                    licon = "🔰"
                                                                    if cl['LVL'] >= 200:
                                                                        licon ="🔱"
                                                                    if cl['LVL'] >= 700:
                                                                        licon ="⚜️"
                                                                    if cl['LVL'] >= 999:
                                                                        licon = "🏅"
                                                                    lvl = f"{licon} **{cl['LVL']}**"
                                                                    card_lvl = cl['LVL']
                                                                    card_exp = cl['EXP']
                                                                    card_lvl_ap_buff = crown_utilities.level_sync_stats(card_lvl, "AP")
                                                                    card_lvl_attack_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                                                                    card_lvl_defense_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                                                                    card_lvl_hlt_buff = crown_utilities.level_sync_stats(card_lvl, "HLT")
                                                                    
                                                            
                                                            o_moveset = resp['MOVESET']
                                                            o_1 = o_moveset[0]
                                                            o_2 = o_moveset[1]
                                                            o_3 = o_moveset[2]
                                                            o_enhancer = o_moveset[3]
                                                            
                                                            # Move 1
                                                            move1 = list(o_1.keys())[0]
                                                            move1ap = list(o_1.values())[0] + card_lvl_ap_buff
                                                            move1_stamina = list(o_1.values())[1]
                                                            move1_element = list(o_1.values())[2]
                                                            move1_emoji = crown_utilities.set_emoji(move1_element)
                                                            
                                                            # Move 2
                                                            move2 = list(o_2.keys())[0]
                                                            move2ap = list(o_2.values())[0] + card_lvl_ap_buff
                                                            move2_stamina = list(o_2.values())[1]
                                                            move2_element = list(o_2.values())[2]
                                                            move2_emoji = crown_utilities.set_emoji(move2_element)


                                                            # Move 3
                                                            move3 = list(o_3.keys())[0]
                                                            move3ap = list(o_3.values())[0] + card_lvl_ap_buff
                                                            move3_stamina = list(o_3.values())[1]
                                                            move3_element = list(o_3.values())[2]
                                                            move3_emoji = crown_utilities.set_emoji(move3_element)


                                                            # Move Enhancer
                                                            move4 = list(o_enhancer.keys())[0]
                                                            move4ap = list(o_enhancer.values())[0]
                                                            move4_stamina = list(o_enhancer.values())[1]
                                                            move4enh = list(o_enhancer.values())[2]
                                                        
                                                            traits = ut.traits
                                                            mytrait = {}
                                                            traitmessage = ''
                                                            for trait in traits:
                                                                if trait['NAME'] == o_show:
                                                                    mytrait = trait
                                                                if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                                                                    if trait['NAME'] == 'Pokemon':
                                                                        mytrait = trait
                                                            if mytrait:
                                                                traitmessage = f"**{mytrait['EFFECT']}:** {mytrait['TRAIT']}"


                                                            embedVar = Embed(title= f"{resp['NAME']}", description=textwrap.dedent(f"""\
                                                            {icon} **[{index}]** 
                                                            {card_tier}: {lvl}
                                                            ❤️ **{resp['HLT']}** 🗡️ **{resp['ATK']}** 🛡️ **{resp['DEF']}** 🏃 **{resp['SPD']}**

                                                            {move1_emoji} **{move1}:** {move1ap}
                                                            {move2_emoji} **{move2}:** {move2ap}
                                                            {move3_emoji} **{move3}:** {move3ap}
                                                            🦠 **{move4}:** {move4enh} {move4ap}{enhancer_suffix_mapping[move4enh]}

                                                            ♾️ {traitmessage}
                                                            """), color=0x7289da)
                                                            embedVar.add_field(name="__Affinities__", value=f"{affinity_message}")
                                                            embedVar.set_thumbnail(url=show_img)
                                                            embedVar.set_footer(text=f"/enhancers - 🩸 Enhancer Menu")
                                                            embed_list.append(embedVar)

                                                        buttons = [
                                                            Button(style=3, label="Donate", custom_id="Donate"),
                                                        ]
                                                        custom_action_row = ActionRow(*buttons)
                                                        # custom_button = Button(style=3, label="Equip")

                                                        async def custom_function(self, button_ctx):
                                                            if button_ctx.author == ctx.author:
                                                                updated_vault = db.queryVault({'DID': d['DID']})
                                                                sell_price = 0

                                                                selected_card = str(button_ctx.origin_message.embeds[0].title)
                                                                card_levels = updated_vault['CARD_LEVELS']
                                                                for cl in card_levels:
                                                                    if selected_card == cl['CARD']:
                                                                        card_lvl = cl['LVL']
                                                                        card_tier = cl['TIER']
                                                                        card_exp = cl['EXP']
                                                                        card_lvl_ap_buff = crown_utilities.level_sync_stats(card_lvl, "AP")
                                                                        card_lvl_attack_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                                                                        card_lvl_defense_buff = crown_utilities.level_sync_stats(card_lvl, "ATK_DEF")
                                                                        card_lvl_hlt_buff = crown_utilities.level_sync_stats(card_lvl, "HLT")
                                                                if button_ctx.custom_id == "Donate":
                                                                    #print("donate")
                                                                    guild_query = {"GNAME": guild["GNAME"]}
                                                                    if selected_card == d['CARD']:
                                                                        await ctx.send(f"🕋 | **{selected_card}** cannot donate Equipped Card")
                                                                        return
                                                                    if len(card_storage) <= 300:
                                                                        transaction_message = f":kaaba:  | {ctx.author} Donated 🎴**{selected_card}**."
                                                                        query = {'DID': str(ctx.author.id)}
                                                                        update_storage_query = {
                                                                            '$pull': {'CARDS': selected_card, 'CARD_LEVELS': {'CARD' :  selected_card}},
                                                                        }
                                                                        response = db.updateUserNoFilter(query, update_storage_query)
                                                                        update_gstorage_query = {
                                                                            '$addToSet' : {'CSTORAGE' : str(selected_card)},
                                                                            '$push': {'TRANSACTIONS': transaction_message}                                                                         
                                                                        }
                                                                        response = db.updateGuildAlt(guild_query, update_gstorage_query)
                                                                        update_glevel_query = {
                                                                        '$addToSet' : {
                                                                                'S_CARD_LEVELS': {'CARD': str(selected_card), 'LVL': card_lvl, 'TIER': card_tier, 'EXP': card_exp,
                                                                                                'HLT': card_lvl_hlt_buff, 'ATK': card_lvl_attack_buff, 'DEF': card_lvl_defense_buff, 'AP': card_lvl_ap_buff}}
                                                                        }
                                                                        response = db.updateGuildAlt(guild_query, update_glevel_query)
                                                                        await msg.delete()
                                                                        await ctx.send(f"🕋 | **{selected_card}** has been added to the Armory")
                                                                        return
                                                                    else:
                                                                        await ctx.send("Not enough space in storage")
                                                                        return
                                                            else:
                                                                await ctx.send("This is not your card list.")
                                                        await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                                                            custom_action_row,
                                                            custom_function,
                                                        ]).run()
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
                                            if button_ctx.custom_id == "titles":
                                                query = {'DID': str(ctx.author.id)}
                                                guild_query = {"GNAME": guild["GNAME"]}
                                                d = db.queryUser(query)
                                                vault = db.queryVault({'DID': d['DID']})
                                                storage_type = d['STORAGE_TYPE']
                                                if vault:
                                                    try:
                                                        name = d['DISNAME'].split("#",1)[0]
                                                        avatar = d['AVATAR']
                                                        balance = vault['BALANCE']
                                                        current_title = d['TITLE']
                                                        titles_list = vault['TITLES']
                                                        total_titles = len(titles_list)
                                                        storage = vault['TSTORAGE']
                                                        titles=[]
                                                        current_gems = []
                                                        for gems in vault['GEMS']:
                                                            current_gems.append(gems['UNIVERSE'])
                                                        icon = "🪙"
                                                        if balance >= 150000:
                                                            icon = "💸"
                                                        elif balance >=100000:
                                                            icon = "💰"
                                                        elif balance >= 50000:
                                                            icon = "💵"


                                                        embed_list = []
                                                        for title in titles_list:
                                                            index = titles_list.index(title)
                                                            resp = db.queryTitle({"TITLE": str(title)})
                                                            title_passive = resp['ABILITIES'][0]
                                                            title_passive_type = list(title_passive.keys())[0]
                                                            title_passive_value = list(title_passive.values())[0]
                                                            title_available = resp['AVAILABLE']
                                                            title_exclusive = resp['EXCLUSIVE']
                                                            icon = "🎗️"
                                                            if resp['UNIVERSE'] == "Unbound":
                                                                icon = ":crown:"
                                                            elif title_available and title_exclusive:
                                                                icon = "🔥"
                                                            elif title_available == False and title_exclusive ==False:
                                                                icon = ":japanese_ogre:"
                                                            
                                                            
                                                            embedVar = Embed(title= f"{resp['TITLE']}", description=textwrap.dedent(f"""
                                                            {icon} **[{index}]**
                                                            🦠 **{title_passive_type}:** {title_passive_value}
                                                            🌍 **Universe:** {resp['UNIVERSE']}"""), 
                                                            color=0x7289da)
                                                            embedVar.set_thumbnail(url=player_class.avatar)
                                                            embedVar.set_footer(text=f"{title_passive_type}: {title_enhancer_mapping[title_passive_type]}")
                                                            embed_list.append(embedVar)
                                                        
                                                        buttons = [
                                                            Button(style=3, label="Donate", custom_id="Donate"),
                                                        ]
                                                        custom_action_row = ActionRow(*buttons)

                                                        async def custom_function(self, button_ctx):
                                                            if button_ctx.author == ctx.author:
                                                                updated_vault = db.queryVault({'DID': d['DID']})
                                                                sell_price = 0
                                                                selected_title = str(button_ctx.origin_message.embeds[0].title)
                                                                if selected_title == d['TITLE']:
                                                                        await ctx.send(f"🕋 | **{selected_title}** cannot donate Equipped Title")
                                                                        return
                                                                if button_ctx.custom_id == "Donate":
                                                                    if len(title_storage) <= 300:
                                                                        transaction_message = f":kaaba:  | {ctx.author} Donated 🎗️ **{selected_title}**."
                                                                        query = {'DID': str(ctx.author.id)}
                                                                        update_storage_query = {
                                                                            '$pull': {'TITLES': selected_title},
                                                                        }
                                                                        response = db.updateUserNoFilter(query, update_storage_query)
                                                                        update_gstorage_query = {
                                                                            '$addToSet' : {'TSTORAGE' : str(selected_title)},
                                                                            '$push': {'TRANSACTIONS': transaction_message}                                                                          
                                                                        }
                                                                        response = db.updateGuildAlt(guild_query, update_gstorage_query)
                                                                        await msg.delete()
                                                                        await ctx.send(f"🕋 | **{selected_title}** has been added to the Armory")
                                                                        return
                                                                    else:
                                                                        await ctx.send("Not enough space in storage")
                                                                        return
                                                            else:
                                                                await ctx.send("This is not your card list.")
                                                        await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                                                            custom_action_row,
                                                            custom_function,
                                                        ]).run()
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
                                            if button_ctx.custom_id == "arms":
                                                guild_query = {"GNAME": guild["GNAME"]}
                                                query = {'DID': str(ctx.author.id)}
                                                d = db.queryUser(query)
                                                vault = db.queryVault({'DID': d['DID']})
                                                
                                                storage_type = d['STORAGE_TYPE']
                                                if vault:
                                                    try:
                                                        name = d['DISNAME'].split("#",1)[0]
                                                        avatar = d['AVATAR']
                                                        current_arm = d['ARM']
                                                        balance = vault['BALANCE']
                                                        arms_list = vault['ARMS']
                                                        total_arms = len(arms_list)
                                                        storage = vault['ASTORAGE']
                                                        arms=[]
                                                        current_gems = []
                                                        for gems in vault['GEMS']:
                                                            current_gems.append(gems['UNIVERSE'])

                                                        icon = "🪙"
                                                        if balance >= 150000:
                                                            icon = "💸"
                                                        elif balance >=100000:
                                                            icon = "💰"
                                                        elif balance >= 50000:
                                                            icon = "💵"

                                                        embed_list = []
                                                        for arm in arms_list:
                                                            index = arms_list.index(arm)
                                                            resp = db.queryArm({"ARM": str(arm['ARM'])})
                                                            element = resp['ELEMENT']
                                                            arm_passive = resp['ABILITIES'][0]
                                                            arm_passive_type = list(arm_passive.keys())[0]
                                                            arm_passive_value = list(arm_passive.values())[0]
                                                            arm_available = resp['AVAILABLE']
                                                            arm_exclusive = resp['EXCLUSIVE']
                                                            icon = "🦾"
                                                            if resp['UNIVERSE'] == "Unbound":
                                                                icon = ":crown:"
                                                            elif arm_available and arm_exclusive:
                                                                icon = "🔥"
                                                            elif arm_available == False and arm_exclusive ==False:
                                                                icon = ":japanese_ogre:"
                                                            element_available = ['BASIC', 'SPECIAL', 'ULTIMATE']
                                                            if element and arm_passive_type in element_available:
                                                                element_name = element
                                                                element = crown_utilities.set_emoji(element)
                                                                arm_type = f"**{arm_passive_type.title()} {element_name.title()} Attack**"
                                                                arm_message = f"{element} **{resp['ARM']}:** {arm_passive_value}"
                                                                footer = f"The new {arm_passive_type.title()} attack will reflect on your card when equipped"

                                                            else:
                                                                arm_type = f"**Unique Passive**"
                                                                arm_message = f"🦠 **{arm_passive_type.title()}:** {arm_passive_value}"
                                                                footer = f"{arm_passive_type}: {enhancer_mapping[arm_passive_type]}"



                                                            embedVar = Embed(title= f"{resp['ARM']}", description=textwrap.dedent(f"""
                                                            {icon} **[{index}]**

                                                            {arm_type}
                                                            {arm_message}
                                                            🌍 **Universe:** {resp['UNIVERSE']}
                                                            ⚒️ {arm['DUR']}
                                                            """), 
                                                            color=0x7289da)
                                                            embedVar.set_thumbnail(url=player_class.avatar)
                                                            embedVar.set_footer(text=f"{footer}")
                                                            embed_list.append(embedVar)
                                                        
                                                        buttons = [
                                                            Button(style=3, label="Donate", custom_id="Donate"),
                                                        ]
                                                        custom_action_row = ActionRow(*buttons)

                                                        async def custom_function(self, button_ctx):
                                                            if button_ctx.author == ctx.author:
                                                                u_vault = db.queryVault({'DID': d['DID']})
                                                                updated_vault = []
                                                                storage = u_vault['ASTORAGE']
                                                                for arm in u_vault['ARMS']:
                                                                    updated_vault.append(arm['ARM'])
                                                                
                                                                sell_price = 0
                                                                selected_arm = str(button_ctx.origin_message.embeds[0].title)
                                                                if selected_arm == d['ARM']:
                                                                        await ctx.send(f"🕋 | **{selected_arm}** cannot donate Equipped Arm")
                                                                        return
                                                                if button_ctx.custom_id == "Donate":
                                                                    durability = 0
                                                                    for names in u_vault['ARMS']:
                                                                        if names['ARM'] == selected_arm:
                                                                            durability = names['DUR']
                                                                    if len(arm_storage) <= 300:
                                                                        transaction_message = f":kaaba:  | {ctx.author} Donated 🦾 **{selected_arm}**."
                                                                        query = {'DID': str(ctx.author.id)}
                                                                        update_storage_query = {
                                                                            '$pull': {'ARMS': {'ARM' : str(selected_arm)}}
                                                                        }
                                                                        response = db.updateUserNoFilter(query, update_storage_query)
                                                                        update_gstorage_query = {
                                                                            '$addToSet' : {'ASTORAGE': { 'ARM' : str(selected_arm), 'DUR' : int(durability)}},
                                                                            '$push': {'TRANSACTIONS': transaction_message}                                                                           
                                                                        }
                                                                        response = db.updateGuildAlt(guild_query, update_gstorage_query)
                                                                        await msg.delete()
                                                                        await ctx.send(f"🕋 | **{selected_arm}** has been added to the Armory")
                                                                        return
                                                            else:
                                                                await ctx.send("This is not your card list.")
                                                        await Paginator(bot=self.bot, disableAfterTimeout=True, useQuitButton=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                                                            custom_action_row,
                                                            custom_function,
                                                        ]).run()
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
                        else:
                            await ctx.send("This is not your command.")    
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
                await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
            else:
                await ctx.send(m.GUILD_DOESNT_EXIST)
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

async def raid(ctx, guild):
    registered_player = await crown_utilities.player_check(ctx)
    if not registered_player:
        return

    try:
        guildname = guild
        private_channel = ctx
        if isinstance(private_channel.channel, discord.channel.DMChannel):
            await private_channel.send(m.SERVER_FUNCTION_ONLY)
            return
        starttime = time.asctime()
        h_gametime = starttime[11:13]
        m_gametime = starttime[14:16]
        s_gametime = starttime[17:19]

        # Get Session Owner Disname for scoring
        sowner = db.queryUser({'DID': str(ctx.author.id)})
        if sowner['DIFFICULTY'] == "EASY":
            await ctx.send("Raiding is unavailable on Easy Mode! Use /difficulty to change your difficulty setting.")
            return

        guild = sowner['TEAM']
        guild_info = db.queryTeam({'TEAM_NAME': guild.lower()})
        oguild_name = "PCG"
        shield_test_active = False
        shield_training_active = False
        if guild_info:
            oguild_name = guild_info['GUILD']
            oassociation = db.queryGuildAlt({'GNAME': oguild_name})
        player_guild = sowner['GUILD']

        if oguild_name == "PCG":
            await ctx.send(m.NO_GUILD, delete_after=5)
            return
        if oassociation['SHIELD'] == sowner['DISNAME']:
            shield_training_active = True
        elif player_guild == guildname:
            shield_test_active = True
            

        guild_query = {'GNAME': guildname}
        association_info = db.queryGuildAlt(guild_query)
        guild_shield = ""

        if not association_info:
            await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
            return
        guild_shield = association_info['SHIELD']
        shield_id = association_info['SDID']
        guild_hall = association_info['HALL']
        hall_info = db.queryHall({'HALL': str(guild_hall)})
        hall_def = hall_info['DEFENSE']
        t_user = db.queryUser({'DID': shield_id})
        tteam_name = t_user['TEAM']
        tteam_info = db.queryTeam({'TEAM_NAME': tteam_name.lower()})
        tteam = tteam_info['TEAM_NAME']
        tguild = tteam_info['GUILD']
        if tteam_info:
            tguild = tteam_info['GUILD']
        tarm = db.queryArm({'ARM': t_user['ARM']})
        ttitle = db.queryTitle({'TITLE': t_user['TITLE']})
        
        # Guild Fees
        title_match_active = False
        fee = hall_info['FEE']
        if oguild_name == tguild:
            title_match_active = True
        
        
        mode = "RAID"
        
        player = sowner
        player2 = t_user
        p1 = Player(player['AUTOSAVE'], player['DISNAME'], player['DID'], player['AVATAR'], oguild_name, player['TEAM'], player['FAMILY'], player['TITLE'], player['CARD'], player['ARM'], player['PET'], player['TALISMAN'], player['CROWN_TALES'], player['DUNGEONS'], player['BOSS_WINS'], player['RIFT'], player['REBIRTH'], player['LEVEL'], player['EXPLORE'], player['SAVE_SPOT'], player['PERFORMANCE'], player['TRADING'], player['BOSS_FOUGHT'], player['DIFFICULTY'], player['STORAGE_TYPE'], player['USED_CODES'], player['BATTLE_HISTORY'], player['PVP_WINS'], player['PVP_LOSS'], player['RETRIES'], player['PRESTIGE'], player['PATRON'], player['FAMILY_PET'], player['EXPLORE_LOCATION'], player['SCENARIO_HISTORY'])    
        p2 = Player(player2['AUTOSAVE'], player2['DISNAME'], player2['DID'], player2['AVATAR'], tteam, player2['TEAM'], player2['FAMILY'], player2['TITLE'], player2['CARD'], player2['ARM'], player2['PET'], player2['TALISMAN'], player2['CROWN_TALES'], player2['DUNGEONS'], player2['BOSS_WINS'], player2['RIFT'], player2['REBIRTH'], player2['LEVEL'], player2['EXPLORE'], player2['SAVE_SPOT'], player2['PERFORMANCE'], player2['TRADING'], player2['BOSS_FOUGHT'], player2['DIFFICULTY'], player2['STORAGE_TYPE'], player2['USED_CODES'], player2['BATTLE_HISTORY'], player2['PVP_WINS'], player2['PVP_LOSS'], player2['RETRIES'], player2['PRESTIGE'], player2['PATRON'], player2['FAMILY_PET'], player2['EXPLORE_LOCATION'], player2['SCENARIO_HISTORY'])  
        battle = Battle(mode, p1)
        battle.create_raid(title_match_active, shield_test_active, shield_training_active, association_info, hall_info, tteam, oguild_name)
        


        

        # o = db.queryCard({'NAME': sowner['CARD']})
        # otitle = db.queryTitle({'TITLE': sowner['TITLE']})

        # t = db.queryCard({'NAME': t_user['CARD']})
        # ttitle = db.queryTitle({'TITLE': t_user['TITLE']})
        
        if private_channel:
            await battle_commands(main, ctx, battle, p1, None, p2, player3=None)
        else:
            await ctx.send("Failed to start raid battle!")
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
            'PLAYER': str(ctx.author),
            'type': type(ex).__name__,
            'message': str(ex),
            'trace': trace
        }))
        guild = self.bot.get_guild(self.bot.guild_id)
        channel = guild.get_channel(self.bot.guild_channel)
        await channel.send(f"'PLAYER': **{str(ctx.author)}**, 'GUILD': **{str(ctx.author.guild)}**,  TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
        return


def stat_distribution(stats):
    def accumulate(category_stats, totals):
        for stat in category_stats:
            totals['MATCHES'] += stat['TOTAL_RUNS']
            totals['COMPLETED'] += stat['TOTAL_CLEARS']
            totals['DAMAGE_DEALT'] += stat['DAMAGE_DEALT']
            totals['DAMAGE_HEALED'] += stat['DAMAGE_HEALED']
            totals['DAMAGE_TAKEN'] += stat['DAMAGE_TAKEN']

    totals = {
        'TALES': {'MATCHES': 0, 'COMPLETED': 0, 'DAMAGE_DEALT': 0, 'DAMAGE_HEALED': 0, 'DAMAGE_TAKEN': 0},
        'DUNGEONS': {'MATCHES': 0, 'COMPLETED': 0, 'DAMAGE_DEALT': 0, 'DAMAGE_HEALED': 0, 'DAMAGE_TAKEN': 0},
        'SCENARIOS': {'MATCHES': 0, 'COMPLETED': 0, 'DAMAGE_DEALT': 0, 'DAMAGE_HEALED': 0, 'DAMAGE_TAKEN': 0},
    }

    if stats['TALES_STATS']:
        accumulate(stats['TALES_STATS'], totals['TALES'])
    if stats['DUNGEON_STATS']:
        accumulate(stats['DUNGEON_STATS'], totals['DUNGEONS'])
    if stats['SCENARIO_STATS']:
        accumulate(stats['SCENARIO_STATS'], totals['SCENARIOS'])

    return totals


def setup(bot):
    Lookup(bot)


def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]


enhancer_mapping = {'ATK': 'Increase Attack %',
'DEF': 'Increase Defense %',
'STAM': 'Increase Stamina',
'HLT': 'Heal yourself or companion',
'LIFE': 'Steal Health from Opponent',
'DRAIN': 'Drain Stamina from Opponent',
'FLOG': 'Steal Attack from Opponent',
'WITHER': 'Steal Defense from Opponent',
'RAGE': 'Lose Defense, Increase AP',
'BRACE': 'Lose Attack, Increase AP',
'BZRK': 'Lose Health, Increase Attack',
'CRYSTAL': 'Lose Health, Increase Defense',
'GROWTH': 'Lose 10% Max Health, Increase Attack, Defense and AP',
'STANCE': 'Swap your Attack & Defense, Increase Defense',
'CONFUSE': 'Swap Opponent Attack & Defense, Decrease Opponent Defense',
'BLINK': 'Decrease your  Stamina, Increase Target Stamina',
'SLOW': 'Increase Opponent Stamina, Decrease Your Stamina then Swap Stamina with Opponent',
'HASTE': 'Increase your Stamina, Decrease Opponent Stamina then Swap Stamina with Opponent',
'FEAR': 'Lose 10% Max Health, Decrease Opponent Attack, Defense and AP',
'SOULCHAIN': 'You and Your Opponent Stamina Link',
'GAMBLE': 'You and Your Opponent Health Link',
'WAVE': 'Deal Damage, Decreases over time',
'CREATION': 'Heals you, Decreases over time',
'BLAST': 'Deals Damage, Increases over time based on card tier',
'DESTRUCTION': 'Decreases Your Opponent Max Health, Increases over time based on card tier',
'BASIC': 'Increase Basic Attack AP',
'SPECIAL': 'Increase Special Attack AP',
'ULTIMATE': 'Increase Ultimate Attack AP',
'ULTIMAX': 'Increase All AP Values',
'MANA': 'Increase Enchancer AP',
'SHIELD': 'Blocks Incoming DMG, until broken',
'BARRIER': 'Nullifies Incoming Attacks, until broken',
'PARRY': 'Returns 25% Damage, until broken',
'SIPHON': 'Heal for 10% DMG inflicted + AP'
}



