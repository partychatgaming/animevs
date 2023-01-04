import asyncio
# from operator import is_
# from urllib import response
import cogs.profile

import crown_utilities
import db
import time
import classes as data
import messages as m
import discord
import DiscordUtils
from discord.ext import commands, tasks
import numpy as np
import help_commands as h
import destiny as d
# Converters
from discord import User
from discord_slash import SlashCommand
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
import textwrap
from discord_slash import cog_ext, SlashContext
from dinteractions_Paginator import Paginator
from discord_slash.utils.manage_commands import create_option, create_choice
import os
import logging
from decouple import config
import textwrap
import random
import unique_traits as ut
now = time.asctime()
import asyncio
import topgg
import requests
import json
import datetime


# Logging Logic

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

guild_ids = None
guild_id = None
guild_channel = None

intents = discord.Intents.all()
client = discord.Client()

if config('ENV') == "production":
   # PRODUCTION
   bot = commands.Bot(command_prefix=".", intents=intents)
   guild_id = 543442011156643871
   guild_channel = 957061470192033812
else:
   # TEST
   bot = commands.Bot(command_prefix=",", intents=intents)
   guild_ids = [839352855000776735]
   guild_id = 839352855000776735
   guild_channel = 962580388432195595


slash = SlashCommand(bot, sync_commands=True)


async def load(ctx, extension):
   # Goes into cogs folder and looks for extension
   bot.load_extension(f'cogs.{extension}')

async def unload(ctx, extension):
   # Goes into cogs folder and looks for extension
   bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
   if filename.endswith('.py'):
      # :-3 removes .py from filename
      bot.load_extension(f'cogs.{filename[:-3]}')


bot.remove_command("help")

@slash.slash(name="Help", description="Learn the commands", options=[
                        create_option(
                            name="selection",
                            description="select an option you need help with",
                            option_type=3,
                            required=True,
                            choices=[
                                create_choice(
                                    name="⚔️ How to Play?",
                                    value="play",
                                ),
                                create_choice(
                                    name="❓ What do these emoji's mean?",
                                    value="legend",
                                ),
                                create_choice(
                                    name="🦠 What are enhancers?",
                                    value="enhancers",
                                ),
                                create_choice(
                                    name="🔅 What are elements?",
                                    value="elements",
                                ),
                                create_choice(
                                    name="👑 Your Cards, Accessories, Quests, Destinies, Shop, Blacksmith, Trade, Gift, Analysis, Codes",
                                    value="menu",
                                ),
                                create_choice(
                                    name="🌍 All Info, Cards, Accessories, Quests, Destinies a universe has to offer",
                                    value="universe",
                                ),
                                create_choice(
                                    name="👥 Family, Guild, Association",
                                    value="teams",
                                ),
                                create_choice(
                                    name="📔 Read the Anime VS+ Manual",
                                    value="manual",
                                ),

                            ]
                        )
                    ]
 ,guild_ids=guild_ids)
