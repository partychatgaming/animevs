"""Local editor for the live gameplay database.

Run from the project folder:

    .venv/bin/python dashboard/app.py

Then open http://127.0.0.1:5055  (add --lan to open it from your phone on the
same Wi-Fi; see the bottom of this file).

Saves write straight to the Mongo database selected by ENV in .env. Card-art
uploads go to the Supabase bucket and the public link is stored on the card as
CARD_ART. Card pictures are drawn by the bot's own renderer, so they match Discord.
"""

import copy
import hashlib
import json
import os
import re
import secrets
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import db  # noqa: E402
from bson import ObjectId  # noqa: E402
from bson.errors import InvalidId  # noqa: E402
from flask import (  # noqa: E402
    Flask, Response, abort, flash, jsonify, redirect, render_template, request,
    send_from_directory, session, url_for,
)

from dashboard import cardviz  # noqa: E402
from dashboard.catalogs import (  # noqa: E402
    ARM_TYPE_EMOJI, ARM_TYPES, CARD_ENHANCERS, CATALOGS, CLASS_EMOJI, CLASSES, DROP_STYLES,
    ELEMENT_STYLES, ELEMENTS, ENHANCER_TYPES, SUMMON_TYPES, TITLE_ABILITIES, element_style,
    field_map, get_catalog,
)
from dashboard.images import host_card_art, rows_from_pairs, storage  # noqa: E402

app = Flask(__name__)
app.secret_key = os.environ.get("DASHBOARD_SECRET") or secrets.token_hex(32)
PER_PAGE = 36
FONT_DIR = ROOT / "fonts"
WEB_FONTS = {"KomikaTitle.ttf", "KomikaTitle-Paint.ttf", "Roboto-Black.ttf", "Roboto-Bold.ttf",
             "RobotoCondensed-Bold.ttf", "YesevaOne-Regular.ttf", "Jersey20-Regular.ttf"}


# --------------------------------------------------------------------------- helpers
def collection(catalog):
    return getattr(db, catalog["collection"])


def csrf_token():
    token = session.get("csrf")
    if not token:
        token = secrets.token_hex(16)
        session["csrf"] = token
    return token


def require_csrf():
    sent = request.form.get("csrf") or request.headers.get("X-CSRF")
    if not sent or sent != session.get("csrf"):
        abort(400, "This form expired. Reload the page and try again.")


_universe_cache = {"at": 0.0, "names": []}


def universe_names(fresh=False):
    if fresh or time.monotonic() - _universe_cache["at"] > 60:
        names = [u.get("TITLE") for u in db.universe_col.find({}, {"TITLE": 1}) if u.get("TITLE")]
        _universe_cache.update(at=time.monotonic(), names=sorted(names))
    return list(_universe_cache["names"])


def option_list(name, current=None):
    lists = {
        "universes": universe_names(),
        "classes": CLASSES,
        "drops": DROP_STYLES,
        "elements": [""] + ELEMENTS,
    }
    options = list(lists[name])
    if current not in (None, "") and current not in options:
        options.append(current)
    return options


def display(value):
    if isinstance(value, list):
        return str(len(value))
    if value is None:
        return ""
    return value


def find_doc(catalog, id_text):
    try:
        oid = ObjectId(id_text)
    except InvalidId:
        abort(404)
    doc = collection(catalog).find_one({"_id": oid})
    if doc is None:
        abort(404)
    return doc


