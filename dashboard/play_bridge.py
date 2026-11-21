"""Play Anime VS+ in the browser by running the bot's real commands.

The game code talks to Discord through a handful of objects: the command
context (ctx), the channel it sends to, the messages it edits, and the bot
(client) it waits on for button presses.  This module provides web versions of
those objects:

  * every message the game sends or edits is captured, turned into JSON
    (Components V2 containers, embeds, buttons, select menus, images, GIFs) and
    handed to the browser;
  * when the game waits for a button (bot.wait_for_component), a paginator
    registers button callbacks (bot.add_component_callback), or the game waits
    for a typed reply (bot.wait_for("on_message_create")), the browser's click
    or text is delivered exactly as Discord would deliver it.

Nothing about the rules is reimplemented: /play, /explore, /build, /cards ...
run unchanged, so rewards, levels, drops, saves, stats, wins and losses are
written to the database by the same code the bot uses.

All game coroutines run on one asyncio loop in a background thread.  Flask
threads talk to it through run_coroutine_threadsafe and wait for changes with
a threading.Condition (long polling).
"""

import asyncio
import base64
import contextvars
import inspect
import io
import itertools
import os
import threading
import time
import traceback
import types
import uuid
from collections import OrderedDict

import db

CURRENT = contextvars.ContextVar("avs_web_session", default=None)
_loop = None
_loop_lock = threading.Lock()
_patched = False
SESSIONS = {}
SESSIONS_LOCK = threading.Lock()
MAX_MESSAGES = 40
MAX_FILES = 80
SLEEP_CAP = 2.5            # the game paces some screens with sleeps; keep them snappy on the web


# --------------------------------------------------------------------------- loop
def loop():
    global _loop
    with _loop_lock:
        if _loop is None:
            _loop = asyncio.new_event_loop()
            threading.Thread(target=_loop.run_forever, name="avs-web-game", daemon=True).start()
            asyncio.run_coroutine_threadsafe(_noop(), _loop).result()
    return _loop


async def _noop():
    return None


def _install_patches():
    """One-time hooks: capped sleeps and win/loss events from the bot's own handlers."""
    global _patched
    if _patched:
        return
    _patched = True
    real_sleep = asyncio.sleep

    async def capped_sleep(delay=0, result=None):
        return await real_sleep(min(float(delay or 0), SLEEP_CAP), result)

    asyncio.sleep = capped_sleep

    from cogs.classes.battle_class import Battle
    from cogs.game_state import GameState

    # play.py calls all three result handlers after every match and each one
    # checks who won.  Report the result from the battle's own flags, once.
    def hook(name):
        original = getattr(GameState, name, None)
        if original is None or getattr(original, "_avs_web", False):
            return

        async def wrapper(*args, **kwargs):
            try:
                return await original(*args, **kwargs)
            finally:
                session = CURRENT.get()
                battle = next((a for a in args if isinstance(a, Battle)), None)
                if session is not None and battle is not None:
                    session.report(battle)

        wrapper._avs_web = True
        setattr(GameState, name, wrapper)

    for name in ("pvp_end_game", "you_win_non_pvp", "you_lose_non_pvp"):
        hook(name)


# --------------------------------------------------------------------------- serialising
def _emoji(e):
    if e is None:
        return None
    if isinstance(e, str):
        if e.startswith("<") and ":" in e:
            parts = e.strip("<>").split(":")
            if len(parts) == 3:
                animated = parts[0] == "a"
                return {"name": parts[1], "url": f"https://cdn.discordapp.com/emojis/{parts[2]}.{'gif' if animated else 'png'}"}
        return {"name": e}
    eid = getattr(e, "id", None)
    name = getattr(e, "name", None) or str(e)
    if eid:
        animated = bool(getattr(e, "animated", False))
        return {"name": name, "url": f"https://cdn.discordapp.com/emojis/{eid}.{'gif' if animated else 'png'}"}
    return {"name": name}


def _emoji_raw(e):
    if not e:
        return None
    if isinstance(e, dict):
        if e.get("id"):
            return {"name": e.get("name"), "url": f"https://cdn.discordapp.com/emojis/{e['id']}.{'gif' if e.get('animated') else 'png'}"}
        return {"name": e.get("name")}
    return _emoji(e)


def _style(value):
    try:
        return int(value)
    except Exception:
        return {"PRIMARY": 1, "BLURPLE": 1, "SECONDARY": 2, "GREY": 2, "GRAY": 2, "SUCCESS": 3, "GREEN": 3,
                "DANGER": 4, "RED": 4, "LINK": 5, "URL": 5}.get(str(value).split(".")[-1].upper(), 2)


def _as_embed(e):
    """Discord returns parsed Embed objects even when the code sent dicts; so do we."""
    if isinstance(e, dict):
        try:
            from interactions import Embed
            return Embed.from_dict(e)
        except Exception:
            return e
    return e


