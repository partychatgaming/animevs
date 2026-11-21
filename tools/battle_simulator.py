"""Headless battle simulator for Anime VS+ (developer tool, never used by the bot).

Plays real battles through the real game code (cogs/play.py, the Battle/Card
classes, rewards, results screens, Adventure mode...) without Discord and
without touching your database:

  * MongoDB is replaced by an in-memory mongomock database filled with
    synthetic cards, titles, arms, summons, universes, bosses, scenarios and
    abyss floors covering every universe, class, element and enhancer;
  * Discord is replaced by fake users/channels/messages, and a fake player
    presses random buttons (attacks, enhancers, block, blitz, resolve, summon,
    save, quit, rematch, adventure moves...);
  * the fake messages check Discord's limits (embed sizes, button rows...),
    which the real API would reject with a 400.

Every exception is reported, including the ones the game code catches and
only prints.  Exit code 1 if anything crashed.

Setup (once):   pip install mongomock
Run:            python tools/battle_simulator.py --battles 500
Options:        --seed N  --modes Tales,Dungeon,RPG  --render  --detail <text>

Modes: Tales Dungeon Boss PVP Tutorial Explore Abyss Scenario ATales RPG
--render draws the real card images and power-up animations (slower, ~1-2 s per battle).
"""
import os, sys, random, asyncio, traceback, time, collections, io, json, re, builtins, argparse

_parser = argparse.ArgumentParser(description="Simulate Anime VS+ battles headlessly.")
_parser.add_argument("--battles", type=int, default=200)
_parser.add_argument("--seed", type=int, default=1)
_parser.add_argument("--modes", default="all", help="comma separated list, or 'all'")
_parser.add_argument("--render", action="store_true", help="render real card images")
_parser.add_argument("--detail", default=None, help="print full tracebacks for errors containing this text ('all' for every error)")
_parser.add_argument("--timeout", type=float, default=60, help="seconds before a single battle counts as hung")
_parser.add_argument("--src", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), help=argparse.SUPPRESS)
_args = _parser.parse_args()

SRC = os.path.abspath(_args.src)
N = _args.battles
SEED = _args.seed
MODES = None if _args.modes == "all" else _args.modes.split(",")
RENDER = _args.render
VERBOSE = os.environ.get("SIM_VERBOSE") == "1"
if _args.detail:
    os.environ["SIM_DETAIL"] = _args.detail
os.environ["SIM_TIMEOUT"] = str(_args.timeout)
# Never reach real services: no OpenAI key, a dummy database URL (MongoClient is mocked below).
os.environ["OPENAI_API"] = ""
os.environ.setdefault("ENV", "test")
os.environ["MONGO_LOGIN"] = "mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=200"
os.environ.setdefault("DISCORD_TOKEN", "x")
os.environ.setdefault("NEW_TEST_DISCORD_TOKEN", "x")
os.environ.setdefault("EMOJI_CACHE_DIR", os.path.join(os.environ.get("TMPDIR", "/tmp"), "animevs_sim_emoji"))
sys.dont_write_bytecode = True
sys.path.insert(0, SRC)
os.chdir(SRC)
random.seed(SEED)

import mongomock, pymongo
class _MC(mongomock.MongoClient):
    def __init__(self, *a, **kw):
        super().__init__()
pymongo.MongoClient = _MC

import logging
logging.disable(logging.WARNING)

# ------------------------------------------------------------------ error capture
ERRORS = collections.Counter()
SAMPLES = {}
CURRENT = {"battle": None}

def _record(kind, key, detail):
    k = (kind, key)
    ERRORS[k] += 1
    if k not in SAMPLES:
        SAMPLES[k] = (detail, CURRENT["battle"])

_real_print = builtins.print
def _print(*a, **kw):
    s = " ".join(str(x) for x in a)
    if s.startswith("{'type'"):
        m = re.search(r"'type': '([^']+)', 'message': '(.*?)', 'trace': (\[.*\])", s, re.S)
        if m:
            frames = re.findall(r"'filename': '([^']+)', 'name': '([^']+)', 'lineno': (\d+)", m.group(3))
            loc = " <- ".join(f"{os.path.basename(f)}:{n}:{l}" for f, n, l in reversed(frames[-3:]))
            _record("swallowed", f"{m.group(1)}: {m.group(2)[:120]} @ {loc}", s[:3000])
            return
    if VERBOSE:
        _real_print(*a, **kw)
builtins.print = _print

import custom_logging
def _dbg(ex):
    tb = traceback.extract_tb(ex.__traceback__)
    loc = " <- ".join(f"{os.path.basename(f.filename)}:{f.name}:{f.lineno}" for f in reversed(tb[-3:]))
    _record("swallowed", f"{type(ex).__name__}: {str(ex)[:120]} @ {loc}", "".join(traceback.format_exception(ex))[-3000:])
custom_logging.debug = _dbg

from logger import loggy
def _crit(msg, *a, **kw):
    msg = str(msg)
    first = msg.splitlines()[0][:200]
    _record("CRASH", first, msg[-4000:])
loggy.critical = _crit
_orig_error = loggy.error
def _err(msg, *a, **kw):
    _record("error-log", str(msg).splitlines()[0][:200], str(msg)[-3000:])
loggy.error = _err

# ------------------------------------------------------------------ speedups
_real_sleep = asyncio.sleep
async def _fast_sleep(delay=0, result=None):
    SLEEPS[0] += delay
    await _real_sleep(0)
    return result
SLEEPS = [0.0]
asyncio.sleep = _fast_sleep
import contextvars
IN_THREAD = contextvars.ContextVar("in_thread", default=False)
async def _inline_to_thread(func, *a, **kw):
    tok = IN_THREAD.set(True)
    try:
        return func(*a, **kw)
    finally:
        IN_THREAD.reset(tok)
asyncio.to_thread = _inline_to_thread

