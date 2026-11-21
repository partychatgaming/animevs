"""Content of the /help guide.

Each topic is a list of pages; a page is (title, body markdown).  Pages are kept
well under Discord's 4000-character limit for one Components V2 message.
Numbers that the game uses (damage multipliers, stamina costs...) are read
from the code so the guide can't drift out of date.
"""
import textwrap

import crown_utilities
import damage
import help_commands as legacy

SUPPORT = "[Anime VS+ support server](https://discord.gg/pcn)"


def _d(text):
    return textwrap.dedent(text).strip()


def _class_emoji(name):
    try:
        return str(crown_utilities.class_emojis[name])
    except Exception:
        return "🥋"


# --------------------------------------------------------------------------- topics
def getting_started():
    return [
        ("Your first five minutes", _d(f"""
            Welcome to **Anime VS+**: collect characters from your favourite anime and games, build them up, and battle across the multiverse.

            **1. Make your account** · `/register`
            Pick your starting universe. You get starter cards, a title, an arm and your first summon.

            **2. Learn to fight** · `/play` → **🆘 Anime VS+ Tutorial**
            A guided battle against a training dummy. It walks you through every button, one task at a time.

            **3. Check your build** · `/build`
            Your equipped card, title, arm, summon and talisman in one place. Browse your collection with `/cards` and press **Equip** on the one you like.

            **4. Start your first run** · `/play` → **⚔️ Tales Run**
            A chain of battles in one universe. Win to earn cards, gear, coins and experience.

            **5. Come back every day** · `/daily`
            Free rewards, a Boss Arena key and new quests (`/quests`).
            """)),
        ("What to aim for", _d(f"""
            🎴 **Collect** · every universe has its own cards, titles, arms and summons. `/universes` shows what each one offers.

            📈 **Grow** · cards level up as they battle, which raises their stats and move power. Higher **tiers** (1–10) start stronger and unlock stronger class perks.

            🎒 **Gear up** · a title, an arm, a summon and a talisman all change how a fight plays. Matching gear to your card's universe gives an extra **Universe Buff**.

            🗺️ **Climb** · Tales → Dungeons (harder, better drops) → Scenarios → Raids. Pick a `/difficulty` that suits you: Easy for a relaxed game, Normal as intended, Hard for bigger rewards.

            🤝 **Play together** · join a guild (`/guild`), trade (`/trade`) and challenge rivals (`/pvp`).

            Stuck? Pick a topic from the menu below, or ask in the {SUPPORT}.
            """)),
    ]


