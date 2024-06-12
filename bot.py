import custom_logging
import datetime
from cogs.classes.custom_paginator import CustomPaginator
from ai import suggested_title_scenario
import db
import time
import classes as data
import messages as m
import help_commands as h
import aiohttp
from bson.int64 import Int64
import textwrap
import os
import logging
from logger import loggy
from decouple import config
import textwrap
import random
import unique_traits as ut
now = time.asctime()
import asyncio
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

guild_ids = None
guild_id = None
guild_channel = None

# bot = Client(intents=Intents.ALL, sync_interactions=True, send_command_tracebacks=False)
bot = Client(intents=Intents.ALL, sync_interactions=True, send_command_tracebacks=False, token=config('DISCORD_TOKEN' if config('ENV') == "production" else 'NEW_TEST_DISCORD_TOKEN'))

@listen()
async def on_ready():
   server_count = len(bot.guilds)
   await bot.change_presence(status=Status.ONLINE, activity=Activity(name=f"in {server_count} servers 🆚!", type=1))
   loggy.info('Bot is ready!')
   check_heartbeat.start()


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


if config('ENV') == "production":
   guild_id = 543442011156643871
   guild_channel = 957061470192033812
else:
   guild_ids = [839352855000776735]
   guild_id = 839352855000776735
   guild_channel = 962580388432195595

def load(ctx, extension):
   bot.load_extension(f'cogs.{extension}')

def unload(ctx, extension):
   bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
   if filename.endswith('.py'):
      # :-3 removes .py from filename
      bot.load_extension(f'cogs.{filename[:-3]}')

# @context_menu(name="pingme", context_type=CommandType.USER)
# async def pingme(ctx: InteractionContext):
#     member: Member = ctx.target
#     await ctx.send(member.mention)

# @context_menu(name="clickme", context_type=CommandType.MESSAGE)
# async def clickme(ctx: InteractionContext):
#    message: Message = ctx.target
#    print(message)
#    await ctx.send("You clicked on a message!")

# @slash_command(name="ping")
# async def ping(ctx: InteractionContext):
#    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


@slash_command(name="help", description="Learn the commands", options=[
                     SlashCommandOption(
                            name="selection",
                            description="select an option you need help with",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="⚔️ How to Play?",
                                    value="play",
                                ),
                                SlashCommandChoice(
                                    name="❓ What do these emoji's mean?",
                                    value="legend",
                                ),
                                SlashCommandChoice(
                                    name="🥋 What are classes?",
                                    value="classes",
                                ),
                                SlashCommandChoice(
                                    name="🦠 What are enhancers?",
                                    value="enhancers",
                                ),
                                SlashCommandChoice(
                                    name="🔅 What are elements?",
                                    value="elements",
                                ),
                                SlashCommandChoice(
                                    name="👑 Your Cards, Accessories, Quests, Destinies, Shop, Blacksmith, Trade, Gift, Analysis, Codes",
                                    value="menu",
                                ),
                                SlashCommandChoice(
                                    name="🌍 All Info, Cards, Accessories, Quests, Destinies a universe has to offer",
                                    value="universe",
                                ),
                                SlashCommandChoice(
                                    name="👥 Family, Guild, Association",
                                    value="teams",
                                ),
                                SlashCommandChoice(
                                    name="📔 Read the Anime VS+ Manual",
                                    value="manual",
                                ),

                            ]
                        )
                    ]
 ,scopes=guild_ids)
