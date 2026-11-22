"""Pictures for the dashboard.

Cards and summons are drawn by the bot's own renderers, so the dashboard
shows the same portrait Discord does. Other records have a plain image link;
those are fetched through here so the browser gets them from the same origin,
which three.js needs for textures.
"""

import copy
import hashlib
import io
import json
import threading
from collections import OrderedDict
from types import SimpleNamespace

from PIL import Image

RENDER_KEYS = (
    "NAME", "UNIVERSE", "CLASS", "TIER", "HLT", "STAM", "ATK", "DEF", "SPD", "MOVESET",
    "PATH", "FPATH", "RPATH", "RNAME", "CARD_ART", "CARD_FOCUS_ART", "CARD_RESOLVE_ART",
    "CARD_ART_CROP", "DROP_STYLE",
)

# Keys create_card_from_data reads with [] (a missing one would make it fail).
CARD_DEFAULTS = {
    "PATH": "", "PRICE": 0, "AVAILABLE": False, "SKIN_FOR": "N/A", "HLT": 500, "STAM": 100,
    "ATK": 25, "DEF": 25, "TYPE": 0, "PASS": [{"NAME": 0, "TYPE": "TYPE"}], "SPD": 1,
    "UNIVERSE": "Unbound", "TIER": 1, "WEAKNESS": [], "RESISTANT": [], "REPEL": [], "ABSORB": [],
    "IMMUNE": [], "GIF": "N/A", "FPATH": "N/A", "RNAME": "N/A", "RPATH": "N/A", "CLASS": "FIGHTER",
    "DROP_STYLE": "TALES", "DESCRIPTIONS": [],
}

_cache = OrderedDict()
_cache_lock = threading.Lock()
_CACHE_MAX = 240

_renderer = None
_renderer_error = None
_renderer_lock = threading.Lock()


def render_key(doc):
    relevant = {key: doc.get(key) for key in RENDER_KEYS}
    raw = json.dumps(relevant, sort_keys=True, default=str).encode()
    return hashlib.sha1(raw).hexdigest()[:16]


def renderer():
    """(create_card_from_data, card_render) or raises RuntimeError with the import problem."""
    global _renderer, _renderer_error
    if _renderer is not None:
        return _renderer
    with _renderer_lock:
        if _renderer is None and _renderer_error is None:
            try:
                import card_render
                import crown_utilities
                _renderer = (crown_utilities.create_card_from_data, card_render)
            except Exception as exc:  # the bot's modules failed to import
                _renderer_error = f"{type(exc).__name__}: {exc}"
    if _renderer is None:
        raise RuntimeError(f"The bot's card renderer could not load ({_renderer_error}).")
    return _renderer


def _cached(key):
    with _cache_lock:
        hit = _cache.get(key)
        if hit is not None:
            _cache.move_to_end(key)
        return hit


def _store(key, value):
    with _cache_lock:
        _cache[key] = value
        while len(_cache) > _CACHE_MAX:
            _cache.popitem(last=False)


def _encode(im, width=None, quality=88):
    im = im.convert("RGB")
    if width and width < im.width:
        im = im.resize((int(width), int(round(im.height * width / im.width))), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return out.getvalue()


def _card_object(doc):
    create, card_render = renderer()
    data = copy.deepcopy({k: v for k, v in doc.items() if k != "_id"})
    for key, value in CARD_DEFAULTS.items():
        if data.get(key) is None:
            data[key] = copy.deepcopy(value)
    card = create(data)
    if not card:
        return None
    return card


def render_card(doc, width=None):
    """JPEG bytes of the Discord card image for ``doc`` (a card record, saved or not)."""
    key = f"card:{render_key(doc)}:{width or 0}"
    hit = _cached(key)
    if hit is not None:
        return hit
    full_key = f"card:{render_key(doc)}:0"
    full = _cached(full_key)
    if full is None:
        _, card_render = renderer()
        card = _card_object(doc)
        if card is None:
            png = card_render.fallback(SimpleNamespace(
                name=doc.get("NAME", "Card"), health=doc.get("HLT", 0), stamina=doc.get("STAM", 0),
                attack=doc.get("ATK", 0), defense=doc.get("DEF", 0)))
        else:
            png = card_render.render(card)
        full = _encode(Image.open(png))
        _store(full_key, full)
    if not width:
        return full
    small = _encode(Image.open(io.BytesIO(full)), width=width, quality=84)
    _store(key, small)
    return small


SUMMON_KEYS = ("PET", "NAME", "UNIVERSE", "PATH", "LVL", "BOND", "ABILITIES")


def summon_key(doc):
    relevant = {key: doc.get(key) for key in SUMMON_KEYS}
    raw = json.dumps(relevant, sort_keys=True, default=str).encode()
    return hashlib.sha1(raw).hexdigest()[:16]


def render_summon(doc, width=None):
    """JPEG bytes of the Discord summon portrait for ``doc``."""
    key = f"summon:{summon_key(doc)}:{width or 0}"
    hit = _cached(key)
    if hit is not None:
        return hit
    full_key = f"summon:{summon_key(doc)}:0"
    full = _cached(full_key)
    if full is None:
        import summon_render
        png = summon_render.render(**summon_render.parts_from_doc(doc))
        full = _encode(Image.open(png))
        _store(full_key, full)
    if not width:
        return full
    small = _encode(Image.open(io.BytesIO(full)), width=width, quality=84)
    _store(key, small)
    return small


def render_image(url, width=640):
    """Same-origin JPEG of an image link, or None when it cannot be fetched."""
    key = f"img:{url}:{width}"
    hit = _cached(key)
    if hit is not None:
        return hit
    import render_cache
    data = render_cache.fetch_image_bytes(url)
    if data is None:
        return None
    try:
        im = Image.open(io.BytesIO(data))
        im.seek(0)
        out = _encode(im, width=width, quality=84)
    except Exception:
        return None
    _store(key, out)
    return out


def card_type(doc):
    """The card's type: the element of its Ultimate (third move), as the bot defines it."""
    moves = doc.get("MOVESET") or []
    if len(moves) >= 3 and isinstance(moves[2], dict):
        return str(moves[2].get("ELEMENT") or "").upper()
    return ""


def universe_accent(universe):
    try:
        import battle_scene
        r, g, b = battle_scene.universe_accent(universe)
    except Exception:
        h = hashlib.md5(str(universe).encode()).digest()
        r, g, b = 80 + h[0] % 170, 80 + h[1] % 170, 80 + h[2] % 170
    return f"#{r:02x}{g:02x}{b:02x}"