def name_taken(catalog, name, exclude_id=None):
    query = {catalog["name"]: {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
    if exclude_id is not None:
        query["_id"] = {"$ne": exclude_id}
    return collection(catalog).count_documents(query) > 0


def parse_moves(form):
    count = int(form.get("move_count") or 0)
    moves = []
    for index in range(count):
        name = (form.get(f"m_name_{index}") or "").strip()
        if not name:
            continue
        try:
            power = int(float(form.get(f"m_power_{index}") or 0))
            stam = int(float(form.get(f"m_stam_{index}") or 0))
        except ValueError as exc:
            raise ValueError(f"Move {name}: power and stamina must be numbers.") from exc
        tag = form.get(f"m_tag_{index}") or "ELEMENT"
        if tag not in ("ELEMENT", "TYPE"):
            tag = "ELEMENT"
        value = (form.get(f"m_tagval_{index}") or "").strip()
        moves.append({name: power, "STAM": stam, tag: value})
    if not moves:
        raise ValueError("A card needs at least one move.")
    return moves


def moves_from_doc(doc):
    rows = []
    for move in doc.get("MOVESET") or []:
        if not isinstance(move, dict):
            continue
        name, power = "", 0
        tag, tag_value = "ELEMENT", ""
        if "TYPE" in move and "ELEMENT" not in move:
            tag, tag_value = "TYPE", move.get("TYPE") or ""
        elif "ELEMENT" in move:
            tag, tag_value = "ELEMENT", move.get("ELEMENT") or ""
        for key, value in move.items():
            if key not in ("STAM", "ELEMENT", "TYPE"):
                name, power = key, value
                break
        rows.append({
            "name": name,
            "power": power if power is not None else 0,
            "stam": move.get("STAM") or 0,
            "tag": tag,
            "tag_value": tag_value,
        })
    while len(rows) < 4:
        rows.append({"name": "", "power": 0, "stam": 10 if len(rows) == 0 else 20,
                     "tag": "TYPE" if len(rows) == 3 else "ELEMENT", "tag_value": ""})
    return rows


def coerce(field, raw, current):
    kind = field["type"]
    if kind == "bool":
        return raw in ("on", True, "true", "1", 1)
    if kind == "elements":
        if isinstance(raw, str):
            raw = [raw]
        return [str(item).strip().upper() for item in (raw or []) if str(item).strip()]
    if kind == "roster":
        if isinstance(raw, str):
            raw = [part.strip() for part in raw.splitlines() if part.strip()]
        return [str(item).strip() for item in (raw or []) if str(item).strip()]
    if kind == "json" and isinstance(raw, (list, dict)):
        return raw
    if kind == "list" and isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    text = ("" if raw is None else str(raw)).strip()
    if kind in ("str", "url"):
        if kind == "url" and text and not text.lower().startswith(("http://", "https://", "n/a")):
            raise ValueError(f"{field['label']} must be an http(s) link.")
        return text
    if kind == "int":
        if text == "":
            return current if current is not None else 0
        try:
            return int(float(text))
        except ValueError as exc:
            raise ValueError(f"{field['label']} must be a whole number.") from exc
    if kind == "float":
        if text == "":
            return current if current is not None else 0
        try:
            number = float(text)
        except ValueError as exc:
            raise ValueError(f"{field['label']} must be a number.") from exc
        return int(number) if number.is_integer() and isinstance(current, int) else number
    if kind == "list":
        if not text:
            return []
        return [part.strip() for part in text.splitlines() if part.strip()]
    if kind == "json":
        if not text:
            return [] if isinstance(current, list) else {}
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{field['label']} is not valid JSON ({exc.msg}).") from exc
    if kind == "select":
        return text
    raise ValueError(f"Unknown field {field['key']}")


def presented(doc, field):
    value = doc.get(field["key"])
    kind = field["type"]
    if kind == "bool":
        return bool(value)
    if kind in ("elements", "roster"):
        if isinstance(value, str):
            return [part.strip() for part in value.splitlines() if part.strip()]
        if isinstance(value, list):
            items = [str(item).strip() for item in value if str(item or "").strip()]
            return [item.upper() for item in items] if kind == "elements" else items
        return []
    if kind == "list":
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "\n".join("" if item is None else str(item) for item in value)
        return ""
    if kind == "json":
        if isinstance(value, str):
            return value
        if value is None:
            value = []
        return json.dumps(value, indent=2, default=str)
    if value is None:
        return ""
    return value


def doc_from_form(catalog_key, catalog, doc, form, strict=True):
    """The record as the editor form describes it. Raises ValueError when strict."""
    update = {}
    for field in catalog["fields"]:
        if field.get("identity") and form.get("allow_rename") != "on":
            continue
        raw = form.getlist(field["key"]) if field["type"] in ("elements", "roster") else form.get(field["key"])
        if raw is None and field["type"] not in ("bool", "elements", "roster"):
            continue
        try:
            update[field["key"]] = coerce(field, raw, doc.get(field["key"]))
        except ValueError:
            if strict:
                raise
    if catalog_key == "cards" and "move_count" in form:
        try:
            update["MOVESET"] = parse_moves(form)
        except ValueError:
            if strict:
                raise
    return update


def art_url(doc):
    return doc.get("CARD_ART") or doc.get("PATH") or ""


def short_number(value):
    try:
        n = round(float(value))
    except (TypeError, ValueError):
        return str(value or "")
    if abs(n) < 10_000:
        return f"{n:,}"
    if abs(n) < 1_000_000:
        return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "K"
    return f"{n / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"


def ability_summary(catalog_key, doc):
    """[(emoji, text)] describing what the record does in battle."""
    out = []
    abilities = doc.get("ABILITIES") or []
    if not isinstance(abilities, list):
        return out
    for ability in abilities[:3]:
        if not isinstance(ability, dict):
            continue
        if catalog_key == "titles":
            kind = ability.get("ABILITY") or next(iter(ability), "")
            power = ability.get("POWER", ability.get(kind, ""))
            element = ability.get("ELEMENT") or ""
            text = f"{kind} {power}".strip()
            if element:
                text += f" · {element.title()}"
            if ability.get("DURATION"):
                text += f" · {ability['DURATION']} turns"
            out.append(("✨", text))
        elif catalog_key == "arms":
            for key, value in ability.items():
                out.append((ARM_TYPE_EMOJI.get(str(key).upper(), element_style(key)["emoji"]), f"{key} {value}"))
                break
        elif catalog_key == "summons":
            kind = ability.get("TYPE", "")
            for key, value in ability.items():
                if key != "TYPE":
                    out.append((element_style(kind)["emoji"], f"{key} {value} · {kind}"))
                    break
    return out


def tile(catalog_key, catalog, doc):
    """Everything the gallery and 3D views need to draw one record."""
    doc_id = str(doc["_id"])
    name = doc.get(catalog["name"]) or "Untitled"
    universe = doc.get("UNIVERSE") or (name if catalog_key == "universes" else "")
    item = {
        "id": doc_id,
        "name": name,
        "universe": universe if catalog_key != "universes" else "",
        "available": doc.get("AVAILABLE", True) is not False,
        "edit": url_for("edit", catalog_key=catalog_key, doc_id=doc_id),
        "accent": cardviz.universe_accent(universe),
        "chips": [],
        "stats": [],
        "abilities": [],
        "image": "",
        "render": "",
    }
    if catalog_key == "cards":
        kind = cardviz.card_type(doc)
        style = element_style(kind)
        item["type"] = style
        version = cardviz.render_key(doc)
        item["render"] = url_for("card_render_img", doc_id=doc_id, w=480, v=version)
        item["render_full"] = url_for("card_render_img", doc_id=doc_id, v=version)
        tier = doc.get("TIER") or 1
        item["chips"] = [
            f"{'★' * min(int(float(tier or 1)), 10)}",
            f"{CLASS_EMOJI.get(str(doc.get('CLASS', '')).upper(), '')} {str(doc.get('CLASS', '')).title()}".strip(),
            f"{style['emoji']} {style['key'].title() or 'No type'}",
        ]
        item["stats"] = [("HP", short_number(doc.get("HLT")), "hp"), ("ATK", short_number(doc.get("ATK")), "atk"),
                         ("DEF", short_number(doc.get("DEF")), "def")]
        item["has_art"] = bool(doc.get("CARD_ART"))
    else:
        element = doc.get("ELEMENT") or ""
        if catalog_key == "arms" and not element:
            first = (doc.get("ABILITIES") or [{}])[0]
            element = next(iter(first), "") if isinstance(first, dict) else ""
        style = element_style(element)
        item["type"] = style
        item["abilities"] = ability_summary(catalog_key, doc)
        image_field = catalog.get("image")
        if image_field and doc.get(image_field):
            version = hashlib.sha1(str(doc.get(image_field)).encode()).hexdigest()[:10]
            item["image"] = url_for("record_art", catalog_key=catalog_key, doc_id=doc_id, v=version)
        for label, key in catalog["columns"][2:4]:
            value = doc.get(key)
            if value not in (None, "", []):
                item["stats"].append((label, display(value), ""))
        if doc.get("DROP_STYLE"):
            item["chips"].append(str(doc["DROP_STYLE"]).title())
        if element:
            item["chips"].append(f"{style['emoji']} {str(element).title()}")
        if doc.get("RARITY"):
            item["chips"].append(str(doc["RARITY"]).title())
    return item


def quick_spec(catalog_key, catalog, doc):
    fields = field_map(catalog)
    spec = []
    for key in catalog.get("quick", []):
        field = dict(fields[key])
        field["value"] = presented(doc, field)
        if field["type"] == "json":
            raw = doc.get(key)
            field["raw"] = raw if isinstance(raw, (list, dict)) else []
        if field["type"] == "select":
            field["choices"] = option_list(field["options"], doc.get(key))
        spec.append(field)
    return spec


def builder_options():
    return {
        "elements": ELEMENTS,
        "arm_types": ARM_TYPES,
        "title_abilities": TITLE_ABILITIES,
        "summon_types": SUMMON_TYPES,
        "enhancers": CARD_ENHANCERS,
        "styles": {key: {"emoji": e, "color": c, "glow": g} for key, (e, c, g) in ELEMENT_STYLES.items()},
        "arm_emoji": ARM_TYPE_EMOJI,
    }


@app.context_processor
def inject():
    return {"csrf": csrf_token(), "catalogs": CATALOGS, "database": db.use_database,
            "builder": builder_options(), "element_style": element_style, "all_universes": universe_names()}


@app.template_filter("short")
def _short(value):
    return short_number(value)


# --------------------------------------------------------------------------- assets
@app.get("/fonts/<name>")
def font(name):
    if name not in WEB_FONTS:
        abort(404)
    response = send_from_directory(FONT_DIR, name, mimetype="font/ttf")
    response.cache_control.max_age = 86400 * 7
    return response


def _image_response(data, immutable):
    response = Response(data, mimetype="image/jpeg")
    if immutable:
        response.cache_control.max_age = 86400 * 30
        response.cache_control.immutable = True
    else:
        response.cache_control.no_cache = True
    return response


@app.get("/cards/<doc_id>/render.jpg")
def card_render_img(doc_id):
    doc = find_doc(CATALOGS["cards"], doc_id)
    width = request.args.get("w", type=int)
    width = max(120, min(width, 720)) if width else None
    try:
        data = cardviz.render_card(doc, width)
    except RuntimeError as exc:
        abort(503, str(exc))
    return _image_response(data, immutable=request.args.get("v") == cardviz.render_key(doc))


@app.post("/cards/<doc_id>/preview.jpg")
def card_preview_img(doc_id):
    """Render the card as the editor form currently describes it, without saving."""
    require_csrf()
    catalog = CATALOGS["cards"]
    doc = find_doc(catalog, doc_id)
    draft = dict(doc)
    draft.update(doc_from_form("cards", catalog, doc, request.form, strict=False))
    if request.form.get("NAME"):
        draft["NAME"] = request.form.get("NAME")
    try:
        data = cardviz.render_card(draft, 540)
    except RuntimeError as exc:
        abort(503, str(exc))
    return _image_response(data, immutable=False)


@app.get("/art/<catalog_key>/<doc_id>.jpg")
def record_art(catalog_key, doc_id):
    catalog = get_catalog(catalog_key)
    if catalog is None or not catalog.get("image"):
        abort(404)
    doc = find_doc(catalog, doc_id)
    url = doc.get(catalog["image"])
    data = cardviz.render_image(url, width=request.args.get("w", 640, type=int)) if url else None
    if data is None:
        abort(404)
    return _image_response(data, immutable=bool(request.args.get("v")))


# --------------------------------------------------------------------------- stats
_stats_cache = {}


def _cached_stats(key, builder):
    hit = _stats_cache.get(key)
    if hit and time.monotonic() - hit[0] < 60:
        return hit[1]
    value = builder()
    _stats_cache[key] = (time.monotonic(), value)
    return value


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def card_stats(universe=""):
    query = {"UNIVERSE": universe} if universe else {}
    fields = ["NAME", "UNIVERSE", "CLASS", "TIER", "HLT", "ATK", "DEF", "SPD", "PRICE", "DROP_STYLE",
              "AVAILABLE", "MOVESET", "CARD_ART", "WEAKNESS", "RESISTANT", "IMMUNE", "REPEL", "ABSORB"]
    docs = list(db.cards_col.find(query, {key: 1 for key in fields}))
    by_universe, by_class, by_type, by_drop, by_tier = Counter(), Counter(), Counter(), Counter(), Counter()
    tier_sums = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])
    affinity = {el: {"WEAKNESS": 0, "RESISTANT": 0, "IMMUNE": 0, "REPEL": 0, "ABSORB": 0} for el in ELEMENTS}
    scatter, ultimates = [], []
    available = with_art = 0
    for doc in docs:
        tier = max(1, min(10, int(_num(doc.get("TIER")) or 1)))
        kind = cardviz.card_type(doc) or "NONE"
        by_universe[doc.get("UNIVERSE") or "?"] += 1
        by_class[str(doc.get("CLASS") or "?").upper()] += 1
        by_type[kind] += 1
        by_drop[str(doc.get("DROP_STYLE") or "?").upper()] += 1
        by_tier[tier] += 1
        available += doc.get("AVAILABLE", False) is True
        with_art += bool(doc.get("CARD_ART"))
        ult = 0
        moves = doc.get("MOVESET") or []
        if len(moves) >= 3 and isinstance(moves[2], dict):
            ult = next((_num(v) for k, v in moves[2].items() if k not in ("STAM", "ELEMENT", "TYPE")), 0)
            ultimates.append(ult)
        sums = tier_sums[tier]
        sums[0] += 1
        sums[1] += _num(doc.get("HLT"))
        sums[2] += _num(doc.get("ATK"))
        sums[3] += _num(doc.get("DEF"))
        sums[4] += ult
        for key in affinity.get("FIRE", {}):
            for element in doc.get(key) or []:
                element = str(element).upper()
                if element in affinity:
                    affinity[element][key] += 1
        if len(scatter) < 2500:
            scatter.append({"id": str(doc["_id"]), "n": doc.get("NAME"), "u": doc.get("UNIVERSE"),
                            "a": _num(doc.get("ATK")), "d": _num(doc.get("DEF")), "h": _num(doc.get("HLT")),
                            "t": tier, "c": str(doc.get("CLASS") or "").upper(), "k": kind})
    tiers = []
    for tier in range(1, 11):
        count, hp, atk, dfn, ult = tier_sums.get(tier, [0, 0, 0, 0, 0])
        tiers.append({"tier": tier, "count": count,
                      "hp": round(hp / count) if count else 0, "atk": round(atk / count) if count else 0,
                      "def": round(dfn / count) if count else 0, "ult": round(ult / count) if count else 0})
    return {
        "total": len(docs), "available": available, "with_art": with_art,
        "by_universe": by_universe.most_common(30),
        "by_class": by_class.most_common(),
        "by_type": by_type.most_common(),
        "by_drop": by_drop.most_common(),
        "by_tier": [[t, by_tier.get(t, 0)] for t in range(1, 11)],
        "tiers": tiers,
        "affinity": affinity,
        "scatter": scatter,
        "ultimates": ultimates,
    }


