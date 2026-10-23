"""Offline command-line entry point."""
import argparse
import json
from pathlib import Path
from .retrieval import Document, HybridIndex
from .grounding import answer
from .evaluation import evaluate
from .storage import connect, ingest, all_documents, save_evaluation


def read_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def main() -> None:
    p = argparse.ArgumentParser(description="VerityRAG evidence workbench")
    p.add_argument("--db", default="./verityrag.db")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest").add_argument("path")
    sub.add_parser("search").add_argument("query")
    sub.add_parser("answer").add_argument("query")
    ev = sub.add_parser("evaluate")
    ev.add_argument("questions")
    ev.add_argument("qrels")
    args = p.parse_args()
    con = connect(args.db)
    try:
        if args.command == "ingest":
            result = {"upserted": ingest(con, [Document(**d) for d in read_jsonl(args.path)])}
        else:
            index = HybridIndex(all_documents(con))
            if args.command == "search":
                result = {"hits": [h.as_dict() for h in index.search(args.query)]}
            elif args.command == "answer":
                result = answer(args.query, index.search(args.query)).as_dict()
            else:
                qrels = {q["id"]: set(q["relevant"]) for q in read_jsonl(args.qrels)}
                result = evaluate(index, read_jsonl(args.questions), qrels)
                result["evaluation_id"] = save_evaluation(con, result)
        print(json.dumps(result, indent=2))
    finally:
        con.close()


if __name__ == "__main__":
    main()