import render_cache
from PIL import Image
_png_cache = {}
def _fake_http(url, timeout):
    if url not in _png_cache:
        size = (64, 64) if ("emoji" in url or "twemoji" in url or "cdn" in url and url.endswith(".png") and "card" not in url) else (1200, 600)
        if "/card/" in url or "/summon/" in url or "/uni/" in url:
            size = (1200, 600) if "/card/" in url else (600, 600)
        if "/raw/" in url:
            size = {"tall": (640, 900), "square": (700, 700), "wide": (1280, 720)}.get(url.split("/raw/")[1].split("/")[0], (800, 1000))
            if "/upload/c_fill" in url:
                STATS["cloudinary_crops"] += 1
                if random.random() < 0.2:
                    return None          # Cloudinary refused the transformation: must fall back
        h = __import__("hashlib").md5(url.encode()).digest()
        im = Image.new("RGBA", size, (h[0], h[1], h[2], 255))
        b = io.BytesIO(); im.save(b, "PNG"); _png_cache[url] = b.getvalue()
    return _png_cache[url]
render_cache._http_get = _fake_http

import db, crown_utilities, classes as data_classes
from cogs.classes.card_class import Card
import cogs.play as play_mod
from cogs.play import Play
from cogs.classes.battle_class import Battle
from cogs.battle_config import BattleConfig
import cogs.classes.card_class as card_mod

DBCALLS = collections.Counter()
if os.environ.get("SIM_DBCOUNT"):
    import inspect, types
    for _n, _f in list(vars(db).items()):
        if isinstance(_f, types.FunctionType) and _f.__module__ == "db" and not _n.startswith("_"):
            def _wrap(f=_f, n=_n):
                def w(*a, **kw):
                    if IN_THREAD.get():
                        return f(*a, **kw)
                    fr = sys._getframe(1)
                    chain = []
                    while fr is not None and len(chain) < 4:
                        nm = os.path.basename(fr.f_code.co_filename)
                        if nm not in ("battle_simulator.py",):
                            chain.append(f"{nm}:{fr.f_code.co_name}")
                        fr = fr.f_back
                    where = " <- ".join(chain)
                    DBCALLS[(n, where)] += 1
                    return f(*a, **kw)
                return w
            setattr(db, _n, _wrap())

if not RENDER:
    def _fast_showcard(self, *a, **kw):
        return io.BytesIO(b"\x89PNG fake")
    Card.showcard = _fast_showcard
    crown_utilities.showsummon = lambda *a, **kw: io.BytesIO(b"\x89PNG fake")
    import battle_scene as _bs
    def _fast_power_up(left, right, sides, *a, **kw):
        STATS["power_up_gif"] += 1
        for side, state in sides.items():
            STATS[f"power_up_{state}"] += 1
        return io.BytesIO(b"GIF89a fake"), "gif"
    _bs.render_power_up = _fast_power_up

# ------------------------------------------------------------------ coverage counters
COVER = collections.Counter()
def _cover(mod, name):
    f = getattr(mod, name)
    if asyncio.iscoroutinefunction(f):
        async def w(*a, **k):
            COVER[name] += 1
            return await f(*a, **k)
    else:
        def w(*a, **k):
            COVER[name] += 1
            return f(*a, **k)
    setattr(mod, name, w)
import cogs.game_state as _gs, cogs.reward_drops as _rd
for _n in ("abyss_level_up_message", "scenario_win", "abyss_win", "explore_win", "rpg_win", "close_loss_screen"):
    if hasattr(_gs, _n): _cover(_gs, _n)
for _n in ("reward_drop", "scenario_drop"):
    _cover(_gs, _n)
for _cls, _n in ((Battle, "set_boss_win"), (Battle, "save_abyss_win"), (Battle, "explore_embed"), (_gs.GameState, "you_lose_non_pvp"), (_gs.GameState, "you_win_non_pvp"), (_gs.GameState, "pvp_end_game")):
    _cover(_cls, _n)
import cogs.classes.rpg_class as _rpg
for _n in ("create_rpg_battle", "open_shop", "generate_quest", "change_map", "encounter_handler"):
    _cover(_rpg.RPG, _n)

# ------------------------------------------------------------------ synthetic data
ELEMENTS = list(crown_utilities.elements)
UNIVERSES = [u for u in crown_utilities.crest_dict.keys()]
CLASSES = list(crown_utilities.class_emojis.keys())
CARD_ENH = ['ATK','DEF','STAM','HLT','LIFE','DRAIN','FLOG','WITHER','RAGE','BRACE','BZRK','CRYSTAL','GROWTH','STANCE','CONFUSE','BLINK','SLOW','HASTE','FEAR','SOULCHAIN','GAMBLE','WAVE','CREATION','BLAST','DESTRUCTION']
TITLE_ABILITIES = list(crown_utilities.title_prefix_mapping.keys())
ARM_TYPES = ['BASIC','SPECIAL','ULTIMATE','ULTIMAX','SHIELD','BARRIER','PARRY','SIPHON','MANA']
SUMMON_TYPES = ELEMENTS + ['ATK','DEF','HLT','LIFE','DRAIN','FLOG','WITHER','RAGE','BRACE','GROWTH','FEAR','STAM','BARRIER','PARRY','SHIELD','BLAST','WAVE','CREATION','DESTRUCTION','GAMBLE','SOULCHAIN','CONFUSE','STANCE','SLOW','HASTE']
TACTICS = ["ENRAGE","OVERWHELMING POWER","DAMAGE CHECK","DEATH BLOW","ALMIGHTY WILL","STAGGER","INTIMIDATION","PETRIFIED FEAR","REGENERATION","BLOODLUST"]

def rsub(lst, k):
    return random.sample(lst, k)