def gear_stats(universe=""):
    query = {"UNIVERSE": universe} if universe else {}
    titles, arms, summons = Counter(), Counter(), Counter()
    arm_elements, title_universes, arm_universes = Counter(), Counter(), Counter()
    for doc in db.titles_col.find(query, {"ABILITIES": 1, "UNIVERSE": 1}):
        title_universes[doc.get("UNIVERSE") or "?"] += 1
        for ability in doc.get("ABILITIES") or []:
            if isinstance(ability, dict):
                titles[str(ability.get("ABILITY") or next(iter(ability), "?")).upper()] += 1
    for doc in db.arm_col.find(query, {"ABILITIES": 1, "ELEMENT": 1, "UNIVERSE": 1}):
        arm_universes[doc.get("UNIVERSE") or "?"] += 1
        first = (doc.get("ABILITIES") or [{}])[0]
        if isinstance(first, dict) and first:
            arms[str(next(iter(first))).upper()] += 1
        if doc.get("ELEMENT"):
            arm_elements[str(doc["ELEMENT"]).upper()] += 1
    for doc in db.pet_col.find(query, {"ABILITIES": 1}):
        first = (doc.get("ABILITIES") or [{}])[0]
        if isinstance(first, dict):
            summons[str(first.get("TYPE") or "?").upper()] += 1
    return {
        "title_abilities": titles.most_common(),
        "arm_types": arms.most_common(),
        "arm_elements": arm_elements.most_common(),
        "summon_types": summons.most_common(),
        "title_universes": title_universes.most_common(15),
        "arm_universes": arm_universes.most_common(15),
    }


