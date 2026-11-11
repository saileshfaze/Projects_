"""Command-line interface; all examples operate on synthetic bytes."""
import argparse,json
from pathlib import Path
from .wire import Frame,encode,decode
from .campaign import run
from .trace import export_trace,import_trace
def main(argv=None):
    p=argparse.ArgumentParser(description="PacketForge framed-protocol laboratory")
    sub=p.add_subparsers(dest="command",required=True)
    e=sub.add_parser("encode");e.add_argument("text");e.add_argument("--kind",type=int,default=1);e.add_argument("--sequence",type=int,default=0)
    d=sub.add_parser("decode");d.add_argument("hex")
    c=sub.add_parser("campaign");c.add_argument("--seed",type=int,default=2026);c.add_argument("--cases",type=int,default=500);c.add_argument("--output")
    t=sub.add_parser("trace");t.add_argument("--output",required=True)
    args=p.parse_args(argv)
    if args.command=="encode": print(encode(Frame(args.kind,args.sequence,args.text.encode())).hex())
    elif args.command=="decode":
        f=decode(bytes.fromhex(args.hex));print(json.dumps({"kind":f.kind,"sequence":f.sequence,"payload_hex":f.payload.hex()}))
    elif args.command=="campaign":
        output=json.dumps(run(args.seed,args.cases).to_dict(),indent=2,sort_keys=True)
        if args.output:
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(output+"\n")
        print(output)
    elif args.command=="trace":
        path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(export_trace([Frame(1,i,f"sample-{i}".encode()) for i in range(5)])+"\n")
        print(path)
if __name__=="__main__":main()