def _as_component(c):
    if isinstance(c, dict):
        try:
            from interactions.models.discord.components import BaseComponent
            return BaseComponent.from_dict_factory(c)
        except Exception:
            return c
    return c


def _file_parts(f):
    """(name, bytes) for an interactions File, a path, raw bytes or a file-like object."""
    name = getattr(f, "file_name", None)
    inner = getattr(f, "file", f)
    data = None
    try:
        if isinstance(inner, (bytes, bytearray)):
            data = bytes(inner)
        elif isinstance(inner, str):
            if os.path.exists(inner):
                with open(inner, "rb") as fh:
                    data = fh.read()
            name = name or os.path.basename(inner)
        elif hasattr(inner, "getvalue"):
            data = inner.getvalue()
        elif hasattr(inner, "read"):
            pos = inner.tell() if hasattr(inner, "tell") else None
            data = inner.read()
            if pos is not None:
                inner.seek(pos)
    except Exception:
        data = None
    if not name:
        name = "file.png"
    return name, data


def _mime(name, data):
    n = name.lower()
    if n.endswith(".gif") or (data or b"")[:4] == b"GIF8":
        return "image/gif"
    if n.endswith((".jpg", ".jpeg")) or (data or b"")[:2] == b"\xff\xd8":
        return "image/jpeg"
    if n.endswith(".webp"):
        return "image/webp"
    if n.endswith(".png") or (data or b"")[:4] == b"\x89PNG":
        return "image/png"
    return "application/octet-stream"


class Serializer:
    """Turns interactions objects into plain JSON the browser renders."""

    def __init__(self, session, attachments):
        self.session = session
        self.attachments = attachments        # file name -> url

    def url(self, value):
        if value is None:
            return None
        value = str(getattr(value, "url", value))
        if value.startswith("attachment://"):
            return self.attachments.get(value[len("attachment://"):])
        return value

    def raw(self, c):
        """A component already converted to Discord's JSON (paginators send these)."""
        kind = c.get("type")
        kids = c.get("components") or []
        if kind == 1:
            return {"t": "row", "items": [self.raw(k) if isinstance(k, dict) else self.component(k) for k in kids]}
        if kind == 2:
            return {"t": "button", "id": c.get("custom_id"), "label": c.get("label"), "emoji": _emoji_raw(c.get("emoji")),
                    "style": _style(c.get("style", 2)), "disabled": bool(c.get("disabled")), "url": c.get("url")}
        if kind in (3, 5, 6, 7, 8):
            return {"t": "select", "id": c.get("custom_id"), "placeholder": c.get("placeholder"),
                    "options": [{"label": o.get("label"), "value": o.get("value"), "description": o.get("description"),
                                 "emoji": _emoji_raw(o.get("emoji")), "default": bool(o.get("default"))} for o in c.get("options") or []],
                    "min": c.get("min_values", 1), "max": c.get("max_values", 1), "disabled": bool(c.get("disabled"))}
        if kind == 17:
            accent = c.get("accent_color")
            return {"t": "container", "accent": f"#{int(accent):06x}" if isinstance(accent, int) else None,
                    "items": [self.raw(k) if isinstance(k, dict) else self.component(k) for k in kids]}
        if kind == 10:
            return {"t": "text", "md": c.get("content") or ""}
        if kind == 12:
            return {"t": "gallery", "items": [{"url": self.url((i.get("media") or {}).get("url")), "desc": i.get("description")} for i in c.get("items") or []]}
        if kind == 11:
            return {"t": "thumb", "url": self.url((c.get("media") or {}).get("url"))}
        if kind == 14:
            return {"t": "sep", "divider": c.get("divider", True) is not False}
        if kind == 9:
            acc = c.get("accessory")
            return {"t": "section", "items": [self.raw(k) if isinstance(k, dict) else self.component(k) for k in kids],
                    "accessory": (self.raw(acc) if isinstance(acc, dict) else self.component(acc)) if acc else None}
        return {"t": "text", "md": ""}

    def component(self, c):
        name = type(c).__name__
        if isinstance(c, dict):
            return self.raw(c)
        if isinstance(c, (list, tuple)):
            return {"t": "row", "items": [self.component(x) for x in c]}
        if name == "ContainerComponent":
            kids = getattr(c, "components", None)
            if kids is None:
                kids = list(c)
            accent = getattr(c, "accent_color", None)
            accent = getattr(accent, "value", accent)
            return {"t": "container", "accent": f"#{int(accent):06x}" if isinstance(accent, int) else None,
                    "items": [self.component(k) for k in kids]}
        if name == "TextDisplayComponent":
            return {"t": "text", "md": getattr(c, "content", "") or ""}
        if name == "MediaGalleryComponent":
            items = []
            for it in getattr(c, "items", None) or []:
                media = getattr(it, "media", it)
                items.append({"url": self.url(getattr(media, "url", media)), "desc": getattr(it, "description", None)})
            return {"t": "gallery", "items": items}
        if name == "ThumbnailComponent":
            media = getattr(c, "media", None)
            return {"t": "thumb", "url": self.url(getattr(media, "url", media))}
        if name == "SeparatorComponent":
            return {"t": "sep", "divider": getattr(c, "divider", True) is not False}
        if name == "SectionComponent":
            acc = getattr(c, "accessory", None)
            return {"t": "section", "items": [self.component(k) for k in getattr(c, "components", None) or []],
                    "accessory": self.component(acc) if acc is not None else None}
        if name == "ActionRow":
            return {"t": "row", "items": [self.component(k) for k in getattr(c, "components", None) or []]}
        if name == "Button":
            return {"t": "button", "id": getattr(c, "custom_id", None), "label": getattr(c, "label", None),
                    "emoji": _emoji(getattr(c, "emoji", None)), "style": _style(getattr(c, "style", 2)),
                    "disabled": bool(getattr(c, "disabled", False)), "url": getattr(c, "url", None)}
        if "SelectMenu" in name:
            options = []
            for o in getattr(c, "options", None) or []:
                options.append({"label": getattr(o, "label", str(o)), "value": getattr(o, "value", str(o)),
                                "description": getattr(o, "description", None), "emoji": _emoji(getattr(o, "emoji", None)),
                                "default": bool(getattr(o, "default", False))})
            return {"t": "select", "id": getattr(c, "custom_id", None), "placeholder": getattr(c, "placeholder", None),
                    "options": options, "min": getattr(c, "min_values", 1) or 1, "max": getattr(c, "max_values", 1) or 1,
                    "disabled": bool(getattr(c, "disabled", False))}
        if name == "FileComponent":
            return {"t": "text", "md": "-# 📎 file"}
        if isinstance(c, str):
            return {"t": "text", "md": c}
        return {"t": "text", "md": f"-# ({name})"}

    def embed(self, e):
        if e is None:
            return None
        if isinstance(e, dict):
            d = e
        else:
            try:
                d = e.to_dict()
            except Exception:
                d = {"title": getattr(e, "title", None), "description": getattr(e, "description", None)}
        color = d.get("color")
        return {
            "title": d.get("title"), "description": d.get("description"), "url": d.get("url"),
            "color": f"#{int(color):06x}" if isinstance(color, int) else None,
            "fields": [{"name": f.get("name"), "value": f.get("value"), "inline": f.get("inline")} for f in d.get("fields") or []],
            "image": self.url((d.get("image") or {}).get("url")),
            "thumbnail": self.url((d.get("thumbnail") or {}).get("url")),
            "author": {"name": (d.get("author") or {}).get("name"), "icon": self.url((d.get("author") or {}).get("icon_url"))} if d.get("author") else None,
            "footer": {"text": (d.get("footer") or {}).get("text"), "icon": self.url((d.get("footer") or {}).get("icon_url"))} if d.get("footer") else None,
        }


