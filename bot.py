import custom_logging
import os
import datetime
from cogs.classes.custom_paginator import CustomPaginator
from ai import suggested_title_scenario
import db
import time
import classes as data
import translation_manager as tm
from language_cache import LanguageCache
from choicemanager import ChoicesManager
import messages as m
import help_commands as h
import aiohttp
from bson.int64 import Int64
import textwrap
import logging
from logger import loggy
from decouple import config
import textwrap
import random
import unique_traits as ut
now = time.asctime()
import asyncio
from characters import character_list
import requests
import json
import uuid
from cogs.quests import Quests
from interactions.ext.paginators import Paginator
from interactions import Task, IntervalTrigger, Client, ActionRow, Button, ButtonStyle, Intents, const, Status, Activity, listen, slash_command, global_autocomplete, InteractionContext, SlashCommandOption, OptionType, slash_default_member_permission, SlashCommandChoice, context_menu, CommandType, Permissions, cooldown, Buckets, Embed, AutocompleteContext, slash_option
import crown_utilities

logging.basicConfig()
cls_log = logging.getLogger(const.logger_name)
cls_log.setLevel(logging.WARNING)
translator = tm.TranslationManager(default_language="en")
language_cache = LanguageCache()

heartbeat_started = False
class CustomClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language_cache = language_cache
        self.translator = translator

    def get_text(self, user_id: int, key: str, language: str = None) -> str:
        """Get translated text for any user ID"""
        if language is None:
            language = self.language_cache.get_user_language(db.users_col, user_id)
        return self.translator.get_text(key, language)
    
bot = CustomClient(
    intents=Intents.MESSAGES | Intents.REACTIONS | Intents.GUILDS | Intents.TYPING | Intents.MESSAGE_CONTENT,
    sync_interactions=True,
    send_command_tracebacks=False,
    token=config('DISCORD_TOKEN' if config('ENV') == "production" else 'NEW_TEST_DISCORD_TOKEN')
    )


@listen()
async def on_ready():
    global heartbeat_started
    server_count = len(bot.guilds)
    await bot.change_presence(status=Status.ONLINE, activity=Activity(name=f"in {server_count} servers 🆚!\nGAME OVERHAUL HAS BEEN RELEASED! All accounts have been reset. Please use /register to start!", type=1))
    loggy.info('The bot is up and running')
    await bot.synchronise_interactions()
    if not heartbeat_started:
        check_heartbeat.start()
        heartbeat_started = True

def add_universes_names_to_autocomplete_list():
   try:
      response = db.queryAllUniverses()
      list_of_universes = []
      for universe in response:
            list_of_universes.append({"name": universe["TITLE"], "value": universe["TITLE"]})
      return sorted(list_of_universes, key=lambda x: x['name'])
   except Exception as e:
      loggy.critical(e)
      return False

def load(ctx, extension):
   bot.load_extension(f'cogs.{extension}')

def unload(ctx, extension):
   bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
   if filename.endswith('.py'):
      # :-3 removes .py from filename
      bot.load_extension(f'cogs.{filename[:-3]}')

async def validate_user(ctx):
   query = {'DID': str(ctx.author.id)}
   valid = db.queryUser(query)

   if valid:
      return True
   else:
      msg = await ctx.send(m.USER_NOT_REGISTERED, delete_after=5)
      return False


