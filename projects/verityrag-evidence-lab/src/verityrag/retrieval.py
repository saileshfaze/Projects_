"""Deterministic, offline lexical retrieval with two complementary rankers."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Iterable

TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def chargrams(text: str, n: int = 3) -> list[str]:
    normalized = " ".join(tokenize(text))
    return [normalized[i : i + n] for i in range(max(0, len(normalized) - n + 1))]


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    body: str
    source: str = "synthetic"
    category: str = "general"

    @property
    def text(self) -> str:
        return f"{self.title} {self.title} {self.body}"


@dataclass(frozen=True)
class Hit:
    document: Document
    score: float
    bm25_rank: int | None
    char_rank: int | None

    def as_dict(self) -> dict:
        return {"id": self.document.id, "title": self.document.title,
                "source": self.document.source, "category": self.document.category,
                "score": round(self.score, 8), "bm25_rank": self.bm25_rank,
                "char_rank": self.char_rank}


class HybridIndex:
    """BM25 + character-trigram TF-IDF cosine; fused by reciprocal rank.

    Character grams are a spelling-robust *lexical* signal, not semantic embeddings.
    """

    def __init__(self, documents: Iterable[Document], k1: float = 1.5, b: float = 0.75):
        self.documents = sorted(list(documents), key=lambda d: d.id)
        if len({d.id for d in self.documents}) != len(self.documents):
            raise ValueError("duplicate document IDs")
        self.k1, self.b = k1, b
        self.terms = [Counter(tokenize(d.text)) for d in self.documents]
        self.lengths = [sum(v.values()) for v in self.terms]
        self.avgdl = sum(self.lengths) / max(1, len(self.lengths))
        self.grams = [Counter(chargrams(d.text)) for d in self.documents]
        self.df = Counter(t for row in self.terms for t in row)
        self.gdf = Counter(t for row in self.grams for t in row)
        self.norms = [self._norm(row) for row in self.grams]

    def _idf(self, df: int) -> float:
        n = len(self.documents)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def _gidf(self, gram: str) -> float:
        return math.log((1 + len(self.documents)) / (1 + self.gdf[gram])) + 1

    def _norm(self, row: Counter) -> float:
        return math.sqrt(sum((1 + math.log(count)) ** 2 * self._gidf(g) ** 2
                             for g, count in row.items()))

    def _bm25(self, query: list[str], i: int) -> float:
        row, dl = self.terms[i], self.lengths[i]
        return sum(self._idf(self.df[t]) * (row[t] * (self.k1 + 1)) /
                   (row[t] + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1)))
                   for t in set(query) if row[t])

    def _cosine(self, query: Counter, i: int, qnorm: float) -> float:
        if not qnorm or not self.norms[i]:
            return 0.0
        row = self.grams[i]
        dot = sum((1 + math.log(count)) * self._gidf(g) *
                  (1 + math.log(row[g])) * self._gidf(g)
                  for g, count in query.items() if row[g])
        return dot / (qnorm * self.norms[i])

    def search(self, query: str, k: int = 5, rrf_k: int = 60) -> list[Hit]:
        if k < 1 or k > 100:
            raise ValueError("k must be between 1 and 100")
        tokens = tokenize(query)
        if not tokens or not self.documents:
            return []
        grams = Counter(chargrams(query))
        qnorm = self._norm(grams)
        bm = [(i, self._bm25(tokens, i)) for i in range(len(self.documents))]
        cg = [(i, self._cosine(grams, i, qnorm)) for i in range(len(self.documents))]
        bm = [x for x in sorted(bm, key=lambda x: (-x[1], self.documents[x[0]].id)) if x[1] > 0]
        cg = [x for x in sorted(cg, key=lambda x: (-x[1], self.documents[x[0]].id)) if x[1] >= 0.15]
        ranks_b = {i: rank for rank, (i, _) in enumerate(bm, 1)}
        ranks_c = {i: rank for rank, (i, _) in enumerate(cg, 1)}
        candidates = set(ranks_b) | set(ranks_c)
        scored = [(i, sum(1 / (rrf_k + r) for r in (ranks_b.get(i), ranks_c.get(i)) if r))
                  for i in candidates]
        scored.sort(key=lambda item: (-item[1], self.documents[item[0]].id))
        return [Hit(self.documents[i], score, ranks_b.get(i), ranks_c.get(i))
                for i, score in scored[:k]]
