import crown_utilities
import custom_logging
import db
import asyncio
import uuid
from interactions import User
from interactions import ActionRow, Button, ButtonStyle, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, SlashCommandChoice, Embed, Extension
from cogs.classes.trade_class import Trading
from cogs.quests import Quests

class Trade(Extension):
    def __init__(self, bot):
        self.bot = bot



    @listen()
    async def on_ready(self):
        print('Trade Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)


    @slash_command(description="Trade with another Player", options=[
        SlashCommandOption(
            name="player",
            description="Player to Trade with",
            type=OptionType.USER,
            required=True
        )
    ])
    async def trade(self, ctx: InteractionContext, player: User):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        try:
            _uuid = uuid.uuid4()
            merchant_did, trade_partner_did, trade = get_merchant_and_trade_partner(ctx.author.id, player.id)
            # if not trade:
            #     embed = Embed(title="Error Loading Trade", description=f"There is no active trade with <@{player.id}>.", color=0x7289da)
            #     await ctx.send(embed=embed)
            #     return
            tp = db.queryUser({'DID': str(trade_partner_did)})
            trade_partner = crown_utilities.create_player_from_data(tp)
            m = db.queryUser({'DID': str(merchant_did)})
            merchant = crown_utilities.create_player_from_data(m)
            not_eligible = crown_utilities.get_trade_eligibility(merchant, trade_partner)

            if trade_partner.did == merchant.did:
                embed = Embed(title="Error Loading Trade", description=f"You can't trade with yourself!", color=0x7289da)
                await ctx.send(embed=embed)
                return

            if not_eligible:
                await ctx.send(not_eligible)
                return

            if trade:
                trade_info = Trading(merchant, trade_partner)
                set_trade_info(trade_info, trade)
                executioner = str(ctx.author.id)
                friend = str(player.id)
                await self.trade_exists(ctx, _uuid, trade_info, executioner, friend)
            else:
                await self.create_trade(ctx, _uuid, merchant, trade_partner)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Error Loading Trade", description=f"There was an error loading the trade command.", color=0x7289da)
            await ctx.send(embed=embed)
            return
    

    @slash_command(description="Add Items to Current Trade",
                       options=[
                            SlashCommandOption(
                                name="player",
                                description="Player you are trading with",
                                type=OptionType.USER,
                                required=True
                            ),
                           SlashCommandOption(
                               name="mode",
                               description="Item Type",
                               type=OptionType.STRING,
                               required=True,
                               choices=[
                                   SlashCommandChoice(
                                       name="Add Coins",
                                       value="add"
                                   ),
                                   SlashCommandChoice(
                                       name="Subtract Coins",
                                       value="subtract"
                                   )
                               ]
                           ),
                           SlashCommandOption(
                               name="amount",
                               description="Total Coins",
                               type=OptionType.STRING,
                               required=True
                           )
                       ]
        )
    async def tradecoins(self, ctx: InteractionContext, player: User, mode: str, amount: int):
        registered_player = await crown_utilities.player_check(ctx)
        if not registered_player:
            return
        try:
            merchant_did, trade_partner_did, trade = get_merchant_and_trade_partner(ctx.author.id, player.id)
            if not trade:
                embed = Embed(title="Error Loading Trade", description=f"There is no active trade with <@{player.id}>.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            tp = await asyncio.to_thread(db.queryUser, {'DID': str(trade_partner_did)})
            trade_partner = crown_utilities.create_player_from_data(tp)
            m = await asyncio.to_thread(db.queryUser, {'DID': str(merchant_did)})
            merchant = crown_utilities.create_player_from_data(m)
            trade_info = Trading(merchant, trade_partner)
            set_trade_info(trade_info, trade)

            if mode == "add":
                trade_info.add_gold(str(ctx.author.id), int(amount))
                await asyncio.to_thread(db.updateTrade, trade_info.get_query(), {'$set': trade_info.get_trade_data()})
                embed = Embed(title="Trade Updated", description=f"Added 🪙 {int(amount):,} gold to the trade with <@{player.id}>.", color=0x7289da)
                await ctx.send(embed=embed)
                return

            if mode == "subtract":
                trade_info.subtract_gold(str(ctx.author.id), int(amount))
                await asyncio.to_thread(db.updateTrade, trade_info.get_query(), {'$set': trade_info.get_trade_data()})
                embed = Embed(title="Trade Updated", description=f"Subtracted 🪙 {int(amount):,} gold from the trade with <@{player.id}>.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="Error Loading Trade", description=f"There was an error loading the trade command.", color=0x7289da)
            await ctx.send(embed=embed)
            return


    async def trade_exists(self, ctx, _uuid, trade_info, executioner, friend):
        if str(ctx.author.id) == trade_info.merchant.did:
            trade_buttons = [
                Button(
                    style=ButtonStyle.GREEN,
                    label="Confirm Trade",
                    custom_id=f"{_uuid}|confirm"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="End Trade",
                    custom_id=f"{_uuid}|end"
                ),
                Button(
                    style=ButtonStyle.GRAY,
                    label="Cancel",
                    custom_id=f"{_uuid}|cancel"
                )
            ]
        else:
            trade_buttons = [
                Button(
                    style=ButtonStyle.RED,
                    label="End Trade",
                    custom_id=f"{_uuid}|end"
                ),
                Button(
                    style=ButtonStyle.GRAY,
                    label="Cancel",
                    custom_id=f"{_uuid}|cancel"
                )
            ]
        trade_buttons_action_row = ActionRow(*trade_buttons)

        msg = await ctx.send(embeds=trade_info.get_trade_message(), components=[trade_buttons_action_row])

        def check(component: Button) -> bool:
            return component.ctx.author == ctx.author
 
        try:
            button_ctx = await self.bot.wait_for_component(components=[trade_buttons_action_row], check=check, timeout=120)

            if button_ctx.ctx.custom_id == f"{_uuid}|confirm":
                _uuid = uuid.uuid4()
                confirm_buttons = [
                    Button(
                        style=ButtonStyle.GREEN,
                        label="Yes, lets trade!",
                        custom_id=f"{_uuid}|yes"
                    ),
                    Button(
                        style=ButtonStyle.RED,
                        label="No, not yet!",
                        custom_id=f"{_uuid}|no"
                    )
                ]
                confirm_buttons_action_row = ActionRow(*confirm_buttons)
                embed = Embed(title=f"🤝 Trade Request", description=f"<@{executioner}> has confirmed the trade. Do you accept <@{friend}>?")
                confimation_msg = await button_ctx.ctx.send(embed=embed, components=[confirm_buttons_action_row])

                def check(component: Button) -> bool:
                    return str(component.ctx.author.id) == str(friend)

                try:
                    button_ctx = await self.bot.wait_for_component(components=[confirm_buttons_action_row], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                        await button_ctx.ctx.defer(edit_origin=True)
                        trade_ready = await self.receive_trade_items(trade_info)
                        if trade_ready:
                            trade_info.set_open(False)
                            db.updateTrade(trade_info.get_query(), {"$set": trade_info.get_trade_data()})
                            user = await self.bot.fetch_user(str(executioner))
                            user2 = await self.bot.fetch_user(str(friend))
                            await Quests.quest_check(self, trade_info.merchant, "TRADE")
                            await Quests.quest_check(self, trade_info.buyer, "TRADE")
                            await user.send(embed=trade_info.get_trade_message())
                            await user2.send(embed=trade_info.get_trade_message())
                            embed = Embed(title=f"🤝 Trade Completed", description=f"🎊 Trade between <@{executioner}> and <@{friend}> has been completed! 🎊. A reciept has been sent to both indiviuals dm's. 📨")
                            await confimation_msg.edit(embed=embed, components=[])
                            return
                        else:
                            embed = Embed(title=f"🤝 Trade Failed", description=f"Failed to complete Trade.")
                            await confimation_msg.edit(embed=embed, components=[])
                            return
                    
                    if button_ctx.ctx.custom_id == f"{_uuid}|no":
                        await button_ctx.ctx.defer(edit_origin=True)
                        embed = Embed(title=f"🤝 Trade Not Completed", description=f"The trade has not been accepted.")
                        await confimation_msg.edit(embed=embed, components=[])
                        return

                except asyncio.TimeoutError:
                    embed = Embed(title=f"🤝 Trade Ended", description=f"Failed to complete Trade in time.")
                    await msg.edit(embed=embed, components=[])
                    return

            if button_ctx.ctx.custom_id == f"{_uuid}|end":
                await button_ctx.ctx.defer(edit_origin=True)
                embed = Embed(title=f"🤝 Trade Ended", description=f"The trade has ended and no items were traded.")
                trade_info.set_open(False)
                respone = db.updateTrade(trade_info.get_query(), {"$set": trade_info.get_trade_data()})
                await msg.edit(embed=embed, components=[])
                return

            if button_ctx.ctx.custom_id == f"{_uuid}|cancel":
                await button_ctx.ctx.defer(edit_origin=True)
                embed = Embed(title=f"🤝 Trade Window Closing", description=f"Closing the trade window. Feel free to check your trade again later.")
                await msg.edit(embed=embed, components=[])
                return

        except asyncio.TimeoutError:
            embed = Embed(title=f"🤝 Trade Ended", description=f"Failed to complete Trade in time.")
            await msg.edit(embed=embed, components=[])
            return


    async def create_trade(self, ctx, _uuid, merchant, trade_partner):
        trade_buttons = [
            Button(
                style=ButtonStyle.GREEN,
                label="Yes",
                custom_id=f"{_uuid}|yes"
            ),
            Button(
                style=ButtonStyle.RED,
                label="No",
                custom_id=f"{_uuid}|no"
            )
        ]
        trade_buttons_action_row = ActionRow(*trade_buttons)
        trade_info = Trading(merchant, trade_partner)
        embed = Embed(title=f"🤝 Trade Request", description=f"<@{merchant.did}> has requested to trade with you. Do you accept?")
        msg = await ctx.send(embeds=embed, components=[trade_buttons_action_row])

        def check(component: Button):
            return str(component.ctx.author.id) == str(trade_partner.did)

        try:
            button_ctx = await self.bot.wait_for_component(components=[trade_buttons_action_row], check=check, timeout=120)

            if button_ctx.ctx.custom_id == f"{_uuid}|yes":
                await button_ctx.ctx.defer(edit_origin=True)
                response = db.createTrade(trade_info.get_trade_data())
                embed = Embed(title=f"🤝 Trade Opened", description=f"Trade between <@{merchant.did}> and <@{trade_partner.did}> has been opened.")
                await msg.edit(embed=embed, components=[])
                return
            
            if button_ctx.ctx.custom_id == f"{_uuid}|no":
                await button_ctx.ctx.defer(edit_origin=True)
                embed = Embed(title=f"🤝 Trade Ended", description=f"<@{trade_partner.did}> has declined the trade request.")
                await msg.edit(embed=embed, components=[])
                return
        except asyncio.TimeoutError:
            embed = Embed(title=f"🤝 Trade Ended", description=f"Failed to start Trade in time.")
            await msg.edit(embed=embed, components=[])


    async def receive_trade_items(self, trade_info):
        try:
            m = db.queryUser({'DID': str(trade_info.merchant.did)})
            t = db.queryUser({'DID': str(trade_info.buyer.did)})
            merchant = crown_utilities.create_player_from_data(m)
            trade_partner = crown_utilities.create_player_from_data(t)
            if trade_info.cards:
                for card in trade_info.cards:            
                    card_data = db.queryCard({"NAME": card["NAME"]})
                    c = crown_utilities.create_card_from_data(card_data)
                    level_array = [{"CARD": card["NAME"], "LVL": card["LVL"], "TIER": card["TIER"], "EXP": 0}]
                    c.set_card_level_buffs(level_array)
                    if str(card['DID']) == str(merchant.did):
                        trade_partner.save_card(c)
                        merchant.remove_card(c.name)
                    else:
                        merchant.save_card(c)
                        trade_partner.remove_card(c.name)
            
            if trade_info.arms:
                for arm in trade_info.arms:
                    arm_data = db.queryArm({"ARM": arm['NAME']})
                    a = crown_utilities.create_arm_from_data(arm_data)
                    a.durability = arm['DUR']
                    if str(arm['DID']) == str(merchant.did):
                        trade_partner.save_arm(a)
                        merchant.remove_arm(a.name)
                    else:
                        merchant.save_arm(a)
                        trade_partner.remove_arm(a.name)

            if trade_info.summons:
                for summon in trade_info.summons:
                    summon_data = db.querySummon({"PET": summon['NAME']})
                    s = crown_utilities.create_summon_from_data(summon_data)
                    s.level = summon['LVL']
                    s.bond = summon['BOND']
                    if summon['DID'] == str(merchant.did):
                        trade_partner.save_summon(s)
                        merchant.remove_summon(s)
                    else:
                        merchant.save_summon(s)
                        trade_partner.remove_summon(s.name)

            if trade_info.gold:
                for gold in trade_info.gold:
                    if str(gold['DID']) == str(merchant.did):
                        await crown_utilities.bless(gold['AMOUNT'], trade_partner.did)
                        await crown_utilities.curse(gold['AMOUNT'], merchant.did)
                    else:
                        await crown_utilities.bless(gold['AMOUNT'], merchant.did)
                        await crown_utilities.curse(gold['AMOUNT'], trade_partner.did)

            return True
        except Exception as ex:
            custom_logging.debug(ex)
            return False


def set_trade_info(trade_info, trade):
    trade_info.set_cards(trade['CARDS'])
    trade_info.set_arms(trade['ARMS'])
    trade_info.set_summons(trade['SUMMONS'])
    trade_info.set_gold(trade['GOLD'])
    trade_info.set_tax(trade['TAX'])
    trade_info.set_open(trade['OPEN'])


def get_merchant_and_trade_partner(your_did, player_did):
    query1 = {'MERCHANT': str(your_did), 'BUYER': str(player_did), 'OPEN': True}
    query2 = {'MERCHANT': str(player_did), 'BUYER': str(your_did), 'OPEN': True}
    response = db.queryTrade(query1)
    if response:
        return your_did, player_did, response
    else:
        response = db.queryTrade(query2)
        if response:
            return player_did, your_did, response
        else:
            return your_did, player_did, None

def setup(bot):
    Trade(bot)