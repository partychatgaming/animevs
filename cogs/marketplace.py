import crown_utilities
import custom_logging
import db
import asyncio
import messages as m
from interactions import User
from interactions import Client, ActionRow, Button, ButtonStyle, Intents, listen, slash_command, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, Extension
from interactions.ext.paginators import Paginator

class Marketplace(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print('Marketplace Cog is ready!')

    async def cog_check(self, ctx):
        return await self.bot.validate_user(ctx)

    @slash_command(description="Marketplace view command",
                    options=[
                        SlashCommandOption(
                            name="market",
                            description="Choose the type of market items you want to view.",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="🎴 Cards",
                                    value="card"
                                ),
                                SlashCommandChoice(
                                    name="🧬 Summons",
                                    value="summon"
                                ),
                                SlashCommandChoice(
                                    name="🦾 Arms",
                                    value="arm"
                                ),
                            ]
                        )
                    ]
        )
    async def marketplace(self, ctx, market):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            player = crown_utilities.create_player_from_data(a_registered_player)
            if market == "card":
                list_of_cards = db.queryAllMarketByParam({"MARKET_TYPE": "CARD"})
                if not list_of_cards:
                    embed = Embed(title="🏷️ Marketplace", description="There are no cards on the marketplace.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return
                cards = [x for x in list_of_cards]
                all_cards = []
                embed_list = []
                
                sorted_card_list = sorted(cards, key=lambda card: card["ITEM_NAME"])
                for index, card in enumerate(sorted_card_list):
                    card_data = db.queryCard({"NAME": card["ITEM_NAME"]})
                    c = crown_utilities.create_card_from_data(card_data)
                    card_level = [{"CARD": c.name,"LVL": card["CARD_LEVEL"], "EXP": 0}]
                    c.set_card_level_buffs(card_level)
                    all_cards.append(f"🏷️ **{card['MARKET_CODE']}** 🪙 **{'{:,}'.format(card['PRICE'])}**\n[{str(index)}] {c.universe_crest} : 🀄 **{c.tier}** **{c.name}** [{c.class_emoji}] {c.move1_emoji} {c.move2_emoji} {c.move3_emoji}\n{c.drop_emoji} **{c.level_icon}**: {str(c.card_lvl)} ❤️ {c.health} 🗡️ {c.attack} 🛡️ {c.defense}\n")
                
                for i in range(0, len(all_cards), 10):
                    sublist = all_cards[i:i+10]
                    embedVar = Embed(title=f"🏷️ Cards on the Marketplace", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"{len(all_cards)} Total Cards on the Marketplace\nTo purchase a card, use the /buy command and enter the Market Code for the card.")
                    embed_list.append(embedVar)

                pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                pagination.show_select_menu = True
                await pagination.send(ctx)

            if market == "summon":
                list_of_summons = db.queryAllMarketByParam({"MARKET_TYPE": "SUMMON"})
                if not list_of_summons:
                    embed = Embed(title="🏷️ Marketplace", description="There are no summons on the marketplace.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return
                summons = [x for x in list_of_summons]
                all_summons = []
                embed_list = []


                sorted_summons = sorted(summons, key=lambda summon: summon["ITEM_NAME"])
                for index, summon in enumerate(sorted_summons):
                    s = db.querySummon({'PET': summon['ITEM_NAME']})
                    summon_class = crown_utilities.create_summon_from_data(s)
                    all_summons.append(f"🏷️ **{summon['MARKET_CODE']}** 🪙 **{'{:,}'.format(summon['PRICE'])}**\n[{str(index)}] {summon_class.universe_crest} : **Level {summon['SUMMON_LEVEL']}** | **Bond {summon['BOND_LEVEL']}** 🧬 **{summon_class.name}**\n{summon_class.emoji} **{summon_class.ability_type.capitalize()}** **{summon['ability']}:** {summon['ability_power']}")

                for i in range(0, len(all_summons), 10):
                    sublist = all_summons[i:i+10]           
                    embedVar = Embed(title=f"🏷️ Summons on the Marketplace", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"{len(all_summons)} Total Summons on the Marketplace\nTo purchase a summon, use the /buy command and enter the Market Code for the summon.")
                    embed_list.append(embedVar)

                pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                pagination.show_select_menu = True
                await pagination.send(ctx)

            if market == "arm":
                list_of_arms = db.queryAllMarketByParam({"MARKET_TYPE": "ARM"})
                if not list_of_arms:
                    embed = Embed(title="🏷️ Marketplace", description="There are no arms on the marketplace.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return
                arms = [x for x in list_of_arms]
                all_arms = []
                embed_list = []

                icon = ""
                sorted_arms = sorted(arms, key=lambda arm: arm["ITEM_NAME"])
                for index, arm in enumerate(sorted_arms):
                    arm_data = db.queryArm({'ARM': arm['ITEM_NAME']})
                    a = crown_utilities.create_arm_from_data(arm_data)
                    all_arms.append(f"🏷️ **{arm['MARKET_CODE']}** 🪙 **{'{:,}'.format(arm['PRICE'])}**\n[{str(index)}] {a.universe_crest} {a.element_emoji} : **{a.name}**\n**{a.passive_type}** : *{a.passive_value}* ⚒️*25*\n")


                for i in range(0, len(all_arms), 10):
                    sublist = all_arms[i:i+10]
                    embedVar = Embed(title=f"🏷️ Arms on the Marketplace", description="\n".join(sublist), color=0x7289da)
                    embedVar.set_footer(text=f"{len(all_arms)} Total Arms on the Marketplace\nTo purchase a arm, use the /buy command and enter the Market Code for the arm.")
                    embed_list.append(embedVar)
                    
                    pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                    pagination.show_select_menu = True
                    await pagination.send(ctx)
            
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🏷️ Error", description="Something went wrong with the Marketplace command. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)


    @slash_command(description="Buy from marketplace command",
                    options=[
                        SlashCommandOption(
                            name="market",
                            description="Choose the type of market items you want to buy.",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="🎴 Cards",
                                    value="card"
                                ),
                                SlashCommandChoice(
                                    name="🧬 Summons",
                                    value="summon"
                                ),
                                SlashCommandChoice(
                                    name="🦾 Arms",
                                    value="arm"
                                ),
                            ]
                        ),
                        SlashCommandOption(
                            name="code",
                            description="Market code for the item you want to buy.",
                            type=OptionType.STRING,
                            required=True,
                        ),                    
                        ]
        )
    async def buy(self, ctx, market, code):
        await ctx.defer()
        a_registered_player = await crown_utilities.player_check(ctx)
        if not a_registered_player:
            return

        try:
            _uuid = _uuid.uuid4()
            market_item_info = db.queryMarket({"MARKET_CODE": code})
            if not market_item_info:
                embed = Embed(title="🏷️ Marketplace", description="There are no items on the marketplace with this code number.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            player = crown_utilities.create_player_from_data(a_registered_player)
            confirmation_buttons = [
                Button(
                    style=ButtonStyle.GREEN,
                    label="1️⃣",
                    custom_id = f"{_uuid}|yes"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="2️⃣",
                    custom_id = f"{_uuid}|no"
                )
            ]
            row = ActionRow(*confirmation_buttons)

            if player.balance < market_item_info["PRICE"]:
                embed = Embed(title="🏷️ Marketplace", description=f"You do not have enough gold to purchase this item.", color=0x7289da)
                await ctx.send(embed=embed)
                return
            price = market_item_info["PRICE"]
            if market == "card":
                card_data = db.queryCard({"NAME": market_item_info["ITEM_NAME"]})
                c = crown_utilities.create_card_from_data(card_data)
                card_level = [{"CARD": c.name, "LVL": market_item_info["CARD_LEVEL"], "EXP": 0}]
                c.set_card_level_buffs(card_level)
                embed = Embed(title="🏷️ Marketplace", description=f"Are you sure you want to purchase {c.name}?", color=0x7289da)
                message = await ctx.send(embed=embed, components=[row])
                
                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[row], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = player.save_card(c)
                        if response:
                            removal = db.deleteMarketEntry({"MARKET_CODE": code})
                            purchase = crown_utilities.curse(price, player.did)
                            embed = Embed(title=f"🏷️ Success", description=f"{c.name} has been removed from the market.")
                            await message.edit(embed=embed, components=[])
                            return
                        else:
                            embed = Embed(title=f"🏷️ Error", description=f"You are unable to purchase this card at this time. Please check if you already have this card or if your storage is full.", color=0xff0000)
                            await message.edit(embed=embed, components=[])
                            return
                    
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        await message.delete()
                        return

                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond.")
                    return
                except Exception as ex:
                    custom_logging.debug(ex)
                    await ctx.send("Something went wrong. Please try again later.")
                    return

            if market == "summon":
                summon_data = db.querySummon({"PET": market_item_info["ITEM_NAME"]})
                s = crown_utilities.create_summon_from_data(summon_data)
                s.level = market_item_info["SUMMON_LEVEL"]
                s.bond = market_item_info["BOND_LEVEL"]
                embed = Embed(title="🏷️ Marketplace", description=f"Are you sure you want to purchase {s.name}?", color=0x7289da)
                message = await ctx.send(embed=embed, components=[row])
                
                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[row], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = player.save_summon(s)
                        if response:
                            removal = db.deleteMarketEntry({"MARKET_CODE": code})
                            purchase = crown_utilities.curse(price, player.did)
                            embed = Embed(title=f"🏷️ Success", description=f"{s.name} has been removed from the market.")
                            await message.edit(embed=embed, components=[])
                            return
                        else:
                            embed = Embed(title=f"🏷️ Error", description=f"You are unable to purchase this summon at this time. Please check if you already have this summon.", color=0xff0000)
                            await message.edit(embed=embed, components=[])
                            return                    
                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        await message.delete()
                        return

                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond.")
                    return
                except Exception as ex:
                    custom_logging.debug(ex)
                    await ctx.send("Something went wrong. Please try again later.")
                    return

            if market == "arm":
                arm_data = db.queryArm({"ARM": market_item_info["ITEM_NAME"]})
                a = crown_utilities.create_arm_from_data(arm_data)
                a.durability = 25
                embed = Embed(title="🏷️ Marketplace", description=f"Are you sure you want to purchase {a.name}?", color=0x7289da)
                message = await ctx.send(embed=embed, components=[row])
                
                def check(component: Button) -> bool:
                    return component.ctx.author == ctx.author

                try:
                    button_ctx = await self.client.wait_for_component(components=[row], check=check, timeout=120)

                    if button_ctx.ctx.custom_id == f"{self._uuid}|yes":
                        response = player.save_arm(a)
                        if response:
                            removal = db.deleteMarketEntry({"MARKET_CODE": code})
                            purchase = crown_utilities.curse(price, player.did)
                            embed = Embed(title=f"🏷️ Success", description=f"{a.name} has been removed from the market.")
                            await message.edit(embed=embed, components=[])
                            return
                        else:
                            embed = Embed(title=f"🏷️ Error", description=f"You are unable to purchase this arm at this time. Please check if you already have this arm or if your storage is full.", color=0xff0000)
                            await message.edit(embed=embed, components=[])
                            return

                    if button_ctx.ctx.custom_id == f"{self._uuid}|no":
                        await message.delete()
                        return

                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond.")
                    return
                except Exception as ex:
                    custom_logging.debug(ex)
                    await ctx.send("Something went wrong. Please try again later.")
                    return

        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🏷️ Error", description="Something went wrong with the Marketplace command. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)

def setup(bot):
    Marketplace(bot)