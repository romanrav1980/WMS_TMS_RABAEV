import json
from pathlib import Path
s=Path("scripts/ni081_range_proposal_continue_case.py").read_text(encoding="utf-8")
s=s.replace("RANGE157.SAVE:","RANGE157.SAVE2:").replace("RANGE157.CANCEL:","RANGE157.CANCEL2:").replace("RANGE157.ACTIVE:","RANGE157.ACTIVE2:")
print(json.dumps({"scripts/ni081_range_proposal_concurrency_case.py":s}))
