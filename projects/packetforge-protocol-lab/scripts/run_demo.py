"""Produce deterministic sample report."""
import json
from pathlib import Path
from packetforge.campaign import run
def main():
    out=Path(__file__).resolve().parents[1]/"data"/"sample-campaign.json"
    out.write_text(json.dumps(run(2026,250).to_dict(),indent=2,sort_keys=True)+"\n")
    print(out)
if __name__=="__main__":main()
