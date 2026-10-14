import json
from pathlib import Path
s=Path("scripts/source376_aware_small_case.py").read_text(encoding="utf-8").replace("376","499")
print(json.dumps({"scripts/source499_aware_small_case.py":s}))
