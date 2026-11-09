"""Command-line interface for offline hydraulic studies."""
import argparse,json
from pathlib import Path
from .model import from_dict
from .solver import solve
from .scenarios import simulate
from .report import write_json,svg

def main(argv=None):
    parser=argparse.ArgumentParser(description='Synthetic hydraulic network analysis')
    parser.add_argument('--network',default='data/network.json')
    parser.add_argument('--output',default='artifacts/report.json')
    parser.add_argument('--svg',default='artifacts/network.svg')
    parser.add_argument('--trials',type=int,default=100)
    parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args(argv)
    network=from_dict(json.loads(Path(args.network).read_text()))
    solution=solve(network)
    if not solution.converged:raise SystemExit('solver did not converge')
    experiment=simulate(network,seed=args.seed,trials=args.trials)
    write_json(args.output,{'solution':solution.as_dict(),'experiment':experiment})
    p=Path(args.svg);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(svg(network,solution))
    print(f"Converged in {solution.iterations} iterations; residual={solution.residual:.3g}; trials={args.trials}")
    return 0

if __name__=='__main__':raise SystemExit(main())
