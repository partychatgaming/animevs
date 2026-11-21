"""Batch-replace card art: search -> pick best image -> upload to Supabase -> point the card at it.

    python tools/refresh_card_art.py --dry-run --limit 10      # look, change nothing
    python tools/refresh_card_art.py --universe Naruto         # one universe
    python tools/refresh_card_art.py                           # every card (resumable)

For each card in Mongo CARDS it takes the AniList character art (matched to the
card's universe), falling back to Google Images via SerpApi only when AniList has
nothing (--source google flips the order; --source anilist-only never uses Google), downloads
the candidates, scores them (resolution, portrait shape, title match, source),
uploads the winner to the Supabase Storage bucket as a JPEG and sets
CARD_ART to the public Supabase URL.  The renderer already prefers CARD_ART
over the old template PATH, so every card screen and battle switches over.
PATH is never touched; the previous CARD_ART / CARD_ART_CROP are kept in
CARD_ART_PREV / CARD_ART_CROP_PREV so --rollback can restore them.

.env keys (only names are read here; values never printed):
    MONGO_LOGIN            existing
    SERPAPI_KEY            serpapi.com key (optional: without it only AniList is used)
    SUPABASE_URL           https://<project>.supabase.co
    SUPABASE_SERVICE_KEY   service_role key (Settings -> API).  Keep it server-side only.
    SUPABASE_BUCKET        optional, default "card-art" (created public on first run)

Progress is saved in tools/.card_art_state.json, so an interrupted run resumes;
--force redoes cards already done.  Results go to tools/card_art_report.csv.
"""
import argparse
import csv
import datetime
import difflib
import hashlib
import io
import json
import math
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlparse

import requests
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, ".card_art_state.json")
REPORT_FILE = os.path.join(HERE, "card_art_report.csv")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
MIN_SHORT_SIDE = 500          # reject smaller images
MAX_LONG_SIDE = 1600          # stored size cap
MAX_DOWNLOAD = 15 * 1024 * 1024
CANDIDATES = 8                # images downloaded per card from search
TIMEOUT = 20

# Stock/watermark sites and thumbnail farms produce bad card art.
BLOCKED_HOSTS = (
    "shutterstock", "alamy", "dreamstime", "gettyimages", "istockphoto", "depositphotos",
    "123rf", "stock.adobe", "vectorstock", "freepik", "pngtree", "lookaside.fbsbx",
    "redbubble", "teepublic", "amazon.", "ebay.", "etsy", "aliexpress", "walmart",
    "pinimg.com/236x", "pinimg.com/474x", "tiktok", "youtube", "ytimg",
)
GOOD_HOSTS = ("fandom.com", "wikia", "anilist", "myanimelist", "zerochan", "artstation", "pixiv")
BAD_WORDS = ("cosplay", "figure", "funko", "nendoroid", "plush", "shirt", "poster for sale",
             "keychain", "meme", "lego", "sticker", "wallpaper 4k collage", "tier list", "vs ")


# ----------------------------------------------------------------- utilities
def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:80] or "card"


# Form / variant tags in card names ("KCM Naruto", "Anbu Kakashi Hatake") - not part of the character name.
VARIANT_WORDS = {
    "kcm", "kcm2", "bm", "dms", "ems", "ms", "anbu", "sage", "six", "paths", "path", "rinnegan", "sharingan",
    "captain", "sensei", "granny", "lord", "lady", "young", "kid", "old", "adult", "teen", "seal", "mode",
    "base", "final", "form", "awakened", "true", "ssj", "ssj2", "ssj3", "ssj4", "ssg", "ssb", "ui", "mui",
    "bankai", "hollow", "shikai", "gear", "second", "third", "fourth", "fifth", "dark", "evil", "god",
}


NUMBERS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
           "8": "eight", "9": "nine", "10": "ten"}


def core_name(name):
    """Card name without variant tags/numbers: 'KCM2 Naruto' -> 'Naruto', '10 Tails' -> 'ten Tails'."""
    parts = str(name).split()
    keep = []
    for i, w in enumerate(parts):
        lw = w.lower().strip(".")
        if lw in VARIANT_WORDS and len(parts) > 1:
            continue
        if w.isdigit():
            if w in NUMBERS and i + 1 < len(parts):
                keep.append(NUMBERS[w])
            continue
        keep.append(w)
    return " ".join(keep) or str(name)


def name_matches(card_name, char_names):
    return _match_strength(card_name, char_names) > 0