async def help(ctx: SlashContext, selection):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"
   
   if selection == "menu":
      embedVar = discord.Embed(title= f"Your stuff, your way!", description=h.CTAP_COMMANDS, colour=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "legend":
      embedVar = discord.Embed(title= f"What do these emoji's mean?", description=h.LEGEND, colour=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "elements":
      embedVar = discord.Embed(title= f"What does each element do?", description=h.ELEMENTS, colour=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "play":
      embedVar = discord.Embed(title= f"Start playing now!", description=h.CROWN_UNLIMITED_GAMES, colour=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return


   if selection == "universe":
      embedVar = discord.Embed(title= f"🌍 Universe Info!", description=h.UNIVERSE_STUFF, colour=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
      return

   if selection == "teams":
      embedVar = discord.Embed(title= f"Gang up and play!", description=h.BOT_COMMANDS, colour=0x7289da)
      embedVar.set_thumbnail(url=avatar)
      embedVar.set_footer(text=f"/animevs - Anime VS+ Manual")
      await ctx.send(embed=embedVar)
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


@bot.event
async def on_ready():
   print('Bot is ready!')
   for server in bot.guilds:
        print(server.name)


# @slash.slash(name="Enhancers", description="List of Enhancers", guild_ids=guild_ids)
async def enhancers(ctx):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"

   try:
      embedVar1 = discord.Embed(title= f"Enhancer Type: Boosts",colour=0x7289da)
      embedVar1.set_thumbnail(url=avatar)
      embedVar1.add_field(name="`BOOSTS`", value="**ATK**\n**Title, Arm, Card Passive Effect:** Increase Attack by Flat AP value.\n**Card Active Enhancer Effect:** Increase Attack By AP %.\n\n**DEF**\n**Title, Arm, Card Passive Effect:** Increase Defense by Flat AP value.\n**Card Active Enhancer Effect:** Increase Defense By AP %.\n\n**HLT**\n**Title, Arm, Card Passive Effect:** Increase Health by Flat AP value.\n**Card Active Enhancer Effect:** Increase Health By Flat AP + 16% of Current Health.\n\n**STAM** - Increase Stamina by Flat AP\n\n")
      embedVar1.set_footer(text=f"/help - Bot Help")

      embedVar2 = discord.Embed(title= f"Enhancer Type: Steals",colour=0x7289da)
      embedVar2.set_thumbnail(url=avatar)
      embedVar2.add_field(name="`STEALS`", value="**FLOG**- Steal Opponent Attack and Add it to Your Attack by AP %\n\n**WITHER**- Steal Opponent Defense and Add it to Your Defense by AP %\n\n**LIFE**\n**Title, Arm, Card Passive Effect:** Steal Opponent Health and Add it to your Max Health by AP %\n**Card Active Enhancer Effect:** Steal Opponent Health and Add it to your Current Health by Flat AP + 9% of Opponent Current Health. \n\n**DRAIN** - Steal Opponent Stamina and Add it to your Stamina by Flat AP\n\n")
      embedVar2.set_footer(text=f"/help - Bot Help")

      embedVar3 = discord.Embed(title= f"Enhancer Type: Sacrifice",colour=0x7289da)
      embedVar3.set_thumbnail(url=avatar)
      embedVar3.add_field(name="`SACRIFICE`", value="**RAGE** - Decrease Your Defense by AP %, Increase All Moves AP by Amount of Decreased Defense\n\n**BRACE** - Decrease Your Attack by AP %, Increase All Moves AP By Amount of Decreased Attack\n\n**BZRK** - Decrease Your Current Health by AP %,  Increase Your Attack by Amount of Decreased Health\n\n**CRYSTAL** - Decrease Your Health by AP %, Increase Your Defense by Amount of Decreased Health\n\n")
      embedVar3.set_footer(text=f"/help - Bot Help")

      embedVar4 = discord.Embed(title= f"Enhancer Type: Conversion",colour=0x7289da)
      embedVar4.set_thumbnail(url=avatar)
      embedVar4.add_field(name="`CONVERSION`", value="**STANCE** - Swap Your Attack and Defense, Increase Your Defense By Flat AP\n\n**CONFUSE** - Swap Opponenet Attack and Defense, Decrease Opponent Defense by Flat AP\n\n")
      embedVar4.set_footer(text=f"/help - Bot Help")

      embedVar5 = discord.Embed(title= f"Enhancer Type: Time Manipulation",colour=0x7289da)
      embedVar5.set_thumbnail(url=avatar)
      embedVar5.add_field(name="`TIME MANIPULATION`", value="**BLINK**  - Decrease Your Stamina by Flat AP, Increase Opponent Stamina by Flat AP\n\n**SLOW** - Increase Opponent Stamina, Decrease Your Stamina then Swap Stamina with Opponent\n\n**HASTE** - Increase your Stamina, Decrease Opponent Stamina then Swap Stamina with Opponent\n\n")
      embedVar5.set_footer(text=f"/help - Bot Help")

      embedVar6 = discord.Embed(title= f"Enhancer Type: Control",colour=0x7289da)
      embedVar6.set_thumbnail(url=avatar)
      embedVar6.add_field(name="`CONTROL`", value="**SOULCHAIN** - You and Your Opponent's Stamina Equal Flat AP\n\n**GAMBLE** - You and Your Opponent's Health Equal Flat AP\n\n")
      embedVar6.set_footer(text=f"/help - Bot Help")

      embedVar7 = discord.Embed(title= f"Enhancer Type: Fortitude",colour=0x7289da)
      embedVar7.set_thumbnail(url=avatar)
      embedVar7.add_field(name="`FORTITUDE`", value="**GROWTH**- Decrease Your Max Health by 10%, Increase Your Attack, Defense and all Moves AP by GROWTH AP\n\n**FEAR** - Decrease Your Max Health by 10%, Decrease Opponent Attack, Defense, and all moves AP by FEAR AP\n\n")
      embedVar7.set_footer(text=f"/help - Bot Help")

      embedVar8 = discord.Embed(title= f"Enhancer Type: Damage",colour=0x7289da)
      embedVar8.set_thumbnail(url=avatar)
      embedVar8.add_field(name="`DAMAGE`", value="**WAVE** - Deal Flat AP Damage to Opponent. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will deal 75% AP Damage.*\n\n**BLAST** - Deal Flat AP Damage to Opponent. AP Increases each turn.\n\n")
      embedVar8.set_footer(text=f"/help - Bot Help")

      embedVar9 = discord.Embed(title= f"Enhancer Type: Divinity",colour=0x7289da)
      embedVar9.set_thumbnail(url=avatar)
      embedVar9.add_field(name="`DIVINITY`", value="**CREATION** - Increase Max Health by Flat AP. AP Decreases each turn (Can Crit). *If used on turn that is divisible by 10 you will heal Health & Max Health for 75% AP.*\n\n**DESTRUCTION** - Decrease Your Opponent Max Health by Flat AP (only opponent on PET use). AP Increases each turn.\n\n")
      embedVar9.set_footer(text=f"/help - Bot Help")
      
      embedVar10 = discord.Embed(title= f"Arm Enhancer Type: Offensive",colour=0x7289da)
      embedVar10.set_thumbnail(url=avatar)
      embedVar10.add_field(name="`OFFENSE`", value="**BASIC** - Equip a new Basic Attack and Element \n\n**SPECIAL** - Equip a new Special Attack and Element \n\n**ULTIMATE** - Equip a new Ultimate Attack and Element \n\n**ULTIMAX** - Increase **ALL** Attack Move Ability Power by Value \n\n**MANA** - Increase 🦠 Enhancer Ability Power by Percentage \n\n💉 **SIPHON** - Heal for 10% DMG + AP\n\n")
      embedVar10.set_footer(text=f"/help - Bot Help")
      
      embedVar11 = discord.Embed(title= f"Arm Enhancer Type: Defensive",colour=0x7289da)
      embedVar11.set_thumbnail(url=avatar)
      embedVar11.add_field(name="`DEFENSE`", value="🌐 **SHIELD**- Grant Damage absorbing Shield until destroyed \n\n💠 **BARRIER** - Blocks all Attack Damage until player Attacks or is Destoyed (Enhancers Exempt)\n\n🔄 **PARRY** - Reflects 25% Damage back to Attacker\n\n")
      embedVar11.set_footer(text=f"/help - Bot Help")
      

      embeds = [embedVar1, embedVar2, embedVar3, embedVar4, embedVar5, embedVar6, embedVar7, embedVar8, embedVar9, embedVar10, embedVar11]
      await Paginator(bot=bot, ctx=ctx, pages=embeds, timeout=60).run()
      
   
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
            await ctx.send("Hmm something ain't right. Check with support.", hidden=True)
            return


# @slash.slash(description="Anime VS+ Manual", guild_ids=guild_ids)
async def animevs(ctx):
   avatar="https://res.cloudinary.com/dkcmq8o15/image/upload/v1620496215/PCG%20LOGOS%20AND%20RESOURCES/Legend.png"


   embedVar1 = discord.Embed(title= f"About Anime VS+",colour=0x7289da)
   embedVar1.set_thumbnail(url=avatar)
   embedVar1.add_field(name="**About The Game!**", value=textwrap.dedent(f"""\
      
   **Anime VS+** is a Multiplatform Card Game exploring **Universes** from your favorite Video Game and Anime Series!

   Explore Tales, Dungeons, and Bosses! Play **Solo**, or with **Friends**!
   
   Customize your experince by setting your personal /difficulty!
   """))

   embedVar2 = discord.Embed(title= f"Getting Started", description=textwrap.dedent(f"""\
   Players begin with 3 cards from the **Starter Universes**.
   
   The Title **Starter** and the Arm **Stock** are equipped.
   
   Your first Summon **Chick** will be joining as well!
      
   Play **Single Player** and **Multiplayer** Modes to earn :coin:
   Buy and equip better Items to Conquer the Multiverse!
   """), colour=0x7289da)
   embedVar2.set_thumbnail(url=avatar)

   embedVar3 = discord.Embed(title= f"Card Mechanics", description=textwrap.dedent(f"""\
   **Card Stats** 
   Health (**HLT**) Stamina (**STAM**) Attack (**ATK**) Defense(**DEF**)

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
   
   **Damage Type**
   Attacks have bonus effects based on the 🔅Element Type
   Use /help to find information on **Elements**
   
   **Enhancer**
   Enhancers either boost your stats or inflict status effects on your opponent. Use **/enhancers** for full list of Enhancers and their effects.
   🦠 Enhancer _uses 20 stamina_
   
   **Block**
   Doubles Defense for 1 turn
   🛡️ _uses 20 stamina_ 
   """), colour=0x7289da)
   embedVar3.set_thumbnail(url=avatar)
   
   embedVar11 = discord.Embed(title= f"Card Types", description=textwrap.dedent(f"""                                                                           
   🎴 **Universe Cards** - Purchasable in the **Shop** and Drops in **Tales**
   🃏 **Card Skins** - Craftable in the **Craft**
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
   Cards Start at **Level 0** and Max out at **Level 999**

   ✨ **Destinies**
   Card Specific Quest that earn **Destiny Cards**
   
   🃏 **Skins**
   Card Skins have different stats and abilities but can complete the main card **Destinies** !
 
   """), colour=0x7289da)
   embedVar11.set_thumbnail(url=avatar)
   
   embedVar17 = discord.Embed(title= f"Damage, Elements & Talismans", description=textwrap.dedent(f"""                                                                           
   🗯️**Engagement** Each of you Attack Moves deals damage based on the *Engagement**.
   
   💢: **Desperate Engagement**: Your opponent has overwhelming defense... Deal %33-%50 of AP
   ❕: **Brave Engagement**: Your opponent's defense is strong. Deal %50-%75 AP
   ‼️: **Nuetral Engagement**: Your attack and defense are nuetral. Deal %75-%120 AP
   〽️x1.5: **Aggressive Engagement**: Your attacks deal additional damage. Deal %120-%150 AP
   ❌x2: **Lethal Engagement**: Your attacks are lethal! Deal $150-%200 AP
   
   The Engagement is a factor of Attack + Move Ap vs Opponent Defense
   When your attack is higher than your oppoenents defense you will deal more damage
   
   🧮**Strike Calculation** Strike calcalation adds variance and balance to Engagements.
   Your ability also deals damage based on the type of **Strike**
   :palm_down_hand: **Miss** - You completely miss... No Damage
   :anger: **Chip** - You barely strike. 30% Damage Reduction
   :bangbang: **Connects** - Your ability strikes. No Reduction
   :anger_right: **Hits** - Land a significant Strike. 20% Increase
   :boom: **Critical Hit** - You land a lethal blow. 250% Increase
   
   **🔅 Elements**
   Each of your Card moves inflicts elemnental damage.

   👊 Physical - If ST(stamina) greater than 80, Deals double Damage 
   
   🔥 Fire - Does 25% damage of previous attack over the next opponent turns, stacks.
   
   ❄️ Ice - After 2 uses opponent freezes and loses 1 turn.
   💧 Water - Increases all water attack dmg by 40 Flat.
   ⛰️ Earth - Cannot be Parried. Increases Def by 25% AP.
   ⚡️ Electric- Add 15% to Shock damage, added to all attacks.
   🌪️ Wind - Cannot Miss, boosts all wind damage by 15% of damage dealt.
   
   🔮 Psychic - Penetrates Barriers. Reduce opponent ATK & DEF by 15% AP.
   
   ☠️ Death - Deals 20% opponent max health as damage.
   ❤️‍🔥 Life - Heal for 20% AP.
   🌕 Light - Regain 50% Stamina Cost, Increases ATK by 20% of DMG.
   
   ♠️ Dark- Penetrates shields & decreases opponent stamina by 15.
   🧪 Poison - Penetrates shields, Poison 30 damage stacking up to 600.
   
   🏹 Ranged - If ST(stamina) greater than 30, Deals 1.7x Damage 
   💙 Spirit - Has higher chance of Crit.
   ♻️ Recoil - Deals 60% damage back to you while dealing significantly more damage to opponent. If Recoild would kill you reduce HP to 1
   
   ⌛ Time - If ST is less than 80, You Block and Focus for 1 Turn. 
   🅱️ Bleed - After 3 Attacks deal 10x turn count damage to opponent.
   
   🪐 Gravity - Disables Opponent Block and Reduce opponent DEF by 25% AP.
   
   📿**Talismans**
 
   """), colour=0x7289da)
   embedVar17.set_thumbnail(url=avatar)

   embedVar4 = discord.Embed(title= f"Titles, Arms, and Summons ", description=textwrap.dedent(f"""\
   **Titles** & **Arms** 
   Modify you or the Opponents **Stats** by applying **Enhancers** during battle.
   
   🎗️ **Title Exlusivity**
   **Titles** apply enhancers at the **start** of your turn or during **Focus State**
   ⚠️ Titles are only effective on cards from the same Universe or Unbound!
   Buy **Titles** and **Arms** with :coin: or Earn them via **Drops**
   
   🦾 **Arm Durability**
   Arms are effective across the Multiverse, however they do break! Turning into **Gems**
   ⚠️ Arms from a different universe will break at a faster rate!
   Stock up on **Asrms** and repair **Durability** in the **/blacksmith**
   🪔 Elemental Arms also provide **Essence**. Use **Essence** to craft **Talismans**

   👑 **Universe Buff** :Match Your Titles and Arms to your **Card Universe**.
   **Buff**: **Base Stats** + 100 **HLT** , 20 **ATK** & 20 **DEF**.

   ✨ **Destiny Universe Buff** Destiny Cards gain an additional **Buff**.
   **Buff**: **Universe Buff** + 50 **HLT**, 5 **ATK** and 5 **DEF**.

   🧬 **Summons**
   Can assist during battle with an **Enhancer**.
   Earn **Summons** through Tales, Dungeon and Boss **Drops** or through trade with other Players!
   Battle with your **Summon** to gain **EXP** to increase Summon **Ability Power**. 

   Mix and Match Titles, Arms and Summons to gain the **Tactical Advantage**!
   """) ,colour=0x7289da)
   embedVar4.set_thumbnail(url=avatar)

   embedVar5 = discord.Embed(title= f"Battle Mechanics", description=textwrap.dedent(f"""\
   Players take turns dealing damage using one of their 5 **Abilities**.
   
   🌀 **Stamina** costs are standard across all Cards 
   _See Card Mechanics page for details_.
   
   ⚕️ **Recovery**
   When Players have used all of their **Stamina** they enter **Focus State**.

   The Match is over when a players **Health** reaches 0.
   """) ,colour=0x7289da)
   embedVar5.set_thumbnail(url=avatar)

   embedVar6 = discord.Embed(title= f"Focus & Resolve", description=textwrap.dedent(f"""\
   ⚕️ **Focus**
   Players can take advantage of **Focus State** to **Recover**.
   **Focus State** sacrifices a turn to Level Up Stats, increase **Stamina** to 90, and **Recover** some **Health**.
   
   ⚡**Resolve**
   Once in **Focus State** players can **Resolve**!
   **Resolved Characters** transform to greatly increase attack and health while sacrificing defense.
   **Resolved Characters** can call on Summons to aid them in battle.
   ⚡ Resolve _uses 1 turn_. You no longer stack focus Stats

   **Summon Assistance!**
   Summons Enhancers can either boost your stats or inflict status effects on your opponent. Summon moves do not end the player turn!
   🧬 Summon _uses 15 stamina_.

   """) ,colour=0x7289da)
   embedVar6.set_thumbnail(url=avatar)
   
   embedVar16 = discord.Embed(title= f"Difficulty & Progression", description=textwrap.dedent(f"""\
   ⚙️**Difficulty**
   Anime VS+ allows you to tailor your experience to your desired level.
   
   **3 Difficulties**
   **Easy** *Play the game freely and casually*
   - Lower Enemy Scaling
   - Bypass Abyss Requirements for Tales, Coop and Duo
   - No Destinies, Dungeons, Bosses, Drops, Raids or Abyss
   
   **Normal** *Play Anime VS+ the Intended Way*
   - Traverse the **/solo** to earn levels and unlock modes
   - Standard drop rates for items in game modes
   - Rebirth for increase in base stats and drop rates
   
   **Hard** *Not for the faint of Heart*
   - Normal Mode but with increasing scaling, drops and rewards
   - Clout
   
   🌑**Abyss** *Seasonal Ranking System*
   - Climb the Abyss each season for new Rewards!
   - 100 Floors with customized battles
   - Earn unqiue Abyssal build every 10 floors
   - Earn Title of God on completion of Floor 100
   
   🎊**Abyss Floor Unlocks**
   0 - Shop
   2 - Tales
   3 - Coop
   6 - PVP
   7 - Duo
   8 - Crafting
   9 - Guilds, Families and Associations
   10- Trading
   20 - Gifting
   25 - Explore Mode
   40 - Dungeons
   60 - Bosses
   100 - Boss Soul Exchange
   """),colour=0x7289da)
   embedVar16.set_thumbnail(url=avatar)

   embedVar7 = discord.Embed(title= f"Single Player", description=textwrap.dedent(f"""\
   **Single Player**
   
   👤 **Solo**/solo
   **Tales:** Single player adventures where you traverse through your favorite universes as characters from various worlds!
   **Dungeon:** Hard version of tales with better loot and better drop rates! (Unlocks after completing **Anime VS+ Tale**)
   **Boss:** End Game battles featuring Iconic Villians from Anime VS+ Universes. (Unlocks after completing **Anime VS+ Dungeon**)
   
   👥 **Duo**/duo *Beta*
   **Tales Deck(1-3):** Battle with your favorite AI preset in this Duo Tale!
   **Dungeon Deck(1-3):** Bring your strongest builds through the Darkest Duo Dungeons.
 
   🔮 **Anime VS+ Rifts**
   Mash-Up Universes featuring heroes and villians connected through common traits and themes!
   *Pay attention, Rifts will not stay open if you continue through your Tale!*
   """),colour=0x7289da)
   embedVar7.set_thumbnail(url=avatar)

   embedVar8 = discord.Embed(title= f"Multiplayer", description=textwrap.dedent(f"""\
   **Multiplayer**
   
   :people_hugging: **Co-Op**/coop *Beta*
   **Tales @partner:** Take a companion with your through your favorite tales with higher stakes!
   **Dungeon @partner:** Bring a companion through the darkest dungeons to earn awesome loot together.
   **Boss @partner:** Epic battles between two high level companions and one Incredible Boss.
   
   **Coop Mechanics**
   Coop Adds two new mechanics to gameplayer
   **Defending** - Your **Block** becomes **Defend** You will gain the **Block** bonus and take damage for your **Companion**
   **Assist** - Assist applies your enhancer to buff your **Companion**. *Damage dealing enhancers apply to enemy*

   🤼 **PVP**
   **/pvp @player:** Select your Build and Challenge any Anime VS+ Player to a quick match!
   
   🔮 **Anime VS+ Rifts**
   Anime VS+ Rifts are Co-Op Compatable and Helping other players in Co-Op **WILL NOT** close your open Rift!
   Grind Those Rifts Together!
   
   """),colour=0x7289da)
   embedVar8.set_thumbnail(url=avatar)

   embedVar9 = discord.Embed(title= f"Presets",description=textwrap.dedent(f"""\
   Save your favorite builds in your **Preset**
   **/menu** tselect **View Preset** option, select a preset with **1-3**
   *Select **Save Preset** to save a new Build!
   
   **Preset Builds**
   You can bring your preset builds into Duo Battles!
   """) ,colour=0x7289da)
   embedVar9.set_thumbnail(url=avatar)

   embedVar10 = discord.Embed(title= f"Economy",description=textwrap.dedent(f"""\
   **Shop**
   Use **/menu** to access the **Shop**!
   The shop sells Cards, Titles and Arms.

   **Trading**
   **/trade** will allow you to trade Cards, Titles, Arms and Summons with other players.
   Add items to the open trade using the buttons on the item menu *ex. /cards*
   **/tradecoins** allows you to add or remove coins from the trade
   
   **Resell**
   Sell Cards, Titles, and Arms back to the market for :coin:**Coins**.
   
   **Crafting**b
   **/menu** to **Start Crafting!** Craft **Card Skins**, **Summons**, and **Destinies**!

   **Dismantle**
   Dismantle Cards, Titles and Arms into :gem:**Gems**. and 🪔**Essense**
   
   **Universe Trinkets**
   Craftable Boost that increase the limits of your cards levels!
   💟 **Universe Heart** - will allow you to level cards past 200!
   🌹 **Universe Soul** - Grants 2x XP for all cards in Universe!
   
   **Blacksmith**
   **/menu** to purchase Card Levels, Arm Durability and **Storage**!
   
    👛 **Gabe's Purse** - will allow you to keep all items after a **Rebirth**
   
   **Currency**
   :coin: - Coins can be used to purchase Cards, Titles and Arms. You can use them to trade and sell items to other players!
   :gem: - When Arms break they turn into **Gems**, You can also dismantle items from your inventory into **Gems**! 
   **Gems** are universe specific items that can be crafted into Skins, Trinkets or **Destinies**
   
   """) ,colour=0x7289da)
   embedVar10.set_thumbnail(url=avatar)
   
   embedVar15 = discord.Embed(title= f"Guilds", description=textwrap.dedent(f"""\
   **Guilds Explained**
   Use **/guild** to lookup any Anime VS+ Guild!
   
   **Guild Members** earn extra :coin: towards the **Guild Bank** 

   **Creating A Guild**
   Use **/createguild** and create a **Guild Name**
   **/recruit** your friends to join your newly named **Guild** !
   Players can use **/apply** to join as well!
   
   **Guild Bonusus**
   Guildmates gain an extra **50 Attack** and **Defense** playing Co-Op Together !
   Guilds earn additional :coin: for every **Tales**, **Dungeon** and **Boss** Victory
   
   **Guild Economy**
   Players across **Anime VS+** can **/donate** :coin: to their favorite Guilds!
   Guild Owners can ****/pay**** their members a wage.
   """),colour=0x7289da)
   embedVar15.set_thumbnail(url=avatar)

   embedVar12 = discord.Embed(title= f"Families",description=textwrap.dedent(f"""\
   **Families Explained**
   Use **/family** to lookup any Anime VS+ Family!
   
   Two players with a strong bond can come together and form a **Family**
   
   **Starting A Family**
   Use **/marry** to start a marriage proposal to your chosen **Partner**
   If they accept, your will form a Household under your name
   **2 Kids** can be adopted into the family to create a 4 player Maximum.
   
   **Family Bonuses**
   Family Members gain an extra **100 Health** when playing Co-Op Together !
   Family Members earn extra :coin: towards the **Family Bank**.
   Families can /invest their income together.
   Heads of Household and Partners can pay **/allowance** to Family members. 
   
   **Housing**
   The **Family Bank** can be used to buy **Houses**
   **Houses** increase your :coin: earned via **Mutlipliers**
   **/invest** your income to buy bigger **Houses** and earn more :coin: across the game.
   """) ,colour=0x7289da)
   embedVar12.set_thumbnail(url=avatar)

   embedVar13 = discord.Embed(title= f"Associations",description=textwrap.dedent(f"""\
   **Association Explained**
   Associations in Anime VS+ are formed by an Oath between two Guild Owners
   
   The Oathgiver becomes the **Founder** and the Oathreciever becomes the ****Sworn and Shield****.
   
   The **Shield** defends the Association from raiding players.
   
   Both teams become enlisted as **Swords** of the new **Association**
   Their respective members become **Blades**
   
   The Founder & Sworn may /ally with other Teams increasing the size and power of the Association.
   These are the **Owners** and can **/sponsor** other teams allied with the Association.
   
   **Associations** earn money by winning **PvP** matches, Income from **Universe Crest** and defending against **Raids**
   
   **Universe Crest** 
   When a member of a Association defeats a **Dungeon** or **Boss** they earn the **Universe Crest** from that Universe.
   This Crest will earn the Association **Passive Income** whenever someone goes into that universe in all servers!
   

   **Association Bonuses**
   Associations earn extra income towards the **Association Bank**
   Associations increase the earned income in **PvP**
   Associations can **/raid**
   Associations can earn passive income owning **Universe Crest**
   Associations can purchase **Halls**
   
   
   **Halls**
   The **Association Bank** can be used to purchase **Halls**
   **Halls** increase the Income earned to Associations via **Multipliers**
   **Halls** increase the income earned to **Blades** via **Splits**
   **Halls** increase the defense of the **Shield**
   **Halls** increase the **Bounty** cost to raid the **Association**
   """) ,colour=0x7289da)
   embedVar13.set_thumbnail(url=avatar)
   
   embedVar14 = discord.Embed(title= f"Raids",description=textwrap.dedent(f"""\
   **Raids Explained**
   Players aligned with a Association can use /raid to claim bounties from other guilds
   
   Victory claims the bounty and resets the Associations victory multiplier !
   
   Income from Raids is limited to the bounty offered from the Association.
   To take money from a **Association Bank** players must compete in PvP
   
   Raiding an Association is no easy feat and must be done **Without Summons**
   
   **Raid Benefits**
   Earn Large Bounties from guilds.
   Earn Wins for your Anime VS+ **Guild**
   
   **Shield  Defense Explained**
   The **Shield** has a big repsonsible to defend the **Association** from raids, earning income from **Challengers**.
   
   The **Shield** exist within the Association hall as the **Current Equipped Build** of the **Shield Player**.
   
   As the **Shield**, whenever your Avatar succesfully defends a raid you earn :coin:
   With each victory you will build a streak earning both respect and more :coin: via **Multipliers**.
   
   **Association Competition**
   However, many of **Blades** will covet this position and may /raid you themseleves triggering a **Title Match**
   The winner of this **Title MAtch** becomes the new **Shield** and must defend the 
   Occasionally the Founder or Sworn may /raid to start a Defense Test gauging the strength of their Chosen Shield
   host a /raid tournament within the Association to find a new champion or simply /knight one yourself
   
   
   **Shield Benefits**
   Earn income by defending your Association from raiders
   Guild has a 30% reduction in buff cost
   Earn respect by increasing the Association victory streak 
   
   """) ,colour=0x7289da)
   embedVar14.set_thumbnail(url=avatar)



   embeds = [embedVar1, embedVar2, embedVar3, embedVar11,embedVar17, embedVar4, embedVar5, embedVar6, embedVar16, embedVar7, embedVar8,embedVar9, embedVar10,embedVar15,embedVar12,embedVar13,embedVar14]
   await Paginator(bot=bot, ctx=ctx, pages=embeds, timeout=60).run()
  

@slash.slash(description="Rewards for voting", guild_ids=guild_ids)
async def voted(ctx):
   try:
      query = {'DID': str(ctx.author.id)}
      user = db.queryUser(query)
      vault = db.queryVault(query)
      gem_list = vault['GEMS']

      if user['VOTED']:
         await ctx.send("You've already received your voting rewards!")
         return
      else:
         auth_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk1NTcwNDkwMzE5ODcxMTgwOCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjQ5MDAyNDY0fQ.zNf3ECu2PBWVlfYlYH9YMy7PRb2P-sQFBGRkBp-DwUo'
         head = {'Authorization': 'Bearer ' + auth_token}
         
         response = requests.get(f"https://top.gg/api/bots/955704903198711808/check?userId={ctx.author.id}", headers=head)
         response_dict = json.loads(response.text)

         if response_dict['voted'] == 1:
            if gem_list:
               for universe in gem_list:
                  update_query = {
                     '$inc': {'GEMS.$[type].' + "GEMS": 500000}
                  }
                  filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
                  res = db.updateVault(query, update_query, filter_query)

            await crown_utilities.bless(int(500000), ctx.author.id)
            respond = db.updateUserNoFilter(query, {'$set': {'VOTED': True}})


            embedVar = discord.Embed(title=f"✅ Daily Voter Rewards!", description=textwrap.dedent(f"""\
            Thank you for voting, {ctx.author.mention}!
            
            **Daily Voter Earnings** 
            :coin: **{'{:,}'.format(500000)}**
            💎 **{'{:,}'.format(500000)}** *all craftable universes*
            """), colour=0xf1c40f)
            
            await ctx.send(embed=embedVar)

         else:
            embedVar = discord.Embed(title=f"❌ Daily Voter Rewards!", description=textwrap.dedent(f"""\
            You have not voted for Anime VS+ today, {ctx.author.mention}!

            To earn your voter rewards, [Vote for Anime VS+!](https://top.gg/bot/955704903198711808/vote)

            **What are the Daily Voter Rewards?** 
            :coin: **{'{:,}'.format(500000)}**
            💎 **{'{:,}'.format(500000)}**
            """), colour=0xf1c40f)
            
            await ctx.send(embed=embedVar)

   except Exception as e:
      print(e)


# async def retrieve_user_object(player_id):
#    response = await bot.fetch_user(player_id)
#    return response

@slash.slash(description="Register for Anime VS+", guild_ids=guild_ids)
async def register(ctx):
   reg_query = {'DID' : str(ctx.author.id)}
   applied = db.queryUser(reg_query)
   server_created = db.queryServer({"GNAME": str(ctx.author.guild)})
   if applied:
      vault_query = {'DID':str(ctx.author.id)}
      registered = db.queryVault(vault_query)
      if registered:
         await ctx.send(f"{ctx.author.mention} You already have a Anime VS+ Account!")
         return 
      else:
         await ctx.author.send(f"Previous Registration Failed...Lets try again!")
         await ctx.send(f"{ctx.author.mention} Previous Registration Failed...Lets try again!")
         r_response = applied
         disname = str(ctx.author)
   else:
      disname = str(ctx.author)
      name = disname.split("#",1)[0]
      summon_info = {'NAME': 'Chick', 'LVL': 1, 'EXP': 0, 'Heal': 5, 'TYPE': 'HLT', 'BOND': 0, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1638814575/Pets/CHICK.png"}
      family = db.createFamily(data.newFamily({'HEAD': str(disname), 'SUMMON': summon_info}), str(disname))
      update_summon = db.updateFamily({'HEAD': str(disname)}, {'$set' : {'SUMMON': summon_info}})
      user = {'DISNAME': disname, 'NAME': name, 'DID' : str(ctx.author.id), 'AVATAR': str(ctx.author.avatar_url), 'SERVER': str(ctx.author.guild), 'FAMILY': str(disname)}
      r_response = db.createUsers(data.newUser(user))

      if not server_created:
         create_server_query = {'GNAME': str(ctx.author.guild)}
         created_server = db.createServer(data.newServer(create_server_query))
         await asyncio.sleep(1)
         server_query = {'GNAME': str(ctx.author.guild)}
         update_server_query = {
            '$inc': {'SERVER_BALANCE': 1000},
            '$addToSet': {'SERVER_PLAYERS': str(ctx.author.id)}
         }
         updated_server = db.updateServer(server_query, update_server_query)


   if r_response:
      try:
         await ctx.send(f"🆕 Registration Started!\n{ctx.author.mention}, prepare to select a starting universe.")
         vault = db.createVault(data.newVault({'OWNER': str(ctx.author), 'DID' : str(ctx.author.id)}))
         await asyncio.sleep(2)
         await ctx.send(f"{ctx.author.mention}, your starting universe will give you 🎴 cards and 🎗️ 🦾 accessories from that universe to get you started on your journey!")
         await asyncio.sleep(2)
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

      try:
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
                  traitmessage = f"**{mytrait['EFFECT']}:** {mytrait['TRAIT']}"
               available = f"{crown_utilities.crest_dict[uni['TITLE']]}"
               
               tales_list = ", ".join(uni['CROWN_TALES'])

               embedVar = discord.Embed(title= f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
               **Select A Starting Universe, {ctx.author.mention}!**

               Selecting a Starter Universe will give you *3* 🎴 Cards, :reminder_ribbon: Titles, and :mechanical_arm: Arms to begin!
               
               :infinity: - Unique Universe Trait
               {traitmessage}
               """))
               embedVar.set_image(url=uni['PATH'])
               embedVar.set_footer(text="You can earn or purchase items after Abyss floor 0")
               universe_embed_list.append(embedVar)
               
         buttons = [
               manage_components.create_button(style=3, label="Select This Starter Universe", custom_id="Select")
            ]
         custom_action_row = manage_components.create_actionrow(*buttons)
         # custom_button = manage_components.create_button(style=3, label="Equip")

         async def custom_function(self, button_ctx):
            try:
               if button_ctx.author == ctx.author:
                  universe = str(button_ctx.origin_message.embeds[0].title)
                  user_info = db.queryUser({'DID':str(ctx.author.id)})
                  
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
                     
                     title_message = []
                     arm_message = []
                     card_message = []
                     gem_message = []
                     gem_info = {'UNIVERSE': str(universe), 'GEMS' : 1000, 'UNIVERSE_HEART' : False, 'UNIVERSE_SOUL' : False}
                     response = db.updateVaultNoFilter(vault_query, {'$addToSet' : {'GEMS' :gem_info }})
                     while count < 3:
                        selectable_titles = list(range(0, len(list(list_of_titles))))
                        for selected in selected_titles:
                           if selected in selectable_titles:
                              selectable_titles.remove(selected)
                        selection = random.choice(selectable_titles)
                        selected_titles.append(selection)
                        title = list_of_titles[selection]
                        response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})
                        title_message.append(f"**{title['TITLE']}**!")
                        #await button_ctx.send(f"You collected :reminder_ribbon: **{title['TITLE']}**.")
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
                        db.updateVaultNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 75}}})        
                        arm_message.append(f"**{arm}**!")                   
                        #await button_ctx.send(f"You collected :mechanical_arm: **{arm}**.")
                        count = count + 1
                        
                     list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION'] and x['AVAILABLE'] and x['NAME'] not in current_cards]
                     count = 0
                     selected_cards = [1000]
                     counter = 1
                     destiny_counter = 0
                     destiny_message = []
                     has_destiny=False
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

                        cresponse = db.updateVaultNoFilter(vault_query, {'$addToSet': {'CARDS': str(card_name)}})
                        cardname_list = []
                        if cresponse:
                           if card_name not in cardname_list:
                              update_query = {'$addToSet': {
                                    'CARD_LEVELS': {'CARD': str(card_name), 'LVL': 0, 'TIER': int(tier),
                                                   'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                              r = db.updateVaultNoFilter(vault_query, update_query)
                           cardname_list.append(card_name)
                           card_message.append(f"**{card_name}**!")
                           #await button_ctx.send(f"You collected 🎴 **{card_name}**!")

                           # Add Destiny
                           for destiny in d.destiny:
                              if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                                 destiny_counter = destiny_counter + 1
                                 db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
                                 has_destiny=True
                                 if counter > 0:
                                    destiny_message.append(f"**{destiny['NAME']}** : Earn 🎴 **{destiny['EARN']}**.!")
                                    counter = counter - 1
                                    # await button_ctx.send(
                                    #    f"✨**{destiny['NAME']}** addes to **/destinylist**.", hidden=True)
                        count = count + 1
                     title_drop_message_into_embded = "\n".join(title_message)
                     arm_drop_message_into_embded = "\n".join(arm_message)
                     card_drop_message_into_embded = "\n".join(card_message)
                     destiny_drop_message_into_embded = "\n".join(destiny_message)
                     embedVar = discord.Embed(title=f"**Welcome to Anime VS+**!",description=textwrap.dedent(f"""
                     **Let's get started** {ctx.author.mention}!
                     :one:**/build** with **{universe} Items**
                     
                     :two:**/menu** for **🎴Cards**, **:reminder_ribbon:Titles**, and **:mechanical_arm:Arms**!
                     
                     :three:**/solo** and select **:sos: The Tutorial**!
   
                     **The /help command is your ❤️ Friend!**
                     Use the /help to learn how to play Anime VS+!
                     """),colour=0x1abc9c)
                     embedVar.add_field(name=f"🎴 My Cards*/cards*", value=f"{card_drop_message_into_embded}", inline=True)
                     embedVar.add_field(name=f":reminder_ribbon: My Titles*/titles*", value=f"{title_drop_message_into_embded}", inline=True)
                     embedVar.add_field(name=f":mechanical_arm: My Arms*/arms*", value=f"{arm_drop_message_into_embded}", inline=True)
                     if has_destiny:
                        embedVar.add_field(name=f"✨ **Destinies***/destnies to view destinies*", value=f"{destiny_drop_message_into_embded}", inline=False)
                     embedVar.add_field(name=f":sos: Support!", value=f"[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)", inline=False)
                     embedVar.set_author(name=f"Registration Complete!", icon_url=user_info['AVATAR'])
                     embedVar.set_footer(text="📜Use /daily for Daily Reward and Quest\n🔥/difficulty - Change difficulty setting!",
                                 icon_url="https://cdn.discordapp.com/emojis/877233426770583563.gif?v=1")
                     #await button_ctx.send(f"Nice choice {ctx.author.mention}!\n\nCreate your first **Build**!\n**/cards** Select your 🎴  Card\n**/titles** Select your 🎗️ Title\n**/arms** Select your 🦾  Arm\n\nOnce you're done, run **/tutorial** to begin the **Tutorial Battle**! ⚔️")
                     await button_ctx.send(embed=embedVar)
                     await ctx.author.send(embed=embedVar)
                     await asyncio.sleep(3)

                     # embedVar = discord.Embed(title=f"**Welcome to Anime VS+**!", description=textwrap.dedent(f"""
                     # Welcome 🆕 {ctx.author.mention}!                                                                                           
                     
                     # Congrats on selecting your starting universe! **Now what?**

                     # **Let's get started playing the game!**
                     # **Step 1:** Use the /daily command right now for your daily reward!
                     # **Step 2:** Use /menu to open your list of **Cards**, **Titles**, and **Arms** and equip a card you just got!
                     # **Step 3:** Use /solo and select **tutorial** to learn how to play through battle!

                     # **The /help command is your ❤️ Friend!**
                     # Use the help command dropdown to learn how to play Anime VS+!

                     # **/difficulty** - Change difficulty setting! **You start on easy mode**

                     # [Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
                     # """), colour=0xe91e63)
                     # embedVar.set_footer(text="Changing your Discord Account Name or Numbers will break your Anime VS+ Account.")
                     # await ctx.author.send(embed=embedVar)
                     # await ctx.send(embed=embedVar)

                     self.stop = True
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
         
         await Paginator(bot=bot, ctx=ctx, disableAfterTimeout=True, timeout=5000, pages=universe_embed_list, customActionRow=[
            custom_action_row,
            custom_function,
         ]).run()
         
         #family = {'HEAD': disname, 'HOUSE': 'Cave', 'BANK' : 1000000, 'UNIVERSE': 'Unbound'}
         #new_family = db.createFamily(data.newFamily(family))

      except Exception as ex:
         user = str(ctx.author)
         query = {'DID': str(ctx.author.id)}
         response = db.deleteVault({'DID': str(ctx.author.id)})
         delete_user_resp = db.deleteUser(user)
         await ctx.author.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
         await ctx.send(f"{ctx.author.mention} your Registration was cancelled. You must interact before the timeout!")
         
      
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
      # await ctx.send(m.USER_HAS_REGISTERED, delete_after=5)
      
   else:
      await ctx.send(m.RESPONSE_NOT_DETECTED, delete_after=3)


@slash.slash(name="Rebirth", description="Rebirth for permanent buffs", guild_ids=guild_ids)
async def rebirth(ctx):
   query = {'DID': str(ctx.author.id)}
   user_is_validated = db.queryUser(query)
   if user_is_validated:
      rLevel = user_is_validated['REBIRTH']
      gabes_purse = user_is_validated['TOURNAMENT_WINS']
      if rLevel < 5:
         pursemessage = "You will lose all of your equipped and vaulted items."
         if gabes_purse == 1:
            pursemessage = ":purse: | Gabe's Purse Activated! All Items Will Be Retained!\n*You will not be able to select a new starting universe!*"
         rebirthCost = round(10000000 * (1 + (rLevel)))

         util_buttons = [
                manage_components.create_button(
                    style=ButtonStyle.blue,
                    label="Yes",
                    custom_id = "Y"
                ),
                manage_components.create_button(
                    style=ButtonStyle.red,
                    label="No",
                    custom_id = "N"
                )
            ]
         util_action_row = manage_components.create_actionrow(*util_buttons)
         components = [util_action_row]

         embedVar1 = discord.Embed(title= f":heart_on_fire:{user_is_validated['NAME']}'s Rebirth",colour=0x7289da)
         embedVar1.set_thumbnail(url=user_is_validated['AVATAR'])
         embedVar1.add_field(name=f"Rebirth Level: {user_is_validated['REBIRTH']}\nRebirth Cost: :coin:{'{:,}'.format(rebirthCost)}", value=textwrap.dedent(f"""\
         **Rebirth Effects**
         New Starting Deck
         Starting Summon Bond
         Increase Base ATK + 10
         Increase Base DEF + 10
         Increased :coin: drops + %10
         Increased Item Drop Rates + 50%
         Keep All Card Levels
         
         {pursemessage}
         
         *Rebirth is permanent and cannot be undone*
         """))
         accept = await ctx.send(embed=embedVar1, components=[util_action_row])

         def check(button_ctx):
               return button_ctx.author == ctx.author

         try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(bot, components=[util_action_row], timeout=120,check=check)
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
                              db.updateVaultNoFilter({"OWNER" : user_is_validated['DISNAME']}, {'$set': {'BALANCE' : 1000000}})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
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
                                       db.updateVaultNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                       message = f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                       await button_ctx.send(message)
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Charmander', 'TITLE': 'Reborn', 'ARM':'Reborn Stock'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")                              
                        elif rLevel == 1:
                           if gabes_purse == 1:
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              db.updateVaultNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
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

                           delete = db.deleteVault({'DID': user_is_validated['DISNAME']})
                           vault = db.createVault(data.newVault({'OWNER': user_is_validated['DISNAME'], 'DID': str(user_is_validated['DID']), 'GEMS': [], 'CARDS': ['Kirishima','Squirtle','Malphite'], 'TITLES': ['Reborn Soldier'], 'ARMS': [{'ARM': 'Deadgun', 'DUR': 999999}], 'DECK': [{'CARD': 'Kirishima', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}, {'CARD': 'Squirtle', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}, {'CARD': 'Malphite', 'TITLE': 'Reborn Soldier', 'ARM': 'Deadgun', 'PET': 'Chick'}], 'PETS' : [{'NAME': 'Chick', 'LVL': 3, 'EXP': 0, 'Heal': 10, 'TYPE': 'HLT', 'BOND': 2, 'BONDEXP': 0, 'PATH': "https://res.cloudinary.com/dkcmq8o15/image/upload/v1622307902/Pets/chick.jpg"}], 'CARD_LEVELS': card_level_list}))
                           if vault:
                              cardList = ['Squirtle', 'Malphite', 'Kirishima']
                              for card in cardList:
                                 for destiny in d.destiny:
                                    if card in destiny["USE_CARDS"]:
                                       db.updateVaultNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                       message = f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                       await button_ctx.send(message)
                              nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Malphite', 'TITLE': 'Reborn Soldier', 'ARM':'Deadgun'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                        elif rLevel == 2:
                           if gabes_purse == 1:
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              db.updateVaultNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
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
                                       db.updateVaultNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                       message = f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                       await button_ctx.send(message)
                              nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Mineta', 'TITLE': 'Reborn Legion', 'ARM':'Glaive'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                        elif rLevel == 3:
                           if gabes_purse == 1:
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              db.updateVaultNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
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
                                       db.updateVaultNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                       message = f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                       await button_ctx.send(message)
                              nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Clefairy', 'TITLE': 'Reborn King', 'ARM':'Kings Glaive'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
                        elif rLevel == 4:
                           if gabes_purse == 1:
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              db.updateVaultNoFilter({"DID" : user_is_validated['DID']}, {'$set': {'BALANCE' : 1000000}})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
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
                                       db.updateVaultNoFilter({'DID': user_is_validated['DID']},{'$addToSet':{'DESTINY': destiny}})
                                       message = f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault."
                                       await button_ctx.send(message)
                              nCard = db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CARD': 'Xayah And Rakan', 'TITLE': 'Reborn Legend', 'ARM':'Legendary Weapon'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PET': 'Chick'}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'CROWN_TALES': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'DUNGEONS': ['']}})
                              db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'BOSS_WINS': ['']}})
                              nRebirth = db.updateUserNoFilter(query, {'$inc': {'REBIRTH': 1 }})
                              await button_ctx.send(f":heart_on_fire: | You are now Rebirth Level: {user_is_validated['REBIRTH'] + 1}")
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
                                    traitmessage = f"**{mytrait['EFFECT']}:** {mytrait['TRAIT']}"
                                 available = f"{crown_utilities.crest_dict[uni['TITLE']]}"
                                 
                                 tales_list = ", ".join(uni['CROWN_TALES'])

                                 embedVar = discord.Embed(title= f"{uni['TITLE']}", description=textwrap.dedent(f"""                                                                                         
                                 **Select A Starting Universe, {ctx.author.mention}!**

                                 Selecting a Starter Universe will give you *3* 🎴 Cards, :reminder_ribbon: Titles, and :mechanical_arm: Arms to begin!
                                 
                                 :infinity: - Unique Universe Trait
                                 {traitmessage}
                                 """))
                                 embedVar.set_image(url=uni['PATH'])
                                 universe_embed_list.append(embedVar)
                                 
                           buttons = [
                                 manage_components.create_button(style=3, label="Select This Starter Universe", custom_id="Select")
                              ]
                           custom_action_row = manage_components.create_actionrow(*buttons)
                           # custom_button = manage_components.create_button(style=3, label="Equip")

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
                                          response = db.updateVaultNoFilter(vault_query,{'$addToSet':{'TITLES': str(title['TITLE'])}})
                                          await button_ctx.send(f":reminder_ribbon: **{title['TITLE']}**.")
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
                                          db.updateVaultNoFilter(vault_query,{'$addToSet':{'ARMS': {'ARM': str(arm), 'DUR': 75}}})                           
                                          await button_ctx.send(f":mechanical_arm: **{arm}**.")
                                          count = count + 1
                                          
                                       list_of_cards = [x for x in db.queryAllCardsBasedOnUniverse({'UNIVERSE': str(universe), 'TIER': {'$in': acceptable}}) if not x['EXCLUSIVE'] and not x['HAS_COLLECTION'] and x['AVAILABLE'] and x['NAME'] not in current_cards]
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

                                          cresponse = db.updateVaultNoFilter(vault_query, {'$addToSet': {'CARDS': str(card_name)}})
                                          if cresponse:
                                             if card_name not in owned_card_levels_list:
                                                update_query = {'$addToSet': {
                                                      'CARD_LEVELS': {'CARD': str(card_name), 'LVL': 0, 'TIER': int(tier),
                                                                     'EXP': 0, 'HLT': 0, 'ATK': 0, 'DEF': 0, 'AP': 0}}}
                                                r = db.updateVaultNoFilter(vault_query, update_query)

                                             await button_ctx.send(f"🎴 **{card_name}**!")

                                             # Add Destiny
                                             for destiny in d.destiny:
                                                if card_name in destiny["USE_CARDS"] and destiny['NAME'] not in owned_destinies:
                                                      db.updateVaultNoFilter(vault_query, {'$addToSet': {'DESTINY': destiny}})
                                                      await button_ctx.send(
                                                         f"**DESTINY AWAITS!**\n**{destiny['NAME']}** has been added to your vault.", hidden=True)
                                          count = count + 1
                                       await button_ctx.send(f"Nice choice {ctx.author.mention}!\n\nCreate your first **Build**!\n**/cards** Select your 🎴  Card\n**/titles** Select your 🎗️ Title\n**/arms** Select your 🦾  Arm\n\nOnce you're done, run **/tutorial** to begin the **Tutorial Battle**! ⚔️")
                                       self.stop = True
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
                                 await ctx.send("Rebirth Issue Seek support.")
                           await Paginator(bot=bot, ctx=ctx, disableAfterTimeout=True, pages=universe_embed_list, customActionRow=[
                              custom_action_row,
                              custom_function,
                           ]).run()
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
                           await ctx.send("Rebirth Issue Seek support.")
                     else:
                        await button_ctx.send(f"Not enough :coin:!\nYou need {'{:,}'.format(rebirthCost)} to Rebirth:angel:", delete_after=5)
                  else:
                     await button_ctx.send("No Vault:angel:", delete_after=5)
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
                  await ctx.send("Rebirth Issue Seek support.")
            elif button_ctx.custom_id == "N":
               await button_ctx.send(f":heart_on_fire: | Ahhhh...another time then?", delete_after=5)
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
            await ctx.send("Rebirth Issue Seek support.")
      else:
         await ctx.send(f"You are at full Rebirth\n:angel:Level: {user_is_validated['REBIRTH']} ", delete_after=5)