def make_card(name, universe, drop_style, tier=None, cls=None):
    tier = tier or random.randint(1, 10)
    els = [random.choice(ELEMENTS) for _ in range(3)]
    if random.random() < 0.08:
        els[2] = "DRACONIC"
    pool = [e for e in ELEMENTS]
    random.shuffle(pool)
    return {
        "NAME": name, "PATH": f"https://img.test/card/{name}.png", "FPATH": f"https://img.test/card/{name}_f.png",
        "RPATH": f"https://img.test/card/{name}_r.png", "RNAME": name + " (Resolved)", "GIF": "N/A",
        "PRICE": 1000, "AVAILABLE": True, "SKIN_FOR": "N/A", "IS_SKIN": False, "EXCLUSIVE": False,
        "HLT": random.randint(1200, 3000), "STAM": 100, "ATK": random.randint(25, 200), "DEF": random.randint(25, 200),
        "TYPE": 0, "PASS": [{"NAME": 0, "TYPE": "TYPE"}], "SPD": random.randint(10, 100), "UNIVERSE": universe, "TIER": tier,
        "MOVESET": [
            {f"{name} Basic": random.randint(40, 160), "STAM": 10, "ELEMENT": els[0]},
            {f"{name} Special": random.randint(90, 260), "STAM": 30, "ELEMENT": els[1]},
            {f"{name} Ultimate": random.randint(160, 420), "STAM": 80, "ELEMENT": els[2]},
            {f"{name} Enhancer": 0, "STAM": 20, "TYPE": random.choice(CARD_ENH)},
        ],
        "WEAKNESS": pool[0:random.randint(0, 3)], "RESISTANT": pool[3:3 + random.randint(0, 3)],
        "REPEL": pool[6:6 + random.randint(0, 1)], "ABSORB": pool[7:7 + random.randint(0, 1)],
        "IMMUNE": pool[8:8 + random.randint(0, 1)], "CLASS": cls or random.choice(CLASSES),
        "DROP_STYLE": drop_style, "DESCRIPTIONS": [], "STOCK": 5, "HAS_COLLECTION": False, "COLLECTION": "N/A",
        **battle_art_fields(name),
    }

def battle_art_fields(name):
    """About half the cards get raw battle art (Cloudinary-style URLs, various shapes)."""
    r = random.random()
    if r < 0.5:
        return {}
    shape = random.choice(["tall", "square", "wide"])
    out = {"CARD_ART": f"https://res.cloudinary.com/sim/image/upload/v1/raw/{shape}/{name}.png"}
    if random.random() < 0.5:
        out["CARD_FOCUS_ART"] = f"https://img.test/raw/{shape}/{name}_f.png"
    if random.random() < 0.5:
        out["CARD_RESOLVE_ART"] = f"https://img.test/raw/{shape}/{name}_r.png"
    if random.random() < 0.3:
        out["CARD_ART_CROP"] = random.choice(["0.5,0.3", [0.4, 0.2], "70,40", "junk", {"x": 0.6, "y": 0.5}])
    return out

def make_title(name, universe, n_abilities):
    abilities = []
    for _ in range(n_abilities):
        ab = random.choice(TITLE_ABILITIES)
        abilities.append({"ABILITY": ab, "POWER": random.choice([0, random.randint(1, 40)]) if ab not in ("ELEMENTAL BUFF", "ELEMENTAL DEBUFF") else 0,
                          "ELEMENT": random.choice(ELEMENTS), "DURATION": random.randint(0, 5)})
    return {"TITLE": name, "UNIVERSE": universe, "ABILITIES": abilities, "RARITY": "Common",
            "UNLOCK_METHOD": {"METHOD": "TALES RUN", "VALUE": 1, "ELEMENT": ""}, "AVAILABLE": True, "ID": name, "PRICE": 0}

def make_arm(name, universe, drop_style, kind=None):
    kind = kind or random.choice(ARM_TYPES)
    vals = {"BASIC": random.randint(20, 120), "SPECIAL": random.randint(40, 160), "ULTIMATE": random.randint(80, 220),
            "ULTIMAX": random.randint(5, 40), "SHIELD": random.randint(200, 1500), "BARRIER": random.randint(1, 4),
            "PARRY": random.randint(1, 6), "SIPHON": random.randint(10, 90), "MANA": random.randint(105, 140)}
    el = random.choice(ELEMENTS) if kind in ("BASIC", "SPECIAL", "ULTIMATE") else ""
    return {"ARM": name, "UNIVERSE": universe, "ABILITIES": [{kind: vals[kind]}], "DROP_STYLE": drop_style,
            "AVAILABLE": True, "ELEMENT": el, "PRICE": 0, "EXCLUSIVE": False}

def make_summon(name, universe, drop_style):
    t = random.choice(SUMMON_TYPES)
    return {"PET": name, "UNIVERSE": universe, "PATH": f"https://img.test/summon/{name}.png", "AVAILABLE": True,
            "DROP_STYLE": drop_style, "ABILITIES": [{f"{name} Strike": random.randint(5, 150), "TYPE": t}], "EXCLUSIVE": False}