# --------------------------------------------------------------------------- fake discord
class WebGuild:
    def __init__(self):
        self.id = 0
        self.name = "Anime VS+ Web"
        self.members = []
        self.channels = []

    def __str__(self):
        return self.name

    def get_member(self, *a, **kw):
        return None


GUILD = WebGuild()


class WebUser:
    def __init__(self, did, name):
        self.id = int(did)
        self.did = str(did)
        self.name = name or f"Player {did}"
        self.username = self.name
        self.display_name = self.name
        self.global_name = self.name
        self.mention = f"<@{did}>"
        self.bot = False
        self.avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
        self.avatar = types.SimpleNamespace(url=self.avatar_url)
        self.display_avatar = self.avatar
        self.guild = GUILD

    def __eq__(self, other):
        return getattr(other, "id", None) == self.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return self.name

    async def send(self, content=None, **kw):
        session = CURRENT.get()
        if session is None:
            return None
        kw["content"] = content
        return session.post(kw, dm=True)

    async def fetch_dm(self, *a, **kw):
        return self


class WebMessage:
    _ids = itertools.count(1)

    def __init__(self, session, payload, ephemeral=False, dm=False):
        self.session = session
        self.id = next(WebMessage._ids)
        self.channel = session.channel
        self.channel_id = session.channel.id
        self.author = session.bot.user
        self.ephemeral = ephemeral
        self.dm = dm
        self.deleted = False
        self.created = time.time()
        self.content = None
        self.embeds = []
        self.components = []
        self.files = {}                       # file name -> url
        self.jump_url = ""
        self.attachments = []
        self._apply(payload, replace_files=True)

    def _apply(self, kw, replace_files=False):
        if "content" in kw:
            self.content = kw.get("content")
        if "embed" in kw or "embeds" in kw:
            emb = kw.get("embeds") if "embeds" in kw else ([kw["embed"]] if kw.get("embed") is not None else [])
            if emb is not None and not isinstance(emb, (list, tuple)):
                emb = [emb]
            self.embeds = [_as_embed(e) for e in (emb or [])]
        if "components" in kw:
            comps = kw.get("components")
            if comps is None:
                comps = []
            if not isinstance(comps, (list, tuple)):
                comps = [comps]
            self.components = [_as_component(c) for c in comps]
        files = []
        if kw.get("file") is not None:
            files.append(kw["file"])
        files += list(kw.get("files") or [])
        if files or replace_files or kw.get("attachments") == [] or "files" in kw:
            if files or kw.get("attachments") == [] or "files" in kw:
                self.files = {}
            for f in files:
                name, data = _file_parts(f)
                if data is None:
                    continue
                self.files[name] = self.session.store_file(name, data)
        self.attachments = [types.SimpleNamespace(filename=n, url=u) for n, u in self.files.items()]

    async def edit(self, content=None, **kw):
        if self.deleted:
            from interactions.client.errors import NotFound
            err = NotFound.__new__(NotFound)
            Exception.__init__(err, "404 Not Found (error code: 10008): Unknown Message")
            err.status, err.code, err.text, err.errors, err.route, err.response = 404, 10008, "Unknown Message", {}, None, None
            raise err
        if content is not None:
            kw["content"] = content
        self._apply(kw)
        self.session.touch()
        return self

    async def delete(self, delay=None, **kw):
        if delay:
            async def later():
                await asyncio.sleep(delay)
                await self.delete()
            asyncio.ensure_future(later())
            return
        self.deleted = True
        self.session.touch()

    async def reply(self, content=None, **kw):
        kw["content"] = content
        return self.session.post(kw)

    async def add_reaction(self, *a, **kw):
        return None

    async def remove_reaction(self, *a, **kw):
        return None

    async def clear_reactions(self, *a, **kw):
        return None

    async def fetch_channel(self, *a, **kw):
        return self.channel

    def custom_ids(self):
        ids = []

        def walk(c):
            if c is None:
                return
            if isinstance(c, (list, tuple)):
                for x in c:
                    walk(x)
                return
            if isinstance(c, dict):
                if c.get("custom_id"):
                    ids.append(c["custom_id"])
                walk(c.get("components") or [])
                if c.get("accessory"):
                    walk(c["accessory"])
                return
            cid = getattr(c, "custom_id", None)
            if cid:
                ids.append(cid)
            kids = getattr(c, "components", None)
            if kids is None and type(c).__name__ == "ContainerComponent":
                kids = list(c)
            if kids:
                walk(list(kids))
            acc = getattr(c, "accessory", None)
            if acc is not None:
                walk(acc)

        walk(self.components)
        return ids

    def to_json(self):
        ser = Serializer(self.session, self.files)
        return {
            "id": self.id,
            "ephemeral": self.ephemeral,
            "content": self.content if isinstance(self.content, str) else (str(self.content) if self.content else None),
            "embeds": [ser.embed(e) for e in self.embeds if e is not None],
            "components": [ser.component(c) for c in self.components],
            "files": [u for n, u in self.files.items() if not self._referenced(n)],
        }

    def _referenced(self, name):
        target = f"attachment://{name}"

        def has(obj):
            if obj is None:
                return False
            if isinstance(obj, str):
                return target in obj
            if isinstance(obj, (list, tuple)):
                return any(has(o) for o in obj)
            if isinstance(obj, dict):
                return any(has(v) for v in obj.values())
            for attr in ("url", "media", "items", "components", "accessory", "image", "thumbnail"):
                if has(getattr(obj, attr, None)):
                    return True
            if type(obj).__name__ == "ContainerComponent":
                return any(has(k) for k in list(obj))
            if hasattr(obj, "to_dict"):
                try:
                    return target in str(obj.to_dict())
                except Exception:
                    return False
            return False

        return has(self.embeds) or has(self.components)


