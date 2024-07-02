import asyncio
import textwrap
import uuid
import db
import classes as data
from typing import Callable, Coroutine, List, Optional, Sequence, TYPE_CHECKING, Union
import crown_utilities
import custom_logging
from cogs.battle_config import BattleConfig as bc
from cogs.quests import Quests
import random

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
        self.raid_action = False

        # Storage Functions
        self.storage_card = False
        self.storage_arm = False
        self.storage_summon = False
        self.storage_title = False

        # Cards Functions
        self.equip_card = False
        self.dismantle_card = False
        self.trade_card = False
        self.card_storage = False
        self.market_card = False


        # Talisman Functions
        self.equip_talisman = False
        self.unequip_talisman = False


        # Arm Functions
        self.equip_arm = False
        self.arm_storage = False
        self.trade_arm = False
        self.dismantle_arm = False
        self.market_arm = False

        # Summon Functions
        self.equip_summon = False
        self.summon_storage = False
        self.trade_summon = False
        self.dismantle_summon = False
        self.market_summon = False


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

        # Register Functions
        self.register_start = False
        self.register_select = False
        self.register_action = False

        # Universe Lists Functions
        self.cards_list_action = False
        self.arms_list_action = False
        self.summons_list_action = False
        self.titles_list_action = False

        self.scenario_start = False
        self.raid_start = False
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
                    f"{self._uuid}|register",
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
                    f"{self._uuid}|quit",
                    f"{self._uuid}|market",
                    f"{self._uuid}|🎴cards",
                    f"{self._uuid}|🎗️titles",
                    f"{self._uuid}|🦾abilityarms",
                    f"{self._uuid}|🦾protectionarms",
                    f"{self._uuid}|🧬summons",
                    f"{self._uuid}|draw",
                    
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
            case "register":
                if self.register_action:
                    self.register_select = True
                    response = await self.activate_register_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
                    return
            case "callback":
                if self.callback:
                    return await self.callback(ctx)
                original_buttons = True
            case "🎴cards":
                if self.cards_list_action:
                    response = await self.activate_cards_list(ctx, self._message.embeds[0].title)
                    await self._message.edit(embeds=[response], components=[])
            case "🦾abilityarms":
                if self.arms_list_action:
                    response = await self.activate_arms_list(ctx, self._message.embeds[0].title, "ability")
                    await self._message.edit(embeds=[response], components=[])
                    return
            case "🦾protectionarms":
                if self.arms_list_action:
                    response = await self.activate_arms_list(ctx, self._message.embeds[0].title, "protections")
                    await self._message.edit(embeds=[response], components=[])
                    return
            case "🧬summons":
                if self.summons_list_action:
                    response = await self.activate_summons_list(ctx, self._message.embeds[0].title)
                    await self._message.edit(embeds=[response], components=[])
            case "🎗️titles":
                if self.titles_list_action:
                    response = await self.activate_titles_list(ctx, self._message.embeds[0].title)
                    await self._message.edit(embeds=[response], components=[])
            case "equip":
                if self.talisman_action:
                    self.equip_talisman = True
                    response = await self.activate_talisman_action(ctx, self._message.embeds[0], self.equip_talisman)
                    await self._message.edit(embeds=[response], components=[])
                if self.titles_action:
                    self.equip_title = True
                    response = await self.activate_title_action(ctx, self._message.embeds[0].title, self.equip_title)
                    await self._message.edit(embeds=[response], components=[])
                if self.cards_action:
                    self.equip_card = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.equip_card)
                if self.arms_action:
                    self.equip_arm = True
                    response = await self.activate_arm_action(ctx, self._message.embeds[0].title, self.equip_arm)
                    await self._message.edit(embeds=[response], components=[])
                if self.summon_action:
                    self.equip_summon = True
                    response = await self.activate_summon_action(ctx, self._message.embeds[0].title, self.equip_summon)
            case "storage":
                if self.titles_action:
                    self.title_storage = True
                    response = await self.activate_title_action(ctx, self._message.embeds[0].title, self.title_storage)
                    if response:
                        await self._message.edit(embeds=[response], components=[])
                if self.cards_action:
                    self.card_storage = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.card_storage)
                if self.arms_action:
                    self.arm_storage = True
                    response = await self.activate_arm_action(ctx, self._message.embeds[0].title, self.arm_storage)
            case "unequip":
                if self.talisman_action:
                    self.equip_talisman = True
                    response = await self.activate_talisman_action(ctx, self._message.embeds[0], self.equip_talisman)
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
            case "market":
                if self.cards_action:
                    self.market_card = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.market_card)
                    await self._message.delete()
                if self.arms_action:
                    self.market_arm = True
                    response = await self.activate_arm_action(ctx, self._message.embeds[0].title, self.market_arm)
                    await self._message.delete()
                if self.summon_action:
                    self.market_summon = True
                    response = await self.activate_summon_action(ctx, self._message.embeds[0].title, self.market_summon)
                    await self._message.delete()
            case "draw":
                if self.storage_card:
                    response = await self.activate_storage_action(ctx, "draw", "card")
                    await self._message.delete()
                if self.storage_arm:
                    response = await self.activate_storage_action(ctx, "draw", "arm")
                    await self._message.delete()
                if self.storage_summon:
                    response = await self.activate_storage_action(ctx, "draw", "summon")
                    await self._message.delete()
                if self.storage_title:
                    response = await self.activate_storage_action(ctx, "draw", "title")
                    await self._message.delete()
            case "trade":
                if self.cards_action:
                    self.trade_card = True
                    response = await self.activate_card_action(ctx, self._message.embeds[0].title, self.trade_card)
                    await self._message.delete()
                if self.arms_action:
                    self.trade_arm = True
                    response = await self.activate_arm_action(ctx, self._message.embeds[0].title, self.trade_arm)
                    await self._message.delete()
                if self.summon_action:
                    self.trade_summon = True
                    response = await self.activate_summon_action(ctx, self._message.embeds[0].title, self.trade_summon)
                    await self._message.delete()
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
                if self.scenario_action:
                    self.scenario_start = True 
                    embed = Embed(title="Starting Scenario...", description="Please wait...")
                    await ctx.send(embed=embed, components=[], delete_after=5)
                    response = await self.activate_scenario_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
                if self.raid_action:
                    self.raid_start = True
                    embed = Embed(title="Starting Raid...", description="Please wait...")
                    await ctx.send(embed=embed, components=[], delete_after=5)
                    response = await self.activate_raid_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
                if self.universe_tale_action or self.universe_dungeon_action:
                    if self.universe_tale_action:
                        self.universe_tale_start = True
                    if self.universe_dungeon_action:
                        self.universe_dungeon_start = True
                    response = await self.activate_universe_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
            case "quit":
                if self.scenario_action:
                    self.quit = True
                    response = await self.activate_scenario_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
                if self.raid_action:
                    self.quit = True
                    response = await self.activate_raid_action(ctx, self._message.embeds[0].title)
                    await self._message.delete()
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

        if action_type == "Raid":
            self.raid_action = True
        
        if action_type == "Register":
            self.register_action = True

        if action_type == "UniverseLists":
            self.cards_list_action = True
            self.arms_list_action = True
            self.summons_list_action = True
            self.titles_list_action = True

        if action_type == "Card Storage":
            self.storage_card = True
        
        if action_type == "Arm Storage":
            self.storage_arm = True

        if action_type == "Summon Storage":
            self.storage_summon = True

        if action_type == "Title Storage":
            self.storage_title = True

    
    async def activate_talisman_action(self, ctx, data, action: str):
        user_query = {'DID': str(ctx.author.id)}
        user_data = db.queryUser(user_query)
        user = crown_utilities.create_player_from_data(user_data)
        # data.title is the talisman name
        embed = Embed(title=f"{data.title} Talisman {data.title.capitalize()} Successfully Completed")
        quest_message = await Quests.milestone_check(user, "EQUIPPED_TALISMAN", 1)
        if quest_message:
            embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)


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
            
            embed = Embed(title=f"{ctx.author.display_name} wants to join {guild['TEAM_DISPLAY_NAME']}", description=f"Owner, Officers, or Captains - Please accept or deny")
            
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
                    team_query = {'TEAM_NAME': guild['TEAM_NAME'].lower()}
                    new_value_query = {'$push': {'MEMBERS': player['DID']}}
                    response = db.addTeamMember(team_query, new_value_query, player['DID'], guild['TEAM_DISPLAY_NAME'])
                    
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
            response = await self.equip_title_function(ctx, title)
            return response

        if self.title_storage:
            response = await self.title_storage_function(ctx, title)
            return response
        
        if self.charge_title_function:
            response = self.charge_title_function(ctx, title)
            return response
            

    async def equip_title_function(self, ctx, title):
        try:
            user = db.queryUser({'DID': str(ctx.author.id)})
            player = crown_utilities.create_player_from_data(user)
            if title in user['TITLES']:
                user_query = {'DID': str(ctx.author.id)}
                response = db.updateUserNoFilter(user_query, {'$set': {'TITLE': title}})
                if response:
                    embed = Embed(title=f"🎗️ Title Equipped", description=f"Title {title} equipped")
                    quest_message = await Quests.milestone_check(player, "EQUIPPED_TITLE", 1)
                    if quest_message:
                        embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

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
                    user = db.queryUser({'DID': str(ctx.author.id)})
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
        if self.equip_arm:
            response = await self.equip_arm_function(ctx, arm)
            return response
        
        if action == self.arm_storage:
            response = await self.arm_storage_function(ctx, arm)
            return response
        
        if action == self.dismantle_arm:
            response = await self.dismantle_arm_function(ctx, arm)
            return response

        if self.market_arm:
            response = await self.market_arm_function(ctx, arm)
            return response

        if self.trade_arm:
            response = await self.trade_arm_function(ctx, arm)
            return response


    async def market_arm_function(self, ctx, arm):
        try:
            _uuid = generate_6_digit_code()
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            arm_data = db.queryArm({"ARM": arm})
            arm = crown_utilities.create_arm_from_data(arm_data)
            exists_on_trade_already = crown_utilities.arm_being_traded(user['DID'], arm.name)
            if exists_on_trade_already:
                embed = Embed(title=f"🦾 Arm is currently being Traded", description=f"{arm.name} is currently being traded. Please remove it from the trade before adding it to the market.")
                await ctx.send(embed=embed)
                return
            exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": arm.name})
            confirm_buttons = [
                        Button(
                            style=ButtonStyle.GREEN,
                            label="Yes",
                            custom_id=f"{self._uuid}|yes"
                        ),
                        Button(
                            style=ButtonStyle.RED,
                            label="No",
                            custom_id=f"{self._uuid}|no"
                        )
                    ]
            if exists_on_market_already:
                components = ActionRow(*confirm_buttons)
                embed = Embed(title=f"🏷️ Arm is Currently On The Market", description=f"{arm.name} is still on the market. Would you like to remove it from the market?")
                message = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = db.deleteMarketEntry({"ITEM_OWNER": player.did, "ITEM_NAME": arm.name})
                        embed = Embed(title=f"🏷️ Success", description=f"{arm.name} has been removed from the market.")
                        await message.edit(embed=embed, components=[])
                        return
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        await message.delete()
                        return

                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title=f"🏷️ Arm Not Removed from the Market", description=f"Failed to remove {arm.name} from the market - Error Logged")
                    await ctx.send(embed=embed)
                    return


            if arm.name == player.equipped_arm:
                embed = Embed(title=f"🏷️ Arm Not Added to Market", description=f"Failed to add {arm.name} to the market as it is currently equipped")
                await ctx.send(embed=embed)
                return
            
             # Since the card is not currently on the market, create the market object and post it to the market
            embed = Embed(title=f"🏷️ Price For Arm", description=f"How much would you like to sell {arm.name} for?")
            message = await ctx.send(embed=embed)

            def check(event):
                return event.message.author.id == ctx.author.id

            try:
                response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                price = int(response.message.content)

                market_object = {
                    "MARKET_CODE": str(_uuid),
                    "MARKET_TYPE": "ARM",
                    "ITEM_NAME": arm.name,
                    "CARD_LEVEL": 0,
                    "ARM_DURABILITY": 25,
                    "SUMMON_LEVEL": 0,
                    "BOND_LEVEL": 0,
                    "PRICE": price,
                    "ITEM_OWNER": player.did,
                }

                components = ActionRow(*confirm_buttons)

                embed = Embed(title=f"🏷️ Market Code - {market_object['MARKET_CODE']}", description=f"Would you like to add {arm.name} to the market for 🪙 {'{:,}'.format(price)}")
                msg = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = db.createMarketEntry(market_object)
                        quest_response = await Quests.quest_check(player, "MARKETPLACE")
                        if response:
                            embed = Embed(title=f"🏷️ Market Code - {market_object['MARKET_CODE']}", description=f"{arm.name} has been added to the market for 🪙 {'{:,}'.format(price)}")
                            if quest_response:
                                embed.add_field(name="Quest Complete", value=quest_response)
                            await msg.edit(embed=embed, components=[])
                            return
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        embed = Embed(title=f"🏷️ Arm Not Added to Market", description=f"Failed to add {arm.name} to the market as it is already on the market")
                        await msg.edit(embed=embed, components=[])
                        return

                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title=f"🏷️ Arm Not Added to Market", description=f"Failed to add {arm.name} to the market - Error Logged")
                    await ctx.send(embed=embed)
                    return
            except Exception as ex:
                custom_logging.debug(ex)
                embed = Embed(title=f"🏷️ Arm Not Added to Market", description=f"Failed to add {arm.name} to the market - Error Logged")
                await ctx.send(embed=embed)
                return

        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title=f"🏷️ Arm Not Added to Market", description=f"Failed to add arm to the market - Error Logged")
            await ctx.send(embed=embed)
            return
    

    async def equip_arm_function(self, ctx, arm_name):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            exists_on_trade_already = crown_utilities.arm_being_traded(user['DID'], arm_name)
            if exists_on_trade_already:
                embed = Embed(title=f"🦾 Arm is currently being Traded", description=f"{arm_name} is currently being traded. Please remove it from the trade before equipping it.")
                await ctx.send(embed=embed)
                return

            exists_on_market_already = db.queryMarket({"ITEM_OWNER": user['DID'], "ITEM_NAME": arm_name})
            if exists_on_market_already:
                embed = Embed(title=f"🏷️ Arm is on the Market", description=f"{arm_name} is still on the market. Please remove it from the market before equipping it")
                await ctx.send(embed=embed)
                return

            for arm in player.arms:
                if arm['ARM'] == arm_name:
                    response = db.updateUserNoFilter(user_query, {'$set': {'ARM': arm_name}})
                    if response:
                        embed = Embed(title=f"🦾 Arm Equipped", description=f"Arm {arm_name} equipped")
                        quest_message = await Quests.milestone_check(player, "EQUIPPED_ARM", 1)
                        if quest_message:
                            embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

                        return embed
                    else:
                        embed = Embed(title=f"🦾 Arm Not Equipped", description=f"Failed to equip arm {arm_name}")
                        return embed
            embed = Embed(title=f"🦾 Arm Not Equipped", description=f"Failed to equip arm {arm_name} - Arm not available")
            return embed
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title=f"🦾 Arm Not Equipped", description=f"Failed to equip arm {arm_name} - Error Logged")
            return embed
    

    async def arm_storage_function(self, ctx, arm):
        print("Arm Storage Function")
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)
        exists_on_trade_already = crown_utilities.arm_being_traded(user['DID'], arm)
        if exists_on_trade_already:
            embed = Embed(title=f"🦾 Arm is currently being Traded", description=f"{arm} is currently being traded. Please remove it from the trade before storaging it.")
            await ctx.send(embed=embed)
            return

        exists_on_market_already = db.queryMarket({"ITEM_OWNER": user['DID'], "ITEM_NAME": arm})
        if exists_on_market_already:
            embed = Embed(title=f"🏷️ Arm is on the Market", description=f"{arm} is still on the market. Please remove it from the market before equipping it")
            await ctx.send(embed=embed)
            return
        if arm == player.equipped_arm:
            embed = Embed(title=f"🦾 Arm Storage", description=f"Arm {arm} is equipped - Please unequip arm before storing")
            await ctx.send(embed=embed)
            return
        
        for arms in player.arms:
            if arms['ARM'].strip() == arm.strip():
                print(f"Arm: {arms['ARM']}")
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
                            if player.equipped_arm == arm['ARM']:
                                embed = Embed(title=f"🦾 Arm Storage", description=f"Arm {arm['ARM']} is equipped - Please unequip arm before storing")
                                await msg.edit(embed=embed, components=[])
                                return
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
                            if player.astorage_length <= (player.storage_type * 15):
                                query = {'DID': str(ctx.author.id)}
                                print(f"Arm: {arms['ARM']}")

                                update_storage_query = {
                                    '$pull': {'ARMS': {'ARM' : arms['ARM']}},
                                    '$addToSet': {'ASTORAGE': { 'ARM' : arms['ARM'], 'DUR' : int(arms['DUR'])}},
                                }
                                response = db.updateUserNoFilter(query, update_storage_query)
                                
                                embed = Embed(title=f"🦾 Arm Storage", description=f"{arms['ARM']} has been added to storage")
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
                    custom_logging.debug(ex)
                    await ctx.send("There's an issue with your Arms list. Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92", ephemeral=True)
                    return


    async def trade_arm_function(self, ctx, arm):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            arm_data = db.queryArm({"ARM": arm})
            arm = crown_utilities.create_arm_from_data(arm_data)
            if arm.name == player.equipped_arm:
                embed = Embed(title=f"🦾 Arm Storage", description=f"Arm {arm.name} is equipped - Please unequip arm before trading")
                await ctx.send(embed=embed)
                return
            exists_on_trade_already = crown_utilities.arm_being_traded(user['DID'], arm.name)
            exists_on_market_already = db.queryMarket({"ITEM_OWNER": user['DID'], "ITEM_NAME": arm.name})
            if exists_on_market_already:
                embed = Embed(title=f"🏷️ Arm is on the Market", description=f"{arm.name} is still on the market. Please remove it from the market before trading it")
                await ctx.send(embed=embed)
                return


            if exists_on_trade_already:
                embed = Embed(title=f"🦾 Arm is currently being Traded", description=f"{arm.name} is currently being traded. Please remove it from the trade before adding it to the market.")
                await ctx.send(embed=embed)
                return
            trade_query = {'MERCHANT': player.did, 'OPEN': True}
            trade_data = db.queryTrade(trade_query)
            if not trade_data:
                trade_query = {'BUYER': player.did, 'OPEN': True}
                trade_data = db.queryTrade(trade_query)
            if trade_data:
                for a in player.arms:
                    if a['ARM'] == arm.name:
                        arm.durability = a['DUR']

                trade_object = {
                    "DID": player.did,
                    "NAME": arm.name,
                    "DUR": arm.durability,
                }
                response = db.updateTrade(trade_query, {'$push': {'ARMS': trade_object}})
                if response:
                    # Make embed for being added to Trade
                    embed = Embed(title=f"🦾 Arm Added to Trade", description=f"{arm.name} has been added to the trade")
                    await ctx.send(embed=embed)
                    return
            else:
                # Make embed for there not being a Trade open at this time
                embed = Embed(title=f"🦾 Arm Not Added to Trade", description=f"There is no trade open at this time")
                await ctx.send(embed=embed)
                return
        except Exception as ex:
            custom_logging.debug(ex)
            # Make embed for not being added to Trade
            embed = Embed(title=f"🦾 Arm Not Added to Trade", description=f"Failed to add arm to the trade - Error Logged")
            await ctx.send(embed=embed)
            return
        

    async def dismantle_arm_function(self, ctx, arm_title):
        await ctx.defer()
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            exists_on_trade_already = crown_utilities.arm_being_traded(user['DID'], arm_title)
            if exists_on_trade_already:
                embed = Embed(title=f"🦾 Arm is currently being Traded", description=f"{arm_title} is currently being traded. Please remove it from the trade before dismantling it.")
                await ctx.send(embed=embed)
                return

            exists_on_market_already = db.queryMarket({"ITEM_OWNER": user['DID'], "ITEM_NAME": arm_title})
            if exists_on_market_already:
                embed = Embed(title=f"🏷️ Arm is on the Market", description=f"{arm_title} is still on the market. Please remove it from the market before equipping it")
                await ctx.send(embed=embed)
                return
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
                    response = await self.trade_card_action(ctx, card)
                    self.trade_card = False

                if self.market_card:
                    response = await self.market_card_action(ctx, card)
                    self.market_card = False
        except Exception as e:
            print(e)
            return None
    

    async def equip_card_action(self, ctx, card):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = await asyncio.to_thread(db.queryUser, user_query)

            # Check if card is being traded
            if crown_utilities.card_being_traded(user['DID'], card):
                embed = Embed(title="🎴 Card is being Traded", description=f"{card} is still being traded. Please remove it from the trade before equipping it")
                await ctx.send(embed=embed)
                return

            # Check if card is on the market
            if await asyncio.to_thread(db.queryMarket, {"ITEM_OWNER": user['DID'], "ITEM_NAME": card}):
                embed = Embed(title="🏷️ Card is on the Market", description=f"{card} is still on the market. Please remove it from the market before equipping it")
                await ctx.send(embed=embed)
                return

            # Check if card is already equipped
            if card == user['CARD']:
                embed = Embed(title="🎴 Card Equipped", description=f"{card} is already equipped")
                await ctx.send(embed=embed)
                return

            # Equip card if it exists in user's inventory
            if card in user['CARDS']:
                response = await asyncio.to_thread(db.updateUserNoFilter, user_query, {'$set': {'CARD': card}})
                player = crown_utilities.create_player_from_data(user)
                if response:
                    embed = Embed(title="🎴 Card Equipped", description=f"{card} has been equipped")
                    quest_message = await Quests.milestone_check(player, "EQUIPPED_CARD", 1)
                    if quest_message:
                        embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

                    await ctx.send(embed=embed)
                else:
                    embed = Embed(title="🎴 Card Not Equipped", description=f"Failed to equip {card}. Please try again.")
                    await ctx.send(embed=embed)
            else:
                embed = Embed(title="🎴 Card Not Equipped", description=f"Failed to equip {card} as it is not in your inventory")
                await ctx.send(embed=embed)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🎴 Card Not Equipped", description=f"Failed to equip {card} - Error Logged")
            await ctx.send(embed=embed)


    async def market_card_action(self, ctx, card):
        try:
            _uuid = generate_6_digit_code()
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            exists_on_trade_already = crown_utilities.card_being_traded(user['DID'], card)
            if exists_on_trade_already:
                embed = Embed(title=f"🎴 Card is being Traded", description=f"{card} is still being traded. Please remove it from the trade before addint it to the market")
                await ctx.send(embed=embed)
                return

            player = crown_utilities.create_player_from_data(user)
            card_data = db.queryCard({'NAME': card})
            card = crown_utilities.create_card_from_data(card_data)
            card.set_card_level_buffs(player.card_levels)
            exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": card.name})
            confirm_buttons = [
                        Button(
                            style=ButtonStyle.GREEN,
                            label="Yes",
                            custom_id=f"{self._uuid}|yes"
                        ),
                        Button(
                            style=ButtonStyle.RED,
                            label="No",
                            custom_id=f"{self._uuid}|no"
                        )
                    ]
            if exists_on_market_already:
                components = ActionRow(*confirm_buttons)
                embed = Embed(title=f"🏷️ Card is Currently On The Market", description=f"{card.name} is still on the market. Would you like to remove it from the market?")
                message = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = db.deleteMarketEntry({"ITEM_OWNER": player.did, "ITEM_NAME": card.name})
                        embed = Embed(title=f"🏷️ Success", description=f"{card.name} has been removed from the market.")
                        await message.edit(embed=embed, components=[])
                        return
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        await message.delete()
                        return

                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title=f"🏷️ Card Not Removed from the Market", description=f"Failed to remove {card.name} from the market - Error Logged")
                    await ctx.send(embed=embed)
                    return


            if card.name == player.equipped_card:
                embed = Embed(title=f"🏷️ Card Not Added to Market", description=f"Failed to add {card.name} to the market as it is currently equipped")
                await ctx.send(embed=embed)
                return
            
             # Since the card is not currently on the market, create the market object and post it to the market
            embed = Embed(title=f"🏷️ Price For Card", description=f"How much would you like to sell your level {str(card.card_lvl)} {card.name} for?")
            message = await ctx.send(embed=embed)

            def check(event):
                return event.message.author.id == ctx.author.id

            try:
                response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                price = int(response.message.content)

                market_object = {
                    "MARKET_CODE": str(_uuid),
                    "MARKET_TYPE": "CARD",
                    "ITEM_NAME": card.name,
                    "CARD_LEVEL": card.card_lvl,
                    "ARM_DURABILITY": 0,
                    "SUMMON_LEVEL": 0,
                    "BOND_LEVEL": 0,
                    "PRICE": price,
                    "ITEM_OWNER": player.did,
                }

                components = ActionRow(*confirm_buttons)

                embed = Embed(title=f"🏷️ Market Code - {market_object['MARKET_CODE']}", description=f"Would you like to add {card.name} to the market for 🪙 {'{:,}'.format(price)}")
                msg = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        quest_response = await Quests.quest_check(player, "MARKETPLACE")
                        milestone_response = await Quests.milestone_check(player, "MARKETPLACE", 1)
                        response = db.createMarketEntry(market_object)
                        if response:
                            embed = Embed(title=f"🏷️ Market Code - {market_object['MARKET_CODE']}", description=f"{card.name} has been added to the market for 🪙 {'{:,}'.format(price)}")
                            if quest_response:
                                embed.add_field(name="🏷️ Quest Completed", value=f"{quest_response}")
                            if milestone_response:
                                embed.add_field(name="🏆 Milestone Completed", value=f"{milestone_response}")
                            await msg.edit(embed=embed, components=[])
                            return
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        embed = Embed(title=f"🏷️ Card Not Added to Market", description=f"Failed to add {card.name} to the market as it is already on the market")
                        await msg.edit(embed=embed, components=[])
                        return

                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title=f"🏷️ Card Not Added to Market", description=f"Failed to add {card.name} to the market - Error Logged")
                    await ctx.send(embed=embed)
                    return
            except Exception as ex:
                custom_logging.debug(ex)
                embed = Embed(title=f"🏷️ Card Not Added to Market", description=f"Failed to add {card.name} to the market - Error Logged")
                await ctx.send(embed=embed)
                return

        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title=f"🏷️ Card Not Added to Market", description=f"Failed to add {card.name} to the market - Error Logged")
            await ctx.send(embed=embed)
            return
             
    
    async def dismantle_card_action(self, ctx, card):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            card_data = db.queryCard({'NAME': card})
            exists_on_trade_already = crown_utilities.card_being_traded(user['DID'], card)
            if exists_on_trade_already:
                embed = Embed(title=f"🎴 Card is being Traded", description=f"{card} is still being traded. Please remove it from the trade before dismantling it")
                await ctx.send(embed=embed)
                return

            exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": card})
            if exists_on_market_already:
                embed = Embed(title=f"🏷️ Card is on the Market", description=f"Failed to dismantle {card} as it is currently on the market")
                await ctx.send(embed=embed)
                return
            c = crown_utilities.create_card_from_data(card_data)
            c.set_card_level_buffs(player.card_levels)
            if c.card_lvl == 0:
                c.card_lvl = 1
            dismantle_amount = (5000 * c.tier) * c.card_lvl
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
                embed = Embed(title=f"🎴 Dismantle Card", description=f"Are you sure you want to dismantle {card} for 💎 & 🪙 {dismantle_amount:,} gems and coin?")
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
                        gem_amount = round(.10 * dismantle_amount)
                        response = player.save_gems(c.universe, gem_amount)

                        if response:

                            remove_card_response = player.remove_card(c)
                            await crown_utilities.bless(dismantle_amount, player.did)
                            if remove_card_response:
                                embed = Embed(title=f"🎴 Card Dismantled", description=f"{c.name} has been dismantled for 🪙 {dismantle_amount:,} Coin & 💎 {gem_amount:,} {c.universe_crest} {c.universe} Gems.")
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


    async def trade_card_action(self, ctx, card):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            card_data = db.queryCard({'NAME': card})
            c = crown_utilities.create_card_from_data(card_data)
            c.set_card_level_buffs(player.card_levels)
            if c.name == player.equipped_card:
                embed = Embed(title=f"🎴 Card Not Added to Trade", description=f"Failed to add {c.name} to the trade as it is currently equipped")
                await ctx.send(embed=embed)
                return
            exists_on_trade_already = crown_utilities.card_being_traded(user['DID'], card)
            if exists_on_trade_already:
                embed = Embed(title=f"🎴 Card is being Traded", description=f"{card} is already being traded.")
                await ctx.send(embed=embed)
                return

            exists_on_market_already = db.queryMarket({"ITEM_OWNER": user['DID'], "ITEM_NAME": card})
            if exists_on_market_already:
                embed = Embed(title=f"🏷️ Card is on the Market", description=f"{card} is still on the market. Please remove it from the market before trading it")
                await ctx.send(embed=embed)
                return

            trade_query = {'MERCHANT': player.did, 'OPEN': True}
            trade_data = db.queryTrade(trade_query)
            if not trade_data:
                trade_query = {'BUYER': player.did, 'OPEN': True}
                trade_data = db.queryTrade(trade_query)

            if trade_data:
                trade_object = {
                    "DID": player.did,
                    "NAME": c.name,
                    "LVL": c.card_lvl,
                    "TIER": c.tier,
                }
                response = db.updateTrade(trade_query, {'$push': {'CARDS': trade_object}})
                if response:
                    # Make embed for being added to Trade
                    embed = Embed(title=f"🎴 Card Added to Trade", description=f"{c.name} has been added to the trade")
                    await ctx.send(embed=embed)
                    return
            else:
                # Make embed for there not being a Trade open at this time
                embed = Embed(title=f"🎴 Card Not Added to Trade", description=f"There is no trade open at this time")
                await ctx.send(embed=embed)
                return
        except Exception as ex:
            custom_logging.debug(ex)
            # Make embed for not being added to Trade
            embed = Embed(title=f"🎴 Card Not Added to Trade", description=f"Failed to add {c.name} to the trade - Error Logged")
            await ctx.send(embed=embed)
            return


    async def card_storage_function(self, ctx, card):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)
        exists_on_trade_already = crown_utilities.card_being_traded(user['DID'], card)
        if exists_on_trade_already:
            embed = Embed(title=f"🎴 Card is being Traded", description=f"{card} is still being traded. Please remove it from the trade before storaging it")
            await ctx.send(embed=embed)
            return

        exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": card})
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
    STORAGE FUNCTIONS
    This section contains all the functions related to storage
    """
    async def activate_storage_action(self, ctx, action, action_type):
        try:
            if action == "draw":
                response = await self.draw_storage_action(ctx, action_type)
                self.storage_card = False
                self.storage_arm = False
                self.storage_summon = False
                self.storage_title = False
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"📦 Storage Activation Failed", description=f"Failed to activate storage - Error Logged")
            await ctx.send(embed=embed)


    async def draw_storage_action(self, ctx, action_type):
        try:
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            if action_type == "card":
                embed = Embed(title=f"🎴 Card Storage", description=f"Which card would you like to move from storage?\nPlease use the [number] from the storage card list.")
                message = await ctx.send(embed=embed)

                def check(event):
                    return event.message.author.id == ctx.author.id

                try:
                    response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                    option = validate_and_convert(response.message.content)
                    # If the option variable is a string and not an array then it's an error message
                    # Create an embed and edit the message with the error message
                    if isinstance(option, str):
                        embed = Embed(title=f"🎴 Card Storage", description=f"{option}")
                        await message.edit(embed=embed)
                        return
                    return_message = ""

                    for number in option:    
                        storage_card = player.storage[number]
                        exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": storage_card})
                        if exists_on_market_already:
                            embed = Embed(title=f"🏷️ Card is on the Market", description=f"{storage_card} is still on the market. Please remove it from the market before drawing it")
                            await message.edit(embed=embed)
                            return
                        
                        exists_on_trade_already = crown_utilities.card_being_traded(user['DID'], storage_card)
                        if exists_on_trade_already:
                            embed = Embed(title=f"🎴 Card is being Traded", description=f"{storage_card} is still being traded. Please remove it from the trade before storaging it")
                            await ctx.send(embed=embed)
                            return
                        if storage_card:
                            # Draw Card
                            update_storage_query = {
                                            '$pull': {'STORAGE': storage_card},
                                            '$addToSet': {'CARDS': storage_card},
                                        }
                            response = db.updateUserNoFilter(user_query, update_storage_query)
                            return_message += f"🎴 {storage_card} has been drawn from storage\n"
                        else:
                            return_message += f"🎴 Failed to draw {storage_card} - Invalid card number\n"
                    embed = Embed(title=f"🎴 Card Storage", description=f"{return_message}")
                    await message.edit(embed=embed)
                    return

                except asyncio.TimeoutError:
                    embed = Embed(title=f"🎴 Card Storage", description=f"Failed to draw cards - Timed Out")
                    await message.edit(embed=embed, components=[])
                    return                
            if action_type == "arm":
                embed = Embed(title=f"🦾 Arm Storage", description=f"Which arm would you like to move from storage?\nPlease use the [number] from the storage arm list.")
                message = await ctx.send(embed=embed)

                def check(event):
                    return event.message.author.id == ctx.author.id

                try:
                    response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                    option = validate_and_convert(response.message.content)
                    # If the option variable is a string and not an array then it's an error message
                    # Create an embed and edit the message with the error message
                    if isinstance(option, str):
                        embed = Embed(title=f"🦾 Arm Storage", description=f"{option}")
                        await message.edit(embed=embed)
                        return
                    return_message = ""

                    for number in option:    
                        storage_arm = player.astorage[number]
                        exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": storage_arm['ARM']})
                        if exists_on_market_already:
                            embed = Embed(title=f"🏷️ Arm is on the Market", description=f"{storage_arm['ARM']} is still on the market. Please remove it from the market before drawing it")
                            await message.edit(embed=embed)
                            return
                        
                        exists_on_trade_already = crown_utilities.arm_being_traded(user['DID'], storage_arm['ARM'])
                        if exists_on_trade_already:
                            embed = Embed(title=f"🦾 Arm is being Traded", description=f"{storage_arm['ARM']} is still being traded. Please remove it from the trade before storaging it")
                            await ctx.send(embed=embed)
                            return
                        if storage_arm:
                            # Draw Card
                            update_storage_query = {
                                            '$pull': {'ASTORAGE': {'ARM': storage_arm['ARM']}},
                                            '$addToSet': {'ARMS': {'ARM': storage_arm['ARM'], 'DUR': storage_arm['DUR']}},
                                        }
                            response = db.updateUserNoFilter(user_query, update_storage_query)
                            return_message += f"🦾 {storage_arm['ARM']} has been drawn from storage\n"
                        else:
                            return_message += f"🦾 Failed to draw {storage_arm['ARM']} - Invalid arm number\n"
                    embed = Embed(title=f"🦾 Arm Storage", description=f"{return_message}")
                    await message.edit(embed=embed)
                    return
                except asyncio.TimeoutError:
                    embed = Embed(title=f"🦾 Arm Storage", description=f"Failed to draw item from Storage - Error Logged")
            if action_type == "title":
                embed = Embed(title=f"🎗️ Title Storage", description=f"Which title would you like to move from storage?\nPlease use the [number] from the storage title list.")
                message = await ctx.send(embed=embed)

                def check(event):
                    return event.message.author.id == ctx.author.id

                try:
                    response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                    option = validate_and_convert(response.message.content)
                    # If the option variable is a string and not an array then it's an error message
                    # Create an embed and edit the message with the error message
                    if isinstance(option, str):
                        embed = Embed(title=f"🎗️ Title Storage", description=f"{option}")
                        await message.edit(embed=embed)
                        return
                    return_message = ""

                    for number in option:    
                        storage_title = player.tstorage[number]
                        if storage_title:
                            # Draw Card
                            update_storage_query = {
                                            '$pull': {'TSTORAGE': storage_title},
                                            '$addToSet': {'TITLES': storage_title},
                                        }
                            response = db.updateUserNoFilter(user_query, update_storage_query)
                            return_message += f"🎗️ {storage_title} has been drawn from storage\n"
                        else:
                            return_message += f"🎗️ Failed to draw {storage_title} - Invalid title number\n"
                    embed = Embed(title=f"🎗️ Title Storage", description=f"{return_message}")
                    await message.edit(embed=embed)
                    return

                except asyncio.TimeoutError:
                    embed = Embed(title=f"🎗️ Title Storage", description=f"Failed to draw item from Storage - Error Logged")
                    await message.edit(embed=embed)
                    return
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"Storage Failure", description=f"Failed to draw item from Storage - Error Logged")
            await ctx.send(embed=embed)
            return



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

                if self.market_summon:
                    response = await self.market_summon_action(ctx, summon)
                    self.market_summon = False

                if self.trade_summon:
                    response = await self.trade_summon_action(ctx, summon)
                    self.trade_summon = False

        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🔮 Summon Activation Failed", description=f"Failed to activate {summon} - Error Logged")
            await ctx.send(embed=embed)


    async def market_summon_action(self, ctx, summon_title):
        try:
            _uuid = generate_6_digit_code()
            user_query = {'DID': str(ctx.author.id)}
            user = db.queryUser(user_query)
            player = crown_utilities.create_player_from_data(user)
            summon_data = db.querySummon({'PET': summon_title})
            summon = crown_utilities.create_summon_from_data(summon_data)
            for s in player.summons:
                if s['NAME'] == summon_title:
                    summon.level = s['LVL']
                    summon.bond = s['BOND']
            exists_on_trade_already = crown_utilities.summon_being_traded(user['DID'], summon_title)
            if exists_on_trade_already:
                embed = Embed(title=f"🧬 Summon is being Traded", description=f"{summon_title} is still being traded. Please remove it from the trade before adding it to the market")
                await ctx.send(embed=embed)
                return
            exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": summon.name})
            confirm_buttons = [
                        Button(
                            style=ButtonStyle.GREEN,
                            label="Yes",
                            custom_id=f"{self._uuid}|yes"
                        ),
                        Button(
                            style=ButtonStyle.RED,
                            label="No",
                            custom_id=f"{self._uuid}|no"
                        )
                    ]
            if exists_on_market_already:
                components = ActionRow(*confirm_buttons)
                embed = Embed(title=f"🏷️ Summon is Currently On The Market", description=f"{summon.name} is still on the market. Would you like to remove it from the market?")
                message = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = db.deleteMarketEntry({"ITEM_OWNER": player.did, "ITEM_NAME": summon.name})
                        embed = Embed(title=f"🏷️ Success", description=f"{summon.name} has been removed from the market.")
                        await message.edit(embed=embed, components=[])
                        return
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        await message.delete()
                        return

                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title=f"🏷️ Summon Not Removed from the Market", description=f"Failed to remove {summon.name} from the market - Error Logged")
                    await ctx.send(embed=embed)
                    return


            if summon.name == player.equipped_summon:
                embed = Embed(title=f"🏷️ Summon Not Added to Market", description=f"Failed to add {summon.name} to the market as it is currently equipped")
                await ctx.send(embed=embed)
                return
            
             # Since the card is not currently on the market, create the market object and post it to the market
            embed = Embed(title=f"🏷️ Price For Summon", description=f"How much would you like to sell {summon.name} for?")
            message = await ctx.send(embed=embed)

            def check(event):
                return event.message.author.id == ctx.author.id

            try:
                response = await self.client.wait_for('on_message_create', checks=check, timeout=120)
                price = int(response.message.content)

                market_object = {
                    "MARKET_CODE": str(_uuid),
                    "MARKET_TYPE": "SUMMON",
                    "ITEM_NAME": summon.name,
                    "CARD_LEVEL": 0,
                    "ARM_DURABILITY": 0,
                    "SUMMON_LEVEL": summon.level,
                    "BOND_LEVEL": summon.bond,
                    "PRICE": price,
                    "ITEM_OWNER": player.did,
                }

                components = ActionRow(*confirm_buttons)

                embed = Embed(title=f"🏷️ Market Code - {market_object['MARKET_CODE']}", description=f"Would you like to add {summon.name} to the market for 🪙 {'{:,}'.format(price)}")
                msg = await ctx.send(embed=embed, components=[components])

                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = db.createMarketEntry(market_object)
                        quest_response = await Quests.quest_check(player, "MARKETPLACE")
                        if response:
                            embed = Embed(title=f"🏷️ Market Code - {market_object['MARKET_CODE']}", description=f"{summon.name} has been added to the market for 🪙 {'{:,}'.format(price)}")
                            if quest_response:
                                embed.add_field(name="🏷️ Quest Completed", value=f"{quest_response}")
                            await msg.edit(embed=embed, components=[])
                            return
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        embed = Embed(title=f"🏷️ Summon Not Added to Market", description=f"Failed to add {summon.name} to the market as it is already on the market")
                        await msg.edit(embed=embed, components=[])
                        return

                except Exception as ex:
                    custom_logging.debug(ex)
                    embed = Embed(title=f"🏷️ Summon Not Added to Market", description=f"Failed to add {summon.name} to the market - Error Logged")
                    await ctx.send(embed=embed)
                    return
            except Exception as ex:
                custom_logging.debug(ex)
                embed = Embed(title=f"🏷️ Summon Not Added to Market", description=f"Failed to add {summon.name} to the market - Error Logged")
                await ctx.send(embed=embed)
                return

        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title=f"🏷️ Summon Not Added to Market", description=f"Failed to add {summon.name} to the market - Error Logged")
            await ctx.send(embed=embed)
            return
    

    async def equip_summon_action(self, ctx, summon_title):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)
        updated = False
        exists_on_trade_already = crown_utilities.summon_being_traded(user['DID'], summon_title)
        if exists_on_trade_already:
            embed = Embed(title=f"🧬 Summon is being Traded", description=f"{summon_title} is still being traded. Please remove it from the trade before equipping it")
            await ctx.send(embed=embed)
            return
        exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": summon_title})
        if exists_on_market_already:
            embed = Embed(title=f"🏷️ Summon is on the Market", description=f"{summon_title} is still on the market. Please remove it from the market before equipping it")
            await ctx.send(embed=embed)
            return

        if summon_title == player.equipped_summon:
            embed = Embed(title=f"🧬 Summon Not Equipped", description=f"{summon_title} is already equipped")
            await ctx.send(embed=embed)
            return
        for summon in player.summons:
            if summon_title == summon['NAME']:
                update_summon_query = {
                                '$set': {'PET': summon_title},
                            }
                response = db.updateUserNoFilter(user_query, update_summon_query)
                embed = Embed(title=f"🧬 Summon Equipped", description=f"Successfully equipped {summon_title}")
                quest_message = await Quests.milestone_check(player, "EQUIPPED_SUMMON", 1)
                if quest_message:
                    embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

                updated = True
                await ctx.send(embed=embed)
        
        if not updated:
            embed = Embed(title=f"🧬 Summon Not Equipped", description=f"Failed to equip {summon_title} as it is not in your inventory")
            await ctx.send(embed=embed)


    async def dismantle_summon_action(self, ctx, summon_title):
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        summon_data = db.querySummon({'PET': summon_title})
        player = crown_utilities.create_player_from_data(user)
        summon = crown_utilities.create_summon_from_data(summon_data)
        available_to_dismantle = False
        exists_on_trade_already = crown_utilities.summon_being_traded(user['DID'], summon_title)
        if exists_on_trade_already:
            embed = Embed(title=f"🧬 Summon is being Traded", description=f"{summon_title} is still being traded. Please remove it from the trade before dismantling it")
            await ctx.send(embed=embed)
            return
        exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": summon_title})
        if exists_on_market_already:
            embed = Embed(title=f"🏷️ Summon is on the Market", description=f"{summon_title} is still on the market. Please remove it from the market before equipping it")
            await ctx.send(embed=embed)
            return

        for s in player.summons:
            if summon_title == s['NAME']:
                available_to_dismantle = True
                break

        if summon_title == player.equipped_summon:
            embed = Embed(title=f"🧬 Summon Not Dismantled", description=f"{summon_title} is equipped and cannot be dismantled.")
            await ctx.send(embed=embed)
            return

        if not available_to_dismantle:
            embed = Embed(title=f"🧬 Summon Not Dismantled", description=f"{summon_title} is not in your inventory.")
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
            embed = Embed(title=f"🧬 Dismantle Card", description=f"Are you sure you want to dismantle {summon.name} for 💎 {summon.dismantle_amount} gems?")
            msg = await ctx.send(embed=embed, components=[components])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author

            try:
                button_ctx = await self.client.wait_for_component(components=[components], check=check, timeout=120)

                if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                    embed = Embed(title=f"🧬 Summon Not Dismantled", description=f"Cancelled dismantle of {summon.name}")
                    await msg.edit(embed=embed, components=[])
                    return

                if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                    response = player.save_gems(summon.universe, summon.dismantle_amount)

                    if response:
                        remove_card_response = player.remove_summon(summon.name)
                        if remove_card_response:
                            embed = Embed(title=f"🧬 Summon Dismantled", description=f"{summon.name} has been dismantled for 💎 {summon.dismantle_amount} {summon.universe_crest} {summon.universe} Gems")
                            await msg.edit(embed=embed, components=[])
                    else:
                        embed = Embed(title=f"🧬 Summon Not Dismantled", description=f"Failed to dismantle {summon.name} - Error Logged")
                        await msg.edit(embed=embed, components=[])

            except asyncio.TimeoutError:
                embed = Embed(title=f"🧬 Summon Not Dismantled", description=f"Failed to dismantle {summon.name} - Timed Out")
                await msg.edit(embed=embed, components=[])
                return
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🔮 Summon Dismantle Failed", description=f"Failed to dismantle {summon.name} - Error Logged")
            await msg.edit(embed=embed)


    async def trade_summon(self, ctx, summon_title):
        '''
        Trade a summon
        '''
        user_query = {'DID': str(ctx.author.id)}
        user = db.queryUser(user_query)
        player = crown_utilities.create_player_from_data(user)
        summon_data = db.querySummon({'PET': summon_title})
        summon = crown_utilities.create_summon_from_data(summon_data)
        if summon.name == player.equipped_summon:
            embed = Embed(title=f"🧬 Summon Not Added to Trade", description=f"Failed to add {summon.name} to the trade as it is currently equipped")
            await ctx.send(embed=embed)
            return
        exists_on_trade_already = crown_utilities.summon_being_traded(user['DID'], summon_title)
        if exists_on_trade_already:
            embed = Embed(title=f"🧬 Summon is being Traded", description=f"{summon_title} is still being traded. Please remove it from the trade before trading it")
            await ctx.send(embed=embed)
            return
        
        exists_on_market_already = db.queryMarket({"ITEM_OWNER": player.did, "ITEM_NAME": summon_title})
        if exists_on_market_already:
            embed = Embed(title=f"🏷️ Summon is on the Market", description=f"{summon_title} is still on the market. Please remove it from the market before trading it")
            await ctx.send(embed=embed)
            return
        
        trade_query = {'MERCHANT': player.did, 'OPEN': True}
        trade_data = db.queryTrade(trade_query)
        if not trade_data:
            trade_query = {'BUYER': player.did, 'OPEN': True}
            trade_data = db.queryTrade(trade_query)
        if trade_data:
            for s in player.summons:
                if s['NAME'] == summon_title:
                    summon.level = s['LVL']
                    summon.bond = s['BOND']
            trade_object = {
                "DID": player.did,
                "NAME": summon.name,
                "LVL": summon.level,
                "BOND": summon.bond,
            }
            response = db.updateTrade(trade_query, {'$push': {'SUMMONS': trade_object}})
            if response:
                # Make embed for being added to Trade
                embed = Embed(title=f"🧬 Summon Added to Trade", description=f"{summon.name} has been added to the trade")
                await ctx.send(embed=embed)
                return
        else:
            # Make embed for there not being a Trade open at this time
            embed = Embed(title=f"🧬 Summon Not Added to Trade", description=f"There is no trade open at this time")
            await ctx.send(embed=embed)
            return


    """
    UNIVERSE FUNCTIONS
    This section contains all the functions related to universe selections
    """
    async def activate_universe_action(self, ctx, universe):
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
            
            else:
                player.make_available()
                embed = Embed(title= f"{universe['TITLE']} Match Making Cancelled.", description="You have cancelled the match making process due to the universe not having characters in this mode.", ephemeral=True)
                await ctx.send(embed=embed)

        except Exception as ex:
            player.make_available()
            custom_logging.debug(ex)
            await ctx.send("There was an error starting the tale. Please try again later.", ephemeral=True)


    """
    SCENARIO FUNCTIONS
    This section contains all the functions related to scenario selections
    """
    async def activate_scenario_action(self, ctx, scenario):
        if self.scenario_start:
            await self.start_scenario(ctx, scenario)
            self.scenario_start = False

        if self.quit:
            await self.quit_universe_selection(ctx)
            self.quit = False


    async def start_scenario(self, ctx, scenario_title):
        try:
            user_data = db.queryUser({'DID': str(ctx.author.id)})
            player = crown_utilities.create_player_from_data(user_data)
            scenario = db.queryScenario({"TITLE": scenario_title})
            mode = "SCENARIO"

            await bc.create_scenario_battle(self, ctx, mode, player, scenario)
        except Exception as ex:
            print(ex)
            embed = Embed(title=f"🎴 Scenario Failed", description=f"Failed to start - Error Logged")
            await ctx.send(embed=embed)

    """
    RAID FUNCTIONS
    This section contains all the functions related to raid selections
    """
    async def activate_raid_action(self, ctx, raid):
        if self.raid_start:
            await self.start_raid(ctx, raid)
            self.raid_start = False

        if self.quit:
            await self.quit_universe_selection(ctx)
            self.quit = False


    async def start_raid(self, ctx, raid_title):
        user_data = db.queryUser({'DID': str(ctx.author.id)})
        player = crown_utilities.create_player_from_data(user_data)
        raid = db.queryScenario({"TITLE": raid_title})
        mode = "SCENARIO"

        await bc.create_raid_battle(self, ctx, mode, player, raid)


    """
    REGISTER FUNCTIONS
    This section contains all the functions related to registering a user
    """
    async def activate_register_action(self, ctx, universe_title):
        if self.register_select:
            await self.start_register(ctx, universe_title)
            self.register_select = False


    async def start_register(self, ctx, universe_title):
        await ctx.defer()
        user_data = db.queryUser({'DID': str(ctx.author.id)})
        player = crown_utilities.create_player_from_data(user_data)
        acceptable = [1,2,3,4,5]
        arm_message = []
        card_message = []
        current_arms = []


        embed1 = Embed(title=f"Registration Complete", description=f"Welcome to Anime VS+ {ctx.author.mention}! You have selected **{universe_title}** as your starting universe. Let's get you started!")
        embed1.add_field(name=f"__New Beginnings__", value=f"Now that you've selected **{universe_title}**, you'll receive 3 cards, some arms, and a title to give you a head start. By default, you also start the game with 3 additional starting cards: Naruto, Luffy, and Ichigo.\n\n**Check the next pages to see what you've received.**")
        embed1.set_footer(text="🎗️Use /daily for Daily Reward and Quest\n🔥/difficulty - Change difficulty setting of the game!", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
        
        list_of_titles = [x['TITLE'] for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': universe_title}) if x['UNLOCK_METHOD']['METHOD'] == "TALES RUN" and x['UNLOCK_METHOD']['VALUE'] == 0]
        titles_gained = []

        for title in list_of_titles:
            db.updateUserNoFilter(player.user_query,{'$addToSet':{'TITLES': title}, '$set': {'TITLE': title}})
            titles_gained.append(f"🎗️ **{title}**!")


        titles_gained_message = "\n".join(titles_gained)

        embed2 = Embed(title=f"🎗️ Titles Gained", description=f"🎗️ You earned the following titles from {crown_utilities.crest_dict[universe_title]} **{universe_title}**:\n{titles_gained_message}")
        embed2.add_field(name=f"__🎗️ Title: My Valor__", value=f"Titles are unique descriptors that provide passive buffs to your cards' stats, debuff opponents, or grant special battle effects.", inline=False)
        embed2.set_footer(text="🎗️ Use /titles to view the titles you own.", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
        
        list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': universe_title}) if x["DROP_STYLE"] ==  "TALES" and x['AVAILABLE'] and x['ARM'] not in current_arms]
        count = 0
        selected_arms = [1000]
        while count < 3:
            for arm in player.arms:
                current_arms.append(arm['ARM'])
            selectable_arms = list(range(0, len(list(list_of_arms))))
            for selected in selected_arms:
                if selected in selectable_arms:
                    selectable_arms.remove(selected)
            selection = random.choice(selectable_arms)
            selected_arms.append(selection)
            arm = list_of_arms[selection]['ARM']
            db.updateUserNoFilter(player.user_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 75}}, '$set': {'ARM': arm}})        
            arm_message.append(f"**{arm}**!")                   
            count = count + 1

        list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe_title), 'TIER': {'$in': acceptable}}) if x['DROP_STYLE'] == "TALES" and x['NAME'] not in player.cards]
        count = 0
        selected_cards = [1000]
        player_cards = []
        while count < 3:
            selectable_cards = list(range(0, len(list(list_of_cards))))
            for selected in selected_cards:
                if selected in selectable_cards:
                    selectable_cards.remove(selected)
            selection = random.choice(selectable_cards)
            # print(selection)
            selectable_cards.append(selection)
            if list_of_cards[selection]['NAME'] not in player_cards:
                card = crown_utilities.create_card_from_data(db.queryCard({'NAME': list_of_cards[selection]['NAME']}))
                player_cards.append(card.name)
                # db.updateUserNoFilter(player.user_query,{'$addToSet':{'CARDS': card.name}})
                player.save_card(card)
                card_message.append(f"**{card.name}**!")
                count = count + 1


        arm_drop_message_into_embded = "\n".join(arm_message)
        card_drop_message_into_embded = "\n".join(card_message)

        embed3 = Embed(title=f"🎴 Cards Gained", description=f"You earned the following cards from {crown_utilities.crest_dict[universe_title]} **{universe_title}**:\n{card_drop_message_into_embded}")
        embed3.add_field(name=f"__🎴 My Cards, My Power__", value=f"Cards are the characters you will use to battle in Anime VS+. Each card has a unique set of stats, abilities, and elements to master. Cards can be leveled up, evolved, and equipped with arms and titles to increase their power.", inline=False)
        embed3.set_footer(text="🎴 Use /cards to view the cards you own.", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
                          
        embed4 = Embed(title=f"🦾 Arms Gained", description=f"You earned the following arms from {crown_utilities.crest_dict[universe_title]} **{universe_title}**:\n{arm_drop_message_into_embded}")
        embed4.add_field(name=f"__🦾 My Arms, My Arsenal__", value=f"Arms are the abilties, weapons or protections you will use to battle in Anime VS+. Arms can be equipped to your cards to increase their power and give them new abilities.", inline=False)
        embed4.set_footer(text="🦾 Use /arms to view the arms you own.", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")

        embed5 = Embed(title="🔧Build and Strategize", description="Now that you have some items, it's time to **Build**. We have you covered to start with a default build that is designed to win battles. Use the **/build** command to see the default build", color=0x7289da)
        embed5.add_field(name="__Build Freedom__", value="Your build is crucial to your success. Spend some time mix and matching to find what works best for you. Use the **/cards, /titles, /arms, /summons, and /talismans** and develop a winning strategy.", inline=False)
        embed5.set_footer(text="🔧 Use /build to view your current build.", icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
                          
        embed6 = Embed(title="📿Talismans?🧬 Summons?", description="Oh yeah! Almost forgot. In addition to your cards, titles, and arms there are equippable summons and talismans. Summons are companions you can call on during battle to attack or protect you, and talismans are equippables that can be used to bypass elemental resistances. Neat, right?", color=0x7289da)
        embed6.add_field(name="__🔮 Summoning and Talismans__", value="Use the **/summons** command to view the summons you own and the **/talismans** command to view the talismans you own.", inline=False)

        embed7 = Embed(title="Ready To Play", description="You're all set to start playing Anime VS+! Use the **/daily** command to claim your daily reward and check your quests. If you have any questions, feel free to ask in the support channel or check the **/help** command for more information.", color=0x7289da)
        embed7.add_field(name="__🎮 Let's Play__", value="Use the **/play** command and select the 🆘Anime VS+ Tutorial to learn the combat systems interactively.", inline=False)
        
        embed_list = [embed1, embed2, embed3, embed4, embed5, embed6, embed7]

        paginator = Paginator.create_from_embeds(self.client, *embed_list, timeout=160)
        paginator.show_select_menu = True
        await paginator.send(ctx)

        # await ctx.send(embed=embedVar)
        return
        


    """
    UNIVERSE LIST FUNCTIONS
    This section contains all the functions related to universe list selections
    """
    async def activate_cards_list(self, ctx, universe_title):
        if self.cards_list_action:
            await self.start_cards_list(ctx, universe_title)
            self.cards_list_action = False

    
    async def activate_arms_list(self, ctx, universe_title, arm_type):
        if self.arms_list_action:
            await self.start_arms_list(ctx, universe_title, arm_type)
            self.arms_list_action = False


    async def activate_titles_list(self, ctx, universe_title):
        if self.titles_list_action:
            await self.start_titles_list(ctx, universe_title)
            self.titles_list_action = False


    async def activate_summons_list(self, ctx, universe_title):
        if self.summons_list_action:
            await self.start_summons_list(ctx, universe_title)
            self.summons_list_action = False


    async def start_arms_list(self, ctx, universe_title, arm_type):
        await ctx.defer()
        if arm_type == "protections":
            list_of_arms = db.queryAllArmsBasedOnUniverses({
                "$and": [
                    {"UNIVERSE": universe_title},
                    {
                        "$or": [
                            {"ABILITIES.MANA": {"$exists": True}},
                            {"ABILITIES.SHIELD": {"$exists": True}},
                            {"ABILITIES.PARRY": {"$exists": True}},
                            {"ABILITIES.SIPHON": {"$exists": True}},
                            {"ABILITIES.BARRIER": {"$exists": True}},
                            {"ABILITIES.ULTIMAX": {"$exists": True}}
                        ]
                    }
                ]
            })
        if arm_type == "ability":
            list_of_arms = db.queryAllArmsBasedOnUniverses(
                {
                    "$and": [
                        {"UNIVERSE": universe_title},
                        {
                            "$nor": [
                                {"ABILITIES.MANA": {"$exists": True}},
                                {"ABILITIES.SHIELD": {"$exists": True}},
                                {"ABILITIES.PARRY": {"$exists": True}},
                                {"ABILITIES.SIPHON": {"$exists": True}},
                                {"ABILITIES.BARRIER": {"$exists": True}},
                                {"ABILITIES.ULTIMAX": {"$exists": True}}
                            ]
                        }
                    ]
                })
        try:
            if not list_of_arms:
                embed = Embed(title="No Arms Available", description="There are no arms available in this universe at this time.", color=0x7289da)
                await ctx.send(embed=embed)
                return

            arms = [x for x in list_of_arms]
            all_arms = []
            embed_list = []

            sorted_arms = sorted(arms, key=lambda arm: arm["ARM"])
            for index, arm in enumerate(sorted_arms):
                arm_data = crown_utilities.create_arm_from_data(arm)
                # if arm_data.element:
                #     continue
                arm_data.set_drop_style()
                all_arms.append(f"{arm_data.universe_crest} {arm_data.element_emoji} {arm_data.drop_emoji} : **{arm_data.name}**\n**{arm_data.passive_type}** : *{arm_data.passive_value}*\n")

            for i in range(0, len(all_arms), 10):
                sublist = all_arms[i:i+10]
                embedVar = Embed(title=f"🌍 {universe_title}'s List of Arms", description="\n".join(sublist), color=0x7289da)
                embedVar.set_footer(text=f"{len(all_arms)} Total Arms")
                embed_list.append(embedVar)
            pagination = Paginator.create_from_embeds(self.client, *embed_list, timeout=160)
            await pagination.send(ctx)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🌍 Universe List Error", description="There was an error getting the list of arms for this universe at this time.", color=0x7289da)
            await ctx.send(embed=embed)


    async def start_cards_list(self, ctx, universe_title):
        try:
            card_list_type_buttons = [
                Button(
                    style=ButtonStyle.PRIMARY,
                    label="All Cards",
                    custom_id=f"{self._uuid}|all"
                ),
                Button(
                    style=ButtonStyle.PRIMARY,
                    label="🎴 Tale Cards",
                    custom_id=f"{self._uuid}|tale"
                ),
                Button(
                    style=ButtonStyle.PRIMARY,
                    label="👺 Dungeon Cards",
                    custom_id=f"{self._uuid}|dungeon"
                ),
                Button(
                    style=ButtonStyle.PRIMARY,
                    label="🎞️ Scenario Cards",
                    custom_id=f"{self._uuid}|scenario"
                ),
                Button(
                    style=ButtonStyle.PRIMARY,
                    label="🌟 Destiny Cards",
                    custom_id=f"{self._uuid}|destiny"
                )
            ]

            components = ActionRow(*card_list_type_buttons)
            embed = Embed(title=f"🎴 Which cards would you like to view?", description="Please select the type of cards you would like to view.", color=0x7289da)
            msg = await ctx.send(embed=embed, components=[components])

            def check(component: Button) -> bool:
                return component.ctx.author == ctx.author
            
            try:
                button_ctx = await self.client.wait_for_component(components=[components], timeout=1200, check=check)

                # Mapping of custom_id suffix to DROP_STYLE
                drop_style_map = {
                    "all": None,
                    "tale": "TALES",
                    "dungeon": "DUNGEON",
                    "scenario": "SCENARIO",
                    "destiny": "DESTINY"
                }

                # Extracting the action from the custom_id
                action = button_ctx.ctx.custom_id.split("|")[1]

                # Determine the DROP_STYLE based on the action
                drop_style = drop_style_map.get(action)

                # Build the query parameters
                query_params = {'UNIVERSE': str(universe_title)}
                if drop_style:
                    query_params['DROP_STYLE'] = drop_style

                # Query the database based on the parameters
                list_of_cards = db.queryAllCardsBasedOnUniverse(query_params)

                # Clean up after ourselves
                await msg.delete()
                
                if not list_of_cards:
                    embed = Embed(title="No Cards Available", description="There are no cards available for this universe at this time.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return
                
                cards = [x for x in list_of_cards]
                all_cards = []
                embed_list = []
                
                sorted_card_list = sorted(cards, key=lambda card: card["TIER"])
                for index, card in enumerate(sorted_card_list):
                    try:
                        c = crown_utilities.create_card_from_data(card)
                        all_cards.append(f"{c.universe_crest} : 🀄 **{c.tier}** **{c.name}** [{c.class_emoji}] {c.move1_emoji} {c.move2_emoji} {c.move3_emoji}\n{c.drop_emoji}: {str(c.card_lvl)} ❤️ {c.health} 🗡️ {c.attack} 🛡️ {c.defense}\n")
                    except Exception as ex:
                        print(ex)
                        print(c)
                        continue

                for i in range(0, len(all_cards), 10):
                    sublist = all_cards[i:i+10]
                    embedVar = Embed(title=f"🌍 {universe_title}'s List of Cards", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"{len(all_cards)} Total Cards")
                    embed_list.append(embedVar)

                pagination = Paginator.create_from_embeds(self.client, *embed_list, timeout=160)
                await pagination.send(ctx)
            except asyncio.TimeoutError:
                embed = Embed(title="🎴 Card List Error", description="There was an error getting the list of cards for this universe at this time.", color=0x7289da)
                await ctx.send(embed=embed)
        except Exception as ex:
            # custom_logging.debug(ex)
            embed = Embed(title="🎴 Card List Error", description="There was an error getting the list of cards for this universe at this time.", color=0x7289da)
            await ctx.send(embed=embed)


    async def start_titles_list(self, ctx, universe_title):
        list_of_titles = db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe_title)})
        if not list_of_titles:
            embed = Embed(title="No Titles Available", description="There are no titles available in this universe at this time.", color=0x7289da)
            await ctx.send(embed=embed)
            return

        titles = [x for x in list_of_titles]
        all_titles = []
        embed_list = []

        sorted_titles = sorted(titles, key=lambda title: title["TITLE"])
        for index, title in enumerate(sorted_titles):
            try:
                title_data = crown_utilities.create_title_from_data(title)                    
                all_titles.append(f"{title_data.universe_crest}: **{title_data.name}** 🔸{str(len(title_data.abilities))}\n")
            except Exception as ex:
                print(ex)
                print(title)
                continue
        for i in range(0, len(all_titles), 10):
            sublist = all_titles[i:i+10]           
            embedVar = Embed(title=f"🌍 {universe_title}'s List of Titles", description="\n".join(sublist), color=0x7289da)
            embedVar.set_author(name=f"The🔸represents the number of effects the title has")
            embedVar.set_footer(
                text=f"{len(all_titles)} Total Titles")
            embed_list.append(embedVar)

        pagination = Paginator.create_from_embeds(self.client, *embed_list, timeout=160)
        await pagination.send(ctx)


    async def start_summons_list(self, ctx, universe_title):
        list_of_summons = db.queryAllSummonsBasedOnUniverse({'UNIVERSE': str(universe_title)})
        if not list_of_summons:
            embed = Embed(title="No Summons Available", description="There are no summons available in this universe at this time.", color=0x7289da)
            await ctx.send(embed=embed)
            return

        summons = [x for x in list_of_summons]
        all_summons = []
        embed_list = []

        sorted_summons = sorted(summons, key=lambda summon: summon["PET"])
        for index, summon in enumerate(sorted_summons):
            s = crown_utilities.create_summon_from_data(summon)
            all_summons.append(f"{s.universe_crest} : 🧬 **{s.name}**\n{s.emoji} {s.ability_type.title()} - {s.ability_power}\n")

        for i in range(0, len(all_summons), 10):
            sublist = all_summons[i:i+10]
            embedVar = Embed(title=f"🌍 {universe_title}'s List of Summons", description="\n".join(sublist), color=0x7289da)
            embedVar.set_footer(text=f"{len(all_summons)} Total Summons")
            embed_list.append(embedVar)

        pagination = Paginator.create_from_embeds(self.client, *embed_list, timeout=160)
        await pagination.send(ctx)

def generate_6_digit_code():
    return random.randint(100000, 999999)

def validate_and_convert(option):
    # Check if 'option' contains only numbers and commas
    if all(char.isdigit() or char == ',' for char in option):
        # Split by commas
        numbers = option.split(',')
        try:
            # Convert to int, filter out empty strings for cases like "3,"
            numbers_int = [int(num) for num in numbers if num]
            # Return as a single int if only one number, else as a list
            return [numbers_int[0]] if len(numbers_int) == 1 else numbers_int
        except ValueError:
            # Handle the case where conversion to int fails (should not happen due to checks)
            return "Invalid input; contains non-numeric values. Please type only numbers and commas."
    else:
        return "Invalid input; contains forbidden characters. Please type only numbers and commas."