@slash_command(name="daily", description="Receive your daily reward and quests", scopes=crown_utilities.guild_ids)
@cooldown(Buckets.USER, 1, 86400)
async def daily(ctx):
   try:
      await ctx.defer()
      query = {'DID': str(ctx.author.id)}
      user_data = db.queryUser(query)
      player = crown_utilities.create_player_from_data(user_data)

      milestone_message = await Quests.milestone_check(player, "DAILY", 1)

      aicon = crown_utilities.prestige_icon(player.prestige)
      dailyamount = 100000
      daily_bonus = int(dailyamount * (player.rebirth + 1) + (1000000 * player.prestige))
         
      await crown_utilities.bless(daily_bonus, player.did)
      difference = daily_bonus - dailyamount

      
      if ctx.author.guild:
         server_query = {'GNAME': player.did}
         update_server_query = {
            '$inc': {'SERVER_BALANCE': daily_bonus}
         }
         updated_server = db.updateServer(server_query, update_server_query)
      
      # boss_key_message = "🗝️ | Boss Arena Unlocked" if player.boss_fought == True else ""
      bonus_message =f"❤️‍🔥 | *+🪙{'{:,}'.format(difference)}*" if difference > 0 else ""
      # prestige_message =f"**{aicon} Prestige {player.prestige} |** Quest Requirements Reduced!" if player.prestige > 0 else ""

      player.quests = db.queryUser({"DID": str(player.did)})["QUESTS"]
      current_quests = player.quests

      # Update quests with QUEST_FLAG as true
      for quest in crown_utilities.quest_list:
         if quest['QUEST_FLAG']:
            matching_quest = next((q for q in current_quests if q['TYPE'] == quest['TYPE']), None)
            if matching_quest:
                  matching_quest['AMOUNT'] = 0
                  matching_quest['COMPLETED'] = False
            else:
                  current_quests.append(quest)

      # Prepare the update data
      update_data = {
         'QUESTS': current_quests,
         'BOSS_FOUGHT': False,
         'VOTED': False
      }

      # Update the user's quests in the database
      await asyncio.to_thread(db.updateUserNoFilter, query, {'$set': update_data})

      # Determine the retry message and update RETRIES accordingly
      retry_message = f"🆚 | Rematches : {player.retries}"
      if player.retries >= 25:
         await asyncio.to_thread(db.updateUserNoFilter, query, {'$set': {'RETRIES': 25}})
      else:
         await asyncio.to_thread(db.updateUserNoFilter, query, {'$inc': {'RETRIES': 2}})
         retry_message = f"🆚 | Rematches : {player.retries} **+ 2**"

      quest_messages = []
      for quest in crown_utilities.quest_list:
         quest_messages.append(f"🆕 {quest['NAME']} 💎 {quest['REWARD']:,}")

      embedVar = Embed(title=f"☀️ Daily Rewards!", description=textwrap.dedent(f"""\
      Welcome back, {ctx.author.mention}!
      {retry_message}
      🪙 | +{'{:,}'.format(daily_bonus)}
      """), color=0xf1c40f)

      if milestone_message:
         # milestone message is a list of strings
         embedVar.add_field(name="🏆 **Milestone**", value="\n".join(milestone_message), inline=False
                            )
      embedVar.add_field(name="📜 **New Quests** */quest*", value="\n".join(quest_messages), inline=False)
      embedVar.add_field(name="Vote for Anime VS+!", value="🗳️ | **/vote** to earn daily rewards!", inline=False)
      embedVar.add_field(name="Patch Notes", value="📜 | Fixed the issue where you aren't able to add items to the marketplace or trade. Enjoy!\n**Codes for special unlocks coming soon!**", inline=False)
      embedVar.set_footer(text=f"☀️ | You can vote twice a Day with /daily!")
      await ctx.send(embed=embedVar)
   except Exception as ex:
      custom_logging.debug(ex)
      return
   

def check_quest_wins(win_value, prestige_level):
   check = win_value - prestige_level#casperjayden
   if check <= 0:
      return 1
   else:
      return check


@slash_command(name="gift", description="Give money to friend", options=[
   SlashCommandOption(name="player", description="Player to gift", type=OptionType.USER, required=True),
], scopes=crown_utilities.guild_ids)
@cooldown(Buckets.USER, 1, 5)
async def gift(ctx, player, amount: int):
   user2 = player
   vault = db.queryVault({'DID': str(ctx.author.id)})
   user_data = db.queryUser({'DID': str(ctx.author.id)})
   if user_data['LEVEL'] < 21:
      await ctx.send(f"🔓 Unlock Gifting by completing Floor 20 of the 🌑 Abyss! Use /solo to enter the abyss.")
      return

   balance = vault['BALANCE']
   tax = amount * .09
   amount_plus_tax = amount + tax

   if balance <= int(amount_plus_tax):
      await ctx.send(f"You do not have that amount (:coin{amount_plus_tax}) to gift.")
   else:
      await crown_utilities.bless(int(amount), user2.id)
      await crown_utilities.curse(amount_plus_tax, ctx.author.id)
      await ctx.send(f"🪙{amount} has been gifted to {user2.mention}.")
      return


