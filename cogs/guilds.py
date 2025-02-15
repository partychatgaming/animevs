import crown_utilities
import db
import classes as data
import messages as m
from cogs.quests import Quests
from interactions import ActionRow, Button, ButtonStyle, listen, slash_command, SlashCommandOption, OptionType, Embed, Extension, cooldown, Buckets
import uuid
import asyncio
import logging
from logger import loggy
emojis = ['👍', '👎']

class Teams(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        # print('Teams Cog is ready!')
        loggy.info('Guild Cog is ready')

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
        
        if team['OWNER'] != user['DID']:
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


    @slash_command(name="pay", description="Pay a Guild Member", options=[
    SlashCommandOption(name="player", description="Player to pay", type=OptionType.USER, required=True),
    SlashCommandOption(name="amount", description="Amount to pay", type=OptionType.INTEGER, required=True),
    ], scopes=crown_utilities.guild_ids)
    @cooldown(Buckets.USER, 1, 10)
    async def pay(ctx, player, amount):
        await ctx.defer()
        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            team = db.queryTeam({'TEAM_NAME': user['TEAM'].lower()})
            access = False
            tax = round(.25 * int(amount))

            if user['TEAM'] == 'PCG':
                await ctx.send("You are not a part of a guild.")
                return

            if user['DID'] == team['OWNER']:
                access = True

            if user['DID'] in team['OFFICERS']:
                access = True
            
            if not access:
                await ctx.send("You must be owner or officer of guild to pay members. ")
                return
            
            if str(player.id) not in team['MEMBERS']:
                await ctx.send("You can only pay guild members. ")
                return


            icon = "🪙"
            if int(amount) >= 500000:
                icon = "💸"
            elif int(amount) >=300000:
                icon = "💰"
            elif int(amount) >= 150000:
                icon = "💵"

            taxicon = "🪙"
            if int(amount) >= 500000:
                taxicon = "💸"
            elif int(amount) >=300000:
                taxicon = "💰"
            elif int(amount) >= 150000:
                taxicon = "💵"

            balance = team['BANK']
            payment = round(int(amount) + int(tax))
            different = 0 
            if balance <= payment:
                difference = round(abs(balance - payment))
                embed = Embed(title="Pay", description=f"Your Guild does not have **{icon}{'{:,}'.format(int(payment))}**\n*Taxes & Fees:* **{taxicon}{'{:,}'.format(int(difference))}**")
                await ctx.send(embeds = [embed])
            else:
                await crown_utilities.bless(int(amount), player.id)
                await crown_utilities.curseteam(int(payment), team['TEAM_NAME'])

                embed = Embed(title="Pay", description=f"{icon} **{'{:,}'.format(int(amount))}** has been paid to {player.mention}.\n*Taxes & Fees:* **{taxicon}{'{:,}'.format(int(tax))}**")
                await ctx.send(embeds = [embed])
                transaction_message =f"🪙 | {str(ctx.author)} paid {str(player)} {'{:,}'.format(int(amount))}."
                team_query = {'TEAM_NAME': team['TEAM_NAME']}
                new_value_query = {
                    '$addToSet': {'TRANSACTIONS': transaction_message},
                    }
                db.updateTeam(team_query, new_value_query)
                return
        except Exception as ex:
            loggy.error(f"Error in Pay command: {ex}")
            await ctx.send("Pay Issue Seek support.")
            return



    @slash_command(description="Promote, Demote, or Remove Guild Members", options=[
    SlashCommandOption(
            name="player",
            description="Player to update",
            type=OptionType.USER,
            required=True
    ),

    SlashCommandOption(
            name="operation",
            description="Operation to perform",
            type=OptionType.STRING,
            required=True,
            choices=[
                SlashCommandChoice(
                name="Promote",
                value="Promote"
                ),
                SlashCommandChoice(
                name="Demote",
                value="Demote"
                ),
                SlashCommandChoice(
                name="Remove",
                value="Remove"
                ),

            ]
    )
    ],
    scopes=crown_utilities.guild_ids)
    async def guildoperations(ctx, player, operation: str):
        await ctx.defer()
        try:
            user = crown_utilities.create_player_from_data(db.queryUser({"DID": str(ctx.author.id)}))
            query = {'TEAM_NAME': user.guild.lower()}
            team = db.queryTeam(query)
            team_officers = team['OFFICERS']
            team_captains = team['CAPTAINS']
            team_owner = team['OWNER']
            team_display_name = team['TEAM_DISPLAY_NAME']
            update_message = ""
            transaction_message = ""
            team_query = {}
            access = False
            is_officer = False
            is_captain = False
            is_owner = False

            if user.guild == 'PCG':
                embed = Embed(title="Guild Operations", description="You are not in a guild.")
                await ctx.send(embeds=[embed])
                return

            if str(player.id) not in team['MEMBERS']:
                embed = Embed(title="Guild Operations", description="You can only utilize Guild Controls on Guild members.")
                await ctx.send(embeds=[embed])
                return

            if operation == "Remove":
                await deletemember(ctx, player)
                return

            if user.did == team['OWNER']:
                access = True

            if user.did in team['OFFICERS']:
                access = True
                
            if not access:
                embed = Embed(title="Guild Operations", description="You must be owner or officer of guild to promote members.")
                await ctx.send(embeds=[embed])
                return
            
            if str(player.id) == team_owner:
                embed = Embed(title="Guild Operations", description="Guild Owners can not be promoted.")
                await ctx.send(embeds=[embed])


            if str(player.id) in team_officers:
                is_officer = True
                if operation == "Promote":
                    embed = Embed(title="Guild Operations", description="You can not promote a guild member higher than an Officer position.")
                    await ctx.send(embeds=[embed])
                    return
                elif operation == "Demote":
                    transaction_message =f"⏬ | {str(player)} was demoted to Captain"
                    team_query = {
                    '$pull': {'OFFICERS': str(player.id)},
                    '$push': {'CAPTAINS': str(player.id)},
                    '$addToSet': {'TRANSACTIONS': transaction_message}
                    }
                    update_message =f"{player.mention} has been demoted to a **Captain** of **{team['TEAM_DISPLAY_NAME']}**"


            if str(player.id) in team_captains:
                is_captain = True
                if operation == "Promote":
                    transaction_message =f"⏫ | {str(player)} was promoted to Officer"
                    team_query = {
                    '$pull': {'CAPTAINS': str(player.id)},
                    '$push': {'OFFICERS': str(player.id)},
                    '$addToSet': {'TRANSACTIONS': transaction_message}
                    }
                    update_message =f"{player.mention} has been promoted to an **Officer** of **{team['TEAM_DISPLAY_NAME']}**"
                
                elif operation == "Demote":
                    transaction_message =f"⏬ | {str(player)} was demoted to basic membership"
                    team_query = {
                    '$pull': {'CAPTAINS': str(player.id)},
                    '$addToSet': {'TRANSACTIONS': transaction_message}
                    }
                    update_message =f"{player.mention} has been demoted to a **Member** of **{team['TEAM_DISPLAY_NAME']}**"
                

            if not is_captain and not is_officer and not is_owner:
                if operation == "Promote":
                    transaction_message =f"⏫ | {str(player)} was promoted to Captain"
                    team_query = {
                    '$push': {'CAPTAINS': str(player.id)},
                    '$addToSet': {'TRANSACTIONS': transaction_message}
                    }
                    update_message =f"{player.mention} has been promoted to a **Captain** of **{team['TEAM_DISPLAY_NAME']}**"
                elif operation == "Demote":
                    embed = Embed(title="Guild Operations", description="Guild Members can not be demoted from basic membership.")
                    await ctx.send(embeds=[embed])
                    return
                
            response = db.updateTeam(query, team_query)
            if response:
                await ctx.send(update_message)
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
            loggy.error(f"Error in Guild Operations command: {ex}")
            await ctx.send("Guild Operations Issue Seek support.")
            return

    @slash_command(name="donate", description="Donate money to Guild, Convert 10% as Gems", options=[
    SlashCommandOption(name="amount", description="Amount to donate", type=OptionType.INTEGER, required=True),
    ], scopes=crown_utilities.guild_ids)
    @cooldown(Buckets.USER, 1, 60)
    async def donate(ctx, amount):
        await ctx.defer()
        try:
            user = crown_utilities.create_player_from_data(db.queryUser({"DID": str(ctx.author.id)}))
            equipped_card = crown_utilities.create_card_from_data(db.queryCard({"NAME": user.equipped_card}))
            query = {'TEAM_NAME': str(user.guild.lower())}
            team_data = db.queryTeam(query)
            if not team_data or user.guild == 'PCG':
                embed = Embed(title="Donate to Guild", description="You are not in a guild.")
                await ctx.send(embeds=[embed])
                return
            team_display_name = team_data['TEAM_DISPLAY_NAME']
            team_balance = team_data['BANK']
            guild_amount = round(int(amount) * .90)
            original_amount = amount
            gem_amount = 0
            if team_balance >= 0:
                stars = "⭐"
                rank = "D Rank Guild"
                gem_amount = round(amount * .02)
            if team_balance >= 1000000:
                stars = "⭐⭐"
                rank = "C Rank Guild"
                gem_amount = round(amount * .04)
            if team_balance >= 100000000:
                stars = "⭐⭐⭐"
                rank = "B Rank Guild"
                gem_amount = round(amount * .06)
            if team_balance >= 1000000000:
                stars = "⭐⭐⭐⭐"
                rank = "A Rank Guild"
                gem_amount = round(amount * .08)
            if team_balance >= 100000000000:
                stars = "✨✨✨✨✨"
                rank = "S Rank Guild"
                gem_amount = round(amount * .10)

            if team_data:
                if user.balance <= int(amount):
                    embed = Embed(title="Donate to Guild", description="You do not have that amount to donate.")
                    await ctx.send(embeds=[embed])
                else:
                    await crown_utilities.blessteam(round(int(guild_amount) * .90), team_display_name)
                    await crown_utilities.curse(int(original_amount), ctx.author.id)
                    
                    if user.gems:
                        for universe in user.gems:
                            query = {"DID": str(ctx.author.id)}
                            update_query = {
                                '$inc': {'GEMS.$[type].' + "GEMS": gem_amount}
                            }
                            filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
                            res = await asyncio.to_thread(db.updateUser,query, update_query, filter_query)
                        embed = Embed(title="Donate to Guild", description=f"🪙 {guild_amount:,} has been invested into the {team_display_name} guild. 💎 {gem_amount:,} gems have been added to all of your explored universes.")

                        quest_message = await Quests.milestone_check(user, "DONATION", amount)
                        if quest_message:
                            embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)
                        await ctx.send(embeds = [embed])
                    else:
                        universe_to_add_gems = equipped_card.universe
                        user.save_gems(universe_to_add_gems, gem_amount)
                        embed = Embed(title="Donate to Guild", description=f"🪙 {guild_amount:,} has been invested to the {team_display_name} guild. 💎 {gem_amount:,} gems have been added to {equipped_card.universe} gem count.")
                        await ctx.send(embeds=[embed])
                        return
            else:
                embed = Embed(title="Donate to Guild", description=f"Guild: {team_display_name} does not exist")
                await ctx.send(embeds=[embed])
        except Exception as ex:
            loggy.error(f"Error in Donate command: {ex}")
            await ctx.send("Donate Issue Seek support.")
            return