def showcase_cards(limit=10):
    pipeline = [{"$match": {"CARD_ART": {"$nin": [None, ""]}}}, {"$sample": {"size": limit}}]
    try:
        docs = list(db.cards_col.aggregate(pipeline))
    except Exception:
        docs = []
    if len(docs) < limit:
        seen = {doc["_id"] for doc in docs}
        for doc in db.cards_col.find({}).limit(limit * 2):
            if doc["_id"] not in seen and len(docs) < limit:
                docs.append(doc)
    return [tile("cards", CATALOGS["cards"], doc) for doc in docs]


# --------------------------------------------------------------------------- pages
@app.get("/")
def home():
    counts = []
    for key, catalog in CATALOGS.items():
        counts.append({"key": key, "label": catalog["label"], "blurb": catalog["blurb"], "icon": catalog["icon"],
                       "color": catalog["color"], "count": collection(catalog).estimated_document_count()})
    stats = _cached_stats("cards:", lambda: card_stats(""))
    return render_template("home.html", counts=counts, showcase=showcase_cards(),
                           mini={k: stats[k] for k in ("by_tier", "by_type", "by_universe", "total",
                                                       "available", "with_art")})


@app.get("/stats")
def stats_page():
    universe = (request.args.get("universe") or "").strip()
    cards = _cached_stats(f"cards:{universe}", lambda: card_stats(universe))
    gear = _cached_stats(f"gear:{universe}", lambda: gear_stats(universe))
    return render_template("stats.html", cards=cards, gear=gear, universe=universe, universes=universe_names(),
                           class_emoji=CLASS_EMOJI)


@app.get("/<catalog_key>")
def listing(catalog_key):
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    args = request.args
    query_text = (args.get("q") or "").strip()
    universe = (args.get("universe") or "").strip()
    view = args.get("view") or ("grid" if catalog_key != "titles" else "grid")
    if view not in ("grid", "table", "3d"):
        view = "grid"
    page = max(args.get("page", 1, type=int) or 1, 1)
    sort = args.get("sort") or catalog["sort"]
    if sort not in {key for key, _ in catalog.get("sorts", [])}:
        sort = catalog["sort"]
    query = {}
    if universe and catalog["universe"]:
        query[catalog["universe"]] = universe
    if query_text:
        query[catalog["name"]] = {"$regex": re.escape(query_text), "$options": "i"}
    filters = {"cls": args.get("cls", ""), "tier": args.get("tier", ""), "type": args.get("type", ""),
               "avail": args.get("avail", ""), "art": args.get("art", "")}
    if catalog_key == "cards":
        if filters["cls"]:
            query["CLASS"] = filters["cls"]
        if filters["tier"]:
            try:
                query["TIER"] = {"$in": [int(filters["tier"]), float(filters["tier"])]}
            except ValueError:
                pass
        if filters["type"]:
            query["MOVESET.2.ELEMENT"] = filters["type"]
        if filters["art"] == "art":
            query["CARD_ART"] = {"$nin": [None, ""]}
        elif filters["art"] == "none":
            query["CARD_ART"] = {"$in": [None, ""]}
    if filters["avail"] in ("1", "0"):
        query["AVAILABLE"] = filters["avail"] == "1"
    col = collection(catalog)
    total = col.count_documents(query)
    per_page = PER_PAGE if view != "table" else 60
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(page, pages)
    direction = -1 if sort.startswith("-") else 1
    sort_key = sort.lstrip("-")
    docs = list(col.find(query).sort([(sort_key, direction), (catalog["name"], 1)])
                .skip((page - 1) * per_page).limit(per_page))
    rows, tiles = [], []
    for doc in docs:
        cells = [display(doc.get(key)) for label, key in catalog["columns"]]
        rows.append({"id": str(doc["_id"]), "cells": cells, "available": doc.get("AVAILABLE", True) is not False})
        tiles.append(tile(catalog_key, catalog, doc))
    params = {k: v for k, v in {"q": query_text, "universe": universe, "sort": sort if sort != catalog["sort"] else "",
                                "view": view if view != "grid" else "", **filters}.items() if v}
    return render_template(
        "list.html", catalog_key=catalog_key, catalog=catalog, rows=rows, tiles=tiles, total=total,
        page=page, pages=pages, q=query_text, universe=universe, universes=universe_names(),
        view=view, sort=sort, filters=filters, params=params, classes=CLASSES, elements=ELEMENTS,
        class_emoji=CLASS_EMOJI,
        editable={f["key"] for f in catalog["fields"]
                  if f["key"] in catalog.get("quick", []) and f["type"] in ("int", "float", "str")},
    )


