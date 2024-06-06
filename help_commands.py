import textwrap


CROWN_UNLIMITED_GAMES = textwrap.dedent(f"""\
**🆕How to Register, Delete, Lookup your account**
**/register**: 🆕 Register your account
**/deleteaccount**: Delete your account
**/player**: Lookup your account, or a friends
**/build**: View your current build, cards, titles, arms, talismans, summons and more

**PVE Game Modes**
**🆘 The Tutorial** - Learn Anime VS+ battle system
**⚔️ Tales** - Normal battle mode to earn cards, accessories and more
**🔥 Dungeon** - Hard battle mode to earn dungeon cards, dungeon accessories, and more
**📽️ Scenario Battle** - Battle through unique scenarios to earn Cards and Moves

**PVE**
**/play** - Battle through a variety of PVE modes
                                        
**PVP**
**/pvp** - Battle a rival in PVP mode

[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
""")


UNIVERSE_STUFF = textwrap.dedent(f"""\
**View Universes!**
**/universes** - View all available universe info including all available cards, accessories, and destinies

[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
""")


LEGEND = textwrap.dedent(f"""\
**Card Basics**
🀄 - **Card Tier** *1-7*
🔱 - **Card Level** *1-999*
🥋 - **Card Class**
❤️ - **Card Health** (HLT)
🌀 / ⚡ - **Card Stamina** (ST)
🗡️ - **Attack (ATK)** Blue Crystal 🟦
🛡️ - **Defense (DEF)** Red Crystal 🟥
🏃 - **Speed**
🩸 - Card Passive *Card Passive enhancers are applied each turn, passively.*

**Accessories & Summons**
⚠️ - Your title or arm does not match your universe
🎗️ - **Title accessory**  *Title enhancers are applied each turn, passively.*
🦾 - **Arm accessory** *Arm enhancers are applied passively throughout the duration of battle.*
📿 - **Talisman** *Equip Elemntal  Talismans to bypass opponent affinities*
🧬 - **Summon!** *Summons use Active Enhancers that are available during battle after you Resolve*

**Currency**
💰 - **Coins** *Buy items in the shop and blacksmith*
💎 - **Gems** *Craft universe hearts, souls, cards, and destiny lines!*
🪔 - **Essence** *Craft Elemental Talismans*

[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
""")


ELEMENTS_LIST = [
    "👊 Physical - If ST(stamina) greater than 80, Deals Bonus Damage. After 3 Strike gain a Parry\n",
    "🔥 Fire - Does 50% damage of previous attack over the next opponent turns, stacks.\n",
    "❄️ Ice - Every 2 attacks, opponent freezes and loses 1 turn.\n",
    "💧 Water - Increases all water move AP by 100 Flat.\n",
    "⛰️ Earth - Cannot be Parried. Grants Shield and Increases Def by 40% AP.\n",
    "🌩️ Electric- Add 10% DMG Dealt to Shock damage, added to all Move AP.\n",
    "🌪️ Wind - On Miss, Use Wind Attack, boosts all wind damage by 35% of damage dealt.\n",
    "🔮 Psychic - Penetrates Barriers. Reduce opponent ATK & DEF by 15% DMG. After 3 Hits Gain a Barrier\n",
    "☠️ Death - Deals 40% DMG to opponent max health. Gain Attack equal to that amount.\n",
    "❤️‍🔥 Life - Create Max Health and Heal for 35% DMG.\n",
    "🌕 Light - Regain 50% ST(Stamina) Cost, Illumination Increases ATK by 40% of DMG.\n",
    "🌑 Dark- Penetrates Shields, Barriers and Parries & decreases opponent ST(Stamina) by 15.\n",
    "🧪 Poison - Penetrates shields, Poison 40 damage stacking up to (150 * Card Tier).\n",
    "🏹 Ranged - If ST(stamina) greater than 30, Deals 1.7x Damage. Every 4 Ranged Attacks Increase Hit Chance by 5%\n",
    "🧿 Energy - Has higher 35% higher chance of Crit.\n",
    "♻️ Reckless - Deals Incredible Bonus Damage, take 40% as reckless at the cost of a turn to recover. If Reckless would kill you reduce HP to 1. reckless is buffed when resolved, but you take more damage as well.\n",
    "⌛ Time - Strong Block and Increase Turn Count by 3, If ST(Stamina) is < 50, Focus for 1 Turn and goes through and lowers opponent barriers and parrys.\n",
    "🅱️ Bleed - Every 2 Attacks deal (10x turn count + 5% Health) damage to opponent.\n",
    "🪐 Gravity - Disables Opponent Block, Reduce opponent DEF by 40% DMG, Decrease Turn Count By 3, goes through barrier and parry.\n"
]