@bot.event
async def on_slash_command_error(ctx, ex):
   if isinstance(ex, commands.CommandOnCooldown): # Checks Cooldown
      remaining_time = str(datetime.timedelta(seconds=int(ex.retry_after)))
      msg = f'You have already used this command... Try again in {remaining_time} *hh:mm:ss*'
      await ctx.send(msg)


@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.channel.send("Hello 👋. **Anime VS+** uses / Slash commands! Use `/register` to get started or `/help` for additional assistance. Cheers!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.HTTPException):
      guild = bot.get_guild(guild_id)
      channel = guild.get_channel(guild_channel)
      await ctx.send(f"Anime VS+ has been Rate Limited")


@tasks.loop(hours=1)
async def called_once_a_day():
   guild = bot.get_guild(guild_id)
   channel = guild.get_channel(966810770987966484)

   message_channel = channel

   universes = db.queryAllUniverse()
   corruption = False

   for u in universes:
      if u['CORRUPTED']:
         corruption = True

   if corruption:
      update_query = {'$set': {'CORRUPTED': False, 'CORRUPTION_LEVEL': 0}}
      db.updateManyUniverses(update_query)
      message = "Corruption Hour has ended..."
   else:
      update_query = {'$set': {'CORRUPTED': True, 'CORRUPTION_LEVEL': 1}}
      db.updateManyUniverses(update_query)
      message = "Corruption Hour has started!"
   
   embedVar = discord.Embed(title= f"👾 {message}", description=textwrap.dedent(f"""
   👾 Corruption Hour

   During Corruption Hour defeat cards in solo, duo, or coop battle to earn 💎150,000 Craftable Gems!
   Earn 💎300,000 when playing on Hard difficulty!
   """))

   await message_channel.send(embed=embedVar)

@called_once_a_day.before_loop
async def before():
   await bot.wait_until_ready()
   print("Finished waiting")

called_once_a_day.start()


@slash.slash(name="Daily", description="Receive your daily reward and quests", guild_ids=guild_ids)
@commands.check(validate_user)
@commands.cooldown(1, 60*60*12, commands.BucketType.user)
async def daily(ctx):
   try:
      dailyamount = 1000000
      await crown_utilities.bless(dailyamount, ctx.author.id)
      query = {'DID': str(ctx.author.id)}
      user_data = db.queryUser(query)
      user_completed_tales = user_data['CROWN_TALES']
      universes = db.queryAllUniverse()
      if ctx.author.guild:
         server_query = {'GNAME': str(ctx.author.guild)}
         update_server_query = {
            '$inc': {'SERVER_BALANCE': 50000}
         }
         updated_server = db.updateServer(server_query, update_server_query)


      user_available_opponents = []


      for x in universes:
         user_available_opponents.append(x['CROWN_TALES'])

      opponents = [x for x in user_available_opponents for x in x]
      oppponent_len = len(opponents)
      q1 = random.randint(0, oppponent_len)
      q2 = random.randint(0, oppponent_len)
      q3 = random.randint(0, oppponent_len)

      q1_earn = round(random.randint(50000, 300000))
      q2_earn = round(random.randint(200000, 500000))
      q3_earn = round(random.randint(400000, 800000))

      quests = [{'OPPONENT': opponents[q1], 'TYPE': 'Tales', 'GOAL': 1, 'WINS': 0, 'REWARD': q1_earn },{'OPPONENT': opponents[q2], 'TYPE': 'Tales', 'GOAL': 2, 'WINS': 0, 'REWARD': q2_earn }, {'OPPONENT': opponents[q3], 'TYPE': 'Tales', 'GOAL': 3, 'WINS': 0, 'REWARD': q3_earn }]
      db.updateVaultNoFilter(query, {'$set': {'QUESTS': quests}})
      db.updateUserNoFilter(query, {'$set': {'BOSS_FOUGHT': False}})
      db.updateUserNoFilter(query, {'$set': {'VOTED': False}})
      
      embedVar = discord.Embed(title=f"☀️ Daily Rewards!", description=textwrap.dedent(f"""\
      Welcome back, {ctx.author.mention}!
      **Daily Earnings** 
      :coin: {'{:,}'.format(dailyamount)}
      
      📜 **New Quests**
      Defeat **{opponents[q1]}** to earn :coin: {'{:,}'.format(q1_earn)}
      Defeat **{opponents[q2]}** to earn :coin: {'{:,}'.format(q2_earn)}
      Defeat **{opponents[q3]}** to earn :coin: {'{:,}'.format(q3_earn)}
      Use **/menu** command to open Quests and complete your quests!

      Use **/voted** command to receive Daily voting rewards!

      [Support our Patreon for Rewards!](https://www.patreon.com/partychatgaming?fan_landing=true)
      [Vote for Anime VS+!](https://top.gg/bot/955704903198711808/vote)
      [Add Anime VS+ to your server!](https://discord.com/api/oauth2/authorize?client_id=955704903198711808&permissions=139586955344&scope=applications.commands%20bot)
      [Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
      """), colour=0xf1c40f)
      
      await ctx.send(embed=embedVar)
   
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
         'PLAYER': str(ctx.author),
         'type': type(ex).__name__,
         'message': str(ex),
         'trace': trace
      }))
      return