@slash_command(name="roll", description="Spend 10,000 🪙coins per roll for a chance at random cards, arms, summons, and gems", options=[
    SlashCommandOption(name="rolls", description="Number of rolls to perform", choices=[
        SlashCommandChoice(name="1 Roll", value=1),
        SlashCommandChoice(name="5 Rolls", value=5),
        SlashCommandChoice(name="10 Rolls", value=10),
        SlashCommandChoice(name="25 Rolls", value=25),
    ], type=OptionType.INTEGER, required=False),
], scopes=crown_utilities.guild_ids)
@cooldown(Buckets.USER, 1, 45)
async def roll(ctx, rolls: int = 1):
    await ctx.defer()
    a_registered_player = await crown_utilities.player_check(ctx)
    if not a_registered_player:
        return
    
   
    cost = 10000 * rolls
   
   
    user = crown_utilities.create_player_from_data(a_registered_player)
    if user.balance < cost:
        embed = Embed(title="Gacha", description=f"You do not have enough 🪙 to roll the Gacha. It costs 🪙 {cost:,} coin for {rolls} Rolls.")
        await ctx.send(embeds=[embed])
        return
    
    await crown_utilities.curse(cost, user.did)

    # Retrieve all necessary data in one go
    cards, arms, summons, universes = await asyncio.gather(
        asyncio.to_thread(db.getCardsFromAvailableUniverses),
        asyncio.to_thread(db.getArmsFromAvailableUniverses),
        asyncio.to_thread(db.getSummonsFromAvailableUniverses),
        asyncio.to_thread(db.queryAllUniverses)
    )

    quest_message = await Quests.milestone_check(user, "ROLL", 1)
    
    all_cards = list(cards)
    all_arms = list(arms)
    all_summons = list(summons)
    universe_list = list(universes)

    items = []

    for _ in range(rolls):
        roll = random.random()
        if roll <= 0.0002:  # 0.02% chance
            scenario_or_destiny = [item for item in all_cards + all_arms if item['DROP_STYLE'] in ['SCENARIO', 'DESTINY']]
            if scenario_or_destiny:
                selected_item = random.choice(scenario_or_destiny)
                if 'NAME' in selected_item:
                    user.save_card(crown_utilities.create_card_from_data(selected_item))
                else:
                    user.save_arm(crown_utilities.create_arm_from_data(selected_item))
                items.append(selected_item)
        elif roll <= 0.001:  # 0.1% chance (cumulative)
            dungeon_summons = [item for item in all_summons if item['DROP_STYLE'] == 'DUNGEON']
            if dungeon_summons:
                selected_item = random.choice(dungeon_summons)
                user.save_summon(crown_utilities.create_summon_from_data(selected_item))
                items.append(selected_item)
        elif roll <= 0.005:  # 0.4% chance (cumulative)
            tales_summons = [item for item in all_summons if item['DROP_STYLE'] == 'TALES']
            if tales_summons:
                selected_item = random.choice(tales_summons)
                user.save_summon(crown_utilities.create_summon_from_data(selected_item))
                items.append(selected_item)
        elif roll <= 0.015:  # 1.0% chance (cumulative)
            dungeon_items = [item for item in all_cards + all_arms if item['DROP_STYLE'] == 'DUNGEON']
            if dungeon_items:
                selected_item = random.choice(dungeon_items)
                if 'NAME' in selected_item:
                    user.save_card(crown_utilities.create_card_from_data(selected_item))
                else:
                    user.save_arm(crown_utilities.create_arm_from_data(selected_item))
                items.append(selected_item)
        elif roll <= 0.05:  # 5.0% chance (cumulative)
            tales_items = [item for item in all_cards + all_arms if item['DROP_STYLE'] == 'TALES']
            if tales_items:
                selected_item = random.choice(tales_items)
                if 'NAME' in selected_item:
                    user.save_card(crown_utilities.create_card_from_data(selected_item))
                else:
                    user.save_arm(crown_utilities.create_arm_from_data(selected_item))
                items.append(selected_item)
        else:  # 95% chance
            gem_amount = random.randint(1000, 10000)
            selected_universe = random.choice(universe_list)
            user.save_gems(selected_universe["TITLE"], gem_amount)
            items.append({"type": "gems", "amount": gem_amount, "universe": selected_universe['TITLE']})

    super_rare_gif = "https://i.pinimg.com/originals/85/03/1d/85031d29916b8746829d7e721381cf6b.gif"
    rare_gif = "https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/alejandroaldana/23tRzVvUNcn54i4rmoPMmabLUHBJL19eqoNwRsnJrhuJ3TyHMww66C8c4fruCJUNNpfcQ.gif"
    normal_rare_gif = "https://pa1.narvii.com/6237/8d2ff4e7f9dce12a5772c597ae857f29e1804c92_hq.gif"

    embeds = []
    for item in items:
        if isinstance(item, dict) and item.get('type') == 'gems':
            embed = Embed(
                title="You have earned gems!",
                description=f"You earned 💎 {item['amount']:,} gems in {crown_utilities.crest_dict[item['universe']]} {item['universe']}"
            )
            embed.set_image(url=normal_rare_gif)
        else:
            name = item.get('NAME') or item.get('ARM') or item.get('PET')
            drop_style = item.get('DROP_STYLE')
            type_emoji = "🎴" if 'NAME' in item else "🦾" if 'ARM' in item else "🧬"

            if drop_style == 'DUNGEON':
                embed = Embed(title=f"You have earned a {type_emoji} item!", description=f"{type_emoji} {name} - You have earned a rare item!")
                embed.set_image(url=rare_gif)
            elif drop_style in ['SCENARIO', 'DESTINY']:
                embed = Embed(title=f"You have earned a {type_emoji} item!", description=f"{type_emoji} {name} - You have earned a super rare item!")
                embed.set_image(url=super_rare_gif)
            else:
                embed = Embed(title=f"You have earned a {type_emoji} item!", description=f"{type_emoji} {name} - You have earned an item!")
                embed.set_image(url=normal_rare_gif)

        if quest_message:
            embed.add_field(name="🏆 **Milestone**", value="\n".join(quest_message), inline=False)

        embed.set_thumbnail(url=user.avatar)
        embeds.append(embed)

    paginator = Paginator.create_from_embeds(bot, *embeds)
    paginator.show_select_menu = True
    await paginator.send(ctx)

