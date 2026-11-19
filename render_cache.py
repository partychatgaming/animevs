"""Shared caches and safe network access for everything that renders images.

Why this exists
---------------
Every card render used to:
  * download the card art again (``requests.get`` with no timeout),
  * download every emoji again from a third-party CDN (also no timeout),
  * re-read ~10 font files and a star sprite from disk,
and it did so once (sometimes twice) per turn.  A slow or failed download
returned ``None`` and the battle died a few lines later.

This module makes all of those lookups cached, time-limited and failure-safe:
  * card art     -> bounded in-memory LRU of the downloaded bytes (+ TTL)
  * emoji        -> memory + on-disk cache, negative caching, circuit breaker
  * fonts        -> one FreeType face per (file, size), loaded once
  * star sprites -> loaded once
Nothing in here ever raises to the caller; on failure a placeholder is used.
"""
import hashlib
import os
import threading
import time
from collections import OrderedDict
from functools import lru_cache
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont
from pilmoji.source import BaseSource

from logger import loggy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# (connect timeout, read timeout) in seconds
HTTP_TIMEOUT = (4, 10)
EMOJI_HTTP_TIMEOUT = (3, 5)
IMAGE_CACHE_MAX_BYTES = _env_int("IMAGE_CACHE_MB", 96) * 1024 * 1024
IMAGE_CACHE_TTL = _env_int("IMAGE_CACHE_TTL_SECONDS", 6 * 60 * 60)
NEGATIVE_TTL = 120            # how long a failed download is remembered
MAX_DOWNLOAD_BYTES = 15 * 1024 * 1024
PNG_COMPRESS_LEVEL = _env_int("CARD_PNG_COMPRESS_LEVEL", 3)

EMOJI_DISK_DIR = os.environ.get("EMOJI_CACHE_DIR") or os.path.join(BASE_DIR, "image_cache", "emoji")

# PIL/FreeType objects are shared between renders, so text drawing is
# serialised.  Drawing holds the GIL anyway, so this costs nothing.
RENDER_LOCK = threading.RLock()

# Renders get their own small thread pool.  On the default pool, a burst of
# battles all rendering at once filled every worker (most of them just waiting
# for RENDER_LOCK) and database calls queued up behind them.  Two workers let
# one card decode/encode while another is being drawn.
_RENDER_EXECUTOR = None
_RENDER_EXECUTOR_LOCK = threading.Lock()


def _render_executor():
    global _RENDER_EXECUTOR
    if _RENDER_EXECUTOR is None:
        with _RENDER_EXECUTOR_LOCK:
            if _RENDER_EXECUTOR is None:
                from concurrent.futures import ThreadPoolExecutor
                _RENDER_EXECUTOR = ThreadPoolExecutor(max_workers=_env_int("RENDER_THREADS", 2), thread_name_prefix="render")
    return _RENDER_EXECUTOR


async def render_async(func, *args, **kwargs):
    """Run an image-rendering function (showcard, showsummon...) off the event loop."""
    import asyncio
    import functools
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_render_executor(), functools.partial(func, *args, **kwargs))

_HEADERS = {"User-Agent": "Mozilla/5.0 (AnimeVS bot image fetcher)"}
_NETWORK_ENABLED = os.environ.get("RENDER_OFFLINE", "") not in ("1", "true", "True")
_local = threading.local()


def _session():
    """One pooled HTTP session per worker thread (keep-alive saves a TLS handshake per image)."""
    s = getattr(_local, "session", None)
    if s is None:
        s = requests.Session()
        s.headers.update(_HEADERS)
        _local.session = s
    return s


def _http_get(url, timeout):
    """Return the body of ``url`` or None.  Never raises."""
    if not _NETWORK_ENABLED:
        return None
    try:
        with _session().get(url, timeout=timeout, stream=True) as resp:
            if resp.status_code != 200:
                loggy.warning(f"image fetch {resp.status_code} for {url}")
                return None
            chunks, size = [], 0
            for chunk in resp.iter_content(64 * 1024):
                size += len(chunk)
                if size > MAX_DOWNLOAD_BYTES:
                    loggy.warning(f"image too large, skipped: {url}")
                    return None
                chunks.append(chunk)
            return b"".join(chunks)
    except Exception as ex:  # timeouts, DNS, TLS, connection resets...
        loggy.warning(f"image fetch failed for {url}: {type(ex).__name__}: {ex}")
        return None