@bot.command()
@commands.check(validate_user)
async def servers(ctx):
   if ctx.author.guild_permissions.administrator == True:
      try:
         for server in bot.guilds:
            await ctx.send(server.name)
            print(server.name)
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
         
   else:
      await ctx.send("Admin only.")


# @bot.command()
# async def buc(ctx):
#    await bot._http.overwrite_application_command(int(bot.me.id), [])


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'Your Daily Reward is on cooldown! You can use it in {round(error.retry_after/3600)} hours!')


async def DM(ctx, user : User, m,  message=None):
    message = message or "This Message is sent via DM"
    await user.send(m)


@slash.slash(name="Gift", description="Give money to friend", guild_ids=guild_ids)
@commands.check(validate_user)
async def gift(ctx, player: User, amount: int):
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
      await ctx.send(f":coin:{amount} has been gifted to {user2.mention}.")
      return

@slash.slash(name="battlehistory", description="How much battle history do you want to see during battle? 2 - 6", guild_ids=guild_ids)
async def battlehistory(ctx, history: int):
   try:
      allowed = [2,3,4,5,6]
      if history not in allowed:
         await ctx.send("You must enter a number between 2 and 6 only. Try again.")
         return
      user_query = {"DID": str(ctx.author.id)}
      update_query = {"$set": {"BATTLE_HISTORY": history}}
      db.updateUserNoFilter(user_query, update_query)
      await ctx.send(f"You will now see up to {str(history)} history messages during battle.")
   except Exception as e:
      await ctx.send(e)