async def deletemember(ctx, member):
   _uuid = uuid.uuid4()
   owner_profile = crown_utilities.create_player_from_data(db.queryUser({'DID': str(ctx.author.id)}))
   team_profile = db.queryTeam({'TEAM_NAME': owner_profile.guild.lower()})
   
   if team_profile:
      if owner_profile.did == team_profile['OWNER']:  
            team_buttons = [
               Button(
                  style=ButtonStyle.BLUE,
                  label="✔️",
                  custom_id=f"{_uuid}|yes"
               ),
               Button(
                  style=ButtonStyle.RED,
                  label="❌",
                  custom_id=f"{_uuid}|no"
               )
            ]
            transaction_message =f"❌ | {str(member)} was removed from guild."
            team_buttons_action_row = ActionRow(*team_buttons)
            msg = await ctx.send(f"Do you want to remove {member.mention} from the **{team_profile['TEAM_DISPLAY_NAME']}**?".format(bot), components=[team_buttons_action_row])

            def check(component: Button) -> bool:
               return component.ctx.author == ctx.author

            try:
               button_ctx  = await bot.wait_for_component(components=[team_buttons_action_row], timeout=120, check=check)
               
               if button_ctx.ctx.custom_id ==f"{_uuid}|no":
                  embed = Embed(title="Member Not Deleted.", description=f"{member.mention} was not removed from {team_profile['TEAM_DISPLAY_NAME']}", color=0x00ff00)
                  await msg.edit(embed=embed, components=[])
                  return

               if button_ctx.ctx.custom_id ==f"{_uuid}|yes":   
                  team_query = {'TEAM_NAME': team_profile['TEAM_NAME']}
                  new_value_query = {
                        '$pull': {
                            'MEMBERS': str(member.id),
                            'OFFICERS': str(member.id),
                            'CAPTAINS': str(member.id),
                        },
                        '$inc': {'MEMBER_COUNT': -1},
                        '$push': {'TRANSACTIONS': transaction_message},
                        }
                  response = db.deleteTeamMember(team_query, new_value_query, str(member.id))
                  if response:
                     embed = Embed(title="Member Deleted.", description=f"{member.mention} was removed from {team_profile['TEAM_DISPLAY_NAME']}", color=0x00ff00)
                     await msg.edit(embed=embed, components=[])
            except:
               embed = Embed(title="Member Not Deleted.", description=f"{member.mention} was not removed from {team_profile['TEAM_DISPLAY_NAME']}", color=0x00ff00)
               await msg.edit(embed=embed, components=[])
      else:
            await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)
   else:
      await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)


