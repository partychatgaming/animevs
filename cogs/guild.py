import discord
from discord.ext import commands
import bot as main
import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import help_commands as h
# Converters
from discord import User
from discord import Member
from PIL import Image, ImageFont, ImageDraw
import requests
from collections import ChainMap
import DiscordUtils
import textwrap
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from dinteractions_Paginator import Paginator

emojis = ['👍', '👎']

class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Guild Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)


    @cog_ext.cog_slash(description="Swear into Association!", guild_ids=main.guild_ids)
    async def oath(self, ctx, sworn: User, association: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            owner = sworn
            guild_name = association
            cost = 1000000
            
            founder_profile = db.queryUser({'DID': str(ctx.author.id)})
            guildsearch_name = founder_profile['GUILD']
            
            if founder_profile['LEVEL'] < 16:
                await ctx.send("🔓 Unlock Associations by completing Floor 15 of the 🌑 Abyss! Use /solo to enter the abyss.")
                return
            if guildsearch_name != "PCG":
                guildsearch_query = {'GNAME' : guildsearch_name}
                guildsearch = db.queryGuildAlt(guildsearch_query)
                if guildsearch:
                    if guild_name != guildsearch_name:
                        await ctx.send(m.FOUNDER_LEAVE)
                        return
                    await ctx.send(f"{guildsearch_name} NEW OATH!")
                    sworn_profile = db.queryUser({'DID': str(owner.id)}) 
                    if sworn_profile['LEVEL'] < 16:
                        await ctx.send("🔓 Sworn Must Unlock Associations by completing Floor 15 of the 🌑 Abyss! Use /solo to enter the abyss.")
                        return
                    if sworn_profile['LEVEL'] < 16:
                        await ctx.send(f"🔓 {sworn.mention} Has not Unlocked Associations! Complete Floor 15 of the 🌑 Abyss! Use /solo to enter the abyss.")
                        return             
                    if sworn_profile['GUILD'] != 'PCG' and guildsearch['SHIELD'] != sworn_profile['DISNAME']:
                        await ctx.send(m.USER_IN_GUILD, delete_after=3)
                        return
                    else:
                        if founder_profile['TEAM'] == 'PCG' or sworn_profile['TEAM'] == 'PCG':
                            await ctx.send(m.FOUNDER_NO_TEAM, delete_after=3)
                            return
                        else:
                            fteam_query = {'TEAM_NAME' : founder_profile['TEAM']}
                            steam_query = {'TEAM_NAME' : sworn_profile['TEAM']}
                            founder_team = db.queryTeam(fteam_query)
                            sworn_team = db.queryTeam(steam_query)
                            fbal = founder_team['BANK']
                            sbal = sworn_team['BANK']
                            if founder_team['TEAM_NAME'] == sworn_team['TEAM_NAME']:
                                await ctx.send(m.SAME_TEAM, delete_after=3)
                                return
                            # if sbal < cost:
                            #     await ctx.send(m.NBROKE_TEAM, delete_after=3)
                            #     return
                        
                            guild_query = {'FDID': str(ctx.author.id)}
                            guild_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="✔️",
                                    custom_id="Yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.red,
                                    label="❌",
                                    custom_id="No"
                                )
                            ]
                            guild_buttons_action_row = manage_components.create_actionrow(*guild_buttons)
                            await ctx.send(f"Do you wish to swear an oath with {owner.mention}?".format(self), components=[guild_buttons_action_row])


                            def check(button_ctx):
                                return button_ctx.author == ctx.author

                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[guild_buttons_action_row], check=check)

                                if button_ctx.custom_id == "No":
                                    await button_ctx.send("No Oath Sent")
                                    return
                                
                                if button_ctx.custom_id == "Yes":
                                    await main.DM(ctx, owner, f"{ctx.author.mention}" + f" would like to join the Association {guild_name}" + f" React in server to join their Association" )
                                    await ctx.send(f"{owner.mention}" +f" will you swear the oath?".format(self), components=[guild_buttons_action_row])
                                    def check(button_ctx):
                                        return button_ctx.author == sworn

                                    try:
                                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[guild_buttons_action_row], check=check)

                                        if button_ctx.custom_id == "No":
                                            await button_ctx.send("Oath Request Denied")
                                            return
                                        
                                        if button_ctx.custom_id == "Yes":
                                            try:
                                                sword_list = []
                                                for sword in guildsearch['SWORDS']:
                                                    sword_list.append(sword)
                                                newvalue = {'$set': {'SWORN': str(owner), 'WDID': str(owner.id)}}
                                                nextresponse = db.addGuildSworn(guild_query, newvalue, ctx.author, owner)
                                                await ctx.send(nextresponse)
                                                shield = db.updateGuild(guild_query, {'$set' : {'SHIELD' : str(owner), 'SDID' : owner.id}})
                                                newvalue = {'$set': {'SHIELD': str(owner), 'SDID': str(owner.id)}}
                                                response = db.addGuildShield(guild_query, newvalue, ctx.author, owner)
                                                await ctx.send(response)
                                                if sworn_team['TEAM_NAME'] not in sword_list:
                                                    newvalue = {'$push': {'SWORDS': str(sworn_team['TEAM_NAME'])}}
                                                    swordaddition2 = db.addGuildSword(guild_query, newvalue, ctx.author, str(sworn_team['TEAM_NAME']))
                                                    await ctx.send(swordaddition2)
                                                gbank = db.updateGuild(guild_query,{'$inc' : {'BANK' : cost }})
                                                s_new_bal = sbal - cost
                                                new_value = {'$set' : {'BANK' : s_new_bal}}
                                                steambal = db.updateTeam(steam_query, new_value)       
                                                
                                                guild_query = {'GNAME': guild_name}
                                                guild = db.queryGuildAlt(guild_query)
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
                                                
                                                sword_list = []
                                                sword_count = 0
                                                blade_count = 0
                                                for swords in guild['SWORDS']:
                                                    blade_count = 0
                                                    sword_count = sword_count + 1
                                                    sword_team = db.queryTeam({'TEAM_NAME': swords})
                                                    dubs = sword_team['SCRIM_WINS']
                                                    els = sword_team['SCRIM_LOSSES']
                                                    for blades in sword_team['MEMBERS']:
                                                        blade_count = blade_count + 1
                                                    sword_bank = sword_team['BANK']
                                                    sword_list.append(f"~ {swords} ~ W**{dubs}** / L**{els}**\n:man_detective: | **Owner: **{sword_team['OWNER']}\n:coin: | **Bank: **{'{:,}'.format(sword_bank)}\n:knife: | **Members: **{blade_count}\n_______________________")
                                                crest_list = []
                                                for c in crest:
                                                    crest_list.append(f"{crown_utilities.crest_dict[c]} | {c}")
                                                
                                                embed1 = discord.Embed(title= f":flags: |{str(guild_name)} Association Card - :coin: {'{:,}'.format(2000000)}".format(self), description=textwrap.dedent(f"""\
                
                                                :nesting_dolls: | **Founder ~** {founder_profile['NAME']}
                                                :dolls: | **Sworn ~** {sworn_profile['NAME']}
                                                

                                                :japanese_goblin: | **Shield: ~**{sworn_profile['NAME']} ~ :beginner: | **Victories: **{0}
                                                :flower_playing_cards: | **Card: **{sworn_profile['CARD']}
                                                :reminder_ribbon: | **Title: **{sworn_profile['TITLE']}
                                                :mechanical_arm: | **Arm: **{sworn_profile['ARM']}
                                                
                                                :ninja: | **Swords: ** 2
                                                **{founder_team['TEAM_NAME']}**
                                                **{sworn_team['TEAM_NAME']}**
                                                :dollar: | **Guild Split: **{hall_split} 
                                                :secret: | **Universe Crest: **{len(crest_list)} 
                                                    
                                                :shinto_shrine: | **Hall: **{hall_name} 
                                                :shield: | **Raid Defenses: ** {hall_def}
                                                :coin: | **Raid Fee: **{'{:,}'.format(hall_fee)}
                                                :yen: | **Bounty: **{'{:,}'.format(bounty)}
                                                :moneybag: | **Victory Bonus: **{'{:,}'.format(bonus)}
                                                """), colour=000000)
                                                embed1.set_image(url=hall_img)
                                                embed1.set_footer(text=f"/raid {guild_name} - Test Raid Defenses!")
                                                await ctx.send(embed =embed1)
                                                           
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
                                    except:
                                        print("Association creation ended unexpectedly. ")
                            except:
                                print("Association creation ended unexpectedly. ")                    
            else:
                sworn_profile = db.queryUser({'DID': str(owner.id)})
                investment = cost * 2
                if founder_profile['GUILD'] != 'PCG' and founder_profile['GUILD'] != 'N/A' and founder_profile['GUILD'] != founder_profile['DISNAME'] :
                    await ctx.send(m.USER_IN_GUILD, delete_after=3)
                    return
                elif sworn_profile['GUILD'] != 'PCG' and sworn_profile['GUILD'] != 'N/A':
                    await ctx.send(m.USER_IN_GUILD, delete_after=3)
                    return
                else:
                    if founder_profile['TEAM'] == 'PCG' or sworn_profile['TEAM'] == 'PCG':
                        await ctx.send(m.FOUNDER_NO_TEAM, delete_after=3)
                        return
                    else:
                        fteam_query = {'TEAM_NAME' : founder_profile['TEAM'].lower()}
                        steam_query = {'TEAM_NAME' : sworn_profile['TEAM'].lower()}
                        founder_team = db.queryTeam(fteam_query)
                        sworn_team = db.queryTeam(steam_query)
                        fbal = founder_team['BANK']
                        sbal = sworn_team['BANK']
                        if founder_team['TEAM_NAME'] == sworn_team['TEAM_NAME']:
                            await ctx.send(m.SAME_TEAM, delete_after=3)
                            return
                        if fbal < cost or sbal < cost:
                            await ctx.send(m.BROKE_TEAM, delete_after=3)
                            return
                                        
                        guild_query = {'FOUNDER': str(ctx.author), 'FDID': str(ctx.author.id)}
                        guild_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="✔️",
                                custom_id="Yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.red,
                                label="❌",
                                custom_id="No"
                            )
                        ]
                        guild_buttons_action_row = manage_components.create_actionrow(*guild_buttons)
                        await ctx.send(f"Do you wish to swear an oath with {owner.mention}?".format(self), components=[guild_buttons_action_row])


                        def check(button_ctx):
                            return button_ctx.author == ctx.author

                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[guild_buttons_action_row], check=check)

                            if button_ctx.custom_id == "No":
                                await button_ctx.send("No Oath Sent")
                                return
                            
                            if button_ctx.custom_id == "Yes":
                                await main.DM(ctx, owner, f"{ctx.author.mention}" + f" would like to join the Association {guild_name}" + f" React in server to join their Association" )
                                await ctx.send(f"{owner.mention}" +f" will you swear the oath?".format(self), components=[guild_buttons_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == owner

                                try:
                                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[guild_buttons_action_row], check=check)

                                    if button_ctx.custom_id == "No":
                                        await button_ctx.send("Oath Request Denied")
                                        return
                                    
                                    if button_ctx.custom_id == "Yes":
                                        try:
                                            firstresponse = db.createGuild(data.newGuild(guild_query), ctx.author, str(guild_name))
                                            await ctx.send(firstresponse)
                                            nameguild = db.updateGuild(guild_query,{'$set' : {'GNAME' : str(guild_name)}})
                                            newvalue = {'$set': {'SWORN': str(owner), 'WDID':str(owner.id)}}
                                            nextresponse = db.addGuildSworn(guild_query, newvalue, ctx.author, owner)
                                            await ctx.send(nextresponse)
                                            shield = db.updateGuild(guild_query, {'$set' : {'SHIELD' : str(owner), 'SDID': str(owner.id)}})
                                            newvalue = {'$set': {'SHIELD': str(owner), 'SDID': str(owner.id)}}
                                            response = db.addGuildShield(guild_query, newvalue, ctx.author, owner)
                                            await ctx.send(response)
                                            newvalue = {'$push': {'SWORDS': str(founder_team['TEAM_NAME'])}}
                                            swordaddition = db.addGuildSword(guild_query, newvalue, ctx.author, str(founder_team['TEAM_NAME']))
                                            await ctx.send(swordaddition)
                                            newvalue = {'$push': {'SWORDS': str(sworn_team['TEAM_NAME'])}}
                                            swordaddition2 = db.addGuildSword(guild_query, newvalue, ctx.author, str(sworn_team['TEAM_NAME']))
                                            await ctx.send(swordaddition2)
                                            gbank = db.updateGuild(guild_query,{'$set' : {'BANK' : investment }})
                                            new_bal = fbal - cost
                                            new_value = {'$set' : {'BANK' : new_bal}}
                                            fteambal = db.updateTeam(fteam_query, new_value)
                                            s_new_bal = sbal - cost
                                            new_value = {'$set' : {'BANK' : s_new_bal, 'SHIELDING': True}}
                                            steambal = db.updateTeam(steam_query, new_value)    
                                            
                                            guild_query = {'GNAME': guild_name}
                                            guild = db.queryGuildAlt(guild_query)
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
                                            
                                            sword_list = []
                                            sword_count = 0
                                            blade_count = 0
                                            for swords in guild['SWORDS']:
                                                blade_count = 0
                                                sword_count = sword_count + 1
                                                sword_team = db.queryTeam({'TEAM_NAME': swords})
                                                dubs = sword_team['WINS']
                                                els = sword_team['LOSSES']
                                                for blades in sword_team['MEMBERS']:
                                                    blade_count = blade_count + 1
                                                sword_bank = sword_team['BANK']
                                                sword_list.append(f"~ {swords} ~ W**{dubs}** / L**{els}**\n:man_detective: | **Owner: **{sword_team['OWNER']}\n:coin: | **Bank: **{'{:,}'.format(sword_bank)}\n:knife: | **Members: **{blade_count}\n_______________________")
                                            crest_list = []
                                            for c in crest:
                                                crest_list.append(f"{crown_utilities.crest_dict[c]} | {c}")
                                            
                                            embed1 = discord.Embed(title= f":flags: |{str(guild_name)} Association Card - :coin: {'{:,}'.format(2000000)}".format(self), description=textwrap.dedent(f"""\
            
                                            :nesting_dolls: | **Founder ~** {founder_profile['NAME']}
                                            :dolls: | **Sworn ~** {sworn_profile['NAME']}
                                            

                                            :japanese_goblin: | **Shield: ~**{sworn_profile['NAME']} ~ :beginner: | **Victories: **{0}
                                            :flower_playing_cards: | **Card: **{sworn_profile['CARD']}
                                            :reminder_ribbon: | **Title: **{sworn_profile['TITLE']}
                                            :mechanical_arm: | **Arm: **{sworn_profile['ARM']}
                                            
                                            :ninja: | **Swords: ** 2
                                            **{founder_team['TEAM_NAME']}**
                                            **{sworn_team['TEAM_NAME']}**
                                            :dollar: | **Guild Split: **{hall_split} 
                                            :secret: | **Universe Crest: **{len(crest_list)} 
                                                
                                            :shinto_shrine: | **Hall: **{hall_name} 
                                            :shield: | **Raid Defenses: ** {hall_def}
                                            :coin: | **Raid Fee: **{'{:,}'.format(hall_fee)}
                                            :yen: | **Bounty: **{'{:,}'.format(bounty)}
                                            :moneybag: | **Victory Bonus: **{'{:,}'.format(bonus)}
                                            """), colour=000000)
                                            embed1.set_image(url=hall_img)
                                            embed1.set_footer(text=f"/raid {guild_name} - Test Raid Defenses!")
                                            await ctx.send(embed =embed1)
                                                        
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
            await ctx.send(
                "There's an issue with your Oath. Alert support.")
            return
            
                   
    @cog_ext.cog_slash(description="Betray your Association (Association Sworn)", guild_ids=main.guild_ids)
    async def betray(self, ctx, founder: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            sworn_profile = db.queryUser({'DID': str(ctx.author.id)})
            founder_profile = db.queryUser({'DID': str(founder.id)})
            if sworn_profile['GUILD'] != founder_profile['GUILD']:
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
                return
            guild_query = {'FDID': str(founder.id)}
            guild_profile = db.queryGuild(guild_query)
            guild_bank = guild_profile['BANK']
            team_name = sworn_profile['TEAM'].lower()
            
            warchest = guild_bank
            
            if guild_profile:
                if sworn_profile['DID'] == guild_profile['WDID']:
                    trade_buttons = [
                        manage_components.create_button(
                            style=ButtonStyle.red,
                            label="Betray Association",
                            custom_id="yes"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="No",
                            custom_id="no"
                        )
                    ]
                    trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                    await ctx.send(f"Will you renounce your Oath?".format(self), components=[trade_buttons_action_row])
                    
                    def check(button_ctx):
                        return button_ctx.author == ctx.author

                    
                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                        if button_ctx.custom_id == "no":
                            await button_ctx.send("No Change")
                            self.stop = True
                            return
                        if button_ctx.custom_id == "yes":
                            prev_team_update = {'$set': {'SHIELDING': False}}
                            remove_shield = db.updateTeam({'TEAM_NAME': str(team_name)}, prev_team_update)
                            newvalue = {'$pull': {'SWORDS': str(team_name)}}
                            response2 = db.deleteGuildSword(guild_query, newvalue, ctx.author, str(team_name))
                            await ctx.send(response2)
                            new_value_query = {'$set': {'SWORN': 'BETRAYED', 'SHIELD' : str(founder), 'WDID' : str("BETRAYED"), 'SDID' : str(founder.id)}}
                            response = db.deleteGuildSwornAlt(guild_query, new_value_query, ctx.author)
                            await ctx.send(response)                  
                        
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
                    await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)
            else:
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
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

    @cog_ext.cog_slash(description="Ask Guild Owner to join Association! (Association Owner)", guild_ids=main.guild_ids)
    async def ally(self, ctx, owner: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            founder_profile = db.queryUser({'DID': str(ctx.author.id)})
            guildname = founder_profile['GUILD']
            sword_profile = db.queryUser({'DID': str(owner.id)})
            team_profile = db.queryTeam({'TEAM_NAME': sword_profile['TEAM'].lower()})
            if not team_profile:
                await ctx.send(f"{owner.mention} does not own a Guild")
            team_name = team_profile['TEAM_NAME']
            team_owner = team_profile['OWNER']
            if founder_profile['GUILD'] == 'PCG':
                await ctx.send(m.USER_NOT_IN_GUILD, delete_after=3)
            elif team_profile['GUILD'] != 'PCG':
                await ctx.send(m.USER_IN_GUILD, delete_after=3)
            elif sword_profile['DISNAME'] != team_owner:
                await ctx.send(m.SWORD_NO_TEAM, delete_after=3)
            else:
                guild_query = {'GNAME': str(guildname)}
                guild = db.queryGuildAlt(guild_query)
                new_query = {'FDID' : guild['FDID']}
                f_profile = guild['FDID']
                s_profile = guild['WDID']
                guild_name = guildname
                if founder_profile['DID'] != f_profile and founder_profile['DID'] != s_profile:
                    await ctx.send(m.ENLIST_GUILD_FOUNDER, delete_after=3)
                    return
                trade_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="Ally",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                await ctx.send(f"Do you want to ally with {team_name}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No Change")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        await main.DM(ctx, owner, f"{ctx.author.mention}" + f" would like to ally with your team!" + f" React in server to join their Association" )
                        trade_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Form Alliance",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.blue,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                        await ctx.send(f"{owner.mention}" +f" will you join {guild_name}?".format(self), components=[trade_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == owner

                        
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                            if button_ctx.custom_id == "no":
                                await button_ctx.send("No Change")
                                self.stop = True
                                return
                            if button_ctx.custom_id == "yes":
                                newvalue = {'$push': {'SWORDS': str(team_name)}}
                                response = db.addGuildSword(new_query, newvalue, ctx.author, str(team_name))
                                await ctx.send(response)
                        
                        except:
                            await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)
                except:
                    print("No proposal Sent") 
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
            await ctx.send(
                "There's an issue with your commnads. Alert support.")
            return    
                
    @cog_ext.cog_slash(description="Knight your Association Shield! (Association Owner)", guild_ids=main.guild_ids)
    async def knight(self, ctx, blade: User):
        try:
            a_registered_player = await crown_utilities.player_check(ctx)
            if not a_registered_player:
                return

            founder_profile = db.queryUser({'DID': str(ctx.author.id)})
            shield_profile = db.queryUser({'DID' : str(blade.id)})
            if not shield_profile:
                await ctx.send(m.USER_NOT_REGISTERED)
            shield_team_name = shield_profile['TEAM'].lower()
            if shield_team_name == 'PCG':
                await ctx.send(m.KNIGHT_NOT_TEAM, delete_after=3)
                return
            shield_team = db.queryTeam({'TEAM_NAME' : str(shield_team_name)})
            if shield_team['GUILD'] != founder_profile['GUILD']:
                await ctx.send(m.KNIGHT_NOT_TEAM, delete_after=3)
                return
            guildname = founder_profile['GUILD']
            if founder_profile['GUILD'] == 'PCG':
                await ctx.send(m.USER_NOT_IN_GUILD, delete_after=3)
                return
            guild_query = {'GNAME': str(guildname)}
            guild = db.queryGuildAlt(guild_query)
            if guild:
                prev_id = guild['SDID']
                prev_user = db.queryUser({'DID':prev_id})
                prev_team = db.queryTeam({'TEAM_NAME':prev_user['TEAM']})
                prev_team_exist = False
                if prev_team:
                    prev_team_exist = True
                new_query = {'FDID' : guild['FDID']}
                f_profile = guild['FDID']
                s_profile = guild['WDID']
                if founder_profile['DID'] != f_profile and founder_profile['DID'] != s_profile:
                    await ctx.send(m.KNIGHT_GUILD_FOUNDER, delete_after=3)
                    return
                trade_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="Knight",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                await ctx.send(f"Do you wish to knight {blade.mention}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No Change")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        try: 
                            await main.DM(ctx, blade, f"{ctx.author.mention}" + f" would like you to serve as the Association Shield!" + f" React in server to protect the Association" )
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Serve",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await ctx.send(f"{blade.mention}" +f" will you defend **:flags:{guildname}**?".format(self), components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == blade

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("Knight Refused")
                                    self.stop = True
                                    return
                                if button_ctx.custom_id == "yes":
                                    if prev_team_exist:
                                        prev_team_update = {'$set': {'SHIELDING': False}}
                                        remove_shield = db.updateTeam({'TEAM_NAME': str(prev_team['TEAM_NAME'])}, prev_team_update)
                                    update_shielding = {'$set': {'SHIELDING': True}}
                                    add_shield = db.updateTeam({'TEAM_NAME': str(shield_team_name)}, update_shielding)
                                    newvalue = {'$set': {'SHIELD': str(blade), 'STREAK' : 0, 'SDID' : str(blade.id)}}
                                    response = db.addGuildShield(new_query, newvalue, ctx.author, blade)
                                    await ctx.send(response)
                                    
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
                                await ctx.send(
                                    "There's an issue with your commnads. Alert support.")
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
                            await ctx.send(
                                "There's an issue with your commnads. Alert support.")
                            return
                except:
                    print("No proposal Sent")
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
            await ctx.send(
                "There's an issue with your commnads. Alert support.")
            return
    
    @cog_ext.cog_slash(description="Exile Guild from Association (Association Owner)", guild_ids=main.guild_ids)
    async def exile(self, ctx, owner: User):
        try:
            leader_profile = db.queryUser({'DID': str(ctx.author.id)})
            exiled_profile = db.queryUser({'DID': str(owner.id)})
            if not exiled_profile:
                await ctx.send(m.USER_DOESNT_EXIST, delete_after=5)
                return
            exiled_team = db.queryTeam({'TEAM_NAME' : exiled_profile['TEAM'].lower()})
            if leader_profile['GUILD'] != exiled_team['GUILD']:
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
                return
            guild_query = {'GNAME': leader_profile['GUILD']}
            guild_profile = db.queryGuildAlt(guild_query)
            new_query = {'FDID' : guild_profile['FDID']}
            
            if guild_profile:
                if leader_profile['DID'] == guild_profile['FDID'] or leader_profile['DID'] == guild_profile['WDID'] or leader_profile['DID'] == guild_profile['SDID']: 
                    accept = await ctx.send(f"".format(self), delete_after=8)
                    trade_buttons = [
                        manage_components.create_button(
                            style=ButtonStyle.red,
                            label="Exile Guild",
                            custom_id="yes"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="No",
                            custom_id="no"
                        )
                    ]
                    trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                    await ctx.send(f"Do you wish to Exile {owner.mention} and {exiled_profile['TEAM']}?".format(self), components=[trade_buttons_action_row])
                    
                    def check(button_ctx):
                        return button_ctx.author == ctx.author

                    
                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                        if button_ctx.custom_id == "no":
                            await button_ctx.send("No Change")
                            self.stop = True
                            return
                        if button_ctx.custom_id == "yes":
                            prev_team_update = {'$set': {'SHIELDING': False}}
                            remove_shield = db.updateTeam({'TEAM_NAME': str(exiled_team['TEAM_NAME'])}, prev_team_update)
                            new_value_query = {'$pull': {'SWORDS': str(exiled_profile['TEAM'])}, '$set': {'SHIELD': guild_profile['SWORN'], 'SDID': guild_profile['WDID']}}
                            response2 = db.deleteGuildSword(new_query, new_value_query, ctx.author, str(exiled_profile['TEAM']))
                            await ctx.send(response2)
                    except:
                        print("No Exile")
                else:
                    await ctx.send(m.EXILE_GUILD_FOUNDER, delete_after=5)
            else:
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
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
            await ctx.send(
                "There's an issue with your commnads. Alert support.")
            return
    @cog_ext.cog_slash(description="Abandon Association (Guild Owner)", guild_ids=main.guild_ids)
    async def renounce(self, ctx):
        try:
            sword_profile = db.queryUser({'DID': str(ctx.author.id)})
            team_profile = db.queryTeam({'TEAM_NAME' : sword_profile['TEAM'].lower()})
            if sword_profile['DISNAME'] != team_profile['OWNER'] or sword_profile['TEAM'] == 'PCG':
                await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)
                return
            team_name = team_profile['TEAM_NAME']
            guild_query = {'GNAME': team_profile['GUILD']}
            guild_profile = db.queryGuildAlt(guild_query)  
            if guild_profile:
                if sword_profile['DID'] == guild_profile['WDID']:
                    await ctx.send(m.SWORD_LEAVE, delete_after=5)
                    return      
                trade_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="Renounce Oath",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                await ctx.send(f"Do you wish to renounce your allegiance to {guild_profile['GNAME']}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No Change")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        try:
                            prev_team_update = {'$set': {'SHIELDING': False}}
                            remove_shield = db.updateTeam({'TEAM_NAME': str(team_profile['TEAM_NAME'])}, prev_team_update)
                            new_value_query = {'$pull': {'SWORDS': str(team_name)}, '$set': {'SHIELD': guild_profile['SWORN'], 'SDID': guild_profile['WDID']}}
                            response = db.deleteGuildSwordAlt(guild_query, new_value_query, str(team_name))
                            await ctx.send(response)
                        except:
                            print("Association not created. ")
                except:
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
                await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
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
            await ctx.send(
                "There's an issue with your commnads. Alert support.")
            return
    
    @cog_ext.cog_slash(description="Disband your Association (Association Founder)", guild_ids=main.guild_ids)
    async def disband(self, ctx):
        try:
            guild_query = {'FDID': str(ctx.author.id)}
            guild = db.queryGuild(guild_query)
            if guild:
                if guild['FDID'] == str(ctx.author.id):
                    trade_buttons = [
                        manage_components.create_button(
                            style=ButtonStyle.red,
                            label="Disband Assosiation",
                            custom_id="yes"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="No",
                            custom_id="no"
                        )
                    ]
                    trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                    await ctx.send(f"Do you want to disband the {guild['GNAME']}?".format(self), components=[trade_buttons_action_row])
                    
                    def check(button_ctx):
                        return button_ctx.author == ctx.author

                    
                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                        if button_ctx.custom_id == "no":
                            await button_ctx.send("Association not Disbanded")
                            self.stop = True
                            return
                        if button_ctx.custom_id == "yes":
                            try:
                                response = db.deleteGuild(guild, ctx.author)

                                user_query = {'DID': str(ctx.author.id)}
                                new_value = {'$set': {'GUILD': 'PCG'}}
                                db.updateUserNoFilter(user_query, new_value)

                                await ctx.send(response)
                            
                            except:
                                print("Association Not Deleted. ")
                    except:
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
                    await ctx.send("Only the Founder can disband the Association. ")
            else:
                await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)
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
            await ctx.send(
                "There's an issue with your commnads. Alert support.")
            return

def setup(bot):
    bot.add_cog(Guild(bot))