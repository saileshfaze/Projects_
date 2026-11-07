from pathlib import Path
from contrastcraft.audit import audit_file,report
from contrastcraft.colors import grade
import json
root=Path(__file__).resolve().parents[1]
print(json.dumps({'accessible':report(audit_file(root/'data/accessible.html')),'issues':report(audit_file(root/'data/issues.html')),'contrast':grade('#222','#fff')},indent=2))