CARDS, TITLES, ARMS, SUMMONS = {}, {}, {}, {}
UNIVERSE_DOCS = {}
def build_world():
    for u in UNIVERSES:
        tales = [f"{u} Tale {i}" for i in range(4)]
        dungeons = [f"{u} Dungeon {i}" for i in range(3)]
        boss = f"{u} Boss"
        for n in tales: CARDS[n] = make_card(n, u, "TALES")
        for n in dungeons: CARDS[n] = make_card(n, u, "DUNGEON")
        CARDS[boss] = make_card(boss, u, "BOSS", tier=random.randint(6, 10))
        CARDS[f"{u} Destiny"] = make_card(f"{u} Destiny", u, "DESTINY")
        CARDS[f"{u} Scenario"] = make_card(f"{u} Scenario", u, "SCENARIO")
        for i in range(3): TITLES[f"{u} Title {i}"] = make_title(f"{u} Title {i}", u, 1)
        for i in range(3): TITLES[f"{u} HTitle {i}"] = make_title(f"{u} HTitle {i}", u, random.randint(2, 3))
        TITLES[f"{u} Boss Title"] = make_title(f"{u} Boss Title", u, 3)
        for ds in ("TALES", "DUNGEON", "BOSS"):
            for kind in ARM_TYPES:
                n = f"{u} {ds} {kind} Arm"
                ARMS[n] = make_arm(n, u, ds, kind)
            for i in range(2):
                n = f"{u} {ds} Summon {i}"
                SUMMONS[n] = make_summon(n, u, ds)
        UNIVERSE_DOCS[u] = {"TITLE": u, "PATH": f"https://img.test/uni/{u}.png", "CROWN_TALES": tales, "DUNGEONS": dungeons,
                            "HAS_DUNGEON": True, "HAS_CROWN_TALES": True, "UNIVERSE_BOSS": boss, "AVAILABLE": True,
                            "UTITLE": f"{u} Title 0", "UARM": f"{u} TALES BASIC Arm", "DTITLE": f"{u} HTitle 0", "DARM": f"{u} DUNGEON BASIC Arm",
                            "UPET": f"{u} TALES Summon 0", "DPET": f"{u} DUNGEON Summon 0", "TIER": random.randint(1, 10), "GUILD": "PCG",
                            "CORRUPTED": random.random() < 0.15, "CORRUPTION_LEVEL": 0, "ESSENCE": "NULL", "PREREQUISITE": "",
                            "UNIVERSE_SOUL": f"{u} Soul", "UNIVERSE_HEART": f"{u} Heart", "GEMS": 0}
        db.boss_col.insert_one({"NAME": boss, "CARD": boss, "TITLE": f"{u} Boss Title", "ARM": f"{u} BOSS SHIELD Arm",
                                "PET": f"{u} BOSS Summon 0", "UNIVERSE": u, "AVAILABLE": True, "PATH": "https://img.test/boss.png",
                                "DESCRIPTION": [f"Boss line {i}" for i in range(15)], "TACTICS": rsub(TACTICS, random.randint(1, 5))})
        db.scenario_col.insert_one({"TITLE": f"{u} Scenario", "IMAGE": "https://img.test/scn.png", "ENEMY_LEVEL": random.randint(10, 900),
                                    "ENEMIES": tales[:2] + dungeons[:1], "EASY_DROPS": [f"{u} Scenario"], "NORMAL_DROPS": [f"{u} TALES BASIC Arm"],
                                    "HARD_DROPS": [f"{u} DUNGEON Summon 0"], "UNIVERSE": u, "AVAILABLE": True, "IS_RAID": random.random() < 0.3,
                                    "TACTICS": rsub(TACTICS, random.randint(0, 3)), "IS_DESTINY": random.random() < 0.2,
                                    "DESTINY_CARDS": [f"{u} Destiny"], "MUST_COMPLETE": [], "LOCATION": "", "DESTINY_TITLE": ""})
    db.cards_col.insert_many(list(CARDS.values()))
    db.titles_col.insert_many(list(TITLES.values()))
    db.arm_col.insert_many(list(ARMS.values()))
    db.pet_col.insert_many(list(SUMMONS.values()))
    db.universe_col.insert_many(list(UNIVERSE_DOCS.values()))
    for floor in range(0, 101):
        u = random.choice(UNIVERSES)
        uni = UNIVERSE_DOCS[u]
        db.abyss_col.insert_one({"FLOOR": floor, "ENEMIES": uni["CROWN_TALES"][:2] + uni["DUNGEONS"][:1], "SPECIAL_BUFF": random.randint(10, 1500),
                                 "TITLE": f"{u} Title 0", "ARM": f"{u} DUNGEON SHIELD Arm", "PET": f"{u} DUNGEON Summon 0",
                                 "BANNED_TIERS": [], "BANNED_UNIVERSES": [], "BANNED_TITLES": [], "BANNED_ARMS": [], "BANNED_PETS": [], "BANNED_CARDS": []})
    CARDS["Training Dummy"] = make_card("Training Dummy", "Unbound", "TALES", tier=1, cls="TANK")
    db.cards_col.insert_one(CARDS["Training Dummy"])
    for n, d in (("Starter", make_title("Starter", "Unbound", 1)),):
        db.titles_col.insert_one(d)
    db.arm_col.insert_one(make_arm("Stock", "Unbound", "TALES", "SHIELD"))
    SUMMONS["Chick"] = make_summon("Chick", "Unbound", "TALES")
    db.pet_col.insert_one(SUMMONS["Chick"])
    tdoc = make_user_doc("837538366509154407", "Tutorial Bot", "Training Dummy")
    tdoc["PETS"].append(summon_entry("Chick"))
    db.users_col.insert_one(tdoc)

def summon_entry(name):
    s = SUMMONS.get(name) or db.pet_col.find_one({"PET": name})
    ab = s["ABILITIES"][0]
    ab_name = [k for k in ab if k != "TYPE"][0]
    return {"NAME": name, "LVL": random.randint(1, 10), "EXP": 0, ab_name: ab[ab_name], "TYPE": ab["TYPE"],
            "BOND": random.randint(0, 3), "BONDEXP": 0, "PATH": s["PATH"]}