@app.get("/<catalog_key>/<doc_id>")
def edit(catalog_key, doc_id):
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    doc = find_doc(catalog, doc_id)
    return render_template("edit.html", **editor_context(catalog_key, catalog, doc))


def editor_context(catalog_key, catalog, doc, moves=None):
    fields = []
    for field in catalog["fields"]:
        shown = dict(field)
        shown["value"] = presented(doc, field)
        if field["type"] == "select":
            shown["choices"] = option_list(field["options"], doc.get(field["key"]))
        if field["type"] == "elements":
            selected = shown["value"] if isinstance(shown["value"], list) else []
            extras = [item for item in selected if item not in ELEMENTS]
            shown["choices"] = ELEMENTS + extras
            shown["selected"] = set(selected)
        fields.append(shown)
    groups = []
    for field in fields:
        name = field.get("group", "Details")
        if not groups or groups[-1]["name"] != name:
            existing = next((g for g in groups if g["name"] == name), None)
            if existing:
                existing["fields"].append(field)
                continue
            groups.append({"name": name, "fields": []})
        groups[-1]["fields"].append(field)
    return {
        "catalog_key": catalog_key,
        "catalog": catalog,
        "doc": doc,
        "doc_id": str(doc["_id"]),
        "fields": fields,
        "groups": groups,
        "tile": tile(catalog_key, catalog, doc) if "_id" in doc else None,
        "moves": moves if moves is not None else (moves_from_doc(doc) if catalog_key == "cards" else None),
        "elements": ELEMENTS,
        "enhancers": ENHANCER_TYPES,
        "art": art_url(doc) if catalog_key == "cards" else "",
        "previous_art": doc.get("CARD_ART_PREV") or "",
    }


@app.post("/<catalog_key>/<doc_id>")
def save(catalog_key, doc_id):
    require_csrf()
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    doc = find_doc(catalog, doc_id)
    try:
        update = doc_from_form(catalog_key, catalog, doc, request.form)
        new_name = update.get(catalog["name"])
        if new_name is not None and new_name != doc.get(catalog["name"]):
            if not new_name:
                raise ValueError("The name cannot be blank.")
            if name_taken(catalog, new_name, exclude_id=doc["_id"]):
                raise ValueError(f"Another record is already called {new_name}.")
        if catalog_key == "cards" and request.form.get("host_art") == "on":
            link = update.get("CARD_ART") or doc.get("CARD_ART")
            if not link:
                raise ValueError("Add a card art link before hosting it.")
            store, problem = storage()
            if problem:
                raise ValueError(problem)
            hosted = host_card_art(collection(catalog), {**doc, "NAME": update.get("NAME", doc["NAME"]),
                                                         "UNIVERSE": update.get("UNIVERSE", doc.get("UNIVERSE"))}, link, store)
            update["CARD_ART"] = hosted
            update.pop("CARD_ART_CROP", None)
    except ValueError as exc:
        flash(str(exc), "error")
        posted = dict(doc)
        for field in catalog["fields"]:
            if field["type"] == "bool":
                posted[field["key"]] = request.form.get(field["key"]) == "on"
            elif field["type"] in ("elements", "roster"):
                posted[field["key"]] = request.form.getlist(field["key"])
            elif field["key"] in request.form:
                posted[field["key"]] = request.form.get(field["key"])
        moves = None
        if catalog_key == "cards":
            moves = []
            for index in range(int(request.form.get("move_count") or 0)):
                moves.append({
                    "name": request.form.get(f"m_name_{index}") or "",
                    "power": request.form.get(f"m_power_{index}") or 0,
                    "stam": request.form.get(f"m_stam_{index}") or 0,
                    "tag": request.form.get(f"m_tag_{index}") or "ELEMENT",
                    "tag_value": request.form.get(f"m_tagval_{index}") or "",
                })
        return render_template("edit.html", **editor_context(catalog_key, catalog, posted, moves)), 400

    collection(catalog).update_one({"_id": doc["_id"]}, {"$set": update})
    _stats_cache.clear()
    flash(f"Saved {update.get(catalog['name'], doc.get(catalog['name']))}.", "ok")
    return redirect(url_for("edit", catalog_key=catalog_key, doc_id=doc_id))


# --------------------------------------------------------------------------- create / duplicate
def new_record(catalog_key, name, universe):
    import classes
    universe = universe or "Unbound"
    if catalog_key == "cards":
        doc = classes.newCard({"NAME": name, "PATH": ""})
        doc.update({
            "UNIVERSE": universe, "CLASS": "FIGHTER", "DROP_STYLE": "TALES", "RNAME": name,
            "FPATH": "", "RPATH": "", "HLT": 1500, "ATK": 50, "DEF": 50, "BASEATK": 50, "BASEDEF": 50,
            "SPD": 50, "STOCK": 5, "CARD_ART": "",
            "MOVESET": [
                {f"{name} Strike": 60, "STAM": 10, "ELEMENT": "PHYSICAL"},
                {f"{name} Special": 140, "STAM": 30, "ELEMENT": "PHYSICAL"},
                {f"{name} Ultimate": 260, "STAM": 80, "ELEMENT": "PHYSICAL"},
                {f"{name} Boost": 0, "STAM": 20, "TYPE": "ATK"},
            ],
        })
    elif catalog_key == "titles":
        doc = classes.newTitle({"TITLE": name, "UNIVERSE": universe})
        doc.update({"ABILITIES": [{"ABILITY": "ATK", "POWER": 10, "ELEMENT": "", "DURATION": 0}],
                    "ELEMENT": "", "RARITY": "COMMON", "METHOD": "", "VALUE": 0, "SCENARIO_DROP": False})
    elif catalog_key == "arms":
        doc = classes.newArm({"ARM": name, "UNIVERSE": universe})
        doc.update({"ABILITIES": [{"BASIC": 20}], "DROP_STYLE": "TALES"})
    elif catalog_key == "summons":
        doc = classes.newPet({"PET": name, "UNIVERSE": universe})
        doc.update({"ABILITIES": [{f"{name} Strike": 20, "TYPE": "PHYSICAL"}], "DROP_STYLE": "TALES",
                    "AVAILABLE": False})
    elif catalog_key == "universes":
        doc = classes.newUniverse({"TITLE": name})
        doc.update({"AVAILABLE": False, "CROWN_TALES": [], "DUNGEONS": []})
    elif catalog_key == "bosses":
        doc = classes.newBoss({"NAME": name, "UNIVERSE": universe})
        doc.update({"AVAILABLE": False, "DESCRIPTION": []})
    elif catalog_key == "scenarios":
        doc = classes.newScenario({"TITLE": name, "UNIVERSE": universe})
        doc.update({"AVAILABLE": False, "ENEMIES": [], "EASY_DROPS": [], "NORMAL_DROPS": [], "HARD_DROPS": []})
    else:
        abort(404)
    return doc