@slash.slash(name="Donate", description="Donate money to Guild", guild_ids=guild_ids)
@commands.check(validate_user)
async def donate(ctx, amount, guild = None):
   try:
      dteam = ""
      if guild:
         dteam = guild.lower()
      else:
         user_query = {"DID": str(ctx.author.id)}
         user = db.queryUser(user_query)
         dteam = user['TEAM'].lower()

      vault = db.queryVault({'DID': str(ctx.author.id)})
      balance = vault['BALANCE']
      gem_list = vault['GEMS']
      query = {'TEAM_NAME': str(dteam)}
      team_data = db.queryTeam(query)
      team_display_name = team_data['TEAM_DISPLAY_NAME']
      gem_bless = 0
      if team_data:
         if balance <= int(amount):
            await ctx.send("You do not have that amount to donate.")
         else:
            await crown_utilities.blessteam(int(amount), dteam)
            await crown_utilities.curse(int(amount), ctx.author.id)
            
            gem_bless = round(int(amount) * .10)
            if gem_list:
               for universe in gem_list:
                  query = {"DID": str(ctx.author.id)}
                  update_query = {
                     '$inc': {'GEMS.$[type].' + "GEMS": gem_bless}
                  }
                  filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
                  res = db.updateVault(query, update_query, filter_query)
               await ctx.send(f"**:coin:{amount}** has been gifted to **{team_display_name}**.\nYou earned **:gem:{gem_bless}** gems! *All Universes* ")
            else:
               await ctx.send(f"**:coin:{amount}** has been gifted to **{team_display_name}**.\n**Dismantle** *Items to earn Gems in return for Donations!*")
               
            
            return
      else:
         await ctx.send(f"Guild: {dteam} does not exist")
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



@slash.slash(name="Invest", description="Invest money in your Family", guild_ids=guild_ids)
@commands.check(validate_user)
async def invest(ctx, amount):
   user = db.queryUser({'DID': str(ctx.author.id)})
   family = db.queryFamily({'HEAD': user['FAMILY']})
   vault = db.queryVault({'DID': str(ctx.author.id)})
   balance = vault['BALANCE']
   if family:
      if balance <= int(amount):
         await ctx.send("You do not have that amount to invest.", hidden=True)
      else:
         await crown_utilities.blessfamily_Alt(int(amount), user['FAMILY'])
         await crown_utilities.curse(int(amount), ctx.author.id)
         await ctx.send(f"**:coin:{amount}** invested into **{user['NAME']}'s Family**.")
         return
   else:
      await ctx.send(f"Family does not exist")


@slash.slash(name="Pay", description="Pay a Guild Member", guild_ids=guild_ids)
@commands.check(validate_user)
async def pay(ctx, player: User, amount):
   try:
      user = db.queryUser({'DID': str(ctx.author.id)})
      team = db.queryTeam({'TEAM_NAME': user['TEAM'].lower()})
      access = False
      tax = round(.25 * int(amount))

      if user['TEAM'] == 'PCG':
         await ctx.send("You are not a part of a guild.")
         return

      if user['DISNAME'] == team['OWNER']:
         access = True

      if user['DISNAME'] in team['OFFICERS']:
         access = True
      
      if not access:
         await ctx.send("You must be owner or officer of guild to pay members. ")
         return
      
      if str(player) not in team['MEMBERS']:
         await ctx.send("You can only pay guild members. ")
         return


      icon = ":coin:"
      if int(amount) >= 500000:
         icon = ":money_with_wings:"
      elif int(amount) >=300000:
         icon = ":moneybag:"
      elif int(amount) >= 150000:
         icon = ":dollar:"

      taxicon = ":coin:"
      if int(amount) >= 500000:
         taxicon = ":money_with_wings:"
      elif int(amount) >=300000:
         taxicon = ":moneybag:"
      elif int(amount) >= 150000:
         taxicon = ":dollar:"

      balance = team['BANK']
      payment = round(int(amount) + int(tax))
      different = 0 
      if balance <= payment:
         difference = round(abs(balance - payment))
         await ctx.send(f"Your Guild does not have **{icon}{'{:,}'.format(int(payment))}**\n*Taxes & Fees:* **{taxicon}{'{:,}'.format(int(difference))}**")
      else:
         await crown_utilities.bless(int(amount), player.id)
         await crown_utilities.curseteam(int(payment), team['TEAM_NAME'])
         await ctx.send(f"{icon} **{'{:,}'.format(int(amount))}** has been paid to {player.mention}.\n*Taxes & Fees:* **{taxicon}{'{:,}'.format(int(tax))}**")
         transaction_message = f"{str(ctx.author)} paid {str(player)} {'{:,}'.format(int(amount))}."
         team_query = {'TEAM_NAME': team['TEAM_NAME']}
         new_value_query = {
               '$addToSet': {'TRANSACTIONS': transaction_message},
               }
         await db.updateTeam(team_query, new_value_query)
         return
   except:
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


@slash.slash(description="Promote, Demote, or Remove Guild Members", options=[
   create_option(
         name="player",
         description="Player to update",
         option_type=6,
         required=True
   ),

   create_option(
         name="operation",
         description="Operation to perform",
         option_type=3,
         required=True,
         choices=[
            create_choice(
               name="Promote",
               value="Promote"
            ),
            create_choice(
               name="Demote",
               value="Demote"
            ),
            create_choice(
               name="Remove",
               value="Remove"
            ),

         ]
   )
   ],
guild_ids=guild_ids)
@commands.check(validate_user)
async def guildoperations(ctx, player: User, operation: str):
   try:
      user = db.queryUser({'DID': str(ctx.author.id)})
      query = {'TEAM_NAME': user['TEAM'].lower()}
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

      if user['TEAM'] == 'PCG':
         await ctx.send("You are not a part of a guild.")
         return

      if str(player) not in team['MEMBERS']:
         await ctx.send("You can only utilize Guild Controls on Guild members.")
         return

      if operation == "Remove":
         await deletemember(ctx, player)
         return

      if user['DISNAME'] == team['OWNER']:
         access = True

      if user['DISNAME'] in team['OFFICERS']:
         access = True
        
      if not access:
         await ctx.send("You must be owner or officer of guild to promote members. ")
         return
      
      if str(player) == team_owner:
         await ctx.send("Guild Owners can not be promoted.")


      if str(player) in team_officers:
         is_officer = True
         if operation == "Promote":
            await ctx.send("You can not promote a guild member higher than an Officer position.")
            return
         elif operation == "Demote":
            transaction_message = f"{str(player)} was demoted to Captain"
            team_query = {
               '$pull': {'OFFICERS': str(player)},
               '$push': {'CAPTAINS': str(player)},
               '$addToSet': {'TRANSACTIONS': transaction_message}
            }
            update_message = f"{player.mention} has been demoted to a **Captain** of **{team['TEAM_DISPLAY_NAME']}**"


      if str(player) in team_captains:
         is_captain = True
         if operation == "Promote":
            transaction_message = f"{str(player)} was promoted to Officer"
            team_query = {
               '$pull': {'CAPTAINS': str(player)},
               '$push': {'OFFICERS': str(player)},
               '$addToSet': {'TRANSACTIONS': transaction_message}
            }
            update_message = f"{player.mention} has been promoted to an **Officer** of **{team['TEAM_DISPLAY_NAME']}**"
         elif operation == "Demote":
            transaction_message = f"{str(player)} was demoted to basic membership"
            team_query = {
               '$pull': {'CAPTAINS': str(player)},
               '$addToSet': {'TRANSACTIONS': transaction_message}
            }
            update_message = f"{player.mention} has been demoted to a **Member** of **{team['TEAM_DISPLAY_NAME']}**"
           

      if not is_captain and not is_officer and not is_owner:
         if operation == "Promote":
            transaction_message = f"{str(player)} was promoted to Captain"
            team_query = {
               '$push': {'CAPTAINS': str(player)},
               '$addToSet': {'TRANSACTIONS': transaction_message}
            }
            update_message = f"{player.mention} has been promoted to a **Captain** of **{team['TEAM_DISPLAY_NAME']}**"
         elif operation == "Demote":
            await ctx.send("Guild Members can not be demoted from basic membership.")
            return
        
      response = db.updateTeam(query, team_query)
      if response:
         await ctx.send(update_message)
         return
   except:
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