async def allowance(ctx, player, amount):
   try: 
      user2 = player
      user = db.queryUser({'DID': str(ctx.author.id)})
      user2_info = db.queryUser({'DID' : str(user2.id)})
      family = db.queryFamily({'HEAD' : user['DID']})
      if user['FAMILY'] == 'PCG' or (family['HEAD'] != user['DID'] and user['DID'] != family['PARTNER']):
         await ctx.send("You must be the Head of a Household or Partner to give allowance. ")
         return

      family = db.queryFamily({'HEAD': user['DID']})
      kids = family['KIDS']

      if str(user2.id) not in family['KIDS'] and str(user2.id) != family['PARTNER'] and str(user2.id) != family['HEAD']:
         await ctx.send("You can only give allowance family members. ")
         return
      balance = family['BANK']
      if balance <= int(amount):
         await ctx.send("You do not have that amount saved.")
      else:
         await crown_utilities.bless(int(amount), user2.id)
         await crown_utilities.cursefamily(int(amount), family['HEAD'])
         transaction_message =f"🪙 | {user['DISNAME']} paid 🪙{amount}  allowance to {user2_info['DISNAME']}"
         update_family = db.updateFamily(family['HEAD'], {'$addToSet': {'TRANSACTIONS': transaction_message}})
         await ctx.send(f"🪙{amount} has been gifted to {user2.mention}.")
         return
   except Exception as ex:
      loggy.error(f"Error in Allowance command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #    trace.append({
      #          "filename": tb.tb_frame.f_code.co_filename,
      #          "name": tb.tb_frame.f_code.co_name,
      #          "lineno": tb.tb_lineno
      #    })
      #    tb = tb.tb_next
      # print(str({
      #    'type': type(ex).__name__,
      #    'message': str(ex),
      #    'trace': trace
      # }))
      await ctx.send("There's an issue with your Allowance. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
      return
     
      


def setup(bot):
    Teams(bot)

    