# --------------------------------------------------------------------------- card art
class _ByteLRU:
    """Thread-safe LRU keyed by URL, bounded by total payload size, with TTL."""

    def __init__(self, max_bytes, ttl):
        self.max_bytes = max_bytes
        self.ttl = ttl
        self._data = OrderedDict()   # key -> (bytes, stored_at)
        self._size = 0
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self._lock:
            item = self._data.get(key)
            if item is None:
                self.misses += 1
                return None
            data, stored_at = item
            if self.ttl and time.monotonic() - stored_at > self.ttl:
                self._size -= len(data)
                del self._data[key]
                self.misses += 1
                return None
            self._data.move_to_end(key)
            self.hits += 1
            return data

    def put(self, key, data):
        if len(data) > self.max_bytes:
            return
        with self._lock:
            old = self._data.pop(key, None)
            if old is not None:
                self._size -= len(old[0])
            self._data[key] = (data, time.monotonic())
            self._size += len(data)
            while self._size > self.max_bytes and self._data:
                _, (evicted, _) = self._data.popitem(last=False)
                self._size -= len(evicted)

    def clear(self):
        with self._lock:
            self._data.clear()
            self._size = 0

    def stats(self):
        with self._lock:
            return {"entries": len(self._data), "bytes": self._size, "hits": self.hits, "misses": self.misses}


_image_bytes = _ByteLRU(IMAGE_CACHE_MAX_BYTES, IMAGE_CACHE_TTL)
_failed_urls = {}                 # url -> monotonic time of the failure
_url_locks = {}
_url_locks_guard = threading.Lock()


def _lock_for(url):
    with _url_locks_guard:
        lock = _url_locks.get(url)
        if lock is None:
            if len(_url_locks) > 4096:
                _url_locks.clear()
            lock = _url_locks[url] = threading.Lock()
        return lock


def fetch_image_bytes(url):
    """Download (or reuse) the raw bytes behind an image URL.  Returns None on failure."""
    if not url or not isinstance(url, str) or not url.lower().startswith(("http://", "https://")):
        return None
    data = _image_bytes.get(url)
    if data is not None:
        return data
    failed_at = _failed_urls.get(url)
    if failed_at is not None and time.monotonic() - failed_at < NEGATIVE_TTL:
        return None
    with _lock_for(url):                      # collapse concurrent downloads of the same art
        data = _image_bytes.get(url)
        if data is not None:
            return data
        started = time.monotonic()
        data = _http_get(url, HTTP_TIMEOUT)
        if data is None and time.monotonic() - started < 2:
            # failed fast (reset / 5xx): one retry.  Timeouts are not retried so a
            # hung CDN costs one timeout, not two.
            data = _http_get(url, HTTP_TIMEOUT)
        if data is None:
            if len(_failed_urls) > 2048:
                _failed_urls.clear()
            _failed_urls[url] = time.monotonic()
            return None
        _failed_urls.pop(url, None)
        _image_bytes.put(url, data)
        return data


def placeholder_image(size=(1200, 600), label=None):
    """Neutral card background used when art cannot be downloaded."""
    im = Image.new("RGBA", size, (28, 30, 38, 255))
    draw = ImageDraw.Draw(im)
    w, h = size
    draw.rectangle((8, 8, w - 9, h - 9), outline=(90, 96, 115, 255), width=4)
    if label:
        try:
            draw.text((40, h - 70), str(label)[:60], (150, 156, 175), font=get_font("Neuton-Light.ttf", 34))
        except Exception:
            pass
    return im


