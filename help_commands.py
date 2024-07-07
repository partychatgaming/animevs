import textwrap


CROWN_UNLIMITED_GAMES = textwrap.dedent(f"""\
__Account Management__
**/register**: 🆕 Register your account
**/deleteaccount**: Delete your account
**/player**: Lookup your account, or a friends
**/build**: View your current build, cards, titles, arms, talismans, summons and more
                                                                            
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

PVE_MODES = textwrap.dedent(f"""\
__PVP Commands__
**/play** - Battle through a variety of PVE modes
**/explore** - Toggle Explore mode                           

__PVE Game Modes__
**🆘 The Tutorial** - Learn Anime VS+ battle system
**⚡ Randomize** - Select and start a Random Game Mode Below
**🗺️ Adventure** - Enter a 2D universe to battle, loot and more
**⚔️ Tales** - Normal battle mode to earn cards, accessories and more
**👺 Dungeon** - Hard battle mode to earn dungeon cards, dungeon accessories, and more
**📽️ Scenario** - Battle through unique scenarios to earn Cards and Moves
**💀 Raid** - Battle through High Level scenarios to earn Mythical Cards and Moves
**🌌 Explore** - Random Encounter battles to earn rare cards and major rewards
                                          
[Join the Anime VS+ Support Server](https://discord.gg/pcn)                                          
""")

PVP_MODES = textwrap.dedent(f"""\
__PVP Game Modes__
**/pvp** - Battle a rival in PVP mode
*More PVP modes coming soon!*
                            
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

UNIVERSE_STUFF = textwrap.dedent(f"""\
__Universe Information__
**/universes** - View all available universe info including all available cards, accessories, and destinies

**/view** - Lookup/View all available game items.
                                 
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

CARD_LEGEND = textwrap.dedent(f"""\
__Card Basics__
🎴 - **Card**
♾️ - **Card Universe**
🀄 - **Card Tier** *1-10*
🔰/🔱/⚜️ - **Card Level**
🥋 - **Card Class**
❤️ - **Card Health** (HLT)
🌀 / ⚡ - **Card Stamina** (ST)
🗡️ - **Card Attack (ATK)** Blue Crystal 🟦
🛡️ - **Card Defense (DEF)** Red Crystal 🟥
🏃 - **Card Evasion** (EVASION)
                              
__Card Moveset__
💥 - **Card Basic** Attack
☄️ - **Card Special** Attack            
🏵️ - **Card Ultimate* Attack
🦠 - **Card Enhancer** Ability
                              
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

EQUIPMENT_LEGEND = textwrap.dedent(f"""\
__Equipment & Summons__
⚠️ - Your title or arm does not match your universe
🎗️ - **Title**  *Title effects are applied each turn, passively.*
🦾 - **Arm** *Arms grant new Attacks, Increased ability or grant protections.*
🧬 - **Summon** *Summons use Attacks or Protections during battle*
📿 - **Talisman** *Equip Elemntal  Talismans to bypass opponent affinities*
⚒️ - **Durability** *Durability of your arm or talisman, decreases with each use*
                                   
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

CURRENCY_LEGEND = textwrap.dedent(f"""\
__Currency Commands__
**/balance** - View your current balance and guild balance
**/gems** - View your current gems
**/essence** - View your current essence

**Currency**
💰 - **Coins** *Buy items in Marketplace or via trade.*
💎 - **Gems** *Craft Card levels and items in the Blacksmith*
🪔 - **Essence** *Craft Elemental Talismans*
                                  
 [Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")
      
ELEMENTS_LIST = [
    "👊 Physical - If ST(stamina) greater than 80, Deals Bonus Damage. After 3 Strike gain a Parry\n",
    "⚔️ Sword - Every 3rd attack will result in a Critical Strike that also increases Atack by 40% of damage dealt.\n",
    "🏹 Ranged - If ST(stamina) greater than 30, Deals 1.7x Damage. Every 3 Ranged Attacks Increase Hit Chance by 10%\n",
    "🔫 Gun - Goes through shields. Has a 40% chance to strike twice. Double striking lowers opponents defense by 35% of the current value.\n",
    "♻️ Reckless - Deals Incredible Bonus Damage, take 40% as reckless at the cost of a turn to recover. If Reckless would kill you reduce HP to 1. Reckless is buffed when resolved, but you take more damage as well.\n",
    "🔥 Fire - Does 50% damage of previous attack over the next opponent turns, burn effect bypasses shields and stacks.\n",
    "💧 Water - Each strike increases all water move AP by 100. Every 200 AP, gain a shield. Every 400 AP send a Tsunami Strike for True Damage.\n",
    "⛰️ Earth - Penetrates Parry. Increases Def by 25% AP. Grants Shield - Increase by 50% DMG.\n",
    "🌩️ Electric- Add 10% DMG Dealt to Shock damage, Shock damage amplifies all Move AP.\n",
    "🌪️ Wind - On Miss or Crit, boosts all wind damage by 50% of damage dealt.\n",
    "🌿 Nature - Saps Opponent ATK and DEF for 10% of Damage & heals Health and Max Health for that amount as well.\n",
    "❄️ Ice - Every 3rd attack, opponent freezes and loses 1 turn, and loses attack and defense equal to 50% of damage dealt.\n",
    "🅱️ Bleed - Penetrates Parry. Every 2 Attacks deal (10x turn count + 5% Health) damage to opponent.\n",
    "🧿 Energy - Has higher 35% higher chance of Crit. This crit hit goes through all protections\n",
    "🔮 Psychic - Penetrates Barriers. Reduce opponent ATK & DEF by 10% DMG. After 3 Hits Gain a Barrier\n",
    "💤 Sleep - Every 2nd attack adds a stack of Rest. Before Opponent focuses they must Rest, skipping their turn, for each stack of Rest. Opponent only takes sleep damage while Resting.\n",
    "☠️ Death - Deals 25% DMG to opponent max health. Gain Attack equal to that amount. Executes opponent if their health equals 10% of their base max health.\n",
    "❤️‍🔥 Life - Create Max Health and Heal for 40% DMG.\n",
    "🌕 Light - Increases ATK by 25% of DMG. 25% of DMG is stored and attacks the damages when they focus\n",
    "🌑 Dark- Penetrates all Protections & decreases opponent ST(Stamina) by 15.\n",
    "🧪 Poison - Penetrates Shields and Parry. Stacks Poison damage equal to 35% of damage done. Stacking up to 30% of opponent max health. The Opponent takes damage when they attack.\n",
    "🩻 Rot - Penetrates Shields and Parry. Stacks Rot damage equal to 15% of damage done stacking up to 20% of max health. The Opponent takes damage when they attack.\n",
    "⌛ Time - Strong Block and Increase Turn Count by 3, If ST(Stamina) is < 50, Focus for 1 Turn and goes through and lowers opponent barriers and parry and AP is increased by damage dealt * turn total / 100.\n",
    "🪐 Gravity - Disables Opponent Block, Reduce opponent DEF by 25% DMG, Decrease Turn Count By 3, goes through barrier and parry.\n",
    "🐲 Draconic - Draconic attacks can only be ULTIMATE or Summoned. Pentrates all protections. Combines the AP and Elemental Effects of your BASIC and SPECIAL attack into one powerful blow!.",

]

ELEMENTS = textwrap.dedent(f"""\
**🔅 Elements**    
👊 Physical - If ST(stamina) greater than 80, Deals Bonus Damage. After 3 Strike gain a Parry
                           
⚔️ Sword - Every 3rd attack will result in a Critical Strike that also increases Atack by 40% of damage dealt.
                           
🏹 Ranged - If ST(stamina) greater than 30, Deals 1.7x Damage. Every 3 Ranged Attacks Increase Hit Chance by 10%
                           
🔫 Gun - Penetrates Shield. Has a 40% chance to deal a double hit. Double striking lowers opponents defense by 35% of the current value.
                           
♻️ Reckless - Deals Incredible Bonus Damage, take 60% as reckless. If Reckless would kill you reduce HP to 1. After striking you enter a resting state, skipping your turn.

🔥 Fire - Does 50% damage of previous attack over the next opponent turns, burn effect bypasses shields and stacks.

❄️ Ice - Every 3 attacks, opponent freezes and loses 1 turn, and loses attack and defense equal to 50% of damage dealt.

💧 Water - Each strike increases all water move AP by 100. Every 200 AP, gain a shield. Every 400 AP send a Tsunami Strike for True Damage

⛰️ Earth - Cannot be Parried. Grants Shield and Increases Def by 30% AP.
                           
🌿 Nature - Saps Opponent ATK and DEF for 35% of Damage & heals Health and Max Health for that amount as well.

🌩️ Electric- Add 10% DMG Dealt to Shock damage, added to all Move AP.

🌪️ Wind - On Miss or Crit boosts all wind damage by 60% of damage dealt.

🔮 Psychic - Penetrates Barriers. Reduce opponent ATK & DEF by 15% DMG. After 3 Hits Gain a Barrier
                           
💤 Sleep - Every 2nd attack adds a stack of Rest. Before Opponent focuses they must Rest, skipping their turn, for each stack of Rest. Opponent only takes sleep damage while Resting.

☠️ Death - Deals 30% DMG to opponent max health. Gain Attack equal to that amount.

❤️‍🔥 Life - Steals 30% damage done health and max health from opponent.

🌕 Light - Increases ATK by 40% of DMG. 40% of DMG is stored and damages the opponent when they focus.

🌑 Dark- Penetrates Shields, Barriers and Parries & decreases opponent ST(Stamina) by 15.

🧪 Poison - Penetrates shields, stacks poison damage equal to 35% of damage done stacking up to 30% of max health. This damage hits the opponent when the opponent attacks.

🩻 Rot - Penetrates shields, stacks rot damage equal to 15% of damage done stacking up to 20% of max health. This damage hits the opponents max health when the opponent attacks.

🧿 Energy - Has higher 35% higher chance of Crit.

⌛ Time - Strong Block and Increase Turn Count by 3, If ST(Stamina) is < 50, Focus for 1 Turn and lower opponent protections and goes through parry.

🅱️ Bleed - Every 2 Attacks deal (10x turn count + 5% Health) damage to opponent.

🪐 Gravity - Disables Opponent Block, Reduce opponent DEF by 50% DMG, Decrease Turn Count By 3, goes through barrier and parry.
                           
🐲 Draconic - Draconic attacks can only be ULTIMATE or Summoned, combines the AP and Elemental Effects of your BASIC and SPECIAL attack into one powerful blow!.

[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

BOT_COMMANDS = textwrap.dedent(f"""\
__Guild Commands__
**/guild** - Guild lookup, configurations, and apply for
**/guildoperations** - Guild operations
**/createguild** - Create guild 
**/disbandguild** - Delete guild
**/recruit** - Recruit player to your guild
**/leaveguild guild** - Leave Guild
**/pay** - Send Guild Members coin
**/donate** - Donate coin to Guild Bank

[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

FAMILY_COMMANDS = textwrap.dedent(f"""\
__Family Commands__
**/family** - Family Menu
**/familyoperations** - Family Operations
**/allowance** - Send Family Members coin from Family Bank
**/invest** - Invest coin into family Bank

__House Commands__
**/houses** - Show list of available houses
**/viewhouse** - View House Information
**/buyhouse** - Buy a house from Family Bank
                   
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

ASSOCIATION_COMMANDS = textwrap.dedent(f"""\
__Association Commands__
**/association** - Association lookup
**/associatoinoperations** - Association Operations
**/sponsor** - Send Guild coin from Association Bank
**/fund** - Donate coin to Association Bank from Guild Bank
**/bounty** - Set Association Bounty
                                       
__Hall Commands__
**/halls** - Show list of available halls
**/viewhall** - View Hall Information
**/buyhall** - Buy a hall from Association Bank
                   
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

CTAP_COMMANDS = textwrap.dedent(f"""\
__Build Commands__
**/cards** - View your available cards
**/titles** - View your available titles
**/arms** - View your available arms
**/summons** - View your available summons
**/talismans** - View your available talismans
**/attune** - Attune elemental talismans from essence
                            
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

SHOP_COMMANDS = textwrap.dedent(f"""\
__Shop Commands__
**/marketplace** - View the online marketplace
**/blacksmith** - View the blacksmith               

[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

TRADE_COMMANDS = textwrap.dedent(f"""\
__Trade Commands__
**/trade** - Start a trade with a friend!
**/tradecoins** - Add 🪙 to your trade!              

__Gift__
**/gift** - Gift a friend some 🪙Coin!
                                 
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

REWARDS_COMMANDS = textwrap.dedent(f"""\
__Rewards Commands__
**/daily** - Claim your daily reward
**/vote** - Claim your voted reward

__Gacha Gacha! ⌨️__
**/code** - Enter in codes to earn in-game rewards!
**/roll** - Spend gold to open lootboxes!
                                   
[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")

OPTION_COMMANDS = textwrap.dedent(f"""\
__Game Options__
**/help** - View all help commands and manual
**/explore**  - Toggle Explore mode / universe
**/difficulty** - Change the difficulty of the game
**/autosave** - Toggle autosave on or off
**/battlehistory** - Update battle history length
**/battleview** - Toggle Opponent Stats in Battle

[Join the Anime VS+ Support Server](https://discord.gg/pcn)
""")