from __future__ import annotations

import argparse
import json
import sys

from .recommender import default_recommender


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="moodmusic-recommend", description="Recommend songs by mood text")
    p.add_argument(
        "mood_text",
        nargs="+",
        help="Your mood description (one or more words/sentences).",
    )
    p.add_argument("-k", type=int, default=5, help="How many recommendations to return (default: 5)")
    p.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable text.",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    mood_text = " ".join(args.mood_text).strip()
    rec = default_recommender()

    try:
        hits = rec.recommend(mood_text, k=args.k)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(2)

    if args.json:
        payload = {
            "model": rec.config.model_name,
            "results": [
                {
                    "score": h.score,
                    "song": h.song.model_dump(),
                }
                for h in hits
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"Model: {rec.config.model_name}")
    for i, h in enumerate(hits, start=1):
        print(f"{i}. {h.song.title} — {h.song.artist}  (score={h.score:.4f})")
