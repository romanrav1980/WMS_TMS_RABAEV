from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/db.py");s=p.read_text(encoding="utf-8")
s=s.replace("    connection = pool.acquire()\n    try:","    connection = pool.acquire()\n    connection.call_timeout = max(1000, min(120000, int(os.environ.get(\"WMS_ORACLE_CALL_TIMEOUT_MS\", \"30000\"))))\n    try:")
s=s.replace("        try:\n            connection.rollback()","        try:\n            connection.call_timeout = 3000\n            connection.rollback()")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py");s=p.read_text(encoding="utf-8")
s=s.replace("                inp, out = q.var(oracledb.DB_TYPE_CLOB), q.var(oracledb.DB_TYPE_CLOB)\n                inp.setvalue(0, wire)\n                q.callproc(\"RRL_WEIGHT_BOX_CHOICE_API.approve_request\", [inp, actor, out])","                # Canonical ASCII request is bounded to 16KB by the native contract.\n                # Bind VARCHAR directly: Oracle converts to CLOB before entering the package.\n                out = q.var(oracledb.DB_TYPE_CLOB)\n                q.callproc(\"RRL_WEIGHT_BOX_CHOICE_API.approve_request\", [wire, actor, out])")
out[str(p)]=s
p=Path("scripts/capture197_weight_units.py");out[str(p)]=p.read_text(encoding="utf-8").replace("RRL_STOCK_WAVE_REPL_CMD","RRL_STOCK_WAVE_CMD")
print(json.dumps(out,ensure_ascii=True))