class WebChannel:
    def __init__(self, session):
        self.session = session
        self.id = 1000 + abs(hash(session.id)) % 100000
        self.name = "explore-encounters"
        self.guild = session.guild if hasattr(session, "guild") else GUILD
        self.channel = self

    def __str__(self):
        return self.name

    async def send(self, content=None, **kw):
        kw["content"] = content
        return self.session.post(kw)

    async def fetch_message(self, mid):
        return self.session.find(mid)

    def typing(self):
        class _T:
            async def __aenter__(s):
                return s

            async def __aexit__(s, *a):
                return False
        return _T()

    async def trigger_typing(self):
        return None


class WebCtx:
    """Stands in for both a slash-command context and a component (button) context."""

    def __init__(self, session, author, custom_id=None, values=None, message=None):
        self.session = session
        self.author = author
        self.user = author
        self.author_id = author.id
        self.member = author
        self.channel = session.channel
        self.channel_id = session.channel.id
        self.guild = session.guild
        self.guild_id = session.guild.id
        self.bot = session.bot
        self.client = session.bot
        self.custom_id = custom_id
        self.values = list(values or [])
        self.message = message
        self.origin_message = message
        self.responded = False
        self.deferred = False
        self.ephemeral = False
        self.kwargs = {}
        self.args = []
        self.input_text = ""
        self.locale = "en-US"
        self.guild_locale = "en-US"
        self.id = int(time.time() * 1000)
        self._deferred_edit_origin = False

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        self.session.note(f"ctx.{item} was used but the web client doesn't provide it")
        return None

    async def defer(self, ephemeral=False, edit_origin=False, suppress_error=False, **kw):
        self.deferred = True
        self.responded = True
        self._deferred_edit_origin = edit_origin
        return None

    async def send(self, content=None, ephemeral=False, **kw):
        kw["content"] = content
        self.responded = True
        if kw.pop("delete_after", None):
            msg = self.session.post(kw, ephemeral=ephemeral)

            async def drop():
                await asyncio.sleep(4)
                msg.deleted = True
                self.session.touch()
            asyncio.ensure_future(drop())
            return msg
        return self.session.post(kw, ephemeral=ephemeral)

    respond = send
    reply = send

    async def edit_origin(self, content=None, **kw):
        self.responded = True
        if content is not None:
            kw["content"] = content
        if self.message is not None and not self.message.deleted:
            return await self.message.edit(**kw)
        return self.session.post(kw)

    async def edit(self, message=None, content=None, **kw):
        if content is not None:
            kw["content"] = content
        target = message if isinstance(message, WebMessage) else self.message
        if target is None:
            return self.session.post(kw)
        return await target.edit(**kw)

    async def delete(self, message=None):
        target = message if isinstance(message, WebMessage) else self.message
        if target is not None:
            await target.delete()

    async def send_modal(self, *a, **kw):
        self.session.note("This screen asks for a Discord pop-up form, which the web client can't show yet.")
        return None


