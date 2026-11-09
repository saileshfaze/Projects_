"""Command-line evaluation, simulation and event summaries."""
import argparse, json, random
from dataclasses import asdict
from .core import load_flags, evaluate
from .metrics import summarize

def main():
    parser=argparse.ArgumentParser(description='Flagship progressive delivery lab')
    parser.add_argument('command',choices=['evaluate','simulate'])
    parser.add_argument('--config',default='data/flags.json')
    parser.add_argument('--flag',default='new-checkout')
    parser.add_argument('--subject',default='demo-user')
    parser.add_argument('--count',type=int,default=1000)
    parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args()
    flag=load_flags(args.config)[args.flag]
    if args.command=='evaluate':
        print(json.dumps(asdict(evaluate(flag,args.subject)),indent=2))
    else:
        rng=random.Random(args.seed)
        events=[]
        for i in range(args.count):
            decision=evaluate(flag,f'user-{i}')
            probability=0.16 if decision.variation=='treatment' else 0.12
            events.append({'subject':f'user-{i}','variation':decision.variation,'converted':rng.random()<probability})
        print(json.dumps([asdict(s) for s in summarize(events)],indent=2))
if __name__=='__main__':main()