def _match_strength(card_name, char_names):
    """2 = every card-name word found in a character name; 1 = the character's whole name is inside
    the card name ('Levi' for 'Levi Ackerman'); 0 = no match ('Obito Uchiha' vs 'Itachi Uchiha')."""
    core = set(words(core_name(card_name)))
    best = 0
    for n in char_names:
        char = set(words(n))
        if not core or not char:
            continue
        if all(any(_same(w, x) for x in char) for w in core):
            return 2
        if all(any(_same(x, w) for w in core) for x in char):
            best = 1
    return best


def norm(word):
    """Romanization-insensitive: hyuuga/hyuga, chouji/choji, jiroubou/jirobo."""
    return word.replace("ou", "o").replace("uu", "u").replace("oo", "o")


def words(text):
    return [w for w in re.split(r"[^a-z0-9]+", str(text).lower()) if len(w) > 1]


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


class Settings:
    """Reads .env through python-decouple (same as db.py) without echoing values."""

    def __init__(self):
        from decouple import config
        self.serpapi_key = config("SERPAPI_KEY", default="")
        self.supabase_url = config("SUPABASE_URL", default="").strip().rstrip("/")
        for suffix in ("/rest/v1", "/storage/v1", "/auth/v1"):
            if self.supabase_url.endswith(suffix):
                self.supabase_url = self.supabase_url[: -len(suffix)]
        self.supabase_key = config("SUPABASE_SERVICE_KEY", default="")
        self.bucket = config("SUPABASE_BUCKET", default="card-art")

    def check(self, dry_run):
        missing = []
        if not dry_run:
            if not self.supabase_url:
                missing.append("SUPABASE_URL")
            if not self.supabase_key:
                missing.append("SUPABASE_SERVICE_KEY")
        if missing:
            sys.exit("Missing in .env: " + ", ".join(missing))
        if not self.serpapi_key:
            print("note: SERPAPI_KEY not set - using AniList only")