class Waiter:
    def __init__(self, kind, ids, check, future):
        self.kind = kind            # "component" or "message"
        self.ids = set(ids or [])
        self.check = check
        self.future = future


class WebBot:
    def __init__(self, session):
        self.session = session
        self.user = types.SimpleNamespace(id=1, name="Anime VS+", mention="@Anime VS+", bot=True,
                                          avatar=types.SimpleNamespace(url=""), display_name="Anime VS+")
        self.guilds = []
        self.guild_id = GUILD.id
        self.guild_channel = 0
        self.latency = 0.0
        self.callbacks = {}         # custom_id -> ComponentCommand

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        self.session.note(f"bot.{item} was used but the web client doesn't provide it")
        return None

    async def fetch_user(self, uid, *a, **kw):
        return self.session.user_for(uid)

    def get_user(self, uid, *a, **kw):
        return self.session.user_for(uid)

    async def fetch_member(self, uid, *a, **kw):
        return self.session.user_for(uid)

    def get_member(self, uid, *a, **kw):
        return self.session.user_for(uid)

    def get_guild(self, *a, **kw):
        return None

    async def fetch_guild(self, *a, **kw):
        return None

    def get_channel(self, *a, **kw):
        return self.session.channel

    async def fetch_channel(self, *a, **kw):
        return self.session.channel

    async def validate_user(self, ctx):
        return True

    def add_component_callback(self, command):
        for listener in getattr(command, "listeners", []) or []:
            self.callbacks[str(listener)] = command
        self.session.touch()

    def remove_component_callback(self, command=None, *a, **kw):
        if command is None:
            return
        for listener in getattr(command, "listeners", []) or []:
            self.callbacks.pop(str(listener), None)

    async def wait_for_component(self, messages=None, components=None, check=None, timeout=None, **kw):
        ids = _collect_ids(components)
        if not ids and messages is not None:
            for m in messages if isinstance(messages, (list, tuple)) else [messages]:
                if isinstance(m, WebMessage):
                    ids += m.custom_ids()
        return await self.session.wait("component", ids, check, timeout)

    async def wait_for(self, event=None, checks=None, check=None, timeout=None, **kw):
        name = getattr(event, "__name__", None) or str(event)
        if "message" in name.lower():
            return await self.session.wait("message", [], check or checks, timeout)
        if timeout:
            await asyncio.sleep(min(timeout, 1))
        raise asyncio.TimeoutError()

    async def wait_for_modal(self, *a, timeout=None, **kw):
        raise asyncio.TimeoutError()