@app.post("/new/<catalog_key>")
def create(catalog_key):
    require_csrf()
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    name = (request.form.get("name") or "").strip()
    universe = (request.form.get("universe") or "").strip()
    if not name:
        flash("Give it a name first.", "error")
        return redirect(url_for("listing", catalog_key=catalog_key))
    if name_taken(catalog, name):
        flash(f"{catalog['label'][:-1]} {name} already exists.", "error")
        return redirect(url_for("listing", catalog_key=catalog_key, q=name))
    doc = new_record(catalog_key, name, universe)
    result = collection(catalog).insert_one(doc)
    _stats_cache.clear()
    universe_names(fresh=catalog_key == "universes")
    flash(f"Created {name}. It starts unavailable so players can't get it until you switch it on.", "ok")
    return redirect(url_for("edit", catalog_key=catalog_key, doc_id=str(result.inserted_id)))


@app.post("/<catalog_key>/<doc_id>/duplicate")
def duplicate(catalog_key, doc_id):
    require_csrf()
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    doc = find_doc(catalog, doc_id)
    base = (request.form.get("name") or "").strip() or f"{doc.get(catalog['name'])} Copy"
    name, number = base, 2
    while name_taken(catalog, name):
        name = f"{base} {number}"
        number += 1
    clone = copy.deepcopy({k: v for k, v in doc.items() if k not in ("_id", "CARD_ART_PREV")})
    clone[catalog["name"]] = name
    clone["AVAILABLE"] = False
    if catalog_key == "cards":
        clone["RNAME"] = name
    result = collection(catalog).insert_one(clone)
    _stats_cache.clear()
    flash(f"Duplicated as {name} (unavailable until you switch it on).", "ok")
    return redirect(url_for("edit", catalog_key=catalog_key, doc_id=str(result.inserted_id)))


@app.get("/lookup/cards")
def lookup_cards():
    """Card names for the tale and dungeon lists. Stays inside one universe unless asked."""
    text = (request.args.get("q") or "").strip()
    universe = (request.args.get("universe") or "").strip()
    query = {}
    if universe and request.args.get("all") != "1":
        query["UNIVERSE"] = universe
    if text:
        query["NAME"] = {"$regex": re.escape(text), "$options": "i"}
    docs = db.cards_col.find(query, {"NAME": 1, "UNIVERSE": 1, "CLASS": 1}).sort("NAME", 1).limit(40)
    return jsonify([
        {"name": doc.get("NAME") or "", "universe": doc.get("UNIVERSE") or "", "class": doc.get("CLASS") or ""}
        for doc in docs if doc.get("NAME")
    ])


# --------------------------------------------------------------------------- quick edit API
@app.get("/api/<catalog_key>/<doc_id>")
def api_get(catalog_key, doc_id):
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    doc = find_doc(catalog, doc_id)
    return jsonify({"tile": tile(catalog_key, catalog, doc), "fields": quick_spec(catalog_key, catalog, doc),
                    "builder": catalog_key if catalog_key in ("titles", "arms", "summons") else None})


@app.patch("/api/<catalog_key>/<doc_id>")
def api_patch(catalog_key, doc_id):
    require_csrf()
    catalog = get_catalog(catalog_key)
    if catalog is None:
        abort(404)
    doc = find_doc(catalog, doc_id)
    payload = request.get_json(silent=True) or {}
    fields = field_map(catalog)
    update, errors = {}, []
    for key, raw in payload.items():
        field = fields.get(key)
        if field is None or field.get("identity"):
            errors.append(f"{key} can't be changed here.")
            continue
        try:
            update[key] = coerce(field, raw, doc.get(key))
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    if update:
        collection(catalog).update_one({"_id": doc["_id"]}, {"$set": update})
        _stats_cache.clear()
        doc.update(update)
    return jsonify({"ok": True, "tile": tile(catalog_key, catalog, doc)})


# --------------------------------------------------------------------------- card images (bulk)
@app.post("/cards/<doc_id>/restore-art")
def restore_art(doc_id):
    require_csrf()
    catalog = get_catalog("cards")
    doc = find_doc(catalog, doc_id)
    previous = doc.get("CARD_ART_PREV")
    if not previous:
        flash("This card has no previous art to restore.", "error")
        return redirect(url_for("edit", catalog_key="cards", doc_id=doc_id))
    collection(catalog).update_one(
        {"_id": doc["_id"]},
        {"$set": {"CARD_ART": previous}, "$unset": {"CARD_ART_PREV": ""}},
    )
    flash("Restored the previous card art.", "ok")
    return redirect(url_for("edit", catalog_key="cards", doc_id=doc_id))


def image_entries(universe):
    if not universe:
        return [{"name": "", "url": "", "current": ""}]
    docs = db.cards_col.find({"UNIVERSE": universe}, {"NAME": 1, "CARD_ART": 1, "PATH": 1}).sort("NAME", 1)
    return [{"name": doc["NAME"], "url": "", "current": art_url(doc)} for doc in docs]


def posted_entries(universe):
    names = request.form.getlist("name")
    urls = request.form.getlist("url")
    entries = [{"name": (name or "").strip(), "url": (url or "").strip(), "current": ""} for name, url in zip(names, urls)]
    if not entries:
        return image_entries(universe)
    for entry in entries:
        if not entry["name"]:
            continue
        query = {"NAME": {"$regex": f"^{re.escape(entry['name'])}$", "$options": "i"}}
        if universe:
            query["UNIVERSE"] = universe
        doc = db.cards_col.find_one(query, {"CARD_ART": 1, "PATH": 1})
        entry["current"] = art_url(doc) if doc else ""
    return entries


def render_images(universe, entries, preview=None, results=None, storage_ready=None, storage_problem=None, bucket="card-art"):
    if storage_ready is None:
        store, storage_problem = storage()
        storage_ready = store is not None
        bucket = store.bucket if store else bucket
    return render_template(
        "images.html", universes=universe_names(), universe=universe, entries=entries,
        storage_ready=storage_ready, storage_problem=storage_problem, bucket=bucket,
        preview=preview, results=results,
    )


