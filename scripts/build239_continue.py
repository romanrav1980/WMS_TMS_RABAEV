from pathlib import Path
import json
s=Path("scripts/continue230_to_store.py").read_text(encoding="utf-8").replace("context230.json","context239.json").replace("IW230","IW239").replace("QI230","QI239").replace("Own230","Own239").replace("READY230","READY239")
print(json.dumps({"scripts/continue239_to_depart.py":s},ensure_ascii=True))