def make_user_doc(did, name, card=None):
    u = random.choice(UNIVERSES)
    card = card or random.choice([c for c in CARDS if not c.startswith("Training")])
    cu = CARDS[card]["UNIVERSE"] if card in CARDS else u
    title = random.choice([t for t in TITLES if TITLES[t]["UNIVERSE"] == cu] or list(TITLES))
    arm = random.choice([a for a in ARMS if ARMS[a]["UNIVERSE"] == cu] or list(ARMS))
    summon = random.choice(list(SUMMONS))
    doc = data_classes.newUser({"DISNAME": name, "NAME": name, "DID": did})
    lvl = random.choice([0, 5, 30, 61, 150, 300, 500, 700, 1000, 1500, 2500])
    doc.update({
        "CARD": card, "TITLE": title, "ARM": arm, "PET": summon, "CARDS": [card], "TITLES": [title],
        "ARMS": [{"ARM": arm, "DUR": random.randint(1, 100)}], "PETS": [summon_entry(summon)], "DECK": [],
        "CARD_LEVELS": [{"CARD": card, "LVL": lvl, "TIER": CARDS[card]["TIER"] if card in CARDS else 1, "EXP": 0, "HLT": 0, "ATK": 0, "DEF": 0, "AP": 0,
                          "CLASS": CARDS[card]["CLASS"] if card in CARDS else "TANK", "ID": "X"}],
        "DIFFICULTY": random.choice(["EASY", "NORMAL", "HARD", "NORMAL"]),
        "TALISMAN": random.choice(["NULL", "NULL"] + ELEMENTS), "TALISMANS": [{"TYPE": e, "DUR": 50} for e in ELEMENTS],
        "PERFORMANCE": random.random() < 0.15, "AUTOSAVE": random.random() < 0.3, "BATTLE_HISTORY": random.randint(3, 8),
        "PRESTIGE": random.randint(0, 10), "REBIRTH": random.randint(0, 10), "LEVEL": random.randint(0, 100),
        "GUILD": "PCG", "TEAM": "PCG", "FAMILY": "PCG", "RIFT": random.choice([0, 0, 1]),
        "CROWN_TALES": [random.choice(UNIVERSES)], "DUNGEONS": [random.choice(UNIVERSES)], "BOSS_WINS": [],
        "GEMS": [], "STORAGE": [], "TSTORAGE": [], "ASTORAGE": [], "QUESTS": [], "DESTINY": [], "RPG_LEVELS": [],
    })
    return doc

# ------------------------------------------------------------------ fake discord
class FakeUser:
    def __init__(self, uid, name=None):
        self.id = int(uid); self.did = str(uid); self.name = name or f"user{uid}"
        self.mention = f"<@{uid}>"; self.avatar_url = "https://img.test/avatar.png"; self.display_name = self.name
        self.username = self.name; self.global_name = self.name; self.bot = False
        self.avatar = type("A", (), {"url": self.avatar_url})()
        self.guild = FakeGuild()
    def __eq__(self, o): return isinstance(o, FakeUser) and o.id == self.id
    def __hash__(self): return self.id
    def __str__(self): return self.name
    async def send(self, *a, **kw): return FakeMessage(None, kw)

class FakeGuild:
    name = "SimGuild"; id = 1
    def __str__(self): return self.name

MSG_ID = [0]
STATS = collections.Counter()
def _file_names(kw):
    files = []
    if kw.get("file") is not None: files.append(kw["file"])
    files += list(kw.get("files") or [])
    names = []
    for f in files:
        n = getattr(f, "file_name", None)
        names.append(n if n else (os.path.basename(f) if isinstance(f, str) else "file"))
    return names

class FakeMessage:
    def __init__(self, channel, payload):
        MSG_ID[0] += 1
        self.id = MSG_ID[0]; self.channel = channel; self.payload = payload; self.deleted = False
        self.embeds = [payload.get("embed")] if payload.get("embed") else payload.get("embeds") or []
        self.components = payload.get("components")
        self.content = payload.get("content")
        self.v2 = is_v2(payload.get("components"))
        self.attachments = _file_names(payload)
    async def edit(self, **kw):
        STATS["edit"] += 1
        has_files = kw.get("file") is not None or bool(kw.get("files")) or kw.get("files") == []
        attachments = _file_names(kw) if has_files else self.attachments
        validate_payload(kw, "edit", attachments)
        new_v2 = is_v2(kw.get("components"))
        if self.v2 and (kw.get("embed") or kw.get("embeds") or kw.get("content")):
            _record("discord-400", "embeds/content on a Components V2 message", "edit")
        if not self.v2 and new_v2:
            _record("discord-400", "edited a classic message into Components V2", "edit")
        if self.deleted:
            from interactions.client.errors import NotFound
            err = NotFound.__new__(NotFound)
            Exception.__init__(err, "404 Not Found (error code: 10008): Unknown Message")
            err.status, err.code, err.text, err.errors, err.route, err.response = 404, 10008, "Unknown Message", {}, None, None
            STATS["edit_deleted"] += 1
            raise err
        self.payload.update(kw)
        if has_files: self.attachments = attachments
        if "components" in kw: self.components = kw["components"]
        return self
    async def delete(self, delay=None, **kw):
        STATS["delete"] += 1; self.deleted = True
    async def add_reaction(self, *a, **kw): pass
    async def reply(self, *a, **kw): return FakeMessage(self.channel, kw)

V2_TYPES = {"ContainerComponent", "TextDisplayComponent", "MediaGalleryComponent", "SeparatorComponent",
            "SectionComponent", "ThumbnailComponent", "FileComponent"}

def is_v2(components):
    if not components: return False
    comps = components if isinstance(components, (list, tuple)) else [components]
    return any(type(c).__name__ in V2_TYPES for c in comps)

def _children(c):
    name = type(c).__name__
    if name == "ContainerComponent": return list(c)
    if name == "SectionComponent":
        kids = list(c.components or [])
        if getattr(c, "accessory", None) is not None: kids.append(c.accessory)
        return kids
    if name == "ActionRow": return list(c.components or [])
    return []

def _valid_emoji(e):
    if e is None: return True
    if getattr(e, "id", None): return True
    name = str(getattr(e, "name", e) or "")
    import emoji as _emoji
    return bool(name) and (_emoji.is_emoji(name) or _emoji.is_emoji(name.replace("\ufe0f", "")) or _emoji.is_emoji(name + "\ufe0f"))