async def help(ctx: InteractionContext, selection):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
   
   if selection == "menu":
      embedVar = Embed(title=f"Your stuff, your way!", description=h.CTAP_COMMANDS, color=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "legend":
      embedVar = Embed(title=f"What do these emoji's mean?", description=h.LEGEND, color=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "elements":
      embed_list = []
      for i in range(0, len(h.ELEMENTS_LIST), 5):
            sublist = h.ELEMENTS_LIST[i:i + 5]
            embedVar = Embed(title=f"What does each element do?",description="\n".join(sublist), color=0x7289da)
            embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
            embed_list.append(embedVar)

      paginator = Paginator.create_from_embeds(bot, *embed_list)
      paginator.show_select_menu = True
      await paginator.send(ctx)

   if selection == "play":
      embedVar = Embed(title=f"Start playing now!", description=h.CROWN_UNLIMITED_GAMES, color=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return


   if selection == "universe":
      embedVar = Embed(title=f"🌍 Universe Info!", description=h.UNIVERSE_STUFF, color=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "teams":
      embedVar = Embed(title=f"Gang up and play!", description=h.BOT_COMMANDS, color=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "classes":
      await classes(ctx)
      return

   if selection == "enhancers":
      await enhancers(ctx)
      return
      
   if selection == "manual":
      await animevs(ctx)
      return


async def validate_user(ctx):
   query = {'DID': str(ctx.author.id)}
   valid = db.queryUser(query)

   if valid:
      return True
   else:
      msg = await ctx.send(m.USER_NOT_REGISTERED, delete_after=5)
      return False


# @slash_command(name="Enhancers", description="List of Enhancers", scopes=guild_ids)
async def enhancers(ctx):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"

   try:
      embedVar1 = Embed(title=f"Enhancer Type: Boosts",color=0x7289da)
      embedVar1.set_thumbnail(url=avatar)
      embedVar1.add_field(name="`BOOSTS`", value="**ATK**\n**Title, Arm, Card Passive Effect:** Increase Attack by Flat AP value.\n**Card Active Enhancer Effect:** Increase Attack By AP %.\n\n**DEF**\n**Title, Arm, Card Passive Effect:** Increase Defense by Flat AP value.\n**Card Active Enhancer Effect:** Increase Defense By AP %.\n\n**HLT**\n**Title, Arm, Card Passive Effect:** Increase Health by Flat AP value.\n**Card Active Enhancer Effect:** Increase Health By Flat AP + 16% of Current Health.\n\n**STAM** - Increase Stamina by Flat AP\n\n")
      embedVar1.set_footer(text=f"/help - Bot Help")

      embedVar2 = Embed(title=f"Enhancer Type: Steals",color=0x7289da)
      embedVar2.set_thumbnail(url=avatar)
      embedVar2.add_field(name="`STEALS`", value="**FLOG**- Steal Opponent Attack and Add it to Your Attack by AP %\n\n**WITHER**- Steal Opponent Defense and Add it to Your Defense by AP %\n\n**LIFE**\n**Title, Arm, Card Passive Effect:** Steal Opponent Health and Add it to your Max Health by AP %\n**Card Active Enhancer Effect:** Steal Opponent Health and Add it to your Current Health by Flat AP + 9% of Opponent Current Health. \n\n**DRAIN** - Steal Opponent Stamina and Add it to your Stamina by Flat AP\n\n")
      embedVar2.set_footer(text=f"/help - Bot Help")

      embedVar3 = Embed(title=f"Enhancer Type: Sacrifice",color=0x7289da)
      embedVar3.set_thumbnail(url=avatar)
      embedVar3.add_field(name="`SACRIFICE`", value="**RAGE** - Decrease Your Defense by AP %, Increase All Moves AP by Amount of Decreased Defense\n\n**BRACE** - Decrease Your Attack by AP %, Increase All Moves AP By Amount of Decreased Attack\n\n**BZRK** - Decrease Your Current Health by AP %,  Increase Your Attack by Amount of Decreased Health\n\n**CRYSTAL** - Decrease Your Health by AP %, Increase Your Defense by Amount of Decreased Health\n\n")
      embedVar3.set_footer(text=f"/help - Bot Help")

      embedVar4 = Embed(title=f"Enhancer Type: Conversion",color=0x7289da)
      embedVar4.set_thumbnail(url=avatar)
      embedVar4.add_field(name="`CONVERSION`", value="**STANCE** - Swap Your Attack and Defense, Increase Your Defense By Flat AP\n\n**CONFUSE** - Swap Opponenet Attack and Defense, Decrease Opponent Defense by Flat AP\n\n")
      embedVar4.set_footer(text=f"/help - Bot Help")

      embedVar5 = Embed(title=f"Enhancer Type: Time Manipulation",color=0x7289da)
      embedVar5.set_thumbnail(url=avatar)
      embedVar5.add_field(
         name="`TIME MANIPULATION`", 
         value=(
            "**BLINK**  - Decreases Your Stamina by AP, Increases Opponent Stamina by AP. No swapping.\n\n"
            "**SLOW** - Increases the turn total by AP.\n\n"
            "**HASTE** - Decreases the turn total by AP.\n\n"
         )
      )
      embedVar5.set_footer(text="/help - Bot Help")

      embedVar6 = Embed(title=f"Enhancer Type: Control",color=0x7289da)
      embedVar6.set_thumbnail(url=avatar)
      embedVar6.add_field(name="`CONTROL`", value="**SOULCHAIN** - You and Your Opponent's Stamina Equal AP\n\n**GAMBLE** - At the cost of your total stamina, You and Your Opponent's Health Equal between 500 & AP value\n\n")
      embedVar6.set_footer(text=f"/help - Bot Help")

      embedVar7 = Embed(title=f"Enhancer Type: Fortitude",color=0x7289da)
      embedVar7.set_thumbnail(url=avatar)
      embedVar7.add_field(name="`FORTITUDE`", value="**GROWTH**- Decrease Your Max Health by 10%, Increase Your Attack, Defense and AP Buff by AP\n\n**FEAR** - Decrease Your Max Health and Health by 20%, Decrease Opponent Attack, Defense, and reduce Opponent AP Buffs by AP\n\n")
      embedVar7.set_footer(text=f"/help - Bot Help")

      embedVar8 = Embed(title=f"Enhancer Type: Damage",color=0x7289da)
      embedVar8.set_thumbnail(url=avatar)
      embedVar8.add_field(name="`DAMAGE`", value="**WAVE** - Deal Flat AP Damage to Opponent. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will deal 75% AP Damage.*\n\n**BLAST** - Deal Flat AP Damage to Opponent. AP Increases each turn.\n\n")
      embedVar8.set_footer(text=f"/help - Bot Help")

      embedVar9 = Embed(title=f"Enhancer Type: Divinity",color=0x7289da)
      embedVar9.set_thumbnail(url=avatar)
      embedVar9.add_field(name="`DIVINITY`", value="**CREATION** - Increase Max Health by Flat AP. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will heal Health & Max Health for 75% AP.*\n\n**DESTRUCTION** - Decrease Your Opponent Max Health by Flat AP (only opponent on PET use). AP Increases each turn.\n\n")
      embedVar9.set_footer(text=f"/help - Bot Help")
      
      embedVar10 = Embed(title=f"Arm Enhancer Type: Offensive",color=0x7289da)
      embedVar10.set_thumbnail(url=avatar)
      embedVar10.add_field(name="`OFFENSE`", value="**BASIC** - Equip a new Basic Attack and Element \n\n**SPECIAL** - Equip a new Special Attack and Element \n\n**ULTIMATE** - Equip a new Ultimate Attack and Element \n\n**ULTIMAX** - Increase **ALL** Attack Move Ability Power by Value \n\n**MANA** - Increase 🦠 Enhancer Ability Power by Percentage \n\n💉 **SIPHON** - Heal for 10% DMG + AP\n\n")
      embedVar10.set_footer(text=f"/help - Bot Help")
      
      embedVar11 = Embed(title=f"Arm Enhancer Type: Defensive",color=0x7289da)
      embedVar11.set_thumbnail(url=avatar)
      embedVar11.add_field(name="`DEFENSE`", value="🌐 **SHIELD**- Grant Damage absorbing Shield until destroyed \n\n💠 **BARRIER** - Blocks all Attack Damage until player Attacks or is Destoyed (Enhancers Exempt)\n\n🔄 **PARRY** - Reflects 25% Damage back to Attacker\n\n")
      embedVar11.set_footer(text=f"/help - Bot Help")
      

      embeds = [embedVar1, embedVar2, embedVar3, embedVar4, embedVar5, embedVar6, embedVar7, embedVar8, embedVar9, embedVar10, embedVar11]
      paginator = CustomPaginator.create_from_embeds(bot, *embeds)
      paginator.show_select_menu = True
      await paginator.send(ctx)
      # await Paginator(bot=bot, ctx=ctx, pages=embeds, timeout=60).run()
      
   
   except Exception as ex:
            loggy.error(f"Error in enhancers: {ex}")
            await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
            return


async def classes(ctx):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
    
   class_descriptions = [
        (crown_utilities.class_emojis['SUMMONER'], "Summoner", "Can use Summon from start of battle. Summon attacks are boosted based on Card Tier."),
        (crown_utilities.class_emojis['ASSASSIN'], "Assassin", "Initial Attacks cost 0 Stamina and have increased Critical Chance\nCommon - 1 Attack\nRare - 2 Attacks\nLegendary - 3 Attacks\nMythic - 4 Attacks\nGod - 5 Attacks.\Poison & Death damage boosted."),
        (crown_utilities.class_emojis['FIGHTER'], "Fighter", "Starts each fight with up to 6 Parries\nCommon - 2 Parry\nRare - 3 Parries\nLegendary - 4 Parries\nMythic - 5 Parries\nGod - 6 Parries.\nDouble Parry on Physical damage proc."),
        (crown_utilities.class_emojis['RANGER'], "Ranger", "Starts each fight with up to 6 Barriers & can attack without disengaging Barrier\nCommon - 2 Barriers\nRare - 3 Barriers\nLegendary - 4 Barriers\nMythic - 5 Barriers\nGod - 6 Barriers."),
        (crown_utilities.class_emojis['TANK'], "Tank", "Starts each fight with Card Tier * 500 Shield & gain the same Shield on Resolve\nCommon - 500/1000/1500 Shield\nRare - 2000/2500\nLegendary - 3000/3500\nMythic - 4000/4500\nGod - 5000."),
        (crown_utilities.class_emojis['SWORDSMAN'], "Swordsman", "On Resolve, Gain up to 6 Critical Strikes\nCommon - 2 Attack\nRare - 3 Attacks\nLegendary - 4 Attacks\nMythic - 5 Attacks\nGod - 6 Attacks\nBleed damage boosted."),
        (crown_utilities.class_emojis['MONSTROSITY'], "Monstrosity", "On Resolve gain up to 6 Double Strikes\nCommon - 2 Attack\nRare - 3 Attacks\nLegendary - 4 Attacks\nMythic - 5 Attacks\nGod - 6 Attacks."),
        (crown_utilities.class_emojis['MAGE'], "Mage", "Increases Elemental damage up to 60%\nElemental effects are greatly boosted"),
        (crown_utilities.class_emojis['HEALER'], "Healer", "Stores up to 80% of damage taken and heals Health and Max Health for the total amount each Focus\nLifesteal abilities are boosted\nStacked Status effects removed on Focus"),
    ]
    
   embed_list = []
   embedVar = Embed(title=f"Classes", description=textwrap.dedent(f"""\
   🥋 **Card Class**
   Your Class grants you a boost in battle
   The boost is determined by your Card Tier Range
   Common : [1 - 3]
   Rare : [4 - 5]
   Legendary : [6 - 7]
   Mythical : [8 - 9]
   God : [10]
   """),color=0x7289da)
   embed_list.append(embedVar)
   for emoji, title, description in class_descriptions:
        embedVar = Embed(title=title, description=f"{emoji} {description}", color=0x7289da)
        embedVar.set_thumbnail(url=avatar)
        embed_list.append(embedVar)

   paginator = CustomPaginator.create_from_embeds(bot, *embed_list)
   paginator.show_select_menu = True
   await paginator.send(ctx)


# @slash_command(description="Anime VS+ Manual", scopes=guild_ids)
async def animevs(ctx):
   try:
      avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"


      embedVar1 = Embed(title=f"About Anime VS+",color=0x7289da)
      
      embedVar1.set_thumbnail(url=avatar)
      
      embedVar1.add_field(name="**About The Game!**", value=textwrap.dedent(f"""\
         
      **Anime VS+** is a Multiplatform Card Game exploring **Universes** from your favorite Video Game and Anime Series!

      Explore Tales, Dungeons, and Bosses! Play **Solo**, or with **Friends**!
      
      Customize your experince by setting your personal /difficulty!
      """))

      embedVar2 = Embed(title=f"Getting Started", description=textwrap.dedent(f"""\
      Players begin with 3 cards from the **Starter Universes**.
      
      The Title **Starter** and the Arm **Stock** are equipped.
      
      Your first Summon **Chick** will be joining as well!
         
      Play **Single Player** and **Multiplayer** Modes to earn 🪙
      Buy and equip better Items to Conquer the Multiverse!
      """), color=0x7289da)
      
      embedVar2.set_thumbnail(url=avatar)
      
      embedVar0 = Embed(title=f"Cards", description=textwrap.dedent(f"""\
      Players begin with 3 cards from the **Starter Universes**.
      
      The Title **Starter** and the Arm **Stock** are equipped.
      
      Your first Summon **Chick** will be joining as well!
         
      Play **Single Player** and **Multiplayer** Modes to earn 🪙
      Buy and equip better Items to Conquer the Multiverse!
      """), color=0x7289da)
      
      embedVar0.set_thumbnail(url=avatar)

      embedVar3 = Embed(title=f"Card Mechanics", description=textwrap.dedent(f"""\
      **Card Stats** 
      Health (**HLT**) Stamina (**STAM**) Attack (**ATK**) Defense(**DEF**)
      
      🥋 **Card Class**
      Your Class determines how you enter the battle
      Use /help to find information on **Classes**
      
      **Cards Have 5 Abilities** 
      3 Attack Moves
      1 Enhancer
      1 Block
      
      **Attack Moves**
      Attacks inflict damage on the opponent.
      Each Attack matches an **Emoji** and **Stamina Cost** in the Movelist.
      💥 Basic Attack _uses 10 stamina_
      ☄️ Special Attack _uses 30 stamina_
      🏵️ Ultimate Attack _uses 80 stamina_
      
      🔅**Elemental Damage**
      Attacks have bonus effects based on the 🔅**Element** Type
      Use /help to find information on **Elements**
      
      **Enhancer**
      Enhancers either boost your stats or inflict status effects on your opponent. Use **/help** for full list of **Enhancers** and their effects.
      🦠 Enhancer _uses 20 stamina_
      
      **Block**
      Doubles Defense for 1 turn
      🛡️ _uses 20 stamina_ 
      """), color=0x7289da)
      
      embedVar3.set_thumbnail(url=avatar)
      
      embedVar11 = Embed(title=f"Card Types", description=textwrap.dedent(f"""                                                                           
      🎴 **Universe Cards** - Purchasable in the **Shop** and Drops in **Tales**
      🃏 **Card Skins** - Create in the **/craft**
      🔥 **Dungeon Cards** - Drops in **Dungeons**
      ✨ **Destiny Cards** - Earned via **Destinies**
      👹 **Boss Cards** - Exchange for **Boss Souls**
      
      **Cards Have 7 Passive Elements** 
      Card Type
      Card Tier
      Affinities
      1 Unique Passive
      1 Universe Trait
      Card Level
      Destinies
      
      🀄 **Card Tier**
      Card Tier Determines Base Stats and Enhancer Types/Values.
      Common : Tier 1 - 3
      Rare : Tier 4 - 5
      Legendary : Tier 6 - 7
      
      🔅 **Affinities**
      Affinities determine how you card reacts to **Damage types**
      Weaknesses - Take more damage
      Resistances - Take less damage
      Immunities - Immune to damage
      Repels - Reflects damage back
      Absorb - Absorbs damage as Health
      
      🩸 **Unique Passive**
      Enhancers that take effect **at the beginning** of the battle.

      ♾️ **Universe Traits**
      Universe specific abilities activated during battle. 
      Use **/traits** for a full list.
      
      🎇 **Card Level**
      As you battle your card will level up, increasing Stats and Ability Power 
      Cards Start at **Level 0** and Max out at **Level 3500**

      ✨ **Destinies**
      Card Specific Quests in scenarios that earn **Destiny Cards**
      
      🃏 **Skins**
      Card Skins have different stats and abilities but can complete the main card **Destinies** !
   
      """), color=0x7289da)
      
      embedVar11.set_thumbnail(url=avatar)
      
      embedVar17 = Embed(title=f"Damage, Elements & Talismans", description=textwrap.dedent(f"""                                                                           
      🗯️**Engagement** Each of you Attack Moves deals damage based on the **Engagement**.
      
      💢: **Desperate Engagement**: Your opponent has overwhelming defense... Deal %33-%50 of AP
      ❕: **Brave Engagement**: Your opponent's defense is strong. Deal %50-%75 AP
      ‼️: **Nuetral Engagement**: Your attack and defense are nuetral. Deal %75-%120 AP
      〽️x1.5: **Aggressive Engagement**: Your attacks deal additional damage. Deal %120-%150 AP
      ❌x2: **Lethal Engagement**: Your attacks are lethal! Deal $150-%200 AP
      
      The Engagement is a factor of Attack + Move Ap vs Opponent Defense
      When your attack is higher than your oppoenents defense you will deal more damage
      
      🏃**Evasion**
      Your cards speed determines your evasion stat.
      **Fast** Cards SPD [70-100] increase their evasion by 5% every 10 Speed STAT i.e SPD 80 = 10% Evasion
      **Slow** Cards SPD [0-30] decrease their evasion by 5% i.e SPD 10 = -15% Evasion
      **Nuetral** Cards SPD [31-69] do not modify evasion
      
      🧮**Strike Calculation** Strike calcalation adds variance and balance to Engagements.
      Your ability also deals damage based on the type of **Strike**
      Strike is determined by your Move Accuracy vs Opponent Evasion
      :palm_down_hand: **Miss** - You completely miss... No Damage
      :anger: **Chip** - You barely strike. 30% Damage Reduction
      :bangbang: **Connects** - Your ability strikes. No Reduction
      🗯️ **Hits** - Land a significant Strike. 20% Increase
      💥 **Critical Hit** - You land a lethal blow. 250% Increase
      
      📿**Talismans**
      Talismans nullify the affinities of the chosen **Element**. 
      **/attune** and equip /**talismans** from stored **Essence**
   
      """), color=0x7289da)
      
      embedVar17.set_thumbnail(url=avatar)

      embedVar4 = Embed(title=f"Titles, Arms, and Summons ", description=textwrap.dedent(f"""\
      **Titles** & **Arms** 
      Modify you or the Opponents **Stats** by applying **Enhancers** during battle.
      
      🎗️ **Title Exlusivity**
      **Titles** apply enhancers at the **start** of your turn or during **Focus State**
      ⚠️ Titles are only effective on cards from the same Universe or Unbound!
      Titles can only be earned via playing through the various game modes
      
      🦾 **Arm Durability**
      Arms are effective across the Multiverse, however they do break! Turning into **Gems**
      ⚠️ Arms from a different universe will break at a faster rate!
      Stock up on **Asrms** and repair **Durability** in the **/blacksmith**
      🪔 Elemental Arms also provide **Essence**. Use **Essence** to craft **Talismans**

      👑 **Universe Buff** :Match Your Titles and Arms to your **Card Universe**.
      **Buff**: **Base Stats** + 300 **HLT** , 30 **ATK** & 30 **DEF**.

      ✨ **Destiny Universe Buff** Destiny Cards gain an additional **Buff**.
      **Buff**: **Universe Buff** + 200 **HLT**, 20 **ATK** and 20 **DEF**.

      🧬 **Summons**
      Can assist during battle with an **Elemntal Attack** or **Defensive Boost**.
      Earn **Summons** through Tales, Dungeon and Boss **Drops** or through trade with other Players!
      Battle with your **Summon** to gain **EXP** to increase Summon **Ability Power**. 

      Mix and Match Titles, Arms and Summons to gain the **Tactical Advantage**!
      """) ,color=0x7289da)
      
      embedVar4.set_thumbnail(url=avatar)

      embedVar5 = Embed(title=f"Battle Mechanics", description=textwrap.dedent(f"""\
      Players take turns dealing damage using one of their 5 **Abilities**.
      
      🌀 **Stamina** costs are standard across all Cards 
      _See Card Mechanics page for details_.
      
      ⚕️ **Recovery**
      When Players have used all of their **Stamina** they enter **Focus State**.

      The Match is over when a players **Health** reaches 0.
      """) ,color=0x7289da)
      
      embedVar5.set_thumbnail(url=avatar)

      embedVar6 = Embed(title=f"Focus & Resolve", description=textwrap.dedent(f"""\
      ⚕️ **Focus**
      Players can take advantage of **Focus State** to **Recover**.
      **Focus State** sacrifices a turn to Level Up Stats, increase **Stamina** to 90, and **Recover** some **Health**.
      
      ⚡**Resolve**
      Once in **Focus State** players can **Resolve**!
      **Resolved Characters** transform to greatly increase attack and health while sacrificing defense.
      **Resolved Characters** can call on Summons to aid them in battle.
      ⚡ Resolve _uses 1 turn_. You no longer stack Focus Stats

      **Summon Assistance!**
      Summons Enhancers either use an Elemental Attack or Grant the player a Defensive Arm. Summon moves do not end the player turn!
      🧬 Summon _uses 15 stamina_.

      """) ,color=0x7289da)
      
      embedVar6.set_thumbnail(url=avatar)
      
      embedVar16 = Embed(title=f"Difficulty & Progression", description=textwrap.dedent(f"""\
      ⚙️**Difficulty**
      Anime VS+ allows you to tailor your experience to your desired level.
      
      **3 Difficulties**
      **Easy** *Play the game freely and casually*
      - Lower Enemy Scaling
      - No Destinies, Dungeons, Bosses, Drops, Raids or Abyss
      
      **Normal** *Play Anime VS+ the Intended Way*
      - Traverse the **/solo** to earn levels and unlock modes
      - Standard drop rates for items in game modes
      - Rebirth for increase in base stats and drop rates
      
      **Hard** *Not for the faint of Heart*
      - Normal Mode but with increasing scaling, drops and rewards
      - Clout

      """),color=0x7289da)
      
      embedVar16.set_thumbnail(url=avatar)

      embedVar7 = Embed(title=f"Game Modes", description=textwrap.dedent(f"""\
      /play
      **Tales:** Single player adventures where you traverse through your favorite universes as characters from various worlds!
      **Dungeon:** Hard version of tales with better loot and better drop rates! (Unlocks after completing **Anime VS+ Tale**)
      **Scenario:** Play through various scenarios from the source material to earn cards of all kind
      **Explore:** Play in random encounters to earn coins and cards
      
      """),color=0x7289da)
      
      embedVar7.set_thumbnail(url=avatar)


      embedVar9 = Embed(title=f"Presets",description=textwrap.dedent(f"""\
      Save your favorite builds in your **Preset**
      **/menu** tselect **View Preset** option, select a preset with **1-3**
      *Select **Save Preset** to save a new Build!
      
      **Preset Builds**
      You can bring your preset builds into Duo Battles!
      """) ,color=0x7289da)
      
      embedVar9.set_thumbnail(url=avatar)

      embedVar10 = Embed(title=f"Economy",description=textwrap.dedent(f"""\
      **Marketplace**
      Use **/marketplace** to access the **Market!**!
      Use the marketplace to buy and sell Cards, Arms and Summons!
                                                                      
      **Trading**
      **/trade** will allow you to trade Cards, Arms and Summons with other players.
      Add items to the open trade using the buttons on the item menu *ex. /cards*
      **/tradecoins** allows you to add or remove coins from the trade

      **Dismantle**
      Dismantle Cards, Titles and Arms into :gem:**Gems**. and 🪔**Essense**
      
      
      **Blacksmith**
      **/menu** to purchase Card Levels, Arm Durability and **Storage**!

      
      👛 **Gabe's Purse** - will allow you to keep all items after a **Rebirth**
      
      **Currency**
      🪙 - Coins can be used to purchase Cards, Titles and Arms. You can use them to trade and sell items to other players!
      💎 - When Arms break they turn into **Gems**, You can also dismantle items from your inventory into **Gems**! 
      **Gems** are universe specific items that can be crafted into Skins, Trinkets or **Destinies**
      
      """) ,color=0x7289da)
      
      embedVar10.set_thumbnail(url=avatar)
      
      embedVar15 = Embed(title=f"Guilds", description=textwrap.dedent(f"""\
      **Guilds Explained**
      - Use **/guild** to lookup any Anime VS+ Guild!
      - **Guild Members** earn extra 🪙 towards the **Guild Bank** 

      **Creating A Guild**
      - Use **/createguild** and create a **Guild Name**
      - **/recruit** your friends to join your newly named **Guild** !
      - Players can use **/apply** to join as well!
      
      **Guild Bonusus**
      - Guildmates gain an extra **50 Attack** and **Defense** playing Co-Op Together !
      - Guilds earn additional 🪙 for every **Tales**, **Dungeon** and **Boss** Victory
      
      **Guild Economy**
      - Players across **Anime VS+** can **/donate** 🪙 to their favorite Guilds!
      - Guild Owners can ****/pay**** their members a wage.
      
      **Guild Buffs**
      - Quest Buff: Start Quest from the required fight in the Tale, not for dungeons
      - Level Buff: Each fight will grant you a level up
      - Stat Buff: Add 100 ATK & DEF, 100 AP, and 500 HLT
      - Rift Buff: Rifts will always be available

      Guild Position Explanations
      - Owner: All operations
      - Officer: Can Add members, Delete members, Pay members, Buy, Swap, and Toggle Buffs
      - Captain: Can Toggly Buffs, Pay members
      - Member: No operations
      """),color=0x7289da)
      
      embedVar15.set_thumbnail(url=avatar)

      # embedVar12 = Embed(title=f"Families",description=textwrap.dedent(f"""\
      # **Families Explained**
      # - When you create an AnimeVs+ account you start a family
      # - Use **/family** to lookup any Anime VS+ Family!
      
      # **Marriage**
      # - Two players with a strong bond can come together and form a **Family**
      # - Use **/marry** to start a marriage proposal to your chosen **Partner**
      # - If they accept, they will join your dfamily
      # - **2 Kids** can be adopted into the family to create a 4 player Maximum.
      
      # **Family Bonuses**
      # - Family Members gain an extra **100 Health** when playing Co-Op Together !
      # - Family Members earn extra 🪙 towards the **Family Bank**.
      # - Families can **/invest** their income together.
      # - Heads of Household and Partners can pay **/allowance** to Family members. 
      
      # **Housing**
      # - The **Family Bank** can be used to buy **Houses**
      # - **Houses** increase your 🪙 earned via **Mutlipliers**
      # - **/invest** your income to buy bigger **Houses** and earn more 🪙 across the game.
      # - Use the *Real Estate Menu** to buy and sell Estates
      
      # **Family Summon**
      # - Family members can equip the Family Summon to aid them in battle!
      
      # Family Position Explanations
      # - Head of Household: All operations.
      # - Partner: Can equip/update family summon, change equipped house.
      # - Kids: Can equip family summon.
      # """) ,color=0x7289da)
      
      # embedVar12.set_thumbnail(url=avatar)

      # embedVar13 = Embed(title=f"Associations",description=textwrap.dedent(f"""\
      # **Association Explained**
      # - Associations in Anime VS+ are formed by an Oath between two Guild Owners
      # - The Oathgiver becomes the **Founder** and the Oathreciever becomes the ****Sworn and Shield****.
      # - The **Shield** defends the Association from raiding players.
      # - Both teams become enlisted as **Swords** of the new **Association**
      # - Their respective members become **Blades**
      # - The Founder & Sworn may /ally with other Teams increasing the size and power of the Association.
      # - These are the **Owners** and can **/sponsor** other teams allied with the Association.
      # - **Associations** earn money by winning **PvP** matches, Income from **Universe Crest** and defending against **Raids**
      
      # **Universe Crest** 
      # - When a member of a Association defeats a **Dungeon** or **Boss** they earn the **Universe Crest** from that Universe.
      # - This Crest will earn the Association **Passive Income** whenever someone goes into that universe in all servers!
      
      # **Association Bonuses**
      # - Associations earn extra income towards the **Association Bank**
      # - Associations increase the earned income in **PvP**
      # - Associations can Raid
      # - Associations can earn passive income owning **Universe Crest**
      # - Associations can purchase **Halls**
      
      # **Halls**
      # - The **Association Bank** can be used to purchase **Halls**
      # - Increase the Income earned to Associations via **Multipliers**
      # - Increase the income earned to **Blades** via **Splits**
      # - Increase the defense of the **Shield**
      # - Increase the **Bounty** cost to raid the **Association**
      # """) ,color=0x7289da)
      
      # embedVar13.set_thumbnail(url=avatar)
      
      # embedVar14 = Embed(title=f"Raids",description=textwrap.dedent(f"""\
      # **Raids Explained**
      # - Players aligned with a Association can use /raid to claim bounties from other guilds
      # - Victory claims the bounty and resets the Associations victory multiplier !
      # - Income from Raids is limited to the bounty offered from the Association.
      # - To take money from a **Association Bank** players must compete in PvP
      
      # Raiding an Association is no easy feat and must be done **Without Summons**
      
      # **Raid Benefits**
      # - Earn Large Bounties from guilds.
      # - Earn Wins for your Anime VS+ **Guild**
      
      # **Shield  Defense Explained**
      # - The **Shield** has a big repsonsible to defend the **Association** from raids, earning income from **Challengers**.
      # - The **Shield** exist within the Association hall as the **Current Equipped Build** of the **Shield Player**.
      # - As the **Shield**, whenever your Avatar succesfully defends a raid you earn 🪙
      # - With each victory you will build a streak earning both respect and more 🪙 via **Multipliers**.
      
      # **Shield Benefits**
      # - Earn income by defending your Association from raiders
      # - Guild has a 30% reduction in buff cost
      # - Earn respect by increasing the Association victory streak 
      
      # """) ,color=0x7289da)
      
      # embedVar14.set_thumbnail(url=avatar)

      embeds = [embedVar1, embedVar2, embedVar3, embedVar11,embedVar17, embedVar4, embedVar5, embedVar6, embedVar16, embedVar7, embedVar9, embedVar10,embedVar15, embedVar0]
      paginator = Paginator.create_from_embeds(bot, *embeds)
      paginator.show_select_menu = True
      await paginator.send(ctx)
   except Exception as ex:
      loggy.error(f"Error in animevs command: {ex}")
      await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
      return

@slash_command(description="rewards for voting", scopes=guild_ids)
async def voted(ctx):
   try:
      query = {'DID': str(ctx.author.id)}
      user = db.queryUser(query)
      vault = db.queryVault(query)
      gem_list = vault['GEMS']
      prestige = int(user['PRESTIGE'])
      aicon = crown_utilities.prestige_icon(prestige)
      user_completed_tales = user['CROWN_TALES']
      rebirth = int(user['REBIRTH'])

      voting_amount = 5000000
      voting_gems = 500000
      gem_bonus = int(voting_gems * (rebirth + 1) + (500000 * prestige))
      voting_bonus = int(voting_amount * (rebirth + 1) + (2000000 * prestige))
      if user['VOTED']:
         await ctx.send("You've already received your voting rewards!")
         return
      else:
         auth_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk1NTcwNDkwMzE5ODcxMTgwOCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjQ5MDAyNDY0fQ.zNf3ECu2PBWVlfYlYH9YMy7PRb2P-sQFBGRkBp-DwUo'
         head = {'Authorization': 'Bearer ' + auth_token}
         
         response = requests.get(f"https://top.gg/api/bots/955704903198711808/check?userId={ctx.author.id}", headers=head)
         response_dict = json.loads(response.text)
         retry_message =f"🆚 Rematches : **{user['RETRIES']}**"
         if response_dict['voted'] == 1:
            if gem_list:
               for universe in gem_list:
                  update_query = {
                     '$inc': {'GEMS.$[type].' + "GEMS": gem_bonus}
                  }
                  filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
                  res = db.updateUser(query, update_query, filter_query)

            await crown_utilities.bless(int(voting_bonus), ctx.author.id)
            respond = db.updateUserNoFilter(query, {'$set': {'VOTED': True}})
            retry_message =f"🆚 Rematches : **{user['RETRIES']}**"  
            db.updateUserNoFilter(query, {'$inc': {'RETRIES': 3}})
            retry_message =f"🆚 Rematches : {user['RETRIES']} **+ 3**!"


            embedVar = Embed(title=f"✅ Daily Voter Rewards!", description=textwrap.dedent(f"""\
            Thank you for voting, {ctx.author.mention}!
            
            **Daily Voter Earnings** 
            🪙 **{'{:,}'.format(voting_bonus)}**
            💎 **{'{:,}'.format(gem_bonus)}** *all craftable universes*
            {retry_message}
            
            [Support our Patreon for Rewards!](https://www.patreon.com/partychatgaming?fan_landing=true)
            [Add Anime VS+ to your server!](https://discord.com/api/oauth2/authorize?client_id=955704903198711808&permissions=139586955344&scope=applications.commands%20bot)
            """), color=0xf1c40f)
            
            await ctx.send(embed=embedVar)

         else:
            retry_message =f"🆚 Rematches : **+3**"
            embedVar = Embed(title=f"❌ Daily Voter Rewards!", description=textwrap.dedent(f"""\
            You have not voted for Anime VS+ today, {ctx.author.mention}!
            To earn your voter rewards, [Vote for Anime VS+!](https://top.gg/bot/955704903198711808/vote)
            **What are the Daily Voter Rewards?** 
            🪙 **{'{:,}'.format(voting_bonus)}**
            💎 **{'{:,}'.format(gem_bonus)}**
            {retry_message}
            
            [Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
            """), color=0xf1c40f)
            
            await ctx.send(embed=embedVar)

   except Exception as e:
      loggy.error(e)
      await ctx.send("Hmm something ain't right. Check with support.", ephemeral=True)
      return


# Update Later
@slash_command(description="Register for Anime VS+", scopes=guild_ids)
async def register(ctx):
   await ctx.defer()
   server_created = db.queryServer({"GNAME": str(ctx.author.guild)})
   if db.queryUser({"DID": str(ctx.author.id)}):
      await ctx.send(f"{ctx.author.mention} You already have a Anime VS+ Account!")
      return 

   else:
      disname = str(ctx.author)
      did = str(ctx.author.id)
      name = disname.split("#",1)[0]
      summon_info = {
         "NAME": "Chick",
         "LVL": 1,
         "EXP": 0,
         "Peck": 100,
         "TYPE": "PHYSICAL",
         "BOND": 0,
         "BONDEXP": 0,
         "PATH": "https://res.cloudinary.com/dkcmq8o15/image/upload/v1638814575/Pets/CHICK.png"
      }
      user = {
         'DISNAME': disname, 
         'NAME': name, 
         'DID': did, 
         'AVATAR': str(ctx.author.avatar_url), 
         'SERVER': str(ctx.author.guild), 
         'FAMILY': did,
         'FAMILY_DID': did,
         'BALANCE': Int64(1500000),
      }
      r_response = db.createUsers(data.newUser(user))

      if not server_created:
         create_server_query = {'GNAME': str(ctx.author.guild.name)}
         created_server = db.createServer(data.newServer(create_server_query))
         server_query = {'GNAME': str(ctx.author.guild)}
         update_server_query = {
            '$inc': {'SERVER_BALANCE': 10000},
            '$addToSet': {'SERVER_PLAYERS': str(ctx.author.id)}
         }
         updated_server = db.updateServer(server_query, update_server_query)


   if r_response:
      # await ctx.send(f"🆕 Registration Started!\n{ctx.author.mention}, prepare to select a starting universe.")
      # await asyncio.sleep(2)
      # await ctx.send(f"{ctx.author.mention}, your starting universe will give you 🎴 cards and 🎗️ 🦾 accessories from that universe to get you started on your journey!")
      # await asyncio.sleep(2)

      # Write code that gives freely all titles in a universe that has 
      # unlock method as Tales and unlock value as 0
      try:
         _uuid = str(uuid.uuid4())
         # Create Embed briefly introducing the game
         # Create buttons to proceed to the next step or to cancel registration
         # if the user cancels registration, delete the user from the database and end this process
         # if the user proceeds, show the user the list of starting universes
         accept_buttons = [
               Button(
                  style=ButtonStyle.GREEN,
                  label="Continue",
                  custom_id=f"{_uuid}|yes"
               ),
               Button(
                  style=ButtonStyle.RED,
                  label="End Registration Here",
                  custom_id=f"{_uuid}|no"
               )
         ]

         embed = Embed(title="Anime VS+ Registration", description="Welcome to Anime VS+! Embark on an epic journey through the multiverse of anime and video games. Collect your favorite characters, unlock unique gear and companions, and dominate countless universes. Dive into solo adventures, customize your experience, and earn awesome rewards. Are you ready to register and choose your starter universe? Let's see how powerful you can become!", color=0x7289da)

         embed.add_field(name="__What happens if you continue?__", value="Click Continue to start your registration. You'll choose your starting universe, granting you access to 3 unique Cards, a Title, and an Arm to kickstart your adventure.", inline=False)

         embed.add_field(name="__What happens if you cancel?__", value="You'll be removed from the registration process. You can always come back and register later.", inline=False)

         embed.set_footer(text="Anime VS+ | Registration")

         action_row = ActionRow(*accept_buttons)

         message = await ctx.send(embed=embed, components=[action_row])

         def check(component: Button):
            return str(component.ctx.author.id) == str(ctx.author.id)

         try:
            button_ctx = await bot.wait_for_component(components=[action_row], check=check, timeout=120)
            # await button_ctx.ctx.defer()

            if button_ctx.ctx.custom_id == f"{_uuid}|no":
               embed = Embed(title="Anime VS+ Registration", description="Your registration has been cancelled. You can always come back and register later.", color=0x7289da)
               await message.edit(components=[], embed=embed)
               return

            if button_ctx.ctx.custom_id == f"{_uuid}|yes":
               await message.edit(components=[], embed=embed)
               universe_data = db.queryAllUniverse()
               universe_embed_list = []
               for uni in universe_data:
                  available = ""
                  if uni['HAS_CROWN_TALES'] == True:
                     traits = ut.traits
                     mytrait = {}
                     traitmessage = ''
                     o_show = uni['TITLE']
                     universe = o_show
                     for trait in traits:
                        if trait['NAME'] == o_show:
                              mytrait = trait
                        if o_show == 'Pokemon':
                              if trait['NAME'] == 'Pokemon':
                                 mytrait = trait
                     if mytrait:
                        traitmessage =f"**{mytrait['EFFECT']}|** {mytrait['TRAIT']}"
                     available =f"{crown_utilities.crest_dict[uni['TITLE']]}"
                     
                     embedVar = Embed(title=f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
                     **{available} Select A Starting Universe, {ctx.author.mention}!**

                     Selecting a Starter Universe will give you *3* additional 🎴 Cards and 🦾 Arms to begin! 

                     Don't overthink it! You can always earn more cards, arms, titles and more later!
                     
                     ♾️ - Unique Universe Trait
                     {traitmessage}
                     """))
                     embedVar.set_image(url=uni['PATH'])
                     embedVar.set_footer(text="You can earn or purchase items after Abyss floor 0")
                     universe_embed_list.append(embedVar)
                     
               paginator = CustomPaginator.create_from_embeds(bot, *universe_embed_list, custom_buttons=["Register"], paginator_type="Register")
               paginator.show_select_menu = True
               await paginator.send(ctx)
         
         except asyncio.TimeoutError:
            await message.edit(components=[], embed=embed, content="You took too long to respond.")
            await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
            db.deleteUser({"DID": str(ctx.author.id)})
            return

      except Exception as ex:
         custom_logging.debug(ex)
         await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
         
   else:
      db.deleteUser(str(ctx.author.id))
      await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)

# Update Later
@slash_command(name="rebirth", description="Rebirth for permanent buffs", scopes=guild_ids)
async def rebirth(ctx):
   query = {'DID': str(ctx.author.id)}
   user_is_validated = db.queryUser(query)
   try:
      if user_is_validated:
         rLevel = user_is_validated['REBIRTH']
         pLevel = user_is_validated['PRESTIGE']
         
         
         rebirthCost = round(100000000 * (1 + (1.5 * (rLevel))))
         pReq = 100 - (pLevel * 10)
         picon = crown_utilities.prestige_icon(pLevel)
         
         pursemessage = " "
         gabes_purse = user_is_validated['TOURNAMENT_WINS']
         if gabes_purse == 1:
            pursemessage = ":purse: | Gabe's Purse Activated! All Items Will Be Retained! *You will not be able to select a new starting universe!*"
         
         
         
         if (rLevel > 4 and rLevel <10) and pLevel < (rLevel - 4):
            embedVar1 = Embed(title=f"❤️‍🔥{user_is_validated['NAME']}'s Rebirth",color=0x7289da)
            embedVar1.set_thumbnail(url=user_is_validated['AVATAR'])
            embedVar1.add_field(name=f":angel: Rebirth Level: {user_is_validated['REBIRTH']}\n{picon}Prestige Level: {pLevel}\n\nRebirth Cost: 🪙{'{:,}'.format(rebirthCost)}", value=textwrap.dedent(f"""\
            **Rebirth Effects**
            New Starting Deck
            Starting Summon Bond
            Increase Base ATK + 100 (Max 1000)
            Increase Base DEF + 100 (Max 1000)
            Increase Move AP by +2% (Max 20%)
            Increased 🪙 drops + %10
            Increased Item Drop Rates + 50%
            Keep All Card Levels
            
            {pursemessage}
            
            **You need to increase your Prestige Level to Rebirth again. 
            Complete floor {pReq}**
            """))
            await ctx.send(embed=embedVar1)
            return
         elif rLevel < 10:
            pursemessage = "You will lose all of your equipped and vaulted items."
            

            util_buttons = [
                  Button(
                     style=ButtonStyle.BLUE,
                     label="Yes",
                     custom_id = "Y"
                  ),
                  Button(
                     style=ButtonStyle.RED,
                     label="No",
                     custom_id = "N"
                  )
               ]
            util_action_row = ActionRow(*util_buttons)
            components = [util_action_row]

            embedVar1 = Embed(title=f"❤️‍🔥{user_is_validated['NAME']}'s Rebirth",color=0x7289da)
            embedVar1.set_thumbnail(url=user_is_validated['AVATAR'])
            embedVar1.add_field(name=f"Rebirth Level: {user_is_validated['REBIRTH']}\nPrestige Level: {pLevel}\n\nRebirth Cost: 🪙{'{:,}'.format(rebirthCost)}", value=textwrap.dedent(f"""\
            **Rebirth Effects**
            New Starting Deck
            Starting Summon Bond
            Increase Base ATK + 100 (Max 1000)
            Increase Base DEF + 100 (Max 1000)
            Increase Move AP by +2% (Max 20%)
            Increased 🪙 drops + %10
            Increased Item Drop Rates + 50%
            Keep All Card Levels
            
            {pursemessage}
            
            *Rebirth is permanent and cannot be undone*
            """))
            accept = await ctx.send(embed=embedVar1, components=[util_action_row])

            def check(button_ctx):
                  return button_ctx.author == ctx.author

            try:
               button_ctx  = await self.bot.wait_for_component(bot, components=[util_action_row], timeout=120,check=check)
               if button_ctx.custom_id == "Y":
                  try:
                     vault = db.queryVault({'DID': user_is_validated['DID']})
                     if vault:
                        if vault['BALANCE'] >= rebirthCost:
                           if rLevel == 0:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"OWNER" : user_is_validated['DISNAME']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Twice' not in owned_cards:
                                 card_level_list.append({'CARD': 'Twice', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Charmander' not in owned_cards:
                                 card_level_list.append({'CARD': 'Charmander', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Braum' not in owned_cards:
                                 card_level_list.append({'CARD': 'Braum', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER': user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Twice','Charmander','Braum'], 'TITLES': ['Reborn'], 'ARMS': [{'ARM': 'Reborn Stock', 'DUR': 999999}],'DECK': [{'CARD': 'Charmander', 'TITLE': 'Reborn', 'ARM': 'Reborn Stock', 'PET': 'Chick'}, {'CARD': 'Twice', 'TITLE': 'Reborn', 'ARM': 'Reborn Stock', 'PET': 'Chick'}, {'CARD': 'Braum', 'TITLE': 'Reborn', 'ARM': 'Reborn Stock', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 1, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Charmander', 'Twice', 'Braum']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Charmander', 'TITLE': 'Reborn', 'ARM':'Reborn Stock'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")                              
                           elif rLevel == 1:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Kirishima' not in owned_cards:
                                 card_level_list.append({'CARD': 'Kirishima', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Squirtle' not in owned_cards:
                                 card_level_list.append({'CARD': 'Squirtle', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Malphite' not in owned_cards:
                                 card_level_list.append({'CARD': 'Malphite', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER': user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Kirishima','Squirtle','Malphite'], 'TITLES': ['Reborn Soldier'], 'ARMS': [{'ARM': 'Deadgun', 'DUR': 999999}], 'DECK': [{'CARD': 'Kirishima', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}, {'CARD': 'Squirtle', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}, {'CARD': 'Malphite', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 3, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Squirtle', 'Malphite', 'Kirishima']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Malphite', 'TITLE': 'Reborn Soldier', 'ARM':'Deadgun'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 2:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Mineta' not in owned_cards:
                                 card_level_list.append({'CARD': 'Mineta', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Bulbasaur' not in owned_cards:
                                 card_level_list.append({'CARD': 'Bulbasaur', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Shen' not in owned_cards:
                                 card_level_list.append({'CARD': 'Shen', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Mineta','Bulbasaur','Shen'], 'TITLES': ['Reborn Legion'], 'ARMS': [{'ARM': 'Glaive', 'DUR': 999999}], 'DECK': [{'CARD': 'Mineta', 'TITLE': 'Reborn Legion', 'ARM': 'Glaive', 'PET': 'Chick'}, {'CARD': 'Bulbasaur', 'TITLE': 'Reborn Legion', 'ARM': 'Glaive', 'PET': 'Chick'}, {'CARD': 'Shen', 'TITLE': 'Reborn Legion', 'ARM': 'Glaive', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 5, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Bulbasaur', 'Mineta', 'Shen']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Mineta', 'TITLE': 'Reborn Legion', 'ARM':'Glaive'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 3:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Hawks' not in owned_cards:
                                 card_level_list.append({'CARD': 'Hawks', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Clefairy' not in owned_cards:
                                 card_level_list.append({'CARD': 'Clefairy', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Yasuo' not in owned_cards:
                                 card_level_list.append({'CARD': 'Yasuo', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Hawks','Clefairy','Yasuo'], 'TITLES': ['Reborn King'], 'ARMS': [{'ARM': 'Kings Glaive', 'DUR': 999999}], 'DECK': [{'CARD': 'Hawks', 'TITLE': 'Reborn King', 'ARM': 'Kings Glaive', 'PET': 'Chick'}, {'CARD': 'Clefairy', 'TITLE': 'Reborn King', 'ARM': 'Kings Glaive', 'PET': 'Chick'}, {'CARD': 'Yasuo', 'TITLE': 'Reborn King', 'ARM': 'Kings Glaive', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 1, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Hawks', 'Clefairy', 'Yasuo']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Clefairy', 'TITLE': 'Reborn King', 'ARM':'Kings Glaive'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 4:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Stain' not in owned_cards:
                                 card_level_list.append({'CARD': 'Stain', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Onix' not in owned_cards:
                                 card_level_list.append({'CARD': 'Onix', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Xayah And Rakan' not in owned_cards:
                                 card_level_list.append({'CARD': 'Xayah And Rakan', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Stain','Onix','Xayah And Rakan'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Stain', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Onix', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Xayah And Rakan', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 5, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Stain', 'Onix', 'Xayah And Rakan']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Xayah And Rakan', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 5:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Meliodas' not in owned_cards:
                                 card_level_list.append({'CARD': 'Meliodas', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Tusk Shadow' not in owned_cards:
                                 card_level_list.append({'CARD': 'Tusk Shadow', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Kratos And Atreus' not in owned_cards:
                                 card_level_list.append({'CARD': 'Kratos And Atreus', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Meliodas','Tusk Shadow','Kratos And Atreus'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Meliodas', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Tusk Shadow', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Kratos And Atreus', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Meliodas', 'Tusk Shadow', 'Kratos And Atreus']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Kratos And Atreus', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 6:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Asta' not in owned_cards:
                                 card_level_list.append({'CARD': 'Asta', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Maka' not in owned_cards:
                                 card_level_list.append({'CARD': 'Maka', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Asuna' not in owned_cards:
                                 card_level_list.append({'CARD': 'Asuna', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Asta','Maka','Asuna'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Asta', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Maka', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Asuna', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Asta', 'Maka', 'Asuna']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Asuna', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 7:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Tepellin' not in owned_cards:
                                 card_level_list.append({'CARD': 'Tepellin', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Kyogre' not in owned_cards:
                                 card_level_list.append({'CARD': 'Kyogre', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Omnimon' not in owned_cards:
                                 card_level_list.append({'CARD': 'Omnimon', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Tepellin','Kyogre','Omnimon'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Tepellin', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Kyogre', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Omnimon', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Tepellin', 'Kyogre', 'Omnimon']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Omnimon', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 8:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Gon' not in owned_cards:
                                 card_level_list.append({'CARD': 'Gon', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Obito' not in owned_cards:
                                 card_level_list.append({'CARD': 'Obito', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Kurama' not in owned_cards:
                                 card_level_list.append({'CARD': 'Kurama', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Gon','Kurama','Obito'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Gon', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Obito', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Kurama', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Gon', 'Obito', 'Kurama']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Kurama', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           elif rLevel == 9:
                              if gabes_purse == 1:
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 db.updateUserNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                                 db.updateUserNoFilter(query, {'$set': {'TOURNAMENT_WINS': 0 }})
                                 return
                              card_level_list = vault['CARD_LEVELS']
                              owned_cards = []
                              for card in card_level_list:
                                 owned_cards.append(card['CARD'])
                              if 'Meister Maka' not in owned_cards:
                                 card_level_list.append({'CARD': 'Meister Maka', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Byakuran' not in owned_cards:
                                 card_level_list.append({'CARD': 'Byakuran', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              if 'Cthulhu' not in owned_cards:
                                 card_level_list.append({'CARD': 'Cthulhu', 'LVL': 0, 'TIER': 1, 'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0})

                              delete = db.deleteVault({'DID': user_is_validated['DID']})
                              vault = db.createVault(data.newVault({'OWNER' : user_is_validated['DISNAME'],'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Meister Maka','Byakuran','Cthulhu'], 'TITLES': ['Reborn Legend'], 'ARMS': [{'ARM': 'Legendary Weapon', 'DUR': 999999}], 'DECK': [{'CARD': 'Meister Maka', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Byakuran', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}, {'CARD': 'Cthulhu', 'TITLE': 'Reborn Legend', 'ARM': 'Legendary Weapon', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 6, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 3, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                              if vault:
                                 cardList = ['Meister Maka', 'Byakuran', 'Cthulhu']
                                 for card in cardList:
                                    for destiny in d.destiny:
                                       if card in destiny["USE_CARDS"]:
                                          db.updateUserNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                          message =f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                          await button_ctx.send(message)
                                 nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Cthulhu', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                                 db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'U_PRESET': False}})
                                 nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                                 await button_ctx.send(f"❤️‍🔥 | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                           #Starting Selection
                           try:
                              if gabes_purse == 1:
                                 await button_ctx.send(f":purse: | Gabe's Purse Activated! All Items Will Be Retained!\nNo Starting Universe Selection...")
                                 return
                              universe_data = db.queryAllUniverse()
                              universe_embed_list = []
                              for uni in universe_data:
                                 available = ""
                                 if uni['HAS_CROWN_TALES'] == True:
                                    traits = ut.traits
                                    mytrait = {}
                                    traitmessage = ''
                                    o_show = uni['TITLE']
                                    universe = o_show
                                    for trait in traits:
                                       if trait['NAME'] == o_show:
                                             mytrait = trait
                                       if o_show == 'Kanto Region' or o_show == 'Johto Region' or o_show == 'Kalos Region' or o_show == 'Unova Region' or o_show == 'Sinnoh Region' or o_show == 'Hoenn Region' or o_show == 'Galar Region' or o_show == 'Alola Region':
                                             if trait['NAME'] == 'Pokemon':
                                                mytrait = trait
                                    if mytrait:
                                       traitmessage =f"**{mytrait['EFFECT']}|** {mytrait['TRAIT']}"
                                    available =f"{crown_utilities.crest_dict[uni['TITLE']]}"
                                    
                                    tales_list = ", ".join(uni['CROWN_TALES'])

                                    embedVar = Embed(title=f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
                                    **Select A Starting Universe, {ctx.author.mention}!**
                                    Selecting a Starter Universe will give you *3* 🎴 Cards, 🎗️ Titles, and 🦾 Arms to begin!
                                    
                                    ♾️ - Unique Universe Trait
                                    {traitmessage}
                                    """))
                                    embedVar.set_image(url=uni['PATH'])
                                    universe_embed_list.append(embedVar)
                                    
                              buttons = [
                                    Button(style=3, label="Select This Starter Universe", custom_id="Select")
                                 ]
                              custom_action_row = ActionRow(*buttons)
                              # custom_button = Button(style=3, label="Equip")

                              async def custom_function(self, button_ctx):
                                 try:
                                    if button_ctx.author == ctx.author:
                                       universe = str(button_ctx.origin_message.embeds[0].title)
                                       vault_query = {'DID' : str(ctx.author.id)}
                                       vault = db.altQueryVault(vault_query)
                                       current_titles = vault['TITLES']
                                       current_cards = vault['CARDS']
                                       current_arms = []
                                       for arm in vault['ARMS']:
                                          current_arms.append(arm['ARM'])

                                       owned_card_levels_list = []
                                       for c in vault['CARD_LEVELS']:
                                          owned_card_levels_list.append(c['CARD'])
                                       owned_destinies = []
                                       for destiny in vault['DESTINY']:
                                          owned_destinies.append(destiny['NAME'])
                                       
                                       if button_ctx.custom_id == "Select":
                                          acceptable = [1,2,3,4]
                                          list_of_titles =[x for x in db.queryAllTitlesBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE'] and x['TITLE'] not in current_titles]
                                          count = 0
                                          selected_titles = [1000]
                                          while count < 3:
                                             selectable_titles = list(range(0, len(list(list_of_titles))))
                                             for selected in selected_titles:
                                                if selected in selectable_titles:
                                                   selectable_titles.remove(selected)
                                             selection = random.choice(selectable_titles)
                                             selected_titles.append(selection)
                                             title = list_of_titles[selection]
                                             response = db.updateUserNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})
                                             await button_ctx.send(f"🎗️ **{title['TITLE']}**.")
                                             count = count + 1
                                          
                                          
                                          list_of_arms = [x for x in db.queryAllArmsBasedOnUniverses({'UNIVERSE': str(universe)}) if not x['EXCLUSIVE'] and x['AVAILABLE'] and x['ARM'] not in current_arms]
                                          count = 0
                                          selected_arms = [1000]
                                          while count < 3:
                                             current_arms = vault['ARMS']
                                             selectable_arms = list(range(0, len(list(list_of_arms))))
                                             for selected in selected_arms:
                                                if selected in selectable_arms:
                                                   selectable_arms.remove(selected)
                                             selection = random.choice(selectable_arms)
                                             selected_arms.append(selection)
                                             arm = list_of_arms[selection]['ARM']
                                             db.updateUserNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 75}}})                           
                                             await button_ctx.send(f"🦾 **{arm}**.")
                                             count = count + 1
                                             
                                          list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and x['AVAILABLE'] and x['NAME'] not in current_cards]
                                          count = 0
                                          selected_cards = [1000]
                                          while count < 3:
                                             current_cards = vault['CARDS']
                                             selectable_cards = list(range(0, len(list(list_of_cards))))
                                             for selected in selected_cards:
                                                if selected in selectable_cards:
                                                   selectable_cards.remove(selected)
                                             selection = random.choice(selectable_cards)
                                             selectable_cards.append(selection)
                                             card = list_of_cards[selection]
                                             card_name = card['NAME']
                                             tier = 0

                                             cresponse = db.updateUserNoFilter(vault_query, {'$addToSet': {'CARDS': str(card_name)}})
                                             if cresponse:
                                                if card_name not in owned_card_levels_list:
                                                   update_query = {'$addToSet': {
                                                         'CARD_LEVELS': {'CARD': str(card_name), 'LVL': 0, 'TIER': int(tier),
                                                                        'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                                                   r = db.updateUserNoFilter(vault_query, update_query)

                                                await button_ctx.send(f"🎴 **{card_name}**!")

                                                # Add Destiny
                                                for destiny in d.destiny:
                                                   if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                                                         db.updateUserNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
                                                         await button_ctx.send(
                                                            f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.", ephemeral=True)
                                             count = count + 1
                                          await button_ctx.send(f"Nice choice {ctx.author.mention}!\n\nCreate your first **Build**!\n**/cards** Select your 🎴  Card\n**/titles** Select your 🎗️ Title\n**/arms** Select your 🦾  Arm\n\nOnce you're done, run **/tutorial** to begin the **Tutorial Battle**! ⚔️")
                                          self.stop = True
                                 except Exception as ex:
                                    # trace = []
                                    # tb = ex.__traceback__
                                    # while tb is not None:
                                    #    trace.append({
                                    #       "filename": tb.tb_frame.f_code.co_filename,
                                    #       "name": tb.tb_frame.f_code.co_name,
                                    #       "lineno": tb.tb_lineno
                                    #    })
                                    #    tb = tb.tb_next
                                    # print(str({
                                    #    'type': type(ex).__name__,
                                    #    'message': str(ex),
                                    #    'trace': trace
                                    # }))
                                    loggy.error(f"Error in Rebirth command: {ex}")
                                    await ctx.send("Rebirth Issue Seek support.")
                              await Paginator(bot=bot, ctx=ctx, disableAfterTimeout=True, pages=universe_embed_list, customActionRow=[
                                 custom_action_row,
                                 custom_function,
                              ]).run()
                           except Exception as ex:
                              # trace = []
                              # tb = ex.__traceback__
                              # while tb is not None:
                              #    trace.append({
                              #       "filename": tb.tb_frame.f_code.co_filename,
                              #       "name": tb.tb_frame.f_code.co_name,
                              #       "lineno": tb.tb_lineno
                              #    })
                              #    tb = tb.tb_next
                              # print(str({
                              #    'type': type(ex).__name__,
                              #    'message': str(ex),
                              #    'trace': trace
                              # }))
                              loggy.error(f"Error in Rebirth command: {ex}")
                              await ctx.send("Rebirth Issue Seek support.")
                        else:
                           await button_ctx.send(f"Not enough 🪙!\nYou need {'{:,}'.format(rebirthCost)} to Rebirth:angel:", delete_after=5)
                     else:
                        await button_ctx.send("No Vault:angel:", delete_after=5)
                  except Exception as ex:
                     # trace = []
                     # tb = ex.__traceback__
                     # while tb is not None:
                     #    trace.append({
                     #       "filename": tb.tb_frame.f_code.co_filename,
                     #       "name": tb.tb_frame.f_code.co_name,
                     #       "lineno": tb.tb_lineno
                     #    })
                     #    tb = tb.tb_next
                     # print(str({
                     #    'type': type(ex).__name__,
                     #    'message': str(ex),
                     #    'trace': trace
                     # }))
                     loggy.error(f"Error in Rebirth command: {ex}")
                     await ctx.send("Rebirth Issue Seek support.")
               elif button_ctx.custom_id == "N":
                  await button_ctx.send(f"❤️‍🔥 | Ahhhh...another time then?", delete_after=5)
                  return
            except asyncio.TimeoutError:
               await ctx.send("Rebirth Menu Closed", hidden= True)
            except Exception as ex:
               # trace = []
               # tb = ex.__traceback__
               # while tb is not None:
               #    trace.append({
               #       "filename": tb.tb_frame.f_code.co_filename,
               #       "name": tb.tb_frame.f_code.co_name,
               #       "lineno": tb.tb_lineno
               #    })
               #    tb = tb.tb_next
               # print(str({
               #    'type': type(ex).__name__,
               #    'message': str(ex),
               #    'trace': trace
               # }))
               loggy.error(f"Error in Rebirth command: {ex}")
               await ctx.send("Rebirth Issue Seek support in the Anime 🆚+ support server https://discord.gg/cqP4M92")
         else:
            await ctx.send(f"You are at full Rebirth\n:angel:Level: {user_is_validated['REBIRTH']} ", delete_after=5)
   except Exception as ex:
      loggy.error(f"Error in Rebirth command: {ex}")
      await ctx.send("Rebirth Issue Seek support in the Anime 🆚+ support server")
      return
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #    trace.append({
      #       "filename": tb.tb_frame.f_code.co_filename,
      #       "name": tb.tb_frame.f_code.co_name,
      #       "lineno": tb.tb_lineno
      #    })
      #    tb = tb.tb_next
      # print(str({
      #    'type': type(ex).__name__,
      #    'message': str(ex),
      #    'trace': trace
      # }))


@slash_command(name="daily", description="Receive your daily reward and quests", scopes=guild_ids)
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
      
      boss_key_message = "🗝️ | Boss Arena Unlocked" if player.boss_fought == True else ""
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
      {boss_key_message}
      """), color=0xf1c40f)

      if milestone_message:
         # milestone message is a list of strings
         embedVar.add_field(name="🏆 **Milestone**", value="\n".join(milestone_message), inline=False
                            )
      embedVar.add_field(name="📜 **New Quests** */quest*", value="\n".join(quest_messages), inline=False)
      embedVar.add_field(name="Vote for Anime VS+!", value="🗳️ | **/vote** to earn daily rewards!", inline=False)
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


# async def DM(ctx, user: User, m,  message=None):
#     message = message or "This Message is sent via DM"
#     await user.send(m)


@slash_command(name="gift", description="Give money to friend", options=[
   SlashCommandOption(name="player", description="Player to gift", type=OptionType.USER, required=True),
], scopes=guild_ids)
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
], scopes=guild_ids)
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
            gem_amount = random.randint(25000, 50000)
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
    await paginator.send(ctx)

# Should you only be able to donate to your own guild?
@slash_command(name="donate", description="Donate money to Guild, Convert 10% as Gems", options=[
   SlashCommandOption(name="amount", description="Amount to donate", type=OptionType.INTEGER, required=True),
], scopes=guild_ids)
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


# @slash_command(name="invest", description="Invest money in your Family", scopes=guild_ids)
# @cooldown(Buckets.USER, 1, 10)
# async def invest(ctx, amount):
#    user = db.queryUser({'DID': str(ctx.author.id)})
#    family = db.queryFamily({'HEAD': user['DID']})
#    vault = db.queryVault({'DID': str(ctx.author.id)})
#    balance = vault['BALANCE']
#    if family:
#       if balance <= int(amount):
#          await ctx.send("You do not have that amount to invest.", ephemeral=True)
#       else:
#          await crown_utilities.blessfamily_Alt(int(amount), user['DID'])
#          await crown_utilities.curse(int(amount), ctx.author.id)
#          transaction_message =f"🪙 | {user['DISNAME']} invested 🪙{amount} "
#          update_family = db.updateFamily(family['HEAD'], {'$addToSet': {'TRANSACTIONS': transaction_message}})
#          await ctx.send(f"**🪙{amount}** invested into **{user['NAME']}'s Family**.")
#          return
#    else:
#       await ctx.send(f"Family does not exist")


@slash_command(name="pay", description="Pay a Guild Member", options=[
   SlashCommandOption(name="player", description="Player to pay", type=OptionType.USER, required=True),
   SlashCommandOption(name="amount", description="Amount to pay", type=OptionType.INTEGER, required=True),
], scopes=guild_ids)
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
scopes=guild_ids)
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


@slash_command(name="traits", description="List of Universe Traits", scopes=guild_ids)
@slash_option(
   name="universe",
   description="Universe to list traits for",
   opt_type=OptionType.STRING,
   required=False,
   autocomplete=True
)
async def traits(ctx: InteractionContext, universe: str = ""):
   try: 
      traits = ut.traits

      if not universe:
         embed_list = []
         for trait in traits:
            universe = db.queryUniverse({'TITLE': trait['NAME']})
            embedVar = Embed(
               title=f"{trait['NAME']} Trait",
               description=textwrap.dedent(f"""
               **{trait['EFFECT']}**:
               {trait['TRAIT']}
               """)
            )

            embed_list.append(embedVar)

         paginator = Paginator.create_from_embeds(bot, *embed_list)
         paginator.show_select_menu = True
         await paginator.send(ctx)
      else:
         universe = db.queryUniverse({'TITLE': universe})
         if not universe:
            await ctx.send("That universe does not exist.")
            return
         for trait in traits:
            if trait['NAME'] == universe['TITLE']:
               embedVar = Embed(
                  title=f"{trait['NAME']} Trait",
                  description=textwrap.dedent(f"""
                  **{trait['EFFECT']}**:
                  {trait['TRAIT']}
                  """)
               )
               await ctx.send(embed=embedVar)
               return
         return
   except Exception as ex:
      loggy.error(f"Error in Traits command: {ex}")
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
      await ctx.send("There's an issue with your Traits List. Check with support.", ephemeral=True)
      return


@traits.autocomplete("universe")
async def traits_autocomplete(ctx: AutocompleteContext):
   choices = []
   options = crown_utilities.get_cached_universes()
   """
   for option in options
   if ctx.input_text is empty, append the first 24 options in the list to choices
   if ctx.input_text is not empty, append the first 24 options in the list that match the input to choices as typed
   """
    # Iterate over the options and append matching ones to the choices list
   for option in options:
        if not ctx.input_text:
            # If input_text is empty, append the first 24 options to choices
            if len(choices) < 24:
                choices.append(option)
            else:
                break
        else:
            # If input_text is not empty, append the first 24 options that match the input to choices
            if option["name"].lower().startswith(ctx.input_text.lower()):
                choices.append(option)
                if len(choices) == 24:
                    break

   await ctx.send(choices=choices)


@slash_command(name="allowance", description="Gift Family member an allowance", options=[
   SlashCommandOption(name="player", description="Player to give allowance to", type=OptionType.USER, required=True),
], scopes=guild_ids)
@cooldown(Buckets.USER, 1, 60)
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
   

# @slash_command(name="levelme", description="Level up your character", scopes=guild_ids)
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


@slash_command(name="performance", description="Toggles Text Only Performance Mode", scopes=guild_ids)
async def performance(ctx):
   try:
      player = db.queryUser({"DID": str(ctx.author.id)})
      performance_mode = not player.get("PERFORMANCE", False)
      db.updateUserNoFilter(
         {"DID": str(ctx.author.id)}, {"$set": {"PERFORMANCE": performance_mode}}
      )

      embed = Embed(title=f"Performance Mode {crown_utilities.utility_emojis['ON'] if performance_mode else crown_utilities.utility_emojis['OFF']}")
      await ctx.send(embed=embed)
   except Exception as ex:
      loggy.error(f"Error in performance command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #       trace.append({
      #          "filename": tb.tb_frame.f_code.co_filename,
      #          "name": tb.tb_frame.f_code.co_name,
      #          "lineno": tb.tb_lineno
      #       })
      #       tb = tb.tb_next
      # print(str({
      #       'type': type(ex).__name__,
      #       'message': str(ex),
      #       'trace': trace
      # }))
      await ctx.send("There's an issue with your Performance Mode. Seek support in the Anime 🆚+ support server", ephemeral=True)
   
      


@slash_command(name="autosave", description="Toggles Autosave on Battle Start.", scopes=guild_ids)
async def autosave(ctx):
   try:
      player = db.queryUser({"DID": str(ctx.author.id)})
      autosave_on = player.get("AUTOSAVE", False)

      if not autosave_on:
         db.updateUserNoFilter({"DID": str(ctx.author.id)}, {"$set": {"AUTOSAVE": True}})
         embed = Embed(title="Autosave Activated", description="You can still save your progress with the save button in battle.")
         await ctx.send(embed=embed)
      else:
         db.updateUserNoFilter({"DID": str(ctx.author.id)}, {"$set": {"AUTOSAVE": False}})
         embed = Embed(title="Autosave Deactivated", description="You can still save your progress with the save button in battle.")
         await ctx.send(embed=embed)
   except Exception as ex:
      loggy.error(f"Error in Autosave command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #       trace.append({
      #          "filename": tb.tb_frame.f_code.co_filename,
      #          "name": tb.tb_frame.f_code.co_name,
      #          "lineno": tb.tb_lineno
      #       })
      #       tb = tb.tb_next
      # print(str({
      #       'type': type(ex).__name__,
      #       'message': str(ex),
      #       'trace': trace
      # }))
      await ctx.send("There's an issue with your Autosave. Seek support in the Anime 🆚+ support server", ephemeral=True)
   
      


@slash_command(name="difficulty", description="Change the difficulty setting of Anime VS+",
                    options=[
                        SlashCommandOption(
                            name="mode",
                            description="Difficulty Level",
                            type=OptionType.STRING,
                            required=True,
                            choices=[
                                SlashCommandChoice(
                                    name="⚙️ Normal",
                                    value="NORMAL"
                                ),
                                SlashCommandChoice(
                                    name="⚙️ Easy",
                                    value="EASY"
                                ),
                                SlashCommandChoice(
                                    name="⚙️ Hard",
                                    value="HARD"
                                )
                            ]
                        )
                    ]
        ,scopes=guild_ids)
@cooldown(Buckets.USER, 1, 10)
async def difficulty(ctx, mode):
   try:
      query = {'DID': str(ctx.author.id)}
      player = db.queryUser(query)
      update_query = {'$set': {'DIFFICULTY': mode}}
      response = db.updateUserNoFilter(query, update_query)
      if response:
         embed = Embed(title="Difficulty Updated", description=f"{ctx.author.mention} has been updated to ⚙️ **{mode.lower()}** mode.", color=0x00ff00)
         await ctx.send(embed=embed)
   except Exception as ex:
      loggy.error(f"Error in difficulty command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #       trace.append({
      #          "filename": tb.tb_frame.f_code.co_filename,
      #          "name": tb.tb_frame.f_code.co_name,
      #          "lineno": tb.tb_lineno
      #       })
      #       tb = tb.tb_next
      # print(str({
      #       'type': type(ex).__name__,
      #       'message': str(ex),
      #       'trace': trace
      # }))
      embed = Embed(title="Difficulty Update Failed", description=f"{ctx.author.mention} has failed to update to ⚙️ **{mode.lower()}** mode.", color=0xff0000)
      await ctx.send(embed=embed)
   
      


@slash_command(name="battlehistory", description="How much battle history do you want to see during battle? 2 - 6", options=[
   SlashCommandOption(name="history", 
                     description="How much battle history do you want to see during battle? 2 - 6", 
                     type=OptionType.INTEGER, 
                     required=True,
                     choices=[
                        SlashCommandChoice(name="2 Messages", value=2),
                        SlashCommandChoice(name="3 Messages", value=3),
                        SlashCommandChoice(name="4 Messages", value=4),
                        SlashCommandChoice(name="5 Messages", value=5),
                        SlashCommandChoice(name="6 Messages", value=6)
                     ]
)], scopes=guild_ids)
@cooldown(Buckets.USER, 1, 10)
async def battlehistory(ctx, history: int):
   try:
      user_query = {"DID": str(ctx.author.id)}
      update_query = {"$set": {"BATTLE_HISTORY": history}}
      response = db.updateUserNoFilter(user_query, update_query)
      await ctx.send(f":bookmark_tabs:  | You will now see up to {str(history)} history messages during battle.")
   except Exception as e:
      await ctx.send(e)
   

@slash_command(name="bounty", description="Set Association Bounty", options=[
   SlashCommandOption(name="amount", description="Amount to set bounty to", type=OptionType.INTEGER, required=True),
], scopes=guild_ids)
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


@slash_command(name="sponsor", description="Sponsor Guild with Association Funds", options=[
   SlashCommandOption(name="guild", description="Guild to sponsor", type=OptionType.STRING, required=True),
   SlashCommandOption(name="amount", description="Amount to sponsor", type=OptionType.INTEGER, required=True),
], scopes=guild_ids)
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


@slash_command(name="fund", description="Fund Association From Guild Bank", options=[
   SlashCommandOption(name="amount", description="Amount to fund", type=OptionType.INTEGER, required=True),
], scopes=guild_ids)
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


@slash_command(description="Create Code for Droppables", options=[
   SlashCommandOption(name="code_input", description="Code to create", type=OptionType.STRING, required=True),
   SlashCommandOption(name="coin", description="Coin amount", type=OptionType.INTEGER, required=True),
   SlashCommandOption(name="gems", description="Gem amount", type=OptionType.INTEGER, required=True),
   SlashCommandOption(name="card", description="Card to give", type=OptionType.STRING, required=False),
   SlashCommandOption(name="arm", description="Arm to give", type=OptionType.STRING, required=False),
   SlashCommandOption(name="summon", description="Summon to give", type=OptionType.STRING, required=False),
   SlashCommandOption(name="exp_to_give", description="Exp to give", type=OptionType.INTEGER, required=False),

], scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def createcode(ctx, code_input, coin, gems, card=None, exp_to_give=0):
   is_creator = db.queryUser({'DID': str(ctx.author.id)})['CREATOR']
   if not is_creator:
      await ctx.send("Creator only command.", ephemeral=True)
      return
      
   code_exist = db.queryCodes({'CODE_INPUT': code_input})
   if card:
      card_exist = db.queryCard({'NAME': card})
      if not card_exist:
         await ctx.send("Card does not exist")
         return
   if code_exist:
      await ctx.send("Code already exist")
      return
   else:
      try:
         query = {
            'CODE_INPUT': code_input,
            'COIN': coin,
            'GEMS': gems,
            'AVAILABLE': True, 
            'CARD': card,
            'EXP': exp_to_give
         }
         response = db.createCode(data.newCode(query))
         await ctx.send(f"**{code_input}** Code has been created")
         loggy.info(f"Code {code_input} has been created by {ctx.author}")
      except Exception as e:
         loggy.error(f"Error in Create Code command: {e}")
         await ctx.send("There's an issue with your Code. Seek support in the Anime 🆚+ support server", ephemeral=True)
         return


@slash_command(description="Input Codes", options=[
   SlashCommandOption(name="code_input", description="Code to input", type=OptionType.STRING, required=True),
], scopes=guild_ids)
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
            if gems != 0:
               if not user.gems:
                  universe_to_add_gems = equipped_card.universe
                  user.save_gems(universe_to_add_gems, gems)
               for universe in user.gems:
                  user.save_gems(universe["UNIVERSE"], gems)
               embed = Embed(title="Gems Increased", description=f"💎 **{gems:,}** gems have been added to your balance!", color=0x00ff00)
               embed_list.append(embed)

            if coin != 0:
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


@slash_command(description="admin only", options=[
   SlashCommandOption(name="collection", description="Collection to update", type=OptionType.STRING, required=True),
   SlashCommandOption(name="new_field", description="New Field to add", type=OptionType.STRING, required=True),
   SlashCommandOption(name="field_type", description="Field Type", type=OptionType.STRING, required=True),
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
], scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def addfield(ctx, collection, new_field, field_type, password, key):
   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   if key != '937':
      return await ctx.send("Admin Only")
   
   if field_type == "fix":
      field_type = True
   elif field_type == 'string':
      field_type = ""
   elif field_type == 'int':
      field_type = 0
   elif field_type == 'list':
      field_type = [
         {"ELEMENT": "PHYSICAL", "ESSENCE": 5000},
         {"ELEMENT": "FIRE", "ESSENCE": 5000},
         {"ELEMENT": "ICE", "ESSENCE": 5000},
         {"ELEMENT": "WATER", "ESSENCE": 5000},
         {"ELEMENT": "EARTH", "ESSENCE": 5000},
         {"ELEMENT": "ELECTRIC", "ESSENCE": 5000},
         {"ELEMENT": "WIND", "ESSENCE": 5000},
         {"ELEMENT": "PSYCHIC", "ESSENCE": 5000},
         {"ELEMENT": "DEATH", "ESSENCE": 5000},
         {"ELEMENT": "LIFE", "ESSENCE": 5000},
         {"ELEMENT": "LIGHT", "ESSENCE": 5000},
         {"ELEMENT": "DARK", "ESSENCE": 5000},
         {"ELEMENT": "POISON", "ESSENCE": 5000},
         {"ELEMENT": "RANGED", "ESSENCE": 5000},
         {"ELEMENT": "ENERGY", "ESSENCE": 5000},
         {"ELEMENT": "RECKLESS", "ESSENCE": 5000},
         {"ELEMENT": "TIME", "ESSENCE": 5000},
         {"ELEMENT": "BLEED", "ESSENCE": 5000},
         {"ELEMENT": "GRAVITY", "ESSENCE": 5000}
      ]
   elif field_type == 'deck':
      new_field = "DECK.$[].TALISMAN"
      field_type = "NULL"
   elif field_type == 'blank_list':
      field_type = []
   elif field_type == 'bool':
      field_type = False

   elif field_type == 'dict':
      field_type = {}
      
   if collection == 'fix':
      response = db.updateManyUsers({'$set': {'BOSS_FOUGHT': True}})
   elif collection == 'cards':
      response = db.updateManyCards({'$set': {new_field: field_type}})
   elif collection == 'scenarios':
      response = db.updateManyScenarios({'$set': {new_field: field_type}})
   elif collection == 'titles':
      response = db.updateManyTitles({'$set': {new_field: field_type}})
   elif collection == 'vault':
      response = db.updateManyVaults({'$set': {new_field: field_type}})
   elif collection == 'users':
      response = db.updateManyUsers({'$set': {new_field: field_type}})
   elif collection == 'universe':
      response = db.updateManyUniverses({'$set': {new_field: field_type}})
   elif collection == 'boss':
      response = db.updateManyBosses({'$set': {new_field: field_type}})
   elif collection == 'arms':
      response = db.updateManyArms({'$set': {new_field: field_type}})
   elif collection == 'pets':
      response = db.updateManySummons({'$set': {new_field: field_type}})
   elif collection == 'teams':
      response = db.updateManyTeams({'$set': {new_field: field_type}})
   elif collection == 'house':
      response = db.updateManyHouses({'$set': {new_field: field_type}})
   elif collection == 'hall':
      response = db.updateManyHalls({'$set': {new_field: field_type}})
   elif collection == 'family':
      response = db.updateManyFamily({'$set': {new_field: field_type}})
   elif collection == 'guild':
      response = db.updateManyGuild({'$set': {new_field: field_type}})
   
   await ctx.send("Update completed.")


@slash_command(description="admin only", options=[
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
],scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updatename(ctx, collection, name, new_name, password, key):
   await ctx.defer()

   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   if key != '937':
      return await ctx.send("Admin Only")
   try:
      if collection == 'cards':
         # find if card exists
         card = db.queryCard({'NAME': name})
         
         if card:
            # update cards collection
            response = db.updateCard({'NAME': name}, {'$set': {'NAME': new_name}})

            # update vaults collection
            all_vaults = db.queryAllVault()
            for vault in all_vaults:
               update_vault = False
               if 'CARDS' in vault:
                  for i, card in enumerate(vault['CARDS']):
                        if card == name:
                           vault['CARDS'][i] = new_name
                           update_vault = True
               if 'CARD_LEVELS' in vault:
                  for card in vault['CARD_LEVELS']:
                        if card['CARD'] == name:
                           card['CARD'] = new_name
                           update_vault = True
               if 'DECK' in vault:
                  for card in vault['DECK']:
                        if card['CARD'] == name:
                           card['CARD'] = new_name
                           update_vault = True
               if 'QUESTS' in vault:
                  for card in vault['QUESTS']:
                        if card['OPPONENT'] == name:
                           card['OPPONENT'] = new_name
                           update_vault = True
               if 'DESTINY' in vault:
                  for card in vault['DESTINY']:
                        if card['DEFEAT'] == name:
                           card['DEFEAT'] = new_name
                           update_vault = True
                        if card['EARN'] == name:
                           card['EARN'] = new_name
                           update_vault = True
                        if 'USE_CARDS' in card:
                           if isinstance(card['USE_CARDS'], list):
                              for i, subcard in enumerate(card['USE_CARDS']):
                                    if subcard == name:
                                       card['USE_CARDS'][i] = new_name
                                       update_vault = True
                           elif isinstance(card['USE_CARDS'], dict):
                              for subcard in card['USE_CARDS'].values():
                                    if subcard == name:
                                       card['USE_CARDS'][subcard] = new_name
                                       update_vault = True
                           else:
                              # Convert the string to a list or a dictionary as appropriate
                              if ',' in card['USE_CARDS']:
                                    card['USE_CARDS'] = card['USE_CARDS'].split(',')
                              else:
                                    card['USE_CARDS'] = [card['USE_CARDS']]
                              # Update the list as before
                              for i, subcard in enumerate(card['USE_CARDS']):
                                    if subcard == name:
                                       card['USE_CARDS'][i] = new_name
                                       update_vault = True
               if 'STORAGE' in vault:
                  for i, card in enumerate(vault['STORAGE']):
                        if card == name:
                           vault['STORAGE'][i] = new_name
                           update_vault = True
               if update_vault:
                  db.updateUserNoFilter({'DID': vault['DID']}, {'$set': {'CARDS': vault.get('CARDS', []), 'CARD_LEVELS': vault.get('CARD_LEVELS', []), 'DECK': vault.get('DECK', []), 'QUESTS': vault.get('QUESTS', []), 'DESTINY': vault.get('DESTINY', []), 'STORAGE': vault.get('STORAGE', [])}})            
            
            # update users collection
            all_users = db.queryAllUsers()
            for user in all_users:
               update_user = False
               if 'CARD' in user and user['CARD'] == name:
                  user['CARD'] = new_name
                  update_user = True
               if 'BOSS_WINS' in user:
                  for i, boss in enumerate(user['BOSS_WINS']):
                        if boss == name:
                           user['BOSS_WINS'][i] = new_name
                           update_user = True
               if update_user:
                  db.updateUserNoFilter({'DID': user['DID']}, {'$set': {'CARD': user.get('CARD', ''), 'BOSS_WINS': user.get('BOSS_WINS', [])}})               

            # update universe collection
            all_universes = db.queryAllUniverse()
            for universe in all_universes:
               update_universe = False
               if 'CROWN_TALES' in universe:
                  for i, card in enumerate(universe['CROWN_TALES']):
                        if card == name:
                           universe['CROWN_TALES'][i] = new_name
                           update_universe = True
               if 'UNIVERSE_BOSS' in universe and universe['UNIVERSE_BOSS'] == name:
                  universe['UNIVERSE_BOSS'] = new_name
                  update_universe = True
               if 'DUNGEONS' in universe:
                  for i, card in enumerate(universe['DUNGEONS']):
                        if card == name:
                           universe['DUNGEONS'][i] = new_name
                           update_universe = True
               if update_universe:
                  db.updateUniverse({'TITLE': universe['TITLE']}, {'$set': {'CROWN_TALES': universe.get('CROWN_TALES', []), 'UNIVERSE_BOSS': universe.get('UNIVERSE_BOSS', ''), 'DUNGEONS': universe.get('DUNGEONS', [])}})               
            
            # update scenarios collection
            all_scenarios = db.queryAllScenarios()
            for scenario in all_scenarios:
               update_scenario = False
               if 'ENEMIES' in scenario:
                  for i, card in enumerate(scenario['ENEMIES']):
                        if card == name:
                           scenario['ENEMIES'][i] = new_name
                           update_scenario = True
               if 'NORMAL_DROPS' in scenario:
                  for i, card in enumerate(scenario['NORMAL_DROPS']):
                        if card == name:
                           scenario['NORMAL_DROPS'][i] = new_name
                           update_scenario = True
               if 'EASY_DROPS' in scenario:
                  for i, card in enumerate(scenario['EASY_DROPS']):
                        if card == name:
                           scenario['EASY_DROPS'][i] = new_name
                           update_scenario = True
               if 'HARD_DROPS' in scenario:
                  for i, card in enumerate(scenario['HARD_DROPS']):
                        if card == name:
                           scenario['HARD_DROPS'][i] = new_name
                           update_scenario = True
               if update_scenario:
                  db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'ENEMIES': scenario.get('ENEMIES', []), 'NORMAL_DROPS': scenario.get('NORMAL_DROPS', []), 'EASY_DROPS': scenario.get('EASY_DROPS', []), 'HARD_DROPS': scenario.get('HARD_DROPS', [])}})

            
            # update guild collections
            all_guilds = db.queryAllGuild()
            for guild in all_guilds:
               update_guild = False
               if 'S_CARD_LEVELS' in guild:
                  for card in guild['S_CARD_LEVELS']:
                        if card['CARD'] == name:
                           card['CARD'] = new_name
                           update_guild = True
               if 'CSTORAGE' in guild:
                  for i, card in enumerate(guild['CSTORAGE']):
                        if card == name:
                           guild['CSTORAGE'][i] = new_name
                           update_guild = True
               if update_guild:
                  db.updateGuild({'GNAME': guild['GNAME']}, {'$set': {'S_CARD_LEVELS': guild.get('S_CARD_LEVELS', []), 'CSTORAGE': guild.get('CSTORAGE', [])}})

            # update boss collection
            all_bosses = db.queryAllBosses()
            for boss in all_bosses:
               if 'NAME' in boss and boss['NAME'] == name:
                  boss['NAME'] = new_name
                  db.updateBoss({'NAME': name}, {'$set': {'NAME': new_name}})


            # update abyss collection
            all_abyss = db.queryAllAbyss()
            for abyss in all_abyss:
               update_abyss = False
               if 'ENEMIES' in abyss:
                  for i, card in enumerate(abyss['ENEMIES']):
                        if card == name:
                           abyss['ENEMIES'][i] = new_name
                           update_abyss = True
               if 'BANNED_CARDS' in abyss:
                  for i, card in enumerate(abyss['BANNED_CARDS']):
                        if card == name:
                           abyss['BANNED_CARDS'][i] = new_name
                           update_abyss = True
               if update_abyss:
                  db.updateAbyss({'FLOOR': abyss['FLOOR']}, {'$set': {'ENEMIES': abyss.get('ENEMIES', []), 'BANNED_CARDS': abyss.get('BANNED_CARDS', [])}})


            return await ctx.send(f"Card **{name}** has been renamed to **{new_name}**.")
         else:
            return await ctx.send("This card does not exist.")
      else:
         return await ctx.send("You do not have permissions to run this command.")
   except Exception as ex:
      loggy.error(f"Error in updatename command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #    trace.append({
      #       "filename": tb.tb_frame.f_code.co_filename,
      #       "name": tb.tb_frame.f_code.co_name,
      #       "lineno": tb.tb_lineno
      #    })
      #    tb = tb.tb_next
      # print(str({
      #    'type': type(ex).__name__,
      #    'message': str(ex),
      #    'trace': trace
      # }))
      await ctx.send("Issue with command. Please contact casperjayden#0001")


@slash_command(description="admin only", options=[
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
],scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updatesaves(ctx, password, key):
   await ctx.defer()

   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   if key != '937':
      return await ctx.send("Admin Only")


   try:
      users = db.queryAllUsers()

      count = 0

      for user in users:
         save_spots = user.get("SAVE_SPOT", [])
         unique_combinations = {}
         for save_spot in save_spots:
               combination_key = (save_spot["UNIVERSE"], save_spot["MODE"])
               if combination_key in unique_combinations:
                  unique_combinations[combination_key].append(save_spot)
               else:
                  unique_combinations[combination_key] = [save_spot]

         for combination_key in unique_combinations:
               duplicates = unique_combinations[combination_key]
               if len(duplicates) > 1:
                  sorted_duplicates = sorted(duplicates, key=lambda x: x["CURRENTOPPONENT"], reverse=True)
                  for duplicate in sorted_duplicates[1:]:
                     query = {"_id": user["_id"], "SAVE_SPOT": duplicate}
                     new_value = {"$pull": {"SAVE_SPOT": duplicate}}
                     db.updateUserNoFilter(query, new_value)
                     count += 1

      await ctx.send(f"Updated {count} saves.")
   except Exception as ex:
      loggy.error(f"Error in updatesaves command: {ex}")
      # trace = []
      # tb = ex.__traceback__
      # while tb is not None:
      #    trace.append({
      #       "filename": tb.tb_frame.f_code.co_filename,
      #       "name": tb.tb_frame.f_code.co_name,
      #       "lineno": tb.tb_lineno
      #    })
      #    tb = tb.tb_next
      # print(str({
      #    'type': type(ex).__name__,
      #    'message': str(ex),
      #    'trace': trace
      # }))
      await ctx.send("Issue with command. Please contact casperjayden#0001")


@slash_command(description="admin only", options=[
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
],scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updatepokemonuniverses(ctx, password, key):
   await ctx.defer()

   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   if key != '937':
      return await ctx.send("Admin Only")


   try:
      cards = db.queryAllCardsBasedOnUniverse({
               "UNIVERSE": { "$in": ["Kanto Region", "Johto Region", "Hoenn Region", "Sinnoh Region", "POKEMON"] }
               })
      
      titles = db.queryAllTitlesBasedOnUniverses({
               "UNIVERSE": { "$in": ["Kanto Region", "Johto Region", "Hoenn Region", "Sinnoh Region", "POKEMON"] }
               })
      
      arms = db.queryAllArmsBasedOnUniverses({
               "UNIVERSE": { "$in": ["Kanto Region", "Johto Region", "Hoenn Region", "Sinnoh Region", "POKEMON"] }
               })
      
      summons = db.queryAllSummonsBasedOnUniverses({
               "UNIVERSE": { "$in": ["Kanto Region", "Johto Region", "Hoenn Region", "Sinnoh Region", "POKEMON"] }
               })

      count = 0

      # Update each card in the cards list to have {"UNIVERSE": "Pokemon"}
      # for card in cards:
      #    db.updateCard({'NAME': card['NAME']}, {'$set': {'UNIVERSE': 'Pokemon'}})
      #    count += 1

      # Update each title in the titles list to have {"UNIVERSE": "Pokemon"}
      for title in titles:
         db.updateTitle({'TITLE': title['TITLE']}, {'$set': {'UNIVERSE': 'Pokemon'}})
         count += 1
      
      # Update each arm in the arms list to have {"UNIVERSE": "Pokemon"}
      for arm in arms:
         db.updateArm({'ARM': arm['ARM']}, {'$set': {'UNIVERSE': 'Pokemon'}})
         count += 1

      # Update each summon in the summons list to have {"UNIVERSE": "Pokemon"}
      for summon in summons:
         db.updateSummon({'PET': summon['PET']}, {'$set': {'UNIVERSE': 'Pokemon'}})
         count += 1
         

      await ctx.send(f"Updated {count} items.")
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
      await ctx.send("Issue with command. Please contact casperjayden#0001")


@slash_command(description="admin only", options=[
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
],scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updatescenariosanduniverses(ctx, password, key):
   await ctx.defer()
   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   if key != '937':
      return await ctx.send("Admin Only")

   try:
      """
      Update all scenarios with new fields below
      IS_DESTINY: False
      TACTICS: []
      LOCATIONS: []
      
      Update all universes with new fields below
      LOCATIONS: []
      """
      count = 0
      all_scenarios = db.queryAllScenarios()
      for scenario in all_scenarios:
         if 'IS_DESTINY' not in scenario:
            db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'IS_DESTINY': False}})
         if 'TACTICS' not in scenario:
            db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'TACTICS': []}})
         if 'LOCATIONS' not in scenario:
            db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'LOCATIONS': []}})
         if 'DESTINY_CARDS' not in scenario:
            db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'DESTINY_CARDS': []}})
         count += 1

      # all_universes = db.queryAllUniverses()
      # for universe in all_universes:
      #    if 'LOCATIONS' not in universe:
      #       db.updateUniverse({'TITLE': universe['TITLE']}, {'$set': {'LOCATIONS': []}})
      #    count += 1

      await ctx.send(f"Updated {count} scenarios and universes.")
   except Exception as ex:
      print(e)
      await ctx.send("Issue with command")


@slash_command(description="update moves", options=[
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
], scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updatemoves(ctx, password, key):
   await ctx.defer()

   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   
   if key != '937':
      return await ctx.send("Admin Only")

   counter = 0

   try:
      for card in db.queryAllCardByParam({"UNIVERSE": "Fairy Tail"}):
      # Loop through all moves in the card's moveset
         for move in card['MOVESET']:
            # Check if the move has a STAM value of 10, 30, or 80
            if move['STAM'] in [10, 30, 80]:
                  # Create a new arm if the arm name doesn't already exist
                  if not db.queryArm({'ARM': list(move.keys())[0]}):
                     power = list(move.values())[0]
                     drop_style = "TALES"
                     # Determine the price and abilities of the arm based on the move's STAM value
                     if move['STAM'] == 10:
                        price = 10000
                        ability = 'BASIC'
                        if power > 250:
                           drop_style = "DUNGEONS"
                     elif move['STAM'] == 30:
                        ability = 'SPECIAL'
                        if power > 325:
                           drop_style = "DUNGEONS"
                     elif move['STAM'] == 80:
                        ability = 'ULTIMATE'
                        if power > 550:
                           drop_style = "DUNGEONS"

                     # Create the new arm document
                     arm = {
                        'ABILITIES': [{
                           ability: power
                        }],
                        'ARM': list(move.keys())[0],
                        'UNIVERSE': card['UNIVERSE'],
                        'AVAILABLE': True,
                        'TIMESTAMP': now,
                        'ELEMENT': move['ELEMENT'],
                        'DROP_STYLE': drop_style
                     }
                     
                     # Insert the new arm document into the ARMS collection
                     db.createArm(arm)
                     counter += 1

      await ctx.send(f"Created {counter} new arms")
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


@slash_command(description="update title abilities", options=[
   SlashCommandOption(name="password", description="Admin Password", type=OptionType.STRING, required=True),
   SlashCommandOption(name="key", description="Admin Key", type=OptionType.STRING, required=True)
], scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updatetitleabilities(ctx, password, key):
   await ctx.defer()
   if password != 'casperjayden':  
      return await ctx.send("Admin Only")
   
   if key != '937':
      return await ctx.send("Admin Only")

   counter = 0
   """
   For each title,
   change ABILITIES list object format
   It is currently ABILITIES[{"ATK": 42}]
   It needs to be ABILITIES[{"ABILITY": "ATK", "POWER": 42, "ELEMENT": "", "DURATION": 0}]
   """

   all_titles = db.queryAllTitles()

   for title in all_titles:
      abilities = title['ABILITIES']
      new_abilities = []
      for ability in abilities:
         for key, value in ability.items():
            new_abilities.append({"ABILITY": key, "POWER": value, "ELEMENT": "", "DURATION": 0})
      db.updateTitle({'TITLE': title['TITLE']}, {'$set': {'ABILITIES': new_abilities}})
      counter += 1

   await ctx.send(f"Updated {counter} titles")

   
@slash_command(description="update moves", scopes=guild_ids)
@slash_default_member_permission(Permissions.ADMINISTRATOR)
async def updateclass(ctx):
   await ctx.defer()
   counter = 0

   try:
      mlist = ['RECOIL']
      for card in db.queryAllCards():
         if card['MOVESET'][0]['ELEMENT'] in mlist:
            db.updateCard({'NAME': card['NAME']}, {'$set': {'MOVESET.0.ELEMENT': "RECKLESS"}})
         if card['MOVESET'][1]['ELEMENT'] in mlist:
            db.updateCard({'NAME': card['NAME']}, {'$set': {'MOVESET.1.ELEMENT': "RECKLESS"}})
         if card['MOVESET'][2]['ELEMENT'] in mlist:
            db.updateCard({'NAME': card['NAME']}, {'$set': {'MOVESET.2.ELEMENT': "RECKLESS"}})
         counter += 1
         
      await ctx.send(f"Updated {counter} cards")
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


# Create a slash_command that gets a list of 50 cards and saves it to my account in the database
@slash_command(description="save cards", scopes=guild_ids)
async def savecards(ctx):
   loggy.info("savecards command")
   await ctx.defer()
   try:
      d = db.queryUser({'DID': str(ctx.author.id)})
      loggy.debug(d)
      me = crown_utilities.create_player_from_data(d)
      cards = db.queryAllCards()
      # loggy.info(cards)
      count = 0
      for card in cards:
         loggy.info(f"Saving card: {card['NAME']}")
         card_data = crown_utilities.create_card_from_data(db.queryCard({'NAME': card['NAME']}))
         me.save_card(card_data)
         count += 1
         if  count == 50:
            break
      await ctx.send(f"Saved {count} cards to your account.")
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
      loggy.error(f"Error in savecards command: {ex}")
      await ctx.send("Issue with command.")
      return
         
      
# Create a slash_command that pulls all scenarios and if the title of the scenario starts and ends with quotation marks like "" update the title with removed quotation marks. 
# In addition to this, if the scenario title starts with Defeat the delete the "the" and update the title with the new title.
# @slash_command(description="update scenarios", scopes=guild_ids)
# async def updatescenarios(ctx):
#    loggy.info("updatescenarios command")
#    await ctx.defer()
#    try:
#       scenarios = db.queryAllScenarios()
#       count = 0
#       for scenario in scenarios:
#          if scenario['TITLE'].startswith('"') and scenario['TITLE'].endswith('"'):
#             new_title = scenario['TITLE'][1:-1]
#             db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'TITLE': new_title}})
#             count += 1
#          if scenario['TITLE'].startswith("Defeat the "):
#             new_title = scenario['TITLE'].replace("the", "")
#             db.updateScenario({'TITLE': scenario['TITLE']}, {'$set': {'TITLE': new_title}})
#             count += 1
#       await ctx.send(f"Updated {count} scenarios.")
#    except Exception as ex:
#       loggy.critical(f"Error in updatescenarios command: {ex}")
#       await ctx.send("Issue with command.")

@slash_command(name="createscenarios", description="create scenarios", scopes=guild_ids)
@slash_option(name="mode", description="Mode to create scenarios for", opt_type=OptionType.STRING, choices=[
   SlashCommandChoice(name="Scenario", value="normal"),
   SlashCommandChoice(name="Raid", value="raid")
], required=True)
@slash_option(name="scenario_universe", description="Universe to create scenarios for", opt_type=OptionType.STRING, required=True, autocomplete=True)
async def createscenarios(ctx: InteractionContext, mode, scenario_universe: str=""):
   loggy.info("createscenarios command")

   if ctx.author.id not in [306429381948211210, 263564778914578432]:
      await ctx.send("🛑 You know damn well this command isn't for you.")
      return
   
   await ctx.defer()
   try:
      universes = db.queryAllUniversesForScenario({'TITLE': scenario_universe})

      async def process_universe(universe, mode):
         cards = db.queryAllCardsBasedOnUniverse({"UNIVERSE": universe['TITLE']})
         valid_cards = [card for card in cards if 1 <= card['TIER'] <= 10]
         used_cards = set()
         
         low_end = 25
         high_end = 30

         if mode == "raid":
            low_end = 4
            high_end = 8

         async def create_scenario(mode):
            nonlocal used_cards
            available_cards = [card for card in valid_cards if card['NAME'] not in used_cards]

            if not available_cards:
                  loggy.warning(f"No more available cards for universe {universe['TITLE']}")
                  return
            
            enemy_count = min(random.randint(1, 4), len(available_cards))
            selected_cards = random.sample(available_cards, enemy_count)
            used_cards.update(card['NAME'] for card in selected_cards)

            if mode == "raid":
                  level = random.randint(1500, 5000)
            else:
                  level = random.randint(1, 500)

            if level < 500:
                  tier_range = range(1, 8)
            else:
                  tier_range = range(5, 11)

            selected_cards = [card for card in selected_cards if card['TIER'] in tier_range]
            
            if len(selected_cards) == 1:
                  title = f"Defeat {selected_cards[0]['NAME']} in battle!"
            else:
                  title = await suggested_title_scenario(universe['TITLE'], [card['NAME'] for card in selected_cards])
                  if not title:
                        ran_number_for_secret_files = random.randint(10, 5000)
                        title = f"Secret Files # {str(ran_number_for_secret_files)}"
                  await asyncio.sleep(1)
            existing_scenario = db.queryScenario({"TITLE": title})
            if existing_scenario:
                  loggy.info(f"Scenario with title '{title}' already exists. Skipping.")
                  return


            scenario = {
                  "TITLE": title,
                  "UNIVERSE": universe['TITLE'],
                  "ENEMIES": [card['NAME'] for card in selected_cards],
                  "NORMAL_DROPS": [],
                  "EASY_DROPS": [],
                  "HARD_DROPS": [],
                  "IS_DESTINY": False,
                  "TACTICS": [],
                  "LOCATIONS": [],
                  "IS_RAID": mode == "raid",
                  "MUST_COMPLETE": False,
                  "IMAGE": universe['PATH'],
                  "DESTINY_CARDS": [],
                  "AVAILABLE": True,
                  "ENEMY_LEVEL": level
            }
            loggy.info(f"Creating scenario: {title}")
            db.insertScenario(scenario)

         await asyncio.gather(*(create_scenario(mode) for _ in range(random.randint(low_end, high_end))))

      await asyncio.gather(*(process_universe(universe, mode) for universe in universes))
      await ctx.send("Scenarios created.")
   
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
      loggy.error(f"Error in createscenarios command: {ex}")
      await ctx.send("Issue with command.")
      return


@createscenarios.autocomplete("scenario_universe")
async def createscenarios_autocomplete(ctx: AutocompleteContext):
   choices = []
   options = crown_utilities.get_cached_universes()
   """
   for option in options
   if ctx.input_text is empty, append the first 24 options in the list to choices
   if ctx.input_text is not empty, append the first 24 options in the list that match the input to choices as typed
   """
    # Iterate over the options and append matching ones to the choices list
   for option in options:
        if not ctx.input_text:
            # If input_text is empty, append the first 24 options to choices
            if len(choices) < 24:
                choices.append(option)
            else:
                break
        else:
            # If input_text is not empty, append the first 24 options that match the input to choices
            if option["name"].lower().startswith(ctx.input_text.lower()):
                choices.append(option)
                if len(choices) == 24:
                    break

   await ctx.send(choices=choices)




# if config('ENV') == "production":
#    DISCORD_TOKEN = config('DISCORD_TOKEN')
# else:
#    DISCORD_TOKEN = config('NEW_TEST_DISCORD_TOKEN')

# bot.start(DISCORD_TOKEN)


async def restart_bot():
    await bot.stop()
    await bot.start()


@Task.create(IntervalTrigger(minutes=5))
async def check_heartbeat():
      try:
         # Get the bot's latency
         latency = bot.latency
         loggy.info(f'Heartbeat check - latency: {latency}')
         # Check if latency is within acceptable range (e.g., below 2 seconds)
         if latency and latency > 9.0:
               loggy.warning('High latency detected, restarting bot...')
               await restart_bot()
      except Exception as e:
         loggy.error(f'Error during heartbeat check: {e}')
         await restart_bot()


# Run the bot
bot.start()



