import argparse,json
from pathlib import Path
from .engine import simulate

def main():
    p=argparse.ArgumentParser(description='Deterministic FIFO queue simulator')
    p.add_argument('scenario');p.add_argument('--output');a=p.parse_args()
    result=json.dumps(simulate(json.loads(Path(a.scenario).read_text())),indent=2,sort_keys=True)+'\n'
    if a.output:
        dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(result)
    else:print(result,end='')
if __name__=='__main__':main()
