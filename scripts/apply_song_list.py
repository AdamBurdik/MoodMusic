from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SONGS_PATH = ROOT / "src" / "moodmusic" / "data" / "songs.json"

SONG_LIST = """
Title - Author - Tag1, Tag2, ...
""".strip()


@dataclass(frozen=True)
class Pair:
    title: str
    artist: str


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("&", "and")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]+", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "song"


def parse_pairs(raw: str) -> list[Pair]:
    pairs: list[Pair] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if "—" not in line:
            raise ValueError(f"Invalid line (missing em dash): {line}")
        title, artist = [p.strip() for p in line.split("—", 1)]
        if not title or not artist:
            raise ValueError(f"Invalid line: {line}")
        pairs.append(Pair(title=title, artist=artist))

    # Deduplicate while preserving order.
    seen: set[tuple[str, str]] = set()
    unique: list[Pair] = []
    for p in pairs:
        key = (p.title.casefold(), p.artist.casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def ensure_description(title: str, artist: str) -> str:
    return f"{title} by {artist}."


def load_songs(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("songs.json must be a JSON list")
    return data


def write_songs(path: Path, songs: list[dict]) -> None:
    path.write_text(json.dumps(songs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    songs = load_songs(SONGS_PATH)
    pairs = parse_pairs(SONG_LIST)

    # Index existing songs
    by_title: dict[str, list[int]] = {}
    by_title_artist: dict[tuple[str, str], int] = {}

    for i, s in enumerate(songs):
        title = str(s.get("title") or "").strip()
        artist = str(s.get("artist") or "").strip()
        if not title:
            continue
        tkey = title.casefold()
        by_title.setdefault(tkey, []).append(i)
        if artist:
            by_title_artist[(tkey, artist.casefold())] = i

    # Apply updates/additions
    next_ids: set[str] = {str(s.get("id")) for s in songs if s.get("id")}

    def unique_id(base: str) -> str:
        if base not in next_ids:
            next_ids.add(base)
            return base
        n = 2
        while f"{base}-{n}" in next_ids:
            n += 1
        new = f"{base}-{n}"
        next_ids.add(new)
        return new

    updated = 0
    added = 0

    for p in pairs:
        tkey = p.title.casefold()
        akey = p.artist.casefold()

        if (tkey, akey) in by_title_artist:
            idx = by_title_artist[(tkey, akey)]
            s = songs[idx]
            # Ensure canonical artist/title casing and required fields
            if s.get("title") != p.title:
                s["title"] = p.title
            if s.get("artist") != p.artist:
                s["artist"] = p.artist
                updated += 1
            if not s.get("description"):
                s["description"] = ensure_description(p.title, p.artist)
                updated += 1
            if "tags" not in s or not isinstance(s["tags"], list):
                s["tags"] = []
                updated += 1
            continue

        # Try to reuse an existing entry with same title and Unknown artist.
        reused_idx: int | None = None
        for idx in by_title.get(tkey, []):
            s = songs[idx]
            if str(s.get("artist") or "").strip() == "Unknown":
                reused_idx = idx
                break

        if reused_idx is not None:
            s = songs[reused_idx]
            s["title"] = p.title
            s["artist"] = p.artist
            if not s.get("description"):
                s["description"] = ensure_description(p.title, p.artist)
            if "tags" not in s or not isinstance(s["tags"], list):
                s["tags"] = []
            by_title_artist[(tkey, akey)] = reused_idx
            updated += 1
            continue

        # Otherwise add new.
        new_song = {
            "id": unique_id(f"{slugify(p.artist)}-{slugify(p.title)}"),
            "title": p.title,
            "artist": p.artist,
            "tags": [],
            "description": ensure_description(p.title, p.artist),
        }
        songs.append(new_song)
        idx = len(songs) - 1
        by_title.setdefault(tkey, []).append(idx)
        by_title_artist[(tkey, akey)] = idx
        added += 1

    # Deduplicate exact (title, artist) duplicates, keeping first occurrence.
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for s in songs:
        title = str(s.get("title") or "").strip()
        artist = str(s.get("artist") or "").strip()
        if not title or not artist:
            continue
        key = (title.casefold(), artist.casefold())
        if key in seen:
            continue
        seen.add(key)

        if not s.get("description"):
            s["description"] = ensure_description(title, artist)
        if "tags" not in s or not isinstance(s["tags"], list):
            s["tags"] = []

        deduped.append(s)

    write_songs(SONGS_PATH, deduped)
    print(f"Updated songs.json: updated={updated}, added={added}, total={len(deduped)}")


if __name__ == "__main__":
    main()
