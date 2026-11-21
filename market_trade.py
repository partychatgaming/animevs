"""Buying from the marketplace: checks, the confirmation prompt and the transfer.

Shared by /buy and the Buy button on /marketplace.  A purchase only happens if
every check passes at the moment of confirming:

* the listing still exists and is the type the buyer asked for,
* the buyer isn't the seller, can afford it and has room for it,
* the seller still owns the item.

The listing is then *claimed* by deleting it (only one buyer can win that
delete), the item is given to the buyer, coins move from buyer to seller, and
only then is the item taken from the seller.  If giving the item fails, nothing
else happens and the listing is put back.
"""
import asyncio
import uuid

from interactions import ActionRow, Button, ButtonStyle, Embed

import crown_utilities
import custom_logging
import db
from logger import loggy

MARKET_TYPES = {"card": "CARD", "summon": "SUMMON", "arm": "ARM"}
LABELS = {"card": "card", "summon": "summon", "arm": "arm"}
INVENTORY_LIMIT = 80


def _code_query(code):
    code = str(code).strip()
    values = [code]
    if code.isdigit():
        values.append(int(code))
    return {"MARKET_CODE": {"$in": values}}


def _player(did):
    data = db.queryUser({"DID": str(did)})
    return crown_utilities.create_player_from_data(data) if data else None


def _names(entries, key):
    return {e.get(key) for e in (entries or []) if isinstance(e, dict)}


def _seller_owns(seller, market, name):
    if market == "card":
        return name in (seller.cards or []) or name in (seller.storage or [])
    if market == "summon":
        return name in _names(seller.summons, "NAME")
    return name in _names(seller.arms, "ARM") or name in _names(getattr(seller, "astorage", []), "ARM")


def _buyer_room(buyer, market, name):
    """None if the buyer can take the item, else the reason they can't."""
    if market == "card":
        if name not in (buyer.cards or []) and len(buyer.cards or []) >= INVENTORY_LIMIT:
            return f"Your card inventory is full ({INVENTORY_LIMIT}). Move or dismantle a card first."
        return None
    if market == "summon":
        if name in _names(buyer.summons, "NAME"):
            return f"You already own **{name}**."
        if len(buyer.summons or []) >= INVENTORY_LIMIT:
            return f"Your summon inventory is full ({INVENTORY_LIMIT})."
        return None
    if name in _names(buyer.arms, "ARM"):
        return f"You already own **{name}**."
    if len(buyer.arms or []) >= INVENTORY_LIMIT:
        return f"Your arm inventory is full ({INVENTORY_LIMIT})."
    return None


def check_purchase(buyer_did, code, market):
    """(listing, seller, None) if the buyer may buy ``code`` now, else (None, None, reason).  Blocking: run in a thread."""
    market = market if market in MARKET_TYPES else "card"
    listing = db.queryMarket(_code_query(code))
    if not listing:
        return None, None, "There's no item on the market with that code. It may have just been sold."
    if listing.get("MARKET_TYPE") != MARKET_TYPES[market]:
        actual = next((k for k, v in MARKET_TYPES.items() if v == listing.get("MARKET_TYPE")), "item")
        return None, None, f"That code is for {'an' if actual == 'arm' else 'a'} **{actual}**, not {'an' if market == 'arm' else 'a'} {LABELS[market]}. Try `/buy market:{actual}`."
    if str(listing.get("ITEM_OWNER")) == str(buyer_did):
        return None, None, "That's your own listing. Use the **Market** button on the item to take it down."
    buyer = _player(buyer_did)
    if buyer is None:
        return None, None, "You need an account first: `/register`."
    price = int(listing.get("PRICE") or 0)
    if buyer.balance < price:
        return None, None, f"You need 🪙 **{price - buyer.balance:,}** more to buy this (it costs 🪙 {price:,})."
    name = listing.get("ITEM_NAME")
    room = _buyer_room(buyer, market, name)
    if room:
        return None, None, room
    seller = _player(listing.get("ITEM_OWNER"))
    if seller is None or not _seller_owns(seller, market, name):
        db.deleteMarketEntry({"_id": listing["_id"]})       # stale listing: the seller no longer has it
        return None, None, "That listing is no longer available (the seller doesn't have the item anymore). It has been removed."
    return listing, seller, None


def _build_item(listing, market):
    name = listing.get("ITEM_NAME")
    if market == "card":
        card = crown_utilities.create_card_from_data(db.queryCard({"NAME": name}))
        card.set_card_level_buffs([{"CARD": name, "LVL": listing.get("CARD_LEVEL", 1), "EXP": 0}])
        return card
    if market == "summon":
        summon = crown_utilities.create_summon_from_data(db.querySummon({"PET": name}))
        summon.level = listing.get("SUMMON_LEVEL", summon.level)
        summon.bond = listing.get("BOND_LEVEL", summon.bond)
        return summon
    arm = crown_utilities.create_arm_from_data(db.queryArm({"ARM": name}))
    arm.durability = listing.get("ARM_DURABILITY") or 25
    return arm


