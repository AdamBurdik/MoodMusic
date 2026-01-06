from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from .models import RecommendHit, Song

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass(frozen=True)
class RecommenderConfig:
    model_name: str = DEFAULT_MODEL


def _song_text(song: Song) -> str:
    # Keep this simple and stable; this is the content we embed for songs.
    tags = ", ".join(song.tags)
    return f"{song.title} — {song.artist}. Tags: {tags}. {song.description}".strip()


def _normalize(matrix: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12
    return matrix / denom


@lru_cache(maxsize=1)
def load_songs() -> list[Song]:
    """Load built-in songs catalog shipped with the package."""
    with resources.files("moodmusic.data").joinpath("songs.json").open("r", encoding="utf-8") as f:
        import json

        raw = json.load(f)

    return [Song.model_validate(item) for item in raw]


@lru_cache(maxsize=2)
def _get_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class MoodRecommender:
    def __init__(self, config: RecommenderConfig | None = None):
        self.config = config or RecommenderConfig(model_name=os.getenv("MOODMUSIC_MODEL", DEFAULT_MODEL))

        self._songs: list[Song] = load_songs()
        self._song_embeddings: np.ndarray | None = None

    def _ensure_song_embeddings(self) -> None:
        if self._song_embeddings is not None:
            return

        model = _get_model(self.config.model_name)
        texts = [_song_text(s) for s in self._songs]
        emb = model.encode(texts, normalize_embeddings=True)
        self._song_embeddings = np.asarray(emb, dtype=np.float32)

    def recommend(self, mood_text: str, k: int = 5) -> list[RecommendHit]:
        mood_text = (mood_text or "").strip()
        if not mood_text:
            raise ValueError("mood_text must be non-empty")

        k = int(k)
        if k < 1:
            raise ValueError("k must be >= 1")

        self._ensure_song_embeddings()
        assert self._song_embeddings is not None

        model = _get_model(self.config.model_name)
        q = model.encode([mood_text], normalize_embeddings=True)
        q = np.asarray(q, dtype=np.float32)

        # With normalized vectors, cosine similarity is just dot product.
        scores = (self._song_embeddings @ q[0]).astype(np.float32)

        topk = min(k, len(self._songs))
        idx = np.argpartition(-scores, topk - 1)[:topk]
        idx = idx[np.argsort(-scores[idx])]

        return [
            RecommendHit(song=self._songs[i], score=float(scores[i]))
            for i in idx
        ]


@lru_cache(maxsize=1)
def default_recommender() -> MoodRecommender:
    return MoodRecommender()