def validate_v2(comps, where, attachments):
    count = [0]; text = [0]; ids = []
    def visit(c, depth):
        count[0] += 1
        name = type(c).__name__
        if name == "TextDisplayComponent":
            text[0] += len(c.content or "")
            if not (c.content or "").strip(): _record("discord-400", "empty text display", where)
        elif name == "MediaGalleryComponent":
            items = c.items or []
            if not 1 <= len(items) <= 10: _record("discord-400", f"media gallery with {len(items)} items", where)
            for it in items:
                url = getattr(getattr(it, "media", None), "url", None) or str(getattr(it, "media", ""))
                if url.startswith("attachment://") and url[len("attachment://"):] not in attachments:
                    _record("discord-400", f"gallery references missing attachment {url} (have {attachments})", where)
        elif name == "ActionRow":
            kids = list(c.components or [])
            if not 1 <= len(kids) <= 5: _record("discord-400", f"action row with {len(kids)} items", where)
        elif name == "ContainerComponent" and depth > 0:
            _record("discord-400", "nested container", where)
        elif name == "Button":
            lbl = getattr(c, "label", None)
            if lbl is not None and len(str(lbl)) > 80: _record("discord-400", "button label > 80", where)
            if not lbl and getattr(c, "emoji", None) is None: _record("discord-400", "button without label or emoji", where)
            if not _valid_emoji(getattr(c, "emoji", None)): _record("discord-400", f"invalid button emoji {getattr(c, 'emoji', None)!r}", where)
        elif name == "StringSelectMenu":
            if not 1 <= len(c.options or []) <= 25: _record("discord-400", "select with bad option count", where)
        cid = getattr(c, "custom_id", None)
        if cid:
            ids.append(cid)
            if len(cid) > 100: _record("discord-400", "custom_id > 100", where)
        for k in _children(c): visit(k, depth + 1)
    for c in comps:
        if type(c).__name__ not in V2_TYPES and type(c).__name__ != "ActionRow":
            _record("discord-400", f"{type(c).__name__} at top level of a V2 message", where)
        visit(c, 0)
    if count[0] > 40: _record("discord-400", f"V2 message with {count[0]} components (max 40)", where)
    if text[0] > 4000: _record("discord-400", f"V2 message text {text[0]} chars (max 4000)", where)
    if len(ids) != len(set(ids)): _record("discord-400", f"duplicate custom_ids {sorted(set(i for i in ids if ids.count(i) > 1))}", where)
    STATS["v2_msgs"] += 1

def validate_payload(kw, where, attachments=None):
    """Check Discord limits the real API would enforce (a 400 there kills the call)."""
    comps_v2 = kw.get("components")
    if is_v2(comps_v2):
        if kw.get("embed") or kw.get("embeds") or kw.get("content"):
            _record("discord-400", "content/embeds sent with V2 components", where)
        validate_v2(comps_v2 if isinstance(comps_v2, list) else [comps_v2], where,
                    attachments if attachments is not None else _file_names(kw))
        return
    emb = kw.get("embed") or None
    embeds = [emb] if emb else (kw.get("embeds") or [])
    for e in embeds:
        if e is None or isinstance(e, (str, dict)):
            continue
        try:
            d = e.to_dict()
        except Exception as ex:
            _record("discord-400", f"embed.to_dict failed: {ex}", where); continue
        total = 0
        if len(d.get("title", "") or "") > 256: _record("discord-400", "embed title > 256", where)
        if len(d.get("description", "") or "") > 4096: _record("discord-400", "embed description > 4096", where)
        a = (d.get("author") or {}).get("name", "") or ""
        if len(a) > 256: _record("discord-400", "embed author > 256", where)
        f = (d.get("footer") or {}).get("text", "") or ""
        if len(f) > 2048: _record("discord-400", f"embed footer > 2048 ({len(f)})", where)
        fields = d.get("fields") or []
        if len(fields) > 25: _record("discord-400", "more than 25 fields", where)
        for fl in fields:
            if not fl.get("name") or not str(fl.get("value", "")).strip():
                _record("discord-400", f"empty field name/value: {fl.get('name')!r}", where)
            if len(fl.get("name", "")) > 256: _record("discord-400", "field name > 256", where)
            if len(str(fl.get("value", ""))) > 1024: _record("discord-400", f"field value > 1024 ({fl.get('name')})", where)
            total += len(fl.get("name", "")) + len(str(fl.get("value", "")))
        total += len(d.get("title", "") or "") + len(d.get("description", "") or "") + len(a) + len(f)
        if total > 6000: _record("discord-400", f"embed total > 6000 ({total})", where)
    comps = kw.get("components")
    if comps:
        rows = comps if isinstance(comps, list) else [comps]
        if len(rows) > 5: _record("discord-400", f"more than 5 action rows ({len(rows)})", where)
        ids = []
        for r in rows:
            items = getattr(r, "components", None)
            if items is None:
                items = [r]
            if len(items) > 5: _record("discord-400", f"more than 5 buttons in a row ({len(items)})", where)
            for b in items:
                cid = getattr(b, "custom_id", None)
                lbl = getattr(b, "label", None)
                if lbl is not None and len(str(lbl)) > 80: _record("discord-400", "button label > 80", where)
                if cid: ids.append(cid)
        if len(ids) != len(set(ids)): _record("discord-400", f"duplicate custom_ids {sorted(set(i for i in ids if ids.count(i) > 1))}", where)

class FakeChannel:
    id = 99
    def __init__(self): self.sent = 0
    async def send(self, content=None, **kw):
        STATS["send"] += 1
        validate_payload(kw, "send")
        kw["content"] = content
        return FakeMessage(self, kw)
    def __str__(self): return "sim-channel"

class FakeCtx:
    def __init__(self, author, channel, custom_id=None):
        self.author = author; self.channel = channel; self.custom_id = custom_id
        self.guild = FakeGuild(); self.guild_id = 1; self.responded = False; self.deferred = False
        self.message = FakeMessage(channel, {}); self.user = author; self.values = []
    async def send(self, content=None, **kw):
        STATS["send"] += 1
        if kw.get("ephemeral"): STATS["ephemeral"] += 1
        if self.responded and not self.deferred and not kw.get("ephemeral"):
            pass
        self.responded = True
        validate_payload(kw, "ctx.send"); return FakeMessage(self.channel, kw)
    async def defer(self, *a, **kw):
        if self.responded and not kw.get("suppress_error"):
            _record("discord-400", "interaction acknowledged twice (defer after response)", "ctx.defer")
        self.deferred = True; self.responded = True
    async def edit_origin(self, **kw):
        if self.responded and not self.deferred:
            _record("discord-400", "interaction acknowledged twice (edit_origin after response)", "ctx.edit_origin")
        self.responded = True
        STATS["edit_origin"] += 1
        validate_payload(kw, "ctx.edit_origin", _file_names(kw)); return self.message
    async def edit(self, *a, **kw): return self.message