def _give(buyer, item, market):
    if market == "card":
        result = buyer.save_card(item)
        return result is True or (isinstance(result, str) and result.startswith("Gained"))
    if market == "summon":
        return buyer.save_summon(item) is True
    return buyer.save_arm(item) is True


def _take(seller, item, market):
    if market == "card":
        return seller.remove_card(item)
    if market == "summon":
        return seller.remove_summon(item.name)
    return seller.remove_arm(item.name)


async def execute_purchase(buyer_did, code, market):
    """Re-check and complete the purchase.  Returns (success, message)."""
    try:
        listing, seller, reason = await asyncio.to_thread(check_purchase, buyer_did, code, market)
        if reason:
            return False, reason
        claimed = await asyncio.to_thread(db.market_col.delete_one, {"_id": listing["_id"]})
        if getattr(claimed, "deleted_count", 0) != 1:
            return False, "Someone else just bought it."
        price = int(listing.get("PRICE") or 0)
        name = listing.get("ITEM_NAME")
        buyer = await asyncio.to_thread(_player, buyer_did)
        item = await asyncio.to_thread(_build_item, listing, market)
        if not await asyncio.to_thread(_give, buyer, item, market):
            restored = {k: v for k, v in listing.items() if k != "_id"}
            await asyncio.to_thread(db.createMarketEntry, restored)
            return False, "The item couldn't be added to your inventory, so nothing was charged. Please try again."
        await crown_utilities.curse(price, buyer_did)
        await crown_utilities.bless(price, listing.get("ITEM_OWNER"))
        await asyncio.to_thread(_take, seller, item, market)
        loggy.info(f"market: {buyer_did} bought {market} '{name}' from {listing.get('ITEM_OWNER')} for {price}")
        return True, f"You bought **{name}** for 🪙 **{price:,}**. It's in your inventory now."
    except Exception as ex:
        custom_logging.debug(ex)
        return False, "Something went wrong with that purchase. Nothing was charged if the item didn't arrive; please check and try again."


async def confirm_and_buy(client, ictx, author, code, market, ephemeral=False):
    """Ask the buyer to confirm, then buy.  ``ictx`` is the interaction to answer."""
    listing, seller, reason = await asyncio.to_thread(check_purchase, author.id, code, market)
    if reason:
        await ictx.send(embed=Embed(title="🏷️ Can't buy this", description=reason, color=0xE74C3C), ephemeral=ephemeral)
        return
    price = int(listing.get("PRICE") or 0)
    name = listing.get("ITEM_NAME")
    detail = ""
    if market == "card":
        detail = f" (level {listing.get('CARD_LEVEL', 1)})"
    elif market == "summon":
        detail = f" (level {listing.get('SUMMON_LEVEL', 1)}, bond {listing.get('BOND_LEVEL', 0)})"
    buyer = await asyncio.to_thread(_player, author.id)
    left = (buyer.balance - price) if buyer else 0
    tag = uuid.uuid4().hex[:10]
    row = ActionRow(
        Button(style=ButtonStyle.GREEN, label=f"Buy for {price:,}", emoji="🛒", custom_id=f"{tag}|yes"),
        Button(style=ButtonStyle.GREY, label="Cancel", custom_id=f"{tag}|no"),
    )
    embed = Embed(title="🏷️ Confirm purchase",
                  description=f"Buy **{name}**{detail} for 🪙 **{price:,}**?\nYou'll have 🪙 {left:,} left.",
                  color=0x5865F2)
    message = await ictx.send(embed=embed, components=[row], ephemeral=ephemeral)

    def check(event) -> bool:
        return event.ctx.author.id == author.id

    try:
        event = await client.wait_for_component(components=[f"{tag}|yes", f"{tag}|no"], check=check, timeout=120)
    except asyncio.TimeoutError:
        try:
            if not ephemeral and message is not None:
                await message.edit(embed=Embed(title="🏷️ Purchase timed out", description="Nothing was bought.", color=0x95A5A6), components=[])
        except Exception:
            pass
        return
    if event.ctx.custom_id.endswith("|no"):
        await event.ctx.edit_origin(embed=Embed(title="🏷️ Purchase cancelled", description="Nothing was bought.", color=0x95A5A6), components=[])
        return
    await event.ctx.defer(edit_origin=True)
    ok, text = await execute_purchase(author.id, code, market)
    await event.ctx.edit_origin(embed=Embed(title="🏷️ Purchased!" if ok else "🏷️ Purchase failed", description=text,
                                            color=0x2ECC71 if ok else 0xE74C3C), components=[])
