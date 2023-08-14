import crown_utilities
import db
import dataclasses as data
import messages as m
import numpy as np
import help_commands as h
# Converters
from PIL import Image, ImageFont, ImageDraw
import requests
from collections import ChainMap
import asyncio
import textwrap
from interactions import User
from .classes.custom_paginator import CustomPaginator
from interactions.ext.paginators import Paginator
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension


emojis = ['👍', '👎']

class Family(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Family Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    # @slash_command(description="Marry a player")
    async def marry(self, ctx, player: User):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
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
                    Button(
                        style=ButtonStyle.GREEN,
                        label="Propose!",
                        custom_id="yes"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = ActionRow(*trade_buttons)
                await ctx.send(f"Do you want to propose to **{player.mention}**?", components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                            await button_ctx.send("No **Proposal**")
                            self.stop = True
                            return
                    if button_ctx.custom_id == "yes":
                        await self.bot.DM(ctx, player, f"{ctx.author.mention}" + f" proposed to you !" + f" React in server to join their family" )
                        trade_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Lets Get Married!",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.RED,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        trade_buttons_action_row = ActionRow(*trade_buttons)
                        await button_ctx.send(f"**{player.mention}** do you accept the proposal?".format(self), components=[trade_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == player

                        
                        try:
                            button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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

    # @slash_command(description="Divorce your partner")
    async def divorce(self, ctx, partner: User):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
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
                    Button(
                        style=ButtonStyle.RED,
                        label="Divorce!",
                        custom_id="yes"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = ActionRow(*trade_buttons)
                await ctx.send(f"Do you want to divorce {partner.mention}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No **Divorce**")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        await self.bot.DM(ctx, partner, f"{ctx.author.mention}" + f"is divorcing you!" + f" You will be removed from the family in 90 seconds" )
                        trade_buttons = [
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Accept! Half of Family Bank",
                                custom_id="yes"
                            ),
                            Button(
                                style=ButtonStyle.RED,
                                label="No",
                                custom_id="no"
                            )
                        ]
                        trade_buttons_action_row = ActionRow(*trade_buttons)
                        await button_ctx.send(f"{partner.mention} do you accept the divorce? You will gain half the family bank 🪙**{'{:,}'.format(divorce_split)}**.\n*{family_profile['PARTNER']} will be automatically removed from the family in 90 seconds*".format(self), components=[trade_buttons_action_row])
                        
                        def check(button_ctx):
                            return button_ctx.author == partner

                        
                        try:
                            button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=90, check=check)
                            if button_ctx.custom_id == "no":
                                await button_ctx.send("No **Divorce**")
                                self.stop = True
                            if button_ctx.custom_id == "yes":
                                try:
                                    if str(partner) == family_profile['PARTNER']:
                                        await button_ctx.send(f"**Divorce Finalized** {partner.mention} earned 🪙**{'{:,}'.format(divorce_split)}**")
                                    else:
                                        await button_ctx.send(f"**Divorce Finalized** {ctx.author.mention} earned 🪙**{'{:,}'.format(divorce_split)}**")
                                    
                                    new_value_query = {'$set': {'PARTNER': '' }}
                                    await self.bot.cursefamily(divorce_split,family_profile['HEAD'])
                                    response = db.deleteFamilyMember(family_query, new_value_query, str(ctx.author), str(partner))
                                    if str(ctx.author) == family_profile['PARTNER']:
                                        family_query = {'HEAD': str(partner)}
                                        response = db.deleteFamilyMember(family_query, new_value_query, str(partner), str(ctx.author))
                                        user_query = {'DISNAME':str(partner)}
                                        user_info = db.queryUser(user_query)
                                        old_family = db.updateUserNoFilter({'FAMILY':user_info['DISNAME']})
                                    await button_ctx.send(response)
                                    await self.bot.bless(divorce_split, str(family_profile['PARTNER']))
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
                            await self.bot.cursefamily(divorce_split,family_profile['HEAD'])
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

    # @slash_command(description="Adopt a kid")
    async def adopt(self, ctx, player: User):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
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
                    if kids == kid_profile['DISNAME']:
                        await ctx.send("Member already in family")
                        return
                if kid_count >= 2:
                    await ctx.send(m.MAX_CHILDREN, delete_after=3)
                    return

                trade_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="Adopt!",
                        custom_id="yes"
                    ),
                    Button(
                        style=ButtonStyle.BLUE,
                        label="No",
                        custom_id="no"
                    )
                ]
                trade_buttons_action_row = ActionRow(*trade_buttons)
                await ctx.send(f"Do you want to adopt {player.mention}?".format(self), components=[trade_buttons_action_row])
                
                def check(button_ctx):
                    return button_ctx.author == ctx.author

                
                try:
                    button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
                    if button_ctx.custom_id == "no":
                        await button_ctx.send("No **Adoption**")
                        self.stop = True
                        return
                    if button_ctx.custom_id == "yes":
                        try:
                            await self.bot.DM(ctx, player, f"{ctx.author.mention}" + f" would like to adopt you!" + f" React in server to join their **Family**" )
                            trade_buttons = [
                                Button(
                                    style=ButtonStyle.GREEN,
                                    label="Join Family!",
                                    custom_id="yes"
                                ),
                                Button(
                                    style=ButtonStyle.BLUE,
                                    label="No",
                                    custom_id="no"
                                )
                            ]
                            trade_buttons_action_row = ActionRow(*trade_buttons)
                            await button_ctx.send(f"{player.mention}" +f" would you like to be adopted ?".format(self), components=[trade_buttons_action_row])
                            
                            def check(button_ctx):
                                return button_ctx.author == player

                            
                            try:
                                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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

    # @slash_command(description="Disown your kid")
    async def disown(self, ctx, kid: User):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
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
                        Button(
                            style=ButtonStyle.RED,
                            label="Disown!",
                            custom_id="yes"
                        ),
                        Button(
                            style=ButtonStyle.BLUE,
                            label="No",
                            custom_id="no"
                        )
                    ]
                    trade_buttons_action_row = ActionRow(*trade_buttons)
                    await ctx.send(f"Do you want to disown {kid.mention}?".format(self), components=[trade_buttons_action_row])
                    
                    def check(button_ctx):
                        return button_ctx.author == ctx.author

                    
                    try:
                        button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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

    # @slash_command(description="Leave your adopted family")
    async def leavefamily(self, ctx):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
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
                Button(
                    style=ButtonStyle.RED,
                    label="Leave Family!",
                    custom_id="yes"
                ),
                Button(
                    style=ButtonStyle.BLUE,
                    label="No",
                    custom_id="no"
                )
            ]
            trade_buttons_action_row = ActionRow(*trade_buttons)
            await ctx.send(f"Do you want to **Leave** your family?".format(self), components=[trade_buttons_action_row])
            
            def check(button_ctx):
                return button_ctx.author == ctx.author

            
            try:
                button_ctx  = await self.bot.wait_for_component(components=[trade_buttons_action_row], timeout=120, check=check)
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

    # @slash_command(description="Lookup player family", options=[
    #     SlashCommandOption(
    #         name="player",
    #         description="Player to lookup",
    #         type=OptionType.USER,
    #         required=False
    #     )
    # ])
    async def family(self, ctx, player = None):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        ctx_user = db.queryUser({'DID': str(ctx.author.id)})
        """
        Search for family using DID in either HEAD, PARTNER, or in KIDS array
        The name of the family, if not explicitly stated in new family Field, will be the name of the head of household
        """
        try:                
            if player:
                member = player
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
                icon = "🪙"
                if savings >= 500000000:
                    icon = "💸"
                elif savings >=100000000:
                    icon = "💰"
                elif savings >= 50000000:
                    icon = "💵"

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
                summon_name = summon_object['NAME']
                summon_ability_power = None
                for key in summon_object:
                    if key not in ["NAME", "LVL", "EXP", "TYPE", "BOND", "BONDEXP", "PATH"]:
                        summon_ability_power = summon_object[key]
                summon_ability = list(summon_object.keys())[3]
                summon_type = summon_object['TYPE']
                summon_lvl = summon_object['LVL']
                summon_exp = summon_object['EXP']
                summon_bond = summon_object['BOND']
                summon_bond_exp = summon_object['BONDEXP']
                bond_req = ((summon_ability_power * 5) * (summon_bond + 1))
                lvl_req = int(summon_lvl) * 10

                lvl_message = f"*{summon_exp}/{lvl_req}*"
                bond_message = f"*{summon_bond_exp}/{bond_req}*"
                
                power = (summon_bond * summon_lvl) + int(summon_ability_power)
                summon_path = summon_object['PATH']
                summon_info = {'NAME': summon_name, 'LVL': summon_lvl, 'EXP': summon_exp, summon_ability: summon_ability_power, 'TYPE': summon_type, 'BOND': summon_bond, 'BONDEXP': summon_bond_exp, 'PATH': summon_path}
                summon_file = crown_utilities.showsummon(summon_path, summon_name, crown_utilities.element_mapping[summon_type], summon_lvl, summon_bond)

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
                
                
                kids_names = ", ".join(f'{k}'.format(self) for k in kid_list)
                # if summon_data:
                #     await ctx.send({summon_data})
                    
                first_page = Embed(title=f"👨‍👩‍👧‍👦 | {family_name}", description=textwrap.dedent(f"""
                🧠 **Head of Household** 
                {head_name.split("#",1)[0]}

                🫀 **Partner**
                {partner_name_adjusted}

                👶 **Kids**
                {kids_names}

                🏦**Savings** 
                {icon} {'{:,}'.format(savings)}
                
                🏠**Primary Residence**
                {house_info['HOUSE']} - 〽️**{house_info['MULT']}x** 🪙 per match!
                """), color=0x7289da)
                first_page.set_image(url=house_img)
                
                estates_page = Embed(title=f"Real Estate", description=textwrap.dedent(f"""
                🌇 **Properties**
                {estates_list_joined}
               
                """), color=0x7289da)

                
                activity_page = Embed(title="Recent Family Activity", description=textwrap.dedent(f"""
                {transactions_embed}
                """), color=0x7289da)
                
                summon_page = Embed(title="Family Summon", description=textwrap.dedent(f"""
                🧬**{summon_name}**
                _Bond_ **{summon_bond}** | {bond_message}
                _Level_ **{summon_lvl}** | {lvl_message}
                {crown_utilities.set_emoji(summon_type)} **{summon_type.capitalize()}** | {summon_ability} ~ **{power}**
                :sunny:  : **{crown_utilities.element_mapping[summon_type]}**
                """), color=0x7289da)
                summon_page.set_image(url=summon_path)
                
                
                
                
                
                family_explanations = Embed(title=f"Information", description=textwrap.dedent(f"""
                **Family Explanations**
                - **Earnings**: Families earn coin for every completed battle by its members
                - **Allowance**: Disperse Family Savings to a family member
                - **Invest**: Invest money into Family Bank
                - **Houses**: Give Coin Multipliers in all game modes towards Family Earnings
                - **Home Universe**: Earn Extra gold in Home Universe,
                - **Real Estate**: Own multiple houses, swap your current house buy and sell real estate
                - **Family Summon**: Each family member has access and can equip the family summon 
                - **Summon XP Boost**: The Family Summon gains an additional 100 AP and gains 2x XP and 5x Bond EXP
                

                **Family Position Explanations**
                - **Head of Household**:  All operations.
                - **Partner**:  Can equip/update family summon, change equipped house and give allowances
                - **Kids**:  Can equip family summon.
                """), color=0x7289da)

                embed_list = [first_page, estates_page, summon_page, activity_page, family_explanations]

                buttons = []
                
                if not member:
                    buttons.append(
                        Button(style=3, label="Say Hello", custom_id="hello")
                    )
                    
                if is_head:
                    buttons = [
                        Button(style=3, label="Check/Purchase Properties", custom_id="property"),
                        Button(style=3, label="Equip/Set Family Summon", custom_id="summon"),
                    ]
                elif is_partner:
                    buttons = [
                        Button(style=3, label="Check Properties", custom_id="property"),
                        Button(style=3, label="Equip/Set Family Summon", custom_id="summon"),
                    ]
                    
                elif is_kid:
                    buttons = [
                        Button(style=3, label="View Properties", custom_id="property"),
                        Button(style=3, label="Equip Family Summon", custom_id="summon"),
                    ]
                    
                custom_action_row = ActionRow(*buttons)
                
                async def custom_function(self, button_ctx):
                    try:
                        if button_ctx.author == ctx.author:
                            if button_ctx.custom_id == "hello":
                                await button_ctx.defer(ignore=True)
                                update_query = {
                                        '$push': {'TRANSACTIONS': f"{button_ctx.author} said 'Hello'!"}
                                    }
                                response = db.updateFamily({'HEAD': family['HEAD']}, update_query)
                                await ctx.send(f"**{button_ctx.author.mention}** Said Hello! to {family_name}!")
                                self.stop = True
                                return
                            elif button_ctx.custom_id == "property":
                                await button_ctx.defer(ignore=True)
                                real_estate_message = " "
                                property_buttons = []
                                balance_message = '{:,}'.format(savings)
                                if is_head:
                                    real_estate_message = "\nWelcome Head of Household!\n**View Property** - View Owned Properties or make a Move!\n**Buy New Home** - Buy a new Home for your Family\n**Browse Housing Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    Button(style=2, label="Owned Properties", custom_id="equip"),
                                    Button(style=3, label="Buy/Sell Houses", custom_id="buy"),
                                    Button(style=1, label="Browse Housing Catalog", custom_id="browse"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                    
                                ]
                                if is_partner:
                                    real_estate_message = "\nWelcome Partner!\n**View Property** - View Owned Properties or make a Move!\n**Browse Housing Catalog** - View all Properties for sale"
                                    property_buttons = [
                                    Button(style=1, label="Owned Properties", custom_id="equip"),
                                    Button(style=1, label="Browse Housing Catalog", custom_id="browse"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                ]
                                if is_kid:
                                    real_estate_message = "\nWelcome Kids!\n**View Property** - View Owned Properties"
                                    property_buttons = [
                                    Button(style=1, label="View Properties", custom_id="view"),
                                    Button(style=ButtonStyle.RED, label="Quit", custom_id="q")
                                ]
                                property_action_row = ActionRow(*property_buttons)
                                real_estate_screen = Embed(title=f"Anime VS+ Real Estate", description=textwrap.dedent(f"""\
                                {real_estate_message}
                                *Current Savings*: 
                                🪙 **{balance_message}**
                                """), color=0xe74c3c)
                                real_estate_screen.set_image(url="https://thumbs.gfycat.com/FormalBlankGeese-max-1mb.gif")
                                
                                msg = await ctx.send(embed=real_estate_screen, components=[property_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                try:
                                    house_embed_list = []
                                    button_ctx  = await self.bot.wait_for_component(components=[property_action_row], timeout=120, check=check)
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
                                            embedVar = Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            💰 **Price**: {price_message}
                                            〽️ **Multiplier**: {house_multiplier}
                                            Family earns **{house_multiplier}x** 🪙 per match!
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
                                            embedVar = Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            💰 **Price**: {price_message}
                                            〽️ **Multiplier**: {house_multiplier} 
                                            Family earns **{house_multiplier}x** 🪙 per match!
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
                                            embedVar = Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            💰 **Price**: {price_message}
                                            〽️ **Multiplier**: {house_multiplier} 
                                            Family earns **{house_multiplier}x** 🪙 per match!
                                            """))
                                            embedVar.set_image(url=house_img)
                                            house_embed_list.append(embedVar)
                                            
                                        equip_buttons = [
                                            Button(style=3, label="🏠 Equip House", custom_id="equip"),

                                        ]
                                        equip_action_row = ActionRow(*equip_buttons)
                                        async def equip_function(self, button_ctx):
                                            house_name = str(button_ctx.origin_message.embeds[0].title)
                                            await button_ctx.defer(ignore=True)
                                            if button_ctx.author == ctx.author:
                                                if button_ctx.custom_id == "equip":
                                                    transaction_message = f"🏠 | {ctx.author} changed the family house to **{str(button_ctx.origin_message.embeds[0].title)}**."
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
                                            embedVar = Embed(title= f"{house_name}", description=textwrap.dedent(f"""
                                            **Current Savings**: 🪙 **{current_savings}**                                                                    
                                            {ownership_message}
                                            〽️ **Multiplier**: {house_multiplier}
                                            {sell_message}
                                            Family earns **{house_multiplier}x** 🪙 per match!
                                            """))
                                            embedVar.set_image(url=house_img)
                                            house_embed_list.append(embedVar)
                                        
                                        econ_buttons = [
                                            Button(style=3, label="💰 Buy House", custom_id="buy"),
                                            Button(style=3, label="💱 Sell House", custom_id="sell"),

                                        ]
                                        econ_action_row = ActionRow(*econ_buttons)
                                        
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
                                                                    transaction_message = f"🪙 | {ctx.author} bought a new **{str(button_ctx.origin_message.embeds[0].title)}**."
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
                                                        await crown_utilities.blessfamily_Alt(cost, family['HEAD'])
                                                        transaction_message = f"🪙 | {ctx.author} sold the family home: **{str(house_name)}**."
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
                                summon = list(summon_object.values())[0]
                                summon_name = summon_object['NAME']
                                summon_ability_power = list(summon_object.values())[3]
                                summon_ability = list(summon_object.keys())[3]
                                summon_type = summon_object['TYPE']
                                summon_lvl = summon_object['LVL']
                                summon_exp = summon_object['EXP']
                                summon_bond = summon_object['BOND']
                                summon_bond_exp = summon_object['BONDEXP']
                                bond_req = ((summon_ability_power * 5) * (summon_bond + 1))
                                lvl_req = int(summon_lvl) * 10

                                lvl_message = f"*{summon_exp}/{lvl_req}*"
                                bond_message = f"*{summon_bond_exp}/{bond_req}*"
                                
                                power = (summon_bond * summon_lvl) + int(summon_ability_power)
                                summon_path = summon_object['PATH']
                                head_vault = db.queryVault({'DID' : head_data['DID']})
                                
                                summon_buttons = []
                                if is_head:
                                    summon_message = "Welcome Head of Household! Equip or Change Family Summon Here!"
                                    summon_buttons = [
                                    Button(style=2, label="Change Summon", custom_id="change"),
                                    Button(style=3, label="Equip Family Summon", custom_id="equip"),
                                    
                                ]
                                if is_partner:
                                    summon_message = "Welcome Partner! Equip or Change Family Summon Here!"
                                    summon_buttons = [
                                    Button(style=1, label="Change Summon", custom_id="change"),
                                    Button(style=1, label="Equip Family Summon", custom_id="equip"),
                                ]
                                if is_kid:
                                    summon_message = "Welcome Kids! Equip Family Summon Here!"
                                    summon_buttons = [
                                    Button(style=1, label="Equip Family Summon", custom_id="equip"),
                                ]
                                summon_action_row = ActionRow(*summon_buttons)
                                summon_screen = Embed(title=f"Anime VS+ Family", description=textwrap.dedent(f"""\
                                {summon_message}
                                🧬**{summon_name}**
                                _Bond_ **{summon_bond}** | {bond_message}
                                _Level_ **{summon_lvl}** | {lvl_message}
                                {crown_utilities.set_emoji(summon_type)} **{summon_type.capitalize()}** | {summon_ability} ~ **{power}**
                                :sunny:  : **{crown_utilities.element_mapping[summon_type]}**
                                """), color=0xe74c3c)
                                summon_screen.set_image(url=summon_path)
                                
                                msg = await ctx.send(embed=summon_screen, components=[summon_action_row])
                                def check(button_ctx):
                                    return button_ctx.author == ctx.author
                                try:
                                    button_ctx  = await self.bot.wait_for_component(components=[summon_action_row], timeout=120, check=check)
                                    
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
                                                
                                                pet_bond = pet['BOND']
                                                bond_exp = pet['BONDEXP']
                                                pet_level = pet['LVL']
                                                pet_exp = pet['EXP']
                                                
                                                petmove_ap = list(pet.values())[3] 
                                                bond_req = ((petmove_ap * 5) * (pet_bond + 1))
                                                lvl_req = int(pet_level) * 10
                                                if lvl_req <= 0:
                                                    lvl_req = 2
                                                if bond_req <= 0:
                                                    bond_req = 5
                                                
                                                lvl_message = f"*{pet_exp}/{lvl_req}*"
                                                bond_message = f"*{bond_exp}/{bond_req}*"
                                                
                                                pet_ability = list(pet.keys())[3]
                                                pet_ability_power = list(pet.values())[3]
                                                power = (pet['BOND'] * pet['LVL']) + pet_ability_power
                                                can_change_summon = True
                                                bonus_message = ""
                                                if pet['TYPE'] not in ['BARRIER','PARRY']:
                                                    bonus_message = '+100 Family Bonus'
                                                if pet['NAME'] == summon_name:
                                                    can_change_sumon = False
                                                dash_pet_info = db.querySummon({'PET' : pet['NAME']})
                                                if dash_pet_info:
                                                    pet_available = dash_pet_info['AVAILABLE']
                                                    pet_exclusive = dash_pet_info['EXCLUSIVE']
                                                    pet_universe = dash_pet_info['UNIVERSE']
                                                icon = "🧬"
                                                if pet_available and pet_exclusive:
                                                    icon = "🔥"
                                                elif pet_available == False and pet_exclusive ==False:
                                                    icon = ":japanese_ogre:"

                                                embedVar = Embed(title= f"{pet['NAME']}", description=textwrap.dedent(f"""
                                                {icon}
                                                _Bond_ **{pet['BOND']}** | {bond_message}
                                                _Level_ **{pet['LVL']}** | {lvl_message}
                                                {crown_utilities.set_emoji(pet['TYPE'])} *{pet['TYPE'].capitalize()} Ability*
                                                **{pet_ability}:** {power} *{bonus_message}*
                                                """), 
                                                color=0x7289da)
                                                embedVar.set_thumbnail(url=avatar)
                                                #embedVar.set_footer(text=f"{pet['TYPE']}: {crown_utilities.element_mapping[pet['TYPE']]}")
                                                embed_list.append(embedVar)
                                            
                                            buttons = [
                                                Button(style=3, label="Share Summon", custom_id="share"),
                                            ]
                                            custom_action_row = ActionRow(*buttons)

                                            async def custom_function(self, button_ctx):
                                                if button_ctx.author == ctx.author:
                                                    updated_vault = db.queryVault({'DID': d['DID']})
                                                    sell_price = 0
                                                    selected_summon = str(button_ctx.origin_message.embeds[0].title)
                                                    if selected_summon == summon_name:
                                                        await button_ctx.send(f"🧬 **{str(button_ctx.origin_message.embeds[0].title)}** is already the {family_name} **Summon**.")
                                                        return 
                                                    user_query = {'DID': str(ctx.author.id)}
                                                    user_vault = db.queryVault(user_query)

                                                    vault_summons = user_vault['PETS']
                                                    for l in vault_summons:
                                                        if selected_summon == l['NAME']:
                                                            level = l['LVL']
                                                            xp = l['EXP']
                                                            pet_ability = list(l.keys())[3]
                                                            bonus = 0
                                                            if pet_ability not in ['PARRY','BARRIER']:
                                                                bonus = 100
                                                            pet_ability_power = list(l.values())[3] + bonus
                                                            power = (l['BOND'] * l['LVL']) + pet_ability_power + bonus
                                                            pet_info = {'NAME': l['NAME'], 'LVL': l['LVL'], 'EXP': l['EXP'], pet_ability: pet_ability_power, 'TYPE': l['TYPE'], 'BOND': l['BOND'], 'BONDEXP': l['BONDEXP'], 'PATH': l['PATH']}
                                                    if button_ctx.custom_id == "share":
                                                        #update_query = {'$set': {'SUMMON': }}
                                                        #filter_query = [{'type.' + "NAME": str(pet)}]
                                                        #response = db.updateUser(query, update_query, filter_query)
                                                
                                                        transaction_message = f"🧬 | {ctx.author} changed the family summon to **{str(button_ctx.origin_message.embeds[0].title)}**."
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
                                            transaction_message = f"{ctx.author} equipped the family summon : **{str(summon_name)}**."
                                            response = db.updateUserNoFilter({'DID': str(button_ctx.author.id)}, {'$set' : {'PET': summon_name, 'FAMILY_PET': True}})
                                            response2 = db.updateFamily({'HEAD': family['HEAD']}, {'$push': {'TRANSACTIONS': transaction_message}})
                                            await button_ctx.send(f"🧬 **{str(summon_name)}** is now your **Summon**.")
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



# def setup(bot):
#     Family(bot)