# Should you only be able to donate to your own guild?
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


# @slash_command(name="invest", description="Invest money in your Family", scopes=crown_utilities.guild_ids)
# @cooldown(Buckets.USER, 1, 10)
async def invest(ctx, amount):
   user = db.queryUser({'DID': str(ctx.author.id)})
   family = db.queryFamily({'HEAD': user['DID']})
   vault = db.queryVault({'DID': str(ctx.author.id)})
   balance = vault['BALANCE']
   if family:
      if balance <= int(amount):
         await ctx.send("You do not have that amount to invest.", ephemeral=True)
      else:
         await crown_utilities.blessfamily_Alt(int(amount), user['DID'])
         await crown_utilities.curse(int(amount), ctx.author.id)
         transaction_message =f"🪙 | {user['DISNAME']} invested 🪙{amount} "
         update_family = db.updateFamily(family['HEAD'], {'$addToSet': {'TRANSACTIONS': transaction_message}})
         await ctx.send(f"**🪙{amount}** invested into **{user['NAME']}'s Family**.")
         return
   else:
      await ctx.send(f"Family does not exist")


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
     
      
# @slash_command(name="bounty", description="Set Association Bounty", options=[
#    SlashCommandOption(name="amount", description="Amount to set bounty to", type=OptionType.INTEGER, required=True),
# ], scopes=crown_utilities.guild_ids)
async def bounty(ctx, amount):
   negCurseAmount = 0 - abs(int(amount))
   posCurseAmount = 0 + abs(int(amount))
   user = db.queryUser({'DID': str(ctx.author.id)})
   guild_name = user['GUILD']
   if guild_name == 'PCG':
      await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
      return
   guild_query = {'GNAME' :guild_name}
   guild = db.queryGuildAlt(guild_query)
   founder = guild['FOUNDER']
   sworn = guild['SWORN']
   if user['DISNAME'] != founder and user['DISNAME'] != sworn:
      await ctx.send(m.NOT_LEADER, delete_after=5)
      return

   guild_bank = guild['BANK']
   guild_bounty = guild['BOUNTY']
   finalBount = guild_bounty + posCurseAmount
   finalBal = guild_bank + negCurseAmount
   if finalBal < 0:
      await ctx.send(f"Association does not have that much 🪙", delete_after=5)
      return
   else:
      update_query = {"$set": {'BOUNTY': int(finalBount)}, '$inc': {'BANK' : int(negCurseAmount)}}
      db.updateGuildAlt(guild_query, update_query)
      await ctx.send(f"New {guild['GNAME']} Bounty: :yen: {'{:,}'.format(finalBount)}! Use /raid `Association`{guild['GNAME']} to claim the Bounty!")
      return


