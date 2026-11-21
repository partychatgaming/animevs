"""Download a batch of character images, store them on Supabase, and point the card at the new link."""

import datetime
import io

import requests
from PIL import Image

from tools.refresh_card_art import MAX_DOWNLOAD, Settings, Storage, slug, to_jpeg

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def storage():
    cfg = Settings()
    if not cfg.supabase_url or not cfg.supabase_key:
        return None, "Add SUPABASE_URL and SUPABASE_SERVICE_KEY to .env before hosting images."
    problem = _key_problem(cfg.supabase_key)
    if problem:
        return None, problem
    return Storage(cfg.supabase_url, cfg.supabase_key, cfg.bucket), None


def _key_problem(key):
    if key.startswith("sb_publishable"):
        return ("Image hosting needs the secret key, not the publishable key. In Supabase open "
                "Project Settings → API Keys, copy the secret key (sb_secret_…), and put it in "
                "SUPABASE_SERVICE_KEY. Editing gameplay data still works.")
    if key.startswith("eyJ"):
        role = _jwt_role(key)
        if role and role != "service_role":
            return ("SUPABASE_SERVICE_KEY is a " + role + " key. Image hosting needs the "
                    "service_role secret from Project Settings → API Keys.")
    return None


def _jwt_role(key):
    import base64
    import json
    try:
        payload = key.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("role")
    except Exception:
        return None


def rows_from_pairs(names, urls):
    """Parallel name and url fields from the image table. Empty rows are skipped."""
    rows, errors = [], []
    for number, (name, url) in enumerate(zip(names, urls), 1):
        name, url = (name or "").strip(), (url or "").strip()
        if not name and not url:
            continue
        if not url:
            continue
        if not name:
            errors.append({"line": number, "text": url, "error": "Missing character name"})
            continue
        if not url.lower().startswith(("http://", "https://")):
            errors.append({"line": number, "text": name, "error": "Image link must start with http:// or https://"})
            continue
        rows.append({"line": number, "name": name, "url": url})
    return rows, errors


def parse_lines(text):
    """Lines of `Character Name | https://...`. Blank lines and # comments are ignored."""
    rows, errors = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parsed = _split(line)
        if parsed is None:
            errors.append({"line": number, "text": line, "error": "Use Name | https://image"})
            continue
        if parsed == ("", ""):
            continue
        name, url = parsed
        if not url:
            continue
        if not name:
            errors.append({"line": number, "text": line, "error": "Missing character name"})
            continue
        if not url.lower().startswith(("http://", "https://")):
            errors.append({"line": number, "text": line, "error": "Image link must start with http:// or https://"})
            continue
        rows.append({"line": number, "name": name, "url": url})
    return rows, errors


def _split(line):
    for sep in ("|", "\t"):
        if sep in line:
            name, url = line.split(sep, 1)
            name, url = name.strip(), url.strip()
            if not url:
                return "", ""
            return name, url
    if "," in line:
        name, url = line.rsplit(",", 1)
        if url.strip().lower().startswith("http"):
            return name.strip(), url.strip()
    return None


def download_image(url):
    response = requests.get(url, timeout=25, stream=True, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    response.raise_for_status()
    chunks = []
    size = 0
    for chunk in response.iter_content(64 * 1024):
        if not chunk:
            continue
        size += len(chunk)
        if size > MAX_DOWNLOAD:
            raise RuntimeError("image is larger than 15MB")
        chunks.append(chunk)
    data = b"".join(chunks)
    if not data:
        raise RuntimeError("empty download")
    image = Image.open(io.BytesIO(data))
    image.seek(0)
    return to_jpeg(image)[0]


def host_card_art(cards_col, card, source_url, store):
    """Download one image, upload it, and set CARD_ART. Returns the public URL."""
    jpeg = download_image(source_url)
    path = f"{slug(card.get('UNIVERSE') or 'card')}/{slug(card['NAME'])}.jpg"
    link = store.upload(path, jpeg)
    previous = card.get("CARD_ART")
    update = {
        "CARD_ART": link,
        "CARD_ART_SOURCE": source_url,
        "CARD_ART_UPDATED": datetime.datetime.utcnow().isoformat(timespec="seconds"),
    }
    if previous and previous != link:
        update["CARD_ART_PREV"] = previous
    cards_col.update_one(
        {"_id": card["_id"]},
        {"$set": update, "$unset": {"CARD_ART_CROP": ""}},
    )
    return link
