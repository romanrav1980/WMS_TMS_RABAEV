import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/range_apply.py");s=p.read_text(encoding="utf-8")
s=s.replace('with stock_configuration_transaction(self.gateway, "Publish original pick range and drain policy", actor, "pick_topology_edit") as cur:\n                cur.execute', '''with stock_configuration_transaction(self.gateway, "Publish original pick range and drain policy", actor, "pick_topology_edit") as cur:
                confirmed = range_command(cur, ware, article, operation, "APPROVE", actor, body)
                if confirmed["status"] != "SOURCE_RECOMPUTATION_REQUIRED":
                    return confirmed
                cur.execute''')
out[str(p)]=s
p=Path("db/migrations/2026-10-10_ni081_range_apply/006_core.sql");s=p.read_text(encoding="utf-8")
s=s.replace("create or replace package body RRL_PICK_RANGE_APPLY_CORE as", """create or replace package body RRL_PICK_RANGE_APPLY_CORE as
 procedure current_actor(p_actor varchar2,p_ware number)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
   and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'pick_topology_edit')=1;
  if n!=1 then raise_application_error(-20882,'PICK_RANGE_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;""")
s=s.replace("  if proposal.WARE_ID!=p_ware", "  current_actor(p_actor,p_ware);\n  if proposal.WARE_ID!=p_ware")
s=s.replace("  v_proof:=s.to_clob;", """  for i in 0..selected.get_size-1 loop
   x:=treat(selected.get(i)as json_object_t);candidate(x.get_number('pick_face_id'),p_ware,weight,f);
  end loop;
  current_actor(p_actor,p_ware);
  v_proof:=s.to_clob;""")
s=s.replace("  if s.MODE_CODE!='DRAINING'", "  current_actor(p_actor,p_ware);\n  if s.MODE_CODE!='DRAINING'")
out[str(p)]=s
print(json.dumps(out))
