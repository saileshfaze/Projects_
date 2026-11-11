"""Reproduce fixture traces without network or personal data."""
from pathlib import Path
from packetforge.wire import Frame
from packetforge.trace import export_trace
def main():
    out=Path(__file__).resolve().parents[1]/"data"/"synthetic-trace.json"
    out.write_text(export_trace([Frame(i%3,i,f"synthetic-message-{i}".encode()) for i in range(12)])+"\n")
    print(out)
if __name__=="__main__":main()