# @slash_command(name="sponsor", description="Sponsor Guild with Association Funds", options=[
#    SlashCommandOption(name="guild", description="Guild to sponsor", type=OptionType.STRING, required=True),
#    SlashCommandOption(name="amount", description="Amount to sponsor", type=OptionType.INTEGER, required=True),
# ], scopes=crown_utilities.guild_ids)
async def sponsor(ctx, guild, amount):
   team = guild
   user = db.queryUser({'DID': str(ctx.author.id)})
   guild_name = user['GUILD']
   if guild_name == 'PCG':
      await ctx.send(m.GUILD_DOESNT_EXIST, delete_after=5)
      return
   
   guild_query = {'GNAME' :guild_name}
   guild = db.queryGuildAlt(guild_query)
   founder = guild['FDID']
   sworn = guild['WDID']
   shield = guild['SDID']
   guild_bank = guild['BANK']
   if int(amount) >= guild['BANK']:
      await ctx.send("Association does not have that much 🪙", delete_after=5)
      return

   if user['DID'] != founder and user['DID'] != sworn and user['DID'] != shield:
      await ctx.send(m.NOT_LEADER, delete_after=5)
      return

   team_name = team.lower()
   team_data = db.queryTeam({'TEAM_NAME' : team_name})

   if not team_data:
      await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)
      return

   sword_list = []
   for sword in guild['SWORDS']:
      sword_list.append(sword)

   if team_name not in sword_list:
      await ctx.send(m.USER_NOT_IN_GUILD, delete_after=5)
      return

   team_bank = team_data['BANK']
   transaction_message =f"{guild_name} sponsored {team_name} 🪙{amount}"
   update_query = {'$push': {'TRANSACTIONS': transaction_message}}
   response = db.updateGuildAlt(guild_query, update_query)
   await crown_utilities.blessteam(int(amount), team_name)
   await crown_utilities.curseguild(int(amount), guild['GNAME'])
   await ctx.send(f"{guild_name} sponsored {team_name} 🪙{amount}!!!")
   return


