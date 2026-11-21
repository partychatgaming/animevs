import crown_utilities
import custom_logging
import db
import asyncio
import uuid
from interactions import ActionRow, Button, ButtonStyle, listen, slash_command, SlashCommandOption, OptionType, SlashCommandChoice, Embed, Extension
from interactions.ext.paginators import Paginator
from logger import loggy
import market_trade
import render_cache
from cogs.classes.custom_paginator import CustomPaginator

class Marketplace(Extension):
    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        #print('Marketplace Cog is ready!')
        loggy.info('Marketplace Cog is ready')

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
                await self.show_card_market(ctx, player)
                return

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

                if embed_list:
                    pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                    pagination.show_select_menu = True
                    await pagination.send(ctx)
                else:
                    embed = Embed(title="🏷️ Marketplace", description="There are no summons on the marketplace.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return

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

                if embed_list:
                    pagination = Paginator.create_from_embeds(self.bot, *embed_list, timeout=160)
                    pagination.show_select_menu = True
                    await pagination.send(ctx)
                else:
                    embed = Embed(title="🏷️ Marketplace", description="There are no arms on the marketplace.", color=0x7289da)
                    await ctx.send(embed=embed)
                    return
                
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🏷️ Error", description="Something went wrong with the Marketplace command. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)


    async def show_card_market(self, ctx, player):
        """One listing per page: the portrait card, price, code, seller, and a Buy button."""
        listings = await asyncio.to_thread(lambda: list(db.queryAllMarketByParam({"MARKET_TYPE": "CARD"}) or []))
        if not listings:
            await ctx.send(embed=Embed(title="🏷️ Marketplace", description="There are no cards on the marketplace right now.", color=0x7289da))
            return
        listings.sort(key=lambda l: (str(l.get("ITEM_NAME", "")).lower(), int(l.get("PRICE") or 0)))

        card_docs = await asyncio.gather(*[asyncio.to_thread(db.queryCard, {"NAME": l.get("ITEM_NAME")}) for l in listings])
        seller_ids = sorted({str(l.get("ITEM_OWNER")) for l in listings})
        seller_docs = await asyncio.gather(*[asyncio.to_thread(db.queryUser, {"DID": did}) for did in seller_ids])
        seller_names = {did: (doc or {}).get("DISNAME") or "a player" for did, doc in zip(seller_ids, seller_docs)}

        entries = []
        for listing, card_data in zip(listings, card_docs):
            if not card_data:
                continue
            c = crown_utilities.create_card_from_data(card_data)
            if not c:
                continue
            c.set_card_level_buffs([{"CARD": c.name, "LVL": listing.get("CARD_LEVEL", 1), "EXP": 0}])
            c.set_affinity_message()
            c.set_card_level_icon(player)
            entries.append((listing, c))
        if not entries:
            await ctx.send(embed=Embed(title="🏷️ Marketplace", description="There are no cards on the marketplace right now.", color=0x7289da))
            return

        embeds = []
        for i, (listing, c) in enumerate(entries):
            price = int(listing.get("PRICE") or 0)
            code = listing.get("MARKET_CODE")
            seller = seller_names.get(str(listing.get("ITEM_OWNER")), "a player")
            if str(listing.get("ITEM_OWNER")) == str(player.did):
                status = "🏷️ This is your listing"
            elif player.balance >= price:
                status = f"✅ You can afford this (you have 🪙 {player.balance:,})"
            else:
                status = f"❌ You need 🪙 {price - player.balance:,} more"
            embed = Embed(title=f"{c.name}", description=(
                f"## 🪙 {price:,}\n"
                f"🏷️ Code `{code}`  ·  sold by **{seller}**\n"
                f"{c.universe_crest} {c.universe}  ·  {c.class_emoji} {c.class_message}\n"
                f"{c.level_icon} Level **{c.card_lvl}**  ·  🀄 Tier **{c.tier}**\n"
                f"{status}"
            ), color=0xF1C40F)
            embed.add_field(name="__Affinities__", value=f"{c.affinity_message or 'None'}")
            embed.set_image(url="attachment://card.png")
            embed.set_footer(text=f"Listing {i + 1} of {len(entries)}  ·  Press Buy, or /buy card {code}")
            embeds.append(embed)

        rendered = {}

        async def card_picture(index):
            if index in rendered:
                return rendered[index]
            image = await render_cache.render_async(entries[index][1].showcard)
            try:
                data = image.getvalue()
            finally:
                image.close()
            rendered[index] = data
            while len(rendered) > 12:
                rendered.pop(next(iter(rendered)))
            return data

        async def buy_page(button_ctx, index):
            listing = entries[index][0]
            await market_trade.confirm_and_buy(self.bot, button_ctx, button_ctx.author, listing.get("MARKET_CODE"), "card", ephemeral=True)

        paginator = CustomPaginator.create_from_embeds(self.bot, *embeds, timeout=300, custom_buttons=["Buy"])
        paginator.show_select_menu = True
        paginator.page_image = card_picture
        paginator.page_image_name = "card.png"
        paginator.page_action = buy_page
        await paginator.send(ctx)


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
            await market_trade.confirm_and_buy(self.bot, ctx, ctx.author, code, market, ephemeral=False)
        except Exception as ex:
            custom_logging.debug(ex)
            embed = Embed(title="🏷️ Error", description="Something went wrong with the Marketplace command. Please try again later.", color=0xff0000)
            await ctx.send(embed=embed)


def setup(bot):
    Marketplace(bot)