def battles():
    return [
        ("The battle screen", _d("""
            Every battle is one message that updates each turn.

            **Start screen** · both fighters, the match number, your opponent's moves, and which of your attacks hit their weaknesses. Press **⚔️ Start**, **🤖 Auto Battle** (the game plays it out instantly), **💾 Save & Quit** or **End**.

            **The battle image**
            • **You are always on the left**, your opponent on the right.
            • A **glow** behind a fighter means it's their move.
            • **HP** (health) and **ST** (stamina) bars, **ATK** and **DEF**, plus small tags for active effects: guards, focus/resolve, burn, poison and more.
            • The pill at the top shows the **turn number**.

            **Under the image** · the last few things that happened (newest in normal text).

            **Buttons** · your moves, then Block / Resolve / Summon, then **⚙️ More**: your full kit, the opponent's gear, the longer battle log, **Save & Quit** and **Surrender** (it asks to confirm). Opening More never costs a turn.
            """)),
        ("Your turn: stamina and moves", _d("""
            Every action costs **stamina (ST)**. You start with 100.

            💥 **Basic** · 10 ST · a small attack with its element's effect
            ☄️ **Special** · 30 ST · a stronger attack
            🏵️ **Ultimate** · 80 ST · your biggest attack
            🦠 **Enhancer** · 20 ST · buff yourself or weaken them (see Enhancers)
            🛡️ **Block** · 20 ST · doubles your DEF until your next turn (Tanks triple it)
            💢 **Blitz** · all ST · after your first Focus, below 50 ST: spend everything for a stat surge

            Buttons you can't afford are **greyed out**; each button shows its name and cost, e.g. *Rasengan · 10*.

            **Out of stamina?** Below 10 ST your fighter **Focuses** automatically (next page).
            """)),
        ("Focus, Resolve and Summons", _d("""
            💖 **Focus** · when stamina drops below 10, your turn is spent recovering: stamina refills to **90**, you heal a little and gain ATK/DEF (more the more health you're missing). The screen turns **blue** with speed lines.

            ⚡ **Resolve** · after your first Focus, a **Resolve!** button appears. Resolving transforms your card: big boosts to attack and health at the cost of defense, often with new art and a new name. It uses your turn. The screen erupts in **red and gold**.

            🧬 **Summon** · once you've resolved, your summon can step in once per Focus with an elemental attack or a protection (barrier, shield, parry). **Summoning doesn't end your turn.** Summoner-class cards can summon from the start.

            🎬 When anyone Focuses or Resolves, the screen plays a short power-up animation.
            """)),
        ("Winning, saving and auto battle", _d("""
            🏆 **Win** by bringing your opponent's HP to 0. In Tales and Dungeons you then move on to the next opponent; after a loss you may get **rematches**.

            💾 **Save & Quit** (in More, or on the start screen) keeps your place in a Tales or Dungeon run. It isn't available in Explore, Scenario, Raid, PvP, Boss or the Tutorial. Turn on `/autosave` to save at the start of every match.

            🏳️ **Surrender** ends the match as a loss (in Adventure it just flees the encounter).

            🤖 **Auto Battle** on the start screen resolves the match instantly from both cards' stats.

            ⏱️ You have **5 minutes** per turn. If time runs out, the battle closes; Tales and Dungeon runs are saved where possible.

            🧾 Want more or less of the log on screen? `/battlehistory`.
            """)),
    ]


def damage_pages():
    stat_rows = "\n".join(
        f"• ATK = DEF × {ratio:g} → ×{damage.stat_factor(ratio * 100, 100):.2f}"
        for ratio in (2, 1, 0.5, 0.25, 0.1)
    )
    return [
        ("How much does a hit do?", _d(f"""
            Every attack works the same way:

            > **damage ≈ move AP × {damage.DAMAGE_SCALE:g} × stat factor × hit roll × affinity**  (±{round(damage.VARIANCE * 100)}%)

            **AP** is the number next to each move. Ultimates have the most.

            **Stat factor** · your **ATK** against their **DEF**:
            STAT_ROWS
            (capped between ×{damage.STAT_FACTOR_MIN:g} and ×{damage.STAT_FACTOR_MAX:g}: attack always helps, and a weak card still scratches)

            **No one-shots** · a single hit can never take more than **{round(damage.MAX_HIT_SHARE * 100)}% of the target's max HP**, no matter how many bonuses stack. Big moves still feel big; they just can't end a fight from full health.

            A hit that lands always does at least {round(damage.MIN_DAMAGE_SHARE * 100)}% of the move's AP.
            """).replace("STAT_ROWS", stat_rows)),
        ("Hit roll, speed and affinities", _d(f"""
            🎲 **Hit roll** · each attack rolls a d20, adjusted by both cards' **speed** and some traits:
            • **Miss** · no damage
            • **Glancing** · ×{damage.GLANCING:g}
            • **Normal** · ×1
            • **Strong** · ×{damage.STRONG:g}
            • **Critical** · ×{damage.CRITICAL:g}

            🏃 Faster cards hit and dodge more often; slow cards less. A blocking target can't be critically hit.

            🔅 **Affinities** (shown on the start screen):
            • **Weakness** · ×{damage.WEAKNESS:g}
            • **Resistance** · ×{damage.RESISTANCE:g}
            • **Immunity** · no damage
            • **Repel** · the damage bounces back at the attacker
            • **Absorb** · the target heals instead

            📿 A **talisman** of a move's element ignores the target's resistances and immunities to it.

            The battle log tells you what happened: *hits Crablante for 1,240 damage (strong · fire weakness)*.
            """)),
        ("Protections", _d("""
            Protections come from arms, summons, classes and some elements.

            💠 **Barrier** · blocks an attack completely; you have a number of them. Using an attack yourself drops your barriers (Rangers keep them).

            🌐 **Shield** · a pool of HP that absorbs damage until it breaks.

            🔄 **Parry** · reflects part of the hit back at the attacker and reduces the damage you take; you have a number of them.

            💉 **Siphon** · heals you for part of the damage you deal.

            Several elements break through protections: Dark ignores all of them, Earth and Bleed get through parries, Psychic through barriers, Poison and Rot through shields, Gun through shields. See **Elements**.
            """)),
    ]