# @slash_command(name="fund", description="Fund Association From Guild Bank", options=[
#    SlashCommandOption(name="amount", description="Amount to fund", type=OptionType.INTEGER, required=True),
# ], scopes=crown_utilities.guild_ids)
async def fund(ctx, amount):
   try:
      user = db.queryUser({'DID': str(ctx.author.id)})
      team = db.queryTeam({'TEAM_NAME': user['TEAM'].lower()})
      team_guild = team['GUILD']
      guild = db.queryGuildAlt({'GNAME': team['GUILD']})
      guild_query = {"GNAME": guild['GNAME']}
      if team_guild =="PCG":
         await ctx.send("Your team must join a Association First!")
         return
      if user['TEAM'] == 'PCG' or user['DISNAME'] != team['OWNER']:
         await ctx.send("You must be owner of team to fund the Association. ")
         return

      balance = team['BANK']
      if balance <= int(amount):
         await ctx.send("You do not have that amount to fund.")
      else:
         await crown_utilities.curseteam(int(amount), team['TEAM_NAME'])
         await blessguild_Alt(int(amount), str(team_guild))
         #guild_query = {"GNAME": {str(team_guild)}}
         transaction_message =f"{team['TEAM_DISPLAY_NAME']} funded 🪙{amount}"
         update_query = {'$push': {'TRANSACTIONS': transaction_message}}
         response = db.updateGuildAlt(guild_query, update_query)
         await ctx.send(f"{team_guild} has been funded 🪙 {amount}.")
         return
   except Exception as ex:
      loggy.error(f"Error in Fund command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #     trace.append({
      #         "filename": tb.tb_frame.f_code.co_filename,
      #         "name": tb.tb_frame.f_code.co_name,
      #         "lineno": tb.tb_lineno
      #     })
      #     tb = tb.tb_next
      # print(str({
      #     'type': type(ex).__name__,
      #     'message': str(ex),
      #     'trace': trace
      # }))
      await ctx.send(f"Error when funding Association. Alert support. Thank you!")
      return


async def blessguild_Alt(amount, guild):
   blessAmount = amount
   posBlessAmount = 0 + abs(int(blessAmount))
   query = {'GNAME': str(guild)}
   guild_data = db.queryGuildAlt(query)
   if guild_data:
      hall = guild_data['HALL']
      hall_data = db.queryHall({'HALL': hall})
      multiplier = hall_data['MULT']
      update_query = {"$inc": {'BANK': posBlessAmount}}
      db.updateGuildAlt(query, update_query)
   else:
      loggy.error(f"Guild {guild} does not exist.")


@slash_command(description="Input Codes", options=[
   SlashCommandOption(name="code_input", description="Code to input", type=OptionType.STRING, required=True),
], scopes=crown_utilities.guild_ids)
@cooldown(Buckets.USER, 1, 60)
async def code(ctx, code_input: str):
   await ctx.defer()
   try:
      query = {'DID': str(ctx.author.id)}
      user_data = db.queryUser(query)
      user = crown_utilities.create_player_from_data(user_data)
      code = db.queryCodes({'CODE_INPUT': code_input})
      
      if code and code['AVAILABLE']:
         coin = code['COIN']
         gems = code['GEMS']
         exp = code['EXP']
         card = code['CARD']
         arm = code['ARM']
         summon = code['SUMMON']
         equipped_card = crown_utilities.create_card_from_data(db.queryCard({'NAME': user.equipped_card}))
         card_drop = db.queryCard({'NAME': card}) if card else ""
         arm_drop = db.queryArm({'NAME': arm}) if arm else ""
         embed_list = []
         if code_input not in user.used_codes:
            if gems:
               if not user.gems:
                  universe_to_add_gems = equipped_card.universe
                  user.save_gems(universe_to_add_gems, gems)
               for universe in user.gems:
                  user.save_gems(universe["UNIVERSE"], gems)
               embed = Embed(title="Gems Increased", description=f"💎 **{gems:,}** gems have been added to your balance!", color=0x00ff00)
               embed_list.append(embed)

            if coin:
               await crown_utilities.bless(int(coin), user.did)
               embed = Embed(title="Gold Increased", description=f"🪙 **{coin:,}** gold have been added to your balance!", color=0x00ff00)
               embed_list.append(embed)
            
            if card_drop:
               card = crown_utilities.create_card_from_data(card_drop)
               if card not in user.cards or card not in user.storage:
                  user.save_card(card)
                  embed = Embed(title="🎴 Card Drop", description=f"You received **{card.name}** from {card.universe_crest} {card.universe}!", color=0x00ff00)
                  embed_list.append(embed)
            
            if arm_drop:
               arm = crown_utilities.create_arm_from_data(arm_drop)
               if arm not in user.arms or arm not in user.storage:
                  user.save_arm(arm)
                  embed = Embed(title="🛡️ Arm Drop", description=f"You received **{arm.name}** from {arm.universe_crest} {arm.universe}!", color=0x00ff00)
                  embed_list.append(embed)
            
            if exp:
               user = await bot.fetch_user(ctx.author.id)
               mode = "Purchase"
               level_response = await crown_utilities.cardlevel(user, mode, exp)
               level_up_message = f"Your 🎴 **{equipped_card.name}** card leveled up {level_response:,} times!" if level_response else f"Your 🎴 **{equipped_card.name}** card gained {exp:,} experience points!"
               embed = Embed(title="Experience Gained", description=f"{level_up_message}", color=0x00ff00)
               embed_list.append(embed)
            response = db.updateUserNoFilter(query, {'$addToSet': {'USED_CODES': code_input}})
            if embed_list:
               paginator = Paginator.create_from_embeds(bot, *embed_list)
               paginator.show_select_menu = True
               await paginator.send(ctx)
         else:
            loggy.info(f"Code {code_input} has been used by {ctx.author}")
            embed = Embed(title="Code Already Used", description=f"{ctx.author.mention} has already used **{code_input}**", color=0x00ff00)
            await ctx.send(embed=embed)
            return
      else:
         embed = Embed(title="Invalid Code", description=f"{ctx.author.mention} has entered an invalid code **{code_input}**", color=0x00ff00)
         await ctx.send(embed=embed)
         return
   except Exception as ex:
      custom_logging.debug(ex)
      return


# async def DM(ctx, user: User, m,  message=None):
#     message = message or "This Message is sent via DM"
#     await user.send(m)

# @slash_command(name="levelme", description="Level up your character", scopes=crown_utilities.guild_ids)
# @slash_option(
#    name="exp",
#    description="exp_to_give",
#    opt_type=OptionType.INTEGER,
#    required=False,
# )
# async def levelme(ctx, exp: int = 0):
#    await ctx.defer()
#    try:
#       user = await bot.fetch_user(ctx.author.id)
#       mode = "Purchase"
#       await crown_utilities.cardlevel(user, mode, exp)
#       await ctx.send(f"blah")
#    except Exception as ex:
#       custom_logging.debug(ex)
#       await ctx.send(f"blah")
#       return
 

# @slash_command(name="performance", description="Toggles Text Only Performance Mode", scopes=crown_utilities.guild_ids)
# async def performance(ctx):
#    try:
#       player = db.queryUser({"DID": str(ctx.author.id)})
#       performance_mode = not player.get("PERFORMANCE", False)
#       db.updateUserNoFilter(
#          {"DID": str(ctx.author.id)}, {"$set": {"PERFORMANCE": performance_mode}}
#       )

#       embed = Embed(title=f"Performance Mode {crown_utilities.utility_emojis['ON'] if performance_mode else crown_utilities.utility_emojis['OFF']}")
#       await ctx.send(embed=embed)
#    except Exception as ex:
#       loggy.error(f"Error in performance command: {ex}")
#       # trace = []
#       # tb = ex.__traceback__
#       # while tb is not None:
#       #       trace.append({
#       #          "filename": tb.tb_frame.f_code.co_filename,
#       #          "name": tb.tb_frame.f_code.co_name,
#       #          "lineno": tb.tb_lineno
#       #       })
#       #       tb = tb.tb_next
#       # print(str({
#       #       'type': type(ex).__name__,
#       #       'message': str(ex),
#       #       'trace': trace
#       # }))
#       await ctx.send("There's an issue with your Performance Mode. Seek support in the Anime 🆚+ support server", ephemeral=True)

# @slash_command(description="rewards for voting", scopes=crown_utilities.guild_ids)
# async def voted(ctx):
#    try:
#       query = {'DID': str(ctx.author.id)}
#       user = db.queryUser(query)
#       vault = db.queryVault(query)
#       gem_list = vault['GEMS']
#       prestige = int(user['PRESTIGE'])
#       aicon = crown_utilities.prestige_icon(prestige)
#       user_completed_tales = user['CROWN_TALES']
#       rebirth = int(user['REBIRTH'])

#       voting_amount = 5000000
#       voting_gems = 500000
#       gem_bonus = int(voting_gems * (rebirth + 1) + (500000 * prestige))
#       voting_bonus = int(voting_amount * (rebirth + 1) + (2000000 * prestige))
#       if user['VOTED']:
#          await ctx.send("You've already received your voting rewards!")
#          return
#       else:
#          auth_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk1NTcwNDkwMzE5ODcxMTgwOCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjQ5MDAyNDY0fQ.zNf3ECu2PBWVlfYlYH9YMy7PRb2P-sQFBGRkBp-DwUo'
#          head = {'Authorization': 'Bearer ' + auth_token}
         
#          response = requests.get(f"https://top.gg/api/bots/955704903198711808/check?userId={ctx.author.id}", headers=head)
#          response_dict = json.loads(response.text)
#          retry_message =f"🆚 Rematches : **{user['RETRIES']}**"
#          if response_dict['voted'] == 1:
#             if gem_list:
#                for universe in gem_list:
#                   update_query = {
#                      '$inc': {'GEMS.$[type].' + "GEMS": gem_bonus}
#                   }
#                   filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
#                   res = db.updateUser(query, update_query, filter_query)

#             await crown_utilities.bless(int(voting_bonus), ctx.author.id)
#             respond = db.updateUserNoFilter(query, {'$set': {'VOTED': True}})
#             retry_message =f"🆚 Rematches : **{user['RETRIES']}**"  
#             db.updateUserNoFilter(query, {'$inc': {'RETRIES': 3}})
#             retry_message =f"🆚 Rematches : {user['RETRIES']} **+ 3**!"


#             embedVar = Embed(title=f"✅ Daily Voter Rewards!", description=textwrap.dedent(f"""\
#             Thank you for voting, {ctx.author.mention}!
            
#             **Daily Voter Earnings** 
#             🪙 **{'{:,}'.format(voting_bonus)}**
#             💎 **{'{:,}'.format(gem_bonus)}** *all craftable universes*
#             {retry_message}
            
#             [Support our Patreon for Rewards!](https://www.patreon.com/partychatgaming?fan_landing=true)
#             [Add Anime VS+ to your server!](https://discord.com/api/oauth2/authorize?client_id=955704903198711808&permissions=139586955344&scope=applications.commands%20bot)
#             """), color=0xf1c40f)
            
#             await ctx.send(embed=embedVar)

#          else:
#             retry_message =f"🆚 Rematches : **+3**"
#             embedVar = Embed(title=f"❌ Daily Voter Rewards!", description=textwrap.dedent(f"""\
#             You have not voted for Anime VS+ today, {ctx.author.mention}!
#             To earn your voter rewards, [Vote for Anime VS+!](https://top.gg/bot/955704903198711808/vote)
#             **What are the Daily Voter Rewards?** 
#             🪙 **{'{:,}'.format(voting_bonus)}**
#             💎 **{'{:,}'.format(gem_bonus)}**
#             {retry_message}
            
#             [Join the Anime VS+ Support Server](https://discord.gg/pcn)
#             """), color=0xf1c40f)
            
#             await ctx.send(embed=embedVar)

#    except Exception as e:
#       loggy.error(e)
#       await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
#       return


# Update Later


# async def restart_bot():
#     await bot.stop()
#     await bot.start()


@listen()
async def on_disconnect():
    loggy.warning("Bot disconnected. Attempting to reconnect...")
    await asyncio.sleep(5)  # Wait before attempting to reconnect

async def restart_bot():
    loggy.info("Restarting bot...")
    await bot.stop()
    await asyncio.sleep(5)  # Wait before restarting
    await bot.start()

@Task.create(IntervalTrigger(minutes=5))
async def check_heartbeat():
    try:
        latency = bot.latency
        loggy.info(f'Heartbeat check - latency: {latency}')
        if latency and latency > 2.0:  # Adjusted threshold to 2 seconds
            loggy.warning('High latency detected, restarting bot...')
            await restart_bot()
    except Exception as e:
        loggy.error(f'Error during heartbeat check: {e}')
        await restart_bot()

# Run the bot
try:
    bot.start()
except KeyboardInterrupt:
    loggy.info("Bot stopped by user")
except Exception as e:
    loggy.error(f"An error occurred while running the bot: {e}")
finally:
    # Ensure the bot is properly closed
    if not bot.is_closed:
        asyncio.run(bot.stop())  # Use asyncio.run to properly close the bot


