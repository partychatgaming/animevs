import crown_utilities
import db
import classes as data
import messages as m
import numpy as np
import help_commands as h
from PIL import Image, ImageFont, ImageDraw
import requests
from collections import ChainMap
from interactions import User
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
import uuid
emojis = ['👍', '👎']

class Teams(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Teams Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Create a new guild", options=[
        SlashCommandOption(
            name="guild",
            description="Name of the guild",
            type=OptionType.STRING,
            required=True
        )
    ])
    async def createguild(self, ctx, guild: str):
        _uuid = uuid.uuid4()
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        user = db.queryUser({'DID': str(ctx.author.id)})
        # if user['LEVEL'] < 20:
        #     await ctx.send(f"🔓 Unlock Guild Creation by completing Floor 20 of the 🌑 Abyss! Use /solo to enter the abyss.")
        #     return

        team_name = guild.lower()
        team_display_name = guild
        transaction_message = f"🆕 {user['DISNAME']} has joined the guild."

        
        team_exists = db.queryTeam({'TEAM_NAME': guild.lower()})
        if team_exists:
            await ctx.send(content=f"**{guild}** already exists.", ephemeral=True)
            return


        team_query = {
            'OWNER': str(ctx.author.id), 
            'TEAM_NAME': team_name, 
            'TEAM_DISPLAY_NAME': team_display_name, 
            'MEMBERS': [str(ctx.author.id)],
            'TRANSACTIONS': [transaction_message],
            'BANK': 0,
            'DID': str(ctx.author.id),
            }

        team_buttons = [
            Button(
                style=ButtonStyle.BLUE,
                label="Create",
                custom_id=f"{_uuid}|yes"
            ),
            Button(
                style=ButtonStyle.RED,
                label="Cancel",
                custom_id=f"{_uuid}|no"
            )
        ]
        
        team_buttons_action_row = ActionRow(*team_buttons)
        embed = Embed(title="Guild Creation in Progress", description=f"Would you like to create the Guild, **{team_display_name}**?".format(self), color=0x00ff00)
        msg = await ctx.send(embed=embed, components=[team_buttons_action_row])


        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author
        try:
            button_ctx  = await self.bot.wait_for_component(components=[team_buttons_action_row, team_buttons], timeout=300, check=check)

            if button_ctx.ctx.custom_id == f"{_uuid}|no":
                embed = Embed(title="Guild Creation Cancelled", description=f"Guild creation for **{team_display_name}** has been cancelled.".format(self), color=0x00ff00)
                await msg.edit(embed=embed, components=[])
                return
            
            if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                response = db.createTeam(data.newTeam(team_query), str(ctx.author.id))
                embed = Embed(title="Guild Created", description=f"Guild **{team_display_name}** has been created.".format(self), color=0x00ff00)
                await msg.edit(embed=embed, components=[])
                return
        except:
            emdbed = Embed(title="Guild Creation Cancelled", description=f"Guild creation for **{team_display_name}** has been cancelled as the guild name already exists.".format(self), color=0x00ff00)
            await ctx.send(embed=embed, components=[])
            return
    
    
    @slash_command(description="Recruit New Guild Members", options=[
        SlashCommandOption(
            name="player",
            description="Player to recruit",
            type=OptionType.USER,
            required=True
        )
    ])
    async def recruit(self, ctx, player):
        """
        Recruiting a player to your guild
        The team_profile is your guild's profile
        The individual making the command is the guild_owner
        The player is the individual you are inviting to the guild
        """
        _uuid = uuid.uuid4()
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        guild_owner = crown_utilities.create_player_from_data(registered_player)

        team_profile = db.queryTeam({'TEAM_NAME': guild_owner.guild.lower()})

        if guild_owner.guild == 'PCG':
            embed = Embed(title="Guild Recruitment", description=f"You are not part of a guild.".format(self), color=0x00ff00)
            await ctx.send(embed=embed)
            return  

        else:
            if guild_owner.did == team_profile['OWNER'] or guild_owner.did in team_profile['OFFICERS']:
                joining_member_profile = crown_utilities.create_player_from_data(db.queryUser({'DID': str(player.id)}))

                if joining_member_profile.guild == 'PCG':
                    team_buttons = [
                        Button(
                            style=ButtonStyle.BLUE,
                            label="Join",
                            custom_id=f"{_uuid}|yes"
                        ),
                        Button(
                            style=ButtonStyle.RED,
                            label="Don't Join",
                            custom_id=f"{_uuid}|no"
                        )
                    ]
                    team_buttons_action_row = ActionRow(*team_buttons)
                    transaction_message = f"{player.mention} was recruited."

                    embed = Embed(title="Guild Recruitment", description=f"{player.mention}" +f" do you want to join Guild **{team_profile['TEAM_DISPLAY_NAME']}**?".format(self), color=0x00ff00)
                    msg = await ctx.send(embed=embed, components=[team_buttons_action_row])

                    def check(component: Button):
                        return str(component.ctx.author.id) == str(joining_member_profile.did)

                    try:
                        button_ctx  = await self.bot.wait_for_component(components=[team_buttons_action_row, team_buttons], timeout=120, check=check)
                        
                        if button_ctx.ctx.custom_id == f"{_uuid}|no":
                            embed = Embed(title="Guild Recruitment", description=f"{player.mention}" +f" has declined to join Guild **{team_profile['TEAM_DISPLAY_NAME']}**.".format(self), color=0x00ff00)
                            await msg.edit(embed=embed, components=[])
                            return

                        if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                            team_query = {'TEAM_NAME': team_profile['TEAM_NAME']}
                            new_value_query = {
                                '$push': {'MEMBERS': str(player.id)},
                                '$inc': {'MEMBER_COUNT': 1},
                                '$addToSet': {'TRANSACTIONS': transaction_message}
                                }
                            response = db.addTeamMember(team_query, new_value_query, guild_owner.did, team_profile['TEAM_DISPLAY_NAME'], str(player.id))
                            embed = Embed(title="Guild Recruitment", description=f"{player.mention}" +f" has joined Guild **{team_profile['TEAM_DISPLAY_NAME']}**.".format(self), color=0x00ff00)
                            await msg.edit(embed=embed, components=[])
                            return
                    except:
                        await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)
                        return
                else:
                    await ctx.send(m.USER_ALREADY_ON_TEAM, delete_after=5)
                    return

            else:
                await ctx.send("Recruiting can only be done by Owners and Officers.", delete_after=5)


    @slash_command(description="Leave your guild")
    async def leaveguild(self, ctx):
        await ctx.defer()
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        _uuid = uuid.uuid4()
        member_profile = crown_utilities.create_player_from_data(registered_player)
        team_profile = db.queryTeam({'TEAM_NAME': member_profile.guild.lower()})
        
        if team_profile:
            if ctx.author.id == team_profile['DID']:
                await ctx.send("Owners and Founders can only disband the guild using /disband, not leave it.")
                return

            team_display_name = team_profile['TEAM_DISPLAY_NAME']
            team_name = team_profile['TEAM_NAME'].lower()
            transaction_message = f"{member_profile.disname} has left the guild."

            team_buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="Leave",
                    custom_id=f"{_uuid}|yes"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="Stay",
                    custom_id=f"{_uuid}|no"
                )
            ]
            team_buttons_action_row = ActionRow(*team_buttons)
            embed = Embed(title="Guild Departure", description=f"{ctx.author.mention}" +f" are you sure you want to leave Guild **{team_display_name}**?".format(self), color=0x00ff00)
            msg = await ctx.send(embeds=[embed], components=[team_buttons_action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.bot.wait_for_component(components=[team_buttons_action_row, team_buttons], timeout=300, check=check)

                if button_ctx.ctx.custom_id == f"{_uuid}|no":
                    embed = Embed(title="Guild Departure", description=f"{ctx.author.mention}" +f" you have decided to stay in the guild.".format(self), color=0x00ff00)
                    await msg.edit(embeds=[embed], components=[])
                    return
                
                if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                    team_query = {'TEAM_NAME': team_name}
                    new_value_query = {
                        '$pull': {
                            'MEMBERS': member_profile.did,
                            'OFFICERS': member_profile.did,
                            'CAPTAINS': member_profile.did,
                        },
                        '$addToSet': {'TRANSACTIONS': transaction_message},
                        '$inc': {'MEMBER_COUNT': -1}
                        }
                    response = db.deleteTeamMember(team_query, new_value_query, member_profile.did)
                    embed = Embed(title="Guild Departure", description=f"{ctx.author.mention}" +f" you have left Guild **{team_display_name}**.".format(self), color=0x00ff00)
                    await msg.edit(embeds=[embed], components=[])
            except:
                await msg.edit(content="Response not detected.", components=[])
        else:
            await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)


    @slash_command(description="Delete a guild")
    async def disbandguild(self, ctx):
        """
        Delete your guild as the owner
        """
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return

        _uuid = uuid.uuid4()

        user = crown_utilities.create_player_from_data(registered_player)
        team = db.queryTeam({'TEAM_NAME': user.guild.lower()})
        if team != "PCG":
            team_name = team['TEAM_NAME']
            team_display_name = team['TEAM_DISPLAY_NAME']
        else:
            embed = Embed(title="Guild Recruitment", description=f"{ctx.author.mention}" +f" you are not a part of a guild.".format(self), color=0x00ff00)
            await ctx.send(embed=embed)
            return
        
        if team['OWNER'] != user['DISNAME']:
            embed = Embed(title="Guild Disbandment", description=f"{ctx.author.mention}" +f" you are not the owner of this guild.".format(self), color=0x00ff00)
            await ctx.send(embed=embed)
            return

        if team:
            team_name = team['TEAM_NAME']
            team_display_name = team['TEAM_DISPLAY_NAME']


            if team['OWNER'] == user.did:
                team_buttons = [
                    Button(
                        style=ButtonStyle.BLUE,
                        label="Disband",
                        custom_id=f"{_uuid}|yes"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="Cancel",
                        custom_id=f"{_uuid}|no"
                    )
                ]
                team_buttons_action_row = ActionRow(*team_buttons)

                embed = Embed(title="Guild Disbandment", description=f"{ctx.author.mention}" +f" are you sure you want to disband Guild **{team_display_name}**?".format(self), color=0x00ff00)
                msg = await ctx.send(embed=embed, components=[team_buttons_action_row, team_buttons])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx  = await self.bot.wait_for_component(components=[team_buttons_action_row, team_buttons], timeout=120, check=check)

                    if button_ctx.ctx.custom_id == "No":
                        embed = Embed(title="Guild Disbandment", description=f"{ctx.author.mention}" +f" you have decided to keep your guild.".format(self), color=0x00ff00)
                        await msg.edit(embed=embed, components=[])
                        return

                    if button_ctx.custom_id == "Yes":
                        response = db.deleteTeam(team, str(ctx.author.id))
                        embed = Embed(title="Guild Disbandment", description=f"{ctx.author.mention}" +f" you have disbanded your guild.".format(self), color=0x00ff00)
                        await msg.edit(embed=embed, components=[])
                        return
                except Exception as e:
                    embed = Embed(title="Guild Disbandment", description=f"{ctx.author.mention}" +f" you have not responded in time.".format(self), color=0x00ff00)
                    await msg.edit(embed=embed, components=[])
                    return
            else:
                await ctx.send("Only the owner of the Guild can delete the Guild. ")
        else:
            await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)

def setup(bot):
    Teams(bot)

    