async def deletemember(ctx, member: User):
   owner_profile = db.queryUser({'DID': str(ctx.author.id)})
   team_profile = db.queryTeam({'TEAM_NAME': owner_profile['TEAM'].lower()})
   
   if team_profile:
      if owner_profile['DISNAME'] == team_profile['OWNER']:  
            team_buttons = [
               manage_components.create_button(
                  style=ButtonStyle.blue,
                  label="✔️",
                  custom_id="Yes"
               ),
               manage_components.create_button(
                  style=ButtonStyle.red,
                  label="❌",
                  custom_id="No"
               )
            ]
            transaction_message = f"{str(member)} was removed from guild."
            team_buttons_action_row = manage_components.create_actionrow(*team_buttons)
            await ctx.send(f"Do you want to remove {member.mention} from the **{team_profile['TEAM_DISPLAY_NAME']}**?".format(bot), components=[team_buttons_action_row])

            def check(button_ctx):
               return button_ctx.author == ctx.author

            try:
               button_ctx: ComponentContext = await manage_components.wait_for_component(bot, components=[team_buttons_action_row], check=check)
               
               if button_ctx.custom_id == "No":
                  await button_ctx.send("Member Not Deleted.")
                  return

               if button_ctx.custom_id == "Yes":    
                  team_query = {'TEAM_NAME': team_profile['TEAM_NAME']}
                  new_value_query = {
                        '$pull': {
                            'MEMBERS': str(member),
                            'OFFICERS': str(member),
                            'CAPTAINS': str(member),
                        },
                        '$inc': {'MEMBER_COUNT': -1},
                        '$push': {'TRANSACTIONS': transaction_message},
                        }
                  response = db.deleteTeamMember(team_query, new_value_query, str(member.id))
                  if response:
                     await button_ctx.send(f"{member.mention} has been removed from **{team_profile['TEAM_DISPLAY_NAME']}**")
            except:
               print("Guild not created. ")
      else:
            await ctx.send(m.OWNER_ONLY_COMMAND, delete_after=5)
   else:
      await ctx.send(m.TEAM_DOESNT_EXIST, delete_after=5)



@slash.slash(name="Traits", description="List of Universe Traits", guild_ids=guild_ids)
@commands.check(validate_user)
async def traits(ctx):
   try: 
      traits = ut.traits
      traitmessages = []
      for trait in traits:
         traitmessages.append(f"_{trait['NAME']}_\n**{trait['EFFECT']}**:\n{trait['TRAIT']}\n")

      embedVar = discord.Embed(title="Universe Traits", description="\n".join(traitmessages))

      await ctx.author.send(embed=embedVar)
      await ctx.send(f"{ctx.author.mention} Universe Trait list sent to you via DM!")
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
      await ctx.send("There's an issue with your Traits List. Check with support.", hidden=True)
      return


@slash.slash(name="Allowance", description="Gift Family member an allowance", guild_ids=guild_ids)
@commands.check(validate_user)
async def allowance(ctx, player: User, amount):
   user2 = player
   user = db.queryUser({'DID': str(ctx.author.id)})
   family = db.queryFamily({'HEAD' : user['FAMILY']})
   if user['FAMILY'] == 'PCG' or (user['FAMILY'] != user['DISNAME'] and user['DISNAME'] != family['PARTNER']):
      await ctx.send("You must be the Head of a Household or Partner to give allowance. ")
      return

   family = db.queryFamily({'HEAD': user['FAMILY']})
   kids = family['KIDS']

   if str(user2) not in family['KIDS'] and str(user2) not in family['PARTNER'] and str(user2) not in family['HEAD']:
      await ctx.send("You can only give allowance family members. ")
      return
   balance = family['BANK']
   if balance <= int(amount):
      await ctx.send("You do not have that amount saved.")
   else:
      await crown_utilities.bless(int(amount), user2.id)
      await crown_utilities.cursefamily(int(amount), family['HEAD'])
      await ctx.send(f":coin:{amount} has been gifted to {user2.mention}.")
      return


@slash.slash(name="Performance", description="Toggles Text Only Performance Mode", guild_ids=guild_ids)
async def performance(ctx):
   try:
      player = db.queryUser({"DID": str(ctx.author.id)})
      if not player["PERFORMANCE"]:
            await ctx.send(f"Entering Performance Mode :gear:")
            db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PERFORMANCE': True}})
            return
      if player["PERFORMANCE"]:
            await ctx.send(f"Exiting Performance Mode :gear:")
            db.updateUserNoFilter({'DID': str(ctx.author.id)}, {'$set': {'PERFORMANCE': False}})
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

async def buffshop(ctx, player, team):
   team_query = {'TEAM_NAME': team['TEAM_NAME']}
   guild_buff_available = team['GUILD_BUFF_AVAILABLE']
   team_member_count = len(team['MEMBERS'])
   balance = team['BANK']
   icon = "💳"
   shielding = team['SHIELDING']
   association = team['GUILD']
   shield_buff = False
   if shielding ==True and association != 'PCG':
      shield_buff = True

   if team_member_count <= 2:
      await ctx.send("Guilds must have at least **3** guild members to purchase Guild Buffs.")
      return

   if guild_buff_available:
      guild_buff_length = len(team['GUILD_BUFFS'])
      if guild_buff_length == 3:
         await ctx.send("Guilds may only have up to 3 Guild Buffs at one time, max.")
         return
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
   auto_buff_cost = 60000000 + war_tax
   if shield_buff:
      quest_buff_cost = round(quest_buff_cost * .60)
      rift_buff_cost = round(rift_buff_cost * .60)
      level_buff_cost = round(level_buff_cost * .60)
      stat_buff_cost = round(stat_buff_cost * .60)
      auto_buff_cost = round(auto_buff_cost * .60)
      shield_message = f":flags: **{association} Shield Discount** 30%"
   sell_buttons = [
         manage_components.create_button(
            style=ButtonStyle.green,
            label="🔋 1️⃣",
            custom_id="1"
         ),
         manage_components.create_button(
            style=ButtonStyle.blue,
            label="🔋 2️⃣",
            custom_id="2"
         ),
         manage_components.create_button(
            style=ButtonStyle.red,
            label="🔋 3️⃣",
            custom_id="3"
         ),
         manage_components.create_button(
            style=ButtonStyle.red,
            label="🔋 4️⃣",
            custom_id="4"
         ),
         manage_components.create_button(
            style=ButtonStyle.red,
            label="🔋 5️⃣",
            custom_id="5"
         ),

      ]

   utility_buttons = [
      manage_components.create_button(
         style=ButtonStyle.grey,
         label="Cancel",
         custom_id="cancel"
      )
   ]

   sell_buttons_action_row = manage_components.create_actionrow(*sell_buttons)
   utility_buttons_action_row = manage_components.create_actionrow(*utility_buttons)
   embedVar = discord.Embed(title=f":tickets: | **Buff Shop** - {icon}{'{:,}'.format(balance)} ", description=textwrap.dedent(f"""\
   Welcome {team['TEAM_DISPLAY_NAME']}!
   {war_message}
   {shield_message}
   🔋 1️⃣ **Quest Buff** for :money_with_wings: **{'{:,}'.format(quest_buff_cost)}**
   
   🔋 2️⃣ **Level Buff** for :money_with_wings: **{'{:,}'.format(level_buff_cost)}**

   🔋 3️⃣ **Stat Buff** for :money_with_wings: **{'{:,}'.format(stat_buff_cost)}**

   🔋 4️⃣ **Rift Buff** for :money_with_wings: **{'{:,}'.format(rift_buff_cost)}**

   🔋 5️⃣**Auto Battle Buff** for :money_with_wings: **{'{:,}'.format(auto_buff_cost)}**

   All Buffs are available for 100 uses.
   Auto Battle comes with 1000 uses.

   What would you like to buy?
   """), colour=0xf1c40f)
   msg = await ctx.send(embed=embedVar, components=[sell_buttons_action_row, utility_buttons_action_row])
   def check(button_ctx):
      return button_ctx.author == ctx.author

   try:
      button_ctx: ComponentContext = await manage_components.wait_for_component(bot, components=[sell_buttons_action_row, utility_buttons_action_row], timeout=120,check=check)
      uses = 100
      price = 0
      update_query = {}
      
      if button_ctx.custom_id == "cancel":
         await button_ctx.defer(ignore=True)
         await msg.edit(components=[])
         return

      if button_ctx.custom_id == "1":
         price = quest_buff_cost
         if price > balance:
            await button_ctx.send("Insufficent Balance.", hidden=True)
            await msg.edit(components=[])
            return

         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Quest'},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Quest Buff", 'GUILD_BUFFS': {'TYPE': 'Quest', 'USES': 100}}
         }
     
      if button_ctx.custom_id == "2":
         price = level_buff_cost
         if price > balance:
            await button_ctx.send("Insufficent Balance.", hidden=True)
            return

         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Level'},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Level Buff", 'GUILD_BUFFS': {'TYPE': 'Level', 'USES': 100}}
         }

      if button_ctx.custom_id == "3":
         price= stat_buff_cost
         if price > balance:
            await button_ctx.send("Insufficent Balance.", hidden=True)
            return

         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Stat'},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Stat Buff", 'GUILD_BUFFS': {'TYPE': 'Stat', 'USES': 100}}
         }

      if button_ctx.custom_id == "4":
         price= rift_buff_cost
         if price > balance:
            await button_ctx.send("Insufficent Balance.", hidden=True)
            return

         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Rift'},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Rift Buff", 'GUILD_BUFFS': {'TYPE': 'Rift', 'USES': 100}}
         }

      if button_ctx.custom_id == "5":
         price= auto_buff_cost
         if price > balance:
            await button_ctx.send("Insufficent Balance.", hidden=True)
            return

         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': 'Auto Battle'},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} purchased Auto Battle Buff", 'GUILD_BUFFS': {'TYPE': 'Auto Battle', 'USES': 1000}}
         }


      response = db.updateTeam(team_query, update_query)
      if response:
         await crown_utilities.curseteam(int(price), team['TEAM_NAME'])
         await button_ctx.send("Guild buff purchased successfuly.")
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



async def buffswap(ctx, player, team):
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
         manage_components.create_button(
            style=ButtonStyle.green,
            label=f"[{str(index)}] {buff['TYPE']}",
            custom_id=f"{str(index)}"
         )
      )
      guild_buff_msg.append(f"[{str(index)}] **{buff['TYPE']}** buff: {buff['USES']} uses left!")

   guild_buff_msg_joined = "\n".join(guild_buff_msg)

   buttons_action_row = manage_components.create_actionrow(*buttons)
   embedVar = discord.Embed(title=f"Swap Guild Buffs", description=textwrap.dedent(f"""\
   {guild_buff_msg_joined}

   """), colour=0xf1c40f)
   msg = await ctx.send(embed=embedVar, components=[buttons_action_row])
   def check(button_ctx):
      return button_ctx.author == ctx.author

   try:
      button_ctx: ComponentContext = await manage_components.wait_for_component(bot, components=[buttons_action_row], timeout=120,check=check)
      update_query = {}
      
      if button_ctx.custom_id == "cancel":
         await button_ctx.defer(ignore=True)
         await msg.edit(components=[])
         return

      if button_ctx.custom_id == "0":
         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[0]['TYPE']}"},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[0]['TYPE']} Buff"}
         }
     
      if button_ctx.custom_id == "1":
         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[1]['TYPE']}"},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[1]['TYPE']} Buff"}
         }

      if button_ctx.custom_id == "2":
         update_query = {
            '$set': {'GUILD_BUFF_AVAILABLE': True, 'ACTIVE_GUILD_BUFF': f"{guild_buffs[2]['TYPE']}"},
            '$push': {'TRANSACTIONS': f"{player['DISNAME']} swapped to {guild_buffs[2]['TYPE']} Buff"}
         }


      response = db.updateTeam(team_query, update_query)
      if response:
         await msg.edit(components=[])
         await button_ctx.send("Guild buff swapped successfuly.")
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


@slash.slash(name="Bounty", description="Set Association Bounty", guild_ids=guild_ids)
@commands.check(validate_user)
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
      await ctx.send(f"Association does not have that much :coin:", delete_after=5)
      return
   else:
      update_query = {"$set": {'BOUNTY': int(finalBount)}, '$inc': {'BANK' : int(negCurseAmount)}}
      db.updateGuildAlt(guild_query, update_query)
      await ctx.send(f"New {guild['GNAME']} Bounty: :yen: {'{:,}'.format(finalBount)}! Use /raid `Association`{guild['GNAME']} to claim the Bounty!")
      return


@slash.slash(name="Sponsor", description="Sponsor Guild with Association Funds", guild_ids=guild_ids)
@commands.check(validate_user)
async def sponsor(ctx, guild: str, amount):
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
      await ctx.send("Association does not have that much :coin:", delete_after=5)
      return

   if user['DID'] != founder and user['DID'] != sworn and user['DID'] != shield:
      await ctx.send(m.NOT_LEADER, delete_after=5)
      return

   team_name = team
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

   await crown_utilities.blessteam(int(amount), team_name)
   await crown_utilities.curseguild(int(amount), guild['GNAME'])
   await ctx.send(f"{guild_name} sponsored {team_name} :coin:{amount}!!!")
   return

@slash.slash(name="Difficulty", description="Change the difficulty setting of Anime VS+",
                    options=[
                        create_option(
                            name="mode",
                            description="Difficulty Level",
                            option_type=3,
                            required=True,
                            choices=[
                                # create_choice(
                                #     name="Auto Battler",
                                #     value="ATales"
                                # ),
                                create_choice(
                                    name="Normal",
                                    value="NORMAL"
                                ),
                                create_choice(
                                    name="Easy",
                                    value="EASY"
                                ),
                                create_choice(
                                    name="Hard",
                                    value="HARD"
                                )
                            ]
                        )
                    ]
        ,guild_ids=guild_ids)
@commands.check(validate_user)
async def difficulty(ctx, mode):
   try:
      player = db.queryUser({'DID': str(ctx.author.id)})
      query = {'DID': str(ctx.author.id)}
      update_query = {'$set': {'DIFFICULTY': mode}}
      response = db.updateUserNoFilter(query, update_query)
      if response:
         await ctx.send(f"{ctx.author.mention} has been updated to ⚙️ **{mode.lower()}** mode.")
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
      

