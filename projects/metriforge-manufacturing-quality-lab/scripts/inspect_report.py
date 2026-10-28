"""Print compact lot and rule summaries from a generated JSON report."""
import argparse,json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('report',nargs='?',default='reports/quality-report.json');args=parser.parse_args()
    r=json.loads(Path(args.report).read_text())
    print(json.dumps({'asset':r['asset'],'production_count':r['production_count'],'signal_counts':r['signal_counts'],'lots':r['lots']},indent=2,sort_keys=True))
if __name__=='__main__':main()