def _collect_ids(components):
    ids = []
    if components is None:
        return ids
    if not isinstance(components, (list, tuple)):
        components = [components]
    for c in components:
        if isinstance(c, str):
            ids.append(c)
            continue
        if isinstance(c, (list, tuple)):
            ids += _collect_ids(c)
            continue
        if isinstance(c, dict):
            if c.get("custom_id"):
                ids.append(c["custom_id"])
            ids += _collect_ids(c.get("components") or [])
            continue
        cid = getattr(c, "custom_id", None)
        if cid:
            ids.append(cid)
        inner = getattr(c, "components", None)
        if inner:
            ids += _collect_ids(list(inner))
    return ids


class CogProxy:
    """Lets a cog's methods run with ``self`` = this proxy (has .bot / .client)."""

    def __init__(self, cls, bot):
        self._cls = cls
        self.bot = bot
        self.client = bot

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        attr = getattr(self._cls, item)
        fn = attr if inspect.isfunction(attr) else getattr(attr, "callback", None)
        if inspect.isfunction(fn):
            return types.MethodType(fn, self)
        return attr


# --------------------------------------------------------------------------- session
class Session:
    def __init__(self, did, name):
        self.id = uuid.uuid4().hex[:12]
        self.did = str(did)
        self.player = WebUser(did, name)
        self.users = {self.did: self.player}
        self.bot = WebBot(self)
        self.guild = WebGuild()
        self.channel = WebChannel(self)
        self.guild.channels = [self.channel]
        self.player.guild = self.guild
        self.messages = OrderedDict()
        self.files = OrderedDict()
        self.waiters = []
        self.tasks = set()
        self.version = 0
        self.cond = threading.Condition()
        self.events = []             # [(version, kind, detail)]
        self.notes = []
        self.title = ""
        self.started = time.time()
        self.last_seen = time.time()
        self.record = {"win": 0, "loss": 0}
        self.reported = set()
        self.closed = False

    # ----- state changes (called on the game loop)
    def touch(self):
        with self.cond:
            self.version += 1
            self.cond.notify_all()

    def event(self, kind, detail=None):
        with self.cond:
            self.version += 1
            self.events.append((self.version, kind, detail))
            self.events = self.events[-30:]
            self.cond.notify_all()

    def note(self, text):
        if text not in self.notes:
            self.notes.append(text)
            self.notes = self.notes[-10:]

    def report(self, battle):
        """Emit one win/loss event per finished match, from player 1's side."""
        if battle.player1_wins:
            kind = "win"
        elif battle.player2_wins:
            kind = "loss"
        else:
            return
        key = (id(battle), getattr(battle, "current_opponent_number", 0), getattr(battle, "turn_total", 0), kind)
        if key in self.reported:
            return
        self.reported.add(key)
        self.record[kind] += 1
        try:
            detail = {"you": getattr(battle.player1_card, "name", ""), "foe": getattr(battle.player2_card, "name", ""),
                      "turns": getattr(battle, "turn_total", 0), "mode": getattr(battle, "mode", "")}
        except Exception:
            detail = None
        self.event(kind, detail)

    def store_file(self, name, data):
        key = uuid.uuid4().hex[:10]
        self.files[key] = (data, _mime(name, data))
        while len(self.files) > MAX_FILES:
            self.files.popitem(last=False)
        return f"/play/api/{self.id}/file/{key}"

    def post(self, payload, ephemeral=False, dm=False):
        msg = WebMessage(self, payload, ephemeral=ephemeral, dm=dm)
        self.messages[msg.id] = msg
        while len(self.messages) > MAX_MESSAGES:
            self.messages.popitem(last=False)
        self.touch()
        return msg

    def find(self, mid):
        return self.messages.get(int(mid)) if str(mid).isdigit() else None

    def user_for(self, uid):
        uid = str(uid)
        if uid not in self.users:
            doc = db.users_col.find_one({"DID": uid}, {"DISNAME": 1})
            self.users[uid] = WebUser(uid, (doc or {}).get("DISNAME") or f"Player {uid}")
            self.users[uid].guild = self.guild
        return self.users[uid]

    async def wait(self, kind, ids, check, timeout):
        fut = asyncio.get_running_loop().create_future()
        waiter = Waiter(kind, ids, check, fut)
        self.waiters.append(waiter)
        self.touch()
        try:
            if timeout:
                return await asyncio.wait_for(fut, timeout)
            return await fut
        finally:
            if waiter in self.waiters:
                self.waiters.remove(waiter)
            self.touch()

    # ----- input from the browser (runs on the game loop)
    async def press(self, custom_id, values=None, message_id=None):
        message = self.find(message_id) if message_id else None
        if message is None:
            message = next((m for m in reversed(self.messages.values()) if not m.deleted and custom_id in m.custom_ids()), None)
        ctx = WebCtx(self, self.player, custom_id=custom_id, values=values, message=message)
        event = types.SimpleNamespace(ctx=ctx, component=None)
        for waiter in list(self.waiters):
            if waiter.kind != "component" or waiter.future.done():
                continue
            if waiter.ids and custom_id not in waiter.ids:
                continue
            if waiter.check is not None:
                try:
                    ok = waiter.check(event)
                    if inspect.isawaitable(ok):
                        ok = await ok
                except Exception:
                    ok = False
                if not ok:
                    continue
            waiter.future.set_result(event)
            return {"ok": True}
        command = self.bot.callbacks.get(custom_id)
        if command is None:
            for listener, cmd in self.bot.callbacks.items():
                if hasattr(listener, "match") and listener.match(custom_id):
                    command = cmd
                    break
        if command is not None:
            self.spawn(self._run_callback(command, ctx), label=f"button {custom_id}")
            return {"ok": True}
        return {"ok": False, "error": "That button has expired."}

    async def _run_callback(self, command, ctx):
        callback = getattr(command, "callback", command)
        result = callback(ctx)
        if inspect.isawaitable(result):
            await result

    async def type_text(self, text):
        msg = self.post({"content": text})
        msg.author = self.player
        msg.content = text
        event = types.SimpleNamespace(message=msg)
        for waiter in list(self.waiters):
            if waiter.kind != "message" or waiter.future.done():
                continue
            checks = waiter.check if isinstance(waiter.check, (list, tuple)) else [waiter.check]
            ok = True
            for check in checks:
                if check is None:
                    continue
                try:
                    res = check(event)
                    if inspect.isawaitable(res):
                        res = await res
                except Exception:
                    res = False
                ok = ok and bool(res)
            if ok:
                waiter.future.set_result(event)
                return {"ok": True}
        return {"ok": False, "error": "Nothing is waiting for a typed answer right now."}

    def spawn(self, coro, label="command"):
        async def runner():
            token = CURRENT.set(self)
            try:
                await coro
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                self.event("timeout", label)
            except Exception as ex:
                self.event("error", f"{type(ex).__name__}: {ex}")
                traceback.print_exc()
            finally:
                CURRENT.reset(token)
                self.touch()

        task = asyncio.ensure_future(runner())
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    # ----- read side (Flask threads)
    def busy(self):
        return any(not t.done() for t in self.tasks)

    def snapshot(self):
        messages = [m for m in self.messages.values() if not m.deleted]
        clickable = set()
        for w in self.waiters:
            if w.kind == "component":
                clickable |= w.ids
        clickable |= set(self.bot.callbacks.keys())
        live = []
        for m in messages:
            try:
                live.append(m.to_json())
            except Exception as ex:
                live.append({"id": m.id, "content": f"(couldn't show this message: {ex})", "embeds": [], "components": [], "files": []})
        waiting_text = any(w.kind == "message" for w in self.waiters)
        return {
            "id": self.id, "version": self.version, "messages": live, "clickable": sorted(clickable),
            "waiting_text": waiting_text, "busy": self.busy(), "events": self.events[-12:],
            "record": self.record, "notes": self.notes[-3:], "title": self.title,
        }

    def wait_change(self, version, timeout=25):
        with self.cond:
            if self.version <= version:
                self.cond.wait(timeout)
            return self.version

    async def close(self):
        self.closed = True
        for waiter in list(self.waiters):
            if not waiter.future.done():
                waiter.future.set_exception(asyncio.TimeoutError())
        await asyncio.sleep(0.5)
        for task in list(self.tasks):
            task.cancel()
        try:
            db.users_col.update_one({"DID": self.did}, {"$set": {"AVAILABLE": True}})
        except Exception:
            pass
        self.touch()