@slash.slash(name="Fund", description="Fund Association From Guild Bank", guild_ids=guild_ids)
@commands.check(validate_user)
async def fund(ctx, amount):
   try:
      user = db.queryUser({'DID': str(ctx.author.id)})
      team = db.queryTeam({'TEAM_NAME': user['TEAM'].lower()})
      team_guild = team['GUILD']
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
         await ctx.send(f"{team_guild} has been funded :coin: {amount}.")
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
      print("Cannot find Association")


# @bot.command()
# @commands.check(validate_user)
# async def addDID(ctx):
#    if ctx.author.guild_permissions.administrator == True:
#       all_users = db.queryAllUsers()
#       for user in all_users:
#          disname = user['DISNAME']
#          did = user['DID']
#          response = db.updateVaultNoFilter({'OWNER': disname}, {'$set': {'DID': did}})
#       await ctx.send("All DIDs udpated in database collection VAULT.")
#    else:
#       await ctx.send("Fuck off.")


@bot.command()
@commands.check(validate_user)
async def blessall(ctx, amount: int):
   if ctx.author.guild_permissions.administrator == True:
      is_creator = db.queryUser({'DID': str(ctx.author.id)})['CREATOR']
      if is_creator:
         try:
            all_users = db.queryAllVault()
            for user in all_users:
               await crown_utilities.bless(amount, user['DID'])
            await ctx.send(f"All Anime VS+ Players have been blessed. 👑")
         except Exception as e:
            print(e)
      else:
         await ctx.send("Creator only command.", hidden=True)

   else:
      await ctx.send("Creator only command.", hidden=True)


@slash.slash(description="Create Code for Droppables", guild_ids=guild_ids)
@commands.check(validate_user)
async def createcode(ctx, code_input: str, coin:int, gems:int):
   if ctx.author.guild_permissions.administrator == True:
      is_creator = db.queryUser({'DID': str(ctx.author.id)})['CREATOR']
      if not is_creator:
         await ctx.send("Creator only command.", hidden=True)
         return
         
      code_exist = db.queryCodes({'CODE_INPUT': code_input})
      if code_exist:
         await ctx.send("Code already exist")
         return
      else:
         try:
            query = {
               'CODE_INPUT': code_input,
               'COIN': coin,
               'GEMS': gems,
               'AVAILABLE': True
            }
            response = db.createCode(data.newCode(query))
            await ctx.send(f"**{code_input}** Code has been created")
         except Exception as e:
            print(e)
   else:
      await ctx.send("Creator only command.", hidden=True)

@slash.slash(description="Input Codes", guild_ids=guild_ids)
@commands.check(validate_user)
async def code(ctx, code_input: str):
   try:
      query = {'DID': str(ctx.author.id)}
      user = db.queryUser(query)
      vault = db.queryVault(query)
      code = db.queryCodes({'CODE_INPUT': code_input})
      gem_list = vault['GEMS']
      if code and code['AVAILABLE']:
         coin = code['COIN']
         gems = code['GEMS']
         if code_input not in user['USED_CODES']:
            if gems != 0:
               if gem_list:
                  for universe in gem_list:
                     query = {'DID': str(ctx.author.id)}
                     update_query = {
                        '$inc': {'GEMS.$[type].' + "GEMS": gems}
                     }
                     filter_query = [{'type.' + "UNIVERSE": universe['UNIVERSE']}]
                     res = db.updateVault(query, update_query, filter_query)
                  await ctx.send(f"The gems in each of your craftable universes have increased by 💎 **{'{:,}'.format(gems)}**")
               else:
                  await ctx.send(f"{ctx.author.mention}, you do not have any universes that have gems to increase.")
                  return
            if coin != 0:
               await crown_utilities.bless(int(coin), ctx.author.id)
               await ctx.send(f"You've been rewarded :coin: **{'{:,}'.format(coin)}**.")
            respond = db.updateUserNoFilter(query, {'$addToSet': {'USED_CODES': code_input}})
         else:
            await ctx.send(f"**{code_input}** has already been used by {ctx.author.mention}")
            return
      else:
         await ctx.send(f'**{code_input}** is not a valid code.')
         return
   except:
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
      guild = bot.get_guild(guild_id)
      channel = guild.get_channel(guild_channel)
      await channel.send(f"'PLAYER': **{str(ctx.author)}**, TYPE: {type(ex).__name__}, MESSAGE: {str(ex)}, TRACE: {trace}")
      return

@slash.slash(description="admin only", guild_ids=guild_ids)
@commands.check(validate_user)
async def addfield(ctx, collection, new_field, field_type, password, key):
   if ctx.author.guild_permissions.administrator == True:
      
      if password != 'casper':  
         return await ctx.send("Admin Only")
      
      if key != '513':
         return await ctx.send("Admin Only")

      if field_type == 'string':
         field_type = "NULL"
      elif field_type == 'int':
         field_type = 6
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
            {"ELEMENT": "SPIRIT", "ESSENCE": 5000},
            {"ELEMENT": "RECOIL", "ESSENCE": 5000},
            {"ELEMENT": "TIME", "ESSENCE": 5000},
            {"ELEMENT": "BLEED", "ESSENCE": 5000},
            {"ELEMENT": "GRAVITY", "ESSENCE": 5000}
         ]
      
      elif field_type == 'blank_list':
         field_type = []

      elif field_type == 'bool':
         field_type = False

      if collection == 'cards':
         response = db.updateManyCards({'$set': {new_field: field_type}})
      elif collection == 'titles':
         response = db.updateManyTitles({'$set': {new_field: field_type}})
      elif collection == 'vaults':
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
         response = db.updateManyPets({'$set': {new_field: field_type}})
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
   else:
      print(m.ADMIN_ONLY_COMMAND)



# @slash.slash(description="Update Health of all characters by 1000", guild_ids=guild_ids)
# @commands.check(validate_user)
# async def updatehealth(ctx):
#    try:
#       all_cards = db.queryAllCards()
#       await ctx.send("Updating all card health by 1000...")
#       for card in all_cards:
#          card_name = card["NAME"]
#          card_hlt = int(card["HLT"])
#          new_hlt = int(card_hlt) - 4000
#          query = {
#             'NAME': card_name
#          }
#          update_query = {
#             '$set': {'HLT': int(new_hlt)}
#          }
#          db.updateCard(query, update_query)
#       await ctx.send("All Card Health has been increased.")
#       return
#    except Exception as ex:
#       trace = []
#       tb = ex.__traceback__
#       while tb is not None:
#          trace.append({
#                "filename": tb.tb_frame.f_code.co_filename,
#                "name": tb.tb_frame.f_code.co_name,
#                "lineno": tb.tb_lineno
#          })
#          tb = tb.tb_next
#       print(str({
#          'PLAYER': str(ctx.author),
#          'type': type(ex).__name__,
#          'message': str(ex),
#          'trace': trace
#       }))
#       return



# @bot.command()
# @commands.check(validate_user)
# async def updatedungeoncards(ctx):
#    if ctx.author.guild_permissions.administrator == True:
#       try:
#          all_cards = db.queryDungeonCards()
#          for card in all_cards:
#             query = {'NAME': str(card['NAME'])}
#             update_query = {
#                '$inc': {
#                   'HLT': 50,
#                   'ATK': 30,
#                   'DEF': 30,
#                }
#             }
#             r = db.updateCard(query, update_query)
#          await ctx.send("Dungeon Cards have been updated.")
#       except Exception as ex:
#          trace = []
#          tb = ex.__traceback__
#          while tb is not None:
#                trace.append({
#                   "filename": tb.tb_frame.f_code.co_filename,
#                   "name": tb.tb_frame.f_code.co_name,
#                   "lineno": tb.tb_lineno
#                })
#                tb = tb.tb_next
#          print(str({
#                'type': type(ex).__name__,
#                'message': str(ex),
#                'trace': trace
#          }))      
#    else:
#       await ctx.send("Admin only")

# @bot.command()
# @commands.check(validate_user)
# async def updatedestinycards(ctx):
#    if ctx.author.guild_permissions.administrator == True:
#       try:
#          all_cards = db.queryDestinyCards()
#          for card in all_cards:
#             query = {'NAME': str(card['NAME'])}
#             update_query = {
#                '$inc': {
#                   'HLT': 100,
#                   'ATK': 50,
#                   'DEF': 60,
#                }
#             }
#             r = db.updateCard(query, update_query)
#          await ctx.send("Destiny Cards have been udpated.")
#       except Exception as ex:
#          trace = []
#          tb = ex.__traceback__
#          while tb is not None:
#                trace.append({
#                   "filename": tb.tb_frame.f_code.co_filename,
#                   "name": tb.tb_frame.f_code.co_name,
#                   "lineno": tb.tb_lineno
#                })
#                tb = tb.tb_next
#          print(str({
#                'type': type(ex).__name__,
#                'message': str(ex),
#                'trace': trace
#          }))
#    else:
#       await ctx.send("Admin only")


# @bot.command()
# @commands.check(validate_user)
# async def elements(ctx):
#    try:
#       all_cards = db.queryAllCards()

#       for card in all_cards:
#          query = {"NAME": card['NAME']}
#          update_query1 = {"$set": {"MOVESET.0.ELEMENT": "FIRE"}}
#          update_query2 = {"$set": {"MOVESET.1.ELEMENT": "ELECTRIC"}}
#          update_query3 = {"$set": {"MOVESET.2.ELEMENT": "DARK"}}

#          db.updateCard(query, update_query1)
#          db.updateCard(query, update_query2)
#          db.updateCard(query, update_query3)
#    except:
#       print("errored out")


# @bot.command()
# @commands.check(validate_user)
# async def updatehealth(ctx):
#    try:
#       all_cards = db.queryAllCards()
#       await ctx.send("Updating all card health by 1000...")
#       for card in all_cards:
#          card_name = card["NAME"]
#          card_hlt = int(card["HLT"])
#          new_hlt = int(card_hlt) - 500
#          query = {
#             'NAME': card_name
#          }
#          update_query = {
#             '$set': {'HLT': int(new_hlt)}
#          }
#          db.updateCard(query, update_query)
#       await ctx.send("All Card Health has been increased.")
#       return
#    except Exception as ex:
#       trace = []
#       tb = ex.__traceback__
#       while tb is not None:
#          trace.append({
#                "filename": tb.tb_frame.f_code.co_filename,
#                "name": tb.tb_frame.f_code.co_name,
#                "lineno": tb.tb_lineno
#          })
#          tb = tb.tb_next
#       print(str({
#          'PLAYER': str(ctx.author),
#          'type': type(ex).__name__,
#          'message': str(ex),
#          'trace': trace
#       }))
#       return


# @slash.slash(name="Update", description="function to update stuff", guild_ids=guild_ids)
# async def update(ctx):
#    # Parameters
#    dont_update_enhancer = ["WAVE", "CREATION", "DESTRUCTION", "BLAST", "STAM", "BLINK", "SLOW", "HASTE", "CONFUSE", "STANCE", "GAMBLE", "SOULCHAIN"]
#    dont_update_passive = ["WAVE", "CREATION", "DESTRUCTION", "BLAST", "STAM", "BLINK", "SLOW", "HASTE", "CONFUSE", "STANCE", "GAMBLE", "SOULCHAIN", "ATK", "DEF", "HLT", "LIFE"]
#    universes = [
#       "League Of Legends",
#       "Attack On Titan",
#       "Naruto",
#       "Bleach",
#       "My Hero Academia",
#       "Dragon Ball Z",
#       "Demon Slayer",
#       "7ds",
#       "One Punch Man",
#       "God Of War",
#       "Unbound",
#       "Black Clover",
#       "Solo Leveling",
#       "Kanto Region",
#       "Digimon",
#       "Hoenn Region",
#       "Chainsawman",
#       "Crown Rift Madness",
#       "Crown Rift Slayers",
#       "Souls",
#       "Crown Rift Awakening",
#       "Death Note",
#       "Fate",
#       "Johto Region",
#       "Kalos Region",
#       "Sinnoh Region"
#    ]

#    # Card Update
#    try:
#       # Update Cards 1st
#       card_dump = db.queryAllCards()
#       card_list = []
#       for c in card_dump:
#          if c["UNIVERSE"] in universes:
#             card_list.append(c)

#       for card in card_list:
#          cardname = card["NAME"]
#          # Card Moveset
#          moveset = card["MOVESET"]
#          enhancer = moveset[3]
#          enhancer_name = list(enhancer.keys())[0]
#          enhancer_ap = list(enhancer.values())[0]
#          enhancer_type = list(enhancer.values())[2]

#          passive = card["PASS"][0]
#          passive_name = list(passive.keys())[0]
#          passive_ap = list(passive.values())[0]
#          passive_type = list(passive.values())[1]
#          new_passive_ap_value = 0
#          new_enhancer_ap_value = 0

#          # Card Universe
#          card_universe = db.queryUniverse({"TITLE": card["UNIVERSE"]})
#          card_tier = card_universe["TIER"]
#          if card_tier == 0:
#             card_tier = 9