# ----------------------------------------------------------------- sources
class Sources:
    def __init__(self, serpapi_key, session=None):
        self.key = serpapi_key
        self.http = session or requests.Session()
        self.http.headers["User-Agent"] = UA
        self.serp_calls = 0
        self.lock = threading.Lock()
        self._rosters, self._roster_locks = {}, {}

    def google(self, name, universe):
        """SerpApi Google Images.  Returns [{url, title, source, w, h, origin}]."""
        if not self.key:
            return []
        q = f"{name} {universe} anime official art"
        params = {"engine": "google_images", "q": q, "safe": "active", "api_key": self.key,
                  "imgar": "t"}  # tall / portrait images first
        with self.lock:
            self.serp_calls += 1
        r = self.http.get("https://serpapi.com/search.json", params=params, timeout=40)
        if r.status_code == 429:
            raise RuntimeError("SerpApi rate limit / monthly quota reached")
        r.raise_for_status()
        out = []
        for it in r.json().get("images_results", [])[:40]:
            url = it.get("original")
            if not url:
                continue
            out.append({"url": url, "title": it.get("title", ""), "source": it.get("link") or it.get("source", ""),
                        "w": it.get("original_width") or 0, "h": it.get("original_height") or 0, "origin": "google"})
        return out

    def _gql(self, query, variables):
        for attempt in range(6):
            try:
                r = self.http.post("https://graphql.anilist.co", json={"query": query, "variables": variables},
                                   timeout=TIMEOUT)
            except requests.RequestException:
                time.sleep(3 * (attempt + 1))
                continue
            if r.status_code == 429:
                time.sleep(int(r.headers.get("Retry-After", 30)) + 1)
                continue
            r.raise_for_status()
            return r.json().get("data") or {}
        raise RuntimeError("AniList keeps rate-limiting")

    def roster(self, universe):
        """Every character of the universe's main anime/manga entries (cached per universe)."""
        with self.lock:
            lock = self._roster_locks.setdefault(universe, threading.Lock())
        with lock:
            if universe in self._rosters:
                return self._rosters[universe]
            media_q = """query ($s: String) { Page(perPage: 10) { media(search: $s, sort: [SEARCH_MATCH, POPULARITY_DESC]) {
                id title { romaji english } synonyms popularity } } }"""
            uni = set(words(universe))
            media = []
            for m in self._gql(media_q, {"s": universe}).get("Page", {}).get("media", []):
                titles = [m["title"].get("romaji") or "", m["title"].get("english") or ""] + (m.get("synonyms") or [])
                if any(uni and uni <= set(words(t)) for t in titles):
                    media.append(m)
            media = sorted(media, key=lambda m: -(m.get("popularity") or 0))[:4]
            chars_q = """query ($id: Int, $p: Int) { Media(id: $id) { characters(page: $p, perPage: 25, sort: [FAVOURITES_DESC]) {
                pageInfo { hasNextPage } nodes { id name { full alternative } image { large } favourites } } } }"""
            found = {}
            for m in media:
                for page in range(1, 41):
                    data = self._gql(chars_q, {"id": m["id"], "p": page}).get("Media") or {}
                    block = data.get("characters") or {}
                    for ch in block.get("nodes", []):
                        found.setdefault(ch["id"], ch)
                    if not block.get("pageInfo", {}).get("hasNextPage"):
                        break
            out = list(found.values())
            print(f"AniList roster for {universe}: {len(out)} characters from {len(media)} titles")
            self._rosters[universe] = out
            return out

    def anilist(self, name, universe):
        """AniList art: match against the universe's full roster first, then name search."""
        out = []
        for ch in self.roster(universe):
            img = (ch.get("image") or {}).get("large")
            names = [ch["name"]["full"] or ""] + (ch["name"].get("alternative") or [])
            if img and not img.endswith("default.jpg") and name_matches(name, names):
                out.append({"url": img, "title": ch["name"]["full"] + " " + universe, "source": "anilist.co",
                            "w": 0, "h": 0, "origin": "anilist", "char_name": ch["name"]["full"] or "",
                            "alt_names": ch["name"].get("alternative") or [], "favourites": ch.get("favourites") or 0,
                            "rank": 0})
        if out:
            out.sort(key=lambda c: -c["favourites"])
            for i, c in enumerate(out):
                c["rank"] = i
            return out[:CANDIDATES]
        return self.anilist_search(name, universe)

    def anilist_search(self, name, universe):
        """AniList character search matched to the universe.  Retries with single name words."""
        base = core_name(name)
        tries = [base] + [w for w in base.split() if len(w) > 2 and w.lower() != base.lower()]
        for term in tries:
            found = [c for c in self._anilist(term, universe)
                     if name_matches(name, [c["char_name"]] + list(c["alt_names"]))]
            if found:
                return found
        return []

    def _anilist(self, name, universe):
        query = """query ($s: String) { Page(perPage: 25) { characters(search: $s, sort: [SEARCH_MATCH, FAVOURITES_DESC]) {
            name { full alternative } image { large } favourites
            media(perPage: 25) { nodes { title { romaji english } synonyms } } } } }"""
        data = self._gql(query, {"s": name})
        uni = set(words(universe))
        out = []
        for ch in data.get("Page", {}).get("characters", []):
            img = (ch.get("image") or {}).get("large")
            if not img or img.endswith("default.jpg"):
                continue
            titles = []
            for m in ch.get("media", {}).get("nodes", []):
                t = m.get("title") or {}
                titles += [t.get("romaji") or "", t.get("english") or ""] + (m.get("synonyms") or [])
            in_universe = any(uni and uni <= set(words(t)) for t in titles) or any(
                uni & set(words(t)) for t in titles)
            if not in_universe:
                continue
            out.append({"url": img, "title": ch["name"]["full"] + " " + universe, "source": "anilist.co",
                        "w": 0, "h": 0, "origin": "anilist", "char_name": ch["name"]["full"],
                        "alt_names": ch["name"].get("alternative") or [], "favourites": ch.get("favourites") or 0,
                        "rank": len(out)})
        return out

    def download(self, url):
        r = self.http.get(url, timeout=TIMEOUT, stream=True, headers={"Referer": ""})
        r.raise_for_status()
        data = io.BytesIO()
        for chunk in r.iter_content(64 * 1024):
            data.write(chunk)
            if data.tell() > MAX_DOWNLOAD:
                raise ValueError("too large")
        img = Image.open(io.BytesIO(data.getvalue()))
        img.load()
        return img


# ----------------------------------------------------------------- scoring
def host_of(url):
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def prefilter(c):
    blob = (c["url"] + " " + c.get("source", "")).lower()
    if any(b in blob for b in BLOCKED_HOSTS):
        return False
    if c["url"].lower().split("?")[0].endswith((".svg", ".gif")):
        return False
    title = c.get("title", "").lower()
    return not any(b in title for b in BAD_WORDS)