def load_image(url, fallback_label=None, fallback_size=(1200, 600)):
    """Return a fresh, editable RGBA ``PIL.Image`` for ``url``.

    Always returns an image: a placeholder is produced when the download or
    decode fails, so callers never have to deal with ``None``.
    """
    data = fetch_image_bytes(url)
    if data is not None:
        try:
            im = Image.open(BytesIO(data))
            im.load()
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA")
            return im
        except Exception as ex:
            loggy.warning(f"could not decode image {url}: {type(ex).__name__}: {ex}")
            _failed_urls[url] = time.monotonic()
    return placeholder_image(fallback_size, fallback_label)


def encode_png(im):
    """Encode to an in-memory PNG, rewound and ready to upload.

    A fully opaque RGBA image is saved as RGB: identical on screen, ~20% fewer
    bytes to upload every turn and ~25% less time to encode.
    """
    if im.mode == "RGBA":
        try:
            if im.getchannel("A").getextrema()[0] == 255:
                im = im.convert("RGB")
        except Exception:
            pass
    out = BytesIO()
    im.save(out, "PNG", compress_level=PNG_COMPRESS_LEVEL)
    out.seek(0)
    return out


# --------------------------------------------------------------------------- fonts & sprites
def _freeze(value):
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, _freeze(v)) for k, v in value.items()))
    return value


class CachedFont(ImageFont.FreeTypeFont):
    """FreeType font that remembers the glyph bitmaps and measurements it produced.

    Laying out and rasterising a line of text is by far the most expensive part
    of a card render (the pixel font used for move names costs ~150 ms per
    line), and the same lines are drawn turn after turn.  The cached bitmap is
    exactly what FreeType produced, so output is pixel-identical.
    """

    _CACHE_MAX = 384

    def _memo(self, kind, text, args, kwargs, compute):
        try:
            key = (kind, text, _freeze(args), _freeze(kwargs))
            hash(key)
        except TypeError:
            return compute()
        cache = self.__dict__.get("_rc_cache")
        if cache is None:
            cache = self.__dict__["_rc_cache"] = OrderedDict()
        hit = cache.get(key)
        if hit is not None:
            cache.move_to_end(key)
            return hit[0]
        value = compute()
        cache[key] = (value,)
        if len(cache) > self._CACHE_MAX:
            cache.popitem(last=False)
        return value

    def getmask2(self, text, mode="", *args, **kwargs):
        if mode == "RGBA":      # colour bitmaps are modified in place by ImageDraw
            return super().getmask2(text, mode, *args, **kwargs)
        return self._memo("mask2", text, (mode,) + args, kwargs,
                          lambda: ImageFont.FreeTypeFont.getmask2(self, text, mode, *args, **kwargs))

    def getbbox(self, text, *args, **kwargs):
        return self._memo("bbox", text, args, kwargs,
                          lambda: ImageFont.FreeTypeFont.getbbox(self, text, *args, **kwargs))

    def getlength(self, text, *args, **kwargs):
        return self._memo("length", text, args, kwargs,
                          lambda: ImageFont.FreeTypeFont.getlength(self, text, *args, **kwargs))

    def getsize(self, text, *args, **kwargs):
        def compute():
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                return ImageFont.FreeTypeFont.getsize(self, text, *args, **kwargs)
        return self._memo("size", text, args, kwargs, compute)


# Fonts with a faster drop-in copy.  Jersey 20 (the move-list font) is built from
# hundreds of tiny squares and carries ttfautohint bytecode; running that
# bytecode is ~90 ms per line of text.  The copy has the hinting stripped
# (fonttools) and renders ~20x faster.  At the sizes the cards use the result
# is the same image (at most a few levels of anti-aliasing difference).
# The font is under the SIL Open Font License, which allows this.
_FAST_FONT_VARIANTS = {
    "Jersey20-Regular.ttf": "Jersey20-Regular-NoHint.ttf",
}