def cards():
    return [
        ("Tiers, levels and rarity", _d("""
            🀄 **Tier (1–10)** sets a card's base stats, class strength and enhancer power:
            • **Common** · tier 1–3
            • **Rare** · tier 4–5
            • **Legendary** · tier 6–7
            • **Mythical** · tier 8–9
            • **God** · tier 10

            The stars on a card's frame show its tier, and the frame's metal gets rarer as it climbs, from iron and bronze up to prismatic.

            🔰 **Level** · cards gain experience every battle. Each level raises HP, ATK, DEF and move power. You can also buy levels at the `/blacksmith`.

            📖 Look up any card with `/view`, browse yours with `/cards`, and equip with the **Equip** button or `/equipcard`.
            """)),
        ("Stats and moves", _d("""
            ❤️ **HP** · health. At 0 the card is defeated.
            🌀 **ST** · stamina, spent on every action (see Battles).
            🗡️ **ATK** · raises the damage you deal.
            🛡️ **DEF** · lowers the damage you take.
            🏃 **Speed** · how often you hit and dodge.
            ✨ **AP** · the power of each move.

            **Moves** · every card has three attacks and an enhancer:
            💥 **Basic** (10 ST) · ☄️ **Special** (30 ST) · 🏵️ **Ultimate** (80 ST) · 🦠 **Enhancer** (20 ST)

            Each attack has an **element** (🔥, 💧, 👊...) that adds its own effect on top of the damage. See **Elements**.

            ♾️ Every universe also has a **trait**: a special rule its cards follow in battle. `/traits` lists them.
            """)),
        ("Where cards come from", _d("""
            🎴 **Universe cards** · drop in **Tales** runs and appear in the market.
            👺 **Dungeon cards** · drop in **Dungeons** (not on Easy).
            ✨ **Destiny cards** · earned by completing a card's **Destiny** quest line.
            👹 **Boss cards** · exchanged for Boss Souls with `/exchange`.
            🃏 **Skins** · alternate versions of cards you own.
            🎲 **Rolls** · `/roll` spends coins for a chance at cards, arms, summons and gems.

            🗄️ Too many? Move extras to `/storage`, **Dismantle** them into gems, **Trade** them, or put them on the **Market**: all from the buttons in `/cards`.
            """)),
    ]


CLASS_TEXT = [
    ("SUMMONER", "Summoner", "Can summon from the very start of battle. Summon attacks get +20% AP per tier (up to +200% at God), barrier and parry summons gain extra charges, and summons earn double XP."),
    ("ASSASSIN", "Assassin", "Starts with 2–6 **Sneak Attacks** (by rarity): they cost no stamina, go through every protection and crit more often. Blitzing grants more."),
    ("FIGHTER", "Fighter", "Starts with 3–7 **Parries** and doubles shield and barrier arms. Physical hits grant 2 more parries."),
    ("RANGER", "Ranger", "Starts with 2–6 **Barriers** and can attack without dropping them. Gun and ranged damage is boosted."),
    ("TANK", "Tank", "Starts with a **Shield** of 250 × tier + level, and gets it again on Resolve. **Block triples** defense instead of doubling it."),
    ("SWORDSMAN", "Swordsman", "On Resolve gains 2–6 guaranteed **Critical Strikes**. Sword and bleed damage is boosted."),
    ("MONSTROSITY", "Monstrosity", "On Resolve gains 1–5 **Double Strikes**: attacks hit twice."),
    ("MAGE", "Mage", "Elemental damage +35% to +60% by rarity, and element effects are stronger."),
    ("HEALER", "Healer", "Stores 30–70% of damage taken and heals health and max health with it on each Focus. Lifesteal is boosted and stacked status effects clear on Focus."),
    ("TACTICIAN", "Tactician", "Blocking into Focus earns **Strategy Points**: 1 · protections, 2 · disable their talisman, 3 · a talisman that bypasses all affinities, 4 · a guaranteed crit that breaks their protections, 5 · disable their summon and make them weak to everything."),
]


