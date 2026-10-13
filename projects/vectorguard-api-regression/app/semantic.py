"""Optional embedding similarity from a model already present on disk."""
from pathlib import Path

from .drift import lexical_similarity


def compare_text(left, right, backend="lexical", model_path=None):
    if backend == "lexical":
        return {"backend": "lexical", "similarity": lexical_similarity(left, right)}
    if backend != "embedding":
        raise ValueError("Unsupported similarity backend")
    if not model_path or not Path(model_path).is_dir():
        raise ValueError("Provide a local model directory; remote downloads are disabled")
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install -e '.[ml]'") from exc
    model = SentenceTransformer(model_path, local_files_only=True)
    a, b = model.encode([left, right], normalize_embeddings=True)
    score = float(a @ b)
    return {"backend": "embedding", "similarity": round(max(-1.0, min(1.0, score)), 6)}
