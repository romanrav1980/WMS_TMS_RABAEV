from pathlib import Path
v=Path("scripts/docs591_recognition_checkpoint.py").read_text(encoding="utf-8")
head=v.split('p=Path("wiki/database/nicora_ni071_transport_recognition_20261012.md")',1)[0]
body='p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json")'+v.split('p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json")',1)[1]
exec(head+body)