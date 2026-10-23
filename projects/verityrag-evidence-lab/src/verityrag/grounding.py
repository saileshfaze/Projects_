"""Citation-aware extractive answers. Retrieved text is always untrusted data."""
from __future__ import annotations

from dataclasses import dataclass
import re
from .retrieval import Hit, tokenize

INJECTION = re.compile(r"(?i)(ignore (all |the )?(previous|prior|system) (instructions|prompts)|"
                       r"you are now|developer message:|system prompt:|reveal (your |the )?secrets|"
                       r"execute (this |the )?command|send (the |all )?credentials)")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\w)(?:\+\d{1,3}[ -]?)?(?:\d[ -]?){9,13}(?!\w)")
STOP = {"what", "is", "the", "a", "an", "of", "to", "for", "and", "in", "on", "how",
        "does", "do", "are", "can", "be", "when", "which", "with", "from", "by"}


def redact(text: str) -> str:
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", text))


def untrusted(text: str) -> bool:
    return bool(INJECTION.search(text))


@dataclass(frozen=True)
class Answer:
    question: str
    text: str
    citations: list[dict]
    abstained: bool
    filtered_documents: list[str]

    def as_dict(self) -> dict:
        return {"question": self.question, "answer": self.text,
                "citations": self.citations, "abstained": self.abstained,
                "filtered_documents": self.filtered_documents}


def answer(question: str, hits: list[Hit], min_overlap: float = 0.30,
           max_sentences: int = 2) -> Answer:
    """Only returns contiguous source sentences with document IDs and offsets.

    A score threshold on this extractive baseline is NOT calibrated confidence.
    """
    query = set(tokenize(question)) - STOP
    if not query:
        return Answer(question, "Insufficient evidence.", [], True, [])
    candidates = []
    filtered = []
    for hit in hits:
        body = hit.document.body
        if untrusted(body):
            filtered.append(hit.document.id)
            continue
        for match in re.finditer(r"[^.!?\n]+[.!?]?", body):
            raw = match.group().strip()
            if len(raw) < 18:
                continue
            overlap = len(query & set(tokenize(raw))) / len(query)
            if overlap >= min_overlap:
                candidates.append((overlap, hit.score, hit.document.id,
                                   match.start() + len(match.group()) - len(match.group().lstrip()), raw))
    candidates.sort(key=lambda x: (-x[0], -x[1], x[2], x[3]))
    chosen = []
    seen = set()
    for overlap, _, doc_id, offset, raw in candidates:
        key = (doc_id, offset)
        if key in seen:
            continue
        seen.add(key)
        chosen.append((doc_id, offset, raw, overlap))
        if len(chosen) >= max_sentences:
            break
    if not chosen:
        return Answer(question, "Insufficient evidence.", [], True, filtered)
    return Answer(question, " ".join(redact(raw) for _, _, raw, _ in chosen),
                  [{"document_id": doc_id, "start": offset, "end": offset + len(raw),
                    "excerpt": redact(raw), "query_term_overlap": round(overlap, 3)}
                   for doc_id, offset, raw, overlap in chosen], False, filtered)


def verify_citations(result: Answer, documents: dict[str, str]) -> bool:
    """Validate exact offsets against the unredacted original; reject invented citations."""
    for citation in result.citations:
        body = documents.get(citation["document_id"])
        if body is None:
            return False
        if redact(body[citation["start"]:citation["end"]]) != citation["excerpt"]:
            return False
    return bool(result.citations) != result.abstained