def score(c, img, name):
    w, h = img.size
    short = min(w, h)
    if short < MIN_SHORT_SIDE and c["origin"] != "anilist":
        return None
    s = min(short, 1400) / 1400 * 40                      # resolution, up to 40
    ratio = h / max(w, 1)
    if 1.15 <= ratio <= 1.8:
        s += 30                                           # portrait: ideal for the frame
    elif 0.9 <= ratio < 1.15:
        s += 15
    elif ratio > 1.8:
        s += 10                                           # very tall: still cropable
    else:
        s += 0                                            # landscape: often group shots
    name_words = set(words(name))
    title_words = set(words(c.get("title", "")))
    if name_words and c["origin"] != "anilist":
        s += 20 * len(name_words & title_words) / len(name_words)
    if c["origin"] == "anilist":
        # exact character beats variants ("Goku" vs "Goku Black"); earlier search hits rank higher
        names = [c.get("char_name", "")] + list(c.get("alt_names") or [])
        strength = _match_strength(name, names)
        best = None if not strength else (40 if strength == 2 else 28)
        if best is None:
            return None
        s += best + 6 * math.log10(c.get("favourites", 0) + 1) - 10 * c.get("rank", 0)
    blob = (c["url"] + " " + c.get("source", "")).lower()
    if any(g in blob for g in GOOD_HOSTS):
        s += 10
    return s


def _same(a, b):
    """Loose word match: goku~gokuu, hyuga~hyuuga, deidera~deidara (typo)."""
    a, b = norm(a), norm(b)
    if a == b or (min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a))):
        return True
    return min(len(a), len(b)) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.83


def to_jpeg(img):
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (16, 18, 26))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    if max(img.size) > MAX_LONG_SIDE:
        img.thumbnail((MAX_LONG_SIDE, MAX_LONG_SIDE), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90, optimize=True, progressive=True)
    return buf.getvalue(), img.size


def pick(sources, name, universe, log, order=("anilist", "google")):
    """Best image for a card -> (jpeg_bytes, size, candidate) or None.
    Sources are tried in order; the next one is used only if the previous found nothing usable."""
    seen = set()
    for src in order:
        try:
            pool = sources.anilist(name, universe) if src == "anilist" else \
                [c for c in sources.google(name, universe) if prefilter(c)]
        except Exception as ex:
            log(f"{src} failed: {ex}")
            if "quota" in str(ex):
                raise
            continue
        best = None
        tried = 0
        for c in pool:
            if tried >= CANDIDATES:
                break
            if c.get("w") and c.get("h") and min(c["w"], c["h"]) < MIN_SHORT_SIDE and c["origin"] != "anilist":
                continue
            tried += 1
            try:
                img = sources.download(c["url"])
            except Exception:
                continue
            s = score(c, img, name)
            if s is None:
                continue
            data, size = to_jpeg(img)
            digest = hashlib.sha1(data).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            if not best or s > best[0]:
                best = (s, data, size, c)
        if best:
            return best[1:]
    return None


# ----------------------------------------------------------------- supabase
class Storage:
    def __init__(self, url, key, bucket, session=None):
        self.url, self.bucket = url, bucket
        self.http = session or requests.Session()
        # New sb_secret_ keys go on apikey only; legacy service_role JWTs also on Authorization.
        self.headers = {"apikey": key}
        if key.startswith("eyJ"):
            self.headers["Authorization"] = f"Bearer {key}"

    def ensure_bucket(self):
        r = self.http.get(f"{self.url}/storage/v1/bucket/{self.bucket}", headers=self.headers, timeout=TIMEOUT)
        if r.status_code == 200:
            if not r.json().get("public"):
                print(f"warning: bucket '{self.bucket}' is private; links will not load in Discord")
            return
        r = self.http.post(f"{self.url}/storage/v1/bucket", headers=self.headers, timeout=TIMEOUT,
                           json={"id": self.bucket, "name": self.bucket, "public": True,
                                 "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
                                 "file_size_limit": 10 * 1024 * 1024})
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Could not create bucket '{self.bucket}': HTTP {r.status_code} {r.text[:200]}")
        print(f"created public bucket '{self.bucket}'")

    def upload(self, path, data):
        r = self.http.post(f"{self.url}/storage/v1/object/{self.bucket}/{quote(path)}", data=data,
                           headers={**self.headers, "Content-Type": "image/jpeg", "x-upsert": "true",
                                    "Cache-Control": "max-age=31536000"}, timeout=60)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"upload HTTP {r.status_code}: {r.text[:200]}")
        return f"{self.url}/storage/v1/object/public/{self.bucket}/{quote(path)}"


# ----------------------------------------------------------------- run
ORDER = {"anilist": ("anilist", "google"), "google": ("google", "anilist"),
         "anilist-only": ("anilist",)}


