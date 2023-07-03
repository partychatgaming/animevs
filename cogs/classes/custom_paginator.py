import asyncio
import textwrap
import uuid
import db
from typing import Callable, Coroutine, List, Optional, Sequence, TYPE_CHECKING, Union
import crown_utilities
import custom_logging
from cogs.battle_config import BattleConfig as bc

import attrs

from interactions import (
    Embed,
    ComponentContext,
    ActionRow,
    Button,
    ButtonStyle,
    spread_to_rows,
    ComponentCommand,
    BaseContext,
    Message,
    MISSING,
    Snowflake_Type,
    StringSelectMenu,
    StringSelectOption,
    Color,
    BrandColors,
)

from interactions.ext.paginators import Page, Paginator
from interactions.client.utils.serializer import export_converter
from interactions.models.discord.emoji import process_emoji, PartialEmoji

if TYPE_CHECKING:
    from interactions import Client
    from interactions.ext.prefixed_commands.context import PrefixedContext

class CustomPaginator(Paginator):
    def __init__(self, *args, custom_action_rows: List[ActionRow] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_action_rows = custom_action_rows or []

        # Paginator Function Types
        self.talisman_action = False
        self.guild_buff_action = False
        self.titles_action = False
        self.cards_action = False
        self.arms_action = False
        self.summon_action = False
        self.storage_action = False
        self.charge_action = False
        self.universe_tale_action = False
        self.universe_dungeon_action = False
        self.scenario_action = False

        # Cards Functions
        self.equip_card = False
        self.dismantle_card = False
        self.trade_card = False
        self.card_storage = False


        # Talisman Functions
        self.equip_talisman = False
        self.unequip_talisman = False


        # Arm Functions
        self.equip_arm = False
        self.arm_storage = False
        self.trade_arm = False
        self.dismantle_arm = False 

        # Summon Functions
        self.equip_summon = False
        self.summon_storage = False
        self.trade_summon = False
        self.dismantle_summon = False


        # Title Functions
        self.equip_title = False
        self.title_storage = False
        self.charge_title = False

        # Guild Functions
        self.guild_apply = None
        self.toggle_buff = None
        self.swap_buff = None
        self.buy_buff = None
        self.guild_buff_available = False

        # Universe Tale Selection Functions
        self.universe_tale_start = False
        self.universe_tale_co_op_start = False
        self.universe_tale_duo_start = False
        self.universe_tale_delete_save = False

        # Universe Dungeon Selection Functions
        self.universe_dungeon_start = False
        self.universe_dungeon_co_op_start = False
        self.universe_dungeon_duo_start = False
        self.universe_dungeon_delete_save = False

        self.quit = False



    """
    Paginators are a way to display multiple pages of information in a single message.
    Paginators may have custom buttons. In the case where they have custom buttons,
    the paginators will have custom_button and paginator_type attributes.

    The custom_button attribute is a list of strings that will be used to create the custom buttons.
    The paginator_type attribute is a string that will be used to determine which function to call. We
    will call the set_paginator_action_type function to set the paginator_type attribute.
    """


    def __attrs_post_init__(self) -> None:
        self.client.add_component_callback(
            ComponentCommand(
                name=f"Paginator:{self._uuid}",
                callback=self._on_button,
                listeners=[
                    f"{self._uuid}|select",
                    f"{self._uuid}|first",
                    f"{self._uuid}|back",
                    f"{self._uuid}|callback",
                    f"{self._uuid}|next",
                    f"{self._uuid}|last",
                    f"{self._uuid}|equip",
                    f"{self._uuid}|unequip",
                    f"{self._uuid}|dismantle",
                    f"{self._uuid}|apply",
                    f"{self._uuid}|bufftoggle",
                    f"{self._uuid}|buffswap",
                    f"{self._uuid}|buffshop",
                    f"{self._uuid}|resell",
                    f"{self._uuid}|trade",
                    f"{self._uuid}|storage",
                    f"{self._uuid}|charge",
                    f"{self._uuid}|start",
                    f"{self._uuid}|co-op start",
                    f"{self._uuid}|duo start",
                    f"{self._uuid}|delete save",
                    f"{self._uuid}|universe_dungeon_start",
                    f"{self._uuid}|universe_dungeon_co_op_start",
                    f"{self._uuid}|universe_dungeon_duo_start",
                    f"{self._uuid}|universe_dungeon_delete_save",
                    f"{self._uuid}|scenario_start",
                    f"{self._uuid}|quit",
                    
                ],
            )
        )


    async def _on_button(self, ctx: ComponentContext, *args, **kwargs) -> Optional[Message]:
        if ctx.author.id != self.author_id:
            return (
                await ctx.send(self.wrong_user_message, ephemeral=True)
                if self.wrong_user_message
                else await ctx.defer(edit_origin=True)
            )
        
        if self._timeout_task:
            self._timeout_task.ping.set()

        original_buttons = False

        match ctx.custom_id.split("|")[1]:
            case "first":
                self.page_index = 0
                original_buttons = True
            case "last":
                self.page_index = len(self.pages) - 1
                original_buttons = True
            case "next":
                if (self.page_index + 1) < len(self.pages):
                    self.page_index += 1
                original_buttons = True
            case "back":
                if self.page_index >= 1:
                    self.page_index -= 1
                original_buttons = True
            case "select":
                self.page_index = int(ctx.values[0])
                original_buttons = True
            case "callback":
                if self.callback:
                    return await self.callback(ctx)
                original_buttons = True
            case "equip":
                if self.talisman_action:
                    self.equip_talisman = True
                    response = self.activate_talisman_action(ctx, self._message.embeds[0], self.equip_talisman)
                    await self._message.edit(embeds=[response], components=[])
                if self.titles_action:
                    self.equip_title = True
                    response = self.activate_title_action(ctx, self._message.embeds[0].title, self.equip_title)
                    await self._message.edit(embeds=[response], components=[])
                if self.cards_action:
                    self.equip_card = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.equip_card)
                if self.arms_action:
                    self.equip_arm = True
                    response = await self.activate_arm_action(ctx, self._message.embeds[0].title, self.equip_arm)
                if self.summon_action:
                    self.equip_summon = True
                    response = await self.activate_summon_action(ctx, self._message.embeds[0].title, self.equip_summon)
            case "storage":
                if self.titles_action:
                    self.title_storage = True
                    response = self.activate_title_action(ctx, self._message.embeds[0].title, self.title_storage)
                    if response:
                        await self._message.edit(embeds=[response], components=[])
                if self.cards_action:
                    self.card_storage = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.card_storage)
            case "unequip":
                if self.talisman_action:
                    self.equip_talisman = True
                    response = self.activate_talisman_action(ctx, self._message.embeds[0], self.equip_talisman)
                await self._message.edit(embeds=[response], components=[])
            case "dismantle":
                if self.cards_action:
                    self.dismantle_card = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.dismantle_card)
                if self.arms_action:
                    self.dismantle_arm = True
                    response = await self.activate_arm_action(ctx, self._message.embeds[0].title, self.dismantle_arm)
                if self.summon_action:
                    self.dismantle_summon = True
                    response = await self.activate_summon_action(ctx, self._message.embeds[0].title, self.dismantle_summon)
                # await ctx.edit_origin(content="Dismantled!")
            case "apply":
                if self.guild_buff_action:
                    await paginator.guild_apply()
            case "bufftoggle":
                if self.guild_buff_action:
                    self.toggle_buff = True
                    response = await self.activate_guild_buff_action(ctx, self.toggle_buff)
                    await self._message.edit(embeds=[response], components=[])
            case "buffswap":
                if self.guild_buff_action:
                    self.swap_buff = True
                    response = await self.activate_guild_buff_action(ctx, self.swap_buff)
                    await self._message.delete()
            case "buffshop":
                if self.guild_buff_action:
                    self.buy_buff = True
                    response = await self.activate_guild_buff_action(ctx, self.buy_buff)
                    if response:
                        await self._message.edit(embeds=[response], components=[])
                    else:
                        await self._message.delete()
            case "start":
                if self.universe_tale_action or self.universe_dungeon_action:
                    if self.universe_tale_action:
                        self.universe_tale_start = True
                    if self.universe_dungeon_action:
                        self.universe_dungeon_start = True
                    response = await self.activate_universe_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
            case "quit":
                print("Quit was selected")
                if self.universe_tale_action:
                    self.quit = True
                    response = await self.activate_universe_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
        
        if original_buttons:
            await ctx.edit_origin(**self.to_dict())
            return None


    def _add_custom_buttons(self, custom_buttons):
        buttons = []
        for button in custom_buttons:
            label_text = button
            button = button.replace(" ", "")
            button = button.lower()

            buttons.append(Button(style=ButtonStyle.PRIMARY, label=label_text , custom_id=f"{self._uuid}|{button}"))
        
        if buttons:
            self.custom_action_rows.append(ActionRow(*buttons))
        else:
            self.custom_action_rows = []


    def create_components(self, disable: bool = False) -> List[ActionRow]:
        # Call the original create_components method to get the default ActionRows
        default_action_rows = super().create_components(disable)

        # Add custom ActionRows to the default ones
        combined_action_rows = default_action_rows + self.custom_action_rows
        return combined_action_rows

    
    @classmethod
    def create_from_embeds(cls, client: "Client", *embeds: Embed, timeout: int = 0, custom_buttons: list = [], paginator_type: str = "") -> "CustomPaginator":
        paginator = cls(client, pages=list(embeds), timeout_interval=timeout)
        paginator.set_paginator_action_type(paginator_type)
        paginator._add_custom_buttons(custom_buttons)
        return paginator


    def set_paginator_action_type(self, action_type: str):
        """
        Some paginators have different actions that can be performed on the embeds.
        Some paginators have the same actions that can be performed on the embeds.
        To differentiate the actions, we use this method to set the action type.
        """
        if action_type == "Talisman":
            self.talisman_action = True
        
        if action_type == "Guild Buff":
            self.guild_buff_action = True
        
        if action_type == "Titles":
            self.titles_action = True
        
        if action_type == "Cards":
            self.cards_action = True

        if action_type == "Arms":
            self.arms_action = True
        
        if action_type == "Summons":
            self.summon_action = True

        if action_type == "Universe Tales":
            self.universe_tale_action = True
        
        if action_type == "Universe Dungeon":
            self.universe_dungeon_action = True
        
        if action_type == "Scenario":
            self.scenario_action = True

    
    def activate_talisman_action(self, ctx, data, action: str):
        user_query = {'DID': str(ctx.author.id)}
        embed = Embed(title=f"{data.title} Talisman {action.capitalize()} Successfully Completed")

        if action == self.equip_talisman:
            db.updateUserNoFilter(user_query, {'$set': {'TALISMAN': data.title.upper()}})
            return embed

        elif action == self.unequip_talisman:
            db.updateUserNoFilter(user_query, {'$set': {'TALISMAN': "NULL"}})
            return embed
        
        elif action == "dismantle":
            return "Dismantled!"

    
    """
    GUILD BUFF ACTIONS
    This section contains all the functions related to guild buffs
    """
    async def activate_guild_buff_action(self, ctx,  action: str):
        if self.guild_apply:
            print("Hello World")
            # Come back to this and complete it
        
        if self.toggle_buff:
            if self.guild_buff_available:
                response = self.guild_buff_toggle(ctx)
                if response:
                    return response
                else:
                    return Embed(title="Guild Buff is not available.")
            else:
                return Embed(title="Guild Buff is not available.")
        
        if self.swap_buff:
            if self.guild_buff_available:
                response = await self.guild_buff_swap(ctx)
                if response:
                    return response
                else:
                    return Embed(title="Guild Buff is not available.")
        
        if self.buy_buff:
            response = await self.guild_buff_shop(ctx)
            return response


    async def guild_apply_action(self, ctx, guild_name: str):
        player = db.queryUser({'DID': str(ctx.author.id)})
        guild = db.queryTeam({'TEAM_NAME': guild_name.lower()})

        if player['DID'] not in guild['MEMBERS']:
            team_buttons = [
                Button(
                    style=ButtonStyle.BLUE,
                    label="Accept",
                    custom_id=f"{self._uuid}|yes"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="Deny",
                    custom_id=f"{self._uuid}|no"
                )
            ]
            
            guild_apply_action_row = ActionRow(*team_buttons)
            
            embed = Embed(title=f"{ctx.author.display_name} wants to join {team_profile['TEAM_DISPLAY_NAME']}", description=f"Owner, Officers, or Captains - Please accept or deny")
            
            msg = await ctx.send(embed=embed, components=[guild_apply_action_row])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.client.wait_for_component(components=[guild_apply_action_row, team_buttons], timeout=1200, check=check)
                
                if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                    await button_ctx.send("Application Denied.")
                    await msg.delete()
                    return

                if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                    team_query = {'TEAM_NAME': team_profile['TEAM_NAME'].lower()}
                    new_value_query = {'$push': {'MEMBERS': player['DID']}}
                    response = db.addTeamMember(team_query, new_value_query, player['DID'], team_profile['TEAM_DISPLAY_NAME'])
                    
                    transaction_query = {'$addToSet': {'TRANSACTIONS': f"{ctx.author.display_name} joined the guild."}}
                    response = db.updateTeam(team_query, transaction_query)

                    embed = Embed(title=f"{ctx.author.display_name} has joined {team_profile['TEAM_DISPLAY_NAME']}.")
                    await msg.edit(embed=embed)
                    await button_ctx.ctx.send(response)
            except:
                embed = Embed(title=f"{ctx.author.display_name} did not respond in time. Please try again.")
                await msg.edit(embed=embed, components=[])
        else:
            embed = Embed(title=f"{ctx.author.display_name} is already in a Guild. You may not join another guild.", description=f"Please leave your current guild to join {team_profile['TEAM_DISPLAY_NAME']}.")
            return embed
        

    def guild_buff_toggle(self, ctx):
        player_data = db.queryUser({'DID': str(ctx.author.id)})
        team_data = db.queryTeam({'TEAM_NAME': player_data['TEAM'].lower()})
        guild_buff_on = team_data['GUILD_BUFF_ON']
        team_query = {'TEAM_NAME': team_data['TEAM_NAME']}
        return_message = {}

        if guild_buff_on:
            transaction_message = f"🔴 | {player_data['DISNAME']} turned off Guild Buff."
            new_value_query = {
                '$set': {'GUILD_BUFF_ON': False},
                '$push': {'TRANSACTIONS': transaction_message}
            }
            embed_title = f"{team_data['TEAM_DISPLAY_NAME']} Guild Buff has been turned off."
        else:
            transaction_message = f"🟢 | {player_data['DISNAME']} turned on Guild Buff."
            new_value_query = {
                '$set': {'GUILD_BUFF_ON': True},
                '$push': {'TRANSACTIONS': transaction_message}
            }
            embed_title = f"{team_data['TEAM_DISPLAY_NAME']} Guild Buff has been turned on."

        try:
            response = db.updateTeam(team_query, new_value_query)
            if response:
                return Embed(title=embed_title)
            else:
                return False
        except Exception as ex:
            print(f"Error updating team data: {ex}")
            return False


    async def guild_buff_swap(self, ctx):
        player = db.queryUser({'DID': str(ctx.author.id)})
        team = db.queryTeam({'TEAM_NAME': player['TEAM'].lower()})

        team_query = {'TEAM_NAME': team['TEAM_NAME']}
        guild_buff_available = team['GUILD_BUFF_AVAILABLE']
        guild_buffs = team['GUILD_BUFFS']
        active_guild_buff = team['ACTIVE_GUILD_BUFF']
        team_member_count = len(team['MEMBERS'])
        balance = team['BANK']

        guild_buff_msg = []
        buttons = []

        for buff in guild_buffs:
            index = guild_buffs.index(buff)
            buttons.append(
                Button(
                    style=ButtonStyle.BLUE,
                    label=f"[{str(index)}] {buff['TYPE']}",
                    custom_id=f"{self._uuid}|{str(index)}"
                )
            )
            guild_buff_msg.append(f"[{str(index)}] **{buff['TYPE']}** buff: {buff['USES']} uses left!")

        guild_buff_msg_joined = "\n".join(guild_buff_msg)

        buff_swap_action_row = ActionRow(*buttons)
        embedVar = Embed(title=f"Swap Guild Buffs", description=textwrap.dedent(f"""\
        {guild_buff_msg_joined}
        """), color=0xf1c40f)
        msg = await ctx.send(embed=embedVar, components=[buff_swap_action_row])
        
        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author

        try:
            button_ctx = await self.client.wait_for_component(components=[buff_swap_action_row, buttons], timeout=120,check=check)
            update_query = {}

            if button_ctx.ctx.custom_id == f"{self._uuid}|0":
                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[0]['TYPE']}"},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[0]['TYPE']} Buff"}
                }
            
            if button_ctx.ctx.custom_id == f"{self._uuid}|1":
                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[1]['TYPE']}"},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[1]['TYPE']} Buff"}
                }

            if button_ctx.ctx.custom_id == f"{self._uuid}|2":
                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[2]['TYPE']}"},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[2]['TYPE']} Buff"}
                }
                
            if button_ctx.ctx.custom_id == f"{self._uuid}|3":
                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[3]['TYPE']}"},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[3]['TYPE']} Buff"}
                }
                
            if button_ctx.ctx.custom_id == f"{self._uuid}|4":
                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[4]['TYPE']}"},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[4]['TYPE']} Buff"}
                }


            response = db.updateTeam(team_query, update_query)
            if response:
                embed = Embed(title=f"Guild Buff Swapped successfully")
                await msg.edit(embed=embed, components=[])
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
            await msg.edit(content="Guild buff swap timed out.", components=[])
            return


    async def guild_buff_shop(self, ctx):
        player = db.queryUser({'DID': str(ctx.author.id)})
        team = db.queryTeam({'TEAM_NAME': player['TEAM'].lower()})
        
        team_query = {'TEAM_NAME': team['TEAM_NAME']}
        guild_buff_available = team['GUILD_BUFF_AVAILABLE']
        guild_buffs = team['GUILD_BUFFS']
        team_member_count = len(team['MEMBERS'])
        balance = team['BANK']
        icon = "💳"
        shielding = team['SHIELDING']
        association = team['GUILD']
        shield_buff = False
        rift_buff = False
        level_buff = False
        stat_buff = False
        quest_buff = False
        rematch_buff = False
        for buff in guild_buffs:
            if buff['TYPE'] == 'Stat':
                stat_buff = True
            if buff['TYPE'] == 'Rift':
                rift_buff = True
            if buff['TYPE'] == 'Quest':
                quest_buff = True
            if buff['TYPE'] == 'Level':
                level_buff = True
            if buff['TYPE'] == 'Rematch':
                rematch_buff = True
            
        if shielding ==True and association != 'PCG':
            shield_buff = True

        if team_member_count <= 2:
            embed = Embed(title=f"Guild Buff Shop", description="Guilds must have at least **3** guild members to purchase Guild Buffs.")
            return embed

        if guild_buff_available:
            guild_buff_length = len(team['GUILD_BUFFS'])
            if guild_buff_length >= 5:
                embed = Embed(title=f"Guild Buff Shop", description="Guilds may only have up to 5 Guild Buffs at one time, max.")
                return embed

        war_tax = 0
        war_message = ""
        shield_message = ""
        if team['WAR_FLAG']:
            war_tax = 15000000
            war_message = "War tax applied"
        quest_buff_cost = 20000000 + war_tax
        rift_buff_cost = 18000000 + war_tax
        level_buff_cost = 15000000 + war_tax
        stat_buff_cost = 10000000 + war_tax
        rematch_cost = 30000000 + war_tax
        if shield_buff:
            quest_buff_cost = round(quest_buff_cost * .60)
            rift_buff_cost = round(rift_buff_cost * .60)
            level_buff_cost = round(level_buff_cost * .60)
            stat_buff_cost = round(stat_buff_cost * .60)
            rematch_cost = round(rematch_cost * .60)
            shield_message = f"🎏 **{association} Shield Discount** 30%"
        
        sell_buttons = [
                Button(
                    style=ButtonStyle.GREEN,
                    label="🔋 1️⃣",
                    custom_id=f"{self._uuid}|1"
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="🔋 2️⃣",
                    custom_id=f"{self._uuid}|2"
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="🔋 3️⃣",
                    custom_id=f"{self._uuid}|3"
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="🔋 4️⃣",
                    custom_id=f"{self._uuid}|4"
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="🔋 5️⃣",
                    custom_id=f"{self._uuid}|5"
                )
            ]


        sell_buttons_action_row = ActionRow(*sell_buttons)
        
        embedVar = Embed(title=f":tickets: | **Buff Shop** - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
        Welcome {team['TEAM_DISPLAY_NAME']}!
        {war_message}
        {shield_message}
        🔋 1️⃣ **Quest Buff** for 💸 **{'{:,}'.format(quest_buff_cost)}**
        🔋 2️⃣ **Level Buff** for 💸 **{'{:,}'.format(level_buff_cost)}**
        🔋 3️⃣ **Stat Buff** for 💸 **{'{:,}'.format(stat_buff_cost)}**
        🔋 4️⃣ **Rift Buff** for 💸 **{'{:,}'.format(rift_buff_cost)}**
        🔋 5️⃣ **Rematch Buff** for 💸 **{'{:,}'.format(rematch_cost)}**
        All Buffs are available for 100 uses.
        What would you like to buy?
        """))
        
        msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row])
        
        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author

        try:
            button_ctx = await self.client.wait_for_component(components=[sell_buttons_action_row], timeout=120,check=check)
            uses = 100
            price = 0
            update_query = {}

            if button_ctx.ctx.custom_id == f"{self._uuid}|1":
                if quest_buff: 
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Guild already owns this Buff")
                    await msg.edit(embed=embed, components=[])
                    return
                price = quest_buff_cost

                if price > balance:
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Insufficent Balance")
                    await msg.edit(embed=embed, components=[])
                    return

                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Quest'},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Quest Buff", 'GUILD_BUFFS': {'TYPE': 'Quest', 'USES': 100}}
                }
            
            if button_ctx.ctx.custom_id == f"{self._uuid}|2":
                if level_buff: 
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Guild already owns this Buff")
                    await msg.edit(embed=embed, components=[])
                    return
                price = level_buff_cost
                if price > balance:
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Insufficent Balance")
                    await msg.edit(embed=embed, components=[])
                    return

                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Level'},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Level Buff", 'GUILD_BUFFS': {'TYPE': 'Level', 'USES': 100}}
                }

            if button_ctx.ctx.custom_id == f"{self._uuid}|3":
                if stat_buff: 
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Guild already owns this Buff")
                    await msg.edit(embed=embed, components=[])
                    return
                price= stat_buff_cost
                if price > balance:
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Insufficent Balance")
                    await msg.edit(embed=embed, components=[])
                    return

                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Stat'},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Stat Buff", 'GUILD_BUFFS': {'TYPE': 'Stat', 'USES': 100}}
                }

            if button_ctx.ctx.custom_id == f"{self._uuid}|4":
                if rift_buff: 
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Guild already owns this Buff")
                    await msg.edit(embed=embed, components=[])
                    return
                price= rift_buff_cost
                if price > balance:
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Insufficent Balance")
                    await msg.edit(embed=embed, components=[])
                    return

                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Rift'},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Rift Buff", 'GUILD_BUFFS': {'TYPE': 'Rift', 'USES': 100}}
                }

            if button_ctx.ctx.custom_id == f"{self._uuid}|5":
                if rematch_buff: 
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Guild already owns this Buff")
                    await msg.edit(embed=embed, components=[])
                    return
                price= rematch_cost
                if price > balance:
                    embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Insufficent Balance")
                    await msg.edit(embed=embed, components=[])
                    return

                update_query = {
                    '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Rematch'},
                    '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Rematch Buff", 'GUILD_BUFFS': {'TYPE': 'Rematch', 'USES': 100}}
                }

            response = db.updateTeam(team_query, update_query)
            if response:
                await crown_utilities.curseteam(int(price), team['TEAM_NAME'])
                embed = Embed(title=f"Guild Buff Shop", description="Transaction Successful - Buff Purchased")
                await msg.edit(embed=embed, components=[])
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
            embed = Embed(title=f"Guild Buff Shop", description="Transaction Cancelled - Timed Out")
            await msg.edit(embed=embed, components=[])


    """
    TITLE FUNCTIONS
    This section contains all the functions related to titles
    """
    async def activate_title_action(self, ctx, title, action):
        if self.equip_title:
            response = self.equip_title_function(ctx, title)
            return response

        if self.title_storage:
            response = await self.title_storage_function(ctx, title)
            return response
        
        if self.charge_title_function:
            response = self.charge_title_function(ctx, title)
            return response
            

    def equip_title_function(self, ctx, title):
        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            if title in user['TITLES']:
                user_query = {'DID': str(ctx.author.id)}
                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': title}})
                if response:
                    embed = Embed(title=f"🎗️ Title Equipped", description=f"Title {title} equipped")
                    return embed
                else:
                    embed = Embed(title=f"🎗️ Title Not Equipped", description=f"Failed to equip title {title}")
                    return embed
            else:
                embed = Embed(title=f"🎗️ Title Not Equipped", description=f"Failed to equip title {title} - Title not available")
                return embed
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
            embed = Embed(title=f"🎗️ Title Not Equipped", description=f"Failed to equip title {title} - Error Logged")
            return embed


    def charge_title_function(self, ctx, title):
        return "Charge Title under construction"


    async def title_storage_function(self, ctx, title):
        user = db.queryUser({'DID': str(ctx.author.id)})
        storage = user['TSTORAGE']
        storage_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="Swap Storage Title",
                        custom_id=f"{self._uuid}|swap"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="Add to Storage",
                        custom_id=f"{self._uuid}|store"
                    )
                ]
        storage_buttons_action_row = ActionRow(*storage_buttons)
        embed = Embed(title=f"🎗️ Title Storage", description=f"Would you like to Swap Titles or Add Title to Storage")
        msg = await ctx.send(embed=embed, components=[storage_buttons_action_row])

        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author
        try:
            button_ctx = await self.client.wait_for_component(components=[storage_buttons_action_row], timeout=120, check=check)

            if button_ctx.ctx.custom_id == f"{self._uuid}|swap":
                embed = Embed(title=f"🎗️ Title Storage Swap", description=f"Which title would you like to swap with?")
                await msg.delete()
                msg = await button_ctx.ctx.send(embed=embed)
                
                def check(msg):
                    return msg.author == ctx.author

                try:
                    msg = await self.client.wait_for('on_message_create', check=check, timeout=120)
                    author = msg.author
                    content = msg.content

                    if storage[int(msg.content)]:
                        swap_with = storage[int(msg.content)]
                        query = {'DID': str(msg.author.id)}
                        update_storage_query = {
                            '$pull': {'TITLES': title},
                            '$addToSet': {'TSTORAGE': title},
                        }
                        response = db.updateUserNoFilter(query, update_storage_query)

                        update_storage_query = {
                            '$pull': {'TSTORAGE': swap_with},
                            '$addToSet': {'TITLES': swap_with}
                        }
                        response = db.updateUserNoFilter(query, update_storage_query)

                        embed = Embed(title=f"🎗️ Title Storage Swap", description=f"{title} has been swapped with {swap_with}")
                        await ctx.send(embed=embed)
                    else:
                        embed = Embed(title=f"🎗️ Title Storage Swap Exited", description=f"The title number you want to swap with does not exist. Please try again.")
                        await ctx.send(embed=embed)
                        

                except Exception as e:
                    return False
            
            if button_ctx.ctx.custom_id == f"{self._uuid}|store":                
                try:
                    
                    author = msg.author
                    content = msg.content
                    user = db.queryUser({'DID': str(author.id)})
                    storage_type = user['STORAGE_TYPE']

                    if len(storage) <= (storage_type * 15):
                        query = {'DID': user['DID']}
                        update_storage_query = {
                            '$pull': {'TITLES': title},
                            '$addToSet': {'TSTORAGE': title},
                        }
                        response = db.updateUserNoFilter(query, update_storage_query)
                        
                        embed = Embed(title=f"🎗️ Title Storage", description=f"{title} has been added to storage")
                        await msg.edit(embed=embed, components=[])
                        return
                    else:
                        embed = Embed(title=f"🎗️ Title Storage", description=f"Not enough space in storage - Please upgrade your storage")
                        await msg.edit(embed=embed, components=[])
                        return

                except Exception as e:
                    embed = Embed(title=f"🎗️ Title Storage Exited", description=f"Failed to store or swap title {title} - Error Logged")
                    await msg.edit(embed=embed, components=[])
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
            embed = Embed(title=f"🎗️ Title Storage Exited", description=f"Failed to store or swap title {title} - Error Logged")
            return embed
                            

    """
    ARM FUNCTIONS
    This section contains all the functions for the arm commands
    """
    async def activate_arm_action(self, ctx, arm, action):
        if action == self.equip_arm:
            response = self.equip_arm_function(ctx, arm)
            return response
        
        if action == self.arm_storage:
            response = await self.arm_storage_function(ctx, arm)
            return response
        
        if action == self.dismantle_arm:
            response = await self.dismantle_arm_function(ctx, arm)
            return response


    def equip_arm_function(self, ctx, arm):
        try:
            user = db.queryVault({'DID': str(ctx.author.id)})
            if arm in user['ARMS']:
                user_query = {'DID': str(ctx.author.id)}
                response = db.updateUserNoFilter(user_query, {'$set': {'ARM': arm}})
                if response:
                    embed = Embed(title=f"🦾 Arm Equipped", description=f"Arm {arm} equipped")
                    return embed
                else:
                    embed = Embed(title=f"🦾 Arm Not Equipped", description=f"Failed to equip arm {arm}")
                    return embed
            else:
                embed = Embed(title=f"🦾 Arm Not Equipped", description=f"Failed to equip arm {arm} - Arm not available")
                return embed
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
            embed = Embed(title=f"🦾 Arm Not Equipped", description=f"Failed to equip arm {arm} - Error Logged")
            return embed
        

    async def arm_storage_function(self, ctx, arm):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)

        if arm == player.equipped_arm:
            embed = Embed(title=f"🦾 Arm Storage", description=f"Arm {arm} is equipped - Please unequip arm before storing")
            await ctx.send(embed=embed)
            return
        
        for arm in player.arms:
            if arm['ARM']:
                storage_buttons = [
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="Swap Storage Arm",
                                custom_id=f"{self._uuid}|swap"
                            ),
                            Button(
                                style=ButtonStyle.GREEN,
                                label="Add to Storage",
                                custom_id=f"{self._uuid}|store"
                            )
                        ]
                
                components = ActionRow(*storage_buttons)
                embed = Embed(title=f"🦾 Arm Storage", description=f"Would you like to Swap Arms or Add Arm to Storage")
                msg = await ctx.send(embed=embed, components=[components])
                
                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)


                    if button_ctx.ctx.custom_id == f"{self._uuid}|swap":
                        embed = Embed(title=f"🦾 Arm Storage", description=f"Which arm would you like to swap with?")
                        message = await msg.edit(embed=embed, components=[])
                        
                        def check(event):
                            return event.message.author.id == ctx.author.id

                        try:
                            response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                            option = int(response.message.content)
                            storage_arm = player.astorage[option]
                            if storage_arm:
                                query = {'DID': str(ctx.author.id)}
                                update_storage_query = {
                                    '$pull': {'ARMS': {'ARM' : arm['ARM']}},
                                    '$addToSet': {'ASTORAGE' : { 'ARM' : arm['ARM'], 'DUR' : int(arm['DUR'])}},
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)

                                update_storage_query = {
                                    '$pull': {'ASTORAGE': storage_arm},
                                    '$addToSet': {'ARMS': storage_arm}
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)

                                embed = Embed(title=f"🦾 Arm Storage", description=f"{arm['ARM']} has been swapped with {storage_arm['ARM']}")
                                await message.edit(embed=embed)
                                return
                            else:
                                embed = Embed(title=f"🦾 Arm Storage", description=f"Arm {option} not found")
                                await message.edit(embed=embed)
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
                            embed = Embed(title=f"🦾 Arm Storage", description=f"There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
                            await message.edit(embed=embed)
                            return
                    
                    if button_ctx.ctx.custom_id == f"{self._uuid}|store":
                        
                        try:
                            if len(player.astorage_length) <= (player.storage_type * 15):
                                query = {'DID': str(ctx.author.id)}
                                update_storage_query = {
                                    '$pull': {'ARMS': {'ARM' : arm['ARM']}},
                                    '$addToSet': {'ASTORAGE': { 'ARM' : arm['ARM'], 'DUR' : int(arm['DUR'])}},
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)
                                
                                embed = Embed(title=f"🦾 Arm Storage", description=f"{arm['ARM']} has been added to storage")
                                await msg.edit(embed=embed, components=[])
                                return
                            else:
                                embed = Embed(title=f"🦾 Arm Storage", description=f"Not enough space in storage")
                                await msg.edit(embed=embed, components=[])
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
                            embed = Embed(title=f"🦾 Arm Storage", description=f"There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
                            await msg.edit(embed=embed, components=[])
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
                    await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                    return


    def trade_arm_function(self, ctx, arm):
        return "Trade Arm under construction"


    async def dismantle_arm_function(self, ctx, arm_title):
        await ctx.defer()
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            if arm_title == player.equipped_arm:
                embed = Embed(title=f"🦾 Arm Storage", description=f"You can't dismantle your equipped arm")
                await ctx.send(embed=embed)
                return
            
            for arm in player.arms:
                arm_data = db.queryArm({'ARM': arm['ARM']})
                a = crown_utilities.create_arm_from_data(arm_data)
                a.set_drop_style()
                dismantle_amount = a.dismantle_amount
                if arm['ARM'] == arm_title:
                    dismantle_buttons = [
                                Button(
                                    style=ButtonStyle.PRIMARY,
                                    label="Yes",
                                    custom_id=f"{self._uuid}|yes"
                                ),
                                Button(
                                    style=ButtonStyle.RED,
                                    label="No",
                                    custom_id=f"{self._uuid}|no"
                                )
                            ]

                    components = ActionRow(*dismantle_buttons)
                    embed = Embed(title=f"🦾 Arm Storage", description=f"Are you sure you want to dismantle {arm['ARM']} for 💎 {dismantle_amount} gems?")
                    msg = await ctx.send(embed=embed, components=[components])

                    def check(component: Button) -> bool:
                        return component.ctx.author == ctx.author

                    try:
                        button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                        if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                            embed = Embed(title=f"🦾 Arm Storage", description=f"Arm Dismantle has been cancelled")
                            await msg.edit(embed=embed, components=[])
                            return
                        
                        if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                            response = player.save_gems(a.universe, dismantle_amount)

                            if response:
                                remove_arm_response = player.remove_arm(arm['ARM'])
                                embed = Embed(title=f"🦾 Arm Storage", description=f"{arm['ARM']} has been dismantled and you have received 💎 {dismantle_amount} {a.universe_crest} {a.universe} gems")
                                await msg.edit(embed=embed, components=[])
                            else:
                                embed = Embed(title=f"🦾 Arm Storage", description=f"Failed to dismantle {arm['ARM']}")
                                await msg.edit(embed=embed, components=[])
                                

                    except asyncio.TimeoutError:
                        embed = Embed(title=f"🦾 Arm Storage", description=f"Timed out")
                        await msg.edit(embed=embed, components=[])
                        return
        
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🦾 Arm Storage", description=f"There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
            await ctx.send(embed=embed)

    """
    Card Functions
    This section contains all the functions for cards
    """
    async def activate_card_action(self, ctx, card, action: str):
        try:
            if self.cards_action:
                if action == self.equip_card:
                    response = await self.equip_card_action(ctx, card)
                    self.equip_card = False
                
                if action == self.card_storage:
                    response = await self.card_storage_function(ctx, card)
                    self.card_storage = False

                if action == self.dismantle_card:
                    response = await self.dismantle_card_action(ctx, card)
                    self.dismantle_card = False

                if action == self.trade_card:
                    response = self.trade_card_action(ctx, card)
                    self.trade_card = False
        except Exception as e:
            print(e)
            return None
    

    async def equip_card_action(self, ctx, card):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            if card == user['CARD']:
                embed = Embed(title=f"🎴 Card Equipped", description=f"{card} is already equipped")
                await ctx.send(embed=embed)
                return
            if card in user['CARDS']:
                response = db.updateUserNoFilter(user_query, {'$set': {'CARD': card}})
                if response:
                    embed = Embed(title=f"🎴 Card Equipped", description=f"{card} has been equipped")
                    await ctx.send(embed=embed)
                else:
                    embed = Embed(title=f"🎴 Card Not Equipped", description=f"Failed to equip {card} as it is not in your inventory")
                    await ctx.send(embed=embed)
            else:
                embed = Embed(title=f"🎴 Card Not Equipped", description=f"Failed to equip {card} as it is not in your inventory")
                await ctx.send(embed=embed)
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🎴 Card Not Equipped", description=f"Failed to equip {card} - Error Logged")
            await ctx.send(embed=embed)
    

    async def dismantle_card_action(self, ctx, card):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            card_data = db.queryCard({'NAME': card})
            c = crown_utilities.create_card_from_data(card_data)
            c.set_card_level_buffs(player.card_levels)
            if c.card_lvl == 0:
                c.card_lvl = 1
            dismantle_amount = (250 * c.tier) * c.card_lvl
            if card == player.equipped_card:
                embed = Embed(title=f"🎴 Card Dismantled", description=f"Failed to dismantle {card} as it is currently equipped")
                await ctx.send(embed=embed)
                return
            if card in player.cards:
                dismantle_buttons = [
                            Button(
                                style=ButtonStyle.PRIMARY,
                                label="Yes",
                                custom_id=f"{self._uuid}|yes"
                            ),
                            Button(
                                style=ButtonStyle.RED,
                                label="No",
                                custom_id=f"{self._uuid}|no"
                            )
                        ]

                components = ActionRow(*dismantle_buttons)
                embed = Embed(title=f"🎴 Dismantle Card", description=f"Are you sure you want to dismantle {card} for 💎 {dismantle_amount} gems?")
                msg = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        embed = Embed(title=f"🎴 Card Not Dismantled", description=f"Cancelled dismantling {card}")
                        await msg.edit(embed=embed, components=[])
                        return
                    
                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = player.save_gems(c.universe, dismantle_amount)

                        if response:
                            remove_card_response = player.remove_card(card)
                            if remove_card_response:
                                embed = Embed(title=f"🎴 Card Dismantled", description=f"{c.name} has been dismantled for 💎 {dismantle_amount} {c.universe_crest} {c.universe} Gems")
                                await msg.edit(embed=embed, components=[])
                        else:
                            embed = Embed(title=f"🎴 Card Not Dismantled", description=f"Failed to dismantle {card} - Error Logged")
                            await msg.edit(embed=embed, components=[])

                except asyncio.TimeoutError:
                    embed = Embed(title=f"🎴 Card Not Dismantled", description=f"Failed to dismantle {card} - Timed Out")
                    await msg.edit(embed=embed, components=[])
            else:
                embed = Embed(title=f"🎴 Card Not Dismantled", description=f"Failed to dismantle {card} as it is not in your inventory")
                await ctx.send(embed=embed)  
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🎴 Card Not Dismantled", description=f"Failed to dismantle {card} - Error Logged")
            await ctx.send(embed=embed)


    def trade_card_action(self, ctx, card):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        if card in user['CARDS']:
            card_data = db.queryCard({'NAME': card})
            c = crown_utilities.create_card_from_data(card_data)
            # Come back to this later

    async def card_storage_function(self, ctx, card):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)
        if card == player.equipped_card:
            embed = Embed(title=f"🎴 Card Not Stored", description=f"Failed to store {card} as it is currently equipped")
            await ctx.send(embed=embed)
            return

        if card in player.cards:
            storage_buttons = [
                        Button(
                            style=ButtonStyle.PRIMARY,
                            label="Swap Storage Card",
                            custom_id=f"{self._uuid}|swap"
                        ),
                        Button(
                            style=ButtonStyle.GREEN,
                            label="Add to Storage",
                            custom_id=f"{self._uuid}|store"
                        )
                    ]

            components = ActionRow(*storage_buttons)

            embed = Embed(title=f"🎴 Card Storage", description=f"Would you like to swap with a storage card or add {card} to your storage?")
            msg = await ctx.send(embed=embed, components=[components])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                if button_ctx.ctx.custom_id == f"{self._uuid}|swap":
                    # Swap with storage card
                    embed = Embed(title=f"🎴 Card Storage", description=f"Which card number would you like to swap with?\nPlease use the [number] from the storage card list.")
                    message = await msg.edit(embed=embed, components=[])

                    def check(event):
                        return event.message.author.id == ctx.author.id

                    try:
                        response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                        option = int(response.message.content)
                        storage_card = player.storage[option]
                        if storage_card:
                            # Swap cards
                            swap_with = player.storage[option]
                            update_storage_query = {
                                            '$pull': {'CARDS': card},
                                            '$addToSet': {'STORAGE': card},
                                        }
                            response = db.updateUserNoFilter(user_query, update_storage_query)

                            update_card_query = {
                                            '$pull': {'STORAGE': swap_with},
                                            '$addToSet': {'CARDS': swap_with},
                                        }
                            response = db.updateUserNoFilter(user_query, update_card_query)
                            embed = Embed(title=f"🎴 Card Storage", description=f"Successfully swapped {card} with {swap_with}")
                            await message.edit(embed=embed, components=[])
                            return
                        else:
                            embed = Embed(title=f"🎴 Card Storage", description=f"Failed to swap {card} - Invalid card number")
                            await message.edit(embed=embed, components=[])
                            return
                    except asyncio.TimeoutError:
                        embed = Embed(title=f"🎴 Card Storage", description=f"Failed to swap {card} - Timed Out")
                        await message.edit(embed=embed, components=[])
                        return

                if button_ctx.ctx.custom_id == f"{self._uuid}|store":
                    # Add to storage
                    if player.storage_length <= (player.storage_type * 15):
                        update_storage_query = {
                                        '$pull': {'CARDS': card},
                                        '$addToSet': {'STORAGE': card},
                                    }
                        response = db.updateUserNoFilter(user_query, update_storage_query)
                        embed = Embed(title=f"🎴 Card Storage", description=f"Successfully added {card} to storage")
                        await msg.edit(embed=embed, components=[])
                        return
                    else:
                        embed = Embed(title=f"🎴 Card Storage", description=f"Failed to add {card} to storage - Storage is full")
                        await msg.edit(embed=embed, components=[])
                        return
                    
            except asyncio.TimeoutError:
                embed = Embed(title=f"🎴 Card Storage", description=f"Failed to add {card} to storage - Timed Out")
                await msg.edit(embed=embed, components=[])
                return
        else:
            embed = Embed(title=f"🎴 Card Storage", description=f"Failed to add {card} to storage - Card not in inventory")
            await ctx.send(embed=embed)


    """
    SUMMON FUNCTIONS
    This section contains all the functions related to summons
    """
    async def activate_summon_action(self, ctx, summon, action: str):
        try:
            if self.summon_action:
                if self.equip_summon:
                    response = await self.equip_summon_action(ctx, summon)
                    self.equip_summon = False
                
                if self.dismantle_summon:
                    response = await self.dismantle_summon_action(ctx, summon)
                    self.dismantle_summon = False

        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🔮 Summon Activation Failed", description=f"Failed to activate {summon} - Error Logged")
            await ctx.send(embed=embed)

    
    async def equip_summon_action(self, ctx, summon_title):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)
        updated = False
        if summon_title == player.equipped_summon:
            embed = Embed(title=f"🐦 Summon Not Equipped", description=f"{summon_title} is already equipped")
            await ctx.send(embed=embed)
            return
        for summon in player.summons:
            if summon_title == summon['NAME']:
                update_summon_query = {
                                '$set': {'PET': summon_title},
                            }
                response = db.updateUserNoFilter(user_query, update_summon_query)
                embed = Embed(title=f"🐦 Summon Equipped", description=f"Successfully equipped {summon_title}")
                updated = True
                await ctx.send(embed=embed)
        
        if not updated:
            embed = Embed(title=f"🐦 Summon Not Equipped", description=f"Failed to equip {summon_title} as it is not in your inventory")
            await ctx.send(embed=embed)


    async def dismantle_summon_action(self, ctx, summon_title):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        summon_data = db.querySummon({'PET': summon_title})
        player = crown_utilities.create_player_from_data(user)
        summon = crown_utilities.create_summon_from_data(summon_data)
        available_to_dismantle = False
        for s in player.summons:
            if summon_title == s['NAME']:
                available_to_dismantle = True
                break

        if summon_title == player.equipped_summon:
            embed = Embed(title=f"🐦 Summon Not Dismantled", description=f"{summon_title} is equipped and cannot be dismantled.")
            await ctx.send(embed=embed)
            return

        if not available_to_dismantle:
            embed = Embed(title=f"🐦 Summon Not Dismantled", description=f"{summon_title} is not in your inventory.")
            await ctx.send(embed=embed)
            return

        try:
            dismantle_buttons = [
                        Button(
                            style=ButtonStyle.PRIMARY,
                            label="Yes",
                            custom_id=f"{self._uuid}|yes"
                        ),
                        Button(
                            style=ButtonStyle.RED,
                            label="No",
                            custom_id=f"{self._uuid}|no"
                        )
                    ]

            components = ActionRow(*dismantle_buttons)
            embed = Embed(title=f"🐦 Dismantle Card", description=f"Are you sure you want to dismantle {summon.name} for 💎 {summon.dismantle_amount} gems?")
            msg = await ctx.send(embed=embed, components=[components])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                    embed = Embed(title=f"🐦 Summon Not Dismantled", description=f"Cancelled dismantle of {summon.name}")
                    await msg.edit(embed=embed, components=[])
                    return

                if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                    response = player.save_gems(summon.universe, summon.dismantle_amount)

                    if response:
                        remove_card_response = player.remove_summon(summon.name)
                        if remove_card_response:
                            embed = Embed(title=f"🐦 Summon Dismantled", description=f"{summon.name} has been dismantled for 💎 {summon.dismantle_amount} {summon.universe_crest} {summon.universe} Gems")
                            await msg.edit(embed=embed, components=[])
                    else:
                        embed = Embed(title=f"🐦 Summon Not Dismantled", description=f"Failed to dismantle {summon.name} - Error Logged")
                        await msg.edit(embed=embed, components=[])

            except asyncio.TimeoutError:
                embed = Embed(title=f"🐦 Summon Not Dismantled", description=f"Failed to dismantle {summon.name} - Timed Out")
                await msg.edit(embed=embed, components=[])
                return
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🔮 Summon Dismantle Failed", description=f"Failed to dismantle {summon.name} - Error Logged")
            await msg.edit(embed=embed)




    """
    UNIVERSE FUNCTIONS
    This section contains all the functions related to universe selections
    """
    async def activate_universe_action(self, ctx, universe):
        print("activate_universe_action has been called")
        if self.universe_tale_action:
            mode = "Tales"
        else:
            mode = "Dungeon"

        if self.universe_tale_start or self.universe_dungeon_start:
            await self.start_tale_or_dungeon(ctx, universe, mode)
            self.universe_tale_start = False

        if self.quit:
            await self.quit_universe_selection(ctx)
            self.quit = False


    async def quit_universe_selection(self, ctx):
        user_data = db.queryUser({'DID': str(ctx.author.id)})
        player = crown_utilities.create_player_from_data(user_data)
        player.make_available()
        embed = Embed(title= f"Match Making Cancelled.", description="You have cancelled the match making process.")
        await ctx.send(embed=embed, ephemeral=True)


    async def start_tale_or_dungeon(self, ctx, universe_title, mode):
        print("Start Tale has been called")
        user_data = db.queryUser({'DID': str(ctx.author.id)})
        player = crown_utilities.create_player_from_data(user_data)

        try:
            _uuid = uuid.uuid4()
            save_spot_check = crown_utilities.TALE_M
            currentopponent = 0
            entrance_fee = 5000
            mode_check = "HAS_CROWN_TALES"
            universe = db.queryUniverse({"TITLE": universe_title})
            if mode in crown_utilities.DUNGEON_M:
                entrance_fee = 20000
                save_spot_check = crown_utilities.DUNGEON_M
                mode_check = "HAS_DUNGEON"

            if universe[mode_check] == True:
                if player.difficulty != "EASY":
                    for save in player.save_spot:
                        if save['UNIVERSE'] == universe['TITLE'] and save['MODE'] in save_spot_check:
                            currentopponent = save['CURRENTOPPONENT']

            if self.universe_tale_start or self.universe_dungeon_start:
                await bc.create_universe_battle(self, ctx, mode, universe, player, currentopponent, entrance_fee)
                return

            # if button_ctx.ctx.custom_id == f"{_uuid}|coop":
            #     await button_ctx.ctx.send("Starting")
            #     await msg.edit(components=[])

            # if button_ctx.ctx.custom_id == f"{_uuid}|duo":
            #     await button_ctx.ctx.send("Starting")
            #     await msg.edit(components=[])

            # if button_ctx.ctx.custom_id == f"{_uuid}|deletesave":
            #     player.make_available()
            #     await button_ctx.ctx.send("Deleting Save")
            #     gs.delete_save_spot(player, universe['TITLE'], mode, currentopponent)
            #     await msg.edit(components=[])
            
            # if button_ctx.ctx.custom_id == f"{_uuid}|quit":
            #     player.make_available()
            #     embed = Embed(title= f"{universe['TITLE']} Match Making Cancelled.", description="You have cancelled the match making process.")
            #     await button_ctx.ctx.send(embed=embed)
            #     await msg.edit(components=[])
            #     return
                

            else:
                player.make_available()
                embed = Embed(title= f"{universe['TITLE']} Match Making Cancelled.", description="You have cancelled the match making process due to the universe not having characters in this mode.", ephemeral=True)
                await ctx.send(embed=embed)

        except Exception as ex:
            player.make_available()
            custom_logging.debug(ex)
            await ctx.send("There was an error starting the tale. Please try again later.", ephemeral=True)