def classes():
    intro = _d("""
        Every card has a **class**: a built-in perk that shapes how it fights. The perk grows with the card's rarity:
        **Common** (1–3) · **Rare** (4–5) · **Legendary** (6–7) · **Mythical** (8–9) · **God** (10)
        """)
    pages = []
    chunk = []
    for key, name, text in CLASS_TEXT:
        chunk.append(f"{_class_emoji(key)} **{name}**\n{text}")
        if len(chunk) == 4:
            pages.append(chunk)
            chunk = []
    if chunk:
        pages.append(chunk)
    out = []
    for i, chunk in enumerate(pages):
        body = "\n\n".join(chunk)
        out.append((f"Classes ({i + 1}/{len(pages)})", f"{intro}\n\n{body}" if i == 0 else body))
    return out


def elements():
    rules = ("Elements and affinities", _d(f"""
        Every attack has an **element**. On top of its damage, each element has its own effect: burning, freezing, stealing stats, piercing protections and more.

        Cards react to elements through **affinities**, shown on the start screen and in `/cards`:
        • **Weak** · ×{damage.WEAKNESS:g} damage
        • **Resist** · ×{damage.RESISTANCE:g}
        • **Immune** · no damage
        • **Repel** · the damage hits the attacker
        • **Absorb** · heals the target

        📿 **Talismans** let your attacks ignore a target's resistance, immunity, repel and absorb for one element. Craft them from essence with `/attune` and equip them from `/talismans`.

        The next pages list every element.
        """))
    items = [line.strip() for line in legacy.ELEMENTS_LIST]
    pages = [rules]
    per_page = 6
    for i in range(0, len(items), per_page):
        part = items[i:i + per_page]
        pages.append((f"Elements {i // per_page + 1}/{(len(items) + per_page - 1) // per_page}", "\n\n".join(part)))
    return pages


def enhancers():
    return [
        ("What enhancers do", _d("""
            🦠 Your **enhancer** is your fourth move (20 ST). Instead of damage, it changes the fight: buffing you, weakening them, or bending the rules. Its strength is its **AP**, shown on the button (e.g. *Atk 30%*).

            **Boosts** · **ATK** / **DEF** +AP% · **HLT** heal AP plus part of missing health · **STAM** +AP stamina
            **Steals** · **FLOG** steal ATK · **WITHER** steal DEF · **LIFE** steal health · **DRAIN** steal stamina
            **Sacrifice** · **RAGE** lose DEF, gain move power · **BRACE** lose ATK, gain move power · **BZRK** lose health, gain ATK · **CRYSTAL** lose health, gain DEF
            **Conversion** · **STANCE** swap your ATK and DEF (+AP DEF) · **CONFUSE** swap theirs (−AP DEF)
            """)),
        ("More enhancers", _d("""
            **Time** · **BLINK** give your stamina to them · **SLOW** turn count −AP · **HASTE** turn count +AP
            **Control** · **SOULCHAIN** both fighters' stamina becomes AP · **GAMBLE** costs all your stamina; both fighters' health becomes a random number between 500 and AP
            **Fortitude** · **GROWTH** lose 10% max HP, gain ATK, DEF and AP · **FEAR** lose 20% max HP, lower their ATK, DEF and AP
            **Damage** · **WAVE** direct damage that shrinks each turn (full power on every 10th turn) · **BLAST** direct damage that grows each turn
            **Divinity** · **CREATION** raise your max HP (shrinks each turn, full on every 10th) · **DESTRUCTION** lower their max HP (grows each turn)

            🎯 Enhancers have a 1-in-20 chance to **crit** for double effect.
            """)),
    ]


