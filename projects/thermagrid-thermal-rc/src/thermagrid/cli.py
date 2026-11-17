import argparse,json
from pathlib import Path
from .model import Building,Step,compare_controls

def main():
    p=argparse.ArgumentParser(description='Synthetic RC thermal dynamics lab')
    p.add_argument('scenario');p.add_argument('--output');p.add_argument('--dt',type=float,default=.25);p.add_argument('--target',type=float,default=21.)
    a=p.parse_args();payload=json.loads(Path(a.scenario).read_text())
    result=compare_controls(Building(**payload['building']),[Step(**x) for x in payload['weather']],dt_hours=a.dt,target_c=a.target)
    report=json.dumps(result,indent=2)+'\n'
    if a.output:
        out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(report)
    else:print(report,end='')
if __name__=='__main__':main()
