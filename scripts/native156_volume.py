import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8").replace("from typing import Any","from typing import Any\nimport oracledb")
start=s.index("    volumes = set()");end=s.index("    # Empty dynamic faces",start)
s=s[:start]+'''    volumes = set()
    volume_evidence = []
    complete = True
    for face, cell, _volume, _numerator, _denominator in templates:
        error = None
        native_volume = None
        try:
            cur.execute("""select to_char(RRL_STOCK_REPL_CAPACITY.unit_volume(:cell,:article),
                'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')from dual""", cell=cell, article=article)
            value = cur.fetchone()[0]
            if value is not None and Decimal(value) > 0:
                native_volume = Decimal(value)
                volumes.add(native_volume)
            else:
                complete = False
                error = "NATIVE_UNIT_VOLUME_NOT_CONFIRMED"
        except oracledb.DatabaseError as exc:
            if not 20800 <= getattr(exc.args[0], "code", 0) <= 20999:
                raise
            complete = False
            error = str(exc.args[0]).split("\\n", 1)[0]
        volume_evidence.append({"pick_face_id": face, "cell": cell,
            "native_unit_volume_m3": None if native_volume is None else format(native_volume,"f"),
            "refusal": error})
    unit_volume = next(iter(volumes)) if complete and len(volumes) == 1 else None
''' +s[end:]
s=s.replace('"template_unit_volume_complete": unit_volume is not None,','"template_unit_volume_complete": unit_volume is not None, "native_volume_evidence": volume_evidence,')
print(json.dumps({str(p):s}))