class FakeEvent:
    def __init__(self, ctx): self.ctx = ctx

def collect_ids(components):
    ids = []
    if components is None: return ids
    if not isinstance(components, (list, tuple)): components = [components]
    for c in components:
        if isinstance(c, (list, tuple)):
            ids += collect_ids(c); continue
        inner = getattr(c, "components", None)
        if inner is not None:
            ids += collect_ids(inner); continue
        cid = getattr(c, "custom_id", None)
        if cid: ids.append(cid)
        if isinstance(c, str): ids.append(c)
    return ids

class FakeBot:
    def __init__(self, sim):
        self.sim = sim; self.user = FakeUser(1, "bot"); self.guilds = []
        self.guild_id = 1; self.guild_channel = 1
    async def fetch_user(self, uid): return self.sim.users.setdefault(str(uid), FakeUser(uid))
    def get_user(self, uid): return self.sim.users.setdefault(str(uid), FakeUser(uid))
    def get_guild(self, *a): return None
    async def validate_user(self, ctx): return True
    def add_component_callback(self, *a, **kw): pass
    def remove_component_callback(self, *a, **kw): pass
    async def wait_for_component(self, components=None, timeout=None, check=None, messages=None, **kw):
        STATS["wait"] += 1
        ids = collect_ids(components)
        if not ids:
            raise RuntimeError("wait_for_component with no buttons")
        self.sim.waits += 1
        if self.sim.waits > self.sim.max_waits:
            raise asyncio.TimeoutError()
        cid = self.sim.choose(ids)
        for author in list(self.sim.users.values()):
            ev = FakeEvent(FakeCtx(author, self.sim.channel, cid))
            if check is None or check(ev):
                await _real_sleep(0)
                return ev
        raise RuntimeError(f"no author passes check for {cid}")

class Sim:
    def __init__(self, label):
        self.label = label; self.users = {}; self.channel = FakeChannel(); self.waits = 0; self.max_waits = 400
        self.bot = FakeBot(self)
    def choose(self, ids):
        def suffix(i): return i.split("|")[-1]
        start = [i for i in ids if suffix(i) == "start_game"]
        if start:
            r = random.random()
            if r < 0.03: return [i for i in ids if suffix(i) == "quit_game"][0]
            if r < 0.06:
                auto = [i for i in ids if suffix(i) == "start_game_auto_battle_mode"]
                if auto: return auto[0]
            if r < 0.08:
                sv = [i for i in ids if suffix(i) == "save_game"]
                if sv: return sv[0]
            return start[0]
        panel = ("more", "surrender_ask", "panel_close")
        moves = [i for i in ids if suffix(i) not in ("s", "q", "Q") + panel]
        if moves and any(suffix(i) in ("1", "2", "3", "4", "0", "5", "6", "b") for i in ids):
            r = random.random()
            if r < 0.004:
                q = [i for i in ids if suffix(i) in ("s", "q", "Q")]
                if q: return random.choice(q)
            elif r < 0.03:
                p = [i for i in ids if suffix(i) in panel]
                if p:
                    STATS["panel_clicks"] += 1
                    return random.choice(p)
            # prefer attacks, sometimes everything else
            weights = [5 if suffix(i) in ("1", "2", "3") else 2 for i in moves]
            return random.choices(moves, weights)[0]
        # results screens: rematch / continue / quit
        return random.choice(ids)

# ------------------------------------------------------------------ battles
def new_player(sim, did, name=None, card=None):
    doc = make_user_doc(did, name or f"P{did}", card)
    db.users_col.delete_many({"DID": did})
    db.users_col.insert_one(doc)
    sim.users[did] = FakeUser(did, name)
    p = crown_utilities.create_player_from_data(db.queryUser({"DID": did}))
    import stats as stats_mod
    if not db.query_stats_by_player(did):
        db.create_stats(stats_mod.create_initial_stats(p))
    return p