def gear():
    return [
        ("Titles", _d("""
            🎗️ A **title** applies an effect at the start of each of your turns or when you Focus, all fight long.
            ⚠️ Titles only work on cards from **the same universe** (or Unbound).

            Families of effects:
            • **Boosts / Steals / Sacrifice / Conversion** · the same ideas as enhancers, applied every turn
            • **Protections** · e.g. *Blitz* (hit through parries), *Obliterate* (through shields), *Pierce* (through barriers), *Sharpshooter* (never miss)
            • **Elemental** · *Elemental Buff* (+50% elemental damage), *Elemental Debuff*, *Spell Shield*, *Divinity*
            • **IQ** · stronger Focus buffs, buffs that last past Resolve, a bigger Resolve

            Earn titles by playing; equip with `/titles` or `/equiptitle`.
            """)),
        ("Arms", _d("""
            🦾 An **arm** gives either a protection or a new ability.

            **Protection arms** · 💠 Barrier · 🌐 Shield · 🔄 Parry (see Damage → Protections)
            **Ability arms** · 💥/☄️/🏵️ replace your Basic, Special or Ultimate with a new move and element · 💮 **Ultimax** raises move AP, ATK and DEF · 🪬 **Mana** raises move and enhancer AP by % · 💉 **Siphon** heals you as you hit

            ⚒️ Arms have **durability** and break over time (faster outside their universe), turning into gems. Repair them at the `/blacksmith`.

            Browse and equip with `/arms` or `/equiparm`.
            """)),
        ("Summons, talismans and the Universe Buff", _d("""
            🧬 **Summons** join after you Resolve (from the start for Summoners), once per Focus, with an elemental attack or a protection. They level up as they fight. `/summons` · `/equipsummon`

            📿 **Talismans** make your attacks of one element ignore the target's resistances and affinities. Craft with essence via `/attune`, equip from `/talismans`. Each use wears them down.

            👑 **Universe Buff** · when your title and arm match your card's universe, the card gains bonus HP, ATK and DEF. **Destiny** cards get an even bigger buff.

            💾 Save whole builds with `/savepreset` and swap with `/preset`. `/quickbuild` picks one for you.
            """)),
    ]


def modes():
    return [
        ("Play modes", _d("""
            Start any of these with `/play`:

            🆘 **Tutorial** · a guided first battle.
            ⚔️ **Tales Run** · a chain of battles through one universe, ending with its strongest characters. Drops cards, titles, arms and summons.
            👺 **Dungeon Run** · a harder Tales with better, dungeon-only drops (Normal or Hard).
            🎞️ **Scenario Battle** · hand-built fights with special rules and rewards (Normal or Hard).
            💀 **Raid Battle** · the toughest scenarios, with mythical rewards (**Hard** only).
            🗺️ **Adventure Mode** · walk a map, open chests, talk to characters, shop, take on quests, and battle encounters.
            ⚡ **Randomize** · pick one of the above at random.

            🌌 **Explore** · turn it on with `/explore`; random wild encounters with rare drops appear in your server's explore channel. It also sets your Adventure universe.

            🆚 **PvP** · `/pvp` challenges another player.
            """)),
        ("Difficulty and progress", _d("""
            ⚙️ `/difficulty` changes your whole game:

            **Easy** · relaxed play with weaker enemies. No Dungeons, Destinies, Bosses, Raids or item drops.
            **Normal** · the game as designed, with standard drops.
            **Hard** · stronger enemies, better drops and rewards, and access to Raids.

            🔁 Lost a run? **Rematches** let you retry the same opponent; guild rematch buffs give more.
            💾 Runs can be saved and resumed (see Battles → Saving).
            📜 `/quests` tracks your current goals; `/daily` refreshes them.
            """)),
    ]