# --------------------------------------------------------------------------- commands the web exposes
def _command(module, cls, attr):
    return {"module": module, "cls": cls, "attr": attr}


COMMANDS = {
    "play": _command("cogs.game_modes", "GameModes", "play"),
    "explore": _command("cogs.explore", "Explore", "explore"),
    "build": _command("cogs.profile", "Profile", "build"),
    "cards": _command("cogs.profile", "Profile", "cards"),
    "titles": _command("cogs.profile", "Profile", "titles"),
    "arms": _command("cogs.profile", "Profile", "arms"),
    "summons": _command("cogs.profile", "Profile", "summons"),
    "talismans": _command("cogs.profile", "Profile", "talismans"),
    "storage": _command("cogs.profile", "Profile", "storage"),
    "gems": _command("cogs.profile", "Profile", "gems"),
    "essence": _command("cogs.profile", "Profile", "essence"),
    "blacksmith": _command("cogs.profile", "Profile", "blacksmith"),
    "balance": _command("cogs.profile", "Profile", "balance"),
    "roll": _command("cogs.profile", "Profile", "roll"),
    "preset": _command("cogs.profile", "Profile", "preset"),
    "savepreset": _command("cogs.profile", "Profile", "savepreset"),
    "quickbuild": _command("cogs.profile", "Profile", "quickbuild"),
    "attune": _command("cogs.profile", "Profile", "attune"),
    "equipcard": _command("cogs.profile", "Profile", "equipcard"),
    "equiparm": _command("cogs.profile", "Profile", "equiparm"),
    "equipsummon": _command("cogs.profile", "Profile", "equipsummon"),
    "equiptitle": _command("cogs.titles", "Titles", "equiptitle"),
    "daily": _command("cogs.register", "Register", "daily"),
    "questboard": _command("cogs.quests", "Quests", "questboard"),
    "difficulty": _command("cogs.options", "Options", "difficulty"),
    "autosave": _command("cogs.options", "Options", "autosave"),
    "battleview": _command("cogs.options", "Options", "battleview"),
    "battlehistory": _command("cogs.options", "Options", "battlehistory"),
    "player": _command("cogs.lookup", "Lookup", "player"),
    "universes": _command("cogs.views", "Views", "universes"),
    "view": _command("cogs.views", "Views", "view"),
    "help": _command("cogs.help", "Help", "help"),
}