@app.get("/images")
def images():
    universe = (request.args.get("universe") or "").strip()
    return render_images(universe, image_entries(universe))


@app.get("/images/preview")
def images_preview_get():
    return redirect(url_for("images", universe=(request.args.get("universe") or "").strip()))


@app.post("/images/preview")
def images_preview():
    require_csrf()
    universe = (request.form.get("universe") or "").strip()
    entries = posted_entries(universe)
    rows, errors = rows_from_pairs(request.form.getlist("name"), request.form.getlist("url"))
    preview = match_rows(rows, errors, universe)
    return render_images(universe, entries, preview=preview)


@app.post("/images/apply")
def images_apply():
    require_csrf()
    universe = (request.form.get("universe") or "").strip()
    entries = posted_entries(universe)
    rows, errors = rows_from_pairs(request.form.getlist("name"), request.form.getlist("url"))
    preview = match_rows(rows, errors, universe)
    store, problem = storage()
    if problem:
        flash(problem, "error")
        return render_images(universe, entries, preview=preview, storage_ready=False, storage_problem=problem)
    try:
        store.ensure_bucket()
    except RuntimeError as exc:
        flash(str(exc), "error")
        return render_images(universe, entries, preview=preview, storage_ready=False, storage_problem=str(exc))
    results = []
    saved = 0
    for item in preview["matched"]:
        try:
            link = host_card_art(db.cards_col, item["card"], item["url"], store)
            saved += 1
            results.append({"name": item["card"]["NAME"], "status": "saved", "link": link, "source": item["url"]})
        except Exception as exc:
            results.append({"name": item["card"]["NAME"], "status": "failed", "link": "", "source": item["url"],
                            "error": str(exc)[:240]})
    flash(f"Saved art for {saved} of {len(preview['matched'])} matched cards.", "ok" if saved else "error")
    return render_images(
        universe, entries, preview=preview, results=results,
        storage_ready=True, storage_problem=None, bucket=store.bucket,
    )


def match_rows(rows, errors, universe):
    matched, unmatched = [], list(errors)
    seen = {}
    for row in rows:
        key = row["name"].casefold()
        if key in seen:
            unmatched.append({"line": row["line"], "text": row["name"], "error": "Duplicate name in this list; the earlier line is used."})
            continue
        seen[key] = row
        query = {"NAME": {"$regex": f"^{re.escape(row['name'])}$", "$options": "i"}}
        if universe:
            query["UNIVERSE"] = universe
        found = list(db.cards_col.find(query, {"NAME": 1, "UNIVERSE": 1, "CARD_ART": 1, "PATH": 1}))
        if len(found) != 1:
            reason = "No card with that name" if not found else "More than one card has that name. Pick a universe."
            if universe and not found:
                reason = f"No card named that in {universe}"
            unmatched.append({"line": row["line"], "text": row["name"], "error": reason})
            continue
        matched.append({"line": row["line"], "url": row["url"], "card": found[0], "current": art_url(found[0])})
    return {"matched": matched, "unmatched": unmatched}


# --------------------------------------------------------------------------- play in the browser
# The real bot commands run through dashboard/play_bridge.py, so battles, rewards,
# wins and losses are written by the same code as on Discord.
PLAY_MODES = [
    {"key": "Tutorial", "label": "Tutorial", "blurb": "Learn the battle buttons against a training bot.", "icon": "🆘", "color": "#77d4ff", "universe": False},
    {"key": "Tales", "label": "Tales run", "blurb": "Fight through a universe's tale opponents in order.", "icon": "⚔️", "color": "#f06014", "universe": True},
    {"key": "Dungeon", "label": "Dungeon run", "blurb": "Harder opponents, bigger drops.", "icon": "👺", "color": "#be1428", "universe": True},
    {"key": "Scenario", "label": "Scenario", "blurb": "Story battles with fixed enemies and drops.", "icon": "🎞️", "color": "#be5ae6", "universe": True},
    {"key": "Raid_Scenario", "label": "Raid", "blurb": "Raid scenarios on hard difficulty.", "icon": "💀", "color": "#8c46dc", "universe": True},
    {"key": "RPG", "label": "Adventure", "blurb": "Roam a map, meet encounters, shop and quest.", "icon": "🗺️", "color": "#46aa3c", "universe": True},
    {"key": "Random", "label": "Randomize", "blurb": "A random mode in a random universe.", "icon": "⚡", "color": "#fad228", "universe": False},
]

PLAY_TOOLS = [
    ("build", "Build", "🧰", []), ("cards", "Cards", "🎴", []), ("titles", "Titles", "🎗️", [("filtered", "Filter", "text")]),
    ("arms", "Arms", "🦾", []), ("summons", "Summons", "🧬", []), ("talismans", "Talismans", "📿", []),
    ("daily", "Daily reward", "🎁", []), ("questboard", "Quests", "📜", []), ("balance", "Balance", "🪙", []),
    ("roll", "Roll", "🎲", [("rolls", "Rolls", "number")]), ("blacksmith", "Blacksmith", "⚒️", []),
    ("gems", "Gems", "💎", []), ("essence", "Essence", "✨", []), ("preset", "Load preset", "📦", []),
    ("savepreset", "Save preset", "💾", []), ("quickbuild", "Quick build", "⚙️", []),
    ("equipcard", "Equip card", "🎴", [("card", "Card name", "text")]), ("equiptitle", "Equip title", "🎗️", [("title", "Title name", "text")]),
    ("equiparm", "Equip arm", "🦾", [("arm_name", "Arm name", "text")]), ("equipsummon", "Equip summon", "🧬", [("summon", "Summon name", "text")]),
    ("difficulty", "Difficulty", "🎚️", [("mode", "Difficulty", "EASY|NORMAL|HARD")]), ("autosave", "Toggle autosave", "💾", []),
    ("battleview", "Toggle opponent stats", "👁️", []), ("battlehistory", "Battle history lines", "📜", [("history", "Lines", "2|3|4|5|6")]),
    ("player", "Player lookup", "🔎", []), ("universes", "Universes", "🌌", [("universe", "Universe", "text")]),
    ("view", "Look something up", "🔍", [("name", "Name", "text")]), ("help", "Help", "❔", [("topic", "Topic", "text")]),
]


def _bridge():
    from dashboard import play_bridge
    return play_bridge