def run(args, cards_col, sources, storage, state):
    query = {}
    if args.universe:
        query["UNIVERSE"] = args.universe
    if args.card:
        query["NAME"] = args.card
    fields = {"NAME": 1, "UNIVERSE": 1, "CARD_ART": 1, "CARD_ART_CROP": 1}
    cards = list(cards_col.find(query, fields))
    todo = [c for c in cards if args.force or c["NAME"] not in state]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(cards)} cards matched, {len(todo)} to process"
          f"{' (dry run: nothing uploaded or changed)' if args.dry_run else ''}")
    lock = threading.Lock()
    rows = []
    stop = threading.Event()

    def save_state():
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=1)
        os.replace(tmp, STATE_FILE)

    def work(card):
        if stop.is_set():
            return
        name, uni = card["NAME"], card.get("UNIVERSE") or ""
        notes = []
        try:
            got = pick(sources, name, uni, notes.append, ORDER[args.source])
        except RuntimeError as ex:
            stop.set()
            print(f"STOPPING: {ex}")
            return
        if not got:
            row = [name, uni, "no-image", "", "", "; ".join(notes)]
        else:
            data, size, cand = got
            if args.dry_run:
                row = [name, uni, "dry-run", cand["url"], f"{size[0]}x{size[1]}", cand["origin"]]
            else:
                try:
                    path = f"{slug(uni)}/{slug(name)}.jpg"
                    link = storage.upload(path, data)
                    update = {"CARD_ART": link, "CARD_ART_CROP": None, "CARD_ART_SOURCE": cand["url"],
                              "CARD_ART_UPDATED": datetime.datetime.utcnow().isoformat(timespec="seconds")}
                    if not str(card.get("CARD_ART") or "").startswith(storage.url):
                        update["CARD_ART_PREV"] = card.get("CARD_ART")
                        update["CARD_ART_CROP_PREV"] = card.get("CARD_ART_CROP")
                    cards_col.update_one({"_id": card["_id"]}, {"$set": update})
                    row = [name, uni, "updated", link, f"{size[0]}x{size[1]}", cand["origin"]]
                    with lock:
                        state[name] = link
                        save_state()
                except Exception as ex:
                    row = [name, uni, "error", "", "", str(ex)[:200]]
        with lock:
            rows.append(row)
            print(f"[{len(rows)}/{len(todo)}] {row[2]:8} {name} ({uni}) {row[5] if row[2] != 'updated' else ''}")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for f in as_completed([pool.submit(work, c) for c in todo]):
            f.result()

    with open(REPORT_FILE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["NAME", "UNIVERSE", "RESULT", "LINK", "SIZE", "SOURCE/NOTE"])
        w.writerows(sorted(rows))
    counts = {}
    for r in rows:
        counts[r[2]] = counts.get(r[2], 0) + 1
    print(f"done: {counts}  SerpApi searches used: {sources.serp_calls}  report: {REPORT_FILE}")
    return rows


def rollback(cards_col, args):
    query = {"CARD_ART_UPDATED": {"$exists": True}}
    if args.universe:
        query["UNIVERSE"] = args.universe
    if args.card:
        query["NAME"] = args.card
    n = 0
    for c in cards_col.find(query, {"CARD_ART_PREV": 1, "CARD_ART_CROP_PREV": 1}):
        cards_col.update_one({"_id": c["_id"]}, {
            "$set": {"CARD_ART": c.get("CARD_ART_PREV"), "CARD_ART_CROP": c.get("CARD_ART_CROP_PREV")},
            "$unset": {"CARD_ART_UPDATED": "", "CARD_ART_SOURCE": "", "CARD_ART_PREV": "", "CARD_ART_CROP_PREV": ""}})
        n += 1
    print(f"rolled back {n} cards (Supabase files left in place)")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--universe", help="only cards from this UNIVERSE")
    p.add_argument("--card", help="only this card NAME")
    p.add_argument("--limit", type=int, default=0, help="max cards this run")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--force", action="store_true", help="redo cards already done")
    p.add_argument("--dry-run", action="store_true", help="search and score only; no upload, no DB writes")
    p.add_argument("--source", choices=sorted(ORDER), default="anilist",
                   help="anilist (default: AniList, Google only if AniList has nothing), google, or anilist-only")
    p.add_argument("--rollback", action="store_true", help="restore previous CARD_ART values")
    args = p.parse_args(argv)

    sys.path.insert(0, os.path.dirname(HERE))
    import db  # noqa: E402  (connects with MONGO_LOGIN from .env)
    if args.rollback:
        return rollback(db.cards_col, args)
    cfg = Settings()
    cfg.check(args.dry_run)
    storage = None
    if not args.dry_run:
        storage = Storage(cfg.supabase_url, cfg.supabase_key, cfg.bucket)
        try:
            storage.ensure_bucket()
        except RuntimeError as exc:
            sys.exit(str(exc))
    state = {} if args.dry_run else load_state()
    run(args, db.cards_col, Sources(cfg.serpapi_key), storage, state)


if __name__ == "__main__":
    main()