def economy():
    return [
        ("Currencies and rewards", _d("""
            🪙 **Coins** · the main currency. Earn them by winning; spend them in the market, on rolls, trades and gifts. `/balance`
            💎 **Gems** · from dismantling items and broken arms. Spend them at the `/blacksmith`. `/gems`
            🪔 **Essence** · from elemental arms. Used to craft talismans with `/attune`. `/essence`

            🎁 **Free stuff** · `/daily` (once a day), `/quests` (goals with rewards), `/code` (redeem codes)
            🎲 **Rolls** · `/roll` spends coins for a random card, arm, summon or gems
            """)),
        ("Trading and the market", _d("""
            🏪 **Marketplace** · `/marketplace` to browse, `/buy` with a market code. List your own items with the **Market** button in `/cards`, `/arms` or `/summons`.

            🤝 **Trading** · `/trade` with another player, add items with the **Trade** button on any item list, and add coins with `/tradecoins`. `/gift` sends coins directly.

            ⚒️ **Blacksmith** · `/blacksmith` sells card levels, card tiers, arm repairs and storage space.

            🗄️ **Storage** · `/storage` holds extra cards, titles and arms; **Dismantle** turns items into gems.
            """)),
    ]


def guilds():
    return [
        ("Guilds", _d("""
            🪖 Guilds are teams of players who earn together.

            • `/guild` · look up any guild
            • `/createguild` · start your own, then `/recruit` friends
            • `/guildoperations` · promote, demote or remove members
            • `/donate` · give coins to a guild bank · `/pay` · owners and officers pay members
            • `/leaveguild` · leave · `/disbandguild` · delete your guild

            **Perks** · members earn extra coins for the guild bank on wins, and guilds can buy **buffs**: extra stats, level-ups each fight, quest skips or rematches.

            **Ranks** · Owner (everything) · Officer (members, pay, buffs) · Captain (pay, toggle buffs) · Member

            👨‍👩‍👧 `/tribe` looks up a player's family.
            """)),
    ]


def universes():
    return [
        ("Universes and traits", _d("""
            🌍 Every card belongs to a **universe** (Naruto, Bleach, One Piece...). `/universes` shows each one's cards, titles, arms, summons and destinies.

            ♾️ **Traits** · every universe has a rule its cards use in battle: chakra boosts, bankai, quirks, titan forms and many more. `/traits` lists them all, or `/traits universe:` for one.

            👑 **Universe Buff** · equip a title and arm from the same universe as your card for bonus HP, ATK and DEF.

            ✨ **Destinies** · card-specific quest lines that unlock special Destiny cards.

            🔎 `/view` looks up any card, title, arm, universe or boss by name.
            """)),
    ]


def settings():
    return [
        ("Settings", _d("""
            ⚙️ **Play your way**
            • `/difficulty` · Easy, Normal or Hard
            • `/autosave` · save your run at the start of every match
            • `/battlehistory` · how many log lines a battle keeps (2–6)
            • `/battleview` · toggle the opponent's stats in battle
            • `/explore` · turn Explore encounters on or off, or pick a universe
            • `/setlanguage` · your preferred language

            🎒 **Builds**
            • `/build` · see your current build
            • `/savepreset` · save it · `/preset` · load a saved one · `/quickbuild` · generate one

            🗑️ `/deleteaccount` · permanently delete your account
            """)),
    ]


ADMIN_ONLY = {"addfield", "cardart", "combinegems", "createcode", "createscenarios", "fixspaces", "updatecharacters"}

COMMAND_GROUPS = [
    ("🚀 Start & account", ["register", "daily", "quests", "player", "build", "deleteaccount", "help"]),
    ("⚔️ Play", ["play", "pvp", "explore", "difficulty", "autosave", "battlehistory", "battleview"]),
    ("🎴 Collection", ["cards", "titles", "arms", "summons", "talismans", "storage", "view", "universes", "traits"]),
    ("🎒 Equip & builds", ["equipcard", "equiptitle", "equiparm", "equipsummon", "attune", "preset", "savepreset", "quickbuild"]),
    ("💰 Economy", ["balance", "gems", "essence", "marketplace", "buy", "trade", "tradecoins", "gift", "blacksmith", "roll", "code", "exchange"]),
    ("🪖 Guilds & social", ["guild", "createguild", "recruit", "guildoperations", "donate", "pay", "leaveguild", "disbandguild", "tribe"]),
    ("🛠️ Server setup", ["createexplorechannel", "setexplorechannel", "setlanguage"]),
]


