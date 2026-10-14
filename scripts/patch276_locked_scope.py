from pathlib import Path
import json
p=Path("db/migrations/2026-10-11_ni072_st_defer/002_api.sql")
s=p.read_text(encoding="utf-8")
s=s.replace("if n!=1 then raise_application_error(-20886,'ST_DEFER_ONE_CURRENT_WARE_REQUIRED');end if;","if n!=1 then raise_application_error(-20886,'ST_DEFER_ONE_CURRENT_WARE_REQUIRED');end if;\n  select count(*)into n from RRL_SBORKA_PALLETS where ST_NUMBER=p_st and WARE_ID is null;\n  if n>0 then raise_application_error(-20886,'ST_DEFER_NULL_WARE_REFUSED');end if;")
s=s.replace("scope(p_ware,p_actor,p_right);\n  for x in", "access_st(p_st,p_actor,p_right,p_ware);\n  for x in")
s=s.replace("   select count(*)into n from RRL_TRANSPORT_TASK where ID=t.ID", "   select ID into n from RRL_TRANSPORT_TASK where ID=t.ID for update wait 3;\n   select count(*)into n from RRL_TRANSPORT_TASK where ID=t.ID")
s=s.replace("   select ID into n from RRL_TRANSPORT_TASK where ID=t.ID for update wait 3;\n  end loop;", "  end loop;")
print(json.dumps({str(p):s}))
