import argparse,json,sys
from .audit import audit_file,report
from .colors import grade

def main(argv=None):
    p=argparse.ArgumentParser(description='Static HTML accessibility checks')
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('audit');a.add_argument('file');a.add_argument('--fail-on-errors',action='store_true')
    c=sub.add_parser('contrast');c.add_argument('foreground');c.add_argument('background');c.add_argument('--large',action='store_true')
    args=p.parse_args(argv)
    if args.cmd=='audit':
        result=report(audit_file(args.file));print(json.dumps(result,indent=2));return int(args.fail_on_errors and result['by_severity']['error']>0)
    print(json.dumps(grade(args.foreground,args.background,args.large),indent=2));return 0

if __name__=='__main__':sys.exit(main())
