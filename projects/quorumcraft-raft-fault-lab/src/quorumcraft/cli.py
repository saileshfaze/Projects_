"""QuorumCraft CLI entry point."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .raft import Cluster
from .scenarios import demo_actions, actions_from_dict, run_scenario
from .synthetic import generate
from .persistence import export_run, verify_export
from .report import write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="quorumcraft", description="Deterministic Raft fault-injection laboratory")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="run partition-and-heal scenario")
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--ticks", type=int, default=150)
    demo.add_argument("--output", default="out/demo.json")
    demo.add_argument("--svg", default="out/timeline.svg")
    scenario = commands.add_parser("scenario", help="run scenario JSON file")
    scenario.add_argument("path")
    scenario.add_argument("--output", default="out/scenario.json")
    gen = commands.add_parser("generate", help="write deterministic synthetic scenario")
    gen.add_argument("--output", default="data/partition-heal.json")
    verify = commands.add_parser("verify", help="verify exported audit chain")
    verify.add_argument("path")
    serve = commands.add_parser("serve", help="start FastAPI server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)
    if args.command == "generate":
        print(generate(args.output))
        return 0
    if args.command == "verify":
        valid = verify_export(args.path)
        print(json.dumps({"valid": valid}))
        return 0 if valid else 1
    if args.command == "serve":
        import uvicorn
        uvicorn.run("quorumcraft.api:app", host=args.host, port=args.port)
        return 0
    if args.command == "demo":
        cluster = Cluster(seed=args.seed)
        actions = demo_actions()
        run_scenario(cluster, actions, args.ticks)
        write_report(cluster, args.svg)
    else:
        data = json.loads(Path(args.path).read_text(encoding="utf-8"))
        cluster = Cluster(size=data.get("nodes", 5), seed=data.get("seed", 42))
        run_scenario(cluster, actions_from_dict(data["actions"]), data["until"])
    export_run(cluster, args.output)
    print(json.dumps({"output": args.output, "summary": cluster.summary()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
