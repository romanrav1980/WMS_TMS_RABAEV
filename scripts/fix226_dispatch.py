raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_marked_receive/004_root.sql");s=f.read_text(encoding="utf-8")
for kind,pkg in[("in('INTERWARE_UNLOAD','INTERWARE_RECEIVE')","RRL_STOCK_INTERWARE_REC"),("='INTERWARE_PUTAWAY_PLAN'","RRL_STOCK_INTERWARE_PUT"),("='INTERWARE_CUSTODY_RELEASE'","RRL_STOCK_INTERWARE_CUSTODY")]:
 s=s.replace("   if g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then","   if g_kind "+kind+" then "+pkg+".compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind in('MANUAL_MOVE','COMPAT_MANUAL_MOVE') then",1) if pkg=="RRL_STOCK_INTERWARE_REC" else s.replace("   elsif g_kind='RESERVATION_ALLOCATE_POOL'","   elsif g_kind "+kind+" then "+pkg+".compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='RESERVATION_ALLOCATE_POOL'",1)
 s=s.replace("  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command", "  elsif g_kind "+kind+" then "+pkg+".execute_command(g_request,g_actor,p_result);\n  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command",1)
print(json.dumps({str(f):s}))