@lru_cache(maxsize=256)
def get_font(name, size):
    """Font for ``name`` at ``size``, loaded once.  ``name`` may be a bare file name or a 'fonts/...' path."""
    fast = _FAST_FONT_VARIANTS.get(os.path.basename(name))
    if fast and os.path.exists(os.path.join(FONT_DIR, fast)):
        name = fast
    path = name
    if not os.path.isabs(path):
        candidate = os.path.join(BASE_DIR, name)
        path = candidate if os.path.exists(candidate) else os.path.join(FONT_DIR, os.path.basename(name))
    return CachedFont(path, int(size))


_STAR_FILES = (
    (10, "DARK STARS.png"),
    (9, "PURPLE STARS.png"),
    (7, "RED STARS.png"),
    (4, "BLUE STARS.png"),
    (0, "STARS.png"),
)


@lru_cache(maxsize=None)
def _star_sprite(filename):
    im = Image.open(os.path.join(BASE_DIR, filename))
    im.load()
    return im.convert("RGBA")


def get_star(tier):
    """Star sprite for a card tier (always returns a sprite, even for odd tiers)."""
    try:
        tier = int(tier)
    except (TypeError, ValueError):
        tier = 1
    for minimum, filename in _STAR_FILES:
        if tier >= minimum:
            return _star_sprite(filename)
    return _star_sprite("STARS.png")


# --------------------------------------------------------------------------- emoji
class CachedEmojiSource(BaseSource):
    """pilmoji source that remembers every emoji it has fetched (RAM + disk).

    The stock source re-downloads each emoji on every render and has no
    timeout.  Here a failure is remembered for a while and, after several
    failures in a row, the network is skipped entirely for a cool-down period
    so that a CDN outage cannot slow battles down.
    """

    EMOJI_URL = "https://emojicdn.elk.sh/{emoji}?style=twitter"
    DISCORD_URL = "https://cdn.discordapp.com/emojis/{id}.png"
    BREAKER_THRESHOLD = 4
    BREAKER_COOLDOWN = 300

    def __init__(self, disk_dir=EMOJI_DISK_DIR):
        self._mem = {}
        self._miss = {}
        self._lock = threading.Lock()
        self._failures = 0
        self._open_until = 0.0
        self._disk_dir = disk_dir
        try:
            os.makedirs(self._disk_dir, exist_ok=True)
        except OSError:
            self._disk_dir = None

    def _disk_path(self, key):
        if not self._disk_dir:
            return None
        return os.path.join(self._disk_dir, hashlib.sha1(key.encode("utf-8")).hexdigest() + ".png")

    def _get(self, key, url):
        data = self._mem.get(key)
        if data is not None:
            return BytesIO(data)
        now = time.monotonic()
        missed_at = self._miss.get(key)
        if missed_at is not None and now - missed_at < 600:
            return None
        path = self._disk_path(key)
        if path and os.path.exists(path):
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                if data:
                    self._mem[key] = data
                    return BytesIO(data)
            except OSError:
                pass
        if now < self._open_until:          # circuit open: don't touch the network
            return None
        data = _http_get(url, EMOJI_HTTP_TIMEOUT)
        with self._lock:
            if data is None:
                self._miss[key] = now
                self._failures += 1
                if self._failures >= self.BREAKER_THRESHOLD:
                    self._open_until = now + self.BREAKER_COOLDOWN
                    self._failures = 0
                    loggy.warning("emoji CDN unreachable; rendering text without emoji images for a few minutes")
                return None
            self._failures = 0
            self._mem[key] = data
        if path:
            try:
                tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
                with open(tmp, "wb") as fh:
                    fh.write(data)
                os.replace(tmp, path)
            except OSError:
                pass
        return BytesIO(data)

    def get_emoji(self, emoji, /):
        from urllib.parse import quote_plus
        return self._get("u:" + emoji, self.EMOJI_URL.format(emoji=quote_plus(emoji)))

    def get_discord_emoji(self, id, /):
        return self._get(f"d:{int(id)}", self.DISCORD_URL.format(id=int(id)))


EMOJI_SOURCE = CachedEmojiSource()


def cache_stats():
    return {"images": _image_bytes.stats(), "emoji": len(EMOJI_SOURCE._mem), "fonts": get_font.cache_info()._asdict()}
