"""Gameplay collections the dashboard is allowed to edit.

Player accounts, inventories, and matches are intentionally absent. These are
the records the battle reads: cards, titles, arms, summons, universes, bosses,
and scenarios.
"""

ELEMENTS = [
    "PHYSICAL", "SWORD", "RANGED", "GUN", "RECKLESS", "BLEED", "FIRE", "ICE",
    "WATER", "EARTH", "NATURE", "ELECTRIC", "WIND", "PSYCHIC", "DEATH", "LIFE",
    "LIGHT", "DARK", "POISON", "ENERGY", "TIME", "GRAVITY", "SLEEP", "ROT", "DRACONIC",
]

CLASSES = [
    "FIGHTER", "SWORDSMAN", "RANGER", "TANK", "MAGE", "HEALER", "ASSASSIN",
    "SUMMONER", "MONSTROSITY", "TACTICIAN",
]

DROP_STYLES = ["TALES", "DUNGEON", "SCENARIO", "DESTINY", "BOSS", "RAID", "SKIN"]

# Card enhancers (move 4 TYPE). The first list is what cards use in the bot; the
# rest were already offered by the old editor and are kept so nothing disappears.
CARD_ENHANCERS = [
    "ATK", "DEF", "STAM", "HLT", "LIFE", "DRAIN", "FLOG", "WITHER", "RAGE", "BRACE",
    "BZRK", "CRYSTAL", "GROWTH", "STANCE", "CONFUSE", "BLINK", "SLOW", "HASTE", "FEAR",
    "SOULCHAIN", "GAMBLE", "WAVE", "CREATION", "BLAST", "DESTRUCTION",
]
ENHANCER_TYPES = CARD_ENHANCERS + [t for t in ["SPD", "SHIELD", "BARRIER", "PARRY", "SIPHON", "MANA"]
                                   if t not in CARD_ENHANCERS]

ARM_TYPES = ["BASIC", "SPECIAL", "ULTIMATE", "ULTIMAX", "SHIELD", "BARRIER", "PARRY", "SIPHON", "MANA"]

TITLE_ABILITIES = [
    "ATK", "DEF", "STAM", "HLT", "LIFE", "DRAIN", "FLOG", "WITHER", "RAGE", "BRACE", "BZRK",
    "CRYSTAL", "GROWTH", "FEAR", "STANCE", "CONFUSE", "CREATION", "DESTRUCTION", "SPEED",
    "SLOW", "HASTE", "SOULCHAIN", "GAMBLE", "SINGULARITY", "IQ", "HIGH IQ", "BLITZ",
    "FORESIGHT", "OBLITERATE", "IMPENETRABLE SHIELD", "PIERCE", "SYNTHESIS", "SPELL SHIELD",
    "ELEMENTAL BUFF", "ELEMENTAL DEBUFF", "ENHANCED GUARD", "STRATEGIST", "SHARPSHOOTER", "DIVINITY",
]

SUMMON_TYPES = ELEMENTS + [t for t in CARD_ENHANCERS + ["SHIELD", "BARRIER", "PARRY"] if t not in ELEMENTS]

# Same palette and emoji the bot draws with (element_art.STYLES): emoji, main, glow.
ELEMENT_STYLES = {
    "PHYSICAL": ("👊", "#d6783a", "#ff9646"), "SWORD": ("⚔️", "#96a8be", "#aad2ff"),
    "RANGED": ("🏹", "#78a046", "#aae66e"), "GUN": ("🔫", "#b08c46", "#ffc86e"),
    "RECKLESS": ("♻️", "#dc3228", "#ff5028"), "FIRE": ("🔥", "#f06014", "#ff781e"),
    "WATER": ("💧", "#288ce6", "#50b4ff"), "EARTH": ("⛰️", "#a0703e", "#dcaa5a"),
    "ELECTRIC": ("🌩️", "#fad228", "#ffe650"), "WIND": ("🌪️", "#78dcbe", "#a0ffdc"),
    "NATURE": ("🌿", "#46aa3c", "#78e65a"), "ICE": ("❄️", "#8cd2fa", "#b4ecff"),
    "BLEED": ("🅱️", "#be1428", "#ff283c"), "ENERGY": ("🧿", "#3cc8ff", "#78dcff"),
    "PSYCHIC": ("🔮", "#be5ae6", "#dc78ff"), "SLEEP": ("💤", "#8282dc", "#aaaaff"),
    "DEATH": ("☠️", "#6e6e74", "#beffd2"), "LIFE": ("❤️‍🔥", "#f05a8c", "#ff8caa"),
    "LIGHT": ("🌕", "#fadc78", "#fff0aa"), "DARK": ("🌑", "#502878", "#8c46dc"),
    "POISON": ("🧪", "#78d232", "#96ff3c"), "ROT": ("🩻", "#828250", "#b4c878"),
    "TIME": ("⌛", "#c4a05a", "#f0d282"), "GRAVITY": ("🪐", "#5a50c8", "#826eff"),
    "DRACONIC": ("🐲", "#28aa78", "#5ae6aa"),
}

