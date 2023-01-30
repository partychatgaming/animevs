import discord
from discord.embeds import Embed
from discord.ext import commands
import bot as main
import crown_utilities
import db
import classes as data
import messages as m
import numpy as np
import help_commands as h
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from collections import ChainMap
from io import BytesIO
import io
import DiscordUtils
import textwrap
from .crownunlimited import enhancer_mapping, enhancer_suffix_mapping
from collections import Counter
from discord_slash import cog_ext, SlashContext
from dinteractions_Paginator import Paginator
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from crown_utilities import crest_dict



emojis = ['👍', '👎']

class Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_ready(self):
        print('Lookup Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)

    
    @cog_ext.cog_slash(description="Lookup player stats", guild_ids=main.guild_ids)
    async def player(self, ctx, player = None):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            if player:
                player = player.replace("<","")
                player = player.replace(">","")
                player = player.replace("@","")
                player = player.replace("!","")
                
                
                user = await self.bot.fetch_user(player)
                avi = user.avatar_url
                # print(player)
                # print(str(ctx.author.id))
            else:
                player = ctx.author.id
                avi = ctx.author.avatar_url
            query = {'DID': str(player)}
            
            d = db.queryUser(query)
            
            m = db.queryManyMatchesPerPlayer({'PLAYER': d['DISNAME']})
            v = db.queryVault({'DID': str(player)})
            b = db.queryAllBosses()
            user = await self.bot.fetch_user(d['DID'])
            if d:
                balance = v['BALANCE']
                bal_icon = ":coin:"
                if balance >= 50000000:
                    bal_icon = ":money_with_wings:"
                elif balance >= 10000000:
                    bal_icon = ":moneybag:"
                elif balance >= 500000:
                    bal_icon = ":dollar:"

                bal_message = f"{bal_icon}{'{:,}'.format(balance)}"

                all_cards = len(v['CARDS'])
                all_titles = len(v['TITLES'])
                all_arms = len(v['ARMS'])
                all_pets = len(v['PETS'])
                cstorage = len(v['STORAGE'])
                astorage = len(v['ASTORAGE'])
                tstorage = len(v['TSTORAGE'])

                name = d['DISNAME'].split("#",1)[0]
                difficulty = d['DIFFICULTY']
                games = d['GAMES']
                abyss_level = d['LEVEL']
                if abyss_level > 100:
                    abyss_level = "**Conquered**"
                retries = d['RETRIES']
                card = d['CARD']
                ign = d['IGN']
                team = d['TEAM']
                guild = d['GUILD']
                patreon = d['PATRON']
                patreon_message = ""
                if patreon == True:
                    patreon_message = "**💞 | Patreon Supporter**"
                if team != "PCG":
                    team_info = db.queryTeam({'TEAM_NAME' : str(team.lower())})
                    guild = team_info['GUILD']
                family = d['FAMILY']
                
                family_info = db.queryFamily({"HEAD": str(family)})
                if family_info:
                    family_summon = family_info['SUMMON']
                    family_summon_name = family_summon['NAME']
                fs_message = ""
                if d['FAMILY_PET']:
                    fs_message = f":family_mwgb: **Family Summon** *{family_summon_name}*"
                titles = d['TITLE']
                arm = d['ARM']
                battle_history = d['BATTLE_HISTORY']
                avatar = d['AVATAR']
                matches = d['MATCHES']
                tournament_wins = d['TOURNAMENT_WINS']
                crown_tales = d['CROWN_TALES']
                dungeons = d['DUNGEONS']
                bosses = d['BOSS_WINS']
                pvp_wins = d['PVP_WINS']
                pvp_loss = d['PVP_LOSS']
                pet = d['PET']
                rebirth = d['REBIRTH']
                join_raw = d['TIMESTAMP']
                year_joined = join_raw[20:]
                day_joined = join_raw[:10]
                prestige = d['PRESTIGE']
                aicon = ":new_moon:"
                if prestige == 1:
                    aicon = ":waxing_crescent_moon:"
                elif prestige == 2:
                    aicon = ":first_quarter_moon:"
                elif prestige == 3:
                    aicon = ":waxing_gibbous_moon:"
                elif prestige == 4:
                    aicon = ":full_moon:"
                elif prestige == 5:
                    aicon = ":waning_gibbous_moon:"
                elif prestige == 6:
                    aicon = ":last_quarter_moon:"
                elif prestige == 7:
                    aicon = ":waning_crescent_moon:"
                elif prestige == 8:
                    aicon = ":crescent_moon:"
                elif prestige == 9:
                    aicon = ":crown:"
                elif prestige >= 10:
                    aicon = ":japanese_ogre:"
                prestige_message = "*No Prestige*"
                if prestige > 0 :
                    prestige_message = f"**Prestige:** *{prestige}*"
                #print(day_joined + " " + year_joined)
                birthday = f"🎉 | Registered on {day_joined}, {year_joined}"
                icon = ':triangular_flag_on_post:'
                if rebirth == 0:
                    icon = ':triangular_flag_on_post:'
                elif rebirth == 1:
                    icon = ':heart_on_fire:'
                elif rebirth == 2:
                    icon = ':heart_on_fire::heart_on_fire:'
                elif rebirth == 3:
                    icon = ':heart_on_fire::heart_on_fire::heart_on_fire:'
                elif rebirth == 4:
                    icon = ':heart_on_fire::heart_on_fire::heart_on_fire::heart_on_fire:'
                elif rebirth == 5:
                    icon = ':heart_on_fire::heart_on_fire::heart_on_fire::heart_on_fire::heart_on_fire:'

                talisman = d['TALISMAN']
                talisman_message = "No Talisman Equipped"
                if talisman == "NULL":
                    talisman_message = "No Talisman Equipped"
                else:
                    for t in v["TALISMANS"]:
                        if t["TYPE"].upper() == talisman.upper():
                            talisman_emoji = crown_utilities.set_emoji(talisman.upper())
                            talisman_durability = t["DUR"]
                    talisman_message = f"📿| **{talisman_emoji} {talisman.title()}** ⚒️ {talisman_durability}"

                pvp_matches = []
                boss_matches = []
                dungeon_matches = []
                tales_matches = []
                most_played_card = []
                most_played_card_message = "_No Data For Analysis_"
                match_history_message = ""
                most_universe_played = []
                most_played_universe_message = "_No Data For Analysis_"

                wlmatches = list(d['MATCHES'][0].values())[0]
                wins = wlmatches[0]
                losses = wlmatches[1]
                if m:
                    for match in m:
                        most_played_card.append(match['CARD'])
                        if match['UNIVERSE_TYPE'] == "Tales":
                            tales_matches.append(match)
                            most_universe_played.append(match['UNIVERSE'])
                        elif match['UNIVERSE_TYPE'] == "Dungeon":
                            dungeon_matches.append(match)
                            most_universe_played.append(match['UNIVERSE'])
                        elif match['UNIVERSE_TYPE'] == "Boss":
                            boss_matches.append(match)
                            most_universe_played.append(match['UNIVERSE'])
                        elif match['UNIVERSE_TYPE'] == "PVP":
                            pvp_matches.append(match)
                            
                    
                    
                    if not most_universe_played:
                        most_played_universe_message = "_No Data For Analysis_"
                    if not most_played_card:
                        most_played_card_message = "_No Data For Analysis_"
                    else:
                        card_main = most_frequent(most_played_card)
                        fav_uni = most_frequent(most_universe_played)
                        most_played_card_message = f"**Most Played Card: **{card_main}"
                        most_played_universe_message = f"**Favorite Universe: **{fav_uni}"
                        match_history_message = f"""
                        **Tales Played: **{'{:,}'.format(int(len(tales_matches)))}
                        **Dungeons Played: **{'{:,}'.format(len(dungeon_matches))}
                        **Bosses Played: **{'{:,}'.format(len(boss_matches))}
                        **Pvp Played: **{'{:,}'.format(len(pvp_matches))}
                        """

                crown_list = []
                for crown in crown_tales:
                    if crown != "":
                        crown_list.append(f"{crest_dict[crown]} | {crown}")
                
                dungeon_list = []
                for dungeon in dungeons:
                    if dungeon != "":
                        dungeon_list.append(f"{crest_dict[dungeon]} | {dungeon}")

                boss_list =[]
                uni = "Unbound"
                for boss in bosses:
                    if boss != "":
                        boss_info = db.queryBoss({'NAME': str(boss)})
                        uni = boss_info['UNIVERSE']
                        boss_list.append(f"{crest_dict[uni]} | {boss}")

                matches_to_string = dict(ChainMap(*matches))
                ign_to_string = dict(ChainMap(*ign))
                
                



                embed1 = discord.Embed(title= f"{icon} | " + f"{name}".format(self), description=textwrap.dedent(f"""\
                {aicon} | **Abyss Rank**: {abyss_level}
                :flower_playing_cards: | **Card:** {card}
                :reminder_ribbon:** | Title: **{titles}
                :mechanical_arm: | **Arm: **{arm}
                🧬 | **Summon: **{pet}
                {talisman_message}

                :flags: | **Association: **{guild}
                :military_helmet: | **Guild: **{team} 
                :family_mwgb: | **Family: **{family}
                
                🆚 **Retries** {retries} available
                ⚙️ **Battle History Setting** {str(battle_history)} messages
                ⚙️ **Difficulty** {difficulty.lower().capitalize()}
                """), colour=000000)
                embed1.set_thumbnail(url=avatar)
                
                embed5 = discord.Embed(title= f"{icon} | " + f"{name} AnimeVs+ Stats".format(self), description=textwrap.dedent(f"""\
                ⚔️ | **Tales Played: **{'{:,}'.format(int(len(tales_matches)))}
                🔥 | **Dungeons Played: **{'{:,}'.format(len(dungeon_matches))}
                👹 | **Bosses Played: **{'{:,}'.format(len(boss_matches))}
                🆚 | **Pvp Played: **{'{:,}'.format(len(pvp_matches))}
                📊 | **Pvp Record: ** :regional_indicator_w: **{pvp_wins}** / :regional_indicator_l: **{pvp_loss}**
                
                **Balance** | {bal_message}
                :flower_playing_cards: **Cards** | {all_cards} ~ :briefcase: *{cstorage}*
                :reminder_ribbon: **Titles** | {all_titles} ~ :briefcase: *{tstorage}*
                :mechanical_arm: **Arms** | {all_arms} ~ :briefcase: *{astorage}*
                🧬 **Summons** | {all_pets}
                {fs_message}
                """), colour=000000)
                embed5.set_thumbnail(url=avatar)
                
                embed6 = discord.Embed(title= f"{icon} | " + f"{name} AnimeVs+ Avatar".format(self), description=textwrap.dedent(f"""\
                    **:bust_in_silhouette: | User**: {user.mention}
                    {aicon} | {prestige_message}
                    :military_medal: | {most_played_card_message}
                    :earth_africa: | {most_played_universe_message}
                    {patreon_message}
                """), colour=000000)
                embed6.set_image(url=avi)
                embed6.set_footer(text=f"{birthday}")
                # embed1.add_field(name="Team" + " :military_helmet:", value=team)
                # embed1.add_field(name="Family" + " :family_mwgb:", value=family)
                # embed1.add_field(name="Card" + " ::flower_playing_cards: :", value=' '.join(str(x) for x in titles))
                # embed1.add_field(name="Title" + " :crown:", value=' '.join(str(x) for x in titles))
                # embed1.add_field(name="Arm" + " :mechanical_arm: ", value=f"{arm}")
                # embed1.add_field(name="Pet" + " :dog:  ", value=f"{pet}")
                # embed1.add_field(name="Tournament Wins" + " :fireworks:", value=tournament_wins)

                if crown_list:
                    embed4 = discord.Embed(title= f"{icon} | " + f"{name} Achievements".format(self), description=":bank: | Party Chat Gaming Database™️", colour=000000)
                    embed4.set_thumbnail(url=avatar)
                    embed4.add_field(name="Completed Tales" + " :medal:", value="\n".join(crown_list))
                    if dungeon_list:
                        embed4.add_field(name="Completed Dungeons" + " :fire: ", value="\n".join(dungeon_list))
                        if boss_list:
                            embed4.add_field(name="Boss Souls" + ":japanese_ogre:",value="\n".join(boss_list))
                        else:
                            embed4.add_field(name="Boss Souls" + " :japanese_ogre: ", value="No Boss Souls Collected, yet!")
                    else:
                        embed4.add_field(name="Completed Dungeons" + " :fire: ", value="No Dungeons Completed, yet!")
                else:
                    embed4 = discord.Embed(title= f"{icon} " + f"{name}".format(self), description=":bank: Party Chat Gaming Database™️", colour=000000)
                    embed4.set_thumbnail(url=avatar)
                    embed4.add_field(name="Completed Tales" + " :medal:", value="No completed Tales, yet!")
                    embed4.add_field(name="Completed Dungeons" + " :fire: ", value="No Dungeons Completed, yet!")
                    embed4.add_field(name="Boss Souls" + " :japanese_ogre: ", value="No Boss Souls Collected, yet!")

                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⬅️', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('➡️', "next")
                paginator.add_reaction('⏭️', "last")
                embeds = [embed6, embed1, embed5, embed4]
                await paginator.run(embeds)
            else:
                await ctx.send(m.USER_NOT_REGISTERED)
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
            await ctx.send("There's an issue with your lookup command. Check with support.")
            return

    
    @cog_ext.cog_slash(description="Lookup Guild stats", guild_ids=main.guild_ids)
    async def guild(self, ctx, guild = None):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
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
                owner_data = db.queryUser({'DISNAME': owner})
                owner_object = await self.bot.fetch_user(owner_data['DID'])
                officers = team['OFFICERS']
                captains = team['CAPTAINS']
                members = team['MEMBERS']
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
                        formatted_name = f"🔰 [{str(index)}] **{member}**"
                        formatted_list_of_members.append(formatted_name)

                members_list_joined = ", ".join(formatted_list_of_members)
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
                    association_msg= f":shield: {association}"

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


                first_page = discord.Embed(title=f"{team_display_name}", description=textwrap.dedent(f"""
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
                """), colour=0x7289da)
                # first_page.set_footer(text=f"")
                
                membership_pages = discord.Embed(title=f"Members", description=textwrap.dedent(f"""
                🔰 **Members**
                {members_list_joined}
               
                """), colour=0x7289da)

                
                guild_mission_embed = discord.Embed(title=f"Guild Missions", description=textwrap.dedent(f"""
                **Guild Mission**
                {guild_mission_message}

                **Completed Guild Missions**
                {str(completed_missions)}
               
                """), colour=0x7289da)


                war_embed = discord.Embed(title=f"Guild War", description=textwrap.dedent(f"""
                **War**
                {war_message}

                **Wars Won**
                {str(war_wins)}

               
                """), colour=0x7289da)
                
                activity_page = discord.Embed(title="Recent Guild Activity", description=textwrap.dedent(f"""
                {transactions_embed}
                """), colour=0x7289da)
                
                activity_page = discord.Embed(title="Recent Guild Activity", description=textwrap.dedent(f"""
                {transactions_embed}
                """), colour=0x7289da)
                
                guild_explanations = discord.Embed(title=f"Information", description=textwrap.dedent(f"""
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
                """), colour=0x7289da)

                embed_list = [first_page, membership_pages, guild_mission_embed, war_embed, activity_page, guild_explanations]

                buttons = [] 



                

                if not is_member:
                    buttons.append(
                        manage_components.create_button(style=3, label="Apply", custom_id="guild_apply")
                    )
                
                if is_owner:
                    buttons = [
                        manage_components.create_button(style=3, label="Buff Toggle", custom_id="guild_buff_toggle"),
                        manage_components.create_button(style=3, label="Buff Swap", custom_id="guild_buff_swap"),
                        manage_components.create_button(style=3, label="Buff Shop", custom_id="guild_buff_shop"),
                    ]

                elif is_officer:
                    buttons = [
                        manage_components.create_button(style=3, label="Buff Toggle", custom_id="guild_buff_toggle"),
                        manage_components.create_button(style=3, label="Buff Swap", custom_id="guild_buff_swap"),
                        manage_components.create_button(style=3, label="Buff Shop", custom_id="guild_buff_shop"),
                    ]

                elif is_captain:
                    buttons = [
                        manage_components.create_button(style=3, label="Buff Toggle", custom_id="guild_buff_toggle"),
                    ]

                elif is_member and not is_owner and not is_captain and not is_officer:
                    buttons = [
                        manage_components.create_button(style=2, label="Close", custom_id="Q")
                    ]


                custom_action_row = manage_components.create_actionrow(*buttons)


                async def custom_function(self, button_ctx):
                    if button_ctx.author == ctx.author:
                        if button_ctx.custom_id == "guild_apply":
                            await button_ctx.defer(ignore=True)
                            await apply(self, ctx, owner_object)
                            self.stop = True
                            return
                        elif button_ctx.custom_id == "Q":
                            self.stop = True
                            return
                        elif button_ctx.custom_id == "guild_buff_toggle":
                            if guild_buff_available:
                                response = guild_buff_toggle(user, team)
                                if response:
                                    await button_ctx.send(f"{response['MSG']}")
                                else:
                                    await button_ctx.send("Error in toggling buff. Please seek support https://discord.gg/yWAD5HkDXU")
                                self.stop = True
                            else:
                                await button_ctx.send(f"No Active Guild Buff.")
                        
                        elif button_ctx.custom_id == "guild_buff_swap":
                            if guild_buff_available:
                                await button_ctx.defer(ignore=True)
                                await main.buffswap(ctx, user, team)
                                self.stop = True
                            else:
                                await button_ctx.send(f"No Active Guild Buff.")

                        elif button_ctx.custom_id == "guild_buff_shop":
                            await button_ctx.defer(ignore=True)
                            await main.buffshop(ctx, user, team)
                            self.stop = True
                        self.stop = True
                    else:
                        await button_ctx.send("World Hello")
                        self.stop = True


                await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()
                
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
    
    
    @cog_ext.cog_slash(description="Lookup Association", guild_ids=main.guild_ids)
    async def association(self, ctx, association = None):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

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
                else:
                    await ctx.send("Your Guild is not Associated.")
                    return
                
            if guild:
                hall = db.queryHall({'HALL' : guild['HALL']})
                hall_name = hall['HALL']
                hall_multipler = hall['MULT']
                hall_split = hall['SPLIT']
                hall_fee = hall['FEE']
                hall_def = hall['DEFENSE']
                hall_img = hall['PATH']
                guild_name = guild['GNAME']
                founder_name = guild['FOUNDER']
                sworn_name = guild['SWORN']
                shield_name = guild['SHIELD']
                shield_info = db.queryUser({'DISNAME' : str(shield_name)})
                shield_card = shield_info['CARD']
                shield_arm = shield_info['ARM']
                shield_title = shield_info['TITLE']
                shield_rebirth = shield_info['REBIRTH']
                streak = guild['STREAK']
                # games = guild['GAMES']
                # avatar = game['IMAGE_URL']
                crest = guild['CREST']
                balance = guild['BANK']
                bounty = guild['BOUNTY']
                bonus = int((streak/100) * bounty)
                picon = ":shield:"
                sicon = ":beginner:"
                icon = ":coin:"
                if balance >= 2000000000:
                    icon = ":money_with_wings:"
                elif balance >=1000000000:
                    icon = ":moneybag:"
                elif balance >= 500000000:
                    icon = ":dollar:"
                    
                if streak >= 100:
                    sicon = ":skull_crossbones:"     
                elif streak >= 50:
                    sicon = ":skull:"
                elif streak >=25:
                    sicon = ":ghost:"
                elif streak >= 10:
                    sicon = ":diamond_shape_with_a_dot_inside:"
                    
                # if shield_rebirth > 0:
                #     picon = "::heart_on_fire::"
                

                sword_list = []
                sword_count = 0
                blade_count = 0
                total_blade_count = 0
                for swords in guild['SWORDS']:
                    blade_count = 0
                    sword_count = sword_count + 1
                    sword_team = db.queryTeam({'TEAM_NAME': swords})
                    dubs = sword_team['WINS']
                    els = sword_team['LOSSES']
                    for blades in sword_team['MEMBERS']:
                        blade_count = blade_count + 1
                        total_blade_count = total_blade_count + 1
                    sword_bank = sword_team['BANK']
                    sword_list.append(f"~ {swords} ~ W**{dubs}** / L**{els}**\n:man_detective: | **Owner: **{sword_team['OWNER']}\n:coin: | **Bank: **{'{:,}'.format(sword_bank)}\n:knife: | **Members: **{blade_count}\n_______________________")
                crest_list = []
                for c in crest:
                    crest_list.append(f"{crown_utilities.crest_dict[c]} | {c}")



                # embed1 = discord.Embed(title=f":flags: {guild_name} Guild Card - {icon}{'{:,}'.format(balance)}".format(self), description=":bank: Party Chat Gaming Database", colour=000000)
                # if guild['LOGO_FLAG']:
                #     embed1.set_image(url=logo)
                # embed1.add_field(name="Founder :dolls:", value= founder_name.split("#",1)[0], inline=True)
                # embed1.add_field(name="Sworn :dolls:", value= sworn_name.split("#",1)[0], inline=True)
                embed1 = discord.Embed(title= f":flags: |{guild_name} Association Card - {icon} {'{:,}'.format(balance)}".format(self), description=textwrap.dedent(f"""\
                
                :nesting_dolls: | **Founder ~** {founder_name.split("#",1)[0]}
                :dolls: | **Sworn ~** {sworn_name.split("#",1)[0]}
                
                {sicon} | **Victories: **{streak}
                :japanese_goblin: | **Shield: ~**{shield_name.split("#",1)[0].format(self)}
                :flower_playing_cards: | **Card: **{shield_card}
                :reminder_ribbon: | **Title: **{shield_title}
                :mechanical_arm: | **Arm: **{shield_arm}
                
                :ninja: | **Guilds: **{sword_count}
                :dollar: | **Guild Split: **{hall_split} 
                :secret: | **Universe Crest: **{len(crest_list)} 
                    
                :shinto_shrine: | **Hall: **{hall_name} 
                :shield: | **Raid Defenses: **{hall_def} 
                :coin: | **Raid Fee: **{'{:,}'.format(hall_fee)}
                :yen: | **Bounty: **{'{:,}'.format(bounty)}
                :moneybag: | **Victory Bonus: **{'{:,}'.format(bonus)}
                """), colour=000000)
                embed1.set_image(url=hall_img)
                embed1.set_footer(text=f"/raid {guild_name} - Raid Association")
                
                embed2 = discord.Embed(title=f":flags: |  {guild_name} **Guild** List".format(self), description=":bank: |  Party Chat Gaming Database", colour=000000)
                embed2.add_field(name=f"**Guilds: | ** :ninja: ~ {sword_count}/:knife: {total_blade_count}", value="\n".join(f'**{t}**'.format(self) for t in sword_list), inline=False)
                embed2.set_footer(text=f"/guild - View Association Guild")
                
                embed3 = discord.Embed(title=f":flags: |  {guild_name} **OWNED CREST**".format(self), description=":bank: |  Party Chat Gaming Database", colour=000000)
                embed3.add_field(name=f":secret: | **CREST**", value="\n".join(f'**{c}**'.format(self) for c in crest_list), inline=False)
                embed3.set_footer(text=f"Earn Universe Crest in Dungeons!")
                # if guild['LOGO_FLAG']:
                #     embed3.set_image(url=logo)
                
                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⬅️', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('➡️', "next")
                paginator.add_reaction('⏭️', "last")
                embeds = [embed1,embed2, embed3]
                await paginator.run(embeds)
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


    @cog_ext.cog_slash(description="Lookup player family", guild_ids=main.guild_ids)
    async def family(self, ctx, player = None):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return
        ctx_user = db.queryUser({'DID': str(ctx.author.id)})
        #print(ctx_user)

        try:
            if player != None:
                member = player
            if player:
                player = player.replace("<","")
                player = player.replace(">","")
                player = player.replace("@","")
                player = player.replace("!","")
                user_profile = db.queryUser({'DID': str(player)})
                family = db.queryFamily({'HEAD': user_profile['FAMILY']})
                if family:
                    family_name = family['HEAD']
                else:
                    await ctx.send("Family does not exist.")
                    return
                
            else:
                user_profile = db.queryUser({'DID': str(ctx.author.id)})
                family = db.queryFamily({'HEAD': user_profile['FAMILY']})
                if family:
                    family_name = family['HEAD']
                else:
                    await ctx.send("You are not a part of a Family.")
                    return
                
            if family:
                is_head = False
                is_partner = False
                is_kid = False
                member = False
                
                family_name = family['HEAD'] + "'s Family"
                head_name = family['HEAD']
                partner_name = family['PARTNER']
                savings = int(family['BANK'])
                head_data = db.queryUser({'DISNAME': head_name})
                head_object = await self.bot.fetch_user(head_data['DID'])
                estates = family['ESTATES']
                if partner_name:
                    partner_data = db.queryUser({'DISNAME': partner_name})
                    partner_object = await self.bot.fetch_user(partner_data['DID'])
                    partner_name_adjusted = partner_name.split("#",1)[0]
                else:
                    partner_name_adjusted = '*None*'
                house = family['HOUSE']
                house_info = db.queryHouse({'HOUSE' : house})
                house_img = house_info['PATH']
                kid_list = []
                for kids in family['KIDS']:
                    kid_list.append(kids.split("#",1)[0])
                icon = ":coin:"
                if savings >= 500000000:
                    icon = ":money_with_wings:"
                elif savings >=100000000:
                    icon = ":moneybag:"
                elif savings >= 50000000:
                    icon = ":dollar:"

                if str(ctx.author.id) == head_data['DID']:
                    is_head = True
                    member = True
                if partner_name:
                    if str(ctx.author.id) == partner_data['DID']:
                        is_partner = True
                        member = True
                if kid_list:
                    if ctx_user['NAME'] in kid_list:
                        is_kid = True
                        member = True
                #print(member)
                transactions = family['TRANSACTIONS']
                transactions_embed = ""
                if transactions:
                    transactions_len = len(transactions)
                    if transactions_len >= 10:
                        transactions = transactions[-10:]
                        transactions_embed = "\n".join(transactions)
                    else:
                        transactions_embed = "\n".join(transactions)
                
                        
                summon_object = family['SUMMON']
                summon = list(summon_object.values())[0]
                head_vault = db.queryVault({'DID' : head_data['DID']})
                if head_vault:
                    vault_summons = head_vault['PETS']
                    for l in vault_summons:
                        if summon == l['NAME']:
                            level = l['LVL']
                            xp = l['EXP']
                            pet_ability = list(l.keys())[3]
                            pet_ability_power = list(l.values())[3]
                            power = (l['BOND'] * l['LVL']) + pet_ability_power
                            pet_info = {'NAME': l['NAME'], 'LVL': l['LVL'], 'EXP': l['EXP'], pet_ability: pet_ability_power, 'TYPE': l['TYPE'], 'BOND': l['BOND'], 'BONDEXP': l['BONDEXP'], 'PATH': l['PATH']}
                            summon_img = pet_info['PATH']
                            pet_name = pet_info["NAME"]
                            summon_bond = l["BOND"]
                            summon_lvl = level
                            print(pet_name)
                            summon_type = pet_info["TYPE"]
                            power = (summon_bond * summon_lvl) + int(pet_ability_power)
                            path = pet_info["PATH"]
                            summon_file = crown_utilities.showsummon(summon_img, pet_info['NAME'], enhancer_mapping[pet_info['TYPE']], pet_info['LVL'], pet_info['BOND'])
                    print(pet_name)
                else:
                    partnervault =  db.queryVault({'DID' : partner_data['DID']})
                    if partnervault:
                        vault_summons = partnervault['PETS']
                        for l in vault_summons:
                            if summon == l['NAME']:
                                level = l['LVL']
                                xp = l['EXP']
                                pet_ability = list(l.keys())[3]
                                pet_ability_power = list(l.values())[3]
                                power = (l['BOND'] * l['LVL']) + pet_ability_power
                                pet_info = {'NAME': l['NAME'], 'LVL': l['LVL'], 'EXP': l['EXP'], pet_ability: pet_ability_power, 'TYPE': l['TYPE'], 'BOND': l['BOND'], 'BONDEXP': l['BONDEXP'], 'PATH': l['PATH']}
                                summon_img = pet_info['PATH']
                                summon_type = pet_info["TYPE"]
                                summon_file = crown_utilities.showsummon(summon_img, pet_info['NAME'], enhancer_mapping[pet_info['TYPE']], pet_info['LVL'], pet_info['BOND'])
                                pet_name = pet_info["NAME"]
                                summon_bond = pet_info["BOND"]
                                summon_lvl = level
                                power = (summon_bond * summon_lvl) + int(pet_ability_power)
                                path = pet_info["PATH"]
                                print(pet_name)
                        print(pet_name)
                                
                    else:
                        pet_info = db.queryPet({'PET': summon})
                        summon_img = pet_info['PATH']
                        pet_ability_power = list(pet_info['ABILITIES'][0].values())[0]
                        pet_ability = list(pet_info['ABILITIES'])[0]
                        summon_type = pet_ability['TYPE']
                        summon_bond = 0
                        pet_name = pet_info["PET"]
                        summon_lvl = 0
                        summon_img = pet_info['PATH']
                        power = (summon_bond * summon_lvl) + int(pet_ability_power)
                        path = pet_info["PATH"]
                        summon_file = crown_utilities.showsummon(summon_img, pet_info['PET'], enhancer_mapping[summon_type], 0, 0)
                        print(pet_name)
                universe = family['UNIVERSE']
                universe_data = db.queryUniverse({'TITLE': universe})
                universe_img = universe_data['PATH']
                estates_list = []
                estate_data_list = []
                for houses in estates:
                    house_data = db.queryHouse({'HOUSE': houses})
                    estates_list.append(houses)
                    estate_data_list.append(house_data)
                    
                estates_list_joined = ", ".join(estates_list)
                
                
                kids_names = "\n".join(f'{k}'.format(self) for k in kid_list)
                # if summon_data:
                #     await ctx.send({summon_data})
                    
                first_page = discord.Embed(title=f":family_mwgb: | {family_name}", description=textwrap.dedent(f"""
                :brain: **Head of Household** 
                {head_name.split("#",1)[0]}

                :anatomical_heart: **Partner**
                {partner_name_adjusted}

                :baby: **Kids**
                {kids_names}

                🏦**Savings** 
                {icon} {'{:,}'.format(savings)}
                
                🏠**Primary Residence**
                {house_info['HOUSE']} - 〽️**{house_info['MULT']}x** :coin: per match!
                """), colour=0x7289da)
                first_page.set_image(url=house_img)
                
                estates_page = discord.Embed(title=f"Real Estate", description=textwrap.dedent(f"""
                🌇 **Properties**
                {estates_list_joined}
               
                """), colour=0x7289da)

                
                activity_page = discord.Embed(title="Recent Family Activity", description=textwrap.dedent(f"""
                {transactions_embed}
                """), colour=0x7289da)
                
                summon_page = discord.Embed(title="Family Summon", description=textwrap.dedent(f"""
                🧬**{pet_name}**
                *Bond* **{summon_bond}**
                *Level* **{summon_lvl}**
                :small_blue_diamond: **{summon_type}** ~ **{power}**{enhancer_suffix_mapping[summon_type]}
                🦠 : **{enhancer_mapping[summon_type]}**
                """), colour=0x7289da)
                summon_page.set_image(url=path)
                
                
                
                
                
                family_explanations = discord.Embed(title=f"Information", description=textwrap.dedent(f"""
                **Family Explanations**
                - **Earnings**: Families earn coin for every completed battle by its members
                - **Allowance**: Disperse Family Savings to a family member
                - **Invest**: Invest money into Family Bank
                - **Houses**: Give Coin Multipliers in all game modes towards Family Earnings
                - **Home Universe**: Earn Extra gold in Home Universe,
                - **Real Estate**: Own multiple houses, swap your current house buy and sell real estate.add
                - **Family Summon**: Each family member has access and can equip the family summon
                

                **Family Position Explanations**
                - **Head of Household**:  All operations.
                - **Partner**:  Can equip/update family summon, change equipped house and give allowances
                - **Kids**:  Can equip family summon.
                """), colour=0x7289da)

                embed_list = [first_page, estates_page, summon_page, activity_page, family_explanations]

                buttons = []
                
                if not member:
                    print(member)
                    buttons.append(
                        manage_components.create_button(style=3, label="Say Hello", custom_id="hello")
                    )
                    
                if is_head:
                    buttons = [
                        manage_components.create_button(style=3, label="Check/Purchase Properties", custom_id="property"),
                        manage_components.create_button(style=3, label="Equip/Set Family Summon", custom_id="summon"),
                    ]
                elif is_partner:
                    buttons = [
                        manage_components.create_button(style=3, label="Check Properties", custom_id="property"),
                        manage_components.create_button(style=3, label="Equip/Set Family Summon", custom_id="summon"),
                    ]
                    
                elif is_kid:
                    buttons = [
                        manage_components.create_button(style=3, label="View Properties", custom_id="property"),
                        manage_components.create_button(style=3, label="Equip Family Summon", custom_id="summon"),
                    ]
                    
                custom_action_row = manage_components.create_actionrow(*buttons)
                
                async def custom_function(self, button_ctx):
                    try:
                        if button_ctx.author == ctx.author:
                            if button_ctx.custom_id == "hello":
                                await button_ctx.defer(ignore=True)
                                update_query = {
                                        '$push': {'TRANSACTIONS': f"{button_ctx.author} said 'Hello'!"}
                                    }
                                response = db.updateFamily({'HEAD': family['HEAD']}, update_query)
                                await ctx.send(f"**{button_ctx.author.mention}** Said Hello! to {family_name}'s Family!")
                                self.stop = True
                                return
                            elif button_ctx.custom_id == "property":
                                await button_ctx.defer(ignore=True)
                                real_estate_message = " "
                                property_buttons = []
                                balance_message = '{:,}'.format(savings)
                                if is_head:
                                    real_estate_message = "Welcome Head of Household!\n**View Property** - View Owned Properties or make a Move!\n**Buy New Home** - Buy a new Home for your Family\n**Browse Housing Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    manage_components.create_button(style=2, label="Owned Properties", custom_id="equip"),
                                    manage_components.create_button(style=3, label="Buy/Sell Houses", custom_id="buy"),
                                    manage_components.create_button(style=1, label="Browse Housing Catalog", custom_id="browse"),
                                    manage_components.create_button(style=ButtonStyle.red, label="Quit", custom_id="q")
                                    
                                ]
                                if is_partner:
                                    real_estate_message = "Welcome Partner!\n**View Property** - View Owned Properties or make a Move!\n**Browse Housing Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    manage_components.create_button(style=1, label="Owned Properties", custom_id="equip"),
                                    manage_components.create_button(style=1, label="Browse Housing Catalog", custom_id="browse"),
                                    manage_components.create_button(style=ButtonStyle.red, label="Quit", custom_id="q")
                                ]
                                if is_kid:
                                    real_estate_message = "Welcome Kids!\n**View Property** - View Owned Properties"
                                    property_buttons = [
                                    manage_components.create_button(style=1, label="View Properties", custom_id="view"),
                                    manage_components.create_button(style=ButtonStyle.red, label="Quit", custom_id="q")
                                ]
                                property_action_row = manage_components.create_actionrow(*property_buttons)
                                real_estate_screen = discord.Embed(title=f"Anime VS+ Real Estate", description=textwrap.dedent(f"""\
                                {real_estate_message}
                                \n*Current Savings*: 
                                :coin: **{balance_message}**
                                """), color=0xe74c3c)
                                real_estate_screen.set_image(url="https://thumbs.gfycat.com/FormalBlankGeese-max-1mb.gif")
                                
                                msg = await ctx.send(embed=real_estate_screen, components=[property_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                try:
                                    house_embed_list = []
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[property_action_row], timeout=120, check=check)
                                    if button_ctx.custom_id == "q":
                                        await ctx.send("Real Estate Menu Closed...")
                                        return
                                    if button_ctx.custom_id == "browse":
                                        await button_ctx.defer(ignore=True)
                                        all_houses = db.queryAllHouses()
                                        for houses in all_houses:
                                            house_name = houses['HOUSE']
                                            house_price = houses['PRICE']
                                            price_message = '{:,}'.format(houses['PRICE'])
                                            house_img = houses['PATH']
                                            house_multiplier = houses['MULT']                                            
                                            embedVar = discord.Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            💰 **Price**: {price_message}
                                            〽️ **Multiplier**: {house_multiplier}
                                            Family earns **{house_multiplier}x** :coin: per match!
                                            """))
                                            embedVar.set_image(url=house_img)
                                            house_embed_list.append(embedVar)
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=house_embed_list).run()
                                    if button_ctx.custom_id == "view":
                                        await button_ctx.defer(ignore=True)
                                        for houses in estate_data_list:
                                            house_name = houses['HOUSE']
                                            house_price = houses['PRICE']
                                            price_message = '{:,}'.format(houses['PRICE'])
                                            house_img = houses['PATH']
                                            house_multiplier = houses['MULT']                                            
                                            embedVar = discord.Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            💰 **Price**: {price_message}
                                            〽️ **Multiplier**: {house_multiplier} 
                                            Family earns **{house_multiplier}x** :coin: per match!
                                            """))
                                            embedVar.set_image(url=house_img)
                                            house_embed_list.append(embedVar)
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=house_embed_list).run()
                                    elif button_ctx.custom_id == "equip":
                                        await button_ctx.defer(ignore=True)
                                        for houses in estate_data_list:
                                            house_name = houses['HOUSE']
                                            house_price = houses['PRICE']
                                            price_message = '{:,}'.format(houses['PRICE'])
                                            house_img = houses['PATH']
                                            house_multiplier = houses['MULT']                                            
                                            embedVar = discord.Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            💰 **Price**: {price_message}
                                            〽️ **Multiplier**: {house_multiplier} 
                                            Family earns **{house_multiplier}x** :coin: per match!
                                            """))
                                            embedVar.set_image(url=house_img)
                                            house_embed_list.append(embedVar)
                                            
                                        equip_buttons = [
                                            manage_components.create_button(style=3, label="🏠 Equip House", custom_id="equip"),

                                        ]
                                        equip_action_row = manage_components.create_actionrow(*equip_buttons)
                                        async def equip_function(self, button_ctx):
                                            house_name = str(button_ctx.origin_message.embeds[0].title)
                                            await button_ctx.defer(ignore=True)
                                            if button_ctx.author == ctx.author:
                                                if button_ctx.custom_id == "equip":
                                                    transaction_message = f"{ctx.author} changed the family house to **{str(button_ctx.origin_message.embeds[0].title)}**."
                                                    update_query = {
                                                            '$set': {'HOUSE': house_name},
                                                            '$push': {'TRANSACTIONS': transaction_message}
                                                        }
                                                    response = db.updateFamily({'HEAD': family['HEAD']}, update_query)
                                                    await ctx.send(f"**{family_name}** moved into their **{house_name}**! Enjoy your new Home!")
                                                    self.stop = True
                                            else:
                                                await ctx.send("This is not your command.")
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=house_embed_list, customActionRow=[
                                            equip_action_row,
                                            equip_function,
                                        ]).run()
                                                                                    
                                    elif button_ctx.custom_id == "buy":
                                        house_embed_list = []
                                        all_houses = db.queryAllHouses()
                                        owned = False
                                        current_savings = '{:,}'.format(savings)
                                        for houses in all_houses:
                                            house_name = houses['HOUSE']
                                            house_price = houses['PRICE']
                                            price_message = '{:,}'.format(houses['PRICE'])
                                            house_img = houses['PATH']
                                            house_multiplier = houses['MULT']       
                                            ownership_message = f"💰 **Price**: {price_message}"  
                                            sell_price = house_price *.80
                                            sell_message = " "
                                            sell_message = f"💱 Sells for **{'{:,}'.format(houses['PRICE'])}**"                                  
                                            embedVar = discord.Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            **Current Savings**: :coin: **{current_savings}**                                                                    
                                            {ownership_message}
                                            〽️ **Multiplier**: {house_multiplier}
                                            {sell_message}
                                            Family earns **{house_multiplier}x** :coin: per match!
                                            """))
                                            embedVar.set_image(url=house_img)
                                            house_embed_list.append(embedVar)
                                        
                                        econ_buttons = [
                                            manage_components.create_button(style=3, label="💰 Buy House", custom_id="buy"),
                                            manage_components.create_button(style=3, label="💱 Sell House", custom_id="sell"),

                                        ]
                                        econ_action_row = manage_components.create_actionrow(*econ_buttons)
                                        
                                        async def econ_function(self, button_ctx):
                                            house_name = str(button_ctx.origin_message.embeds[0].title)
                                            await button_ctx.defer(ignore=True)
                                            if button_ctx.author == ctx.author:
                                                if button_ctx.custom_id == "buy":
                                                    if house_name in estates_list:
                                                        await ctx.send("You already own this House. Click 'Sell' to sell it!")
                                                        self.stop = True
                                                        return
                                                    if house_name == 'Cave':
                                                        await button_ctx.send("You already own your **Ancestral Cave.**")
                                                        #self.stop = True
                                                        return
                                                    try: 
                                                        house = db.queryHouse({'HOUSE': {"$regex": f"^{str(house_name)}$", "$options": "i"}})
                                                        currentBalance = family['BANK']
                                                        cost = house['PRICE']
                                                        house_name = house['HOUSE']
                                                        if house:
                                                            if house_name == family['HOUSE']:
                                                                await ctx.send(m.USERS_ALREADY_HAS_HOUSE, delete_after=5)
                                                            else:
                                                                newBalance = currentBalance - cost
                                                                if newBalance < 0 :
                                                                    await ctx.send("You have an insufficent Balance")
                                                                else:
                                                                    await crown_utilities.cursefamily(cost, family['HEAD'])
                                                                    transaction_message = f"{ctx.author} bought a new **{str(button_ctx.origin_message.embeds[0].title)}**."
                                                                    response = db.updateFamily({'HEAD': family['HEAD']},{'$set':{'HOUSE': str(house_name)},'$push': {'TRANSACTIONS': transaction_message}})
                                                                    response2 = db.updateFamily({'HEAD': family['HEAD']},{'$addToSet':{'ESTATES': str(house_name)}})
                                                                    await ctx.send(m.PURCHASE_COMPLETE_H + "Enjoy your new Home!")
                                                                    return
                                                        else:
                                                            await ctx.send(m.HOUSE_DOESNT_EXIST)
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
                                                    house = db.queryHouse({'HOUSE': {"$regex": f"^{str(house_name)}$", "$options": "i"}})
                                                    cost = house['PRICE']
                                                    formatted_cost = '{:,}'.format(cost)
                                                    if house_name not in family['ESTATES']:
                                                        await ctx.send("You need to Own this House to to sell it!")
                                                        #self.stop = True
                                                        return
                                                    if house_name == family['HOUSE']:
                                                        await button_ctx.send("You cannot sell your **Primary Residence**.")
                                                        #self.stop = True
                                                        return
                                                    if house_name == 'Cave':
                                                        await button_ctx.send("You cannot sell your **Ancestral Cave.**")
                                                        #self.stop = True
                                                        return
                                                    elif house_name in family['ESTATES']:
                                                        await crown_utilities.blessfamily(cost, family['HEAD'])
                                                        transaction_message = f"{ctx.author} sold the family home: **{str(house_name)}**."
                                                        response = db.updateFamily({'HEAD': family['HEAD']},{'$pull':{'ESTATES': str(house_name)},'$push': {'TRANSACTIONS': transaction_message}})
                                                        await ctx.send(f'{family_name} sold their **{house_name}** for **{formatted_cost}**')
                                                        #self.stop = True
                                                        return
                                            else:
                                                await ctx.send("This is not your command.")
                                        await Paginator(bot=self.bot, ctx=ctx, useQuitButton=True, deleteAfterTimeout=True, pages=house_embed_list, customActionRow=[
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
                            elif button_ctx.custom_id == "summon":
                                await button_ctx.defer(ignore=True)
                                summon_object = family['SUMMON']
                                summon = summon_object['NAME']
                                head_vault = db.queryVault({'OWNER' : head_data['DISNAME']})
                                if head_vault:
                                    vault_summons = head_vault['PETS']
                                    for l in vault_summons:
                                        if summon == l['NAME']:
                                            level = l['LVL']
                                            xp = l['EXP']
                                            pet_ability = list(l.keys())[3]
                                            pet_ability_power = list(l.values())[3]
                                            power = (l['BOND'] * l['LVL']) + pet_ability_power
                                            pet_info = {'NAME': l['NAME'], 'LVL': l['LVL'], 'EXP': l['EXP'], pet_ability: pet_ability_power, 'TYPE': l['TYPE'], 'BOND': l['BOND'], 'BONDEXP': l['BONDEXP'], 'PATH': l['PATH']}
                                    summon_img = pet_info['PATH']
                                    summon_file = crown_utilities.showsummon(summon_img, pet_info['NAME'], enhancer_mapping[pet_info['TYPE']], pet_info['LVL'], pet_info['BOND'])
                                else:
                                    partnervault =  db.queryVault({'OWNER' : partner_data['DISNAME']})
                                    if partnervault:
                                        vault_summons = partnervault['PETS']
                                        for l in vault_summons:
                                            if summon == l['NAME']:
                
                                                level = l['LVL']
                                                xp = l['EXP']
                                                pet_ability = list(l.keys())[3]
                                                pet_ability_power = list(l.values())[3]
                                                power = (l['BOND'] * l['LVL']) + pet_ability_power
                                                pet_info = {'NAME': l['NAME'], 'LVL': l['LVL'], 'EXP': l['EXP'], pet_ability: pet_ability_power, 'TYPE': l['TYPE'], 'BOND': l['BOND'], 'BONDEXP': l['BONDEXP'], 'PATH': l['PATH']}
                                                summon_img = pet_info['PATH']
                                                summon_file = crown_utilities.showsummon(summon_img, pet_info['NAME'], enhancer_mapping[pet_info['TYPE']], pet_info['LVL'], pet_info['BOND'])
                                    else:
                                        summon_data = db.queryPet({'PET': summon})
                                        summon_img = summon_data['PATH']
                                        pet_ability_power = list(summon_data['ABILITIES'][0].values())[1]
                                        pet_ability = list(summon_data['ABILITIES'])[0]
                                        power =  pet_ability_power
                                        summon_enh = pet_ability['TYPE']
                                        summon_bond = 0
                                        summon_lvl = 0
                                        summon_img = pet_info['PATH']
                                        summon_file = crown_utilities.showsummon(summon_img, summon_data['PET'], enhancer_mapping[summon_enh], 0, 0)
                                summon_buttons = []
                                if is_head:
                                    summon_message = "Welcome Head of Household! Equip or Change Family Summon Here!"
                                    summon_buttons = [
                                    manage_components.create_button(style=2, label="Change Summon", custom_id="change"),
                                    manage_components.create_button(style=3, label="Equip Family Summon", custom_id="equip"),
                                    
                                ]
                                if is_partner:
                                    summon_message = "Welcome Partner! Equip or Change Family Summon Here!"
                                    summon_buttons = [
                                    manage_components.create_button(style=1, label="Change Summon", custom_id="change"),
                                    manage_components.create_button(style=1, label="Equip Family Summon", custom_id="equip"),
                                ]
                                if is_kid:
                                    summon_message = "Welcome Kids! Equip Family Summon Here!"
                                    summon_buttons = [
                                    manage_components.create_button(style=1, label="Equip Family Summon", custom_id="equip"),
                                ]
                                summon_action_row = manage_components.create_actionrow(*summon_buttons)
                                summon_screen = discord.Embed(title=f"Anime VS+ Family", description=textwrap.dedent(f"""\
                                {summon_message}
                                :dna: : **{pet_info['NAME']}**
                                *Bond* **{pet_info['BOND']}**
                                *Level* **{pet_info['LVL']}**
                                :small_blue_diamond: **{pet_info['TYPE']}** ~ **{power}**{enhancer_suffix_mapping[pet_info['TYPE']]}
                                🦠 : **{enhancer_mapping[pet_info['TYPE']]}**
                                """), color=0xe74c3c)
                                summon_screen.set_image(url=pet_info['PATH'])
                                
                                msg = await ctx.send(embed=summon_screen, components=[summon_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[summon_action_row], timeout=120, check=check)
                                    
                                    if button_ctx.custom_id == "change":
                                        await button_ctx.defer(ignore=True)
                                        query = {'DID': str(button_ctx.author.id)}
                                        d = db.queryUser(query)
                                        vault = db.queryVault({'DID': d['DID']})
                                        if vault:
                                            name = d['DISNAME'].split("#",1)[0]
                                            avatar = d['AVATAR']
                                            balance = vault['BALANCE']
                                            current_summon = d['PET']
                                            pets_list = vault['PETS']
                                            
                                            total_pets = len(pets_list)

                                            pets=[]
                                            bond_message = ""
                                            lvl_message = ""
                                            embed_list = []
                                            for pet in pets_list:
                                                #cpetmove_ap= (cpet_bond * cpet_lvl) + list(cpet.values())[3] # Ability Power
                                                bond_message = ""
                                                if pet['BOND'] == 3:
                                                    bond_message = ":star2:"
                                                lvl_message = ""
                                                if pet['LVL'] == 10:
                                                    lvl_message = ":star:"
                                                
                                                pet_ability = list(pet.keys())[3]
                                                pet_ability_power = list(pet.values())[3]
                                                power = (pet['BOND'] * pet['LVL']) + pet_ability_power
                                                dash_pet_info = db.queryPet({'PET' : pet['NAME']})
                                                if dash_pet_info:
                                                    pet_available = dash_pet_info['AVAILABLE']
                                                    pet_exclusive = dash_pet_info['EXCLUSIVE']
                                                    pet_universe = dash_pet_info['UNIVERSE']
                                                icon = "🧬"
                                                if pet_available and pet_exclusive:
                                                    icon = ":fire:"
                                                elif pet_available == False and pet_exclusive ==False:
                                                    icon = ":japanese_ogre:"

                                                embedVar = discord.Embed(title= f"{pet['NAME']}", description=textwrap.dedent(f"""
                                                {icon}
                                                _Bond_ **{pet['BOND']}** {bond_message}
                                                _Level_ **{pet['LVL']} {lvl_message}**
                                                :small_blue_diamond: **{pet_ability}:** {power}{enhancer_suffix_mapping[pet['TYPE']]}
                                                🦠 **Type:** {pet['TYPE']}"""), 
                                                colour=0x7289da)
                                                embedVar.set_thumbnail(url=avatar)
                                                embedVar.set_footer(text=f"{pet['TYPE']}: {enhancer_mapping[pet['TYPE']]}")
                                                embed_list.append(embedVar)
                                            
                                            buttons = [
                                                manage_components.create_button(style=3, label="Share Summon", custom_id="share"),
                                            ]
                                            custom_action_row = manage_components.create_actionrow(*buttons)

                                            async def custom_function(self, button_ctx):
                                                if button_ctx.author == ctx.author:
                                                    updated_vault = db.queryVault({'DID': d['DID']})
                                                    sell_price = 0
                                                    selected_summon = str(button_ctx.origin_message.embeds[0].title)
                                                    user_query = {'DID': str(ctx.author.id)}
                                                    user_vault = db.queryVault(user_query)

                                                    vault_summons = user_vault['PETS']
                                                    for l in vault_summons:
                                                        if selected_summon == l['NAME']:
                                                            level = l['LVL']
                                                            xp = l['EXP']
                                                            pet_ability = list(l.keys())[3]
                                                            pet_ability_power = list(l.values())[3]
                                                            power = (l['BOND'] * l['LVL']) + pet_ability_power
                                                            pet_info = {'NAME': l['NAME'], 'LVL': l['LVL'], 'EXP': l['EXP'], pet_ability: pet_ability_power, 'TYPE': l['TYPE'], 'BOND': l['BOND'], 'BONDEXP': l['BONDEXP'], 'PATH': l['PATH']}
                                                    if button_ctx.custom_id == "share":
                                                        #update_query = {'$set': {'SUMMON': }}
                                                        #filter_query = [{'type.' + "NAME": str(pet)}]
                                                        #response = db.updateVault(query, update_query, filter_query)
                                                        transaction_message = f"{ctx.author} changed the family summon to **{str(button_ctx.origin_message.embeds[0].title)}**."
                                                        response = db.updateFamily({'HEAD': family['HEAD']}, {'$set': {'SUMMON': pet_info}, '$push': {'TRANSACTIONS': transaction_message}})
                                                        await button_ctx.send(f"🧬 **{str(button_ctx.origin_message.embeds[0].title)}** is now the {family_name} **Summon**.")
                                                        self.stop = True
                                                        return
                                                else:
                                                    await ctx.send("This is not your Summons list.")
                                            await Paginator(bot=self.bot, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                                                custom_action_row,
                                                custom_function,
                                            ]).run()

                                    elif button_ctx.custom_id == "equip":
                                        try:
                                            await button_ctx.defer(ignore=True)
                                            transaction_message = f"{ctx.author} equipped the family summon : **{str(pet_info['NAME'])}**."
                                            response = db.updateUserNoFilter({'DID': str(button_ctx.author.id)}, {'$set' : {'PET': pet_info['NAME'], 'FAMILY_PET': True}})
                                            response2 = db.updateFamily({'HEAD': family['HEAD']}, {'$push': {'TRANSACTIONS': transaction_message}})
                                            await button_ctx.send(f"🧬 **{str(pet_info['NAME'])}** is now your **Summon**.")
                                            self.stop = True
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
                
                await Paginator(bot=self.bot, useQuitButton=True, disableAfterTimeout=True, ctx=ctx, pages=embed_list, timeout=60, customActionRow=[
                    custom_action_row,
                    custom_function,
                ]).run()  
            else:
                await ctx.send(m.FAMILY_DOESNT_EXIST)
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

def setup(bot):
    bot.add_cog(Lookup(bot))

def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

def guild_buff_toggle(player, team):
    guild_buff_on = team['GUILD_BUFF_ON']
    team_query = {'TEAM_NAME': team['TEAM_NAME']}
    return_message = {}
    
    if guild_buff_on:
        transaction_message = f"{player['DISNAME']} turned off Guild Buff."
        new_value_query = {
            '$set': {'GUILD_BUFF_ON': False},
            '$push': {'TRANSACTIONS': transaction_message}
            }
        response = db.updateTeam(team_query, new_value_query)
        if response:
            return {"MSG": "Guild Buff has been turned off."}
        else:
            return False
    else:
        transaction_message = f"{player['DISNAME']} turned on Guild Buff."
        new_value_query = {
            '$set': {'GUILD_BUFF_ON': True},
            '$push': {'TRANSACTIONS': transaction_message}
            }
        response = db.updateTeam(team_query, new_value_query)
        if response:
            return {"MSG": "Guild Buff has been turned on."}
        else:
            return False


async def apply(self, ctx, owner: User):
    owner_profile = db.queryUser({'DID': str(owner.id)})
    team_profile = db.queryTeam({'TEAM_NAME': owner_profile['TEAM'].lower()})

    if owner_profile['TEAM'] == 'PCG':
        await ctx.send(m.USER_NOT_ON_TEAM, delete_after=5)
    else:

        if owner_profile['DISNAME'] == team_profile['OWNER']:
            member_profile = db.queryUser({'DID': str(ctx.author.id)})
            if member_profile['LEVEL'] < 4:
                await ctx.send(f"🔓 Unlock Guilds by completing Floor 3 of the 🌑 Abyss! Use /solo to enter the abyss.")
                return

            # If user is part of a team you cannot add them to your team
            if member_profile['TEAM'] != 'PCG':
                await ctx.send("You're already in a Guild. You may not join another guild.")
                return
            else:
                team_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="Accept",
                        custom_id="Yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="Deny",
                        custom_id="No"
                    )
                ]
                team_buttons_action_row = manage_components.create_actionrow(*team_buttons)
                
                msg = await ctx.send(f"{ctx.author.mention}  applies to join **{team_profile['TEAM_DISPLAY_NAME']}**. Owner, Officers, or Captains - Please accept or deny".format(self), components=[team_buttons_action_row])

                def check(button_ctx):
                    return str(button_ctx.author) == str(owner)

                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[team_buttons_action_row], timeout=120, check=check)
                    
                    if button_ctx.custom_id == "No":
                        await button_ctx.send("Application Denied.")
                        await msg.delete()
                        return

                    if button_ctx.custom_id == "Yes":
                        team_query = {'TEAM_NAME': team_profile['TEAM_NAME'].lower()}
                        new_value_query = {'$push': {'MEMBERS': member_profile['DISNAME']}}
                        response = db.addTeamMember(team_query, new_value_query, owner_profile['DISNAME'], member_profile['DISNAME'])
                        await button_ctx.send(response)
                except:
                    await msg.delete()
        else:
            await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)


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