async def run_one(i, mode):
    sim = Sim(f"#{i} {mode}")
    did = str(100000 + i)
    p = new_player(sim, did)
    ctx = FakeCtx(sim.users[did], sim.channel)
    cfg = type("Cfg", (), {})()
    cfg.bot = sim.bot
    uni = random.choice(UNIVERSES)
    udoc = db.queryUniverse({"TITLE": uni})
    CURRENT["battle"] = f"{sim.label} card={p.equipped_card} univ={uni} diff={p.difficulty}"
    if mode in ("Tales", "Dungeon", "ATales", "ADungeon"):
        sel = {"SELECTED_UNIVERSE": uni, "UNIVERSE_DATA": udoc, "CREST_LIST": [], "CREST_SEARCH": False,
               "COMPLETED_TALES": [], "COMPLETED_DUNGEONS": [], "ASSOCIATION_INFO": "", "CURRENTOPPONENT": random.randint(0, 2)}
        b = Battle(mode, p); b.set_universe_selection_config(sel)
        await Play.battle_commands(cfg, ctx, b)
    elif mode == "Boss":
        sel = {"SELECTED_UNIVERSE": uni, "UNIVERSE_DATA": udoc, "CREST_LIST": [], "CREST_SEARCH": False, "COMPLETED_DUNGEONS": [],
               "ASSOCIATION_INFO": "", "BOSS_NAME": udoc["UNIVERSE_BOSS"], "CURRENTOPPONENT": 0}
        b = Battle(mode, p); b.set_universe_selection_config(sel)
        await Play.battle_commands(cfg, ctx, b)
    elif mode in ("PVP", "Tutorial"):
        if mode == "Tutorial":
            sim.users["837538366509154407"] = FakeUser("837538366509154407", "TutorialBot")
            opp = crown_utilities.create_tutorial_bot(db.queryUser({"DID": "837538366509154407"}))
            b = Battle("PVP", p); b.set_tutorial("837538366509154407"); b.mode = "PVP"
        else:
            opp = new_player(sim, str(900000 + i))
            b = Battle("PVP", p); b.is_pvp_game_mode = True; b.set_tutorial(opp.did)
        await Play.battle_commands(cfg, ctx, b, opp)
    elif mode == "Explore":
        b = Battle("EXPLORE", p)
        cards = [x for x in db.querySpecificDropCards(uni)]
        if not cards:
            cards = [CARDS[udoc["CROWN_TALES"][0]]]
        c = crown_utilities.create_card_from_data(random.choice(cards))
        c.set_affinity_message(); c.set_explore_bounty_and_difficulty(b)
        b.set_explore_config(udoc, c)
        await Play.battle_commands(cfg, ctx, b)
    elif mode == "Abyss":
        b = Battle("Abyss", p)
        b.set_abyss_config(p)
        if b.abyss_message and not b.list_of_opponents_by_name:
            return
        await Play.battle_commands(cfg, ctx, b)
    elif mode == "RPG":
        from cogs.classes.rpg_class import RPG
        from interactions import Embed as _E
        rpg = RPG(sim.bot, p, random.choice([None, uni, "Unbound"]) if p.explore_location != "NULL" else random.choice([uni, "Unbound"]))
        p.create_rpg_instance(rpg)
        rpg_msg = await ctx.send(embed=_E(title="Adventure is starting"))
        sim.max_waits = 300
        await rpg.create_rpg(ctx, rpg_msg)
        b = rpg
    elif mode == "Scenario":
        b = Battle("SCENARIO", p)
        b.selected_universe = uni
        b.set_scenario_config(db.queryScenario({"TITLE": f"{uni} Scenario"}))
        await Play.battle_commands(cfg, ctx, b)
    if mode == "RPG":
        STATS["battles"] += 1
        return
    STATS["battles"] += 1
    LONG.append((getattr(b, "turn_total", 0), getattr(b, "_actions_taken", 0), sim.waits, mode, CURRENT["battle"],
                 round(getattr(getattr(b, "player1_card", None), "health", -1) or -1), round(getattr(getattr(b, "player2_card", None), "health", -1) or -1)))
    STATS["turns"] += getattr(b, "turn_total", 0)
    STATS["max_turn"] = max(STATS["max_turn"], getattr(b, "turn_total", 0))

LONG = []
HITS = []
_orig_damage_done = Card.damage_done
def _track_damage_done(self, battle_config, dmg, opponent_card, *a, **kw):
    try:
        if dmg and not dmg.get("ENHANCE") and dmg.get("DMG") and getattr(opponent_card, "max_health", 0):
            HITS.append(100.0 * float(dmg["DMG"]) / float(opponent_card.max_health))
    except Exception:
        pass
    return _orig_damage_done(self, battle_config, dmg, opponent_card, *a, **kw)
Card.damage_done = _track_damage_done
ALL_MODES = ["Tales", "Dungeon", "Boss", "PVP", "Tutorial", "Explore", "Abyss", "Scenario", "ATales", "RPG"]

async def main():
    build_world()
    modes = MODES or ALL_MODES
    t0 = time.time()
    hangs = 0
    for i in range(N):
        mode = modes[i % len(modes)]
        try:
            await asyncio.wait_for(run_one(i, mode), timeout=float(os.environ.get("SIM_TIMEOUT", 60)))
        except asyncio.TimeoutError:
            hangs += 1
            _record("HANG", f"battle did not finish ({mode})", CURRENT["battle"])
        except Exception as ex:
            _record("HARNESS/escaped", f"{type(ex).__name__}: {ex}"[:200], "".join(traceback.format_exception(ex))[-3000:])
    dt = time.time() - t0
    builtins.print = _real_print
    print(f"\n=== {N} battles in {dt:.1f}s  stats={dict(STATS)} slept={SLEEPS[0]:.0f}s hangs={hangs}")
    print("COVER", dict(COVER))
    turns = sorted(row[0] for row in LONG if row[0])
    if turns:
        pct = lambda q: turns[min(len(turns) - 1, int(q * len(turns)))]
        print(f"TURNS per match: median {pct(0.5)}  p90 {pct(0.9)}  max {turns[-1]}  (n={len(turns)})")
    if HITS:
        h = sorted(HITS)
        pct = lambda q: h[min(len(h) - 1, int(q * len(h)))]
        print(f"HIT size (% of target max HP): median {pct(0.5):.1f}  p90 {pct(0.9):.1f}  p99 {pct(0.99):.1f}  max {h[-1]:.1f}  (n={len(h)})")
    for (n, where), c in DBCALLS.most_common(40):
        print(f"DB {c:6d} {n:32s} {where}")
    for row in sorted(LONG, reverse=True)[:int(os.environ.get("SIM_LONG", 0))]:
        print("LONG", row)
    for (kind, key), n in sorted(ERRORS.items(), key=lambda kv: (-{'CRASH':9,'HANG':8,'discord-400':7}.get(kv[0][0],0), -kv[1])):
        print(f"[{kind}] x{n}  {key}")
    if os.environ.get("SIM_DETAIL"):
        for (kind, key), (detail, where) in SAMPLES.items():
            if os.environ["SIM_DETAIL"] in key or os.environ["SIM_DETAIL"] == "all":
                print("-" * 80); print(kind, key); print("battle:", where); print(detail)

asyncio.run(main())
sys.exit(1 if any(kind in ("CRASH", "HANG", "HARNESS/escaped", "discord-400") for kind, _ in ERRORS) else 0)