def player_summary(doc):
    card_name = doc.get("CARD")
    card = db.cards_col.find_one({"NAME": card_name}) if card_name else None
    level = next((c.get("LVL", 0) for c in doc.get("CARD_LEVELS") or [] if c.get("CARD") == card_name), 0)
    stats = db.stats_col.find_one({"DID": doc.get("DID")}) or {}
    modes = []
    for key, label in (("TALES_STATS", "Tales"), ("DUNGEON_STATS", "Dungeon"), ("BOSS_STATS", "Boss"), ("SCENARIO_STATS", "Scenario"),
                       ("RAID_STATS", "Raid"), ("EXPLORE_STATS", "Explore"), ("ABYSS_STATS", "Abyss"), ("PVP_STATS", "PvP")):
        rows = stats.get(key) or []
        runs = sum(int(r.get("TOTAL_RUNS", 0) or 0) for r in rows)
        clears = sum(int(r.get("TOTAL_CLEARS", 0) or 0) for r in rows)
        if runs:
            modes.append({"mode": label, "runs": runs, "clears": clears})
    return {
        "did": doc.get("DID"), "name": doc.get("DISNAME") or doc.get("NAME"), "balance": short_number(doc.get("BALANCE", 0)),
        "level": doc.get("LEVEL", 0), "difficulty": doc.get("DIFFICULTY", "NORMAL"), "available": doc.get("AVAILABLE", True),
        "card": card_name, "card_level": level, "title": doc.get("TITLE"), "arm": doc.get("ARM"), "summon": doc.get("PET"),
        "talisman": doc.get("TALISMAN"), "prestige": doc.get("PRESTIGE", 0), "rebirth": doc.get("REBIRTH", 0),
        "pvp": {"wins": doc.get("PVP_WINS", 0), "losses": doc.get("PVP_LOSS", 0)},
        "boss_wins": len(doc.get("BOSS_WINS") or []), "tales_done": len(doc.get("CROWN_TALES") or []),
        "dungeons_done": len(doc.get("DUNGEONS") or []), "modes": modes,
        "render": url_for("card_render_img", doc_id=str(card["_id"]), w=480, v=cardviz.render_key(card)) if card else "",
        "glow": element_style(cardviz.card_type(card))["glow"] if card else "#77d4ff",
    }


@app.get("/play")
def play_page():
    return render_template("play.html", modes=PLAY_MODES, tools=PLAY_TOOLS, universes=universe_names())


@app.get("/play/api/players")
def play_players():
    q = (request.args.get("q") or "").strip()
    query = {"DISNAME": {"$regex": re.escape(q), "$options": "i"}} if q else {}
    docs = db.users_col.find(query, {"DID": 1, "DISNAME": 1, "LEVEL": 1, "CARD": 1}).sort("DISNAME", 1).limit(40)
    return jsonify([{"did": d.get("DID"), "name": d.get("DISNAME") or d.get("DID"), "level": d.get("LEVEL", 0),
                     "card": d.get("CARD")} for d in docs])


@app.get("/play/api/player/<did>")
def play_player(did):
    doc = db.users_col.find_one({"DID": str(did)})
    if doc is None:
        abort(404)
    return jsonify(player_summary(doc))


@app.post("/play/api/start")
def play_start():
    require_csrf()
    body = request.get_json(silent=True) or {}
    did = str(body.get("did") or "")
    doc = db.users_col.find_one({"DID": did}, {"DISNAME": 1, "CARD": 1})
    if doc is None:
        return jsonify({"ok": False, "error": "Pick a registered player first."}), 400
    card = db.cards_col.find_one({"NAME": doc.get("CARD")}) if doc.get("CARD") else None
    avatar = url_for("card_render_img", doc_id=str(card["_id"]), w=200, v=cardviz.render_key(card)) if card else None
    command = body.get("command") or "play"
    args = {k: v for k, v in (body.get("args") or {}).items() if isinstance(k, str)}
    if command == "roll" and args.get("rolls"):
        args["rolls"] = max(1, min(int(args["rolls"]), 10))
    if command == "explore" and not args.get("universe"):
        # /explore without a universe toggles Discord channel encounters; on the web always explore somewhere
        names = universe_names()
        if names:
            args["universe"] = __import__("random").choice(names)
    if command == "battlehistory" and args.get("history"):
        args["history"] = int(args["history"])
    try:
        bridge = _bridge()
        bridge.reap()
        session = bridge.start(did, doc.get("DISNAME"), command, args, avatar=avatar)
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Couldn't start: {type(exc).__name__}: {exc}"}), 500
    return jsonify({"ok": True, "session": session.id})


def _session_or_404(sid):
    session = _bridge().get_session(sid)
    if session is None:
        abort(404)
    session.last_seen = time.time()
    return session


@app.get("/play/api/<sid>/state")
def play_state(sid):
    session = _session_or_404(sid)
    since = request.args.get("v", -1, type=int)
    if not request.args.get("probe"):
        session.wait_change(since, timeout=20)
    return jsonify(session.snapshot())


@app.post("/play/api/<sid>/press")
def play_press(sid):
    require_csrf()
    session = _session_or_404(sid)
    body = request.get_json(silent=True) or {}
    bridge = _bridge()
    result = bridge.run(session, lambda: session.press(str(body.get("id") or ""), body.get("values"), body.get("message")))
    return jsonify(result), (200 if result.get("ok") else 409)


@app.post("/play/api/<sid>/text")
def play_text(sid):
    require_csrf()
    session = _session_or_404(sid)
    text = ((request.get_json(silent=True) or {}).get("text") or "").strip()[:500]
    result = _bridge().run(session, lambda: session.type_text(text))
    return jsonify(result), (200 if result.get("ok") else 409)


@app.post("/play/api/<sid>/end")
def play_end(sid):
    require_csrf()
    session = _bridge().get_session(sid)
    if session is not None:
        _bridge().end(session)
    return jsonify({"ok": True})


@app.get("/play/api/<sid>/file/<key>")
def play_file(sid, key):
    session = _session_or_404(sid)
    item = session.files.get(key)
    if item is None:
        abort(404)
    response = Response(item[0], mimetype=item[1])
    response.cache_control.max_age = 3600
    response.cache_control.private = True
    return response


def main():
    # --lan lets a phone on the same Wi-Fi open the dashboard (http://<this computer's IP>:5055).
    # Anyone on that network could then edit the database, so only use it on a network you trust.
    host = "0.0.0.0" if "--lan" in sys.argv else "127.0.0.1"
    app.run(host=host, port=5055, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
