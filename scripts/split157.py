import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8")
start=s.index("    volumes = set()");end=s.index("    # Empty dynamic faces",start)
fragment=s[start:end];fragment=fragment.replace("    unit_volume = next(iter(volumes)) if complete and len(volumes) == 1 else None","    return (next(iter(volumes)) if complete and len(volumes) == 1 else None), volume_evidence")
helper='''def native_template_volumes(cur: Any, templates: list[tuple[Any, ...]]) -> tuple[Decimal | None, list[dict[str, Any]]]:
'''+fragment+"\n"
s=s[:start]+"    unit_volume, volume_evidence = native_template_volumes(cur, templates)\n"+s[end:]
pos=s.index("def recommendation_sources")
s=s[:pos]+helper+s[pos:]
print(json.dumps({str(p):s}))
