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
from discord_slash import cog_ext, SlashContext
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

emojis = ['👍', '👎']

class Teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Teams Cog is ready!')

    async def cog_check(self, ctx):
        return await main.validate_user(ctx)

    @cog_ext.cog_slash(description="Create a new guild", guild_ids=main.guild_ids)
    async def createguild(self, ctx, guild: str):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        user = db.queryUser({'DID': str(ctx.author.id)})
        if user['LEVEL'] < 4:
            await ctx.send(f"🔓 Unlock Guilds by completing Floor 3 of the 🌑 Abyss! Use /solo to enter the abyss.")
            return
        team_name = guild.lower()
        team_display_name = guild
        transaction_message = f"{user['DISNAME']} has joined the guild."

        
        team_exists = db.queryTeam({'TEAM_NAME': guild.lower()})
        if team_exists:
            await ctx.send(f"{guild} already exists.")
            return


        team_query = {
            'OWNER': str(ctx.author), 
            'TEAM_NAME': team_name, 
            'TEAM_DISPLAY_NAME': team_display_name, 
            'MEMBERS': [str(ctx.author)],
            'TRANSACTIONS': [transaction_message],
            'BANK': 0
            }

        team_buttons = [
            manage_components.create_button(
                style=ButtonStyle.blue,
                label="Create",
                custom_id="Yes"
            ),
            manage_components.create_button(
                style=ButtonStyle.red,
                label="Cancel",
                custom_id="No"
            )
        ]
        team_buttons_action_row = manage_components.create_actionrow(*team_buttons)
        msg = await ctx.send(f"Create the Guild **{team_display_name}**?".format(self), components=[team_buttons_action_row])


        def check(button_ctx):
            return button_ctx.author == ctx.author

        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[team_buttons_action_row], check=check)

            if button_ctx.custom_id == "No":
                await msg.delete()
                return
            
            if button_ctx.custom_id == "Yes":
                server_query = {'GNAME': str(ctx.author.guild)}
                server_update_query = {
                    '$addToSet': {'SERVER_GUILDS': str(guild)}
                }
                r = db.updateServer(server_query, server_update_query)
                response = db.createTeam(data.newTeam(team_query), str(ctx.author.id))
                await button_ctx.send(response)
                await msg.delete()
        except:
            await ctx.send("Guild already exists")
    
    @cog_ext.cog_slash(description="Recruit New Guild Members", guild_ids=main.guild_ids)
    async def recruit(self, ctx, player: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        owner_profile = db.queryUser({'DID': str(ctx.author.id)})
        team_profile = db.queryTeam({'TEAM_NAME': owner_profile['TEAM'].lower()})
        if owner_profile['LEVEL'] < 4:
            await ctx.send(f"🔓 Unlock Guilds by completing Floor 3 of the 🌑 Abyss! Use /solo to enter the abyss.")
            return


        if owner_profile['TEAM'] == 'PCG':
            await ctx.send(m.USER_NOT_ON_TEAM, delete_after=5)
        else:

            if owner_profile['DISNAME'] == team_profile['OWNER'] or owner_profile['DISNAME'] in team_profile['OFFICERS']:

                member_profile = db.queryUser({'DID': str(player.id)})
                if member_profile['LEVEL'] < 4:
                    await ctx.send(f"🔓 {player.mention} has not unlocked Guilds!. Complete Floor 3 of the 🌑 Abyss! Use /solo to enter the abyss.")
                    return

                # If user is part of a team you cannot add them to your team
                if member_profile['TEAM'] == 'PCG':
                    await main.DM(ctx, player, f"{ctx.author}" + f" has invited you to join **{team_profile['TEAM_DISPLAY_NAME']}** !" + f" React in server to join **{team_profile['TEAM_DISPLAY_NAME']}**" )

                    team_buttons = [
                        manage_components.create_button(
                            style=ButtonStyle.blue,
                            label="Join",
                            custom_id="Yes"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.red,
                            label="Don't Join",
                            custom_id="No"
                        )
                    ]
                    team_buttons_action_row = manage_components.create_actionrow(*team_buttons)
                    transaction_message = f"{member_profile['DISNAME']} was recruited."
                    await ctx.send(f"{player.mention}" +f" do you want to join Guild **{team_profile['TEAM_NAME']}**?".format(self), components=[team_buttons_action_row])

                    def check(button_ctx):
                        return str(button_ctx.author) == str(player)

                    try:
                        button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[team_buttons_action_row], check=check)
                        
                        if button_ctx.custom_id == "No":
                            await button_ctx.send("Member not added.")
                            return

                        if button_ctx.custom_id == "Yes":
                            team_query = {'TEAM_NAME': team_profile['TEAM_NAME']}
                            new_value_query = {
                                '$push': {'MEMBERS': str(player)},
                                '$inc': {'MEMBER_COUNT': 1},
                                '$addToSet': {'TRANSACTIONS': transaction_message}
                                }
                            response = db.addTeamMember(team_query, new_value_query, owner_profile['DISNAME'], member_profile['DISNAME'])
                            await button_ctx.send(response)
                    except:
                        await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)
                else:
                    await ctx.send(m.USER_ALREADY_ON_TEAM, delete_after=5)

            else:
                await ctx.send("Recruiting can only be done by Owners and Officers.", delete_after=5)

    async def apply(self, ctx, owner: User):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        owner_profile = db.queryUser({'DID': str(owner.id)})
        team_profile = db.queryTeam({'TEAM_NAME': owner_profile['TEAM'].lower()})

        if owner_profile['TEAM'] == 'PCG':
            await ctx.send(m.USER_NOT_ON_TEAM, delete_after=5)
        else:

            if owner_profile['DISNAME'] == team_profile['OWNER'] or owner_profile['DISNAME'] in team_profile['OFFICERS'] or owner_profile['DISNAME'] in team_profile['CAPTAINS'] :
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
                    transaction_message = f"{member_profile['DISNAME']} has joined the guild."
                    msg = await ctx.send(f"{ctx.author.mention}  applies to join **{team_profile['TEAM_DISPLAY_NAME']}**. Owner, Officers, or Captains - Please accept or Deny".format(self), components=[team_buttons_action_row])

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
                            new_value_query = {
                                '$push': {'MEMBERS': member_profile['DISNAME']},
                                '$addToSet': {'TRANSACTIONS': transaction_message}
                                }
                            response = db.addTeamMember(team_query, new_value_query, owner_profile['DISNAME'], member_profile['DISNAME'])
                            await button_ctx.send(response)
                    except:
                        await msg.delete()
            else:
                await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)
    
    async def leaveguild(self, ctx):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        member_profile = db.queryUser({'DID': str(ctx.author.id)})
        team_profile = db.queryTeam({'TEAM_NAME': member_profile['TEAM'].lower()})
        
        if team_profile:
            team_display_name = team_profile['TEAM_DISPLAY_NAME']
            team_name = team_profile['TEAM_NAME'].lower()
            transaction_message = f"{member_profile['DISNAME']} has left the guild."

            team_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Leave",
                    custom_id="Yes"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="Stay",
                    custom_id="No"
                )
            ]
            team_buttons_action_row = manage_components.create_actionrow(*team_buttons)
            msg = await ctx.send(f"Leave guild **{team_display_name}**?".format(self), components=[team_buttons_action_row])

            def check(button_ctx):
                return button_ctx.author == ctx.author

            try:
                button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[team_buttons_action_row], check=check)

                if button_ctx.custom_id == "No":
                    await msg.delete()
                    return
                
                if button_ctx.custom_id == "Yes":
                    team_query = {'TEAM_NAME': team_name}
                    new_value_query = {
                        '$pull': {
                            'MEMBERS': member_profile['DISNAME'],
                            'OFFICERS': member_profile['DISNAME'],
                            'CAPTAINS': member_profile['DISNAME'],
                        },
                        '$addToSet': {'TRANSACTIONS': transaction_message},
                        '$inc': {'MEMBER_COUNT': -1}
                        }
                    response = db.deleteTeamMember(team_query, new_value_query, str(ctx.author.id))
                    await ctx.send(response)
                    await msg.delete()
            except:
                print("Guild not Left. ")
        else:
            await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)

    @cog_ext.cog_slash(description="Delete a guild", guild_ids=main.guild_ids)
    async def disbandguild(self, ctx, guild = None):
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        if guild:
            team_name = guild.lower()
            team_query = {'TEAM_NAME': team_name}
            team = db.queryTeam(team_query)
            team_display_name = team['TEAM_DISPLAY_NAME']
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
            team_name = team['TEAM_NAME']
            team_display_name = team['TEAM_DISPLAY_NAME']
            
            # ASSOCIATION CHECK
            guildname = team['GUILD']
            if guildname != 'PCG':
                guildteam=True

            if team['OWNER'] == user['DISNAME']:
                team_buttons = [
                    manage_components.create_button(
                        style=ButtonStyle.blue,
                        label="Delete",
                        custom_id="Yes"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.red,
                        label="Cancel",
                        custom_id="No"
                    )
                ]
                team_buttons_action_row = manage_components.create_actionrow(*team_buttons)

                msg = await ctx.send(f"Delete Guild **{team_display_name}**?".format(self), components=[team_buttons_action_row])

                def check(button_ctx):
                    return button_ctx.author == ctx.author

                try:
                    button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=[team_buttons_action_row], check=check)

                    if button_ctx.custom_id == "No":
                        await msg.delete()
                        return

                    if button_ctx.custom_id == "Yes":
                        response = db.deleteTeam(team, str(ctx.author.id))
                        user_query = {'DID': str(ctx.author.id)}
                        new_value = {'$set': {'TEAM': 'PCG'}}
                        db.updateUserNoFilter(user_query, new_value)
                        await button_ctx.send(response)
                        if guildteam:
                            # ASSOCIATION CHECK
                            guild_query = {'GNAME' : str(guildname)}
                            guild_info = db.queryGuildAlt(guild_query)
                            new_query = {'FOUNDER' : str(guild_info['FOUNDER'])}
                            if guild_info:
                                pull_team = {'$pull' : {'SWORDS' : str(team_name)}}
                                response2 = db.deleteGuildSword(new_query, pull_team, str(guild_info['FOUNDER']), str(team_name))
                                await button_ctx.send(response2)
                except Exception as e:
                    print(e)
            else:
                await ctx.send("Only the owner of the Guild can delete the Guild. ")
        else:
            await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)

def setup(bot):
    bot.add_cog(Teams(bot))

    