def command_pages(commands):
    """Pages listing every registered command.  ``commands`` maps name -> description."""
    seen = set()
    blocks = []
    for title, names in COMMAND_GROUPS:
        lines = []
        for name in names:
            if name in commands and name not in ADMIN_ONLY:
                lines.append(f"`/{name}` · {commands[name]}")
                seen.add(name)
        if lines:
            blocks.append(f"**{title}**\n" + "\n".join(lines))
    rest = [n for n in sorted(commands) if n not in seen and n not in ADMIN_ONLY]
    if rest:
        blocks.append("**✨ More**\n" + "\n".join(f"`/{n}` · {commands[n]}" for n in rest))
    pages, current = [], ""
    for block in blocks:
        if current and len(current) + len(block) > 1700:
            pages.append(current)
            current = ""
        current = f"{current}\n\n{block}" if current else block
    if current:
        pages.append(current)
    return [(f"All commands ({i + 1}/{len(pages)})", page) for i, page in enumerate(pages)] or [("All commands", "No commands found.")]


# --------------------------------------------------------------------------- registry
TOPICS = [
    # key, emoji, title, one-line description, builder
    ("start", "🚀", "Getting Started", "New here? Your first five minutes", getting_started),
    ("battles", "⚔️", "Battles", "The battle screen, stamina, Focus and Resolve", battles),
    ("damage", "💥", "Damage", "How hits, crits and affinities work", damage_pages),
    ("cards", "🎴", "Cards", "Tiers, levels, stats and where cards come from", cards),
    ("classes", "🥋", "Classes", "What each class does in battle", classes),
    ("elements", "🔅", "Elements", "Every element's effect and affinities", elements),
    ("enhancers", "🦠", "Enhancers", "Your fourth move, explained", enhancers),
    ("gear", "🎒", "Gear", "Titles, arms, summons and talismans", gear),
    ("modes", "🗺️", "Game Modes", "Tales, Dungeons, Raids, Adventure, PvP...", modes),
    ("economy", "💰", "Economy", "Coins, gems, trading, market and rewards", economy),
    ("guilds", "🪖", "Guilds", "Teams, perks and ranks", guilds),
    ("universes", "🌍", "Universes", "Universes, traits and destinies", universes),
    ("settings", "⚙️", "Settings", "Difficulty, autosave, presets and more", settings),
    ("commands", "📜", "All Commands", "Every command, grouped", None),
]

TOPIC_INDEX = {key: (emoji, title, blurb, builder) for key, emoji, title, blurb, builder in TOPICS}

# old /help selections, so existing habits still work
ALIASES = {
    "menu": "commands", "legend": "cards", "play": "modes", "universe": "universes", "teams": "guilds",
    "options": "settings", "titles": "gear", "arms": "gear", "manual": "start", "home": "home",
}


def resolve_topic(value):
    value = (value or "").strip().lower()
    if not value:
        return "home"
    if value in TOPIC_INDEX or value == "home":
        return value
    if value in ALIASES:
        return ALIASES[value]
    for key, emoji, title, blurb, _ in TOPICS:
        if value in title.lower() or value in key:
            return key
    return "home"


def pages_for(topic, commands=None):
    if topic == "commands":
        return command_pages(commands or {})
    entry = TOPIC_INDEX.get(topic)
    if entry is None:
        return []
    return entry[3]()


def home_text():
    lines = [f"{emoji} **{title}** · {blurb}" for key, emoji, title, blurb, _ in TOPICS]
    return _d("""
        ## 📚 Anime VS+ Guide
        Collect anime heroes, build them up, and battle across the multiverse.

        **New player?** Start with 🚀 **Getting Started**, then play the Tutorial with `/play`.
        """) + "\n\n" + "\n".join(lines) + "\n\n-# Pick a topic from the menu. Only you can see this guide."