class _Cooldown:
    def __init__(self, fire):
        self.fire = fire

    async def acquire_token(self, *a, **kw):
        return not self.fire          # the bot treats "no token left" as "time for an event"

    async def reset(self, *a, **kw):
        return None

    async def reset_all(self, *a, **kw):
        return None


async def _explore(session, universe):
    """/explore <universe>, then the encounter the bot spawns while you chat."""
    from cogs.explore import Explore
    from cogs.game_modes import GameModes
    _, explore_fn = _resolve(COMMANDS["explore"])
    await explore_fn(CogProxy(Explore, session.bot), WebCtx(session, session.player), universe=universe)
    proxy = CogProxy(GameModes, session.bot)
    proxy.level_up_cooldown = _Cooldown(False)
    proxy.explore_cooldown = _Cooldown(True)
    message = types.SimpleNamespace(author=session.player, channel=session.channel, _guild_id=session.guild.id,
                                    guild_id=session.guild.id, content="explore", id=int(time.time() * 1000))
    listener = GameModes.on_message_create
    fn = listener if inspect.isfunction(listener) else listener.callback
    await fn(proxy, types.SimpleNamespace(message=message))


def _resolve(spec):
    import importlib
    module = importlib.import_module(spec["module"])
    cls = getattr(module, spec["cls"], None)
    if cls is None:  # class name differs: take the Extension subclass defined there
        from interactions import Extension
        cls = next(v for v in vars(module).values() if inspect.isclass(v) and issubclass(v, Extension) and v is not Extension)
    attr = getattr(cls, spec["attr"])
    fn = getattr(attr, "callback", attr)
    return cls, fn


def get_session(sid):
    with SESSIONS_LOCK:
        return SESSIONS.get(sid)


def start(did, name, command, kwargs, avatar=None):
    """Start a command for player ``did``.  Ends that player's previous web session."""
    _install_patches()
    spec = COMMANDS.get(command)
    if spec is None:
        raise ValueError(f"Unknown command {command}")
    cls, fn = _resolve(spec)
    with SESSIONS_LOCK:
        old = [s for s in SESSIONS.values() if s.did == str(did) and not s.closed]
    for s in old:
        asyncio.run_coroutine_threadsafe(s.close(), loop()).result(timeout=10)
        with SESSIONS_LOCK:
            SESSIONS.pop(s.id, None)
    session = Session(did, name)
    session.title = command
    if avatar:
        session.player.avatar_url = avatar
        session.player.avatar = types.SimpleNamespace(url=avatar)
        session.player.display_avatar = session.player.avatar
    with SESSIONS_LOCK:
        SESSIONS[session.id] = session
    proxy = CogProxy(cls, session.bot)
    ctx = WebCtx(session, session.player)
    clean = {k: v for k, v in (kwargs or {}).items() if v not in (None, "")}

    async def go():
        if command == "explore":
            session.spawn(_explore(session, clean.get("universe")), label=command)
        else:
            session.spawn(fn(proxy, ctx, **clean), label=command)

    asyncio.run_coroutine_threadsafe(go(), loop()).result(timeout=10)
    return session


def run(session, coro_factory, timeout=10):
    return asyncio.run_coroutine_threadsafe(coro_factory(), loop()).result(timeout=timeout)


def end(session):
    run(session, session.close)
    with SESSIONS_LOCK:
        SESSIONS.pop(session.id, None)


def reap(max_idle=1800):
    """Close sessions nobody has looked at for a while (frees the player)."""
    now = time.time()
    with SESSIONS_LOCK:
        stale = [s for s in SESSIONS.values() if now - s.last_seen > max_idle]
    for s in stale:
        try:
            end(s)
        except Exception:
            pass