ELEMENTS = textwrap.dedent(f"""\
**🔅 Elements**    
👊 Physical - If ST(stamina) greater than 80, Deals Bonus Damage. After 3 Strike gain a Parry

🔥 Fire - Does 50% damage of previous attack over the next opponent turns, stacks.

❄️ Ice - Every 2 attacks, opponent freezes and loses 1 turn.

💧 Water - Increases all water move AP by 100 Flat.

⛰️ Earth - Cannot be Parried. Grants Shield and Increases Def by 30% AP.

🌩️ Electric- Add 10% DMG Dealt to Shock damage, added to all Move AP.

🌪️ Wind - On Miss, Use Wind Attack, boosts all wind damage by 35% of damage dealt.

🔮 Psychic - Penetrates Barriers. Reduce opponent ATK & DEF by 15% DMG. After 3 Hits Gain a Barrier

☠️ Death - Deals 30% DMG to opponent max health. Gain Attack equal to that amount.

❤️‍🔥 Life - Create Max Health and Heal for 35% DMG.

🌕 Light - Regain 50% ST(Stamina) Cost, Illumination Increases ATK by 30% of DMG.

🌑 Dark- Penetrates Shields, Barriers and Parries & decreases opponent ST(Stamina) by 15.

🧪 Poison - Penetrates shields, Poison 30 damage stacking up to (150 * Card Tier).

🏹 Ranged - If ST(stamina) greater than 30, Deals 1.7x Damage. Every 4 Ranged Attacks Increase Hit Chance by 5%

🧿 Energy - Has higher 35% higher chance of Crit.

♻️ Reckless - Deals Incredible Bonus Damage, take 40% as reckless. If Reckless would kill you reduce HP to 1

⌛ Time - Strong Block and Increase Turn Count by 3, If ST(Stamina) is < 50, Focus for 1 Turn and lower opponent protections and goes through parry.

🅱️ Bleed - Every 2 Attacks deal (10x turn count + 5% Health) damage to opponent.

🪐 Gravity - Disables Opponent Block, Reduce opponent DEF by 50% DMG, Decrease Turn Count By 3, goes through barrier and parry.

[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
""")


BOT_COMMANDS = textwrap.dedent(f"""\
**Guild Commands**
**/guild** - Guild lookup, configurations, and apply for
**/guildoperations** - Guild operations
**/createguild** - Create guild 
**/disbandguild** - Delete guild
**/recruit** - Recruit player to your guild
**/leaveguild guild** - Leave Guild
**/pay** - Send Guild Members coin
**/donate** - Donate coin to Guild Bank


**Association Commands**
**/association** - Association lookup
**/oath** - Create Association/Reswear Association
**/disband** - Delete Association (Founder Only)
**/betray** - Leave Association (Sworn Only)
**/knight** - Set Association Shield to Player (Association Owners Only)
**/ally** - Add Guild To Association (Association Owners Only)
**/exile** - Kick Guild from Association (Association Owners Only)
**/renounce** - Leave Association (Guild Owner Only)
**/sponsor** - Send Guild coin (Association Owners Onlu)
**/fund** - Donate coin to Association Bank
**/bounty** - Set Association Bounty (Association Owners Only)
**/viewhall** - View Hall Information


**Family Commands**
**/family** - Family Menu
**/marry** - Invite User to join Family
**/divorce** - Ask for divorce from partner
**/adopt** - Adopt kid into family
**/disown** - Remove Kid From Family
**/leavefamily** - Leave from family (Kid Only)
**/allowance** - Send Family Members coin (Head/Partner Only)
**/invest** - Invest coin into family Bank
**/houses** - Show list of available houses
**/viewhouse** - View House Information

[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
""")


CTAP_COMMANDS = textwrap.dedent(f"""\
**Main Menu!⚒️**
**/menu** - Access your current build, cards, titles, arms, quests, and destinies. You can also open the shop and visit the blacksmith here!

**Reward Codes! ⌨️**
**/code** - Enter in codes to earn in-game rewards!

**Trade! 🎴 🎗️ 🦾**
**/trade** - Start a trade with a friend!
**/tradecoins** - Add 🪙 to your trade!

**Gift! 🪙**
**/gift** - Gift a friend some 🪙!

**Card Analysis! 🎴**
**/analysis** - View specific card statistics and optimal builds for that card

**Do you already know the card or accessories name?**
*If you already know what you want to equip / view, use the fast equip commands below to equip your item...*
*/equipcard*
*/equiparm*
*/equiptitle*
*/equipsummon*
------------------
*/view*

[Join the Anime VS+ Support Server](https://discord.gg/2JkCqcN3hB)
""")