CLASS_EMOJI = {
    "FIGHTER": "🥊", "SWORDSMAN": "🗡️", "RANGER": "🎯", "TANK": "🛡️", "MAGE": "🪄",
    "HEALER": "💚", "ASSASSIN": "🥷", "SUMMONER": "🌀", "MONSTROSITY": "👹", "TACTICIAN": "♟️",
}

ARM_TYPE_EMOJI = {
    "BASIC": "🥋", "SPECIAL": "💥", "ULTIMATE": "☄️", "ULTIMAX": "🌋", "SHIELD": "🌐",
    "BARRIER": "💠", "PARRY": "🔄", "SIPHON": "💉", "MANA": "🔷",
}


def _f(key, label, kind, **extra):
    field = {"key": key, "label": label, "type": kind}
    field.update(extra)
    return field


# Each catalog lists:
#   fields   every editable field, grouped by "group" on the editor
#   quick    the fields offered in the quick-edit sheet on the gallery
#   image    the field holding a picture the gallery can show (cards are rendered instead)
CATALOGS = {
    "cards": {
        "label": "Cards",
        "icon": "🃏",
        "color": "#ff2e88",
        "collection": "cards_col",
        "name": "NAME",
        "universe": "UNIVERSE",
        "sort": "NAME",
        "image": None,
        "blurb": "Stats, moves, elements, class, and the art the battle displays.",
        "columns": [("Name", "NAME"), ("Universe", "UNIVERSE"), ("Class", "CLASS"),
                    ("Tier", "TIER"), ("HP", "HLT"), ("ATK", "ATK"), ("DEF", "DEF"), ("Drop", "DROP_STYLE")],
        "sorts": [("NAME", "Name"), ("-TIER", "Tier ↓"), ("-HLT", "HP ↓"), ("-ATK", "ATK ↓"),
                  ("-DEF", "DEF ↓"), ("-PRICE", "Price ↓"), ("UNIVERSE", "Universe")],
        "quick": ["TIER", "CLASS", "HLT", "ATK", "DEF", "STAM", "SPD", "PRICE", "DROP_STYLE", "AVAILABLE"],
        "fields": [
            _f("NAME", "Name", "str", identity=True, group="Identity"),
            _f("UNIVERSE", "Universe", "select", options="universes", group="Identity"),
            _f("CLASS", "Class", "select", options="classes", group="Identity"),
            _f("DROP_STYLE", "Drop style", "select", options="drops", group="Identity"),
            _f("TIER", "Tier", "float", group="Stats", min=1, max=10, step=1),
            _f("HLT", "Health", "int", group="Stats", min=0, max=5000, step=10),
            _f("STAM", "Stamina", "int", group="Stats", min=0, max=200, step=5),
            _f("ATK", "Attack", "int", group="Stats", min=0, max=500, step=1),
            _f("DEF", "Defense", "int", group="Stats", min=0, max=500, step=1),
            _f("BASEATK", "Base attack", "int", group="Stats", min=0, max=500, step=1),
            _f("BASEDEF", "Base defense", "int", group="Stats", min=0, max=500, step=1),
            _f("SPD", "Speed", "float", group="Stats", min=0, max=150, step=1),
            _f("PRICE", "Price", "int", group="Shop"),
            _f("STOCK", "Stock", "int", group="Shop"),
            _f("AVAILABLE", "Available", "bool", group="Shop"),
            _f("EXCLUSIVE", "Exclusive", "bool", group="Shop"),
            _f("IS_SKIN", "Skin", "bool", group="Shop"),
            _f("SKIN_FOR", "Skin for", "str", group="Shop"),
            _f("TYPE", "Type", "int", group="Advanced", hint="Legacy type number. Leave it unless you know this card uses it."),
            _f("RNAME", "Resolved name", "str", group="Identity"),
            _f("WEAKNESS", "Weaknesses", "elements", group="Affinities"),
            _f("RESISTANT", "Resistances", "elements", group="Affinities"),
            _f("REPEL", "Repels", "elements", group="Affinities"),
            _f("IMMUNE", "Immunities", "elements", group="Affinities"),
            _f("ABSORB", "Absorbs", "elements", group="Affinities"),
            _f("CARD_ART", "Card image", "url", group="Art",
               hint="The one picture this card uses, including while focused or resolved. A blank box shows the image already saved on the card."),
            _f("CARD_ART_CROP", "Art crop", "str", group="Art", hint="Focal point as x,y from 0 to 1, for example 0.5,0.3. Blank uses automatic framing."),
            _f("GIF", "GIF", "url", group="Art"),
            _f("PASS", "Passive", "json", group="Advanced"),
            _f("DESCRIPTIONS", "Descriptions", "json", group="Advanced"),
        ],
    },
    "titles": {
        "label": "Titles",
        "icon": "👑",
        "color": "#ffd400",
        "collection": "titles_col",
        "name": "TITLE",
        "universe": "UNIVERSE",
        "sort": "TITLE",
        "image": None,
        "blurb": "Title names and the stat ability they grant in battle.",
        "columns": [("Title", "TITLE"), ("Universe", "UNIVERSE"), ("Method", "METHOD"), ("Value", "VALUE")],
        "sorts": [("TITLE", "Name"), ("UNIVERSE", "Universe"), ("-VALUE", "Unlock value ↓")],
        "quick": ["ABILITIES", "ELEMENT", "RARITY", "AVAILABLE", "SCENARIO_DROP"],
        "fields": [
            _f("TITLE", "Title", "str", identity=True, group="Identity"),
            _f("UNIVERSE", "Universe", "select", options="universes", group="Identity"),
            _f("AVAILABLE", "Available", "bool", group="Identity"),
            _f("ELEMENT", "Element", "select", options="elements", group="Identity"),
            _f("RARITY", "Rarity", "str", group="Identity"),
            _f("ABILITIES", "Abilities", "json", group="Abilities", builder="title",
               hint='Example: [{"ABILITY": "DEF", "POWER": 45, "ELEMENT": "", "DURATION": 0}]'),
            _f("METHOD", "Unlock method", "str", group="Unlock"),
            _f("VALUE", "Unlock value", "int", group="Unlock"),
            _f("SCENARIO_DROP", "Scenario drop", "bool", group="Unlock"),
            _f("UNLOCK_METHOD", "Unlock details", "json", group="Unlock"),
        ],
    },
    "arms": {
        "label": "Arms",
        "icon": "⚔️",
        "color": "#18e0ff",
        "collection": "arm_col",
        "name": "ARM",
        "universe": "UNIVERSE",
        "sort": "ARM",
        "image": None,
        "blurb": "Weapons and the battle ability stored on each arm.",
        "columns": [("Arm", "ARM"), ("Universe", "UNIVERSE"), ("Element", "ELEMENT"), ("Price", "PRICE"), ("Drop", "DROP_STYLE")],
        "sorts": [("ARM", "Name"), ("UNIVERSE", "Universe"), ("-PRICE", "Price ↓")],
        "quick": ["ABILITIES", "ELEMENT", "PRICE", "DROP_STYLE", "AVAILABLE"],
        "fields": [
            _f("ARM", "Name", "str", identity=True, group="Identity"),
            _f("UNIVERSE", "Universe", "select", options="universes", group="Identity"),
            _f("ELEMENT", "Element", "select", options="elements", group="Identity"),
            _f("ABILITIES", "Abilities", "json", group="Abilities", builder="arm",
               hint='Example: [{"PARRY": 5}] or [{"BASIC": 20}]'),
            _f("PRICE", "Price", "int", group="Shop"),
            _f("STOCK", "Stock", "int", group="Shop"),
            _f("AVAILABLE", "Available", "bool", group="Shop"),
            _f("EXCLUSIVE", "Exclusive", "bool", group="Shop"),
            _f("DROP_STYLE", "Drop style", "select", options="drops", group="Shop"),
            _f("TOURNAMENT_REQUIREMENTS", "Tournament requirement", "int", group="Shop"),
            _f("COLLECTION", "Collection", "str", group="Shop"),
        ],
    },
    "summons": {
        "label": "Summons",
        "icon": "🐉",
        "color": "#a6ff3c",
        "collection": "pet_col",
        "name": "PET",
        "universe": "UNIVERSE",
        "sort": "PET",
        "image": "PATH",
        "blurb": "Summons, their image, and the ability they use in battle.",
        "columns": [("Summon", "PET"), ("Universe", "UNIVERSE"), ("Level", "LVL"), ("Drop", "DROP_STYLE")],
        "sorts": [("PET", "Name"), ("UNIVERSE", "Universe"), ("-LVL", "Level ↓")],
        "quick": ["ABILITIES", "LVL", "DROP_STYLE", "AVAILABLE"],
        "fields": [
            _f("PET", "Name", "str", identity=True, group="Identity"),
            _f("UNIVERSE", "Universe", "select", options="universes", group="Identity"),
            _f("PATH", "Image", "url", group="Identity"),
            _f("ABILITIES", "Abilities", "json", group="Abilities", builder="summon",
               hint='Each ability is an object. The move name is its own key, plus TYPE.'),
            _f("LVL", "Level", "int", group="Stats"),
            _f("EXP", "Experience", "float", group="Stats"),
            _f("AVAILABLE", "Available", "bool", group="Stats"),
            _f("EXCLUSIVE", "Exclusive", "bool", group="Stats"),
            _f("DROP_STYLE", "Drop style", "select", options="drops", group="Stats"),
            _f("COLLECTION", "Collection", "str", group="Stats"),
        ],
    },
    "universes": {
        "label": "Universes",
        "icon": "🌌",
        "color": "#8b5cff",
        "collection": "universe_col",
        "name": "TITLE",
        "universe": None,
        "sort": "TITLE",
        "image": "PATH",
        "blurb": "Universe art, tale and dungeon paths, and the gear new players receive.",
        "columns": [("Universe", "TITLE"), ("Boss", "UNIVERSE_BOSS"), ("Tales", "CROWN_TALES"), ("Dungeons", "DUNGEONS")],
        "sorts": [("TITLE", "Name"), ("-TIER", "Tier ↓")],
        "quick": ["TIER", "UNIVERSE_BOSS", "HAS_CROWN_TALES", "HAS_DUNGEON", "CORRUPTED"],
        "fields": [
            _f("TITLE", "Title", "str", identity=True, group="Identity"),
            _f("PATH", "Image", "url", group="Identity"),
            _f("TIER", "Tier", "int", group="Identity"),
            _f("UNIVERSE_BOSS", "Universe boss", "str", group="Identity"),
            _f("PREREQUISITE", "Prerequisite", "str", group="Identity"),
            _f("GUILD", "Guild", "str", group="Identity"),
            _f("UTITLE", "Tale title", "str", group="Starter gear"),
            _f("UARM", "Tale arm", "str", group="Starter gear"),
            _f("UPET", "Tale summon", "str", group="Starter gear"),
            _f("DTITLE", "Dungeon title", "str", group="Starter gear"),
            _f("DARM", "Dungeon arm", "str", group="Starter gear"),
            _f("DPET", "Dungeon summon", "str", group="Starter gear"),
            _f("HAS_CROWN_TALES", "Has tales", "bool", group="Modes"),
            _f("HAS_DUNGEON", "Has dungeon", "bool", group="Modes"),
            _f("CORRUPTED", "Corrupted", "bool", group="Modes"),
            _f("CORRUPTION_LEVEL", "Corruption level", "int", group="Modes"),
            _f("ESSENCE", "Essence", "str", group="Modes"),
            _f("CROWN_TALES", "Tales", "roster", group="Paths", hint="Drag a fight to change its place. Search adds a card at the end."),
            _f("DUNGEONS", "Dungeons", "roster", group="Paths", hint="Drag a fight to change its place. Search adds a card at the end."),
        ],
    },
    "bosses": {
        "label": "Bosses",
        "icon": "💀",
        "color": "#ff7a1a",
        "collection": "boss_col",
        "name": "NAME",
        "universe": "UNIVERSE",
        "sort": "NAME",
        "image": "PATH",
        "blurb": "Boss fights: which card, title, arm, and summon they bring.",
        "columns": [("Boss", "NAME"), ("Universe", "UNIVERSE"), ("Card", "CARD"), ("Title", "TITLE"), ("Arm", "ARM")],
        "sorts": [("NAME", "Name"), ("UNIVERSE", "Universe")],
        "quick": ["CARD", "TITLE", "ARM", "AVAILABLE"],
        "fields": [
            _f("NAME", "Name", "str", identity=True, group="Identity"),
            _f("UNIVERSE", "Universe", "select", options="universes", group="Identity"),
            _f("PATH", "Image", "url", group="Identity"),
            _f("AVAILABLE", "Available", "bool", group="Identity"),
            _f("CARD", "Card", "str", group="Loadout"),
            _f("TITLE", "Title", "str", group="Loadout"),
            _f("ARM", "Arm", "str", group="Loadout"),
            _f("PET", "Summon", "json", group="Loadout"),
            _f("DESCRIPTION", "Description", "json", group="Advanced"),
            _f("TACTICS", "Tactics", "json", group="Advanced"),
        ],
    },
    "scenarios": {
        "label": "Scenarios",
        "icon": "🗺️",
        "color": "#ff4d4d",
        "collection": "scenario_col",
        "name": "TITLE",
        "universe": "UNIVERSE",
        "sort": "TITLE",
        "image": "IMAGE",
        "blurb": "Scenario enemies, level, and the drops for each difficulty.",
        "columns": [("Scenario", "TITLE"), ("Universe", "UNIVERSE"), ("Level", "ENEMY_LEVEL"), ("Enemies", "ENEMIES")],
        "sorts": [("TITLE", "Name"), ("-ENEMY_LEVEL", "Level ↓"), ("UNIVERSE", "Universe")],
        "quick": ["ENEMY_LEVEL", "AVAILABLE", "IS_RAID", "IS_DESTINY"],
        "fields": [
            _f("TITLE", "Title", "str", identity=True, group="Identity"),
            _f("UNIVERSE", "Universe", "select", options="universes", group="Identity"),
            _f("IMAGE", "Image", "url", group="Identity"),
            _f("ENEMY_LEVEL", "Enemy level", "int", group="Identity"),
            _f("AVAILABLE", "Available", "bool", group="Identity"),
            _f("IS_RAID", "Raid", "bool", group="Identity"),
            _f("IS_DESTINY", "Destiny", "bool", group="Identity"),
            _f("ENEMIES", "Enemies", "list", group="Fights", hint="One card name per line."),
            _f("EASY_DROPS", "Easy drops", "list", group="Drops"),
            _f("NORMAL_DROPS", "Normal drops", "list", group="Drops"),
            _f("HARD_DROPS", "Hard drops", "list", group="Drops"),
            _f("DESTINY_CARDS", "Destiny cards", "list", group="Drops"),
            _f("MUST_COMPLETE", "Must complete", "list", group="Fights"),
            _f("TACTICS", "Tactics", "json", group="Advanced"),
            _f("LOCATIONS", "Locations", "json", group="Advanced"),
        ],
    },
}


def get_catalog(key):
    return CATALOGS.get(key)


def field_map(catalog):
    return {field["key"]: field for field in catalog["fields"]}


def element_style(element):
    key = str(element or "").upper().strip()
    key = {"RECOIL": "RECKLESS", "SPIRIT": "ENERGY", "SPIRIT ENERGY": "ENERGY"}.get(key, key)
    emoji, color, glow = ELEMENT_STYLES.get(key, ("✨", "#c48c28", "#ffd678"))
    return {"key": key, "emoji": emoji, "color": color, "glow": glow}
