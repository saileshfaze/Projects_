import json,sys
from pathlib import Path
from contrastcraft.audit import audit_file,report

def main():
    root=Path(__file__).resolve().parents[1]
    output=root/'assets/report.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report(audit_file(root/'data/issues.html')),indent=2)+'\n')
    print(output)
if __name__=='__main__':main()
