"""Generate the tracked synthetic scenarios and flight-fix CSV deterministically."""
import csv,json
from dataclasses import asdict
from pathlib import Path
from skyweave.scenarios import crossing,separated
from skyweave.models import flights_payload

ROOT=Path(__file__).resolve().parents[1]
def main():
    data=ROOT/'data';data.mkdir(exist_ok=True)
    for name,flights in [('crossing',crossing()),('separated',separated())]:
        (data/f'{name}.json').write_text(json.dumps(flights_payload(flights),indent=2)+'\n')
    with (data/'flight_fixes.csv').open('w',newline='') as fp:
        writer=csv.writer(fp);writer.writerow(['scenario','callsign','t','lat','lon','alt_ft'])
        for name,flights in [('crossing',crossing()),('separated',separated())]:
            for f in flights:
                for p in f.fixes:writer.writerow([name,f.callsign,p.t,p.lat,p.lon,p.alt_ft])
    print('Generated 2 synthetic scenarios and 1 CSV dataset')
if __name__=='__main__':main()