#          # Card Enhancer and Passive update
#          if enhancer_type not in dont_update_enhancer:
#             if enhancer_ap >= 40 and enhancer_ap > 39:
#                if card_tier == 1:
#                   new_enhancer_ap_value = 15
#                if card_tier == 2:
#                   new_enhancer_ap_value = 20
#                if card_tier == 3:
#                   new_enhancer_ap_value = 25
#                if card_tier == 4:
#                   new_enhancer_ap_value = 35
#                if card_tier == 5:
#                   new_enhancer_ap_value = 40
#                if card_tier == 9:
#                   new_enhancer_ap_value = 23
#             elif enhancer_ap >= 30 and enhancer_ap < 39:
#                if card_tier == 1:
#                   new_enhancer_ap_value = 10
#                if card_tier == 2:
#                   new_enhancer_ap_value = 15
#                if card_tier == 3:
#                   new_enhancer_ap_value = 20
#                if card_tier == 4:
#                   new_enhancer_ap_value = 30
#                if card_tier == 5:
#                   new_enhancer_ap_value = 35
#                if card_tier == 9:
#                   new_enhancer_ap_value = 18
#             elif enhancer_ap >= 20 and enhancer_ap < 30:
#                if card_tier == 1:
#                   new_enhancer_ap_value = 5
#                if card_tier == 2:
#                   new_enhancer_ap_value = 10
#                if card_tier == 3:
#                   new_enhancer_ap_value = 15
#                if card_tier == 4:
#                   new_enhancer_ap_value = 20
#                if card_tier == 5:
#                   new_enhancer_ap_value = 25
#                if card_tier == 9:
#                   new_enhancer_ap_value = 13
#             elif enhancer_ap >= 0 and enhancer_ap < 20:
#                if card_tier == 1:
#                   new_enhancer_ap_value = 3
#                if card_tier == 2:
#                   new_enhancer_ap_value = 8
#                if card_tier == 3:
#                   new_enhancer_ap_value = 10
#                if card_tier == 4:
#                   new_enhancer_ap_value = 15
#                if card_tier == 5:
#                   new_enhancer_ap_value = 20
#                if card_tier == 9:
#                   new_enhancer_ap_value = 9

#             query = {"NAME": cardname}
#             update_query = {'$set': {'MOVESET.$[type].' + enhancer_name: new_enhancer_ap_value}}
#             filter_query = [{'type.' + enhancer_name: enhancer_ap}]
#             resp = db.updateCardWithFilter(query, update_query, filter_query)
#          if passive_type not in dont_update_passive:  
#             if passive_ap >= 40 and passive_ap > 39:
#                if card_tier == 1:
#                   new_passive_ap_value = 15
#                if card_tier == 2:
#                   new_passive_ap_value = 20
#                if card_tier == 3:
#                   new_passive_ap_value = 25
#                if card_tier == 4:
#                   new_passive_ap_value = 35
#                if card_tier == 5:
#                   new_passive_ap_value = 40
#                if card_tier == 9:
#                   new_passive_ap_value = 23
#             elif passive_ap >= 30 and passive_ap < 39:
#                if card_tier == 1:
#                   new_passive_ap_value = 10
#                if card_tier == 2:
#                   new_passive_ap_value = 15
#                if card_tier == 3:
#                   new_passive_ap_value = 20
#                if card_tier == 4:
#                   new_passive_ap_value = 30
#                if card_tier == 5:
#                   new_passive_ap_value = 35
#                if card_tier == 9:
#                   new_passive_ap_value = 18
#             elif passive_ap >= 20 and passive_ap < 30:
#                if card_tier == 1:
#                   new_passive_ap_value = 5
#                if card_tier == 2:
#                   new_passive_ap_value = 10
#                if card_tier == 3:
#                   new_passive_ap_value = 15
#                if card_tier == 4:
#                   new_passive_ap_value = 20
#                if card_tier == 5:
#                   new_passive_ap_value = 25
#                if card_tier == 9:
#                   new_passive_ap_value = 13
#             elif passive_ap >= 0 and passive_ap < 20:
#                if card_tier == 1:
#                   new_passive_ap_value = 3
#                if card_tier == 2:
#                   new_passive_ap_value = 8
#                if card_tier == 3:
#                   new_passive_ap_value = 10
#                if card_tier == 4:
#                   new_passive_ap_value = 15
#                if card_tier == 5:
#                   new_passive_ap_value = 20
#                if card_tier == 9:
#                   new_passive_ap_value = 9

#             query = {"NAME": cardname}
#             update_query = {'$set': {'PASSIVE.$[type].' + passive_name: new_passive_ap_value}}
#             filter_query = [{'type.' + passive_name: passive_ap}]
#             resp = db.updateCardWithFilter(query, update_query, filter_query)

#       print("Update Cards complete.")
#    except Exception as ex:
#         trace = []
#         tb = ex.__traceback__
#         while tb is not None:
#             trace.append({
#                 "filename": tb.tb_frame.f_code.co_filename,
#                 "name": tb.tb_frame.f_code.co_name,
#                 "lineno": tb.tb_lineno
#             })
#             tb = tb.tb_next
#         print(str({
#             'type': type(ex).__name__,
#             'message': str(ex),
#             'trace': trace
#         }))
#         pass

#    # Arm Update
#    try:
#       # Update Arms 1st
#       arm_dump = db.queryAllArms()
#       arm_list = []
#       for c in arm_dump:
#          if c["UNIVERSE"] in universes:
#             arm_list.append(c)
#       for arm in arm_list:
#          armname = arm["ARM"]

#          passive = arm["ABILITIES"][0]
#          passive_type = list(passive.keys())[0]
#          passive_ap = list(passive.values())[0]
#          new_passive_ap_value = 0

#          # Card Universe
#          card_universe = db.queryUniverse({"TITLE": arm["UNIVERSE"]})
#          card_tier = card_universe["TIER"]
#          if card_tier == 0:
#             card_tier = 9

#          if passive_type not in dont_update_passive:  
#             if passive_ap >= 40 and passive_ap > 39:
#                if card_tier == 1:
#                   new_passive_ap_value = 10
#                if card_tier == 2:
#                   new_passive_ap_value = 15
#                if card_tier == 3:
#                   new_passive_ap_value = 18
#                if card_tier == 4:
#                   new_passive_ap_value = 20
#                if card_tier == 5:
#                   new_passive_ap_value = 25
#                if card_tier == 9:
#                   new_passive_ap_value = 19
#             elif passive_ap >= 30 and passive_ap < 39:
#                if card_tier == 1:
#                   new_passive_ap_value = 8
#                if card_tier == 2:
#                   new_passive_ap_value = 13
#                if card_tier == 3:
#                   new_passive_ap_value = 18
#                if card_tier == 4:
#                   new_passive_ap_value = 27
#                if card_tier == 5:
#                   new_passive_ap_value = 30
#                if card_tier == 9:
#                   new_passive_ap_value = 17
#             elif passive_ap >= 20 and passive_ap < 30:
#                if card_tier == 1:
#                   new_passive_ap_value = 6
#                if card_tier == 2:
#                   new_passive_ap_value = 10
#                if card_tier == 3:
#                   new_passive_ap_value = 15
#                if card_tier == 4:
#                   new_passive_ap_value = 24
#                if card_tier == 5:
#                   new_passive_ap_value = 25
#                if card_tier == 9:
#                   new_passive_ap_value = 12
#             elif passive_ap >= 0 and passive_ap < 20:
#                if card_tier == 1:
#                   new_passive_ap_value = 3
#                if card_tier == 2:
#                   new_passive_ap_value = 8
#                if card_tier == 3:
#                   new_passive_ap_value = 10
#                if card_tier == 4:
#                   new_passive_ap_value = 18
#                if card_tier == 5:
#                   new_passive_ap_value = 20
#                if card_tier == 9:
#                   new_passive_ap_value = 9

#             query = {"ARM": armname}
#             update_query = {'$set': {'ABILITIES.$[type].' + passive_type: new_passive_ap_value}}
#             filter_query = [{'type.' + passive_type: passive_ap}]
#             resp = db.updateArmWithFilter(query, update_query, filter_query)
#       print("Update Arm complete.")
#    except Exception as ex:
#         trace = []
#         tb = ex.__traceback__
#         while tb is not None:
#             trace.append({
#                 "filename": tb.tb_frame.f_code.co_filename,
#                 "name": tb.tb_frame.f_code.co_name,
#                 "lineno": tb.tb_lineno
#             })
#             tb = tb.tb_next
#         print(str({
#             'type': type(ex).__name__,
#             'message': str(ex),
#             'trace': trace
#         }))
#         pass

#    # Title Update
#    try:
#       # Update Cards 1st
#       title_dump = db.queryAllTitles()
#       title_list = []
#       for c in title_dump:
#          if c["UNIVERSE"] in universes:
#             title_list.append(c)

#       for title in title_list:
#          titlename = title["TITLE"]

#          passive = title["ABILITIES"][0]
#          passive_type = list(passive.keys())[0]
#          passive_ap = list(passive.values())[0]
#          new_passive_ap_value = 0

#          # Card Universe
#          card_universe = db.queryUniverse({"TITLE": title["UNIVERSE"]})
#          card_tier = card_universe["TIER"]
#          if card_tier == 0:
#             card_tier = 9

#          if passive_type not in dont_update_passive:  
#             if passive_ap >= 40 and passive_ap > 39:
#                if card_tier == 1:
#                   new_passive_ap_value = 10
#                if card_tier == 2:
#                   new_passive_ap_value = 18
#                if card_tier == 3:
#                   new_passive_ap_value = 20
#                if card_tier == 4:
#                   new_passive_ap_value = 25
#                if card_tier == 5:
#                   new_passive_ap_value = 35
#                if card_tier == 9:
#                   new_passive_ap_value = 22
#             elif passive_ap >= 30 and passive_ap < 39:
#                if card_tier == 1:
#                   new_passive_ap_value = 8
#                if card_tier == 2:
#                   new_passive_ap_value = 15
#                if card_tier == 3:
#                   new_passive_ap_value = 18
#                if card_tier == 4:
#                   new_passive_ap_value = 28
#                if card_tier == 5:
#                   new_passive_ap_value = 32
#                if card_tier == 9:
#                   new_passive_ap_value = 19
#             elif passive_ap >= 20 and passive_ap < 30:
#                if card_tier == 1:
#                   new_passive_ap_value = 5
#                if card_tier == 2:
#                   new_passive_ap_value = 12
#                if card_tier == 3:
#                   new_passive_ap_value = 16
#                if card_tier == 4:
#                   new_passive_ap_value = 26
#                if card_tier == 5:
#                   new_passive_ap_value = 28
#                if card_tier == 9:
#                   new_passive_ap_value = 11
#             elif passive_ap >= 0 and passive_ap < 20:
#                if card_tier == 1:
#                   new_passive_ap_value = 3
#                if card_tier == 2:
#                   new_passive_ap_value = 8
#                if card_tier == 3:
#                   new_passive_ap_value = 10
#                if card_tier == 4:
#                   new_passive_ap_value = 14
#                if card_tier == 5:
#                   new_passive_ap_value = 20
#                if card_tier == 9:
#                   new_passive_ap_value = 9

#             query = {"TITLE": titlename}
#             update_query = {'$set': {'ABILITIES.$[type].' + passive_type: new_passive_ap_value}}
#             filter_query = [{'type.' + passive_type: passive_ap}]
#             resp = db.updateTitleWithFilter(query, update_query, filter_query)
#       print("Update Title complete.")
#    except Exception as ex:
#         trace = []
#         tb = ex.__traceback__
#         while tb is not None:
#             trace.append({
#                 "filename": tb.tb_frame.f_code.co_filename,
#                 "name": tb.tb_frame.f_code.co_name,
#                 "lineno": tb.tb_lineno
#             })
#             tb = tb.tb_next
#         print(str({
#             'type': type(ex).__name__,
#             'message': str(ex),
#             'trace': trace
#         }))
#         pass

# @slash.slash(name="Menu", description="Menu Options for things to do", guild_ids=guild_ids)
# @commands.check(validate_user)
# async def menu(ctx):
#    try:
#       response = db.queryAllMenu()
#       profile, story, pvp, objectives = "", "", "", ""
#       for menu in response:
#          if menu['NAME'] == "Profile":
#             profile = menu['PATH']
#          if menu['NAME'] == "Story":
#             story = menu['PATH']
#          if menu['NAME'] == "PVP":
#             pvp = menu['PATH']
#          if menu['NAME'] == "Objectives":
#             objectives = menu['PATH']

#       embedVar1 = discord.Embed(title= f"Story Mode", description="Journey through Universes to defeat powerful foes to unlock vast new worlds, tough boss fights, and new possibilities! Click arrow below to go to the next page!", colour=0x7289da)
#       embedVar1.set_image(url=story)
#       embedVar1.set_footer(text=f"use /animevs for additional assistance")

#       embedVar2 = discord.Embed(title= f"Profile Menu", description="View and Edit your Cards, Titles, Arms, and Summons to craft new Builds and strategies.", colour=0x7289da)
#       embedVar2.set_image(url=profile)
#       # embedVar2.add_field(name="Help Navigation", value="*First Page: :track_previous:|Prev Page: :rewind:|\nNext Page: :fast_forward:| Last Page: :track_next:*")
#       embedVar2.set_footer(text=f"use /animevs for additional assistance")

#       embedVar3 = discord.Embed(title= f"PVP Mode", description="Face off against friend or foe!", colour=0x7289da)
#       embedVar3.set_image(url=pvp)
#       # embedVar3.add_field(name="Help Navigation", value="*First Page: :track_previous:|Prev Page: :rewind:|\nNext Page: :fast_forward:| Last Page: :track_next:*")
#       embedVar3.set_footer(text=f"use /animevs for additional assistance")

#       embedVar4 = discord.Embed(title= f"TIPS", description="5 Primary Objectives of Anime VS+.", colour=0x7289da)
#       embedVar4.set_image(url=objectives)
#       # embedVar4.add_field(name="Help Navigation", value="*First Page: :track_previous:|Prev Page: :rewind:|\nNext Page: :fast_forward:| Last Page: :track_next:*")
#       embedVar4.set_footer(text=f"use /animevs for additional assistance")

#       paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
#       paginator.add_reaction('⏮️', "first")
#       paginator.add_reaction('⬅️', "back")
#       paginator.add_reaction('🔒', "lock")
#       paginator.add_reaction('➡️', "next")
#       paginator.add_reaction('⏭️', "last")
#       embeds = [embedVar1, embedVar3,embedVar2, embedVar4]
#       await paginator.run(embeds)

#    except Exception as e:
#       await ctx.send(f"Error has occurred: {e}")

if config('ENV') == "production":
   DISCORD_TOKEN = config('DISCORD_TOKEN')
else:
   DISCORD_TOKEN = config('NEW_TEST_DISCORD_TOKEN')

bot.run(DISCORD_TOKEN)