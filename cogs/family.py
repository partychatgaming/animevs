import discord
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
import DiscordUtils
from discord_slash import cog_ext, SlashContext
import asyncio
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from dinteractions_Paginator import Paginator

emojis = ['👍', '👎']

class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Family Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)


    @cog_ext.cog_slash(description="Marry a player", guild_ids=main.guild_ids)
    async def marry(self, ctx, player: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            head_profile = db.queryUser({'DID': str(ctx.author.id)})
            partner_profile = db.queryUser({'DID': str(player.id)})
            if head_profile['LEVEL'] < 31:
                await ctx.send(f"🔓 {ctx.author.mention} Unlock Family by completing Floor 30 of the 🌑 Abyss! Use /solo to enter the abyss.")
                return
            if partner_profile['LEVEL'] < 31:
                await ctx.send(f"🔓 {player.mention} Unlock Family by completing Floor 30 of the 🌑 Abyss! Use /solo to enter the abyss.")
                return

            if head_profile['DISNAME'] == partner_profile['DISNAME']:
                await ctx.send("You cannot **Marry** yourself", delete_after=8)
                return
            if head_profile['FAMILY'] != 'PCG' and head_profile['FAMILY'] != 'N/A' and head_profile['FAMILY'] != head_profile['DISNAME'] :
                await ctx.send(m.USER_IN_FAMILY, delete_after=3)
            elif partner_profile['FAMILY'] != 'PCG' and partner_profile['FAMILY'] != 'N/A' and partner_profile['FAMILY'] != partner_profile['DISNAME']:
                await ctx.send(m.USER_IN_FAMILY, delete_after=3)
            else:
                family_query = {'HEAD': str(ctx.author)}
                
                trade_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="Propose!",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                await ctx.send(f"Do you want to propose to **{player.mention}**?", components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                            await button_ctx.send("No **Proposal**")
                            self.stop = True
                            return
                    if button_ctx.custom_id == "yes":
                        await main.DM(ctx, player, f"{ctx.author.mention}" + f" proposed to you !" + f" React in server to join their family" )
                        trade_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Lets Get Married!",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.red,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                        await button_ctx.send(f"**{player.mention}** do you accept the proposal?".format(self), components=[trade_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == player

                        
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                            if button_ctx.custom_id == "no":
                                    await button_ctx.send("**Proposal Denied**")
                                    self.stop = True
                                    return
                            if button_ctx.custom_id == "yes":
                                try:
                                    #response = db.createFamily(data.newFamily(family_query), str(ctx.author))
                                    #await ctx.send(response)
                                    newvalue = {'$set': {'PARTNER': str(player)}}
                                    nextresponse = db.addFamilyMember(family_query, newvalue, str(ctx.author), str(player))
                                    update_player = {'$set': {'FAMILY': str(ctx.author)}}
                                    player_response = db.updateUserNoFilter(update_player)
                                    await ctx.send(nextresponse)
                                except:
                                    await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)
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
                            await ctx.send(f"ERROR:\nTYPE: {type(ex).__name__}\nMESSAGE: {str(ex)}\nLINE: {trace} ")
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
                'PLAYER': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            return

    @cog_ext.cog_slash(description="Divorce your partner", guild_ids=main.guild_ids)
    async def divorce(self, ctx, partner: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        head_profile = db.queryUser({'DID': str(ctx.author.id)})
        partner_profile = db.queryUser({'DISNAME': str(partner)})
        family_profile = db.queryFamily({'HEAD': head_profile['FAMILY']})
        if family_profile['HEAD'] == str(ctx.author):
            if family_profile['PARTNER'] != str(partner):
                await ctx.send(f"Must select your **partner**: {family_profile['PARTNER']}", delete_after=8)
                return
        elif family_profile['PARTNER'] == str(ctx.author):
            if family_profile['HEAD'] != str(partner):
                await ctx.send(f"Must select your **partner**: {family_profile['HEAD']}", delete_after=8)
                return
        if not family_profile:
            family_profile = db.queryFamily({'HEAD': partner_profile['FAMILY']})
        if head_profile['DISNAME'] == partner_profile['DISNAME']:
            await ctx.send("You cannot **divorce** yourself", delete_after=8)
            return
        family_bank = family_profile['BANK']
        divorce_split = int(family_bank * .50)
        family_query = {'HEAD': str(ctx.author)}
        if family_profile:
            if head_profile['DISNAME'] == family_profile['HEAD'] or head_profile['DISNAME'] == family_profile['PARTNER']:
                trade_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="Divorce!",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                await ctx.send(f"Do you want to divorce {partner.mention}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No **Divorce**")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        await main.DM(ctx, partner, f"{ctx.author.mention}" + f"is divorcing you!" + f" You will be removed from the family in 90 seconds" )
                        trade_buttons = [
                            manage_components.create_button(
                                style=ButtonStyle.green,
                                label="Accept! Half of Family Bank",
                                custom_id="yes"
                            ),
                            manage_components.create_button(
                                style=ButtonStyle.red,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                        await button_ctx.send(f"{partner.mention} do you accept the divorce? You will gain half the family bank :coin:**{'{:,}'.format(divorce_split)}**.\n*{family_profile['PARTNER']} will be automatically removed from the family in 90 seconds*".format(self), components=[trade_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == partner

                        
                        try:
                            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=90, check=check)
                            if button_ctx.custom_id == "no":
                                await button_ctx.send("No **Divorce**")
                                self.stop = True
                            if button_ctx.custom_id == "yes":
                                try:
                                    if str(partner) == family_profile['PARTNER']:
                                        await button_ctx.send(f"**Divorce Finalized** {partner.mention} earned :coin:**{'{:,}'.format(divorce_split)}**")
                                    else:
                                        await button_ctx.send(f"**Divorce Finalized** {ctx.author.mention} earned :coin:**{'{:,}'.format(divorce_split)}**")
                                    
                                    new_value_query = {'$set': {'PARTNER': '' }}
                                    await main.cursefamily(divorce_split,family_profile['HEAD'])
                                    response = db.deleteFamilyMember(family_query, new_value_query, str(ctx.author), str(partner))
                                    if str(ctx.author) == family_profile['PARTNER']:
                                        family_query = {'HEAD': str(partner)}
                                        response = db.deleteFamilyMember(family_query, new_value_query, str(partner), str(ctx.author))
                                        user_query = {'DISNAME':str(partner)}
                                        user_info = db.queryUser(user_query)
                                        old_family = db.updateUserNoFilter({'FAMILY':user_info['DISNAME']})
                                    await button_ctx.send(response)
                                    await main.bless(divorce_split, str(family_profile['PARTNER']))
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
                                    return
                        except asyncio.TimeoutError:
                            if str(partner) == family_profile['PARTNER']:
                                await button_ctx.send(f"**Divorce Finalized** {partner.mention} removed!")
                            else:
                                await button_ctx.send(f"**Divorce Finalized** {ctx.author.mention} removed!")
                            new_value_query = {'$set': {'PARTNER': '' }}
                            await main.cursefamily(divorce_split,family_profile['HEAD'])
                            response = db.deleteFamilyMember(family_query, new_value_query, str(ctx.author), str(partner))
                            if str(ctx.author) == family_profile['PARTNER']:
                                family_query = {'HEAD': str(partner)}
                                response = db.deleteFamilyMember(family_query, new_value_query, str(partner), str(ctx.author))
                            await button_ctx.send(response)
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
                    return
            else:
                await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)
        else:
            await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)

    @cog_ext.cog_slash(description="Adopt a kid", guild_ids=main.guild_ids)
    async def adopt(self, ctx, player: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            head_profile = db.queryUser({'DID': str(ctx.author.id)})
            kid_profile = db.queryUser({'DISNAME': str(player)})
            partner_mode = False
            if head_profile['FAMILY'] == 'PCG':
                await ctx.send("Join or Start a family to adopt Kids!", delete_after=3)
            #elif kid_profile['FAMILY'] != 'PCG':
                #await ctx.send(m.USER_IN_FAMILY, delete_after=3)
            else:
                family_query = {'HEAD': str(ctx.author)}
                family = db.queryFamily(family_query)
                if not family:
                    family_query = {'PARTNER':str(ctx.author)}
                    family = db.queryFamilyAlt(family_query)
                    partner_mode=True
                if family['HEAD'] != str(ctx.author):
                    if family['PARTNER'] != str(ctx.author):
                        await ctx.send("Must be **Head or Partner** to adopt!")
                kid_count = 0
                for kids in family['KIDS']:
                    kid_count = kid_count + 1
                if kid_count >= 2:
                    await ctx.send(m.MAX_CHILDREN, delete_after=3)
                    return

                trade_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.green,
                        label="Adopt!",
                        custom_id="yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                await ctx.send(f"Do you want to adopt {player.mention}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No **Adoption**")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        try:
                            await main.DM(ctx, player, f"{ctx.author.mention}" + f" would like to adopt you!" + f" React in server to join their **Family**" )
                            trade_buttons = [
                                manage_components.create_button(
                                    style=ButtonStyle.green,
                                    label="Join Family!",
                                    custom_id="yes"
                                ),
                                manage_components.create_button(
                                    style=ButtonStyle.blue,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                            await button_ctx.send(f"{player.mention}" +f" would you like to be adopted ?".format(self), components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == player

                            
                            try:
                                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                                if button_ctx.custom_id == "no":
                                    await button_ctx.send("No **Adoption**")
                                    self.stop = True
                                    return
                                if button_ctx.custom_id == "yes":
                                    try:
                                        newvalue = {'$push': {'KIDS': str(player)}}
                                        if partner_mode:
                                            response = db.addFamilyMemberAlt(family_query, newvalue, str(ctx.author), str(player))
                                        else:
                                            response = db.addFamilyMember(family_query, newvalue, str(ctx.author), str(player))
                                        user_update = {'$set' : {'FAMILY': str(family['HEAD'])}}
                                        user_query = {'DID' : kid_profile['DID']}
                                        user_update = db.updateUserNoFilter(user_query, user_update)
                                        await button_ctx.send(response)                                       
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
                                    'PLAYER': str(ctx.author),
                                    'type': type(ex).__name__,
                                    'message': str(ex),
                                    'trace': trace
                                }))
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
                        'PLAYER': str(ctx.author),
                        'type': type(ex).__name__,
                        'message': str(ex),
                        'trace': trace
                    }))
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
                'PLAYER': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            return

    @cog_ext.cog_slash(description="Disown your kid", guild_ids=main.guild_ids)
    async def disown(self, ctx, kid: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            head_profile = db.queryUser({'DID': str(ctx.author.id)})
            family_profile = db.queryFamily({'HEAD': head_profile['FAMILY']})
            family_query = {'HEAD': str(ctx.author)}
            if str(ctx.author) != family_profile['HEAD']:
                await ctx.send(f"Must be **Head of Household** to Disown.")
                return
            if family_profile:
                kidlist = []
                for k in family_profile['KIDS']:
                    kidlist.append(k)
                if str(kid) not in kidlist:
                    await ctx.send(f"{kid} not your **Kid**")
                    return
                if head_profile['DISNAME'] == family_profile['HEAD']:
                    trade_buttons = [
                        manage_components.create_button(
                            style=ButtonStyle.red,
                            label="Disown!",
                            custom_id="yes"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="No",
                            custom_id="no"
                        )
                    ]
                    trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
                    await ctx.send(f"Do you want to disown {kid.mention}?".format(self), components=[trade_buttons_action_row])
                    
                    def check(button_ctx):
                        return button_ctx.author == ctx.author

                    
                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                        if button_ctx.custom_id == "no":
                            await button_ctx.send("Not **Disowned**")
                            self.stop = True
                            return
                        if button_ctx.custom_id == "yes":
                            try:
                                new_value_query = {'$pull': {'KIDS': str(kid) }}
                                response = db.deleteFamilyMember(family_query, new_value_query, str(ctx.author), str(kid))
                                user_update = {'$set' : {'FAMILY': str(kid)}}
                                user_query = {'DID' : str(kid.id)}
                                user_update = db.updateUserNoFilter(user_query, user_update)
                                await button_ctx.send(response)
                            except:
                                print("No Disown")
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
                        return
                else:
                    await ctx.send("Only **Head of Household** can disown.", delete_after=5)
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
                'PLAYER': str(ctx.author),
                'type': type(ex).__name__,
                'message': str(ex),
                'trace': trace
            }))
            return 

    @cog_ext.cog_slash(description="Leave your adopted family", guild_ids=main.guild_ids)
    async def leavefamily(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        kid_profile = db.queryUser({'DID': str(ctx.author.id)})
        family_profile = db.queryFamily({'HEAD': kid_profile['FAMILY']})
        kidlist = []
        family_query = {'HEAD': kid_profile['FAMILY']}
        if family_profile:
            for k in family_profile['KIDS']:
                kidlist.append(k)
            if str(ctx.author) not in kidlist:
                await ctx.send(f"Must be an **Adopted Kid**")
                return
            trade_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="Leave Family!",
                    custom_id="yes"
                ),
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="No",
                    custom_id="no"
                )
            ]
            trade_buttons_action_row = manage_components.create_actionrow(*trade_buttons)
            await ctx.send(f"Do you want to **Leave** your family?".format(self), components=[trade_buttons_action_row])
            
            def check(button_ctx):
                return button_ctx.author == ctx.author

            
            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[trade_buttons_action_row], timeout=120, check=check)
                if button_ctx.custom_id == "no":
                    await button_ctx.send("Family Not **Abandoned**")
                    self.stop = True
                    return
                if button_ctx.custom_id == "yes":
                    try:
                        new_value_query = {'$pull': {'KIDS': str(ctx.author)}}
                        response = db.deleteFamilyMemberAlt(family_query, new_value_query, str(ctx.author))
                        await ctx.send(response)
                        user_update = {'$set' : {'FAMILY': str(kid_profile['DISNAME'])}}
                        user_query = {'DID' : kid_profile['DID']}
                        user_update = db.updateUserNoFilter(user_query, user_update)
                    except:
                        print("Team not created. ")
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
                return 
        else:
            await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)

def setup(bot):
    bot.add_cog(Family(bot))