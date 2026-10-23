"""Reproducible baseline ranking evaluation from the checked-in synthetic dataset."""
import json
from pathlib import Path
from verityrag.retrieval import Document, HybridIndex
from verityrag.evaluation import evaluate

def load(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def main():
    root = Path(__file__).resolve().parents[1]
    docs = [Document(**item) for item in load(root / "data/documents.jsonl")]
    questions = load(root / "data/questions.jsonl")
    qrels = {row["id"]: set(row["relevant"]) for row in load(root / "data/qrels.jsonl")}
    report = evaluate(HybridIndex(docs), questions, qrels, k=5)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
